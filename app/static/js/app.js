/**
 * BillPro - Premium Application JavaScript
 * Enhanced UX with smooth animations and interactions
 */

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    initFlashMessages();
    initConfirmDialogs();
    initFormEnhancements();
    initTableEnhancements();
    initSmoothScrolling();
    initKeyboardShortcuts();
    initNumberFormatting();
    initLoadingStates();
    
    // Add loaded class for CSS transitions
    document.body.classList.add('loaded');
    
    console.log('🧾 BillPro initialized successfully');
});

// ============================================
// FLASH MESSAGES - Auto dismiss with animation
// ============================================
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach((msg, index) => {
        // Stagger animation
        msg.style.animationDelay = `${index * 100}ms`;
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            dismissFlash(msg);
        }, 5000 + (index * 500));
    });
}

function dismissFlash(element) {
    element.style.transition = 'all 0.3s ease-out';
    element.style.opacity = '0';
    element.style.transform = 'translateX(100px)';
    
    setTimeout(() => {
        element.remove();
    }, 300);
}

// ============================================
// CONFIRM DIALOGS - Modern confirmation
// ============================================
function initConfirmDialogs() {
    document.querySelectorAll('[data-confirm]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Are you sure you want to proceed?';
            
            if (!confirm(message)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });
}

// ============================================
// FORM ENHANCEMENTS
// ============================================
function initFormEnhancements() {
    // Auto-focus first input
    const form = document.querySelector('form:not(.no-autofocus)');
    if (form) {
        const firstInput = form.querySelector('input:not([type="hidden"]):not([readonly]):not([disabled]), select:not([disabled])');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
    
    // Add floating label effect
    document.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
            input.parentElement.classList.remove('focused');
        });
    });
    
    // Number input formatting
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('wheel', (e) => {
            if (document.activeElement === input) {
                e.preventDefault();
            }
        });
    });
}

// ============================================
// TABLE ENHANCEMENTS
// ============================================
function initTableEnhancements() {
    // Add row click highlighting
    document.querySelectorAll('tbody tr').forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking a link or button
            if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                return;
            }
            
            // Check if row has a link
            const link = this.querySelector('a[href]');
            if (link && !e.target.closest('a')) {
                // Visual feedback
                this.style.transform = 'scale(0.99)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 100);
            }
        });
    });
    
    // Add hover effects to table rows
    document.querySelectorAll('tbody tr').forEach((row, index) => {
        row.style.animationDelay = `${index * 30}ms`;
    });
}

// ============================================
// SMOOTH SCROLLING
// ============================================
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Escape to close modals
        if (e.key === 'Escape') {
            const modal = document.querySelector('.modal-backdrop');
            if (modal) {
                closeModal();
            }
        }
        
        // Ctrl+S to save forms
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            const form = document.querySelector('form[method="post"]');
            if (form) {
                e.preventDefault();
                form.submit();
            }
        }
        
        // Ctrl+N for new invoice
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            if (window.location.pathname.includes('billing')) {
                e.preventDefault();
                window.location.href = '/billing/new';
            }
        }
    });
}

// ============================================
// NUMBER FORMATTING - Indian currency
// ============================================
function initNumberFormatting() {
    document.querySelectorAll('.number, [data-format="currency"]').forEach(el => {
        const value = parseFloat(el.textContent.replace(/[₹,]/g, ''));
        if (!isNaN(value) && !el.textContent.includes('₹')) {
            // Already formatted or not a number
        }
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

function formatNumber(amount) {
    return new Intl.NumberFormat('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// ============================================
// LOADING STATES
// ============================================
function initLoadingStates() {
    // Add loading state to buttons on form submit
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.dataset.originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                
                // Re-enable after 10 seconds in case of error
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.dataset.originalText;
                }, 10000);
            }
        });
    });
}

// Show loading overlay
function showLoading(message = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.innerHTML = `
        <div style="background: white; padding: 30px 50px; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); text-align: center;">
            <div class="loading" style="width: 40px; height: 40px; margin: 0 auto 15px;"></div>
            <p style="margin: 0; font-weight: 500; color: #1e293b;">${message}</p>
        </div>
    `;
    overlay.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(4px);
        display: flex; align-items: center; justify-content: center;
        z-index: 9999; animation: fadeIn 0.2s ease-out;
    `;
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => overlay.remove(), 200);
    }
}

// ============================================
// MODAL FUNCTIONS
// ============================================
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Focus first input
        setTimeout(() => {
            const input = modal.querySelector('input:not([type="hidden"]), select');
            if (input) input.focus();
        }, 100);
    }
}

function closeModal() {
    const modals = document.querySelectorAll('.modal-backdrop');
    modals.forEach(modal => {
        modal.style.opacity = '0';
        setTimeout(() => {
            modal.style.display = 'none';
            modal.style.opacity = '';
        }, 200);
    });
    document.body.style.overflow = '';
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `flash-message flash-${type}`;
    toast.style.cssText = `
        position: fixed; bottom: 20px; right: 20px;
        z-index: 9999; min-width: 300px; max-width: 500px;
        animation: slideUp 0.3s ease-out;
    `;
    toast.innerHTML = `
        ${message}
        <button class="flash-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove
    setTimeout(() => {
        dismissFlash(toast);
    }, 4000);
}

