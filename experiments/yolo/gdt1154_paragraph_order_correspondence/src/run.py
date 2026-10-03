"""Frozen GDT1154 complete-search order statistic; no lexical meanings."""
import collections, csv, hashlib, itertools, json, os, random
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path
E=Path(__file__).resolve().parents[1]
R=E.parents[2]
A=E/'artifacts'
SOURCE='experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'

def dump(name,x):
 (A/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def flatten(lines,key='words'):
 return [w for l in lines for w in l[key]]

def mask(words):
 d={}
 for i,w in enumerate(words): d[w]=d.get(w,0)|(1<<i)
 return d

def lcs(a,bmask):
 s=0
 for w in a:
  x=s|bmask.get(w,0); s=x&~(x-((s<<1)|1))
 return s.bit_count()

def eligible(p):
 lines=p['lines']; reasons=[]
 if len(lines)<6: reasons.append('FEWER_THAN_6_LINES')
 if not all(l['anchor_eligible'] for l in lines): reasons.append('INELIGIBLE_WHOLE_LINE')
 n=sum(len(l['words']) for l in lines[1:-1])
 if n<20: reasons.append('FEWER_THAN_20_INTERIOR_GROUPS')
 return reasons,n

def trace(a,b):
 wa=flatten(a['lines'][1:-1]);wb=flatten(b['lines'][1:-1]);ia=flatten(a['lines'][1:-1],'source_ids');ib=flatten(b['lines'][1:-1],'source_ids')
 la=[l['locus'] for l in a['lines'][1:-1] for w in l['words']];lb=[l['locus'] for l in b['lines'][1:-1] for w in l['words']]
 dp=[[0]*(len(wb)+1) for _ in range(len(wa)+1)]
 for i,x in enumerate(wa,1):
  for j,y in enumerate(wb,1): dp[i][j]=dp[i-1][j-1]+1 if x==y else max(dp[i-1][j],dp[i][j-1])
 i,j=len(wa),len(wb);out=[]
 while i and j:
  if wa[i-1]==wb[j-1]:
   out.append({'word':wa[i-1],'a_index':i-1,'b_index':j-1,'a_source_id':ia[i-1],'b_source_id':ib[j-1],'a_locus':la[i-1],'b_locus':lb[j-1]});i-=1;j-=1
  elif dp[i-1][j]>=dp[i][j-1]:i-=1
  else:j-=1
 out.reverse()
 return {'matches':out,'a_lines':sorted({x['a_locus'] for x in out}),'b_lines':sorted({x['b_locus'] for x in out})}

PANELS=None; PAIRS=None

def init(panels,pairs):
 global PANELS,PAIRS
 PANELS=panels;PAIRS=pairs

def null(rep):
 rng=random.Random(1154000+rep);best=Fraction(0);winners=[]
 for reader,ps in sorted(PANELS.items()):
  seq=[]
  for p in ps:
   ls=list(p['lines'][1:-1]);rng.shuffle(ls);seq.append(flatten(ls))
  masks=[mask(s) for s in seq]
  for i,j in PAIRS[reader]:
   k=lcs(seq[i],masks[j]);den=len(seq[i])+len(seq[j]);score=Fraction(2*k,den)
   if score>best:best=score;winners=[]
   if score==best:winners.append({'reader':reader,'a':ps[i]['id'],'b':ps[j]['id'],'lcs':k,'denominator':den})
 return {'replicate':rep,'seed':1154000+rep,'max_numerator':best.numerator,'max_denominator':best.denominator,'max_score':float(best),'winners':winners}

def main():
 pins=json.loads((E/'PREREG_LOCK.json').read_text())['files']
 for p,h in pins.items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 source=json.loads((R/SOURCE).read_text()); panels={};elig={};pairs={};allrows=[]
 for reader,ps in sorted(source.items()):
  panels[reader]=[];elig[reader]=[]
  for p in sorted(ps,key=lambda p:p['id']):
   assert not p['page'].startswith('f84') and p['page']!='f116v'
   reasons,n=eligible(p)
   elig[reader].append({'id':p['id'],'page':p['page'],'leaf':p['leaf'],'lines':len(p['lines']),'interior_groups':n,'eligible':not reasons,'reasons':reasons,'ineligible_lines':[l['locus'] for l in p['lines'] if not l['anchor_eligible']]})
   if not reasons:panels[reader].append(p)
  ps=panels[reader];seq=[flatten(p['lines'][1:-1]) for p in ps];masks=[mask(s) for s in seq];bags=[collections.Counter(s) for s in seq]
  pairs[reader]=[(i,j) for i,j in itertools.combinations(range(len(ps)),2) if ps[i]['leaf']!=ps[j]['leaf'] and max(len(seq[i]),len(seq[j]))<=2*min(len(seq[i]),len(seq[j]))]
  for i,j in pairs[reader]:
   k=lcs(seq[i],masks[j]);den=len(seq[i])+len(seq[j])
   allrows.append({'reader':reader,'a':ps[i]['id'],'b':ps[j]['id'],'a_groups':len(seq[i]),'b_groups':len(seq[j]),'lcs':k,'numerator':2*k,'denominator':den,'score':2*k/den,'common_multiset':sum((bags[i]&bags[j]).values())})
 dump('eligibility.json',elig)
 fields=['reader','a','b','a_groups','b_groups','lcs','numerator','denominator','score','common_multiset']
 with (A/'ALL_PAIRS.tsv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(allrows)
 observed=max((Fraction(x['numerator'],x['denominator']) for x in allrows),default=Fraction(0))
 winners=[x for x in allrows if Fraction(x['numerator'],x['denominator'])==observed]
 if allrows:
  with ProcessPoolExecutor(max_workers=min(32,os.cpu_count() or 1),initializer=init,initargs=(panels,pairs)) as pool: draws=list(pool.map(null,range(1,200)))
 else:draws=[]
 dump('NULL_MAXIMA.json',draws)
 exceed=sum(Fraction(x['max_numerator'],x['max_denominator'])>=observed for x in draws);p_rank=(1+exceed)/200 if draws else None
 selected=[]
 for reader in sorted(panels):
  ranked=sorted([x for x in allrows if x['reader']==reader],key=lambda x:(-Fraction(x['numerator'],x['denominator']),x['a'],x['b']))
  selected.extend(ranked[:10])
 for w in winners:
  if w not in selected:selected.append(w)
 contexts=[]
 for row in selected:
  reader=row['reader'];pm={p['id']:p for p in panels[reader]};a=pm[row['a']];b=pm[row['b']];alignment=trace(a,b)
  assert len(alignment['matches'])==row['lcs']
  availability={r:{side:{'exact_paragraph_id_present':any(p['id']==row[side] for p in ps),'exact_paragraph_id_eligible':any(p['id']==row[side] for p in panels[r]),'same_page_cached_paragraph_ids':[p['id'] for p in ps if p['page']==pm[row[side]]['page']]} for side in ['a','b']} for r,ps in sorted(source.items())}
  contexts.append({**row,'global_winner':row in winners,'alignment':alignment,'line_coverage_pass':len(alignment['a_lines'])>=3 and len(alignment['b_lines'])>=3,'paragraph_a':a,'paragraph_b':b,'alternative_reader_availability':availability})
 dump('TOP_CONTEXTS.json',contexts)
 nominated=[x for x in contexts if x['global_winner'] and x['line_coverage_pass'] and p_rank<=.05]
 status='NO_CAPACITY' if not allrows else 'NO_ORDER_LEAD' if p_rank>.05 else 'ORDER_CORRESPONDENCE_CANDIDATES' if nominated else 'CONCENTRATED_MATCH_ONLY'
 result={'status':status,'observed_max':float(observed),'observed_max_numerator':observed.numerator,'observed_max_denominator':observed.denominator,'global_winners':winners,'null_draws':len(draws),'null_at_least_observed':exceed,'p_rank':p_rank,'nominated_pairs':[{'reader':x['reader'],'a':x['a'],'b':x['b']} for x in nominated],'counts':{r:{'cached_paragraphs':len(source[r]),'eligible_paragraphs':len(panels[r]),'eligible_pairs':len(pairs[r])} for r in sorted(source)},'meanings':0,'independent_confirmation':False,'manuscript_wide_significance_claim':False,'ancestry_claim':False,'relation_packet_score_ready':False,'provenance':{'pins_verified_before_run_source_read':True,'pins':pins,'implementation_schema_inspection_before_pin_verification':True,'schema_inspection_note':'A schema excerpt of already-exposed pinned PARAGRAPHS.json was inspected after preregistration but before developer hash verification; no eligibility or scores were computed before verification.'}}
 dump('RESULT.json',result)
 text=['# GDT1154 descriptive top pairs','','Top 10 per reader plus every exact global tie. No meanings or ancestry assigned. Full search in artifacts/ALL_PAIRS.tsv.','','|Reader|Paragraph A|Paragraph B|LCS|Denominator|Score|Common multiset|Lines A/B|Global winner|','|---|---|---|---:|---:|---:|---:|---|---|']
 for x in contexts:text.append('|'+ '|'.join([x['reader'],x['a'].replace('|',' / '),x['b'].replace('|',' / '),str(x['lcs']),str(x['denominator']),f"{x['score']:.8f}",str(x['common_multiset']),str(len(x['alignment']['a_lines']))+'/'+str(len(x['alignment']['b_lines'])),str(x['global_winner'])])+'|')
 (E/'CANDIDATE_TABLE.md').write_text('\n'.join(text)+'\n')
 text=['# GDT1154 full candidate contexts','','All groups retained; first and last lines excluded only from scoring. Matched source IDs are recorded in alignment tables. Unmatched words remain visible in full paragraphs.']
 for n,x in enumerate(contexts,1):
  text.extend(['',f"## {n}. {x['reader']} {x['a']} / {x['b']}",'',f"LCS {x['lcs']}; score {x['score']:.8f}; line coverage {len(x['alignment']['a_lines'])}/{len(x['alignment']['b_lines'])}; global winner {x['global_winner']}."])
  for side in ['a','b']:
   p=x['paragraph_'+side];text.extend(['',f"### Paragraph {side.upper()}: {p['id']}",''])
   for i,l in enumerate(p['lines']):text.extend([l['locus']+(' [unscored boundary]' if i in (0,len(p['lines'])-1) else '')+': `'+ ' '.join(l['words'])+'`',''])
  text.extend(['### Deterministic matched groups','','|Word|Source A|Source B|','|---|---|---|'])
  for m in x['alignment']['matches']:text.append('|'+m['word']+'|'+m['a_source_id'].replace('|',' / ')+'|'+m['b_source_id'].replace('|',' / ')+'|')
  text.extend(['','Alternative-reader paragraph availability (not independent replication):','','```json',json.dumps(x['alternative_reader_availability'],indent=2),'```'])
 (E/'WHOLE_CONTEXTS.md').write_text('\n'.join(text)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
