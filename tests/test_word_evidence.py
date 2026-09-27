"""Behavioral guards: explicit rules cannot silently become word meanings."""
import copy
import unittest

from tools.word_evidence import evaluate_rule, validate_contract, selected_rows


def occurrence(edition, locus, index, total, token='daiin', previous=None, following=None):
    return {'source_group_id': f'{edition}|{locus}|G{index:03}',
            'edition': edition, 'page': locus.split('.')[0], 'locus': locus,
            'kind': 'P', 'source_group_index': index, 'source_group_count': total,
            'ivtff_group_raw': token, 'previous_literal': previous,
            'next_literal': following,
            'position': 'single' if total == 1 else 'start' if index == 1 else 'end' if index == total else 'middle'}


def rule(kind, **kwargs):
    return dict(id='fixture', form='daiin', rule=kind, strength='necessary',
                basis='Synthetic necessary rule, not an inferred Voynich grammar.',
                assumptions=['A physical line is the stipulated boundary for this fixture.'], **kwargs)


class ConditionalRuleTests(unittest.TestCase):
    def test_full_scope_and_bounded_examples_are_distinct(self):
        rows = [occurrence('ZL3b', f'f2r.{i}', 1, 2, following='daiin') for i in range(1, 13)]
        result = evaluate_rule(rule('forbidden_next', values=['daiin']), rows, limit=2)
        self.assertEqual(result['status'], 'CONDITIONAL_CONTRADICTION')
        self.assertEqual(result['by_reader']['ZL3b']['violating_occurrences'], 12)
        self.assertEqual(len(result['by_reader']['ZL3b']['counterexamples']), 2)

    def test_alternate_readings_never_form_three_occurrences_of_one_line(self):
        rows = [occurrence(e, 'f2r.1', 1, 2) for e in ['ZL3b', 'IT2a', 'RF1b']]
        result = evaluate_rule(rule('max_per_locus', maximum=1), rows)
        self.assertEqual(result['status'], 'COMPATIBLE_IN_DECLARED_SCOPE')
        self.assertEqual(len(result['by_reader']), 3)

    def test_counterexample_in_single_reader_is_not_majority_voted_away(self):
        rows = [occurrence('ZL3b', 'f2r.1', 2, 2), occurrence('IT2a', 'f2r.1', 1, 2)]
        result = evaluate_rule(rule('allowed_positions', values=['end']), rows)
        self.assertEqual(result['status'], 'CONDITIONAL_CONTRADICTION')
        self.assertEqual(result['by_reader']['ZL3b']['violating_occurrences'], 0)
        self.assertEqual(result['by_reader']['IT2a']['violating_occurrences'], 1)

    def test_missing_data_cannot_vacuously_pass(self):
        self.assertEqual(evaluate_rule(rule('allowed_positions', values=['end']), [])['status'], 'NO_CAPACITY')

    def test_soft_prior_mismatch_is_not_hard_grammar_exclusion(self):
        prediction = rule('max_per_locus', maximum=1)
        prediction['strength'] = 'expectation'
        rows = [occurrence('ZL3b', 'f2r.1', i, 2) for i in [1, 2]]
        self.assertEqual(evaluate_rule(prediction, rows)['status'], 'EXPECTATION_MISMATCH')

    def test_raw_next_form_not_substring(self):
        rows = [occurrence('ZL3b', 'f2r.1', 1, 2, following='qodaiin')]
        self.assertEqual(evaluate_rule(rule('forbidden_next', values=['daiin']), rows)['status'], 'COMPATIBLE_IN_DECLARED_SCOPE')

    def test_line_boundary_is_preserved_not_bridged_by_required_neighbor(self):
        rows = [occurrence('ZL3b', 'f2r.1', 2, 2)]
        result = evaluate_rule(rule('required_next', values=['chol']), rows)
        self.assertEqual(result['status'], 'CONDITIONAL_CONTRADICTION')
        self.assertIn('physical line', result['assumptions'][0])

    def test_scope_is_explicit(self):
        rows = [occurrence('ZL3b', 'f2r.1', 1, 2), occurrence('IT2a', 'f3r.1', 1, 2)]
        self.assertEqual(selected_rows(rows, {'pages': ['f2r'], 'editions': ['ZL3b']}), rows[:1])


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = {'schema_version': 1, 'id': 'fixture',
                         'assignments': [{'form': 'daiin', 'meaning': 'Winter'}],
                         'predictions': []}

    def test_free_meaning_is_accepted_as_unpredicted_hypothesis(self):
        validate_contract(self.contract)
        alternative = copy.deepcopy(self.contract)
        alternative['assignments'][0]['meaning'] = 'Sommer'
        validate_contract(alternative)  # spelling the meaning never supplies a rule

    def test_sealed_scope_fails(self):
        self.contract['scope'] = {'pages': ['f84r']}
        with self.assertRaisesRegex(ValueError, 'sealed'):
            validate_contract(self.contract)

    def test_rule_requires_explicit_assumptions(self):
        self.contract['predictions'] = [rule('max_per_locus', maximum=1)]
        self.contract['predictions'][0]['assumptions'] = []
        with self.assertRaisesRegex(ValueError, 'assumptions'):
            validate_contract(self.contract)

    def test_unknown_rule_field_fails_closed(self):
        self.contract['predictions'] = [rule('max_per_locus', maximum=1, exemptions=['f2r'])]
        with self.assertRaisesRegex(ValueError, 'unknown prediction field'):
            validate_contract(self.contract)


if __name__ == '__main__':
    unittest.main()
