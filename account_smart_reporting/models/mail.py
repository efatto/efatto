# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import osv


class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'

    def generate_email_for_composer_batch(self, cr, uid, template_id,
                                          res_ids, context=None,
                                          fields=None):
        values = super(mail_compose_message, self).generate_email_for_composer_batch(cr, uid, template_id,
                                          res_ids, context=context,
                                          fields=fields)
        try:
            template_id = self.pool.get('ir.model.data'). \
                get_object_reference(
                cr, uid, 'account_smart_reporting',
                'email_template_sales_details'
            )
        except:
            pass  # todo raise
        if context['default_template_id'] == template_id[1]:
            # TODO get list of pdf to attach
            attachment_ids = []
            attachment_obj = self.pool['ir.attachment']
            for invoice in self.pool['account.invoice'].browse(
                cr, uid, context['active_ids']):
                if invoice.type in ['out_invoice', 'out_refund']:
                    doc_type = 'out'
                    # attach report
                else:
                    attachment_ids += attachment_obj.search(
                        cr, uid, [(
                            'res_model', '=', 'account.invoice'),
                            ('res_id', '=', invoice.id),
                        ])
        values[values.keys()[0]].update({'attachment_ids': attachment_ids})
        return values
