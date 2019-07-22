# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
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
    def _compute_hours(self):
        newself = self.sudo()
        analytic_line_model = self.env['account.analytic.line']
        project_task_model = self.env['project.task']
        sale_line_model = newself.env['sale.order.line']
        time_type_id = self.env.ref('product.uom_categ_wtime')
        for analytic in self:
            qty_ordered = 0.0
            hours_delivered = 0.0
            hours_invoiced = 0.0
            project_fetch_data = project_task_model.read_group(
                [('project_id', 'in', analytic.sudo().project_ids.ids)],
                ['planned_hours'], [],
            )
            hours_planned = project_fetch_data[0]['planned_hours'] or 0.0
            analytic_fetch_data = analytic_line_model.read_group(
                [('project_id', 'in', analytic.sudo().project_ids.ids)],
                ['unit_amount'], [],
            )
            hours_done = analytic_fetch_data[0]['unit_amount'] or 0.0
            sale_fetch_data = sale_line_model.read_group(
                [('order_id.project_id', '=', analytic.id),
                 ('product_uom.category_id', '=', time_type_id.id),
                 ('order_id.state', 'not in', ['draft', 'sent', 'cancel'])],
                ['product_uom_qty', 'qty_delivered', 'qty_invoiced',
                 'product_uom'], ['product_uom'],
            )
            for d in sale_fetch_data:
                if not d.get('product_uom_qty') and not d.get('qty_delivered')\
                        and not d.get('qty_invoiced'):
                    continue
                # get total hours planned
                uom = self.env.ref('product.product_uom_hour')
                uom_base = self.env['product.uom'].browse(d['product_uom'][0])
                if d.get('product_uom_qty'):
                    qty_ordered += uom_base._compute_quantity(
                        d['product_uom_qty'], uom)
                if d.get('qty_delivered'):
                    hours_delivered += uom_base._compute_quantity(
                        d['qty_delivered'], uom)
                if d.get('qty_invoiced'):
                    hours_invoiced += uom_base._compute_quantity(
                        d['qty_invoiced'], uom)
            analytic.hours_done = hours_done
            analytic.qty_ordered = qty_ordered
            analytic.hours_planned = hours_planned
            analytic.hours_residual = hours_planned - hours_done
            analytic.hours_delivered = hours_delivered
            analytic.hours_invoiced = hours_invoiced
            #FIXME le ore sono da fatturare se non gia chiuso l'ordine
            # e se l'ordine va fatturato ad ore (le singole righe a sto punto)
            analytic.hours_tobe_invoiced = hours_delivered - hours_invoiced

    @api.multi
    def _get_amount_sal_to_invoice(self):
        for account in self:
            total = 0.0
            for sal in account.account_analytic_sal_ids:
                if sal.done or sal.percent_completion > 0.0:
                    # account.progress_works_planned >
                    # and not sal.invoiced:
                    total += sal.amount_toinvoice
                    total -= sal.amount_invoiced
            account.amount_sal_to_invoice += total

    @api.multi
    def _get_amount_remaining(self):
        for account in self:
            account.amount_remaining = \
                account.total_sale - account.total_invoiced

    @api.multi
    @api.depends('invoice_line_ids')
    def _get_last_invoice_date(self):
        invoice_model = self.env['account.invoice']
        for analytic in self:
            fetch_data = invoice_model.search_read(
                [('invoice_line_ids.account_analytic_id', '=', analytic.id),
                 ('state', 'in', ['open', 'paid']),
                 ('type', 'in', ['out_invoice', 'out_refund'])],
                ['date_invoice'], limit=1, order='date_invoice desc',
            )
            if fetch_data:
                analytic.last_invoice_date = fetch_data[0]['date_invoice']

    invoice_line_ids = fields.One2many(
        string='Invoice lines',
        comodel_name='account.invoice.line',
        inverse_name='account_analytic_id')
    last_invoice_date = fields.Date(
        string='Last invoice Date', compute='_get_last_invoice_date',
        store=True)
    use_sal = fields.Boolean(
        string='Use SAL')
    amount_remaining = fields.Float(
        compute='_get_amount_remaining',
        string='Remaining Revenue',
        help="Computed using the formula: Sale Amount - Invoiced Amount",
        digits=dp.get_precision('Account'))
    qty_ordered = fields.Float(
        string="Ordered Qty",
        help="Sum qty ordered as shown in sale order lines",
        compute='_compute_hours')
    hours_planned = fields.Float(
        string="Planned Hours",
        help="Sum hours planned in tasks",
        compute='_compute_hours')
    hours_done = fields.Float(
        string="Done Hours",
        help="Sum hours done in timesheets",
        compute='_compute_hours')
    hours_delivered = fields.Float(
        string="Delivered Hours",
        help="Sum hours delivered as shown in sale order lines",
        compute='_compute_hours')
    hours_tobe_invoiced = fields.Float(
        string="Hours to be Invoiced",
        compute='_compute_hours')
    hours_invoiced = fields.Float(
        string="Hours Invoiced",
        help="Sum hours invoiced as shown in sale order lines",
        compute='_compute_hours')
    hours_residual = fields.Float(
        string="Residual Hours",
        help="Hours planned - Hours done",
        compute='_compute_hours')
    progress_hours = fields.Float(
        help='Progress % of Hours done / Hours planned',
        compute='get_progress')
    account_analytic_sal_ids = fields.One2many(
        comodel_name='account.analytic.sal',
        inverse_name='account_analytic_id',
        string='Analytic SAL progression')
    amount_sal_to_invoice = fields.Float(
        compute='_get_amount_sal_to_invoice',
        help='Amount to invoice from SAL')
    manager_id = fields.Many2one(
        'res.users', 'Account Manager', track_visibility='onchange')
    date_end = fields.Date('End Date')
    total_invoiced_form = fields.Float(related='total_invoiced')
    total_sale_form = fields.Float(related='total_sale')


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    tag_id = fields.Many2one('account.analytic.tag', string="Tag", copy=True)

    @api.model
    def create(self, values):
        # todo add tag from creator model?
        #  create tag, if missing, for creator model
        #  then assign it to line
        if self._context.get('invoice') and self._context.get('type'):
            if self._context['type'] in ['out_invoice', 'out_refund']:
                tag_id = self._get_tag(_('Sales'))
            else:
                tag_id = self._get_tag(_('Purchases'))
        else:
            tag_id = self._get_tag(_('Timesheets'))
        # tag_id = self._get_tags('Materials')
        # tag_id = self._get_tags('Generic')
        values.update({
            'tag_id': tag_id.id
        })
        res = super(AccountAnalyticLine, self).create(values)
        return res

    @api.multi
    def _get_tag(self, name):
        tag_id = self.env['account.analytic.tag'].search([
            ('name', '=', name)
        ], limit=1)
        if not tag_id:
            tag_id = self.env['account.analytic.tag'].create({
                'name': name
            })
        return tag_id


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    account_analytic_sal_id = fields.Many2one(
        comodel_name='account.analytic.sal',
        string='Analytic SAL',
        help='SAL linked to this line'
    )


