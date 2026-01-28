/**
 * BillPro - Application JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(msg) {
        setTimeout(function() {
            msg.style.opacity = '0';
            setTimeout(function() {
                msg.remove();
            }, 300);
        }, 5000);
    });
    
    // Confirm dialogs for delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm || 'Are you sure?')) {
                e.preventDefault();
            }
        });
    });
    
    // Auto-focus first input in forms
    const firstInput = document.querySelector('form input:not([type="hidden"]):not([readonly])');
    if (firstInput) {
        firstInput.focus();
    }
});

/**
 * Invoice form helpers
 */
const InvoiceForm = {
    itemCount: 0,
    
    addItem: function() {
        this.itemCount++;
        const tbody = document.getElementById('invoice-items');
        if (!tbody) return;
        
        const row = document.createElement('tr');
        row.id = `item-row-${this.itemCount}`;
        row.innerHTML = `
            <td>
                <select name="product_id[]" class="product-select" onchange="InvoiceForm.onProductChange(this, ${this.itemCount})">
                    <option value="">Select Product</option>
                </select>
            </td>
            <td><input type="text" name="hsn[]" id="hsn-${this.itemCount}" readonly></td>
            <td><input type="number" name="quantity[]" id="qty-${this.itemCount}" step="0.001" min="0" value="1" onchange="InvoiceForm.calculateRow(${this.itemCount})"></td>
            <td><input type="number" name="rate[]" id="rate-${this.itemCount}" step="0.01" min="0" onchange="InvoiceForm.calculateRow(${this.itemCount})"></td>
            <td><input type="number" name="discount[]" id="disc-${this.itemCount}" step="0.01" min="0" max="100" value="0" onchange="InvoiceForm.calculateRow(${this.itemCount})"></td>
            <td class="number"><span id="gst-${this.itemCount}">0%</span></td>
            <td class="number"><span id="amount-${this.itemCount}">0.00</span></td>
            <td><button type="button" class="btn btn-sm btn-danger" onclick="InvoiceForm.removeItem(${this.itemCount})">×</button></td>
        `;
        tbody.appendChild(row);
        
        // Populate product dropdown
        this.populateProducts(row.querySelector('.product-select'));
    },
    
    removeItem: function(index) {
        const row = document.getElementById(`item-row-${index}`);
        if (row) {
            row.remove();
            this.calculateTotals();
        }
    },
    
    populateProducts: function(select) {
        fetch('/inventory/api/search?q=')
            .then(response => response.json())
            .then(products => {
                products.forEach(p => {
                    const option = document.createElement('option');
                    option.value = p.id;
                    option.textContent = `${p.name} (${p.code || 'N/A'})`;
                    option.dataset.price = p.selling_price;
                    option.dataset.gst = p.gst_percent;
                    option.dataset.hsn = p.hsn_code || '';
                    select.appendChild(option);
                });
            });
    },
    
    onProductChange: function(select, index) {
        const option = select.selectedOptions[0];
        if (option && option.value) {
            document.getElementById(`rate-${index}`).value = option.dataset.price || 0;
            document.getElementById(`hsn-${index}`).value = option.dataset.hsn || '';
            document.getElementById(`gst-${index}`).textContent = (option.dataset.gst || 0) + '%';
            this.calculateRow(index);
        }
    },
    
    calculateRow: function(index) {
        const qty = parseFloat(document.getElementById(`qty-${index}`).value) || 0;
        const rate = parseFloat(document.getElementById(`rate-${index}`).value) || 0;
        const disc = parseFloat(document.getElementById(`disc-${index}`).value) || 0;
        
        const gross = qty * rate;
        const discAmount = gross * disc / 100;
        const taxable = gross - discAmount;
        
        document.getElementById(`amount-${index}`).textContent = taxable.toFixed(2);
        
        this.calculateTotals();
    },
    
    calculateTotals: function() {
        let subtotal = 0;
        let cgst = 0;
        let sgst = 0;
        let igst = 0;
        
        const isGst = document.getElementById('is_gst_invoice')?.checked ?? true;
        const isIgst = document.getElementById('is_igst')?.checked ?? false;
        
        document.querySelectorAll('[id^="amount-"]').forEach(el => {
            const index = el.id.split('-')[1];
            const amount = parseFloat(el.textContent) || 0;
            const gstPercent = parseFloat(document.getElementById(`gst-${index}`)?.textContent) || 0;
            
            subtotal += amount;
            
            if (isGst && gstPercent > 0) {
                const taxAmount = amount * gstPercent / 100;
                if (isIgst) {
                    igst += taxAmount;
                } else {
                    cgst += taxAmount / 2;
                    sgst += taxAmount / 2;
                }
            }
        });
        
        const total = subtotal + cgst + sgst + igst;
        const roundedTotal = Math.round(total);
        const roundOff = roundedTotal - total;
        
        if (document.getElementById('subtotal')) {
            document.getElementById('subtotal').textContent = subtotal.toFixed(2);
        }
        if (document.getElementById('cgst-total')) {
            document.getElementById('cgst-total').textContent = cgst.toFixed(2);
        }
        if (document.getElementById('sgst-total')) {
            document.getElementById('sgst-total').textContent = sgst.toFixed(2);
        }
        if (document.getElementById('igst-total')) {
            document.getElementById('igst-total').textContent = igst.toFixed(2);
        }
        if (document.getElementById('round-off')) {
            document.getElementById('round-off').textContent = roundOff.toFixed(2);
        }
        if (document.getElementById('grand-total')) {
            document.getElementById('grand-total').textContent = roundedTotal.toFixed(2);
        }
    }
};

/**
 * Party search with autocomplete
 */
function searchParty(input, type) {
    const query = input.value;
    if (query.length < 2) return;
    
    fetch(`/ledgers/api/search?q=${encodeURIComponent(query)}&type=${type}`)
        .then(response => response.json())
        .then(parties => {
            // Show autocomplete dropdown
            console.log(parties);
        });
}

/**
 * Format numbers as Indian currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(amount);
}

/**
 * Date picker enhancement
 */
function setDefaultDate(inputId) {
    const input = document.getElementById(inputId);
    if (input && !input.value) {
        input.valueAsDate = new Date();
    }
}
