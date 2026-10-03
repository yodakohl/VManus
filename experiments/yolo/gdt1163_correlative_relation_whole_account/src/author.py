#!/usr/bin/env python3
"""One frozen C0 author account. Whole execution is partial; core projections are conditional.

execute(policy, relation_transform=None) returns the actual constructed, returned,
and consumed records. A transform receives a deepcopy of each produced edge and
must return its replacement; mutations are applied before reference and consumer.
No diagnostic packet is opened here.
"""
import copy
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path('experiments/yolo/gdt1163_correlative_relation_whole_account')
CORE_PATH = EXP / 'src/CORE_FREEZE.json'
CORE_SHA = '3adc9461119c05eb738b5becc0a6d7abf909a56ca462bf0dfb5be7348ae31f90'
POLICIES = ('FORWARD_ORIGIN', 'INVERTED_ORIGIN', 'INVERTED_DESTINATION')
EXTENSIONS = {
    'qokeedy': {'meaning': 'consider', 'category': 'CONSIDER_HEAD', 'composition': 'Exact whole-word imperative; requires a written nominal or clause complement.', 'roots': ['CONSIDERATION'], 'heads': ['CONSIDER']},
    'qolchey': {'meaning': 'concerning understanding', 'category': 'SCOPE_PHRASE', 'composition': 'Exact QOL+CHEY license, where CHEY retains frozen ACT(UNDERSTAND); no global QOL rule.', 'roots': [], 'heads': ['CONCERNING']},
    'otchey': {'meaning': 'understanding itself', 'category': 'ACT_NOMINAL', 'composition': 'Exact OT+CHEY license, with frozen ACT(UNDERSTAND); no global OT rule or new actor.', 'roots': [], 'heads': ['SELF']},
    'qoky': {'meaning': 'a relation', 'category': 'RELATION_NOMINAL', 'composition': 'Exceptional whole noun; naming a relation does not construct an edge or identify its endpoints.', 'roots': ['RELATION_NOMINAL'], 'heads': []},
}
CORE_ENGLISH = {
    'chey': 'understanding', 'cheey': 'a knower', 'chedy': 'the knowable',
    'shey': 'loving', 'sheey': 'a lover', 'shedy': 'the lovable',
    'qokeey': 'the corresponding active bearer',
    'qokedy': 'active/receptive correlative relation',
    'solchedy': 'the earlier relation concerning the knowable',
    'qody': 'the named active bearer is the selected relation\'s endpoint',
}
# These are disclosed candidate attachments, not a decoded general sentence parser.
ATTACHMENTS = {
    '25': [('consider', 'Known consideration operator; candidate complement .25G003–005, modified by .25G002.'), ('scope', 'Concerning UNDERSTAND; modifies the considered relation, not its endpoint.'), ('active', 'Written cataphoric active argument of .25G004; root unified to .25G005.'), ('producer', 'Binary constructor with contiguous .25G003/.25G005.'), ('recipient', 'Written receptive argument of .25G004.'), ('unknown', 'Could qualify, close, negate, quantify or change the scope of the preceding considered relation.')],
    '26': [('act_nominal', 'Exact self-modified UNDERSTAND act nominal; no predication attachment recovered.'), ('active_unbound', 'Active nominal is written, but no local QOKEDY exists; its principle stays unbound.'), ('relation_nominal', 'Names a relation; cannot produce an edge or bind .26G002.'), ('unknown', 'Link between relation, the active bearer and the following receptive nominal is unread.'), ('recipient_unattached', 'LOVE receptive nominal is written; no edge-producing head binds it here.'), ('unknown', 'Could supply a predicate, scope or relation affecting this row; not a hidden producer.')],
    '27': [('unknown', 'Could introduce a subject, anaphor, quantifier or discourse scope for CHEDY and consideration.'), ('recipient_unattached', 'UNDERSTAND receptive nominal; no new QOKEDY edge is written.'), ('consider_pending', 'Same consideration operator as .25/.30; SHCKHEDY complement type/content remains unknown.'), ('unknown', 'First exact SHCKHEDY; its role and contribution to the consideration argument are unread.'), ('unknown', 'Second exact SHCKHEDY; same unknown lexical function, two written occurrences; no free emphasis or idempotence.')],
    '28': [('unknown', 'Could change question/assertion, quantification or subject scope of the following relation.'), ('unknown', 'Could change the attachment or force of the following relational clause; spelling is not normalized to CHEEY.'), ('active', 'Written active LOVE argument of .28G004.'), ('producer', 'Binary constructor with contiguous .28G003/.28G005.'), ('recipient', 'Written receptive LOVE argument of .28G004.'), ('unknown', 'First OLDY; may be a scope/role/predicate supplement, not an assumed archive or no-op.')],
    '29': [('reference', 'Nearest earlier written QOKEDY relation of UNDERSTAND; actually .25G004 in the core projection.'), ('named_active', 'Named ACTIVE(UNDERSTAND) kind used by .29G003; no material predicate.'), ('consumer', 'Checks the named kind against actual returned relation endpoint under policy.'), ('unknown', 'Could qualify, deny or restrict the endpoint assertion, or begin another construction.'), ('unknown', 'Same OLDY function as .28; attachment and effect unread. Not executed after a failed core assertion.')],
    '30': [('unknown', 'May identify a consideration, a participant or an outer operator; no S+OKEEDY decomposition licensed.'), ('consider', 'Same consideration operator; local candidate nominal complement is .30G003.'), ('relation_nominal', 'Names a relation as consideration complement; no new edge or referent is created.'), ('unknown', 'Unread exact SAIRN tail; may change final consideration/closure. RF SAIIN is not substituted.')],
}
CONNECTED = (
    'Consider, concerning understanding, the corresponding active bearer’s relation to the knowable — UNKNOWN[otal]. '
    'Understanding itself: a corresponding active bearer [UNKNOWN: its principle and predicate], a relation — UNKNOWN[tol] — the lovable — UNKNOWN[qokylddy]. '
    'UNKNOWN[dain] the knowable: consider UNKNOWN[shckhedy] UNKNOWN[shckhedy]. '
    'UNKNOWN[saiin] UNKNOWN[cheeky]: the lover’s relation to the lovable — UNKNOWN[oldy]. '
    'In the earlier relation concerning the knowable, the knower is its active origin — UNKNOWN[kesd] UNKNOWN[oldy]. '
    'UNKNOWN[sokeedy]: consider a relation — UNKNOWN[sairn].'
)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def inputs():
    core_bytes = (ROOT / CORE_PATH).read_bytes()
    if sha(core_bytes) != CORE_SHA:
        raise ValueError('frozen core hash changed')
    core = json.loads(core_bytes)
    source_bytes = (ROOT / core['input']['native_packet']).read_bytes()
    if sha(source_bytes) != core['input']['native_packet_sha256']:
        raise ValueError('bound native source hash changed')
    source = json.loads(source_bytes)
    rows = [r for r in source['rows'] if r['edition'] == 'IT2a']
    if len(rows) != 32 or len(source['rows']) != 97:
        raise ValueError('wrong source count')
    expected = [w for line in core['input']['groups'].values() for w in line]
    if [r['ivtff_group_raw'] for r in rows] != expected:
        raise ValueError('source primary sequence changed')
    return core, source, rows