// ============================================
// INVOICE FORM HELPERS
// ============================================
const InvoiceForm = {
    itemCount: 0,
    products: [],
    
    init: function() {
        this.loadProducts();
    },
    
    loadProducts: function() {
        fetch('/inventory/api/search?q=')
            .then(response => response.json())
            .then(products => {
                this.products = products;
            })
            .catch(err => console.error('Failed to load products:', err));
    },
    
    addItem: function() {
        this.itemCount++;
        const tbody = document.getElementById('invoice-items');
        if (!tbody) return;
        
        const row = document.createElement('tr');
        row.id = `item-row-${this.itemCount}`;
        row.className = 'animate-in';
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
        
        // Focus the new select
        row.querySelector('select').focus();
    },
    
    removeItem: function(index) {
        const row = document.getElementById(`item-row-${index}`);
        if (row) {
            row.style.transform = 'translateX(50px)';
            row.style.opacity = '0';
            setTimeout(() => {
                row.remove();
                this.calculateTotals();
            }, 200);
        }
    },
    
    populateProducts: function(select) {
        if (this.products.length > 0) {
            this.products.forEach(p => {
                const option = document.createElement('option');
                option.value = p.id;
                option.textContent = `${p.name} (${p.code || 'N/A'})`;
                option.dataset.price = p.selling_price;
                option.dataset.gst = p.gst_percent;
                option.dataset.hsn = p.hsn_code || '';
                select.appendChild(option);
            });
        } else {
            fetch('/inventory/api/search?q=')
                .then(response => response.json())
                .then(products => {
                    this.products = products;
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
        }
    },
    
    onProductChange: function(select, index) {
        const option = select.selectedOptions[0];
        if (option && option.value) {
            document.getElementById(`rate-${index}`).value = option.dataset.price || 0;
            document.getElementById(`hsn-${index}`).value = option.dataset.hsn || '';
            document.getElementById(`gst-${index}`).textContent = (option.dataset.gst || 0) + '%';
            
            // Highlight the updated fields
            const rateInput = document.getElementById(`rate-${index}`);
            rateInput.style.background = '#d1fae5';
            setTimeout(() => {
                rateInput.style.background = '';
            }, 500);
            
            this.calculateRow(index);
        }
    },
    
    calculateRow: function(index) {
        const qty = parseFloat(document.getElementById(`qty-${index}`)?.value) || 0;
        const rate = parseFloat(document.getElementById(`rate-${index}`)?.value) || 0;
        const disc = parseFloat(document.getElementById(`disc-${index}`)?.value) || 0;
        
        const gross = qty * rate;
        const discAmount = gross * disc / 100;
        const taxable = gross - discAmount;
        
        const amountEl = document.getElementById(`amount-${index}`);
        if (amountEl) {
            amountEl.textContent = taxable.toFixed(2);
            
            // Animation
            amountEl.style.transform = 'scale(1.1)';
            amountEl.style.color = '#10b981';
            setTimeout(() => {
                amountEl.style.transform = '';
                amountEl.style.color = '';
            }, 200);
        }
        
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
        
        this.updateTotalDisplay('subtotal', subtotal);
        this.updateTotalDisplay('cgst-total', cgst);
        this.updateTotalDisplay('sgst-total', sgst);
        this.updateTotalDisplay('igst-total', igst);
        this.updateTotalDisplay('round-off', roundOff);
        this.updateTotalDisplay('grand-total', roundedTotal, true);
    },
    
    updateTotalDisplay: function(id, value, highlight = false) {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = value.toFixed(2);
            if (highlight) {
                el.style.transform = 'scale(1.05)';
                setTimeout(() => el.style.transform = '', 300);
            }
        }
    }
};

// ============================================
// PARTY SEARCH WITH AUTOCOMPLETE
// ============================================
function searchParty(input, type) {
    const query = input.value;
    if (query.length < 2) {
        hideAutocomplete();
        return;
    }
    
    fetch(`/ledgers/api/search?q=${encodeURIComponent(query)}&type=${type}`)
        .then(response => response.json())
        .then(parties => {
            showAutocomplete(input, parties);
        });
}

function showAutocomplete(input, items) {
    hideAutocomplete();
    
    if (items.length === 0) return;
    
    const dropdown = document.createElement('div');
    dropdown.id = 'autocomplete-dropdown';
    dropdown.className = 'autocomplete-dropdown';
    dropdown.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        max-height: 200px;
        overflow-y: auto;
        z-index: 100;
    `;
    
    items.forEach(item => {
        const option = document.createElement('div');
        option.className = 'autocomplete-option';
        option.style.cssText = 'padding: 10px 15px; cursor: pointer; border-bottom: 1px solid #f1f5f9;';
        option.textContent = item.name;
        option.onmouseover = () => option.style.background = '#f1f5f9';
        option.onmouseout = () => option.style.background = '';
        option.onclick = () => {
            input.value = item.name;
            if (document.getElementById('party_id')) {
                document.getElementById('party_id').value = item.id;
            }
            hideAutocomplete();
        };
        dropdown.appendChild(option);
    });
    
    input.parentElement.style.position = 'relative';
    input.parentElement.appendChild(dropdown);
}

function hideAutocomplete() {
    const dropdown = document.getElementById('autocomplete-dropdown');
    if (dropdown) dropdown.remove();
}

// ============================================
// DATE HELPERS
// ============================================
function setDefaultDate(inputId) {
    const input = document.getElementById(inputId);
    if (input && !input.value) {
        input.valueAsDate = new Date();
    }
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// ============================================
// PRINT HELPERS
// ============================================
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
        <head>
            <title>Print</title>
            <link rel="stylesheet" href="/static/css/main.css">
            <style>
                body { padding: 20px; }
                @media print { body { padding: 0; } }
            </style>
        </head>
        <body>${element.innerHTML}</body>
        </html>
    `);
    printWindow.document.close();
    printWindow.onload = () => {
        printWindow.print();
        printWindow.close();
    };
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

// Add slideUp animation keyframe
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);
