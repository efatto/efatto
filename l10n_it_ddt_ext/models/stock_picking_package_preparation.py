# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class StockDdtType(models.Model):
    _inherit = 'stock.ddt.type'

    carriage_condition_id = fields.Many2one(
        'stock.picking.carriage_condition', 'Carriage Condition')
    goods_description_id = fields.Many2one(
        'stock.picking.goods_description', 'Description of Goods')
    transportation_reason_id = fields.Many2one(
        'stock.picking.transportation_reason',
        'Reason for Transportation')
    transportation_method_id = fields.Many2one(
        'stock.picking.transportation_method',
        'Method of Transportation')


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'
    _order = 'ddt_number desc'

    FIELDS_STATES = {'done': [('readonly', True)],
                     'in_pack': [('readonly', True)],
                     'cancel': [('readonly', True)]}

    @api.multi
    def _get_all_picking_done(self):
        for sppp in self:
            picking_state = sppp.picking_ids.mapped('state')
            sppp.all_picking_done = True if (
                len(picking_state) == 1
                and picking_state[0] == 'done') else False

    ddt_date_start = fields.Datetime(
        string='DDT date start',
    )
    date = fields.Date(
        string='Document Date',
        default=fields.Datetime.now,
        states=FIELDS_STATES,
    )
    partner_invoice_id = fields.Many2one(string='Invoice Address')
    partner_shipping_id = fields.Many2one(string='Delivery Address')
    ddt_type_id = fields.Many2one(required=True)
    all_picking_done = fields.Boolean(compute=_get_all_picking_done)

    @api.multi
    def action_draft(self):
        if any(prep.state == 'done' for prep in self):
            raise exceptions.Warning(
                _('Done package preparations cannot be reset to draft.')
            )
        self.write({'state': 'draft'})

    @api.multi
    def set_done(self):
        # put fy in context to get fy sequence
        for package in self:
            if not package.ddt_number:
                fy_id = self.env['account.fiscalyear'].find(
                    dt=datetime.strptime(
                        package.date, DEFAULT_SERVER_DATE_FORMAT))
                package.ddt_number = package.ddt_type_id.sequence_id.\
                    with_context({'fiscalyear_id': fy_id}).get(
                        package.ddt_type_id.sequence_id.code)
        return super(StockPickingPackagePreparation, self).set_done()

    @api.multi
    def action_put_in_pack(self):
        # put fy in context to get fy sequence
        for package in self:
            # ----- Assign ddt number if ddt type is set
            if package.ddt_type_id and not package.ddt_number:
                fy_id = self.env['account.fiscalyear'].find(
                    dt=datetime.strptime(
                        package.date, DEFAULT_SERVER_DATE_FORMAT))
                package.ddt_number = package.ddt_type_id.sequence_id.\
                    with_context({'fiscalyear_id': fy_id}).get(
                        package.ddt_type_id.sequence_id.code)
                # check date progression
                ddt_type_ids = self.env['stock.ddt.type'].search([
                    ('sequence_id', '=', package.ddt_type_id.sequence_id.id)
                ])
                last_ddt = self.search([
                    ('date', '>', package.date),
                    ('ddt_number', '<', package.ddt_number),
                    ('ddt_type_id', 'in', ddt_type_ids.ids),
                    ],
                    order='date desc', limit=1,
                )
                # last_ddt has a date > current ddt
                if last_ddt:
                    # today can be used
                    if fields.Date.today() > last_ddt.date:
                        package.date = fields.Date.today()
                    # last date is in the future, so use it
                    else:
                        package.date = last_ddt.date
        return super(StockPickingPackagePreparation, self).action_put_in_pack()

    @api.onchange('partner_id', 'ddt_type_id')
    def on_change_partner(self):
        super(StockPickingPackagePreparation, self).on_change_partner()
        if self.ddt_type_id:
            if not self.carriage_condition_id:
                if self._context.get('carriage_condition_id', False):
                    self.carriage_condition_id = self._context[
                        'carriage_condition_id']
                else:
                    self.carriage_condition_id = \
                        self.ddt_type_id.carriage_condition_id.id \
                        if self.ddt_type_id.carriage_condition_id else False
            if not self.goods_description_id:
                if self._context.get('goods_description_id', False):
                    self.goods_description_id = self._context[
                        'goods_description_id']
                else:
                    self.goods_description_id = \
                        self.ddt_type_id.goods_description_id.id \
                        if self.ddt_type_id.goods_description_id else False
            if not self.transportation_reason_id:
                if self._context.get('transportation_reason_id', False):
                    self.transportation_reason_id = self._context[
                        'transportation_reason_id']
                else:
                    self.transportation_reason_id = \
                        self.ddt_type_id.transportation_reason_id.id \
                        if self.ddt_type_id.transportation_reason_id else False
            if not self.transportation_method_id:
                if self._context.get('transportation_method_id', False):
                    self.transportation_method_id = self._context[
                        'transportation_method_id']
                else:
                    self.transportation_method_id = \
                        self.ddt_type_id.transportation_method_id.id \
                        if self.ddt_type_id.transportation_method_id else False
