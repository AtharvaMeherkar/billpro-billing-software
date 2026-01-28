"""
Accounting Routes - Registers, Books, Summaries
"""
from flask import render_template, request, redirect, url_for, flash
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import func

from app.accounting import accounting_bp
from app.models.base import db
from app.models.invoice import Invoice
from app.models.purchase import Purchase
from app.models.accounting import Expense, ExpenseCategory, CashTransaction, BankTransaction, JournalEntry
from app.models.party import Party
from app.utils.date_utils import get_month_range, get_fy_date_range


@accounting_bp.route('/')
def index():
    """Accounting dashboard"""
    today = date.today()
    month_start, month_end = get_month_range(today.year, today.month)
    fy_start, fy_end = get_fy_date_range()
    
    # Current month stats
    month_sales = db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.invoice_date >= month_start,
        Invoice.invoice_date <= month_end,
        Invoice.status == 'ACTIVE'
    ).scalar() or 0
    
    month_purchases = db.session.query(func.sum(Purchase.total_amount)).filter(
        Purchase.purchase_date >= month_start,
        Purchase.purchase_date <= month_end,
        Purchase.status == 'ACTIVE'
    ).scalar() or 0
    
    month_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.expense_date >= month_start,
        Expense.expense_date <= month_end
    ).scalar() or 0
    
    # FY stats
    fy_sales = db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.invoice_date >= fy_start,
        Invoice.invoice_date <= fy_end,
        Invoice.status == 'ACTIVE'
    ).scalar() or 0
    
    fy_purchases = db.session.query(func.sum(Purchase.total_amount)).filter(
        Purchase.purchase_date >= fy_start,
        Purchase.purchase_date <= fy_end,
        Purchase.status == 'ACTIVE'
    ).scalar() or 0
    
    return render_template('accounting/index.html',
                          month_sales=month_sales,
                          month_purchases=month_purchases,
                          month_expenses=month_expenses,
                          fy_sales=fy_sales,
                          fy_purchases=fy_purchases)


@accounting_bp.route('/sales-register')
def sales_register():
    """Sales register"""
    date_from = request.args.get('date_from', date.today().replace(day=1).isoformat())
    date_to = request.args.get('date_to', date.today().isoformat())
    
    invoices = Invoice.query.filter(
        Invoice.invoice_date >= date_from,
        Invoice.invoice_date <= date_to,
        Invoice.status == 'ACTIVE'
    ).order_by(Invoice.invoice_date, Invoice.id).all()
    
    # Totals
    totals = {
        'subtotal': sum(float(i.subtotal or 0) for i in invoices),
        'cgst': sum(float(i.cgst_amount or 0) for i in invoices),
        'sgst': sum(float(i.sgst_amount or 0) for i in invoices),
        'igst': sum(float(i.igst_amount or 0) for i in invoices),
        'total': sum(float(i.total_amount or 0) for i in invoices)
    }
    
    return render_template('accounting/sales_register.html',
                          invoices=invoices,
                          totals=totals,
                          date_from=date_from,
                          date_to=date_to)


@accounting_bp.route('/purchase-register')
def purchase_register():
    """Purchase register"""
    date_from = request.args.get('date_from', date.today().replace(day=1).isoformat())
    date_to = request.args.get('date_to', date.today().isoformat())
    
    purchases = Purchase.query.filter(
        Purchase.purchase_date >= date_from,
        Purchase.purchase_date <= date_to,
        Purchase.status == 'ACTIVE'
    ).order_by(Purchase.purchase_date, Purchase.id).all()
    
    totals = {
        'subtotal': sum(float(p.subtotal or 0) for p in purchases),
        'cgst': sum(float(p.cgst_amount or 0) for p in purchases),
        'sgst': sum(float(p.sgst_amount or 0) for p in purchases),
        'igst': sum(float(p.igst_amount or 0) for p in purchases),
        'total': sum(float(p.total_amount or 0) for p in purchases)
    }
    
    return render_template('accounting/purchase_register.html',
                          purchases=purchases,
                          totals=totals,
                          date_from=date_from,
                          date_to=date_to)


