#!/usr/bin/env python3
import csv,json,hashlib,re,itertools
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P25')
S=D.parent/'P11/INPUT.json';T=Path('experiments/yolo/gdt811_four_page_content_synthesis/artifacts/FOUR_PAGES_FULL_TEXT.md')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,v):(D/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def tab(n,rs):
 with (D/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs)
lines=json.loads(S.read_text())['lines'];assert sum(len(r['groups']) for r in lines)==145
# Source is an already published, four-page bounded display; select f88r section only.
section=T.read_text().split('## f88r\n',1)[1].split('\n## ',1)[0]
labels=[]
for m in re.finditer(r'### (f88r\.\d+) — LOCAL INSCRIPTION\n\n([^\n]+)',section): labels.append({'locus':m[1],'raw':m[2]})
assert len(labels)==15 and sum(len(x['raw'].split()) for x in labels)==16
classes={'cthy':'Pflanzenzubereitung','chor':'Blütenzubereitung','shor':'Fruchtzubereitung','chocthy':'feine Fraktion','cthaiin':'grobe Fraktion','okaiin':'flüssige Zubereitung'}
lex=classes|{'chol':'trocken','shol':'feucht','daiin':'III'}
js('INPUT.json',{'herb_source':str(S),'herb_sha256':sha(S),'label_source':str(T),'label_sha256':sha(T),'decision_sha256':sha(D/'DECISION.md'),'lines':lines,'labels':labels})
js('MODEL.json',{'whole_word_hypotheses':lex,'all_hypothetical':True,'class_tree_root':'cthy','class_tree_children':[x for x in classes if x!='cthy'],'definition_scope':'whole paragraph homogeneous object','list_scope':'new item at every class occurrence'})
allconf=[];allval=[];summ=[];signatures={};bindings=[]
for model in ['D','L']:
 rows=[];rec=None;current=None;properties={};counter=0
 for line in lines:
  r=line['locus'].split('.')[0]
  if rec!=r:rec=r;current=None;properties={};counter=0
  signatures.setdefault(rec,{'classes':set(),'qualities':set()})
  for i,w in enumerate(line['groups'],1):
   loc=f"{line['locus']}:{i}";gloss='['+w+']';bound='NA';role='OPEN'
   if w in classes:
    signatures[rec]['classes'].add(w);role='CLASS';counter+=1
    current=rec+(':definition' if model=='D' else ':item'+str(counter));bound=current
    gloss=('ist unter anderem ' if model=='D' else 'Listenposten: ')+classes[w]
    bindings.append({'model':model,'record':rec,'locus':loc,'word':w,'target':bound})
   elif w in ['chol','shol']:
    signatures[rec]['qualities'].add(w);role='QUALITY';bound=rec+':definition' if model=='D' else current or 'UNBOUND';gloss=lex[w]+' → '+bound
   elif w=='daiin':
    role='VALUE';prev=line['groups'][i-2] if i>1 else None
    bound=f"{line['locus']}:{i-1}" if prev in classes or prev in ['chol','shol'] else 'UNBOUND'
    gloss=('Grad III' if model=='D' else 'drei Portionen')+' → '+bound
    allval.append({'model':model,'record':rec,'locus':loc,'target':bound,'reading':gloss})
   attrs=[]
   if w in ['chol','shol']:attrs=[w]
   if w in ['chocthy','cthaiin']:attrs=[w]
   if attrs and bound not in ['NA','UNBOUND']:
    p=properties.setdefault(bound,{})
    for a in attrs:
     opposite={'chol':'shol','shol':'chol','chocthy':'cthaiin','cthaiin':'chocthy'}[a]
     if opposite in p:allconf.append({'model':model,'record':rec,'target':bound,'earlier_locus':p[opposite],'earlier_property':opposite,'later_locus':loc,'later_property':a})
     p[a]=loc
   rows.append({'record':rec,'locus':loc,'word':w,'role':role,'target':bound,'reading':gloss})
 assert len(rows)==145
 tab('ALIGNMENT_'+model+'.tsv',rows)
 prose=['# P25 '+model+' — vollständige hypothetische Fassung','','Alle Klammerwörter sind offen; auch die übrigen Werte sind unbestätigt.']
 for line in lines:
  a=[x for x in rows if x['locus'].rsplit(':',1)[0]==line['locus']]
  prose+=['','## '+line['locus'],'','Quelle: `'+line['raw_line']+'`','','Lesung: '+' · '.join(x['reading'] for x in a)]
 (D/('READING_'+model+'.md')).write_text('\n'.join(prose)+'\n')
 summ.append({'model':model,'hypothesis_positions':sum(x['role']!='OPEN' for x in rows),'open_positions':sum(x['role']=='OPEN' for x in rows),'conflict_pairs':sum(x['model']==model for x in allconf),'unbound_qualities':sum(x['role']=='QUALITY' and x['target']=='UNBOUND' for x in rows),'bound_value_fields':sum(x['role']=='VALUE' and x['target']!='UNBOUND' for x in rows),'unbound_values':sum(x['role']=='VALUE' and x['target']=='UNBOUND' for x in rows)})
tab('CONTRADICTIONS.tsv',allconf);tab('VALUE_FIELDS.tsv',allval);tab('CLASS_BINDINGS.tsv',bindings)
edge=[]
for c in classes:
 if c=='cthy':continue
 witnesses=[r for r,s in signatures.items() if c in s['classes'] and 'cthy' in s['classes']]
 edge.append({'child':c,'parent':'cthy','cooccurrence_records':','.join(witnesses) or 'NONE','child_loci':','.join(x['locus'] for x in bindings if x['model']=='D' and x['word']==c),'parent_loci_in_witness_records':','.join(x['locus'] for x in bindings if x['model']=='D' and x['word']=='cthy' and x['record'] in witnesses) or 'NONE','written_subordination_operator':'NOT_IDENTIFIED','status':'AUTHORED_EDGE_NOT_ESTABLISHED'})
tab('TREE_EDGES.tsv',edge)
pairs=[]
for a,b in itertools.combinations(signatures,2):
 sa=signatures[a]['classes']|signatures[a]['qualities'];sb=signatures[b]['classes']|signatures[b]['qualities']
 pairs.append({'entry_a':a,'entry_b':b,'a_only':','.join(sorted(sa-sb)) or 'NONE','b_only':','.join(sorted(sb-sa)) or 'NONE','same_feature_set':int(sa==sb),'status':'AUTHORED_GLOSSES_NOT_SEMANTIC_DISTINCTIONS'})
tab('ALL_ENTRY_PAIRS.tsv',pairs)
lab=[]
for r in labels:
 for i,w in enumerate(r['raw'].split(),1):lab.append({'locus':r['locus']+':'+str(i),'word':w,'reading':lex.get(w,'['+w+']'),'exact_hypothesis_match':int(w in lex)})
tab('ALL_LABEL_GROUPS.tsv',lab)
result={'status':'PARTIAL_DEFINITION_LIST_COMPARISON','herb_groups':145,'whole_word_assumptions':9,'models':summ,'class_nodes':6,'authored_edges':5,'edges_with_same_record_cooccurrence':sum(x['cooccurrence_records']!='NONE' for x in edge),'identified_subordination_operators':0,'entry_pairs':6,'distinct_authored_feature_sets':sum(not x['same_feature_set'] for x in pairs),'label_inscriptions':15,'label_groups':16,'exact_label_transfers':sum(x['exact_hypothesis_match'] for x in lab),'independent_confirmation_capacity':0,'confirmed_meanings':0,'held_pages_opened':0}
js('RESULT.json',result);print(json.dumps(result,indent=2))
