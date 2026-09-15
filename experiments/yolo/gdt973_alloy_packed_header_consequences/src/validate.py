"""Independent direct necessary-condition reconstruction, without primary import."""
import collections,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
RULES=['MIN_GROUPS','HEADER_WIDTH','HEADER_ISOLATION','ALL_GROUP_MIN','GLOBAL_INITIAL','HEADER_ENTRY','HEADER_END']
def evaluate(words,model):
 f={k:None for k in RULES};f['MIN_GROUPS']=len(words)>4;conflicts=[]
 if len(words)>3:
  lower=[12,5,5,3] if model=='R1' else [10,3,3,1];upper=[144,56,56,24] if model=='R1' else [128,40,40,8]
  f['HEADER_WIDTH']=all(lower[i]<=len(words[i])<=upper[i] for i in range(4))
  for i in range(4):
   for j in range(len(words)):
    if i==j:continue
    n=min(len(words[i]),len(words[j]))
    if words[i][:n]==words[j][:n]:conflicts.append([i,j,words[j]])
  f['HEADER_ISOLATION']=len(conflicts)==0
  if model=='R1':
   f['ALL_GROUP_MIN']=not any(len(w)<3 for w in words)
   f['GLOBAL_INITIAL']=len(set(''.join(w[:1] for w in words)))<3
   f['HEADER_ENTRY']=words[1][0]==words[2][0]==words[3][0]
   f['HEADER_END']=words[0][-1]==words[1][-1]==words[2][-1]==words[3][-1]
 bad=[k for k in RULES if f[k] is False]
 return dict(header=words[:4],header_lengths=[len(w) for w in words[:4]],min_group_length=min([len(w) for w in words],default=None),initials=sorted(set(w[0] for w in words)),conditions=f,prefix_conflicts=conflicts,contradictions=bad,decision=next(iter(bad),'NECESSARY_FORM_ONLY'))
def main():
 lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for n,h in lock['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
 if not (E/'artifacts/RESULT.json').exists():print('PASS_REGISTRATION_ONLY');return
 allowed=json.loads((R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json').read_text())['allowed_selectors'];assert len(set(allowed))==179 and not any(s.startswith('f84') or s=='f116v' for s in allowed)
 raw=json.loads((R/'experiments/yolo/gdt970_rota_whole_part_conjugacy/artifacts/PARAGRAPHS.json').read_text());rows=[];panels={}
 for m in ('R1','R2'):
  panels[m]={}
  for ed,ps in raw.items():
   panel=dict(complete=len(ps),eligible=0,unknown=0,literal_leaves=0,first={},all_failures={},survivors=[],survivor_leaves=[]);leaves=set();svleaves=set()
   for p in ps:
    assert p['page'] in allowed
    words=[]
    for line in p['lines']:words.extend(line['words'])
    assert p['full_text']==' '.join(words)
    x=dict(model=m,edition=ed,id=p['id'],page=p['page'],leaf=p['leaf'],eligible=p['literal_eligible'],defects=p['defects'],groups=len(words))
    if x['eligible']:
     assert words and all(w and set(w)<=set('abcdefghijklmnopqrstuvwxyz') for w in words)
     x.update(evaluate(words,m));panel['eligible']+=1;leaves.add(p['leaf'])
     panel['first'][x['decision']]=panel['first'].get(x['decision'],0)+1
     for c in x['contradictions']:panel['all_failures'][c]=panel['all_failures'].get(c,0)+1
     if not x['contradictions']:panel['survivors'].append(x['id']);svleaves.add(x['leaf'])
    else:
     panel['unknown']+=1;x.update(header=None,header_lengths=None,min_group_length=None,initials=None,conditions=dict.fromkeys(RULES),prefix_conflicts=[],contradictions=[],decision='UNKNOWN_NONLITERAL_COMPLETE')
    rows.append(x)
   panel['literal_leaves']=len(leaves);panel['survivor_leaves']=sorted(svleaves);panels[m][ed]=panel
 result=json.loads((E/'artifacts/RESULT.json').read_text());primary=json.loads((E/'artifacts/PREDICTIONS.json').read_text())
 counts={m:sum(len(x['survivors']) for x in panels[m].values()) for m in panels}
 expected=dict(status={m:'ALL_LITERAL_FORMS_CONTRADICTED' if not n else 'NECESSARY_FORM_SURVIVORS_NO_FULL_READING' for m,n in counts.items()},panels=panels,survivors=counts,rows=len(rows),translated_words=0,independent_confirmation_capacity=0,reserve_access=False,full_code_or_arithmetic_tested=False)
 checks={k:result.get(k)==v for k,v in expected.items()};checks['predictions_exact']=primary==rows
 j=lambda x:json.dumps(x,separators=(',',':'))
 table=[['model','edition','id','page','leaf','eligible','defects','groups','header',*RULES,'prefix_conflicts','contradictions','decision']]
 for x in rows:table.append([x['model'],x['edition'],x['id'],x['page'],x['leaf'],str(x['eligible']),j(x['defects']),str(x['groups']),j(x['header']),*[str(x['conditions'][k]) for k in RULES],j(x['prefix_conflicts']),j(x['contradictions']),x['decision']])
 with (E/'artifacts/CANDIDATE_PREDICTIONS.tsv').open() as f:checks['table_exact_cells']=list(csv.reader(f,delimiter='\t'))==table
 out=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,rows=len(rows),independent_meaning_confirmation=False)
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));assert out['status']=='PASS'
if __name__=='__main__':main()
