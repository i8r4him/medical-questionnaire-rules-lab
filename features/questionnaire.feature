Feature: Gesundheitsfragebögen nachvollziehbar zur Prüfung vorbereiten
  Die Ergebnisse beschreiben den Bearbeitungsweg eines synthetischen Fragebogens.

  @US1 @US2
  Scenario Outline: Die Demo-Fälle erhalten den vorgesehenen Bearbeitungsstatus
    Given der synthetische Fragebogen "<case_id>"
    When ich den Fragebogen mit Regelbasis "1.0.0" prüfe
    Then lautet der Bearbeitungsstatus "<status>"
    And sind Regelversion und Prüfsumme im Ergebnis enthalten

    Examples:
      | case_id | status           |
      | DEMO01  | READY_FOR_REVIEW |
      | DEMO02  | INCOMPLETE       |
      | DEMO03  | MANUAL_REVIEW    |
      | DEMO04  | INCOMPLETE       |
      | DEMO05  | INCOMPLETE       |
      | DEMO06  | MANUAL_REVIEW    |

  @US2
  Scenario: Ein fehlendes Detail bleibt sichtbar trotz Weiterleitungsregel
    Given der synthetische Fragebogen "DEMO02"
    When ich den Fragebogen mit Regelbasis "1.0.0" prüfe
    Then lautet der Bearbeitungsstatus "INCOMPLETE"
    And nennt das Ergebnis die Regeln "Q03,Q05"

  @US3
  Scenario: Ein wiederholter Lauf liefert dasselbe Prüfergebnis
    Given der synthetische Fragebogen "DEMO03"
    When ich den Fragebogen mit Regelbasis "1.0.0" prüfe
    And ich den Fragebogen erneut prüfe
    Then ist das Prüfergebnis unverändert
