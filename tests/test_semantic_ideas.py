"""Concrete semantic cards must not be placeholders, execution permits or merged rivals."""
import copy,json,tempfile,unittest
from pathlib import Path
from tools import semantic_ideas as ideas

class SemanticIdeasTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)
        (self.root/'reports').mkdir();(self.root/'reports/evidence.md').write_text('powder is a candidate\nis is a rival candidate\nAn opening role is structural\n')
        (self.root/'research_registry/decisions').mkdir(parents=True)
        self.inventory=self.root/'research_registry/semantic_inventory.jsonl'
        self.inventory.write_text(json.dumps({'id':'SOURCE1'})+'\n'+json.dumps({'id':'SOURCE2'})+'\n')
        for p in ideas.REVIEWS:(self.root/p).write_text(json.dumps({'cards':[],'dispositions':[]}))

    def card(self,identifier='CARD1',claim='okaiin means powder',claim_type='lexical_hypothesis',line=1):
        return dict(id=identifier,claim=claim,claim_type=claim_type,member_ids=['SOURCE1'],
            evidence=[dict(path='reports/evidence.md',line=line,quote=(self.root/'reports/evidence.md').read_text().splitlines()[line-1])],status='unconfirmed',ready=False)

    def build(self,cards):
        (self.root/ideas.REVIEWS[0]).write_text(json.dumps({'cards':cards,'dispositions':[]}))
        return ideas.build(self.root)

    def test_no_source_pointer_empty_status_or_method_assignment_as_idea(self):
        base=self.card()
        for change in [dict(claim_type='source_excerpt'),dict(claim_type='unresolved_source_pointer'),
                       dict(claim=''),dict(claim='Unknown source requires review'),
                       dict(claim='REVIEW_PRIORITY'),dict(claim='Status: PASS'),
                       dict(claim='sha256 = abcdef'),dict(claim='n = 420'),dict(claim='p_value = 0.01')]:
            with self.subTest(change=change),self.assertRaises(ValueError):ideas.validate_card(dict(base,**change),self.root,{'SOURCE1'})

    def test_dangling_ids_and_inexact_quotes_rejected(self):
        c=self.card();c['member_ids']=['MISSING']
        with self.assertRaises(ValueError):ideas.validate_card(c,self.root,{'SOURCE1'})
        c=self.card();c['evidence'][0]['quote']='not the source'
        with self.assertRaises(ValueError):ideas.validate_card(c,self.root,{'SOURCE1'})

    def test_build_rejects_input_execution_approval(self):
        c=self.card();c['ready']=True
        with self.assertRaises(ValueError):self.build([c])

    def test_distinct_meanings_remain_distinct(self):
        self.build([self.card(),self.card('CARD2','okaiin means is',line=2)])
        result=ideas.get_page(self.root)
        self.assertEqual(result['matched'],2)
        self.assertEqual({r['claim'] for r in result['results']},{'okaiin means powder','okaiin means is'})

    def test_exact_assertion_groups_cases_without_merging_source_records(self):
        second=self.card('CARD2');second['member_ids']=['SOURCE2'];second['scope']='second source context'
        self.build([self.card(),second]);result=ideas.get_page(self.root)
        self.assertEqual(result['matched'],1)
        detail=ideas.show(self.root,result['results'][0]['id'])
        self.assertEqual(set(detail['member_ids']),{'SOURCE1','SOURCE2'})
        self.assertEqual(len(detail['cases']),2)
        self.assertIs(detail['ready'],False)

    def test_default_semantic_view_excludes_formal_roles(self):
        self.build([self.card(),self.card('ROLE','Form X marks an opening role','formal_role',3)])
        self.assertEqual(ideas.get_page(self.root)['matched'],1)
        self.assertEqual(ideas.get_page(self.root,include_formal=True)['matched'],2)

    def test_stale_evidence_blocks_display(self):
        self.build([self.card()]);(self.root/'reports/evidence.md').write_text('changed')
        with self.assertRaises(ValueError):ideas.get_page(self.root)

    def test_changed_source_id_inventory_blocks_display(self):
        self.build([self.card()]);self.inventory.write_text(json.dumps({'id':'OTHER'})+'\n')
        with self.assertRaises(ValueError):ideas.get_page(self.root)

    def test_direct_detail_paging_limits_enforced(self):
        self.build([self.card()])
        for limit,offset in [(0,0),(21,0),(2,-1)]:
            with self.subTest(limit=limit,offset=offset),self.assertRaises(ValueError):ideas.show(self.root,'CARD1',field='evidence',limit=limit,offset=offset)

