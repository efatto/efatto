# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import base64
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import datetime
import re


class RibaFileExport(orm.TransientModel):
    _inherit = "riba.file.export"

    def _Record50(self, importo_debito, invoice_ref, data_invoice,
                  partita_iva_creditore):
        self._descrizione = invoice_ref
        return (
            " 50" + str(self._progressivo).rjust(7, '0') +
            self._descrizione.ljust(80)[0:80] + " " * 10 +
            partita_iva_creditore.ljust(16, ' ') + " " * 4 + "\r\n")

    def act_getfile(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', [])
        order_obj = self.pool['riba.distinta'].browse(
            cr, uid, active_ids, context=context)[0]
        credit_bank = order_obj.config_id.bank_id
        name_company = order_obj.config_id.company_id.partner_id.name
        if not credit_bank.iban:
            raise orm.except_orm('Error', _('No IBAN specified'))
        iban = credit_bank.iban.replace(" ", "")
        credit_abi = credit_bank.bank.abi or iban[-22:-17]
        credit_cab = credit_bank.bank.cab or iban[-17:-12]
        credit_conto = iban[-12:]
        if not credit_bank.codice_sia:
            raise orm.except_orm(
                'Error', _('No SIA Code specified for: ') + name_company)
        credit_sia = credit_bank.codice_sia
        dataemissione = datetime.datetime.now().strftime("%d%m%y")
        nome_supporto = datetime.datetime.now().strftime(
            "%d%m%y%H%M%S") + credit_sia
        creditor_address = order_obj.config_id.company_id.partner_id
        creditor_city = creditor_address.city or ''
        if (
            not order_obj.config_id.company_id.partner_id.vat and not
            order_obj.config_id.company_id.partner_id.fiscalcode
        ):
            raise orm.except_orm(
                'Error',
                _('No VAT or Fiscalcode specified for: ') + name_company)
        array_testata = [
            credit_sia,
            credit_abi,
            credit_cab,
            credit_conto,
            dataemissione,
            nome_supporto,
            'E',
            name_company,
            creditor_address.street or '',
            creditor_address.zip or '' + ' ' + creditor_city,
            order_obj.config_id.company_id.partner_id.ref or '',
            (
                order_obj.config_id.company_id.partner_id.vat and
                order_obj.config_id.company_id.partner_id.vat[2:] or
                order_obj.config_id.company_id.partner_id.fiscalcode),
        ]
        arrayRiba = []
        for line in order_obj.line_ids:
            debitor_address = line.partner_id
            debitor_street = debitor_address.street or ''
            debitor_zip = debitor_address.zip or ''
            debit_abi = debit_cab = debit_bank_name = False
            if line.bank_riba_id:
                debit_riba_bank = line.bank_riba_id
                if (debit_riba_bank.abi and debit_riba_bank.cab):
                    debit_abi = debit_riba_bank.abi
                    debit_cab = debit_riba_bank.cab
                debit_bank_name = debit_riba_bank.name
            elif line.bank_id:
                debit_bank = line.bank_id
                if debit_bank.iban:
                    debit_iban = debit_bank.iban.replace(" ", "")
                    debit_abi = debit_iban[5:10]
                    debit_cab = debit_iban[10:15]
                debit_bank_name = debit_bank.bank.name or debit_bank.bank_name
            else:
                raise orm.except_orm(
                    _('Error'),
                    _('No IBAN or ABI/CAB specified for ') +
                    line.partner_id.name)
            debitor_city = debitor_address.city and debitor_address.city.ljust(
                23)[0:23] or ''
            debitor_province = (
                debitor_address.state_id and debitor_address.state_id.code or
                '')
            if not line.due_date:  # ??? VERIFICARE
                due_date = '000000'
            else:
                due_date = datetime.datetime.strptime(
                    line.due_date[:10], '%Y-%m-%d').strftime("%d%m%y")

            if not line.partner_id.vat and not line.partner_id.fiscalcode:
                raise orm.except_orm(
                    'Error',
                    _('No VAT or Fiscalcode specified for: ') +
                    line.partner_id.name)
            if not debit_bank_name:
                #  removed: bank and debit_bank.bank.name or
                #  debit_bank.bank_name):
                raise orm.except_orm(
                    'Error',
                    _('No debit_bank specified for ') + line.partner_id.name)
            invoice_ref = ''
            if line.invoice_number and line.invoice_number != '':
                invoice_ref = 'FT N. ' + line.invoice_number + ' DEL ' + \
                    datetime.datetime.strptime(
                        line.invoice_date, DEFAULT_SERVER_DATE_FORMAT
                    ).strftime('%d/%m/%Y')
            else:
                if line.move_line_ids:
                    if line.move_line_ids[0].move_line_id:
                        invoice_ref = line.move_line_ids[0].move_line_id.name \
                            and line.move_line_ids[0].move_line_id.name or ''
            Riba = [
                line.sequence,
                due_date,
                line.amount,
                # using regex we remove chars outside letters, numbers, space,
                # dot and comma because, special chars cause errors.
                re.sub(r'[^\w\s,.]+', '', line.partner_id.name)[:60],
                line.partner_id.vat and line.partner_id.vat[
                    2:] or line.partner_id.fiscalcode,
                re.sub(r'[^\w\s,.]+', '', debitor_street)[:30],
                debitor_zip[:5],
                debitor_city[:24],
                debitor_province,
                debit_abi,
                debit_cab,
                debit_bank_name,  # changed
                line.partner_id.ref and line.partner_id.ref[:16] or '',
                invoice_ref,  # changed
                line.invoice_date,
            ]
            arrayRiba.append(Riba)

        out = base64.encodestring(
            self._creaFile(array_testata, arrayRiba).encode("utf8"))
        self.write(
            cr, uid, ids, {
                'state': 'get',
                'riba_txt': out,
                'file_name': '%s.txt' % order_obj.name
                }, context=context)

        model_data_obj = self.pool.get('ir.model.data')
        view_rec = model_data_obj.get_object_reference(
            cr, uid, 'l10n_it_ricevute_bancarie', 'wizard_riba_file_export')
        view_id = view_rec and view_rec[1] or False

        return {
            'view_type': 'form',
            'view_id': [view_id],
            'view_mode': 'form',
            'res_model': 'riba.file.export',
            'res_id': ids[0],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
