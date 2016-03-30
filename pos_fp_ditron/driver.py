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
        '''
        slave on, msg='TASTIERA DISABILITATA'			;disabilita la tastiera
        CLEAR        						            ;preme il tasto C
        CHIAVE REG              						;conferma che la cassa si trovi in assetto REGistrazione

        VEND REP=1,PREZZO=0.55          			;vendita semplice a reparto 1
        SCONTO VAL=0.05                  			;sconto assoluto diretto su reparto

        VEND REP=2,PREZZO=0.25          			;vendita semplice a reparto 2
        VEND REP=3,PREZZO=0.25          			;vendita semplice a reparto 3
        VEND REP=4,PREZZO=0.25          			;vendita semplice a reparto 4

        VEND REP=2,PREZZO=0.25,STORNO   			;storno della vendita semplice a reparto 2

        VEND REP=2,QTY=6,PREZZO=0.25    	        ;vendita su reparto con quantita' non unitaria
        VEND REP=3,PRE=0.30,DES='CANCELLERIA' 	    ;vendita su reparto con descrizione

        PERCA ALI=50, SUBTOT 			            ;Sconto del 50% sul subtotale

        CORT R1='PROVA MESSAGGIO 1',R2='PROVA MESSAGGIO 2' 	;messaggio di cortesia

        SUBT                            			;subtotale

        CHIUS T=1,IMP=0.40              			;chiusura mista : 0.40 Euro in contanti
        CHIUS T=2                       			;                 e il resto a credito #ahah
        #oppure
        CHIUS T=1                                   ;Chiusura in contanti
        slave off						            ;riabilita la tastiera
            '''
        receipt = self.receipt_data
        ticket = []
        ticket.append(u"slave on, msg='TASTIERA DISABILITATA'") #  receipt.date.strftime('%d/%m/%Y %H:%M:%S') + ' ' + receipt.reference
        ticket.append(u'')
        ticket.append(u'CLEAR') #receipt.user.company_id.name
        ticket.append(u'CHIAVE REG') #str(receipt.user.company_id.phone)

        # ticket.append(u'User: ' + receipt.user.name)
        # ticket.append(u'POS: ' + receipt.cash_register_name)
        ticket.append(u'')
        
        #lines = self.get_product_line()
        for line in self.product_lines:
            self.subtotal += line.price_subtotal
            if line.discount:
                self.discount += line.product_id.list_price * line.qty - line.price_subtotal
            qty = line.qty != 0 or 1
            reparto = 1
            if line.product_id and line.product_id.taxes_id and line.product_id.taxes_id[0]:
                if line.product_id.taxes_id[0].department.department:
                    reparto = line.product_id.taxes_id[0].department.department
            price = line.price_subtotal_incl

            if price != 0.0:
                ticket.append(u"VEND REP={reparto},QTY={qty:.0f},PRE={price:.2f},DES='{name:.24}'".format(
                    reparto=reparto, name=line.product_id.name, qty=qty, price=price))
                if line.discount:
                    ticket.append(
                        u'SCONTO VAL={discount:.2f}'.format(discount=line.product_id.list_price * line.qty - line.price_subtotal))
                
            #line = self.get_product_line()

        ticket.append(u'')

        ticket.append(u'SUBT')
        ticket.append(u'CHIUS T=1') # PER CASSA
        ticket.append(u'slave off')  # {text:<30}{subtotal:>9.2f} €'.format(text='Subtotal: ', subtotal=self.subtotal))
        # ticket.append(
        #     u'Tax:                          {tax:9.2f} €'.format(tax=receipt.amount_tax))
        # ticket.append(
        #     u'Discount:                     {discount:9.2f} €'.format(discount=self.discount))
        # ticket.append(
        #     u'Total:                        {total:9.2f} €'.format(total=receipt.amount_total))

        ticket.append(u'')

        # for payment in receipt.payments:
        #     ticket.append(u'{name:<30}{amount:9.2f} €'.format(
        #         name=payment.name_get()[0][1], amount=payment.amount))
        #
        # ticket.append(u'')
        #
        # ticket.append(
        #     u'Change:                       {a_return:9.2f} €'.format(a_return=receipt.amount_return))
        
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
