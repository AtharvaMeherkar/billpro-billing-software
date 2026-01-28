"""
Inventory Routes - Product and Stock Management
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from decimal import Decimal

from app.inventory import inventory_bp
from app.models.base import db
from app.models.product import Product, ProductCategory, StockMovement
from app.services.stock_manager import StockManager
from config.settings import Config


@inventory_bp.route('/')
def index():
    """List all products"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category')
    show_inactive = request.args.get('inactive') == '1'
    low_stock_only = request.args.get('low_stock') == '1'
    
    query = Product.query
    
    if not show_inactive:
        query = query.filter_by(is_active=True)
    
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.code.ilike(f'%{search}%'),
                Product.hsn_code.ilike(f'%{search}%')
            )
        )
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if low_stock_only:
        query = query.filter(Product.current_stock <= Product.low_stock_threshold)
    
    products = query.order_by(Product.name).paginate(page=page, per_page=25)
    categories = ProductCategory.query.order_by(ProductCategory.name).all()
    
    # Summary stats
    total_products = Product.query.filter_by(is_active=True).count()
    low_stock_count = Product.query.filter(
        Product.is_active == True,
        Product.current_stock <= Product.low_stock_threshold
    ).count()
    inventory_value = StockManager.get_inventory_value()
    
    return render_template('inventory/index.html',
                          products=products,
                          categories=categories,
                          total_products=total_products,
                          low_stock_count=low_stock_count,
                          inventory_value=inventory_value,
                          gst_rates=Config.DEFAULT_GST_RATES)


@inventory_bp.route('/add', methods=['GET', 'POST'])
def add():
    """Add new product"""
    if request.method == 'POST':
        try:
            product = Product(
                name=request.form.get('name'),
                code=request.form.get('code') or None,
                description=request.form.get('description'),
                category_id=request.form.get('category_id') or None,
                hsn_code=request.form.get('hsn_code'),
                gst_percent=Decimal(request.form.get('gst_percent', '18')),
                cost_price=Decimal(request.form.get('cost_price', '0')),
                selling_price=Decimal(request.form.get('selling_price', '0')),
                mrp=Decimal(request.form.get('mrp', '0')) or None,
                current_stock=Decimal(request.form.get('opening_stock', '0')),
                low_stock_threshold=Decimal(request.form.get('low_stock_threshold', '10')),
                unit=request.form.get('unit', 'PCS')
            )
            
            db.session.add(product)
            db.session.commit()
            
            # Create opening stock movement
            if product.current_stock > 0:
                movement = StockMovement(
                    product_id=product.id,
                    movement_type='ADJUSTMENT',
                    quantity=product.current_stock,
                    reference_type='OPENING',
                    stock_before=0,
                    stock_after=product.current_stock,
                    notes='Opening stock'
                )
                db.session.add(movement)
                db.session.commit()
            
            flash(f'Product "{product.name}" added successfully', 'success')
            return redirect(url_for('inventory.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'error')
    
    categories = ProductCategory.query.order_by(ProductCategory.name).all()
    return render_template('inventory/add.html', 
                          categories=categories,
                          gst_rates=Config.DEFAULT_GST_RATES)


@inventory_bp.route('/<int:id>')
def view(id):
    """View product details"""
    product = Product.query.get_or_404(id)
    movements = StockManager.get_stock_movements(id, limit=20)
    
    return render_template('inventory/view.html', product=product, movements=movements)


@inventory_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit product"""
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            product.name = request.form.get('name')
            product.code = request.form.get('code') or None
            product.description = request.form.get('description')
            product.category_id = request.form.get('category_id') or None
            product.hsn_code = request.form.get('hsn_code')
            product.gst_percent = Decimal(request.form.get('gst_percent', '18'))
            product.cost_price = Decimal(request.form.get('cost_price', '0'))
            product.selling_price = Decimal(request.form.get('selling_price', '0'))
            product.mrp = Decimal(request.form.get('mrp', '0')) or None
            product.low_stock_threshold = Decimal(request.form.get('low_stock_threshold', '10'))
            product.unit = request.form.get('unit', 'PCS')
            product.is_active = request.form.get('is_active') == 'on'
            
            db.session.commit()
            
            flash('Product updated successfully', 'success')
            return redirect(url_for('inventory.view', id=id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'error')
    
    categories = ProductCategory.query.order_by(ProductCategory.name).all()
    return render_template('inventory/edit.html', 
                          product=product,
                          categories=categories,
                          gst_rates=Config.DEFAULT_GST_RATES)


@inventory_bp.route('/<int:id>/adjust-stock', methods=['POST'])
def adjust_stock(id):
    """Adjust stock quantity"""
    product = Product.query.get_or_404(id)
    
    try:
        new_stock = Decimal(request.form.get('new_stock', '0'))
        reason = request.form.get('reason', 'Manual adjustment')
        
        StockManager.adjust_stock(product.id, new_stock, notes=reason)
        
        flash(f'Stock adjusted to {new_stock} {product.unit}', 'success')
    except Exception as e:
        flash(f'Error adjusting stock: {str(e)}', 'error')
    
    return redirect(url_for('inventory.view', id=id))


@inventory_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete product (mark inactive)"""
    product = Product.query.get_or_404(id)
    product.is_active = False
    db.session.commit()
    
    flash(f'Product "{product.name}" deleted', 'success')
    return redirect(url_for('inventory.index'))


# Categories
@inventory_bp.route('/categories')
def categories():
    """List categories"""
    cats = ProductCategory.query.order_by(ProductCategory.name).all()
    return render_template('inventory/categories.html', categories=cats)


@inventory_bp.route('/categories/add', methods=['POST'])
def add_category():
    """Add category"""
    name = request.form.get('name')
    if name:
        cat = ProductCategory(name=name, description=request.form.get('description'))
        db.session.add(cat)
        db.session.commit()
        flash(f'Category "{name}" added', 'success')
    return redirect(url_for('inventory.categories'))


@inventory_bp.route('/categories/<int:id>/delete', methods=['POST'])
def delete_category(id):
    """Delete category"""
    cat = ProductCategory.query.get_or_404(id)
    # Check for products
    if cat.products.count() > 0:
        flash('Cannot delete category with products', 'error')
    else:
        db.session.delete(cat)
        db.session.commit()
        flash('Category deleted', 'success')
    return redirect(url_for('inventory.categories'))


# Low stock report
@inventory_bp.route('/low-stock')
def low_stock():
    """Low stock report"""
    products = StockManager.get_low_stock_products()
    return render_template('inventory/low_stock.html', products=products)


# Stock valuation report
@inventory_bp.route('/valuation')
def valuation():
    """Stock valuation report"""
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    
    total_value = Decimal('0')
    items = []
    for p in products:
        value = Decimal(str(p.current_stock or 0)) * Decimal(str(p.cost_price or 0))
        items.append({
            'product': p,
            'value': value
        })
        total_value += value
    
    return render_template('inventory/valuation.html', items=items, total_value=total_value)


# API
@inventory_bp.route('/api/search')
def api_search():
    """Search products for autocomplete"""
    q = request.args.get('q', '')
    products = Product.query.filter(
        Product.is_active == True,
        db.or_(
            Product.name.ilike(f'%{q}%'),
            Product.code.ilike(f'%{q}%')
        )
    ).limit(20).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'code': p.code,
        'hsn_code': p.hsn_code,
        'gst_percent': float(p.gst_percent or 0),
        'selling_price': float(p.selling_price or 0),
        'unit': p.unit,
        'stock': float(p.current_stock or 0)
    } for p in products])
