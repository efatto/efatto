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

import tempfile
import os
from datetime import datetime


class Ecr():
    reference = ''

    def __init__(self, config, cash_register_name):
        self.__name__ = config.name
        self.config = config
        self.cash_register_name = cash_register_name
    
    def get_product_line(self):
        if self.product_lines:
            line = self.product_lines[0] # perchè c'era questo??? .pop(0)
            self.subtotal += line.price_subtotal
            if line.discount:
                self.discount += line.product_id.list_price * line.qty - line.price_subtotal
            return line
        else:
            return False
        
    def create(self, receipt):
        self.discount = 0.0
        self.subtotal = 0.0
        self.product_lines = receipt.lines
        self.receipt_data = receipt
        self.receipt_data.cash_register_name = self.cash_register_name
        
        self.receipt = self.compose()
    
    def __unicode__(self):
        return u'\r\n'.join(self.receipt) + u'\r\n\r\n'

    def __str__(self):
        return u'\r\n'.join(self.receipt) + u'\r\n\r\n'
    
    def compose(self):
        pass
    
    def print_receipt(self):
        pass
    
    def dry_print(self):
        destination = os.path.join(tempfile.gettempdir(), 'fp_tmp')
        if not os.path.exists(destination):
            os.makedirs(destination)
        ticket = datetime.now().strftime("%Y%m%d.%H%M") + '.txt'

        file(os.path.join(destination, ticket), 'w').write(
            unicode(self).encode('utf8'))
        
        return True
