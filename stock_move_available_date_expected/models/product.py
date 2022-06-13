# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
from odoo.addons.stock.models.product import OPERATORS


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    date_oldest_open_move = fields.Datetime(compute='_compute_date_oldest_open_move')

    @api.multi
    def _compute_date_oldest_open_move(self):
        for product_template in self:
            moves = self.env['stock.move'].search([
                ('product_id.product_tmpl_id', 'in', self.ids),
                ('state', 'not in', ['cancel', 'done']),
            ])
            if not moves:
                moves = self.env['stock.move'].search([
                    ('product_id.product_tmpl_id', 'in', self.ids),
                ])
            product_template.date_oldest_open_move = min(
                [x.date_expected for x in moves] or [fields.Datetime.now(), ])

    def open_view_stock_reserved(self):
        domain = [('product_id.product_tmpl_id', 'in', self.ids),
                  ('state', '!=', 'cancel'),
                  ('date_expected', '>=', self.date_oldest_open_move)]
        view = self.env.ref(
            'stock_move_available_date_expected.view_stock_reserved_tree')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock reserved',
            'domain': domain,
            'views': [(view.id, 'tree'), (False, 'pivot')],
            'res_model': 'stock.move',
            'context': {},
        }


class Product(models.Model):
    _inherit = "product.product"

    virtual_available_at_date_expected = fields.Float(
        'Forecast Quantity Expected Date',
        compute='_compute_quantities_by_date_expected',
        search='_search_virtual_available_by_date_expected',
        digits=dp.get_precision('Product Unit of Measure')
    )

    def open_view_stock_reserved(self):
        domain = [('product_id', '=', self.id),
                  ('state', '!=', 'cancel'),
                  ('date_expected', '>=', self.product_tmpl_id.date_oldest_open_move)]
        view = self.env.ref(
            'stock_move_available_date_expected.view_stock_reserved_tree')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock reserved',
            'domain': domain,
            'views': [(view.id, 'tree'), (False, 'pivot')],
            'res_model': 'stock.move',
            'context': {},
        }

    def _search_virtual_available_by_date_expected(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_quantity(
            operator, value, 'virtual_available_at_date_expected')

    def _search_product_quantity_by_date_expected(self, operator, value, field):
        # TDE FIXME: should probably clean the search methods
        # to prevent sql injections
        if field not in (
                'qty_available', 'virtual_available_at_date_expected', 'incoming_qty',
                'outgoing_qty'):
            raise UserError(_('Invalid domain left operand %s') % field)
        if operator not in ('<', '>', '=', '!=', '<=', '>='):
            raise UserError(_('Invalid domain operator %s') % operator)
        if not isinstance(value, (float, int)):
            raise UserError(_('Invalid domain right operand %s') % value)

        # TODO: Still optimization possible when searching virtual quantities
        ids = []
        # Order the search on `id` to prevent the default order on the product name
        # which slows
        # down the search because of the join on the translation table to get the
        # translated names.
        for product in self.with_context(prefetch_fields=False).search([], order='id'):
            if OPERATORS[operator](product[field], value):
                ids.append(product.id)
        return [('id', 'in', ids)]

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def _compute_quantities_by_date_expected(self):
        res = self._compute_quantities_by_date_expected_dict(
            self._context.get('lot_id'), self._context.get('owner_id'),
            self._context.get('package_id'), self._context.get('from_date'),
            self._context.get('to_date'))
        for product in self:
            # product.qty_available = res[product.id]['qty_available']
            # product.incoming_qty = res[product.id]['incoming_qty']
            # product.outgoing_qty = res[product.id]['outgoing_qty']
            product.virtual_available_at_date_expected = res[product.id][
                'virtual_available_at_date_expected']

    def _compute_quantities_by_date_expected_dict(
            self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = \
            self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        # only to_date as to_date will correspond to qty_available
        to_date = fields.Datetime.to_datetime(to_date)
        if to_date and to_date < fields.Datetime.now():
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            domain_move_in += [('date_expected', '>=', from_date)]
            domain_move_out += [('date_expected', '>=', from_date)]
        if to_date:
            domain_move_in += [('date_expected', '<=', to_date)]
            domain_move_out += [('date_expected', '<=', to_date)]

        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [
            ('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))
        ] + domain_move_in
        domain_move_out_todo = [
            ('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))
        ] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty'])
                            for item in Move.read_group(
            domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'],
            orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty'])
                             for item in Move.read_group(
            domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'],
            orderby='id'))
        quants_res = dict((item['product_id'][0], item['quantity'])
                          for item in Quant.read_group(
            domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))
        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time
            # (as most questions will be recent ones)
            domain_move_in_done = [
                ('state', '=', 'done'), ('date_expected', '>', to_date)
            ] + domain_move_in_done
            domain_move_out_done = [
                ('state', '=', 'done'), ('date_expected', '>', to_date)
            ] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty'])
                                     for item in Move.read_group(
                domain_move_in_done, ['product_id', 'product_qty'], ['product_id'],
                orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty'])
                                      for item in Move.read_group(
                domain_move_out_done, ['product_id', 'product_qty'], ['product_id'],
                orderby='id'))

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            product_id = product.id
            rounding = product.uom_id.rounding
            res[product_id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(product_id, 0.0) - moves_in_res_past.get(
                    product_id, 0.0) + moves_out_res_past.get(product_id, 0.0)
            else:
                qty_available = quants_res.get(product_id, 0.0)
            res[product_id]['qty_available'] = float_round(
                qty_available, precision_rounding=rounding)
            res[product_id]['incoming_qty'] = float_round(
                moves_in_res.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['outgoing_qty'] = float_round(
                moves_out_res.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['virtual_available_at_date_expected'] = float_round(
                qty_available + res[product_id]['incoming_qty']
                - res[product_id]['outgoing_qty'], precision_rounding=rounding)

        return res
