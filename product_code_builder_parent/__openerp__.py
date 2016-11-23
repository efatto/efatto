# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016 Sergio Corato - SimplERP srl (<http://www.simplerp.it>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{
    'name': 'Compute variants on product template using only parent attribute',
    'version': '8.0.1.0.0',
    'category': 'other',
    'description': """
With this module variants are created only for product attribute values,
without mixing all possibility.
E.g.: a template has an attribute "Leather Sand" which has three colors:
only 3 variant of Leather Sand colors will be computed for this template.
""",
    'author': 'Sergio Corato - SimplERP SRL',
    'website': 'http://www.simplerp.it',
    'license': 'AGPL-3',
    "depends": [
        'product_attribute_value_image',
        'product_code_builder',
        'product_variants_no_automatic_creation',
        'sale_order_recalculate_prices_variants',
    ],
    "data": [
        'views/product_view.xml',
    ],
    "installable": True
}
