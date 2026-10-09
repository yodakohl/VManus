"""Bounded manual-reading packet; uses the existing guarded profile cache."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re,subprocess
from tools.word_profiles import ensure_cache,receipt,occurrences,EDITIONS

P=Path('research_registry/proposals/production_origin_supply_20261003')
spec_path=P/'HAND_WORD_EXTREMES_SELECTION_20261005.json'
spec=json.loads(spec_path.read_text()); signs=spec['inventory']
c=ensure_cache()

def parses(w):
    if not re.fullmatch('[a-z]+',w): return []
    dp=[[] for _ in range(len(w)+1)];dp[0]=[[]]
    for i in range(len(w)):
        for s in signs:
            if w.startswith(s,i):
                dp[i+len(s)].extend(p+[s] for p in dp[i])
    return dp[-1]

def natural(s):
    return tuple((0,int(x)) if x.isdigit() else (1,x) for x in re.split('(\\d+)',s))

voc={ed:[dict(r) for r in c.execute('SELECT form,n FROM vocabulary WHERE edition=? ORDER BY n DESC,form',(ed,))] for ed in EDITIONS}
freq={ed:rows[:3] for ed,rows in voc.items()}
long={};raw_long={};eligible={}
for ed,rows in voc.items():
    tmp=[];excluded=defaultdict(int)
    for r in rows:
        pp=parses(r['form'])
        if len(pp)==1: tmp.append(dict(r,glyphs=pp[0],length=len(pp[0])))
        else: excluded['nonliteral_or_unparsed' if not pp else 'multiple_parses']+=r['n']
    long[ed]=sorted(tmp,key=lambda r:(-r['length'],r['form']))[:2]
    eligible[ed]={'types':len(tmp),'excluded_tokens':dict(excluded)}
    raw_long[ed]=sorted([r for r in rows if re.fullmatch('[a-z]+',r['form'])],key=lambda r:(-len(r['form']),r['form']))[:2]
freq_forms=sorted({r['form'] for rows in freq.values() for r in rows})
long_forms=sorted({r['form'] for rows in long.values() for r in rows})
maps={ed:{r['form']:r['n'] for r in rows} for ed,rows in voc.items()}
rare={}
for length in (3,5,7):
    candidates=[]
    for w,n in maps['ZL3b'].items():
        pp=parses(w)
        if n!=1 or len(pp)!=1 or len(pp[0])!=length or not all(maps[e].get(w)==1 for e in EDITIONS): continue
        rr=occurrences(c,w)
        if len({(r['page'],r['locus']) for r in rr})!=1:continue
        if not all(r['left_separator'] in ('DEFINITE_SPACE','LINE_START') and r['right_separator'] in ('DEFINITE_SPACE','LINE_END') for r in rr):continue
        z=next(r for r in rr if r['edition']=='ZL3b')
        candidates.append((natural(z['page']),natural(z['locus']),z['source_group_index'],w))
    rare[str(length)]={'eligible_forms':len(candidates),'selected':min(candidates)[-1] if candidates else None}
forms=sorted(set(freq_forms+long_forms+[v['selected'] for v in rare.values() if v['selected']]+['daldy']))
loci=set();reasons=defaultdict(list)
for w in forms:
    rr=occurrences(c,w)
    if w in long_forms or any(v['selected']==w for v in rare.values()):
        for r in rr:loci.add((r['page'],r['locus']));reasons[r['page'],r['locus']].append(w)
    if w in freq_forms:
        z=[r for r in rr if r['edition']=='ZL3b' and r['kind']=='P']
        z.sort(key=lambda r:(natural(r['page']),natural(r['locus']),r['source_group_index']))
        chosen=z[:1]+[r for r in z if r['next_same']][:1]
        for r in chosen:loci.add((r['page'],r['locus']));reasons[r['page'],r['locus']].append(w)
loci.add(('f45r','f45r.10'));reasons['f45r','f45r.10'].append('daldy')
lines=[]
for page,loc in sorted(loci,key=lambda x:(natural(x[0]),natural(x[1]))):
    for ed in EDITIONS:
        rows=[dict(r) for r in c.execute('SELECT * FROM groups WHERE edition=? AND page=? AND locus=? ORDER BY source_group_index',(ed,page,loc))]
        assert rows and len(rows)==rows[0]['source_group_count'],(page,loc,ed)
        lines.append({'page':page,'locus':loc,'edition':ed,'selected_for':sorted(set(reasons[page,loc])),'groups':rows})
packet={'selection':spec,'selection_sha256':hashlib.sha256(spec_path.read_bytes()).hexdigest(),'extractor_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cache_receipt':receipt(c),'frequent':freq,'long':long,'ascii_length_only':raw_long,'long_eligibility':eligible,'rare':rare,'forms':forms,'lines':lines}
(P/'HAND_WORD_EXTREMES_PACKET_20261005.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
with (P/'HAND_WORD_EXTREMES_PROFILES_20261005.json').open('w') as out:
    subprocess.run(['./vmanus-work','words','profile',*forms,'--json','--limit','3'],stdout=out,check=True)
print(json.dumps({k:packet[k] for k in ('frequent','long','ascii_length_only','rare','forms')},ensure_ascii=False,indent=2))
print('Complete reader-lines:',len(lines))
