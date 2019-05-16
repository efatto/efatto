# -*- coding: utf-8 -*-

from openerp.http import Controller, route, request, Response


class FatturaPAAttachmentDownload(Controller):

    @route('/download/<model>', type='https', auth='user', methods=['GET'])
    def index(self, model=None, **kwargs):
        if model == 'out':
            fa_model = 'fatturapa.attachment.out'
        elif model == 'in':
            fa_model = 'fatturapa.attachment.in'
        else:
            return '<h1>Only out or in accepted</h1>'
        FatturaPAAttachment = request.env[fa_model]
        atts = FatturaPAAttachment.search([])
        return request.render('l10n_it_fatturapa_share.index', {'atts': atts})
