# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockScrapLog(models.Model):
    _name = 'stock.scrap.log'
    _description = 'Stock Scrap Log'
    _rec_name = 'name'  # Optional: Display this field in dropdowns

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    batch_id = fields.Char(string='Batch ID')
    quantity = fields.Float(string='Quantity', required=True)
    scrap_date = fields.Date(string='Scrap Date', default=fields.Date.today)
    reason = fields.Text(string='Reason')
    source_location_id = fields.Many2one('stock.location', string='Source Location')
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.scrap.log') or '/'
        return super(StockScrapLog, self).create(vals)
