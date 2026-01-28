"""
Ledgers Blueprint - Party Management
"""
from flask import Blueprint

ledgers_bp = Blueprint('ledgers', __name__, template_folder='../templates/ledgers')

from app.ledgers import routes
