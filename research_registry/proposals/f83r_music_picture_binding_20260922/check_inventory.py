#!/usr/bin/env python3
"""Exact whole-key audit and exhaustive role renaming; no musical event simulator."""
import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'research_registry/proposals'

def read(name):
    return json.loads((BASE / name).read_text())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    proposal_path = BASE / 'raw_f83r_music_pictured_role_partition_20260922.json'
    proposal = json.loads(proposal_path.read_text())
    receipts = []
    for item in proposal['source_receipts']:
        actual = digest(ROOT / item['path'])
        assert actual == item['sha256'], item['path']
        receipts.append({'path': item['path'], 'sha256': actual})
    a = read('raw_f83r_rota_complete_persistent_voices_20260921.json')
    b = read('raw_f83r_rota_second_paragraph_frozen53_20260921.json')
    c = read('raw_f76v_rota_complete_frozen71_scope_variants_20260921.json')
    inventories = [a['lexicon'], b['new_18_lexical_entries'], c['new20_lexicon']]
    assert [len(x) for x in inventories] == [53, 18, 20]
    assert all(not (set(x) & set(y)) for x, y in itertools.combinations(inventories, 2))
    lexicon = inventories[0] | inventories[1] | inventories[2]
    assert len(lexicon) == 91
    assert b['frozen_parent']['all_53_lexical_entries_unchanged'] == inventories[0]
    assert c['frozen_family']['all71_entries_unchanged'] == inventories[0] | inventories[1]
    clauses = a['whole_paragraph_clauses'] + b['complete_new_block_clauses'] + c['complete_new_clauses']
    assert len(clauses) == 31
    assert sum(len(x['raw'].split()) for x in clauses) == 150
    assert all(w in lexicon for x in clauses for w in x['raw'].split())
    with (OUT / 'CAPTION_ROWS.tsv').open(newline='') as f:
        captions = list(csv.DictReader(f, delimiter='\t'))
    assert [(x['locus'], x['label_surface']) for x in captions] == [
        ('f83r.45','chtorol'), ('f83r.46','olsaiin'), ('f83r.50','sasoldal'), ('f83r.51','darolsy')]
    assert all(x['page'] == 'f83r' and x['label_token_count'] == '1' for x in captions)
    membership = []
    for row in captions:
        word = row['label_surface']
        membership.append({'locus': row['locus'], 'whole_form': word,
            'old71_member': word in inventories[0] | inventories[1],
            'added20_member': word in inventories[2], 'fixed91_member': word in lexicon,
            'whole_denotation': lexicon.get(word),
            'status': 'FIXED_VALUE_REQUIRES_CONTEXT_BINDING' if word in lexicon else 'UNKNOWN_UNDER_FIXED91',
            'component_id': row['component_id'], 'owner_class': row['owner_class'],
            'attachment_relation': row['attachment_relation']})
    # Enumerating names only. All musical consequences are inherited/manual,
    # not newly calculated schedules or evidence of an observed performance.
    fields = ['map_id', 'R0_leader', 'R1_first_follower', 'R2_later_follower',
              'U_P1_terminal_rest', 'L_P2_internal_rest', 'initial_onset_figures',
              'initially_pending_figures', 'cue_owner_R1', 'cue_owner_R2',
              'complete_clause_audit', 'caption_status', 'image_discriminates']
    rows = []
    upper = ('F83_UPPER_SPRAY', 'F83_MIDDLE_LOOP', 'F83_LOWER_DRIP')
    lower = ('LOWER_COUPLED_LEFT_FIGURE', 'LOWER_COUPLED_RIGHT_FIGURE')
    for rota in itertools.permutations(upper):
        for pes in itertools.permutations(lower):
            row = dict(zip(fields[:6], [f'M{len(rows)+1:02}', *rota, *pes]))
            row.update(initial_onset_figures='|'.join((rota[0], *pes)),
                initially_pending_figures='|'.join(rota[1:]), cue_owner_R1=rota[0],
                cue_owner_R2=rota[1], complete_clause_audit='REPORT:C01-C14,D01-D06,F01-F11',
                caption_status='ALL4_UNKNOWN_UNDER_FIXED91', image_discriminates='NO_BOUND_BRIDGE')
            rows.append(row)
    assert len(rows) == 12
    assert len({tuple(r[x] for x in fields[1:6]) for r in rows}) == 12
    with (OUT / 'ROLE_MAPS.tsv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fields, delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    result = {'status': 'EXACT_INVENTORY_AUDIT_PASS_CROSSMODAL_BINDING_INCOMPLETE',
        'proposal_sha256': digest(proposal_path), 'source_receipts': receipts,
        'inventory_sizes': [53,18,20], 'fixed_whole_values':91,
        'inherited_dictionary_copies_exact':True, 'complete_projected_clauses':31,
        'complete_projected_positions':150, 'caption_membership':membership,
        'figure_role_bijections':12, 'event_simulation_performed':False,
        'new_meaning_assignments':0, 'independent_meaning_confirmation':False,
        'manual_semantics_location':'REPORT.md',
        'local_input_sha256':{n:digest(OUT/n) for n in ('DECISION.md','CAPTION_ROWS.tsv','PANEL_ROWS.tsv')}}
    (OUT / 'INVENTORY_CHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'], 'whole_values':91,
        'caption_hits':sum(x['fixed91_member'] for x in membership), 'maps':12,
        'clauses':31,'projected_positions':150}))

if __name__ == '__main__':
    main()
