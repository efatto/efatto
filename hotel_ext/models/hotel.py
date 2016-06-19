# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _
from openerp.exceptions import ValidationError


class HotelRoom(models.Model):
    _inherit = 'hotel.room'

    @api.model
    def create(self, vals):
        vals.update({'purchase_ok': False})
        return super(HotelRoom, self).create(vals)


class HotelFolio(models.Model):
    _inherit = 'hotel.folio'

    @api.constrains('checkin_date', 'checkout_date')
    def check_dates(self):
        self.ensure_one()
        if self.checkin_date and self.checkout_date:
            if self.checkin_date >= self.checkout_date:
                raise ValidationError(_('Check in Date Should be \
                less than the Check Out Date!'))
