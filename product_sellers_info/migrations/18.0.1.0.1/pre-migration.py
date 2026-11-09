from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, installed_version):
    # save a copy of custom_purchase_delay to reuse later
    openupgrade.copy_columns(
        env.cr,
        {"product_template": [("custom_purchase_delay", None, None)]},
    )
