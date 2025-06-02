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
