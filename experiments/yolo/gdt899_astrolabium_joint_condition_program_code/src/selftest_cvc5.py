#!/usr/bin/env python3
"""Small exact interface tests. These are not manuscript evidence."""
from run import fit

order=['location','mercury','companion']
source={'programs':[{'id':str(i),'header_factors':{'location':['A'],'mercury':['B'],'companion':['C']},'after_header':['D'],'body_atoms':[atom]} for i,atom in enumerate(['E','F'])]}
def target(strings):
    return {'panels':{'IT2a':[{'id':str(i),'text':t,'words':t.split(' '),'page':'f1r','physical_folio':'f1'} for i,t in enumerate(strings)]}}
sat=fit(source,target(['ab de','ab df']),order,10,lambda x:None)
assert sat['status']=='SAT' and sat['witness_validation']=='PASS_COMPLETE_EQUATIONS'
assert fit(source,target(['abc','abd']),order,10,lambda x:None)['status']=='UNSAT'
atomic={'programs':[{'id':str(i),'header_factors':{r:[] for r in order},'after_header':[],'body_atoms':[a]} for i,a in enumerate(['X','Y'])]}
# Add a second copy of the variable: source CONCAT remains an ordinary term.
for p in atomic['programs']:p['body_atoms']*=2
assert fit(atomic,target(['aa','aaaa']),order,10,lambda x:None)['status']=='UNSAT'
print('PASS: complete-equation SAT/space witness, length UNSAT, prefix collision UNSAT')
