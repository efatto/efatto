# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, _
from openerp.exceptions import Warning as UserError


class wizard_giornale(models.TransientModel):
    _inherit = "wizard.giornale"

    def print_giornale(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)

        if wizard.target_move == 'all':
            target_type = ['posted', 'draft']
        else:
            target_type = [wizard.target_move]

        move_line_obj = self.pool['account.move.line']
        move_line_ids = move_line_obj.search(cr, uid, [
            ('date', '>=', wizard.date_move_line_from),
            ('date', '<=', wizard.date_move_line_to),
            ('move_id.state', 'in', target_type)
            ], order='date, move_id asc')
        if not move_line_ids:
            raise UserError(_('No documents found in the current selection'))
        datas = {}
        datas_form = {}
        datas_form['date_move_line_from'] = wizard.date_move_line_from
        datas_form['last_def_date_print'] = wizard.last_def_date_print
        datas_form['date_move_line_to'] = wizard.date_move_line_to
        datas_form['fiscal_page_base'] = wizard.fiscal_page_base
        datas_form['progressive_debit'] = wizard.progressive_debit2
        datas_form['progressive_credit'] = wizard.progressive_credit
        datas_form['start_row'] = wizard.start_row
        datas_form['fiscalyear'] = wizard.fiscalyear.id
        datas_form['fiscalyear_code'] = wizard.fiscalyear.code
        datas_form['print_state'] = 'draft'
        report_name = 'l10n_it_central_journal.report_giornale'
        datas = {
            'ids': move_line_ids,
            'model': 'account.move',
            'form': datas_form
        }
        return self.pool['report'].get_action(
            cr, uid, [], report_name, data=datas, context=context)

    def print_giornale_final(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        if wizard.date_move_line_from <= wizard.last_def_date_print:
            raise UserError(_('Date already printed'))
        else:
            if wizard.target_move == 'all':
                target_type = ['posted', 'draft']
            else:
                target_type = [wizard.target_move]

            move_line_obj = self.pool['account.move.line']
            move_line_ids = move_line_obj.search(cr, uid, [
                ('date', '>=', wizard.date_move_line_from),
                ('date', '<=', wizard.date_move_line_to),
                ('move_id.state', 'in', target_type)
                ], order='date, move_id asc')
            if not move_line_ids:
                raise UserError(
                    _('No documents found in the current selection'))
            datas = {}
            datas_form = {}
            datas_form['date_move_line_from'] = wizard.date_move_line_from
            datas_form['last_def_date_print'] = wizard.last_def_date_print
            datas_form['date_move_line_to'] = wizard.date_move_line_to
            datas_form['fiscal_page_base'] = wizard.fiscal_page_base
            datas_form['progressive_debit'] = wizard.progressive_debit2
            datas_form['progressive_credit'] = wizard.progressive_credit
            datas_form['fiscalyear'] = wizard.fiscalyear.id
            datas_form['fiscalyear_code'] = wizard.fiscalyear.code
            datas_form['start_row'] = wizard.start_row
            datas_form['print_state'] = 'def'
            report_name = 'l10n_it_central_journal.report_giornale'
            datas = {
                'ids': move_line_ids,
                'model': 'account.move',
                'form': datas_form
            }
            return self.pool['report'].get_action(
                cr, uid, [], report_name, data=datas, context=context)
