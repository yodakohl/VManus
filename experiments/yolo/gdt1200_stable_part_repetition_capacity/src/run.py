"""Fixed literal construction census; no fitted grammar or native meanings."""
from pathlib import Path
import sys,json,hashlib,re
from collections import defaultdict,Counter
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
sys.path.insert(0,str(ROOT))
from tools import word_profiles as wp
EDITIONS=('ZL3b','IT2a','RF1b')

def plain(s):return re.fullmatch('[a-z]+',s) is not None

def write(name,data):
    (A/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def main():
    lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    conn=wp.ensure_cache(ROOT);receipt=wp.receipt(conn)
    pages=set(receipt['inputs']['selectors'])
    assert len(pages)==179 and not any(p.startswith('f84') or p=='f116v' for p in pages)
    rows=[dict(r) for r in conn.execute('SELECT '+','.join(wp.COLUMNS)+' FROM groups ORDER BY edition,page,locus,source_group_index')];conn.close()
    words={e:defaultdict(list) for e in EDITIONS};pairs={e:defaultdict(list) for e in EDITIONS}
    excluded=Counter();all_lines=defaultdict(list)
    for r in rows:
        assert r['page'] in pages and r['edition'] in EDITIONS
        all_lines[r['edition'],r['page'],r['locus']].append(r)
        if plain(r['ivtff_group_raw']):words[r['edition']][r['ivtff_group_raw']].append(r)
        else:excluded[r['edition']]+=1
    for (edition,page,locus),line in all_lines.items():
        for left,right in zip(line,line[1:]):
            b=left['ivtff_group_raw']
            if (len(b)>=2 and plain(b) and right['ivtff_group_raw']==b+'dy'
                and right['source_group_index']==left['source_group_index']+1
                and left['right_separator']=='DEFINITE_SPACE' and right['left_separator']=='DEFINITE_SPACE'):
                pairs[edition][b].append({'left':left,'right':right})
    bases={'dal'}
    for e in EDITIONS:
        v=words[e]
        bases.update(b for b in v if len(b)>=2 and b+'y' in v and b+'dy' in v)
        for w in v:
            if w.endswith('dy'):
                stem=w[:-2];n=len(stem)//2
                if n>=2 and len(stem)==2*n and stem[:n]==stem[n:]:bases.add(stem[:n])
        bases.update(pairs[e])
    family=[];wanted=set();repeat_lines=set()
    for b in sorted(bases):
        forms={'base':b,'y':b+'y','dy':b+'dy','or':b+'or','joined_repeat':b+b+'dy'}
        wanted.update(forms.values());item={'base':b,'forms':forms,'readers':{}}
        for e in EDITIONS:
            cells={key:len(words[e].get(form,[])) for key,form in forms.items()}
            cells['separate_repeat']=len(pairs[e].get(b,[]))
            cells['base_family']=all(cells[k]>0 for k in ('base','y','dy'))
            cells['joined_capacity']=cells['base_family'] and cells['joined_repeat']>0
            cells['either_channel_capacity']=cells['base_family'] and (cells['joined_repeat']>0 or cells['separate_repeat']>0)
            item['readers'][e]=cells
            for r in words[e].get(forms['joined_repeat'],[]):repeat_lines.add((e,r['page'],r['locus']))
            for pair in pairs[e].get(b,[]):repeat_lines.add((e,pair['left']['page'],pair['left']['locus']))
        family.append(item)
    profiles=[]
    for e in EDITIONS:
        for w in sorted(wanted):
            own=words[e].get(w,[])
            profiles.append({'edition':e,'form':w,'n':len(own),
                'selectors':sorted({r['page'] for r in own}),
                'leaves':sorted({re.match(r'f[0-9]+',r['page']).group() for r in own}),
                'loci':sorted({r['locus'] for r in own}),
                'sections':dict(sorted(Counter(r['section'] for r in own).items())),
                'source_group_ids':[r['source_group_id'] for r in own]})
    joint={k:[x['base'] for x in family if x['base']!='dal' and all(x['readers'][e][k] for e in ('ZL3b','IT2a'))]
        for k in ('base_family','joined_capacity','either_channel_capacity')}
    n=len(joint['either_channel_capacity'])
    status='FORMAL_REPEATED_BASE_CANDIDATE' if n>=2 else 'ISOLATED_EXTENSION_ONLY' if n==1 else 'NO_CROSS_BASE_CAPACITY'
    result={'status':status,'candidate_bases':len(bases),'non_dal_joint':joint,
        'reader_capacities':{e:{k:[x['base'] for x in family if x['readers'][e][k]] for k in joint} for e in EDITIONS},
        'source_group_counts':dict(Counter(r['edition'] for r in rows)),
        'excluded_nonliteral_group_counts':dict(excluded),'independent_confirmation_capacity':0,
        'scope':'Literal formal capacity only. No meaning, morphological proof, significance, historical attribution or complete writer.'}
    write('SOURCE_RECEIPT.json',receipt);write('FAMILIES.json',family);write('FORM_PROFILES.json',profiles)
    write('SEPARATE_PAIRS.json',{e:dict(pairs[e]) for e in EDITIONS})
    view_loci=sorted({(p,l) for e,p,l in repeat_lines})
    write('REPEAT_SOURCE_LINES.json',[{'edition':e,'page':p,'locus':l,'groups':all_lines[e,p,l]} for p,l in view_loci for e in EDITIONS])
    write('RESULT.json',result)
    write('RUN_RECEIPT.json',{'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'registration_sha256':hashlib.sha256((A/'REGISTRATION_LOCK.json').read_bytes()).hexdigest()})
    print(json.dumps(result,indent=2))
    for x in family:
        if x['base']=='dal' or any(r['joined_repeat'] or r['separate_repeat'] for r in x['readers'].values()):
            print(x['base'],json.dumps({e:{k:v for k,v in r.items() if not isinstance(v,bool)} for e,r in x['readers'].items()}))

if __name__=='__main__':main()
