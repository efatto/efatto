from odoo.tools.date_utils import relativedelta
from odoo.addons.mrp_production_demo.tests.common_data import TestProductionData
from odoo.tools import mute_logger
from odoo.exceptions import UserError

from odoo import fields


class TestStockReserveDateCheck(TestProductionData):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref('base.res_partner_2')
        cls.partner.customer = True
        cls.buy_route = cls.env.ref('purchase_stock.route_warehouse0_buy')
        cls.manufacture_route = cls.env.ref(
            'mrp.route_warehouse0_manufacture')
        cls.vendor = cls.env.ref('base.res_partner_3')
        supplierinfo = cls.env['product.supplierinfo'].create([{
            'name': cls.vendor.id,
            'delay': 10,
        }])
        cls.product = cls.env['product.product'].create([{
            'name': 'Product Test',
            'standard_price': 50.0,
            'seller_ids': [(6, 0, [supplierinfo.id])],
            'route_ids': [(6, 0, [cls.buy_route.id])],
        }])
        # Create User:
        cls.test_user = cls.env['res.users'].create({
            'name': 'John',
            'login': 'test',
            'email': 'test@test.email',
        })
        cls.test_user.write({
            'groups_id': [(4, cls.env.ref('sales_team.group_sale_salesman').id)],
        })

    def _create_sale_order_line(self, order, product, qty, commitment_date=False):
        vals = {
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': qty,
            'price_unit': 100,
            }
        if commitment_date:
            vals.update({
                'commitment_date': commitment_date,
            })
        line = self.env['sale.order.line'].sudo(self.test_user).create(vals)
        line.product_id_change()
        line._convert_to_write(line._cache)
        return line

    @mute_logger(
        'odoo.models', 'odoo.models.unlink', 'odoo.addons.base.ir.ir_model'
    )
    def test_00_sale_from_stock(self):
        order1 = self.env['sale.order'].sudo(self.test_user).create({
            'partner_id': self.partner.id,
        })
        self._create_sale_order_line(order1, self.product, 5)
        with self.assertRaises(UserError):
            order1.sudo(self.test_user).action_confirm()
        self.assertEqual(order1.state, 'draft')

    def test_01_sale_from_stock(self):
        order2 = self.env['sale.order'].sudo(self.test_user).create({
            'partner_id': self.partner.id,
        })
        commitment_date = \
            fields.Datetime.now() + relativedelta(days=10)
        self._create_sale_order_line(order2, self.product, qty=5,
                                     commitment_date=commitment_date)
        order2.sudo(self.test_user).action_confirm()
        self.assertEqual(order2.state, 'sale')

    @mute_logger(
        'odoo.models', 'odoo.models.unlink', 'odoo.addons.base.ir.ir_model'
    )
    def test_02_sale_from_mrp(self):
        self.top_product.produce_delay = 14
        order3 = self.env['sale.order'].sudo(self.test_user).create({
            'partner_id': self.partner.id,
        })
        commitment_date = \
            fields.Datetime.now() + relativedelta(days=10)
        self._create_sale_order_line(order3, self.top_product, qty=5,
                                     commitment_date=commitment_date)
        with self.assertRaises(UserError):
            order3.sudo(self.test_user).action_confirm()
        self.assertEqual(order3.state, 'draft')
        commitment_date = \
            fields.Datetime.now() + relativedelta(days=14)
        order_line = order3.order_line[0]
        order_line.write({'commitment_date': commitment_date})
        order_line._convert_to_write(order_line._cache)
        order3.sudo(self.test_user).action_confirm()
        self.assertEqual(order3.state, 'sale')
