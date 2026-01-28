"""
Payroll Blueprint
"""
from flask import Blueprint

payroll_bp = Blueprint('payroll', __name__, template_folder='../templates/payroll')

from app.payroll import routes
