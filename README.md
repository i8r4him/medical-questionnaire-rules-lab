# Medical Questionnaire Rules Lab

[![Tests](https://github.com/i8r4him/medical-questionnaire-rules-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/i8r4him/medical-questionnaire-rules-lab/actions/workflows/tests.yml)

Ein kleines Python-Projekt: synthetische Gesundheitsfragebögen auf vollständige Antworten prüfen, ergänzende Angaben anfordern und Fälle nachvollziehbar zur menschlichen Prüfung weiterleiten.

Die fachliche Demo-Regelbasis liegt separat in JSON. Der Bericht nennt passende Regel-IDs, Gründe, Regelversion und SHA-256-Prüfsumme. So lässt sich erkennen, welche Regelbasis zu einem Prüfergebnis gehört.

## Ausprobieren

Python 3.10 oder neuer, keine Produktionsabhängigkeiten:

```bash
python3 -m health_rules data/cases.json --output reports/demo.json
python3 -m unittest discover -s tests -v
```

Die sechs Beispiele ergeben einen vollständigen Fragebogen ohne zusätzliche Weiterleitungsregel, drei unvollständige Fragebögen und zwei Fälle für eine menschliche Prüfung. [Beispielbericht](examples/review.json).

| Fall | Situation | Ergebnis |
| --- | --- | --- |
| DEMO01 | Beide Fragen vollständig mit `false` beantwortet | READY_FOR_REVIEW |
| DEMO02 | Laufende Behandlung angegeben, Details fehlen | INCOMPLETE |
| DEMO03 | Regelmäßige Medikamenteneinnahme mit Demo-Details | MANUAL_REVIEW |
| DEMO04 | Antwort zur laufenden Behandlung fehlt | INCOMPLETE |
| DEMO05 | Zeichenkette `"false"` statt Boolean `false` | INCOMPLETE |
| DEMO06 | Laufende Behandlung mit Demo-Details | MANUAL_REVIEW |

`READY_FOR_REVIEW` bedeutet, dass die konfigurierten Prüfungen keine Rückfrage oder besondere Weiterleitung ergeben haben. Die Ergebnisse beschreiben den Bearbeitungsstatus des Fragebogens.

## Regeln und Eingaben

Die [Regelbasis](rules/questionnaire.json) enthält sechs Regeln:

- Q01/Q02: Boolean-Antworten auf die beiden Pflichtfragen.
- Q03/Q04: Bei `true` wird ein nicht leerer Detailtext erwartet.
- Q05/Q06: Positive Antworten erzeugen einen Hinweis für menschliche Prüfung.

Fehlende Angaben haben Vorrang: Ein Fall mit fehlenden Details und einem Weiterleitungshinweis bleibt `INCOMPLETE`; beide Gründe bleiben im Ergebnis sichtbar. Texte werden auf Vorhandensein geprüft. Es werden nur die konfigurierten Felder berücksichtigt, zusätzliche Antwortfelder werden ignoriert. Die Regeln und Daten sind synthetische Beispiele.

Eingabe: nicht leere JSON-Liste mit eindeutigen `case_id`-Werten und einem `answers`-Objekt. Defekte Dateien oder unzulässige Regeldefinitionen ergeben Exit-Code 2. Gültige Verarbeitung ergibt Exit-Code 0, auch bei `INCOMPLETE`-Ergebnissen. Eingabe und Regelbasis können nicht als Ausgabedatei überschrieben werden.

## Testautomatisierung

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m xmlrunner discover -s tests -o reports/unit -v
python -m behave --junit --junit-directory reports/acceptance
```

Die Tests sichern korrekte Bearbeitungswege, fehlerhafte Datentypen, fehlende Details, Prioritäten, Regeländerungen und die Kommandozeile ab. Gherkin-Szenarien verknüpfen Anforderungen und ausführbare Tests. Behave ist der Python-Testläufer; das Projekt verwendet Gherkin und hat keine Cucumber-Abhängigkeit.

Der [Jenkinsfile](Jenkinsfile) installiert Testwerkzeuge in einer virtuellen Umgebung, führt Tests und Demo aus und veröffentlicht JUnit-Ergebnisse sowie Artefakte. GitHub Actions ist für Python 3.10 und 3.13 vorbereitet. [Prüfbericht](docs/test-report.md).

Weitere Unterlagen: [Anforderungen](docs/requirements.md), [Funktionsweise](docs/guide.md) und [Roadmap](docs/ROADMAP.md). `fhir/questionnaire.json` beschreibt die Fragen. `fhir/questionnaire-response-demo01.json` ist die Antwort von DEMO01. Die Regelprüfung liest beide Dateien nicht.
