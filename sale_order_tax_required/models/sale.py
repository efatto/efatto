# -*- coding: utf-8 -*-

from openerp import models, api, exceptions, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def tax_required(self):
        errors = []
        for order in self:
            for order_line in order.order_line:
                if not order_line.tax_id or len(order_line.tax_id) > 1:
                    error_string = "%s \n" % order_line.name
                    errors.append(error_string)
        if errors:
            errors_full_string = ','.join(x for x in errors)
            raise exceptions.Warning(
                _('Missing or Multiple Taxes Defined in lines:'), errors_full_string)
        else:
            return True

    @api.multi
    def action_button_confirm(self):
        self.tax_required()
        res = super(SaleOrder, self).action_button_confirm()
        return res
