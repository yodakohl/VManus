#!/usr/bin/env python3
"""Hash-bound source-only extraction. Full text is written only to external cache.

No semantic annotation, target input, or corpus selection is performed here.
Whitespace is normalized for annotation; original bytes remain separately pinned.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import tempfile
import urllib.request
from collections import Counter
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def norm(text):
    return re.sub(r'\s+', ' ', text).strip()


def roman(n):
    out = ''
    for value, token in [(100,'C'),(90,'XC'),(50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]:
        while n >= value:
            out += token
            n -= value
    return out


def unit(work, key, text, heading, locator, **extra):
    text = norm(text)
    assert text, (work, key)
    return dict(work=work, unit_id=f'{work}:{key}', heading=heading,
                locator=locator, text=text, text_sha256=sha(text.encode()),
                words=len(text.split()), **extra)


def dom(module, raw):
    parser = module.Parser()
    parser.feed(raw.decode('utf-8'))
    return parser


def plain(node, omit=()):
    if isinstance(node, str):
        return node
    if set(node.attrs.get('class', '').split()) & set(omit):
        return ''
    if node.tag in {'script','style'}:
        return ''
    if node.tag == 'br':
        return ' '
    return ''.join(plain(c, omit) for c in node.children)


def galen(module, path):
    # Exact native1049 extraction; redirect every output, never modify legacy files.
    with tempfile.TemporaryDirectory(prefix='gdt1162_galen_') as td:
        temp = Path(td)
        (temp/'runtime').mkdir()
        (temp/'artifacts').mkdir()
        module.SOURCE, module.EXP = path, temp
        rows, meta = module.extract()
    original = json.loads((ROOT/'experiments/yolo/gdt1049_galen_season_concept_countercheck/artifacts/SOURCE_UNITS.json').read_text())
    assert meta['paragraphs'] == original['paragraphs']
    assert len(rows) == 266 and meta['outside_authorial_text_count'] == 0
    units = [unit('GALEN', r['paragraph_id'], r['text'], r['chapter_id'],
                  {'chapter_id':r['chapter_id'],'paragraph_id':r['paragraph_id']}, book=r['book']) for r in rows]
    assert all(a['text_sha256'] == b['paragraph_sha256'] for a,b in zip(units, rows))
    return units, dict(native1049_all_paragraph_metadata_equal=True, paragraphs=266,
        chapter_ids=module.CHAPTERS, headings='All native chapter IDs retained; no authorial prose outside paragraphs.',
        outside_authorial_text=0, parser_mismatches=meta['parser_mismatches'],
        literal_editorial_marker='Exact1049 correction: I_16 first paragraph Erasistratus[143] -> Erasistratus; substantive bracketed additions retained.')


def quinte(module, path):
    ps = dom(module, path.read_bytes())
    nodes = [n for n in module.walk(ps.root) if not isinstance(n,str)]
    book = None
    active = False
    rows, cells, headings, ignored, unexpected = [], Counter(), [], Counter(), []
    omitted = {'tag','pagenum'}
    for n in nodes:
        if n.attrs.get('id') in {'book_i','book_ii'}:
            book = n.attrs['id'].upper()
            active = True
            headings.append(norm(plain(n)))
        if active and n.tag == 'h3' and norm(plain(n)) == 'FOOTNOTES':
            break
        if not active:
            continue
        classes = set(n.attrs.get('class','').split())
        if n.tag == 'td':
            if 'maintext' in classes:
                cells[book] += 1
                rows.append(unit('QUINTE',f'{book}.cell{cells[book]:03d}',plain(n, omitted),
                    book,{'book':book,'maintext_cell':cells[book]},book=book))
            else:
                value = norm(plain(n, omitted))
                if value:
                    if classes & {'sidenote','ednote'}:
                        ignored['editorial_'+','.join(sorted(classes))] += 1
                    else:
                        unexpected.append({'kind':'nonempty_unclassified_td','text':value})
        # Every substantive direct text segment must have a declared owner.
        direct = norm(''.join(c for c in n.children if isinstance(c,str)))
        if direct:
            ancestors = list(module.ancestors(n))
            if not any(a.tag=='td' or re.fullmatch('h[1-6]',a.tag) or
                       set(a.attrs.get('class','').split()) & {'tag','pagenum'} for a in ancestors):
                unexpected.append({'kind':'unowned_direct_text','text':direct,'tag':n.tag})
    assert len(rows)==168, len(rows)
    assert set(cells)=={'BOOK_I','BOOK_II'}
    assert all('Explicit' in [r for r in rows if r['book']==b][-1]['text'] for b in cells)
    assert not unexpected, unexpected
    return rows, dict(maintext_cells=dict(cells),book_headings=headings,
        both_explicit_endings_retained=True,unclassified_content=[],
        excluded_editorial_cells=dict(ignored),parser_mismatches=ps.mismatches,
        removed_inline_classes=sorted(omitted),
        limits='HTML table cells are editorial layout units, not inferred authorial paragraphs. All maintext cells retained; expanded letters and uncertain substantive passages retained. Gloss links contribute their displayed word; footnote numeral links do not. Separate Spheres text, frontmatter, side summaries and apparatus excluded.')


def salerno(module, path):
    ps = dom(module,path.read_bytes())
    nodes = [n for n in module.walk(ps.root) if not isinstance(n,str) and n.tag=='h3']
    groups, current = [], None
    for n in nodes:
        value = norm(plain(n))
        if re.fullmatch('[IVXLCDM]+',value):
            current = dict(roman=value, parts=[])
            groups.append(current)
        elif value:
            assert current is not None, value
            current['parts'].append(value)
    assert [r['roman'] for r in groups] == [roman(i) for i in range(1,105)]
    rows = [unit('SALERNO',g['roman'],' '.join(g['parts']),g['parts'][0],
                 {'section':g['roman'],'section_number':i}) for i,g in enumerate(groups,1)]
    # Source's section container must have no substantive post-start material
    # outside h3 elements; preserve title as metadata, reject unexpected prose.
    active=False
    unexpected=[]
    for n in module.walk(ps.root):
        if isinstance(n,str):continue
        if n.tag=='h3' and norm(plain(n))=='I':active=True
        if active and 'navigatio' in n.attrs.get('class','').split():break
        if active:
            direct=norm(''.join(c for c in n.children if isinstance(c,str)))
            if direct and not any(a.tag=='h3' for a in module.ancestors(n)):
                unexpected.append({'tag':n.tag,'text':direct})
    assert not unexpected, unexpected
    return rows,dict(sections=104,complete_roman_sequence=True,all_section_titles_retained=True,
                     unexpected_content=[],parser_mismatches=ps.mismatches,
                     boundaries='From section I through CIV inclusive; source title and edition metadata retained in SOURCES. Modern image caption, navigation and edition frontmatter excluded.')


def balneis(path):
    text=path.read_bytes().decode('utf-8')
    lines=text.splitlines(keepends=True)
    starts=[(i,re.match(r'^([IVX]+)\. ',line).group(1)) for i,line in enumerate(lines) if re.match(r'^([IVX]+)\. ',line)]
    assert [r for _,r in starts]==[roman(i) for i in range(1,34)]
    spans=[(0,starts[0][0],'PROLOGUE')]+[(i,starts[j+1][0] if j+1<len(starts) else len(lines),r) for j,(i,r) in enumerate(starts)]
    rows=[]
    for start,end,key in spans:
        raw=''.join(lines[start:end])
        heading=re.search(r'\[([^]]+)\]',lines[start])
        assert heading is not None
        rows.append(unit('BALNEIS',key,raw,heading.group(1),
                         {'line_start':start+1,'line_end_inclusive':end},
                         raw_interval_sha256=sha(raw.encode())))
    assert ''.join(''.join(lines[a:b]) for a,b,_ in spans)==text
    return rows,dict(units=34,numbered_sequence=33,prologue_retained=True,dedication_XXXI_retained=True,
                     all_raw_characters_covered=True,headings_retained_in_text=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cache',type=Path,required=True,help='External directory for raw sources and annotation_units.json')
    ap.add_argument('--fetch',action='store_true',help='Fetch only missing pinned source files; fail on changed bytes')
    args=ap.parse_args()
    cache=args.cache.resolve()
    assert ROOT.resolve() not in cache.parents and cache != ROOT.resolve(), 'Fulltext cache must be outside repository'
    cache.mkdir(parents=True,exist_ok=True)
    spec=json.loads((EXP/'src/SOURCES.json').read_text())
    for path,pin in spec['dependencies'].items():
        assert sha((ROOT/path).read_bytes())==pin, f'Changed dependency: {path}'
    paths={}
    for source in spec['sources']:
        path=cache/source['cache_name']
        if not path.exists():
            if source.get('local_prior') and (ROOT/source['local_prior']).exists():
                raw=(ROOT/source['local_prior']).read_bytes()
            elif args.fetch:
                with urllib.request.urlopen(source['url'],timeout=90) as response:raw=response.read()
            else:
                raise FileNotFoundError(f"Provide pinned {source['cache_name']} in external cache or use --fetch")
            assert sha(raw)==source['sha256'] and len(raw)==source['bytes'], f"Changed download: {source['id']}"
            path.write_bytes(raw)
        raw=path.read_bytes()
        assert sha(raw)==source['sha256'] and len(raw)==source['bytes'], f"Changed source: {source['id']}"
        paths[source['id']]=path
    native=ROOT/'experiments/yolo/gdt1049_galen_season_concept_countercheck/src/run.py'
    loader=importlib.util.spec_from_file_location('gdt1049_native_readonly',native)
    module=importlib.util.module_from_spec(loader);loader.loader.exec_module(module)
    allrows=[]; audits={}
    for work, extractor in [('GALEN',galen),('QUINTE',quinte),('SALERNO',salerno)]:
        rows,audit=extractor(module,paths[work]);allrows.extend(rows);audits[work]=audit
    rows,audit=balneis(paths['BALNEIS']);allrows.extend(rows);audits['BALNEIS']=audit
    assert len({r['unit_id'] for r in allrows})==len(allrows)
    bodies={}
    for work in audits:
        selected=[r for r in allrows if r['work']==work]
        body='\n\n'.join(r['text'] for r in selected)
        char_offset=word_offset=0
        for i,r in enumerate(selected):
            if i:char_offset+=2
            r['body_char_start']=char_offset
            r['body_char_end_exclusive']=char_offset+len(r['text'])
            r['body_word_start']=word_offset
            r['body_word_end_exclusive']=word_offset+r['words']
            assert body[r['body_char_start']:r['body_char_end_exclusive']]==r['text']
            char_offset+=len(r['text']);word_offset+=r['words']
        assert char_offset==len(body) and word_offset==len(body.split())
        bodies[work]={'text':body,'text_sha256':sha(body.encode()),
                      'characters':len(body),'words':word_offset,
                      'unit_ids':[r['unit_id'] for r in selected]}
    local={'schema':'GDT1162_ANNOTATION_UNITS_V1','source_only':True,'units':allrows,'bodies':bodies}
    dump(cache/'annotation_units.json',local)
    metadata={'schema':'GDT1162_SOURCE_UNITS_V1','preparation_only':True,'semantic_annotations_performed':False,
              'sources_sha256':sha((EXP/'src/SOURCES.json').read_bytes()),
              'extractor_sha256':sha(Path(__file__).read_bytes()),
              'local_annotation_units_sha256':sha((cache/'annotation_units.json').read_bytes()),
              'word_count_definition':'Whitespace-delimited normalized text tokens; source-unit metadata, not semantic counts.',
              'offset_definition':'Zero-based Unicode-character and whitespace-word offsets; ends exclusive. Units joined in source order with two LF characters. No synthetic heading words inserted.',
              'bodies':{w:{k:v for k,v in b.items() if k!='text'} for w,b in bodies.items()},
              'works':{w:{'units':sum(r['work']==w for r in allrows),'words':sum(r['words'] for r in allrows if r['work']==w),
                          'audit':audits[w]} for w in audits},
              'units':[{k:v for k,v in r.items() if k!='text'} for r in allrows]}
    dump(EXP/'artifacts/SOURCE_UNITS.json',metadata)
    print(json.dumps({'works':{w:{k:v for k,v in a.items() if k!='audit'} for w,a in metadata['works'].items()},
                      'local_annotation_units_sha256':metadata['local_annotation_units_sha256']}))


if __name__=='__main__':main()
