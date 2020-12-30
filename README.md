DA SISTEMARE ALLA FINE DELLA CONVERSIONE, QUESTE SONO LE RICHIESTE ORIGINALI!!

Vendite – order to deliver:

kanban ordini per settimana in base a delivery date con colori (tonalità chiara per leggibilità):

bianco = non ancora a calendario

rosso = mancano componenti da comperare

arancione = mancano componenti da produrre

giallo = pronto da produrre

verde = produzione iniziata

grigio = produzione terminata


Cambiando la delivery date, ad es. da novembre 2014 a gennaio 2015 lo stato viene ricalcolato e l'ordine può diventare producibile. (Nota: le settimane non tengono conto dell'anno, ci sono ancora vecchi ordini con settimana di gennaio 2014 che si sovrapporranno a ordini nuovi 2015).

La stessa cosa succede trascinando l'ordine nella vista kanban.

E' possibile forzare il ricalcolo dello stato cliccando “compute” vicino a “a calendario”. Possono essere visualizzati dei messaggi d'errore:

Launch scheduler and/or check orderpoints: significa che c'è un procurement make to stock in eccezione e manca un order point per soddisfare la richiesta – se le regole sono corrette e lo scheduler è passato non dovrebbe succedere
altri messaggi riguardano situazioni particolari, se capitano avvisateci


NB.: da aggiungere la mail al cliente per avvisarlo


Specifiche del calcolo dello stato:

viene esaminato tutto l'ordine riga per riga

per le righe con prodotti BUY e MAKE TO ORDER: si guarda la scheduled date della riga dell'ordine d'acquisto collegato e si confronta con la delivery date

per i prodotti MAKE TO STOCK (sia BUY sia MANUFACTURE) si guarda se il procurement collegato è in eccezione. Se NON lo è, significa che il prodotto è disponibile, altrimenti (dando per scontato che esistano corrette regole di riordino) considera la data calcolata da OpenERP in cui l'acquisto o la produzione generati automaticamente renderanno il prodotto disponibile. Se questa data è anteriore al giorno di calcolo, considera il giorno di calcolo (significa che il procurement è stato in sospeso)

per i prodotti MANUFACTURE e MAKE TO ORDER: si guarda lo stato del procurement del prodotto e dei suoi componenti, se ce n'è almeno uno non pronto, considera la data peggiore usando le stesse regole dei punti precedenti

Lo stato finale dell'ordine è il peggiore degli stati trovati. Se almeno un procurement dei prodotti contenuti nell'ordine o dei loro figli non è ancora stato analizzato dallo scheduler, l'ordine resta nello stato “non ancora a calendario”

NB.: eventuali ordini di acquisto e di produzione non aggiornati possono falsare i risultati. Ad es. MO make to stock previsti per mesi passati e mai prodotti e non cancellati. E' opportuno annullare eventuali vecchi PO o MO in sospeso.

E' importante notare che questo meccanismo è diverso da quello del forecast:

il forecast riguarda preventivi che non hanno ancora generato nessun ordine di acquisto o di produzione, quindi fa un calcolo teorico

il calendario invece riguarda ordini che hanno già generato acquisti e MO, attraverso il meccanismo dei procurement, quindi la consegnabilità dipende da operazioni che sono già state pianificate e man mano vengono portate avanti

Nel caso un fornitore ritardi la consegna, è opportuno cambiare la expected date nel PO parte “incoming shipments & invoices”, in modo che il calendario ne tenga conto.

SC: nota:
SO centralina > so con nome centralina
genera un MO
controlla disponibilità
produrre!
stato in corso
marca come completato quando la linea produzione ha prodotto