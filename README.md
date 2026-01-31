<div align="center">

<!-- Animated Header -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=180&section=header&text=🧾%20BillPro&fontSize=50&fontColor=fff&animation=twinkling&fontAlignY=32&desc=Complete%20Billing%20%26%20Accounting%20Software&descSize=18&descAlignY=55"/>

<p align="center">
  <strong>🚀 A powerful, GST-compliant billing solution built for Indian businesses</strong>
</p>

<!-- Badges Row 1 -->
<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"></a>
  <a href="https://www.sqlite.org/"><img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"></a>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<!-- Badges Row 2 -->
<p align="center">
  <img src="https://img.shields.io/badge/🇮🇳_Made_in-India-orange?style=flat-square" alt="Made in India">
  <img src="https://img.shields.io/badge/GST-Compliant-success?style=flat-square" alt="GST Compliant">
  <img src="https://img.shields.io/badge/Thermal_Printer-Supported-blue?style=flat-square" alt="Thermal Printer">
  <img src="https://img.shields.io/badge/E--Invoice-Ready-purple?style=flat-square" alt="E-Invoice">
  <img src="https://img.shields.io/badge/Offline-First-red?style=flat-square" alt="Offline First">
</p>

<br/>

<!-- Quick Links -->
<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-screenshots">Screenshots</a> •
  <a href="#️-configuration">Configuration</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-contributing">Contributing</a>
</p>

<br/>

<!-- Hero Banner -->
<img src="https://user-images.githubusercontent.com/placeholder/hero-banner.png" alt="BillPro Dashboard" width="90%"/>

</div>

---

## 🎯 Why BillPro?

<table>
<tr>
<td>

**BillPro** is not just another billing software – it's a **complete business management solution** designed specifically for Indian small and medium businesses. From generating GST-compliant invoices to managing inventory, tracking payments, and processing payroll – BillPro handles it all.

</td>
</tr>
</table>

<div align="center">

| 💡 **Simple** | ⚡ **Fast** | 🔒 **Secure** | 💰 **Free** |
|:---:|:---:|:---:|:---:|
| Easy to use interface | Instant invoice generation | Offline-first, your data stays local | Open source, no hidden costs |

</div>

---

## ✨ Features

<div align="center">

### 🏪 Everything Your Business Needs

</div>

<table>
<tr>
<td width="50%" valign="top">

### 📋 Billing & Invoicing
```
✅ GST-compliant invoices (CGST/SGST/IGST)
✅ Thermal printer support (58mm/80mm)
✅ A4 PDF invoice generation
✅ Multiple payment modes
✅ Bill preview before printing
✅ E-Invoice JSON generation (GST Portal ready)
✅ Auto invoice numbering
✅ Multiple tax rates support
```

### 📦 Inventory Management
```
✅ Product catalog with HSN codes
✅ Real-time stock tracking
✅ Low stock alerts
✅ Category management
✅ Stock adjustment with history
✅ Multiple units (KG, PCS, LTR, etc.)
✅ Cost & selling price tracking
✅ Barcode-ready
```

</td>
<td width="50%" valign="top">

### 👥 Party Ledgers
```
✅ Customer & Supplier management
✅ Party-wise transaction history
✅ Payment tracking
✅ Receivables & Payables
✅ Credit limit management
✅ Balance calculation
✅ Export to CSV
✅ GST details storage
```

### 💰 Accounting
```
✅ Daily cash book
✅ Bank account management
✅ Income & expense tracking
✅ GST reports (GSTR-1 format)
✅ Profit & Loss statements
✅ Financial year support
✅ Multi-account tracking
✅ Transaction categorization
```

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 👨‍💼 Payroll Management
```
✅ Employee master data
✅ Monthly salary processing
✅ Printable salary slips
✅ PF/ESI/TDS deductions
✅ Attendance-based calculation
✅ Bank account details
✅ Salary history
✅ Bulk processing
```

</td>
<td width="50%" valign="top">

### 📊 Reports & Analytics
```
✅ Sales reports (daily/monthly/yearly)
✅ Purchase reports
✅ Stock valuation report
✅ GST summary reports
✅ Party-wise outstanding
✅ Dashboard with insights
✅ Export capabilities
✅ Visual charts
```

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** installed on your system
- **pip** (Python package manager)

### 📥 Installation

```bash
# 1️⃣ Clone the repository
git clone https://github.com/AtharvaMeherkar/billpro-billing-software.git

# 2️⃣ Navigate to project folder
cd billpro-billing-software

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Run the application
python run.py
```

### 🌐 Access the Application

<div align="center">

| Open your browser and go to: |
|:---:|
| **http://localhost:5000** |

</div>

---

## 📸 Screenshots

<div align="center">

<i>🖼️ Screenshots coming soon!</i>

