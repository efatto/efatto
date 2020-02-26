# -*- coding: utf-8 -*-

from openerp import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    analytic_line_id = fields.Many2one(
        comodel_name='account.analytic.line',
        string='Account analytic line',
    )

    def _prepare_analytic_line(self):
        journal = self.env.ref(
            'stock_analytic_delivery.analytic_journal_delivery')
        sign = 1
        if self.location_dest_id.usage == 'customer':
            sign = -1
        res = {
            'name': self.name,
            'ref': self.picking_id.name,
            'product_id': self.product_id.id,
            'journal_id': journal.id,
            'unit_amount': -sign * self.product_uom_qty,
            'amount': sign * self.product_uom_qty * self.product_id.standard_price,
            'account_id': self.analytic_account_id.id,
            'user_id': self.env.user.id,
            'product_uom_id': self.product_uom.id
        }
        return res

    @api.multi
    def action_done(self):
        res = super(StockMove, self).action_done()
        for move in self:
            if move.analytic_account_id and (
                    move.location_dest_id.usage == 'customer' or
                    move.location_id.usage == 'customer'):
                move_id = self.env['account.analytic.line'].create(
                    move._prepare_analytic_line())
                move.analytic_line_id = move_id.id
        return res

    @api.multi
    def action_cancel(self):
        for move in self:
            if move.analytic_line_id:
                move.analytic_line_id.unlink()
        return super(StockMove, self).action_cancel()
