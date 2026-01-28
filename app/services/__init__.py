"""
Shared Services
"""
from app.services.financial_year import get_or_create_current_fy, get_current_fy
from app.services.tax_calculator import TaxCalculator
from app.services.stock_manager import StockManager