def nominal(row, core):
    value = core['whole_word_licenses'].get(row['ivtff_group_raw'], {})
    if value.get('role') not in ('ACTIVE', 'RECEPTIVE'):
        return None
    return {'source_group_id': row['source_group_id'], 'raw': row['ivtff_group_raw'], 'root': value['root'], 'role': value['role']}

def edge_for(index, rows, core, policy):
    producer = rows[index]
    if index == 0 or index + 1 == len(rows):
        return None, 'missing contiguous argument'
    left, right = rows[index - 1], rows[index + 1]
    if not (left['locus'] == producer['locus'] == right['locus']):
        return None, 'cross-line argument prohibited'
    if left['right_separator'] != 'DEFINITE_SPACE' or producer['right_separator'] != 'DEFINITE_SPACE':
        return None, 'uncertain seam'
    a, b = nominal(left, core), nominal(right, core)
    if a is None or b is None:
        return None, 'unlicensed argument'
    if sorted((a['role'], b['role'])) != ['ACTIVE', 'RECEPTIVE']:
        return None, 'role conflict'
    active, recipient = (a, b) if a['role'] == 'ACTIVE' else (b, a)
    if active['root'] == 'LOCAL_PRINCIPLE_VARIABLE':
        active['root'] = recipient['root']
    if active['root'] != recipient['root'] or recipient['root'] == 'LOCAL_PRINCIPLE_VARIABLE':
        return None, 'principle conflict'
    origin, destination = (active, recipient) if policy == 'FORWARD_ORIGIN' else (recipient, active)
    return {'producer': producer['source_group_id'], 'producer_raw': producer['ivtff_group_raw'], 'root': recipient['root'], 'arguments': [left['source_group_id'], right['source_group_id']], 'active': active, 'receptive': recipient, 'origin': origin, 'destination': destination}, None

