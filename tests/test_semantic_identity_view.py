import hashlib,json,tempfile,unittest
from pathlib import Path
from tools import semantic_ideas as ideas,semantic_identity as identity

class IdentityViewTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);self.root=Path(tmp.name)
        (self.root/'research_registry/decisions').mkdir(parents=True)
        (self.root/'report.md').write_text('Two names propose a liquid carrier.\nA powder proposal is a rival.\n')
        (self.root/'research_registry/semantic_inventory.jsonl').write_text('{"id":"SOURCE1"}\n')
        for f in ideas.REVIEWS:(self.root/f).write_text(json.dumps({'cards':[],'dispositions':[]}))
        cs=[dict(id=i,claim=c,claim_type='lexical_hypothesis',member_ids=['SOURCE1'],evidence=[dict(path='report.md',line=1,quote='Two names propose a liquid carrier.')],status='unconfirmed',ready=False) for i,c in [('A','qokaiin means working liquid'),('B','qokaiin means liquid carrier'),('C','qokaiin means powder')]]
        (self.root/ideas.REVIEWS[0]).write_text(json.dumps({'cards':cs,'dispositions':[]}));ideas.build(self.root)
        self.cards=ideas.registry.read_jsonl(self.root/ideas.DATA)
        self.ids={c['review_ids'][0]:c['id'] for c in self.cards}
        members=[self.ids['A'],self.ids['B']];by_id={c['id']:c for c in self.cards}
        self.decision=dict(id='PAIR1',decision_key='PAIR',previous_revision=None,relation='equivalent_proposition',status='approved',member_ids=members,card_basis={m:identity.original_basis(by_id[m]) for m in members},effective_basis={m:identity.effective_basis(by_id[m]) for m in members},reviewer='reviewer',reason='Same scoped proposed carrier.',evidence=[dict(path='report.md',line=1,quote='Two names propose a liquid carrier.',sha256=hashlib.sha256((self.root/'report.md').read_bytes()).hexdigest())])
        identity.append_decision(self.root,self.root/ideas.IDENTITIES,self.decision,self.cards)

    def test_group_searches_all_names_and_preserves_original_ids_and_cases(self):
        self.assertEqual(ideas.get_page(self.root)['matched'],2)
        liquid=ideas.get_page(self.root,'working liquid')['results'][0]
        self.assertEqual(liquid['equivalent_variants'],2)
        self.assertEqual(liquid['group_scope_cases'],2)
        names=ideas.show(self.root,self.ids['A'],'equivalents')['items']
        self.assertEqual({x['id'] for x in names},{self.ids['A'],self.ids['B']})
        self.assertEqual(ideas.show(self.root,self.ids['B'])['claim'],'qokaiin means liquid carrier')
        self.assertEqual(ideas.show(self.root,self.ids['B'],'cases')['matched'],1)
        self.assertEqual(ideas.get_page(self.root,'powder')['results'][0]['equivalent_variants'],1)

    def test_revision_invalidates_cache_without_rewriting_original_snapshot(self):
        ideas.get_page(self.root);original=(self.root/ideas.DATA).read_bytes()
        second=dict(self.decision,id='PAIR2',previous_revision='PAIR1',status='rejected',reason='Scope identity withdrawn.')
        identity.append_decision(self.root,self.root/ideas.IDENTITIES,second,self.cards)
        self.assertEqual(ideas.get_page(self.root)['matched'],3)
        self.assertEqual((self.root/ideas.DATA).read_bytes(),original)

    def test_stale_evidence_never_reuses_cached_group(self):
        ideas.get_page(self.root)
        (self.root/'report.md').write_text('Changed source\n')
        with self.assertRaises(ValueError):ideas.get_page(self.root)

    def test_scoped_failure_is_visible_without_rejecting_broader_card(self):
        target=self.ids['C'];card=next(c for c in self.cards if c['id']==target)
        d=dict(id='F1',decision_key='F',previous_revision=None,status='reviewed_scoped_context',targets=[target],
            card_basis={target:ideas.card_basis(card)},effective_basis={target:identity.effective_basis(card)},
            evidence=self.decision['evidence'],claim='Powder with a particular owner.',scope='Only the explicit owner transfer.',
            claim_ceiling='Does not refute powder generally.',reason_class='empirical_failure')
        ideas.registry.write_jsonl(self.root/ideas.FAILURES,[d])
        result=ideas.show(self.root,target,'assessments')['items'][0]
        self.assertEqual(result['reason_class'],'empirical_failure')
        self.assertFalse(result['automatic_card_status_propagation'])
        self.assertEqual(ideas.show(self.root,target)['status'],'unconfirmed')
        d['card_basis'][target]='0'*64;ideas.registry.write_jsonl(self.root/ideas.FAILURES,[d])
        with self.assertRaisesRegex(ValueError,'stale scoped'):ideas.show(self.root,target,'assessments')

    def test_scoped_assessment_revision_cannot_erase_history(self):
        target=self.ids['C'];card=next(c for c in self.cards if c['id']==target)
        d=dict(id='F1',decision_key='F',previous_revision=None,status='reviewed_scoped_context',targets=[target],
            card_basis={target:ideas.card_basis(card)},effective_basis={target:identity.effective_basis(card)},
            evidence=self.decision['evidence'],scope='Restricted test.',claim_ceiling='No broader conclusion.')
        changed=dict(d,id='F2')
        ideas.registry.write_jsonl(self.root/ideas.FAILURES,[d,changed])
        with self.assertRaisesRegex(ValueError,'revision chain'):ideas.show(self.root,target,'assessments')
        changed['previous_revision']='F1';ideas.registry.write_jsonl(self.root/ideas.FAILURES,[d,changed])
        self.assertEqual(ideas.show(self.root,target,'assessments')['items'][0]['id'],'F2')

if __name__=='__main__':unittest.main()
