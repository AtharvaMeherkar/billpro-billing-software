"""
Financial Year Service
"""
from datetime import date
from app.models.base import db
from app.models.config import FinancialYear


def get_fy_from_date(d=None):
    """
    Get financial year name and code from a date.
    Indian FY: April 1 to March 31
    """
    if d is None:
        d = date.today()
    
    if d.month >= 4:  # April onwards = current year FY
        start_year = d.year
        end_year = d.year + 1
    else:  # Jan-March = previous year FY
        start_year = d.year - 1
        end_year = d.year
    
    fy_name = f"{start_year}-{str(end_year)[-2:]}"  # e.g., "2024-25"
    fy_code = f"{str(start_year)[-2:]}{str(end_year)[-2:]}"  # e.g., "2425"
    fy_start = date(start_year, 4, 1)
    fy_end = date(end_year, 3, 31)
    
    return {
        'name': fy_name,
        'code': fy_code,
        'start_date': fy_start,
        'end_date': fy_end
    }


def get_or_create_current_fy():
    """Get or create the current financial year"""
    fy_info = get_fy_from_date()
    
    fy = FinancialYear.query.filter_by(code=fy_info['code']).first()
    if not fy:
        # Create new FY
        fy = FinancialYear(
            name=fy_info['name'],
            code=fy_info['code'],
            start_date=fy_info['start_date'],
            end_date=fy_info['end_date'],
            is_active=True
        )
        db.session.add(fy)
        
        # Deactivate other FYs
        FinancialYear.query.filter(FinancialYear.code != fy_info['code']).update(
            {'is_active': False}
        )
        
        db.session.commit()
    
    return fy


def get_current_fy():
    """Get the active financial year"""
    fy = FinancialYear.query.filter_by(is_active=True).first()
    if not fy:
        fy = get_or_create_current_fy()
    return fy


def get_all_financial_years():
    """Get all financial years ordered by date"""
    return FinancialYear.query.order_by(FinancialYear.start_date.desc()).all()
