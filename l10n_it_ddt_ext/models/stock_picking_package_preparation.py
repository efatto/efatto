# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class StockDdtType(models.Model):
    _inherit = 'stock.ddt.type'

    # fields for migration compatibility from 8.0 todo test if it works!!!
    default_carriage_condition_id = fields.Many2one(
        'stock.picking.carriage_condition', 'Carriage Condition',
        oldname='carriage_condition_id')
    default_goods_description_id = fields.Many2one(
        'stock.picking.goods_description', 'Description of Goods',
        oldname='goods_description_id')
    default_transportation_reason_id = fields.Many2one(
        'stock.picking.transportation_reason',
        'Reason for Transportation',
        oldname='transportation_reason_id')
    default_transportation_method_id = fields.Many2one(
        'stock.picking.transportation_method',
        'Method of Transportation',
        oldname='transportation_method_id')


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'
    _order = 'ddt_number desc'

    FIELDS_STATES = {'done': [('readonly', True)],
                     'in_pack': [('readonly', True)],
                     'cancel': [('readonly', True)]}

    ddt_date_start = fields.Datetime(string='DDT date start',
                                     copy=False)
    date = fields.Date(string='Document Date',
                       default=fields.Datetime.now,
                       states=FIELDS_STATES,
                       copy=False)
    partner_invoice_id = fields.Many2one('res.partner',
                                         string='Invoice Address')
    partner_shipping_id = fields.Many2one(string='Delivery Address')
    ddt_type_id = fields.Many2one(required=True)

    @api.multi
    def action_done(self):
        # do not transfer already done pickings todo check if needed
        if not self.mapped('package_id'):
            raise exceptions.Warning(
                _('The package has not been generated.')
            )
        self.picking_ids.filtered(lambda x: x.state != 'done').do_transfer()
        self.write({'state': 'done', 'date_done': fields.Datetime.now()})

    @api.multi
    def set_done(self):
        # put date in context to get correct next id sequence
        for package in self:
            if not package.ddt_number:
                package.ddt_number = package.ddt_type_id.sequence_id.\
                    with_context({'ir_sequence_date': package.date}
                                 ).next_by_id()
        return super(StockPickingPackagePreparation, self).set_done()

    @api.multi
    def action_put_in_pack(self):
        # put date in context to get correct next id sequence and check if
        # the date of ddt is possible, if not change it to last date available
        for package in self:
            # ----- Assign ddt number if ddt type is set
            if package.ddt_type_id and not package.ddt_number:
                package.ddt_number = package.ddt_type_id.sequence_id.\
                    with_context({'ir_sequence_date': package.date}
                                 ).next_by_id()
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
