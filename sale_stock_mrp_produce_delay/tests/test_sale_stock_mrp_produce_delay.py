# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase
from odoo import fields
from odoo.tools.date_utils import relativedelta


class TestSaleStockMrpProduceDelay(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product.write({
            'seller_ids': [
                (0, 0, {
                    'name': cls.env.ref('base.res_partner_3').id,
                    'price': 5.0,
                    'min_qty': 0.0,
                    'sequence': 1,
                    'date_start': fields.Date.today() - relativedelta(days=100),
                    'delay': 28,
                }),
            ]
        })
        cls.subproduct_1_1.write({
            'seller_ids': [
                (0, 0, {
                    'name': cls.env.ref('base.res_partner_3').id,
                    'price': 5.0,
                    'min_qty': 0.0,
                    'sequence': 1,
                    'date_start': fields.Date.today() - relativedelta(days=100),
                    'delay': 28,
                }),
            ]
        })
        cls.subproduct_2_1.write({
            'seller_ids': [
                (0, 0, {
                    'name': cls.env.ref('base.res_partner_3').id,
                    'price': 5.0,
                    'min_qty': 0.0,
                    'sequence': 1,
                    'date_start': fields.Date.today() - relativedelta(days=100),
                    'delay': 35,
                }),
            ]
        })

    def test_00_available_info_product(self):
        # check product to purchase
        order1 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        line1 = self._create_sale_order_line(order1, self.product, 5)
        self.assertEqual(line1.available_date.date(),
                         fields.Date.today() + relativedelta(days=28))
        self.assertEqual(
            line1.available_dates_info,
            'Need purchase for %s %s on date %s for qty %s.\n' % (
                'product' if self.product.bom_ids else 'component',
                self.product.display_name,
                (fields.Date.today() + relativedelta(days=28)).strftime('%d/%m/%Y'),
                5.0,
            )
        )

    def test_01_available_info_product_mrp(self):
        # todo simulate a product with multiple child boms to show a "tree" of
        #  availability like
        #  product (stock): [available at date x | purchesable for date x]¹
        #  top product (bom): [available at date x | produceable for date x]²
        #    -> 5pc subproduct1 (bom): ¹
        #       -> 2pc subproduct_1_1 (stock) -> 28 days to purchase
        #    -> 2pc subproduct2 (bom): ²
        #       -> 4pc subproduct_2_1 (stock) -> 35 days to purchase
        #       -> 3pc subproduct_1_1 (stock) -> 28 days to purchase
        order1 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        line1 = self._create_sale_order_line(order1, self.top_product, 3)
        self.assertEqual(line1.available_date.date(),
                         fields.Date.today() + relativedelta(days=35))
        info = ''.join([
                'Need purchase for %s %s on date %s for qty %s.\n' % (
                    'product' if x.bom_ids else 'component',
                    x.display_name,
                    (fields.Date.today() + relativedelta(
                        days=x.purchase_delay)).strftime('%d/%m/%Y'),
                    y,
                ) for x, y in [
                    [self.subproduct_1_1, 30.0],
                    [self.subproduct_2_1, 24.0],
                    [self.subproduct_1_1, 18.0],
                ]
            ])
        self.assertEqual(line1.available_dates_info, info)
        # subbom1: 3*5*2 subproduct_1_1 = 30 -> 2 in stock, 25 incoming on 28-5 days (so
        # before the purchase delay), 30+18 needed
        # subbom2: 3*2*3 subproduct_1_1 = 18 -> see above
        #          3*2*4 subproduct_2_1 = 24 -> 0 in stock,  incoming on  days (so
        # before the purchase delay),  needed
        purchase_order1 = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
        })
        purchase_planned_date = fields.Datetime.now() + relativedelta(
                days=self.subproduct_1_1.purchase_delay - 5)
        purchase_line1 = self._create_purchase_order_line(
            purchase_order1, self.subproduct_1_1, 25, purchase_planned_date)
        purchase_order1.button_confirm()
        picking = purchase_order1.picking_ids[0]
        self.assertEqual(picking.move_lines[0].product_id, self.subproduct_1_1)
        self.assertAlmostEqual(picking.move_lines[0].product_qty, 25)
        self.assertAlmostEqual(
            self.subproduct_1_1.virtual_available, 25
        )
        self.assertEqual(
            self.subproduct_1_1.with_context(
                to_date=fields.Date.today()
            ).virtual_available_at_date_expected,
            0
        )
        self.assertEqual(
            self.subproduct_1_1.with_context(
                to_date=purchase_planned_date
            ).virtual_available_at_date_expected,
            25
        )
        # now we have:
        # 3 sold top_product in mo confirmed: they are shown in quantity as -3
        # components of 3 top product:
        # 5pc subproduct1 * 3 = 15
        #   2pc subproduct_1_1 * 15 = 30
        # 2pc subproduct2 * 3 = 6
        #   4pc subproduct_2_1 * 6 =  24
        #   3pc subproduct_1_1 * 6 =  18
        # total                       72
        # NOT visible as not in this order product1
        # 2 offered top_product: they are shown in quantity as              -2
        # total top_products                                                -5
        # order1.action_confirm()
        # now we have outgoing stock.move and mo to be produced             +3
        # self.assertEqual(order1.state, 'sale')
        # self.production = self.env['mrp.production'].search(
        #     [('origin', '=', order1.name)])
        #
        # self.production.action_assign()
        # produce_form = Form(self.env['mrp.product.produce'].with_context(
        #         active_id=self.production.id,
        #         active_ids=[self.production.id],
        #     ))
        # produce_form.product_qty = 2.0
        # wizard = produce_form.save()
        # wizard.do_produce()
        # self.assertEqual(len(self.production), 1)

    # def test_negative_forecast_product(self):
    #     order1 = self.env['sale.order'].create({
    #         'partner_id': self.partner.id,
    #     })
    #     self._update_product_qty(
    #         self.product, order1.warehouse_id.in_type_id.default_location_dest_id, 10)
    #     self._create_sale_order_line(order1, self.product, 15)
    #     # forecast = self.get_forecast(order1)
    #     # self.assertFalse(forecast)
    #     # set commitment date to view forecast
    #     order1.commitment_date = fields.Datetime.now()
    #     forecast = self.get_forecast(order1)
    #     self.assertEqual(forecast[0].get('product_id')[0], self.product.id)
    #     self.assertAlmostEqual(forecast[0].get('quantity'), -5)
    #     order2 = self.env['sale.order'].create({
    #         'partner_id': self.partner.id,
    #         'commitment_date': fields.Datetime.now(),
    #     })
    #     self._create_sale_order_line(order2, self.product, 10)
    #     forecast1 = self.get_forecast(order2)
    #     self.assertAlmostEqual(forecast1[0].get('quantity'), -15)
    #     order1.action_confirm()
