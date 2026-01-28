"""
E-Invoice Routes - GST E-Invoice JSON Generation (Offline)
"""
import json
import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, send_file, Response

from app.einvoice import einvoice_bp
from app.models.base import db
from app.models.invoice import Invoice
from config.settings import Config


@einvoice_bp.route('/')
def index():
    """E-invoice dashboard"""
    # Get invoices eligible for e-invoice (B2B, GST invoices)
    invoices = Invoice.query.filter(
        Invoice.is_gst_invoice == True,
        Invoice.status == 'ACTIVE'
    ).order_by(Invoice.id.desc()).limit(50).all()
    
    generated_count = Invoice.query.filter_by(einvoice_generated=True).count()
    
    return render_template('einvoice/index.html', 
                          invoices=invoices,
                          generated_count=generated_count)


@einvoice_bp.route('/generate/<int:id>', methods=['POST'])
def generate(id):
    """Generate e-invoice JSON for an invoice"""
    invoice = Invoice.query.get_or_404(id)
    
    if not invoice.is_gst_invoice:
        flash('E-invoice can only be generated for GST invoices', 'error')
        return redirect(url_for('einvoice.index'))
    
    try:
        # Generate JSON
        einvoice_data = _generate_einvoice_json(invoice)
        
        # Save JSON file
        einvoice_dir = os.path.join(Config.BASE_DIR, 'einvoices')
        os.makedirs(einvoice_dir, exist_ok=True)
        
        filename = f"einvoice_{invoice.invoice_number.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(einvoice_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(einvoice_data, f, indent=2, default=str)
        
        # Update invoice
        invoice.einvoice_generated = True
        invoice.einvoice_json_path = filepath
        db.session.commit()
        
        flash(f'E-invoice JSON generated: {filename}', 'success')
    
    except Exception as e:
        flash(f'Error generating e-invoice: {str(e)}', 'error')
    
    return redirect(url_for('einvoice.index'))


@einvoice_bp.route('/download/<int:id>')
def download(id):
    """Download e-invoice JSON"""
    invoice = Invoice.query.get_or_404(id)
    
    if not invoice.einvoice_json_path or not os.path.exists(invoice.einvoice_json_path):
        flash('E-invoice JSON not found', 'error')
        return redirect(url_for('einvoice.index'))
    
    return send_file(invoice.einvoice_json_path, as_attachment=True)


@einvoice_bp.route('/view/<int:id>')
def view(id):
    """View e-invoice JSON"""
    invoice = Invoice.query.get_or_404(id)
    
    if not invoice.einvoice_json_path or not os.path.exists(invoice.einvoice_json_path):
        # Generate on the fly for preview
        einvoice_data = _generate_einvoice_json(invoice)
    else:
        with open(invoice.einvoice_json_path, 'r') as f:
            einvoice_data = json.load(f)
    
    return render_template('einvoice/view.html', 
                          invoice=invoice, 
                          einvoice_data=json.dumps(einvoice_data, indent=2, default=str))


