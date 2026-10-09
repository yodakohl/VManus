import collections,functools,gzip,hashlib,json,math,re
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
@functools.lru_cache(None)
def run_polynomial(length):
 states={(0,0,0):1,(1,1,0):1}
 for _ in range(1,length):
  new=collections.Counter()
  for (ones,last,cuts),count in states.items():
   for bit in [0,1]:new[(ones+bit,bit,cuts+int(last!=bit))]+=count
  states=new
 out=collections.Counter()
 for (ones,last,cuts),count in states.items():out[(ones,cuts)]+=count
 return dict(out)
@functools.lru_cache(None)
def distribution(runs,r):
 poly={(0,0):1}
 for length in runs:
  new=collections.Counter()
  for (a,c),count in poly.items():
   for (b,d),count2 in run_polynomial(length).items():
    if a+b<=r:new[(a+b,c+d)]+=count*count2
  poly=new
 return {cuts:count for (ones,cuts),count in poly.items() if ones==r}

def main():
 s=json.loads((B/'src/SPEC.json').read_text());result=json.loads((B/'artifacts/RESULT.json').read_text());packets=json.loads(gzip.decompress((B/'artifacts/PAIRS.json.gz').read_bytes()));unpaired=json.loads((B/'artifacts/UNPAIRED.json').read_text());exclusions=json.loads((B/'artifacts/EXCLUSIONS.json').read_text())
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 assert hashlib.sha256((R/s['fit']).read_bytes()).hexdigest()==json.loads((R/s['fit_lock']).read_text())['train_sha256']
 data=json.loads(gzip.decompress((R/s['source']).read_bytes()));labels=json.loads((R/s['fit']).read_text())['labels'];leaf=lambda row:int(re.match(r'f([0-9]+)',row['page']).group(1));expected_unpaired=[];expected_exclusions=[];checks=[]
 for reader in s['readers']:
  rows=data[reader];assert all(not row['page'].startswith('f84') and row['page']!='f116v' for row in rows)
  knownwhole={tuple(row['units']) for row in rows if leaf(row)%2==1};knowninside={tuple(row['units'][1:-1]) for row in rows if leaf(row)%2==1 and len(row['units'])>=s['minimum_interior_units']+2}
  for cohort in s['cohorts']:
   groups=collections.defaultdict(list);counts=collections.Counter();leafs=collections.defaultdict(lambda:{'groups':0,'edges':0,'observed':0,'expected':Fraction(0),'pairs':0,'informative_pairs':0,'unpaired_groups':0})
   for row in rows:
    if leaf(row)%2:continue
    inner=row['units'][1:-1]
    if cohort=='UNSEEN_WHOLE' and tuple(row['units']) in knownwhole:continue
    if cohort=='UNSEEN_INTERIOR' and tuple(inner) in knowninside:continue
    counts['source_groups']+=1
    if len(inner)<s['minimum_interior_units']:counts['too_short']+=1;continue
    counts['eligible_groups']+=1
    if any(u not in labels for u in inner):counts['unknown_unit_groups']+=1;expected_exclusions.append({'reader':reader,'cohort':cohort,'id':row['id'],'reason':'UNSEEN_TRAIN_UNIT','whole_units':row['units']});continue
    item={'id':row['id'],'page':row['page'],'leaf':leaf(row),'whole_units':row['units'],'interior':inner,'bits':[labels[u] for u in inner]};groups[(row['page'],len(inner))].append(item);counts['scorable_groups']+=1;q=leafs[leaf(row)];q['groups']+=1;q['edges']+=len(inner)-1
   expected_pairs=[]
   for (page,n),items in sorted(groups.items()):
    expected_pairs.extend((page,n,i//2,items[i],items[i+1]) for i in range(0,len(items)-1,2))
    if len(items)%2:
     item=items[-1];expected_unpaired.append({'reader':reader,'cohort':cohort,**item});value=sum(a!=b for a,b in zip(item['bits'],item['bits'][1:]));q=leafs[item['leaf']];q['observed']+=value;q['expected']+=value;q['unpaired_groups']+=1;counts['unpaired_groups']+=1
   saved=[p for p in packets if p['reader']==reader and p['cohort']==cohort];assert len(saved)==len(expected_pairs)
   for p,(page,n,index,left,right) in zip(saved,expected_pairs):
    assert p['page']==page and p['length']==n and p['pair_index']==index and p['left']==left and p['right']==right
    x,y=left['bits'],right['bits'];cols=[sum(z) for z in zip(x,y)];assert cols==p['column_sums'];k=cols.count(1);r=sum(x)-cols.count(2);assert k==p['variable_columns'] and r==p['first_variable_ones']
    runs=[];pos=0
    while pos<n:
     if cols[pos]!=1:pos+=1;continue
     stop=pos
     while stop<n and cols[stop]==1:stop+=1
     runs.append(stop-pos);pos=stop
    assert runs==p['variable_runs'];constant=sum(1 if (a==1)!=(b==1) else 2*int(a!=b) if a!=1 and b!=1 else 0 for a,b in zip(cols,cols[1:]));assert constant==p['constant']
    dist=distribution(tuple(runs),r);total=sum(dist.values());assert total==math.comb(k,r)==p['configurations']
    mean=Fraction(sum((constant+2*c)*count for c,count in dist.items()),total);minimum=constant+2*min(dist);maximum=constant+2*max(dist);obs=sum(x[i]!=x[i+1] for i in range(n-1))+sum(y[i]!=y[i+1] for i in range(n-1));informative=len(dist)>1
    assert Fraction(*p['expected'])==mean and p['minimum']==minimum and p['maximum']==maximum and p['observed']==obs and p['informative']==informative
    # One concrete alternative demonstrates exact glyph-bag and within-class-order preservation.
    free=[j for j,c in enumerate(cols) if c==1];chosen=set(free[:r]);a=[int(c==2 or(c==1 and j in chosen)) for j,c in enumerate(cols)];b=[c-bit for c,bit in zip(cols,a)];assert sum(a)==sum(x) and sum(b)==sum(y)
    for original,bits in [(left['interior'],a),(right['interior'],b)]:
     queues={v:iter([u for u in original if labels[u]==v]) for v in [0,1]};new=[next(queues[v]) for v in bits];assert collections.Counter(new)==collections.Counter(original) and [labels[u] for u in new]==bits
    q=leafs[left['leaf']];q['observed']+=obs;q['expected']+=mean;q['pairs']+=1;q['informative_pairs']+=int(informative);counts['pairs']+=1;counts['informative_pairs']+=int(informative)
   report=next(q for q in result['reports'] if q['reader']==reader and q['cohort']==cohort);assert counts==collections.Counter(report['counts']);assert [q['leaf'] for q in report['leaves']]==sorted(leafs);effects=[];inform_effects=[]
   for rec in report['leaves']:
    q=leafs[rec['leaf']];excess=q['observed']-q['expected'];effect=excess/q['edges']
    for key in ['groups','edges','observed','pairs','informative_pairs','unpaired_groups']:assert q[key]==rec[key]
    assert Fraction(*rec['expected'])==q['expected'] and Fraction(*rec['excess'])==excess and Fraction(*rec['effect'])==effect and rec['informative']==(q['informative_pairs']>0)
    effects.append(effect)
    if q['informative_pairs']:inform_effects.append(effect)
   avg=lambda es:sum(es,Fraction(0))/len(es) if es else Fraction(0);positive=sum(e>0 for e in inform_effects);pf=Fraction(positive,len(inform_effects)) if inform_effects else Fraction(0);capacity=len(inform_effects)>=s['minimum_informative_leaves'];passed=capacity and pf>=Fraction(*s['positive_fraction']) and avg(inform_effects)>=Fraction(*s['minimum_mean_excess'])
   assert report['scorable_leaves']==len(effects) and report['informative_leaves']==len(inform_effects) and report['positive_informative_leaves']==positive and report['zero_informative_leaves']==inform_effects.count(0)
   assert Fraction(*report['mean_all'])==avg(effects) and Fraction(*report['mean_informative'])==avg(inform_effects) and Fraction(*report['positive_fraction'])==pf and report['capacity_pass']==capacity and report['gate_pass']==passed
   checks.append({'reader':reader,'cohort':cohort,'pairs':len(saved),'informative_pairs':counts['informative_pairs'],'informative_leaves':len(inform_effects),'positive_leaves':positive,'mean_informative':float(avg(inform_effects)),'gate_pass':passed})
 assert expected_unpaired==unpaired and expected_exclusions==exclusions
 primary=[q for q in result['reports'] if q['reader']==s['primary_reader'] and q['cohort'] in s['primary_cohorts']];status='JOINT_CONTROL_CAPACITY_STOP' if not all(q['capacity_pass'] for q in primary) else 'PAIRED_POSITION_BAG_LEAD_RETAINED' if all(q['gate_pass'] for q in primary) else 'JOINT_PAIRED_LEAD_NOT_ESTABLISHED';assert result['status']==status
 val={'status':'PASS','pairs_verified':len(packets),'unpaired_verified':len(unpaired),'checks':checks,'independence':'Source/cohort/cache-order reconstruction; full run score distributions by generating-polynomial convolution, not primary expectation or min/max formulas; exact rational leaf/gate checks; no primary import.','limits':'Restricted fixed-pair reference only, no pvalue or semantic/historical confirmation.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(val,indent=2)+'\n');print(json.dumps(val,indent=2))
if __name__=='__main__':main()
