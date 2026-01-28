"""
Ledgers Routes - Customer/Supplier Management
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, Response
from datetime import date, datetime
from decimal import Decimal
import csv
import io

from app.ledgers import ledgers_bp
from app.models.base import db
from app.models.party import Party, PartyTransaction
from app.models.accounting import CashTransaction, BankTransaction
from config.settings import Config


@ledgers_bp.route('/')
def index():
    """List all parties"""
    party_type = request.args.get('type', 'all')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = Party.query.filter_by(is_active=True)
    
    if party_type != 'all':
        query = query.filter_by(party_type=party_type)
    
    if search:
        query = query.filter(
            db.or_(
                Party.name.ilike(f'%{search}%'),
                Party.gstin.ilike(f'%{search}%'),
                Party.phone.ilike(f'%{search}%')
            )
        )
    
    parties = query.order_by(Party.name).paginate(page=page, per_page=25)
    
    # Summary
    total_receivable = db.session.query(db.func.sum(Party.current_balance)).filter(
        Party.party_type == 'customer',
        Party.current_balance > 0
    ).scalar() or 0
    
    total_payable = db.session.query(db.func.sum(Party.current_balance)).filter(
        Party.party_type == 'supplier',
        Party.current_balance > 0
    ).scalar() or 0
    
    return render_template('ledgers/index.html',
                          parties=parties,
                          party_type=party_type,
                          total_receivable=total_receivable,
                          total_payable=total_payable,
                          state_codes=Config.STATE_CODES)


@ledgers_bp.route('/add', methods=['GET', 'POST'])
def add():
    """Add new party"""
    if request.method == 'POST':
        try:
            party = Party(
                name=request.form.get('name'),
                party_type=request.form.get('party_type', 'customer'),
                code=request.form.get('code') or None,
                gstin=request.form.get('gstin') or None,
                pan=request.form.get('pan') or None,
                contact_person=request.form.get('contact_person'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address_line1=request.form.get('address_line1'),
                address_line2=request.form.get('address_line2'),
                city=request.form.get('city'),
                state=request.form.get('state'),
                state_code=request.form.get('state_code'),
                pincode=request.form.get('pincode'),
                opening_balance=Decimal(request.form.get('opening_balance', '0')),
                credit_limit=Decimal(request.form.get('credit_limit', '0')),
                credit_days=int(request.form.get('credit_days', '30') or 30)
            )
            
            # Set current balance to opening balance
            party.current_balance = party.opening_balance
            
            db.session.add(party)
            db.session.flush()
            
            # Create opening balance transaction if any
            if party.opening_balance != 0:
                txn = PartyTransaction(
                    party_id=party.id,
                    transaction_date=date.today(),
                    transaction_type='OPENING',
                    reference_type='OPENING',
                    debit=party.opening_balance if party.opening_balance > 0 else 0,
                    credit=abs(party.opening_balance) if party.opening_balance < 0 else 0,
                    balance=party.opening_balance,
                    narration='Opening Balance'
                )
                db.session.add(txn)
            
            db.session.commit()
            
            flash(f'{party.party_type.title()} "{party.name}" added successfully', 'success')
            return redirect(url_for('ledgers.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding party: {str(e)}', 'error')
    
    return render_template('ledgers/add.html', state_codes=Config.STATE_CODES)


@ledgers_bp.route('/<int:id>')
def view(id):
    """View party ledger"""
    party = Party.query.get_or_404(id)
    
    # Date filters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = PartyTransaction.query.filter_by(party_id=id)
    
    if date_from:
        query = query.filter(PartyTransaction.transaction_date >= date_from)
    if date_to:
        query = query.filter(PartyTransaction.transaction_date <= date_to)
    
    transactions = query.order_by(PartyTransaction.transaction_date.desc(), 
                                  PartyTransaction.id.desc()).all()
    
    return render_template('ledgers/view.html', party=party, transactions=transactions)


@ledgers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit party"""
    party = Party.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            party.name = request.form.get('name')
            party.code = request.form.get('code') or None
            party.gstin = request.form.get('gstin') or None
            party.pan = request.form.get('pan') or None
            party.contact_person = request.form.get('contact_person')
            party.phone = request.form.get('phone')
            party.email = request.form.get('email')
            party.address_line1 = request.form.get('address_line1')
            party.address_line2 = request.form.get('address_line2')
            party.city = request.form.get('city')
            party.state = request.form.get('state')
            party.state_code = request.form.get('state_code')
            party.pincode = request.form.get('pincode')
            party.credit_limit = Decimal(request.form.get('credit_limit', '0'))
            party.credit_days = int(request.form.get('credit_days', '30') or 30)
            party.is_active = request.form.get('is_active') == 'on'
            
            db.session.commit()
            
            flash('Party updated successfully', 'success')
            return redirect(url_for('ledgers.view', id=id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating party: {str(e)}', 'error')
    
    return render_template('ledgers/edit.html', party=party, state_codes=Config.STATE_CODES)


@ledgers_bp.route('/<int:id>/receive-payment', methods=['POST'])
def receive_payment(id):
    """Record payment receipt from customer"""
    party = Party.query.get_or_404(id)
    
    try:
        amount = Decimal(request.form.get('amount', '0'))
        payment_mode = request.form.get('payment_mode', 'CASH')
        reference = request.form.get('reference', '')
        notes = request.form.get('notes', '')
        payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d').date()
        
        if amount <= 0:
            flash('Invalid amount', 'error')
            return redirect(url_for('ledgers.view', id=id))
        
        # Create party transaction (credit)
        txn = PartyTransaction(
            party_id=id,
            transaction_date=payment_date,
            transaction_type='RECEIPT',
            reference_type='RECEIPT',
            reference_number=reference,
            debit=0,
            credit=amount,
            narration=notes or f'Payment received via {payment_mode}'
        )
        db.session.add(txn)
        
        # Update party balance
        party.update_balance(amount, 'credit')
        
        # Create cash/bank entry
        if payment_mode == 'CASH':
            cash = CashTransaction(
                transaction_date=payment_date,
                transaction_type='RECEIPT',
                party_id=id,
                description=f'Payment from {party.name}',
                receipt=amount,
                reference_number=reference,
                narration=notes
            )
            db.session.add(cash)
        else:
            bank = BankTransaction(
                transaction_date=payment_date,
                transaction_type='DEPOSIT',
                party_id=id,
                description=f'Payment from {party.name}',
                deposit=amount,
                cheque_number=reference,
                narration=notes
            )
            db.session.add(bank)
        
        db.session.commit()
        
        flash(f'Payment of ₹{amount} received successfully', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error recording payment: {str(e)}', 'error')
    
    return redirect(url_for('ledgers.view', id=id))


@ledgers_bp.route('/<int:id>/make-payment', methods=['POST'])
def make_payment(id):
    """Record payment to supplier"""
    party = Party.query.get_or_404(id)
    
    try:
        amount = Decimal(request.form.get('amount', '0'))
        payment_mode = request.form.get('payment_mode', 'CASH')
        reference = request.form.get('reference', '')
        notes = request.form.get('notes', '')
        payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d').date()
        
        if amount <= 0:
            flash('Invalid amount', 'error')
            return redirect(url_for('ledgers.view', id=id))
        
        # Create party transaction (debit for supplier)
        txn = PartyTransaction(
            party_id=id,
            transaction_date=payment_date,
            transaction_type='PAYMENT',
            reference_type='PAYMENT',
            reference_number=reference,
            debit=amount,
            credit=0,
            narration=notes or f'Payment made via {payment_mode}'
        )
        db.session.add(txn)
        
        # Update party balance (decrease)
        party.update_balance(amount, 'debit')
        
        # Create cash/bank entry
        if payment_mode == 'CASH':
            cash = CashTransaction(
                transaction_date=payment_date,
                transaction_type='PAYMENT',
                party_id=id,
                description=f'Payment to {party.name}',
                payment=amount,
                reference_number=reference,
                narration=notes
            )
            db.session.add(cash)
        else:
            bank = BankTransaction(
                transaction_date=payment_date,
                transaction_type='WITHDRAWAL',
                party_id=id,
                description=f'Payment to {party.name}',
                withdrawal=amount,
                cheque_number=reference,
                narration=notes
            )
            db.session.add(bank)
        
        db.session.commit()
        
        flash(f'Payment of ₹{amount} made successfully', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error recording payment: {str(e)}', 'error')
    
    return redirect(url_for('ledgers.view', id=id))


@ledgers_bp.route('/<int:id>/export')
def export_ledger(id):
    """Export party ledger to CSV"""
    party = Party.query.get_or_404(id)
    transactions = PartyTransaction.query.filter_by(party_id=id)\
        .order_by(PartyTransaction.transaction_date).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Date', 'Type', 'Reference', 'Debit', 'Credit', 'Narration'])
    
    for t in transactions:
        writer.writerow([
            t.transaction_date.strftime('%d-%m-%Y'),
            t.transaction_type,
            t.reference_number or '',
            float(t.debit) if t.debit else '',
            float(t.credit) if t.credit else '',
            t.narration or ''
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={party.name}_ledger.csv'}
    )


@ledgers_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete party (mark inactive)"""
    party = Party.query.get_or_404(id)
    
    # Check for transactions
    if party.current_balance != 0:
        flash('Cannot delete party with outstanding balance', 'error')
        return redirect(url_for('ledgers.view', id=id))
    
    party.is_active = False
    db.session.commit()
    
    flash(f'Party "{party.name}" deleted', 'success')
    return redirect(url_for('ledgers.index'))


# API
@ledgers_bp.route('/api/search')
def api_search():
    """Search parties for autocomplete"""
    q = request.args.get('q', '')
    party_type = request.args.get('type', 'all')
    
    query = Party.query.filter(
        Party.is_active == True,
        db.or_(
            Party.name.ilike(f'%{q}%'),
            Party.phone.ilike(f'%{q}%')
        )
    )
    
    if party_type != 'all':
        query = query.filter_by(party_type=party_type)
    
    parties = query.limit(20).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'gstin': p.gstin,
        'phone': p.phone,
        'balance': float(p.current_balance or 0)
    } for p in parties])
