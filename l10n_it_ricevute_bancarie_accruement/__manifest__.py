# Copyright 2017-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Ricevute bancarie accruement',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'description': '''
Ricevute bancarie con processo di maturazione per valuta
--------------------------------------------------------
Con questo modulo viene modificato il processo per rendere possibili i
seguenti passaggi:

- Creazione delle ri.ba. con emissione del flusso.
- Accettazione dell'intero flusso ri.ba. emesso verso la banca.
  Viene creata la registrazione di chiusura del credito
  v/il cliente e l'entrata corrispondente usualmente nel
  conto "Effetti all'incasso". Questo conto va configurato
  come "crediti" e contenendo data di scadenza e dettagli sul cliente,
  è utile per la chiusura di bilancio.
- Registrazione di accredito del flusso: è possibile farlo sia
  per l'intero flusso o per una/più linee dalle distinte riba, oppure
  per una/più righe dal menu linee riba. Viene creata una registrazione
  di accredito dell'importo nel c/c, con corrispondente importo
  a debito nel conto ri.ba. all'incasso. Questa registrazione è in
  sostanza un giroconto per l'apertura del debito verso la banca, in
  corrispondenza dell'anticipazione di credito ricevuta.
- Registrazione di maturazione a valuta per selezione di
  singole ri.ba. (eseguibile dalla vista elenco ri.ba.) o dell'intero
  flusso, eseguibile dalla distinta ri.ba. Viene riconciliato il partner.
- Registrazione di insoluti multipli su una sola registrazione contabile.
    ''',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_ricevute_bancarie',
    ],
    'data': [
        'views/riba_view.xml',
        'views/wizard_accreditation.xml',
        'views/wizard_unsolved.xml',
        'views/wizard_accruement.xml',
        'views/account_view.xml',
    ],
    'installable': True
}
