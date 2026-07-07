{
    'name': 'HR Saudi Arabia',
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Comprehensive HR system for Saudi Arabia: Payroll, GOSI, EOS, Loans, Documents, Warnings, Assets, GPS Attendance',
    'description': """
HR Saudi Arabia
===============
Complete human resources management system tailored for Saudi labor law:

• Employee Management — Saudi/Non-Saudi fields, GOSI, Iqama, Passport, License
• GOSI Calculations — Auto deductions (9.75% Saudi, 2% Non-Saudi employer)
• EOS Benefits — ½ month (0-5 yrs) / full month (5+ yrs) per Saudi Labor Law
• Loan & Advance — Workflow with installment repayment schedules
• Document Tracking — Iqama, Passport, License expiry alerts (30/15/7 days)
• Disciplinary Warnings — Verbal → Written → Final with escalation
• Asset Allocation — Laptop, Phone, Vehicle, SIM assignment tracking
• GPS Attendance — Geofence-based check-in with coordinate validation
• MUDAD Export — Excel-compatible wage protection system export
• Bilingual — Arabic & English support

Contact
-------
Email   : abdzoro89@gmail.com | a.osman@bab.com.sa
Phone   : +966 562 984 106 | +966 553 368 212
Website : https://leapai.ai/
    """,
    'author': 'LeapAI',
    'website': 'https://leapai.ai/',
    'support': 'a.osman@bab.com.sa',
    'depends': [
        'hr',
        'hr_attendance',
        'hr_holidays',
        'hr_payroll',
        'mail',
        'account',
    ],
    'data': [
        'security/hr_sa_security.xml',
        'security/ir.model.access.csv',
        'data/cron_jobs.xml',
        'data/hr_sa_payroll_data.xml',
        'views/hr_employee_views.xml',
        'views/hr_loan_views.xml',
        'views/hr_employee_document_views.xml',
        'views/hr_warning_views.xml',
        'views/hr_asset_allocation_views.xml',
        'views/hr_work_location_views.xml',
        'views/hr_attendance_views.xml',
        'views/hr_payroll_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Leaflet map library (bundled so no CDN dependency)
            'leapai_hr_sa/static/lib/leaflet/leaflet.css',
            'leapai_hr_sa/static/lib/leaflet/leaflet.js',
            # GPS map widget component
            'leapai_hr_sa/static/src/css/gps_map_widget.css',
            'leapai_hr_sa/static/src/xml/gps_map_widget.xml',
            'leapai_hr_sa/static/src/js/gps_map_widget.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
}
