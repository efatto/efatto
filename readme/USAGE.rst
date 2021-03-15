1. nel prodotto ho aggiunto un campo "Tempo di consegna Acquisto" che è calcolato in automatico dal campo "Tempo di consegna" del primo fornitore presente nella tabella "Fornitori" del prodotto nel tab "Acquisto" (si accettano consigli per un metodo di calcolo diverso, media? max? non ci si può basare sull'ordine di vendita comunque);

2. la (i) sulla riga è in blu se il prodotto è disponibile per la data promessa (o la data attuale se non indicata) e viene calcolata:

. se il prodotto è in casa: la data promessa - i giorni del campo "Tempi di consegna Cliente";

. se il prodotto non è in casa: la data promessa - i giorni dei campi ("Tempi di consegna Cliente" + "Tempo di Produzione" + "Tempo di consegna Acquisto")*;

La (i) è rossa in caso contrario.

3. sul pop-up informativo aperto dalla (i) è stato aggiunto il campo "Tempi di consegna al cliente" per scopo informativo, in quanto sulla vista forecast che si apre dal bottone a fianco i dati mostrati di magazzino sono per data ingresso a magazzino, che viene maggiorata del campo "Tempi di consegna Cliente" per valutarne la fattibilità di consegna entro la data promessa.

4. la data di arrivo indicata nel popup è stata rinominata "Prima data consegna disponibile" ed è il risultato di: data attuale + ("Tempi di consegna Cliente" + "Tempo di Produzione" + "Tempo di consegna Acquisto")*, quindi è la data in cui arriva il prodotto se lo riacquisto e lo faccio avere al cliente;

5. nel popup del forecast di magazzino che si apre ho bloccato lo scorrimento della prima colonna, così puoi scorrere avendo chiaro quale articolo stai leggendo; inoltre le date mostrate sono solo quelle in cui c'è qualche movimento (di stock, vendita, produzione) e sono precise (non settimanali come prima). Infine la quantità cumulativa è visibile solo per i movimenti originati da stock.

* se un prodotto viene solo acquistato, il campo "Tempo di Produzione" sarà 0, e viceversa per il campo "Tempo di consegna Acquisto".

n.b. la disponibilità di un articolo in arrivo in magazzino il giorno x è calcolata per il giorno x+1