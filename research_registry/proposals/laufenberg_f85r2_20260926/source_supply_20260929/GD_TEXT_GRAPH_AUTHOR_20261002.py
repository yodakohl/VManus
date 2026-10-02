"""Finite image-blind C0 continuation. Only four authorized inputs are read.

No general parser, decoder, complete reading, or manuscript confirmation.
The constructor return, rather than a second spelling-derived register, is
passed directly to the later consumer. run() here never calls parent's run().
"""
from pathlib import Path
import copy
import csv
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
STEM = 'GD_TEXT_GRAPH_AUTHOR_20261002'
INPUTS = [
    'GD_TEXT_GRAPH_AUTHOR_PACKET_20261002.tsv',
    'GD_TEXT_GRAPH_PARENT_INPUT_20261002.json',
    'GD_MOTION_SHARED_GRADE_AUTHOR_20261002.py',
    'GD_TEXT_GRAPH_AUTHOR_PRIORS_20261002.json',
]
spec = importlib.util.spec_from_file_location('frozen_motion_definitions', P / INPUTS[2])
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)  # Definitions only; frozen.run is never called.
A, And = frozen.A, frozen.And
WORLD = 'W_actual'

PRIMITIVES = {
    'ch': {'value': 'RECEPTACLE noun', 'cost': 1,
           'scope': 'CH in OTCHDY/CHEOL/CHDAL only; not a universal CH gloss.'},
    'e_CH': {'value': 'proper-part construction: E_CH(holder, outlet) returns PROPER_PART(outlet, holder)',
             'cost': 1, 'scope': 'Distinct paid scoped homonym of other inherited E uses; no grade change.'},
    'ed': {'value': 'Finite destination frame: root + ED + location gives actual event and GOAL(event, location)',
           'cost': 1, 'scope': 'SH/ED/AL only; no universal EDY deletion or new motion grade.'},
    'dal': {'value': 'PORTION relational material noun; PORTION_OF(new portion, written source)',
            'cost': 1, 'scope': 'DAL/CHDAL/SAROLDAL only. No purity negation or count.'},
    'for_material': {'value': 'FOR_MATERIAL(receptacle, portion)', 'cost': 1,
                     'scope': 'The CH/DAL assembly; suitability/intended holding, not actual containment.'},
}
ASSEMBLIES = {
    'otchdy': ['ot', 'ch', 'dy'], 'shedal': ['sh', 'ed', 'al'],
    'dal': ['dal'], 'cheol': ['ch', 'e', 'ol'], 'chdal': ['ch', 'dal'],
    'ol': ['ol'], 'chey': ['chey'], 'olsaiin': ['ol', 'saiin'],
    'saroldal': ['sar', 'ol', 'dal'],
}
COSTS = [
    {'id': 'P01', 'kind': 'new semantic primitive', 'units': 1, 'rule': PRIMITIVES['ch']['value']},
    {'id': 'P02', 'kind': 'new semantic primitive', 'units': 1, 'rule': PRIMITIVES['e_CH']['value']},
    {'id': 'P03', 'kind': 'new finite frame', 'units': 1, 'rule': PRIMITIVES['ed']['value']},
    {'id': 'P04', 'kind': 'new semantic primitive', 'units': 1, 'rule': PRIMITIVES['dal']['value']},
    {'id': 'P05', 'kind': 'new semantic relation', 'units': 1, 'rule': PRIMITIVES['for_material']['value']},
    {'id': 'H01', 'kind': 'scoped homonym', 'units': 1,
     'rule': 'E_CH proper-part differs from E_QOK grade and E_SH capability. No universal E semantics.'},
    {'id': 'A01', 'kind': 'semantic alias', 'units': 1,
     'rule': 'DAL portion overlaps inherited exact QOTEEDY portion; spelling is not normalized.'},
    {'id': 'A02', 'kind': 'finite-frame semantic overlap', 'units': 1,
     'rule': 'ED and EDY both assert actuality, but ED additionally accepts a written location operand. No formal deletion rule.'},
    {'id': 'G01', 'kind': 'cross-record identity policy', 'units': 1,
     'rule': 'Import only P4 actual returned/register references C/O/L into this local continuation; P4 R/P6 and doses unused. References retain C/O/L, not new copies.'},
    {'id': 'G02', 'kind': 'word-order/frame convention', 'units': 1,
     'rule': 'In Q1, OTCHDY and SHEDAL address one event E_Q1 in I_Q1, with L as patient. This is one manual span, not line syntax.'},
    {'id': 'G03', 'kind': 'reference-closure type extension', 'units': 1,
     'rule': 'DY may close a CH receptacle location reference in OTCHDY; inherited OL/QO uses unchanged.'},
    {'id': 'G04', 'kind': 'forward binding', 'units': 1,
     'rule': 'OTCHDY receptacle slot remains pending until the actual Q1 CHEOL constructor return; then substitute its holder. No holder seeded before constructor.'},
    {'id': 'G05', 'kind': 'context source default', 'units': 1,
     'rule': 'Bare DAL introduces portion D_Q1 of the imported written case material L. No dose identity or numerical amount.'},
    {'id': 'G06', 'kind': 'modifier attachment', 'units': 1,
     'rule': 'Inherited LOL with-liquid modifies E_Q1 and uses imported L; CHE(D)Y PURE modifies D_Q1 at T_Q1_final.'},
    {'id': 'G07', 'kind': 'within-record identity policy', 'units': 1,
     'rule': 'CHDAL reads the holder from Q1 CHEOL and the portion from DAL; it creates neither a second holder nor a new portion.'},
    {'id': 'G08', 'kind': 'cross-record anaphora/producer-consumer', 'units': 1,
     'rule': 'Q2 CHEOL reads Q1 CHEOL actual immutable relation return through an explicitly authored discourse port. No lookup by raw spelling and no duplicate register seed.'},
    {'id': 'G09', 'kind': 'bare noun/reference assembly', 'units': 1,
     'rule': 'Bare OL is nominal mention of imported outlet O; bare CHEY nominal mention of imported conduit C. No unstated event/edge.'},
    {'id': 'G10', 'kind': 'operator pending state', 'units': 1,
     'rule': 'Inherited DAIN opens Series_Q2 for successive actual event mentions; none is supplied in this assigned Q2 fragment. Do not convert nouns to events.'},
    {'id': 'G11', 'kind': 'caption frame/default', 'units': 1,
     'rule': 'OLS(A)IIN licenses a nominal temporal frame: outlet O in a phase subsequent to I_Q1. Caption phase J_CAP46 is authored, not an actual event.'},
    {'id': 'G12', 'kind': 'caption noun-chain assembly', 'units': 1,
     'rule': 'SAR/OL/DAL licenses source/location/head order: portion D_CAP50 of batch B_CAP50, at outlet O. These are distinct discourse witnesses, with no assertion of physical distinctness or identity with L/D_Q1.'},
    {'id': 'G13', 'kind': 'description-time convention', 'units': 1,
     'rule': 'T_Q1_final follows I_Q1. PURE at that description time does not assert purity during the entire dispensing event.'},
    {'id': 'G14', 'kind': 'caption source-type default', 'units': 1,
     'rule': 'SAR batch in caption50 is a material batch, supplying the material-source type required by DAL. No source identity with the P4 case liquid is asserted.'},
]
COSTS += [{'id': 'L_' + raw, 'kind': 'exact ordered assembly license', 'units': 1,
           'rule': raw + ' = ' + ' + '.join(parts)} for raw, parts in ASSEMBLIES.items()]

