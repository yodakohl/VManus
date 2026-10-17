#!/usr/bin/env python3
"""Independent DOM/text-node source replay, no builder import or native access."""
import hashlib,json,unicodedata as U,xml.dom.minidom as D
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def attrs(node):
    out={}
    for i in range(node.attributes.length):
        a=node.attributes.item(i);k=('{'+a.namespaceURI+'}'+a.localName) if a.namespaceURI else a.name;out[k]=a.value
    return out

def extract(e):
    # DOM text nodes include sibling tails naturally. Ignored element children are never visited.
    stack=list(reversed(list(e.childNodes)));out=[]
    while stack:
        n=stack.pop()
        if n.nodeType in [n.TEXT_NODE,n.CDATA_SECTION_NODE]:out.append(n.data)
        elif n.nodeType==n.ELEMENT_NODE and n.localName not in ['note','emph','milestone','anchor']:
            stack.extend(reversed(list(n.childNodes)))
    return ''.join(out)
def letter(c):return U.category(c)[0]=='L' and U.name(c,'').split(' ',1)[0]=='SYRIAC'
def runs(s):
    cuts=[i for i,c in enumerate(s) if not letter(c)];bounds=[-1]+cuts+[len(s)]
    return [s[a+1:b] for a,b in zip(bounds,bounds[1:]) if b>a+1]
def main():
    spec=json.loads((E/'src/SPEC.json').read_text());p=ROOT/spec['source_xml'];assert sha(p)==spec['source_sha256']
    saved=json.loads((E/'artifacts/SOURCE_PROJECTION.json').read_text())
    assert saved['source_sha256']==sha(p) and saved['source_bytes']==p.stat().st_size==205704
    assert saved['spec_sha256']==sha(E/'src/SPEC.json') and saved['source_builder_sha256']==sha(E/'src/source.py')
    dom=D.parse(str(p));bodies=[e for e in dom.getElementsByTagName('*') if e.localName=='body'];assert len(bodies)==1
    children=[e for e in bodies[0].childNodes if e.nodeType==e.ELEMENT_NODE];accepted=[];rejected=[];section=None
    for i,e in enumerate(children):
        at=attrs(e)
        if e.localName=='div' and at.get('type')=='section':section=at
        base=extract(e);norm=''.join(c for c in base if U.category(c)[0]!='M' and U.category(c)!='Cf');ws=runs(norm)
        bad=sorted({c for c in norm if U.category(c)[0]=='L' and not letter(c)})
        reasons=[]
        if e.localName!='p':reasons.append('NOT_DIRECT_BODY_PARAGRAPH')
        if set(base)&set('[]<>'):reasons.append('EDITORIAL_BRACKET')
        if chr(65533) in base:reasons.append('REPLACEMENT_CHARACTER')
        if bad:reasons.append('UNSUPPORTED_ALPHABETIC_LETTER')
        if not ws:reasons.append('NO_SYRIAC_LETTERS')
        row={'body_child_index':i,'element':e.localName,'attributes':at,'section_marker':section,'base_text':base,'normalized_text':norm,'words':ws,'unsupported_letters':[{'character':c,'codepoint':f'U+{ord(c):04X}','name':U.name(c,'')} for c in bad]}
        if reasons:row['exclusion_reasons']=reasons;rejected.append(row)
        else:accepted.append(row)
    assert accepted==saved['records'] and rejected==saved['excluded_records']
    words=sorted(set(w for r in accepted for w in r['words']));alpha=sorted(set(c for w in words for c in w));pairs=set()
    for r in accepted:
        for i in range(1,len(r['words'])):pairs.add((r['words'][i-1],r['words'][i]))
    assert saved['words']==words and saved['alphabet']==alpha and saved['edges']==[list(z) for z in sorted(pairs)]
    counts={'direct_body_children':len(children),'direct_body_paragraphs':sum(e.localName=='p' for e in children),'accepted_records':len(accepted),'excluded_records':len(rejected),'tokens':sum(len(r['words']) for r in accepted),'unique_words':len(words),'alphabet':len(alpha),'unique_edges':len(pairs)}
    assert saved['counts']==counts
    # Fixed parser fixtures: nested omission keeps tails; combining/format removal; dotless remains a letter.
    sample=D.parseString('<p>ܐ<note>BAD<hi>BAD2</hi></note>ܒ<hi>ܓ<emph>BAD3</emph>ܕ</hi>ܖ</p>')
    assert extract(sample.documentElement)=='ܐܒܓܕܖ' and letter('\u0716')
    assert runs('ܐ ܒ,ܖ')==['ܐ','ܒ','ܖ']
    assert ''.join(c for c in 'ܐ\u0730\u200fܒ' if U.category(c)[0]!='M' and U.category(c)!='Cf')=='ܐܒ'
    eligible=next((r for r in accepted if len(r['words'])>=32),None)
    control_info=None
    if eligible:
        window=eligible['words'][:32];used=set(''.join(window));key={c:spec['signs'][j%spec['control_mapping_modulo']] for j,c in enumerate(alpha)}
        active_pairs=[[a,b] for i,a in enumerate(alpha) for b in alpha[i+1:] if a in used and b in used and key[a]==key[b]]
        control_info={'first_eligible_body_child_index':eligible['body_child_index'],'record_tokens':len(eligible['words']),'window_tokens':32,'active_collision_pairs':active_pairs,'source_metadata_only_no_search':True}
    result={'status':'PASS_INDEPENDENT_DOM_SOURCE_REPLAY','source_sha256':sha(p),'projection_sha256':sha(E/'artifacts/SOURCE_PROJECTION.json'),'source_builder_sha256':sha(E/'src/source.py'),'source_validator_sha256':sha(Path(__file__)),'unicode_database_version':U.unidata_version,'counts':counts,'alphabet_codepoints':[{'character':c,'codepoint':f'U+{ord(c):04X}','name':U.name(c,'')} for c in alpha],'dotless_retained':chr(0x716) in alpha,'control_source_metadata':control_info,'checks':['All accepted and rejected records exactly reconstructed by independent DOM traversal','Every derived base text, normalized text, word, child index and section/element attribute verified','All unique word/alphabet sets and within-record edges rebuilt; rejected records contribute no edges','Nested omission/tails, Syriac runs, mark/format removal and dotless-letter fixtures passed'],'limits':['Source integrity only; no native or calibration search, no linguistic meanings.','Bare edited strict subset and lost vocalization/editorial distinctions remain; not diplomatic or phonetic restoration.','A codepoint inventory is not an identified historical sound inventory; U+0716 deliberately unresolved.']}
    out=E/'artifacts/SOURCE_VALIDATION.json'
    if out.exists():assert json.loads(out.read_text())==result,'Refuse changed validation overwrite'
    else:out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'counts':counts,'control_source_metadata':control_info,'alphabet':alpha,'dotless_retained':result['dotless_retained']},ensure_ascii=False))
if __name__=='__main__':main()
