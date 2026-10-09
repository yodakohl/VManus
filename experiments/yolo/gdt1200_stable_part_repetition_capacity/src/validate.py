"""Separate reconstruction. Does not import run.py; same author, same exposed data."""
from pathlib import Path
import sys,json,hashlib,re
from collections import Counter,defaultdict
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
sys.path.insert(0,str(ROOT))
from tools import word_profiles as wp
E=('ZL3b','IT2a','RF1b')
def read(n):return json.loads((A/n).read_text())
def literal(s):return bool(s) and s.isascii() and s.isalpha() and s.islower()

def main():
    for p,h in read('REGISTRATION_LOCK.json')['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert read('RUN_RECEIPT.json')['runner_sha256']==hashlib.sha256((D/'src/run.py').read_bytes()).hexdigest()
    assert read('RUN_RECEIPT.json')['registration_sha256']==hashlib.sha256((A/'REGISTRATION_LOCK.json').read_bytes()).hexdigest()
    c=wp.ensure_cache(ROOT);receipt=wp.receipt(c);assert receipt==read('SOURCE_RECEIPT.json')
    allowed=set(receipt['inputs']['selectors']);assert len(allowed)==179
    assert all(not p.startswith('f84') and p!='f116v' for p in allowed)
    rows={r['source_group_id']:dict(r) for r in c.execute('SELECT '+','.join(wp.COLUMNS)+' FROM groups')}
    assert all(r['page'] in allowed and r['edition'] in E for r in rows.values())
    vocab={e:Counter() for e in E};occ=defaultdict(list);lines=defaultdict(list)
    for r in rows.values():
        lines[r['edition'],r['page'],r['locus']].append(r)
        if literal(r['ivtff_group_raw']):
            vocab[r['edition']][r['ivtff_group_raw']]+=1
            occ[r['edition'],r['ivtff_group_raw']].append(r)
    for line in lines.values():line.sort(key=lambda r:r['source_group_index'])
    pair_ids=defaultdict(list)
    query='''SELECT l.edition AS ed,l.ivtff_group_raw AS base,l.source_group_id AS lid,r.source_group_id AS rid
    FROM groups l JOIN groups r ON l.edition=r.edition AND l.page=r.page AND l.locus=r.locus
    AND r.source_group_index=l.source_group_index+1
    WHERE r.ivtff_group_raw=l.ivtff_group_raw || 'dy' AND l.right_separator='DEFINITE_SPACE'
    AND r.left_separator='DEFINITE_SPACE' ORDER BY l.edition,l.page,l.locus,l.source_group_index'''
    for r in c.execute(query):
        if len(r['base'])>=2 and literal(r['base']):pair_ids[r['ed'],r['base']].append((r['lid'],r['rid']))
    c.close()
    candidate={'dal'}
    for ed,v in vocab.items():
        candidate|={w[:-1] for w in v if w.endswith('y') and len(w[:-1])>=2 and w[:-1] in v and w[:-1]+'dy' in v}
        for w in v:
            match=re.fullmatch(r'(.{2,})\1dy',w)
            if match:candidate.add(match.group(1))
    candidate|={b for ed,b in pair_ids}
    observed=read('FAMILIES.json');assert [r['base'] for r in observed]==sorted(candidate)
    expected_caps={ed:{k:[] for k in ('base_family','joined_capacity','either_channel_capacity')} for ed in E}
    requested=set();joined_loci=set()
    for family in observed:
        b=family['base'];forms={'base':b,'y':b+'y','dy':b+'dy','or':b+'or','joined_repeat':b+b+'dy'}
        assert family['forms']==forms;requested.update(forms.values())
        for ed in E:
            actual=family['readers'][ed];counts={k:vocab[ed][w] for k,w in forms.items()}
            counts['separate_repeat']=len(pair_ids[ed,b]);base=all(counts[k] for k in ('base','y','dy'))
            caps={'base_family':base,'joined_capacity':base and counts['joined_repeat']>0,
                'either_channel_capacity':base and bool(counts['joined_repeat'] or counts['separate_repeat'])}
            assert actual==dict(counts,**caps),(ed,b,actual,counts)
            for k,on in caps.items():
                if on:expected_caps[ed][k].append(b)
            joined_loci.update((r['page'],r['locus']) for r in occ[ed,forms['joined_repeat']])
    profile=read('FORM_PROFILES.json');assert len(profile)==len(requested)*3
    assert {(x['edition'],x['form']) for x in profile}=={(ed,w) for ed in E for w in requested}
    for p in profile:
        own=sorted(occ[p['edition'],p['form']],key=lambda r:(r['page'],r['locus'],r['source_group_index']))
        expected={'edition':p['edition'],'form':p['form'],'n':len(own),
            'selectors':sorted({r['page'] for r in own}),
            'leaves':sorted({re.match(r'f[0-9]+',r['page']).group() for r in own}),
            'loci':sorted({r['locus'] for r in own}),
            'sections':dict(sorted(Counter(r['section'] for r in own).items())),
            'source_group_ids':[r['source_group_id'] for r in own]}
        assert p==expected,(p['edition'],p['form'])
    pair_packet=read('SEPARATE_PAIRS.json')
    for ed in E:
        assert set(pair_packet[ed])=={b for (e,b),ids in pair_ids.items() if e==ed and ids}
        for b,pairs in pair_packet[ed].items():
            assert [(p['left']['source_group_id'],p['right']['source_group_id']) for p in pairs]==pair_ids[ed,b]
            for p in pairs:
                assert p['left']==rows[p['left']['source_group_id']] and p['right']==rows[p['right']['source_group_id']]
                joined_loci.add((p['left']['page'],p['left']['locus']))
    packet=read('REPEAT_SOURCE_LINES.json')
    assert len(packet)==3*len(joined_loci)
    assert {(p['edition'],p['page'],p['locus']) for p in packet}=={(ed,p,l) for ed in E for p,l in joined_loci}
    for p in packet:assert p['groups']==lines[p['edition'],p['page'],p['locus']]
    joint={k:sorted((set(expected_caps['ZL3b'][k])&set(expected_caps['IT2a'][k]))-{'dal'}) for k in expected_caps['ZL3b']}
    result=read('RESULT.json');assert result['non_dal_joint']==joint and result['reader_capacities']==expected_caps
    assert result['candidate_bases']==len(candidate)
    assert result['source_group_counts']==dict(Counter(r['edition'] for r in rows.values()))
    assert result['excluded_nonliteral_group_counts']==dict(Counter(r['edition'] for r in rows.values() if not literal(r['ivtff_group_raw'])))
    n=len(joint['either_channel_capacity'])
    expected_status='FORMAL_REPEATED_BASE_CANDIDATE' if n>=2 else 'ISOLATED_EXTENSION_ONLY' if n==1 else 'NO_CROSS_BASE_CAPACITY'
    assert result['status']==expected_status and result['independent_confirmation_capacity']==0
    # Retained exact-form baseline checks are independent of the new candidate selection.
    old=read('REGISTRATION_LOCK.json')
    prior=json.loads((ROOT/'experiments/yolo/gdt1198_daldy_exact_contexts/artifacts/RESULT.json').read_text())
    for ed in E:
        for form in ('dal','daly','daldy'):
            assert vocab[ed][form]==prior['summaries'][ed][form]['count']
    # Examples of what this literal parser does and does not establish.
    assert re.fullmatch(r'(.{2,})\1dy','daldaldy').group(1)=='dal'
    assert not re.fullmatch(r'(.{2,})\1dy','daldydaldy')
    assert not literal('alal@152;y') and not literal('alal<!corr?>dy')
    summary={'status':'PASS','scope':'Exact exposed-source counts, candidate completeness, separate pair guard and fixed decision reduction only',
        'independent_author':False,'independent_data':False,'semantic_or_morphological_validation':False,
        'source_groups':len(rows),'candidate_bases':len(candidate),'profiles':len(profile),'repeat_source_loci':len(joined_loci),
        'non_dal_joint_counts':{k:len(v) for k,v in joint.items()},'validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (A/'VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
