"""
Inventory Blueprint
"""
from flask import Blueprint

inventory_bp = Blueprint('inventory', __name__, template_folder='../templates/inventory')

from app.inventory import routes
