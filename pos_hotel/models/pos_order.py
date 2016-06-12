# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class PosOrder(models.Model):
    _inherit = "pos.order"

    # folio_id = fields.Many2one('hotel.folio', 'Folio Number')
    # room_no = fields.Char('Room Number')
    #
    # @api.onchange('folio_id')
    # def get_folio_partner_id(self):
    #     '''
    #     When you change folio_id, based on that it will update
    #     the guest_name and room_no as well
    #     ---------------------------------------------------------
    #     @param self: object pointer
    #     '''
    #     for rec in self:
    #         self.partner_id = False
    #         self.room_no = False
    #         if rec.folio_id:
    #             self.partner_id = rec.folio_id.partner_id.id
    #             self.room_no = rec.folio_id.room_lines[0].product_id.name

    @api.multi
    def action_paid(self):
        """
        When pos order created this method called,and sale order line
        created for current folio
        --------------------------------------------------------------
        @param self: object pointer
        """
        hotel_folio_obj = self.env['hotel.folio']
        hsl_obj = self.env['hotel.service.line']
        so_line_obj = self.env['sale.order.line']
        for order_obj in self:
                if order_obj.partner_id.folio_id:
                    for line in order_obj.lines:
                        values = {'order_id':
                                  order_obj.partner_id.folio_id.order_id.id,
                                  'name': line.product_id.name,
                                  'product_id': line.product_id.id,
                                  'product_uom_qty': line.qty,
                                  'price_unit': line.price_unit,
                                  'price_subtotal': line.price_subtotal,
                                  'state': 'confirmed',
                                  }
                        sol_rec = so_line_obj.create(values)
                        hsl_obj.create({
                            'folio_id': order_obj.partner_id.folio_id.id,
                            'service_line_id': sol_rec.id})
                        hf_rec = hotel_folio_obj.browse(
                            order_obj.partner_id.folio_id.id)
                        hf_rec.write({'folio_pos_order_ids':
                                      [(4, order_obj.id)]})
        return super(PosOrder, self).action_paid()