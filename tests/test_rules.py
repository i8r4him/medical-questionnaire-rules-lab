import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from health_rules.engine import DEFAULT_RULES, evaluate, load_rules, review


ROOT = DEFAULT_RULES.parent.parent


class RuleTests(unittest.TestCase):
    def setUp(self):
        self.book = load_rules()
        self.case = {'case_id': 'TEST01', 'answers': {
            'ongoing_treatment': False, 'regular_medication': False}}

    def test_demo_outcomes_and_summary(self):
        cases = json.loads((ROOT / 'data/cases.json').read_text())
        report = review(cases, self.book)
        self.assertEqual([item['status'] for item in report['results']], [
            'READY_FOR_REVIEW', 'INCOMPLETE', 'MANUAL_REVIEW',
            'INCOMPLETE', 'INCOMPLETE', 'MANUAL_REVIEW'])
        self.assertEqual(report['summary'], {'READY_FOR_REVIEW': 1, 'INCOMPLETE': 3, 'MANUAL_REVIEW': 2})

    def test_boolean_answers_are_not_coerced(self):
        for value in [0, 1, 'false', 'true', None, [], {}]:
            with self.subTest(value=value):
                self.case['answers']['ongoing_treatment'] = value
                result = evaluate(self.case, self.book)
                self.assertEqual(result['status'], 'INCOMPLETE')
                self.assertEqual([item['rule_id'] for item in result['findings']], ['Q01'])

    def test_missing_answer(self):
        del self.case['answers']['regular_medication']
        self.assertEqual(evaluate(self.case, self.book)['findings'][0]['rule_id'], 'Q02')

    def test_follow_up_details_are_required_for_both_questions(self):
        for field, details, rule in [('ongoing_treatment', 'treatment_details', 'Q03'),
                                     ('regular_medication', 'medication_details', 'Q04')]:
            for value in [None, '', '  ', 12, [], {}]:
                with self.subTest(field=field, details=value):
                    case = copy.deepcopy(self.case)
                    case['answers'].update({field: True, details: value})
                    result = evaluate(case, self.book)
                    self.assertEqual(result['status'], 'INCOMPLETE')
                    self.assertIn(rule, [item['rule_id'] for item in result['findings']])

    def test_complete_positive_answers_require_human_review(self):
        self.case['answers'].update(ongoing_treatment=True, treatment_details='Synthetische Angabe.',
                                    regular_medication=True, medication_details='Synthetische Angabe.')
        result = evaluate(self.case, self.book)
        self.assertEqual(result['status'], 'MANUAL_REVIEW')
        self.assertEqual([item['rule_id'] for item in result['findings']], ['Q05', 'Q06'])

    def test_incomplete_has_priority_over_manual_review(self):
        self.case['answers']['ongoing_treatment'] = True
        result = evaluate(self.case, self.book)
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertEqual([item['outcome'] for item in result['findings']], ['INCOMPLETE', 'MANUAL_REVIEW'])

    def test_result_identifies_rules_and_is_repeatable(self):
        first = evaluate(self.case, self.book)
        self.assertEqual(first, evaluate(self.case, load_rules()))
        self.assertEqual(first['rules_version'], '1.0.0')
        self.assertEqual(first['rules_sha256'], self.book['sha256'])
        self.assertEqual(len(first['rules_sha256']), 64)

    def test_rule_change_requires_new_details_without_engine_change(self):
        self.case['answers'].update(ongoing_treatment=True, treatment_details='Synthetische Angabe.')
        self.assertEqual(evaluate(self.case, self.book)['status'], 'MANUAL_REVIEW')
        changed = json.loads(DEFAULT_RULES.read_text())
        changed['version'] = '1.1.0'
        changed['rules'].append({'id': 'Q07', 'operation': 'details_if_true',
                                 'field': 'ongoing_treatment', 'details_field': 'follow_up_context',
                                 'message': 'Zusätzlicher Kontext für den Demo-Workflow fehlt.'})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'rules.json'
            path.write_text(json.dumps(changed))
            book = load_rules(path)
        result = evaluate(self.case, book)
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertEqual(result['findings'][-1]['rule_id'], 'Q07')
        self.assertEqual(result['rules_version'], '1.1.0')
        self.assertNotEqual(result['rules_sha256'], self.book['sha256'])
        self.case['answers']['follow_up_context'] = 'Synthetischer Zusatzkontext.'
        self.assertEqual(evaluate(self.case, book)['status'], 'MANUAL_REVIEW')
        self.assertEqual(evaluate(self.case, self.book)['status'], 'MANUAL_REVIEW')

    def test_invalid_rulebooks_are_rejected(self):
        baseline = json.loads(DEFAULT_RULES.read_text())
        variants = [None, [], {}, {**baseline, 'version': ''}, {**baseline, 'rules': []},
                    {**baseline, 'rules': [None]},
                    {**baseline, 'rules': baseline['rules'] + [baseline['rules'][0]]}]
        for operation, details in [('eval', 'x'), ('details_if_true', ''), ('review_if_true', 'x')]:
            variants.append({**baseline, 'rules': [{'id': 'BAD', 'operation': operation,
                             'field': 'unvalidated', 'message': 'Test.', 'details_field': details}]})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'rules.json'
            for index, book in enumerate(variants):
                with self.subTest(variant=index):
                    path.write_text(json.dumps(book))
                    with self.assertRaises(ValueError):
                        load_rules(path)

    def test_invalid_cases_and_duplicate_ids_are_rejected(self):
        for cases in [None, {}, [], [None], [{}], [{'case_id': 'X', 'answers': []}],
                      [{'case_id': ' ', 'answers': {}}], [self.case, self.case]]:
            with self.subTest(cases=cases), self.assertRaises(ValueError):
                review(cases, self.book)


class CommandTests(unittest.TestCase):
    def command(self, *args):
        return subprocess.run([sys.executable, '-m', 'health_rules', *map(str, args)],
                              cwd=ROOT, capture_output=True, text=True)

    def test_demo_writes_report_and_matches_stdout(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'nested/report.json'
            result = self.command(ROOT / 'data/cases.json', '--output', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text()), json.loads(result.stdout))
            self.assertEqual(len(json.loads(result.stdout)['results']), 6)

    def test_invalid_json_preserves_previous_report(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'bad.json', Path(directory) / 'report.json'
            source.write_text('{broken')
            output.write_text('previous report')
            result = self.command(source, '--output', output)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_text(), 'previous report')

    def test_input_and_rulebook_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            source, rules = Path(directory) / 'cases.json', Path(directory) / 'rules.json'
            source.write_bytes((ROOT / 'data/cases.json').read_bytes())
            rules.write_bytes(DEFAULT_RULES.read_bytes())
            for target in [source, rules]:
                with self.subTest(target=target):
                    before = target.read_bytes()
                    result = self.command(source, '--rules', rules, '--output', target)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(target.read_bytes(), before)
