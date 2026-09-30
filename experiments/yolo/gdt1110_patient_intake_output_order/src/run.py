#!/usr/bin/env python3
import csv,io,json,hashlib,subprocess,datetime
from pathlib import Path
from collections import Counter
E=Path(__file__).resolve().parents[1]; R=E.parents[2]; O=E/'artifacts'
def read(p): return list(csv.DictReader(io.StringIO(p),delimiter='\t'))
def query(path,cols,pages):
    cmd=[str(R/'vmanus-exp'),'query-tsv',str(R/path),'--selector','page']
    for page in pages: cmd+=['--allow',page]
    cmd+=['--columns',','.join(cols),'--forbid-prefix','f84','--forbid-prefix','f84r']
    r=subprocess.run(cmd,cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    return read(r.stdout)
def main():
    m=json.loads((E/'src/MODEL.json').read_text())
    for p,h in m['input_hashes'].items(): assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    pages=sorted({x['page'] for x in read((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').read_text())})
    assert len(pages)==179 and not any(p.startswith('f84') or p=='f116v' for p in pages)
    b='experiments/yolo/gdt822_qokeey_physical_fire_context/artifacts/'
    blocks=query(b+'BLOCKS.tsv',['block_id','page','kind','complete','first','last','loci_json','qokeey_targets_json'],pages)
    contexts=query(b+'CONTEXTS.tsv',['block_id','page','locus','kind','paragraph_start','paragraph_end','ivtff_raw','target','inherited821','readings_json'],pages)
    cols=['source_group_id','edition','locus','page','source_group_index','source_group_count','paragraph_start','paragraph_end','left_separator','right_separator','ivtff_group_raw','clean_ascii_fragments','clean_ascii_fragment_count','legacy_surface_positions_1based','legacy_mapping_status']
    groups=query(b+'SOURCE_GROUPS.tsv',cols,pages)
    selected=[x for x in blocks if x['kind']=='P' and x['complete']=='1']; assert selected
    c={x['locus']:x for x in contexts}; by={}
    for g in groups: by.setdefault((g['locus'],g['edition']),[]).append(g)
    cases=[]; doc=['# GDT1110 complete exposed block reader','','Only two WHOLE forms mapped provisionally. UNKNOWN retains every other group. Labels remain separate; no subject, material, heat or purpose supplied.','']
    for b0 in selected:
        loci=json.loads(b0['loci_json']); p=[l for l in loci if c[l]['kind']=='P']; assert p and c[p[0]]['paragraph_start']=='1' and c[p[-1]]['paragraph_end']=='1'
        for ed in ['ZL3b','IT2a','RF1b']:
            seq=[]; doc+=['## '+b0['block_id']+' '+ed,'']
            for l in loci:
                v=sorted(by[l,ed],key=lambda x:int(x['source_group_index'])); assert v and [int(x['source_group_index']) for x in v]==list(range(1,len(v)+1))
                assert all(int(x['source_group_count'])==len(v) for x in v)
                doc+=['- '+l+' '+c[l]['kind']+': '+json.dumps([{'raw':g['ivtff_group_raw'],'separator_after':g['right_separator'],'A':m['candidates']['A'].get(g['ivtff_group_raw'],'UNKNOWN'),'B':m['candidates']['B'].get(g['ivtff_group_raw'],'UNKNOWN')} for g in v],ensure_ascii=False)]
                if c[l]['kind']=='P': seq+=v
            for cid,values in m['candidates'].items():
                events=[{'source_group_id':g['source_group_id'],'locus':g['locus'],'index':int(g['source_group_index']),'whole':g['ivtff_group_raw'],'phase':values[g['ivtff_group_raw']],'paragraph_offset':i+1} for i,g in enumerate(seq) if g['ivtff_group_raw'] in values]
                ins=[x['paragraph_offset'] for x in events if x['phase']=='INTAKE_BY_PATIENT']; outs=[x['paragraph_offset'] for x in events if x['phase']=='DISCHARGE_BY_PATIENT']
                status='MISSING_PHASE' if not ins or not outs else ('INTAKE_FIRST' if min(ins)<min(outs) else 'DISCHARGE_FIRST')
                cases.append({'candidate':cid,'block_id':b0['block_id'],'page':b0['page'],'edition':ed,'prose_groups':len(seq),'intake_count':len(ins),'discharge_count':len(outs),'first_intake':min(ins) if ins else None,'first_discharge':min(outs) if outs else None,'status':status,'events':events,'unbound_roles':['patient','input_material','output_material','warm_room','clothing'],'independent_meaning_capacity':0})
            doc+=['']
    result={'experiment_id':'GDT1110','execution_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete_P_blocks':len(selected),'original_GDT822_complete_P_blocks':31,'current_scope_pages':sorted({x['page'] for x in selected}),'cases':len(cases),'candidates':{},'confirmed_words':0,'independent_meaning_capacity':0,'significance':False,'source_role_bindings_found':0}
    for cid in m['candidates']:
        ctr=Counter(x['status'] for x in cases if x['candidate']==cid)
        result['candidates'][cid]={'whole_values':m['candidates'][cid],'statuses':dict(ctr),'universal_bridge':'REJECTED' if ctr['DISCHARGE_FIRST'] else 'NECESSARY_ORDER_ONLY_UNCONFIRMED'}
    result['status']='NO_UNIVERSAL_INTAKE_OUTPUT_DIRECTION' if all(v['universal_bridge']=='REJECTED' for v in result['candidates'].values()) else 'ORDER_ONLY_CONDITIONAL_LEAD_NO_MEANING'
    (O/'CASES.json').write_text(json.dumps(cases,indent=2)+'\n');(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(O/'FULL_READER.md').write_text('\n'.join(doc)+'\n')
    fields=['candidate','block_id','page','edition','prose_groups','intake_count','discharge_count','first_intake','first_discharge','status','independent_meaning_capacity']
    with (O/'CANDIDATE_TABLE.tsv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows({k:x[k] for k in fields} for x in cases)
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
