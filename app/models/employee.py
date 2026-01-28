"""
Employee and Payroll Models
"""
from datetime import datetime
from decimal import Decimal
from app.models.base import db


class Employee(db.Model):
    """Employee master"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Info
    employee_code = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(200), nullable=False)
    
    # Contact
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    
    # Employment Info
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    date_of_joining = db.Column(db.Date)
    date_of_leaving = db.Column(db.Date)
    
    # Bank Details
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(20))
    ifsc_code = db.Column(db.String(15))
    
    # Salary Components
    basic_salary = db.Column(db.Numeric(12, 2), default=0)
    hra = db.Column(db.Numeric(12, 2), default=0)  # House Rent Allowance
    da = db.Column(db.Numeric(12, 2), default=0)   # Dearness Allowance
    other_allowances = db.Column(db.Numeric(12, 2), default=0)
    
    # Deductions
    pf_deduction = db.Column(db.Numeric(12, 2), default=0)  # Provident Fund
    esi_deduction = db.Column(db.Numeric(12, 2), default=0)  # ESI
    other_deductions = db.Column(db.Numeric(12, 2), default=0)
    
    # ID Documents
    pan = db.Column(db.String(10))
    aadhar = db.Column(db.String(12))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    salary_slips = db.relationship('SalarySlip', backref='employee', lazy='dynamic')
    
    def __repr__(self):
        return f'<Employee {self.name}>'
    
    @property
    def gross_salary(self):
        """Calculate gross salary"""
        return (
            float(self.basic_salary or 0) +
            float(self.hra or 0) +
            float(self.da or 0) +
            float(self.other_allowances or 0)
        )
    
    @property
    def total_deductions(self):
        """Calculate total deductions"""
        return (
            float(self.pf_deduction or 0) +
            float(self.esi_deduction or 0) +
            float(self.other_deductions or 0)
        )
    
    @property
    def net_salary(self):
        """Calculate net salary"""
        return self.gross_salary - self.total_deductions


class SalarySlip(db.Model):
    """Monthly salary slips"""
    __tablename__ = 'salary_slips'
    
    id = db.Column(db.Integer, primary_key=True)
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Period
    salary_month = db.Column(db.Integer, nullable=False)  # 1-12
    salary_year = db.Column(db.Integer, nullable=False)
    
    # Working Days
    total_working_days = db.Column(db.Integer, default=30)
    days_worked = db.Column(db.Integer, default=30)
    days_absent = db.Column(db.Integer, default=0)
    
    # Earnings
    basic_salary = db.Column(db.Numeric(12, 2), default=0)
    hra = db.Column(db.Numeric(12, 2), default=0)
    da = db.Column(db.Numeric(12, 2), default=0)
    other_allowances = db.Column(db.Numeric(12, 2), default=0)
    overtime = db.Column(db.Numeric(12, 2), default=0)
    bonus = db.Column(db.Numeric(12, 2), default=0)
    gross_salary = db.Column(db.Numeric(12, 2), default=0)
    
    # Deductions
    pf_deduction = db.Column(db.Numeric(12, 2), default=0)
    esi_deduction = db.Column(db.Numeric(12, 2), default=0)
    tds = db.Column(db.Numeric(12, 2), default=0)
    loan_deduction = db.Column(db.Numeric(12, 2), default=0)
    other_deductions = db.Column(db.Numeric(12, 2), default=0)
    absent_deduction = db.Column(db.Numeric(12, 2), default=0)
    total_deductions = db.Column(db.Numeric(12, 2), default=0)
    
    # Net
    net_salary = db.Column(db.Numeric(12, 2), default=0)
    
    # Payment
    payment_date = db.Column(db.Date)
    payment_mode = db.Column(db.String(20))  # CASH, BANK
    payment_reference = db.Column(db.String(50))
    is_paid = db.Column(db.Boolean, default=False)
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SalarySlip {self.employee.name} {self.salary_month}/{self.salary_year}>'
    
    def calculate_salary(self):
        """Calculate salary from employee master and attendance"""
        emp = self.employee
        
        # Fallback to query if relationship not loaded
        if emp is None:
            emp = Employee.query.get(self.employee_id)
        
        if emp is None:
            return
        
        # Calculate day rate
        day_rate = float(emp.gross_salary) / self.total_working_days
        
        # Prorated amounts based on days worked
        ratio = self.days_worked / self.total_working_days
        
        self.basic_salary = Decimal(str(float(emp.basic_salary or 0) * ratio))
        self.hra = Decimal(str(float(emp.hra or 0) * ratio))
        self.da = Decimal(str(float(emp.da or 0) * ratio))
        self.other_allowances = Decimal(str(float(emp.other_allowances or 0) * ratio))
        
        self.gross_salary = self.basic_salary + self.hra + self.da + self.other_allowances + \
                           Decimal(str(self.overtime or 0)) + Decimal(str(self.bonus or 0))
        
        # Deductions
        self.pf_deduction = Decimal(str(float(emp.pf_deduction or 0) * ratio))
        self.esi_deduction = Decimal(str(float(emp.esi_deduction or 0) * ratio))
        self.other_deductions = Decimal(str(self.loan_deduction or 0)) + \
                               Decimal(str(emp.other_deductions or 0))
        
        # Absent deduction
        self.absent_deduction = Decimal(str(self.days_absent * day_rate))
        
        self.total_deductions = (self.pf_deduction + self.esi_deduction + 
                                Decimal(str(self.tds or 0)) + self.other_deductions +
                                self.absent_deduction)
        
        self.net_salary = self.gross_salary - self.total_deductions
