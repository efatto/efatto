# -*- coding: utf-8 -*-
import json
import base64
import werkzeug

from openerp.http import Controller, route, request, Response,\
    serialize_exception as _serialize_exception
from openerp.tools import html_escape


class FatturaPAAttachmentDownload(Controller):

    @route('/download/<model>', type='http', auth='user', methods=['GET'])
    def index(self, model=None, **kwargs):
        res = {}
        if model not in ['fatturapa.attachment.out',
                         'fatturapa.attachment.in']:
            return '<h1>Only type \'fatturapa.attachment.out\' or' \
                   ' \'fatturapa.attachment.in\' are accepted</h1>'
        domain = []
        for key, value in kwargs.items():
            if key == 'date_start':
                domain.append(('create_date', '>=', value))
            elif key == 'date_end':
                domain.append(('create_date', '<=', value))
        atts = request.env[model].search(domain)
        config_obj = request.env['ir.config_parameter'].get_param(
            'web.base.url')
        attachment_url = config_obj + "/web/" + model + "/token/"
        for att_obj in atts:
            if att_obj.access_token:
                att_link = attachment_url + att_obj.access_token
                res.update({
                    att_obj.name: att_link})
        return request.render('l10n_it_fatturapa_share.index', {'atts': res})

    @route('/web/<string:model>/token/<string:token>', type='http', auth="none")
    def get_attachments(self, model, token, **kwargs):
        try:
            attachment_ids = request.env[model].sudo().search(
                [('access_token', '=', token)])
            if attachment_ids:
                for attachment_obj in attachment_ids:
                    file_content = base64.b64decode(attachment_obj.datas)
                    disposition = 'attachment; filename=%s' % werkzeug.urls.\
                        url_quote(attachment_obj.datas_fname)
                    return request.make_response(
                        file_content,
                        [('Content-Type', attachment_obj.file_type),
                         ('Content-Length', len(file_content)),
                         ('Content-Disposition', disposition)])
            else:
                error = {
                    'code': 200,
                    'message': "Unable to find the attachments",
                }
                return request.make_response(html_escape(json.dumps(error)))

        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error %s " % se,
            }
            return request.make_response(html_escape(json.dumps(error)))
