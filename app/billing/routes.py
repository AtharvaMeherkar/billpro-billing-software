"""
Billing Routes - Sales Invoice Management
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from decimal import Decimal

from app.billing import billing_bp
from app.models.base import db
from app.models.invoice import Invoice, InvoiceItem
from app.models.product import Product
from app.models.party import Party, PartyTransaction
from app.models.accounting import CashTransaction, BankTransaction, JournalEntry
from app.services.financial_year import get_current_fy
from app.services.tax_calculator import TaxCalculator
from app.services.stock_manager import StockManager
from app.utils.number_utils import number_to_words


@billing_bp.route('/')
def index():
    """List all invoices"""
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    # Filters
    search = request.args.get('search', '')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    payment_mode = request.args.get('payment_mode')
    
    query = Invoice.query.filter_by(status='ACTIVE')
    
    if search:
        query = query.join(Party).filter(
            db.or_(
                Invoice.invoice_number.ilike(f'%{search}%'),
                Party.name.ilike(f'%{search}%')
            )
        )
    
    if date_from:
        query = query.filter(Invoice.invoice_date >= date_from)
    if date_to:
        query = query.filter(Invoice.invoice_date <= date_to)
    if payment_mode:
        query = query.filter(Invoice.payment_mode == payment_mode)
    
    invoices = query.order_by(Invoice.id.desc()).paginate(page=page, per_page=per_page)
    
    return render_template('billing/index.html', invoices=invoices)


@billing_bp.route('/new')
def new():
    """Create new invoice form"""
    customers = Party.query.filter_by(party_type='customer', is_active=True).order_by(Party.name).all()
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    
    return render_template('billing/new.html', 
                          customers=customers, 
                          products=products,
                          today=date.today())


@billing_bp.route('/create', methods=['POST'])
def create():
    """Create new invoice"""
    try:
        fy = get_current_fy()
        
        # Get form data
        party_id = request.form.get('party_id', type=int)
        invoice_date = datetime.strptime(request.form.get('invoice_date'), '%Y-%m-%d').date()
        is_gst = request.form.get('is_gst_invoice') == 'on'
        payment_mode = request.form.get('payment_mode', 'CASH')
        notes = request.form.get('notes', '')
        
        # Validate party
        party = Party.query.get(party_id)
        if not party:
            flash('Invalid customer selected', 'error')
            return redirect(url_for('billing.new'))
        
        # Determine IGST or CGST+SGST based on state codes
        import json
        import os
        from config.settings import Config
        
        company = {}
        if os.path.exists(Config.COMPANY_CONFIG):
            with open(Config.COMPANY_CONFIG, 'r') as f:
                company = json.load(f)
        
        seller_state = company.get('address', {}).get('state_code', '')
        buyer_state = party.state_code or TaxCalculator.get_state_code_from_gstin(party.gstin)
        is_igst = TaxCalculator.is_interstate(seller_state, buyer_state) if is_gst else False
        
        # Generate invoice number
        invoice_number = fy.get_next_invoice_number()
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            financial_year_id=fy.id,
            party_id=party_id,
            is_gst_invoice=is_gst,
            is_igst=is_igst,
            payment_mode=payment_mode,
            notes=notes
        )
        db.session.add(invoice)
        db.session.flush()  # Get invoice ID
        
        # Process line items
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        rates = request.form.getlist('rate[]')
        discounts = request.form.getlist('discount[]')
        
        for i, product_id in enumerate(product_ids):
            if not product_id:
                continue
            
            product = Product.query.get(int(product_id))
            if not product:
                continue
            
            qty = Decimal(quantities[i] or 0)
            rate = Decimal(rates[i] or 0)
            discount = Decimal(discounts[i] or 0)
            
            if qty <= 0:
                continue
            
            # Calculate amounts
            gross_amount = qty * rate
            discount_amount = (gross_amount * discount / 100) if discount else Decimal('0')
            taxable_amount = gross_amount - discount_amount
            
            # Create invoice item
            item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=product.id,
                description=product.name,
                hsn_code=product.hsn_code,
                quantity=qty,
                unit=product.unit,
                rate=rate,
                discount_percent=discount,
                discount_amount=discount_amount,
                taxable_amount=taxable_amount,
                gst_percent=product.gst_percent if is_gst else 0
            )
            
            # Calculate tax
            if is_gst:
                item.calculate_tax(is_igst=is_igst)
            else:
                item.total_amount = taxable_amount
            
            db.session.add(item)
            
            # Deduct stock
            StockManager.deduct_stock(
                product_id=product.id,
                quantity=qty,
                reference_type='INVOICE',
                reference_id=invoice.id,
                notes=f'Sale: {invoice_number}'
            )
        
        # Calculate invoice totals
        invoice.calculate_totals()
        
        # Create accounting entries
        _create_sale_accounting_entries(invoice, party)
        
        db.session.commit()
        
        flash(f'Invoice {invoice_number} created successfully', 'success')
        return redirect(url_for('billing.view', id=invoice.id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating invoice: {str(e)}', 'error')
        return redirect(url_for('billing.new'))


def _create_sale_accounting_entries(invoice, party):
    """Create accounting entries for a sale"""
    
    # Journal entry for sale
    sale_entry = JournalEntry(
        entry_date=invoice.invoice_date,
        account_type='SALES',
        account_name='Sales',
        debit=0,
        credit=invoice.subtotal,
        reference_type='INVOICE',
        reference_id=invoice.id,
        reference_number=invoice.invoice_number,
        narration=f'Sale to {party.name}',
        financial_year_id=invoice.financial_year_id
    )
    db.session.add(sale_entry)
    
    # Party ledger entry (debit for customer)
    if invoice.payment_mode == 'CREDIT':
        party_entry = PartyTransaction(
            party_id=party.id,
            transaction_date=invoice.invoice_date,
            transaction_type='SALE',
            reference_type='INVOICE',
            reference_id=invoice.id,
            reference_number=invoice.invoice_number,
            debit=invoice.total_amount,
            credit=0,
            narration=f'Sale Invoice {invoice.invoice_number}'
        )
        db.session.add(party_entry)
        party.update_balance(invoice.total_amount, 'debit')
    
    # Cash/Bank entry
    if invoice.payment_mode == 'CASH':
        cash_entry = CashTransaction(
            transaction_date=invoice.invoice_date,
            transaction_type='RECEIPT',
            party_id=party.id,
            description=f'Cash sale to {party.name}',
            receipt=invoice.total_amount,
            reference_type='INVOICE',
            reference_id=invoice.id,
            reference_number=invoice.invoice_number
        )
        db.session.add(cash_entry)
    
    elif invoice.payment_mode == 'BANK':
        bank_entry = BankTransaction(
            transaction_date=invoice.invoice_date,
            transaction_type='DEPOSIT',
            party_id=party.id,
            description=f'Bank sale to {party.name}',
            deposit=invoice.total_amount,
            reference_type='INVOICE',
            reference_id=invoice.id,
            reference_number=invoice.invoice_number
        )
        db.session.add(bank_entry)


@billing_bp.route('/<int:id>')
def view(id):
    """View invoice details"""
    invoice = Invoice.query.get_or_404(id)
    amount_words = number_to_words(float(invoice.total_amount))
    
    return render_template('billing/view.html', invoice=invoice, amount_words=amount_words)


@billing_bp.route('/<int:id>/print')
def print_invoice(id):
    """Print invoice - A4 format"""
    invoice = Invoice.query.get_or_404(id)
    amount_words = number_to_words(float(invoice.total_amount))
    
    import json
    import os
    from config.settings import Config
    
    company = {}
    if os.path.exists(Config.COMPANY_CONFIG):
        with open(Config.COMPANY_CONFIG, 'r') as f:
            company = json.load(f)
    
    return render_template('bills/invoice_a4.html', 
                          invoice=invoice, 
                          company=company,
                          amount_words=amount_words)


@billing_bp.route('/<int:id>/preview-thermal')
def preview_thermal(id):
    """Preview invoice - Thermal format (on screen)"""
    invoice = Invoice.query.get_or_404(id)
    
    import json
    import os
    from config.settings import Config
    
    company = {}
    printer_config = {}
    
    if os.path.exists(Config.COMPANY_CONFIG):
        with open(Config.COMPANY_CONFIG, 'r') as f:
            company = json.load(f)
    
    if os.path.exists(Config.PRINTER_CONFIG):
        with open(Config.PRINTER_CONFIG, 'r') as f:
            printer_config = json.load(f)
    
    return render_template('bills/thermal_preview.html', 
                          invoice=invoice, 
                          company=company,
                          printer_config=printer_config)


@billing_bp.route('/<int:id>/print-thermal')
def print_thermal(id):
    """Print invoice - Thermal format"""
    invoice = Invoice.query.get_or_404(id)
    
    from app.printing.printer import ThermalPrinter
    
    try:
        printer = ThermalPrinter()
        result = printer.print_invoice(invoice)
        
        if result:
            flash('Invoice sent to printer', 'success')
        else:
            flash('Printing failed', 'error')
    except Exception as e:
        flash(f'Printing error: {str(e)}', 'error')
    
    return redirect(url_for('billing.view', id=id))


@billing_bp.route('/<int:id>/cancel', methods=['POST'])
def cancel(id):
    """Cancel an invoice"""
    invoice = Invoice.query.get_or_404(id)
    
    if invoice.status == 'CANCELLED':
        flash('Invoice is already cancelled', 'warning')
        return redirect(url_for('billing.view', id=id))
    
    # Reverse stock
    for item in invoice.items:
        StockManager.add_stock(
            product_id=item.product_id,
            quantity=item.quantity,
            reference_type='INVOICE_CANCEL',
            reference_id=invoice.id,
            notes=f'Invoice cancellation: {invoice.invoice_number}'
        )
    
    # Reverse party balance if credit sale
    if invoice.payment_mode == 'CREDIT':
        party = invoice.party
        party.update_balance(invoice.total_amount, 'credit')
        
        # Create reversal transaction
        reversal = PartyTransaction(
            party_id=party.id,
            transaction_date=date.today(),
            transaction_type='SALE_REVERSAL',
            reference_type='INVOICE',
            reference_id=invoice.id,
            reference_number=invoice.invoice_number,
            debit=0,
            credit=invoice.total_amount,
            narration=f'Sale Invoice Cancelled: {invoice.invoice_number}'
        )
        db.session.add(reversal)
    
    invoice.status = 'CANCELLED'
    db.session.commit()
    
    flash(f'Invoice {invoice.invoice_number} cancelled', 'success')
    return redirect(url_for('billing.view', id=id))


# API endpoints for AJAX
@billing_bp.route('/api/product/<int:id>')
def get_product(id):
    """Get product details for invoice form"""
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'hsn_code': product.hsn_code,
        'gst_percent': float(product.gst_percent or 0),
        'selling_price': float(product.selling_price or 0),
        'unit': product.unit,
        'current_stock': float(product.current_stock or 0)
    })


@billing_bp.route('/api/party/<int:id>')
def get_party(id):
    """Get party details for invoice form"""
    party = Party.query.get_or_404(id)
    return jsonify({
        'id': party.id,
        'name': party.name,
        'gstin': party.gstin,
        'state_code': party.state_code_from_gstin or party.state_code,
        'address': party.full_address,
        'current_balance': float(party.current_balance or 0)
    })
