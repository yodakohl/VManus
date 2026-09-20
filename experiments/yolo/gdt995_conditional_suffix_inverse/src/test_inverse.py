#!/usr/bin/env python3
"""Small invented counterexamples; no historical or manuscript input."""
import importlib.util,unittest
from collections import Counter
from pathlib import Path
P=Path(__file__).parent
def load(n):
 s=importlib.util.spec_from_file_location(n,P/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
runner=load('run');validator=load('validate')
def key(suffixes=('a','ae'),wholes=()):
 k={c:dict(role='L',output=c) for c in 'abcdefghijklmnopqrstuvwxyz'}
 k.update({f'S{i}':dict(role='S',output=x) for i,x in enumerate(suffixes)})
 k.update({f'W{i}':dict(role='W',output=x) for i,x in enumerate(wholes)})
 return k
class Tests(unittest.TestCase):
 def compare(self,words,k):
  w=Counter(tuple(x) for x in words);a=runner.encode_summary(w,k);b=validator.direct_orders(w,k)
  self.assertEqual(a['compatible'],bool(b));self.assertEqual(sorted(tuple(o) for o in a['suffix_orders']),b);return a
 def test_mandatory(self):self.assertFalse(self.compare([list('causa')],key())['compatible'])
 def test_minimum(self):self.assertTrue(self.compare([list('aa')],key())['compatible'])
 def test_suffix(self):self.assertTrue(self.compare([list('caus')+['S0']],key())['compatible'])
 def test_short_suffix(self):self.assertFalse(self.compare([['a','S0']],key())['compatible'])
 def test_whole(self):self.assertFalse(self.compare([list('caus')+['S0']],key(wholes=['causa']))['compatible'])
 def test_whole_beats_suffix(self):self.assertTrue(self.compare([['W0']],key(wholes=['causa']))['compatible'])
 def test_overlap_order(self):
  a=self.compare([list('abc')+['S1']],key(('e','ae')));self.assertEqual(a['suffix_orders'],[['S1','S0']])
 def test_global_cycle(self):
  a=self.compare([list('abc')+['S1'],list('deca')+['S0']],key(('e','ae')));self.assertFalse(a['compatible'])
 def test_internal_suffix(self):self.assertFalse(self.compare([['S0','b']],key())['compatible'])
 def test_inactive_suffix(self):self.assertFalse(self.compare([list('abcus')],key(('us',)))['compatible'])
 def test_literal_domain(self):
  w=Counter({tuple('causa'):2});allowed,blocked=runner.suffix_domains(w,key(),['a','ae'])
  self.assertEqual(allowed,['ae']);self.assertEqual(allowed,validator.independent_allowed(w,key(),['a','ae']))
if __name__=='__main__':unittest.main()
