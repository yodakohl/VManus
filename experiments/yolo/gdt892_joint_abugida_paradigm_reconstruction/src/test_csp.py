"""Independent brute-force checks of the exact generic table solver."""

import importlib.util
from itertools import permutations, product
from pathlib import Path
import random
import time
import unittest
from unittest.mock import patch


_SPEC = importlib.util.spec_from_file_location("gdt892_csp", Path(__file__).with_name("csp.py"))
csp = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(csp)


def brute(tables, nvars, nvalues, accept=None):
    return {mapping for mapping in permutations(range(nvalues), nvars)
            if all(tuple(mapping[var] for var in table["vars"]) in set(map(tuple, table["rows"]))
                   for table in tables)
            and (accept is None or accept(mapping))}


class CSPTests(unittest.TestCase):
    def compare(self, tables, nvars, nvalues, accept=None):
        result = csp.solve_tables(tables, nvars, nvalues, time.monotonic() + 20, accept)
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(set(result["solutions"]), brute(tables, nvars, nvalues, accept))
        self.assertEqual(len(result["solutions"]), len(set(result["solutions"])))
        return result

    def test_unconstrained_injection_is_fully_enumerated(self):
        result = self.compare([], 4, 5)
        self.assertEqual(len(result["solutions"]), 120)

    def test_zero_variables_and_zero_values(self):
        self.assertEqual(self.compare([], 0, 0)["solutions"], [()])
        self.assertEqual(self.compare([], 0, 4)["solutions"], [()])
        self.assertEqual(self.compare([], 1, 0)["solutions"], [])
        self.assertEqual(self.compare([], 3, 2)["solutions"], [])

    def test_empty_scope_true_and_false_tables(self):
        self.assertEqual(self.compare([{"vars": (), "rows": [(), ()]}], 0, 0)["solutions"], [()])
        self.assertEqual(self.compare([{"vars": (), "rows": []}], 0, 0)["solutions"], [])
        self.compare([{"vars": (), "rows": [()]}], 2, 3)
        self.compare([{"vars": (), "rows": []}], 2, 3)

    def test_duplicate_rows_and_noninjective_rows(self):
        tables = [{"vars": (1, 0), "rows": [(0, 1), (0, 1), (1, 0), (2, 2), (2, 2)]}]
        result = self.compare(tables, 2, 3)
        self.assertEqual(result["stats"]["duplicate_rows"], 2)
        self.assertEqual(result["stats"]["noninjective_rows_removed"], 1)

    def test_overlapping_tables_preserve_joint_support(self):
        tables = [{"vars": (0, 1), "rows": [(0, 1), (1, 0), (2, 3)]},
                  {"vars": (1, 2), "rows": [(1, 2), (0, 3), (3, 0)]},
                  {"vars": (0, 2), "rows": [(0, 2), (1, 2), (2, 0)]}]
        self.compare(tables, 3, 4)

    def test_hall_conflict_without_singletons(self):
        tables = [{"vars": (var,), "rows": [(0,), (1,)]} for var in range(3)]
        result = self.compare(tables, 3, 3)
        self.assertEqual(result["solutions"], [])
        self.assertGreater(result["stats"]["matching_failures"], 0)

    def test_matching_requires_reassignment_along_augmenting_path(self):
        tables = [{"vars": (0,), "rows": [(0,), (1,)]},
                  {"vars": (1,), "rows": [(0,), (2,)]},
                  {"vars": (2,), "rows": [(0,), (2,)]}]
        self.assertEqual(len(self.compare(tables, 3, 3)["solutions"]), 2)

    def test_accept_callback_is_final_and_not_first_solution_selection(self):
        called = []
        def accept(mapping):
            self.assertEqual(len(mapping), 3)
            self.assertEqual(len(set(mapping)), 3)
            called.append(mapping)
            return mapping[0] == 2
        result = csp.solve_tables([], 3, 4, time.monotonic() + 20, accept)
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(len(called), 24)
        self.assertEqual(len(result["solutions"]), 6)
        self.assertEqual(set(result["solutions"]), brute([], 3, 4, lambda m: m[0] == 2))

    def test_zero_variable_callback_and_exception_propagation(self):
        self.assertEqual(self.compare([], 0, 0, lambda mapping: False)["solutions"], [])
        def broken(mapping):
            raise RuntimeError("invented callback failure")
        with self.assertRaisesRegex(RuntimeError, "invented callback failure"):
            csp.solve_tables([], 0, 0, time.monotonic() + 20, broken)

    def test_expired_deadline_never_claims_complete(self):
        result = csp.solve_tables([], 0, 0, time.monotonic() - 1)
        self.assertEqual(result["status"], "UNKNOWN_BUDGET")
        self.assertEqual(result["solutions"], [])

    def test_timeout_in_callback_keeps_only_predeadline_solutions(self):
        clock = [0.0]
        calls = []
        def accept(mapping):
            calls.append(mapping)
            if len(calls) == 2:
                clock[0] = 2.0
            return True
        with patch.object(csp.time, "monotonic", side_effect=lambda: clock[0]):
            result = csp.solve_tables([], 2, 3, 1.0, accept)
        self.assertEqual(result["status"], "UNKNOWN_BUDGET")
        self.assertEqual(len(result["solutions"]), 1)
        self.assertEqual(result["stats"]["budget_stage"], "accept_callback")

    def test_timeout_during_table_preparation(self):
        clock = [0.0]
        def rows():
            for index in range(1000):
                if index == 400:
                    clock[0] = 2.0
                yield (index % 3,)
        with patch.object(csp.time, "monotonic", side_effect=lambda: clock[0]):
            result = csp.solve_tables([{"vars": (0,), "rows": rows()}], 1, 3, 1.0)
        self.assertEqual(result["status"], "UNKNOWN_BUDGET")
        self.assertEqual(result["stats"]["budget_stage"], "preparation")

    def test_all_binary_two_variable_table_relations(self):
        possible = list(product(range(2), repeat=2))
        for mask in range(1 << len(possible)):
            rows = [row for index, row in enumerate(possible) if mask & (1 << index)]
            self.compare([{"vars": (1, 0), "rows": rows}], 2, 2)

    def test_random_small_tables_against_complete_permutation_oracle(self):
        rng = random.Random(892103)
        for _ in range(160):
            nvars, nvalues = rng.randrange(5), rng.randrange(1, 6)
            tables = []
            for _ in range(rng.randrange(5)):
                width = rng.randrange(min(3, nvars) + 1)
                scope = tuple(rng.sample(range(nvars), width))
                rows = [row for row in product(range(nvalues), repeat=width) if rng.random() < .3]
                if rows:
                    rows.extend(rows[:2])
                tables.append({"vars": scope, "rows": rows})
            self.compare(tables, nvars, nvalues)

    def test_malformed_inputs_are_errors_not_scientific_rejections(self):
        fixtures = [
            ([{"vars": (0, 0), "rows": [(0, 1)]}], 1, 2),
            ([{"vars": (1,), "rows": [(0,)]}], 1, 2),
            ([{"vars": (0,), "rows": [(2,)]}], 1, 2),
            ([{"vars": (0,), "rows": [(0, 1)]}], 1, 2),
            ([], -1, 2),
            ([], 1, -1),
        ]
        for tables, nvars, nvalues in fixtures:
            with self.subTest(tables=tables, nvars=nvars, nvalues=nvalues):
                with self.assertRaises(ValueError):
                    csp.solve_tables(tables, nvars, nvalues, time.monotonic() + 20)


if __name__ == "__main__":
    unittest.main()
