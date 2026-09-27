#!/usr/bin/env python3
"""Independent GDT1049 replay: stdlib DOM extraction, annotation and arithmetic.

No producer imports or implementation access. Semantic review is a separate
human/model reading record; executable checks cannot establish its truth.
"""
from __future__ import annotations

import collections
import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
ART = HERE / 'artifacts'
RAW = ROOT / 'research_registry/proposals/laufenberg_f85r2_20260926/external_cache/complete_source_roster/galen_gutenberg43383.html'
RAW_SHA = 'd234a983f9c363828a8c71b9b7ae68569548c72cfe2b2691ad5c0409d3609590'
CHAPTERS = [f'{b}_{i}' for b, n in [('I',17),('II',9),('III',15)] for i in range(1,n+1)]
FIELDS = ('winter', 'summer', 'winter_topic', 'summer_topic')
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def require(condition, detail):
    if not condition:
        raise AssertionError(detail)

class Node:
    def __init__(self, tag='', attrs=None):
        self.tag, self.attrs, self.children = tag, dict(attrs or []), []

class DOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('document')
        self.stack = [self.root]
    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs)
        self.stack[-1].children.append(n)
        if tag not in VOID:
            self.stack.append(n)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break
    def handle_data(self, data):
        self.stack[-1].children.append(data)

def ignored(n):
    classes = set(n.attrs.get('class','').split())
    return bool(classes & {'footnote','footnotes','fnanchor','pagenum','pn'})

def flatten(n):
    if isinstance(n,str):
        return n
    if ignored(n):
        return ''
    return ''.join(flatten(c) for c in n.children)

def extract(raw):
    text = raw.decode('utf-8')
    start = text.index('<h3> <a id="I_1">')
    end = text.index('<h2>ΓΑΛΗΝΟΥ</h2>',start)
    parser = DOM()
    parser.feed(text[start:end])
    parser.close()
    chapter = None
    seen, outside, empty, rows = [], [], [], []
    serial = collections.Counter()
    literal_markers = []
    def visit(node, heading=False):
        nonlocal chapter
        if isinstance(node,str):
            if chapter and not heading and node.strip():
                outside.append(re.sub(r'\s+',' ',node).strip())
            return
        if ignored(node):
            return
        anchor = node.attrs.get('id')
        if anchor in CHAPTERS:
            chapter = anchor
            seen.append(anchor)
        if node.tag == 'p' and chapter:
            value = re.sub(r'\s+',' ',flatten(node)).strip()
            if not value:
                empty.append(chapter)
                return
            serial[chapter] += 1
            pid = f'{chapter}.p{serial[chapter]:03d}'
            initial_sha = sha(value.encode())
            if pid == 'I_16.p001':
                require(value.count('Erasistratus[143]') == 1,'registered literal marker absent/duplicated')
                value = value.replace('Erasistratus[143]','Erasistratus',1)
                literal_markers.append({'paragraph_id':pid,'before_sha256':initial_sha,
                                       'after_sha256':sha(value.encode())})
            rows.append({'paragraph_id':pid,'chapter_id':chapter,'book':chapter.split('_')[0],
                         'paragraph_sha256':sha(value.encode()),'words':len(value.split()),'text':value})
            return
        for child in node.children:
            visit(child,heading or node.tag in {'h1','h2','h3','h4','h5','h6'})
    visit(parser.root)
    require(seen == CHAPTERS,'native chapter order/coverage differs')
    require(not outside,'uncovered authorial text outside paragraph elements')
    return rows, empty, literal_markers

def verify_annotations(rows, metadata):
    require(len(rows) == len(metadata),'missing or extra annotation row')
    ids = [r['paragraph_id'] for r in rows]
    require(len(set(ids)) == len(ids),'duplicate annotation row')
    byid = {r['paragraph_id']:r for r in metadata}
    require(set(ids) == set(byid),'annotation paragraph population differs')
    for r in rows:
        p = byid[r['paragraph_id']]
        require(r['chapter_id'] == p['chapter_id'],'annotation chapter mismatch')
        require(r['paragraph_sha256'] == p['paragraph_sha256'],'annotation paragraph hash mismatch')
        require(r.get('complete_read') is True,'incomplete reading declaration')
        require(isinstance(r.get('reader'),str) and r['reader'],'missing reader')
        require(isinstance(r.get('note'),str) and r['note'],'missing annotation note')
        require('antecedents' in r,'missing antecedent field')
        for concept in ('winter','summer'):
            require(r[concept] in ('E','A','U','N'),'invalid local state')
            require(r[concept+'_topic'] in ('ACTIVE','NONE','UNCLEAR'),'invalid topic state')
            if r[concept] == 'A' or r[concept+'_topic'] == 'ACTIVE':
                require(bool(r['antecedents']),'anaphoric/active topic without antecedent')

