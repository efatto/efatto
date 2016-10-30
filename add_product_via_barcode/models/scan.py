# -*- coding: utf-8 -*-

from openerp import models, fields, api
import threading
import math
Tlock = threading.RLock()


def ean_checksum(eancode):
    """returns the checksum of an ean string of length 13,
     returns -1 if the string has the wrong length"""
    if len(eancode) != 13:
        return -1
    oddsum=0
    evensum=0
    total=0
    eanvalue=eancode
    reversevalue = eanvalue[::-1]
    finalean=reversevalue[1:]

    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total=(oddsum * 3) + evensum

    check = int(10 - math.ceil(total % 10.0)) %10
    return check


def check_ean(eancode):
    """returns True if eancode is a valid ean13 string, or null"""
    if not eancode:
        return True
    if len(eancode) != 13:
        return False
    try:
        int(eancode)
    except:
        return False
    return ean_checksum(eancode) == int(eancode[-1])


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    scan = fields.Char('Scan')

    @api.onchange('scan')
    def _sale_scan_calculation(self):
        if self.scan:
            Tlock.acquire()
            res = check_ean(self.scan)
            product_obj = None

            if res:
                product_obj = self.env['product.product'].search(
                    [('ean13', '=', self.scan), ('sale_ok', '=', True)])
                if not product_obj:
                    product_obj = self.env['product.product'].search(
                        [('default_code', '=', self.scan),
                         ('sale_ok', '=', True)])
            else:
                product_obj = self.env['product.product'].search(
                    [('default_code', '=', self.scan), ('sale_ok', '=', True)])

            line_list = []
            flag = 0
            if product_obj:
                for record in self.order_line:
                    if record.product_id.id == product_obj.id:
                        qty = record.product_uom_qty + 1
                        flag = 1
                    else:
                        qty = record.product_uom_qty
                    values = {
                        'order_id': record.order_id,
                        'product_id': record.product_id.id,
                        'name': record.name,
                        'product_uom_qty': qty,
                        'price_unit': record.price_unit,
                        'product_uom': record.product_uom.id,
                        'state': record.state,
                        'delay': record.delay,
                        'tax_id': record.tax_id,
                        'price_subtotal': record.price_subtotal
                    }
                    line_list.append((0,0,values))

                if not flag:
                    vals = {
                        'order_id': self.id,
                        'product_id': product_obj.id,
                        'name': product_obj.name_template,
                        'product_uom_qty': 1,
                        'price_unit': product_obj.product_tmpl_id.list_price,
                        'product_uom': product_obj.product_tmpl_id.uom_id.id,
                        'state': 'draft',
                        'delay': 0.0
                    }
                    line_list.append((0, 0, vals))
                self.order_line = line_list
                self.scan = ''
            else:
                self.scan = ''
                #raise Warning(_('Unknown Barcode OR Product can not be sale!!'))
            Tlock.release()

    # @api.onchange('scan')
    # def add_product_via_scan(self):
    #     threaded_calculation = threading.Thread(
    #         target=self._sale_scan_calculation,
    #         args=self,
    #     )
    #     threaded_calculation.start()


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    scan = fields.Char('Scan')

    @api.onchange('scan')
    def _purchase_scan_calculation(self):
        if self.scan:
            Tlock.acquire()
            res = check_ean(self.scan)
            product_obj = None

            if res:
                product_obj = self.env['product.product'].search(
                    [('ean13', '=', self.scan), ('purchase_ok', '=', True)])
                if not product_obj:
                    product_obj = self.env['product.product'].search(
                        [('default_code', '=', self.scan),
                         ('purchase_ok', '=', True)])
            else:
                product_obj = self.env['product.product'].search(
                    [('default_code', '=', self.scan),
                     ('purchase_ok', '=', True)])

            line_list = []
            flag = 0
            if product_obj:
                for record in self.order_line:
                    if record.product_id.id == product_obj.id:
                        qty = record.product_qty + 1
                        flag = 1
                    else:
                        qty = record.product_qty
                    values = {
                        'order_id': record.order_id,
                        'product_id': record.product_id.id,
                        'name': record.name,
                        'product_qty': qty,
                        'price_unit': record.price_unit,
                        'product_uom': record.product_uom.id,
                        'state': record.state,
                        'taxes_id': record.taxes_id,
                        'price_subtotal': record.price_subtotal,
                        'date_planned': record.date_planned
                    }
                    line_list.append((0, 0, values))

                if not flag:
                    vals = {
                        'order_id': self.id,
                        'product_id': product_obj.id,
                        'name': product_obj.name_template,
                        'product_qty': 1,
                        'price_unit': product_obj.product_tmpl_id.list_price,
                        'product_uom': product_obj.product_tmpl_id.uom_id.id,
                        'state': 'draft',
                        'date_planned': fields.Date.today()
                    }

                    line_list.append((0, 0, vals))
                self.order_line = line_list
                self.scan = ''
            else:
                self.scan= ''
                #raise Warning(_('Unknown Barcode
                # OR Product can not be purchase!!'))
            Tlock.release()

    # @api.onchange('scan')
    # def add_product_via_scan(self):
    #     threaded_calculation = threading.Thread(
    #         target=self._purchase_scan_calculation,
    #         args=self,
    #     )
    #     threaded_calculation.start()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    _sql_constraints = [
        ('barcode_uniq', 'unique(ean13)',
         'EAN13 Barcode must be unique!!'),
        ('default_code_uniq', 'unique(default_code)',
         'Internal Reference must be unique!!')
    ]
