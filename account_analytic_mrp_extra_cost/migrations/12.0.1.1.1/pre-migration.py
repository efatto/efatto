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
                'exclude_from_actual_cost',
            )
        ]
    )
