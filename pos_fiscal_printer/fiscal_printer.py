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

from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools.translate import _

import time
import datetime
from openerp import pooler

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


class pos_order(osv.osv):
    _inherit = 'pos.order'

    def create_from_ui(self, cr, uid, orders, context=None):
        #_logger.info('orders: %r', orders)
        order_ids = []
        # print orders

        for tmp_order in orders:
            order = tmp_order['data']
            order_id = self.create(cr, uid, {
                'name': order['name'],
                'user_id': order['user_id'] or False,
                'session_id': order['pos_session_id'],
                'lines': order['lines'],
                'pos_reference': order['name']
            }, context)

            for payments in order['statement_ids']:
                payment = payments[2]
                self.add_payment(cr, uid, order_id, {
                    'amount': payment['amount'] or 0.0,
                    'payment_date': payment['name'],
                    'statement_id': payment['statement_id'],
                    'payment_name': payment.get('note', False),
                    'journal': payment['journal_id']
                }, context=context)
                
            if order['amount_return']:
                session = self.pool['pos.session'].browse(
                    cr, uid, order['pos_session_id'], context=context)
                cash_journal = session.cash_journal_id
                
                if not cash_journal:
                    cash_journal_ids = filter(
                        lambda st: st.journal_id.type == 'cash', session.statement_ids)
                    if not len(cash_journal_ids):
                        raise osv.except_osv(_('error!'),
                                             _('No cash statement found for this session. Unable to record returned cash.'))
                    cash_journal = cash_journal_ids[0].journal_id
                self.add_payment(cr, uid, order_id, {
                    'amount': -order['amount_return'],
                    'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'payment_name': _('return'),
                    'journal': cash_journal.id,
                }, context=context)
            order_ids.append(order_id)
            wf_service = netsvc.LocalService('workflow')
            wf_service.trg_validate(uid, 'pos.order', order_id, 'paid', cr)

            self.print_receipt(cr, uid, order_id, order['pos_session_id'], context)

        return order_ids

    def print_receipt(self, cr, uid, order_id, pos_session_id, context):
        receipt = Receipt(cr, uid, order_id, context)
        printer = fiscal_printer(cr, uid, pos_session_id)
        printer.print_receipt(receipt)


class Receipt():
    def __init__(self, cr, uid, order_id, context=None):
        self.pool = pooler.get_pool(cr.dbname)

        self.order = self.pool['pos.order'].browse(cr, uid, order_id, context)

        utc_date_order = datetime.datetime.strptime(
            self.order.date_order, '%Y-%m-%d %H:%M:%S')
        self.date = fields.datetime.context_timestamp(
            cr, uid, utc_date_order, context=context)
        self.name = self.order.name
        self.reference = self.order.pos_reference
        self.user = self.pool['res.users'].browse(cr, uid, uid)

        self.lines = self.order.lines
        self.amount_total = self.order.amount_total
        self.amount_paid = self.order.amount_paid
        self.amount_tax = self.order.amount_tax
        self.amount_return = self.order.amount_return
        self.payments = self.order.statement_ids


class fiscal_printer():
    def __init__(self, cr, uid, pos_session_id):
        self.pool = pooler.get_pool(cr.dbname)
        fp_config_obj = self.pool['fp.config']
        pos_session = self.pool['pos.session'].browse(cr, uid, pos_session_id)
        cash_register_id = pos_session.config_id.id

        printer_configs = fp_config_obj.search(
            cr, uid, [('cash_register_id', '=', cash_register_id)])
        self.cash_register = self.pool['pos.config'].browse(cr, uid, cash_register_id)

        if printer_configs:
            self.config = fp_config_obj.browse(cr, uid, printer_configs[0])
        else:
            raise osv.except_osv(
                'Warning', _('Cash register {cash_register} has no fiscal printers'.format(cash_register=self.cash_register.name)))
        
        module = __import__('openerp.addons.' + self.config.driver_id.module + '.driver', fromlist=[str(self.config.driver_id.class_name)])
        self.driver = getattr(module, str(self.config.driver_id.class_name))(self.config, self.cash_register.name)

    def print_receipt(self, receipt):
        self.driver.create(receipt)
        if self.config.dry:
            _logger.info('Discarding receipt for order {0}'.format(receipt.reference))
            self.driver.dry_print()
        else:
            if self.driver.print_receipt():
                _logger.info('Receipt for {0} printed successfully'.format(receipt.reference))
            else:
                _logger.error('There are problems with printing Receipt for {0}'.format(receipt.reference))


class fp_config(osv.osv):
    _name = 'fp.config'
    _description = 'Fiscal Printer configuration'

    def _get_name(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}

        res = {}
        
        configs = self.browse(cr, uid, ids)

        for config in configs:
            res[config.id] = config.cash_register_id.name + \
                ' : ' + config.driver_id.name

        return res

    _columns = {
        'name': fields.function(_get_name, 'Name', type='char', method=True),
        'cash_register_id': fields.many2one('pos.config', 'Cash Register', required=True),
        'driver_id': fields.many2one('fp.driver', 'Driver', required=True, help='Printer driver used for this client'),
        'ecr_password': fields.char('Password ECR', size=16, required=False, help='Password, if needed to print to fiscal printer'),
        'host': fields.char('Fiscal Printer Host Address', size=15, required=False, help='Fiscal Printer IP Address or Hostname (if Hostname can be resolved)'),
        'port': fields.integer('Port', required=False, help='Fiscal Printer Port'),
        'user': fields.char('Username', size=15, required=False, help='Username, if needed to access fiscal printer'),
        'password': fields.char('Password', size=15, required=False, help='Password, if needed to access fiscal printer'),
        'destination': fields.char('Destination', size=256, required=False, help='Destination directory, where receipt should be placed'),
        'dry': fields.boolean('Dry Run')
    }

    _sql_constraints = [
        ('cash_register_uniq', 'unique(cash_register_id)', 'Cash register must be unique!')
    ]


class fp_driver(osv.osv):
    _name = 'fp.driver'
    _description = 'Fiscal Printer Drivers'
    
    _columns = {
        'name': fields.char('FP Description', size=32, required=True, help='The Description of the Fiscal Printer'),
        'class_name': fields.char('Class Name', size=32, required=True, help='Name of the class that contain driver for printing on Fiscal Printer'),
        'module': fields.char('Driver module name', size=32, required=True, help='The name of the driver module'),
    }


class department(osv.osv):
    _name = 'department'
    _description = 'Tax department'
    
    _columns = {
        'name': fields.char('Department description', size=32, required=True, help='The Description of the department'),
        'department': fields.integer('Department', required=True)
    }


class account_tax(osv.osv):
    _inherit = 'account.tax'
    
    _columns = {
        'department': fields.many2one('department', 'Department', required=False)
    }
