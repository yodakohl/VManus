"""Source-only intake. Gold is separated from numeric predictor interfaces."""
import collections,hashlib,json,unicodedata,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
ORDER=['b4','b6','br1','bs1','gr1','w1']
ROLES={'title','opener','instruction','ingredient','tool','dish','name','closer','kitchenTip','householdTip','servingTip','time','dietetics','alternative','ref','unclear'}
XMLID='{http://www.w3.org/XML/1998/namespace}id'
def lname(n):return n.tag.rsplit('}',1)[-1]
def normtitle(x):return ' '.join(unicodedata.normalize('NFC',x).casefold().split())
def intake(root,source):
 records={};counts={}
 for spec in source['data']:
  path=root/spec['path'];raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==spec['sha256'] and len(raw)==spec['bytes']
  collection=spec['collection_id'];tree=ET.fromstring(raw);rs=[];den=collections.Counter()
  for ordinal,recipe in enumerate(tree.findall('.//*[@type="recipe"]'),1):
   rid=recipe.get(XMLID,f'{collection}.ordinal{ordinal}');events=[];excluded=[];titles=[];element_ordinal=0
   for node in recipe.iter():
    tag=lname(node)
    if tag not in ROLES:continue
    element_ordinal+=1
    if tag=='title':
     title=node.get('en') or node.get('key') or ''.join(node.itertext());titles.append(normtitle(title))
    if tag!='ingredient':continue
    den['ingredient_elements']+=1;rawspan=''.join(node.itertext());surface=unicodedata.normalize('NFC',rawspan).strip();concept=node.get('commodity','');reasons=[]
    if not concept.strip():reasons.append('EMPTY_COMMODITY')
    if any(child is not node and child.get('commodity','').strip() for child in node.iter()):reasons.append('COMMODITY_BEARING_DESCENDANT')
    if node.get('ana','').strip():reasons.append('NONEMPTY_ANA')
    if len(surface.split())!=1:reasons.append('NOT_ONE_WHITESPACE_TOKEN')
    e={'source_id':f'{collection}|{rid}|E{element_ordinal:04d}','recipe_id':rid,'element_ordinal':element_ordinal,'original_span':rawspan,'surface':surface,'concept':concept,'english_label':node.get('en') or node.get('key') or '', 'ana':node.get('ana',''),'reasons':reasons}
    if reasons:excluded.append(e);den['excluded']+=1;den.update('reason:'+r for r in reasons)
    else:events.append(e);den['eligible']+=1
   rs.append({'collection':collection,'recipe_id':rid,'recipe_ordinal':ordinal,'normalized_titles':sorted(set(t for t in titles if t)),'events':events,'excluded':excluded})
  den['recipes']=len(rs);records[collection]=rs;counts[collection]=dict(den)
 assert set(records)==set(ORDER)
 predictors=[];gold=[]
 for fi,held in enumerate(ORDER):
  training=[r for col in ORDER if col!=held for r in records[col]];test=records[held];cf=collections.Counter(c for r in training for c in {e['concept'] for e in r['events']});wf=collections.Counter(w for r in test for w in {e['surface'] for e in r['events']})
  concepts=sorted(cf,key=lambda c:(-cf[c],c))[:4];forms=sorted(wf,key=lambda w:(-wf[w],w.encode('utf-8')))[:7]
  capacity=len(concepts)==4 and len(forms)==7
  S=[[int(c in {e['concept'] for e in r['events']}) for c in concepts] for r in training];B=[[int(w in {e['surface'] for e in r['events']}) for w in forms] for r in test]
  predictors.append({'fold_index':fi,'held_collection':held,'capacity':capacity,'train_incidence':S,'held_incidence':B})
  labels={c:sorted({e['english_label'] for r in training for e in r['events'] if e['concept']==c and e['english_label']}) for c in concepts};formrows=[]
  for w in forms:
   es=[e for r in test for e in r['events'] if e['surface']==w];qs=collections.Counter(e['concept'] for e in es)
   formrows.append({'surface':w,'recipe_presence':wf[w],'occurrences':len(es),'gold_counts':dict(sorted(qs.items())),'gold_labels':{c:sorted({e['english_label'] for e in es if e['concept']==c and e['english_label']}) for c in qs},'source_ids':[e['source_id'] for e in es],'original_spans':sorted({e['original_span'] for e in es})})
  train_titles={t for r in training for t in r['normalized_titles']};held_titles={t for r in test for t in r['normalized_titles']};total=sum(len(r['events']) for r in test)
  gold.append({'fold_index':fi,'held_collection':held,'concepts':concepts,'concept_labels':labels,'concept_recipe_presence':{c:cf[c] for c in concepts},'forms':formrows,'training_recipe_ids':[r['collection']+'|'+r['recipe_id'] for r in training],'held_recipe_ids':[held+'|'+r['recipe_id'] for r in test],'total_held_eligible_occurrences':total,'selected_form_occurrences':sum(x['occurrences'] for x in formrows),'unselected_form_occurrences':total-sum(x['occurrences'] for x in formrows),'normalized_title_rule':'NFC,casefold,whitespace collapse; en then key then source title text','shared_normalized_titles':sorted(train_titles&held_titles),'held_recipes_with_shared_title':sum(bool(set(r['normalized_titles'])&train_titles) for r in test)})
 return {'collections':records,'counts':counts},predictors,gold
