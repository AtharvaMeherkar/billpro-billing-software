"""
Thermal Printer Abstraction Layer
Supports: ESC/POS USB, Serial/COM, Windows Printers
"""
import json
import os
from datetime import datetime
from config.settings import Config


class ThermalPrinter:
    """Abstraction layer for thermal printing"""
    
    def __init__(self):
        self.config = self._load_config()
        self.printer_type = self.config.get('printer_type', 'windows')
        self.paper_width = self.config.get('paper_width', 80)
        
        # Characters per line based on paper width
        self.chars_per_line = 48 if self.paper_width == 80 else 32
    
    def _load_config(self):
        """Load printer configuration"""
        if os.path.exists(Config.PRINTER_CONFIG):
            with open(Config.PRINTER_CONFIG, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_company(self):
        """Load company configuration"""
        if os.path.exists(Config.COMPANY_CONFIG):
            with open(Config.COMPANY_CONFIG, 'r') as f:
                return json.load(f)
        return {}
    
    def _get_printer(self):
        """Get printer instance based on configuration"""
        if self.printer_type == 'usb':
            return self._get_usb_printer()
        elif self.printer_type == 'serial':
            return self._get_serial_printer()
        else:
            return self._get_windows_printer()
    
    def _get_usb_printer(self):
        """Get USB ESC/POS printer"""
        try:
            from escpos.printer import Usb
            vendor_id = int(self.config.get('usb_vendor_id', '0'), 16)
            product_id = int(self.config.get('usb_product_id', '0'), 16)
            return Usb(vendor_id, product_id)
        except Exception as e:
            raise Exception(f"USB printer error: {str(e)}")
    
    def _get_serial_printer(self):
        """Get Serial/COM port printer"""
        try:
            from escpos.printer import Serial
            port = self.config.get('serial_port', 'COM1')
            baudrate = self.config.get('serial_baudrate', 9600)
            return Serial(port, baudrate=baudrate)
        except Exception as e:
            raise Exception(f"Serial printer error: {str(e)}")
    
    def _get_windows_printer(self):
        """Get Windows printer (via win32print)"""
        return WindowsPrinter(
            self.config.get('printer_name', 'Default'),
            self.chars_per_line
        )
    
    def _format_header(self, values=None):
        """Format header from config template"""
        company = self._load_company()
        header_config = self.config.get('header', {})
        
        placeholders = {
            '{{company_name}}': company.get('name', ''),
            '{{company_address}}': ', '.join(filter(None, [
                company.get('address', {}).get('line1', ''),
                company.get('address', {}).get('city', ''),
                company.get('address', {}).get('state', '')
            ])),
            '{{company_phone}}': company.get('contact', {}).get('phone', ''),
            '{{company_gstin}}': company.get('gstin', '')
        }
        
        lines = []
        for i in range(1, 5):
            line = header_config.get(f'line{i}', '')
            for key, value in placeholders.items():
                line = line.replace(key, value)
            if line:
                lines.append(line)
        
        return lines
    
    def _format_footer(self):
        """Format footer from config"""
        footer_config = self.config.get('footer', {})
        lines = []
        for i in range(1, 4):
            line = footer_config.get(f'line{i}', '')
            if line:
                lines.append(line)
        return lines
    
    def print_invoice(self, invoice):
        """Print invoice to thermal printer"""
        try:
            printer = self._get_printer()
            company = self._load_company()
            
            if isinstance(printer, WindowsPrinter):
                return self._print_invoice_windows(printer, invoice, company)
            else:
                return self._print_invoice_escpos(printer, invoice, company)
        except Exception as e:
            print(f"Print error: {str(e)}")
            return False
    
    def _print_invoice_escpos(self, p, invoice, company):
        """Print invoice using ESC/POS commands"""
        from app.utils.number_utils import number_to_words
        
        # Header
        p.set(align='center', bold=True, double_height=True)
        for line in self._format_header():
            p.text(line + '\n')
        
        p.set(align='center', bold=False, double_height=False)
        p.text('-' * self.chars_per_line + '\n')
        
        # Invoice details
        p.set(align='left')
        p.text(f"Invoice: {invoice.invoice_number}\n")
        p.text(f"Date: {invoice.invoice_date.strftime('%d-%m-%Y')}\n")
        p.text(f"Customer: {invoice.party.name}\n")
        if invoice.party.gstin:
            p.text(f"GSTIN: {invoice.party.gstin}\n")
        
        p.text('-' * self.chars_per_line + '\n')
        
        # Items header
        p.set(bold=True)
        p.text(self._format_line('Item', 'Qty', 'Rate', 'Amt'))
        p.set(bold=False)
        p.text('-' * self.chars_per_line + '\n')
        
        # Items
        for item in invoice.items:
            name = (item.description or item.product.name)[:20]
            p.text(f"{name}\n")
            p.text(self._format_line(
                '',
                f"{float(item.quantity):.2f}",
                f"{float(item.rate):.2f}",
                f"{float(item.total_amount):.2f}"
            ))
        
        p.text('-' * self.chars_per_line + '\n')
        
        # Totals
        p.text(self._format_total_line('Subtotal', float(invoice.subtotal)))
        
        if invoice.is_gst_invoice:
            if invoice.cgst_amount:
                p.text(self._format_total_line('CGST', float(invoice.cgst_amount)))
            if invoice.sgst_amount:
                p.text(self._format_total_line('SGST', float(invoice.sgst_amount)))
            if invoice.igst_amount:
                p.text(self._format_total_line('IGST', float(invoice.igst_amount)))
        
        if invoice.round_off:
            p.text(self._format_total_line('Round Off', float(invoice.round_off)))
        
        p.text('-' * self.chars_per_line + '\n')
        p.set(bold=True)
        p.text(self._format_total_line('TOTAL', float(invoice.total_amount)))
        p.set(bold=False)
        
        # Amount in words
        p.text('\n')
        words = number_to_words(float(invoice.total_amount))
        p.text(f"{words}\n")
        
        p.text('-' * self.chars_per_line + '\n')
        
        # Footer
        p.set(align='center')
        for line in self._format_footer():
            p.text(line + '\n')
        
        # Cut paper
        if self.config.get('cut_paper', True):
            p.cut()
        
        # Open drawer
        if self.config.get('open_drawer', False):
            p.cashdraw(2)
        
        return True
    
    def _print_invoice_windows(self, printer, invoice, company):
        """Print invoice via Windows printer"""
        from app.utils.number_utils import number_to_words
        
        lines = []
        
        # Header
        for line in self._format_header():
            lines.append(('center', line))
        
        lines.append(('left', '-' * self.chars_per_line))
        
        # Invoice details
        lines.append(('left', f"Invoice: {invoice.invoice_number}"))
        lines.append(('left', f"Date: {invoice.invoice_date.strftime('%d-%m-%Y')}"))
        lines.append(('left', f"Customer: {invoice.party.name}"))
        if invoice.party.gstin:
            lines.append(('left', f"GSTIN: {invoice.party.gstin}"))
        
        lines.append(('left', '-' * self.chars_per_line))
        lines.append(('left', self._format_line('Item', 'Qty', 'Rate', 'Amt')))
        lines.append(('left', '-' * self.chars_per_line))
        
        # Items
        for item in invoice.items:
            name = (item.description or item.product.name)[:20]
            lines.append(('left', name))
            lines.append(('left', self._format_line(
                '',
                f"{float(item.quantity):.2f}",
                f"{float(item.rate):.2f}",
                f"{float(item.total_amount):.2f}"
            )))
        
        lines.append(('left', '-' * self.chars_per_line))
        
        # Totals
        lines.append(('left', self._format_total_line('Subtotal', float(invoice.subtotal))))
        
        if invoice.is_gst_invoice:
            if invoice.cgst_amount:
                lines.append(('left', self._format_total_line('CGST', float(invoice.cgst_amount))))
            if invoice.sgst_amount:
                lines.append(('left', self._format_total_line('SGST', float(invoice.sgst_amount))))
            if invoice.igst_amount:
                lines.append(('left', self._format_total_line('IGST', float(invoice.igst_amount))))
        
        if invoice.round_off:
            lines.append(('left', self._format_total_line('Round Off', float(invoice.round_off))))
        
        lines.append(('left', '-' * self.chars_per_line))
        lines.append(('left', self._format_total_line('TOTAL', float(invoice.total_amount))))
        
        # Amount in words
        words = number_to_words(float(invoice.total_amount))
        lines.append(('left', ''))
        lines.append(('left', words))
        
        lines.append(('left', '-' * self.chars_per_line))
        
        # Footer
        for line in self._format_footer():
            lines.append(('center', line))
        
        return printer.print_lines(lines)
    
    def _format_line(self, col1, col2, col3, col4):
        """Format a 4-column line for receipt"""
        if self.paper_width == 80:
            return f"{col1:<20}{col2:>8}{col3:>10}{col4:>10}"
        else:
            return f"{col1:<12}{col2:>6}{col3:>7}{col4:>7}"
    
    def _format_total_line(self, label, amount):
        """Format a total line"""
        amt_str = f"Rs.{amount:,.2f}"
        padding = self.chars_per_line - len(label) - len(amt_str)
        return f"{label}{' ' * padding}{amt_str}"
    
    def test_print(self):
        """Print a test page"""
        try:
            printer = self._get_printer()
            
            if isinstance(printer, WindowsPrinter):
                lines = [
                    ('center', 'PRINTER TEST'),
                    ('center', '-' * self.chars_per_line),
                    ('left', f'Date: {datetime.now().strftime("%d-%m-%Y %H:%M")}'),
                    ('left', f'Paper Width: {self.paper_width}mm'),
                    ('left', f'Chars/Line: {self.chars_per_line}'),
                    ('center', '-' * self.chars_per_line),
                    ('center', 'Test Successful!'),
                ]
                return printer.print_lines(lines)
            else:
                printer.set(align='center', bold=True)
                printer.text('PRINTER TEST\n')
                printer.set(bold=False)
                printer.text('-' * self.chars_per_line + '\n')
                printer.set(align='left')
                printer.text(f'Date: {datetime.now().strftime("%d-%m-%Y %H:%M")}\n')
                printer.text(f'Paper Width: {self.paper_width}mm\n')
                printer.text(f'Chars/Line: {self.chars_per_line}\n')
                printer.set(align='center')
                printer.text('-' * self.chars_per_line + '\n')
                printer.text('Test Successful!\n')
                
                if self.config.get('cut_paper', True):
                    printer.cut()
                
                return True
        
        except Exception as e:
            print(f"Test print error: {str(e)}")
            return False


class WindowsPrinter:
    """Windows printer wrapper using win32print"""
    
    def __init__(self, printer_name, chars_per_line):
        self.printer_name = printer_name
        self.chars_per_line = chars_per_line
    
    def print_lines(self, lines):
        """Print lines to Windows printer"""
        try:
            import win32print
            import win32ui
            from PIL import Image, ImageDraw, ImageFont
            
            # Create receipt image - 58mm paper = ~384 pixels at 203 DPI (standard thermal)
            line_height = 24
            width = 384 if self.chars_per_line <= 32 else 576  # 58mm = 384px, 80mm = 576px
            height = len(lines) * line_height + 30
            
            img = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Use larger font for thermal printer readability
            try:
                font = ImageFont.truetype('consola.ttf', 18)  # Larger font for 58mm
                font_bold = ImageFont.truetype('consolab.ttf', 18)
            except:
                try:
                    font = ImageFont.truetype('cour.ttf', 18)
                    font_bold = font
                except:
                    font = ImageFont.load_default()
                    font_bold = font
            
            y = 5
            for align, text in lines:
                if align == 'center':
                    text_bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    x = (width - text_width) // 2
                else:
                    x = 5  # Minimal left margin
                
                draw.text((x, y), text, fill='black', font=font)
                y += line_height
            
            # Print via Windows
            if self.printer_name == 'Default':
                printer_name = win32print.GetDefaultPrinter()
            else:
                printer_name = self.printer_name
            
            # Save temp file and print
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.bmp', delete=False) as f:
                temp_path = f.name
                img.save(temp_path, 'BMP')
            
            # Print using shell
            import subprocess
            subprocess.run(['mspaint', '/p', temp_path], shell=True, timeout=30)
            
            # Cleanup
            import os
            os.remove(temp_path)
            
            return True
        
        except Exception as e:
            print(f"Windows print error: {str(e)}")
            # Fallback: print to console
            print("\n=== RECEIPT PRINT ===")
            for _, text in lines:
                print(text)
            print("=== END RECEIPT ===\n")
            return True
