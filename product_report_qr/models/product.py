# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.report import report_sxw
try:
    import qrcode
except ImportError:
    qrcode = None
# import StringIO
# try:
#     import elaphe
# except ImportError:
#     barcode = None

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'labels': self._get_labels,
        })
        self.cache = {}

    # def _qr(self, text):
    #     text = text.encode('utf-8')
    #     if self.name == 'product.product.labels.data.matrix':
    #         img = elaphe.barcode(
    #             'datamatrix', text,)
    #             # options = dict(version=None, eclevel='M'),
    #             # margin = 1, data_mode = '8bits')
    #         draw = img.convert("RGB")
    #     else:
    #         qr_code = qrcode.QRCode(version=None, box_size=1, border=1)
    #         qr_code.add_data(text)
    #         qr_code.make(fit=True)
    #         qr_img = qr_code.make_image()
    #         draw = qr_img._img.convert("RGB")
    #
    #     encoding = 'base64'
    #     code_stream = StringIO.StringIO()
    #     draw.save(code_stream, 'PNG')
    #     value = code_stream.getvalue().encode(encoding)
    #     code_stream.close()
    #     return value

    def _get_labels(self):
        group_label = {}
        labels = []
        i = 0
        for product in self.pool['product.product'].browse(
                self.cr, self.uid, self.ids):
            group_label.update({
                i: {
                    # 'qrcode': product.default_code and self._qr(
                    #     product.default_code) or product.name and self._qr(
                    #         product.name) or False,
                    'default_code': product.default_code and
                    product.default_code or product.name and
                    product.name or False,
                }
            })
            i += 1
            if i == 12:
                labels += [group_label]
                group_label = {}
                i = 0
        if 0 < i < 12:
            for f in range(i, 12, 1):
                group_label.update({
                    f: {
                        # 'qrcode': False,
                        'default_code': False,
                    }
                })
            labels += [group_label]
        return labels
