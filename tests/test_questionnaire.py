import json
from pathlib import Path
import unittest

from health_rules.engine import load_rules


ROOT = Path(__file__).resolve().parent.parent
QUESTIONNAIRE_PATH = ROOT / 'fhir' / 'questionnaire.json'
RESPONSE_DEMO01_PATH = ROOT / 'fhir' / 'questionnaire-response-demo01.json'


def load_questionnaire():
    return json.loads(QUESTIONNAIRE_PATH.read_text(encoding='utf-8'))


def link_ids(items):
    found = []
    for item in items:
        found.append(item['linkId'])
        found.extend(link_ids(item.get('item', [])))
    return found


def answer_fields(book):
    names = set()
    for rule in book['rules']:
        names.add(rule['field'])
        details = rule.get('details_field')
        if isinstance(details, str):
            names.add(details)
    return names


class QuestionnaireResourceTests(unittest.TestCase):
    def setUp(self):
        self.book = load_rules()
        self.questionnaire = load_questionnaire()

    def test_questionnaire_loads_and_link_ids_match_rule_fields(self):
        self.assertEqual(self.questionnaire['resourceType'], 'Questionnaire')
        self.assertEqual(self.questionnaire['status'], 'draft')
        self.assertEqual(self.questionnaire['version'], self.book['version'])
        self.assertEqual(
            self.questionnaire['url'],
            'https://example.org/fhir/Questionnaire/synthetic-health-questionnaire')
        identifiers = link_ids(self.questionnaire['item'])
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(set(identifiers), answer_fields(self.book))

    def test_details_follow_the_boolean_they_depend_on(self):
        items = {item['linkId']: item for item in self.questionnaire['item']}
        required = {rule['field'] for rule in self.book['rules'] if rule['operation'] == 'required_boolean'}
        details = {rule['field']: rule['details_field'] for rule in self.book['rules']
                   if rule['operation'] == 'details_if_true'}
        self.assertEqual(set(items), required)
        for field, details_field in details.items():
            item = items[field]
            self.assertEqual(item['type'], 'boolean')
            self.assertTrue(item['required'])
            nested = item['item']
            self.assertEqual([child['linkId'] for child in nested], [details_field])
            child = nested[0]
            self.assertEqual(child['type'], 'string')
            self.assertTrue(child['required'])
            self.assertEqual(child['enableWhen'], [{
                'question': field, 'operator': '=', 'answerBoolean': True}])

    def test_review_rule_ids_are_not_questionnaire_items(self):
        review_ids = {rule['id'] for rule in self.book['rules'] if rule['operation'] == 'review_if_true'}
        self.assertTrue(review_ids)
        self.assertTrue(review_ids.isdisjoint(link_ids(self.questionnaire['item'])))


class QuestionnaireResponseDemo01Tests(unittest.TestCase):
    def test_demo01_boolean_answers_match_the_case(self):
        cases = json.loads((ROOT / 'data' / 'cases.json').read_text(encoding='utf-8'))
        demo01 = next(case for case in cases if case['case_id'] == 'DEMO01')
        questionnaire = load_questionnaire()
        response = json.loads(RESPONSE_DEMO01_PATH.read_text(encoding='utf-8'))
        known_link_ids = set(link_ids(questionnaire['item']))

        self.assertEqual(response['resourceType'], 'QuestionnaireResponse')
        self.assertEqual(response['status'], 'completed')
        self.assertEqual(response['questionnaire'], questionnaire['url'])

        answered = {}
        for item in response['item']:
            self.assertIn(item['linkId'], known_link_ids)
            answer = item['answer']
            self.assertEqual(len(answer), 1)
            value_fields = [key for key in answer[0] if key.startswith('value')]
            self.assertEqual(value_fields, ['valueBoolean'])
            value = answer[0]['valueBoolean']
            self.assertIs(type(value), bool)
            answered[item['linkId']] = value
        self.assertEqual(answered, demo01['answers'])
