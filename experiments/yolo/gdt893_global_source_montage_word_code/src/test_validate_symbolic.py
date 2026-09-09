import copy
import unittest
import validate_symbolic as v


class SymbolicCertificateTests(unittest.TestCase):
    def fixture(self):
        pool = [(0, 2, {1: 2, 3: 4}), (0, 2, {1: 2, 3: 5})]
        independent = {'status': 'COMPLETE', 'best_weight': 2, 'optimal_solutions': [[0], [1]]}
        primary = {'status': 'COMPLETE', 'best_weight': 2, 'oneoptimum': [0],
                   'forced_candidate_indices': [], 'forced_word_values': [[1, 2]],
                   'stats': {'best_weight_is_proven': True, 'universal_projection_is_complete': True},
                   'query_certificates': [
                       {'kind': 'FORBID_CANDIDATE', 'candidate_index': 0, 'target_weight': 2,
                        'outcome': 'FOUND_WITNESS', 'witness': [1]},
                       {'kind': 'FORBID_WORD_PAIR', 'word_pair': [1, 2], 'target_weight': 2,
                        'outcome': 'EXHAUSTIVE_UNSAT', 'witness': None}]}
        return pool, primary, independent

    def test_correct_witness_and_universal_pair(self):
        self.assertEqual(v.evaluate(*self.fixture())['status'], 'PASS')

    def test_false_unsat_rejected(self):
        pool, primary, independent = self.fixture()
        primary['query_certificates'][0].update(outcome='EXHAUSTIVE_UNSAT', witness=None)
        with self.assertRaises(ValueError):
            v.evaluate(pool, primary, independent)

    def test_failed_pair_exclusion_rejected(self):
        pool, primary, independent = self.fixture()
        primary['query_certificates'][1].update(outcome='FOUND_WITNESS', witness=[1])
        with self.assertRaises(ValueError):
            v.evaluate(pool, primary, independent)

    def test_unknown_is_not_pass(self):
        pool, primary, independent = self.fixture()
        primary.update(status='UNKNOWN_BUDGET', forced_candidate_indices=None, forced_word_values=None)
        primary['stats']['universal_projection_is_complete'] = False
        primary['query_certificates'][1].update(outcome='UNKNOWN_BUDGET')
        self.assertEqual(v.evaluate(pool, primary, independent)['status'], 'UNKNOWN_BUDGET')
        primary['forced_word_values'] = [[1, 2]]
        with self.assertRaises(ValueError):
            v.evaluate(pool, primary, independent)

    def test_incomplete_reference_cannot_pass(self):
        pool, primary, _ = self.fixture()
        self.assertEqual(v.evaluate(pool, primary, {'status': 'UNKNOWN_BUDGET'})['status'], 'UNKNOWN_BUDGET')


if __name__ == '__main__':
    unittest.main()
