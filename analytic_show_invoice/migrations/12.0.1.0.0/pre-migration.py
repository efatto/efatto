# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

xmlids_to_rename = [
    ('contract_show_invoice.act_analytic_invoices',
     'analytic_show_invoice.act_analytic_invoices'),
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, xmlids_to_rename)
