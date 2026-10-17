"""Exploratory complete-paragraph conditional reading; no lexical translation."""
from pathlib import Path
from collections import deque
import json, hashlib
D=Path(__file__).resolve().parent
ROOT=D.parents[2]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def derive(rows, edition, window):
    rows=sorted([r for r in rows if r['edition']==edition and r['locus'] in window],key=lambda r:(window.index(r['locus']),int(r['source_group_index'])))
    trace=[];facts=[];clauses=[]
    for r in rows:
        raw=r['ivtff_group_raw'];gid=f"{edition}|{r['locus']}|G{int(r['source_group_index']):03d}"
        if raw.startswith('q'):
            assert len(raw)>1,'Empty antecedent is outside this draft'
            if not clauses or clauses[-1]['body']:
                clauses.append({'id':len(clauses)+1,'antecedents':[],'antecedent_ids':[],'body':[],'body_ids':[]})
            c=clauses[-1];c['antecedents'].append(raw[1:]);c['antecedent_ids'].append(gid)
            role='antecedent';pred=raw[1:];ci=c['id']
        else:
            pred=raw
            if clauses:
                c=clauses[-1];c['body'].append(raw);c['body_ids'].append(gid);role='consequent';ci=c['id']
            else:facts.append(raw);role='fact';ci=None
        trace.append({'source':r,'id':gid,'role':role,'clause':ci,'predicate':pred})
    assert not clauses or clauses[-1]['body'],'Incomplete final case'
    return {'trace':trace,'facts':facts,'clauses':clauses}

def closure(facts,clauses,seed=()):
    known=set(facts)|set(seed)
    while True:
        nxt=known|{x for c in clauses if set(c['antecedents'])<=known for x in c['body']}
        if nxt==known:return sorted(known)
        known=nxt

def main():
    p=D/'CONDITIONAL42_F89V1_PLAN_20261017.json';plan=json.loads(p.read_text());s=ROOT/plan['source']['path'];assert digest(s)==plan['source']['sha256']
    source=json.loads(s.read_text());window=plan['rules']['window'];readers={}
    for ed in ['IT2a','ZL3b','RF1b']:
        r=derive(source['query']['rows'],ed,window)
        units=[u for u in source['units'] if u['edition']==ed and u['locus'] in window]
        for u in units:
            assert [t['source']['ivtff_group_raw'] for t in r['trace'] if t['source']['locus']==u['locus']]==u['groups']
        r['own_paragraph_flags']=[{'locus':u['locus'],'start':u.get('paragraph_start',[]),'end':u.get('paragraph_end',[])} for u in units]
        r['scope_note']='Own ZL/IT paragraph flags retained; RF is only the borrowed13–20window without an independent marked paragraph.'
        readers[ed]=r
    it=readers['IT2a'];clauses=it['clauses'];assert all(len(c['antecedents'])==1 for c in clauses)
    predicates=sorted({t['predicate'] for t in it['trace']});ante=sorted({x for c in clauses for x in c['antecedents']})
    paths=[]
    for syms in plan['rules']['expected_paths']:
        ids=[]
        for a,b in zip(syms,syms[1:]):
            found=[c['id'] for c in clauses if c['antecedents']==[a] and b in c['body']];assert found,(a,b)
            ids.append(found[0])
        paths.append({'symbols':syms,'clauses':ids})
    primary={'groups':len(it['trace']),'facts':len(it['facts']),'clauses':len(clauses),'q_types':len({t['source']['ivtff_group_raw'] for t in it['trace'] if t['role']=='antecedent'}),'predicate_types':len(predicates),'body_counts':[len(c['body']) for c in clauses],'paths':paths,'conditional_closures':{a:closure(it['facts'],clauses,[a]) for a in ante},'fact_closure':closure(it['facts'],clauses),'converse_probe':{'seed':'ykchol','does_not_entail':'ockhy','closure':closure(it['facts'],clauses,['ykchol'])}}
    expected=plan['rules']['expected_primary_counts'];assert primary['groups']==expected['groups'] and primary['facts']==expected['unconditional_groups'] and primary['clauses']==expected['conditional_clauses'] and primary['q_types']==expected['q_form_types'];assert primary['body_counts']==[24,1,17,1,3,7,12]
    assert not set(ante)&set(primary['fact_closure']);assert 'ockhy' not in primary['converse_probe']['closure']
    german=['Arbeitsrekonstruktion, keine Übersetzung. Alle Großschriftformen sind unbenannte Prädikate desselben hypothetischen x.','Einleitung: Über x werden die Angaben '+', '.join(x.upper() for x in it['facts'])+' behauptet.']
    for c in clauses:german.append('Fall '+str(c['id'])+': Wenn '+ ' und '.join(x.upper() for x in c['antecedents'])+' für x gilt, dann gelten '+', '.join(x.upper() for x in c['body'])+'.')
    german+=['Verbindung: Unter OCKHY folgt zunächst OKAIIN und darüber YKCHOL. Unter OTCHY folgt OKOL; die zwei OKOL-Fälle liefern gemeinsam CHEOL, DAL, CHOL und DAM.','Ohne tatsächlich geltende Ausgangsvoraussetzung wird damit nichts davon als Tatsache behauptet. Gleiche Aussagewiederholungen bleiben im Text, sind hier aber logisch redundant. q ist weder übersetzt noch als Morphem bestätigt.']
    result={'status':'EXPLORATORY_COMPLETE_SCOPE_CONDITIONAL_PATHS_NOT_CONFIRMED','source_sha256':digest(s),'plan_sha256':digest(p),'builder_sha256':digest(Path(__file__)),'primary_edition':'IT2a','readers':readers,'primary':primary,'german_reading':german,'claim_ceiling':'Full source accounting and logical consequences under authored local qscope/samex/unarypredicate assumptions only; no actual word meaning, phoneme, global grammar, independent data or semantic confirmation.','independent_readers':False,'translated_words':0}
    out=D/'CONDITIONAL42_F89V1_DERIVATION_20261017.json';assert not out.exists(),'Refuse derivation overwrite';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:primary[k] for k in ['groups','facts','clauses','q_types','predicate_types','body_counts']},ensure_ascii=False))

if __name__=='__main__':main()
