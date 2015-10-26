# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from openerp.tools.float_utils import float_round, float_compare
from openerp.tools.translate import _


class google_calendar(models.AbstractModel):
    _inherit = 'google.calendar'

    def update_from_google(self, cr, uid, event, single_event_dict, type, context):
        res = super(google_calendar, self).update_from_google(cr, uid, event, single_event_dict, type, context)
        # todo: create task
        calendar_event = self.pool['calendar.event']
        cal_event = calendar_event.browse(cr, uid, res)
        hours_work = cal_event.duration
        self.pool['project.task'].create(cr, uid, vals, context=context)
        return res

    def delete_an_event(self, cr, uid, event_id, context=None):
        super(google_calendar, self).delete_an_event(cr, uid, event_id=event_id, context=context)
        # todo: delete task
