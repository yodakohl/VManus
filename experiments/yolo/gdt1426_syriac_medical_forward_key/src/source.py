#!/usr/bin/env python3
"""Strict edited Syriac source projection; no native or solver access."""
import hashlib,json,unicodedata as U,xml.etree.ElementTree as ET
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
OMIT={'note','emph','milestone','anchor'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tag(e):return e.tag.rsplit('}',1)[-1]
def text(e):
    parts=[e.text or '']
    for child in e:
        if tag(child) not in OMIT:parts.append(text(child))
        parts.append(child.tail or '')
    return ''.join(parts)
def syriac(c):return U.category(c).startswith('L') and U.name(c,'').startswith('SYRIAC ')
def project():
    spec=json.loads((E/'src/SPEC.json').read_text());p=ROOT/spec['source_xml'];assert sha(p)==spec['source_sha256']
    bodies=[e for e in ET.parse(p).getroot().iter() if tag(e)=='body'];assert len(bodies)==1
    records=[];excluded=[];section=None
    for index,e in enumerate(bodies[0]):
        if tag(e)=='div' and e.attrib.get('type')=='section':section=dict(e.attrib)
        raw=text(e);norm=''.join(c for c in raw if not (U.category(c).startswith('M') or U.category(c)=='Cf'))
        row={'body_child_index':index,'element':tag(e),'attributes':dict(e.attrib),'section_marker':section,'base_text':raw,'normalized_text':norm}
        reasons=[]
        if tag(e)!='p':reasons.append('NOT_DIRECT_BODY_PARAGRAPH')
        if any(c in raw for c in '[]<>'):reasons.append('EDITORIAL_BRACKET')
        if '\ufffd' in raw:reasons.append('REPLACEMENT_CHARACTER')
        unsupported=sorted({c for c in norm if U.category(c).startswith('L') and not syriac(c)})
        if unsupported:reasons.append('UNSUPPORTED_ALPHABETIC_LETTER')
        tokens=[];buf=[]
        for c in norm:
            if syriac(c):buf.append(c)
            elif buf:tokens.append(''.join(buf));buf=[]
        if buf:tokens.append(''.join(buf))
        if not tokens:reasons.append('NO_SYRIAC_LETTERS')
        row.update(words=tokens,unsupported_letters=[{'character':c,'codepoint':f'U+{ord(c):04X}','name':U.name(c,'')} for c in unsupported])
        if reasons:row['exclusion_reasons']=reasons;excluded.append(row)
        else:records.append(row)
    words=sorted({w for r in records for w in r['words']});alphabet=sorted(set(''.join(words)));edges=sorted({(a,b) for r in records for a,b in zip(r['words'],r['words'][1:])})
    out={'status':'STRICT_EDITED_SYRIAC_SUBSET_NOT_DIPLOMATIC_RESTORATION','source':spec['source_xml'],'source_sha256':sha(p),'source_bytes':p.stat().st_size,'spec_sha256':sha(E/'src/SPEC.json'),'source_builder_sha256':sha(Path(__file__)),'unicode_database_version':U.unidata_version,'source_notice':spec['source_notice'],'records':records,'excluded_records':excluded,'alphabet':alphabet,'words':words,'edges':[list(z) for z in edges],'counts':{'direct_body_children':len(bodies[0]),'direct_body_paragraphs':sum(tag(e)=='p' for e in bodies[0]),'accepted_records':len(records),'excluded_records':len(excluded),'tokens':sum(len(r['words']) for r in records),'unique_words':len(words),'alphabet':len(alphabet),'unique_edges':len(edges)},'rules':{'omitted_subtrees':sorted(OMIT),'retained_tails':True,'removed_categories':'M* and Cf only','letter_test':'Unicode category L* and character name begins SYRIAC','record_rejection':'Any base-text []<> or U+FFFD, any unsupported alphabetic letter after M*/Cf removal; non-p elements and empty Syriac records excluded','body_child_index':'zero-based among direct body ELEMENT children; no descendant-p selection','edges':'Within each accepted record only; no cross-record or excluded-record bridge'},'limits':['Edited strict subset, not complete work or a diplomatic/phonetic reconstruction.','Omitted editorial subtrees and combining/format controls lose distinctions; their retained tails are concatenated literally without invented spacing.','Dotless U+0716 and every other accepted Syriac letter remain distinct; no d/r or other allographic folding.','Excluded records retain derived text and candidate runs for audit but contribute zero words or edges.','Word graph is a lexical adjacency relaxation, not a source grammar, native meaning, or language identification.']}
    target=E/'artifacts/SOURCE_PROJECTION.json';target.parent.mkdir(exist_ok=True)
    if target.exists():assert json.loads(target.read_text())==out,'Refuse overwrite of changed source projection'
    else:target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(out['counts']))
if __name__=='__main__':project()