UNRESOLVED = {
    'qokchdy': 'QOK/CH/DY is a possible surface split. Frozen QOK finite/capability frames require EDY/EY (or Y intention); DY is reference closure. No chosen new QOK/CH finite versus nominal frame. This is unresolved, not impossible.',
    'aiin': 'No frozen AIIN meaning. Very frequent general form; do not equate with IRN/II remainder, quantity one, liquid, or an omitted copula.',
    'sol': 'S/OL split would place FINAL event operator before an outlet reference; inherited S needs an event/phase expression. No chosen nominal temporal extension or HERE alias.',
    'daiiin': 'Not DAIN or DAIIN. No numerical I ladder or ordered-series semantic alias licensed.',
    'solkeey': 'No LK EY frame licensed. SOL/K/E/EY and S/OLK/E/EY both require new stems/frames. No chosen whole value.',
    'qekey': 'QE/KEY or Q/EK/EY inventory absent. Do not repair to QOKEY or QOKEEY.',
    'raly': 'R/AL/Y would require a new R root and a new use of Y with outlet noun; frozen Y is FLOW intention. No chosen frame.',
    'solchkal': 'SOL/CHK/AL or S/OL/CHK/AL requires unassigned CHK and SOL conventions. AL may be an outlet trace, but no clause value follows.',
    'qotar': 'A receiver noun is plausible beside frozen QOTARY of-receiver and QOTAL into-receiver. No segmentation or nominal residual is selected; do not silently strip Y or AL.',
    'daiin': 'Frequent broad form could be a discourse operator. DAIN series alias would be a new paid decision, not an extra-I fact; none selected.',
    'ldalor': 'L/DAL/OR would need a new L material-reference homonym and OR relation. Frozen L links matching FLOW intention, not portion noun. No chosen extension.',
    'rtain': 'R/TAIN requires unassigned parts and syntax. No medicine/receiver value borrowed from neighboring forms.',
    'r': 'RF raw group R is preserved separately; no automatic merger with TAIN or guessed meaning.',
    'tain': 'RF raw group TAIN is preserved after its uncertain small space; no automatic RTAIN reconstruction.',
    'cthol': 'CTH/OL has an outlet-reference trace, but CTH is unknown. Not merged with CTHAL.',
    'cthal': 'CTH/AL has an outlet-noun trace, but CTH is unknown. Not merged with CTHOL.',
    'cth@221;l': 'RF raw entity uncertainty remains unresolved; neither CTHAL nor CTHOL is silently chosen.',
    'cheal': 'RF alternative to CHEOL is not a typo. CH/E/AL differs from CH/E/OL and requires an additional assembly/reference policy; none selected.',
    'chtorol': 'CH/T/OR/OL would require OR and a new T relation; frozen T binds FLOW intentions to goals. No chosen caption meaning.',
    'sasoldal': 'ZL SA/SOL/DAL does not equal IT SAR/OL/DAL. SA topic operator does not supply SOL meaning. Caption remains unresolved.',
    's@221;roldal': 'RF uncertain entity prevents selecting SAR. Preserve raw caption, with no silent IT replacement.',
    'darolsy': 'DAR/OL/S/Y needs DAR and new nominal uses of FINAL/INTENTION. Inherited DAROR residue cannot be truncated into a licensed root. No chosen caption meaning.',
}

