"""
E-Invoice Blueprint
"""
from flask import Blueprint

einvoice_bp = Blueprint('einvoice', __name__, template_folder='../templates/einvoice')

from app.einvoice import routes
