# -*- coding: utf-8 -*-

from . import models
from . import controllers

import uuid
import logging
from openerp import SUPERUSER_ID


def post_init_hook(cr, registry):
    out_attachment_model = registry['fatturapa.attachment.out']
    in_attachment_model = registry['fatturapa.attachment.in']
    logging.getLogger('openerp.addons.l10n_it_fatturapa_share').info(
        'Setting values for token of e-invoices')
    out_attachment_ids = out_attachment_model.search(cr, SUPERUSER_ID, [])
    for out_attachment_id in out_attachment_ids:
        out_attachment_model.write(
            cr, SUPERUSER_ID, out_attachment_id, {
                'access_token': uuid.uuid4()})
    in_attachment_ids = in_attachment_model.search(cr, SUPERUSER_ID, [])
    for in_attachment_id in in_attachment_ids:
        in_attachment_model.write(
            cr, SUPERUSER_ID, in_attachment_id, {
                'access_token': uuid.uuid4()})
