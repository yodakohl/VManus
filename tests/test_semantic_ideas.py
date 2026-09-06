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

    def corrected_fixture(self,action):
        (self.root/'tools').mkdir(exist_ok=True)
        (self.root/'tools/semantic_ideas.py').write_bytes(Path(ideas.__file__).read_bytes())
        self.build([self.card()])
        original=json.loads((self.root/ideas.DATA).read_text().splitlines()[0])
        review=dict(id='REVISION1',target=original['id'],previous_revision=None,
                    action=action,reason='Source-level interpretation correction, not a scientific result.',
                    target_basis_sha256=ideas.card_basis(original),evidence=original['evidence'])
        if action=='restate_scope':
            review['replacement']={'claim':'This exact whole form has a proposed powder-related role.','claim_type':'formal_role'}
        (self.root/ideas.CORRECTIONS).write_text(json.dumps(review)+'\n')
        self.build([self.card()])
        return original

    def test_independent_audit_counts_archived_cases_without_scientific_rejection(self):
        self.corrected_fixture('archive_source_error')
        report=audit_actual(self.root)
        self.assertEqual((report['cards'],report['archived_source_error_cards'],report['review_cases_preserved']),(0,1,1))
        archived=json.loads((self.root/ideas.ARCHIVE).read_text())
        archived['status']='scientifically_rejected'
        (self.root/ideas.ARCHIVE).write_text(json.dumps(archived)+'\n')
        import hashlib
        manifest=json.loads((self.root/ideas.MANIFEST).read_text())
        manifest['archive_sha256']=hashlib.sha256((self.root/ideas.ARCHIVE).read_bytes()).hexdigest()
        (self.root/ideas.MANIFEST).write_text(json.dumps(manifest))
        with self.assertRaises(AssertionError):audit_actual(self.root)

    def test_independent_audit_scope_restatement_keeps_original_even_if_snapshot_rehashed(self):
        original=self.corrected_fixture('restate_scope')
        self.assertTrue(audit_actual(self.root)['original_assertions_and_case_fields_preserved'])
        changed=json.loads((self.root/ideas.DATA).read_text())
        self.assertEqual(changed['source_original_assertion']['claim'],original['claim'])
        changed['source_original_assertion']['claim']='A silently different old meaning'
        (self.root/ideas.DATA).write_text(json.dumps(changed)+'\n')
        import hashlib
        manifest=json.loads((self.root/ideas.MANIFEST).read_text())
        manifest['data_sha256']=hashlib.sha256((self.root/ideas.DATA).read_bytes()).hexdigest()
        (self.root/ideas.MANIFEST).write_text(json.dumps(manifest))
        with self.assertRaises(AssertionError):audit_actual(self.root)

