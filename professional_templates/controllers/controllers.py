# -*- coding: utf-8 -*-
from openerp import http
from openerp.addons.report.controllers.main import ReportController
from openerp.addons.web.http import Controller, route, request
from werkzeug import exceptions, url_decode
from openerp.addons.web.controllers.main import _serialize_exception, content_disposition
from openerp.tools import html_escape
import json
from openerp import SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

class DownloadedReportFilename(ReportController):

	@route(['/report/download'], type='http', auth="user")
    	def report_download(self, data, token):
            """This function is used by 'qwebactionmanager.js' in order to trigger the download of
            a pdf/controller report.

            :param data: a javascript array JSON.stringified containg report internal url ([0]) and
            type [1]
            :returns: Response with a filetoken cookie and an attachment header
            """
	    response = super(DownloadedReportFilename, self).report_download(data, token)

	    requestcontent = json.loads(data)
            url, type = requestcontent[0], requestcontent[1]
            if type == 'qweb-pdf':
		   reportname = url.split('/report/pdf/')[1].split('?')[0]
		   docids = None
                   if '/' in reportname:
                       reportname, docids = reportname.split('/')

                   cr, uid = request.cr, SUPERUSER_ID
                   report = request.registry['report']._get_report_from_name(cr, uid, reportname)
		   xreport =None
                   if docids and len(docids) ==1:
                      # Generic report:
                      xreport = request.registry[report.model].browse(cr, uid, [int(docids)])
		   filename = None
		   if xreport:
			if report.model == 'account.invoice' and xreport.number:
			   filename = ( (xreport.type in ['out_invoice'] and 'Invoice'  or 'Bill') + 
				      '-' + xreport.number.replace(' ','_').replace('/', '_' ))
			elif report.model == 'purchase.order' and xreport.name:
			   filename = ( (xreport.state in ['draft', 'sent', 'to approve'] and 'RFQ' or 'Purchase_Order') + 
				       '-' + xreport.name.replace(' ', '_' ).replace('/', '_' ))
			elif report.model == 'sale.order' and xreport.name:
			   filename = ( (xreport.state in ['draft', 'sent'] and 'Quotation' or 'Sale_Order') + 
				       '-' + xreport.name.replace(' ', '_' ).replace('/', '_' ))
			elif report.model == 'stock.picking' and xreport.name:
			   filename = ( report.name.replace(' ','_').replace('/', '_' ) + 
				       '-' +xreport.name.replace(' ', '_' ).replace('/', '_' ))
					
		   if filename:
		      filename = '{}.pdf'.format(filename)
		      response.headers.remove('Content-Disposition')
		      response.headers.add('Content-Disposition', content_disposition(filename))

	    return response