<!-- Add your screenshots here like this:
<img src="screenshots/dashboard.png" width="45%"/>
<img src="screenshots/invoice.png" width="45%"/>
-->

</div>

---

## 🖨️ Thermal Printer Setup

BillPro supports **58mm and 80mm thermal printers** out of the box!

### Supported Printers
- POS-58 Series
- Epson TM Series
- Any ESC/POS compatible printer

### Configuration

Edit `config/printer.json`:

```json
{
    "printer_type": "windows",
    "printer_name": "POS58 Printer",
    "paper_width": 58,
    "cut_paper": true
}
```

> 💡 **Tip**: Run `Get-Printer` in PowerShell to find your exact printer name

---

## ⚙️ Configuration

### 🏢 Company Details

Edit `config/company.json` to set your business information:

```json
{
  "name": "Your Business Name",
  "gstin": "YOUR15DIGITGSTIN",
  "address": {
    "line1": "Your Address",
    "city": "City",
    "state": "State",
    "pincode": "000000"
  },
  "contact": {
    "phone": "9999999999",
    "email": "email@example.com"
  }
}
```

---

## 📁 Project Structure

```
📦 BillPro
├── 📂 app/
│   ├── 📂 billing/          # 🧾 Invoice management
│   ├── 📂 inventory/        # 📦 Stock management
│   ├── 📂 ledgers/          # 👥 Party management
│   ├── 📂 accounting/       # 💰 Cash & bank
│   ├── 📂 payroll/          # 👨‍💼 Employee salaries
│   ├── 📂 einvoice/         # 📄 E-Invoice JSON
│   ├── 📂 reports/          # 📊 Business reports
│   ├── 📂 printing/         # 🖨️ Thermal printing
│   ├── 📂 models/           # 🗃️ Database models
│   ├── 📂 templates/        # 🎨 HTML templates
│   └── 📂 static/           # 📁 CSS, JS, images
├── 📂 config/               # ⚙️ Configuration files
├── 📂 database/             # 💾 SQLite database
├── 📄 run.py                # 🚀 Entry point
├── 📄 requirements.txt      # 📋 Dependencies
└── 📄 README.md             # 📖 You are here!
```

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|:---:|:---:|
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white) |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-red?style=flat) |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) |
| **PDF** | ![ReportLab](https://img.shields.io/badge/ReportLab-green?style=flat) |
| **Printing** | ![ESC/POS](https://img.shields.io/badge/ESC%2FPOS-blue?style=flat) ![Win32](https://img.shields.io/badge/Win32Print-orange?style=flat) |

</div>

---

## 📋 Requirements

```txt
Flask>=2.0.0
Flask-SQLAlchemy>=3.0.0
reportlab>=4.0.0
python-escpos>=3.0
Pillow>=10.0.0
pywin32>=306
```

---

## 🔜 Roadmap

<div align="center">

| Feature | Status |
|:---|:---:|
| Multi-user login system | 🔄 Planned |
| Barcode scanner integration | 🔄 Planned |
| WhatsApp bill sharing | 🔄 Planned |
| Cloud backup & sync | 🔄 Planned |
| Mobile responsive design | 🔄 Planned |
| Multi-branch support | 🔄 Planned |
| Purchase orders | 🔄 Planned |
| Quotation management | 🔄 Planned |

</div>

---

## 🤝 Contributing

Contributions are **welcome and appreciated**! Here's how you can help:

1. 🍴 **Fork** the repository
2. 🌿 Create a **feature branch** (`git checkout -b feature/AmazingFeature`)
3. 💾 **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. 📤 **Push** to the branch (`git push origin feature/AmazingFeature`)
5. 🔃 Open a **Pull Request**

### 💡 Ideas for Contribution
- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🎨 UI/UX enhancements
- 🌐 Translations

---

## 📄 License

<div align="center">

This project is licensed under the **MIT License**

See the [LICENSE](LICENSE) file for details

</div>

---

## 👤 Author

<div align="center">

**Atharva Meherkar**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/AtharvaMeherkar)

</div>

---

<div align="center">

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

<br/>

### 💬 Support

<p>
  <a href="https://github.com/AtharvaMeherkar/billpro-billing-software/issues">🐛 Report Bug</a>
  &nbsp;&nbsp;•&nbsp;&nbsp;
  <a href="https://github.com/AtharvaMeherkar/billpro-billing-software/issues">💡 Request Feature</a>
  &nbsp;&nbsp;•&nbsp;&nbsp;
  <a href="https://github.com/AtharvaMeherkar/billpro-billing-software/discussions">💬 Discussions</a>
</p>

---

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer"/>

**Made with ❤️ in India 🇮🇳**

<sub>© 2024-2026 BillPro. All rights reserved.</sub>

</div>
