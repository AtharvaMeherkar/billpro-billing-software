"""
Payroll Routes - Employee and Salary Management
"""
from flask import render_template, request, redirect, url_for, flash
from datetime import date, datetime
from decimal import Decimal

from app.payroll import payroll_bp
from app.models.base import db
from app.models.employee import Employee, SalarySlip
from app.models.accounting import Expense, CashTransaction, BankTransaction


@payroll_bp.route('/')
def index():
    """Employee list"""
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
    
    # This month's payroll summary
    today = date.today()
    month_slips = SalarySlip.query.filter_by(
        salary_month=today.month,
        salary_year=today.year
    ).all()
    
    total_processed = len(month_slips)
    total_paid = sum(1 for s in month_slips if s.is_paid)
    total_salary = sum(float(s.net_salary or 0) for s in month_slips)
    
    return render_template('payroll/index.html',
                          employees=employees,
                          total_processed=total_processed,
                          total_paid=total_paid,
                          total_salary=total_salary,
                          current_month=today.strftime('%B %Y'))


@payroll_bp.route('/employees/add', methods=['GET', 'POST'])
def add_employee():
    """Add new employee"""
    if request.method == 'POST':
        try:
            emp = Employee(
                employee_code=request.form.get('employee_code') or None,
                name=request.form.get('name'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address=request.form.get('address'),
                designation=request.form.get('designation'),
                department=request.form.get('department'),
                date_of_joining=datetime.strptime(request.form.get('date_of_joining'), '%Y-%m-%d').date() if request.form.get('date_of_joining') else None,
                bank_name=request.form.get('bank_name'),
                bank_account=request.form.get('bank_account'),
                ifsc_code=request.form.get('ifsc_code'),
                basic_salary=Decimal(request.form.get('basic_salary', '0')),
                hra=Decimal(request.form.get('hra', '0')),
                da=Decimal(request.form.get('da', '0')),
                other_allowances=Decimal(request.form.get('other_allowances', '0')),
                pf_deduction=Decimal(request.form.get('pf_deduction', '0')),
                esi_deduction=Decimal(request.form.get('esi_deduction', '0')),
                other_deductions=Decimal(request.form.get('other_deductions', '0')),
                pan=request.form.get('pan'),
                aadhar=request.form.get('aadhar')
            )
            
            db.session.add(emp)
            db.session.commit()
            
            flash(f'Employee "{emp.name}" added successfully', 'success')
            return redirect(url_for('payroll.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding employee: {str(e)}', 'error')
    
    return render_template('payroll/add_employee.html')


@payroll_bp.route('/employees/<int:id>')
def view_employee(id):
    """View employee details"""
    employee = Employee.query.get_or_404(id)
    salary_slips = SalarySlip.query.filter_by(employee_id=id)\
        .order_by(SalarySlip.salary_year.desc(), SalarySlip.salary_month.desc())\
        .limit(12).all()
    
    return render_template('payroll/view_employee.html', 
                          employee=employee, 
                          salary_slips=salary_slips)


@payroll_bp.route('/employees/<int:id>/edit', methods=['GET', 'POST'])
def edit_employee(id):
    """Edit employee"""
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            employee.employee_code = request.form.get('employee_code') or None
            employee.name = request.form.get('name')
            employee.phone = request.form.get('phone')
            employee.email = request.form.get('email')
            employee.address = request.form.get('address')
            employee.designation = request.form.get('designation')
            employee.department = request.form.get('department')
            employee.bank_name = request.form.get('bank_name')
            employee.bank_account = request.form.get('bank_account')
            employee.ifsc_code = request.form.get('ifsc_code')
            employee.basic_salary = Decimal(request.form.get('basic_salary', '0'))
            employee.hra = Decimal(request.form.get('hra', '0'))
            employee.da = Decimal(request.form.get('da', '0'))
            employee.other_allowances = Decimal(request.form.get('other_allowances', '0'))
            employee.pf_deduction = Decimal(request.form.get('pf_deduction', '0'))
            employee.esi_deduction = Decimal(request.form.get('esi_deduction', '0'))
            employee.other_deductions = Decimal(request.form.get('other_deductions', '0'))
            employee.pan = request.form.get('pan')
            employee.aadhar = request.form.get('aadhar')
            employee.is_active = request.form.get('is_active') == 'on'
            
            db.session.commit()
            
            flash('Employee updated successfully', 'success')
            return redirect(url_for('payroll.view_employee', id=id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating employee: {str(e)}', 'error')
    
    return render_template('payroll/edit_employee.html', employee=employee)


@payroll_bp.route('/process', methods=['GET', 'POST'])
def process_payroll():
    """Process monthly payroll"""
    today = date.today()
    
    if request.method == 'POST':
        month = int(request.form.get('month', today.month))
        year = int(request.form.get('year', today.year))
        total_days = int(request.form.get('total_days', 30))
        
        employees = Employee.query.filter_by(is_active=True).all()
        processed = 0
        
        for emp in employees:
            # Check if already processed
            existing = SalarySlip.query.filter_by(
                employee_id=emp.id,
                salary_month=month,
                salary_year=year
            ).first()
            
            if existing:
                continue
            
            days_worked = int(request.form.get(f'days_{emp.id}', total_days))
            bonus = Decimal(request.form.get(f'bonus_{emp.id}', '0'))
            loan_deduction = Decimal(request.form.get(f'loan_{emp.id}', '0'))
            
            slip = SalarySlip(
                employee_id=emp.id,
                salary_month=month,
                salary_year=year,
                total_working_days=total_days,
                days_worked=days_worked,
                days_absent=total_days - days_worked,
                bonus=bonus,
                loan_deduction=loan_deduction
            )
            
            slip.calculate_salary()
            db.session.add(slip)
            processed += 1
        
        db.session.commit()
        flash(f'Payroll processed for {processed} employees', 'success')
        return redirect(url_for('payroll.salary_slips', month=month, year=year))
    
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
    
    return render_template('payroll/process.html',
                          employees=employees,
                          current_month=today.month,
                          current_year=today.year)


@payroll_bp.route('/salary-slips')
def salary_slips():
    """View salary slips"""
    today = date.today()
    month = request.args.get('month', today.month, type=int)
    year = request.args.get('year', today.year, type=int)
    
    slips = SalarySlip.query.filter_by(salary_month=month, salary_year=year)\
        .order_by(SalarySlip.id).all()
    
    total_payable = sum(float(s.net_salary or 0) for s in slips if not s.is_paid)
    total_paid = sum(float(s.net_salary or 0) for s in slips if s.is_paid)
    
    return render_template('payroll/salary_slips.html',
                          slips=slips,
                          month=month,
                          year=year,
                          total_payable=total_payable,
                          total_paid=total_paid)


@payroll_bp.route('/salary-slips/<int:id>')
def view_salary_slip(id):
    """View individual salary slip"""
    slip = SalarySlip.query.get_or_404(id)
    return render_template('payroll/view_salary_slip.html', slip=slip)


@payroll_bp.route('/salary-slips/<int:id>/print')
def print_salary_slip(id):
    """Print salary slip"""
    slip = SalarySlip.query.get_or_404(id)
    
    import json
    import os
    from config.settings import Config
    
    company = {}
    if os.path.exists(Config.COMPANY_CONFIG):
        with open(Config.COMPANY_CONFIG, 'r') as f:
            company = json.load(f)
    
    return render_template('payroll/print_salary_slip.html', slip=slip, company=company)


@payroll_bp.route('/salary-slips/<int:id>/pay', methods=['POST'])
def pay_salary(id):
    """Mark salary as paid"""
    slip = SalarySlip.query.get_or_404(id)
    
    if slip.is_paid:
        flash('Salary already paid', 'warning')
        return redirect(url_for('payroll.view_salary_slip', id=id))
    
    try:
        payment_mode = request.form.get('payment_mode', 'BANK')
        reference = request.form.get('reference', '')
        
        slip.is_paid = True
        slip.payment_date = date.today()
        slip.payment_mode = payment_mode
        slip.payment_reference = reference
        
        # Create expense entry
        expense = Expense(
            expense_date=date.today(),
            description=f'Salary - {slip.employee.name} ({slip.salary_month}/{slip.salary_year})',
            amount=slip.net_salary,
            payment_mode=payment_mode,
            reference_number=reference,
            vendor_name=slip.employee.name
        )
        db.session.add(expense)
        
        # Create cash/bank entry
        if payment_mode == 'CASH':
            cash = CashTransaction(
                transaction_date=date.today(),
                transaction_type='PAYMENT',
                description=f'Salary payment - {slip.employee.name}',
                payment=slip.net_salary,
                reference_type='SALARY',
                reference_id=slip.id
            )
            db.session.add(cash)
        else:
            bank = BankTransaction(
                transaction_date=date.today(),
                transaction_type='WITHDRAWAL',
                description=f'Salary payment - {slip.employee.name}',
                withdrawal=slip.net_salary,
                reference_type='SALARY',
                reference_id=slip.id
            )
            db.session.add(bank)
        
        db.session.commit()
        
        flash(f'Salary of ₹{slip.net_salary} paid to {slip.employee.name}', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing payment: {str(e)}', 'error')
    
    return redirect(url_for('payroll.view_salary_slip', id=id))
