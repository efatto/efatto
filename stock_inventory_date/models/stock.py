# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, exceptions, api, _


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    theoretical_qty = fields.Float(compute='_get_theoretical_qty')

    @api.multi
    def _get_theoretical_qty(self, name, args):
        if self.inventory_id.date_inventory:
            return {}
        else:
            return super(StockInventoryLine, self)._get_theoretical_qty(
                name, args)


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    date_inventory = fields.Date()

    @api.model
    def _get_inventory_lines_by_date(self, inventory):
        location_obj = self.env['stock.location']
        location_ids = location_obj.search([
            ('id', 'child_of', [inventory.location_id.id])])
        # filter for date for now:
        # 'none' for all products, 'product' for one, 'categories' for some ctg
        if inventory.filter not in ['none', 'categories', 'product']:
            raise exceptions.ValidationError(
                'Filter available by date are:'
                '"None", "Categories", "Product"')
        if inventory.filter == 'categories':
            product_ids = self.env['product.product'].search([
                ('categ_id', 'in', inventory.categ_ids.ids)
            ])
        elif inventory.filter == 'product':
            product_ids = inventory.product_id
        else:
            product_ids = self.env['product.product'].search([])
        res = {}
        flag = False
        move_obj = self.env['stock.move']
        uom_obj = self.env['product.uom']
        for location in location_ids:
            datas = {}
            res[location.id] = {}
            move_ids = move_obj.search(
                ['|',
                    ('location_dest_id', '=', location.id),
                    ('location_id', '=', location.id),
                    ('state', '=', 'done'),
                    ('product_id', 'in', product_ids.ids),
                    ('date', '<=', inventory.date_inventory)])
            for move in move_ids:
                lot_id = False
                if move.lot_ids:
                    #todo: create one line for lot
                    lot_id = move.lot_ids[0].id
                prod_id = move.product_id.id
                if move.location_dest_id.id == location.id:
                    qty = uom_obj._compute_qty(move.product_uom.id,
                                               move.product_qty,
                                               move.product_id.uom_id.id)
                else:
                    qty = -uom_obj._compute_qty(move.product_uom.id,
                                                move.product_qty,
                                                move.product_id.uom_id.id)

                if datas.get((prod_id, lot_id)):
                    qty += datas[(prod_id, lot_id)]['product_qty']

                datas[(prod_id, lot_id)] = {
                    'product_id': prod_id,
                    'location_id': location.id,
                    'product_qty': qty,
                    'theoretical_qty': qty,
                    'product_uom_id': move.product_id.uom_id.id,
                    'prod_lot_id': lot_id,
                    'inventory_id': inventory.id,
                }
            if datas:
                flag = True
                res[location.id] = datas

        if not flag:
            raise exceptions.ValidationError(
                _('No product in this location.'))
        vals = []
        for stock_move in res.values():
            for stock_move_details in stock_move.values():
                vals.append(stock_move_details)
        return vals

    @api.multi
    def prepare_inventory(self):
        inventory_line_obj = self.env['stock.inventory.line']
        for inventory in self:
            if inventory.date_inventory:
                vals = self._get_inventory_lines_by_date(inventory)
                for product_line in vals:
                    inventory_line_obj.create(product_line)
            else:
                return super(StockInventory, self).prepare_inventory()
        return self.write({
            'state': 'confirm',
            'date': fields.Datetime.now()})
