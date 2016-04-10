# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os
from os.path import isfile, join
from os import listdir
from openerp import http
import xml.etree.ElementTree as ET
from time import sleep
from datetime import datetime
from threading import Thread
import openerp.addons.hw_proxy.controllers.main as hw_proxy

_logger = logging.getLogger(__name__)


class Ditron(Thread):
    reference = ''

    def __init__(self):
        Thread.__init__(self)
        self.receipt_xml = ''
        self.receipt = self.compose()
        self.set_status('connecting')
        self.device_path = self._find_device_path_by_probing()

    def __unicode__(self):
        return u'\r\n'.join(self.receipt) + u'\r\n\r\n'

    def __str__(self):
        return u'\r\n'.join(self.receipt) + u'\r\n\r\n'

    def set_status(self, status, messages=[]):
        self.status = {
            'status': status,
            'messages': messages
        }

    def get_status(self):
        return self.status

    def _find_device_path_by_probing(self):
        destination = "/home/pi/share"
        if not os.path.exists(destination):
            os.makedirs(destination)
        ticket = 'scontrino.txt'

        file_destination = os.path.join(destination, ticket)
        if isfile(file_destination):  # scontrino.txt not already printed, ECRCOM driver dead???
            _logger.debug("Probing " + file_destination)
            self.set_status('error', ["Couldn't Connected to Ditron"])
        # while isfile(file_destination):
        #     sleep(5)  # quanto?
        # else:
        else:
            self.set_status('connected', 'Connected to Ditron')
        return True

    def compose(self):
        '''
        VEND REP=1,PREZZO=0.55          			;vendita semplice a reparto 1
        SCONTO VAL=0.05                  			;sconto assoluto diretto su reparto

        VEND REP=2,PREZZO=0.25          			;vendita semplice a reparto 2
        VEND REP=3,PREZZO=0.25          			;vendita semplice a reparto 3
        VEND REP=4,PREZZO=0.25          			;vendita semplice a reparto 4

        VEND REP=2,PREZZO=0.25,STORNO   			;storno della vendita semplice a reparto 2
        vend rep=1, pre=1.00, des='Articolo 3', reso
        VEND REP=2,QTY=6,PREZZO=0.25    	        ;vendita su reparto con quantita' non unitaria
        VEND REP=3,PRE=0.30,DES='CANCELLERIA' 	    ;vendita su reparto con descrizione

        PERCA ALI=50, SUBTOT 			            ;Sconto del 50% sul subtotale

        CORT R1='PROVA MESSAGGIO 1',R2='PROVA MESSAGGIO 2' 	;messaggio di cortesia


        CHIUS T=1,IMP=0.40              			;chiusura mista : 0.40 Euro in contanti
        CHIUS T=2                       			;                 e il resto a credito #ahah

        scontrini parlanti:
        ;ESEMPIO CON CODICE FISCALE:

        INP TERM=61
        INP ALFA='MRTRSR76S11F158E',TERM=49
        VEND REP=1, PRE=1.00
        VEND REP=2,PRE=1.50,QTY=5,DES='ARTICOLO PROVA'
        CHIUS

        ;ESEMPIO CON P.IVA

        INP TERM=61
        INP ALFA='07291140635',TERM=49
        VEND REP=1, PRE=1.00
        VEND REP=2,PRE=1.50,QTY=5,DES='ARTICOLO PROVA'
        CHIUS
        '''
        ticket = []
        if self.receipt_xml:
            ticket.append(
                u"slave on, msg='TASTIERA DISABILITATA'")
            #  receipt.date.strftime('%d/%m/%Y %H:%M:%S') + ' ' + receipt.reference
            ticket.append(u'')
            ticket.append(u'CLEAR')  # ;preme il tasto C
            ticket.append(u'CHIAVE REG')
            # ;conferma che la cassa si trovi in assetto REGistrazione
            root = ET.fromstring(self.receipt_xml)
            for child in root.iter('receipt_lines'):
                for line in child.findall('line_vend'):
                    reso = ''
                    if float(line.find('pre').text) < 0.0:
                        reso = ', reso'
                    if float(line.find('pre').text) != 0.0:
                        ticket.append(
                            u"VEND REP={reparto},QTY={qty:.0f},PRE={price:.2f},DES='{name:.24}{reso}'".format(
                                reparto=line.find('rep').text, name=line.find('des').text,
                                qty=float(line.find('qty').text),
                                price=float(line.find('pre').text),
                                reso=reso,)
                        )
                        if float(line.find('sconto').text) != 0.0:
                            ticket.append(
                                u'SCONTO VAL={discount:.2f}'.format(
                                    discount=float(line.find('sconto').text) / 100 * float(
                                        line.find('qty').text) * float(line.find('pre').text)))
            # ticket.append(u'User: ' + receipt.user.name)
            # #receipt.user.company_id.name
            # ticket.append(u'POS: ' + receipt.cash_register_name)

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
            # for payment in receipt.payments:
            #     ticket.append(u'{name:<30}{amount:9.2f} €'.format(
            #         name=payment.name_get()[0][1], amount=payment.amount))
            #
            ticket.append(u'')
            ticket.append(u'SUBT')   # ;subtotale
            ticket.append(u'CHIUS T=1') # ;Chiusura in contanti
            ticket.append(u'slave off')  # ;riabilita la tastiera  #{text:<30}{subtotal:>9.2f} €'.format(text='Subtotal: ', subtotal=self.subtotal))
            ticket.append(u'')
            _logger.debug("Appended Ticket")
        return ticket

    def print_receipt(self):
        destination = "/home/pi/share"  # os.path.join(tempfile.gettempdir(), 'opentmp')
        if not os.path.exists(destination):
            os.makedirs(destination)
        ticket = 'scontrino.txt'

        file_destination = os.path.join(destination, ticket)
        if isfile(file_destination):  # scontrino.txt not already printed, ECRCOM driver dead???
            ticket = 'scontrino' + str(datetime.now()).replace(':','').replace('.','').replace(' ','') + '.txt'
            file_destination = os.path.join(destination, ticket)
        file(file_destination, 'w').write(
            unicode(self).encode('utf8'))

        return True

    def print_queue(self):
        destination = "/home/pi/share"
        ticket = 'scontrino.txt'
        while [f for f in listdir(destination) if isfile(join(destination, f))]:
            for ticket_queue in [f for f in listdir(destination) if isfile(join(destination, f))]:
                if not isfile(os.path.join(destination, ticket)):
                    if ticket_queue != ticket:
                        os.rename(os.path.join(destination, ticket_queue), os.path.join(destination, ticket))
                        sleep(2)

    def push_task(self, receipt_xml):
        self.receipt_xml = receipt_xml
        self.receipt = self.compose()
        self.print_receipt()
        self.print_queue()

driver = Ditron()
#driver.push_task('printstatus')
hw_proxy.drivers['ditron'] = driver


class DitronDriver(hw_proxy.Proxy):
    @http.route('/hw_proxy/print_xml_receipt', type='json', auth='none', cors='*')
    def print_xml_receipt(self, receipt):
        _logger.info('DITRON: PRINT XML RECEIPT')
        driver.push_task(receipt)
