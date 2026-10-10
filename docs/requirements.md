# Anforderungen und Abnahme

## US1: Angaben vollständig erfassen

Als bearbeitende Person möchte ich fehlende und falsch typisierte Antworten erkennen, damit ich gezielt nachfragen kann.

- Beide Pflichtfragen brauchen einen echten JSON-Boolean. `0`, `1` oder `"false"` werden nicht automatisch umgewandelt.
- Positive Antworten brauchen nicht leere ergänzende Angaben.
- Ein fehlender Detailtext hat Vorrang vor der Weiterleitung zur fachlichen Prüfung.

Nachweis: Gherkin DEMO02/04/05 und Prioritätsszenario; `test_boolean_answers_are_not_coerced`, `test_follow_up_details_are_required_for_both_questions`, `test_incomplete_has_priority_over_manual_review`.

## US2: Den Bearbeitungsweg erklären

Als bearbeitende Person möchte ich passende Regel-IDs und Gründe sehen, damit ein Ergebnis nachvollziehbar ist.

- Ein vollständiger Fall ohne positive Antwort ergibt `READY_FOR_REVIEW`.
- Ein vollständiger Fall mit positiver Antwort ergibt `MANUAL_REVIEW`.
- Alle zutreffenden Hinweise bleiben im Ergebnis, auch wenn ein anderer Hinweis den Gesamtstatus bestimmt.

Nachweis: Gherkin DEMO01/03/06 und Regel-ID-Szenario; `test_complete_positive_answers_require_human_review`, `test_demo_outcomes_and_summary`.

## US3: Regeln kontrolliert ändern

Als entwickelnde Person möchte ich Regeln unabhängig vom Programmcode pflegen und Änderungen testen.

- Version und SHA-256 der eingelesenen Regeldatei werden im Ergebnis gespeichert. Die Prüfsumme bezeichnet die konkreten Dateibytes und ist keine digitale Signatur.
- Identische Daten und Regeldateien ergeben identische Ergebnisse.
- Unbekannte Operationen, doppelte Regel-IDs und Regeln ohne Pflichtprüfung werden abgewiesen.

Nachweis: Gherkin-Wiederholungsszenario; `test_result_identifies_rules_and_is_repeatable`, `test_invalid_rulebooks_are_rejected`, `test_rule_change_requires_new_details_without_engine_change`.

### Beispieländerung 1.0.0 → 1.1.0

Im automatisierten Test wird eine temporäre Kopie der Regelbasis um Q07 ergänzt: Bei laufender Behandlung verlangt der Demo-Workflow zusätzlich `follow_up_context`. Der vorher vollständige DEMO-Fall wird damit `INCOMPLETE`. Nach Ergänzung des Kontextes muss er wieder `MANUAL_REVIEW` ergeben. Die Originaldatei bleibt unverändert. Die Änderung ist ein Lernbeispiel für ein zusätzliches Formularfeld, keine neue medizinische Bewertungsregel.

## Jenkins verwenden

Pipeline-, Git- und JUnit-Plugins sowie ein Unix-Agent mit Git und `python3` ab 3.10 werden benötigt. Die Agent-Umgebung muss virtuelle Python-Umgebungen erstellen und Pakete herunterladen können. In einem Pipeline-Job „Pipeline script from SCM“ wählen und `Jenkinsfile` als Script Path verwenden. Die Pipeline ist auf zehn Minuten begrenzt, lässt keine gleichzeitigen Builds zu und behält die letzten zehn Builds.

JUnit-Ergebnisse werden in den jeweiligen Teststufen auch bei Testfehlern veröffentlicht. Der Demo-Bericht und XML-Dateien werden als Artefakte gespeichert. Nur die eigenen Testausgaben unter `reports/` werden vor einem neuen Lauf entfernt. Für GitHub Actions muss das Projekt als Repository mit aktiviertem Actions-Dienst vorliegen.
