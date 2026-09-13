"""Compose frozen scoped hypotheses; no decoder or state simulator."""
import ast,collections,copy,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def save(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def table(n,rr,cols=None):
 cols=[k for k in (cols or list(rr[0])) if k!='row_status']+['row_status']
 with (E/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=cols,delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rr)
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
source=read(W/'W02/SOURCE.json');alt=read(W/'W02/ALTERNATE_LINES.json')['readings'];rules=read(W/'W05/SPEC.json')
D={r['form']:r for r in rows(W/'W02/LEXICON.tsv')}
for word,o in rules['word_overrides'].items():D[word]={**D[word],**o}
D['sheeody']={'role':'MATERIAL','hypothesis':'Pulver [Materialhypothese]'};D['qokeeo']={'role':'ACTION','hypothesis':'rühre [Hypothese]'}
ACT=set(rules['action_roles']);MAT=set(rules['material_roles']);MOD=set(rules['transparent_roles']);extracts={'cheor','okeeor','okeor','keeor','cheeor','sheeor'}
glosses={r['raw']:r['H'] for r in rows(W/'W10/ALIGNMENT.tsv')};glosses.update({k:D[k]['hypothesis'] for k in ('sheeody','qokeeo')})
for old,name in [('W05','base_arguments'),('W11','solve'),('W13','requal')]:
 fn=next(n for n in ast.parse((W/old/'build.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name)
 exec(compile(ast.Module(body=[fn],type_ignores=[]),'frozen_'+old+'_'+name,'exec'))
cols=['patient','patient_form','coingredient','rule','debts','shared_run','additional_grammar_assumption']
oldargs={(r['edition'],r['variant'],r['operation']):r for r in rows(W/'W05/ARGUMENTS.tsv')}
oldP={(r['edition'],r['variant'],r['operation']):r for r in rows(W/'W11/ARGUMENTS.tsv') if r['model']=='P'}
oldR={(r['edition'],r['variant'],r['operation']):r for r in rows(W/'W12/ARGUMENTS.tsv') if r['model']=='R'}
oldtake={(r['edition'],r['grammar'],r['target']):r for r in rows(W/'W08/TAKE_ARGUMENTS.tsv')};oldq=rows(W/'W05/QUALITY_ASSERTIONS.tsv')
allargs=[];comparisons=[];takes=[];quality=[];qcensus=[];allflat={};parity=collections.Counter()
def take(flat,x,aa,g):
 line=[z for z in flat if z['locus']==x['locus']];amap={a['operation']:a for a in aa};stop=min([z['offset'] for z in line if z['id'] in amap],default=10**9)
 right=[z for z in line if x['offset']<z['offset']<stop and z['role'] in MAT];earlier=[z for z in flat if z['offset']<x['offset'] and z['role'] in MAT]
 a=right[0] if right else earlier[-1] if earlier else None;rule='LOCAL_RIGHT' if right else 'PARAGRAPH_CARRY' if earlier else 'MISSING';debt=[]
 if a:
  lo,hi=sorted((a['offset'],x['offset']));debt=['UNREAD_BETWEEN:'+z['id'] for z in flat if lo<z['offset']<hi and z['role']=='OPEN']
  if rule=='PARAGRAPH_CARRY':debt.append('IMPLICIT_SUBJECT_CONTINUATION')
 else:debt=['MISSING_PATIENT']
 j=1;shared=[]
 while j<len(line) and line[j]['id'] in amap:shared.append(line[j]);j+=1
 if shared and g in ('J','M'):
  if g=='M':
   while j<len(line) and line[j]['role'] in MOD:j+=1
  if j<len(line) and line[j]['role'] in MAT:a=line[j];rule='SHARED_RIGHT_'+g;debt=[]
 return dict(patient=a['id'] if a else '',patient_form=a['form'] if a else '',rule=rule,debts=';'.join(debt))
for ed,ll in alt.items():
 mapped={l['metadata']['locus']:l for l in ll}
 for target in source['targets']:
  p=target['hosts']['ZL3b'][0];raw=[]
  for line in p['lines']:
   assert not line['locus'].startswith('f84')
   words=[z['ivtff_group_raw'] for z in mapped[line['locus']]['groups']]
   if ed=='ZL3b':assert words==line['words']
   for i,word in enumerate(words,1):raw.append(dict(id=line['locus']+':'+str(i),locus=line['locus'],index=i,form=word,role=D.get(word,{}).get('role','OPEN'),offset=len(raw)))
  cases={}
  for model in S['models']:
   flat=copy.deepcopy(raw)
   for x in flat:
    if x['form']=='sheeody' and 'P' not in model:x['role']='OPEN'
    if x['form']=='qokeeo' and 'R' not in model:x['role']='OPEN'
   versions=solve(flat);cases[model]=versions;allflat[(ed,p['id'],model)]=flat
   for g,aa in versions.items():
    for a in aa:
     allargs.append(dict(edition=ed,model=model,variant=g,paragraph=p['id'],**a))
     old={'U':oldargs,'P':oldP,'R':oldR}.get(model)
     if old is not None:
      prior=old[(ed,g,a['operation'])];assert all(a[k]==prior[k] for k in cols),(model,a,prior);parity[model]+=1
    for x in [x for x in flat if x['form']=='ychor']:
     assert x['index']==1
     n=take(flat,x,aa,g);old=oldtake[(ed,g,x['id'])]
     takes.append(dict(edition=ed,model=model,grammar=g,paragraph=p['id'],target=x['id'],**n,changed_fields=','.join(k for k in n if n[k]!=old[k])))
    if ed=='ZL3b':
     byid={x['id']:x for x in flat}
     for q in oldq:
      if q['variant']!=g or q['paragraph']!=p['id'] or q['kind']!='STANDALONE':continue
      qr=requal(q,flat,aa);x=byid[q['mention']];m=byid.get(qr['patient'])
      earlier=[a for a in aa if m and a['patient']==m['id'] and byid[a['operation']]['locus']==m['locus'] and byid[a['operation']]['offset']<m['offset']]
      eligible=bool(m and m['locus']==x['locus'] and m['offset']==x['offset']-1 and m['role'] in MAT and earlier)
      quality.append(dict(model=model,grammar=g,paragraph=p['id'],mention=q['mention'],form=q['form'],axis=q['axis'],value=q['value'],patient=qr['patient'],patient_form=qr['patient_form'],rule=qr['rule'],debts=qr['debts'],changed_fields=','.join(k for k in ('patient','patient_form','rule','debts') if q[k]!=qr[k]),input_eligible=eligible))
  for g in S['variants']:
   maps={m:{a['operation']:a for a in versions[g]} for m,versions in cases.items()}
   for op,joint in maps['PR'].items():
    base=maps['U'].get(op);pr=maps['P'].get(op);rr=maps['R'].get(op);unexpected=[];changes=[]
    if base:
     for k in cols:
      pv,rv,bv=pr[k],rr[k],base[k]
      if pv!=bv and rv!=bv and pv!=rv:unexpected.append(k+':COMPETING_SINGLE_CHANGES')
      expect=pv if pv!=bv else rv
      if joint[k]!=expect:unexpected.append(k+':JOINT_DIFFERS_FROM_SINGLE_UNION')
      if joint[k]!=bv:changes.append(k)
    elif rr:
     unexpected=[k+':NEW_ACTION_INTERACTION' for k in cols if joint[k]!=rr[k]]
    else:unexpected=['UNREGISTERED_ACTION']
    comparisons.append(dict(edition=ed,grammar=g,paragraph=p['id'],operation=op,form=joint['form'],old_patient=base['patient'] if base else '',joint_patient=joint['patient'],joint_patient_form=joint['patient_form'],old_debts=base['debts'] if base else '',joint_debts=joint['debts'],changed_fields=','.join(changes),new_action=base is None,interaction=';'.join(unexpected)))
table('ARGUMENTS.tsv',allargs);table('COMPOSITION_CHECK.tsv',comparisons);table('TAKE_ARGUMENTS.tsv',takes);table('QUALITY_BINDINGS.tsv',quality)
full=[];summary=[]
for r in rows(W/'W15/ALIGNMENT.tsv'):
 word=r['raw'];new=word in ('sheeody','qokeeo');full.append(dict(r,joint=glosses[word] if new else r['H'],joint_status='ASSUMED' if new else r['status'],branch='P' if word=='sheeody' else 'R' if word=='qokeeo' else 'N' if word=='ychor' else 'H' if word=='chol' else 'INHERITED'))
table('ALIGNMENT.tsv',full)
reader=['# W16 – gemeinsame bedingte Arbeitslesung','',
'Alle deutschen Wortwerte sind Hypothesen. N/H/P/R/I ist eine redaktionelle Zusammenstellung, keine entschlüsselte Sprache. Jede Originalgruppe bleibt erhalten; unbekannte Gruppen stehen unverändert in der Lesung. Die unten angeführten Handlungsobjekte verwenden durchgehend M. B und J stehen vollständig in den Tabellen; M ist nicht empirisch ausgewählt. Eingangsattribute gelten nur bei markierten J/M-Stellen. „Erneut“ bleibt mit offener Vorbedingung stehen. Keine Sätze über Pulver→Auszug oder identische Portionen werden ergänzt.','',
'Die Varianten MIX ein-/zweistellig sowie qotchy trenne/verbinde bleiben offen; die Argumenttabelle zeigt den bestehenden zweistelligen Vertrag. D=trockne und die übrigen Einzelwort-Rivalen bleiben außerhalb dieser Anzeigefassung erhalten.']
for p in dict.fromkeys(r['paragraph'] for r in full):
 pp=[r for r in full if r['paragraph']==p];aa=[r for r in allargs if r['edition']=='ZL3b' and r['model']=='PR' and r['variant']=='M' and r['paragraph']==p];nn=[r for r in takes if r['edition']=='ZL3b' and r['model']=='PR' and r['grammar']=='M' and r['paragraph']==p]
 summary.append(dict(paragraph=p,groups=len(pp),assumed=sum(r['joint_status']!='UNREAD' for r in pp),unread=sum(r['joint_status']=='UNREAD' for r in pp),processing_commands_M=len(aa),take_commands_M=len(nn),missing_processing_patient_M=sum(not r['patient'] for r in aa),processing_commands_with_debts_M=sum(bool(r['debts']) for r in aa)))
 reader+=['','## '+p,'',str(summary[-1]['assumed'])+'/'+str(len(pp))+' Gruppen mit angenommenem Wortwert; '+str(summary[-1]['unread'])+' offen.']
 for loc in dict.fromkeys(r['locus'] for r in pp):
  rr=[r for r in pp if r['locus']==loc];reader+=['',loc+': `'+' '.join(r['raw'] for r in rr)+'`','',' · '.join(r['joint']+(' {Eingangsattribut J/M}' if r['input_attribute_grammars'] else '')+(' {erneut: Vorbedingung offen}' if r['repeat_obligation']!='UNCHANGED' else '') for r in rr)]
  here=[a for a in aa if a['operation'].rsplit(':',1)[0]==loc]
  for a in here:reader+=['','M-Bindung '+a['operation']+' '+a['meaning']+' → '+(a['patient_form']+' ('+a['patient']+')' if a['patient'] else '**Objekt fehlt**')+('; zweites Objekt '+a['coingredient'] if a['coingredient'] else '')+('; offene Bindung: '+a['debts'] if a['debts'] else '')+'.']
  for n in nn:
   if n['target'].rsplit(':',1)[0]==loc:reader+=['','Separates Nimm-Objekt: '+(n['patient_form']+' ('+n['patient']+')' if n['patient'] else '**fehlt**')+('; '+n['debts'] if n['debts'] else '')+'.']
(E/'READING.md').write_text('\n'.join(reader)+'\n');table('PARAGRAPHS.tsv',summary)
result={'primary_paragraphs':len(summary),'primary_lines':len({r['locus'] for r in full}),'primary_groups':len(full),'assumed_groups':sum(r['joint_status']!='UNREAD' for r in full),'unread_groups':sum(r['joint_status']=='UNREAD' for r in full),'isolated_argument_parity':dict(parity),'joint_argument_rows':len(comparisons),'unexpected_interaction_rows':sum(bool(r['interaction']) for r in comparisons),'old_patient_change_rows':sum(r['old_patient']!=r['joint_patient'] and not r['new_action'] for r in comparisons),'old_patient_change_operations':sorted({r['operation'] for r in comparisons if r['old_patient']!=r['joint_patient'] and not r['new_action']}),'joint_take_changes':[r for r in takes if r['model']=='PR' and r['changed_fields']],'joint_quality_changes':[r for r in quality if r['model']=='PR' and r['changed_fields']],'joint_input_attributes':[dict(grammar=r['grammar'],mention=r['mention'],patient=r['patient']) for r in quality if r['model']=='PR' and r['input_eligible']],'state_simulation':False,'confirmed_meanings':0,'independent_confirmation_capacity':0,'held_access':False}
save('RESULT.json',result);print(json.dumps(result,ensure_ascii=False))
