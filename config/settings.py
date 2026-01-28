"""
BillPro Configuration Settings
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    """Application configuration"""
    
    # Base directory
    BASE_DIR = BASE_DIR
    
    # Database
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'billpro.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application
    SECRET_KEY = 'billpro-local-key-change-in-production'
    DEBUG = True
    
    # Paths
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')
    BILL_TEMPLATES_DIR = os.path.join(BASE_DIR, 'bill_templates')
    DATABASE_DIR = os.path.join(BASE_DIR, 'database')
    
    # Company config file
    COMPANY_CONFIG = os.path.join(CONFIG_DIR, 'company.json')
    PRINTER_CONFIG = os.path.join(CONFIG_DIR, 'printer.json')
    
    # Financial Year (Indian: April to March)
    FY_START_MONTH = 4  # April
    FY_START_DAY = 1
    
    # Invoice prefix
    INVOICE_PREFIX = 'INV'
    PURCHASE_PREFIX = 'PUR'
    
    # Default GST rates
    DEFAULT_GST_RATES = [0, 5, 12, 18, 28]
    
    # State codes for GST
    STATE_CODES = {
        '01': 'Jammu & Kashmir',
        '02': 'Himachal Pradesh',
        '03': 'Punjab',
        '04': 'Chandigarh',
        '05': 'Uttarakhand',
        '06': 'Haryana',
        '07': 'Delhi',
        '08': 'Rajasthan',
        '09': 'Uttar Pradesh',
        '10': 'Bihar',
        '11': 'Sikkim',
        '12': 'Arunachal Pradesh',
        '13': 'Nagaland',
        '14': 'Manipur',
        '15': 'Mizoram',
        '16': 'Tripura',
        '17': 'Meghalaya',
        '18': 'Assam',
        '19': 'West Bengal',
        '20': 'Jharkhand',
        '21': 'Odisha',
        '22': 'Chhattisgarh',
        '23': 'Madhya Pradesh',
        '24': 'Gujarat',
        '26': 'Dadra & Nagar Haveli and Daman & Diu',
        '27': 'Maharashtra',
        '29': 'Karnataka',
        '30': 'Goa',
        '31': 'Lakshadweep',
        '32': 'Kerala',
        '33': 'Tamil Nadu',
        '34': 'Puducherry',
        '35': 'Andaman & Nicobar Islands',
        '36': 'Telangana',
        '37': 'Andhra Pradesh',
        '38': 'Ladakh',
    }
