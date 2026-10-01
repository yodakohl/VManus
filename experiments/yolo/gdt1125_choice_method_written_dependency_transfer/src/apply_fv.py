"""Literal FV eligibility/finite-production accounting; no semantic executor."""
import csv
import hashlib
import itertools
import json
import re
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    specpath = E / 'src/SPEC.json'
    spec = json.loads(specpath.read_text())
    opening = json.loads((E / 'artifacts/OPEN_RECEIPT.json').read_text())
    assert spec['status'] == 'PREOPEN_FROZEN'
    assert opening['status'] == 'ROOT_EXPLICIT_APPLICATION_GO'
    assert opening['spec_sha256'] == digest(specpath)
    for path, expected in spec['input_hashes'].items():
        assert digest(ROOT / path) == expected, path
    source = E / 'artifacts/APPLICATION_PACKET.json'
    assert opening['source_packet_sha256'] == digest(source)
    modelpath = ROOT / spec['candidate_json']['FV']
    model = json.loads(modelpath.read_text())
    packet = json.loads(source.read_text())
    cards = model['dictionary']
    output = []
    cases = []
    for side in ['F75V', 'F104V']:
        for edition in ['ZL3b', 'IT2a', 'RF1b']:
            uid = 'FW_' + side + '_CURRENT'
            groups = [g for g in packet['groups'] if g['unit_id'] == uid and g['edition'] == edition]
            by_locus = {}
            for g in groups:
                by_locus.setdefault(g['locus'], []).append(g)
            barriers, frames, line_matches, pairs = [], [], [], []
            for locus, gs in by_locus.items():
                analyses = []
                for g in gs:
                    raw = g['ivtff_group_raw']
                    parts = model['lexical_packing'].get(raw, [raw])
                    alts = [[cards[p]['tag'] for p in parts]] if all(p in cards for p in parts) else []
                    if raw == 'qokeedy':
                        alts.append([cards['qokeed']['tag'], cards['y']['tag']])
                    analyses.append(alts)
                # R17's two COMPLETE nominal frames, never a blanket noun cast.
                kind_tags = {'KIND_A', 'KIND_B', 'SOURCE_KIND'}
                def has_tag(i, tag):
                    return i < len(gs) and [tag] in analyses[i]
                def kind_slot(i):
                    return i < len(gs) and (any(len(a) == 1 and a[0] in kind_tags for a in analyses[i]) or not analyses[i] and re.fullmatch('[a-z]+', gs[i]['ivtff_group_raw']) is not None)
                for i in range(len(gs)):
                    slots = []
                    if i + 5 < len(gs) and has_tag(i, 'MATERIAL_SPEC_HEAD') and kind_slot(i+1) and has_tag(i+2, 'REPLACE_SPEC') and has_tag(i+3, 'OLD_ROLE_REF') and kind_slot(i+4) and has_tag(i+5, 'SELECT_ASSEMBLE_FINISH'):
                        slots = [i+1, i+4]
                    elif i + 4 < len(gs) and has_tag(i, 'SOURCE_OF') and kind_slot(i+1) and has_tag(i+2, 'PART_SPEC_HEAD') and has_tag(i+3, 'REPLACE_SPEC') and has_tag(i+4, 'OLD_ROLE_REF'):
                        slots = [i+1]
                    if slots:
                        frames.append({'locus': locus, 'rule': 'R17', 'slot_source_ids': [gs[k]['source_group_id'] for k in slots]})
                        for k in slots:
                            if not analyses[k]:
                                analyses[k] = [['OPAQUE_SOURCE_KIND_R17']]
                    if i+1 < len(gs) and gs[i]['ivtff_group_raw'] == 'chey' and gs[i+1]['ivtff_group_raw'] == 'tal':
                        pairs.append({'source_ids': [gs[i]['source_group_id'], gs[i+1]['source_group_id']], 'seam': gs[i]['right_separator']})
                tags = []
                if all(analyses):
                    for combination in itertools.product(*analyses):
                        flat = [t for a in combination for t in a]
                        tags.append(flat)
                matched = [p['id'] for p in model['finite_clause_productions'] if p['terminal_pattern'] in tags]
                line_matches.append({'locus': locus, 'exact_base_productions': matched, 'qualification': 'No prose-only variant or R17 generic production is automatically inferred; manual frozen-rule audit remains authoritative.'})
                for g, alts in zip(gs, analyses):
                    if not alts:
                        barriers.append({'source_id': g['source_group_id'], 'raw': g['ivtff_group_raw'], 'kind': 'MARKED_OR_UNLISTED_POSSIBLE_CONTROL'})
                    output.append({'source_id': g['source_group_id'], 'unit': uid, 'reader': edition, 'locus': locus, 'raw': g['ivtff_group_raw'], 'alternatives': alts, 'source_retained': True})
            selectors = [g['source_group_id'] for g in groups if g['ivtff_group_raw'] in ['dalshdy', 'tchedy']]
            references = [g['source_group_id'] for g in groups if g['ivtff_group_raw'] == 'chedy']
            consumer_candidates = [g['source_group_id'] for g in groups if g['ivtff_group_raw'] in ['qokal', 'qokchdy', 'cheedar']]
            if not pairs:
                status = 'UNBOUND_OPERATOR_ALTERNATE'
            elif barriers or not selectors or len(consumer_candidates) < 2:
                status = 'NO_CAPACITY_FOR_DECLARED_COMPLETE_TRANSFER'
            else:
                status = 'LITERAL_ELIGIBILITY_ONLY_MANUAL_TYPED_AUDIT_REQUIRED'
            cases.append({'candidate': 'FV_C0_1', 'unit': uid, 'reader': edition, 'groups': len(groups), 'literal_status': status, 'exact_pairs': pairs, 'first_unknown_barrier': barriers[0] if barriers else None, 'all_unknown_barriers': barriers, 'R17_complete_frames': frames, 'exact_selector_ids': selectors, 'exact_result_reference_ids': references, 'consumer_inventory_candidates_not_bound_consumers': consumer_candidates, 'line_base_production_matches': line_matches, 'scope': 'CURRENT_ONLY_NO_PREVIOUS_DONATION', 'executed_semantic_program': False, 'confirmed_words': 0})
    result = {'status': 'LITERAL_FIXED_FV_ACCOUNTING_NOT_SEMANTIC_OR_GRAMMAR_PASS', 'spec_sha256': digest(specpath), 'source_packet_sha256': digest(source), 'candidate_sha256': digest(modelpath), 'cases': cases, 'rows': output, 'frozen_model_changed': False, 'independent_confirmation_capacity': 0}
    (E / 'artifacts/FV_TRANSFER.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    with (E / 'artifacts/FV_TRANSFER.tsv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for row in output:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v for k, v in row.items()})
    print(json.dumps({'cases': [{k: c[k] for k in ['unit','reader','groups','literal_status']} for c in cases], 'qualification': result['status']}))


if __name__ == '__main__':
    main()
