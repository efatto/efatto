# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from . import models


def pre_init_hook(cr):
    cr.execute(
        "SELECT name, id"
        " from account_move WHERE id not in(SELECT MIN(id)"
        " from account_move GROUP BY name, company_id)")

    duplicated_ids = cr.fetchall()
    i = 0
    for duplicated_id in duplicated_ids:
        i += 1
        cr.execute(
            "UPDATE account_move SET name = '{0}' WHERE"
            " id = {1}".format(duplicated_id[0] + '-%s' % i, duplicated_id[1]))
