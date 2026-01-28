"""
BillPro Flask Application Factory
"""
import os
import json
from flask import Flask, render_template

# Import db from models.base to avoid duplicate SQLAlchemy instances
from app.models.base import db


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    from config.settings import Config
    app.config.from_object(Config)
    
    # Ensure directories exist
    os.makedirs(Config.DATABASE_DIR, exist_ok=True)
    os.makedirs(Config.BILL_TEMPLATES_DIR, exist_ok=True)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from app.billing import billing_bp
    from app.inventory import inventory_bp
    from app.accounting import accounting_bp
    from app.ledgers import ledgers_bp
    from app.einvoice import einvoice_bp
    from app.payroll import payroll_bp
    from app.reports import reports_bp
    from app.printing import printing_bp
    
    app.register_blueprint(billing_bp, url_prefix='/billing')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(accounting_bp, url_prefix='/accounting')
    app.register_blueprint(ledgers_bp, url_prefix='/ledgers')
    app.register_blueprint(einvoice_bp, url_prefix='/einvoice')
    app.register_blueprint(payroll_bp, url_prefix='/payroll')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(printing_bp, url_prefix='/printing')
    
    # Load company config into app context
    @app.context_processor
    def inject_company():
        company = {}
        if os.path.exists(Config.COMPANY_CONFIG):
            with open(Config.COMPANY_CONFIG, 'r') as f:
                company = json.load(f)
        return {'company': company}
    
    # Dashboard route
    @app.route('/')
    def dashboard():
        from app.models import Invoice, Party, Product, Expense
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        month_start = today.replace(day=1)
        
        # Get summary stats
        stats = {
            'total_sales_today': db.session.query(func.sum(Invoice.total_amount)).filter(
                Invoice.invoice_date == today
            ).scalar() or 0,
            'total_sales_month': db.session.query(func.sum(Invoice.total_amount)).filter(
                Invoice.invoice_date >= month_start
            ).scalar() or 0,
            'total_customers': Party.query.filter_by(party_type='customer').count(),
            'total_products': Product.query.count(),
            'low_stock_count': Product.query.filter(
                Product.current_stock <= Product.low_stock_threshold
            ).count(),
            'pending_receivables': db.session.query(func.sum(Party.current_balance)).filter(
                Party.party_type == 'customer',
                Party.current_balance > 0
            ).scalar() or 0,
        }
        
        # Recent invoices
        recent_invoices = Invoice.query.order_by(Invoice.id.desc()).limit(10).all()
        
        return render_template('dashboard.html', stats=stats, recent_invoices=recent_invoices)
    
    # Settings route
    @app.route('/settings', methods=['GET', 'POST'])
    def settings():
        from flask import request, redirect, url_for, flash
        
        if request.method == 'POST':
            company_data = {
                'name': request.form.get('name'),
                'gstin': request.form.get('gstin'),
                'pan': request.form.get('pan'),
                'address': {
                    'line1': request.form.get('address_line1'),
                    'line2': request.form.get('address_line2'),
                    'city': request.form.get('city'),
                    'state': request.form.get('state'),
                    'state_code': request.form.get('state_code'),
                    'pincode': request.form.get('pincode')
                },
                'contact': {
                    'phone': request.form.get('phone'),
                    'email': request.form.get('email')
                },
                'invoice_prefix': request.form.get('invoice_prefix'),
                'invoice_terms': request.form.get('invoice_terms')
            }
            
            with open(Config.COMPANY_CONFIG, 'w') as f:
                json.dump(company_data, f, indent=4)
            
            flash('Settings saved successfully', 'success')
            return redirect(url_for('settings'))
        
        company = {}
        if os.path.exists(Config.COMPANY_CONFIG):
            with open(Config.COMPANY_CONFIG, 'r') as f:
                company = json.load(f)
        
        return render_template('settings.html', company=company)
    
    @app.route('/settings/company', methods=['GET', 'POST'])
    def company_settings():
        from flask import request, redirect, url_for, flash
        
        if request.method == 'POST':
            company_data = {
                'name': request.form.get('name'),
                'gstin': request.form.get('gstin'),
                'pan': request.form.get('pan'),
                'address': {
                    'line1': request.form.get('address_line1'),
                    'line2': request.form.get('address_line2'),
                    'city': request.form.get('city'),
                    'state': request.form.get('state'),
                    'state_code': request.form.get('state_code'),
                    'pincode': request.form.get('pincode')
                },
                'contact': {
                    'phone': request.form.get('phone'),
                    'email': request.form.get('email')
                },
                'bank': {
                    'name': request.form.get('bank_name'),
                    'account_number': request.form.get('account_number'),
                    'ifsc': request.form.get('ifsc'),
                    'branch': request.form.get('branch')
                },
                'invoice_terms': request.form.get('invoice_terms')
            }
            
            with open(Config.COMPANY_CONFIG, 'w') as f:
                json.dump(company_data, f, indent=4)
            
            flash('Company settings saved successfully', 'success')
            return redirect(url_for('company_settings'))
        
        company = {}
        if os.path.exists(Config.COMPANY_CONFIG):
            with open(Config.COMPANY_CONFIG, 'r') as f:
                company = json.load(f)
        
        return render_template('settings/company.html', company=company, state_codes=Config.STATE_CODES)
    
    # Create tables
    with app.app_context():
        from app import models
        db.create_all()
        
        # Create default financial year if not exists
        from app.models import FinancialYear
        from app.services.financial_year import get_or_create_current_fy
        get_or_create_current_fy()
    
    return app