@accounting_bp.route('/expense-register')
def expense_register():
    """Expense register"""
    date_from = request.args.get('date_from', date.today().replace(day=1).isoformat())
    date_to = request.args.get('date_to', date.today().isoformat())
    category_id = request.args.get('category')
    
    query = Expense.query.filter(
        Expense.expense_date >= date_from,
        Expense.expense_date <= date_to
    )
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    expenses = query.order_by(Expense.expense_date.desc()).all()
    categories = ExpenseCategory.query.order_by(ExpenseCategory.name).all()
    
    total = sum(float(e.amount or 0) for e in expenses)
    
    return render_template('accounting/expense_register.html',
                          expenses=expenses,
                          categories=categories,
                          total=total,
                          date_from=date_from,
                          date_to=date_to)


@accounting_bp.route('/expenses/add', methods=['GET', 'POST'])
def add_expense():
    """Add expense"""
    if request.method == 'POST':
        try:
            expense = Expense(
                expense_date=datetime.strptime(request.form.get('expense_date'), '%Y-%m-%d').date(),
                category_id=request.form.get('category_id') or None,
                description=request.form.get('description'),
                amount=Decimal(request.form.get('amount', '0')),
                is_gst_expense=request.form.get('is_gst') == 'on',
                gst_amount=Decimal(request.form.get('gst_amount', '0')),
                payment_mode=request.form.get('payment_mode', 'CASH'),
                reference_number=request.form.get('reference'),
                vendor_name=request.form.get('vendor_name'),
                notes=request.form.get('notes')
            )
            
            db.session.add(expense)
            
            # Create cash/bank entry
            if expense.payment_mode == 'CASH':
                cash = CashTransaction(
                    transaction_date=expense.expense_date,
                    transaction_type='PAYMENT',
                    description=expense.description,
                    payment=expense.amount,
                    reference_type='EXPENSE',
                    reference_id=expense.id,
                    narration=f'Expense: {expense.description}'
                )
                db.session.add(cash)
            else:
                bank = BankTransaction(
                    transaction_date=expense.expense_date,
                    transaction_type='WITHDRAWAL',
                    description=expense.description,
                    withdrawal=expense.amount,
                    reference_type='EXPENSE',
                    reference_id=expense.id,
                    narration=f'Expense: {expense.description}'
                )
                db.session.add(bank)
            
            db.session.commit()
            
            flash('Expense added successfully', 'success')
            return redirect(url_for('accounting.expense_register'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding expense: {str(e)}', 'error')
    
    categories = ExpenseCategory.query.order_by(ExpenseCategory.name).all()
    return render_template('accounting/add_expense.html', categories=categories)


@accounting_bp.route('/expense-categories')
def expense_categories():
    """Manage expense categories"""
    categories = ExpenseCategory.query.order_by(ExpenseCategory.name).all()
    return render_template('accounting/expense_categories.html', categories=categories)


@accounting_bp.route('/expense-categories/add', methods=['POST'])
def add_expense_category():
    """Add expense category"""
    name = request.form.get('name')
    if name:
        cat = ExpenseCategory(name=name, description=request.form.get('description'))
        db.session.add(cat)
        db.session.commit()
        flash(f'Category "{name}" added', 'success')
    return redirect(url_for('accounting.expense_categories'))


@accounting_bp.route('/cash-book')
def cash_book():
    """Cash book"""
    date_from = request.args.get('date_from', date.today().replace(day=1).isoformat())
    date_to = request.args.get('date_to', date.today().isoformat())
    
    transactions = CashTransaction.query.filter(
        CashTransaction.transaction_date >= date_from,
        CashTransaction.transaction_date <= date_to
    ).order_by(CashTransaction.transaction_date, CashTransaction.id).all()
    
    # Calculate running balance
    opening_balance = 0  # TODO: Calculate from previous period
    total_receipts = sum(float(t.receipt or 0) for t in transactions)
    total_payments = sum(float(t.payment or 0) for t in transactions)
    closing_balance = opening_balance + total_receipts - total_payments
    
    return render_template('accounting/cash_book.html',
                          transactions=transactions,
                          opening_balance=opening_balance,
                          total_receipts=total_receipts,
                          total_payments=total_payments,
                          closing_balance=closing_balance,
                          date_from=date_from,
                          date_to=date_to)


@accounting_bp.route('/bank-book')
def bank_book():
    """Bank book"""
    date_from = request.args.get('date_from', date.today().replace(day=1).isoformat())
    date_to = request.args.get('date_to', date.today().isoformat())
    
    transactions = BankTransaction.query.filter(
        BankTransaction.transaction_date >= date_from,
        BankTransaction.transaction_date <= date_to
    ).order_by(BankTransaction.transaction_date, BankTransaction.id).all()
    
    opening_balance = 0
    total_deposits = sum(float(t.deposit or 0) for t in transactions)
    total_withdrawals = sum(float(t.withdrawal or 0) for t in transactions)
    closing_balance = opening_balance + total_deposits - total_withdrawals
    
    return render_template('accounting/bank_book.html',
                          transactions=transactions,
                          opening_balance=opening_balance,
                          total_deposits=total_deposits,
                          total_withdrawals=total_withdrawals,
                          closing_balance=closing_balance,
                          date_from=date_from,
                          date_to=date_to)


@accounting_bp.route('/day-book')
def day_book():
    """Day book - all transactions for a day"""
    selected_date = request.args.get('date', date.today().isoformat())
    
    # Get all transactions for the day
    invoices = Invoice.query.filter(
        Invoice.invoice_date == selected_date,
        Invoice.status == 'ACTIVE'
    ).all()
    
    purchases = Purchase.query.filter(
        Purchase.purchase_date == selected_date,
        Purchase.status == 'ACTIVE'
    ).all()
    
    expenses = Expense.query.filter_by(expense_date=selected_date).all()
    
    cash_txns = CashTransaction.query.filter_by(transaction_date=selected_date).all()
    bank_txns = BankTransaction.query.filter_by(transaction_date=selected_date).all()
    
    return render_template('accounting/day_book.html',
                          selected_date=selected_date,
                          invoices=invoices,
                          purchases=purchases,
                          expenses=expenses,
                          cash_txns=cash_txns,
                          bank_txns=bank_txns)


@accounting_bp.route('/monthly-summary')
def monthly_summary():
    """Monthly summary report"""
    year = request.args.get('year', date.today().year, type=int)
    
    # Get monthly totals for each category
    months_data = []
    
    for month in range(1, 13):
        start, end = get_month_range(year, month)
        
        sales = db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.invoice_date >= start,
            Invoice.invoice_date <= end,
            Invoice.status == 'ACTIVE'
        ).scalar() or 0
        
        purchases = db.session.query(func.sum(Purchase.total_amount)).filter(
            Purchase.purchase_date >= start,
            Purchase.purchase_date <= end,
            Purchase.status == 'ACTIVE'
        ).scalar() or 0
        
        expenses = db.session.query(func.sum(Expense.amount)).filter(
            Expense.expense_date >= start,
            Expense.expense_date <= end
        ).scalar() or 0
        
        months_data.append({
            'month': start.strftime('%B'),
            'sales': float(sales),
            'purchases': float(purchases),
            'expenses': float(expenses),
            'gross_profit': float(sales) - float(purchases),
            'net_profit': float(sales) - float(purchases) - float(expenses)
        })
    
    return render_template('accounting/monthly_summary.html',
                          months_data=months_data,
                          year=year)
