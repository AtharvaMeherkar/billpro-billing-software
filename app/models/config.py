"""
Configuration and Financial Year Models
"""
from datetime import datetime, date
from app.models.base import db


class FinancialYear(db.Model):
    """Financial year management"""
    __tablename__ = 'financial_years'
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(20), unique=True, nullable=False)  # e.g., "2024-25"
    code = db.Column(db.String(4), unique=True, nullable=False)   # e.g., "2425"
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    is_active = db.Column(db.Boolean, default=False)
    is_closed = db.Column(db.Boolean, default=False)
    
    # Counter for invoice numbering
    invoice_counter = db.Column(db.Integer, default=0)
    purchase_counter = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FinancialYear {self.name}>'
    
    @property
    def is_current(self):
        """Check if this is the current financial year"""
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    def get_next_invoice_number(self, prefix='INV'):
        """Generate next invoice number for this FY"""
        self.invoice_counter += 1
        return f"{prefix}/{self.code}/{str(self.invoice_counter).zfill(4)}"
    
    def get_next_purchase_number(self, prefix='PUR'):
        """Generate next purchase number for this FY"""
        self.purchase_counter += 1
        return f"{prefix}/{self.code}/{str(self.purchase_counter).zfill(4)}"


class SystemConfig(db.Model):
    """System-wide configuration key-value store"""
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemConfig {self.key}={self.value}>'
    
    @classmethod
    def get(cls, key, default=None):
        """Get config value by key"""
        config = cls.query.filter_by(key=key).first()
        return config.value if config else default
    
    @classmethod
    def set(cls, key, value, description=None):
        """Set config value"""
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = value
            if description:
                config.description = description
        else:
            config = cls(key=key, value=value, description=description)
            db.session.add(config)
        db.session.commit()
        return config
