"""Frozen lexicons, explicit whole-frame reference rivals and complete gap audit."""
import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path

EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2];ART=EXP/'artifacts'
EDS=['ZL3b','IT2a','RF1b'];PAGES=['f77r','f17r','f21r','f32v','f29v']


def table(rows):
    out=io.StringIO();w=csv.DictWriter(out,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(rows);return out.getvalue()


def build():
    for path,digest in json.loads((EXP/'PREREG_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    spec=json.loads((EXP/'src/MODEL.json').read_text())
    frames=json.loads((ROOT/spec['frames']).read_text())['paragraph_frames']
    models=json.loads((ROOT/spec['lexicons']).read_text())['models']
    source=json.loads((ROOT/spec['source']).read_text())['groups']
    source=sorted(source,key=lambda r:(EDS.index(r['edition']),PAGES.index(r['page']),int(r['locus'].split('.')[1]),int(r['source_group_index'])))
    baseline={(r['model'],r['source_group_id']):r for r in csv.DictReader((ROOT/spec['baseline_bindings']).open(),delimiter='\t')}
    blocks=defaultdict(list);lines=defaultdict(list)
    for r in source:
        n=int(r['locus'].split('.')[1])
        ff=[i for i,(lo,hi) in enumerate(frames[r['page']],1) if lo<=n<=hi] if r['kind']=='P' else []
        assert r['kind']!='P' or len(ff)==1
        r=dict(r,block=r['page']+':P'+str(ff[0]) if ff else r['locus']+':LABEL')
        blocks[r['edition'],r['block']].append(r);lines[r['edition'],r['locus']].append(r)
    refs=[];intervals={};readings=[]
    for mid,m in models.items():
        lex=m['lexicon']
        for (ed,bid),rr in blocks.items():
            roles=[lex.get(r['ivtff_group_raw'],('', 'UNREAD'))[1] for r in rr]
            ids=[r['source_group_id'] for r in rr];positions={sid:i for i,sid in enumerate(ids)}
            material=[role=='MATERIAL' or (role=='PART' and i+1<len(rr) and roles[i+1]=='GENITIVE') for i,role in enumerate(roles)]
            nominal=[role in spec['ordinary_nominal_roles'] for role in roles]
            for i,r in enumerate(rr):
                if r['kind']=='P' and r['page']=='f77r' and int(r['locus'].split('.')[1])>=25:
                    readings.append({'model':mid,**r,'role':roles[i],'reading':lex[r['ivtff_group_raw']][0]+'?' if roles[i]!='UNREAD' else '⟦'+r['ivtff_group_raw']+'⟧'})
            for policy in spec['policies']:
                flow_material={}
                # Every flow is evaluated before continuations, without permitting later antecedents in new policies.
                for i in [j for j,r in enumerate(rr) if r['kind']=='P' and roles[j]=='FLOW']:
                    if policy=='LOCAL':head=positions.get(baseline[mid,ids[i]]['head_id'])
                    else:
                        valid=material if policy=='TYPED_BACK' else nominal
                        earlier=[j for j in range(i) if valid[j]];head=earlier[-1] if earlier else None
                    status=('NO_ANTECEDENT' if head is None else 'COMPATIBLE' if material[head]
                            else 'TYPE_CONFLICT' if roles[head] in ('VESSEL','PLACE') else 'UNRESOLVED_NOMINAL_TYPE')
                    flow_material[i]=(head,status)
                for i,r in enumerate(rr):
                    role=roles[i]
                    if r['kind']!='P' or role not in ('FLOW','CONTINUATION'):continue
                    if role=='FLOW':
                        participant,status=flow_material[i];head=participant
                    else:
                        if policy=='LOCAL':head=positions.get(baseline[mid,ids[i]]['head_id'])
                        else:
                            prior_flows=[j for j in range(i) if roles[j]=='FLOW'];head=prior_flows[-1] if prior_flows else None
                        if head is None:participant=None;status='NO_FLOW_ANTECEDENT'
                        else:
                            participant,status=flow_material[head]
                            if status!='COMPATIBLE':status='FLOW_'+status
                    def between(pos):
                        return list(range(min(pos,i)+1,max(pos,i))) if pos is not None else []
                    hi=between(head);pi=between(participant)
                    audit_gap=pi if participant is not None else hi
                    case_id='|'.join([policy,mid,r['source_group_id']])
                    intervals[case_id]={'head_gap':[ids[j] for j in hi],'participant_gap':[ids[j] for j in pi]}
                    new_material=[ids[j] for j in hi if material[j]] if role=='CONTINUATION' else []
                    qsource=rr[i+1] if role=='FLOW' and i+1<len(rr) and roles[i+1] in ('SOURCE','GOAL') else None
                    ref={'case_id':case_id,'policy':policy,'model':mid,'edition':ed,'block':bid,'source_group_id':ids[i],
                        'locus':r['locus'],'group_index':r['source_group_index'],'raw':r['ivtff_group_raw'],'role':role,
                        'head_id':ids[head] if head is not None else '',
                        'head_raw':rr[head]['ivtff_group_raw'] if head is not None else '',
                        'participant_id':ids[participant] if participant is not None else '',
                        'participant_raw':rr[participant]['ivtff_group_raw'] if participant is not None else '',
                        'participant_role':roles[participant] if participant is not None else '',
                        'status':status,'head_cross_line':bool(head is not None and rr[head]['locus']!=r['locus']),
                        'head_gap_groups':len(hi) if head is not None else '',
                        'unknown_head_gap_groups':sum(roles[j]=='UNREAD' for j in hi) if head is not None else '',
                        'participant_gap_groups':len(pi) if participant is not None else '',
                        'unknown_participant_gap_groups':sum(roles[j]=='UNREAD' for j in pi) if participant is not None else '',
                        'audit_gap_basis':'participant' if participant is not None else 'head',
                        'intervening_bare_nominals':json.dumps([ids[j] for j in audit_gap if nominal[j]]),
                        'intervening_copulas':json.dumps([ids[j] for j in audit_gap if roles[j]=='COPULA']),
                        'material_mentions_after_flow':json.dumps(new_material),
                        'immediate_path_id':qsource['source_group_id'] if qsource else '',
                        'immediate_path_reading':lex[qsource['ivtff_group_raw']][0] if qsource else '',
                        'meaning_confirmed':False}
                    refs.append(ref)
    result={'experiment':'GDT933','status':'CONDITIONAL_PARAGRAPH_REFERENCE_DRAFTS_NO_MEANING_SELECTION','source_groups':len(source),
            'models':{},'lexicons_changed':False,'new_words':0,'confirmed_words':0,'selected_translation':None,
            'development_seed':'M remains conditional, without promotion','new_admissions':0,'reserved_pages_opened':False,
            'statistical_significance_claimed':False,'independent_meaning_tests':0,'visual_relation_evidence_added':False}
    for mid in models:
        result['models'][mid]={}
        for ed in EDS:
            result['models'][mid][ed]={}
            for policy in spec['policies']:
                aa=[r for r in refs if (r['model'],r['edition'],r['policy'])==(mid,ed,policy)]
                result['models'][mid][ed][policy]={
                    'flow_status':dict(Counter(r['status'] for r in aa if r['role']=='FLOW')),
                    'continuation_status':dict(Counter(r['status'] for r in aa if r['role']=='CONTINUATION')),
                    'compatible_with_unread_gap':sum(r['status']=='COMPATIBLE' and r['unknown_participant_gap_groups']>0 for r in aa),
                    'continuations_with_intervening_material_mention':sum(bool(json.loads(r['material_mentions_after_flow'])) for r in aa if r['role']=='CONTINUATION')}
    out={'REFERENCE_CASES.tsv':table(refs),'INTERVALS.json':json.dumps(intervals,separators=(',',':'))+'\n',
         'RESULT.json':json.dumps(result,indent=2,ensure_ascii=False)+'\n'}
    for ed in EDS:
        doc=[f'# GDT933 — vollständige P2/P3-Entwürfe {ed}','',
             'Neun Wortwerte aus GDT932 unverändert. M=Rohr/Flüssigkeit/Fließen, V=Flüssigkeit/Anteil/Weiter.',
             'Alle Aussagen und Bezüge hypothetisch. Unbekannte Zwischenwörter bleiben ungeprüft; keine vollständige Absatzübersetzung.','']
        for n in range(25,49):
            locus='f77r.'+str(n);rr=lines[ed,locus]
            raw=''.join(('' if i==0 else ' / ' if 'UNCERTAIN' in r['left_separator'] else ' ')+r['ivtff_group_raw'] for i,r in enumerate(rr))
            doc+=['## '+locus+' — '+rr[0]['block'],'',f'`{raw}`','']
            for mid in models:
                aa=[a for a in readings if (a['model'],a['edition'],a['locus'])==(mid,ed,locus)]
                doc+=[mid+': '+' '.join(a['reading'] for a in aa),'']
                for policy in ('TYPED_BACK','NOMINAL_BACK'):
                    cc=[r for r in refs if (r['model'],r['edition'],r['locus'],r['policy'])==(mid,ed,locus,policy)]
                    for c in cc:
                        gap=str(c['unknown_participant_gap_groups'])+' ungelesene Gruppen zum Teilnehmer' if c['participant_id'] else 'Teilnehmerintervall OFFEN'
                        doc += [f"- {policy} #{c['group_index']} {c['raw']}: {c['status']}; Kopf {c['head_id'] or 'OFFEN'}; Teilnehmer {c['participant_id'] or 'OFFEN'}; {gap}; Ortszusatz {c['immediate_path_reading'] or 'OFFEN/kein unmittelbar geschriebener Zusatz'}."]
                    if cc:doc+=['']
        out['P2_P3_READING_'+ed+'.md']='\n'.join(doc).rstrip()+'\n'
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for name,content in build().items():
        if args.check:assert (ART/name).read_text()==content,name
        else:(ART/name).write_text(content)
    r=json.loads((ART/'RESULT.json').read_text());print(json.dumps({'status':r['status'],'ZL3b':{mid:r['models'][mid]['ZL3b'] for mid in r['models']}},indent=2))


if __name__=='__main__':main()
