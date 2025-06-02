from odoo import models, fields, api


class IncomingStock(models.Model):
    _name = 'incoming.stock'
    _description = 'Incoming Stock'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # ✅ Add this line


    product_id = fields.Many2one('product.product', string="Product", required=True)
    batch_id = fields.Char(string="Batch ID")
    quantity = fields.Float(string="Quantity", required=True)
    unit_price = fields.Float(string="Unit Price", required=True)  # ← Add this line
    date = fields.Date(string="Date", default=fields.Date.today)
    location_id = fields.Many2one(
        'stock.location',
        string="Warehouse Location",
        domain="[('usage', '=', 'internal')]",
        required=True
    )
    reference = fields.Char(string="Reference")
    supplier_id = fields.Many2one('res.partner', string="Supplier", domain="[('supplier_rank', '>', 0)]")
    # state = fields.Selection([
    #     ('draft', 'Incoming'),
    #     ('quality_check', 'Quality Check'),
    #     ('received', 'At Warehouse'),
    # ], string="Status", default='draft', tracking=True)
    qc_status = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed')
    ], string="QC Status")

    shelf_location_id = fields.Many2one(
        'stock.location',
        string="Shelf Location",
        domain="[('usage', '=', 'internal')]"
    )

    stock_id = fields.Char(
        string="Stock ID",
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    _rec_name = 'stock_id'
    state = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'),
    ], string='State', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('stock_id', 'New') == 'New':
            vals['stock_id'] = self.env['ir.sequence'].next_by_code('incoming.stock') or '/'
        return super(IncomingStock, self).create(vals)

    def name_get(self):
        result = []
        for record in self:
            name = record.stock_id or 'Unnamed'
            result.append((record.id, name))
        return result

    @api.onchange('qc_status')
    def _onchange_qc_status_create_scrap(self):
        for record in self:
            if record.qc_status == 'failed':
                self.env['stock.scrap.log'].create({
                    'product_id': record.product_id.id,
                    'batch_id': record.batch_id,
                    'quantity': record.quantity,
                    'reason': 'Failed Quality Check',
                    'source_location_id': record.location_id.id,
                })

    # still in incoming_stock.py
    quality_check_ids = fields.One2many(
        'quality.check', 'incoming_id', string='QC Lines', readonly=True
    )

    qc_done = fields.Boolean(
        string='QC Done',
        compute='_compute_qc_done',
        store=True,
        index=True,
    )

    # one QC line may exist, but we use count() so it works even if you allow many
    @api.depends('quality_check_ids.qc_status')
    def _compute_qc_done(self):
        for rec in self:
            rec.qc_done = bool(rec.quality_check_ids)

    # def action_start_qc(self):
    #     for rec in self:
    #         rec.state = 'quality_check'
    #
    # def action_receive(self):
    #     for rec in self:
    #         rec.state = 'received'
    #
    # def action_start_quality_check(self):
    #     for rec in self:
    #         quality_check = self.env['quality.check'].create({
    #             'incoming_id': rec.id
    #         })
    #         rec.state = 'quality_check'
    #
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'quality.check',
    #             'res_id': quality_check.id,
    #             'view_mode': 'form',
    #             'target': 'new',
    #         }
    #
