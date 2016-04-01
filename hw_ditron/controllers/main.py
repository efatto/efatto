# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from os.path import isfile
from openerp import http
import xml.etree.ElementTree as ET
import openerp.addons.hw_proxy.controllers.main as hw_proxy

_logger = logging.getLogger(__name__)

import tempfile
import os
from datetime import datetime
from threading import Thread

class Ecr(Thread):
    reference = ''

    def __init__(self, receipt):
        Thread.__init__(self)
        self.receipt_data = receipt
        self.receipt_xml = ''
        self.receipt = self.compose()
        self.status = {}

    def __unicode__(self):
        return u'\r\n'.join(self.receipt) + u'\r\n\r\n'

    def __str__(self):
        return u'\r\n'.join(self.receipt) + u'\r\n\r\n'

    def compose(self):
        pass

    def print_receipt(self):
        pass

    def set_status(self, status, message=None):
        _logger.info(status + ' : ' + (message or 'no message'))
        # if status == self.status['status']:
        #     if message != None and (len(self.status['messages']) == 0 or message !=
        #         self.status['messages'][-1]):
        #         self.status['messages'].append(message)
        # else:
        #self.status['status'] = status
        if message:
            self.status['messages'] = [message]
        else:
            self.status['messages'] = []

        if status == 'error' and message:
            _logger.error('DITRON Error: ' + message)
        elif status == 'disconnected' and message:
            _logger.warning('DITRON Device Disconnected: ' + message)

    def get_status(self):
        self.set_status('connected', 'Connected to Ditron')
        return True

    def dry_print(self):
        destination = os.path.join(tempfile.gettempdir(), 'fp_tmp')
        if not os.path.exists(destination):
            os.makedirs(destination)
        ticket = datetime.now().strftime("%Y%m%d.%H%M") + '.txt'

        file(os.path.join(destination, ticket), 'w').write(
            unicode(self).encode('utf8'))

        return True


class Ditron(Ecr):
    def compose(self):
        '''
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


        CHIUS T=1,IMP=0.40              			;chiusura mista : 0.40 Euro in contanti
        CHIUS T=2                       			;                 e il resto a credito #ahah
            '''
        ticket = []
        ticket.append(
            u"slave on, msg='TASTIERA DISABILITATA'")  # ;disabilita la tastiera
        #  receipt.date.strftime('%d/%m/%Y %H:%M:%S') + ' ' + receipt.reference
        ticket.append(u'')
        ticket.append(
            u'CLEAR')  # ;preme il tasto C  #receipt.user.company_id.name
        ticket.append(
            u'CHIAVE REG')  # ;conferma che la cassa si trovi in assetto REGistrazione #str(receipt.user.company_id.phone)

        if self.receipt_xml:
            root = ET.fromstring(self.receipt_xml)
            for child in root.findall('receipt_lines'):
                for line in child:
                    if line.tag == 'line_vend':
                        # if price != 0.0:
                        ticket.append(u"VEND REP={reparto},QTY={qty:.0f},PRE={price:.2f},DES='{name:.24}'".format(
                                    reparto=line.find('rep').text, name=line.find('des').text, qty=line.find('qty').text, price=line.find('pre').text))
                    if line.find('sconto'):
                        ticket.append(
                        u'SCONTO VAL={discount:.2f}'.format(discount=line.find('sconto').text * line.find('qty').text * line.find('pre').text))

        # ticket.append(u'User: ' + receipt.user.name)
        # ticket.append(u'POS: ' + receipt.cash_register_name)
        #ticket.append(receipt_xml)

        # for line in self.product_lines:
        #     self.subtotal += line.price_subtotal
        #     if line.discount:
        #         self.discount += line.product_id.list_price * line.qty - line.price_subtotal
        #     qty = line.qty != 0 or 1
        #     reparto = 1
        #     if line.product_id and line.product_id.taxes_id and line.product_id.taxes_id[0]:
        #         if line.product_id.taxes_id[0].department.department:
        #             reparto = line.product_id.taxes_id[0].department.department
        #     price = line.price_subtotal_incl
        #
        #     if price != 0.0:
        #         ticket.append(u"VEND REP={reparto},QTY={qty:.0f},PRE={price:.2f},DES='{name:.24}'".format(
        #             reparto=reparto, name=line.product_id.name, qty=qty, price=price))
        #         if line.discount:
        #             ticket.append(
        #                 u'SCONTO VAL={discount:.2f}'.format(discount=line.product_id.list_price * line.qty - line.price_subtotal))

        ticket.append(u'')
        ticket.append(u'SUBT')   # ;subtotale
        ticket.append(u'CHIUS T=1') # ;Chiusura in contanti
        ticket.append(u'slave off')  # ;riabilita la tastiera  #{text:<30}{subtotal:>9.2f} €'.format(text='Subtotal: ', subtotal=self.subtotal))
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
        destination = "/home/sergio/share"  # os.path.join(tempfile.gettempdir(), 'opentmp')
        if not os.path.exists(destination):
            os.makedirs(destination)
        ticket = 'scontrino.txt'

        file(os.path.join(destination, ticket), 'w').write(
            unicode(self.receipt).encode('utf8'))

        return True


    def push_task(self, receipt_xml):
        self.receipt_xml = receipt_xml
        # self.lockedstart()
        self.receipt = self.compose()
        self.print_receipt()


driver = Ditron(Ecr)
#driver.push_task('printstatus')
hw_proxy.drivers['ditron'] = driver


class DitronDriver(hw_proxy.Proxy):
    @http.route('/hw_proxy/print_xml_receipt', type='json', auth='none', cors='*')
    def print_xml_receipt(self, receipt):
        _logger.info('DITRON: PRINT XML RECEIPT')
        driver.push_task(receipt)
