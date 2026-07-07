from odoo import models, fields, api


class HrAssetAllocation(models.Model):
    _name = 'hr.asset.allocation'
    _description = 'Company Asset Allocation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'allocation_date desc'

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        ondelete='restrict', tracking=True,
    )
    department_id = fields.Many2one(
        related='employee_id.department_id', store=True,
    )
    asset_type = fields.Selection([
        ('laptop', 'Laptop / Computer'),
        ('phone', 'Mobile Phone'),
        ('vehicle', 'Vehicle / Car'),
        ('sim_card', 'SIM Card'),
        ('tablet', 'Tablet'),
        ('other', 'Other'),
    ], string='Asset Type', required=True, tracking=True)
    serial_number = fields.Char(string='Serial Number / Plate Number')
    model_number = fields.Char(string='Model / Brand')
    allocation_date = fields.Date(
        string='Allocation Date', default=fields.Date.today, required=True,
    )
    return_date = fields.Date(string='Return Date')
    state = fields.Selection([
        ('allocated', 'Allocated'),
        ('returned', 'Returned'),
        ('lost', 'Lost / Damaged'),
    ], default='allocated', string='Status', tracking=True)
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company,
    )
    attachment_ids = fields.Many2many(
        'ir.attachment', string='Attachments',
        relation='hr_asset_allocation_attachment_rel',
        column1='asset_id', column2='attachment_id',
    )

    def action_return(self):
        self.write({'state': 'returned', 'return_date': fields.Date.today()})

    def action_mark_lost(self):
        self.write({'state': 'lost'})

    def action_reallocate(self):
        self.write({'state': 'allocated', 'return_date': False})
