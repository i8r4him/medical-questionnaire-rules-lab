import json

from behave import given, when, then

from health_rules.engine import DEFAULT_RULES, evaluate, load_rules


@given('der synthetische Fragebogen "{case_id}"')
def questionnaire(context, case_id):
    cases = json.loads((DEFAULT_RULES.parent.parent / 'data/cases.json').read_text())
    context.case = next(case for case in cases if case['case_id'] == case_id)


@when('ich den Fragebogen mit Regelbasis "{version}" prüfe')
def run_rules(context, version):
    context.book = load_rules()
    assert context.book['version'] == version
    context.result = evaluate(context.case, context.book)


@when('ich den Fragebogen erneut prüfe')
def repeat(context):
    context.repeated = evaluate(context.case, load_rules())


@then('lautet der Bearbeitungsstatus "{status}"')
def status(context, status):
    assert context.result['status'] == status, context.result


@then('sind Regelversion und Prüfsumme im Ergebnis enthalten')
def provenance(context):
    assert context.result['rules_version'] == context.book['version']
    assert context.result['rules_sha256'] == context.book['sha256']


@then('nennt das Ergebnis die Regeln "{identifiers}"')
def findings(context, identifiers):
    assert [finding['rule_id'] for finding in context.result['findings']] == identifiers.split(',')


@then('ist das Prüfergebnis unverändert')
def same_result(context):
    assert context.repeated == context.result
