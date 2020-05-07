from odoo import models, fields, api, exceptions, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_cancel(self):
        for invoice in self:
            # override original check to bypass it and remove link to
            # move line in riba distinta move line
            move_line_model = self.env['account.move.line']
            rdml_model = self.env['riba.distinta.move.line']
            move_line_ids = move_line_model.search([
                ('move_id', '=', invoice.move_id.id),
                ('date_maturity', '!=', False)])
            if move_line_ids:
                riba_line_ids = rdml_model.search(
                    [('move_line_id', 'in', [m.id for m in move_line_ids])])
                if riba_line_ids:
                    riba_line_ids.write({'move_line_id': False})
        super(AccountInvoice, self).action_cancel()


# class AccountMoveLine(models.Model):
#     _inherit = "account.move.line"
#
#     @api.multi
#     def reconcile(
#         self, writeoff_acc_id=False, writeoff_journal_id=False
#     ):
#         res = super(AccountMoveLine, self).reconcile(
#              writeoff_acc_id=writeoff_acc_id,
#              writeoff_journal_id=writeoff_journal_id)
#         move_rec_obj = self.env['account.move.reconcile']
#         rec = move_rec_obj.browse(res)
#         for line in self.filtered(
#                 lambda x: x.riba and x.date_maturity):
#             rdml_model = self.env['riba.distinta.move.line']
#             # here we search for closing lines of move line of invoice: if
#             # found, line of invoice is linked to riba emitted
#             for rec_line in rec.line_id:
#                 riba_line_ids = rdml_model.search([
#                     ('move_line_id', '=', False),  # means has been unlinked
#                     ('amount', '=', rec_line.credit),
#                     ('riba_line_id.due_date', '=', line.date_maturity),
#                     ('riba_line_id.partner_id', '=',
#                      line.move_id.partner_id.id)])
#                 if riba_line_ids:
#                     riba_line_ids[0].write({'move_line_id': line.id})
#
#         return res
#
#     @api.multi
#     def reconcile_partial(
#         self, type='auto', writeoff_acc_id=False,
#         writeoff_period_id=False, writeoff_journal_id=False
#     ):
#         res = super(AccountMoveLine, self).reconcile_partial(
#             type=type, writeoff_acc_id=writeoff_acc_id,
#             writeoff_period_id=writeoff_period_id,
#             writeoff_journal_id=writeoff_journal_id)
#         move_rec_obj = self.env['account.move.reconcile']
#         rec = move_rec_obj.browse(res)
#         for line in self.filtered(
#                 lambda x: x.riba and x.date_maturity):
#             rdml_model = self.env['riba.distinta.move.line']
#             # here we search for closing lines of move line of invoice: if
#             # found, line of invoice is linked to riba emitted
#             for rec_line in rec.line_partial_ids:
#                 riba_line_ids = rdml_model.search([
#                     ('move_line_id', '=', False),  # means has been unlinked
#                     ('amount', '=', rec_line.credit),
#                     ('riba_line_id.due_date', '=', line.date_maturity),
#                     ('riba_line_id.partner_id', '=',
#                      line.move_id.partner_id.id)])
#                 if riba_line_ids:
#                     riba_line_ids[0].write({'move_line_id': line.id})
#
#         return res
