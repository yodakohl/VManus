#!/usr/bin/env python3
"""Independent exact-group inventory, paragraph expansion and literal accounting."""
import argparse
import copy
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
ADMISSIONS = ['experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv',
              'experiments/yolo/gdt812_additional_page_semantic_bridge/src/PAGE_ADMISSIONS.tsv']
PROPOSAL = 'experiments/yolo/gdt820_grouped_predicate_repetition_context/src/ASCENT_TRIAL.json'
ATLAS = 'experiments/semantic_assumptions/results/source_separator_transcription.tsv'
EDITIONS = {'ZL3b':'zl3b_clean','IT2a':'it2a_clean','RF1b':'rf1b_clean'}
META = ['page','locus','kind','paragraph_start','paragraph_end','eva_clean','ivtff_raw']
GCOLS = ['source_group_id','edition','locus','page','source_group_index','source_group_count','paragraph_start','paragraph_end',
         'left_separator','right_separator','ivtff_group_raw','clean_ascii_fragments','clean_ascii_fragment_count',
         'legacy_surface_positions_1based','legacy_mapping_status']
MARKS = {'DEFINITE_SPACE':'.','UNCERTAIN_SMALL_SPACE':',','DRAWING_INTERRUPTION':'<->','DRAWING_INTERRUPTION_UNALIGNED':'<~>'}
BASE = {'qokaiin':'Luft?','qokain':'Wasser?','chedy':'wird?','sheedy':'wenn?','chedaiin':'ist?',
        'chealy':'kalt?','solkeey':'Dampf?','okaiin':'dessen?','daiin':'viel?'}
CONFIDENCE = 'C0_COMPLETION_MOTIVATED_NOT_LEXICAL_EVIDENCE'


def require(ok, message):
    if not ok: raise ValueError(message)


def exact(actual, expected):
    require(actual == expected, 'Independent reconstruction differs')


def rejected(actual, expected):
    try: exact(actual, expected)
    except ValueError: return True
    return False


def enc(value):
    return json.dumps(value, ensure_ascii=False)


def table(path, fields=None):
    with path.open() as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        if fields is not None: exact(reader.fieldnames, fields)
        return list(reader)


def query(path, columns, pages, count):
    command = ['./vmanus-exp','query-tsv',path,'--selector','page']
    for page in pages: command += ['--allow',page]
    command += ['--columns',','.join(columns),'--forbid-prefix','f84','--forbid-prefix','f84r']
    process = subprocess.run(command,cwd=ROOT,text=True,capture_output=True,check=True)
    stats = [json.loads(s[12:]) for s in process.stderr.splitlines() if s.startswith('GUARD_STATS ')]
    reader = csv.DictReader(io.StringIO(process.stdout),delimiter='\t')
    require(len(stats)==1 and reader.fieldnames==columns,'Guard schema')
    rows = list(reader)
    require(len(rows)==stats[0]['selected']==count and {r['page'] for r in rows}==set(pages),'Guard coverage')
    return rows,dict(command=command,stats=stats[0],projection_sha256=hashlib.sha256(process.stdout.encode()).hexdigest())


def clean(raw):
    raw = re.sub(r'\[([^:\]]+)(?::[^\]]*)?\]',lambda m:m[1],raw)
    raw = re.sub(r'\{[^}]*\}','',raw)
    raw = re.sub(r'<[^>]*>',' ',raw).translate(str.maketrans('','',"?!*'"))
    return [w for part in re.split(r'[\s.,;:=/\\|+\-]+',raw) if (w:=re.sub('[^A-Za-z]','',part).lower())]


def hit_class(raw):
    return 'EXACT' if raw=='raiin' else 'ASCII_ONLY' if 'raiin' in clean(raw) else 'NEITHER'


def group_line(groups):
    require(groups and groups[0]['left_separator']=='LINE_START' and groups[-1]['right_separator']=='LINE_END','Group endpoints')
    raw, fragments, position = '', [], 1
    for i,g in enumerate(groups):
        require(int(g['source_group_index'])==i+1 and int(g['source_group_count'])==len(groups),'Group coverage')
        require(g['source_group_id']==f"{g['edition']}|{g['locus']}|G{i+1:03}",'Group ID')
        require(all(g[k]==groups[0][k] for k in ['locus','page','edition','paragraph_start','paragraph_end']),'Group flags')
        emitted = clean(g['ivtff_group_raw']); exact(emitted,g['clean_ascii_fragments'].split())
        state = 'ZERO_ASCII_FRAGMENT' if not emitted else 'ONE_ASCII_FRAGMENT' if len(emitted)==1 else 'MULTI_ASCII_FRAGMENT'
        require(int(g['clean_ascii_fragment_count'])==len(emitted) and g['legacy_mapping_status']==state and
                g['legacy_surface_positions_1based']==','.join(map(str,range(position,position+len(emitted)))),'Fragment accounting')
        if i:
            require(groups[i-1]['right_separator']==g['left_separator'],'Separator adjacency')
            raw += MARKS[g['left_separator']]
        raw += g['ivtff_group_raw']; fragments += emitted; position += len(emitted)
    return raw,fragments


