"""Post-run finite projection certificates and complete tuple census."""
import csv,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
cfg=read(E/'src/SPEC.json');result=read(A/'RESULT.json');rows=read(A/'ROWS.json');pred=read(A/'PREDICTIONS.json');g=read(R/cfg['grammar']);key=lambda v:json.dumps(v,sort_keys=True)
p24=pred[0]['paragraphs'][1];p100,p96=pred[1]['paragraphs'];assert p24['words'][26]=='okaiin' and len(p24['words'])==33 and p100['words'][29]=='dcheor' and len(p100['words'])==36
assert g['patterns']['CONCLUSION']==['THUS','ALL','UNHARMED','THERE','ATTENDED_BY','@Agent']
assert [(k,i) for k,pat in g['patterns'].items() for i,v in enumerate(pat) if v=='ALONE']==[('ALONE',1)]
assert [(k,i) for k,pat in g['patterns'].items() for i,v in enumerate(pat) if v=='RETURN']==[('WITH_RETURN',2),('ALONE',0)]
assert sum(len(g['patterns'][k]) for k in ('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION'))==26 and len(p96['words'])==30
assert p96['words'][16]=='s' and p96['words'][19]=='dcheor' and g['patterns']['STAY']==['LEAVE','THERE']
assert [(k,i) for k,pat in g['patterns'].items() for i,v in enumerate(pat) if v=='THERE']==[('STAY',1),('CONCLUSION',3)]
# At30groups, STAY leaves only2groups beyond mandatory scope. Any successful
# transport needs a voyage, so it would be exactly one2group voyage and noTHEN.
# Then s at17 can only be mandatory CAPACITY's last cargo, FERRY's last cargo,
# or EXCLUDE's last cargo. All end17; STAY starts19, leaving unowned position18.
assert g['patterns']['CAPACITY'][-1]=='@Cargo' and g['patterns']['FERRY'][-1]==g['patterns']['EXCLUDE'][-1]=='@CargoRef'
assert sorted(k for k in ('WITH_OUT','EXCLUDE','FERRY','WITH_RETURN','CONVEY','ALONE','FINAL_TRIP') if len(g['patterns'][k])==2)==['ALONE','EXCLUDE','FERRY']
proofs=[dict(id='FINAL_RETURN',systems=['P0-3','P2-4'],conditions=['okaiin=ALONE','okaiin=RETURN','dcheor=ALONE'],argument='These values force a return ending immediately before the mandatory conclusion, on f24 or f100. No later trip exists. Agent ends L, but complete goal requires R.'),dict(id='TWO_CARGO_CAPACITY',system='P2-4',condition='dcheor and s are distinct members of W/G/C',argument='Both explicitly named cargoes on f96 belong to the initial inventory. At least3voyages are needed to move two cargoes and agent R; mandatory26 plus minimum6voyage groups requires32, exceeding30. All6unequal pairs are impossible.'),dict(id='STAY_SLOT',system='P2-4',condition='dcheor=THERE; s in W/G/C',argument='THERE at20 forces STAY19–20 because CONCLUSION THERE is28. Mandatory26+STAY2 leaves2groups, exactly one minimum voyage with noTHEN. A cargo at17 must then end CAPACITY13–17 or FERRY/EXCLUDE16–17. Position18 is uncovered before STAY19, requiring at leastone additional group. Thus no complete coherent layout fits30groups.')]
expected0=[dict(okaiin=x) for x in ['ALONE','RETURN']]
expected1=[dict(dcheor=d,s=s,shodol='M') for d in ['ALONE','THERE'] for s in ['C','G','W']]+[dict(dcheor=d,s=s,shodol='M') for d in ['C','G','W'] for s in ['C','G','W'] if d!=s]
assert {key(x) for x in result['systems'][0]['syntax_only_tuples']}=={key(x) for x in expected0}
assert {key(x) for x in result['systems'][1]['syntax_only_tuples']}=={key(x) for x in expected1}
lines=['# All syntax projection representatives','','These full grammatical parses need not be coherent worlds. The fixed GDT1003 tuple projection determines whether some coherent full dictionary/parse exists for each tuple; that status does not assert this arbitrary syntax representative is coherent.']
table=[]
for r,p,c in zip(rows,pred,result['systems']):
 excluded={key(x) for x in c['syntax_only_tuples']}
 for i,t in enumerate(r['tuples'],1):
  ident=r['id']+'-S'+str(i).zfill(2);survives=key(t['values']) not in excluded
  table.append([ident,r['id'],key(t['values']),True,survives,0]);lines+=['',f"## {ident}: {t['values']}",'',f"Some coherent dictionary exists for this shared tuple: {survives}."]
  for par,parse in zip(p['paragraphs'],t['witness']['parses']):
   lines+=['',par['id'],'','| All written groups | Fixed hypothetical terminal values |','|---|---|'];lines += ['| '+' '.join(par['words'][n['start']:n['end']])+' | '+n['kind']+': '+' '.join(n['symbols'])+' |' for n in parse]
with (A/'TUPLES.tsv').open('w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['id','system','shared_values','grammar_possible','some_coherent_world_possible','independent_meaning_capacity']);w.writerows(table)
(A/'READINGS.md').write_text('\n'.join(lines)+'\n');out=dict(status='PASS',scope='Post-run exact set comparison and short logical consequences; no new fit',syntax_tuples=len(table),content_excluded_tuples=sum(not r[4] for r in table),certificates=proofs,conditional_relation='If s and dcheor both name cargoes, they name the same cargo in this fixed two-paragraph model. Their cargo status itself is not established.')
(A/'EXPLANATIONS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
