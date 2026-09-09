"""Exact finite-table CSP enumeration for GDT892.

All variables take distinct integer values.  This module reads no files and
contains no linguistic, cipher, or plaintext assumptions.  Its deadline is an
absolute ``time.monotonic()`` value; an incomplete search is UNKNOWN_BUDGET.
"""

from __future__ import annotations

from collections import deque
import math
import time


class _DeadlineExceeded(Exception):
    pass


def _integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def solve_tables(tables, nvars, nvalues, deadline, accept=None):
    """Return every accepted injective assignment satisfying every table.

    ``tables`` contain distinct variable indices in ``vars`` and aligned rows
    of value IDs in ``rows``.  An empty-scope table containing ``()`` is true;
    a table with no rows is false.  With zero variables, the only possible
    assignment is ``()``.  Duplicate rows never create duplicate solutions.

    ``accept`` is called only on complete valid assignments.  Its exceptions
    propagate rather than being mistaken for rejection.  A callback cannot be
    preempted, but its completion is checked against the same deadline before
    its result is retained.  Timeout returns already retained solutions and
    UNKNOWN_BUDGET; their number does not establish uniqueness.
    """
    if not _integer(nvars) or nvars < 0:
        raise ValueError("nvars must be a nonnegative integer")
    if not _integer(nvalues) or nvalues < 0:
        raise ValueError("nvalues must be a nonnegative integer")
    if not isinstance(deadline, (int, float)) or math.isnan(deadline):
        raise ValueError("deadline must be an absolute monotonic time")
    if accept is not None and not callable(accept):
        raise ValueError("accept must be callable or None")

    began = time.monotonic()
    stats = {
        "tables": 0,
        "input_rows": 0,
        "unique_rows": 0,
        "duplicate_rows": 0,
        "noninjective_rows_removed": 0,
        "nodes": 0,
        "branches": 0,
        "table_revisions": 0,
        "table_rowset_reductions": 0,
        "domain_values_removed": 0,
        "singleton_rounds": 0,
        "matching_checks": 0,
        "matching_failures": 0,
        "constraint_conflicts": 0,
        "complete_assignments": 0,
        "callback_calls": 0,
        "callback_rejections": 0,
        "solutions_accepted": 0,
        "maximum_stack_size": 0,
    }
    solutions = []
    stage = "preparation"
    operations = 0

    def check(force=False):
        nonlocal operations
        operations += 1
        if (force or operations % 256 == 0) and time.monotonic() >= deadline:
            raise _DeadlineExceeded

    def finish(status):
        stats["elapsed_seconds"] = time.monotonic() - began
        stats["budget_stage"] = stage if status == "UNKNOWN_BUDGET" else None
        return {"status": status, "solutions": solutions, "stats": stats}

    try:
        check(True)
        scopes = []
        indexes = []
        initial_rows = []
        incident = [[] for _ in range(nvars)]
        for table in tables:
            check(True)
            try:
                scope = tuple(table["vars"])
                rows = table["rows"]
            except (KeyError, TypeError) as error:
                raise ValueError("Each table requires vars and rows") from error
            if any(not _integer(var) or not 0 <= var < nvars for var in scope):
                raise ValueError("Variable index outside the declared domain")
            if len(set(scope)) != len(scope):
                raise ValueError("A table scope must contain distinct variables")
            unique = set()
            for original_row in rows:
                check()
                row = tuple(original_row)
                stats["input_rows"] += 1
                if len(row) != len(scope):
                    raise ValueError("Table row width does not match its scope")
                if any(not _integer(value) or not 0 <= value < nvalues for value in row):
                    raise ValueError("Value index outside the declared domain")
                if row in unique:
                    stats["duplicate_rows"] += 1
                else:
                    unique.add(row)
            stats["unique_rows"] += len(unique)
            columns = [{} for _ in scope]
            row_count = 0
            for row in sorted(unique):
                check()
                # The global injection makes any repeated value within a
                # distinct-variable table row impossible before search.
                if len(set(row)) != len(row):
                    stats["noninjective_rows_removed"] += 1
                    continue
                row_bit = 1 << row_count
                row_count += 1
                for column, value in enumerate(row):
                    columns[column][value] = columns[column].get(value, 0) | row_bit
            table_id = len(scopes)
            scopes.append(scope)
            indexes.append([tuple((1 << value, row_bits)
                                  for value, row_bits in sorted(column.items()))
                            for column in columns])
            initial_rows.append((1 << row_count) - 1)
            for var in scope:
                incident[var].append(table_id)
        stats["tables"] = len(scopes)
        check(True)
        if nvars > nvalues or any(rows == 0 for rows in initial_rows):
            stats["constraint_conflicts"] += 1
            return finish("COMPLETE")

        def narrow(var, new_domain, domains, queue, queued):
            old_domain = domains[var]
            if new_domain == old_domain:
                return True
            stats["domain_values_removed"] += old_domain.bit_count() - new_domain.bit_count()
            domains[var] = new_domain
            if new_domain == 0:
                return False
            for table_id in incident[var]:
                if table_id not in queued:
                    queued.add(table_id)
                    queue.append(table_id)
            return True

        def singleton_closure(domains, queue, queued):
            changed = True
            while changed:
                check()
                stats["singleton_rounds"] += 1
                assigned = 0
                for domain in domains:
                    if domain == 0:
                        return False
                    if domain & (domain - 1) == 0:
                        if assigned & domain:
                            return False
                        assigned |= domain
                changed = False
                for var, domain in enumerate(domains):
                    if domain & (domain - 1):
                        new_domain = domain & ~assigned
                        if new_domain != domain:
                            changed = True
                            if not narrow(var, new_domain, domains, queue, queued):
                                return False
            return True

        def has_injective_matching(domains):
            """Hall feasibility by independent augmenting paths, not pruning."""
            stats["matching_checks"] += 1
            value_owner = [-1] * nvalues
            assigned_value = [-1] * nvars
            for start_var in sorted(range(nvars), key=lambda var: (domains[var].bit_count(), var)):
                check()
                queue = deque([start_var])
                reached_vars = {start_var}
                reached_values = 0
                parent = [-1] * nvalues
                free_value = None
                while queue and free_value is None:
                    var = queue.popleft()
                    choices = domains[var] & ~reached_values
                    while choices:
                        check()
                        bit = choices & -choices
                        choices ^= bit
                        value = bit.bit_length() - 1
                        reached_values |= bit
                        parent[value] = var
                        owner = value_owner[value]
                        if owner == -1:
                            free_value = value
                            break
                        if owner not in reached_vars:
                            reached_vars.add(owner)
                            queue.append(owner)
                if free_value is None:
                    stats["matching_failures"] += 1
                    return False
                value = free_value
                while value != -1:
                    var = parent[value]
                    previous = assigned_value[var]
                    assigned_value[var] = value
                    value_owner[value] = var
                    value = previous
            return True

        def propagate(domains, active_rows, dirty):
            queue = deque(dirty)
            queued = set(dirty)
            if not singleton_closure(domains, queue, queued):
                return False
            while queue:
                check(True)
                table_id = queue.popleft()
                queued.remove(table_id)
                stats["table_revisions"] += 1
                possible_rows = active_rows[table_id]
                scope = scopes[table_id]
                columns = indexes[table_id]
                for var, column in zip(scope, columns):
                    supported_rows = 0
                    for value_bit, row_bits in column:
                        check()
                        if domains[var] & value_bit:
                            supported_rows |= row_bits
                    possible_rows &= supported_rows
                    if not possible_rows:
                        return False
                if possible_rows != active_rows[table_id]:
                    stats["table_rowset_reductions"] += 1
                    active_rows[table_id] = possible_rows
                for var, column in zip(scope, columns):
                    supported_values = 0
                    for value_bit, row_bits in column:
                        check()
                        if possible_rows & row_bits:
                            supported_values |= value_bit
                    if not narrow(var, domains[var] & supported_values, domains, queue, queued):
                        return False
                if not singleton_closure(domains, queue, queued):
                    return False
            return has_injective_matching(domains)

        stage = "search"
        initial_domains = [(1 << nvalues) - 1 for _ in range(nvars)]
        stack = [(initial_domains, initial_rows, tuple(range(len(scopes))))]
        stats["maximum_stack_size"] = 1
        while stack:
            check(True)
            domains, active_rows, dirty = stack.pop()
            stats["nodes"] += 1
            if not propagate(domains, active_rows, dirty):
                stats["constraint_conflicts"] += 1
                continue
            undecided = [var for var, domain in enumerate(domains) if domain & (domain - 1)]
            if not undecided:
                mapping = tuple(domain.bit_length() - 1 for domain in domains)
                stats["complete_assignments"] += 1
                check(True)
                admitted = True
                if accept is not None:
                    stage = "accept_callback"
                    stats["callback_calls"] += 1
                    admitted = bool(accept(mapping))
                    check(True)
                    stage = "search"
                if admitted:
                    solutions.append(mapping)
                    stats["solutions_accepted"] += 1
                else:
                    stats["callback_rejections"] += 1
                continue
            var = min(undecided, key=lambda item: (domains[item].bit_count(), -len(incident[item]), item))
            choices = domains[var]
            children = []
            while choices:
                check()
                bit = choices & -choices
                choices ^= bit
                child_domains = domains.copy()
                child_domains[var] = bit
                children.append((child_domains, active_rows.copy(), tuple(incident[var])))
            stats["branches"] += len(children)
            # Stack reversal preserves ascending value order without selecting
            # or discarding any branch after the first valid assignment.
            stack.extend(reversed(children))
            stats["maximum_stack_size"] = max(stats["maximum_stack_size"], len(stack))
        check(True)
        return finish("COMPLETE")
    except _DeadlineExceeded:
        return finish("UNKNOWN_BUDGET")
