from odoo import models, fields, api, _

class productTemplate(models.Model):
    _inherit = "product.template"

    list_price = fields.Float(tracking=True)
