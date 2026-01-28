"""
Accounting Blueprint
"""
from flask import Blueprint

accounting_bp = Blueprint('accounting', __name__, template_folder='../templates/accounting')

from app.accounting import routes
