from odoo import models, fields

class PurchaseConfirmPopup(models.TransientModel):
    _name = 'purchase.confirm.popup'
    _description = 'Confirm Raw Material Purchase'

    mo_id = fields.Many2one('mrp.production', string='Manufacturing Order')

    def confirm(self):
        print("DEBUG: Wizard confirm triggered")
        self.mo_id.create_po_for_short_materials()
        return {'type': 'ir.actions.act_window_close'}
