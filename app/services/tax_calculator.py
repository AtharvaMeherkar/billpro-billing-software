"""
Tax Calculator Service
Handles GST calculations: CGST, SGST, IGST
"""
from decimal import Decimal, ROUND_HALF_UP
import json
import os


class TaxCalculator:
    """GST Tax calculation service"""
    
    @staticmethod
    def is_interstate(seller_state_code, buyer_state_code):
        """
        Determine if transaction is interstate (IGST) or intrastate (CGST+SGST)
        """
        if not seller_state_code or not buyer_state_code:
            return False  # Default to intrastate if unknown
        return seller_state_code != buyer_state_code
    
    @staticmethod
    def get_state_code_from_gstin(gstin):
        """Extract state code from GSTIN (first 2 digits)"""
        if gstin and len(gstin) >= 2:
            return gstin[:2]
        return None
    
    @staticmethod
    def calculate_item_tax(amount, gst_percent, is_igst=False):
        """
        Calculate tax breakdown for an amount
        
        Returns dict with:
        - taxable_amount
        - cgst_percent, cgst_amount
        - sgst_percent, sgst_amount
        - igst_percent, igst_amount
        - total_tax
        - total_amount
        """
        amount = Decimal(str(amount))
        gst_rate = Decimal(str(gst_percent))
        
        result = {
            'taxable_amount': amount,
            'cgst_percent': Decimal('0'),
            'cgst_amount': Decimal('0'),
            'sgst_percent': Decimal('0'),
            'sgst_amount': Decimal('0'),
            'igst_percent': Decimal('0'),
            'igst_amount': Decimal('0'),
            'total_tax': Decimal('0'),
            'total_amount': amount
        }
        
        if gst_rate <= 0:
            return result
        
        if is_igst:
            # Interstate - full IGST
            igst = (amount * gst_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            result['igst_percent'] = gst_rate
            result['igst_amount'] = igst
            result['total_tax'] = igst
        else:
            # Intrastate - split CGST + SGST
            half_rate = gst_rate / 2
            cgst = (amount * half_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            sgst = (amount * half_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            result['cgst_percent'] = half_rate
            result['cgst_amount'] = cgst
            result['sgst_percent'] = half_rate
            result['sgst_amount'] = sgst
            result['total_tax'] = cgst + sgst
        
        result['total_amount'] = amount + result['total_tax']
        return result
    
    @staticmethod
    def calculate_tax_inclusive(amount_with_tax, gst_percent, is_igst=False):
        """
        Reverse calculate tax from tax-inclusive amount
        """
        amount = Decimal(str(amount_with_tax))
        gst_rate = Decimal(str(gst_percent))
        
        if gst_rate <= 0:
            return {
                'taxable_amount': amount,
                'tax_amount': Decimal('0'),
                'total_amount': amount
            }
        
        # Taxable = Total / (1 + GST%)
        taxable = (amount * 100 / (100 + gst_rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        tax = amount - taxable
        
        return {
            'taxable_amount': taxable,
            'tax_amount': tax,
            'total_amount': amount
        }
    
    @staticmethod
    def round_off(amount, round_to=1):
        """
        Round amount to nearest rupee (or specified denomination)
        Returns: (rounded_amount, round_off_adjustment)
        """
        amount = Decimal(str(amount))
        rounded = round(float(amount) / round_to) * round_to
        rounded = Decimal(str(rounded))
        adjustment = rounded - amount
        return rounded, adjustment
    
    @staticmethod
    def validate_gstin(gstin):
        """
        Validate GSTIN format
        Format: 2 digits state code + 10 char PAN + 1 entity code + 1 check digit + Z
        Example: 27AAAAA0000A1Z5
        """
        if not gstin:
            return False, "GSTIN is empty"
        
        gstin = gstin.upper().strip()
        
        if len(gstin) != 15:
            return False, "GSTIN must be 15 characters"
        
        # State code check
        state_code = gstin[:2]
        valid_states = [
            '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '26', '27', '29', '30', '31', '32',
            '33', '34', '35', '36', '37', '38'
        ]
        if state_code not in valid_states:
            return False, f"Invalid state code: {state_code}"
        
        return True, "Valid GSTIN"
