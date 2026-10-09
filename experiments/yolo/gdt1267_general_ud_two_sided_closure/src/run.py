import json,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
LEFT='experiments/yolo/gdt1240_prefix_expansion_fourth_power/artifacts/NATIVE_PROOF.json'
RIGHT='experiments/yolo/gdt1241_suffix_quotient_expansion/artifacts/PROOFS.json'
SOURCE='experiments/yolo/gdt1240_prefix_expansion_fourth_power/artifacts/RESULT.json'
def main():
    lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
    for name,h in lock['sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    a=json.loads((ROOT/LEFT).read_text());b=json.loads((ROOT/RIGHT).read_text());old=json.loads((ROOT/SOURCE).read_text())
    out={}
    for r in ['IT2a','RF1b','ZL3b']:
        def node(which,units):
            data=a[r]['proof_events'] if which=='left' else b[r]['nodes']
            key='units' if which=='left' else 'word'
            found=[n for n in data if n[key]==units and n['parents'] is None];assert len(found)==1
            n=found[0]
            return dict(origin=LEFT if which=='left' else RIGHT,node_id=n['event_id' if which=='left' else 'id'],units=units,source_ids=n['source_ids'],frequency=n['occurrences' if which=='left' else 'frequency'],pages=n['pages'])
        singletons={}
        for g in 'kes':
            if g=='s':singletons[g]=dict(rule='WHOLE',premises=[node('left',['s'])])
            elif g=='e' and r!='RF1b':singletons[g]=dict(rule='TWO_SIDED',premises=[node('left',['sh','e']),node('left',['sh','e','e']),node('right',['e','a','r']),node('right',['a','r'])])
            elif g=='k' and r=='IT2a':singletons[g]=dict(rule='TWO_SIDED',premises=[node('left',['sh','e']),node('left',['sh','e','k']),node('right',['k','l']),node('right',['l'])])
            else:singletons[g]=dict(rule='WHOLE',premises=[node('right',[g])])
        out[r]=dict(singletons=singletons,whole_witness_occurrences=a[r]['whole_witness_occurrences'],forced_parse=['k','e','e','e','e','s'])
    assert all(v['supporting_tokens']==0 for v in old['sources'].values())
    result=dict(status='GENERAL_UD_FIXED_SOURCE_EXCLUSION_EXTENDED',readers=out,source_results=old['sources'],native_closure_executed=False,new_source_census=False,scope='logical bridge of old premises; conditional fixed five-source exclusion, not a language ban')
    (P/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    (P/'artifacts/RUN_RECEIPT.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),lock_sha256=hashlib.sha256((P/'src/REGISTRATION_LOCK.json').read_bytes()).hexdigest()),indent=2)+'\n')
    print(json.dumps({'status':result['status'],'readers':list(out),'singleton_conclusions':9,'two_sided_bridges':3,'native_closure_executed':False,'new_source_census':False}))
if __name__=='__main__':main()
