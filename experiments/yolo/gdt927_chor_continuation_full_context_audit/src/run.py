import csv,json,re,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];P=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer';EDS=['ZL3b','IT2a','RF1b'];TARGETS=['chor','ykchor','chordy','ykchor chordy']
def write(n,x):(E/'artifacts'/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def load():
 for p,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 allowed=set(json.loads((P/'src/SPEC.json').read_text())['allowed_selectors']);data={}
 for ed in EDS:
  ls=[]
  for phase in ['DISCOVERY','EVALUATION']:
   d=json.loads((P/'artifacts'/f'SOURCE_{phase}_{ed}.json').read_text())
   for x in d['lines']:
    m=x['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84')
    if m['kind']!='P':continue
    gs=[dict(zip(d['group_columns'],g)) for g in x['groups']];w=[g['ivtff_group_raw'] for g in gs]
    seams=[a['right_separator']==b['left_separator']=='DEFINITE_SPACE' and int(b['source_group_index'])==int(a['source_group_index'])+1 for a,b in zip(gs,gs[1:])]
    safe=[(i==0 or seams[i-1]) and (i==len(w)-1 or seams[i]) for i in range(len(w))]
    ls.append({'id':m['page']+'|'+m['locus'],'metadata':m,'words':w,'group_ids':[g['source_group_id'] for g in gs],'safe':safe,'seams':seams,'literal_line':all(re.fullmatch('[a-z]+',z) for z in w) and all(seams) and len(w)>=2})
  data[ed]=sorted(ls,key=lambda l:(l['metadata']['page'],int(l['metadata']['source_row_index'])))
 return data

def paragraph(ls,locus):
 host=next(x for x in ls if x['metadata']['locus']==locus);page=host['metadata']['page'];same=[x for x in ls if x['metadata']['page']==page];i=same.index(host)
 starts=[j for j in range(i+1) if same[j]['metadata']['paragraph_start']=='1'];ends=[j for j in range(i,len(same)) if same[j]['metadata']['paragraph_end']=='1'];a=starts[-1] if starts else 0;b=ends[0] if ends else len(same)-1;chunk=same[a:b+1]
 nums=[int(x['metadata']['locus'].rsplit('.',1)[1]) for x in chunk];continuous=all(y==x+1 for x,y in zip(nums,nums[1:]));internal_boundary=any(x['metadata']['paragraph_start']=='1' for x in chunk[1:]) or any(x['metadata']['paragraph_end']=='1' for x in chunk[:-1])
 complete=bool(starts and ends and continuous and not internal_boundary)
 return {'seed':locus,'complete_marked_paragraph':complete,'has_start':bool(starts),'has_end':bool(ends),'consecutive_loci':continuous,'internal_boundary':internal_boundary,'lines':chunk,'groups':sum(len(x['words']) for x in chunk)}

def main():
 data=load();allocc={};summaries={};contexts={};joins={};paragraphs={};hostlines={}
 for ed,ls in data.items():
  flags=any(x['metadata']['paragraph_end']=='1' for x in ls);occ=[];bg=collections.Counter();hostlines[ed]={}
  for l in ls:
   w=l['words'];m=l['metadata'];leaf=int(re.match(r'f(\d+)',m['page'])[1]);N=len(w)
   for i,z in enumerate(w):
    if l['safe'][i] and re.fullmatch('[a-z]+',z):
     bg['safe_literal_groups']+=1
     if i==N-1:
      bg['line_final_groups']+=1
      if flags and m['paragraph_end']=='1':bg['paragraph_final_groups']+=1
   for target in TARGETS:
    seq=target.split();n=len(seq)
    for i in range(N-n+1):
     if w[i:i+n]!=seq:continue
     safe=all(l['safe'][j] for j in range(i,i+n));last=i+n==N;pend=(last and m['paragraph_end']=='1') if flags else None
     sig=None
     if safe and i>=2 and all(l['safe'][j] and re.fullmatch('[a-z]+',w[j]) for j in [i-2,i-1]):
      if last:right='PARAGRAPH_END' if flags and pend else 'LINE_END' if flags else 'UNKNOWN_PARAGRAPH_END'
      elif l['safe'][i+n] and re.fullmatch('[a-z]+',w[i+n]):right=w[i+n]
      else:right=None
      if right is not None:sig=[w[i-2],w[i-1],right]
     o={'target':target,'line':l['id'],'page':m['page'],'leaf':leaf,'locus':m['locus'],'start':i,'source_ids':l['group_ids'][i:i+n],'locally_safe':safe,'literal_line':l['literal_line'],'line_final':last,'paragraph_final':pend,'host_paragraph_end':m['paragraph_end'] if flags else 'UNAVAILABLE','left':w[:i],'right':w[i+n:],'signature':sig}
     occ.append(o);hostlines[ed][l['id']]=l
  allocc[ed]=occ;stats={}
  for t in TARGETS:
   os=[o for o in occ if o['target']==t];safe=[o for o in os if o['locally_safe']]
   stats[t]={'exact_occurrences':len(os),'safe_occurrences':len(safe),'leaves':len({o['leaf'] for o in safe}),'line_final':sum(o['line_final'] for o in safe),'paragraph_final':sum(o['paragraph_final'] is True for o in safe) if flags else None,'nonparagraph_final':sum(o['paragraph_final'] is False for o in safe) if flags else None,'complete_literal_line_occurrences':sum(o['literal_line'] for o in safe)}
  left=collections.defaultdict(list);right=collections.defaultdict(list)
  for o in occ:
   if o['signature'] is not None and o['target'] in {'chor','ykchor chordy'}:(left if o['target']=='chor' else right)[tuple(o['signature'])].append(o)
  joins[ed]=[{'signature':list(k),'chor':left[k],'long':right[k]} for k in sorted(left.keys()&right.keys())]
  leaves={o['leaf'] for j in joins[ed] for o in j['chor']+j['long']}
  summaries[ed]={'paragraph_flags_available':flags,'counts':stats,'background':dict(bg),'shared_flank_signatures':len(joins[ed]),'shared_flank_leaves':len(leaves),'expansion_capacity':len(joins[ed])>=2 and len(leaves)>=3,'strict_chor_closure':('UNAVAILABLE' if not flags else 'CONTRADICTED' if stats['chor']['nonparagraph_final'] else 'NOT_CONTRADICTED')}
  paragraphs[ed]=[paragraph(ls,x) for x in ['f15v.12','f19r.10']]
 write('OCCURRENCES.json',allocc);write('HOST_LINES.json',hostlines);write('PARAGRAPHS.json',paragraphs);write('FLANK_COMPARISONS.json',joins);write('RESULT.json',{'status':'COMPLETE_FIXED_CONTINUATION_AUDIT','panels':summaries,'confirmed_meanings':0,'significance_claim':False,'held_access':False,'prior_exposure':True})
 with (E/'artifacts/OCCURRENCES.tsv').open('w') as f:
  keys=['target','locus','start','locally_safe','literal_line','line_final','paragraph_final'];w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['edition']+keys+['left','right','row_status'])
  for ed,os in allocc.items():
   for o in os:w.writerow([ed]+[o[k] for k in keys]+[' '.join(o['left']),' '.join(o['right']),'recorded'])
 text=['# Whole seed paragraphs and missing-boundary contexts','','Original groups retained, including uncertainty. Paragraphs are transcriber markup, not independently established sentences.','']
 for ed,ps in paragraphs.items():
  for p in ps:
   text += [f"## {ed}: {p['seed']}",'',f"Complete marked paragraph: {p['complete_marked_paragraph']}; start/end: {p['has_start']}/{p['has_end']}; groups: {p['groups']}.",'']
   for l in p['lines']:text.append(l['metadata']['locus']+': `'+ ' '.join(l['words'])+'`')
   text.append('')
 (E/'FULL_PARAGRAPHS.md').write_text('\n'.join(text).rstrip()+'\n')
 print(json.dumps(summaries))
if __name__=='__main__':main()
