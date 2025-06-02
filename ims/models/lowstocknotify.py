from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()

        for picking in self:
            low_stock_products = []

            for move in picking.move_ids:
                product = move.product_id
                qty_available = product.qty_available

                # Check for replenishment rule (orderpoint)
                orderpoint = self.env['stock.warehouse.orderpoint'].sudo().search([
                    ('product_id', '=', product.id)
                ], limit=1)

                min_qty = orderpoint.product_min_qty if orderpoint else 0.0

                if min_qty:
                    _logger.info(f"🔍 Threshold (min_qty): {min_qty}")
                else:
                    _logger.warning(f"⚠️ No threshold set for {product.display_name}")

                if min_qty and qty_available < min_qty:
                    _logger.warning(f"⚠️ LOW STOCK: {product.display_name} — {qty_available} < {min_qty}")
                    low_stock_products.append(product.display_name)

            # ✅ Send one email if at least one product is low
            if low_stock_products:
                try:
                    template = self.env.ref(
                        'inventory__mrp.email_template_low_stock_alert_sale', raise_if_not_found=False
                    )
                    if template:
                        # Inject custom context for email template
                        ctx = {
                            'default_low_stock_products': ', '.join(low_stock_products),
                        }
                        template.sudo().with_context(ctx).send_mail(picking.id, force_send=True)
                        _logger.info("✅ Email sent with low stock list.")
                    else:
                        _logger.warning("❌ Email template not found.")
                except Exception as e:
                    _logger.warning(f"❌ Failed to send email: {e}")

        return res
