"""
Product and Inventory Models
"""
from datetime import datetime
from app.models.base import db


class ProductCategory(db.Model):
    """Product categories for organization"""
    __tablename__ = 'product_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<ProductCategory {self.name}>'


class Product(db.Model):
    """Product master with inventory tracking"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Info
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True)  # SKU/Product code
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    
    # GST Info
    hsn_code = db.Column(db.String(8))  # HSN/SAC code
    gst_percent = db.Column(db.Numeric(5, 2), default=18.00)  # GST percentage
    
    # Pricing
    cost_price = db.Column(db.Numeric(12, 2), default=0)  # Purchase price
    selling_price = db.Column(db.Numeric(12, 2), default=0)  # Selling price
    mrp = db.Column(db.Numeric(12, 2))  # Maximum retail price
    
    # Inventory
    current_stock = db.Column(db.Numeric(12, 3), default=0)  # Current quantity
    low_stock_threshold = db.Column(db.Numeric(12, 3), default=10)  # Alert threshold
    unit = db.Column(db.String(20), default='PCS')  # UOM: PCS, KG, LTR, etc.
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoice_items = db.relationship('InvoiceItem', backref='product', lazy='dynamic')
    purchase_items = db.relationship('PurchaseItem', backref='product', lazy='dynamic')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    @property
    def is_low_stock(self):
        """Check if stock is below threshold"""
        return self.current_stock <= self.low_stock_threshold
    
    @property
    def stock_value(self):
        """Calculate inventory value at cost"""
        return float(self.current_stock or 0) * float(self.cost_price or 0)
    
    def adjust_stock(self, quantity, operation='add'):
        """
        Adjust stock quantity
        operation: 'add' or 'subtract'
        """
        if operation == 'add':
            self.current_stock = float(self.current_stock or 0) + float(quantity)
        elif operation == 'subtract':
            self.current_stock = float(self.current_stock or 0) - float(quantity)
        self.updated_at = datetime.utcnow()


class StockMovement(db.Model):
    """Track all stock movements for audit"""
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    movement_type = db.Column(db.String(20), nullable=False)  # SALE, PURCHASE, ADJUSTMENT
    quantity = db.Column(db.Numeric(12, 3), nullable=False)
    
    # Reference to source document
    reference_type = db.Column(db.String(20))  # INVOICE, PURCHASE, MANUAL
    reference_id = db.Column(db.Integer)
    
    stock_before = db.Column(db.Numeric(12, 3))
    stock_after = db.Column(db.Numeric(12, 3))
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    product = db.relationship('Product', backref='stock_movements')
    
    def __repr__(self):
        return f'<StockMovement {self.movement_type} {self.quantity}>'
