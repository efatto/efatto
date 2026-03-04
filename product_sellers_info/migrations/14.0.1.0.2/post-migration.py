import logging

from openupgradelib import openupgrade
from psycopg2 import sql

from odoo import fields

logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, installed_version):
    # Assign purchase delay value from custom_purchase_delay saved in the pre-migration
    legacy_name_custom_purchase_delay = openupgrade.get_legacy_name(
        "custom_purchase_delay"
    )
    product_templates = env["product.template"].search(
        [
            ("seller_ids", "!=", False),
        ]
    )
    env.cr.execute(
        sql.SQL(
            "SELECT id, {} FROM product_template WHERE id in %s " "AND {} > 1"
        ).format(
            sql.Identifier(legacy_name_custom_purchase_delay),
            sql.Identifier(legacy_name_custom_purchase_delay),
        ),
        (tuple(product_templates.ids),),
    )
    custom_purchase_delays = dict(env.cr.fetchall())
    for pt in product_templates:
        seller = fields.first(
            pt.seller_ids.filtered(
                lambda s: not s.date_end or s.date_end >= fields.Date.today()
            )
        )
        if seller:
            custom_purchase_delay = custom_purchase_delays.get(pt.id, None)
            if custom_purchase_delay and custom_purchase_delay != seller.delay:
                pt.purchase_delay = custom_purchase_delay
                assert pt.purchase_delay == seller.delay
                logger.info(
                    f"Updated product template {pt.default_code} seller "
                    f"{seller.name.name} to purchase delay {seller.delay}"
                )
