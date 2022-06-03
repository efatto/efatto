# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import logging
import poplib
import time
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from openerp.osv import fields, osv
from openerp import tools, api, models

_logger = logging.getLogger(__name__)
MAX_POP_MESSAGES = 50
MAIL_TIMEOUT = 60

# Workaround for Python 2.7.8 bug https://bugs.python.org/issue23906
poplib._MAXLINE = 65536
import pickle


class imap_track_seen_email_uids(models.Model):
    _name = 'fetchmail.imap_track_seen_email_uids'
    _description = 'UIDVALIDITY relative set for imap server account'
    _columns = {
            'account_fingerprint':fields.char(required=True ),
            'uidsset': fields.char(required=True, default=pickle.dumps(set()))
      }

    def _get_record(self, account_fingerprint):
        record = self.search([('account_fingerprint', '=', account_fingerprint)])
        if len(record) == 0:
            record = self.create({'account_fingerprint': account_fingerprint})
        return record

    def filter_unprocessed_email_uids_set(self, account_fingerprint, uidsset):
        record = self._get_record(account_fingerprint)

        pickled_set = record.uidsset
        processed_set = pickle.loads(pickled_set)
        return uidsset-processed_set

    def update_processed_email_uids_set(self, account_fingerprint, uids_set):
        if not uids_set: #No need to read and write from db when the update does not have an effect
            return

        record = self._get_record(account_fingerprint)

        processed_set = pickle.loads(record.uidsset)
        processed_set.update(uids_set)
        record.uidsset = pickle.dumps(processed_set)


class fetchmail_server(osv.osv):
    """Incoming POP/IMAP mail server account"""
    _inherit = 'fetchmail.server'

    def fetch_mail(self, cr, uid, ids, context=None):
        """WARNING: meant for cron usage only - will commit() after each email!"""
        env = models.api.Environment(cr, uid, context)
        imap_track_seen_email_uids = env['fetchmail.imap_track_seen_email_uids']
        context = dict(context or {})
        context['fetchmail_cron_running'] = True
        mail_thread = self.pool.get('mail.thread')
        action_pool = self.pool.get('ir.actions.server')
        for server in self.browse(cr, uid, ids, context=context):
            _logger.info('start checking for new emails on %s server %s', server.type, server.name)
            context.update({'fetchmail_server_id': server.id, 'server_type': server.type})
            count, failed = 0, 0
            imap_server = False
            pop_server = False
            if server.type == 'imap':
                processed_email_uids = set()
                try:
                    imap_server = server.connect()
                    imap_server.select()

                    email_uids_validity = imap_server.response('UIDVALIDITY')[1][0]
                    account_fingerprint = pickle.dumps((uid, server.name, server.type, server.id,email_uids_validity))

                    inbox_email_uids = imap_server.uid('search', 'all')
                    inbox_email_uids_set = set([int(x) for x in inbox_email_uids[1][0].split()])

                    email_uids_to_fetch = imap_track_seen_email_uids.filter_unprocessed_email_uids_set(account_fingerprint, inbox_email_uids_set)

                    for email_uid in email_uids_to_fetch:
                        res_id = None
                        result, data = imap_server.uid('fetch', email_uid, '(BODY.PEEK[])')
                        try:
                            processed_email_uids.update(set([email_uid])) #Move this after res_id=... to always retry failed messages!
                            res_id = mail_thread.message_process(cr, uid, server.object_id.model,
                                                                 data[0][1],
                                                                 save_original=server.original,
                                                                 strip_attachments=(not server.attach),
                                                                 context=context)
                        except Exception:
                            _logger.exception('Failed to process mail from %s server %s.', server.type, server.name)
                            failed += 1

                        if res_id and server.action_id:
                            action_pool.run(cr, uid, [server.action_id.id], {'active_id': res_id, 'active_ids': [res_id], 'active_model': context.get("thread_model", server.object_id.model)})
                        cr.commit()
                        count += 1
                    _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", count, server.type, server.name, (count - failed), failed)

                except Exception:
                    _logger.exception("General failure when trying to fetch mail from %s server %s.", server.type, server.name)

                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
                        imap_track_seen_email_uids.update_processed_email_uids_set(account_fingerprint, processed_email_uids)

            elif server.type == 'pop':
                try:
                    while True:
                        pop_server = server.connect()
                        (numMsgs, totalSize) = pop_server.stat()
                        pop_server.list()
                        for num in range(1, min(MAX_POP_MESSAGES, numMsgs) + 1):
                            (header, msges, octets) = pop_server.retr(num)
                            msg = '\n'.join(msges)
                            res_id = None
                            try:
                                res_id = mail_thread.message_process(cr, uid, server.object_id.model,
                                                                     msg,
                                                                     save_original=server.original,
                                                                     strip_attachments=(not server.attach),
                                                                     context=context)
                                pop_server.dele(num)
                            except Exception:
                                _logger.exception('Failed to process mail from %s server %s.', server.type, server.name)
                                failed += 1
                            if res_id and server.action_id:
                                action_pool.run(cr, uid, [server.action_id.id], {'active_id': res_id, 'active_ids': [res_id], 'active_model': context.get("thread_model", server.object_id.model)})
                            cr.commit()
                        if numMsgs < MAX_POP_MESSAGES:
                            break
                        pop_server.quit()
                        _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", numMsgs, server.type, server.name, (numMsgs - failed), failed)
                except Exception:
                    _logger.exception("General failure when trying to fetch mail from %s server %s.", server.type, server.name)
                finally:
                    if pop_server:
                        pop_server.quit()
            server.write({'date': time.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)})
        return True
