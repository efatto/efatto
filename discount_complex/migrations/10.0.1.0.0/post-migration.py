# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def split_discount_to_triple(env):
    openupgrade.logged_query(
        env.cr, """
            UPDATE sale_order_line 
                SET 
                discount = (string_to_array(complex_discount, '+'))[1],
                discount2 = (string_to_array(complex_discount, '+'))[2],
                discount3 = (string_to_array(complex_discount, '+'))[3]
                WHERE complex_discount is not null;
            """
    )


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(
        env.cr, 'sale_order_line', 'complex_discount',
    ):
        split_discount_to_triple(env)
