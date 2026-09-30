"""Whole-context alignment of manually hypothesized efficacy/material readings."""
import csv, hashlib, io, json, subprocess
from collections import defaultdict, Counter
from pathlib import Path
D=Path('research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929')
OLD=Path('experiments/yolo/gdt1104_source_head_consumer_contrast/artifacts/RETAINED_SOURCE.json')
SOURCE=Path('experiments/semantic_assumptions/results/source_separator_transcription.tsv')
ALLOW=Path('experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv')
COLS='source_group_id,edition,page,locus,kind,code,source_row_index,source_group_index,paragraph_start,paragraph_end,ivtff_group_raw,left_separator,right_separator'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def make():
    units=[]
    for u in json.loads((D/'BM_COMPLETE_CONTEXTS.json').read_text()):
        units.append({'id':f"{u['edition']}|f56r|{u['unit']}",'native':u['boundary_basis']=='native_flags','lines':[l['groups'] for l in u['lines']]})
    units+=json.loads((D/'BR_SOURCE.json').read_text())['units']
    old=json.loads(OLD.read_text())
    for e in ('ZL3b','IT2a','RF1b'):
        lines=defaultdict(list)
        for r in old['projected_rows']:
            if r['edition']==e and r['page']=='f29v' and r['kind']=='P' and int(r['locus'].rsplit('.',1)[1])<=4:
                lines[r['locus']].append(r)
        ls=[sorted(l,key=lambda r:int(r['source_group_index'])) for _,l in sorted(lines.items(),key=lambda v:int(v[0].rsplit('.',1)[1]))]
        assert len(ls)==4
        units.append({'id':f'{e}|f29v|1-4','native':e!='RF1b','lines':ls})
    assert 'f115v' in ALLOW.read_text().splitlines()
    cmd=['./vmanus-exp','query-tsv',str(SOURCE),'--selector','page','--allow','f115v','--columns',COLS]
    proc=subprocess.run(cmd,text=True,capture_output=True,check=True)
    rows=list(csv.DictReader(io.StringIO(proc.stdout),delimiter='\t'))
    assert len(rows)==1219 and {r['page'] for r in rows}=={'f115v'}
    chosen=[]
    for e in ('ZL3b','IT2a'):
        lines=defaultdict(list)
        for r in rows:
            if r['edition']==e and r['kind']=='P':lines[r['locus']].append(r)
        current=[]
        for line in sorted(lines.values(),key=lambda l:int(l[0]['source_row_index'])):
            line.sort(key=lambda r:int(r['source_group_index']))
            if any(r['paragraph_start']=='1' for r in line):
                assert not current
            current.append(line)
            if any(r['paragraph_end']=='1' for r in line):
                flat=[r for l in current for r in l]
                if any(flat[i]['ivtff_group_raw']=='qotchy' and flat[i+1]['ivtff_group_raw']=='chody' for i in range(len(flat)-1)):
                    assert any(r['paragraph_start']=='1' for r in current[0])
                    chosen.append({'id':f"{e}|f115v|{current[0][0]['locus']}-{line[0]['locus']}",'native':True,'lines':current})
                current=[]
        assert not current
    assert len(chosen)==2
    selected_loci={r['locus'] for u in chosen for l in u['lines'] for r in l}
    rf=defaultdict(list)
    for r in rows:
        if r['edition']=='RF1b' and r['kind']=='P' and r['locus'] in selected_loci:rf[r['locus']].append(r)
    chosen.append({'id':'RF1b|f115v|unmarked8-10','native':False,'lines':[sorted(l,key=lambda r:int(r['source_group_index'])) for _,l in sorted(rf.items(),key=lambda v:int(v[0].rsplit('.',1)[1]))]})
    units+=chosen
    receipts={'inputs':{str(p):sha(p) for p in [D/'BM_COMPLETE_CONTEXTS.json',D/'BR_SOURCE.json',OLD,SOURCE,ALLOW]},'guard_command':cmd,'guard_stderr':proc.stderr.strip(),'projected_page_groups':len(rows),'selected_f115_groups':sum(len(l) for u in chosen for l in u['lines']),'previous_project_exposure':True,'reserved_confirmation':False,'sealed':['f84','f84r']}
    packet={'units':units,'receipts':receipts}
    (D/'BT_SOURCE.json').write_text(json.dumps(packet,indent=2,ensure_ascii=False)+'\n')
    return packet