def new_cheol(holder, outlet, source_id):
    """CH nominal feeds E_CH; OL supplies the inherited outlet operand."""
    relation = A('PROPER_PART', WORLD, outlet, holder)
    return {'type': 'ReceptacleOutletRelation', 'holder': holder, 'outlet': outlet,
            'relation': relation, 'noun_fact': A('RECEPTACLE', WORLD, holder),
            'producer': source_id, 'assembly': ['ch', 'e', 'ol']}

def consume_cheol(actual_return, consumer_source_id):
    """Read the actual return. No holder/outlet exists in a consumer context."""
    if actual_return is None:
        raise ValueError('Missing actual CHEOL producer return')
    if actual_return['type'] != 'ReceptacleOutletRelation':
        raise ValueError('Wrong producer payload type')
    return {'producer': actual_return['producer'], 'consumer': consumer_source_id,
            'holder_read': actual_return['holder'], 'outlet_read': actual_return['outlet'],
            'returned_predicates': And(copy.deepcopy(actual_return['noun_fact']),
                                       copy.deepcopy(actual_return['relation']))}

def execute(packet, parent_refs, holder_seed='H_Q1'):
    """One finite authored fragment in native written order; unknowns stay unknown."""
    result = []
    returns = {}
    for edition in ['ZL3b', 'IT2a', 'RF1b']:
        own = [x for x in packet if x['edition'] == edition]
        producer = None
        portion = None
        rows = []
        for src in own:
            raw, unit = src['ivtff_group_raw'], src['unit_id']
            sid = src['source_group_id']
            r = {'source': dict(src), 'raw_unchanged': raw, 'assembly': [],
                 'status': 'UNRESOLVED', 'meaning': None, 'operator_input': None,
                 'returned_predicates': None, 'actual_payload': None, 'cost_ids': []}
            if raw == 'otchdy' and unit == 'F83_Q1':
                r.update(meaning='At the later-written receptacle, for E_Q1.',
                         operator_input={'noun_reference': '$future_H', 'event': 'E_Q1'},
                         returned_predicates=frozen.location_relation('AT_EVENT', ('RECEPTACLE', '$future_H'), WORLD, parent_refs['case_material'], 'E_Q1'),
                         cost_ids=['P01', 'G02', 'G03', 'G04', 'L_otchdy'])
            elif raw == 'shedal' and unit == 'F83_Q1':
                r.update(meaning='Actual dispensing of the P4 case liquid toward its outlet; arrival not asserted.',
                         operator_input={'root': 'DISPENSE', 'patient': parent_refs['case_material'], 'target': parent_refs['outlet'], 'event': 'E_Q1', 'phase': 'I_Q1'},
                         returned_predicates=And(frozen.actual('DISPENSE', WORLD, 'E_Q1', parent_refs['case_material'], 'I_Q1'), A('OUTLET', WORLD, parent_refs['outlet']), A('GOAL', WORLD, 'E_Q1', parent_refs['outlet'])),
                         cost_ids=['P03', 'A02', 'G01', 'G02', 'L_shedal'])
            elif raw == 'dal' and unit == 'F83_Q1':
                portion = {'port': 'D_Q1', 'source': parent_refs['case_material'], 'producer': sid}
                r.update(meaning='A portion of the written case liquid.',
                         operator_input={'source': parent_refs['case_material']}, actual_payload=copy.deepcopy(portion),
                         returned_predicates=And(A('MATERIAL', WORLD, portion['port']), A('PORTION_OF', WORLD, portion['port'], portion['source'])),
                         cost_ids=['P04', 'A01', 'G05', 'L_dal'])
            elif raw == 'cheol' and unit == 'F83_Q1':
                producer = new_cheol(holder_seed, parent_refs['outlet'], sid)
                returns[edition] = copy.deepcopy(producer)
                r.update(meaning='A receptacle whose proper part is the already written outlet.',
                         operator_input={'ch_noun_witness': holder_seed, 'ol_operand': parent_refs['outlet']},
                         actual_payload=copy.deepcopy(producer),
                         returned_predicates=And(producer['noun_fact'], producer['relation']),
                         cost_ids=['P01', 'P02', 'H01', 'G01', 'L_cheol'])
            elif raw == 'cheol' and unit == 'F83_Q2':
                consumed = consume_cheol(producer, sid)
                r.update(meaning='The same receptacle/outlet proper-part relation actually returned in Q1.',
                         operator_input={'actual_return': copy.deepcopy(producer)}, actual_payload=consumed,
                         returned_predicates=consumed['returned_predicates'],
                         cost_ids=['P01', 'P02', 'H01', 'G08', 'L_cheol'])
            elif raw == 'lol' and unit == 'F83_Q1':
                r.update(meaning='With liquid (frozen whole value), attached to E_Q1.',
                         operator_input={'event': 'E_Q1', 'liquid': parent_refs['case_material']},
                         returned_predicates=A('WITH_LIQUID', WORLD, 'E_Q1', parent_refs['case_material']), cost_ids=['G01', 'G06'])
            elif raw == 'chdal' and unit == 'F83_Q1':
                assert producer is not None and portion is not None
                r.update(meaning='The actual Q1 receptacle is for the actual DAL portion; no containment assertion.',
                         operator_input={'holder_payload': copy.deepcopy(producer), 'portion_payload': copy.deepcopy(portion)},
                         returned_predicates=A('FOR_MATERIAL', WORLD, producer['holder'], portion['port']),
                         cost_ids=['P01', 'P04', 'P05', 'G07', 'L_chdal'])
            elif raw == 'chedy':
                assert portion is not None
                r.update(meaning='The Q1 portion is pure (frozen value) at T_Q1_final.',
                         operator_input={'patient': portion['port'], 'time': 'T_Q1_final'},
                         returned_predicates=A('PURE', WORLD, portion['port'], 'T_Q1_final'), cost_ids=['G06', 'G13'])
            elif raw == 'ol':
                r.update(meaning='Nominal mention of the same written outlet; no omitted relation supplied.',
                         operator_input={'written_reference': parent_refs['outlet']},
                         returned_predicates=A('MENTION', WORLD, parent_refs['outlet']), cost_ids=['G01', 'G09', 'L_ol'])
            elif raw == 'chey':
                r.update(meaning='Nominal mention of the same P4 conduit; no identity with Q1 receptacle asserted.',
                         operator_input={'written_reference': parent_refs['conduit']},
                         returned_predicates=A('CONDUIT', WORLD, parent_refs['conduit']), cost_ids=['G01', 'G09', 'L_chey'])
            elif raw == 'dain':
                r.update(meaning='Ordered series (frozen operator); event-membership obligation remains open.',
                         operator_input={'series': 'Series_Q2', 'actual_members': []},
                         returned_predicates=A('ORDERED_SERIES', WORLD, 'Series_Q2'), cost_ids=['G10'])
            elif raw == 'olsaiin':
                r.update(meaning='The written outlet in a phase subsequent to the Q1 dispensing phase; temporal caption.',
                         operator_input={'outlet': parent_refs['outlet'], 'previous_phase': 'I_Q1', 'caption_phase': 'J_CAP46'},
                         returned_predicates=And(A('MENTION_IN_PHASE', WORLD, parent_refs['outlet'], 'J_CAP46'), A('SUBSEQUENT', WORLD, 'J_CAP46', 'I_Q1')),
                         cost_ids=['G01', 'G11', 'L_olsaiin'])
            elif raw == 'saroldal':
                r.update(meaning='A portion of a batch, at the written outlet; relational nominal caption.',
                         operator_input={'source_noun': 'B_CAP50', 'location': parent_refs['outlet'], 'head_portion': 'D_CAP50'},
                         returned_predicates=And(A('BATCH', WORLD, 'B_CAP50'), A('MATERIAL', WORLD, 'B_CAP50'), A('MATERIAL', WORLD, 'D_CAP50'), A('PORTION_OF', WORLD, 'D_CAP50', 'B_CAP50'), A('AT_MATERIAL', WORLD, 'D_CAP50', parent_refs['outlet'])),
                         cost_ids=['P04', 'A01', 'G01', 'G12', 'G14', 'L_saroldal'])
            if r['returned_predicates'] is not None:
                r['status'] = 'ASSIGNED_C0_FRAGMENT'
                r['assembly'] = ASSEMBLIES.get(raw, [raw])
                if raw == 'dain':
                    r['status'] = 'ASSIGNED_C0_OPERATOR_WITH_UNMET_MEMBER_OBLIGATION'
            else:
                r['native_barrier'] = UNRESOLVED[raw]
            rows.append(r)
        assert producer is not None
        for r in rows:
            if r['raw_unchanged'] == 'otchdy':
                r['forward_resolution'] = {'actual_producer_return': copy.deepcopy(producer), 'substitution': {'$future_H': producer['holder']}}
                r['resolved_predicates'] = frozen.substitute(r['returned_predicates'], {'$future_H': producer['holder']})
            else:
                r['resolved_predicates'] = copy.deepcopy(r['returned_predicates'])
        result.extend(rows)
    return result, returns

