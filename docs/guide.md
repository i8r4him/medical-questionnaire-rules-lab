# Funktionsweise

## Überblick

Das Medical Questionnaire Rules Lab prüft synthetische Gesundheitsfragebögen. Pflichtangaben, zusätzliche Details und Weiterleitungen sind als JSON-Regeln hinterlegt. Ein kleiner Python-Interpreter führt diese Regeln aus und dokumentiert Gründe sowie die verwendete Regelversion. Mit unittest und Gherkin-Szenarien wird das Verhalten überprüft.

## Warum gibt es drei Ergebnisse?

`INCOMPLETE` bedeutet: Angaben fehlen oder haben den falschen Datentyp. `MANUAL_REVIEW` bedeutet: Die Angaben sind vorhanden, aber eine Demo-Regel sieht eine menschliche Prüfung vor. `READY_FOR_REVIEW` bedeutet: Es gibt keinen zusätzlichen Hinweis aus den konfigurierten Regeln.

## Was passiert bei mehreren passenden Regeln?

Alle Hinweise werden gesammelt. Für den Gesamtstatus haben fehlende Angaben Vorrang. Beispiel DEMO02: Q03 meldet fehlende Behandlungsdetails, Q05 verlangt eine menschliche Prüfung. Der Gesamtstatus bleibt zunächst `INCOMPLETE`.

## Warum keine automatische Umwandlung von „false“?

In JSON sind `false` und `"false"` unterschiedliche Datentypen. Eine automatische Umwandlung kann fehlerhafte Eingaben verdecken. Deshalb prüft Q01 den Typ ausdrücklich; auch die Zahl 0 wird nicht als gültige Antwort behandelt.

## Was zeigt der Änderungstest?

Der Test ergänzt in einer temporären Regelbasis ein neues erforderliches Detailfeld und erhöht die Version. Ohne Änderung am Interpreter muss sich das Ergebnis passend ändern. Mit dem ergänzten Detail muss der Fall wieder vollständig sein. Die Tests sichern zusätzlich das Verhalten der alten Regelbasis ab.

## Welche Rolle haben Version und SHA-256?

Die Version beschreibt den fachlichen Änderungsstand. Die Prüfsumme bezeichnet die eingelesenen Dateibytes. Beides wird mit dem Ergebnis gespeichert. Eine absichtliche Manipulation wird dadurch nicht verhindert; die Prüfsumme ist keine Unterschrift und keine Echtheitsgarantie.

## Was sind die Grenzen?

Es gibt zwei Demo-Fragen, sechs Grundregeln und synthetische Daten. Freitext wird nur auf Vorhandensein geprüft. Das Projekt beurteilt keine medizinischen Inhalte. Es gibt keine Datenbank, Weboberfläche, produktive Systemanbindung oder FHIR-Konformitätsprüfung.

## Ein Beispiel verändern

DEMO02 ausführen, die Hinweise Q03 und Q05 ansehen und anschließend einen synthetischen `treatment_details`-Text ergänzen. Danach ergibt der Fall `MANUAL_REVIEW`.
