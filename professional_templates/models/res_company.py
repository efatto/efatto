# -*- coding: utf-8 -*-

from openerp import models, fields, api

class pt_res_company(models.Model):
        _inherit = ["res.company"]

        facebook = fields.Char('Facebook ID')
        twitter = fields.Char('Twitter Handle')
        googleplus = fields.Char('Google-Plus ID')



class default_report_sett(models.Model):
	_inherit=["res.company"]

        @api.model
        def _default_so_template(self):
            def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'SO Template' ), ('type', '=', 'qweb')], 
		order='id asc', limit=1)
            return def_tpl or self.env.ref('sale.report_saleorder_document')

        @api.model
        def _default_po_template(self):
            def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'PO Template' ), ('type', '=', 'qweb')], 
		order='id asc', limit=1)
            return def_tpl or self.env.ref('purchase.report_purchaseorder_document')

        @api.model
        def _default_rfq_template(self):
            def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'RFQ Template' ), ('type', '=', 'qweb')], 
		order='id asc', limit=1)
            return def_tpl or self.env.ref('purchase.report_purchasequotation_document')

        @api.model
        def _default_dn_template(self):
            def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'Delivery Template' ), ('type', '=', 'qweb')], 
		order='id asc', limit=1)
            return def_tpl or self.env.ref('stock.report_picking')

        @api.model
        def _default_pk_template(self):
            def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'Picking Template' ), ('type', '=', 'qweb')], 
		order='id asc', limit=1)
            return def_tpl or self.env.ref('stock.report_picking')

        @api.model
        def _default_inv_template(self):
            def_tpl = self.env['ir.ui.view'].search([('name', 'like', 'Invoice Template' ), ('type', '=', 'qweb')],
                order='id asc', limit=1)
            return def_tpl or self.env.ref('account.report_invoice_document')


	invoice_logo = fields.Binary("Report Logo", attachment=True,
               help="This the image used as logo for any report, if non is uploaded, the company logo will be used by default")	
	template_so = fields.Many2one('ir.ui.view', 'Sales Order Template', default=_default_so_template, 
			domain="[('type', '=', 'qweb'), ('name', 'like', 'SO Template' )]", required=False)

	template_po = fields.Many2one('ir.ui.view', 'Purchase Order Template', default=_default_po_template, 
			domain="[('type', '=', 'qweb'), ('name', 'like', 'PO Template' )]", required=False)

	template_rfq = fields.Many2one('ir.ui.view', 'RFQ Template', default=_default_rfq_template, 
			domain="[('type', '=', 'qweb'), ('name', 'like', 'RFQ Template' )]", required=False)

	template_dn = fields.Many2one('ir.ui.view', 'Delivery Note Template', default=_default_dn_template, 
			domain="[('type', '=', 'qweb'), ('name', 'like', 'Delivery Template' )]", required=False)

	template_pk = fields.Many2one('ir.ui.view', 'Picking Template', default=_default_pk_template, 
			domain="[('type', '=', 'qweb'), ('name', 'like', 'Picking Template' )]", required=False)

##########################################################################################################################################


        invoice_logo = fields.Binary("Logo", attachment=True,
                help="This field holds the image used as logo for the invoice, if non is uploaded, the company logo will be used")
        template_invoice = fields.Many2one('ir.ui.view', 'Invoice Template', default=_default_inv_template,
                        domain="[('type', '=', 'qweb'), ('name', 'like', 'Invoice Template' )]", required=False)
        odd = fields.Char('Odd parity Color', size=7, required=True, default="#F2F2F2", help="The background color for Odd invoice lines in the invoice")       
        even = fields.Char('Even parity Color', size=7, required=True, default="#FFFFFF", help="The background color for Even invoice lines in the invoice" )   
        theme_color = fields.Char('Theme Color', size=7, required=True, default="#F07C4D", help="The Main Theme color of the invoice. Normally this\
                         should be one of your official company colors")
        text_color = fields.Char('Text Color', size=7, required=True, default="#6B6C6C", help="The Text color of the invoice. Normally this\
                         should be one of your official company colors or default HTML text color")
        name_color = fields.Char('Company Name Color', size=7, required=True, default="#F07C4D", help="The Text color of the Company Name. Normally this\
                         should be one of your official company colors or default HTML text color")
        cust_color = fields.Char('Customer Name Color', size=7, required=True, default="#F07C4D", help="The Text color of the Customer Name. Normally this\
                         should be one of your official company colors or default HTML text color")
        theme_txt_color = fields.Char('Theme Text Color', size=7, required=True, default="#FFFFFF",
                         help="The Text color of the areas bearing the theme color. Normally this should NOT be the same color as the\
                                theme color. Otherwise the text will not be visible")

        header_font = fields.Selection([(x,str(x)) for x in range(1,51)], string="Header Font-Size(px):", default=10, required=True)
        body_font = fields.Selection([(x,str(x)) for x in range(1,51)], string="Body Font-Size(px):", default=10,required=True)
        footer_font = fields.Selection([(x,str(x)) for x in range(1,51)], string="Footer Font-Size(px):", default=8,required=True)
        font_family = fields.Char('Font Family:', default="sans-serif", required=True)
        aiw_report = fields.Boolean('Show amount in words', default=True, help="Check this box to enable the display of amount in words in the invoice/quote/sale order reports by default..this means when you create a new report, the amount in words will appear in the report unless you override it in the settings of that particular report")
        show_img = fields.Boolean('Display Product Image in Reports?', default=True, help="Check this box to display product image in Sales Order, Quotation, Invoice and Delivery Note")
