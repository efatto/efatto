# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

xmlids_to_rename = [
    ('contract_show_invoice.act_analytic_invoices',
     'analytic_show_invoice.act_analytic_invoices'),
    ('contract_show_invoice.action_analytic_show_invoice_tree',
     'analytic_show_invoice.action_analytic_show_invoice_tree'),
    ('contract_show_invoice.action_analytic_show_invoice_form',
     'analytic_show_invoice.action_analytic_show_invoice_form'),
    ('contract_show_invoice.account_analytic_account_button_invoice',
     'analytic_show_invoice.account_analytic_account_button_invoice'),
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, xmlids_to_rename)
