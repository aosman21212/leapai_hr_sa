from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # ── Nationality ────────────────────────────────────────────────────────────
    nationality_type = fields.Selection([
        ('saudi', 'Saudi'),
        ('non_saudi', 'Non-Saudi'),
    ], string='Nationality Type', default='non_saudi', tracking=True)

    # ── Official Documents ─────────────────────────────────────────────────────
    national_id = fields.Char(string='National ID / Iqama Number')
    national_id_expiry = fields.Date(string='Iqama / National ID Expiry')
    passport_number = fields.Char(string='Passport Number')
    passport_expiry = fields.Date(string='Passport Expiry')
    driving_license_number = fields.Char(string='Driving License Number')
    driving_license_expiry = fields.Date(string='Driving License Expiry')

    # ── GOSI ───────────────────────────────────────────────────────────────────
    gosi_number = fields.Char(string='GOSI Number')
    gosi_employee_rate = fields.Float(
        string='GOSI Employee Rate (%)',
        compute='_compute_gosi_rates', store=True,
    )
    gosi_employer_rate = fields.Float(
        string='GOSI Employer Rate (%)',
        compute='_compute_gosi_rates', store=True,
    )

    # ── Bank Details ───────────────────────────────────────────────────────────
    bank_name = fields.Char(string='Bank Name')
    bank_account_number = fields.Char(string='Bank Account / IBAN')

    # ── EOS (End of Service) ───────────────────────────────────────────────────
    eos_years_of_service = fields.Float(
        string='Years of Service',
        compute='_compute_eos', store=True,
    )
    eos_entitlement_days = fields.Float(
        string='EOS Entitlement (Days)',
        compute='_compute_eos', store=True,
    )
    eos_monthly_provision = fields.Float(
        string='Monthly EOS Provision',
        compute='_compute_eos', store=True,
    )

    # ── Related Records ────────────────────────────────────────────────────────
    loan_ids = fields.One2many('hr.loan', 'employee_id', string='SA Loans & Advances')
    loan_count = fields.Integer(compute='_compute_loan_count', string='Loans')

    document_ids = fields.One2many('hr.employee.document', 'employee_id', string='SA Documents')
    document_count = fields.Integer(compute='_compute_document_count', string='Documents')

    warning_ids = fields.One2many('hr.warning', 'employee_id', string='SA Disciplinary Warnings')
    warning_count = fields.Integer(compute='_compute_warning_count', string='Warnings')

    asset_allocation_ids = fields.One2many('hr.asset.allocation', 'employee_id', string='SA Assets')
    asset_count = fields.Integer(compute='_compute_asset_count', string='Assets')

    # ── GPS Work Location ──────────────────────────────────────────────────────
    work_location_sa_id = fields.Many2one(
        'hr.work.location.sa', string='GPS Work Location',
    )

    # ── Computes ───────────────────────────────────────────────────────────────

    @api.depends('nationality_type')
    def _compute_gosi_rates(self):
        for emp in self:
            if emp.nationality_type == 'saudi':
                emp.gosi_employee_rate = 9.75
                emp.gosi_employer_rate = 9.75
            else:
                emp.gosi_employee_rate = 0.0
                emp.gosi_employer_rate = 2.0

    @api.depends('contract_date_start', 'contract_wage')
    def _compute_eos(self):
        today = fields.Date.today()
        for emp in self:
            start = emp.contract_date_start
            if not start:
                emp.eos_years_of_service = 0.0
                emp.eos_entitlement_days = 0.0
                emp.eos_monthly_provision = 0.0
                continue

            # Years of service
            rd = relativedelta(today, start)
            years = rd.years + rd.months / 12.0
            emp.eos_years_of_service = round(years, 2)

            # Saudi Labor Law: ½ month for first 5 yrs, full month thereafter
            wage = emp.contract_wage or 0.0
            if years <= 5:
                annual_eos = years * (wage / 2)
            else:
                annual_eos = (5 * (wage / 2)) + ((years - 5) * wage)

            emp.eos_entitlement_days = round(years * 30 if years <= 5 else (5 * 15) + ((years - 5) * 30), 1)
            emp.eos_monthly_provision = round(annual_eos / 12, 2)

    @api.depends('loan_ids')
    def _compute_loan_count(self):
        for emp in self:
            emp.loan_count = len(emp.loan_ids)

    @api.depends('document_ids')
    def _compute_document_count(self):
        for emp in self:
            emp.document_count = len(emp.document_ids)

    @api.depends('warning_ids')
    def _compute_warning_count(self):
        for emp in self:
            emp.warning_count = len(emp.warning_ids)

    @api.depends('asset_allocation_ids')
    def _compute_asset_count(self):
        for emp in self:
            emp.asset_count = len(emp.asset_allocation_ids)

    # ── Smart Buttons ──────────────────────────────────────────────────────────

    def action_view_loans(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Loans & Advances',
            'res_model': 'hr.loan',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }

    def action_view_documents(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'hr.employee.document',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }

    def action_view_warnings(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Warnings',
            'res_model': 'hr.warning',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }

    def action_view_assets(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asset Allocations',
            'res_model': 'hr.asset.allocation',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }
