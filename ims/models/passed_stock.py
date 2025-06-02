from odoo import models, fields, api

class PassedStock(models.Model):
    _name = 'passed.stock'
    _description = 'Passed Stock'
    _rec_name = 'display_name'  # <-- this controls the top label


    product_id = fields.Many2one('product.product', string="Product", required=True, readonly=True)
    total_quantity = fields.Float(string="Total Quantity", compute="_compute_total_quantity", store=True)
    total_valuation = fields.Float(string="Total Value", compute="_compute_total_quantity", store=True)
    line_ids = fields.One2many('passed.stock.line', 'passed_stock_id', string="Shelf Lines")
    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True)


    @api.depends('line_ids.quantity', 'line_ids.price_unit')
    def _compute_total_quantity(self):
        for record in self:
            total_qty = sum(line.quantity for line in record.line_ids)
            total_value = sum(line.quantity * line.price_unit for line in record.line_ids)
            record.total_quantity = total_qty
            record.total_valuation = total_value

    @api.depends('product_id')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.product_id.name or 'Unnamed'


class PassedStockLine(models.Model):
    _name = 'passed.stock.line'
    _description = 'Passed Stock Line'

    passed_stock_id = fields.Many2one('passed.stock', string="Passed Stock", required=True, ondelete='cascade')
    shelf_location_id = fields.Many2one('stock.location', string="Shelf Location", required=True)
    quantity = fields.Float(string="Quantity", required=True)
    price_unit = fields.Float(string="Price/Unit", required=True)
    qc_id = fields.Many2one('quality.check', string="QC Reference", readonly=True)
