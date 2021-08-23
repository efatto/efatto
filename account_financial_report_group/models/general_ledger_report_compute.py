# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class GeneralLedgerReportMoveLine(models.TransientModel):

    _inherit = 'report_general_ledger_move_line'

    is_orphan = fields.Boolean()
    sequence = fields.Integer(default=0)
    merged = fields.Boolean()


class GeneralLedgerReportCompute(models.TransientModel):
    _inherit = 'report_general_ledger'

    group_method = fields.Selection([
        ('group_payments', 'Merge payments'),
        ('group_invoices', 'Group Invoices'),
        ('no_group', 'No Group')
    ], string="Group method")

    @api.multi
    def compute_data_for_report(self,
                                with_line_details=True,
                                with_partners=True):
        res = super().compute_data_for_report(
            with_line_details=with_line_details,
            with_partners=with_partners)
        if self.group_method != 'no_group':
            receivable_lines = self.env['report_general_ledger_account'].search([
                ('report_id', '=', self.id),
                ('account_id', 'in', self.filter_account_ids.ids),
            ])
            lines = self.env['report_general_ledger_partner'].search([
                ('report_account_id', 'in', receivable_lines.ids),
                ('partner_id', 'in', self.filter_partner_ids.ids),
            ])
            if self.group_method == 'group_payments':
                for line in lines:
                    self._merge_lines(line.move_line_ids)
            elif self.group_method == 'group_invoices':
                for line in lines:
                    sorted_lines = self._get_sorted_invoices(line.move_line_ids)
                    i = 1
                    for sorted_line in sorted_lines:
                        sorted_line.sequence = i
                        i += 1
        return res

    @staticmethod
    def _merge_lines(lines):
        for line in lines:
            for l in [x for x in lines if x.id != line.id and not x.merged]:
                if l.date == line.date and \
                        l.entry == line.entry and \
                        l.journal == line.journal and \
                        l.partner == line.partner and \
                        l.label == line.label and \
                        l.currency_id == line.currency_id:
                        # l['supplier_invoice_number'] == \
                        #     line['supplier_invoice_number']:
                    line.debit += l.debit
                    line.credit += l.credit
                    line.amount_currency += l.amount_currency
                    line.cumul_balance = l.cumul_balance
                    line.date_maturity = ''
                    l.credit = l.debit = l.amount_currency = 0.0

    @staticmethod
    def _get_sorted_invoices(lines):
        inv_lines = sorted([x for x in lines if x.move_line_id.invoice_id],
                           key=lambda z: (
                               z.move_line_id.invoice_id.number +
                               z.move_line_id.date_maturity.strftime('%d-%m-%Y')))
        res_lines = sorted([x for x in lines if x not in inv_lines],
                           key=lambda y: y.move_line_id.date)
        inv = False
        for i, line in enumerate(inv_lines):
            a = 0
            if line.move_line_id.invoice_id:
                inv = line.move_line_id.invoice_id
            for res_line in res_lines:
                # line with reconcile_id are never passed with name search
                if inv and res_line in [x for x in inv.unsolved_move_line_ids]:
                    settlement_lines = inv.move_id.line_ids.filtered(
                        lambda t: t.account_id.id == inv.partner_id.
                        property_account_receivable.id)
                    if len(settlement_lines) > 1:
                        # if this line have date > all settlement lines
                        # put in the last
                        last_settlement_line = settlement_lines.sorted(
                            key=lambda k: k.date_maturity, reverse=True)[0]
                        if last_settlement_line.date <= line.move_line_id.date:
                            if line == last_settlement_line:
                                inv_lines.insert(i + a + 1, res_line)
                                a += 1
                                res_lines.remove(res_line)
                            continue
                        # if there is a another settlement_line with
                        # date <= this line, continue
                        elif settlement_lines.filtered(
                                lambda k: line.move_line_id.date < k.date <=
                                res_line.move_line_id.date and k != line):
                            continue
                        else:
                            inv_lines.insert(i + a + 1, res_line)
                            a += 1
                            res_lines.remove(res_line)
                    else:
                        inv_lines.insert(i + a + 1, res_line)
                        a += 1
                        res_lines.remove(res_line)
                elif res_line.move_line_id.full_reconcile_id:
                    if res_line.move_line_id.full_reconcile_id \
                            == line.move_line_id.full_reconcile_id:
                        inv_lines.insert(i + a + 1, res_line)
                        a += 1
                        res_lines.remove(res_line)
                elif line.move_line_id.name == res_line.move_line_id.name or \
                        line.move_line_id.invoice_id and \
                        line.move_line_id.invoice_id.number \
                        == res_line.move_line_id.name:
                    inv_lines.insert(i+a+1, res_line)
                    a += 1
                    res_lines.remove(res_line)
        if len(res_lines) > 0:
            for reline in res_lines:
                reline.is_orphan = True
            inv_lines += res_lines
        return inv_lines
