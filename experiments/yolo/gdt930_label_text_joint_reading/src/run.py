"""Render a frozen small reading hypothesis; no decoder or parameter search."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
PAGES = ['f77r','f17r','f21r','f32v','f29v']
EDITIONS = ['ZL3b','IT2a','RF1b']


def table(rows, fields):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fields, delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def loc_key(row):
    return (PAGES.index(row['page']),int(row['locus'].split('.')[1]),int(row['source_group_index']))


def block(row, model):
    if row['kind'] != 'P':
        return row['locus'] + ':LABEL'
    number = int(row['locus'].split('.')[1])
    matches = [i for i,(lo,hi) in enumerate(model['paragraph_frames'][row['page']],1) if lo <= number <= hi]
    assert len(matches) == 1
    return f"{row['page']}:P{matches[0]}"


def build():
    for f,digest in json.loads((EXP/'MODEL_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((EXP/f).read_bytes()).hexdigest() == digest, f
    model = json.loads((EXP/'src/MODEL.json').read_text())
    rows = json.loads((EXP/'artifacts/SOURCE.json').read_text())['groups']
    models = {m['id']:m for m in model['models']}
    bases = {p['base']:p for p in model['pairs']}
    marked = {p['marked']:p for p in model['pairs']}
    assert len(bases) == len(marked) == 4 and not set(bases) & set(marked)
    alignment, consequences, label_rows = [], [], []
    previous = {}
    sorted_rows = sorted(rows,key=lambda r:(EDITIONS.index(r['edition']),loc_key(r)))
    for row in sorted_rows:
        raw = row['ivtff_group_raw']; bid = block(row,model)
        ed = row['edition']; source_id = row['source_group_id']
        key = (ed,bid)
        prior = previous.get(key) if row['kind'] == 'P' else None
        a = {'source_group_id':source_id,'edition':ed,'block':bid,'locus':row['locus'],
             'group_index':row['source_group_index'],'kind':row['kind'],'raw':raw,
             'left_separator':row['left_separator'],'right_separator':row['right_separator']}
        for mid,m in models.items():
            if raw in bases:
                a[mid] = bases[raw]['id']+'?'
            elif raw in marked:
                pair = marked[raw]
                a[mid] = m['marked_template'].format(name=pair['id'])+'?'
                if mid != 'N' and row['kind'] == 'P':
                    status = ('NO_LEFT_GROUP' if prior is None else
                              'LEFT_IS_MARKED_FORM' if prior['ivtff_group_raw'] in marked else
                              'ASSUMED_BASE_HEAD' if prior['ivtff_group_raw'] in bases else 'HEAD_UNTRANSLATED')
                    head = prior['source_group_id'] if prior else ''
                    endpoint = pair['id']+' (concept, not identified individual)'
                    direction = (endpoint+' -> '+head if mid == 'S' else head+' -> '+endpoint)
                    consequences.append({'edition':ed,'model':mid,'source_group_id':source_id,
                        'locus':row['locus'],'group_index':row['source_group_index'],'raw':raw,'pair':pair['id'],
                        'head_source_group_id':head,'head_raw':prior['ivtff_group_raw'] if prior else '',
                        'left_separator':row['left_separator'],
                        'attachment_status':status,'relation':m['relation'],'proposed_direction':direction,
                        'semantic_credit':'0; stipulated reading only'})
            else:
                a[mid] = '⟦'+raw+'⟧'
        alignment.append(a)
        if row['kind'] == 'P':
            previous[key] = row
        elif row['page'] == 'f77r':
            exact = [x['source_group_id'] for x in sorted_rows if x['edition']==ed and x['kind']=='P' and x['ivtff_group_raw']==raw]
            q_exact = [x['source_group_id'] for x in sorted_rows if x['edition']==ed and x['kind']=='P' and x['ivtff_group_raw']=='q'+raw]
            label_rows.append({'edition':ed,'locus':row['locus'],'source_group_id':source_id,'raw':raw,
                'exact_prose':json.dumps(exact),'literal_q_plus_prose':json.dumps(q_exact),
                'candidate_pair':bases[raw]['id'] if raw in bases else '',
                'raw_form_status':'UNCERTAIN_FRAGMENT' if 'UNCERTAIN' in (row['left_separator']+row['right_separator']) else 'SOURCE_GROUP',
                'hypothesis_status':'DECLARED_WHOLE_PAIR' if raw in bases else 'NOT_IN_CANDIDATE_INVENTORY',
                'meaning':'Neither identity nor a productive prefix meaning established'})
    outputs = {'ALIGNMENT.tsv':table(alignment,list(alignment[0])),
               'CONSEQUENCES.tsv':table(consequences,list(consequences[0])),
               'LABEL_REUSE.tsv':table(label_rows,list(label_rows[0]))}
    counts = []
    for ed in EDITIONS:
        rr = [r for r in sorted_rows if r['edition']==ed]
        raw_counts = Counter(r['ivtff_group_raw'] for r in rr)
        for p in model['pairs']:
            counts.append({'edition':ed,'pair':p['id'],'base':p['base'],'base_count':raw_counts[p['base']],
                           'marked':p['marked'],'marked_count':raw_counts[p['marked']]})
        doc = [f'# GDT930 — vollständige Quellausrichtung {ed}', '',
               'C0-Hypothesen, keine vollständige Übersetzung. A/B/C/D sind unentzifferte Begriffe; A/B haben mögliche Bildbezüge.',
               'Nur acht vollständige Rohformen werden angesetzt. ⟦…⟧ bleibt ungelesen; ? markiert eine Hypothese.',
               'Die sichtbaren Quelldaten behalten Entitäten und unsichere Trenner. Gemeinsame Absatzrahmen sind Arbeitsgrenzen.', '']
        for mid,m in models.items():
            doc += ['## '+mid+' — '+m['title'],'',m['claim'],'']
            current = None
            lines = defaultdict(list)
            for a in alignment:
                if a['edition']==ed:
                    lines[a['locus']].append(a)
            for locus,aa in lines.items():
                if aa[0]['block'] != current:
                    current = aa[0]['block']; doc += ['### '+current,'']
                raw = ''.join(('' if i==0 else ' / ' if 'UNCERTAIN' in a['left_separator'] else ' ') + a['raw'] for i,a in enumerate(aa))
                reading = ' '.join(a[mid] for a in aa)
                separators = ' | '.join(f"{a['group_index']}:{a['right_separator']}" for a in aa[:-1] if a['right_separator']!='DEFINITE_SPACE')
                doc += [f'**{locus}** `{raw}`', '', reading,'']
                if separators: doc += ['Quelltrenner: '+separators,'']
        outputs[f'READING_{ed}.md'] = '\n'.join(doc).rstrip()+'\n'
    outputs['PAIR_COUNTS.tsv'] = table(counts,list(counts[0]))
    edge_fields = ['edge_id','batch_id','page','physical_folio','diagram_unit_id','pivot_visual_id','pivot_locus',
                   'target_visual_id','target_locus','relation_type','direction_basis','ownership_basis',
                   'geometry_only_selection','source_manifest_id','page_crop_sha256','pivot_crop_sha256',
                   'target_crop_sha256','source_aware_localizer','relation_reviewer','relation_confidence',
                   'ambiguity_state','formal_access_state','fold_assignment','eligibility_status']
    packet = []; packet_members = {}; seen_locus_pairs = {}
    for r in sorted_rows:
        if r['edition'] != 'ZL3b' or r['kind'] != 'P': continue
        for p in model['pairs']:
            if p['image_label'] and r['ivtff_group_raw'] in (p['base'],p['marked']):
                edge_key = (p['image_label'],r['locus'])
                if edge_key in seen_locus_pairs:
                    packet_members[seen_locus_pairs[edge_key]].append(r['source_group_id'])
                    continue
                e = dict.fromkeys(edge_fields,'NONE')
                e.update(edge_id='GDT930_'+str(len(packet)+1),batch_id='GDT930_EXPOSED_NOMINAL_HYPOTHESIS',
                    page='f77r',physical_folio='f77',diagram_unit_id='WHOLE_PAGE_NO_CERTIFIED_OWNER',
                    pivot_visual_id='UNASSIGNED_REGION',pivot_locus=p['image_label'],target_visual_id='UNASSIGNED_TEXT_HEAD',
                    target_locus=r['locus'],relation_type='EXACT_OR_EXPLICIT_PAIRED_WHOLE',
                    direction_basis='NONE_WRITTEN_FORM_ONLY',ownership_basis='NO_IDENTIFIED_SEMANTIC_ENDPOINT',
                    geometry_only_selection='FALSE',source_manifest_id='GDT930',
                    page_crop_sha256=json.loads((EXP/'src/VISUAL_NOTES.json').read_text())['image_sha256'],
                    source_aware_localizer='root_exposed_development',relation_reviewer='same_root_not_independent',
                    relation_confidence='LOW',ambiguity_state='HYPOTHESIS_NOT_AUTHORIAL_RELATION',
                    formal_access_state='UNSEALED_ALREADY_INSPECTED',fold_assignment='EXPLORATORY',
                    eligibility_status='INELIGIBLE_EXPOSED_FORM_RELATION')
                packet.append(e)
                seen_locus_pairs[edge_key] = e['edge_id']
                packet_members[e['edge_id']] = [r['source_group_id']]
    outputs['RELATION_PACKET.tsv'] = table(packet,edge_fields)
    outputs['PACKET_MEMBERS.json'] = json.dumps(packet_members,indent=2)+'\n'
    totals = {}
    for ed in EDITIONS:
        rr = [r for r in sorted_rows if r['edition']==ed]
        known = sum(r['ivtff_group_raw'] in bases or r['ivtff_group_raw'] in marked for r in rr)
        cc = [c for c in consequences if c['edition']==ed and c['model']=='S']
        totals[ed] = {'source_groups':len(rr),'hypothesis_groups':known,'untranslated_groups':len(rr)-known,
            'marked_occurrences':len(cc),'attachment_statuses':dict(Counter(c['attachment_status'] for c in cc)),
            'f77_label_loci':len({r['locus'] for r in rr if r['page']=='f77r' and r['kind']!='P'}),
            'prose_blocks':len({block(r,model) for r in rr if r['kind']=='P'})}
    result = {'experiment':'GDT930','status':'EXPLORATORY_NOMINAL_CORE_READING_UNDERDETERMINED',
        'editions':totals,'models':list(models),'fixed_complete_pairs':4,'source_groups_total':len(rows),
        'candidate_differences':'N asserts no added relation; L belongs-to, S source, T target. Same coverage is not a ranking.',
        'certified_visual_owner_edges':0,'independently_identified_content_words':0,'confirmed_translated_words':0,
        'independent_confirmation_capacity':'None established in this exposed development packet.',
        'new_admissions':0,'reserved_pages_opened':False,'decoder_built':False,
        'model_selected_as_translation':None,'scientific_meanings_validated':False,
        'hypothesis_ceiling':'Four nominal-core pairings and their stipulated relations. Missing heads and unknowns retained; no general q morpheme.',
        'source_sha256':hashlib.sha256((EXP/'artifacts/SOURCE.json').read_bytes()).hexdigest(),
        'model_sha256':hashlib.sha256((EXP/'src/MODEL.json').read_bytes()).hexdigest()}
    outputs['RESULT.json'] = json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    return outputs


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args = parser.parse_args()
    for name,text in build().items():
        path=EXP/'artifacts'/name
        if args.check: assert path.read_text()==text, name
        else: path.write_text(text)
    result = json.loads((EXP/'artifacts/RESULT.json').read_text())
    print(json.dumps({'status':result['status'],'editions':result['editions']},ensure_ascii=False))


if __name__ == '__main__':
    main()
