Questo modulo permette di gestire il fine ciclo di vita del prodotto sostituendolo in maniera programmata.

Si basa sul modulo `product_state` che aggiunge gli stati del prodotto.

Aggiunge i campi:

#. "È in fine ciclo di vita" nello stato del prodotto
#. "Quantità minima a magazzino" nel prodotto
#. "Prodotti sostitutivi", che è una lista di prodotti sostitutivi, nel prodotto
#. "Data disponibilità prodotto sostitutivo" nel prodotto

Quando al prodotto viene assegnato uno stato in cui è attivo il flag "È in fine ciclo di vita":

#. viene compilato automaticamente il campo "Quantità minima a magazzino" da un cron giornaliero, che inserisce il 10% del venduto degli ultimi 365 gg.
#. (TODO OPPURE basato sul campo Disponibile?).
#. (NOTE DI SVILUPPO: questo campo si può solo far aggiornare da un cron perché: 1. l'obbligatorietà scatterebbe solo in una fase successiva alla creazione, quindi l'utente non lo sa; 2. il calcolo della quantità a magazzino non è il caso di farla automaticamente con un depends(), scatterebbe troppo spesso inutilmente)
#. se è già stato acquistato almeno uno dei prodotti sostitutivi il campo "Data disponibilità prodotto sostitutivo" viene compilato in automatico con la prima data di ricezione prevista del prodotto
#. (TODO: se non è stato acquistato alcun prodotto sostitutivo → il sistema deve calcolarsi, in base al tempo di consegna del fornitore del prodotto sostitutivo e in base al venduto del prodotto da sostituire, la quantità sotto alla quale inviare PO (che quindi sarà maggiore rispetto alla quantità minima da tenere a magazzino) R. non mi è chiaro quale formula usare, non mi baso sul calcolo fatto dalla regola di riordino quindi? Del tipo che se un prodotto da sostituire tenta di creare un riordino, lo faccio andare verso il prodotto sostitutivo? Il sistema dovrebbe generare regola per il prodotto sostitutivo sulla base del venduto del prodotto sostituto. R. Dovrei fare creare la regola con gli stessi criteri impostati sul modello di generazione delle regole di riordino per il prodotto sostituito, usando i dati relativi al prodotto sostituito, no? Sì)

TODO: Tutto ciò dovrebbe portare ad una serie di azioni automatiche invio mail (testo da definire):

#. mail a tutti quelli citati quando un prodotto passa a "Fine ciclo di vita" inserendo codici e tempi sostitutivi (in modo che ufficio commerciale avvisi i clienti) R. creare un'azione automatica basata sull'aggiornamento del campo che spedisce una mail
#. mail a tutti quelli citati sotto quando un prodotto va sotto la quantità minima da tenere a magazzino (in modo che ufficio tecnico possa aggiornare le distinte) R. verificare se con l'azione automatica si riesce ad intercettare la variazione della quantità minima, altrimenti creare un'azione programmata a un paio d'ore, con invio mail. Se non c'è una regola di riordino, da cui prendere la quantità minima a magazzino, non viene inviata la mail, eccetto il caso in cui il prodotto vada in negativo (o a zero direi).
#. mail ad acquisti quando un prodotto sostitutivo va acquistato (casistica 2) R. creare un campo store=True dove andare ad salvare il fatto che sia "Sostituzione in corso" e sul cambiamento di questo campo creare un'azione automatica che spedisce la mail
#. mail a tutti quelli citati quando l'arrivo (IN) del prodotto sostitutivo diventa Completato (in modo che tutti sappiano che il nuovo prodotto è disponibile) R. sfruttare il campo sopra per passare allo stato "Sostituzione completata" per poter creare un'altra azione automatica che invia un'altra mail

TODO Un'altra casistica potrebbe essere il cambio fornitore per un prodotto. Come possiamo da Odoo avere un avviso quando il lotto del vecchio fornitore termina e inizia quello del nuovo? R. quindi il nome del prodotto resta lo stesso ma è di un altro fornitore? Si dovrebbe attivare la gestione dei lotti in Odoo (argomento tra l'altro che dovrei affrontare anche per il WHS) però lo trattiamo separatamente. Sì esatto, stesso codice, diverso fornitore. La gestione del lotto diventa dunque obbligatoria. R. la attivo sul test, ti scrivo sugli altri ticket aperti a riguardo, prossimamente.


Nota: questa funzionalità non riguarda il caso in cui allo stesso prodotto assegni un codice prodotto del fornitore diverso ma il prodotto rimane lo stesso per te, cosa che è gestibile direttamente dalla lista fornitori nel prodotto.
