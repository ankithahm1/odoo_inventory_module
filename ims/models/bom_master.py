from odoo import models, fields, api
class BOMMaster(models.Model):
    _name = 'bom.master'
    _description = 'Bill of Materials Master'

    name = fields.Char(string='BOM ID', required=True)
    model_no = fields.Char(string='Model No')
    customer = fields.Char(string='Customer')
    category = fields.Char(string='Category')
    created_date = fields.Datetime(string='Created Date')
    created_by = fields.Char(string='Created By')
    scan_ic_qty = fields.Integer(string='Scan IC Qty')
    driver_ic_qty = fields.Integer(string='Driver IC Qty')
    rok_cost = fields.Float(string='ROK Cost')
    ntf_cost = fields.Float(string='NTF Cost')
    ber_cost = fields.Float(string='BER Cost')
    tft = fields.Char(string='TFT')
    cf = fields.Char(string='CF')
    updated_date = fields.Datetime(string='Updated Date')
    updated_by = fields.Char(string='Updated By')
    approved_date = fields.Datetime(string='Approved Date')
    approved_by = fields.Char(string='Approved By')
    approved_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Approval Status', default='pending')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('archived', 'Archived')
    ], string='Status', default='draft')
    version = fields.Char(string='Version')

    component_ids = fields.One2many('bom.component', 'bom_id', string='Components')
