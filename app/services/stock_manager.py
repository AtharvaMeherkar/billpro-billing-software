"""
Stock Manager Service
Handles inventory stock operations
"""
from datetime import datetime
from decimal import Decimal
from app.models.base import db
from app.models.product import Product, StockMovement


class StockManager:
    """Inventory stock management service"""
    
    @staticmethod
    def add_stock(product_id, quantity, reference_type=None, reference_id=None, notes=None):
        """
        Add stock to a product (purchase, adjustment)
        """
        product = Product.query.get(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        quantity = Decimal(str(quantity))
        stock_before = Decimal(str(product.current_stock or 0))
        stock_after = stock_before + quantity
        
        # Update product stock
        product.current_stock = stock_after
        product.updated_at = datetime.utcnow()
        
        # Create stock movement record
        movement = StockMovement(
            product_id=product_id,
            movement_type='PURCHASE' if reference_type == 'PURCHASE' else 'ADJUSTMENT',
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            stock_before=stock_before,
            stock_after=stock_after,
            notes=notes
        )
        db.session.add(movement)
        db.session.commit()
        
        return stock_after
    
    @staticmethod
    def deduct_stock(product_id, quantity, reference_type=None, reference_id=None, notes=None):
        """
        Deduct stock from a product (sale, adjustment)
        """
        product = Product.query.get(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        quantity = Decimal(str(quantity))
        stock_before = Decimal(str(product.current_stock or 0))
        stock_after = stock_before - quantity
        
        # Allow negative stock (backorder) but log warning
        if stock_after < 0:
            notes = (notes or '') + ' [WARNING: Stock went negative]'
        
        # Update product stock
        product.current_stock = stock_after
        product.updated_at = datetime.utcnow()
        
        # Create stock movement record
        movement = StockMovement(
            product_id=product_id,
            movement_type='SALE' if reference_type == 'INVOICE' else 'ADJUSTMENT',
            quantity=-quantity,  # Negative for outward
            reference_type=reference_type,
            reference_id=reference_id,
            stock_before=stock_before,
            stock_after=stock_after,
            notes=notes
        )
        db.session.add(movement)
        db.session.commit()
        
        return stock_after
    
    @staticmethod
    def adjust_stock(product_id, new_quantity, notes=None):
        """
        Set stock to a specific quantity (for adjustments/corrections)
        """
        product = Product.query.get(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        new_quantity = Decimal(str(new_quantity))
        stock_before = Decimal(str(product.current_stock or 0))
        adjustment = new_quantity - stock_before
        
        product.current_stock = new_quantity
        product.updated_at = datetime.utcnow()
        
        movement = StockMovement(
            product_id=product_id,
            movement_type='ADJUSTMENT',
            quantity=adjustment,
            reference_type='MANUAL',
            stock_before=stock_before,
            stock_after=new_quantity,
            notes=notes or 'Manual stock adjustment'
        )
        db.session.add(movement)
        db.session.commit()
        
        return new_quantity
    
    @staticmethod
    def get_stock_movements(product_id, limit=50):
        """Get stock movement history for a product"""
        return StockMovement.query.filter_by(product_id=product_id)\
            .order_by(StockMovement.created_at.desc())\
            .limit(limit).all()
    
    @staticmethod
    def get_low_stock_products():
        """Get all products with stock below threshold"""
        return Product.query.filter(
            Product.is_active == True,
            Product.current_stock <= Product.low_stock_threshold
        ).all()
    
    @staticmethod
    def get_inventory_value():
        """Calculate total inventory value at cost price"""
        products = Product.query.filter_by(is_active=True).all()
        total = Decimal('0')
        for p in products:
            total += Decimal(str(p.current_stock or 0)) * Decimal(str(p.cost_price or 0))
        return total
