#!/usr/bin/env python3
"""Source-only compiler; never reads a manuscript target paragraph."""
import collections
import copy
import hashlib
import itertools
import json
from pathlib import Path
from model import WRITERS, compile_trees

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
B = ROOT / 'research_registry/work_batches/ten_hours_20260915'


def main():
    draft = json.loads((B / 'SMARAGDINA_CONTENT_TREES_DRAFT_20260920.json').read_text())
    witness = json.loads((B / 'SMARAGDINA_MEDIEVAL_SOURCE_COLLATION_20260920.json').read_text())
    rows = copy.deepcopy(draft['clauses'])
    row = {r['id']: r for r in rows}
    row['T03']['tree'][2][1] = 'UNSPECIFIED_AGENT'
    row['T03']['content'] = 'The two reciprocal comparisons have the purpose of penetrating the wonders of one thing; the purpose agent is not identified.'
    row['T04']['tree'] = ['AS', ['BY', ['PAST', ['ORIGIN_FROM', ['ALL', 'THING'], 'INDEFINITE_ONE']], ['MEDITATION_OF', 'INDEFINITE_ONE']]]
    row['T04']['content'] = 'As all things were from one through the meditation/thought of one; identity of these two indefinite referents is not imposed.'
    row['T05']['tree'] = ['ALSO', ['AS', ['BY', ['PAST', ['BORN_FROM', ['ALL', 'THING'], ['THIS_SPECIFIED', ['ONE_OF', 'THING']]]], 'APTATION']]]
    row['T05']['content'] = 'And as all things were born from this one thing through aptation; the overworked group is assumed deleted in this branch.'
    row['T07']['tree'] = ['PAST', row['T07']['tree']]
    row['T09']['tree'] = ['IDENTICAL', ['FATHER_OF', ['OF', ['ALL', 'THELESM'], ['WHOLE', 'WORLD']]], 'THIS']
    row['T09']['content'] = 'This is the father of all thelesm of the whole world; THIS is demonstrative, not a named place.'
    row['T10']['tree'] = ['IF', ['PERFECT', ['TURN_INTO', 'TRANSFORMATION_SUBJECT', 'EARTH']], ['COMPLETE', ['FORCE_OF', 'TOPIC']]]
    row['T11']['tree'] = ['MANNER', ['FUTURE', ['AND', ['SEPARATE', 'YOU', 'EARTH', 'FIRE'], ['SEPARATE', 'YOU', ['SUBTLE', 'THING'], ['DENSE', 'THING']]]], ['AND', 'GENTLE', ['WITH', ['GREAT', 'SKILL']]]]
    row['T14']['tree'] = ['RECEIVE', 'TOPIC', ['FORCE_OF', ['AND', ['PLURAL', 'UPPER'], ['PLURAL', 'LOWER']]]]
    row['T14']['content'] = 'It receives one force jointly qualified by upper and lower plural domains; no distributive duplication of FORCE_OF.'
    row['T15']['tree'] = ['THUS', ['GLORY_TENSE', ['HAVE', 'GLORY_SUBJECT', ['GLORY_OF', ['WHOLE', 'WORLD']]]]]
    row['T16']['tree'] = ['ALSO', row['T16']['tree']]
    reason = ['FUTURE', ['AND', ['OVERCOME', 'STRENGTH_SUBJECT', ['EVERY', ['SUBTLE', 'THING']]], ['PENETRATE', 'STRENGTH_SUBJECT', ['EVERY', ['SOLID', 'THING']]]]]
    row['T17']['tree'] = ['BECAUSE', row['T17']['tree'], reason]
    row['T17']['content'] = 'This is the strong strength of the strength of the whole world, because its bearer will overcome every subtle thing and penetrate every solid thing. The nested emphatic genitive is an explicit interpretation.'
    row['T17']['covers_draft'] = ['T17', 'T18']
    rows = [r for r in rows if r['id'] != 'T18']
    row['T19']['tree'] = ['AS', ['THEREFORE', ['PAST', ['CREATED', 'WORLD']]]]
    row['T20']['tree'] = ['AND', ['FROM_THIS', ['FUTURE', ['EXIST', ['PLURAL', ['WONDROUS', 'APTATION']]]]], ['IDENTICAL', ['METHOD_OF', 'THOSE_APTATIONS'], 'THIS']]
    row['T20']['content'] = 'From this there will be wondrous aptations, whose manner is this; the source of the consequence and both deictic scopes remain contextual.'
    row['T21']['tree'][1][1] = ['PERFECT', row['T21']['tree'][1][1]]
    row['T22']['tree'] = ['COMPLETE', ['ABOUT', ['PAST', ['SAY', 'I', 'THIS_TEXT']], ['OPERATION_OF', ['AND', 'SUN', 'MOON']]]]
    coverage = {'T01': ['T01', 'T02'], 'T02': ['T03'], 'T03': ['T04'], 'T04': ['T05'],
                'T05': ['T06'], 'T06': ['T07'], 'T07': ['T08'], 'T08': ['T09'],
                'T09': ['T10'], 'T10': ['T11'], 'T11': ['T12', 'T13'], 'T12': ['T14'],
                'T13': ['T15'], 'T14': ['T16'], 'T15': ['T17'], 'T16': ['T19'],
                'T17': ['T20'], 'T18': ['T21'], 'T19': ['T22']}
    variants = {}
    for referent, glory in itertools.product(('TOPIC', 'VIS'), ('TOPIC_PAST', 'TOPIC_FUTURE', 'YOU_FUTURE')):
        clauses = copy.deepcopy(rows)
        indexed = {r['id']: r for r in clauses}
        subject = 'TOPIC' if referent == 'TOPIC' else ['FORCE_OF', 'TOPIC']
        indexed['T10']['tree'][1][1][1] = subject
        indexed['T10']['content'] = f'The force of the topic is complete if {"the topic" if referent == "TOPIC" else "that force"} has been turned into earth; this is a condition, not a new command.'
        whom, tense = glory.split('_')
        indexed['T15']['tree'][1][0] = tense
        indexed['T15']['tree'][1][1][1] = whom
        indexed['T15']['content'] = f'Thus {"the topic" if whom == "TOPIC" else "you"} {"had" if tense == "PAST" else "will have"} the glory of the whole world.'
        name = f'VERSA_{referent}__GLORY_{glory}'
        streams = {w: compile_trees(clauses, w) for w in WRITERS}
        counts = collections.Counter(e['root'] for e in streams[WRITERS[0]])
        variants[name] = dict(clauses=clauses, streams=streams,
                             source_support='main preferred habuit or plausible habebit' if whom == 'TOPIC' else 'second-person commentary interpretation; not silently substituted into main native reading',
                             counts=dict(counts), forms=sum(counts.values()), root_types=len(counts), singleton_types=sum(v == 1 for v in counts.values()))
    files = ['SMARAGDINA_CONTENT_TREES_DRAFT_20260920.json', 'SMARAGDINA_MEDIEVAL_SOURCE_COLLATION_20260920.json', 'SMARAGDINA_CONTENT_TREE_SOURCE_AUDIT_20260920.md']
    source = dict(schema='complete-tabula-role-frames-v1', status='EXPLICIT_EXPLORATORY_MEANING_HYPOTHESES',
        source_files={str((B / f).relative_to(ROOT)): hashlib.sha256((B / f).read_bytes()).hexdigest() for f in files},
        normalized_lines=witness['normalized_lines'], source_uncertainties=witness['uncertainty_apparatus'],
        coverage=coverage, variants=variants, writers=list(WRITERS), infix=['AND', 'IF', 'PURPOSE', 'BECAUSE'],
        input_paragraphs='experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json',
        limits=dict(workers=24, solver_seconds=30, projection_seconds=1, external_case_seconds=100, global_solver_seconds=2400),
        interpretation_policy=[
          'Every major source assertion and temporal/number feature has an explicit conceptual representation; the 19-source-unit coverage is exhaustive. This is not a literal Latin token compiler.',
          'TOPIC coindexes parental possessors, carried object, nurse possessor, ascent/descent and receiver as one hypothetical discourse subject, without conserved mass, named substance or literal astronomical assertion.',
          'INDEFINITE_ONE is an indefinite singular expression. Each occurrence introduces a separately scoped unspecified referent; root equality does not impose referent equality. It is not silently equal to TOPIC.',
          'UNSPECIFIED_AGENT leaves the purpose agent existentially unspecified, with no identity to TOPIC or YOU. Its written realization is part of this explicit semantic notation hypothesis.',
          'UPPER/LOWER name qualitative domains, not constant individual objects. PLURAL preserves the later plural construction. Neither is equated to HEAVEN/EARTH.',
          'THIS is a context-sensitive demonstrative expression, not a shared physical location. THIS_SPECIFIED applies a demonstrative determination to a described term. FROM_THIS is a consequence/origin link with its own unresolved antecedent scope.',
          'STRENGTH_SUBJECT is the bearer of the preceding fortitudo claim; it is not silently identical to the earlier vis. THOSE_APTATIONS refers to the newly mentioned plural aptations.',
          'Nested STRENGTH_OF is one explicit genitive interpretation, not two physically measured forces. THELESM remains the source term, with secret/treasure as commentary-supported gloss rivals; these lexical nuances yield the same equations.',
          'THIS_TEXT links the initial speech and final about-operation saying as one discourse span. PHILOSOPHER, I and HERMES are distinct expressions; speaker identity is a declared reading assumption, not a string equality constraint.',
          'The overworked group after una is assumed deleted; corrected sicut, meditatione, aptatione, penetranda, quia, ergo and modus follow the marked normalized readings. Other active-letter or lexical readings are outside this finite source branch, not refuted.',
          'Body boundary excludes the separate incompletely read rubric. The complete Philosophi-dicit frame and Sun-and-Moon closure remain. No clause-sized residual strings, zero argument omissions, BEGIN_RECORD or generic ASSERT atoms are introduced.',
          'SOURCE token completeness does not establish uniquely recoverable meaning; contextual references, singleton roots, multiple code factorizations and the finite source-reading choices remain explicit.'
        ])
    (E / 'src/SOURCE.json').write_text(json.dumps(source, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: {z: v[z] for z in ('forms', 'root_types', 'singleton_types')} for k, v in variants.items()}, indent=2))


if __name__ == '__main__':
    main()
