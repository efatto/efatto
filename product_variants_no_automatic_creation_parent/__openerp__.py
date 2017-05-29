# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2017 Sergio Corato
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
    'name': 'Add variant parent on product configurator',
    'version': '8.0.1.0.0',
    'category': 'other',
    'description': """
With this module variants are created only for product attribute values,
without mixing all possibility.
E.g.: a template has an attribute "Leather Sand" which has three colors:
only 3 variant of Leather Sand colors will be computed for this template.
""",
    'author': 'Sergio Corato',
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    "depends": [
        'product_code_builder_parent',
        'product_variants_no_automatic_creation',
    ],
    "data": [
    ],
    "installable": True
}