def aggregate(rows):
    result = {}
    for book in ('ALL','I','II','III'):
        part = [r for r in rows if book == 'ALL' or r['chapter_id'].split('_')[0] == book]
        entry = {'paragraphs':len(part),'chapters':len({r['chapter_id'] for r in part}),'concepts':{}}
        for concept in ('winter','summer'):
            values = {}
            for name in ('local_definite','local_possible','scope_definite','scope_possible'):
                accepted = []
                for r in part:
                    definite = r[concept] in ('E','A')
                    possible = r[concept] in ('E','A','U')
                    yes = {'local_definite':definite,'local_possible':possible,
                           'scope_definite':definite or r[concept+'_topic'] == 'ACTIVE',
                           'scope_possible':possible or r[concept+'_topic'] in ('ACTIVE','UNCLEAR')}[name]
                    if yes:
                        accepted.append(r)
                values[name] = {'paragraphs':len(accepted),
                                'chapters':len({r['chapter_id'] for r in accepted}),
                                'ids':sorted(r['paragraph_id'] for r in accepted)}
            entry['concepts'][concept] = values
        result[book] = entry
    return result

def apply_corrections(original, corrections):
    rows = copy.deepcopy(original)
    byid = {r['paragraph_id']:r for r in rows}
    for change in corrections:
        require(change['paragraph_id'] in byid,'correction unknown paragraph')
        require(bool(change.get('reason')) and bool(change.get('reviewer')),'unattributed correction')
        before, after = change['before'], change['after']
        require(set(before) == set(after),'correction before/after field mismatch')
        require(set(after) <= set(FIELDS)|{'antecedents','note'},'correction changes fixed identity/read provenance')
        r = byid[change['paragraph_id']]
        for key, val in before.items():
            require(r[key] == val,'correction does not match retained original/prior state')
        r.update(after)
    return rows

