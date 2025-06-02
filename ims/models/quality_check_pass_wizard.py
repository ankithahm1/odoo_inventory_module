from odoo import models, fields, api
from odoo.exceptions import UserError

class QualityCheckPassWizard(models.TransientModel):
    _name = 'quality.check.pass.wizard'
    _description = 'Quality Check Pass Wizard'

    shelf_location_id = fields.Many2one(
        'stock.location',
        string="Shelf Location",
        required=True,
        domain=[('usage', '=', 'internal')]
    )
    quality_check_id = fields.Many2one('quality.check', string="Quality Check")
    passed_quantity = fields.Float(string="Passed Quantity", required=True)

    @api.onchange('quality_check_id')
    def _onchange_quality_check_id(self):
        if self.quality_check_id:
            self.passed_quantity = self.quality_check_id.quantity

    def action_confirm_pass(self):
        self.ensure_one()
        qc = self.quality_check_id
        if not qc:
            raise UserError("No Quality Check record found.")

        total_qty = qc.quantity
        passed_qty = self.passed_quantity
        if passed_qty < 0 or passed_qty > total_qty:
            raise UserError("Passed quantity must be between 0 and total quantity.")

        # Mark QC as passed
        qc.qc_status = 'passed'
        qc.passed_quantity = passed_qty

        # Search or create the PassedStock for this product
        passed_stock = self.env['passed.stock'].search([
            ('product_id', '=', qc.product_id.id)
        ], limit=1)

        if not passed_stock:
            passed_stock = self.env['passed.stock'].create({
                'product_id': qc.product_id.id,
            })

        # Create a new line in PassedStockLine
        self.env['passed.stock.line'].create({
            'passed_stock_id': passed_stock.id,
            'shelf_location_id': self.shelf_location_id.id,
            'quantity': passed_qty,
            'price_unit': qc.incoming_id.unit_price,
            'qc_id': qc.id,
        })

        # Scrap the remaining quantity
        failed_qty = total_qty - passed_qty
        if failed_qty > 0:
            self.env['stock.scrap.log'].create({
                'product_id': qc.product_id.id,
                'batch_id': qc.incoming_id.stock_id,
                'quantity': failed_qty,
                'reason': 'Failed Quantity after Partial QC Pass',
                'source_location_id': qc.incoming_id.location_id.id if qc.incoming_id.location_id else None,
                'created_by': self.env.user.id,
            })

        # Optional: Store shelf location in incoming record
        qc.incoming_id.shelf_location_id = self.shelf_location_id.id
