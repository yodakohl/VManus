from common import *
def prepare():
 lm_path=R/'experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_155_MATCHED_STEM_SUMMARY.tsv'
 with lm_path.open() as f:lm=[[r['l_surface'],r['m_surface']] for r in csv.DictReader(f,delimiter='\t')]
 stems=load(R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/CANDIDATES.json')
 lr=[[[a+'r',b+'r'],[a+'l',b+'l']] for a,b in stems]
 assert len(lm)==155 and len(lr)==22
 lib={'LM':lm,'LR_PHRASE':lr,'meaning':'attested forms only; invariant reference meaning is a new hypothesis'};save(E/'src/LIBRARY.json',lib)
 prior=parent();spec=load(P/'src/SPEC.json');data=load(P/'artifacts/INPUT.json')
 assert {r['page'] for r in data['raw']}=={'f67r2'}
 # Retain only title rows before the inherited projection. No body matching here.
 titles=set(s['title'] for s in spec['sectors']);td={'raw':[r for r in data['raw'] if r['locus'] in titles],'legacy':[]};ts=dict(spec,models=['LITERAL']);rec=prior.line_records(td,ts)
 predictions=[]
 for ed in spec['editions']:
  for model in MODELS:
   for sec in spec['sectors']:
    title=rec[ed,sec['title'],'LITERAL'];vs=variants(title['values'],model,lib)
    predictions.append({'edition':ed,'model':model,'sector':sec['sector'],'locus':sec['title'],'title':title,'variants':vs})
 save(E/'artifacts/FROZEN_TITLE_PREDICTIONS.json',predictions)
 with (E/'artifacts/FROZEN_TITLE_VARIANTS.tsv').open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['edition','model','sector','locus','raw_title','definite_title','variant_count','variant'])
  for x in predictions:
   for v in x['variants']:w.writerow([x['edition'],x['model'],x['sector'],x['locus'],' '.join(x['title']['values']),all(x['title']['valid']),len(x['variants']),' '.join(v)])
 print(json.dumps({'title_model_cases':len(predictions),'expanded_cases':sum(len(x['variants'])>1 for x in predictions),'variants':sum(len(x['variants']) for x in predictions),'body_comparison':'NOT_RUN'}))
if __name__=='__main__':prepare()