def audit_actual(root):
    """Independent output/evidence preservation, not confirmation of claim meanings."""
    import hashlib,re
    from collections import Counter
    data=root/'research_registry/semantic_ideas.jsonl'
    cards=[json.loads(x) for x in data.read_text().splitlines() if x]
    manifest=json.loads((root/'research_registry/SEMANTIC_IDEAS_MANIFEST.json').read_text())
    known={json.loads(x)['id'] for x in (root/'research_registry/semantic_inventory.jsonl').read_text().splitlines() if x}
    assert len({c['id'] for c in cards})==len(cards)==manifest['cards']
    texts={};cases=0
    for c in cards:
        assert c['claim_type'] in {'lexical_hypothesis','semantic_model','functional_hypothesis','formal_role'}
        assert isinstance(c['claim'],str) and c['claim'].strip() and c['ready'] is False
        assert c['member_ids'] and set(c['member_ids'])<=known
        assert c['evidence'] and c['cases'];cases+=len(c['cases'])
        assert not re.match(r'^(?:Status|sha256|p_value|n_jobs)\s*[:=→]',c['claim'],re.I)
        for e in c['evidence']:
            p=Path(e['path']);assert not p.is_absolute() and '..' not in p.parts
            path=root/p;assert path.resolve().is_relative_to(root) and path.is_file()
            if e['path'] not in texts:texts[e['path']]=path.read_text(encoding='utf-8-sig').splitlines()
            assert texts[e['path']][e['line']-1:e['line']-1+len(e['quote'].splitlines())]==e['quote'].splitlines()
            assert hashlib.sha256(path.read_bytes()).hexdigest()==e['sha256']
    expected_cards=0;decisions={}
    for relative in ideas.REVIEWS+[p for p in getattr(ideas,'EXTRA_REVIEWS',[]) if (root/p).exists()]:
        reviewed=json.loads((root/relative).read_text());expected_cards+=len(reviewed['cards'])
        decisions[relative]=len(reviewed.get('dispositions',[]))
    assert cases==expected_cards==manifest['review_cards_before_exact_assertion_grouping']
    for relative,sha in {**manifest['input_sha256'],**manifest['source_sha256']}.items():
        assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==sha
    assert hashlib.sha256(data.read_bytes()).hexdigest()==manifest['data_sha256']
    default=ideas.get_page(root,limit=20)
    public_semantic=sum(c['claim_type']!='formal_role' for c in cards)
    local=ideas.local_cards(root) if hasattr(ideas,'local_cards') else []
    local_semantic=sum(c['claim_type']!='formal_role' for c in local)
    assert default['matched']==public_semantic+local_semantic
    assert all(c['claim_type']!='formal_role' for c in default['results'])
    inventory=[json.loads(x) for x in (root/'research_registry/semantic_inventory.jsonl').read_text().splitlines() if x]
    review_files=ideas.REVIEWS+[p for p in getattr(ideas,'EXTRA_REVIEWS',[]) if (root/p).exists()]
    expected_proposals={r['id'] for r in inventory if r.get('source_set')=='legacy_proposal_extraction' and r.get('item_type') in ('source_excerpt','hypothesis_proposal')}
    expected_components={r['id'] for r in inventory if r.get('source_set')=='legacy_semantic_components' and r.get('item_type')=='hypothesis_component'}
    expected_ip={r['id'] for r in inventory if r.get('source_set')=='research_registry' and r.get('item_type')=='idea'}
    observed={key:[] for key in ('proposal','component','ip')}
    references=0
    all_card_ids={c['id'] for p in review_files for c in json.loads((root/p).read_text())['cards']}
    for relative in review_files:
        reviewed=json.loads((root/relative).read_text())
        for d in reviewed.get('dispositions',[]):
            sid=d['source_id']
            for key,expected in [('proposal',expected_proposals),('component',expected_components),('ip',expected_ip)]:
                if sid in expected:observed[key].append(sid)
            assert set(d.get('card_ids',[]))<=all_card_ids
            references+=len(d.get('card_ids',[]))
            assert d.get('decision',d.get('disposition')) not in ('pending_review','pending_source_review')
    coverage={}
    for key,expected in [('proposal',expected_proposals),('component',expected_components),('ip',expected_ip)]:
        found=observed[key]
        assert len(found)==len(set(found)) and set(found)==expected, key+' source disposition gap or overlap'
        coverage[key]=dict(expected=len(expected),dispositions=len(found),missing=0,overlap=0)
    assert len(expected_proposals)==5370 and len(expected_components)==3788 and len(expected_ip)==82
    return dict(status='PASS',cards=len(cards),default_semantic_cards=public_semantic,local_overlay_semantic_cards=local_semantic,operational_default_cards=default['matched'],
        formal_role_cards=sum(c['claim_type']=='formal_role' for c in cards),review_cases_preserved=cases,
        member_ids_existing=True,exact_source_quotes_and_hashes=True,ready_entries=0,
        source_disposition_coverage=coverage,disposition_card_references_checked=references,
        accepted_item_types=dict(Counter(c['claim_type'] for c in cards)),disposition_rows_by_review=decisions,
        synthetic_tests=9,validator_source='tests/test_semantic_ideas.py',
        input_sha256={'research_registry/semantic_ideas.jsonl':hashlib.sha256(data.read_bytes()).hexdigest(),
                      'tools/semantic_ideas.py':hashlib.sha256((root/'tools/semantic_ideas.py').read_bytes()).hexdigest()},
        limitation='Checks concrete-card schema, source evidence and case preservation. Does not independently establish every semantic classification, logical equivalence, historical meaning, truth, or scientific novelty.')


if __name__=='__main__':unittest.main()
