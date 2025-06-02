from odoo import models, fields, api
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    raw_materials_short = fields.Boolean(
        string="Raw Materials Shortage",
        compute='_compute_raw_materials_short'
    )
    is_po_created = fields.Boolean(string="Raw Materials Ordered", default=False)

    @api.depends('bom_id', 'product_qty', 'move_raw_ids', 'location_src_id')
    def _compute_raw_materials_short(self):
        for mo in self:
            shortage = False
            location = mo.location_src_id or mo.location_id
            print(f"\n🔍 MO: {mo.name} (Location: {location.display_name})")

            if mo.bom_id:
                print("📦 Using BoM lines")
                component_lines = [
                    (line.product_id, line.product_qty * mo.product_qty)
                    for line in mo.bom_id.bom_line_ids
                ]
            else:
                print("🛠️ Using manually added components")
                component_lines = [
                    (move.product_id, move.product_uom_qty)
                    for move in mo.move_raw_ids if move.product_id
                ]

            for product, required_qty in component_lines:
                forecast_qty = product.with_context(location=location.id).virtual_available
                print(f"➡️ {product.name} | Required: {required_qty} | Forecast: {forecast_qty}")

                if forecast_qty < required_qty:
                    print(f"❌ SHORTAGE: {product.name}")
                    shortage = True
                    break

            mo.raw_materials_short = shortage
            print(f"✅ {mo.name} | Shortage Detected: {shortage}")

    def action_purchase_raw_material(self):
        if self.is_po_created:
            raise UserError("Raw materials have already been ordered for this Manufacturing Order.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm Purchase',
            'res_model': 'purchase.confirm.popup',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_mo_id': self.id}
        }

    def create_po_for_short_materials(self):
        PurchaseOrder = self.env['purchase.order']
        for mo in self:
            location = mo.location_src_id or mo.location_id

            if mo.bom_id:
                component_lines = [
                    (line.product_id, line.product_qty * mo.product_qty)
                    for line in mo.bom_id.bom_line_ids
                ]
            else:
                component_lines = [
                    (move.product_id, move.product_uom_qty)
                    for move in mo.move_raw_ids if move.product_id
                ]

            for product, required_qty in component_lines:
                forecast_qty = product.with_context(location=location.id).virtual_available
                if forecast_qty < required_qty:
                    shortage_qty = required_qty - forecast_qty
                    supplier = product.seller_ids and product.seller_ids[0].partner_id
                    if not supplier:
                        raise UserError(f"No supplier found for product: {product.name}")

                    po_vals = {
                        'partner_id': supplier.id,
                        'origin': mo.name,
                        'order_line': [(0, 0, {
                            'product_id': product.id,
                            'name': product.name,
                            'product_qty': shortage_qty,
                            'product_uom': product.uom_po_id.id,
                            'price_unit': product.standard_price,
                            'date_planned': fields.Datetime.now(),
                        })],
                    }
                    PurchaseOrder.create(po_vals)
        self.is_po_created = True