def validate():
    lock = load(HERE/'src/PREREG_LOCK.json')
    require(lock['pre_data'] is True,'preregistration not declared pre-data')
    require(lock['source_sha256'] == RAW_SHA,'preregistered source identity changed')
    for relative, digest in lock['bound_files'].items():
        path = ROOT/relative
        require(path.is_relative_to(ROOT),'preregistered path escapes repository')
        require(sha(path.read_bytes()) == digest,'preregistered file changed: '+relative)
    raw = RAW.read_bytes()
    require(sha(raw) == RAW_SHA,'raw source hash differs')
    rows, empty, marker = extract(raw)
    units = load(ART/'SOURCE_UNITS.json')
    reduced = [{k:v for k,v in r.items() if k!='text'} for r in rows]
    require(reduced == units['paragraphs'],'independent extraction differs from published paragraph metadata')
    require(units['chapters'] == CHAPTERS,'published chapters mismatch')
    require(units['paragraph_count'] == len(rows),'published paragraph count mismatch')
    require(units['word_count'] == sum(r['words'] for r in rows),'published word count mismatch')
    require(units['outside_authorial_text_count'] == 0,'published outside-text exception')
    correction = load(ART/'EXTRACTION_CORRECTION.json')
    initial = load(ART/'INITIAL_SOURCE_UNITS.json')
    expected_initial = copy.deepcopy(reduced)
    for p in expected_initial:
        if p['paragraph_id'] == marker[0]['paragraph_id']:
            p['paragraph_sha256'] = marker[0]['before_sha256']
    require(expected_initial == initial['paragraphs'],'initial extraction preservation mismatch')
    require(len(correction['changes'])==1,'unexpected extraction corrections')
    for key, val in marker[0].items():
        require(correction['changes'][0][key] == val,'marker correction receipt mismatch')
    paths = [ART/'ANNOTATIONS_I_II.json', ART/'ANNOTATIONS_III.json']
    # Freeze entries are a simple {relative annotation path: sha256} mapping.
    freeze = load(ART/'ANNOTATION_FREEZE.json')
    require(freeze.get('all_first_annotations_complete') is True,'original annotation freeze incomplete')
    require(freeze.get('no_supplementary_keyword_scan_before_freeze') is True,'premature keyword-screen exposure')
    frozen = freeze['annotation_files']
    for path in paths:
        relative = 'artifacts/'+path.name
        expected = frozen.get(relative,frozen.get(path.name))
        if isinstance(expected,dict):
            expected = expected['sha256']
        require(expected == sha(path.read_bytes()),'original annotation bytes changed after freeze')
    original = []
    for path in paths:
        original.extend(load(path))
    verify_annotations(original,rows)
    source_order = {r['paragraph_id']:i for i,r in enumerate(rows)}
    original.sort(key=lambda r:source_order[r['paragraph_id']])
    corrections = load(ART/'CORRECTIONS.json')
    reviewed = apply_corrections(original,corrections)
    verify_annotations(reviewed,rows)
    result = load(ART/'RESULT.json')
    require(result['status']=='COMPLETE_SOURCE_EDITION_PROFILE','result incomplete/unexpected claim')
    require(result['original']==aggregate(original),'original aggregation differs')
    require(result['reviewed']==aggregate(reviewed),'reviewed aggregation differs')
    require(result['source_units']==len(rows),'result source-unit count differs')
    require(result['chapters']==len(CHAPTERS),'result chapter count differs')
    require(result['words']==sum(r['words'] for r in rows),'result word count differs')
    require(result['paragraph_word_range']==[min(r['words'] for r in rows),max(r['words'] for r in rows)],'word range differs')
    require(result['correction_count']==len(corrections),'correction count differs')
    require(result['manuscript_data_accessed'] is False,'target access claim changed')
    require(result['source_to_target_bound'] is None,'unauthorized source-target bound')
    require(result['confirmed_translated_words']==0,'unauthorized word-confirmation claim')
    review = load(ART/'SECOND_REVIEW.json')
    required = set()
    for chapter in CHAPTERS:
        selected = [r for r in rows if r['chapter_id']==chapter]
        required.update([selected[0]['paragraph_id'],selected[-1]['paragraph_id']])
    required.update(r['paragraph_id'] for r in original if any(r[c]!='N' or r[c+'_topic']!='NONE' for c in ('winter','summer')))
    require(set(review['review_required_ids']) == required,'second-review contract population mismatch')
    reviewed_ids = {r['paragraph_id'] for r in review['reviewed_rows']}
    require(required <= reviewed_ids,'required limited-review rows missing')
    require(review.get('status') == 'COMPLETE_LIMITED_SECOND_REVIEW','semantic review incomplete')
    require(review['complete_context_read']['chapters']==len(CHAPTERS),'chapter-context reading incomplete')
    require(review['complete_context_read']['paragraphs']==len(rows),'whole context-reading coverage incomplete')
    mutations = []
    def reject(name, operation):
        try:
            operation()
        except AssertionError:
            mutations.append({'case':name,'rejected':True})
        else:
            raise AssertionError('mutation accepted: '+name)
    reject('missing_annotation',lambda:verify_annotations(original[:-1],rows))
    bad = copy.deepcopy(original); bad[0]['paragraph_sha256']='0'*64
    reject('wrong_paragraph_hash',lambda:verify_annotations(bad,rows))
    badresult = copy.deepcopy(result['reviewed']); badresult['ALL']['concepts']['winter']['local_definite']['paragraphs'] += 1
    reject('changed_aggregate_count',lambda:require(badresult==aggregate(reviewed),'count mismatch'))
    altered = paths[0].read_bytes()+b'\n'
    expected = frozen.get('artifacts/'+paths[0].name,frozen.get(paths[0].name))
    if isinstance(expected,dict): expected=expected['sha256']
    reject('changed_original_annotation_without_freeze_receipt',lambda:require(sha(altered)==expected,'freeze mismatch'))
    return {'status':'PASS','validated_utc':datetime.now(timezone.utc).isoformat(),
            'source_sha256':RAW_SHA,'independent_extraction':'stdlib HTMLParser DOM; no producer import',
            'paragraphs':len(rows),'chapters':len(CHAPTERS),'words':sum(r['words'] for r in rows),
            'empty_editorial_paragraphs':len(empty),'outside_authorial_text':0,
            'original_annotations_byte_frozen':True,'original_and_reviewed_aggregations_exact':True,
            'preregistered_file_hashes_verified':lock['bound_files'],
            'registered_second_review_required':len(required),'reviewed_rows':len(reviewed_ids),
            'mutation_rejections':mutations,
            'implementation_notes':['Initial validator comparison used document-order IDs while the result serializes incidence sets lexically; comparison now sorts those IDs, leaving all populations and counts unchanged.',
                                    'DOM traversal includes the final empty page marker before the Greek heading; this adds one empty element to the extraction diagnostic but no authorial paragraph.'],
            'mechanical_claim_ceiling':'Source extraction, byte provenance, schema, coverage and arithmetic only; not semantic truth.',
            'semantic_review':'Separate complete-context reading and limited frozen-annotation review in SECOND_REVIEW.json.'}

def main():
    try:
        result = validate()
    except (AssertionError,KeyError,ValueError,FileNotFoundError) as error:
        result = {'status':'FAIL','validated_utc':datetime.now(timezone.utc).isoformat(),
                  'error':str(error),'mechanical_claim_ceiling':'No semantic truth certified.'}
    (ART/'VALIDATION.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0 if result['status']=='PASS' else 1

if __name__=='__main__':
    raise SystemExit(main())