def endpoint_check(relation, named, policy):
    """Consume actual returned root/endpoint fields; do not regenerate expected edge."""
    endpoint_name = 'destination' if policy == 'INVERTED_DESTINATION' else 'origin'
    endpoint = relation[endpoint_name]
    root_ok = relation['root'] == named['root']
    endpoint_ok = (endpoint['root'], endpoint['role']) == (named['root'], named['role'])
    return {'endpoint_policy': endpoint_name.upper(), 'consumed_endpoint': copy.deepcopy(endpoint), 'named_active': copy.deepcopy(named), 'root_equal': root_ok, 'endpoint_kind_equal': endpoint_ok, 'result': 'PASS' if root_ok and endpoint_ok else 'FAIL', 'consumed_producer': relation['producer']}

def execute(policy='FORWARD_ORIGIN', relation_transform=None):
    if policy not in POLICIES:
        raise ValueError('unknown policy')
    core, source, rows = inputs()
    row_lookup = {r['source_group_id']: r for r in rows}
    ordinal = {r['source_group_id']: i for i, r in enumerate(rows)}
    relations, trace, returned, consumer = [], [], None, None
    producer_bindings = {}
    status = 'UNKNOWN'
    stopped = None
    for i, row in enumerate(rows):
        raw, sid = row['ivtff_group_raw'], row['source_group_id']
        if raw == 'qokedy':
            relation, error = edge_for(i, rows, core, policy)
            if error:
                trace.append({'event': 'unbound_producer', 'source_group_id': sid, 'reason': error})
                continue
            producer_bindings[sid] = set(relation['arguments'])
            if relation_transform is not None:
                relation = relation_transform(copy.deepcopy(relation))
            if relation is not None:
                relations.append(relation)
            trace.append({'event': 'relation_produced', 'source_group_id': sid, 'relation': copy.deepcopy(relation), 'assertion_scope': 'CONDITIONAL_ON_UNREAD_CONTEXT'})
        elif raw == 'solchedy':
            eligible, rejected = [], []
            for r in relations:
                producer_sid = r.get('producer')
                producer_row = row_lookup.get(producer_sid)
                provenance_ok = producer_row is not None and producer_row['ivtff_group_raw'] == 'qokedy' and producer_bindings.get(producer_sid) == set(r.get('arguments', []))
                if not provenance_ok:
                    rejected.append({'producer': producer_sid, 'reason': 'source producer/argument provenance mismatch'})
                    continue
                if ordinal[producer_sid] < i and r['root'] == 'UNDERSTAND':
                    eligible.append(r)
            returned = copy.deepcopy(max(eligible, key=lambda r: ordinal[r['producer']])) if eligible else None
            trace.append({'event': 'relation_reference', 'source_group_id': sid, 'candidate_producers': [r['producer'] for r in eligible], 'returned_relation': copy.deepcopy(returned), 'rejected_provenance': rejected, 'status': 'BOUND' if returned else 'UNBOUND'})
        elif raw == 'qody':
            actor = nominal(rows[i - 1], core) if i else None
            has_ref = i >= 2 and rows[i - 2]['ivtff_group_raw'] == 'solchedy' and rows[i - 2]['locus'] == row['locus'] == rows[i - 1]['locus']
            seams = i >= 2 and rows[i - 2]['right_separator'] == rows[i - 1]['right_separator'] == 'DEFINITE_SPACE'
            if returned is None or actor is None or actor['role'] != 'ACTIVE' or not has_ref or not seams:
                consumer = {'source_group_id': sid, 'result': 'UNKNOWN', 'reason': 'written relation reference or active argument is unbound'}
                status = 'UNKNOWN'
            else:
                consumer = endpoint_check(returned, actor, policy)
                consumer['source_group_id'] = sid
                status = consumer['result']
            trace.append({'event': 'endpoint_consumer', **copy.deepcopy(consumer), 'assertion_scope': 'CONDITIONAL_ON_UNREAD_CONTEXT'})
            if status != 'PASS':
                stopped = i
                break
        elif raw not in core['whole_word_licenses'] and raw not in EXTENSIONS:
            trace.append({'event': 'UNRESOLVED_SCOPE', 'source_group_id': sid, 'raw': raw, 'effect': 'not interpreted; may alter full assertion/attachment/reference force; projection is not whole execution'})
    tail = [r['source_group_id'] for r in rows[stopped + 1:]] if stopped is not None else []
    earliest_unknown = next(r for r in rows if r['ivtff_group_raw'] not in core['whole_word_licenses'] and r['ivtff_group_raw'] not in EXTENSIONS)
    return {'policy': policy, 'status': status, 'conditional_core_result': status, 'relations': relations, 'returned_relation': returned, 'consumer': consumer, 'trace': trace, 'not_executed_tail': tail, 'whole_execution': {'status': 'BLOCKED_UNKNOWN_SCOPE', 'first_blocker': earliest_unknown['source_group_id'], 'first_blocker_raw': earliest_unknown['ivtff_group_raw'], 'no_whole_assertion': True}, 'claim_ceiling': 'Actual conditional core dependency only. UNKNOWNs have not been executed as no-ops; their possible effects prevent a complete reading.'}

