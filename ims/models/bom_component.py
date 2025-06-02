from odoo import models, fields, api
class BOMComponent(models.Model):
    _name = 'bom.component'
    _description = 'BoM Component Detail'

    bom_id = fields.Many2one('bom.master', string='BOM Reference', required=True, ondelete='cascade')
    component_no = fields.Char(string='Component No')
    component_desc = fields.Text(string='Description')
    matty_glossy = fields.Selection([
        ('glossy', 'Glossy'),
        ('anti_glare', 'Anti Glare')
    ], string='Matty/Glossy')
    pol_top_bottom = fields.Selection([
        ('top', 'Top'),
        ('bottom', 'Bottom')
    ], string='Polarizer Top/Bottom')
    warranty = fields.Selection([
        ('in', 'In Warranty'),
        ('out', 'Out of Warranty')
    ], string='Warranty')
    main_comp = fields.Boolean(string='Main Component')
    min_qty = fields.Integer(string='Min Qty')
    max_qty = fields.Integer(string='Max Qty')
    location = fields.Char(string='Location')
    component_type = fields.Selection([
        ('polarizer', 'Polarizer'),
        ('driver_ic', 'Driver IC'),
        ('other', 'Other')
    ], string='Component Type')
    component_3rd_party = fields.Boolean(string='Third Party')
    component_approved = fields.Boolean(string='Approved')
    created_date = fields.Datetime(string='Created Date')
    created_by = fields.Char(string='Created By')
    updated_date = fields.Datetime(string='Updated Date')
    updated_by = fields.Char(string='Updated By')
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='Status', default='active')
    driver_ic_qty = fields.Integer(string='Driver IC Qty')
    source_ic_qty = fields.Integer(string='Source IC Qty')
    oem = fields.Char(string='OEM')
    version = fields.Char(string='Version')
    version2 = fields.Char(string='Version 2')
