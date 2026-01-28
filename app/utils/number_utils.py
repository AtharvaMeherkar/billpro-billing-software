"""
Number and currency utility functions
"""
from decimal import Decimal


def format_currency(amount, symbol='₹', decimal_places=2):
    """Format amount as Indian currency"""
    if amount is None:
        amount = 0
    
    amount = float(amount)
    
    # Indian number system (lakhs, crores)
    if abs(amount) >= 10000000:  # 1 crore
        formatted = f"{amount/10000000:,.2f} Cr"
    elif abs(amount) >= 100000:  # 1 lakh
        formatted = f"{amount/100000:,.2f} L"
    else:
        formatted = f"{amount:,.{decimal_places}f}"
    
    return f"{symbol}{formatted}"


def format_indian_number(amount):
    """Format number in Indian numbering system (XX,XX,XXX)"""
    if amount is None:
        return '0'
    
    amount = float(amount)
    is_negative = amount < 0
    amount = abs(amount)
    
    # Split into integer and decimal
    if '.' in str(amount):
        integer_part, decimal_part = str(amount).split('.')
    else:
        integer_part = str(int(amount))
        decimal_part = '00'
    
    # Apply Indian grouping
    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        
        # Group remaining in pairs
        groups = []
        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        
        formatted = ','.join(groups) + ',' + last_three
    else:
        formatted = integer_part
    
    result = f"{formatted}.{decimal_part[:2]}"
    return f"-{result}" if is_negative else result


def format_quantity(qty, unit='', decimal_places=3):
    """Format quantity with unit"""
    if qty is None:
        qty = 0
    formatted = f"{float(qty):,.{decimal_places}f}".rstrip('0').rstrip('.')
    if unit:
        return f"{formatted} {unit}"
    return formatted


def number_to_words(num):
    """Convert number to words (Indian system)"""
    if num is None or num == 0:
        return "Zero"
    
    num = float(num)
    is_negative = num < 0
    num = abs(num)
    
    # Handle decimals
    rupees = int(num)
    paise = int(round((num - rupees) * 100))
    
    ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
            'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
            'Seventeen', 'Eighteen', 'Nineteen']
    
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    
    def two_digits(n):
        if n < 20:
            return ones[n]
        else:
            return tens[n // 10] + ('' if n % 10 == 0 else ' ' + ones[n % 10])
    
    def three_digits(n):
        if n < 100:
            return two_digits(n)
        else:
            return ones[n // 100] + ' Hundred' + ('' if n % 100 == 0 else ' and ' + two_digits(n % 100))
    
    def indian_number_words(n):
        if n < 100:
            return two_digits(n)
        elif n < 1000:
            return three_digits(n)
        elif n < 100000:  # Less than 1 lakh
            return two_digits(n // 1000) + ' Thousand' + ('' if n % 1000 == 0 else ' ' + three_digits(n % 1000))
        elif n < 10000000:  # Less than 1 crore
            return two_digits(n // 100000) + ' Lakh' + ('' if n % 100000 == 0 else ' ' + indian_number_words(n % 100000))
        else:
            return two_digits(n // 10000000) + ' Crore' + ('' if n % 10000000 == 0 else ' ' + indian_number_words(n % 10000000))
    
    result = ''
    if rupees > 0:
        result = indian_number_words(rupees) + ' Rupees'
    
    if paise > 0:
        if result:
            result += ' and '
        result += two_digits(paise) + ' Paise'
    
    if is_negative:
        result = 'Minus ' + result
    
    return result + ' Only'
