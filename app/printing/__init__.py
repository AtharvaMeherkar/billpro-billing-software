"""
Printing Blueprint - Thermal Printer Support
"""
from flask import Blueprint

printing_bp = Blueprint('printing', __name__, template_folder='../templates/printing')

from app.printing import routes