def projection(actual_return, depiction_binding=None):
    """No picture convention follows from text. A supplied binding is external.

    Missing anchors return zero constraints, never negative image edges.
    Even full anchors need a separately specified literal depiction license;
    this author does NOT adopt that license for the current manuscript.
    """
    text_relation = copy.deepcopy(actual_return['relation'])
    if not depiction_binding:
        return {'text_relation': text_relation, 'unconditional_graph_atoms': [],
                'status': 'NO_ADOPTED_DEPICTION_LICENSE_OR_COMPLETE_OWNER_BINDING'}
    if not depiction_binding.get('literal_depiction_license'):
        return {'text_relation': text_relation, 'unconditional_graph_atoms': [], 'status': 'MISSING_DEPICTION_LICENSE'}
    h, o = actual_return['holder'], actual_return['outlet']
    if h not in depiction_binding['anchors'] or o not in depiction_binding['anchors']:
        return {'text_relation': text_relation, 'unconditional_graph_atoms': [], 'status': 'MISSING_ANCHOR'}
    return {'conditional_graph_atoms': [{'relation': 'PROPER_PART', 'part': depiction_binding['anchors'][o], 'whole': depiction_binding['anchors'][h]}],
            'status': 'CONDITIONAL_ONLY_NOT_CURRENT_PREDICTION'}

