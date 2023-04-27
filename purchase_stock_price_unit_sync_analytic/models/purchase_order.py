# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def stock_price_unit_sync(self):
        super().stock_price_unit_sync()
        for line in self.filtered(lambda l: l.state in ['purchase', 'done']):
            # When the affected product is a kit we do nothing, which is the
            # default behavior on the standard: the move is exploded into moves
            # for the components and those get the default price_unit for the
            # time being. We avoid a hard dependency as well.
            if (
                hasattr(line.product_id, "bom_ids")
                and line.product_id._is_phantom_bom()
            ):
                continue
            purchase_analytic_accounts = line.mapped(
                'move_ids.purchase_line_id.account_analytic_id')
            if purchase_analytic_accounts:
                purchase_analytic_account = purchase_analytic_accounts[0]
                # search without date nor state as they are unpredictable
                # stock move from sales or productions
                used_move_ids = self.env['stock.move'].search([
                    ('product_id', '=', line.product_id.id),
                    ('id', 'not in', line.move_ids.ids),
                    ('location_dest_id.usage', 'in', ['production', 'customer']),
                    '|',
                    ('sale_line_id.order_id.analytic_account_id', '=',
                     purchase_analytic_account.id),
                    ('raw_material_production_id.analytic_account_id', '=',
                     purchase_analytic_account.id)
                ])
                used_move_ids.write({
                    'price_unit': -line.with_context(
                        skip_stock_price_unit_sync=True
                    )._get_stock_move_price_unit(),
                })
