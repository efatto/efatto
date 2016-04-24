# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class account_move(models.Model):
    _inherit = 'account.move'

    # override list in custom module to add/drop columns or change order
    @api.model
    def _report_xls_fields(self):
        return [
            'move', 'name', 'date', 'period', 'partner', 'account',
            'date_maturity', 'debit', 'credit', 'balance', 'reconcile',
            'reconcile_partial',
            #'amount_currency', 'currency_name',
        ]

    # Change/Add Template entries
    @api.model
    def _report_xls_template(self):
        """
        Template updates, e.g.

        my_change = {
            'move':{
                'header': [1, 20, 'text', _('My Move Title')],
                'lines': [1, 0, 'text', _render("line.move_id.name or ''")],
                'totals': [1, 0, 'text', None]},
        }
        return my_change
        """
        return {}