def run():
    packet = list(csv.DictReader((P / INPUTS[0]).open(), delimiter='\t'))
    parent = json.loads((P / INPUTS[1]).read_text())
    priors = json.loads((P / INPUTS[3]).read_text())
    refs = parent['inherited_native_IT_account']['rows'][-1]['reference_registers_after']
    rows, returns = execute(packet, refs)
    # C is independently fixed by P4 and the later written CHEY mention.
    # This changes identity to an existing participant, not an alpha-renaming.
    changed_rows, changed_returns = execute(packet, refs, holder_seed=refs['conduit'])
    sid = 'IT2a|f83r.53|G002'
    consumer = next(r for r in rows if r['source']['source_group_id'] == sid)
    changed_consumer = next(r for r in changed_rows if r['source']['source_group_id'] == sid)
    assert consumer['actual_payload']['holder_read'] == returns['IT2a']['holder']
    assert changed_consumer['actual_payload']['holder_read'] == changed_returns['IT2a']['holder']
    assert consumer['resolved_predicates'] != changed_consumer['resolved_predicates']
    assert changed_consumer['actual_payload']['holder_read'] == refs['conduit']
    assert consumer['actual_payload']['outlet_read'] == changed_consumer['actual_payload']['outlet_read'] == refs['outlet']
    try:
        consume_cheol(None, sid)
    except ValueError as exc:
        absent_error = str(exc)
    else:
        raise AssertionError('Consumer succeeded without donor')
    assert len(rows) == 94
    for edition, expected in [('ZL3b', 31), ('IT2a', 31), ('RF1b', 32)]:
        assert sum(r['source']['edition'] == edition for r in rows) == expected
        assert [r['source'] for r in rows if r['source']['edition'] == edition] == [s for s in packet if s['edition'] == edition]
    assert all(''.join(parts) == raw for raw, parts in ASSEMBLIES.items())
    counts = {e: {u: {s: sum(r['source']['edition'] == e and r['source']['unit_id'] == u and r['status'] == s for r in rows)
                            for s in sorted(set(r['status'] for r in rows))}
                     for u in dict.fromkeys(s['unit_id'] for s in packet)}
              for e in ['ZL3b', 'IT2a', 'RF1b']}
    compact_priors = [{'form': p['form'], 'matching': p['matching'], 'editions': {
        e: {k: v[k] for k in ['count', 'total_groups', 'fraction', 'rank', 'pages_with_form', 'pages_total', 'positions', 'repetition', 'strata']}
        for e, v in p['editions'].items()}} for p in priors['profiles']]
    out = {
        'status': 'FROZEN_IMAGE_BLIND_PARTIAL_C0_NOT_FULL_READING_NOT_CONFIRMATION',
        'confirmed_words': 0, 'complete_native_positions_preserved': 94,
        'own_prior_diagram_knowledge': 'None in this author fork. Route and supplied text contain no geometry facts. Project/root prior exposure remains disclosed; drafting separation is not an independent holdout.',
        'source_receipts': {n: hashlib.sha256((P / n).read_bytes()).hexdigest() for n in INPUTS},
        'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'inherited_parent_status': parent['status'], 'inherited_parent_sha256': parent['frozen_parent_sha256'],
        'inherited_values_unchanged': parent['inherited']['preserved_parent_dictionaries'],
        'inherited_primitive_and_assembly_inventory_unchanged': {'primitives': parent['inherited']['new_primitive_inventory'], 'assemblies': parent['inherited']['new_exact_assemblies']},
        'inherited_motion_map_unchanged': parent['inherited']['shared_motion_grade']['map'],
        'inherited_G_I_difference_preserved': 'LCHEDY G=PURIFIED, I=PURIFICATION_INTENDED. No LCHEDY occurrence here and no branch merger.',
        'parent_variable_access': {'imported_actual_references': refs, 'unused': ['R', 'P6', 'D1', 'D2'], 'cost': 'G01', 'interpretation': 'Explicit local continuation assumption, not neighborhood identity evidence.'},
        'new_primitives': PRIMITIVES, 'exact_assemblies': ASSEMBLIES, 'cost_ledger': COSTS,
        'cost_totals': {'new_primitive_or_frame_entries': 5, 'exact_assembly_licenses': len(ASSEMBLIES),
                        'scoped_homonyms': 1, 'aliases_or_semantic_overlaps': 2,
                        'grammar_identity_binding_defaults': 14, 'whole_form_clause_macros': 0,
                        'unpriced_whole_form_residuals': 0,
                        'interpretation': 'Counts overlap and are authored-decision counts, not likelihoods, evidence, or code length.'},
        'per_position_table': rows, 'coverage': counts,
        'actual_Q1_producer_returns': returns,
        'actual_Q2_consumer_IT': consumer,
        'counterfactual': {'only_changed_author_input': 'Q1 CH nominal witness supplied to constructor: unconstrained H_Q1 -> independently P4-bound conduit C',
                           'same_consumer_code_and_context': True,
                           'baseline_return': returns['IT2a'], 'changed_return': changed_returns['IT2a'],
                           'baseline_consumption': consumer['actual_payload'], 'changed_consumption': changed_consumer['actual_payload'],
                           'consumer_changes': True, 'outlet_unchanged': True, 'missing_donor_error': absent_error,
                           'limit': 'The changed payload identifies the holder with independently bound P4 conduit C, also mentioned by Q2 CHEY. This is a stronger identity constraint, not an alpha-renaming. Baseline does not assert H unequal to C. Neither version is manuscript confirmation or an anchored image prediction.'},
        'image_blind_projection': {'projection_result': projection(returns['IT2a']),
                                  'text_graph_candidate': {'relation': 'PROPER_PART', 'part': 'text_O', 'whole': 'text_H'},
                                  'caption_denotations': {'F83_CAPTION_45': 'UNRESOLVED', 'F83_CAPTION_46': 'text_O in authored subsequent phase', 'F83_CAPTION_50': 'IT-only text_D_CAP50 portion of text_B_CAP50 at text_O', 'F83_CAPTION_51': 'UNRESOLVED'},
                                  'adopted_depiction_license': False, 'unconditional_observable_constraints': [],
                                  'discriminating_observable_consequence': False,
                                  'literal_projection_definition': 'With independently supplied literal depiction license and distinct anchors for both text_O/text_H, project PROPER_PART(text_O,text_H) to exactly PROPER_PART(anchor_O,anchor_H). Nothing else. Neither anchor_H nor depiction license is supplied/selected here.',
                                  'prohibited_inferences': ['No connection/endpoint/contour/count/color/orientation derived from FLOW, DISPENSE, GOAL or temporal captions.', 'FOR_MATERIAL is not CONTAINS.', 'PORTION_OF material is not necessarily a drawn proper part.', 'No equation text_H=text_C, no guessed scene coordinates or image objects.', 'No absent depicted edge inferred from omitted/unresolved text.', 'OLS(A)IIN textual O denotation does not by itself assign image-caption ownership.'],
                                  'rival_depiction': 'Actions, portions and even receptacle/outlet relation may be described without being literally drawn. This remains compatible with the fragment.'},
        'connected_conditional_reading': {
            'Q1': 'At a receptacle [OTCHDY; forward-resolved], [QOKCHDY unresolved], the P4 case liquid is dispensed toward the written outlet [SHEDAL]. A portion of that liquid [DAL]; a receptacle whose proper part is the outlet [CHEOL], with liquid for the dispensing [LOL], and that receptacle is for that portion [CHDAL]. [AIIN unresolved]. [SOL and DAIIIN unresolved]. The portion is pure at a later description time [CHEDY]. This is a connected assigned fragment, not a translation of all Q1.',
            'Q2': '[SOLKEEY QEKEY RALY unresolved]. Mention of the written outlet [OL]. [SOLCHKAL unresolved]. Reuse the actual Q1 receptacle/outlet relation [CHEOL; RF CHEAL unresolved]. [QOTAR unresolved]. Outlet [OL]. [DAIIN unresolved]. Outlet [OL]. An ordered series opens [DAIN], with a mention of the P4 conduit [CHEY], but no actual series members supplied. [LDALOR unresolved]. [SOL RTAIN CTHOL unresolved; alternate native forms retained]. No complete Q2 proposition is obtained.',
            'captions': '45 CHTOROL unresolved. 46 OLSAIIN: outlet in a subsequent authored phase. 50 IT SAROLDAL: portion of a batch at the outlet; ZL SASOLDAL and RF S@221;ROLDAL unresolved. 51 DAROLSY unresolved.',
        },
        'prior_evidence_used': compact_priors,
        'prior_effects': [
            'IT CHEOL count138/pages70, mostly middle128 of138: prefer a reusable relational nominal hypothesis to an image-coordinate or entire-clause code; this does not establish RECEPTACLE or PROPER_PART.',
            'IT DAL count201/pages88 and repeated-lines12: proposed portion is generic rather than a one-off proper name; the QOTEEDY semantic alias is explicitly paid, with no frequency proof.',
            'IT OL count456/pages106/max-per-line4: retain the inherited reference value at all four Q2 mentions; no new object at each repetition.',
            'IT AIIN rank4/count390/pages97 and DAIIN rank1/count740/pages169: do not turn them into target-specific nouns/numerals or broad clause macros to complete a scene.',
            'IT SOL start38 of63 and SOLKEEY start4 of4: phase/frame interpretation is plausible, but not enough to license SOL=S+OL or forbidden LK EY.',
            'IT OTCHDY count25/pages20: proposed AT reference composition is reusable, not a unique scene instruction.',
            'Rare QEKEY/LDALOR/RTAIN and captions do not acquire meanings from rarity. Uncertainty and exact zero-count alternative spellings are not missing manuscript evidence.',
            'ZL/IT/RF descriptive counts are alternate readings of one manuscript, never three independent witnesses or pooled frequency evidence.'
        ],
        'rivals_and_unresolved_alternatives': [
            'CHEOL could be a whole-form lexical item or a CH/EO/L segmentation. CHEEOL mixture remains a different exact form; no deletion/alias to mixture is adopted.',
            'E_CH could encode generic association rather than proper part; that rival changes the textual relation. Current proper-part assignment has no independent semantic discriminator.',
            'CHDAL could introduce a second receptacle instead of reusing H; G07 selects reuse and pays for it.',
            'QOTAR receiver, DAIIN ordered-series alias, SOL temporal operator, and caption45 CH/T/OR/OL are candidate continuations considered but not selected; none is claimed impossible.',
            'Captions may be process or relational expressions and need not form four categories. Caption types here are authored hypotheses only.',
            'P4 C/O/L continuation could describe a new case instead. G01 explicitly chooses same-case identity; nearby records alone do not supply it.'
        ],
        'native_barriers': ['IT Q2 CTHOL versus ZL CTHAL versus RF CTH@221;L remain distinct.', 'RF Q2 CHEAL unassigned; not imputed CHEOL consumer.', 'RF R uncertain-small-space TAIN remains two native groups; not normalized to RTAIN.', 'Caption50 SAROLDAL/SASOLDAL/S@221;ROLDAL remain separate.', 'RF paragraph flags are all zero; supplied Q1/Q2 membership is packet unit definition, not newly inferred RF paragraph ends.', 'No prose grammar assumed for DIAGNOSTIC_NONPROSE captions.'],
        'unmet_obligations': ['Unknown positions prevent complete Q1, Q2 and all-caption same-meaning continuation.', 'DAIN actual-event membership remains open.', 'No complete reader account is claimed for any edition.', 'No whole-unit truth/satisfiability or independent capability accessibility check.', 'No adopted depiction license or complete anonymous-to-caption/image owner binding; zero unconditional image predictions.', 'Actual returned relation is a constructed C0 hypothesis, not established manuscript semantics.'],
        'freeze_policy': 'Final author files are frozen before image/geometry/critic exposure. Do not repair after review. Root owns evaluation and publication.',
    }
    (P / (STEM + '.json')).write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    md = ['# Frozen text-only continuation, 2 October 2026', '',
          'Status: **PARTIAL C0**. Confirmed words: **0**. All94 native positions preserved (31ZL/31IT/32RF). No complete Q1/Q2/all-caption reading, no independent manuscript confirmation, and no unconditional observable image constraint.', '',
          out['own_prior_diagram_knowledge'], '',
          'Only the four authorized source/parent/prior files were read after the live route and author instructions. Frozen parent definitions were imported without calling run(). No geometry contract, decision/advisory, FT account, image, external site or other target text was read.', '',
          '## Conditional assigned fragment', '']
    for k, v in out['connected_conditional_reading'].items():
        md += ['**' + k + '.** ' + v, '']
    md += ['## Actual producer/consumer', '',
           'Q1 `IT2a|f83r.48|G002` CHEOL composes new CH receptacle, scoped E_CH proper-part, and inherited OL outlet. It returns `{holder:H_Q1,outlet:O,relation:PROPER_PART(O,H_Q1)}`. Q2 `IT2a|f83r.53|G002` reads that exact returned package through one paid discourse port. Q2 has no separate holder/outlet context, and missing donor causes an explicit error. CHDAL and the pending OTCHDY location also consume the actual return.', '',
           'Changing only the Q1 constructor holder operand to the independently P4-bound conduit C changes the Q2 returned relation to PROPER_PART(O,C); consumer code/context and outlet remain unchanged. C is already fixed independently of the holder and is later mentioned by written Q2 CHEY. This imposes a stronger identity constraint than the baseline, rather than merely renaming an existential witness; baseline does not assert H unequal to C. It demonstrates real returned-participant dataflow, without confirming either identity in the manuscript. RF CHEAL is unresolved and is not advertised as a complete RF consumer.', '',
           '## Image-blind literal projection', '',
           'The authored fragment asserts a textual proper-part relation. It supplies no rule that those nouns/actions are literally pictured and no independent owner for textual H. Therefore **zero unconditional observable constraints follow**. With an independently supplied literal depiction license and both anonymous referent anchors, project only PROPER_PART(text_O,text_H) to PROPER_PART(anchor_O,anchor_H). That conditional projection is not adopted as a manuscript prediction. Temporal caption46 may mention O, but does not itself bind a visual owner.', '',
           'No contour, endpoint, incidence, connectivity, count, orientation or absence follows. FOR_MATERIAL is suitability, not containment; a material portion is not automatically a drawn proper part. Missing textual edges never mean absent depicted edges.', '',
           '## Costs and unchanged parent', '',
           'The five new semantic/frame entries, nine exact ordered assembly licenses, one scoped homonym, two semantic overlaps/aliases and fourteen grammar/binding/default policies are itemized below. These counts overlap and are not likelihood/evidence. No clause macro, decoder or unpriced whole-form residual is used. Unknown wholes remain unknown. P4 meanings, motion grades, and the G/I LCHEDY difference remain unchanged.', '',
           '| ID | Kind | Units | Exact authored rule |', '|---|---|---:|---|']
    for c in COSTS:
        md.append('| ' + c['id'] + ' | ' + c['kind'] + ' | ' + str(c['units']) + ' | ' + c['rule'].replace('|', '\\|') + ' |')
    md += ['', '## Exact per-position table', '',
           'Raw groups, source IDs, unit positions, separators, uncertainties, paragraph flags and grammar scopes are preserved verbatim in JSON. This table records all94 groups. Assigned fragment entries are hypotheses; the DAIN operator has unmet membership. Reader differences remain separate.', '',
           '| Source group | Unit/position | Raw | Status | Contribution or exact barrier |', '|---|---|---|---|---|']
    for r in rows:
        src = r['source']
        values = [src['source_group_id'], src['unit_id'] + '/' + src['unit_position'], r['raw_unchanged'], r['status'], r['meaning'] or r['native_barrier']]
        md.append('| ' + ' | '.join(v.replace('|', '\\|') for v in values) + ' |')
    md += ['', '## Frequency priors, rivals and limits', '']
    md.extend('- ' + x for x in out['prior_effects'])
    md += ['']
    md.extend('- ' + x for x in out['rivals_and_unresolved_alternatives'])
    md += ['']
    md.extend('- ' + x for x in out['native_barriers'])
    md += ['']
    md.extend('- ' + x for x in out['unmet_obligations'])
    md += ['', 'The new proper-part, receptacle and portion hypotheses are not selected by a scientific semantic discriminator. They are finite authored alternatives that expose exactly where continuation remains blocked; unknown inputs are not evidence of absent research. No later diagnostic can turn this partial authored model into a complete registered result.', '',
           '## Freeze receipts', '', '| Authorized input | SHA-256 |', '|---|---|']
    for n, h in out['source_receipts'].items():
        md.append('| ' + n + ' | ' + h + ' |')
    md += ['', 'Generator SHA-256: `' + out['generator_sha256'] + '`.', '',
           'The JSON contains the exact tables, prior numbers, real producer/consumer and counterfactual returns. Root records final file hashes externally; this file does not claim a self-referential hash. No post-review repair is authorized.', '']
    (P / (STEM + '.md')).write_text('\n'.join(md))
    print(json.dumps({'status': out['status'], 'positions': len(rows), 'coverage': counts,
                      'hashes': {STEM + ext: hashlib.sha256((P / (STEM + ext)).read_bytes()).hexdigest() for ext in ['.py', '.json', '.md']}}, indent=2))

if __name__ == '__main__':
    run()