def audit_actual(root):
    """Independent output/evidence preservation, not confirmation of claim meanings."""
    import hashlib,re
    from collections import Counter
    root=root.resolve()
    data=root/'research_registry/semantic_ideas.jsonl'
    cards=[json.loads(x) for x in data.read_text().splitlines() if x]
    manifest=json.loads((root/'research_registry/SEMANTIC_IDEAS_MANIFEST.json').read_text())
    archive_path=root/ideas.ARCHIVE
    archived=[json.loads(x) for x in archive_path.read_text().splitlines() if x]
    all_cards=cards+archived
    assert len({c['id'] for c in all_cards})==len(all_cards)
    assert len(archived)==manifest['archived_source_errors']
    assert sum(len(c['cases']) for c in archived)==manifest['archived_source_cases']
    assert hashlib.sha256(archive_path.read_bytes()).hexdigest()==manifest['archive_sha256']
    known={json.loads(x)['id'] for x in (root/'research_registry/semantic_inventory.jsonl').read_text().splitlines() if x}
    assert len({c['id'] for c in cards})==len(cards)==manifest['cards']
    texts={};cases=0
    for c in all_cards:
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
    expected_cards=0;decisions={};originals={};links={}
    for relative in ideas.REVIEWS+[p for p in getattr(ideas,'EXTRA_REVIEWS',[]) if (root/p).exists()]:
        reviewed=json.loads((root/relative).read_text());expected_cards+=len(reviewed['cards'])
        decisions[relative]=len(reviewed.get('dispositions',[]))
        for original in reviewed['cards']:
            key=(relative,original['id']);assert key not in originals
            originals[key]=original
        for disposition in reviewed.get('dispositions',[]):
            for target in disposition.get('card_ids',[]):
                links.setdefault(target,set()).add(disposition['source_id'])
    assert cases==expected_cards==manifest['review_cards_before_exact_assertion_grouping']
    actual_cases=[(case['review_file'],case['id']) for c in all_cards for case in c['cases']]
    assert Counter(actual_cases)==Counter(originals.keys()), 'missing, repeated or invented source case'
    corrections_path=root/ideas.CORRECTIONS
    corrections=[json.loads(x) for x in corrections_path.read_text().splitlines() if x] if corrections_path.exists() else []
    histories={};revision_ids=set()
    for correction in corrections:
        assert correction['id'] not in revision_ids;revision_ids.add(correction['id'])
        history=histories.setdefault(correction['target'],[])
        assert correction.get('previous_revision')==(history[-1]['id'] if history else None)
        assert correction['action'] in ('archive_source_error','retain_as_hypothesis','restate_scope')
        assert correction.get('reason','').strip() and correction.get('evidence')
        for e in correction['evidence']:
            path=Path(e['path']);assert not path.is_absolute() and '..' not in path.parts
            source=root/path;assert source.resolve().is_relative_to(root)
            raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256']
            quote=e['quote'].splitlines();assert raw.decode('utf-8-sig').splitlines()[e['line']-1:e['line']-1+len(quote)]==quote
        history.append(correction)
    assert set(histories)<={c['id'] for c in all_cards}
    archived_ids={c['id'] for c in archived}
    for c in all_cards:
        history=histories.get(c['id'],[])
        assert c.get('source_correction_history',[])==history
        original_claim=c.get('source_original_assertion',{'claim':c['claim'],'claim_type':c['claim_type']})
        for case in c['cases']:
            source=originals[(case['review_file'],case['id'])]
            # Compare every original field, not just counts. Builder-added locators are separate.
            for field,value in source.items():
                if field in ('claim','evidence','ready','member_ids'):continue
                assert case[field]==value, 'source case altered: '+field
            assert set(case['member_ids'])==set(source['member_ids'])|links.get(source['id'],set())
            normalize=lambda value:' '.join(value.replace('`','').split())
            assert normalize(source['claim'])==normalize(original_claim['claim'])
            assert source['claim_type']==original_claim['claim_type']
            for e in source['evidence']:
                assert any(all(bound.get(k)==v for k,v in e.items()) for bound in c['evidence'])
        if history:
            basis={k:c[k] for k in ('claim','claim_type','member_ids','evidence','cases')}
            basis.update(original_claim)
            canonical=json.dumps(basis,ensure_ascii=False,sort_keys=True,separators=(',',':'))
            assert hashlib.sha256(canonical.encode()).hexdigest()==history[-1]['target_basis_sha256']
            latest=history[-1]
            if latest['action']=='restate_scope':
                assert set(c['source_original_assertion'])=={'claim','claim_type'}
                assert {k:c[k] for k in ('claim','claim_type')}==latest['replacement']
            else:assert 'source_original_assertion' not in c
            assert (c['id'] in archived_ids)==(latest['action']=='archive_source_error')
        else:assert c['id'] not in archived_ids and 'source_original_assertion' not in c
        # A source-extraction correction must never silently become a scientific rejection.
        if c['id'] in archived_ids:
            assert c['status']=='source_extraction_withdrawn' and c['original_status']=='unconfirmed'
        else:assert c['status']=='unconfirmed'
        assert c.get('verdict') not in ('refuted','rejected','model_failed','scientifically_rejected')

    for relative,sha in {**manifest['input_sha256'],**manifest['source_sha256']}.items():
        assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==sha
    assert hashlib.sha256(data.read_bytes()).hexdigest()==manifest['data_sha256']
    default=ideas.get_page(root,limit=20)
    public_semantic=sum(c['claim_type']!='formal_role' for c in cards)
    local=ideas.local_cards(root) if hasattr(ideas,'local_cards') else []
    local_semantic=sum(c['claim_type']!='formal_role' for c in local)
    from tools import semantic_identity as identity
    identity_index=identity.build_index(cards+local,identity.read_decisions(root/ideas.IDENTITIES),root,archived_ids=[c['id'] for c in archived])
    all_by_id={c['id']:c for c in cards+local};semantic_groups=0
    for start in range(0,identity_index.counts['groups'],100):
        for group in identity_index.page_groups(start,100):
            representative=identity_index.get_group(group['id'],limit=1)['member_ids'][0]
            semantic_groups+=all_by_id[representative]['claim_type']!='formal_role'
    assert default['matched']==semantic_groups
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
    return dict(status='PASS',cards=len(cards),default_semantic_cards=public_semantic,local_overlay_semantic_cards=local_semantic,operational_default_cards=default['matched'],
        formal_role_cards=sum(c['claim_type']=='formal_role' for c in cards),review_cases_preserved=cases,
        archived_source_error_cards=len(archived),archived_source_cases=sum(len(c['cases']) for c in archived),
        correction_revisions_checked=len(corrections),original_assertions_and_case_fields_preserved=True,
        source_corrections_are_not_scientific_rejections=True,
        member_ids_existing=True,exact_source_quotes_and_hashes=True,ready_entries=0,
        source_disposition_coverage=coverage,disposition_card_references_checked=references,
        accepted_item_types=dict(Counter(c['claim_type'] for c in cards)),disposition_rows_by_review=decisions,
        synthetic_tests=unittest.defaultTestLoader.loadTestsFromTestCase(SemanticIdeasTests).countTestCases(),validator_source='tests/test_semantic_ideas.py',
        input_sha256={'research_registry/semantic_ideas.jsonl':hashlib.sha256(data.read_bytes()).hexdigest(),
                      'tools/semantic_ideas.py':hashlib.sha256((root/'tools/semantic_ideas.py').read_bytes()).hexdigest()},
        limitation='Checks concrete-card schema, source evidence and case preservation. Does not independently establish every semantic classification, logical equivalence, historical meaning, truth, or scientific novelty.')


if __name__=='__main__':unittest.main()
