"""Run frozen comparison, then certify identity with the unchanged parent graphs."""
from common import *
from run import run
if __name__=='__main__':
 run()
 old=load(P/'artifacts/corrected/GRAPHS.json');new=load(E/'artifacts/GRAPHS.json')
 ref={(g['edition'],g['bound']):g for g in old['graphs'] if g['model']=='LITERAL'}
 checks=[]
 for g in new['graphs']:
  b=ref[g['edition'],g['bound']];checks.append({'edition':g['edition'],'model':g['model'],'bound':g['bound'],'adjacency_identical':g['adjacency']==b['adjacency'],'count_identical':g['count']==b['count'],'all_marginals_identical':g['marginals']==b['marginals']})
 assert all(all(x[k] for k in ['adjacency_identical','count_identical','all_marginals_identical']) for x in checks)
 save(E/'artifacts/UNCHANGED_GRAPH_CERTIFICATE.json',{'status':'PASS','compared_parent':str((P/'artifacts/corrected/GRAPHS.json').relative_to(R)),'graphs':checks})
