from pathlib import Path
import json,csv,hashlib,collections
D=Path(__file__).resolve().parent.relative_to(Path.cwd());B=D.parent;sp=Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json');s=json.loads(sp.read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);hits=[];lines=[]
for path in s['sources']:
 assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==s['hashes'][path]
 d=json.loads(Path(path).read_text());wi=d['group_columns'].index('ivtff_group_raw');si=d['group_columns'].index('source_group_id')
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84');ws=[g[wi] for g in l['groups']];ids=[g[si] for g in l['groups']];line=dict(edition=m['edition'],page=m['page'],locus=m['locus'],words=ws,ids=ids);lines.append(line)
  hits.extend(line|dict(at=ids[i],index=i,word=w) for i,w in enumerate(ws) if w in {'chotey','teey','teeys'})
loci={r['locus'] for r in hits};src=Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json');ps={(p['edition'],p['id']):p for p in json.loads((B/'W87/PARAGRAPHS.json').read_text())}
for ed,pp in json.loads(src.read_text()).items():
 for p in pp:
  if any(l['locus'] in loci for l in p['lines']):ps[ed,p['id']]=dict(edition=ed,**p)
lex=json.loads((B/'W87/LEXICON.json').read_text())|{'ychocthy':json.loads((B/'W87/MODELS.json').read_text())['A']};rows=[];md=['# W88 complete frozen context reading','Targets remain untranslated. No noun added to satisfy the mixing hypothesis.'];al=[]
for h in hits:
 i=h['index'];ws=h['words'];left=ws[i-1] if i else '';right=ws[i+1] if i+1<len(ws) else ''
 rows.append(dict(edition=h['edition'],locus=h['locus'],at=h['at'],word=h['word'],left=left,left_kind=lex.get(left,{}).get('kind','UNKNOWN'),right=right,right_kind=lex.get(right,{}).get('kind','UNKNOWN'),after_operation=left in {'qotchy','qotaiin','chkaiin','sheey','ychocthy'},motivating_locus=h['locus']=='f93r.24',same_line_materials=' '.join(w for w in ws if lex.get(w,{}).get('kind') in {'MATERIAL','MATERIAL_DOSE'}),same_line_values=' '.join(w for w in ws if w in {'dair','dain','daiin'})))
for p in ps.values():
 md+=['\n## '+p['edition']+' '+p['id']]
 for l in p['lines']:
  gg=[]
  for w,at in zip(l['words'],l['source_ids']):
   n={'dair':'A','dain':'B','daiin':'C'}.get(w);g='Masse '+n+'·Uₚ' if n else lex.get(w,{}).get('meaning','⟦'+w+'⟧');gg.append(g);al.append(dict(edition=p['edition'],paragraph=p['id'],at=at,word=w,gloss=g))
  md+=['\n'+l['locus']+' `'+ ' '.join(l['words'])+'`','\n'+' · '.join(gg)]
for name,rr in [('DIAGNOSTICS.tsv',rows),('ALIGNMENT.tsv',al)]:
 with (D/name).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rr[0]),delimiter='\t');wr.writeheader();wr.writerows(rr)
for name,obj in [('OCCURRENCES.json',hits),('READING_VARIANTS.json',[l for l in lines if l['locus'] in loci]),('PARAGRAPHS.json',list(ps.values())),('LEXICON.json',lex)]: (D/name).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n')
(D/'READING.md').write_text('\n'.join(md)+'\n');r=dict(hits=len(hits),counts=dict(collections.Counter(h['word']+'|'+h['edition'] for h in hits)),loci=sorted(loci),paragraphs=len(ps),groups=len(al),operation_contacts=[r for r in rows if r['after_operation']],meaning_confirmed=False);(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');paths=[sp,Path(s['allow_source']),src,B/'W87/PARAGRAPHS.json',B/'W87/LEXICON.json',B/'W87/MODELS.json']+[Path(p) for p in s['sources']];(D/'SOURCE_HASHES.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n');print(json.dumps(r))
