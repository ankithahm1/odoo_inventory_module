from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class ImsProductRequest(models.Model):
    _name = 'ims.product.request'
    _description = 'IMS Product Request'
    _order = 'create_date desc'

    name = fields.Char(string='Request Reference', required=True, copy=False, default='New')
    requesting_warehouse_id = fields.Many2one('stock.warehouse', string='From Warehouse', required=True)
    requested_warehouse_id = fields.Many2one('stock.warehouse', string='To Warehouse', required=True)
    request_line_ids = fields.One2many('ims.product.request.line', 'request_id', string='Requested Products')
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user)
    requested_date = fields.Datetime(string='Requested Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('arrived', 'Arrived'),
        ('acknowledged', 'Acknowledged'),
    ], string='Status', default='draft', tracking=True)
    linked_sending_id = fields.Many2one('ims.product.sending', string="Related Sending")

# to generate sequence number
    @api.model
    def create(self, vals):
        _logger.info(f"Creating ims.product.request with vals: {vals}")

        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code('ims.product.request') or _('New')
        return super(ImsProductRequest, self).create(vals)

# to automatically set warehouse when logged in user is attached to a warehouse
    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if 'requested_warehouse_id' in fields_list and not defaults.get('requested_warehouse_id'):
            user_warehouse = self.env.user.x_warehouse_access_id
            if user_warehouse:
                defaults['requested_warehouse_id'] = user_warehouse.id
        return defaults

# to make the field readonly when the logged in user is attached to a warehouse
    is_destination_readonly = fields.Boolean(
        string="Readonly Destination", compute="_compute_destination_readonly"
    )

    @api.depends('requested_warehouse_id')
    def _compute_destination_readonly(self):
        for record in self:
            record.is_destination_readonly = bool(self.env.user.x_warehouse_access_id)

    # Validation: prevent same source/destination warehouse
    @api.onchange('requesting_warehouse_id', 'requested_warehouse_id')
    def _onchange_check_same_warehouse(self):
        if self.requesting_warehouse_id and self.requested_warehouse_id:
            if self.requesting_warehouse_id == self.requested_warehouse_id:
                raise ValidationError("Requesting and Requested warehouses must be different.")

# action to create a request and create a entry in sending table
    def action_request(self):
        for rec in self:
            if not rec.request_line_ids or any(line.quantity <= 0 for line in rec.request_line_ids):
                raise UserError("You must add at least one product with quantity greater than zero before sending.")

            rec.state = 'requested'
            rec.requested_date = fields.Datetime.now()
            sending = self.env['ims.product.sending'].sudo().create({
                'linked_request_id': rec.id,
                'responding_warehouse_id': rec.requested_warehouse_id.id,  # Receiving warehouse
                'sending_warehouse_id': rec.requesting_warehouse_id.id,  # Source warehouse (new field)
                'response_line_ids': [
                    (0, 0, {
                        'product_id': line.product_id.id,
                        'quantity': line.quantity,
                    }) for line in rec.request_line_ids.sudo()
                ]
            })

            # Link it back (this write happens as normal user)
            rec.linked_sending_id = sending.id

            # Send email notification
            self._send_warehouse_request_email(rec)

    def _send_warehouse_request_email(self, rec):
        warehouse = rec.requested_warehouse_id
        users = self.env['res.users'].sudo().search([('x_warehouse_access_id', '=', warehouse.id)])

        if not users:
            return  # No users to notify

        email_to = ",".join(user.email for user in users if user.email)
        if not email_to:
            return  # No valid email addresses

        subject = f"New Product Request for {warehouse.name}"
        body = f"""
            Dear Warehouse Manager,<br/><br/>
            A new product request has been created for <b>{warehouse.name}</b>.<br/>
            Requested by: {rec.requested_by.name}<br/>
            Date: {rec.requested_date.strftime('%Y-%m-%d %H:%M:%S')}<br/><br/>
            <b>Requested Items:</b><br/>
            <ul>
                {''.join(f'<li>{line.product_id.display_name} - {line.quantity}</li>' for line in rec.request_line_ids.sudo())}
            </ul>
            <br/>
            Regards,<br/>
            IMS System
        """

        self.env['mail.mail'].sudo().create({
            'subject': subject,
            'body_html': body,
            'email_to': email_to,
            'email_from': self.env.user.email or 'letstest0123@gmail.com',
        }).send()
    arrived_date = fields.Datetime(string='Arrival Date', readonly=True)

# action to mark it as arrived
    def action_arrived(self):
        for rec in self:
            if not rec.linked_sending_id or rec.linked_sending_id.sudo().state != 'shipped':
                raise ValidationError("Cannot mark as arrived unless the linked sending order is shipped.")
            rec.state = 'arrived'
            rec.arrived_date = fields.Datetime.now()
#acknowledge ment mail
    def action_acknowledge(self):
        self.state = 'acknowledged'

        sending = self.linked_sending_id.sudo()
        if sending and sending.responding_warehouse_id:
            # Find users assigned to responding warehouse
            users = self.env['res.users'].sudo().search([('x_warehouse_access_id', '=', sending.responding_warehouse_id.id)])
            email_to = ",".join(user.email for user in users if user.email)
            if email_to:
                subject = f"Shipment Received - Thank You"
                body = f"""
                    Dear Warehouse Team,<br/><br/>
                    Thank you for the shipment from <b>{sending.responding_warehouse_id.name}</b>.<br/>
                    The shipment has been acknowledged by the receiving warehouse.<br/><br/>
                    Regards,<br/>
                    IMS System
                """
                self.env['mail.mail'].sudo().create({
                    'subject': subject,
                    'body_html': body,
                    'email_to': email_to,
                    'email_from': self.env.user.email or 'letstest0123@gmail.com',
                }).send()


class ImsProductRequestLine(models.Model):
    _name = 'ims.product.request.line'
    _description = 'IMS Product Request Line'

    request_id = fields.Many2one('ims.product.request', string='Request')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)
