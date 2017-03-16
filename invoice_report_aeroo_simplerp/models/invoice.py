# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

import time
import re
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from collections import defaultdict, Mapping, OrderedDict
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from PIL import Image

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'invoice_tree': self._get_invoice_tree,
            'italian_number': self._get_italian_number,
            'invoice_move_lines': self._get_invoice_move_lines,
            'ddt': self._get_ddt,
            'ddt_tree': self._get_ddt_tree,
            'set_picking': self._set_picking,
            'div': self._div,
            'line_description': self._line_description,
            'desc_nocode': self._desc_nocode,
            'total_fiscal': self._get_total_fiscal,
            'total_tax_fiscal': self._get_total_tax_fiscal,
            'address_invoice_id': self._get_invoice_address,
            'variant_images': self._variant_images,
            'sale_weight': self._sale_weight,
            'translate': self._translate_text,
            'img_gray': self._convert_to_gray_scale,
            'get_total_discount': self._get_total_discount,
            'get_total_other': self._get_total_other_amount,
            'get_total_contribution': self._get_total_contribution_amount,
            'get_total_transport': self._get_total_transport_amount,
            'get_total_goods': self._get_total_goods_amount,
            'check_installed_module': self._check_installed_module,
        })
        self.cache = {}

    def _get_invoice_address(self):
        invoice = self.pool['account.invoice'].browse(self.cr, self.uid,
                                                      self.ids[0])
        invoice_address = invoice.partner_id
        for address in invoice.partner_id.child_ids:
            if address.type == 'invoice':
                invoice_address = address
        return invoice_address


    def _get_total_tax_fiscal(self, tax_line):
        invoice = self.pool['account.invoice'].browse(self.cr, self.uid, self.ids[0])
        amount_withholding = 0.0
        for line in tax_line:
            if line.tax_code_id.notprintable:
                amount_withholding += line.tax_amount
        if amount_withholding != 0.0:
            return invoice.amount_tax - amount_withholding
        return invoice.amount_tax

    def _get_total_fiscal(self, tax_line):
        invoice = self.pool['account.invoice'].browse(self.cr, self.uid, self.ids[0])
        amount_withholding = 0.0
        for line in tax_line:
            if line.tax_code_id.notprintable:
                amount_withholding += line.tax_amount
        if amount_withholding != 0.0:
            return invoice.amount_total - amount_withholding
        return invoice.amount_total

    def _desc_nocode(self, string):
        return re.compile('\[.*\]\ ').sub('', string)

    def _line_description(self, origin):
        sale_order_line_obj = self.pool['sale.order.line']
        stock_picking_obj = self.pool['stock.picking']
        description = []
        if origin and len(origin.split(':')) == 3: # inserire l10n_it_ddt
            sale_order_id = int(origin.split(':')[2])
            sale_order_line = sale_order_line_obj.browse(self.cr, self.uid, sale_order_id)
            description.append(u'Contratto: {name}'.format(name=sale_order_line.order_id.name))
            picking_in_ids = stock_picking_obj.search(self.cr, self.uid, [('type', '=', 'in'), ('rentable', '=', True), ('origin', '=', sale_order_line.order_id.name)])
            picking_out_ids = stock_picking_obj.search(self.cr, self.uid, [('type', '=', 'out'), ('origin', '=', sale_order_line.order_id.name)])
            picking_in = False
            if picking_in_ids:
                picking_in = stock_picking_obj.browse(self.cr, self.uid, picking_in_ids[0])
            if picking_out_ids:
                picking_out = stock_picking_obj.browse(self.cr, self.uid, picking_out_ids[0])
            if picking_out.ddt_number:
                ddt_date = datetime.strptime(picking_out.ddt_date[:10], DEFAULT_SERVER_DATE_FORMAT)
                description.append('Documento di Uscita: {ddt} del {ddt_date}'.format(ddt=picking_out.ddt_number, ddt_date=ddt_date.strftime("%d/%m/%Y")))
            if picking_in:
                ddt_date = datetime.strptime(picking_in.date[:10], DEFAULT_SERVER_DATETIME_FORMAT)
                description.append('Documento di Reso: {ddt} del {ddt_date}'.format(ddt=picking_in.name.replace('-return', ''), ddt_date=ddt_date.strftime("%d/%m/%Y")))

        return '\n'.join(description)

    def _div(self, up, down):
        res = 0
        if down:
            res = up / down
        return res

    def _set_picking(self, invoice):
        self._get_invoice_tree(invoice.invoice_line, invoice.stock_picking_package_preparation_ids)
        return False

    def _get_ddt(self):
        def get_picking(picking_name):
            picking_ids = self.pool['stock.picking'].search(self.cr, self.uid, [('name', '=', picking_name)])
            if picking_ids:
                return self.pool['stock.picking'].browse(self.cr, self.uid, picking_ids[0])

        invoice = self.pool['account.invoice'].browse(self.cr, self.uid, self.ids[0])
        if hasattr(invoice, 'move_products') and invoice.move_products:
            return self.pool['account.invoice'].browse(self.cr, self.uid, self.ids[0])
        if hasattr(self, 'picking_name'):
            return self.cache.get(self.picking_name, False) or self.cache.setdefault(self.picking_name, get_picking(self.picking_name))
        return False

    def _get_italian_number(self, number, precision=2, no_zero=False):
        if not number and no_zero:
            return ''
        elif not number:
            return '0,00'

        if number < 0:
            sign = '-'
        else:
            sign = ''
        before, after = "{:.{digits}f}".format(number, digits=precision).split('.')
        belist = []
        end = len(before)
        for i in range(3, len(before) + 3, 3):
            start = len(before) - i
            if start < 0:
                start = 0
            belist.append(before[start: end])
            end = len(before) - i
        before = '.'.join(reversed(belist))
        
        if no_zero and int(number) == float(number) or precision == 0: 
            return sign + before
        else:
            return sign + before + ',' + after

    def get_description(self, ddt_name, ddt_date, order_name, order_date):
        description = []

        if ddt_name:
            ## Ex: Rif. Ns. DDT 2012/0335
            ddt_date = datetime.strptime(ddt_date[:10],
                                         DEFAULT_SERVER_DATE_FORMAT)
            description.append(u'Rif. Ns. {ddt} del {ddt_date}'.format(ddt=ddt_name, ddt_date=ddt_date.strftime("%d/%m/%Y")))

        elif order_name:# and not self.pool['res.users'].browse(
            #self.cr, self.uid, self.uid).company_id.disable_sale_ref_invoice_report:
            order_date = datetime.strptime(order_date[:10],
                                           DEFAULT_SERVER_DATE_FORMAT)
            description.append(u'Rif. Ns. Ordine {order} del {order_date}'.format(order=order_name.replace('Consuntivo', ''), order_date=order_date.strftime("%d/%m/%Y")))

        return '\n'.join(description)
    
    # def _get_picking_name(self, line):
    #     picking_obj = self.pool['stock.picking']
    #     picking_ids = picking_obj.search(self.cr, self.uid, [
    #         ('origin', '=', line.origin)])
    #
    #     if len(picking_ids) == 1:
    #         picking = picking_obj.browse(self.cr, self.uid, picking_ids[0])
    #         return picking.name
    #     elif picking_ids:
    #         move_obj = self.pool['stock.move']
    #         move_ids = move_obj.search(self.cr, self.uid, [
    #             ('product_id', '=', line.product_id.id),
    #             ('origin', '=', line.origin)])
    #         if len(move_ids) == 1:
    #             stock_move = move_obj.browse(self.cr, self.uid, move_ids[0])
    #             if stock_move.picking_id:
    #                 return stock_move.picking_id.name
    #             else:
    #                 return False
    #         elif move_ids:
    #             # The same product from the same sale_order is present in various picking lists
    #             raise orm.except_orm('Warning', _('Ambiguous line origin'))
    #         else:
    #             return False
    #     else:
    #         return False
    
    def _get_invoice_tree(self, invoice_lines, picking_preparation_ids):
        invoice = {}
        keys = {}
        ddt = False
        sale_order = False
        ddt_date = False
        sale_order_date = False

        for line in invoice_lines:
            if line.origin:
                if picking_preparation_ids:
                    for picking_preparation in picking_preparation_ids:
                        for picking in picking_preparation.picking_ids:
                            if picking.name == line.origin or \
                                    picking.origin == line.origin:
                                ddt = picking_preparation.ddt_number
                                ddt_date = picking_preparation.date
                                sale_order = picking.sale_id.name
                                sale_order_date = picking.sale_id.date_order
                else:
                    sale_order = line.origin
                    sale_order_date = line.invoice_id.date_invoice or \
                        datetime.now().strftime('%Y-%m-%d')
                    #TODO search date order
            # Order lines by date and by ddt, so first create date_ddt key:
            if ddt:
                if ddt in keys:
                    key = keys[ddt]
                else:
                    key = "{0}_{1}".format(ddt_date, ddt)
            elif sale_order:
                if sale_order in keys:
                    key = keys[sale_order]
                else:
                    key = "{0}_{1}".format(sale_order_date, sale_order)
            else:
                key = False

            if key in invoice:
                invoice[key]['lines'].append(line)
            else:
                description = self.get_description(ddt, ddt_date, sale_order, sale_order_date)
                invoice[key] = {'description': description, 'lines': [line]}
        
        return OrderedDict(sorted(invoice.items(), key=lambda t: t[0])).values()

    def _get_ddt_tree(self, sppp_line):
        keys = {}
        order = {}
        sale_order_name = False
        sale_order_date = False
        order_obj = self.pool['sale.order']
        for line in sppp_line:
            if line.move_id:
                sale_order_name = line.move_id.origin
                sale_order_id = order_obj.search(
                    self.cr, self.uid, [('name', '=', sale_order_name)])
                if sale_order_id:
                    sale_order_date = order_obj.browse(
                        self.cr, self.uid, sale_order_id[0]).date_order
            if sale_order_name:
                if sale_order_name in keys:
                    key = keys[sale_order_name]
                else:
                    key = "{0}_{1}".format(sale_order_date, sale_order_name)
            else:
                key = False
            order_date = datetime.strptime(sale_order_date[:10],
                                           DEFAULT_SERVER_DATE_FORMAT)
            description = \
                'Order ref. %s - %s' % (
                    sale_order_name,
                    order_date.strftime("%d/%m/%Y")
                    )
            order[key] = {'description': description, 'lines': [line]}

        return OrderedDict(
            sorted(order.items(), key=lambda t: t[0])).values()

    def _get_invoice_move_lines(self, move_id):
        if move_id.line_id:
            return [line for line in move_id.line_id if line.date_maturity]
        else:
            return []

    def _variant_images(self):
        res = False
        if self.pool['ir.config_parameter'].get_param(
                self.cr, self.uid, 'product.print_variant_images',
                default=False):
            res = True
        return res

    def _sale_weight(self):
        res = False
        if self.pool['ir.config_parameter'].get_param(
                self.cr, self.uid, 'sale.print_weight',
                default=False):
            res = True
        return res

    def _translate_text(self, source):
        trans_obj = self.pool['ir.translation']
        lang = 'en_US'
        if self.objects:  # needed?
            lang = self.objects[0].partner_id.lang
        return trans_obj._get_source(
            self.cr, self.uid, 'ir.actions.report.xml', 'report', lang, source)

    def _convert_to_gray_scale(self, base64_source, encoding='base64'):
        if not base64_source:
            return False
        image_stream = StringIO.StringIO(base64_source.decode(encoding))
        image = Image.open(image_stream).convert('LA')
        background_stream = StringIO.StringIO()
        image.save(background_stream, 'PNG')
        return background_stream.getvalue().encode(encoding)

    def _get_total_discount(self, lines):
        total_subprices = total_amount = 0.0
        for line in (l for l in lines if l.discount):
            if isinstance(line._model, type(
                    self.pool['account.invoice.line'])):
                total_amount += line.quantity * line.price_unit
            else:
                total_amount += line.product_uom_qty * line.price_unit
            total_subprices += line.price_subtotal
        for line in (l for l in lines if l.product_id.is_discount):
            total_subprices += line.price_subtotal
        return total_amount - total_subprices

    def _get_total_goods_amount(self, lines):
        total_goods_amount = 0.0
        for line in (l for l in lines if not l.is_delivery):
            if not line.product_id.is_transport and \
                    not line.product_id.is_contribution and \
                    not line.product_id.is_other and \
                    not line.product_id.is_discount:
                total_goods_amount += line.price_subtotal
        return total_goods_amount

    def _get_total_other_amount(self, lines):
        total_other_amount = 0.0
        for line in (l for l in lines if l.product_id.is_other):
            total_other_amount += line.price_subtotal
        return total_other_amount

    def _get_total_contribution_amount(self, lines):
        total_contribution_amount = 0.0
        for line in (l for l in lines if l.product_id.is_contribution):
            total_contribution_amount += line.price_subtotal
        return total_contribution_amount

    def _get_total_transport_amount(self, lines):
        total_transport_amount = 0.0
        for line in (l for l in lines if l.is_delivery):
            if not line.product_id.is_transport:
                total_transport_amount += line.price_subtotal
        for line in (l for l in lines if l.product_id.is_transport):
            total_transport_amount += line.price_subtotal
        return total_transport_amount

    def _check_installed_module(self, module):
        res = False
        if self.pool['ir.module.module'].search(self.cr, self.uid,
                                                [('name', '=', module),
                                                 ('state', '=', 'installed')]):
            res = True
        return res
