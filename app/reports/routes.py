"""
Reports Routes - PDF/CSV Export
"""
import csv
import io
from datetime import date
from flask import render_template, request, Response, make_response
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.reports import reports_bp
from app.models.base import db
from app.models.invoice import Invoice
from app.models.purchase import Purchase
from app.models.party import Party, PartyTransaction
from app.models.product import Product


@reports_bp.route('/')
def index():
    """Reports dashboard"""
    return render_template('reports/index.html')


@reports_bp.route('/sales-report')
def sales_report():
    """Sales report"""
    date_from = request.args.get('date_from', date.today().replace(day=1).isoformat())
    date_to = request.args.get('date_to', date.today().isoformat())
    
    invoices = Invoice.query.filter(
        Invoice.invoice_date >= date_from,
        Invoice.invoice_date <= date_to,
        Invoice.status == 'ACTIVE'
    ).order_by(Invoice.invoice_date).all()
    
    totals = {
        'count': len(invoices),
        'subtotal': sum(float(i.subtotal or 0) for i in invoices),
        'tax': sum(float(i.tax_amount or 0) for i in invoices),
        'total': sum(float(i.total_amount or 0) for i in invoices)
    }
    
    return render_template('reports/sales_report.html',
                          invoices=invoices,
                          totals=totals,
                          date_from=date_from,
                          date_to=date_to)


