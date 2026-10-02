#!/usr/bin/env python3
import csv,gzip,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
BARE={'ain','aiin','aiiin'};D={'d'+x for x in BARE};PURE=re.compile('^[a-z]+$')
def load(p):return json.loads(p.read_text())
def write(n,x):
 b=(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=None if n.endswith('.gz') else 2)+'\n').encode();(P/'artifacts'/n).write_bytes(gzip.compress(b,mtime=0) if n.endswith('.gz') else b)
def cls(raw):return 'UNCERTAIN' if not PURE.fullmatch(raw) else 'BARE_MINIM' if raw in BARE else 'D_MINIM' if raw in D else 'OTHER_A' if raw.startswith('a') else 'OTHER'
def main():
 source=load(P/'src/SOURCE.json')
 for x in source['inputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
 for x,h in load(P/'src/PREREG_LOCK.json')['hashes'].items():assert hashlib.sha256((P/x).read_bytes()).hexdigest()==h
 allowed=set(load(ROOT/source['inputs'][0]['path'])['allowed_selectors']);cases=[];blocks=[];firstlines={};readers={};seen=set()
 for ed in ('ZL3b','IT2a','RF1b'):
  rows=[]
  for part in ('DISCOVERY','EVALUATION'):
   data=load(ROOT/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{part}_{ed}.json')
   for r in data['lines']:
    m=r['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84') and m['page']!='f116v'
    if m['kind']=='P':rows.append({'metadata':m,'groups':[dict(zip(data['group_columns'],g)) for g in r['groups']]})
  pages=defaultdict(list)
  for r in rows:pages[r['metadata']['page']].append(r)
  bound={};nblocks=0
  for page,pr in sorted(pages.items()):
   pr.sort(key=lambda r:int(r['metadata']['source_row_index']));pending=[]
   for row in pr:
    m=row['metadata']
    if m['paragraph_start']=='1':pending=[row]
    elif pending:pending.append(row)
    if m['paragraph_end']=='1':
     if pending:
      ident=f"{ed}|{page}|{pending[0]['metadata']['locus']}..{m['locus']}";nblocks+=1
      block={'edition':ed,'id':ident,'page':page,'loci':[r['metadata']['locus'] for r in pending],'line_count':len(pending)};blocks.append(block)
      for r in pending:bound[r['metadata']['locus']]=block
     pending=[]
  inventory=Counter();positions={p:Counter() for p in ('PARAGRAPH_START','CONTINUATION_START','INTERNAL')};diag=Counter();forms=defaultdict(Counter);entry_leaves=defaultdict(set);bareleaves=set();firsts=Counter()
  for row in rows:
   m=row['metadata'];gs=row['groups'];n=int(m['source_group_count']);assert len(gs)==n;block=bound.get(m['locus']);leaf=int(re.match(r'^f([0-9]+)',m['page']).group(1));multi=block is not None and block['line_count']>=2
   if multi and any(g['ivtff_group_raw'] in BARE for g in gs):bareleaves.add(leaf)
   for g in gs:
    gid=g['source_group_id'];assert gid not in seen;seen.add(gid);idx=int(g['source_group_index']);raw=g['ivtff_group_raw'];c=cls(raw);inventory[c]+=1;diag['ALL_P_GROUPS']+=1
    if block is None:scope='UNBOUNDED'
    elif block['line_count']==1:scope='SINGLE_LINE_PARAGRAPH'
    elif n==1:scope='SINGLE_GROUP_LINE'
    else:scope='PRIMARY'
    diag[scope]+=1
    if block and block['line_count']==1:diag['FLAG_SINGLE_LINE_PARAGRAPH']+=1
    if n==1:diag['FLAG_SINGLE_GROUP_LINE']+=1
    pos='PARAGRAPH_START' if idx==1 and m['paragraph_start']=='1' else 'CONTINUATION_START' if idx==1 else 'INTERNAL'
    if idx==1:firsts[c]+=1
    if scope=='PRIMARY':
     positions[pos]['ALL']+=1;positions[pos][c]+=1
     if c!='UNCERTAIN':positions[pos]['PURE']+=1
     if pos=='CONTINUATION_START':entry_leaves[c].add(leaf)
    if c not in ('BARE_MINIM','D_MINIM','OTHER_A'):continue
    f=forms[raw];f['ALL']+=1;f['ALL_FIRST' if idx==1 else 'ALL_NONFIRST']+=1;f[scope+':'+pos]+=1
    case={**g,'edition':ed,'page':m['page'],'locus':m['locus'],'leaf':leaf,'class':c,'scope':scope,'position':pos,'paragraph':block['id'] if block else None,'paragraph_lines':block['line_count'] if block else None,'source_group_count':n,'paragraph_start':m['paragraph_start'],'paragraph_end':m['paragraph_end']};cases.append(case)
    if idx==1:firstlines[ed+'|'+m['locus']]=row
  cont=positions['CONTINUATION_START'];internal=positions['INTERNAL'];capacity=cont['ALL']>=100 and internal['BARE_MINIM']>=50 and len(bareleaves)>=5;control=cont['OTHER_A']>=5 and len(entry_leaves['OTHER_A'])>=2;dent=cont['D_MINIM']>=10 and len(entry_leaves['D_MINIM'])>=3
  readers[ed]={'inventory':dict(inventory),'all_P_first_groups':dict(firsts),'complete_paragraphs':nblocks,'diagnostic_scopes':dict(diag),'positions':{p:dict(c) for p,c in positions.items()},'forms':{k:dict(v) for k,v in sorted(forms.items())},'bare_multiline_paragraph_leaves':sorted(bareleaves),'continuation_leaves':{k:sorted(v) for k,v in entry_leaves.items()},'capacity':capacity,'other_a_control':control,'d_entry_capacity':dent}
 primary=[readers[e] for e in ('ZL3b','IT2a')]
 if not all(r['capacity'] for r in primary):decision='INSUFFICIENT_CAPACITY'
 elif any(r['positions']['CONTINUATION_START'].get('BARE_MINIM',0) for r in primary):decision='BARE_SERIES_BAN_CONTRADICTED'
 elif all(r['other_a_control'] and r['d_entry_capacity'] for r in primary):decision='MINIM_SPECIFIC_CONTINUATION_AVOIDANCE'
 else:decision='CONTROL_OR_DENTRY_CAPACITY_INSUFFICIENT'
 result={'experiment':'GDT1149','decision':decision,'readers':readers,'confirmed_words':0,'independent_confirmation_capacity':0,'significance':'NOT_CLAIMED','RF':'LINE_DIAGNOSTICS_ONLY_NO_NATIVE_PARAGRAPH_FLAGS'}
 write('RESULT.json',result);write('CASES.json.gz',cases);write('BLOCKS.json',blocks);write('ALL_FIRST_LINES.json.gz',firstlines)
 with (P/'artifacts/CANDIDATES.tsv').open('w') as f:
  fields=['edition','form','ALL','ALL_FIRST','ALL_NONFIRST','PRIMARY:PARAGRAPH_START','PRIMARY:CONTINUATION_START','PRIMARY:INTERNAL'];w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader()
  for e,r in readers.items():
   for form,c in r['forms'].items():w.writerow({'edition':e,'form':form,**{k:c.get(k,0) for k in fields[2:]}})
 print(json.dumps({'decision':decision,'readers':{e:{k:r[k] for k in ['inventory','complete_paragraphs','positions','capacity','other_a_control','d_entry_capacity']} for e,r in readers.items()}},indent=2))
if __name__=='__main__':main()
