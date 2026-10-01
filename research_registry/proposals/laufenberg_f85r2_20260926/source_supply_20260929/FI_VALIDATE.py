"""Conserve the frozen exploratory packet and replay its explicit local sort failure.

Not a general Voynich parser, semantic decoder or exhaustive grammar search.
"""
from pathlib import Path
from collections import Counter
import json, hashlib, csv
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
read=lambda n:json.loads((P/n).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
target=read('FI_TARGET.json'); author=read('FI_AUTHOR.json')
contract=read('FI_CONTRACT.json'); spec=read('FI_TYPE_DIAGNOSTIC_SPEC.json')
checks=[]
def check(name,value):
    assert value,name
    checks.append(name)
check('author_fixed_hash',sha(P/'FI_AUTHOR.json')==spec['author_sha256'])
check('target_fixed_hash',sha(P/'FI_TARGET.json')==spec['target_sha256']==contract['target_sha256']==author['target_sha256'])
check('alternate_fixed_hash',sha(P/'FI_ALTERNATE_READINGS.json')==spec['alternate_sha256'])
check('primary_source_hash',sha(ROOT/target['source_path'])==target['source_sha256'])
check('metadata_hash',sha(ROOT/target['metadata_path'])==target['metadata_sha256'])
source=json.loads((ROOT/target['source_path']).read_text())
loci=[x['locus']for x in target['paragraph_metadata']['lines']]
check('entire_native_primary_projection',target['records']==[r for r in source if r['locus']in loci])
def rows(records):
    return [dict(zip(r['columns'],g)) for r in records for g in r['groups']]
primary=rows(target['records'])
check('primary69_unique51',len(primary)==69 and len({r['ivtff_group_raw']for r in primary})==51)
check('metadata_source_group_count',target['paragraph_metadata']['groups']==69)
check('all69_author_order',len(author['positions'])==69 and [r['position']for r in author['positions']]==list(range(1,70)))
for r,a in zip(primary,author['positions']):
    check('contribution_'+str(a['position']), all(a[k]==r[v]for k,v in {'id':'source_group_id','raw_surface':'ivtff_group_raw','left_separator':'left_separator','right_separator':'right_separator'}.items()) and ''.join(a['segmentation'])==a['raw_surface'])
for key,cap in contract['caps'].items():
    check('budget_'+key,author['budget_use'][key]==len(author['inventories'][key])<=cap)
check('partial_not_full',author['status']=='PARTIAL_STOP_FROZEN' and author['scope_and_consumption']['continuous_prefix_fully_consumed_positions']==0 and author['unconsumed_positions']==list(range(1,70)))
check('first_unknown_pol',author['first_unmet']['position']==1 and author['positions'][0]['raw_surface']=='pol')
check('four_conditional_fragments',len(author['conditional_events'])==4)
# No interpretation of these English grammar declarations is inferred by code:
# their exact projected signatures are fixed in the postauthor diagnostic spec
# and independently reviewed against the author inventory.
check('projected_signatures',spec['operator_signature_projection']=={'kain':'MaterialType','ol':{'MaterialType':'MaterialRef','UnaryEventDefinition':'EventExpression'},'q':{'MaterialRef':'EventExpression'}})
state=spec['operator_signature_projection']['kain'];trace=[{'stage':'kain','sort':state}]
failed=None
for stage,op in [('innerOL','ol'),('innerQ','q'),('outerOL','ol'),('outerQ','q')]:
    domains=spec['operator_signature_projection'][op]
    if state not in domains:
        failed={'stage':stage,'received':state,'accepted':list(domains)}
        break
    state=domains[state];trace.append({'stage':stage,'sort':state})
check('actual_first_sort_failure',failed=={'stage':'outerOL','received':'EventExpression','accepted':['MaterialType','UnaryEventDefinition']})
alternates=read('FI_ALTERNATE_READINGS.json')
packets={'IT2a':{'records':target['records'],'own_paragraph_capacity':True},**alternates}
windows=[];rawcounts={}
for ed,packet in packets.items():
    if ed!='IT2a':
        check('source_hash_'+ed,sha(ROOT/packet['source_path'])==packet['source_sha256'])
        originals=json.loads((ROOT/packet['source_path']).read_text())
        check('alternate_complete_projection_'+ed,packet['records']==[r for r in originals if r['locus']in loci])
    rs=rows(packet['records']);rawcounts[ed]=len(rs)
    win=[r for r in rs if r['locus']=='f80v.35'and int(r['source_group_index'])in (5,6,7)]
    check('declared_window_'+ed,[r['ivtff_group_raw']for r in win]==['qol','qol','kain'] and all(r['left_separator']=='DEFINITE_SPACE'and r['right_separator']=='DEFINITE_SPACE'for r in win))
    windows.append({'edition':ed,'ids':[r['source_group_id']for r in win],'surface':['qol','qol','kain'],'own_paragraph_capacity':packet['own_paragraph_capacity'],'fixed_nested_sort_result':failed})
check('all208_original_groups',rawcounts=={'IT2a':69,'ZL3b':70,'RF1b':69})
with(P/'FI_CANDIDATE_TABLE.tsv').open()as f:table=list(csv.DictReader(f,delimiter='\t'))
check('table69_ordered',len(table)==69 and all(t['id']==a['id']and t['raw_surface']==a['raw_surface']and t['status']==a['status']and t['semantic_contribution']==a['semantic_contribution']and t['attachment']==a['attachment']for t,a in zip(table,author['positions'])))
out={'status':'FROZEN_PACKET_AND_LOCAL_SORT_DIAGNOSTIC_PASS','checks':len(checks),'raw_counts':rawcounts,'primary_status_counts':dict(Counter(a['status']for a in author['positions'])),'whole_account_complete':False,'continuous_consumed_prefix':0,'conditional_fragment_count':4,'local_signature_trace':trace,'first_local_sort_failure':failed,'windows':windows,'scope':'One fixed author nesting and signature projection; no exhaustive full-grammar search or generic meaning refutation','confirmed_words':0,'independent_confirmation_capacity':0}
print(json.dumps(out,indent=2))
