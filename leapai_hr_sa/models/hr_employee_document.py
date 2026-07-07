from odoo import models, fields, api
from datetime import date


class HrEmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'Employee Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expiry_date asc'
    _rec_name = 'document_type'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        ondelete='cascade', tracking=True,
    )
    document_type = fields.Selection([
        ('iqama', 'Iqama / Residency Permit'),
        ('national_id', 'National ID'),
        ('passport', 'Passport'),
        ('driving_license', 'Driving License'),
        ('work_permit', 'Work Permit'),
        ('medical_insurance', 'Medical Insurance'),
        ('other', 'Other'),
    ], string='Document Type', required=True, tracking=True)
    document_name = fields.Char(string='Document Name')
    document_number = fields.Char(string='Document Number')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date', required=True, tracking=True)

    days_remaining = fields.Integer(
        string='Days Remaining',
        compute='_compute_days_remaining',
        store=True,
    )
    state = fields.Selection([
        ('valid', 'Valid'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired'),
    ], string='Status', compute='_compute_state', store=True)

    attachment_ids = fields.Many2many(
        'ir.attachment', string='Attachments',
        relation='hr_employee_document_attachment_rel',
        column1='document_id', column2='attachment_id',
    )
    notes = fields.Text(string='Notes')

    # ── Computes ───────────────────────────────────────────────────────────────

    @api.depends('expiry_date')
    def _compute_days_remaining(self):
        today = date.today()
        for doc in self:
            if doc.expiry_date:
                doc.days_remaining = (doc.expiry_date - today).days
            else:
                doc.days_remaining = 0

    @api.depends('days_remaining')
    def _compute_state(self):
        for doc in self:
            if doc.days_remaining < 0:
                doc.state = 'expired'
            elif doc.days_remaining <= 30:
                doc.state = 'expiring_soon'
            else:
                doc.state = 'valid'

    # ── CRON: send alerts ──────────────────────────────────────────────────────

    @api.model
    def _cron_check_expiry(self):
        """Send expiry alerts at 30, 15, and 7 days before expiry."""
        today = date.today()
        alert_days = [30, 15, 7]
        for days in alert_days:
            target_date = today + __import__('datetime').timedelta(days=days)
            docs = self.search([('expiry_date', '=', target_date)])
            for doc in docs:
                doc.message_post(
                    body=(
                        f'⚠️ Document <b>{doc.document_type}</b> for employee '
                        f'<b>{doc.employee_id.name}</b> will expire in '
                        f'<b>{days} days</b> on {doc.expiry_date}.'
                    ),
                    subject=f'Document Expiry Alert – {days} days',
                    partner_ids=doc.employee_id.user_id.partner_id.ids if doc.employee_id.user_id else [],
                )