def validate_light(base_rows):
    """Only exact raiin glosses and the explicitly declared confidence may change."""
    phase='POST_FULL_CONTEXT_READING_SINGLE_RIVAL'; confidence='C0_POST_CONTEXT_RIVAL_NOT_LEXICAL_EVIDENCE'
    proposal=dict(phase=phase,whole='raiin',gloss_de='leicht?',
        sense='LOW_PHYSICAL_HEAVINESS_OF_A_CARRIER_NOT_SMALL_DOSE_MILDNESS_EASE_BRIGHTNESS_SPEED_OR_ASCENT',
        comparison_reference='Physical carrier and weight comparison class or surrounding medium remain unknown; do not insert water, air, equal volume or a substance into an unresolved occurrence.',
        base_trial='artifacts/LITERAL_TRIALS.tsv',confidence=confidence,new_admissions=0,dictionary_changed=False,meanings_validated=False,sealed_data=['f84','f84r'])
    exact(json.loads((EXP/'src/LIGHT_TRIAL.json').read_text()),proposal)
    light=copy.deepcopy(base_rows); replacements=0; source_count=0
    for row,original in zip(light,base_rows):
        words=json.loads(original['source_groups_json']); old=json.loads(original['literal_trial_json'])
        require(len(words)==len(old),'Light trial source consumption')
        new=[]
        for word,gloss in zip(words,old):
            if word=='raiin':
                require(gloss=='steigt?','Fixed ascent baseline'); new.append('leicht?'); replacements+=1
            else: new.append(gloss)
        source_count+=len(words); row['literal_trial_json']=enc(new); row['confidence']=confidence
        require(sum(a!=b for a,b in zip(old,new))==words.count('raiin'),'Only exact raiin changed')
    require(len(light)==195 and source_count==1724 and replacements==28,'Light annex counts')
    exact(table(EXP/'artifacts/LIGHT_TRIALS.tsv',list(light[0])),light)
    result=dict(experiment_id='GDT821',phase=phase,status='ONE_PHYSICAL_LIGHTNESS_RIVAL_NOT_TRANSLATION',context_loci=65,literal_rows=195,
        source_groups=1724,changed_exact_group_readings=28,new_admissions=0,new_image_inspections=0,dictionary_changed=False,
        meanings_validated=False,confirmed_lexemes=0,confirmed_plaintext_clauses=0,base_meanings_unchanged=True,
        forced_finite_predicate=False,referent_and_comparison_reference_unknown=True,sealed_data=['f84','f84r'])
    exact(json.loads((EXP/'artifacts/LIGHT_RESULT.json').read_text()),result)
    mutations={}
    for name,locus,edition,index in [('saiin_label_alias','f66r.12','ZL3b',0),('extended_entity_alias','f77r.34','RF1b',-1)]:
        changed=copy.deepcopy(light); row=next(r for r in changed if (r['locus'],r['edition'])==(locus,edition))
        words=json.loads(row['source_groups_json']); require(words[index]!='raiin','Genuine non-raiin mutation')
        glosses=json.loads(row['literal_trial_json']); glosses[index]='leicht?'; row['literal_trial_json']=enc(glosses)
        mutations[name]=rejected(changed,light)
    require(all(mutations.values()),'Light annex mutation rejection')
    return dict(status='PASS_INDEPENDENT_SAME_SOURCE_PHYSICAL_LIGHTNESS_RIVAL',literal_rows=195,source_groups=1724,changed_exact_group_readings=28,
        allowed_changed_fields=['literal_trial_json','confidence'],source_vectors_and_other_glosses_unchanged=True,
        negative_controls_rejected=mutations,meanings_validated=False,probe_imported_or_called=False,
        proposal_sha256=hashlib.sha256((EXP/'src/LIGHT_TRIAL.json').read_bytes()).hexdigest(),
        artifact_sha256={n:hashlib.sha256((EXP/'artifacts'/n).read_bytes()).hexdigest() for n in ['LIGHT_TRIALS.tsv','LIGHT_RESULT.json']})


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    spec=json.loads((EXP/'src/SPEC.json').read_text())
    exact(spec,dict(experiment_id='GDT821',admission_inputs=ADMISSIONS,expected_admitted_selectors=39,source_atlas=ATLAS,
        inherited_proposal=PROPOSAL,whole='raiin',exact_match='COMPLETE_VERBATIM_SOURCE_GROUP',
        context='COMPLETE_SOURCE_P_WITH_SEPARATE_L_OR_WHOLE_NON_P_RECORD',editions=EDITIONS,extended_glyph_expansion=False,
        new_admissions=0,dictionary_changed=False,meanings_validated=False,sealed_data=['f84','f84r']))
    proposal=json.loads((ROOT/PROPOSAL).read_text())
    exact(proposal,dict(phase='POST_GROUP_READING_C0_CONTINUATION',whole='raiin',gloss_de='steigt?',
        sense='PHYSICAL_UPWARD_MOTION_NOT_INCREASE_HEATING_EVAPORATION_COPULA_OR_DESCENT',
        selection='ALL_EXACT_RAIIN_LOCI_IN_172_CORE_PLUS_TWO_PREVIOUSLY_KNOWN_SAL_RAIIN_COMPARATORS',comparators=['f76r.51','f82r.24'],
        base_exact_glosses=BASE,confidence=CONFIDENCE,new_admissions=0,dictionary_changed=False,meanings_validated=False,sealed_data=['f84','f84r']))
    initial,added=[table(ROOT/p) for p in ADMISSIONS]; pages=sorted({r['source_selector'] for r in initial+added})
    require(len(initial)==35 and len(added)==4 and len(pages)==39 and all(r['decision']=='ADMITTED' for r in added) and
            not any(p.startswith('f84') for p in pages),'Admission union/seals')
    lines,g1=query('transcription/voynich_zl3b_lines.tsv',META,pages,1062)
    cross,g2=query('transcription/voynich_cross_transcription_lines.tsv',['page','locus',*EDITIONS.values()],pages,1062)
    atlas,g3=query(ATLAS,GCOLS,pages,18981)
    by={r['locus']:dict(r) for r in lines}
    require(len(by)==len(cross)==len({r['locus'] for r in cross})==1062,'Unique source loci')
    for r in cross:
        require(r['locus'] in by and by[r['locus']]['page']==r['page'] and by[r['locus']]['eva_clean']==r['zl3b_clean'],'Source join')
        by[r['locus']].update(r)
    hits=[r for r in atlas if hit_class(r['ivtff_group_raw'])=='EXACT']
    false=[r for r in atlas if hit_class(r['ivtff_group_raw'])=='ASCII_ONLY']
    targets={r['locus'] for r in hits}; require(len(hits)==28 and len(targets)==12 and not false,'Raw inventory')
    # Independent P-stream partition; only selected segments must be complete.
    partitions=[]
    for page in pages:
        prose=sorted([r for r in lines if r['page']==page and r['kind']=='P'],key=lambda r:int(r['locus'].split('.')[1]))
        segment=[]
        for row in prose:
            if segment and (row['paragraph_start']=='1' or segment[-1]['paragraph_end']=='1'):
                partitions.append(segment); segment=[]
            segment.append(row)
        if segment: partitions.append(segment)
    chosen=[]
    for segment in partitions:
        if not any(r['locus'] in targets for r in segment): continue
        require(segment[0]['paragraph_start']==segment[-1]['paragraph_end']=='1' and
                all(r['paragraph_start']=='0' for r in segment[1:]) and all(r['paragraph_end']=='0' for r in segment[:-1]),'Selected P boundaries')
        page=segment[0]['page']; first=int(segment[0]['locus'].split('.')[1]); last=int(segment[-1]['locus'].split('.')[1])
        block=[by[f'{page}.{n}'] for n in range(first,last+1)]
        require(all(r['kind'] in ['P','L'] for r in block),'Non-P/L inside P run')
        chosen.append(('P',block))
    chosen += [(by[loc]['kind'],[by[loc]]) for loc in targets if by[loc]['kind']!='P']
    chosen.sort(key=lambda item:(item[1][0]['page'],int(item[1][0]['locus'].split('.')[1])))
    blocks=[]; selected={}; locus_block={}
    for kind,block in chosen:
        bid=block[0]['locus']+'--'+block[-1]['locus']; triggers=sorted([r['locus'] for r in block if r['locus'] in targets],key=lambda l:int(l.split('.')[1]))
        blocks.append(dict(block_id=bid,page=block[0]['page'],kind=kind,first=block[0]['locus'],last=block[-1]['locus'],
            prose_loci=sum(r['kind']=='P' for r in block),separate_label_loci=enc([r['locus'] for r in block if r['kind']=='L']),triggers_json=enc(triggers)))
        for r in block:
            require(r['locus'] not in selected,'Duplicate selected record'); selected[r['locus']]=r; locus_block[r['locus']]=bid
    require(targets<=set(selected) and len(blocks)==9 and len(selected)==65,'Hit/context completeness')
    order=sorted(selected,key=lambda l:(by[l]['page'],int(l.split('.')[1]))); groups=[r for r in atlas if r['locus'] in selected]
    grouped=defaultdict(list)
    for r in groups: grouped[r['locus'],r['edition']].append(r)
    require(len(groups)==1724 and len(grouped)==195,'All-reader group coverage')
    contexts=[]; comparisons=[]; trials=[]; native={}; annotations={}; glosses=BASE|{'raiin':'steigt?'}
    for loc in order:
        r=by[loc]; target=int(loc in targets)
        contexts.append(dict(block_id=locus_block[loc],**{k:r[k] for k in META if k!='eva_clean'},target=target,
            readings_json=enc({rd:r[rd] for rd in EDITIONS.values()})))
        for edition,reader in EDITIONS.items():
            gs=sorted(grouped[loc,edition],key=lambda g:int(g['source_group_index'])); raw,fragments=group_line(gs); native[loc,edition]=raw
            if edition=='ZL3b':
                leading=re.match(r'^<![^>]*>',r['ivtff_raw']); body=r['ivtff_raw']
                if leading: annotations[loc]=leading[0]; body=body[len(leading[0]):]
                exact(raw,body.replace('<%>','').replace('<$>',''))
                require(all(gs[0][k]==r[k] for k in ['page','paragraph_start','paragraph_end']),'ZL source flags')
            words=[g['ivtff_group_raw'] for g in gs]; literal=[glosses.get(w,'['+w+']') for w in words]
            comparisons.append(dict(locus=loc,edition=edition,source_group_count=len(gs),raw_grouped_line=raw,
                flat_matches_current=int(fragments==r[reader].split()),exact_raiin_count=words.count('raiin')))
            trials.append(dict(block_id=locus_block[loc],page=r['page'],locus=loc,kind=r['kind'],edition=edition,target=target,
                source_group_ids_json=enc([g['source_group_id'] for g in gs]),source_groups_json=enc(words),separators_json=enc([g['right_separator'] for g in gs[:-1]]),
                literal_trial_json=enc(literal),confidence=CONFIDENCE))
    expected={'ADMITTED_SELECTORS.tsv':[dict(source_selector=p) for p in pages],'EXACT_HITS.tsv':hits,'CLEAN_ONLY_HITS.tsv':false,
        'BLOCKS.tsv':blocks,'CONTEXTS.tsv':contexts,'SOURCE_GROUPS.tsv':groups,'GROUP_COMPARISON.tsv':comparisons,'LITERAL_TRIALS.tsv':trials}
    expected={name:[{k:str(v) for k,v in r.items()} for r in rows] for name,rows in expected.items()}
    for name,rows in expected.items(): exact(table(EXP/'artifacts'/name,list(rows[0]) if rows else GCOLS),rows)
    doc=['# GDT821 all admitted exact raiin: source-group paragraphs','','Raw source groups, not decoded words. Source periods are spaces, not sentence stops.',
         'Leading locus-placement tags remain in CONTEXTS raw field; unknown entities are opaque.','']
    for loc in order:
        r=by[loc]; doc += [f"## {loc} [{r['kind']}] target={int(loc in targets)} P-start={r['paragraph_start']} P-end={r['paragraph_end']}",'']
        for edition in EDITIONS:
            doc += [edition+(': same source-group line as ZL3b.' if edition!='ZL3b' and native[loc,edition]==native[loc,'ZL3b'] else ': `'+native[loc,edition]+'`')]
        doc += ['']
    exact((EXP/'artifacts/FULL_READER.md').read_text(),'\n'.join(doc).rstrip()+'\n')
    result=dict(experiment_id='GDT821',status='ALL_ADMITTED_EXACT_RAIIN_FIXED_SPATIAL_TRIAL_NOT_TRANSLATION',admitted_selectors=39,admitted_pages=pages,
        inventory_source_loci=1062,inventory_source_groups=18981,exact_hit_group_readings=28,exact_hits_by_edition=dict(Counter(r['edition'] for r in hits)),
        clean_only_group_readings=0,target_loci=12,target_pages=sorted({by[l]['page'] for l in targets}),target_kinds=dict(Counter(by[l]['kind'] for l in targets)),
        blocks=9,complete_P_blocks=sum(b['kind']=='P' for b in blocks),context_loci=65,context_kinds=dict(Counter(r['kind'] for r in contexts)),source_groups=1724,
        group_comparisons=195,flat_matches=sum(r['flat_matches_current'] for r in comparisons),literal_rows=195,exact_raw_match_only=True,extended_glyph_expansion=False,
        all_admitted_exact_raiin=True,new_admissions=0,new_image_inspections=0,dictionary_changed=False,meanings_validated=False,confirmed_lexemes=0,
        confirmed_plaintext_clauses=0,guarded_queries=[g1,g2,g3],sealed_data=['f84','f84r'])
    require(result['flat_matches']==195 and sum(r['exact_raiin_count'] for r in comparisons)==28,'All-reader literal consumption')
    exact(json.loads((EXP/'artifacts/RESULT.json').read_text()),result)
    classifier={'exact':hit_class('raiin')=='EXACT','alternative_ASCII_only':hit_class('r[a:o]iin')=='ASCII_ONLY',
        'entity_not_alias':hit_class('@206;aiin')=='NEITHER','longer_whole_not_alias':hit_class('raiiny')=='NEITHER'}
    mutations={}
    mutations['nonP_label_omitted']=rejected([r for r in expected['CONTEXTS.tsv'] if r['locus']!='f66r.12'],expected['CONTEXTS.tsv'])
    mutations['nonhit_P_context_truncated']=rejected([r for r in expected['CONTEXTS.tsv'] if r['locus']!='f77r.38'],expected['CONTEXTS.tsv'])
    mutations['exact_hit_omitted']=rejected(expected['EXACT_HITS.tsv'][1:],expected['EXACT_HITS.tsv'])
    changed=copy.deepcopy(expected['LITERAL_TRIALS.tsv']); rf=next(r for r in changed if (r['locus'],r['edition'])==('f77r.34','RF1b'))
    literal=json.loads(rf['literal_trial_json']); literal[-1]='steigt?'; rf['literal_trial_json']=enc(literal)
    mutations['opaque_entity_translated']=rejected(changed,expected['LITERAL_TRIALS.tsv'])
    changed=copy.deepcopy(expected['LITERAL_TRIALS.tsv']); r=next(r for r in changed if (r['locus'],r['edition'])==('f82r.24','ZL3b'))
    words=json.loads(r['source_groups_json']); indices=[i for i,w in enumerate(words) if w=='raiin']; require(len(indices)==2,'Actual duplicate')
    literal=json.loads(r['literal_trial_json']); literal.pop(indices[1]); r['literal_trial_json']=enc(literal)
    mutations['second_raiin_omitted']=rejected(changed,expected['LITERAL_TRIALS.tsv'])
    mutations['meaning_promoted']=rejected(dict(result,meanings_validated=True),result)
    require(all(classifier.values()) and all(mutations.values()),'Controls')
    light_validation=validate_light(expected['LITERAL_TRIALS.tsv'])
    validation=dict(experiment_id='GDT821',status='PASS_INDEPENDENT_ADMITTED_RAIIN_CONTEXT_RECONSTRUCTION',admitted_selectors=39,
        exact_hit_group_readings=28,target_loci=12,complete_P_blocks=7,nonP_blocks=2,context_loci=65,source_groups=1724,literal_rows=195,
        clean_only_hits=0,synthetic_classifier_checks=classifier,negative_controls_rejected=mutations,leading_ZL_annotations=annotations,
        guarded_queries=[g1,g2,g3],runner_imported_or_called=False,meanings_validated=False,source_group_not_linguistic_word=True,legacy_files_modified=False,
        separate_post_lightness_annex=light_validation,
        checked_artifact_sha256={n:hashlib.sha256((EXP/'artifacts'/n).read_bytes()).hexdigest() for n in [*expected,'FULL_READER.md','RESULT.json']},
        inherited_proposal_sha256=hashlib.sha256((ROOT/PROPOSAL).read_bytes()).hexdigest())
    output=json.dumps(validation,indent=2,sort_keys=True)+'\n'; path=EXP/'artifacts/VALIDATION.json'
    if args.check: exact(path.read_text(),output)
    else: path.write_text(output)
    print(enc(dict(status=validation['status'],classifier_checks=len(classifier),negative_controls=len(mutations),meanings_validated=False)))


if __name__=='__main__':
    main()
