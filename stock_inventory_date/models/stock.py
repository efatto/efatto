# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, exceptions, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from dateutil import relativedelta


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
    _order = 'date DESC'

    date_inventory = fields.Date(default=fields.Date.context_today)
    search_child_location = fields.Boolean()
    no_consumable = fields.Boolean()

    @api.model
    def _get_inventory_lines_by_date(self, inventory):
        location_obj = self.env['stock.location']
        location_ids = inventory.location_id
        if inventory.search_child_location:
            location_ids = location_obj.search([
                ('id', 'child_of', [inventory.location_id.id])])
        # filter for date available:
        if inventory.filter not in [
                'none', 'categories', 'product', 'products']:
            raise exceptions.ValidationError(
                'Filter available by date are:'
                '"None", "Categories", "Product", "Products"')
        if inventory.filter == 'categories':
            if inventory.no_consumable:
                product_ids = self.env['product.product'].search([
                    ('categ_id', 'in', inventory.categ_ids.ids),
                    ('type', '=', 'product'),
                ])
            else:
                product_ids = self.env['product.product'].search([
                    ('categ_id', 'in', inventory.categ_ids.ids)
                ])
        elif inventory.filter == 'product':
            product_ids = inventory.product_id
        elif inventory.filter == 'products':
            product_ids = inventory.product_ids
        else:
            if inventory.no_consumable:
                product_ids = self.env['product.product'].search([
                    ('type', '=', 'product'),
                ])
            else:
                product_ids = self.env['product.product'].search([])
        res = {}
        flag = False
        move_obj = self.env['stock.move']
        uom_obj = self.env['product.uom']
        date_inventory = (datetime.strptime(
            inventory.date_inventory, DEFAULT_SERVER_DATE_FORMAT
        ) + relativedelta.relativedelta(
            days=1)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT
        )
        for location in location_ids:
            datas = {}
            res[location.id] = {}
            move_ids = move_obj.search(
                ['|',
                    ('location_dest_id', '=', location.id),
                    ('location_id', '=', location.id),
                    ('state', '=', 'done'),
                    ('product_id', 'in', product_ids.ids),
                    ('date', '<', date_inventory)])
            for move in move_ids:
                for quant in move.quant_ids.filtered(
                        lambda x: x.qty > 0.0):
                    lot_id = quant.lot_id.id
                    prod_id = quant.product_id.id
                    if move.location_dest_id.id == location.id:
                        qty = uom_obj._compute_qty(move.product_uom.id,
                                                   quant.qty,
                                                   quant.product_id.uom_id.id)
                    else:
                        qty = -uom_obj._compute_qty(move.product_uom.id,
                                                    quant.qty,
                                                    quant.product_id.uom_id.id)

                    if datas.get((prod_id, lot_id)):
                        qty += datas[(prod_id, lot_id)]['product_qty']

                    datas[(prod_id, lot_id)] = {
                        'product_id': prod_id,
                        'location_id': location.id,
                        'product_qty': qty,
                        'theoretical_qty': qty,
                        'product_uom_id': quant.product_id.uom_id.id,
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
                # default inventory is made with child location by default
                inventory.search_child_location = True
                return super(StockInventory, self).prepare_inventory()
        return self.write({
            'state': 'confirm',
            'date': fields.Datetime.now()})

    @api.cr_uid_context
    def post_inventory(self, cr, uid, inv, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        if inv.date_inventory:
            now = fields.Datetime.now()
            if inv.date_inventory > now:
                raise exceptions.UserError(
                    _("You can not process an actual "
                      "movement date in the future."))
            ctx['date_inventory'] = inv.date_inventory
        return super(StockInventory, self).post_inventory(
            cr, uid, inv, context=ctx)


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_done(self):
        result = super(StockMove, self).action_done()
        # overwrite date field where applicable
        if 'date_inventory' in self.env.context:
            date_inv = self.env.context.get('date_inventory')
            for move in self:
                move.date = date_inv
                if move.quant_ids:
                    move.quant_ids.sudo().write({'in_date': date_inv})
        return result
