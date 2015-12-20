# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from openerp import fields, models, exceptions, api, _


class RibaAccreditation(models.TransientModel):
    _inherit = "riba.accreditation"

    def _get_accreditation_amount(self, cr, uid, context=None):
        super(RibaAccreditation, self)._get_accreditation_amount(cr, uid, context=context)
        if context is None:
            context = {}
        if not context.get('active_id', False):
            return False
        distinta_pool = self.pool['riba.distinta']
        amount = 0.0
        config = False
        if context.get('active_model', False) == 'riba.distinta.line':
            distinta_line_pool = self.pool.get('riba.distinta.line')
            distinta_lines = distinta_line_pool.browse(
                cr, uid, context['active_ids'], context=context)
            for line in distinta_lines:
                if not config:
                    config = line.distinta_id.config_id
                if line.distinta_id.config_id != config:
                    raise exceptions.Warning(
                        _('Error'),
                        _('Accredit only one bank configuration is possible'))
                if line.state in ['confirmed', 'accredited']:
                    amount += line.amount
        elif context.get('active_model', False) == 'riba.distinta':
            distinta = distinta_pool.browse(
                cr, uid, context['active_id'], context=context)
            for line in distinta.line_ids:
                if line.tobe_accredited and line.state in ['confirmed', 'accredited']:
                    amount += line.amount
        return amount

    acceptance_account_id = fields.Many2one(
        'account.account',
        string="Ri.Ba. acceptance account")
    date_accreditation = fields.Date(
        'Accreditation date')
