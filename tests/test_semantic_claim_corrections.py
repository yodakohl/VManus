import hashlib,json,tempfile,unittest
from pathlib import Path
from tools import semantic_ideas as ideas

class SourceCorrectionTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);self.root=Path(tmp.name)
        (self.root/'research_registry/decisions').mkdir(parents=True)
        self.source=self.root/'report.md';self.source.write_text('Count column: 22:6\nA proposed numerical meaning is two.\n')
        (self.root/'research_registry/semantic_inventory.jsonl').write_text('{"id":"SOURCE1"}\n')
        self.cards=[dict(id='ERROR',claim='okeey → 22:6',claim_type='lexical_hypothesis',member_ids=['SOURCE1'],
            evidence=[dict(path='report.md',line=1,quote='Count column: 22:6')],status='unconfirmed',ready=False),
            dict(id='NUMBER',claim='countword → 2',claim_type='lexical_hypothesis',member_ids=['SOURCE1'],
            evidence=[dict(path='report.md',line=2,quote='A proposed numerical meaning is two.')],status='unconfirmed',ready=False)]
        for f in ideas.REVIEWS:(self.root/f).write_text(json.dumps({'cards':[],'dispositions':[]}))
        self.rebuild()
        self.original=next(r for r in ideas.registry.read_jsonl(self.root/ideas.DATA) if r['claim']=='okeey → 22:6')

    def rebuild(self):
        (self.root/ideas.REVIEWS[0]).write_text(json.dumps({'cards':self.cards,'dispositions':[]}))
        return ideas.build(self.root)

    def review(self,**kwargs):
        d=dict(id='REV1',target=self.original['id'],previous_revision=None,action='archive_source_error',
            reason='The source column reports counts, not meaning.',target_basis_sha256=ideas.card_basis(self.original),
            evidence=[dict(path='report.md',line=1,quote='Count column: 22:6',sha256=hashlib.sha256(self.source.read_bytes()).hexdigest())])
        d.update(kwargs);return d

    def write(self,rows):
        ideas.registry.write_jsonl(self.root/ideas.CORRECTIONS,rows)

    def test_extraction_error_leaves_search_but_preserves_cases_and_valid_numeric_meaning(self):
        self.write([self.review()]);self.rebuild()
        page=ideas.get_page(self.root);self.assertEqual([x['claim'] for x in page['results']],['countword → 2'])
        archived=ideas.show(self.root,'ERROR')
        self.assertEqual(archived['status'],'source_extraction_withdrawn')
        self.assertEqual(archived['cases'],self.original['cases'])
        self.assertEqual(archived['evidence'],self.original['evidence'])
        m=ideas.validate(self.root);self.assertEqual(m['archived_source_cases'],1)
        self.assertEqual(m['exact_assertion_repetitions_grouped'],0)

    def test_new_or_stale_correction_blocks_old_display(self):
        self.write([self.review()])
        with self.assertRaises(ValueError):ideas.get_page(self.root)
        self.rebuild();self.source.write_text('Changed source\n')
        with self.assertRaises(ValueError):ideas.get_page(self.root)

    def test_changed_case_scope_requires_explicit_rereview(self):
        self.write([self.review()]);self.rebuild()
        self.cards[0]['scope']={'unit':'a different explicit card unit'}
        with self.assertRaisesRegex(ValueError,'changed corrected claim'):self.rebuild()

    def test_revisions_must_link_and_restore_preserves_prior_error_decision(self):
        old=self.review();new=self.review(id='REV2',action='retain_as_hypothesis',reason='Explicit review reverses the source classification.')
        self.write([old,new])
        with self.assertRaisesRegex(ValueError,'revision chain'):self.rebuild()
        new['previous_revision']='REV1';self.write([old,new]);self.rebuild()
        restored=ideas.show(self.root,'ERROR')
        self.assertEqual([r['id'] for r in restored['source_correction_history']],['REV1','REV2'])
        self.assertEqual(ideas.get_page(self.root)['matched'],2)

    def test_scope_restatement_preserves_original_assertion_and_excludes_formal_from_default(self):
        review=self.review(action='restate_scope',replacement={'claim':'The source assigns a local role to two occurrences.','claim_type':'formal_role'})
        self.write([review]);self.rebuild()
        changed=ideas.show(self.root,'ERROR')
        self.assertEqual(changed['claim_type'],'formal_role')
        self.assertEqual(changed['source_original_assertion']['claim'],'okeey → 22:6')
        self.assertEqual(ideas.card_basis(changed),ideas.card_basis(self.original))
        self.assertEqual(ideas.get_page(self.root)['matched'],1)
        self.assertEqual(ideas.get_page(self.root,include_formal=True)['matched'],2)

if __name__=='__main__':unittest.main()
