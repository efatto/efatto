# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_order_count = fields.Integer(compute='_compute_sale_order_count')
    quotation_order_count = fields.Integer(
        compute='_compute_sale_order_count', string='# of Sales Quotation')

    def _compute_sale_order_count(self):
        sale_data = self.env['sale.order'].read_group(
            domain=[('partner_id', 'child_of', self.ids),
                    ('state', 'not in', ['draft', 'sent', 'cancel'])],
            fields=['partner_id'], groupby=['partner_id'])
        quotation_data = self.env['sale.order'].read_group(
            domain=[('partner_id', 'child_of', self.ids),
                    ('state', 'in', ['draft', 'sent', 'cancel'])],
            fields=['partner_id'], groupby=['partner_id'])
        # read to keep the child/parent relation while aggregating the
        # read_group result in the loop
        partner_child_ids = self.read(['child_ids'])
        mapped_sale_data = dict(
            [(m['partner_id'][0], m['partner_id_count']) for m in sale_data])
        mapped_quotation_data = dict(
            [(m['partner_id'][0], m['partner_id_count']) for m in
             quotation_data])
        for partner in self:
            # let's obtain the partner id and all its child ids from the read
            # up there
            partner_ids = filter(
                lambda r: r['id'] == partner.id, partner_child_ids)[0]
            partner_ids = [partner_ids.get('id')] + \
                          partner_ids.get('child_ids')
            # then we can sum for all the partner's child
            partner.sale_order_count = sum(
                mapped_sale_data.get(child, 0) for child in partner_ids)
            partner.quotation_order_count = sum(
                mapped_quotation_data.get(child, 0) for child in partner_ids)
