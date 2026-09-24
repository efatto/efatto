from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [("stock.picking", "stock_picking", "is_assigned", "is_printed_for_logistics")],
    )
