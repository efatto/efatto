# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def action_invoice_open(self):
        res = super().action_invoice_open()
        if not self:
            return res
        analytic_invoice_line_ids = self.mapped('invoice_line_ids').filtered(
            lambda x: x.product_id and x.account_analytic_id
        )
        # todo group lines by product and analytic account
        analytic_invoice_line_ids.account_stock_price_unit_sync()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def _get_invoice_line_price_unit(self):
        self.ensure_one()
        line = self[0]
        invoice = line.invoice_id
        price_unit = line.price_unit
        if line.invoice_line_tax_ids:
            price_unit = line.invoice_line_tax_ids.with_context(
                round=False
            ).compute_all(
                price_unit, currency=invoice.currency_id, quantity=1.0,
                product=line.product_id, partner=invoice.partner_id
            )['total_excluded']
        if line.uom_id.id != line.product_id.uom_id.id:
            price_unit *= line.uom_id.factor / line.product_id.uom_id.factor
        if invoice.currency_id != invoice.company_id.currency_id:
            price_unit = invoice.currency_id._convert(
                price_unit, invoice.company_id.currency_id,
                self.company_id, invoice.date or fields.Date.today(), round=False)
        return price_unit

    @api.multi
    def account_stock_price_unit_sync(self):
        for line in self:
            # todo a phantom bom is possible in account.invoice.line?
            # When the affected product is a kit we do nothing, which is the
            # default behavior on the standard: the move is exploded into moves
            # for the components and those get the default price_unit for the
            # time being. We avoid a hard dependency as well.
            if (
                hasattr(line.product_id, "bom_ids")
                and line.product_id._is_phantom_bom()
            ):
                continue
            # search without date nor state as they are unpredictable
            # stock move from sales or productions
            used_move_ids = self.env['stock.move'].search([
                ('product_id', '=', line.product_id.id),
                ('location_dest_id.usage', 'in', ['production', 'customer']),
                '|',
                ('sale_line_id.order_id.analytic_account_id', '=',
                 line.account_analytic_id.id),
                ('raw_material_production_id.analytic_account_id', '=',
                 line.account_analytic_id.id)
            ])
            # todo compute an avg price on qty
            """
            aggiornare il costo dei trasferimenti stessi dalle fatture d'acquisto con
            il costo unitario medio risultante per la quantità trasferita a partire dal
            costo in fattura. Deve prendere tutte le righe fattura di quel prodotto
            con quel conto analitico e spalmare il costo ponderato su tutti gli
            scarichi fatti, sempre sul prezzo unitario (acquisto 120 pz a 5 € di
            media ponderata, vado a scrivere 5€ sul costo unitario dei trasferimenti)
            """
            used_move_ids.write({
                'price_unit': -line.with_context(
                    skip_stock_price_unit_sync=True
                )._get_invoice_line_price_unit(),
            })
