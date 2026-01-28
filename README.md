<div align="center">

# 🧾 BillPro - Billing & Accounting Software

<p align="center">
  <strong>A complete billing, inventory, and accounting solution for Indian businesses</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/GST-Compliant-orange?style=flat-square" alt="GST">
  <img src="https://img.shields.io/badge/Thermal_Printer-Supported-blue?style=flat-square" alt="Thermal Printer">
  <img src="https://img.shields.io/badge/E--Invoice-Ready-success?style=flat-square" alt="E-Invoice">
</p>

---

**🚀 Built for small to medium businesses in India • GST-ready invoicing • Offline-first architecture**

</div>

## ✨ Features

<table>
<tr>
<td width="50%">

### 📋 Billing & Invoicing
- ✅ GST-compliant invoices (CGST/SGST/IGST)
- ✅ Thermal printer support (58mm/80mm)
- ✅ A4 PDF invoice generation
- ✅ Multiple payment modes (Cash/UPI/Card/Bank)
- ✅ Bill preview before printing
- ✅ E-Invoice JSON generation

</td>
<td width="50%">

### 📦 Inventory Management
- ✅ Product catalog with HSN codes
- ✅ Stock tracking & low stock alerts
- ✅ Category management
- ✅ Stock adjustment history
- ✅ Cost price & selling price tracking
- ✅ Multiple unit support (KG, PCS, LTR, etc.)

</td>
</tr>
<tr>
<td width="50%">

### 👥 Party Ledgers
- ✅ Customer & Supplier management
- ✅ Party-wise transaction history
- ✅ Payment tracking (receivables/payables)
- ✅ Balance calculation
- ✅ Credit limit management
- ✅ Export to CSV

</td>
<td width="50%">

### 💰 Accounting
- ✅ Daily cash book
- ✅ Income & expense tracking
- ✅ Bank account management
- ✅ GST reports (GSTR-1 format)
- ✅ Profit & Loss statements
- ✅ Financial year support

</td>
</tr>
<tr>
<td width="50%">

### 👨‍💼 Payroll Management
- ✅ Employee master data
- ✅ Monthly salary processing
- ✅ Salary slip generation
- ✅ PF/ESI/TDS deductions
- ✅ Attendance-based calculation
- ✅ Printable salary slips

</td>
<td width="50%">

### 📊 Reports & Analytics
- ✅ Sales reports (daily/monthly/yearly)
- ✅ Purchase reports
- ✅ Stock valuation report
- ✅ GST summary reports
- ✅ Party-wise outstanding
- ✅ Dashboard with insights

</td>
</tr>
</table>

---

## 🖥️ Screenshots

<div align="center">
<i>Coming soon</i>
</div>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AtharvaMeherkar/billpro-billing-software.git
cd billpro-billing-software

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python run.py
```

### 🌐 Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 📁 Project Structure

```
BillPro - Billing Software/
├── 📂 app/
│   ├── 📂 billing/          # Invoice creation & management
│   ├── 📂 inventory/        # Product & stock management
│   ├── 📂 ledgers/          # Customer & supplier ledgers
│   ├── 📂 accounting/       # Cash book & expenses
│   ├── 📂 payroll/          # Employee & salary management
│   ├── 📂 einvoice/         # E-Invoice JSON generation
│   ├── 📂 reports/          # Business reports
│   ├── 📂 models/           # Database models
│   ├── 📂 templates/        # HTML templates
│   └── 📂 static/           # CSS, JS, images
├── 📂 config/               # Configuration files
├── 📂 database/             # SQLite database
├── 📂 bill_templates/       # Invoice templates
├── 📄 run.py                # Application entry point
└── 📄 requirements.txt      # Python dependencies
```

---

## ⚙️ Configuration

### Company Details
Edit `config/company.json` to set your business information:
```json
{
  "name": "Your Business Name",
  "gstin": "YOUR15DIGITGSTIN",
  "address": {
    "line1": "Shop Address",
    "city": "City",
    "state": "State",
    "pincode": "000000"
  }
}
```

### Printer Settings
Edit `config/printer.json` for thermal printer:
```json
{
  "paper_width": 58,
  "printer_name": "POS-58"
}
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.10+, Flask 2.0+ |
| **Database** | SQLite with SQLAlchemy ORM |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **PDF Generation** | ReportLab |
| **Thermal Printing** | python-escpos |

---

## 📋 Requirements

```txt
Flask>=2.0.0
Flask-SQLAlchemy>=3.0.0
reportlab>=4.0.0
python-escpos>=3.0
Pillow>=10.0.0
```

---

## 🔜 Roadmap

- [ ] Multi-user login system
- [ ] Barcode scanner integration
- [ ] WhatsApp bill sharing
- [ ] Cloud backup & sync
- [ ] Mobile-responsive design
- [ ] Multi-branch support

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**
- GitHub: [AtharvaMeherkar](https://github.com/AtharvaMeherkar)

---

<div align="center">

### ⭐ Star this repository if you find it helpful!

<p>
  <a href="https://github.com/AtharvaMeherkar/billpro-billing-software/issues">Report Bug</a>
  •
  <a href="https://github.com/AtharvaMeherkar/billpro-billing-software/issues">Request Feature</a>
</p>

**Made with ❤️ in India**

</div>
