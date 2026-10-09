#!/usr/bin/env python3
"""Post-manual teaching-message replay, not a native text decoder."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
P=Path(__file__).resolve().parent
FILES={
'HUMAN_COMPARISON_WORD_FAMILY_RAW_20261006.json':'1b884ffb0f299b51b86a0d4b7b825c32b81216cd0c39bfd6e58f7b212c57ff9e',
'HUMAN_COMPARISON966_CONTINUATION_AUTHOR_SCOPE_20261006.json':'c322263779006d77e60c027f3a6cf9c3e579dc7dba8bce220bc55d5b97c1848d',
'HUMAN_COMPARISON966_CHALLENGE_20261006.json':'86f4417c7730e9df3ab194693ce40842ebabeff0d4fcca44f3e3c9d1004807f7',
'HUMAN_COMPARISON966_HELD_EXPECTATION_20261006.json':'dfa1a36aca3f4ab2e1c8717d36891a93456193376c3f44edbf6ac73cee7313e2',
'HUMAN_COMPARISON966_ROOT_READBACK_20261006.json':'ce6e17a2d1d4e8081ccda9b77b5971e07bc04636798f2705cb47cde3a8c529f9'}
for name,h in FILES.items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==h,name
raw=json.loads((P/'HUMAN_COMPARISON_WORD_FAMILY_RAW_20261006.json').read_text())
challenge=json.loads((P/'HUMAN_COMPARISON966_CHALLENGE_20261006.json').read_text())
expected=json.loads((P/'HUMAN_COMPARISON966_HELD_EXPECTATION_20261006.json').read_text())
manual=json.loads((P/'HUMAN_COMPARISON966_ROOT_READBACK_20261006.json').read_text())
design=raw['design'];controls=design['controls'];units=set(design['working_units'])
selectors=design['literal_names']['selectors'];assert len(selectors)==21 and'r'not in selectors
assert len(units)==22 and set(selectors)|{'r'}==units
scale_names={('f','p','ch'):'length',('k','t','sh'):'temperature',('ch','f','r'):'mass'}
referents={('f','p','k'):'Ada',('p','k','f'):'Bela'}

def require(ok,reason):
    if not ok:raise ValueError(reason)

def ends(word,name):return len(word)>=3 and word[-3:]==controls[name]

def strip(word,name):
    require(ends(word,name),'missing '+name)
    return word[:-3]

def root_ok(word):return bool(word)and not any(word[i:i+2]==['r','r']for i in range(len(word)-1))

def encode_name(name):
    require(bool(name),'empty name');out=controls['NAME_OPEN'][:]
    for c in name:
        j=ord(c)-32;require(0<=j<=94,'unsupported character');out.extend([selectors[j//21],selectors[j%21]])
    return out+controls['NAME_CLOSE']

def read_term(word):
    if word[:3]==controls['NAME_OPEN']:
        payload=strip(word,'NAME_CLOSE')[3:];require(bool(payload)and len(payload)%2==0,'bad payload length')
        require(all(x in selectors for x in payload),'bad selector');chars=[]
        for i in range(0,len(payload),2):
            j=21*selectors.index(payload[i])+selectors.index(payload[i+1]);require(j<95,'unused pair');chars.append(chr(32+j))
        return ''.join(chars)
    require(root_ok(word),'invalid ordinary term');require(tuple(word)in referents,'unknown referential root')
    return referents[tuple(word)]

def read_head(word):
    neg=ends(word,'NEGATE_WHOLE_LIST_CLAUSE')
    if neg:word=strip(word,'NEGATE_WHOLE_LIST_CLAUSE')
    comparators=[x for x in ['GREATER','LESS','EQUAL_VALUE']if ends(word,x)]
    require(len(comparators)==1,'missing comparator');op=comparators[0];root=strip(word,op)
    require(root_ok(root)and tuple(root)in scale_names,'unknown scale root')
    return {'scale':scale_names[tuple(root)],'root':root,'comparator':op,'negate_whole_list':neg}

def reassemble(lines,width=None):
    out=[];pending=None;marker=controls['CONTINUE_SAME_WORD'];breaks=0;cells=[]
    for line in lines:
        groups=copy.deepcopy(line['groups']);require(bool(groups),'empty physical line')
        require(all(g and set(g)<=units for g in groups),'bad working unit')
        size=sum(map(len,groups))+len(groups)-1;cells.append(size)
        require(width is None or size<=width,'line too wide')
        if pending is not None:
            require(groups[0]==marker,'missing leading continuation');groups.pop(0)
        else:require(groups[0]!=marker,'orphan leading continuation')
        trailing=bool(groups)and groups[-1]==marker
        if trailing:groups.pop();breaks+=1
        require(bool(groups)and all(g!=marker for g in groups),'empty or interior continuation')
        if pending is not None:groups[0]=pending+groups[0];pending=None
        if trailing:pending=groups.pop()
        out.extend(groups)
    require(pending is None,'unfinished continued word')
    return out,breaks,cells

def read_message(words):
    require(bool(words),'empty message');i=0;clauses=[];ended=False
    while i<len(words):
        head=read_head(words[i]);i+=1;subjects=[];closed=False
        while i<len(words):
            w=words[i];i+=1;is_end=ends(w,'END_MESSAGE')
            if is_end:w=strip(w,'END_MESSAGE')
            if ends(w,'END_CLAUSE'):
                standard=read_term(strip(strip(w,'END_CLAUSE'),'STANDARD'))
                require(bool(subjects),'no subjects');closed=True;ended=is_end
                clauses.append(head|{'subjects':subjects,'standard':standard,'end_message':is_end});break
            require(not is_end,'message end without clause close');subjects.append(read_term(w))
        require(closed,'missing standard/closure')
        if ended:require(i==len(words),'content after message end');break
    require(ended,'missing message end');return clauses

def rejects(fn):
    try:fn()
    except ValueError:return True
    raise AssertionError('malformed fixture accepted')

words,breaks,cells=reassemble(challenge['physical_lines'],16)
assert words==expected['logical_words']
clauses=read_message(words)
manual_clauses=[{k:r[k]for k in ['scale','root','comparator','negate_whole_list','subjects','standard','end_message']}for r in manual['clauses']]
assert clauses==manual_clauses
source=[{'scale':x['scale'],'root':x['scale_root'],'comparator':x['comparator'],'negate_whole_list':x['polarity']=='NEGATE_WHOLE_LIST_CLAUSE',
         'subjects':x['subjects_in_written_order'],'standard':x['standard'],'end_message':i==len(expected['clauses'])-1}for i,x in enumerate(expected['clauses'])]
assert clauses==source
assert read_term(encode_name(expected['exact_literal_name']))==manual['manual_name_arithmetic']['exact_name']
for c in map(chr,range(32,127)):assert read_term(encode_name(c))==c
assert len({tuple(encode_name(c))for c in map(chr,range(32,127))})==95

# The old disclosed lesson also remains exactly readable, including its scope.
lesson=read_message(raw['open_teaching_example']['logical_words_as_working_unit_arrays'])
assert [(x['scale'],x['comparator'],x['negate_whole_list'],x['subjects'],x['standard'])for x in lesson]==[
    ('length','GREATER',False,['Ada','Bela'],'Dora'),('temperature','GREATER',True,['Ada','Bela'],'Dora')]
# Meaningful edge cases exercise framing, grammar and name capacity, not native data.
bad=copy.deepcopy(challenge['physical_lines']);bad[3]['groups'].pop(0);assert rejects(lambda:reassemble(bad,16))
bad=copy.deepcopy(challenge['physical_lines']);bad[3]['groups']=[controls['CONTINUE_SAME_WORD']];assert rejects(lambda:reassemble(bad,16))
assert rejects(lambda:read_message(words[:-1]))
assert rejects(lambda:read_message([words[0],words[4],*words[5:]]))
assert rejects(lambda:read_message([*words,words[0]]))
assert rejects(lambda:read_message([words[0],words[0],*words[2:]]))
assert rejects(lambda:read_term(controls['NAME_OPEN']+['a']+controls['NAME_CLOSE']))
assert rejects(lambda:read_term(controls['NAME_OPEN']+['n','y']+controls['NAME_CLOSE']))
assert rejects(lambda:read_term(controls['NAME_OPEN']+controls['NAME_CLOSE']))
assert rejects(lambda:encode_name(chr(127)))

# Explicitly preserve a threefold ordinary subject instead of interpreting a count.
triplet=[words[5],['f','p','k'],['f','p','k'],['f','p','k'],words[-1]]
assert read_message(triplet)[0]['subjects']==['Ada','Ada','Ada']
values=manual['scope_counterexample']['mass_values'];truth=[values[x]<values[clauses[0]['standard']]for x in clauses[0]['subjects']]
assert truth==[False,True,True]and(not all(truth))and not all(not x for x in truth)
assert not all(values[x]>values[clauses[0]['standard']]for x in clauses[0]['subjects'])

physical_groups=sum(len(x['groups'])for x in challenge['physical_lines']);physical_units=sum(sum(map(len,x['groups']))for x in challenge['physical_lines'])
# Count the actually written lexical material, independently of the manual total.
ordinary_units=0;name_units=0;word_index=0
for clause in clauses:
    head=words[word_index];word_index+=1
    if clause['negate_whole_list']:head=strip(head,'NEGATE_WHOLE_LIST_CLAUSE')
    ordinary_units+=len(strip(head,clause['comparator']))
    terms=words[word_index:word_index+len(clause['subjects'])];word_index+=len(terms)
    standard=words[word_index];word_index+=1
    if clause['end_message']:standard=strip(standard,'END_MESSAGE')
    terms.append(strip(strip(standard,'END_CLAUSE'),'STANDARD'))
    for term in terms:
        read_term(term)
        if term[:3]==controls['NAME_OPEN']:name_units+=len(term)
        else:ordinary_units+=len(term)
assert word_index==len(words)
counts={'logical_words':len(words),'logical_working_units':sum(map(len,words)),'continued_breaks':breaks,'continuation_words':2*breaks,'continuation_units':6*breaks,
        'physical_groups':physical_groups,'physical_working_units':physical_units,'visible_same_line_blanks':sum(len(x['groups'])-1 for x in challenge['physical_lines']),'line_cell_widths':cells,
        'grammatical_suffix_units':9*len(clauses)+3*sum(x['negate_whole_list']for x in clauses)+3,
        'literal_name_units_including_frame':name_units,'ordinary_lexical_root_units':ordinary_units}
assert counts==manual['manual_costs']
assert ordinary_units+name_units+counts['grammatical_suffix_units']==counts['logical_working_units']
for our,their in [('logical_words','logical_words'),('continued_breaks','continued_breaks'),('physical_groups','physical_groups'),('logical_working_units','logical_working_drawings'),
                  ('physical_working_units','physical_working_drawings'),('continuation_units','continuation_working_drawings'),('visible_same_line_blanks','physical_within_line_blanks'),('line_cell_widths','line_cells')]:
    assert counts[our]==expected['manual_cost_account'][their]
assert counts['physical_groups']==counts['logical_words']+3*breaks
assert counts['physical_working_units']==counts['logical_working_units']+6*breaks
result={'status':'PASS_NARROW_POST_MANUAL_COMPARISON_READBACK','completed_utc':datetime.now(timezone.utc).isoformat(),'input_hashes':FILES,'clauses':clauses,'counts':counts,
        'checks':['both full teaching messages and hidden-source agreement','95literalcharacters and malformed payload rejection','root-final r retained across controls','three-line continued word and malformed marker handling','list-wide negative truth contrast','written standard change and exact repeated references','all manually reported costs'],
        'limits':'Same-root-author post-manual mechanical check. No independent manuscript evidence, native meaning, historical source coverage or native statistical fit.'}
out=P/'COMPARISON966_HAND_REPLAY_RESULT_20261006.json';assert not out.exists();out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'counts':counts},indent=2))
