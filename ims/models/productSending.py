from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

class ImsProductSending(models.Model):
    _name = 'ims.product.sending'
    _description = 'IMS Product Sending'
    _order = 'create_date desc'

    name = fields.Char(string='Sending Reference', required=True, copy=False, default='New')
    linked_request_id = fields.Many2one('ims.product.request', string='Request ID', required=True)
    responding_warehouse_id = fields.Many2one('stock.warehouse', string='Destination Warehouse', required=True)
    response_line_ids = fields.One2many('ims.product.sending.line', 'sending_id', string='Shipped Products')
    shipped_by = fields.Many2one('res.users', string='Shipped By')
    shipped_date = fields.Datetime(string='Shipped Date')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('shipped', 'Shipped'),
    ], string='Status', default='pending', tracking=True)
    sending_warehouse_id = fields.Many2one(
        'stock.warehouse', string='Source Warehouse', required=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code('ims.product.sending') or 'New'
        return super(ImsProductSending, self).create(vals)

# action when an order is accepted and send mail
    def action_accept(self):
        self.ensure_one()
        print("🚀 [DEBUG] action_accept started for Sending ID:", self.id)

        StockQuant = self.env['stock.quant'].sudo()

        try:
            for line in self.response_line_ids.sudo():

                available_qty = StockQuant._get_available_quantity(
                    line.product_id,
                    self.sending_warehouse_id.lot_stock_id  # ✅ this is the source warehouse
                )

                print(f"🔎 [DEBUG] Available quantity: {available_qty}")
                if available_qty < line.quantity:
                    print(f"❌ [DEBUG] Insufficient stock for product {line.product_id.display_name}")
                    raise UserError(
                        _("Not enough stock for product %s. Available: %s, Required: %s") % (
                            line.product_id.display_name, available_qty, line.quantity)
                    )
        except Exception as e:
            print(f"❗️ [ERROR] Exception during stock check: {e}")
            raise

        print("✅ [DEBUG] All products have sufficient stock. Setting state to 'accepted'.")
        self.state = 'accepted'

        try:
            linked_request = self.linked_request_id.sudo()
            requested_by = linked_request.requested_by.sudo()
            if requested_by.email:
                recipient = requested_by.email
                print(f"✉️ [DEBUG] Preparing to send acceptance email to {recipient}")
                subject = f"Your Product Request {linked_request.name} is Accepted"
                body = f"""
                    Dear {requested_by.name},<br/><br/>
                    Your product request <b>{linked_request.name}</b> has been accepted.<br/><br/>
                    Regards,<br/>
                    IMS System
                """
                self.env['mail.mail'].sudo().create({
                    'subject': subject,
                    'body_html': body,
                    'email_to': recipient,
                    'email_from': self.env.user.email or 'letstest0123@gmail.com',
                }).send()
                print("📧 [DEBUG] Acceptance email sent successfully.")
            else:
                print("⚠️ [DEBUG] No linked request or requester email; skipping email.")
        except Exception as e:
            print(f"❗️ [ERROR] Exception during email sending: {e}")
            raise

# action when an order is rejected and mailed
    def action_reject(self):
        for rec in self:
            _logger.info(f"🚀 [DEBUG] action_reject started for Sending ID: {rec.id}")

            rec.state = 'rejected'

            # Send rejection email to requester
            try:
                linked_request = rec.linked_request_id.sudo()
                requested_by = linked_request.requested_by.sudo()
                subject = f"Product Request Rejected - {linked_request.name or 'N/A'}"
                body = f"""
                    Dear {requested_by.name or 'User'},<br/><br/>
                    Your product request with reference <b>{linked_request.name}</b> has been <b>rejected</b>.<br/><br/>
                    Regards,<br/>
                    IMS System
                """
                email_to = requested_by.email
                if email_to:
                    self.env['mail.mail'].sudo().create({
                        'subject': subject,
                        'body_html': body,
                        'email_to': email_to,
                        'email_from': self.env.user.email or 'letstest0123@gmail.com',
                    }).send()
                    _logger.info(f"📧 [DEBUG] Rejection email sent to: {email_to}")
                else:
                    _logger.warning(f"⚠️ [WARN] No email found for user {requested_by.name}")
            except Exception as e:
                _logger.error(f"❗️ [ERROR] Exception during sending rejection email: {str(e)}")

# action when an order is shipped and mailed
    def action_ship(self):
        for rec in self:
            _logger.info(f"🚀 [DEBUG] action_ship started for Sending ID: {rec.id}")

            if not rec.response_line_ids:
                _logger.warning(f"⚠️ [WARN] No products to ship for Sending ID: {rec.id}")
                raise ValidationError("You must add at least one product to ship.")

            source_location = rec.sending_warehouse_id.lot_stock_id
            dest_location = rec.responding_warehouse_id.lot_stock_id

            Picking = self.env['stock.picking'].sudo()

            picking_type = self.env['stock.picking.type'].sudo().search([
                ('warehouse_id', '=', rec.sending_warehouse_id.id),
                ('code', '=', 'internal')
            ], limit=1)

            if not picking_type:
                raise UserError("No internal picking type found for the sending warehouse.")

            picking = Picking.create({
                'picking_type_id': picking_type.id,
                'location_id': source_location.id,
                'location_dest_id': dest_location.id,
                'origin': rec.name or f"Transfer for Sending ID {rec.id}",
                'move_ids_without_package': [(0, 0, {
                    'name': line.product_id.display_name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': source_location.id,
                    'location_dest_id': dest_location.id,
                }) for line in rec.response_line_ids],
            })

            picking.action_confirm()
            picking.action_assign()

            # Ensure move lines exist and set quantity done
            for move in picking.move_ids:
                if not move.move_line_ids:
                    move._generate_move_line()
                for move_line in move.move_line_ids:
                    move_line.quantity = move.product_uom_qty

            # Validate the picking (process the stock move)
            picking.button_validate()

            # Update IMS record state
            rec.state = 'shipped'
            rec.shipped_by = self.env.user
            rec.shipped_date = fields.Datetime.now()

            try:
                linked_request = rec.linked_request_id.sudo()
                requested_by = linked_request.requested_by.sudo()
                subject = f"Product Request Shipped - {linked_request.name or 'N/A'}"
                body = f"""
                    Dear {requested_by.name or 'User'},<br/><br/>
                    Your product request with reference <b>{linked_request.name}</b> has been <b>shipped</b>.<br/><br/>
                    Regards,<br/>
                    IMS System
                """
                email_to = requested_by.email
                if email_to:
                    self.env['mail.mail'].sudo().create({
                        'subject': subject,
                        'body_html': body,
                        'email_to': email_to,
                        'email_from': self.env.user.email or 'letstest0123@gmail.com',
                    }).send()
                    _logger.info(f"📧 [DEBUG] Shipping email sent to: {email_to}")
                else:
                    _logger.warning(f"⚠️ [WARN] No email found for user {requested_by.name}")
            except Exception as e:
                _logger.error(f"❗️ [ERROR] Exception during sending shipping email: {str(e)}")


class ImsProductSendingLine(models.Model):
    _name = 'ims.product.sending.line'
    _description = 'IMS Product Sending Line'

    sending_id = fields.Many2one('ims.product.sending', string='Sending')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)
