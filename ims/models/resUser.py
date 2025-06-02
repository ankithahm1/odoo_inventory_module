from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    x_warehouse_access_id = fields.Many2one(
        'stock.warehouse',
        string='Accessible Warehouse'
    )
