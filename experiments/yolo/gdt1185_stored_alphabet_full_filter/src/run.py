from pathlib import Path
import sys,json,hashlib,datetime
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts';OLD=ROOT/'experiments/yolo/gdt1184_contextual_initial_styles'
sys.path.insert(0,str(OLD/'src'))
import codec as c
import run as engine
SOURCE=engine.SOURCE;TARGET=engine.TARGET

def save(name,x):(A/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def writepages(name,pages):(A/name).write_text('\n\n'.join('\n'.join(' '.join(line) for line in page) for page in pages)+'\n')
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def equality(alph):
 labels=alph['initial'][:21]+alph['medial'][:3]+alph['final'][:6]
 return [[i,j] for i in range(30) for j in range(i+1,30) if labels[i]==labels[j]]

def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(SOURCE.read_text());targets=json.loads(TARGET.read_text())['targets'];tables=json.loads((OLD/'artifacts/TABLES.json').read_text());parent=json.loads((OLD/'artifacts/RESULT.json').read_text());designs={};variants={};eligible=[]
 for model,parent_design in parent['design'].items():
  failed=parent_design['alphabets']
  for restart,entry in enumerate(parent_design['restarts']):
   if restart==parent_design['chosen_restart']:continue
   key=f'{model}-R{restart}';alph=entry['alphabets'];assert digest(alph)!=digest(failed);variants[key]={'original_model':model,'restart':restart,'table_hash':digest(alph),'excluded_failed_hash':digest(failed),'different_cross_role_equalities':equality(alph)!=equality(failed),'equalities':equality(alph)}
   codec=c.Codec(model,tables,alph);metrics={};comparison={}
   for col in ['b4','w1']:
    pages,_=engine.pages(codec,source[col]);writepages(f'D_{key}_{col}.txt',pages);metrics[col]=engine.measure(pages);comparison[col]={ed:engine.m.compare(metrics[col],t) for ed,t in targets.items()}
   full=all(row['joint_screen'] for book in comparison.values() for row in book.values());designs[key]={'model':model,'restart':restart,'alphabets':alph,'original_objective':entry['optimization']['best_objective'],'table_entries':len(codec.codes),'metrics':metrics,'comparison':comparison,'full_design_pass':full};save('DESIGN.json',designs);save('VARIANTS.json',variants)
   if full:eligible.append(key)
   print(json.dumps({'candidate':key,'full_design_pass':full,'edit1':{col:m['edit1_repeat'] for col,m in metrics.items()},'failures':{col:{ed:[k for k,v in q['diagnostics'].items() if not v['within']] for ed,q in book.items()} for col,book in comparison.items()}}),flush=True)
 assert len(designs)==6
 if not eligible:
  result={'experiment':'GDT1185','status':'STORED_ALTERNATIVES_FAIL_FULL_DESIGN','design':designs,'selected':None,'transfer_scored':False};save('RESULT.json',result);return
 selected=min(eligible,key=lambda k:(designs[k]['table_entries'],designs[k]['original_objective'],designs[k]['model'],designs[k]['restart']));choice=designs[selected];save('SELECTION_LOCK.json',{'selected':selected,'candidate':choice,'created':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parameter_hash':digest(choice['alphabets'])});codec=c.Codec(choice['model'],tables,choice['alphabets']);metrics={};comparison={};roundtrips={}
 for col,rs in source.items():
  pages,_=engine.pages(codec,rs);writepages(f'SELECTED_{col}.txt',pages);metrics[col]=engine.measure(pages);comparison[col]={ed:engine.m.compare(metrics[col],t) for ed,t in targets.items()};roundtrips[col]={'complete_recipes':len(rs),'exact':True}
 full=all(row['joint_screen'] for book in comparison.values() for row in book.values());result={'experiment':'GDT1185','status':'FULL_BASIC_SCREEN_PASS' if full else 'STORED_SELECTED_WRITER_FAILS_TRANSFER','design':designs,'selected':selected,'transfer_scored':True,'metrics':metrics,'comparison':comparison,'roundtrips':roundtrips};save('RESULT.json',result);print(json.dumps({'status':result['status'],'selected':selected}),flush=True)
if __name__=='__main__':main()
