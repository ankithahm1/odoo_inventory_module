# 🧾 Odoo Inventory Management System

A custom Odoo module built with Python and PostgreSQL to manage and streamline inventory workflows.

## 🚀 Features

- 📦 Product & Incoming Stock Management  
- 🏗️ Bill of Materials (BoM) Integration  
- ✅ Quality Checks (Pass/Fail Tracking)  
- 🏢 Warehouse & Inter-Warehouse Transfers  
- 🔐 Role-Based Access for Manager/Admin  
- 📧 Automated Email Notifications for Stakeholder Updates

## 📂 Module Structure

odoo_inventory_module/
├── models/
│ ├── incoming_stock.py
│ ├── quality_check.py
│ ├── passed_stock.py
│ └── ...
├── views/
├── wizards/
├── security/
├── manifest.py
└── init.py

markdown
Copy
Edit

## ⚙️ Installation

1. Clone the repository inside your Odoo `custom_addons` directory
2. Restart your Odoo server
3. Install the module from the Apps menu

```bash
git clone https://github.com/ankithahm1/odoo_inventory_module.git
🛠️ Tech Stack
Python

PostgreSQL

Odoo 18.0

XML (Views & Security Rules)

🤝 Contributions
Open to improvements! Feel free to fork the repo, submit PRs, or raise issues.