def _generate_einvoice_json(invoice):
    """
    Generate GST E-Invoice JSON as per Indian GST specification
    Note: This generates the JSON structure, actual IRN generation requires API call
    """
    # Load company details
    company = {}
    if os.path.exists(Config.COMPANY_CONFIG):
        with open(Config.COMPANY_CONFIG, 'r') as f:
            company = json.load(f)
    
    party = invoice.party
    
    # Transaction Details
    tran_dtls = {
        "TaxSch": "GST",
        "SupTyp": "B2B",  # B2B, SEZWP, SEZWOP, EXPWP, EXPWOP, DEXP
        "RegRev": "N",     # Reverse Charge: Y/N
        "EcmGstin": None,
        "IgstOnIntra": "N" if not invoice.is_igst else "Y"
    }
    
    # Document Details
    doc_dtls = {
        "Typ": "INV",  # INV, CRN, DBN
        "No": invoice.invoice_number,
        "Dt": invoice.invoice_date.strftime("%d/%m/%Y")
    }
    
    # Seller Details
    seller_dtls = {
        "Gstin": company.get('gstin', ''),
        "LglNm": company.get('name', ''),
        "TrdNm": company.get('name', ''),
        "Addr1": company.get('address', {}).get('line1', ''),
        "Addr2": company.get('address', {}).get('line2', ''),
        "Loc": company.get('address', {}).get('city', ''),
        "Pin": int(company.get('address', {}).get('pincode', '0') or 0),
        "Stcd": company.get('address', {}).get('state_code', ''),
        "Ph": company.get('contact', {}).get('phone', ''),
        "Em": company.get('contact', {}).get('email', '')
    }
    
    # Buyer Details
    buyer_dtls = {
        "Gstin": party.gstin or "URP",  # URP for unregistered
        "LglNm": party.name,
        "TrdNm": party.name,
        "Pos": party.state_code or company.get('address', {}).get('state_code', ''),
        "Addr1": party.address_line1 or '',
        "Addr2": party.address_line2 or '',
        "Loc": party.city or '',
        "Pin": int(party.pincode or 0),
        "Stcd": party.state_code or '',
        "Ph": party.phone or '',
        "Em": party.email or ''
    }
    
    # Item List
    item_list = []
    sr_no = 0
    
    for item in invoice.items:
        sr_no += 1
        
        item_entry = {
            "SlNo": str(sr_no),
            "PrdDesc": item.description or item.product.name,
            "IsServc": "N",  # Y for services
            "HsnCd": item.hsn_code or item.product.hsn_code or "",
            "Barcde": None,
            "Qty": float(item.quantity),
            "FreeQty": 0,
            "Unit": _map_unit_code(item.unit or item.product.unit),
            "UnitPrice": float(item.rate),
            "TotAmt": float(item.quantity) * float(item.rate),
            "Discount": float(item.discount_amount or 0),
            "PreTaxVal": 0,
            "AssAmt": float(item.taxable_amount),
            "GstRt": float(item.gst_percent or 0),
            "IgstAmt": float(item.igst_amount or 0),
            "CgstAmt": float(item.cgst_amount or 0),
            "SgstAmt": float(item.sgst_amount or 0),
            "CesRt": 0,
            "CesAmt": 0,
            "CesNonAdvlAmt": 0,
            "StateCesRt": 0,
            "StateCesAmt": 0,
            "StateCesNonAdvlAmt": 0,
            "OthChrg": 0,
            "TotItemVal": float(item.total_amount)
        }
        item_list.append(item_entry)
    
    # Value Details
    val_dtls = {
        "AssVal": float(invoice.subtotal),
        "CgstVal": float(invoice.cgst_amount or 0),
        "SgstVal": float(invoice.sgst_amount or 0),
        "IgstVal": float(invoice.igst_amount or 0),
        "CesVal": 0,
        "StCesVal": 0,
        "Discount": float(invoice.discount_amount or 0),
        "OthChrg": 0,
        "RndOffAmt": float(invoice.round_off or 0),
        "TotInvVal": float(invoice.total_amount),
        "TotInvValFc": 0
    }
    
    # Payment Details
    pay_dtls = {
        "Nm": party.name,
        "Accdet": None,
        "Mode": invoice.payment_mode,
        "Fininsbr": None,
        "Payterm": None,
        "Payinstr": None,
        "Crtrn": None,
        "Dirdr": None,
        "Crday": 0,
        "Paidamt": float(invoice.amount_paid or 0),
        "Paymtdue": float(invoice.amount_due or 0)
    }
    
    # Complete E-Invoice JSON
    einvoice = {
        "Version": "1.1",
        "TranDtls": tran_dtls,
        "DocDtls": doc_dtls,
        "SellerDtls": seller_dtls,
        "BuyerDtls": buyer_dtls,
        "ItemList": item_list,
        "ValDtls": val_dtls,
        "PayDtls": pay_dtls,
        "EwbDtls": None,  # E-way bill details if applicable
        "RefDtls": None   # Reference details
    }
    
    return einvoice


def _map_unit_code(unit):
    """Map unit to GST unit code"""
    unit_mapping = {
        'PCS': 'PCS',
        'NOS': 'NOS',
        'KG': 'KGS',
        'KGS': 'KGS',
        'GM': 'GMS',
        'GMS': 'GMS',
        'LTR': 'LTR',
        'ML': 'MLT',
        'MTR': 'MTR',
        'CM': 'CMS',
        'BOX': 'BOX',
        'PKT': 'PAC',
        'SET': 'SET',
        'DOZ': 'DOZ',
        'PAIR': 'PRS'
    }
    return unit_mapping.get(unit.upper() if unit else 'PCS', 'OTH')