def contributions(rows, core):
    out = []
    for row in rows:
        line = row['locus'].split('.')[-1]
        position = int(row['source_group_index']) - 1
        role, debt = ATTACHMENTS[line][position]
        raw = row['ivtff_group_raw']
        license_ = core['whole_word_licenses'].get(raw)
        extension = EXTENSIONS.get(raw)
        known = license_ is not None or extension is not None
        item = {'source_group_id': row['source_group_id'], 'raw': raw, 'native_row': copy.deepcopy(row), 'lexical_status': 'CORE_C0' if license_ else ('EXTENSION_C0' if extension else 'UNKNOWN'), 'meaning': CORE_ENGLISH.get(raw, extension['meaning'] if extension else 'UNKNOWN[' + raw + ']'), 'attachment': role, 'attachment_debt': debt, 'scope_status': 'UNBOUND_PARAMETER' if role == 'active_unbound' else ('UNRESOLVED' if not known else 'CONDITIONAL_CONTEXT'), 'global_consistency': 'identical exact forms retain identical lexical function; unknown repeated forms remain the same unresolved function'}
        out.append(item)
    return out

def build_account():
    core, source, rows = inputs()
    aligns = contributions(rows, core)
    unreads = [r for r in aligns if r['lexical_status'] == 'UNKNOWN']
    return {'schema_version': 1, 'status': 'PARTIAL_NO_COMPLETE_READING', 'source_receipt': {'core_path': str(CORE_PATH), 'core_sha256': CORE_SHA, 'native_packet': core['input']['native_packet'], 'native_packet_sha256': core['input']['native_packet_sha256'], 'primary_groups': 32, 'native_groups': 97, 'no_new_target_access': True, 'diagnostic_cases_opened': False}, 'native_source': source, 'contributions': aligns, 'extension_lexicon': EXTENSIONS, 'cap_ledger': {'additional_content_roots': {'count': 2, 'items': ['CONSIDERATION', 'RELATION_NOMINAL']}, 'additional_functional_heads': {'count': 3, 'items': ['CONSIDER', 'CONCERNING', 'SELF']}, 'constructions_total': {'count': 6, 'items': ['frozen medial role relation', 'frozen earlier UNDERSTAND relation reference', 'frozen endpoint assertion', 'consideration with written nominal/clause complement', 'exact concerning-understanding scope phrase', 'exact self-modified understanding nominal']}, 'exceptional_whole_form_entries': {'count': 4, 'items': list(EXTENSIONS)}, 'overlap_policy': 'CONSIDER counts as both content root and functional head; the two exact CHEY compounds count as whole-form exceptions as well as using shared frozen CHEY semantics. RELATION_NOMINAL is charged as a content root despite related frozen relational semantics.'}, 'binding_choices': {'count': 32, 'items': [{'source_group_id': r['source_group_id'], 'attachment': r['attachment'], 'debt': r['attachment_debt']} for r in aligns], 'sentence_boundaries': 'No physical line is declared a grammatical sentence boundary; prose punctuation separates displayed fragments only.', 'other_costs': ['10 frozen whole licenses and three frozen constructions', 'four new lexical choices', 'exact QOL+CHEY and OT+CHEY compositions', 'generic-kind equality rather than identical individuals', 'three proposed consideration complements/scope domains', 'unknown adjoining groups can defeat these attachments']}, 'connected_reading': CONNECTED, 'reading_scope': 'Single conditional partial connected draft under FORWARD_ORIGIN; INVERTED_DESTINATION globally reverses directional language with the same endpoint assertion outcome. No fixed-direction English meaning is selected.', 'lexical_coverage': {'core_c0_positions': sum(x['lexical_status'] == 'CORE_C0' for x in aligns), 'extension_c0_positions': sum(x['lexical_status'] == 'EXTENSION_C0' for x in aligns), 'unknown_positions': len(unreads), 'unknown_forms': sorted({x['raw'] for x in unreads}), 'unbound_core_parameters': ['IT2a|f83r.26|G002'], 'complete_translation': False}, 'unknown_dependencies': [{'source_group_id': r['source_group_id'], 'raw': r['raw'], 'possible_effect': r['attachment_debt']} for r in unreads] + [{'source_group_id': 'IT2a|f83r.26|G002', 'raw': 'qokeey', 'possible_effect': 'No local QOKEDY triple binds its principle; frozen rule prevents borrowing either earlier active bearer or following SHEDY as an unlicensed binding.'}], 'extension_attempts_not_admitted': ['OTAL/TOL whole/part would require a new root and independent lexical values; no sentence relation selects that content.', 'OLDY as recipient/earlier-result pronoun would add a reference policy across KESD unknown and duplicate a current recipient without reading its actual contribution.', 'QOKYLDDY as modified QOKY and SOKEEDY as resumed consideration would require additional ungrounded modifier licenses; their raw forms remain intact.', 'SHCKHEDY is repeated twice; no infix, spelling repair, implicit repetition rule or new unknown objects were supplied.'], 'policy_executions': [execute(policy) for policy in POLICIES], 'historical_limits': ['Owned398 supports active/receptive/act exposition and contains knowledge/love examples; it does not select the target roots.', 'No universal EY/DY/Y interpretation; QOKEEY remains an exact whole-word cataphor.', 'All35 diagnostics belong to separate runner and were not opened here.', '1137 material meanings and1146/1147 failures unchanged.'], 'rivals': ['FORWARD_ORIGIN and INVERTED_DESTINATION remain observationally paired; anonymous CHE/SHE principle renaming remains equivalent.', 'Other senses, nominal/predicate assignments and ordinary source genres remain possible.', 'Consider/concerning/self/relation-noun extensions are C0, not preferred by frequency.'], 'decision': 'Retain actual two-edge/reference/endpoint core and four small stable extensions. Whole32 interpretation is incomplete:13 unread positions plus an unbound active principle and unknown scopes affecting focal assertions. Stop this one authoring attempt without filling the tail with free meanings.'}

