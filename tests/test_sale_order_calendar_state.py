# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.addons.base_external_dbsource.exceptions import ConnectionSuccessError
from odoo.exceptions import UserError


class TestSaleOrderCalendarState(TransactionCase):

    def _create_sale_order_line(self, order, product, qty):
        line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': qty,
            'price_unit': 100,
            })
        line.product_id_change()
        line._convert_to_write(line._cache)
        return line

    def setUp(self):
        super(TestSaleOrderCalendarState, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        # Acoustic Bloc Screens, 16 on hand
        self.product1 = self.env.ref('product.product_product_25')
        # Cabinet with Doors, 8 on hand
        self.product2 = self.env.ref('product.product_product_10')
        # Large Cabinet, 250 on hand
        self.product3 = self.env.ref('product.product_product_6')
        # Drawer Black, 0 on hand
        self.product4 = self.env.ref('product.product_product_16')
        self.product1.invoice_policy = 'order'
        self.product2.invoice_policy = 'order'

    def test_complete_picking_from_sale(self):
        order1 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            })
        self._create_sale_order_line(order1, self.product1, 5)
        order1.action_confirm()
        self.assertEqual(order1.state, 'sale')
        self.assertEqual(order1.calendar_state, 'available')
        picking = order1.picking_ids[0]
        picking.action_assign()
        for sml in picking.move_lines.mapped('move_line_ids'):
            sml.qty_done = sml.product_qty
        picking.action_done()
        self.assertEqual(picking.state, 'done')
        self.assertEqual(order1.calendar_state, 'delivery_done')
        # create invoice
        inv_id = order1.action_invoice_create()
        self.assertEqual(order1.calendar_state, 'invoiced')
        invoice = self.env['account.invoice'].browse(inv_id)

    # def test_partial_picking_from_sale(self):
    #     with self.assertRaises(ConnectionSuccessError):
    #         self.dbsource.connection_test()
    #     self.dbsource.with_context(no_return=True).execute_mssql(
    #         sqlquery='DELETE FROM HOST_LISTE', sqlparams=None, metadata=None)
    #     whs_len_records = len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0])
    #     order1 = self.env['sale.order'].create({
    #         'partner_id': self.partner.id,
    #         })
    #     self._create_sale_order_line(order1, self.product1, 5)
    #     self._create_sale_order_line(order1, self.product1, 5)
    #     order1.action_confirm()
    #     self.assertEqual(order1.state, 'sale')
    #     self.assertEqual(order1.mapped('picking_ids.state'), ['waiting'])
    #     picking = order1.picking_ids[0]
    #     self.assertEqual(len(picking.mapped('move_lines.whs_list_ids')), 2)
    #
    #     # check whs list is added
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     self.assertEqual(len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0]),
    #         whs_len_records + 2)
    #
    #     whs_list = picking.mapped('move_lines.whs_list_ids')[0]
    #     # simulate whs work: validate first move partially (3 over 5)
    #     set_liste_elaborated_query = \
    #         "UPDATE HOST_LISTE SET Elaborato=4, QtaMovimentata=%s WHERE " \
    #         "NumLista = '%s' AND NumRiga = '%s'" % (
    #             3, whs_list.num_lista, whs_list.riga
    #         )
    #     self.dbsource.with_context(no_return=True).execute_mssql(
    #         sqlquery=set_liste_elaborated_query, sqlparams=None, metadata=None)
    #
    #     whs_select_query = \
    #         "SELECT Qta, QtaMovimentata FROM HOST_LISTE WHERE Elaborato = 4 AND " \
    #         "NumLista = '%s' AND NumRiga = '%s'" % (
    #             whs_list.num_lista, whs_list.riga
    #         )
    #     result_liste = self.dbsource.execute_mssql(
    #         sqlquery=whs_select_query, sqlparams=None, metadata=None)
    #     self.assertEqual(str(result_liste[0]),
    #                      "[(Decimal('5.000'), Decimal('3.000'))]")
    #
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #
    #     # check move and picking linked to sale order have changed state to done
    #     self.assertEqual(picking.move_lines[0].state, 'assigned')
    #     self.assertAlmostEqual(picking.move_lines[0].move_line_ids[0].qty_done, 3.0)
    #     self.assertEqual(picking.state, 'assigned')
    #
    #     # simulate user partial validate of picking and check backorder exist
    #     backorder_wiz_id = picking.button_validate()['res_id']
    #     backorder_wiz = self.env['stock.backorder.confirmation'].browse(
    #         backorder_wiz_id)
    #     # User cannot create backorder if whs list is not processed on whs system
    #
    #     # with self.assertRaises(UserError):
    #     backorder_wiz.process()
    #
    #     # Simulate whs user validation
    #     whs_lists = picking.mapped('move_lines.whs_list_ids')
    #     for whs_list in whs_lists:
    #         # simulate whs work: total process
    #         set_liste_elaborated_query = \
    #             "UPDATE HOST_LISTE SET Elaborato=4, QtaMovimentata=%s WHERE " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 whs_list.qta,
    #                 whs_list.num_lista, whs_list.riga
    #             )
    #         self.dbsource.with_context(no_return=True).execute_mssql(
    #             sqlquery=set_liste_elaborated_query, sqlparams=None, metadata=None)
    #
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     # picking.action_pack_operation_auto_fill()
    #     backorder_wiz.process()
    #     # check whs list for backorder is created
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     self.assertEqual(len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0]),
    #         whs_len_records + 3)
    #
    #     # check back picking is waiting for whs process
    #     self.assertEqual(len(order1.picking_ids), 2)
    #     backorder_picking = order1.picking_ids - picking
    #     self.assertEqual(backorder_picking.state, 'waiting')
    #     self.assertEqual(backorder_picking.move_lines[0].state, 'assigned')
    #
    # def test_partial_picking_partial_available_from_sale(self):
    #     with self.assertRaises(ConnectionSuccessError):
    #         self.dbsource.connection_test()
    #     self.dbsource.with_context(no_return=True).execute_mssql(
    #         sqlquery='DELETE FROM HOST_LISTE', sqlparams=None, metadata=None)
    #     whs_len_records = len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0])
    #     order1 = self.env['sale.order'].create({
    #         'partner_id': self.partner.id,
    #         })
    #     self._create_sale_order_line(order1, self.product1, 5)
    #     self._create_sale_order_line(order1, self.product2, 20)
    #     order1.action_confirm()
    #     self.assertEqual(order1.state, 'sale')
    #     picking = order1.picking_ids[0]
    #     self.assertEqual(len(picking.mapped('move_lines.whs_list_ids')), 2)
    #     self.assertEqual(picking.state, 'waiting')
    #
    #     # check whs list is added
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     self.assertEqual(len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0]),
    #         whs_len_records + 2)
    #
    #     whs_lists = picking.mapped('move_lines.whs_list_ids')
    #     for whs_list in whs_lists:
    #         # simulate whs work: partial elaboration of product #1
    #         # and total of product #2 so it is -4 on warehouse
    #         set_liste_elaborated_query = \
    #             "UPDATE HOST_LISTE SET Elaborato=4, QtaMovimentata=%s WHERE " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 whs_list.qta - (2 if whs_list.product_id == self.product1 else 0),
    #                 whs_list.num_lista, whs_list.riga
    #             )
    #         self.dbsource.with_context(no_return=True).execute_mssql(
    #             sqlquery=set_liste_elaborated_query, sqlparams=None, metadata=None)
    #
    #     for whs_list in whs_lists:
    #         whs_select_query = \
    #             "SELECT Qta, QtaMovimentata FROM HOST_LISTE WHERE Elaborato = 4 AND " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 whs_list.num_lista, whs_list.riga
    #             )
    #         result_liste = self.dbsource.execute_mssql(
    #             sqlquery=whs_select_query, sqlparams=None, metadata=None)
    #         self.assertEqual(
    #             str(result_liste[0]),
    #             "[(Decimal('5.000'), Decimal('3.000'))]"
    #             if whs_list.product_id == self.product1 else
    #             "[(Decimal('20.000'), Decimal('20.000'))]")
    #
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #
    #     # check move and picking linked to sale order have changed state to done
    #     self.assertEqual(picking.move_lines[0].state, 'assigned')
    #     self.assertAlmostEqual(picking.move_lines[0].move_line_ids[0].qty_done, 3.0)
    #     self.assertEqual(picking.state, 'assigned')
    #
    #     # simulate user partial validate of picking and check backorder exist
    #     backorder_wiz_id = picking.button_validate()['res_id']
    #     backorder_wiz = self.env['stock.backorder.confirmation'].browse(
    #         backorder_wiz_id)
    #     # User cannot create backorder if whs list is not processed on whs system
    #     # with self.assertRaises(UserError):
    #     # TODO: check backorder is created for residual
    #     backorder_wiz.process()
    #
    #     # Simulate whs user validation
    #     whs_lists = picking.mapped('move_lines.whs_list_ids')
    #     for whs_list in whs_lists:
    #         # simulate whs work: total process
    #         set_liste_elaborated_query = \
    #             "UPDATE HOST_LISTE SET Elaborato=4, QtaMovimentata=%s WHERE " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 2 if whs_list.product_id == self.product2 else 3,
    #                 whs_list.num_lista, whs_list.riga
    #             )
    #         self.dbsource.with_context(no_return=True).execute_mssql(
    #             sqlquery=set_liste_elaborated_query, sqlparams=None, metadata=None)
    #
    #     # this function do the action_assign() too
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     # picking.action_pack_operation_auto_fill()
    #     backorder_wiz.process()
    #     self.assertEqual(picking.state, 'done')
    #
    #     # check back picking is waiting as Odoo qty is not considered
    #     self.assertEqual(len(order1.picking_ids), 2)
    #     backorder_picking = order1.picking_ids - picking
    #     self.assertEqual(backorder_picking.move_lines.mapped('state'), ['waiting'])
    #     # todo check also a 'partially_available'
    #     self.assertEqual(backorder_picking.state, 'waiting')
    #
    #     # todo check whs_list for backorder is created
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     back_whs_list = backorder_picking.mapped('move_lines.whs_list_ids')
    #     whs_select_query = \
    #         "SELECT Qta, QtaMovimentata FROM HOST_LISTE WHERE " \
    #         "NumLista = '%s' AND NumRiga = '%s'" % (
    #             back_whs_list.num_lista, back_whs_list.riga
    #         )
    #     result_liste = self.dbsource.execute_mssql(
    #         sqlquery=whs_select_query, sqlparams=None, metadata=None)
    #     self.assertEqual(str(result_liste[0]), "[(Decimal('2.000'), None)]")
    #
    #     # simulate whs work set done to rest of backorder
    #     set_liste_elaborated_query = \
    #         "UPDATE HOST_LISTE SET Elaborato=4, QtaMovimentata=%s WHERE " \
    #         "NumLista = '%s' AND NumRiga = '%s'" % (
    #             2, back_whs_list.num_lista, back_whs_list.riga
    #         )
    #     self.dbsource.with_context(no_return=True).execute_mssql(
    #         sqlquery=set_liste_elaborated_query, sqlparams=None, metadata=None)
    #
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     backorder_picking.button_validate()
    #     self.assertEqual(backorder_picking.state, 'done')
    #
    # def test_partial_picking_from_sale(self):
    #     with self.assertRaises(ConnectionSuccessError):
    #         self.dbsource.connection_test()
    #     self.dbsource.with_context(no_return=True).execute_mssql(
    #         sqlquery='DELETE FROM HOST_LISTE', sqlparams=None, metadata=None)
    #     whs_len_records = len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0])
    #     order1 = self.env['sale.order'].create({
    #         'partner_id': self.partner.id,
    #         })
    #     self._create_sale_order_line(order1, self.product1, 5)  # 16
    #     self._create_sale_order_line(order1, self.product2, 10)  # 8
    #     self._create_sale_order_line(order1, self.product3, 20)  # 250
    #     self._create_sale_order_line(order1, self.product4, 20)  # 0
    #     order1.action_confirm()
    #     self.assertEqual(order1.state, 'sale')
    #     self.assertEqual(order1.mapped('picking_ids.state'), ['waiting'])
    #     picking = order1.picking_ids[0]
    #     self.assertEqual(len(picking.mapped('move_lines.whs_list_ids')), 4)
    #
    #     # check whs list is added
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     self.assertEqual(len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0]),
    #         whs_len_records + 4)
    #
    #     # simulate whs work: validate first move totally and second move partially
    #     whs_lists = picking.mapped('move_lines.whs_list_ids')
    #     for whs_list in whs_lists:
    #         # simulate whs work: total process
    #         set_liste_elaborated_query = \
    #             "UPDATE HOST_LISTE SET Elaborato=4, QtaMovimentata=%s WHERE " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 0 if whs_list.product_id == self.product3 else 5,
    #                 whs_list.num_lista, whs_list.riga
    #             )
    #         self.dbsource.with_context(no_return=True).execute_mssql(
    #             sqlquery=set_liste_elaborated_query, sqlparams=None, metadata=None)
    #
    #     for whs_l in whs_lists:
    #         whs_select_query = \
    #             "SELECT Qta, QtaMovimentata FROM HOST_LISTE WHERE Elaborato = 4 AND " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 whs_l.num_lista, whs_l.riga
    #             )
    #         result_liste = self.dbsource.execute_mssql(
    #             sqlquery=whs_select_query, sqlparams=None, metadata=None)
    #         self.assertEqual(
    #             str(result_liste[0]),
    #             "[(Decimal('5.000'), Decimal('5.000'))]"
    #             if whs_l.product_id == self.product1 else
    #             "[(Decimal('10.000'), Decimal('5.000'))]"
    #             if whs_l.product_id == self.product2 else
    #             "[(Decimal('20.000'), Decimal('0.000'))]"
    #             if whs_l.product_id == self.product3 else
    #             "[(Decimal('20.000'), Decimal('5.000'))]")
    #
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #
    #     # check move and picking linked to sale order have changed state to done
    #     self.assertEqual(picking.move_lines[0].state, 'assigned')
    #     self.assertAlmostEqual(picking.move_lines[0].move_line_ids[0].qty_done, 5.0)
    #     self.assertEqual(picking.state, 'assigned')
    #
    #     # simulate user partial validate of picking and check backorder exist
    #     backorder_wiz_id = picking.button_validate()['res_id']
    #     backorder_wiz = self.env['stock.backorder.confirmation'].browse(
    #         backorder_wiz_id)
    #     backorder_wiz.process()
    #     # check backorder whs list has the correct qty
    #     self.assertEqual(len(order1.picking_ids), 2)
    #     backorder_picking = order1.picking_ids - picking
    #     for move_line in backorder_picking.move_lines:
    #         self.assertAlmostEqual(move_line.whs_list_ids[0].qta, 5 if
    #                                move_line.product_id == self.product2 else 20 if
    #                                move_line.product_id == self.product3 else 15)
    #
    #     # Simulate whs user validation
    #     whs_lists = picking.mapped('move_lines.whs_list_ids')
    #     for whs_list in whs_lists:
    #         # simulate whs work: total process
    #         set_liste_elaborated_query = \
    #             "UPDATE HOST_LISTE SET Elaborato=4, QtaMovimentata=%s WHERE " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 whs_list.qta,
    #                 whs_list.num_lista, whs_list.riga
    #             )
    #         self.dbsource.with_context(no_return=True).execute_mssql(
    #             sqlquery=set_liste_elaborated_query, sqlparams=None, metadata=None)
    #
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     # picking.action_pack_operation_auto_fill()
    #     backorder_wiz.process()
    #     # check whs list for backorder is not created as the first is completed entirely
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     res = self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0]
    #     self.assertEqual(len(res), whs_len_records + 6)
    #
    #     # check back picking is waiting for whs process
    #     self.assertEqual(backorder_picking.state, 'waiting')
    #     self.assertEqual(backorder_picking.mapped('move_lines.state'),
    #                      ['waiting', 'waiting', 'waiting'])
    #
    # def test_unlink_sale_order(self):
    #     with self.assertRaises(ConnectionSuccessError):
    #         self.dbsource.connection_test()
    #     self.dbsource.with_context(no_return=True).execute_mssql(
    #         sqlquery='DELETE FROM HOST_LISTE', sqlparams=None, metadata=None)
    #     whs_len_records = len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0])
    #     order1 = self.env['sale.order'].create({
    #         'partner_id': self.partner.id,
    #         })
    #     self._create_sale_order_line(order1, self.product1, 5)
    #     self._create_sale_order_line(order1, self.product2, 5)
    #     order1.action_confirm()
    #     self.assertEqual(order1.state, 'sale')
    #     self.assertEqual(order1.mapped('picking_ids.state'), ['waiting'])
    #     picking = order1.picking_ids[0]
    #     self.assertEqual(len(picking.mapped('move_lines.whs_list_ids')), 2)
    #
    #     # check whs list is added
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     self.assertEqual(len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0]),
    #         whs_len_records + 2)
    #     # check whs non ci siano i relativi record
    #     order1.action_cancel()
    #     self.assertEqual(len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0]),
    #         whs_len_records)
    #
    # def _create_repair_order_line(self, repair, product, qty):
    #     line = self.env['repair.line'].create({
    #         'name': 'Add product',
    #         'repair_id': repair.id,
    #         'type': 'add',
    #         'product_id': product.id,
    #         'product_uom_qty': qty,
    #         'product_uom': product.uom_id.id,
    #         'price_unit': 5,
    #         'location_id': self.env.ref('stock.stock_location_stock').id,
    #         'location_dest_id': self.env.ref('stock.location_production').id,
    #     })
    #     line.onchange_product_id()
    #     line._convert_to_write(line._cache)
    #     return line
    #
    # def test_repair(self):
    #     with self.assertRaises(ConnectionSuccessError):
    #         self.dbsource.connection_test()
    #     self.dbsource.with_context(no_return=True).execute_mssql(
    #         sqlquery='DELETE FROM HOST_LISTE', sqlparams=None, metadata=None)
    #     whs_len_records = len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0])
    #     repair = self.env['repair.order'].create({
    #         'product_id': self.product1.id,
    #         'product_uom': self.product1.uom_id.id,
    #         'partner_id': self.partner.id,
    #         'product_qty': 1,
    #         'location_id': self.env.ref('stock.stock_location_stock').id,
    #         })
    #     self._create_repair_order_line(repair, self.product2, 5)
    #     self._create_repair_order_line(repair, self.product3, 3)
    #     repair.action_repair_confirm()
    #     self.assertEqual(repair.state, "confirmed",
    #                      'Repair order should be in "Confirmed" state.')
    #     repair.action_repair_start()
    #     self.assertEqual(repair.state, "under_repair",
    #                      'Repair order should be in "Under_repair" state.')
    #     repair.action_repair_end()
    #     self.assertEqual(repair.state, "done",
    #                      'Repair order should be in "Done" state.')
    #     # check whs list is added
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     self.assertEqual(len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0]),
    #         whs_len_records + 2)
    #
    #     # simulate whs work: partial elaboration of product #2
    #     # and total of product #3
    #     whs_lists = repair.mapped('operations.move_id.whs_list_ids')
    #     for whs_list in whs_lists:
    #         set_liste_elaborated_query = \
    #             "UPDATE HOST_LISTE SET Elaborato=4, QtaMovimentata=%s WHERE " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 2 if whs_list.product_id == self.product2 else 3,
    #                 whs_list.num_lista, whs_list.riga
    #             )
    #         self.dbsource.with_context(no_return=True).execute_mssql(
    #             sqlquery=set_liste_elaborated_query, sqlparams=None, metadata=None)
    #
    #     for whs_list in whs_lists:
    #         whs_select_query = \
    #             "SELECT Qta, QtaMovimentata FROM HOST_LISTE WHERE Elaborato = 4 AND " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 whs_list.num_lista, whs_list.riga
    #             )
    #         result_liste = self.dbsource.execute_mssql(
    #             sqlquery=whs_select_query, sqlparams=None, metadata=None)
    #         self.assertEqual(
    #             str(result_liste[0]),
    #             "[(Decimal('5.000'), Decimal('2.000'))]"
    #             if whs_list.product_id == self.product2 else
    #             "[(Decimal('3.000'), Decimal('3.000'))]")
    #
    #     # this update Odoo from WHS
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     # check whs_list are elaborated
    #     for whs_list in whs_lists:
    #         whs_select_query = \
    #             "SELECT Qta, QtaMovimentata FROM HOST_LISTE WHERE Elaborato = 5 AND " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 whs_list.num_lista, whs_list.riga
    #             )
    #         result_liste = self.dbsource.execute_mssql(
    #             sqlquery=whs_select_query, sqlparams=None, metadata=None)
    #         self.assertEqual(
    #             str(result_liste[0]),
    #             "[(Decimal('5.000'), Decimal('2.000'))]"
    #             if whs_list.product_id == self.product2 else
    #             "[(Decimal('3.000'), Decimal('3.000'))]")
    #
    # def _create_purchase_order_line(self, order, product, qty):
    #     line = self.env['purchase.order.line'].create({
    #         'order_id': order.id,
    #         'product_id': product.id,
    #         'product_uom': product.uom_po_id.id,
    #         'name': product.name,
    #         'product_qty': qty,
    #         'price_unit': 100,
    #         'date_planned': fields.Datetime.today(),
    #         })
    #     return line
    #
    # def test_purchase(self):
    #     with self.assertRaises(ConnectionSuccessError):
    #         self.dbsource.connection_test()
    #     self.dbsource.with_context(no_return=True).execute_mssql(
    #         sqlquery='DELETE FROM HOST_LISTE', sqlparams=None, metadata=None)
    #     whs_len_records = len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0])
    #     purchase = self.env['purchase.order'].create({
    #         'partner_id': self.partner.id,
    #         })
    #     self._create_purchase_order_line(purchase, self.product2, 20)
    #     self._create_purchase_order_line(purchase, self.product3, 3)
    #     purchase.button_approve()
    #     self.assertEqual(
    #         purchase.state, 'purchase', 'Purchase state should be "Purchase"')
    #     # check whs list is added
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     self.assertEqual(len(self.dbsource.execute_mssql(
    #         sqlquery="SELECT * FROM HOST_LISTE", sqlparams=None, metadata=None)[0]),
    #         whs_len_records + 2)
    #
    #     # simulate whs work: partial elaboration of product #2
    #     # and total of product #3
    #     whs_lists = purchase.mapped('picking_ids.move_lines.whs_list_ids')
    #     for whs_list in whs_lists:
    #         set_liste_elaborated_query = \
    #             "UPDATE HOST_LISTE SET Elaborato=4, QtaMovimentata=%s WHERE " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 2 if whs_list.product_id == self.product2 else 3,
    #                 whs_list.num_lista, whs_list.riga
    #             )
    #         self.dbsource.with_context(no_return=True).execute_mssql(
    #             sqlquery=set_liste_elaborated_query, sqlparams=None, metadata=None)
    #
    #     for whs_list in whs_lists:
    #         whs_select_query = \
    #             "SELECT Qta, QtaMovimentata FROM HOST_LISTE WHERE Elaborato = 4 AND " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 whs_list.num_lista, whs_list.riga
    #             )
    #         result_liste = self.dbsource.execute_mssql(
    #             sqlquery=whs_select_query, sqlparams=None, metadata=None)
    #         self.assertEqual(
    #             str(result_liste[0]),
    #             "[(Decimal('20.000'), Decimal('2.000'))]"
    #             if whs_list.product_id == self.product2 else
    #             "[(Decimal('3.000'), Decimal('3.000'))]")
    #
    #     # this update Odoo from WHS
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     # check whs_list are elaborated
    #     for whs_list in whs_lists:
    #         whs_select_query = \
    #             "SELECT Qta, QtaMovimentata FROM HOST_LISTE WHERE Elaborato = 5 AND " \
    #             "NumLista = '%s' AND NumRiga = '%s'" % (
    #                 whs_list.num_lista, whs_list.riga
    #             )
    #         result_liste = self.dbsource.execute_mssql(
    #             sqlquery=whs_select_query, sqlparams=None, metadata=None)
    #         self.assertEqual(
    #             str(result_liste[0]),
    #             "[(Decimal('20.000'), Decimal('2.000'))]"
    #             if whs_list.product_id == self.product2 else
    #             "[(Decimal('3.000'), Decimal('3.000'))]")
    #
    #     # simulate user partial validate of picking and check backorder exist
    #     picking = purchase.picking_ids[0]
    #     picking.action_pack_operation_auto_fill()
    #     backorder_wiz_id = picking.button_validate()['res_id']
    #     backorder_wiz = self.env['stock.backorder.confirmation'].browse(
    #         backorder_wiz_id)
    #     backorder_wiz.process()
    #     self.assertEqual(picking.state, 'done')
    #
    #     # check back picking is waiting as waiting for WHS work
    #     self.assertEqual(len(purchase.picking_ids), 2)
    #     backorder_picking = purchase.picking_ids - picking
    #     self.assertEqual(backorder_picking.move_lines.mapped('state'),
    #                      ['waiting'])
    #     self.assertEqual(backorder_picking.state, 'waiting')
    #
    #     # check whs_list for backorder is created
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     back_whs_list = backorder_picking.mapped('move_lines.whs_list_ids')
    #     whs_select_query = \
    #         "SELECT Qta, QtaMovimentata FROM HOST_LISTE WHERE " \
    #         "NumLista = '%s' AND NumRiga = '%s'" % (
    #             back_whs_list.num_lista, back_whs_list.riga
    #         )
    #     result_liste = self.dbsource.execute_mssql(
    #         sqlquery=whs_select_query, sqlparams=None, metadata=None)
    #     self.assertEqual(str(result_liste[0]), "[(Decimal('18.000'), None)]")
    #
    #     # simulate whs work set done to rest of backorder
    #     set_liste_elaborated_query = \
    #         "UPDATE HOST_LISTE SET Elaborato=4, QtaMovimentata=%s WHERE " \
    #         "NumLista = '%s' AND NumRiga = '%s'" % (
    #             18, back_whs_list.num_lista, back_whs_list.riga
    #         )
    #     self.dbsource.with_context(no_return=True).execute_mssql(
    #         sqlquery=set_liste_elaborated_query, sqlparams=None, metadata=None)
    #
    #     self.dbsource.whs_insert_read_and_synchronize_list()
    #     backorder_picking.button_validate()
    #     self.assertEqual(backorder_picking.state, 'done')
