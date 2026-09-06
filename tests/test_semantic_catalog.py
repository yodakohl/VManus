"""Regressions for source changes and claim-component identity boundaries."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import semantic_catalog as catalog

class SemanticCatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'evidence.md').write_text('original evidence')
        self.group={'id':'word-claim','member_ids':['A','B'],'ready_to_run':False,'sources':['evidence.md'],'source_sha256':{'evidence.md':catalog.digest(self.root/'evidence.md')},'relationship':'exact_duplicate'}
        self.data={'groups':[self.group]}
        self.patcher=patch.object(catalog,'_base_records',return_value={'A':{},'B':{}})
        self.patcher.start();self.addCleanup(self.patcher.stop)
    def test_changed_evidence_is_rejected(self):
        catalog.validate_catalog(self.data,self.root)
        (self.root/'evidence.md').write_text('changed result')
        with self.assertRaisesRegex(ValueError,'stale'):catalog.validate_catalog(self.data,self.root)
    def test_dangling_member_is_rejected(self):
        self.group['member_ids'].append('missing')
        with self.assertRaisesRegex(ValueError,'member'):catalog.validate_catalog(self.data,self.root)
    def test_execution_approval_is_rejected(self):
        self.group['ready_to_run']=True
        with self.assertRaisesRegex(ValueError,'readiness'):catalog.validate_catalog(self.data,self.root)
    def test_repeated_group_id_is_rejected(self):
        self.data['groups'].append(copy.deepcopy(self.group))
        with self.assertRaisesRegex(ValueError,'duplicate'):catalog.validate_catalog(self.data,self.root)
    def test_rebuild_does_not_rebind_changed_evidence(self):
        dest=self.root/catalog.DEST;dest.parent.mkdir(parents=True);dest.write_text(json.dumps(self.data))
        (self.root/'evidence.md').write_text('unreviewed replacement')
        with self.assertRaisesRegex(ValueError,'stale'):catalog.build(self.root)
    def test_exact_component_does_not_require_experiment_merge(self):
        result=catalog.validate_catalog(self.data,self.root)
        self.assertFalse(result['semantic_truth_validated'])
        self.assertEqual(self.group['member_ids'],['A','B'])
if __name__=='__main__':unittest.main()
