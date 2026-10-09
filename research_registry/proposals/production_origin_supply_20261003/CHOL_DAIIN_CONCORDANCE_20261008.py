"""Complete literal pair concordance from the existing guarded profile cache.
Descriptive readout only: no meaning, significance, new decoder or native test.
"""
import sys,json,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from tools import word_profiles
B=ROOT/'research_registry/proposals/production_origin_supply_20261003'
conn=word_profiles.ensure_cache();events=[]
for first,second in [('chol','daiin'),('daiin','chol')]:
    for a in word_profiles.occurrences(conn,first):
        if a['next_literal']!=second:continue
        line=[dict(r) for r in conn.execute('SELECT * FROM groups WHERE edition=? AND locus=? ORDER BY source_group_index',(a['edition'],a['locus']))]
        i=next(i for i,r in enumerate(line) if r['source_group_id']==a['source_group_id']);z=line[i+1]
        assert z['ivtff_group_raw']==second
        assert z['source_group_index']==a['source_group_index']+1
        events.append({'reader':a['edition'],'locus':a['locus'],'page':a['page'],'order':[first,second],'group_index':a['source_group_index'],'section':a['section'],'hand':a['hand'],'currier':a['currier'],'kind':a['kind'],'seam':[a['right_separator'],z['left_separator']],'strict_seam':a['right_separator']==z['left_separator']=='DEFINITE_SPACE','left':line[i-1]['ivtff_group_raw'] if i else None,'right':line[i+2]['ivtff_group_raw'] if i+2<len(line) else None,'right_separator':z['right_separator'],'complete_line':line})
summary=[]
for reader in word_profiles.EDITIONS:
    for order in [('chol','daiin'),('daiin','chol')]:
        xs=[e for e in events if e['reader']==reader and e['order']==list(order)]
        frames=collections.defaultdict(list)
        for e in xs:
            if e['strict_seam'] and e['left'] is not None and e['right'] is not None:frames[e['left'],e['right']].append(e['locus'])
        summary.append({'reader':reader,'order':order,'raw_pairs':len(xs),'definite_inner_seam':sum(e['strict_seam'] for e in xs),'pages':len(set(e['page'] for e in xs)),'line_final':sum(e['right'] is None for e in xs),'line_initial':sum(e['left'] is None for e in xs),'left_counts':dict(collections.Counter(e['left'] if e['left'] is not None else '<LINE_START>' for e in xs)),'right_counts':dict(collections.Counter(e['right'] if e['right'] is not None else '<LINE_END>' for e in xs)),'repeated_complete_literal_frames':[{'left':k[0],'right':k[1],'loci':v} for k,v in frames.items() if len(v)>1]})
result={'status':'EXPOSED_LITERAL_PAIR_CONCORDANCE_NO_MEANING','receipt':word_profiles.receipt(conn),'events':events,'summary':summary,'program_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'179admitted cached selectors; same-locus raw adjacency; no entity normalization or cross-line joining. Inner-seam certainty reported separately. Whole lines retained. No boundary or linguistic interpretation; frames are literal descriptive matches, not significance or statement parses.'}
(B/'CHOL_DAIIN_CONCORDANCE_RESULT_20261008.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
for e in events:
 if e['reader']=='ZL3b' and e['order']==['chol','daiin']:
  print(e['locus'],e['seam'], ' '.join(('~ ' if r['left_separator']=='UNCERTAIN_SMALL_SPACE' else '')+r['ivtff_group_raw'] for r in e['complete_line']))
