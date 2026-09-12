from pathlib import Path
import csv,json,hashlib,itertools
D=Path(__file__).resolve().parent;W=D.parent;R=next(p for p in D.parents if (p/'vmanus-work').exists())
def read(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def tab(n,k,rs):
 with (D/n).open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(k+['row_status']);w.writerows([list(x)+['recorded'] for x in rs])
def js(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
s=read(W/'S05/INPUT.tsv');nouns={'cthy','chor','shor','okaiin'};ops={'sho','qotchy'}
lexA=dict(cthy='Rahmen',chor='Stift',shor='Platte',okaiin='Gehäuse',sho='füge an',qotchy='löse ab');lexM=dict(cthy='Krautmaterial',chor='Blütenmaterial',shor='Samenmaterial',okaiin='Flüssiganteil',sho='vermische',qotchy='trenne ab');lexL=lexA|{'sho':'Anfügen','qotchy':'Ablösen'}
bind=[];ev=[];joins=[];later=[]
for rec in dict.fromkeys(x['record'] for x in s):
 rr=[x for x in s if x['record']==rec];edges=set();mixtures=[];consumed=set()
 for i,x in enumerate(rr):
  if x['word'] not in ops:continue
  left=next((z for z in reversed(rr[:i]) if z['word'] in nouns),None)
  stop=next((j for j in range(i+1,len(rr)) if rr[j]['word'] in ops),len(rr));right=next((z for z in rr[i+1:stop] if z['word'] in nouns),None)
  gap=rr[i+1:next((j for j,z in enumerate(rr) if right and z['at']==right['at']),stop)]
  l=left['word'] if left else 'NONE';r=right['word'] if right else 'NONE'
  bind.append((rec,x['at'],x['word'],left['at'] if left else 'NONE',l,right['at'] if right else 'NONE',r,' '.join(z['word'] for z in gap) or 'EMPTY'))
  if not left or not right:a=m='MISSING_ARGUMENT';product='NONE'
  elif x['word']=='sho':
   a='JOINED';edges.add((l,r));product='implicit_product_at_'+right['at']
   if l in consumed or r in consumed:m='UNAVAILABLE_ISOLATED_INPUT'
   else:m='MIXED';mixtures.append({'id':product,'parts':{l,r}});consumed.update({l,r})
   joins.append((rec,x['at'],l,r,right['at'],a,m))
   idx=next(j for j,z in enumerate(rr) if z['at']==right['at'])
   for z in rr[idx+1:]:
    if z['word'] in {l,r}:later.append((rec,x['at'],z['at'],z['word'],'NAME_ONLY_NOT_OPERATION'))
  else:
   a='SELF_DETACH_NO_EDGE' if l==r else ('DETACHED' if (l,r) in edges else 'NO_PRIOR_EDGE')
   if (l,r) in edges:edges.remove((l,r))
   # No word naming a mixture result is bound by this six-card model.
   m='NO_BOUND_MIXTURE_SOURCE';product='NONE'
  ev.append((rec,x['at'],x['word'],l,r,a,m,product,';'.join(f'{a}>{b}' for a,b in sorted(edges)) or 'EMPTY'))
tab('BINDINGS.tsv',['record','at','word','left_at','left_word','right_at','right_word','open_right_interval'],bind)
tab('EVENTS.tsv',['record','at','word','left','right','assembly','mixture','implicit_product','assembly_edges_after'],ev)
tab('LATER_COMPONENT_MENTIONS.tsv',['record','join_at','later_at','word','status'],later)
comparisons=[]
for a,b in itertools.combinations(joins,2):
 comparisons.append((a[1],b[1],a[2]+'>'+a[3],b[2]+'>'+b[3],set(a[2:4])==set(b[2:4]),a[2:4]==b[2:4],a[0]!=b[0]))
tab('ALL_JOIN_PAIRS.tsv',['first','second','direction1','direction2','same_unordered_classes','same_direction','different_records'],comparisons)
for mode,lex in [('A',lexA),('M',lexM),('L',lexL)]:
 tab(f'ALIGNMENT_{mode}.tsv',['record','at','word','gloss'],[(x['record'],x['at'],x['word'],lex.get(x['word'],'OPEN')) for x in s])
 text=[f'# S12 {mode} — vollständiger hypothetischer Entwurf','','Sechs freie Ganzwortkarten; keine identifizierten Geräte oder Stoffe. Offene Gruppen bleiben erhalten. Verbindungen und Produkte sind nur Modellannahmen.','']
 for locus in dict.fromkeys(x['locus'] for x in s):
  ss=[x for x in s if x['locus']==locus];text+=['## '+locus,'','`'+' '.join(x['word'] for x in ss)+'`','',' · '.join(lex.get(x['word'],'⟦OPEN: '+x['word']+'⟧') for x in ss),'']
  for z in ev:
   if z[1].rsplit(':',1)[0]==locus:text += [f'{z[1]}: links {z[3]}, rechts {z[4]}; '+(z[5] if mode=='A' else z[6] if mode=='M' else 'keine Verbindung ausgeführt')+'.','']
 (D/f'READING_{mode}.md').write_text('\n'.join(text).rstrip()+'\n')
js('MODEL.json',{'A':lexA,'M':lexM,'L':lexL,'identity':'same whole per record; independent records','left':'last left noun','right':'first right noun before next operation','all_hypothetical':True})
js('RESULT.json',{'groups':len(s),'hypothesis_occurrences':sum(x['word'] in lexA for x in s),'operations':len(ev),'complete_argument_pairs':sum(x[3]!='NONE' and x[4]!='NONE' for x in ev),'joins':len(joins),'missing_argument_operations':sum(x[5]=='MISSING_ARGUMENT' for x in ev),'self_detach_no_edge':sum(x[5]=='SELF_DETACH_NO_EDGE' for x in ev),'later_component_mentions':len(later),'join_then_detach':sum(x[5]=='DETACHED' for x in ev),'reversed_same_class_join_pairs':sum(x[4] and not x[5] for x in comparisons),'confirmed_meanings':0,'held_access':False,'decision':'two local directional assemblies versus same unordered mixture;no later component-use discriminator;do not select'})
files=['S05/INPUT.tsv','P06/REPORT.md','P27/REPORT.md','S05/REPORT.md','S12/DECISION.md']
js('SOURCE.json',{'files':[{'path':str((W/p).relative_to(R)),'sha256':hashlib.sha256((W/p).read_bytes()).hexdigest()} for p in files],'exposure':'145groups already exposed;whole new hypothesis values explicitly authored','sealed':['f84','f84r']})
print((D/'RESULT.json').read_text())