def render(account):
    lines = ['# GDT1163 author: one partial correlative account', '', '**PARTIAL_NO_COMPLETE_READING.** The conditional core has two actual written producers, an actual earlier relation reference, and an endpoint consumer. The whole32 account remains unread in13 positions and has an unbound QOKEEY principle at .26. All97 native groups are conserved in AUTHOR_ACCOUNT.json. No diagnostic packet was opened.', '', '## Connected conditional draft', '', account['connected_reading'], '', 'Punctuation above displays fragments; it is not evidence of manuscript sentence boundaries. UNKNOWN groups may negate, question, quantify or alter the neighboring known expressions. Thus even the apparently complete clauses are not unconditional manuscript assertions. The three exact QOKEEDY occurrences all mean “consider” in this one C0 attempt; .27 lacks an interpretable complement. .26 QOKEEY cannot receive a principle outside its frozen QOKEDY construction.', '', '## Stable extensions and costs', '', 'Four whole licenses: QOKEEDY “consider”; QOLCHEY “concerning understanding” using exact QOL+CHEY; OTCHEY “understanding itself” using exact OT+CHEY; QOKY “a relation,” a noun which never constructs an edge. Count2 additional content roots,3 functional heads,6 constructions total,4 exceptional whole entries. These are unconfirmed choices. Profiles permit recurring broad roles but select none of these meanings. All32 attachment choices remain paid and separately listed.', '', '## Every primary contribution', '', '| Source position | Exact raw group | Proposed meaning | Attachment and unresolved contribution |', '|---|---|---|---|']
    for r in account['contributions']:
        lines.append('| ' + r['source_group_id'] + ' | ' + r['raw'] + ' | ' + r['meaning'] + ' | ' + r['attachment_debt'] + ' |')
    lines += ['', '## Actual conditional policies', '', '| Policy | Returned producer | Consumed endpoint | Conditional check |', '|---|---|---|---|']
    for e in account['policy_executions']:
        lines.append('| ' + e['policy'] + ' | ' + (e['returned_relation']['producer'] if e['returned_relation'] else 'UNBOUND') + ' | ' + e['consumer'].get('endpoint_policy', 'UNBOUND') + ' | ' + e['conditional_core_result'] + ' |')
    lines += ['', 'Both producers use actual same-line, definite N–QOKEDY–N triples. .25 QOKEEY unifies with the written CHEDY principle; .28 SHEEY/SHEDY share LOVE. SOLCHEDY returns the actual .25 edge because .28 has LOVE. QODY consumes the returned root and chosen endpoint, comparing its kind with the written CHEEY. Inverting only the edge fails; inverting edge and endpoint policy together passes. Anonymous root names are also equivalent. None selects a true English reading.', '', 'The callable execute(policy, relation_transform=None) applies interventions to the actual produced records before the reference and endpoint check. It does not reconstruct expected endpoints in the consumer. Root, producer identity/provenance and endpoint fields affect the returned relation or consumer. The failed policy leaves six tail groups not executed. This is a conditional projection; whole execution is blocked at .25 OTAL rather than treating unknowns as no-ops.', '', '## Why the whole account remains partial', '', 'The13 UNKNOWN positions are preserved with their possible scope effects. In addition, the second QOKEEY has no written local QOKEDY to bind its principle, and the .27 consideration lacks a known complement. OTAL/TOL as whole/part, OLDY as a reference, and extra morphology for QOKYLDDY/SOKEEDY would each be new choices without a written construction that selects them. SHCKHEDY twice remains two exact unresolved occurrences. No additional relation is seeded, no source-product chain is fabricated, and no unknown span becomes punctuation. The frozen core permits a genuine conditional dependency; the permitted small extensions did not produce a complete32-group reading.', '', 'ZL33/IT32/RF32 are alternate readings of one manuscript. ZL has complete paragraph flags; IT end and RF flags remain uncertain. ZL SALCHE\'DY and split S/OKEEDY, RF irregular SHEDY/SOLCHEDY/KESD forms and the final SAII@208;/SAIIN/SAIRN difference remain native and unread where not exactly licensed. These alternatives are not extra confirmations.', '', 'Owned Llull prose supplies an architectural precedent, not a source identification. GDT1137,1146,1147 remain unchanged. No word is confirmed; there is no significance, holdout or global transfer claim. No second lexical account or after-review repair is authorized.', '']
    return '\n'.join(lines)

