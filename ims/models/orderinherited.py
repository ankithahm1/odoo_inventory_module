from odoo import models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        _logger.info("🚨 Custom action_confirm triggered!")

        for order in self:
            for line in order.order_line:
                product = line.product_id
                _logger.info("🔍 Product: %s | Type: %s", product.display_name, product.type)
                _logger.info("🔢 Requested: %s | Available: %s", line.product_uom_qty, product.qty_available)

                # ✅ No product type check
                if line.product_uom_qty > product.qty_available:
                    raise UserError(_(
                        "Cannot confirm the order!\n"
                        "Not enough stock for '%s'.\n"
                        "Requested: %s | Available: %s"
                    ) % (
                                        product.display_name,
                                        line.product_uom_qty,
                                        product.qty_available,
                                    ))

        return super().action_confirm()
