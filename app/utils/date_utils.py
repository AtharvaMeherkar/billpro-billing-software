"""
Date utility functions
"""
from datetime import datetime, date, timedelta
from calendar import monthrange


def format_date(d, fmt='%d-%m-%Y'):
    """Format date for display"""
    if isinstance(d, str):
        d = parse_date(d)
    if d:
        return d.strftime(fmt)
    return ''


def parse_date(date_str, fmt='%Y-%m-%d'):
    """Parse date string to date object"""
    if not date_str:
        return None
    if isinstance(date_str, (date, datetime)):
        return date_str if isinstance(date_str, date) else date_str.date()
    try:
        return datetime.strptime(date_str, fmt).date()
    except ValueError:
        # Try alternate formats
        for f in ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y']:
            try:
                return datetime.strptime(date_str, f).date()
            except ValueError:
                continue
    return None


def to_indian_date(d):
    """Convert to Indian date format DD-MM-YYYY"""
    return format_date(d, '%d-%m-%Y')


def get_month_range(year, month):
    """Get start and end date of a month"""
    start = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end = date(year, month, last_day)
    return start, end


def get_fy_date_range(fy_year=None):
    """
    Get financial year date range (April to March)
    fy_year: starting year of FY (e.g., 2024 for FY 2024-25)
    """
    if fy_year is None:
        today = date.today()
        fy_year = today.year if today.month >= 4 else today.year - 1
    
    start = date(fy_year, 4, 1)
    end = date(fy_year + 1, 3, 31)
    return start, end


def get_quarter_range(year, quarter):
    """Get start and end date of a quarter (Q1=Apr-Jun, Q2=Jul-Sep, etc.)"""
    quarters = {
        1: (4, 6),   # Q1: Apr-Jun
        2: (7, 9),   # Q2: Jul-Sep
        3: (10, 12), # Q3: Oct-Dec
        4: (1, 3)    # Q4: Jan-Mar (next year)
    }
    
    start_month, end_month = quarters.get(quarter, (4, 6))
    
    if quarter == 4:
        start = date(year + 1, start_month, 1)
        _, last_day = monthrange(year + 1, end_month)
        end = date(year + 1, end_month, last_day)
    else:
        start = date(year, start_month, 1)
        _, last_day = monthrange(year, end_month)
        end = date(year, end_month, last_day)
    
    return start, end