def main():
    account = build_account()
    out = ROOT / EXP / 'artifacts'
    out.mkdir(exist_ok=True)
    account_path = out / 'AUTHOR_ACCOUNT.json'
    account_path.write_text(json.dumps(account, ensure_ascii=False, indent=2) + '\n')
    reading_path = ROOT / EXP / 'AUTHOR_READING.md'
    reading_path.write_text(render(account))
    files = [EXP / 'src/author.py', EXP / 'artifacts/AUTHOR_ACCOUNT.json', EXP / 'AUTHOR_READING.md']
    lock = {'schema_version': 1, 'frozen_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': account['status'], 'core_sha256': CORE_SHA, 'files': {str(p): sha((ROOT / p).read_bytes()) for p in files}, 'accounting': account['lexical_coverage'], 'native_groups': 97, 'policy_results': {e['policy']: e['conditional_core_result'] for e in account['policy_executions']}, 'diagnostic_cases_opened': False, 'after_review_repairs': False}
    (out / 'AUTHOR_LOCK.json').write_text(json.dumps(lock, indent=2) + '\n')
    (out / 'AUTHOR_RECEIPT.json').write_text(json.dumps({'frozen_utc': lock['frozen_utc'], 'lock_path': str(EXP / 'artifacts/AUTHOR_LOCK.json'), 'lock_sha256': sha((out / 'AUTHOR_LOCK.json').read_bytes()), 'scope': 'one locked author account; independent review not yet run'}, indent=2) + '\n')
    print(json.dumps({'status': account['status'], 'coverage': account['lexical_coverage'], 'lock_sha256': sha((out / 'AUTHOR_LOCK.json').read_bytes()), 'policies': lock['policy_results']}, indent=2))

if __name__ == '__main__':
    main()