@reports_bp.route('/sales-report/csv')
def sales_report_csv():
    """Export sales report to CSV"""
    date_from = request.args.get('date_from', date.today().replace(day=1).isoformat())
    date_to = request.args.get('date_to', date.today().isoformat())
    
    invoices = Invoice.query.filter(
        Invoice.invoice_date >= date_from,
        Invoice.invoice_date <= date_to,
        Invoice.status == 'ACTIVE'
    ).order_by(Invoice.invoice_date).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Invoice No', 'Date', 'Customer', 'GSTIN', 'Subtotal', 
                    'CGST', 'SGST', 'IGST', 'Total', 'Payment Mode'])
    
    for inv in invoices:
        writer.writerow([
            inv.invoice_number,
            inv.invoice_date.strftime('%d-%m-%Y'),
            inv.party.name,
            inv.party.gstin or '',
            float(inv.subtotal or 0),
            float(inv.cgst_amount or 0),
            float(inv.sgst_amount or 0),
            float(inv.igst_amount or 0),
            float(inv.total_amount or 0),
            inv.payment_mode
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=sales_report_{date_from}_to_{date_to}.csv'}
    )


@reports_bp.route('/sales-report/pdf')
def sales_report_pdf():
    """Export sales report to PDF"""
    date_from = request.args.get('date_from', date.today().replace(day=1).isoformat())
    date_to = request.args.get('date_to', date.today().isoformat())
    
    invoices = Invoice.query.filter(
        Invoice.invoice_date >= date_from,
        Invoice.invoice_date <= date_to,
        Invoice.status == 'ACTIVE'
    ).order_by(Invoice.invoice_date).all()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1)
    elements.append(Paragraph('Sales Report', title_style))
    elements.append(Paragraph(f'{date_from} to {date_to}', styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Table data
    data = [['Invoice No', 'Date', 'Customer', 'Subtotal', 'Tax', 'Total']]
    
    total_subtotal = 0
    total_tax = 0
    total_amount = 0
    
    for inv in invoices:
        subtotal = float(inv.subtotal or 0)
        tax = float(inv.tax_amount or 0)
        total = float(inv.total_amount or 0)
        
        data.append([
            inv.invoice_number,
            inv.invoice_date.strftime('%d-%m-%Y'),
            inv.party.name[:30],
            f'₹{subtotal:,.2f}',
            f'₹{tax:,.2f}',
            f'₹{total:,.2f}'
        ])
        
        total_subtotal += subtotal
        total_tax += tax
        total_amount += total
    
    data.append(['', '', 'TOTAL', f'₹{total_subtotal:,.2f}', 
                f'₹{total_tax:,.2f}', f'₹{total_amount:,.2f}'])
    
    table = Table(data, colWidths=[80, 60, 150, 70, 60, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
    ]))
    
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=sales_report_{date_from}_to_{date_to}.pdf'
    
    return response


@reports_bp.route('/gst-report')
def gst_report():
    """GST Summary Report"""
    date_from = request.args.get('date_from', date.today().replace(day=1).isoformat())
    date_to = request.args.get('date_to', date.today().isoformat())
    
    # Sales GST
    sales = Invoice.query.filter(
        Invoice.invoice_date >= date_from,
        Invoice.invoice_date <= date_to,
        Invoice.status == 'ACTIVE',
        Invoice.is_gst_invoice == True
    ).all()
    
    sales_summary = {
        'taxable': sum(float(i.subtotal or 0) for i in sales),
        'cgst': sum(float(i.cgst_amount or 0) for i in sales),
        'sgst': sum(float(i.sgst_amount or 0) for i in sales),
        'igst': sum(float(i.igst_amount or 0) for i in sales),
        'total_tax': sum(float(i.tax_amount or 0) for i in sales)
    }
    
    # Purchase GST (Input Credit)
    purchases = Purchase.query.filter(
        Purchase.purchase_date >= date_from,
        Purchase.purchase_date <= date_to,
        Purchase.status == 'ACTIVE',
        Purchase.is_gst_invoice == True
    ).all()
    
    purchase_summary = {
        'taxable': sum(float(p.subtotal or 0) for p in purchases),
        'cgst': sum(float(p.cgst_amount or 0) for p in purchases),
        'sgst': sum(float(p.sgst_amount or 0) for p in purchases),
        'igst': sum(float(p.igst_amount or 0) for p in purchases),
        'total_tax': sum(float(p.tax_amount or 0) for p in purchases)
    }
    
    # Net GST Liability
    net_liability = {
        'cgst': sales_summary['cgst'] - purchase_summary['cgst'],
        'sgst': sales_summary['sgst'] - purchase_summary['sgst'],
        'igst': sales_summary['igst'] - purchase_summary['igst']
    }
    net_liability['total'] = net_liability['cgst'] + net_liability['sgst'] + net_liability['igst']
    
    return render_template('reports/gst_report.html',
                          sales_summary=sales_summary,
                          purchase_summary=purchase_summary,
                          net_liability=net_liability,
                          date_from=date_from,
                          date_to=date_to)


@reports_bp.route('/receivables')
def receivables_report():
    """Receivables (Debtors) Report"""
    customers = Party.query.filter(
        Party.party_type == 'customer',
        Party.is_active == True,
        Party.current_balance > 0
    ).order_by(Party.current_balance.desc()).all()
    
    total = sum(float(c.current_balance or 0) for c in customers)
    
    return render_template('reports/receivables.html',
                          customers=customers,
                          total=total)


@reports_bp.route('/payables')
def payables_report():
    """Payables (Creditors) Report"""
    suppliers = Party.query.filter(
        Party.party_type == 'supplier',
        Party.is_active == True,
        Party.current_balance > 0
    ).order_by(Party.current_balance.desc()).all()
    
    total = sum(float(s.current_balance or 0) for s in suppliers)
    
    return render_template('reports/payables.html',
                          suppliers=suppliers,
                          total=total)


@reports_bp.route('/product-sales')
def product_sales_report():
    """Product-wise sales report"""
    date_from = request.args.get('date_from', date.today().replace(day=1).isoformat())
    date_to = request.args.get('date_to', date.today().isoformat())
    
    from app.models.invoice import InvoiceItem
    from sqlalchemy import func
    
    # Product-wise sales
    results = db.session.query(
        Product.name,
        Product.hsn_code,
        func.sum(InvoiceItem.quantity).label('total_qty'),
        func.sum(InvoiceItem.taxable_amount).label('total_amount')
    ).join(InvoiceItem, Product.id == InvoiceItem.product_id)\
     .join(Invoice, InvoiceItem.invoice_id == Invoice.id)\
     .filter(
        Invoice.invoice_date >= date_from,
        Invoice.invoice_date <= date_to,
        Invoice.status == 'ACTIVE'
    ).group_by(Product.id).order_by(func.sum(InvoiceItem.taxable_amount).desc()).all()
    
    return render_template('reports/product_sales.html',
                          results=results,
                          date_from=date_from,
                          date_to=date_to)
