"""
Sales Invoice Models
"""
from datetime import datetime
from decimal import Decimal
from app.models.base import db


class Invoice(db.Model):
    """Sales invoice header"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Invoice Info
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    due_date = db.Column(db.Date)
    
    # Financial Year
    financial_year_id = db.Column(db.Integer, db.ForeignKey('financial_years.id'))
    
    # Party
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    
    # Invoice Type
    is_gst_invoice = db.Column(db.Boolean, default=True)  # GST or non-GST
    is_igst = db.Column(db.Boolean, default=False)  # Interstate (IGST) or intrastate (CGST+SGST)
    
    # Amounts
    subtotal = db.Column(db.Numeric(15, 2), default=0)  # Before tax
    cgst_amount = db.Column(db.Numeric(15, 2), default=0)
    sgst_amount = db.Column(db.Numeric(15, 2), default=0)
    igst_amount = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)  # Total tax
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    round_off = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)  # Final amount
    
    # Payment
    payment_mode = db.Column(db.String(20), default='CASH')  # CASH, BANK, CREDIT
    payment_status = db.Column(db.String(20), default='PAID')  # PAID, PARTIAL, UNPAID
    amount_paid = db.Column(db.Numeric(15, 2), default=0)
    amount_due = db.Column(db.Numeric(15, 2), default=0)
    
    # Additional Info
    notes = db.Column(db.Text)
    terms = db.Column(db.Text)
    
    # E-Invoice
    einvoice_generated = db.Column(db.Boolean, default=False)
    einvoice_json_path = db.Column(db.String(255))
    
    # Status
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, CANCELLED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', lazy='dynamic',
                           cascade='all, delete-orphan')
    financial_year = db.relationship('FinancialYear', backref='invoices')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    def calculate_totals(self):
        """Recalculate all totals from items"""
        subtotal = Decimal('0')
        cgst = Decimal('0')
        sgst = Decimal('0')
        igst = Decimal('0')
        
        for item in self.items:
            subtotal += Decimal(str(item.taxable_amount or 0))
            cgst += Decimal(str(item.cgst_amount or 0))
            sgst += Decimal(str(item.sgst_amount or 0))
            igst += Decimal(str(item.igst_amount or 0))
        
        self.subtotal = subtotal
        self.cgst_amount = cgst
        self.sgst_amount = sgst
        self.igst_amount = igst
        self.tax_amount = cgst + sgst + igst
        
        total = subtotal + self.tax_amount - Decimal(str(self.discount_amount or 0))
        
        # Round off
        rounded_total = round(total)
        self.round_off = Decimal(str(rounded_total)) - total
        self.total_amount = rounded_total
        
        # Update payment status
        if self.payment_mode == 'CREDIT':
            self.payment_status = 'UNPAID'
            self.amount_paid = 0
            self.amount_due = self.total_amount
        else:
            self.payment_status = 'PAID'
            self.amount_paid = self.total_amount
            self.amount_due = 0


class InvoiceItem(db.Model):
    """Sales invoice line items"""
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Item Details
    description = db.Column(db.String(255))  # Override product name if needed
    hsn_code = db.Column(db.String(8))
    
    # Quantity & Rate
    quantity = db.Column(db.Numeric(12, 3), nullable=False)
    unit = db.Column(db.String(20))
    rate = db.Column(db.Numeric(12, 2), nullable=False)  # Unit price
    
    # Discount
    discount_percent = db.Column(db.Numeric(5, 2), default=0)
    discount_amount = db.Column(db.Numeric(12, 2), default=0)
    
    # Tax calculations
    taxable_amount = db.Column(db.Numeric(15, 2), default=0)  # After discount
    gst_percent = db.Column(db.Numeric(5, 2), default=0)
    cgst_percent = db.Column(db.Numeric(5, 2), default=0)
    cgst_amount = db.Column(db.Numeric(12, 2), default=0)
    sgst_percent = db.Column(db.Numeric(5, 2), default=0)
    sgst_amount = db.Column(db.Numeric(12, 2), default=0)
    igst_percent = db.Column(db.Numeric(5, 2), default=0)
    igst_amount = db.Column(db.Numeric(12, 2), default=0)
    
    # Total
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    
    def __repr__(self):
        return f'<InvoiceItem {self.product_id} x {self.quantity}>'
    
    def calculate_tax(self, is_igst=False):
        """Calculate tax amounts based on taxable amount and GST rate"""
        taxable = Decimal(str(self.taxable_amount or 0))
        gst_rate = Decimal(str(self.gst_percent or 0))
        
        if is_igst:
            # Interstate - full IGST
            self.igst_percent = gst_rate
            self.igst_amount = (taxable * gst_rate / 100).quantize(Decimal('0.01'))
            self.cgst_percent = 0
            self.cgst_amount = 0
            self.sgst_percent = 0
            self.sgst_amount = 0
        else:
            # Intrastate - split CGST + SGST
            half_rate = gst_rate / 2
            self.cgst_percent = half_rate
            self.cgst_amount = (taxable * half_rate / 100).quantize(Decimal('0.01'))
            self.sgst_percent = half_rate
            self.sgst_amount = (taxable * half_rate / 100).quantize(Decimal('0.01'))
            self.igst_percent = 0
            self.igst_amount = 0
        
        self.total_amount = taxable + self.cgst_amount + self.sgst_amount + self.igst_amount
