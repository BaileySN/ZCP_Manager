ZCP-Manager

Dieses Tool soll das erstellen von Benutzerkonten im Zarafa mit DB-Plugin und die ganzen Schritte mit externen
Providern erleichtern.

Das Programm wird wie folgt mit den optionen gestartet:

python zcp-manager.py <option>

folgende optionen sind möglich:

help -> listet die Hilfe auf
config -> oeffnet die config datei mit dem Editor nano

Hinweis:
Beim ersten mal Starten, erstellt das Programm selbständig unter bin die Datei config.py und öffnet Sie mit dem
Editor nano.
Dort sollte man die Einstellung von dem derzeitigen getmail4 scripten (Script zum abholen von externen Konten) übernehmen.
Da dies danach für das Automatische erstellen verwendet wird.
