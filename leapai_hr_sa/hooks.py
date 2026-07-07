"""
Post-install hook: remove auto-generated default salary rules from the Saudi
payroll structure.  Odoo copies the generic 'default_structure' rules when a
new hr.payroll.structure is first created; our explicit Saudi rules (BASIC,
GROSS, GOSI_EMP, etc.) are defined separately in the data file, which creates
duplicates.  This hook removes the un-owned copies.
"""


def post_init_hook(env):
    """Remove default-copied rules from the Saudi Monthly Salary structure."""
    structure = env.ref('leapai_hr_sa.structure_sa_basic', raise_if_not_found=False)
    if not structure:
        return

    # External IDs of the rules we explicitly define in hr_sa_payroll_data.xml
    our_xmlids = [
        'leapai_hr_sa.rule_sa_basic',
        'leapai_hr_sa.rule_sa_housing',
        'leapai_hr_sa.rule_sa_transport',
        'leapai_hr_sa.rule_sa_other_alw',
        'leapai_hr_sa.rule_sa_gross',
        'leapai_hr_sa.rule_sa_gosi_emp',
        'leapai_hr_sa.rule_sa_gosi_employer',
        'leapai_hr_sa.rule_sa_loan_ded',
        'leapai_hr_sa.rule_sa_eos_provision',
        'leapai_hr_sa.rule_sa_net',
    ]

    our_rule_ids = set()
    for xmlid in our_xmlids:
        rule = env.ref(xmlid, raise_if_not_found=False)
        if rule:
            our_rule_ids.add(rule.id)

    # Unlink rules that are attached to our structure but were NOT created by us
    default_copies = structure.rule_ids.filtered(lambda r: r.id not in our_rule_ids)
    if default_copies:
        default_copies.unlink()
