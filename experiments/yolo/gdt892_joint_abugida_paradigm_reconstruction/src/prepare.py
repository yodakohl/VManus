"""Acquire/compile public reference data only. Never reads hidden control or Voynich."""
import argparse,csv,hashlib,json,pickle,sys,time
from pathlib import Path
from collections import defaultdict,Counter
from core import normalize,alphabetic,VOWELS,components,pattern
FEATURES=('UPOS','Case','Number','Person','VerbForm','Mood')

def feat_dict(raw):
    return dict(x.split('=',1) for x in raw.split('|') if '=' in x)

def tag(upos,feats):return tuple(upos if k=='UPOS' else feats.get(k,'_') for k in FEATURES)

def conllu_sentences(path):
    rows=[];sid='';bad=False
    with Path(path).open() as f:
        for line in f:
            line=line.rstrip('\n')
            if line.startswith('# sent_id = '):sid=line.split(' = ',1)[1]
            elif line and not line.startswith('#'):
                r=line.split('\t')
                if len(r)!=10:bad=True;continue
                if '-' in r[0]:bad=True;continue
                if '.' in r[0]:continue # explicit empty nodes have no written token
                if not r[0].isdigit():bad=True;continue
                if r[3]=='PUNCT':continue
                form=normalize(r[1])
                if not alphabetic(form):bad=True
                rows.append(dict(id=int(r[0]),form=form,lemma=normalize(r[2]),upos=r[3],feats=feat_dict(r[5]),head=int(r[6]) if r[6].isdigit() else -1,deprel=r[7]))
            elif not line:
                if rows and not bad:yield {'id':sid,'words':rows}
                rows=[];sid='';bad=False
    if rows and not bad:yield {'id':sid,'words':rows}

def build_lexicon(cache,ittb):
    meta=json.loads((cache/'SOURCE.json').read_text())
    for name,info in meta['files'].items():
        assert hashlib.sha256((cache/name).read_bytes()).hexdigest()==info['sha256'],name
    cells={r['cell_id']:r for r in csv.DictReader((cache/'LatInfLexi-cells.csv').open())}
    analyses=defaultdict(set);lemma_analyses=defaultdict(set);counts=Counter()
    for r in csv.DictReader((cache/'LatInfLexi-forms.csv').open()):
        word=normalize(r['orth_form']);counts['rows']+=1
        if not alphabetic(word):counts['nonword_or_missing_or_defective']+=1;continue
        cell=cells[r['cell']];upos='NOUN' if r['POS']=='noun' else 'VERB';t=tag(upos,feat_dict(cell['ud']))
        analyses[word].add(t);lemma_analyses[word].add((r['lexeme'],r['cell']));counts['valid_rows']+=1
    sentences=list(conllu_sentences(ittb));counts['reference_sentences']=len(sentences)
    for s in sentences:
        for w in s['words']:
            analyses[w['form']].add(tag(w['upos'],w['feats']))
            lemma_analyses[w['form']].add((w['lemma'],'UD:'+json.dumps(w['feats'],sort_keys=True,separators=(',',':'))))
    lex={'forms':sorted(analyses),'analyses':{k:sorted(v) for k,v in analyses.items()},'lemma_analyses':{k:sorted(v) for k,v in lemma_analyses.items()},'reference_sentences':sentences,'source':meta,'counts':dict(counts),'ittb_sha256':hashlib.sha256(Path(ittb).read_bytes()).hexdigest()}
    with (cache/'reference_lexicon.pkl').open('wb') as f:pickle.dump(lex,f,protocol=5)
    print(json.dumps({'forms':len(analyses),**counts}),flush=True)
    return lex

def attach_grammar(cache):
    from grammar import build_grammar
    with (cache/'reference_lexicon.pkl').open('rb') as f:lex=pickle.load(f)
    lex['grammar']=build_grammar(lex.pop('reference_sentences'))
    with (cache/'reference.pkl').open('wb') as f:pickle.dump(lex,f,protocol=5)
    (cache/'reference_grammar.json').write_text(json.dumps(lex['grammar'],ensure_ascii=False,separators=(',',':'))+'\n')
    print('grammar attached',flush=True)

def build_patterns(cache):
    with (cache/'reference_lexicon.pkl').open('rb') as f:lex=pickle.load(f)
    for inherent in VOWELS:
        t0=time.monotonic();index=defaultdict(list)
        for i,word in enumerate(lex['forms']):
            cs=components(word,inherent);index[pattern(cs)].append((i,cs))
        with (cache/('patterns_'+inherent+'.pkl')).open('wb') as f:pickle.dump(dict(index),f,protocol=5)
        print(json.dumps({'inherent':inherent,'patterns':len(index),'forms':len(lex['forms']),'seconds':time.monotonic()-t0}),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--cache-dir',type=Path,required=True);p.add_argument('--ittb-source',type=Path);p.add_argument('--stage',choices=['lexicon','patterns','grammar'],required=True);a=p.parse_args()
    if a.stage=='lexicon':build_lexicon(a.cache_dir,a.ittb_source)
    elif a.stage=='patterns':build_patterns(a.cache_dir)
    else:attach_grammar(a.cache_dir)
if __name__=='__main__':main()
