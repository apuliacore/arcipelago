# main
welcome = "Ciao, sono il bot di @apuliacore!\n\nInvia /evento per suggerire un nuovo evento o /oggi per conoscere gli eventi di oggi."
no_event = "Sembra che non ci siano eventi registrati per oggi. Se vuoi puoi suggerirne uno con /evento."
ack_canceled_op = "Ok, operazione annullata."

# create event
poster = "Bene! Per iniziare invia la locandina dell'evento. Invia /cancel in qualsiasi momento per interrompere la conversazione."
ask_event_name = "Come si chiama l'evento?"
ask_venue_name = "Ora inserisci il luogo dell'evento: [ad esempio: Teatro Petruzzelli, Bari]"
ask_event_type = "Scegli la tipologia di evento da creare:"
help_event_type = "Scegli una tipologia di evento tra i valori predefiniti:"
ask_start_date = "Perfetto! Ora inserisci la data di inizio evento: [formato gg.mm.aaaa]"
ask_start_time = "A che ora inizia l'evento? [formato hh:mm]"
ask_event_duration = "Quanto dura l'evento? (in ore)"
similar_event = "Un evento simile al tuo è già stato proposto:"
ask_same_event = "Si tratta dello stesso evento?"
ask_add_end_date = "Ok! L'evento ha una data di fine diversa da quella di inizio?"
ack_same_event = "Ok allora, grazie lo stesso!"
ask_end_date = "Inserisci la data di fine evento: [formato gg.mm.aaaa]"
ask_add_end_time = "Vuoi inserire l'orario di fine evento?"
ask_end_time = "A che ora finisce l'evento? [formato hh:mm]"
ask_opening_hours = "Inserisci gli orari di apertura dell'esposizione: [formato hh:mm - hh:mm]"
ask_category = "Scegli una categoria per l'evento:"
help_category = "La categoria che hai scelto non è tra quelle previste. Usa la tastiera preimpostata:"
ask_description = "Inserisci le info utili per l'evento (come link per acquistare biglietti, programmi, line-up, etc):"
ask_publication_date = "Quando vuoi pubblicare l'evento? Inserisci la data in formato gg.mm.aaaa:"
ask_confirm_send_event = "Confermi di voler consigliare quest'evento?"
send_event_failure = "Si è verificato un errore con la generazione del messaggio :( \n Prova a cambiare leggermente la descrizione o il titolo o contatta i creatori del bot @luigijs e @shift97 per assistenza"
ack_event_accepted_admin = "L'evento è stato programmato per la pubblicazione. Grazie!"
ask_confirm_publish_event = "Confermare?"
ack_event_accepted_user = "L'evento che hai proposto è stato accettato e programmato per la pubblicazione. Grazie!"
ack_event_submitted = "L'evento è stato inviato ai moderatori. Grazie per la richiesta!"
ack_event_not_accepted = "Ti ringraziamo per la tua proposta, ma abbiamo deciso di non condividere l'evento che hai suggerito. Probabilmente non è il tipo di evento che ci proponiamo di promuovere, puoi leggere di più a riguardo qui: www.apuliacore.org/manifesto.html. Se vuoi parlare con noi, puoi scriverci nel gruppo Telegram o sulla nostra pagina Instagram."

# edit event
help_edit = "Invia il codice dell'evento dopo il comando, ad esempio così: /modifica codice-evento"
ack_edit_event = "Ok! Vuoi modificare questo evento:"
ask_edit_field = "Cosa vuoi modificare?"
edit_event_failure = "Non è stato trovato nessun evento con questo codice. L'evento potrebbe essere passato, oppure il codice potrebbe non essere più valido. Se hai un dubbio contattaci!"
help_edit_field = "Il campo che hai scelto non esiste. Scegline uno usando la tastiera qui sotto:"
ask_new_value_field = "Ok, invia il nuovo valore: [se è un orario usa il formato hh:mm, se è una data gg.mm.aaaa]"
ack_event_modified = "Evento modificato."


# send feedback
intro_feedback = "Ok, invia un messaggio con il tuo feedback:"
ask_anon = "Ok, vuoi rimanere anonim*? (in questo caso, non potrai essere ricontattat*)"
help_no_username = "Il tuo account Telegram non ha uno username associato, perciò non potremo ricontattarti. Ricorda che se vuoi puoi scriverci anche su Instagram (@apuliacore)."
ack_feedback_sent_anon = "Il tuo messaggio è stato inviato anonimamente agli admin. Grazie!"
ack_feedback_sent_ident = "Il tuo messaggio è stato inviato agli admin, ti ricontatteremo se necessario. Grazie!"


# donate
intro_donate = "Uau sarebbe bellissimo!"
info_donate = ''.join(["Apuliacore sostiene alcune piccole spese ricorrenti per la creazione e gestione di servizi e strumenti per la comunità. Con il tuo contributo ci aiuteresti a:",
			  "\n• mantenere attivi i server che ospitano il bot e il nostro sito web",
			  "\n• supportare il lavoro dietro lo sviluppo del bot",
			  "\n• promuovere e pubblicizzare Apuliacore attraverso altri mezzi (es. stampa di adesivi e materiale pubblicitario)."])
link_donate = "Se vuoi supportarci, puoi farlo tramite ko-fi a questo link: https://ko-fi.com/apuliacore 🌼\nGrazie!"
