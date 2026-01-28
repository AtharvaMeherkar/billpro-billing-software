"""
Printing Routes
"""
import json
import os
from flask import render_template, request, redirect, url_for, flash

from app.printing import printing_bp
from config.settings import Config


@printing_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """Printer settings"""
    printer_config = {}
    if os.path.exists(Config.PRINTER_CONFIG):
        with open(Config.PRINTER_CONFIG, 'r') as f:
            printer_config = json.load(f)
    
    if request.method == 'POST':
        try:
            printer_config.update({
                'printer_type': request.form.get('printer_type', 'windows'),
                'printer_name': request.form.get('printer_name', 'Default'),
                'usb_vendor_id': request.form.get('usb_vendor_id') or None,
                'usb_product_id': request.form.get('usb_product_id') or None,
                'serial_port': request.form.get('serial_port') or None,
                'serial_baudrate': int(request.form.get('serial_baudrate', 9600)),
                'paper_width': int(request.form.get('paper_width', 80)),
                'cut_paper': request.form.get('cut_paper') == 'on',
                'open_drawer': request.form.get('open_drawer') == 'on',
                'header': {
                    'line1': request.form.get('header_line1', ''),
                    'line2': request.form.get('header_line2', ''),
                    'line3': request.form.get('header_line3', ''),
                    'line4': request.form.get('header_line4', '')
                },
                'footer': {
                    'line1': request.form.get('footer_line1', ''),
                    'line2': request.form.get('footer_line2', ''),
                    'line3': request.form.get('footer_line3', '')
                }
            })
            
            with open(Config.PRINTER_CONFIG, 'w') as f:
                json.dump(printer_config, f, indent=4)
            
            flash('Printer settings saved', 'success')
        
        except Exception as e:
            flash(f'Error saving settings: {str(e)}', 'error')
    
    # Get available Windows printers
    printers = []
    try:
        import win32print
        printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
    except:
        pass
    
    return render_template('printing/settings.html', 
                          config=printer_config,
                          printers=printers)


@printing_bp.route('/test')
def test_print():
    """Test print"""
    from app.printing.printer import ThermalPrinter
    
    try:
        printer = ThermalPrinter()
        result = printer.test_print()
        
        if result:
            flash('Test print sent successfully', 'success')
        else:
            flash('Test print failed', 'error')
    
    except Exception as e:
        flash(f'Printer error: {str(e)}', 'error')
    
    return redirect(url_for('printing.settings'))
