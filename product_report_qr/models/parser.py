# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.report import report_sxw
try:
    import qrcode
except ImportError:
    qrcode = None
import StringIO
try:
    import elaphe
except ImportError:
    elaphe = None


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'labels': self._get_labels,
            'qr': self._qr,
        })
        self.cache = {}

    def _qr(self, text):
        text = text.encode('utf-8')
        qr_code = qrcode.QRCode(version=None, box_size=4, border=1)
        qr_code.add_data(text)
        qr_code.make(fit=True)
        qr_img = qr_code.make_image()
        draw = qr_img._img.convert("RGB")

        encoding = 'base64'
        code_stream = StringIO.StringIO()
        draw.save(code_stream, 'PNG')
        value = code_stream.getvalue().encode(encoding)
        code_stream.close()
        return value

    def _get_labels(self, group_length=0):
        group_label = {}
        labels = []
        i = 0
        if self.name == 'product.product.labels.order':
            for order in self.pool['sale.order'].browse(
                    self.cr, self.uid, self.ids):
                for line in order.order_line.filtered(
                        lambda x: not (x.product_id.is_pack or
                                       x.product_id.is_other or
                                       x.product_id.is_transport or
                                       x.product_id.is_contribution or
                                       x.product_id.is_discount)):
                    for uom in range(0, int(line.product_uom_qty), 1):
                        group_label.update({
                            i: {
                                'code': line.product_id.default_code and
                                line.product_id.default_code or '',
                                'name': line.product_id.product_tmpl_id.name and
                                line.product_id.product_tmpl_id.name[:32] or '',
                                'leather': self._get_prod_leather(
                                    line.product_id) or '',
                                'color': self._get_prod_stitching(
                                    line.product_id) or '',
                            }
                        })
                        i += 1
                        if i == group_length:
                            labels += [group_label]
                            group_label = {}
                            i = 0
                if 0 < i < group_length:
                    for f in range(i, group_length, 1):
                        group_label.update({
                            f: {
                                'code': '',
                                'name': '',
                                'leather': '',
                                'color': '',
                            }
                        })
                    labels += [group_label]
        elif self.name == 'product.template.labels':
            for product in self.pool['product.template'].browse(
                    self.cr, self.uid, self.ids):
                group_label.update({
                    i: {
                        'default_code': product.prefix_code and
                                        product.prefix_code or
                                        product.name and
                                        product.name or False,
                    }
                })
                i += 1
                if i == group_length:
                    labels += [group_label]
                    group_label = {}
                    i = 0
            if 0 < i < group_length:
                for f in range(i, group_length, 1):
                    group_label.update({
                        f: {
                            'default_code': '',
                        }
                    })
                labels += [group_label]
        elif self.name == 'product.product.labels':
            for product in self.pool['product.product'].browse(
                    self.cr, self.uid, self.ids):
                group_label.update({
                    i: {
                        'default_code': product.default_code and
                                        product.default_code or
                                        product.name and
                                        product.name or False,
                    }
                })
                i += 1
                if i == group_length:
                    labels += [group_label]
                    group_label = {}
                    i = 0
            if 0 < i < group_length:
                for f in range(i, group_length, 1):
                    group_label.update({
                        f: {
                            'default_code': '',
                        }
                    })
                labels += [group_label]
        elif self.name == 'product.attribute.labels':
            for attribute in self.pool['product.attribute'].browse(
                    self.cr, self.uid, self.ids):
                for value in attribute.value_ids.sorted(key=lambda r: r.code):
                    group_label.update({
                        i: {
                            'default_code': attribute.code + value.code if
                            attribute.code and value.code else False,
                        }
                    })
                    i += 1
                    if i == group_length:
                        labels += [group_label]
                        group_label = {}
                        i = 0
            if 0 < i < group_length:
                for f in range(i, group_length, 1):
                    group_label.update({
                        f: {
                            'default_code': '',
                        }
                    })
                labels += [group_label]
        return labels

    def _get_prod_stitching(self, product_id):
        stiching_attribute_id = self.pool['product.attribute'].search(
            self.cr, self.uid, [('code', '=', 'ST')])
        for value in product_id.attribute_value_ids:
            if value.attribute_id.id == stiching_attribute_id[0]:
                return value.attribute_id.name + ' ' + value.name

    def _get_prod_leather(self, product_id):
        stiching_attribute_id = self.pool['product.attribute'].search(
            self.cr, self.uid, [('code', '=', 'ST')])
        for value in product_id.attribute_value_ids:
            if value.attribute_id.id != stiching_attribute_id[0]:
                return value.attribute_id.name + ' ' + value.name
