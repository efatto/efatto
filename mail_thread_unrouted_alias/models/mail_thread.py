# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
try:
    import simplejson as json
except ImportError:
    import json
import logging
import re
import socket
from email.message import Message

from openerp import api, tools
from openerp import SUPERUSER_ID
from openerp.addons.mail.mail_message import decode
from openerp.osv import fields, osv, orm
from openerp.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)

mail_header_msgid_re = re.compile('<[^<>]+>')

def decode_header(message, header, separator=' '):
    return separator.join(map(decode, filter(None, message.get_all(header, []))))


class mail_thread(osv.AbstractModel):
    _inherit = 'mail.thread'

    def message_route(self, cr, uid, message, message_dict, model=None, thread_id=None,
                      custom_values=None, context=None):
        """Attempt to figure out the correct target model, thread_id,
        custom_values and user_id to use for an incoming message.
        Multiple values may be returned, if a message had multiple
        recipients matching existing mail.aliases, for example.

        The following heuristics are used, in this order:
             1. If the message replies to an existing thread_id, and
                properly contains the thread model in the 'In-Reply-To'
                header, use this model/thread_id pair, and ignore
                custom_value (not needed as no creation will take place)
             2. Look for a mail.alias entry matching the message
                recipient, and use the corresponding model, thread_id,
                custom_values and user_id.
             3. Fallback to the ``model``, ``thread_id`` and ``custom_values``
                provided.
             4. If all the above fails, raise an exception.

           :param string message: an email.message instance
           :param dict message_dict: dictionary holding message variables
           :param string model: the fallback model to use if the message
               does not match any of the currently configured mail aliases
               (may be None if a matching alias is supposed to be present)
           :type dict custom_values: optional dictionary of default field values
                to pass to ``message_new`` if a new record needs to be created.
                Ignored if the thread record already exists, and also if a
                matching mail.alias was found (aliases define their own defaults)
           :param int thread_id: optional ID of the record/thread from ``model``
               to which this mail should be attached. Only used if the message
               does not reply to an existing thread and does not match any mail alias.
           :return: list of [model, thread_id, custom_values, user_id, alias]

        :raises: ValueError, TypeError
        """
        if not isinstance(message, Message):
            raise TypeError \
                ('message must be an email.message.Message at this point')
        mail_msg_obj = self.pool['mail.message']
        mail_alias = self.pool.get('mail.alias')
        fallback_model = model

        # Get email.message.Message variables for future processing
        message_id = message.get('Message-Id')
        email_from = decode_header(message, 'From')
        email_to = decode_header(message, 'To')
        references = decode_header(message, 'References')
        in_reply_to = decode_header(message, 'In-Reply-To').strip()
        thread_references = references or in_reply_to

        # 0. First check if this is a bounce message or not.
        #    See http://datatracker.ietf.org/doc/rfc3462/?include_text=1
        #    As all MTA does not respect this RFC (googlemail is one of them),
        #    we also need to verify if the message come from "mailer-daemon"
        localpart = (tools.email_split(email_from) or [''])[0].split('@', 1)[0].lower()
        if message.get_content_type() == 'multipart/report' or localpart == 'mailer-daemon':
            _logger.info \
                ("Not routing bounce email from %s to %s with Message-Id %s",
                         email_from, email_to, message_id)
            return []

        # 1. message is a reply to an existing message (exact match of message_id)
        ref_match = thread_references and tools.reference_re.search \
            (thread_references)
        msg_references = mail_header_msgid_re.findall(thread_references)
        mail_message_ids = mail_msg_obj.search(cr, uid,
            [('message_id', 'in', msg_references)], context=context)
        if ref_match and mail_message_ids:
            original_msg = mail_msg_obj.browse(cr, SUPERUSER_ID,
                                               mail_message_ids[0],
                                               context=context)
            model, thread_id = original_msg.model, original_msg.res_id
            alias_ids = mail_alias.search(cr, uid, [('alias_name', '=', (
            tools.email_split(email_to) or [''])[0].split('@', 1)[0].lower())])
            alias = None
            if alias_ids:
                alias = mail_alias.browse(cr, uid, [alias_ids[0]], context=context)
            route = self.message_route_verify(
                cr, uid, message, message_dict,
                (model, thread_id, custom_values, uid, alias),
                update_author=True, assert_model=False, create_fallback=True,
                context=dict(context, drop_alias=True))
            if route:
                _logger.info(
                    'Routing mail from %s to %s with Message-Id %s: direct reply to msg: model: %s, thread_id: %s, custom_values: %s, uid: %s',
                    email_from, email_to, message_id, model, thread_id,
                    custom_values, uid)
                return [route]
            elif route is False:
                return []

        # 2. message is a reply to an existign thread (6.1 compatibility)
        if ref_match:
            reply_thread_id = int(ref_match.group(1))
            reply_model = ref_match.group(2) or fallback_model
            reply_hostname = ref_match.group(3)
            local_hostname = socket.gethostname()
            # do not match forwarded emails from another OpenERP system (thread_id collision!)
            if local_hostname == reply_hostname:
                thread_id, model = reply_thread_id, reply_model
                if thread_id and model in self.pool:
                    model_obj = self.pool[model]
                    compat_mail_msg_ids = mail_msg_obj.search(
                        cr, uid, [
                            ('message_id', '=', False),
                            ('model', '=', model),
                            ('res_id', '=', thread_id),
                        ], context=context)
                    if compat_mail_msg_ids and model_obj.exists(cr, uid,
                                                                thread_id) and hasattr(
                        model_obj, 'message_update'):
                        route = self.message_route_verify(
                            cr, uid, message, message_dict,
                            (model, thread_id, custom_values, uid, None),
                            update_author=True, assert_model=True,
                            create_fallback=True, context=context)
                        if route:
                            # parent is invalid for a compat-reply
                            message_dict.pop('parent_id', None)
                            _logger.info(
                                'Routing mail from %s to %s with Message-Id %s: direct thread reply (compat-mode) to model: %s, thread_id: %s, custom_values: %s, uid: %s',
                                email_from, email_to, message_id, model, thread_id,
                                custom_values, uid)
                            return [route]
                        elif route is False:
                            return []

        # 3. Reply to a private message
        if in_reply_to:
            mail_message_ids = mail_msg_obj.search(cr, uid, [
                ('message_id', '=', in_reply_to),
                '!', ('message_id', 'ilike', 'reply_to')
            ], limit=1, context=context)
            if mail_message_ids:
                mail_message = mail_msg_obj.browse(cr, uid, mail_message_ids[0],
                                                   context=context)
                route = self.message_route_verify(cr, uid, message, message_dict,
                                                  (mail_message.model,
                                                   mail_message.res_id,
                                                   custom_values, uid, None),
                                                  update_author=True,
                                                  assert_model=True,
                                                  create_fallback=True,
                                                  allow_private=True,
                                                  context=context)
                if route:
                    _logger.info(
                        'Routing mail from %s to %s with Message-Id %s: direct reply to a private message: %s, custom_values: %s, uid: %s',
                        email_from, email_to, message_id, mail_message.id,
                        custom_values, uid)
                    return [route]
                elif route is False:
                    return []

        # no route found for a matching reference (or reply), so parent is invalid
        message_dict.pop('parent_id', None)

        # 4. Look for a matching mail.alias entry
        # Delivered-To is a safe bet in most modern MTAs, but we have to fallback on To + Cc values
        # for all the odd MTAs out there, as there is no standard header for the envelope's `rcpt_to` value.
        rcpt_tos = \
            ','.join([decode_header(message, 'Delivered-To'),
                      decode_header(message, 'To'),
                      decode_header(message, 'Cc'),
                      decode_header(message, 'Resent-To'),
                      decode_header(message, 'Resent-Cc')])
        local_parts = [e.split('@')[0].lower() for e in
                       tools.email_split(rcpt_tos)]
        if local_parts:
            alias_ids = mail_alias.search(cr, uid,
                                          [('alias_name', 'in', local_parts)])
            if alias_ids:
                routes = []
                for alias in mail_alias.browse(cr, uid, alias_ids,
                                               context=context):
                    user_id = alias.alias_user_id.id
                    if not user_id:
                        # TDE note: this could cause crashes, because no clue that the user
                        # that send the email has the right to create or modify a new document
                        # Fallback on user_id = uid
                        # Note: recognized partners will be added as followers anyway
                        # user_id = self._message_find_user_id(cr, uid, message, context=context)
                        user_id = uid
                        _logger.info('No matching user_id for the alias %s',
                                     alias.alias_name)
                    route = (
                    alias.alias_model_id.model, alias.alias_force_thread_id,
                    eval(alias.alias_defaults), user_id, alias)
                    route = self.message_route_verify(cr, uid, message,
                                                      message_dict, route,
                                                      update_author=True,
                                                      assert_model=True,
                                                      create_fallback=True,
                                                      context=context)
                    if route:
                        _logger.info(
                            'Routing mail from %s to %s with Message-Id %s: direct alias match: %r',
                            email_from, email_to, message_id, route)
                        routes.append(route)
                return routes

        # 5. Fallback to the provided parameters, if they work
        if not thread_id:
            # Legacy: fallback to matching [ID] in the Subject
            match = tools.res_re.search(decode_header(message, 'Subject'))
            thread_id = match and match.group(1)
            # Convert into int (bug spotted in 7.0 because of str)
            try:
                thread_id = int(thread_id)
            except:
                thread_id = False
        # 6. Last fallback for unrouted mail to unrouted_forward_alias:
        unrouted_alias = self.pool['ir.config_parameter'].get_param(
            cr, uid, 'mail.unrouted_forward_alias', default=True)
        if unrouted_alias:
            alias_ids = mail_alias.search(
                cr, uid, [('alias_name', '=', unrouted_alias)])
        if alias_ids:
            routes = []
            for alias in mail_alias.browse(cr, uid, alias_ids,
                                           context=context):
                user_id = alias.alias_user_id.id
                if not user_id:
                    # TDE note: this could cause crashes, because no clue that the user
                    # that send the email has the right to create or modify a new document
                    # Fallback on user_id = uid
                    # Note: recognized partners will be added as followers anyway
                    # user_id = self._message_find_user_id(cr, uid, message, context=context)
                    user_id = uid
                    _logger.info('No matching user_id for the alias %s',
                                 alias.alias_name)
                route = (
                    alias.alias_model_id.model, alias.alias_force_thread_id,
                    eval(alias.alias_defaults), user_id, alias)
                route = self.message_route_verify(cr, uid, message,
                                                  message_dict, route,
                                                  update_author=True,
                                                  assert_model=True,
                                                  create_fallback=True,
                                                  context=context)
                if route:
                    _logger.info(
                        'Routing mail from %s to %s with Message-Id %s: direct alias match: %r',
                        email_from, email_to, message_id, route)
                    routes.append(route)
            return routes

        route = self.message_route_verify(cr, uid, message, message_dict,
                                          (
                                          fallback_model, thread_id, custom_values,
                                          uid, None),
                                          update_author=True, assert_model=True,
                                          context=context)
        if route:
            _logger.info(
                'Routing mail from %s to %s with Message-Id %s: fallback to model:%s, thread_id:%s, custom_values:%s, uid:%s',
                email_from, email_to, message_id, fallback_model, thread_id,
                custom_values, uid)
            return [route]

        # ValueError if no routes found and if no bounce occured
        raise ValueError(
            'No possible route found for incoming message from %s to %s (Message-Id %s:). '
            'Create an appropriate mail.alias or force the destination model.' %
            (email_from, email_to, message_id)
        )