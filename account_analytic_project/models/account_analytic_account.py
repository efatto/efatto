# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def get_progress(self):
        for account in self:
            account.progress_hours = 0.0
            if account.hours_done and account.hours_planned:
                account.progress_hours = \
                    account.hours_done / account.hours_planned * 100

    @api.multi
    @api.depends('project_ids')
    def _compute_hours(self):
        newself = self.sudo()
        analytic_line_model = self.env['account.analytic.line']
        project_task_model = self.env['project.task']
        sale_line_model = newself.env['sale.order.line']
        uom_time_categ_id = self.env.ref('uom.uom_categ_wtime')
        for analytic in self:
            qty_ordered = 0.0
            hours_delivered = 0.0
            hours_invoiced = 0.0
            project_fetch_data = project_task_model.read_group(
                [('project_id', 'in', analytic.sudo().with_context(
                    active_test=False).project_ids.ids)],
                ['planned_hours'], [],
            )
            hours_planned = project_fetch_data[0]['planned_hours'] or 0.0
            analytic_fetch_data = analytic_line_model.read_group(
                [('project_id', 'in', analytic.sudo().with_context(
                    active_test=False).project_ids.ids)],
                ['unit_amount'], [],
            )
            hours_done = analytic_fetch_data[0]['unit_amount'] or 0.0
            sale_fetch_data = sale_line_model.read_group(
                [('order_id.analytic_account_id', '=', analytic.id),
                 ('order_id.state', 'not in', ['draft', 'sent', 'cancel'])],
                ['product_uom_qty', 'qty_delivered', 'qty_invoiced',
                 'product_uom'], ['product_uom'],
            )
            for d in sale_fetch_data:
                uom_hour = self.env.ref('uom.product_uom_hour')
                uom_base_id = d.get('product_uom', False) and d['product_uom'][:1] \
                    or self.env.ref('uom.product_uom_unit').id
                uom_base = self.env['uom.uom'].browse(uom_base_id)
                if d.get('product_uom_qty'):
                    qty_ordered += uom_base._compute_quantity(
                        d['product_uom_qty'], uom_hour if uom_base.category_id
                        == uom_time_categ_id else uom_base)
                if d.get('qty_delivered'):
                    hours_delivered += uom_base._compute_quantity(
                        d['qty_delivered'], uom_hour if uom_base.category_id ==
                        uom_time_categ_id else uom_base)
                if d.get('qty_invoiced'):
                    hours_invoiced += uom_base._compute_quantity(
                        d['qty_invoiced'], uom_hour if uom_base.category_id ==
                        uom_time_categ_id else uom_base)
            analytic.hours_done = hours_done
            analytic.qty_ordered = qty_ordered
            analytic.hours_planned = hours_planned
            analytic.hours_residual = hours_planned - hours_done
            analytic.hours_delivered = hours_delivered
            analytic.hours_invoiced = hours_invoiced

    @api.multi
    def _get_amount_remaining(self):
        for account in self:
            account.amount_remaining = \
                account.total_sale - account.total_invoiced

    @api.multi
    def _get_last_invoice_date(self):
        invoice_model = self.env['account.invoice']
        for analytic in self:
            fetch_data = invoice_model.search_read(
                [('invoice_line_ids.account_analytic_id', '=', analytic.id),
                 ('invoice_line_ids.invoice_id.date', '!=', False),
                 ('type', 'in', ['out_invoice', 'out_refund'])],
                ['date_invoice'], limit=1, order='date_invoice desc',
            )
            if fetch_data:
                analytic.last_invoice_date = fetch_data[0]['date_invoice']

    last_invoice_date = fields.Date(
        string='Last invoice Date', compute=_get_last_invoice_date)
    amount_remaining = fields.Float(
        compute=_get_amount_remaining,
        string='Remaining Revenue',
        help="Computed using the formula: Sale Amount - Invoiced Amount",
        digits=dp.get_precision('Account'))
    qty_ordered = fields.Float(
        string="Ordered Qty",
        help="Sum qty ordered as shown in sale order lines",
        compute=_compute_hours)
    hours_planned = fields.Float(
        string="Planned Hours",
        help="Sum hours planned in tasks",
        compute=_compute_hours)
    hours_done = fields.Float(
        string="Done Hours",
        help="Sum hours done in timesheets",
        compute=_compute_hours)
    hours_delivered = fields.Float(
        string="Delivered Hours",
        help="Sum hours delivered as shown in sale order lines",
        compute=_compute_hours)
    hours_invoiced = fields.Float(
        string="Hours Invoiced",
        help="Sum hours invoiced as shown in sale order lines",
        compute=_compute_hours)
    hours_residual = fields.Float(
        string="Residual Hours",
        help="Hours planned - Hours done",
        compute=_compute_hours)
    progress_hours = fields.Float(
        help='Progress % of Hours done / Hours planned',
        compute=get_progress)
    manager_id = fields.Many2one(
        'res.users', 'Account Manager', track_visibility='onchange')
    date_end = fields.Date('End Date')
    total_invoiced_form = fields.Float(related='total_invoiced')
    total_sale_form = fields.Float(related='total_sale')
    date_start = fields.Date(string='Start Date')
