# Roadmap

Dieses Projekt prüft synthetische Fragebögen mit einer JSON-Regelbasis. Die nächsten Änderungen gehen in kleinen Schritten Richtung HL7 FHIR R4. Jeder Schritt ist ein eigener Pull Request und soll für sich verständlich sein. Die Regelprüfung bleibt die Referenz, bis ein späterer Schritt dieselben Demo-Fälle dagegenhält.

Es werden nur synthetische Daten verwendet. Es kommt keine FHIR-Server-Implementierung, keine klinische Bewertung und keine Anbindung an ein Krankenhaussystem hinzu.

## Ausgangspunkt

- Zwei Fragen: `ongoing_treatment` und `regular_medication`. Beide sind Pflicht und Boolean.
- Zwei Detailtexte: `treatment_details` und `medication_details`. Pflicht nur bei der Antwort `true`.
- Sechs Regeln in `rules/questionnaire.json`. Q01 bis Q04 prüfen die Vollständigkeit. Q05 und Q06 leiten positive Antworten an eine menschliche Prüfung weiter.
- Der Interpreter in `health_rules/engine.py` liest nur diese Regeldatei. Er kennt FHIR nicht.
- Sechs synthetische Fälle in `data/cases.json`.

| Regel | Bedeutung | Abbildung in FHIR |
| --- | --- | --- |
| Q01, Q02 | Pflicht-Boolean | `Questionnaire.item` mit `type: boolean` und `required: true` |
| Q03, Q04 | Detailtext, wenn die Antwort `true` ist | verschachteltes Item mit `type: string` und `enableWhen` |
| Q05, Q06 | Weiterleitung zur menschlichen Prüfung | keine Frage. Bleibt in der Regelbasis |

`linkId` ist der stabile Name einer Frage. Spätere Antworten verweisen darauf. Die linkIds sind deshalb genau die Feldnamen der Regeln, nicht die Regel-IDs.

## Schritte

### 1. Questionnaire-Ressource — erledigt

`fhir/questionnaire.json` beschreibt die beiden Fragen als FHIR-R4-Questionnaire, Version `1.0.0` wie die Regelbasis. Ein Test lädt die Datei und vergleicht die linkIds mit den Feldern aus `load_rules()`. Die Kommandozeile und die Statuslogik sind unverändert. Die Datei ist keine Konformitätsprüfung und kein Ersatz für die Regeln.

### 2. Eine QuestionnaireResponse für DEMO01 — erledigt

`fhir/questionnaire-response-demo01.json` bildet den synthetischen Fall DEMO01 ab. Beide Antworten sind Boolean `false` und stehen in `answer.valueBoolean`. `questionnaire` ist die Canonical-URL aus `fhir/questionnaire.json`. Die linkIds sind dieselben wie im Questionnaire. Die Detailfragen fehlen in der Antwort, weil sie bei `false` nicht aktiv sind. `status` der Antwort ist `completed`, weil beide Pflichtfragen beantwortet sind. Ein Test liest DEMO01 aus `data/cases.json` und vergleicht die beiden Werte. Die Datei ist keine Konformitätsprüfung. Die übrigen fünf Fälle sind noch nicht abgebildet.

### 3. Alle sechs Demo-Fälle abbilden

Dieselben Regeln für DEMO02 bis DEMO06. Fehlende Antworten werden weggelassen, nicht als `null` ergänzt. Die Zeichenkette `"false"` bleibt eine Zeichenkette. Test: keine Antwort wird still in einen Boolean umgewandelt.

### 4. linkIds gegen den Questionnaire prüfen

Eine kleine Funktion prüft, dass jede Antwort einen linkId aus dem Questionnaire verwendet, inklusive verschachtelter Items. Ein unbekannter linkId ist ein Fehler. Das ist eine Strukturprüfung mit der Standardbibliothek, kein FHIR-Validator.

### 5. Pflichtfelder und enableWhen mit der Regelbasis vergleichen

Für Q01 bis Q04: ein Pflicht-Boolean muss wirklich ein Boolean sein; ein aktiviertes Detail muss ein nicht leerer Text sein. Ob ein Fall dadurch `INCOMPLETE` wird, wird für die sechs Demo-Fälle mit `evaluate` verglichen. Q05 und Q06 bleiben außen vor. Die Regeldatei bleibt die fachliche Referenz.

### 6. Weiterleitung und Herkunft weiter ausweisen

Q05 und Q06 erzeugen weiterhin `MANUAL_REVIEW`, mit Regel-ID, Version und SHA-256. `INCOMPLETE` hat weiter Vorrang. Die Herkunft wird am Ergebnis festgehalten und nicht in zusätzliche Fragen umgebaut. Test mit DEMO02 und DEMO03.

### 7. Synthetische Patient-Ressourcen

Kleine, offensichtlich künstliche Patient-Ressourcen im FHIR-Format, wie sie ein Synthea-Export enthalten würde. `QuestionnaireResponse.subject` verweist auf diese Patient-IDs. Synthea selbst wird in diesem Schritt nicht installiert; die Fixture liegt im Repository. Keine echten Personendaten und keine Kennungen aus realen Vergabesystemen. Ein späterer Lauf von Synthea darf nur synthetische Ausgabe ins Repository legen.

### 8. Antworten in SQLite laden

Mit `sqlite3` aus der Standardbibliothek zwei Tabellen füllen: eine Zeile je Fragebogen, eine Zeile je Antwort (`link_id`, Wert, Typ). Test: eine Abfrage zählt die Antworten je linkId.

### 9. Vollständigkeit per SQL auswerten

Eine SQL-Abfrage findet fehlende Pflicht-linkIds und leere Detailtexte bei Antwort `true`. Die Anzahl wird mit der Zusammenfassung der Regelprüfung verglichen. In den Demo-Fällen sind das drei Ergebnisse mit Status `INCOMPLETE`.

### 10. Dieselben Tests in der bestehenden CI

Die neuen Tests laufen über `python3 -m unittest discover`, also in GitHub Actions und im Jenkinsfile ohne neues Produktionspaket. Eine Abhängigkeit wie `fhir.resources` oder DuckDB kommt nur dazu, wenn ein konkreter Schritt sie braucht und die Standardbibliothek nicht mehr reicht. DuckDB wäre höchstens eine zweite Ansicht auf dieselben Tabellen, nachdem die SQLite-Auswertung steht.

## Grenzen

- Die Dateien unter `fhir/` werden vom Interpreter nicht gelesen.
- `Questionnaire.status: draft` heißt: Lernbeispiel, kein freigegebenes Formular.
- Freitext wird auch später nur auf Vorhandensein geprüft.
- Es gibt kein Scoring und keine medizinische Entscheidung.
- Der Prüfbericht unter `docs/test-report.md` ist ein Snapshot vom 10.10.2026 und wird nicht bei jedem Schritt umgeschrieben.
