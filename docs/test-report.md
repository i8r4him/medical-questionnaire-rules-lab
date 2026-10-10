# Prüfbericht

Stand: 10.10.2026, Europe/Berlin.

## Geprüfter Umfang

Python-Regelinterpreter, versionierte JSON-Regelbasis mit sechs Regeln, sechs synthetische Fragebögen, JSON-Ergebnisbericht, Kommandozeile, automatisierte Tests und CI-Konfiguration.

| Prüfung | Ergebnis |
| --- | --- |
| Regel- und Kommandozeilentests | 13 erfolgreich, keine Fehler |
| Gherkin-Abnahme mit Behave | 8 Szenarien / 32 Schritte erfolgreich; keine übersprungen |
| Demo-Regelbasis 1.0.0 | 1 READY_FOR_REVIEW, 3 INCOMPLETE, 2 MANUAL_REVIEW |
| Regelpflege 1.0.0 → 1.1.0 | Zusätzliche Detailpflicht verändert den Status ohne Interpreteränderung; ergänzte Details erlauben erneut MANUAL_REVIEW |
| Nachvollziehbarkeit | Ergebnisse enthalten passende Regel-IDs, Gründe, Version und SHA-256 der Regeldatei |
| Fehlerfälle | Ungültige Regeldefinitionen und Eingaben werden abgewiesen; fehlerhafte Eingabe überschreibt keinen vorhandenen Bericht |
| Abhängigkeiten | `pip check` ohne Konflikte |

Lokale Umgebung: Python 3.12.14, Behave 1.3.3, unittest-xml-reporting 3.2.0. Die Demo läuft ohne externe Produktionspakete. Der Beispielbericht unter `examples/review.json` entspricht dem aktuellen Ergebnis.

## Jenkins-Ausführung

Der `Jenkinsfile` wurde mit Jenkins 2.580.1 und Temurin Java 21.0.10 auf einer temporären lokalen Instanz ausgeführt. Build `medical-questionnaire-checks #1`: **SUCCESS**. Die Pipeline hat den lokalen Git-Prüfstand ausgecheckt, Abhängigkeiten installiert, beide Testsuiten ausgeführt, 21 Testfälle über das JUnit-Plugin veröffentlicht und XML-Ergebnisse sowie den Demo-Bericht archiviert.

Die temporäre Instanz wurde nach dem Prüflauf beendet. GitHub Actions führt die Tests und Demo bei Pushes und Pull Requests auf Python 3.10 und 3.13 aus. Ergebnisse und herunterladbare Berichte stehen unter [GitHub Actions](https://github.com/i8r4him/medical-questionnaire-rules-lab/actions/workflows/tests.yml). Der Jenkins-Nachweis oben bezieht sich auf den lokalen Prüflauf.

Die Prüfungen verwenden ausschließlich synthetische Fragebögen und Beispielregeln.
