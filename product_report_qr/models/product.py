# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

import time
from openerp.report import report_sxw
try:
    import qrcode
except ImportError:
    qrcode = None
import StringIO


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'labels': self._get_labels,
        })
        self.cache = {}

    def _qr(self, text):
        encoding = 'base64'
        im = qrcode.make(text)
        draw = im.convert('RGB')
        background_stream = StringIO.StringIO()
        draw.save(background_stream, 'PNG')
        return background_stream.getvalue().encode(encoding)

    def _get_labels(self):
        group_label = []
        labels = []
        i = 0
        for product in self.pool['product.product'].browse(
                self.cr, self.uid, self.ids):
            group_label.append({
                'qrcode': product.default_code and self._qr(
                    product.default_code) or product.name and self._qr(
                    product.name) or False,
                'default_code': product.default_code,
            })
            i += 1
            if i == 11:
                labels.append(group_label)
                group_label = []
                i = 0
        if 0 < i < 11:
            labels.append(group_label)
            for f in range(11-i, 11, 1):
                labels.append({
                    'qrcode': False,
                    'default_code': False,
                })
        return labels
