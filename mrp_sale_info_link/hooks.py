# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # recover data from module sale_mrp_link, that can be uninstalled after
    env.cr.execute(
        """
            UPDATE mrp_production
                SET sale_id = sale_order_id
            WHERE sale_id IS NULL
            AND sale_order_id IS NOT NULL
        """
    )
    # recompute stored field for new ids
    model = env['sale.order']
    env.add_todo(model._fields['production_count'], model.search([]))
    model.recompute()
    env.cr.commit()