def align(p):
    rows=[]; relations=[];counts=Counter();md=['# BT: vollständige Rohkontexte mit partiellen LIVING/STOCK-Lesungen','Alle Bedeutungen angesetzt. Keine Absatzübersetzung. Unbekannte Gruppen bleiben sichtbar.\n']
    common={'qokchy':'C0:einnehmen/verabreichen','chotol':'C0:äußere Anwendung','chody':'C0:innere Anwendung','chol':'C0:Arzneimaterial M','schol':'C0:Teil/Posten von M; Bezug ungebunden'}
    for u in p['units']:
        md.append(f"## {u['id']} ({'native' if u['native'] else 'unmarkiertes Vergleichsfenster'})\n")
        for line in u['lines']:
            md.append(f"{line[0]['locus']} Roh: `{' '.join(r['ivtff_group_raw'] for r in line)}`\n")
            per={c:[] for c in ('LIVING','STOCK')}
            for pos,r in enumerate(line):
                f=r['ivtff_group_raw']
                val=common.get(f,f'UNGELESEN<{f}>')
                if f=='s' and pos+1<len(line) and line[pos+1]['ivtff_group_raw']=='chol':
                    val='C0:Teil/Posten von (nur gebundener Ausdruck s chol)'
                values={'LIVING':val,'STOCK':val}
                if f=='qotchy':
                    values={'LIVING':'C0:reinigende/ausscheidende Wirkung am Körper','STOCK':'C0:gereinigtes/abgetrenntes Arzneimaterial'}
                    relations.append({'unit':u['id'],'source_group_id':r['source_group_id'],'locus':r['locus'],'whole_line':' '.join(x['ivtff_group_raw'] for x in line),'LIVING_subject':'medicine; local identity UNBOUND','LIVING_affected':'living recipient IMPLICIT_UNBOUND','STOCK_affected':'drug stock/portion UNBOUND','distinguishing_statement':'NOT_READ','independent_confirmation_capacity':0})
                rows.append({'unit':u['id'],'source_group_id':r['source_group_id'],'locus':r['locus'],'raw':f,**values})
                counts[(r['edition'],'groups')]+=1
                counts[(r['edition'],'unread' if values['LIVING'].startswith('UNGELESEN') else 'hypothesized')]+=1
                for c in per:per[c].append(values[c])
            for c in per:md.append(c+': '+' | '.join(per[c])+'\n')
    ids=[r['source_group_id'] for r in rows]
    assert len(ids)==len(set(ids))
    for fname,rs in [('BT_ALIGNMENT.tsv',rows),('BT_RELATIONS.tsv',relations)]:
        with (D/fname).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs)
    (D/'BT_READINGS.md').write_text('\n'.join(md).rstrip()+'\n')
    result={'phase':'EXPLORATORY_C0','groups':len(rows),'counts':{e:{k:counts[e,k] for k in ['groups','hypothesized','unread']} for e in ['ZL3b','IT2a','RF1b']},'qotchy_rows':len(relations),'native_units':sum(u['native'] for u in p['units']),'RF_windows':sum(not u['native'] for u in p['units']),'candidates':{'LIVING':'C0_UNSELECTED','STOCK':'C0_UNSELECTED'},'newly_read_second_pair':{'locus':'f115v.9','full_native_unit':'f115v.8-10','raw_triplet':'qotchy chody qotain','readers':['ZL3b','IT2a','RF1b'],'independent_confirmation':False},'source_specific_803_package_tested':False,'seed_coats_colour_values_supplied':False,'typed_body_or_stock_output_discriminator_read':False,'confirmed_words':0,'independent_confirmation_capacity':0,'significance':False,'decision':'KEEP_EXPLICIT_EFFICACY_VS_MATERIAL_STATE_FORK_NO_PREFERRED_MEANING'}
    (D/'BT_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    import sys
    p=make() if '--fetch' in sys.argv else json.loads((D/'BT_SOURCE.json').read_text())
    align(p)
