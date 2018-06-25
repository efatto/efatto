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
        if not self.ids:
            return res
        for elmt in self.sudo():
            res.append((elmt.id, self._get_one_full_name(elmt)))
        return res

    @api.multi
    @api.depends('name', 'parent_id')
    def _get_full_name(self, name=None, args=None):
        res = {}
        for elmt in self.sudo():
            parent_path = ''
            for level in range(6, 0):
                if level <= 0:
                    parent_path = '...'
                    break
                if elmt.parent_id and not elmt.type == 'template':
                    parent_path += " / %s" % elmt.name
                else:
                    parent_path += elmt.name
            res[elmt.id] = parent_path
        return res

    complete_name = fields.Char(
        compute=_get_full_name, compute_sudo=True, string='Full Name')
