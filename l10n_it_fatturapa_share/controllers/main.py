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
            return '<h1>Only type \'out\' or \'in\' are accepted</h1>'
        atts = request.env[model].search([])
        config_obj = request.env['ir.config_parameter'].get_param(
            'web.base.url')
        attachment_url = config_obj + "/web/attachments/token/"
        for att_obj in atts:
            if att_obj.access_token:
                att_link = attachment_url + att_obj.access_token
                res.update({
                    att_obj.name: att_link})
        return request.render('l10n_it_fatturapa_share.index', {'atts': res})

    @route('/web/attachments/token/<string:token>', type='http', auth="none")
    def get_attachments(self, token, **kwargs):
        try:
            attachment_ids = request.env['ir.attachment'].sudo().search(
                [('access_token', '=', token)])
            if attachment_ids:
                for attachment_obj in attachment_ids:
                    file_content = base64.b64decode(attachment_obj.datas)
                    disposition = 'attachment; filename=%s' % werkzeug.urls.\
                        url_quote(attachment_obj.datas_fname)
                    return request.make_response(
                        file_content,
                        [('Content-Type', attachment_obj.mimetype),
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
