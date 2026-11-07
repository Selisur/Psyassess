pages = {
	"einladen" : {
		"title" : "Neuen Token versenden",
        "info" : "Sie befinden sich im Admin Bereich. Bitte geben Sie die Informationen des Patienten an, an den Sie eine Einladung versenden wollen, und authentifizieren Sie sich mit dem Admin Passwort.",
		"content" : """
            <div class = "form">
			<form method="post" id="invite">
		    <label> Vornamen <input name="vornamen" required></label>
		    <label> Nachnamen <input name="nachnamen" required></label>
		    <label> Email <input name="email" type="email" required></label>
		    <label> Admin Verifizierung <input name="pw" type="password" required> </label>
            <div class="buttonfield">
		    <button type="submit"> Neuen Patienten einladen </button>
	        </div>
            </form>
            </div>
            """ 
	},

    "eingeladen": {
		"title" : "Information",
        "info" : "Einladung wurde versendet.",
	},

    
	"einloggen" : {
		"title" : "Sitzung beginnen",
        "info" : "Herzlich Willkommen. Mit Klick auf >Einloggen< können Sie Ihre Sitzung beginnen und werden zu dem Formular weitergeleitet. Sie können dann über diesen Browser 2 Stunden lang in das Formular eingeben. Die Sitzung bleibt auch bei Schließen und Neuöffnen des Browsers bestehen. Wenn Sie das Formular absenden, oder 2 Stunden abgelaufen sind, wird die Sitzung beendet. Wollen Sie den Test wiederholen, wenden Sie sich bitte per Email an: it-matthess@t-online.de.",
		"content" : """		
        <div class ="form">
        <form method="post" id="login">
		<div class="buttonfield">
		<button type="submit"> Sitzung starten </button>	
		</div>
		</form>
        </div>
        """ 
        },


    "einreichen" : {
            "title" : "Psychologisches Schnellscreening",
            "info" : """
            Bitte kreuzen Sie nach Zutreffung an bzw. füllen Sie die freien Textfelder aus. Nach Absendung wird ein Ergebnis ausgewertet und Ihnen per Email zugesendet. Ihre Eingaben und Ergebnisse werden für die Dauer ihrer Behandlung bei uns DSGVO-konform in unseren Servern gespeichert. Für weitere Details sehen Sie bitte hier: <a href="/DSGVO"> DSGVO </a>""",
            "content" : """
            <div class = "form">
			<form method="post" id="test1">

				<div class="catalogue">

					<div class="section" id="gen_questions"> </div>

					<div class="section" id = "adhs_questions"> </div>

					<div class="section" id="free_questions"> </div>

				</div>

				<div class="buttonfield">
				<button type="submit"> Absenden </button>
                </div>	
			</form>
            </div>
        """
        },


	"eingereicht" : {
		"title" : "Eingabe erfolgreich",
        "info" : "Herzlichen Dank. Das Formular wurde erfolgreich übermittelt und ausgewertet. Bitte sehen Sie in Ihr Email-Postfach. Sollten Sie keine Antwort erhalten haben, wenden Sie sich bitte an: it-matthess@t-online.de.",
	}
}

