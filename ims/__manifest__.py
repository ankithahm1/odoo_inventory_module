# -*- coding: utf-8 -*-
{
    'name': "Inventory Management System",

    'summary': 'Smart Inventory and Manufacturing with Component Request Management',

    'description': """
Smart Inventory and Manufacturing system with features like:
- Component request handling
- Incoming stock tracking
- Quality checks
- Low stock notifications
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Inventory',
    'version': '0.1',

    'depends': ['base', 'product', 'stock', 'mail', 'mrp', 'sale', 'purchase', 'web'],

    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/ims_security.xml',  # groups + access rights
        'security/ims_rules.xml',  # record rules

        # Views
        'views/resUser.xml',
        'views/templates.xml',
        'views/incoming_stock_views.xml',
        'views/quality_check_views.xml',
        'views/warehouse_views.xml',
        'views/quality_check_pass_wizard_view.xml',
        'views/scrap_logs_views.xml',
        'views/passed_stock_views.xml',
        'views/ims_product_request_views.xml',
        'views/ims_product_sending_views.xml',
        'views/bom_views.xml',
        'views/actions.xml',
        'views/views.xml',

        # Wizards
        'wizards/purchase_confirm.xml',

        # Data
        'data/low_stock_cron.xml',
        'data/low_stock_email_template.xml',
        'data/incoming_stock_sequence.xml',
        'data/quality_check_sequence.xml',
        'data/scrap_logs_sequence.xml',
        'data/ims_request_sequences.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'ims/static/src/dashboard/dashboard.js',
            'ims/static/src/dashboard/dashboard.xml',
        ],
    },

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
