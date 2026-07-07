from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class HrLoan(models.Model):
    _name = 'hr.loan'
    _description = 'Employee Loan / Salary Advance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Reference', readonly=True, default='New', copy=False)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        tracking=True, ondelete='restrict',
    )
    department_id = fields.Many2one(
        related='employee_id.department_id', string='Department', store=True,
    )
    loan_type = fields.Selection([
        ('salary_advance', 'Salary Advance'),
        ('loan', 'Loan'),
    ], string='Type', required=True, default='loan', tracking=True)

    amount = fields.Float(string='Loan Amount', required=True, tracking=True)
    installments = fields.Integer(string='Number of Installments', default=1, required=True)
    monthly_installment = fields.Float(
        string='Monthly Installment', compute='_compute_monthly_installment', store=True,
    )
    date = fields.Date(string='Request Date', default=fields.Date.today, required=True)
    payment_date = fields.Date(string='First Repayment Date')
    reason = fields.Text(string='Reason')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True,
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('paid', 'Fully Paid'),
    ], default='draft', string='Status', tracking=True)

    loan_line_ids = fields.One2many('hr.loan.line', 'loan_id', string='Repayment Schedule')
    total_paid = fields.Float(string='Total Paid', compute='_compute_totals', store=True)
    total_remaining = fields.Float(string='Remaining Balance', compute='_compute_totals', store=True)

    # ── Computes ───────────────────────────────────────────────────────────────

    @api.depends('amount', 'installments')
    def _compute_monthly_installment(self):
        for loan in self:
            loan.monthly_installment = (
                loan.amount / loan.installments if loan.installments else 0.0
            )

    @api.depends('loan_line_ids.paid', 'loan_line_ids.amount')
    def _compute_totals(self):
        for loan in self:
            paid = sum(line.amount for line in loan.loan_line_ids if line.paid)
            loan.total_paid = paid
            loan.total_remaining = loan.amount - paid

    # ── Sequence ───────────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.loan') or 'New'
        return super().create(vals_list)

    # ── Workflow ───────────────────────────────────────────────────────────────

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_approve(self):
        for loan in self:
            loan.write({'state': 'approved'})
            if not loan.loan_line_ids:
                loan._generate_schedule()

    def action_refuse(self):
        self.write({'state': 'refused'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def _generate_schedule(self):
        """Auto-generate the repayment installment lines."""
        self.ensure_one()
        self.loan_line_ids.unlink()
        start = self.payment_date or self.date
        lines = []
        for i in range(self.installments):
            due_date = start + relativedelta(months=i)
            lines.append({
                'loan_id': self.id,
                'date': due_date,
                'amount': self.monthly_installment,
                'paid': False,
            })
        self.env['hr.loan.line'].create(lines)


class HrLoanLine(models.Model):
    _name = 'hr.loan.line'
    _description = 'Loan Repayment Installment'
    _order = 'date asc'

    loan_id = fields.Many2one('hr.loan', string='Loan', required=True, ondelete='cascade')
    employee_id = fields.Many2one(related='loan_id.employee_id', store=True)
    date = fields.Date(string='Due Date', required=True)
    amount = fields.Float(string='Amount', required=True)
    paid = fields.Boolean(string='Paid', default=False)
    paid_date = fields.Date(string='Paid Date')
    notes = fields.Char(string='Notes')

    def action_mark_paid(self):
        self.write({'paid': True, 'paid_date': fields.Date.today()})
        for line in self:
            remaining = sum(l.amount for l in line.loan_id.loan_line_ids if not l.paid)
            if remaining == 0:
                line.loan_id.write({'state': 'paid'})
