import collections,csv,functools,gzip,hashlib,json,re,struct
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
READERS=['ZL3b','IT2a','RF1b']
PAIRS={('LINE_START','DEFINITE_SPACE'),('DEFINITE_SPACE','LINE_END'),('LINE_START','LINE_END')}
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,indent=2)+'\n')
@functools.lru_cache(None)
def parse(s):
 if not s:return ((),)
 out=[]
 for a in A:
  if s.startswith(a):out.extend((a,)+t for t in parse(s[len(a):]))
 return tuple(out[:2])
def project(units,mask):return ''.join(str((mask>>A.index(u))&1) for u in units)
def fixture():
 assert parse('ch')==( ('ch',), ) and parse('!')==()
 assert project(['a'],1<<4)=='0' and project(['a','a'],1<<4)=='00'
 assert len({'0','00'}|{'00','001'})==3
 assert ('UNCERTAIN_SMALL_SPACE','LINE_END') not in PAIRS
 return 'PASS'
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fixture();allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
 strict=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));res={};panel={}
 for ed in READERS:
  edges=[];cnt=collections.Counter();source={}
  for phase in ['DISCOVERY','EVALUATION']:
   d=json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json').read_text());assert d['group_columns']==['source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']
   for line in d['lines']:
    m=line['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84') and m['page'] not in ['f1r','f116v'];assert m['edition']==ed
    indices=[int(g[1]) for g in line['groups']];assert len(indices)==len(set(indices))
    for g in line['groups']:
     ident,idx,raw,left,right=g;assert ident not in source;source[ident]=(m,g);cnt['cached_groups']+=1
     if m['kind']!='P':cnt['non_prose']+=1;continue
     if (left,right) not in PAIRS:cnt['not_fixed_edge_pair']+=1;continue
     if left=='LINE_START':assert int(idx)==min(indices)
     if right=='LINE_END':assert int(idx)==max(indices)
     if not re.fullmatch('[a-z]+',raw):cnt['edge_nonliteral']+=1;continue
     ps=parse(raw)
     if len(ps)!=1:cnt['edge_nonunique_parse']+=1;continue
     cnt['eligible_edge']+=1
     edges.append({'id':ident,'page':m['page'],'locus':m['locus'],'source_group_index':idx,'ivtff_group_raw':raw,'left_separator':left,'right_separator':right,'units':list(ps[0])})
  for row in strict[ed]:
   m,g=source[row['id']];assert m['kind']=='P' and m['page']==row['page'] and m['locus']==row['locus'];assert int(g[1])==int(row['source_group_index']) and g[2]==row['ivtff_group_raw'] and g[3]==g[4]=='DEFINITE_SPACE';assert parse(g[2])==(tuple(row['units']),)
  assert not ({r['id'] for r in edges}&{r['id'] for r in strict[ed]})
  edges.sort(key=lambda r:r['id']);panel[ed]=edges
  payload=gzip.decompress((R/f'experiments/yolo/gdt1312_binary_whole_code_capacity/artifacts/COUNTS_{ed}.u16.gz').read_bytes());counts=struct.unpack('<'+str(len(payload)//2)+'H',payload);masks=[i<<1 for i,k in enumerate(counts) if i and k<=32];out=[]
  for mask in masks:
   old={project(r['units'],mask) for r in strict[ed]};assert len(old)==counts[mask>>1]
   codes={};edgecodes=set()
   for cohort,rows in [('strict',strict[ed]),('edge',edges)]:
    for row in rows:
     code=project(row['units'],mask);v=codes.setdefault(code,{'strict_occurrences':0,'edge_occurrences':0,'witness':row});v[cohort+'_occurrences']+=1
     if cohort=='edge':edgecodes.add(code)
   out.append({'mask':mask,'class1':[a for i,a in enumerate(A) if mask>>i&1],'strict_K':len(old),'edge_K':len(edgecodes),'union_K':len(codes),'fits32':len(codes)<=32,'new_codes':sorted(edgecodes-old,key=lambda s:(len(s),s)),'codes':dict(sorted(codes.items(),key=lambda kv:(len(kv[0]),kv[0])))})
  survivors=[x['mask'] for x in out if x['fits32']]
  res[ed]={'filter_counts':dict(cnt),'strict_groups':len(strict[ed]),'edge_groups':len(edges),'edge_types':len({r['ivtff_group_raw'] for r in edges}),'max_units':max(len(r['units']) for r in strict[ed]+edges),'keys':out,'surviving_masks':survivors,'status':'CAPACITY_RETAINS' if survivors else 'ALL_FIXED_KEYS_EXCLUDED'}
  print(ed,len(edges),[(x['class1'],x['strict_K'],x['union_K']) for x in out],flush=True)
 status='ALL_READINGS_EXCLUDED' if all(not x['surviving_masks'] for x in res.values()) else 'READER_SPECIFIC_EDGE_CAPACITY'
 save('RESULT.json',{'status':status,'fixtures':'PASS','readers':res,'ceiling':'Capacity conditional on physical line edges delimiting complete groups; no decoded values or general cipher rejection.'});(B/'artifacts/EDGES.json.gz').write_bytes(gzip.compress(json.dumps(panel,sort_keys=True,separators=(',',':')).encode(),mtime=0))
if __name__=='__main__':main()
