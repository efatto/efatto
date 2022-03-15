Il modulo permette di gestire la fatturazione delle spese di consegna in modo automatico in base alle consegne effettuate, se i parametri di configurazione "delivery_auto_refresh.auto_add_delivery_line" e "delivery_auto_refresh.refresh_after_picking" sono impostati.

Il sistema standard prevede l'addebito di un importo calcolato sull'ordine di vendita, che nel modulo "delivery_auto_refresh" è esteso con l'aggiornamento automatico delle spese di consegna in base alle consegne eseguite, ma viene resettato ad ogni consegna.
Con questo modulo il calcolo delle spese di consegna è eseguito sui trasporti eseguiti e viene sommato fino a quando non viene fatturato, rendendo quindi possibile effettuare diverse consegne e fatturare l'importo esatto delle spese.
Inoltre, a seguito della fatturazione e a successive consegne, il sistema aggiunge una riga di spese di consegna aggiuntiva parametrata sulle consegna non ancora fatturate, in modo da proseguire con l'addebito corretto.
