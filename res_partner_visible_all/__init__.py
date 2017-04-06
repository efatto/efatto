# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from . import models


def pre_init_hook(cr):
    #  UPDATE all res_partner and set visible for all companies
    cr.execute("UPDATE res_partner set company_id = Null")
