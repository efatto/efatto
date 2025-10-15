from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            (
                'account.invoice.line',
                'account_invoice_line',
                'exclude_extra_cost',
                'exclude_from_actual_cost_mrp',
            ),
            (
                'account.analytic.line',
                'account_analytic_line',
                'extra_cost',
                'actual_cost_mrp',
            ),
            (
                'account.analytic.line',
                'account_analytic_line',
                'extra_cost_unit',
                'actual_cost_mrp_unit',
            ),
            (
                'account.analytic.line',
                'account_analytic_line',
                'extra_cost_qty',
                'actual_cost_mrp_qty',
            ),
            (
                'account.analytic.line',
                'account_analytic_line',
                'extra_cost_invoice_line_ids',
                'actual_cost_mrp_invoice_line_ids',
            ),
        ]
    )
