from odoo import models, fields, api, _


class HrWarning(models.Model):
    _name = 'hr.warning'
    _description = 'Employee Disciplinary Warning'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Reference', readonly=True, default='New', copy=False)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        ondelete='restrict', tracking=True,
    )
    department_id = fields.Many2one(
        related='employee_id.department_id', store=True,
    )
    warning_type = fields.Selection([
        ('verbal', 'Verbal Warning'),
        ('written', 'Written Warning'),
        ('final', 'Final Warning'),
    ], string='Warning Level', required=True, default='verbal', tracking=True)
    date = fields.Date(string='Warning Date', default=fields.Date.today, required=True)
    reason = fields.Text(string='Reason / Description', required=True)
    hr_responsible_id = fields.Many2one(
        'hr.employee', string='HR Responsible',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Issued'),
        ('acknowledged', 'Acknowledged'),
    ], default='draft', string='Status', tracking=True)
    employee_comment = fields.Text(string='Employee Comment')
    attachment_ids = fields.Many2many(
        'ir.attachment', string='Attachments',
        relation='hr_warning_attachment_rel',
        column1='warning_id', column2='attachment_id',
    )
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.warning') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})
        for warning in self:
            warning.message_post(
                body=_(
                    'A <b>%(type)s</b> has been issued to <b>%(emp)s</b> on %(date)s.',
                    type=dict(warning._fields['warning_type'].selection)[warning.warning_type],
                    emp=warning.employee_id.name,
                    date=warning.date,
                ),
            )

    def action_acknowledge(self):
        self.write({'state': 'acknowledged'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
