import hashlib
import json
from pathlib import Path


DEFAULT_RULES = Path(__file__).resolve().parent.parent / 'rules' / 'questionnaire.json'
OPERATIONS = {'required_boolean', 'details_if_true', 'review_if_true'}


def load_rules(path=DEFAULT_RULES):
    content = Path(path).read_bytes()
    book = json.loads(content)
    if not isinstance(book, dict) or not isinstance(book.get('version'), str) or not book['version'].strip():
        raise ValueError('Die Regelbasis braucht eine Versionsnummer.')
    rules = book.get('rules')
    if not isinstance(rules, list) or not rules:
        raise ValueError('Die Regelbasis muss Regeln enthalten.')
    identifiers = set()
    for rule in rules:
        if not isinstance(rule, dict) or any(not isinstance(rule.get(key), str) or not rule[key].strip()
                                           for key in ('id', 'operation', 'field', 'message')):
            raise ValueError('Regel unvollständig.')
        if rule['id'] in identifiers or rule['operation'] not in OPERATIONS:
            raise ValueError('Doppelte Regel-ID oder unbekannte Operation.')
        if rule['operation'] == 'details_if_true' and (
                not isinstance(rule.get('details_field'), str) or not rule['details_field'].strip()):
            raise ValueError('Der Name des Detailfelds fehlt.')
        identifiers.add(rule['id'])
    required = {rule['field'] for rule in rules if rule['operation'] == 'required_boolean'}
    if any(rule['field'] not in required for rule in rules):
        raise ValueError('Für jedes Fragefeld muss eine Boolean-Pflichtprüfung existieren.')
    return {**book, 'sha256': hashlib.sha256(content).hexdigest()}


def evaluate(case, book):
    if not isinstance(case, dict) or not isinstance(case.get('case_id'), str) or not case['case_id'].strip():
        raise ValueError('Jeder Fall braucht eine Fall-ID.')
    answers = case.get('answers')
    if not isinstance(answers, dict):
        raise ValueError('Antworten müssen als Objekt vorliegen.')
    findings = []
    for rule in book['rules']:
        value = answers.get(rule['field'])
        operation = rule['operation']
        outcome = None
        if operation == 'required_boolean' and type(value) is not bool:
            outcome = 'INCOMPLETE'
        elif operation == 'details_if_true' and value is True:
            details = answers.get(rule['details_field'])
            if not isinstance(details, str) or not details.strip():
                outcome = 'INCOMPLETE'
        elif operation == 'review_if_true' and value is True:
            outcome = 'MANUAL_REVIEW'
        if outcome:
            findings.append({'rule_id': rule['id'], 'field': rule['field'],
                             'outcome': outcome, 'message': rule['message']})
    # Fehlende Angaben haben Vorrang vor einer fachlichen Weiterleitung.
    outcomes = {finding['outcome'] for finding in findings}
    status = 'INCOMPLETE' if 'INCOMPLETE' in outcomes else (
        'MANUAL_REVIEW' if 'MANUAL_REVIEW' in outcomes else 'READY_FOR_REVIEW')
    return {'case_id': case['case_id'], 'status': status, 'findings': findings,
            'rules_version': book['version'], 'rules_sha256': book['sha256']}


def review(cases, book):
    if not isinstance(cases, list) or not cases:
        raise ValueError('Die Eingabe muss eine nicht leere Fallliste sein.')
    results = [evaluate(case, book) for case in cases]
    identifiers = [result['case_id'] for result in results]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError('Fall-IDs müssen eindeutig sein.')
    return {'rules_version': book['version'], 'rules_sha256': book['sha256'],
            'summary': {status: sum(result['status'] == status for result in results)
                        for status in ('READY_FOR_REVIEW', 'INCOMPLETE', 'MANUAL_REVIEW')},
            'results': results}
