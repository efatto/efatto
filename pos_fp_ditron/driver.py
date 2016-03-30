# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2013-2014 Andrei Levin (andrei.levin at didotech.com)
#                          All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import tempfile

from openerp.addons.pos_fiscal_printer.ecr import Ecr


def italian_number(number, precision=1, no_zero=False):
    if not number:
        return '0,00'

    if number < 0:
        sign = '-'
    else:
        sign = ''
    # Requires Python >= 2.7:
    # before, after = "{:.{digits}f}".format(number, digits=precision).split('.')
    # Works with Python 2.6:
    before, after = "{0:10.{digits}f}".format(
        number, digits=precision).strip('- ').split('.')

    belist = []
    end = len(before)
    for i in range(3, len(before) + 3, 3):
        start = len(before) - i
        if start < 0:
            start = 0
        belist.append(before[start: end])
        end = len(before) - i
    before = '.'.join(reversed(belist))

    if no_zero and int(number) == float(number):
        return sign + before
    else:
        return sign + before + ',' + after


class Ditron(Ecr):
    def compose(self):
        '''
        line attributes:
            product_id 	- Product
            order_id - Order Ref
            price_unit - Unit Price
            price_subtotal - Subtotal w/o Tax
            company_id - Company
            price_subtotal_incl - Subtotal
            qty - Quantity
            discount - Discount (%)
            name - Line No
        receipt attributes:
            payments
        '''
        receipt = self.receipt_data
        ticket = []
        ticket.append(receipt.date.strftime(
            '%d/%m/%Y %H:%M:%S') + ' ' + receipt.reference)
        ticket.append(u'')
        ticket.append(receipt.user.company_id.name)
        ticket.append(u'Phone: ' + str(receipt.user.company_id.phone))
        ticket.append(u'User: ' + receipt.user.name)
        ticket.append(u'POS: ' + receipt.cash_register_name)
        ticket.append(u'')
        
        line = self.get_product_line()
        while line:
            qty = italian_number(line.qty, 1, True)
            
            if line.product_id and line.product_id.taxes_id and line.product_id.taxes_id[0]:
                reparto = line.product_id.taxes_id[0].department.department
            else:
                reparto = 1
            
            ticket.append(u"rep={reparto} {name:<24}{qty: ^3}{price:>6.2f} €".format(
                reparto=reparto, name=line.product_id.name, qty=qty, price=line.price_subtotal_incl))
            
            if line.discount:
                ticket.append(
                    u'With a {discount}% discount'.format(discount=line.discount))
                
            line = self.get_product_line()

        ticket.append(u'')

        ticket.append(u'{text:<30}{subtotal:>9.2f} €'.format(
            text='Subtotal: ', subtotal=self.subtotal))
        ticket.append(
            u'Tax:                          {tax:9.2f} €'.format(tax=receipt.amount_tax))
        ticket.append(
            u'Discount:                     {discount:9.2f} €'.format(discount=self.discount))
        ticket.append(
            u'Total:                        {total:9.2f} €'.format(total=receipt.amount_total))

        ticket.append(u'')

        for payment in receipt.payments:
            ticket.append(u'{name:<30}{amount:9.2f} €'.format(
                name=payment.name_get()[0][1], amount=payment.amount))

        ticket.append(u'')

        ticket.append(
            u'Change:                       {a_return:9.2f} €'.format(a_return=receipt.amount_return))
        
        return ticket

    def print_receipt(self):
        if self.config.destination:
            destination = self.config.destination
        else:
            destination = os.path.join(tempfile.gettempdir(), 'opentmp')
            if not os.path.exists(destination):
                os.makedirs(destination)
        ticket = 'scontrino.txt'

        file(os.path.join(destination, ticket), 'w').write(
            unicode(self).encode('utf8'))
        
        return True
