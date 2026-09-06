#!/usr/bin/env python3
"""Invented-fixture tests for the integrated constraint; no historical inputs."""
import importlib.util
from itertools import product
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parent
YOLO = SOURCE.parents[1]


def imported(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


HARNESS = r'''
struct Snapshot {
    array<int,38> key,bestkey,initialkey;
    double score,best;
    vector<Decoded> decoded;
    vector<double> edges,families;
    Snapshot(const Search&s):key(s.key),bestkey(s.bestkey),initialkey(s.initialkey),score(s.score),best(s.best),decoded(s.decoded),edges(s.edgevalues),families(s.familyvalues){}
    void unchanged(const Search&s)const {
        if(key!=s.key||bestkey!=s.bestkey||initialkey!=s.initialkey||score!=s.score||best!=s.best||edges!=s.edgevalues||families!=s.familyvalues)throw runtime_error("rejection changed committed state");
        for(size_t i=0;i<decoded.size();i++)if(decoded[i].word!=s.decoded[i].word||decoded[i].id!=s.decoded[i].id||decoded[i].uni!=s.decoded[i].uni)throw runtime_error("rejection changed decoded cache");
    }
};
void verify(Search&s) {
    if(s.priority_legal_cached()!=s.priority_legal_direct())throw runtime_error("cached/direct priority mismatch");
    double score=s.score;auto old=s.decoded;auto edges=s.edgevalues;s.rebuild();
    if(abs(score-s.score)>1e-7)throw runtime_error("full score mismatch");
    for(size_t i=0;i<old.size();i++)if(old[i].word!=s.decoded[i].word||old[i].id!=s.decoded[i].id||abs(old[i].uni-s.decoded[i].uni)>1e-10)throw runtime_error("full decoded mismatch");
    for(size_t i=0;i<edges.size();i++)if(abs(edges[i]-s.edgevalues[i])>1e-8)throw runtime_error("full edge mismatch");
    if(!s.legal()||(s.strict&&!s.priority_legal_direct()))throw runtime_error("invalid final state");
}
int value(const Search&s,int role,const string& word) {
    for(int v=0;v<26+int(s.p.suffixes.size()+s.p.wholes.size());v++)if(s.role(v)==role&&s.output(v)==word)return v;
    throw runtime_error("fixture emission absent");
}
int holder(const array<int,38>& key,int emission) {
    for(int a=0;a<38;a++)if(key[a]==emission)return a;
    throw runtime_error("fixture holder absent");
}
void setup(Search&s,const array<int,38>& key,bool strict) {
    s.strict=strict;s.key=key;s.initialkey=key;s.best=-numeric_limits<double>::infinity();
    if(!s.legal()||!s.priority_legal_direct())throw runtime_error("fixture start incompatible");
    s.rebuild();s.savebest();
}
int main(int argc,char**argv) {
    if(argc>1&&string(argv[1])=="engine")return included_engine_main(argc-1,argv+1);
    try {
        string mode=argv[1];Ref r(argv[2]);Problem p(argv[3]);p.configure(true);
        array<int,38> base{};ifstream input(argv[4]);for(int a=0;a<38;a++)input>>base[a];
        if(!input)throw runtime_error("fixture key read");string out=argv[5];
        Search s(r,p,"OFF",311);
        if(mode=="stop") {
            s.strict=true;bool stopped=false;
            try{s.initialize(1,17,7);}catch(const exception&e){if(string(e.what())!="INITIALIZATION_STOP")throw;stopped=true;}
            if(!stopped||s.initialization_attempts!=7||isfinite(s.best)||s.score!=0)throw runtime_error("initialization cap/best failure");
            for(const auto& d:s.decoded)if(!d.word.empty())throw runtime_error("failed initialization decoded/scored words");
            for(double x:s.edgevalues)if(x!=0)throw runtime_error("failed initialization scored edges");
            cout<<"STOP\t7\tUNSCORED\n";return 0;
        }
        if(mode=="initialize") {
            Search relaxed(r,p,"OFF",311),strict(r,p,"OFF",311);strict.strict=true;
            relaxed.initialize(1,17);strict.initialize(1,17);
            if(relaxed.initialkey!=strict.initialkey||relaxed.key!=strict.key||relaxed.initialization_attempts!=strict.initialization_attempts||relaxed.score!=strict.score||!(relaxed.rng==strict.rng))throw runtime_error("unpaired initialization");
            mt19937_64 expected(311);if(!(strict.rng==expected))throw runtime_error("search RNG includes initialization retries");
            relaxed.write(out+".RELAXED");strict.write(out+".INITIAL");
            strict.optimize(800,1);verify(strict);strict.write(out+".STRICT");
            cout<<"PAIRED_INITIALIZATION_PASS\n";return 0;
        }
        int activeW=holder(base,value(s,4,"zzzzz")),inactiveW=holder(base,value(s,4,"et"));
        int M=holder(base,12),N=holder(base,13),J=holder(base,9),S=holder(base,value(s,2,"am"));
        if(mode=="literal")base[inactiveW]=value(s,4,"abcan");
        if(mode=="suffix")base[inactiveW]=value(s,4,"abcos");
        setup(s,base,true);vector<pair<int,int>> changes;
        if(mode=="active"||mode=="best")changes={{activeW,value(s,4,"abcam")}};
        else if(mode=="inactive") {
            if(!p.affected[inactiveW].empty())throw runtime_error("inactive fixture is observed");
            changes={{inactiveW,value(s,4,"abcam")}};
        }
        else if(mode=="literal")changes={{M,base[N]},{N,base[M]}};
        else if(mode=="suffix")changes={{S,value(s,2,"os")}};
        else if(mode=="owner")changes={{activeW,base[inactiveW]},{inactiveW,base[activeW]}};
        else if(mode=="package")changes={{activeW,base[J]},{J,base[activeW]}};
        else if(mode=="atomic")changes={{activeW,value(s,4,"abcam")},{M,base[N]},{N,base[M]},{S,value(s,2,"as")}};
        else throw runtime_error("unknown fixture mode");
        bool should_reject=mode=="active"||mode=="inactive"||mode=="literal"||mode=="suffix"||mode=="best";
        if(should_reject) {
            for(auto test:vector<pair<double,bool>>{{0,false},{80,false},{0,true}}) {
                Snapshot before(s);
                if(s.change(changes,test.first,test.second))throw runtime_error("strict incompatible move accepted");
                before.unchanged(s);verify(s);
            }
            if(s.priority_rejections!=3)throw runtime_error("priority rejection accounting");
            s.write(out+".STRICT");
            Search relaxed(r,p,"OFF",311);setup(relaxed,base,false);
            double before=relaxed.score;
            if(!relaxed.change(changes,0,true))throw runtime_error("relaxed comparison rejected");
            verify(relaxed);if(relaxed.priority_legal_direct())throw runtime_error("fixture did not create collision");
            if(mode=="best") {
                if(!(relaxed.score>before))throw runtime_error("fixture violation not language-preferred");
                relaxed.optimize(0,0);s.optimize(0,0);verify(relaxed);verify(s);
                if(relaxed.priority_legal_direct()||!s.priority_legal_direct())throw runtime_error("final best feasibility failure");
                s.write(out+".STRICT");
            }
            relaxed.write(out+".RELAXED");
        } else {
            if(!s.change(changes,0,true))throw runtime_error("compatible atomic move rejected");
            verify(s);s.write(out+".STRICT");
        }
        cout<<"FIXTURE_PASS\t"<<mode<<"\n";return 0;
    }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}
}
'''


class IntegratedConstraintTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("g++") is None:
            raise unittest.SkipTest("g++ required")
        cls.reference = imported("gdt836_toy_reference", YOLO / "gdt832_joint_family_context_control/src/reference_model.py")
        cls.projector = imported("gdt836_toy_projector", YOLO / "gdt834_role_blind_mixed_control/src/run.py")
        cls.oracle = imported("gdt836_toy_precedence_oracle", YOLO / "gdt835_wholeword_precedence_audit/src/run.py")
        cls.scratch = tempfile.TemporaryDirectory(prefix="gdt836-constraint-toy-")
        cls.directory = Path(cls.scratch.name)
        cls.pools = {
            "suffix_pool": ["a", "ae", "am", "as", "e", "em", "i", "is", "o", "os", "um", "us"],
            "wholeword_pool": ["zzzzz", "et", "in", "non", "est", "ad", "ut", "per", "abcam", "abcan", "abcos", "longissimo"],
        }
        for a,b in product("abcdefghijklmnopqrstuvwxyz",repeat=2):
            if a+b not in cls.pools["wholeword_pool"]:
                cls.pools["wholeword_pool"].append(a+b)
            if len(cls.pools["wholeword_pool"])==128:
                break
        sentences = [["abcam", "abcam", "abcam"]]*30 + [["abcam", "zzzzz", "abcan"], ["abcos", "et", "abcam"]]
        ref = cls.directory / "toy_reference.jsonl"
        ref.write_text("".join(json.dumps(row)+"\n" for row in sentences))
        families = cls.directory / "toy_families.json"
        families.write_text("{}\n")
        cls.model_dir = cls.directory / "model"
        cls.reference.build(ref,families,cls.model_dir)
        cls.model = cls.reference.load(cls.model_dir)
        emissions = list(range(26))+[28,27,33,37]+list(range(38,46))
        order = list(range(38));random.Random(887).shuffle(order)
        cls.key_values = [0]*38
        for before,after in enumerate(order):cls.key_values[after]=emissions[before]
        name = lambda old:f"X{order[old]:02d}"
        literal = [name(x) for x in (0,1,2,0,12)]
        suffix = [name(x) for x in (0,1,2,26)]
        whole = [name(30)]
        cls.paragraphs = [{"paragraph_id":"toy","words":[literal,whole,suffix,whole,literal]}]
        source = cls.directory / "toy_discovery.json"
        source.write_text(json.dumps({"split":"discovery","paragraphs":cls.paragraphs}))
        cls.projection = cls.directory / "projection.txt"
        cls.projector.projection(source,cls.pools,cls.projection,"BLIND")
        cls.key_file = cls.directory / "key.txt"
        cls.key_file.write_text(" ".join(map(str,cls.key_values)))
        cpp = cls.directory / "harness.cpp"
        cpp.write_text('#define main included_engine_main\n#include "'+str(SOURCE / "decoder.cpp")+'"\n#undef main\n'+HARNESS)
        cls.binary = cls.directory / "harness"
        subprocess.run(["g++","-std=c++17","-O1","-DGDT832_CHECK_DELTAS",str(cpp),"-o",str(cls.binary)],check=True,capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.model.log_character.cache_clear();cls.model.log_unigram.cache_clear();cls.scratch.cleanup()

    def parsed(self,path):
        key,initial,metadata = {},{},{}
        for line in path.read_text().splitlines():
            row=line.split("\t")
            if row[0]=="INITIAL":initial[f"X{int(row[1]):02d}"]={"role":row[2],"output":row[3]}
            elif row[0].isdigit():key[f"X{int(row[0]):02d}"]={"role":row[1],"output":row[2]}
            else:metadata[row[0]]=row[1:]
        self.assertEqual(len(key),38);self.assertEqual(len(initial),38)
        expected=sum(self.model.paragraph_score([''.join(key[a]['output'] for a in word) for word in p['words']]) for p in self.paragraphs)
        self.assertAlmostEqual(float(metadata['SCORE'][0]),expected,places=8)
        return key,initial,metadata

    def run_case(self,mode,projection=None):
        out=self.directory/('result_'+mode)
        result=subprocess.run([str(self.binary),mode,str(self.model_dir),str(projection or self.projection),str(self.key_file),str(out)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        return out,result.stdout

    def check_state(self,path,compatible):
        key,initial,metadata=self.parsed(path)
        self.assertEqual(self.oracle.audit_words(self.paragraphs,key)['passes_W_precedence'],compatible)
        return key,initial,metadata

    def test_active_and_inactive_wholeword_changes_require_global_scan(self):
        for mode in ('active','inactive'):
            with self.subTest(mode=mode):
                out,_=self.run_case(mode)
                self.check_state(Path(str(out)+'.STRICT'),True)
                self.check_state(Path(str(out)+'.RELAXED'),False)

    def test_literal_and_suffix_changes_create_global_dictionary_collisions(self):
        for mode in ('literal','suffix'):
            with self.subTest(mode=mode):
                out,_=self.run_case(mode)
                self.check_state(Path(str(out)+'.STRICT'),True)
                self.check_state(Path(str(out)+'.RELAXED'),False)

    def test_wholeword_owner_and_cross_role_package_swaps_remain_legal(self):
        for mode in ('owner','package'):
            with self.subTest(mode=mode):
                out,_=self.run_case(mode)
                self.check_state(Path(str(out)+'.STRICT'),True)

    def test_multiple_updates_are_checked_as_one_complete_candidate(self):
        out,_=self.run_case('atomic')
        self.check_state(Path(str(out)+'.STRICT'),True)

    def test_forced_greedy_and_final_best_cannot_bypass_strict_constraint(self):
        out,_=self.run_case('best')
        strict,_,strict_meta=self.check_state(Path(str(out)+'.STRICT'),True)
        relaxed,_,relaxed_meta=self.check_state(Path(str(out)+'.RELAXED'),False)
        self.assertGreater(float(relaxed_meta['SCORE'][0]),float(strict_meta['SCORE'][0]))
        self.assertEqual(int(strict_meta['PRIORITY_REJECTIONS'][0]),3)

    def test_common_initialization_and_strict_optimization_keep_compatible_best(self):
        out,_=self.run_case('initialize')
        relaxed,relaxed_initial,rmeta=self.check_state(Path(str(out)+'.RELAXED'),True)
        strict,strict_initial,smeta=self.check_state(Path(str(out)+'.INITIAL'),True)
        self.assertEqual(relaxed,strict);self.assertEqual(relaxed_initial,strict_initial)
        for field in ('INITIALIZATION_ATTEMPTS','INITIALIZATION_SEED','SEARCH_SEED'):
            self.assertEqual(rmeta[field],smeta[field])
        self.check_state(Path(str(out)+'.STRICT'),True)

    def test_infeasible_initialization_retries_to_cap_without_scoring_or_best(self):
        pools={'suffix_pool':self.pools['suffix_pool'],
               'wholeword_pool':[''.join(pair) for pair in list(product('abcdefghijklmnopqrstuvwxyz',repeat=2))[:128]]}
        # All two-letter strings are represented compositionally under every
        # literal bijection, so every permitted W value is forbidden.
        words=[[f'X{a:02d}',f'X{b:02d}'] for a,b in product(range(26),repeat=2)]
        words += [[f'X{a:02d}'] for a in range(26,34)]
        source=self.directory/'impossible_discovery.json';source.write_text(json.dumps({'split':'discovery','paragraphs':[{'words':words}]}))
        projected=self.directory/'impossible_projection.txt';self.projector.projection(source,pools,projected,'BLIND')
        out,stdout=self.run_case('stop',projected)
        self.assertIn('STOP\t7\tUNSCORED',stdout)
        self.assertFalse(out.exists())

    def test_score_entrypoint_accepts_relaxed_but_rejects_incompatible_strict_key(self):
        out,_=self.run_case('active')
        key,_,_=self.parsed(Path(str(out)+'.RELAXED'))
        source=self.directory/'score_key.tsv';source.write_text(''.join(f"{int(a[1:])}\t{row['role']}\t{row['output']}\n" for a,row in sorted(key.items())))
        for mode,success in [('RELAXED',True),('STRICT',False)]:
            target=self.directory/f'score_{mode}.tsv'
            result=subprocess.run([str(self.binary),'engine','--score',str(self.model_dir),str(self.projection),mode,str(source),str(target)],capture_output=True,text=True)
            self.assertEqual(result.returncode==0,success,result.stderr)
            if success:self.check_state(target,False)

    def test_source_validator_skips_other_work_payload_before_comment_or_token_parsing(self):
        validator=imported('gdt836_toy_source_validator',SOURCE/'validate.py')
        path=self.directory/'toy_scope.conllu'
        path.write_text(
            '# sent_id = Other-1\n# text = OTHER_DO_NOT_PARSE\nOTHER_BAD_ROW\n\n'
            '# sent_id = Que-1\n# citation = 1.1\n# text = rosa\n'
            '1\trosa\trosa\tNOUN\t_\t_\t0\troot\t_\t_\n\n'
            '# sent_id = Other-2\n# text = OTHER_DO_NOT_PARSE_AGAIN\nOTHER_BAD_ROW\n'
        )
        original=validator.re.fullmatch
        inspected=[]
        def guarded(pattern,string,*args,**kwargs):
            self.assertNotIn('OTHER_',string)
            inspected.append(string)
            return original(pattern,string,*args,**kwargs)
        with mock.patch.object(validator.re,'fullmatch',guarded):
            rows=list(validator.conllu(path,work='Que'))
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0][0]['sent_id'],'Que-1')
        self.assertEqual(rows[0][0]['text'],'rosa')
        self.assertEqual(len(rows[0][1]),1)
        self.assertEqual(rows[0][1][0][1],'rosa')
        self.assertTrue(inspected)


if __name__=='__main__':unittest.main()
