# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def name_get(self):
        res = []
        for elmt in self.sudo():
            res.append((elmt.id, self._get_one_full_name(elmt)))
        return res

    @api.one
    @api.depends('name', 'parent_id')
    def _get_full_name(self):
        self.complete_name = self._get_one_full_name(self)

    complete_name = fields.Char(
        compute=_get_full_name, store=True, compute_sudo=True,
        string='Full Name')
