"""Source-only full world enumeration; no target data or code search."""
import csv, hashlib, itertools, json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
R=E.parents[2]
def dump(path,obj): path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def check_lock():
    for name,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h,name

def grammar(program,selectors,colors):
    if not 1<=len(program)<=8:return False
    used=set()
    for clause in program:
        i=0;queries=0
        while i<len(clause) and clause[i] in selectors:
            used.add(clause[i]);i+=1;queries+=1;n=0
            while i<len(clause) and clause[i] in colors|{'PARENT'}:i+=1;n+=1
            if n>3:return False
        if i!=len(clause)-1 or (queries,clause[i]) not in {(1,'NE'),(2,'EQ')}:return False
    return used==set(selectors)

def truth(program,world,selectors,filters):
    for clause in program:
        stack=[]
        for atom in clause:
            if atom in selectors:stack.append({selectors[atom]})
            elif atom=='PARENT':stack[-1]={world['parent'][n] for n in stack[-1] if n in world['parent']}
            elif atom in filters:stack[-1]={n for n in stack[-1] if world['colors'][n]==filters[atom]}
            elif atom=='NE':
                if not stack.pop():return False
            elif atom=='EQ':
                if stack.pop()!=stack.pop():return False
            else:raise AssertionError(atom)
        assert not stack
    return True

def worlds(spec):
    nodes=spec['nodes'];root=spec['root'];children=[n for n in nodes if n!=root]
    for values in itertools.product(nodes,repeat=len(children)):
        parent=dict(zip(children,values));valid=True
        for n in children:
            seen=set()
            while n!=root:
                if n in seen:valid=False;break
                seen.add(n);n=parent[n]
            if not valid:break
        if not valid:continue
        for colors in itertools.product(spec['colors'],repeat=len(nodes)):
            yield {'parent':parent,'colors':dict(zip(nodes,colors))}

def identity(w):return json.dumps(w,sort_keys=True,separators=(',',':'))

def main():
    check_lock();s=json.loads((E/'src/SPEC.json').read_text())
    selectors=dict(zip(['FIELD','LION','BORDER','ROUND'],s['nodes']))
    filters={c.upper():c for c in s['colors']}
    for p in s['programs'].values():assert grammar(p,selectors,set(filters))
    reference={k:s['source_scene'][k] for k in ['parent','colors']}
    rows=[];counts={p:0 for p in s['programs']};certificates={}
    for w in worlds(s):
        key=identity(w);answers={p:truth(prog,w,selectors,filters) for p,prog in s['programs'].items()}
        different_parent=w['parent']!=reference['parent'];different_colors=w['colors']!=reference['colors']
        row={'world':key,'source_scene':w==reference,**answers};rows.append(row)
        for p,answer in answers.items():
            counts[p]+=answer
            if answer and different_parent and different_colors:certificates.setdefault(p,w)
    rows.sort(key=lambda x:x['world'])
    with (E/'artifacts/WORLD_TABLE.tsv').open('w',newline='') as f:
        writer=csv.DictWriter(f,list(rows[0]),delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(rows)
    accounts=[]
    for p,clauses in s['programs'].items():
        atoms=[a for clause in clauses for a in clause]
        groups=[''.join(s['fixed_code'][a] for a in atoms[i:i+3]) for i in range(0,len(atoms),3)]
        assert ''.join(groups)==''.join(s['fixed_code'][a] for a in atoms)
        accounts.append({'account':p,'clauses':clauses,'grammar_valid':True,'used_atoms':sorted(set(atoms)),
        'all_atoms_used':set(atoms)==set(s['atoms']),'whole_surface':' '.join(groups),'source_truth':truth(clauses,reference,selectors,filters),
        'accepted_worlds':counts[p],'incompatible_worlds':counts[p]-int(truth(clauses,reference,selectors,filters)),
        'changed_parent_and_color_certificate':certificates.get(p)})
    dump(E/'artifacts/ACCOUNTS.json',accounts)
    with (E/'artifacts/ACCOUNT_TABLE.tsv').open('w',newline='') as f:
        fields=['account','whole_surface','grammar_valid','all_atoms_used','source_truth','accepted_worlds','incompatible_worlds']
        writer=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows([{k:a[k] for k in fields} for a in accounts])
    counter=next(a for a in accounts if a['account']=='all_atoms_self_equalities')
    status='COMPLETE_ACCOUNT_TRUTH_INSUFFICIENT' if counter['source_truth'] and counter['all_atoms_used'] and counter['changed_parent_and_color_certificate'] else 'COUNTEREXAMPLE_NOT_ESTABLISHED'
    result={'status':status,'world_count':len(rows),'tree_count':len({json.dumps(json.loads(x['world'])['parent'],sort_keys=True) for x in rows}),
    'accounts':{a['account']:{k:a[k] for k in ['grammar_valid','all_atoms_used','source_truth','accepted_worlds','incompatible_worlds']} for a in accounts},
    'target_access':False,'confirmed_words':0,'significance_claim':False,'scope':'Five fixed accounts, all worlds in the declared finite family; not all grammar programs or all possible scenes.'}
    dump(E/'artifacts/RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
