from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class QualityCheck(models.Model):
    _name = 'quality.check'
    _description = 'Quality Check'
    incoming_id = fields.Many2one('incoming.stock', string="Incoming Stock")
    stock_id = fields.Char(related='incoming_id.stock_id', store=True, readonly=True, string="Stock ID")
    product_id = fields.Many2one(related='incoming_id.product_id', string="Product", store=True)
    quantity = fields.Float(related='incoming_id.quantity', string="Quantity", store=True)
    date = fields.Date(related='incoming_id.date', string="Date", store=True)
    passed_quantity = fields.Float(string="Passed Quantity", default=0.0, store=True)

    qc_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed')
    ], string="QC Status", default='not_started', tracking=True)

    qc_id = fields.Char(
        string="QC ID",
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    _rec_name = 'qc_id'

    def action_initiate_qc(self):
        for rec in self:
            if rec.qc_status == 'passed':
                raise UserError("This product has already passed Quality Check. You cannot initiate quality check.")
            if rec.qc_status == 'failed':
                raise UserError("This product has already failed Quality Check. You cannot initiate quality check.")

        for rec in self:
            if not rec.incoming_id:
                raise UserError("Select an incoming stock first.")
            rec.qc_status = 'pending'

    def action_pass_qc(self):
        for rec in self:
            if rec.qc_status == 'failed':
                raise UserError("This product has already failed Quality Check. You cannot mark it as passed.")

        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Select Shelf Location',
            'res_model': 'quality.check.pass.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_quality_check_id': self.id,
            },
        }

    def action_fail_qc(self):
        for rec in self:
            if rec.qc_status == 'passed':
                raise UserError("This product has already passed Quality Check. You cannot mark it as failed.")

            rec.qc_status = 'failed'
            incoming = rec.incoming_id

            # Create Scrap Log Record
            self.env['stock.scrap.log'].create({
                'product_id': rec.product_id.id,
                'batch_id': incoming.stock_id,
                'quantity': rec.quantity,
                'reason': 'Failed Quality Check',
                # 'source_location_id': incoming.source_location_id.id if incoming.source_location_id else None,
                'created_by': self.env.user.id,
            })

    @api.model
    def create(self, vals):
        # Set custom QC ID
        if vals.get('qc_id', 'New') == 'New':
            incoming = self.env['incoming.stock'].browse(vals.get('incoming_id'))
            if incoming and incoming.stock_id:
                vals['qc_id'] = f"QC/{incoming.stock_id}"
            else:
                vals['qc_id'] = self.env['ir.sequence'].next_by_code('quality.check') or '/'

        # Create the record
        res = super(QualityCheck, self).create(vals)

        # Mark incoming line as having a QC
        if res.incoming_id:
            res.incoming_id.qc_done = True

        return res

    status_icon = fields.Html(string="Status", compute="_compute_status_icon", store=True)

    @api.depends('qc_status')
    def _compute_status_icon(self):
        for rec in self:
            color = {
                'pending': 'orange',
                'passed': 'green',
                'failed': 'red'
            }.get(rec.qc_status, 'gray')

            tooltip = {
                'pending': 'Pending',
                'passed': 'Passed',
                'failed': 'Failed'
            }.get(rec.qc_status, 'Unknown')

            rec.status_icon = f"""
                    <div title="{tooltip}" style="
                        width: 14px; height: 14px;
                        border-radius: 50%;
                        background-color: {color};
                        display: inline-block;
                        margin: auto;
                    "></div>
                """

    can_initiate_qc = fields.Boolean(compute="_compute_button_visibility", store=True)
    can_pass_qc = fields.Boolean(compute="_compute_button_visibility", store=True)
    can_fail_qc = fields.Boolean(compute="_compute_button_visibility", store=True)

    @api.depends('qc_status')
    def _compute_button_visibility(self):
        for rec in self:
            rec.can_initiate_qc = rec.qc_status not in ['pending', 'passed', 'failed']
            rec.can_pass_qc = rec.qc_status == 'pending'
            rec.can_fail_qc = rec.qc_status == 'pending'

    @api.onchange('qc_status')
    def _onchange_qc_status(self):
        self._compute_button_visibility()
