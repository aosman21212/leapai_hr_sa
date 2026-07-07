from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    # ── GPS Check-In ───────────────────────────────────────────────────────────
    check_in_latitude = fields.Float(string='Check-In Latitude', digits=(10, 8))
    check_in_longitude = fields.Float(string='Check-In Longitude', digits=(11, 8))
    check_in_location_name = fields.Char(string='Check-In Location')

    # ── GPS Check-Out ──────────────────────────────────────────────────────────
    check_out_latitude = fields.Float(string='Check-Out Latitude', digits=(10, 8))
    check_out_longitude = fields.Float(string='Check-Out Longitude', digits=(11, 8))
    check_out_location_name = fields.Char(string='Check-Out Location')

    # ── Matched Work Location ──────────────────────────────────────────────────
    work_location_sa_id = fields.Many2one(
        'hr.work.location.sa', string='GPS Work Location',
        compute='_compute_work_location', store=True,
    )
    within_geofence = fields.Boolean(
        string='Within Geofence', compute='_compute_work_location', store=True,
    )

    @api.depends('check_in_latitude', 'check_in_longitude', 'employee_id')
    def _compute_work_location(self):
        for att in self:
            if not att.check_in_latitude or not att.check_in_longitude:
                att.work_location_sa_id = False
                att.within_geofence = False
                continue

            location = att.employee_id.work_location_sa_id
            if location:
                in_range = location.is_within_radius(
                    att.check_in_latitude, att.check_in_longitude
                )
                att.work_location_sa_id = location
                att.within_geofence = in_range
            else:
                att.work_location_sa_id = False
                att.within_geofence = True  # no location assigned → no restriction
