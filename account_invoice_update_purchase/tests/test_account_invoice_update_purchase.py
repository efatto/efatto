from odoo import fields
from odoo.tests.common import SavepointCase
from odoo.tools import mute_logger
from odoo.tools.date_utils import relativedelta


class AccountInvoiceUpdatePurchase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)
        cls.partner = cls.env.ref("base.res_partner_2")
        buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.vendor = cls.env.ref("base.res_partner_3")
        cls.supplierinfo_expired = cls.env["product.supplierinfo"].create(
            {
                "name": cls.vendor.id,
                "price": 77,
                "date_end": fields.Date.today() + relativedelta(days=-10),
            }
        )
        cls.supplierinfo = cls.env["product.supplierinfo"].create(
            {
                "name": cls.vendor.id,
                "price": 88,
                "date_start": fields.Date.today() + relativedelta(days=-9),
            }
        )
        cls.account_liability = cls.env["account.account"].create(
            {
                "code": "TEST_LIABILITY",
                "name": "Liability account",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_current_liabilities"
                ).id,
            }
        )
        cls.tax22 = cls.env["account.tax"].create(
            {
                "name": "22%",
                "amount": 22,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": cls.env.ref("account.tax_group_taxes").id,
                "invoice_repartition_line_ids": [
                    (
                        0,
                        0,
                        {
                            "repartition_type": "base",
                            "factor_percent": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "repartition_type": "tax",
                            "factor_percent": 100,
                            "account_id": cls.account_liability.id,
                        },
                    ),
                ],
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 77,
                "seller_ids": [
                    (6, 0, [cls.supplierinfo_expired.id, cls.supplierinfo.id])
                ],
                "route_ids": [(6, 0, [buy.id])],
                "supplier_taxes_id": [(6, 0, [cls.tax22.id])],
            }
        )
        cls.test_user = cls.env["res.users"].create(
            {
                "name": "John",
                "login": "test",
            }
        )
        cls.uom_hundred = cls.env["uom.uom"].create(
            {
                "name": "Hundred",
                "category_id": cls.env.ref("uom.product_uom_categ_unit").id,
                "factor_inv": 100,
                "uom_type": "bigger",
                "rounding": 0.01,
            }
        )

    def _create_purchase_order_line(self, order, product, qty, date_planned=False):
        vals = {
            "order_id": order.id,
            "product_id": product.id,
            "product_qty": qty,
            "product_uom": product.uom_po_id.id,
            "price_unit": product.list_price,
            "name": product.name,
        }
        if date_planned:
            vals.update({"date_planned": date_planned})
        line = self.env["purchase.order.line"].create(vals)
        line._onchange_quantity()
        line._convert_to_write(line._cache)
        return line

    @staticmethod
    def _action_pack_operation_auto_fill(picking):
        for op in picking.mapped("move_line_ids"):
            if op.product_id.type == "product":
                op.qty_done = op.move_id.product_uom_qty

    @mute_logger("odoo.models", "odoo.models.unlink", "odoo.addons.base.ir.ir_model")
    def test_01_invoice_update_purchase_with_standard_cost_method(self):
        self.assertEqual(self.product.categ_id.property_cost_method, "standard")
        purchase_order1 = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
            }
        )
        purchase_planned_date1 = fields.Datetime.now() + relativedelta(days=5)
        purchase_line = self._create_purchase_order_line(
            purchase_order1, self.product, 18, purchase_planned_date1
        )
        purchase_order1.button_confirm()
        current_price = purchase_line.price_unit

        self.assertEqual(purchase_line.product_uom_qty, 18)
        self.assertEqual(purchase_order1.state, "purchase")

        picking = purchase_order1.picking_ids[0]
        self._action_pack_operation_auto_fill(picking)
        picking.button_validate()
        self.assertEqual(picking.state, "done")

        res = purchase_order1.action_create_invoice()
        invoice = self.env["account.move"].browse(res.get("res_id"))
        self.assertTrue(invoice)
        invoice_line = invoice.invoice_line_ids
        self.assertEqual(invoice_line.product_id, self.product)

        self.assertEqual(purchase_line.price_unit, current_price)
        self.assertEqual(self.supplierinfo.price, current_price)
        self.assertEqual(
            picking.move_lines.filtered(
                lambda x: x.product_id == self.product
            ).price_unit,
            current_price,
        )

        new_price = invoice_line.price_unit + 66
        invoice_line.with_context(check_move_validity=False).price_unit = new_price
        invoice_line.update_purchase()
        self.assertEqual(purchase_line.price_unit, new_price)
        self.assertEqual(self.supplierinfo.price, new_price)
        self.assertEqual(
            picking.move_lines.filtered(
                lambda x: x.product_id == self.product
            ).price_unit,
            new_price,
        )

        # change uom of invoice and test re-computation
        invoice_line.with_context(
            check_move_validity=False
        ).product_uom_id = self.uom_hundred
        invoice_line.update_purchase()
        self.assertAlmostEqual(purchase_line.price_unit, new_price / 100)
