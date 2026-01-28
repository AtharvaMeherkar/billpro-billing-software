"""
Party (Customer/Supplier) Models
"""
from datetime import datetime
from app.models.base import db


class Party(db.Model):
    """Customer and Supplier master"""
    __tablename__ = 'parties'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Info
    name = db.Column(db.String(200), nullable=False)
    party_type = db.Column(db.String(20), nullable=False)  # customer, supplier
    code = db.Column(db.String(50), unique=True)  # Party code
    
    # GST Info
    gstin = db.Column(db.String(15))  # GSTIN number
    pan = db.Column(db.String(10))
    
    # Contact
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    
    # Address
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    state_code = db.Column(db.String(2))  # GST state code
    pincode = db.Column(db.String(10))
    
    # Financial
    opening_balance = db.Column(db.Numeric(15, 2), default=0)  # Opening balance
    current_balance = db.Column(db.Numeric(15, 2), default=0)  # Running balance
    credit_limit = db.Column(db.Numeric(15, 2), default=0)
    credit_days = db.Column(db.Integer, default=30)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoices = db.relationship('Invoice', backref='party', lazy='dynamic')
    purchases = db.relationship('Purchase', backref='party', lazy='dynamic')
    transactions = db.relationship('PartyTransaction', backref='party', lazy='dynamic',
                                   order_by='PartyTransaction.transaction_date.desc()')
    
    def __repr__(self):
        return f'<Party {self.name} ({self.party_type})>'
    
    @property
    def full_address(self):
        """Get formatted full address"""
        parts = [self.address_line1, self.address_line2, self.city, 
                 self.state, self.pincode]
        return ', '.join([p for p in parts if p])
    
    @property
    def state_code_from_gstin(self):
        """Extract state code from GSTIN"""
        if self.gstin and len(self.gstin) >= 2:
            return self.gstin[:2]
        return self.state_code
    
    def update_balance(self, amount, transaction_type):
        """
        Update running balance
        transaction_type: 'debit' or 'credit'
        For customers: Sale = Debit (increases balance), Receipt = Credit (decreases)
        For suppliers: Purchase = Credit (increases balance), Payment = Debit (decreases)
        """
        amount = float(amount)
        if transaction_type == 'debit':
            self.current_balance = float(self.current_balance or 0) + amount
        elif transaction_type == 'credit':
            self.current_balance = float(self.current_balance or 0) - amount
        self.updated_at = datetime.utcnow()


class PartyTransaction(db.Model):
    """Ledger entries for parties"""
    __tablename__ = 'party_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # SALE, PURCHASE, RECEIPT, PAYMENT, OPENING
    
    # Reference to source document
    reference_type = db.Column(db.String(20))  # INVOICE, PURCHASE, RECEIPT, PAYMENT
    reference_id = db.Column(db.Integer)
    reference_number = db.Column(db.String(50))
    
    # Amounts
    debit = db.Column(db.Numeric(15, 2), default=0)
    credit = db.Column(db.Numeric(15, 2), default=0)
    balance = db.Column(db.Numeric(15, 2), default=0)  # Running balance after this transaction
    
    narration = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PartyTransaction {self.transaction_type} Dr:{self.debit} Cr:{self.credit}>'