class AccountAnalyticSal(models.Model):
    _name = 'account.analytic.sal'
    _description = 'Account Analytic SAL'
    _order = 'id ASC'

    @api.multi
    def get_invoiced_sal(self):
        for sal in self:
            amount_invoiced = 0.0
            account_invoice_line_ids = self.env['account.invoice.line'].search(
                [('account_analytic_sal_id', '=', sal.id)])
            for line in account_invoice_line_ids:
                if line.invoice_id.state in ['open', 'done']:
                    amount_invoiced += line.price_subtotal
            if amount_invoiced >= sal.amount_toinvoice > 0.0:
                sal.invoiced = True
            # set automatically sal done when progress>sal percent completion
            if sal.percent_completion > 0.0:
                #sal.account_analytic_id.progress_works_planned >
                sal.done = True
            sal.amount_invoiced = amount_invoiced

    @api.multi
    def _compute_amount_toinvoice(self):
        for sal in self:
            sal.amount_toinvoice = sal.account_analytic_id.\
                total_sale * sal.percent_toinvoice / 100

    name = fields.Char('SAL name')
    percent_completion = fields.Float(
        'SAL percent completion',
        digits=dp.get_precision('Account'),
        help='Percent SAL completion. When reached will start action linked.'
    )
    percent_toinvoice = fields.Float(
        'SAL percent to invoice',
        digits=dp.get_precision('Account'))
    amount_toinvoice = fields.Float(
        'SAL amount to invoice',
        compute='_compute_amount_toinvoice',
        digits=dp.get_precision('Account'))
    amount_invoiced = fields.Float(
        'SAL amount invoiced',
        compute='get_invoiced_sal',
        digits=dp.get_precision('Account'))
    done = fields.Boolean(
        string='SAL done',
        help='SAL is marked done when completion percent is superior'
             ' of account progress bar. It can be marked even manually.'
    )
    invoiced = fields.Boolean(
        string='SAL invoiced',
        help='SAL is marked invoiced when amount invoice lines with sal '
             'reference is superior '
             'of SAL amount. It can be marked even manually.'
    )
    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic account',
        ondelete='cascade',
        required=True
    )
    action_id = fields.Many2one(
        comodel_name='ir.actions.server',
        string='Server Action to do',
        help='This action will be done on SAL condition if not already done.'
    )
    action_res_model_id = fields.Char(
        string='Related Model for server action done by the event',
        readonly=True
    )
    action_res_id = fields.Integer(
        string='Related ID for server action done by the event',
        readonly=True
    )

    @api.multi
    @api.constrains('percent_toinvoice')
    def _check_percent_toinvoice(self):
        percent_toinvoice_total = 0.0
        for sal in self.account_analytic_id.account_analytic_sal_ids:
            percent_toinvoice_total += sal.percent_toinvoice
        if percent_toinvoice_total > 100.0:
            raise exceptions.ValidationError(
                "SAL total % to invoice must be <= 100%")
