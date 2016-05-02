# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import time
import re
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'raggruppa': self._raggruppa,
            'raggruppaddt': self._raggruppaddt,
            'righe': self._righe,
            'righeddt': self._righeddt,
            'div': self._div,
            'italian_number': self._get_italian_number,
            'get_description': self._get_description,
            'desc_nocode': self._desc_nocode,
        })

    def _desc_nocode(self, string):
        return re.compile('\[.*\]\ ').sub('', string)
        
    def _get_description(self, order_name):
        order_obj = self.pool['sale.order']
        description = []

        if order_name and not self.pool['res.users'].browse(
                self.cr, self.uid, self.uid).company_id.disable_sale_ref_invoice_report:
            order_ids = order_obj.search(self.cr, self.uid, [('name', '=', order_name)])
            if len(order_ids) == 1:
                order = order_obj.browse(self.cr, self.uid, order_ids[0])
                order_date = datetime.strptime(order.date_order, DEFAULT_SERVER_DATE_FORMAT)
                if order.client_order_ref:
                    description.append(u'Rif. Ns. Ordine {order} del {order_date}, Vs. Ordine {client_order}'.format(order=order.name, order_date=order_date.strftime("%d/%m/%Y"), client_order=order.client_order_ref))
                else:
                    description.append(u'Rif. Ns. Ordine {order} del {order_date}'.format(order=order.name, order_date=order_date.strftime("%d/%m/%Y")))

        return ' / '.join(description)

    def _div(self, up, down):
        res = 0
        if down:
            res = up / down
        return res

    def _get_italian_number(self, number, precision=2, no_zero=False):
        if not number and no_zero:
            return ''
        elif not number:
            return '0,00'

        if number < 0:
            sign = '-'
        else:
            sign = ''
        ## Requires Python >= 2.7:
        #before, after = "{:.{digits}f}".format(number, digits=precision).split('.')
        ## Works with Python 2.6:
        if precision:
            before, after = "{0:10.{digits}f}".format(number, digits=precision).strip('- ').split('.')
        else:
            before = "{0:10.{digits}f}".format(number, digits=precision).strip('- ').split('.')[0]
            after = ''
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

    def _raggruppa(self, righe_fattura):
        indice_movimenti = {}
        movimenti_filtrati = []
        for riga in righe_fattura:
            if riga.origin in indice_movimenti and riga.origin in indice_movimenti[riga.origin]:
                print riga
                print riga.origin
            else:
                if riga.origin:
                    print 'Riga Buona'
                    if riga.ddt_origin in indice_movimenti:
                        indice_movimenti[riga.ddt_origin][riga.sale_origin] = riga.sale_origin
                    else:
                        indice_movimenti[riga.ddt_origin] = {riga.sale_origin: riga.sale_origin}
                    movimenti_filtrati.append(riga)
                else:
                    continue
        print indice_movimenti
        print movimenti_filtrati
        return movimenti_filtrati

    def _righe(self, righe_fattura, filtro):
        righe_filtrate = []
        print filtro
        print righe_fattura
        for riga in righe_fattura:
            if ((riga.origin == filtro.origin)):
                righe_filtrate.append(riga)
        return righe_filtrate

    def _raggruppaddt(self, righe_ddt):
        indice_movimenti = {}
        movimenti_filtrati = []
        print righe_ddt
        for riga in righe_ddt:
            if riga.origin in indice_movimenti:
                print riga.origin
            else:
                indice_movimenti[riga.origin] = riga.origin
                movimenti_filtrati.append(riga)
        print indice_movimenti
        return movimenti_filtrati

    def _righeddt(self, righe_ddt, filtro):
        righe_filtrate = []
        print filtro
        print righe_ddt
        for riga in righe_ddt:
            if riga.origin == filtro.origin:
                righe_filtrate.append(riga)
        return righe_filtrate

