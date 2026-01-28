"""
Accounting Models - Expenses, Journal Entries, Cash/Bank Books
"""
from datetime import datetime
from app.models.base import db


class ExpenseCategory(db.Model):
    """Expense categories"""
    __tablename__ = 'expense_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    expenses = db.relationship('Expense', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<ExpenseCategory {self.name}>'


class Expense(db.Model):
    """Expense register entries"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    
    expense_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'))
    
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # GST on expense (if applicable)
    is_gst_expense = db.Column(db.Boolean, default=False)
    gst_amount = db.Column(db.Numeric(12, 2), default=0)
    
    payment_mode = db.Column(db.String(20), default='CASH')  # CASH, BANK
    
    # Reference
    reference_number = db.Column(db.String(50))
    vendor_name = db.Column(db.String(200))
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Expense {self.description} Rs.{self.amount}>'


class JournalEntry(db.Model):
    """Core accounting journal entries - double entry"""
    __tablename__ = 'journal_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    
    entry_date = db.Column(db.Date, nullable=False)
    entry_number = db.Column(db.String(50))
    
    # Account Info
    account_type = db.Column(db.String(50), nullable=False)  # SALES, PURCHASE, EXPENSE, CASH, BANK, RECEIVABLE, PAYABLE
    account_name = db.Column(db.String(100))
    
    # Party reference (if applicable)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'))
    
    # Amounts
    debit = db.Column(db.Numeric(15, 2), default=0)
    credit = db.Column(db.Numeric(15, 2), default=0)
    
    # Reference to source document
    reference_type = db.Column(db.String(20))  # INVOICE, PURCHASE, EXPENSE, RECEIPT, PAYMENT
    reference_id = db.Column(db.Integer)
    reference_number = db.Column(db.String(50))
    
    narration = db.Column(db.Text)
    
    financial_year_id = db.Column(db.Integer, db.ForeignKey('financial_years.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    party = db.relationship('Party', backref='journal_entries')
    financial_year = db.relationship('FinancialYear', backref='journal_entries')
    
    def __repr__(self):
        return f'<JournalEntry {self.account_type} Dr:{self.debit} Cr:{self.credit}>'


class CashTransaction(db.Model):
    """Cash book entries"""
    __tablename__ = 'cash_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # RECEIPT, PAYMENT
    
    # Party (if applicable)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'))
    
    description = db.Column(db.String(255), nullable=False)
    
    # Amounts
    receipt = db.Column(db.Numeric(15, 2), default=0)  # Cash in
    payment = db.Column(db.Numeric(15, 2), default=0)  # Cash out
    balance = db.Column(db.Numeric(15, 2), default=0)  # Running balance
    
    # Reference
    reference_type = db.Column(db.String(20))
    reference_id = db.Column(db.Integer)
    reference_number = db.Column(db.String(50))
    
    narration = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    party = db.relationship('Party', backref='cash_transactions')
    
    def __repr__(self):
        return f'<CashTransaction {self.transaction_type} {self.receipt or self.payment}>'


class BankTransaction(db.Model):
    """Bank book entries"""
    __tablename__ = 'bank_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # DEPOSIT, WITHDRAWAL
    
    # Party (if applicable)
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'))
    
    description = db.Column(db.String(255), nullable=False)
    
    # Amounts
    deposit = db.Column(db.Numeric(15, 2), default=0)  # Money in
    withdrawal = db.Column(db.Numeric(15, 2), default=0)  # Money out
    balance = db.Column(db.Numeric(15, 2), default=0)  # Running balance
    
    # Bank details
    bank_name = db.Column(db.String(100))
    cheque_number = db.Column(db.String(20))
    
    # Reference
    reference_type = db.Column(db.String(20))
    reference_id = db.Column(db.Integer)
    reference_number = db.Column(db.String(50))
    
    narration = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    party = db.relationship('Party', backref='bank_transactions')
    
    def __repr__(self):
        return f'<BankTransaction {self.transaction_type} {self.deposit or self.withdrawal}>'
