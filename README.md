# 🧾 Odoo Inventory Management System

A custom Odoo module built with Python and PostgreSQL to manage and streamline inventory workflows.

## 🚀 Features

📦 Product Management

Create, update, and manage product details including specifications, categories, and associated BoMs.

📥 Incoming Stock Management

Track incoming stock entries and map them to products and BoMs. Ensure all items are logged before processing.

✅ Quality Checks (Pass/Fail Tracking)

Passed items are added to stock and update existing quantities.

Failed items are redirected to a scrap repository with traceability.

🏢 Warehouse and Internal Shelf Location Management

Organize and manage inventory across multiple warehouses and shelf-level locations for efficient access and auditing.

🔄 Inter-Warehouse Transfers with Approval Workflow

Movement of stock between warehouses requires approval from warehouse managers, ensuring accountability and control.

🔐 Role-Based Access for Manager and Admin

Access is restricted by user roles:

- Managers can manage stock and approve transfers

- Admins have full access to configuration and operations

📧 Automated Email Notifications

Notifications sent automatically to warehouse managers and admins for key actions such as quality check results, stock updates, and transfer approvals.

## 📂 Module Structure

ims/
├── controllers/
│   ├── __init__.py
│   └── controllers.py
├── data/
│   ├── ims_request_sequences.xml
│   ├── incoming_stock_sequence.xml
│   ├── low_stock_cron.xml
│   ├── low_stock_email_template.xml
│   ├── quality_check_sequence.xml
│   └── scrap_logs_sequence.xml
├── demo/
│   └── demo.xml
├── models/
│   ├── __init__.py
│   ├── bom_component.py
│   ├── bom_master.py
│   ├── incoming_stock.py
│   ├── lowstocknotify.py
│   ├── mrpProduction.py
│   ├── orderinherited.py
│   ├── passed_stock.py
│   ├── productRequest.py
│   ├── productSending.py
│   ├── productTemplate.py
│   ├── quality_check.py
│   ├── quality_check_pass_wizard.py
│   ├── resUser.py
│   └── stock_scrap_log.py
├── security/
│   ├── ims_rules.xml
│   ├── ims_security.xml
│   └── ir.model.access.csv
├── static/
│   └── description/
│       └── icon.png
│   └── src/dashboard/
│       ├── dashboard.js
│       └── dashboard.xml
├── views/
│   ├── actions.xml
│   ├── bom_views.xml
│   ├── ims_product_request_views.xml
│   ├── ims_product_sending_views.xml
│   ├── incoming_stock_views.xml
│   ├── passed_stock_views.xml
│   ├── quality_check_pass_wizard_view.xml
│   ├── quality_check_views.xml
│   ├── resUser.xml
│   ├── scrap_logs_views.xml
│   ├── templates.xml
│   ├── views.xml
│   └── warehouse_views.xml
├── wizards/
│   ├── __init__.py
│   ├── purchase_confirm.xml
│   └── purchaseConfirm.py
├── __init__.py
└── __manifest__.py


## ⚙️ Installation

1. Clone the repository inside your Odoo `custom_addons` directory
2. Restart your Odoo server
3. Install the module from the Apps menu


🛠️ Tech Stack
Python

PostgreSQL

Odoo 18.0

XML (Views & Security Rules)

🤝 Contributions
Open to improvements! Feel free to fork the repo, submit PRs, or raise issues.
