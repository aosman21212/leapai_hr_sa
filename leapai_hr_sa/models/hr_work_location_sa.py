from odoo import models, fields, api
import math


class HrWorkLocationSa(models.Model):
    _name = 'hr.work.location.sa'
    _description = 'GPS Work Location (Saudi)'
    _order = 'name'

    name = fields.Char(string='Location Name', required=True)
    address = fields.Char(string='Address')
    latitude = fields.Float(string='Latitude', digits=(10, 8), required=True)
    longitude = fields.Float(string='Longitude', digits=(11, 8), required=True)
    radius = fields.Float(
        string='Geofence Radius (meters)', default=100.0, required=True,
        help='Maximum allowed distance from this location for attendance check-in.',
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company,
    )
    employee_ids = fields.One2many(
        'hr.employee', 'work_location_sa_id', string='Assigned Employees',
    )
    employee_count = fields.Integer(compute='_compute_employee_count')

    @api.depends('employee_ids')
    def _compute_employee_count(self):
        for loc in self:
            loc.employee_count = len(loc.employee_ids)

    def is_within_radius(self, latitude, longitude):
        """Return True if the given coordinates are within this location's geofence."""
        self.ensure_one()
        if not self.latitude or not self.longitude:
            return True  # No coords set → always allow
        dist = self._haversine(self.latitude, self.longitude, latitude, longitude)
        return dist <= self.radius

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2):
        """Calculate distance in meters between two GPS coordinates."""
        R = 6371000  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
