from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrSaPayrollWizard(models.TransientModel):
    """Wizard to generate a salary pay run for all active Saudi HR employees."""

    _name = 'hr.sa.payroll.wizard'
    _description = 'Generate Salary Pay Run'

    # ── Period ─────────────────────────────────────────────────────────────────
    date_start = fields.Date(
        string='Period Start',
        required=True,
        default=lambda self: date.today().replace(day=1),
    )
    date_end = fields.Date(
        string='Period End',
        required=True,
        default=lambda self: (date.today().replace(day=1) + relativedelta(months=1, days=-1)),
    )

    # ── Salary Structure ────────────────────────────────────────────────────────
    structure_id = fields.Many2one(
        'hr.payroll.structure',
        string='Salary Structure',
        domain=[('type_id.country_id.code', '=', 'SA')],
    )

    # ── Employee filter ────────────────────────────────────────────────────────
    department_id = fields.Many2one('hr.department', string='Department (optional)')
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Specific Employees',
        help='Leave empty to include all active employees.',
    )

    # ── Actions ────────────────────────────────────────────────────────────────

    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start:
            self.date_end = self.date_start + relativedelta(months=1, days=-1)

    def action_generate(self):
        """Create a pay run and generate payslips for all employees."""
        self.ensure_one()

        if self.date_end < self.date_start:
            raise UserError(_('Period End must be after Period Start.'))

        # Build employee domain
        domain = [('active', '=', True), ('company_id', '=', self.env.company.id)]
        if self.department_id:
            domain.append(('department_id', '=', self.department_id.id))
        if self.employee_ids:
            domain.append(('id', 'in', self.employee_ids.ids))

        employees = self.env['hr.employee'].search(domain)
        if not employees:
            raise UserError(_('No active employees found with the current filter.'))

        # Use sudo() for payroll objects — hr.payroll.structure.type and
        # hr.payslip.run may not be in the HR SA manager's ACL on older
        # installations; the ACL file is the long-term fix, sudo() is the
        # belt-and-suspenders guard that makes the wizard work regardless.
        PayslipRun = self.env['hr.payslip.run'].sudo()
        run = PayslipRun.create({
            'date_start': self.date_start,
            'date_end': self.date_end,
            'structure_id': self.structure_id.id if self.structure_id else False,
        })

        # get valid version_ids for the employees
        version_ids = run._get_valid_version_ids(
            date_start=self.date_start,
            date_end=self.date_end,
            structure_id=self.structure_id.id if self.structure_id else None,
            employee_ids=employees.ids,
        )

        if not version_ids:
            run.sudo().unlink()
            raise UserError(_(
                'No active salary contracts found for the selected employees.\n\n'
                'Please make sure employees have an active contract / HR version '
                'with a valid date range that covers %s to %s.'
            ) % (self.date_start, self.date_end))

        run.sudo().generate_payslips(version_ids=version_ids)

        # Open the pay run
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pay Run'),
            'res_model': 'hr.payslip.run',
            'view_mode': 'form',
            'res_id': run.id,
            'target': 'current',
        }
