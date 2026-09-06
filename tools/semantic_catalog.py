"""Bounded access to assessed hypothesis components; no manuscript data access."""
import argparse
import hashlib
import json
from pathlib import Path
from tools.research_registry import _base_records, _review_rows, evidence_path, digest, bounded_view
ROOT=Path(__file__).resolve().parents[1]
DEST='research_registry/decisions/semantic_catalog.json'
INPUTS=['root_hypothesis_review.json','working_hypothesis_review.json','semantic_family_review.json']

def build(root=ROOT):
    folder=root/'research_registry/decisions'
    if (root/DEST).exists():
        validate_catalog(json.loads((root/DEST).read_text()), root)
    root_groups=json.loads((folder/INPUTS[0]).read_text())['groups']
    work=json.loads((folder/INPUTS[1]).read_text())['groups']
    family=json.loads((folder/INPUTS[2]).read_text())
    groups=[]
    for row in root_groups:
        g=dict(row);g['member_ids']=g.pop('members');groups.append(g)
    for row in work:
        g=dict(row);g['title']=g['id'].removeprefix('WH_').replace('_',' ').title()
        g['claim']=g.pop('hypothesis');g['sources']=g.pop('evidence')
        g['assessment_basis']='primary_reports_and_proposal' if any(x.startswith('IP') for x in g['member_ids']) else 'primary_reports'
        g['priority_tier']='CONDITIONAL_DISCRIMINATOR' if g['rank']<=3 else 'ARCHIVE_WORKING_GUESS'
        g['priority_reason']='Rank is evidence-acquisition value only; no new selecting observation is available.'
        g['reopen_conditions']=g.pop('gates');g['ready_to_run']=False
        groups.append(g)
    for row in family['groups']:
        g=dict(row);g['id']='FG-'+g.pop('group_id');g['member_ids']=g.pop('members')
        g['title']=g['id'][3:].replace('_',' ').title();g['claim']=g['reason']
        g['relationship']=g.pop('relation');g['assessment_basis']=g.pop('basis')
        g['sources']=g.pop('evidence');g['priority_tier']='REFERENCE_GROUP'
        g['priority_reason']='Comparison group only; members retain distinct hypotheses and outcomes.'
        g['ready_to_run']=False;groups.append(g)
    records=_base_records(root);reviews=_review_rows(root)
    # Keep all family/anchor dossiers available, even where a broader comparison group exists.
    # This is inherited navigation coverage, explicitly not a fresh identity adjudication.
    family_reviews={r['record_id']:r for r in family['family_reviews']}
    for rid,r in sorted(records.items()):
        if r['kind'] not in ('family','anchor'):continue
        assessed=family_reviews.get(rid);old=reviews.get(rid,{})
        primary=(assessed or {}).get('primary_sources_read',[])
        groups.append(dict(id='DOSSIER-'+rid,title=r['title'],claim=(assessed or {}).get('hypothesis',r['summary']),member_ids=[rid],relationship='single_existing_dossier_not_duplicate_decision',assessment_basis=(assessed or {}).get('assessment_basis','registry_summary_only'),sources=primary or [s['path'] for s in r.get('sources',[])],priority_tier='SOURCE_REVIEW_ON_DEPENDENCY' if not primary else 'ARCHIVE_FIXED_TEST',priority_reason='Review only when a concrete new candidate depends on the exact predecessor; no blanket family rejection or routine archive sweep.',reopen_conditions=[assessed['reconsider_condition_verbatim']] if assessed else [x.get('detail','') for x in old.get('reopen',{}).get('all_of',[])],ready_to_run=False,scope=(assessed or old or r).get('scope','unknown')))
    for g in groups:
        g['source_sha256']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in g['sources']}
    data={'schema_version':1,'scope':'Whole family/anchor navigation plus explicitly reviewed hypothesis components; historical record coverage is reported separately.','identity_rule':'Only exact_duplicate at the declared claim component level collapses repeated hypotheses. Shared methods, sources and prerequisites never merge hypotheses or entire experiments.','priority_rule':'No READY entries. Conditional ranks order evidence acquisition, not predictions of success.','groups':groups}
    (root/DEST).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    return {'groups':len(groups),'exact_component_duplicate_groups':sum(g['relationship']=='exact_duplicate' for g in groups),'ready':0}

def validate_catalog(data, root=ROOT):
    """Fail closed on stale source evidence; validates references, not group truth."""
    records=_base_records(root);seen=set()
    for group in data['groups']:
        if group['id'] in seen:raise ValueError('duplicate catalog group ID')
        seen.add(group['id'])
        members=group['member_ids']
        if not members or len(set(members))!=len(members) or not set(members)<=set(records):
            raise ValueError('invalid catalog member IDs: '+group['id'])
        if group.get('ready_to_run') is not False:
            raise ValueError('catalog cannot grant execution readiness')
        sources=group.get('sources',[]);hashes=group.get('source_sha256',{})
        if not sources or set(sources)!=set(hashes):raise ValueError('missing catalog evidence')
        for relative in sources:
            path=evidence_path(root,relative)
            if not path.is_file() or digest(path)!=hashes[relative]:
                raise ValueError('stale or missing catalog source: '+relative)
    return {'status':'PASS','groups':len(seen),'semantic_truth_validated':False}

def main(argv=None):
    import sys
    arguments=list(sys.argv[1:] if argv is None else argv)
    if '--queue' in arguments:
        from tools.semantic_inventory import main as inventory_main
        return inventory_main([x for x in arguments if x != '--queue'])
    p=argparse.ArgumentParser();p.add_argument('query',nargs='?',default='');p.add_argument('--show');p.add_argument('--queue',action='store_true');p.add_argument('--disposition');p.add_argument('--tier');p.add_argument('--limit',type=int,default=8);p.add_argument('--offset',type=int,default=0);p.add_argument('--build',action='store_true');a=p.parse_args(argv)
    if a.build:print(json.dumps(build()));return
    if not 1<=a.limit<=20 or a.offset<0:p.error('limit 1..20; offset >=0')
    if a.disposition:p.error('--disposition requires --queue')
    data=json.loads((ROOT/DEST).read_text());validate_catalog(data);rows=data['groups']
    if a.show:
        rows=[g for g in rows if g['id']==a.show]
        if not rows:p.error('unknown group ID')
        print(json.dumps(bounded_view(rows[0]),ensure_ascii=False,indent=2));return
    rows=[g for g in rows if (not a.tier or g['priority_tier']==a.tier) and a.query.casefold() in json.dumps(g,ensure_ascii=False).casefold()]
    rows.sort(key=lambda g:(0 if g['priority_tier']=='CONDITIONAL_DISCRIMINATOR' else 1,g.get('rank',999),g['id']))
    page=rows[a.offset:a.offset+a.limit]
    cards=[{k:g[k] for k in ('id','title','member_ids','relationship','priority_tier','ready_to_run')} for g in page]
    print(json.dumps({'results':cards,'matched':len(rows),'next_offset':a.offset+len(page) if a.offset+len(page)<len(rows) else None,'limit':'Group membership is not a record merge or an execution approval.'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
