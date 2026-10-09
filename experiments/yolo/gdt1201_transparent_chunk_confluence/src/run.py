"""Tiny constructive control. Opaque source symbols are not native word meanings."""
from pathlib import Path
from itertools import product
from functools import lru_cache
import json,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
PRIMITIVE={**dict(zip(('U'+str(i) for i in range(7)),('dal','al','ch','ol','y','dy','or'))),
           'WORD_BREAK':'m','OPEN':'p','CLOSE':'f'}
def emit(source):return ''.join(PRIMITIVE[x] for x in source)
def table():
    out=[{'name':k,'surface':v,'expansion':[k],'kind':'primitive'} for k,v in PRIMITIVE.items()]
    for b in range(4):
        u='U'+str(b)
        for label,source in [('Y',[u,'U4']),('DY',[u,'U5']),('OR',[u,'U6']),('DOUBLE',[u,u]),('DOUBLE_DY',[u,u,'U5'])]:
            out.append({'name':u+'_'+label,'surface':emit(source),'expansion':source,'kind':'transparent_alias'})
    return out

def parser(entries):
    @lru_cache(None)
    def parse(s):
        if not s:return {():1}
        out={}
        for entry in entries:
            if s.startswith(entry['surface']):
                for tail,n in parse(s[len(entry['surface']):]).items():
                    key=tuple(entry['expansion'])+tail
                    out[key]=out.get(key,0)+n
        return out
    return parse

def paths(s,entries):
    if not s:return [[]]
    return [[e['name']]+tail for e in entries if s.startswith(e['surface']) for tail in paths(s[len(e['surface']):],entries)]

def save(name,data):(A/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    entries=table();parse=parser(entries)
    assert len(set(PRIMITIVE.values()))==len(PRIMITIVE)
    assert all(not a.startswith(b) for a in PRIMITIVE.values() for b in PRIMITIVE.values() if a!=b)
    n=multi=total_paths=max_paths=0;stream=hashlib.sha256()
    for length in range(5):
        for source in product(tuple(PRIMITIVE)[:7],repeat=length):
            surface=emit(source);actual=parse(surface);assert set(actual)=={source},(source,surface,actual)
            ways=actual[source];n+=1;multi+=ways>1;total_paths+=ways;max_paths=max(max_paths,ways)
            stream.update((json.dumps([source,surface,ways],separators=(',',':'))+'\n').encode())
    fixtures=[('bound_word',['U3','WORD_BREAK','U3']),('one_word',['U3','U3']),
      ('left_scope',['OPEN','U0','CLOSE','U1']),('right_scope',['U0','OPEN','U1','CLOSE']),
      ('double_scope',['OPEN','U0','U0','CLOSE','U5']),('nested_scope',['OPEN','U0','OPEN','U1','CLOSE','CLOSE']),
      ('ordered',['U0','U1']),('reversed',['U1','U0']),('repeated',['U0','U0']),('single',['U0'])]
    teaching=[]
    for b in range(4):
        for source in [(f'U{b}',),(f'U{b}','U4'),(f'U{b}','U5'),(f'U{b}','U6'),(f'U{b}',f'U{b}','U5')]:
            s=emit(source);teaching.append({'source':source,'surface':s,'parses':paths(s,entries),'expanded_message':source})
    teaching.append({'source':['U3','U3'],'surface':'olol','parses':paths('olol',entries),'expanded_message':['U3','U3']})
    checked=[]
    for name,source in fixtures:
        s=emit(source);actual=parse(s);assert set(actual)=={tuple(source)}
        checked.append({'name':name,'source':source,'surface':s,'parse_count':actual[tuple(source)]})
    # Counterconstruction: same spelling, genuinely different source content.
    bad=entries+[{'name':'INDEPENDENT_WHOLE','surface':'olol','expansion':['NEW_VALUE'],'kind':'bad_opaque_whole'}]
    alternatives=parser(bad)('olol');assert set(alternatives)=={('U3','U3'),('NEW_VALUE',)}
    # A longest-match tie-break picks ONE value; it cannot invert both legal inputs.
    greedy=max((e for e in bad if 'olol'.startswith(e['surface'])),key=lambda e:(len(e['surface']),e['name']=='INDEPENDENT_WHOLE'))
    assert greedy['name']=='INDEPENDENT_WHOLE' and tuple(greedy['expansion'])!=('U3','U3')
    counterexamples=[{'kind':'independent_whole_collision','surface':'olol','expansions':[list(x) for x in sorted(alternatives)],
                     'longest_match_choice':greedy['expansion'],'failed_primitive_source':['U3','U3']},
      {'kind':'erased_word_boundary','first':['U3','WORD_BREAK','U3'],'second':['U3','U3'],
       'distinct_correct_surfaces':[emit(['U3','WORD_BREAK','U3']),emit(['U3','U3'])],'collapsed_surface':'olol'},
      {'kind':'erased_scope','first':['OPEN','U0','CLOSE','U1'],'second':['U0','OPEN','U1','CLOSE'],
       'distinct_correct_surfaces':[emit(['OPEN','U0','CLOSE','U1']),emit(['U0','OPEN','U1','CLOSE'])],'collapsed_surface':emit(['U0','U1'])},
      {'kind':'dropped_repeat','first':['U0','U0'],'second':['U0'],'distinct_correct_surfaces':[emit(['U0','U0']),emit(['U0'])]}]
    save('TABLE.json',{'primitive':PRIMITIVE,'entries':entries,'claim':'Invented opaque symbols and paid structural markers only; no native values.'})
    save('TEACHING.json',teaching);save('STRUCTURE_FIXTURES.json',checked);save('COUNTEREXAMPLES.json',counterexamples)
    result={'status':'CONSTRUCTIVE_MESSAGE_UNIQUENESS_WITH_MULTIPLE_PARSES','enumerated_messages':n,
      'multiple_parse_messages':multi,'total_parse_paths':total_paths,'maximum_paths_one_message':max_paths,
      'canonical_enumeration_sha256':stream.hexdigest(),'primitive_entries':len(PRIMITIVE),'aliases':len(entries)-len(PRIMITIVE),
      'structure_fixtures':len(checked),'negative_witnesses':len(counterexamples),
      'native_words_assigned':0,'native_statistics_tested':False,'independent_confirmation_capacity':0,
      'decision':'Do not demand a unique parse tree; require all allowed parses to preserve the same full message. This supplies neither native primitives nor a statistical writer.'}
    save('RESULT.json',result);save('RUN_RECEIPT.json',{'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
