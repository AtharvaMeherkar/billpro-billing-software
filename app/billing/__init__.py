"""
Billing Blueprint - Sales Invoices
"""
from flask import Blueprint

billing_bp = Blueprint('billing', __name__, template_folder='../templates/billing')

from app.billing import routes
