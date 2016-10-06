# -*- coding: utf-8 -*-
import logging
import simplejson
import os
import openerp
import time
import random
import werkzeug.utils

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import module_boot, login_redirect

_logger = logging.getLogger(__name__)


class PosController(http.Controller):

    @http.route('/notification/needaction', type='json', auth='user')
    def unread_message(self, **k):
        ir_ui_menu = request.registry['ir.ui.menu']
        cr, uid , context = request.cr, request.uid, request.context
        menu_ids = ir_ui_menu.get_user_roots(cr, uid, context=request.context)
        all_menu_ids = ir_ui_menu.search(cr, uid, [('id', 'child_of', menu_ids)], 0, False, False, context=context)
        menu_needaction = ir_ui_menu.get_needaction_data(cr, uid, all_menu_ids, context)
        actions = {}
        for action in menu_needaction:
            if menu_needaction[action]['needaction_enabled'] and menu_needaction[action]['needaction_counter']:
                actions[action] = {'need_action': menu_needaction[action]['needaction_counter']}

        for name in ir_ui_menu.read(cr, uid, actions.keys(), ['complete_name', 'action'] , context=context):
            actions[name['id']]['name'] = name['complete_name']
            actions[name['id']]['action_id'] = (name['action'].split(','))[1]
        return actions
