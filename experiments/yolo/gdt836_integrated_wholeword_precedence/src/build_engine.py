#!/usr/bin/env python3
"""Materialize the reviewed mandatory-W variant of byte-frozen GDT834."""
from pathlib import Path
import hashlib
E=Path(__file__).resolve().parents[1]
p=E.parent/'gdt834_role_blind_mixed_control/src/decoder.cpp'
EXPECTED='aa1ba2f0293ee35323e6c738c934e9646cd467d29f29c89b3e74dd309711d9aa'
if hashlib.sha256(p.read_bytes()).hexdigest()!=EXPECTED:raise RuntimeError('frozen GDT834 decoder changed')
# Parent bytes are also bound by experiment.json; generated source is committed.
s=p.read_text()
s=s.replace('array<int,38> key{},bestkey{};', '''array<int,38> key{},bestkey{},initialkey{};
    bool strict=false;
    int initialization_attempts=0;
    uint64_t initialization_seed=0,search_seed=0,priority_rejections=0;
    Search(const Search&)=delete;
    Search& operator=(const Search&)=delete;''')
s=s.replace('rng(seed){', 'rng(seed){\n        search_seed=seed;')
s=s.replace('    void initialize(int start) {', '''    // No language score or cache is touched while proposing initial packages.
    void generate_packages(int start) {''')
s=s.replace('        rebuild();savebest();\n    }\n    bool change(', '''    }
    bool priority_legal_direct() const {
        unordered_map<string,int> owner;
        for(int a=0;a<38;a++)if(role(key[a])==4) {
            if(!owner.emplace(output(key[a]),a).second)return false;
        }
        for(const auto& word:p.words) {
            string value;for(int a:word.atoms)value+=output(key[a]);
            auto it=owner.find(value);
            if(it!=owner.end()&&(word.atoms.size()!=1||word.atoms[0]!=it->second))return false;
        }
        return true;
    }
    // Preconditions: key and every decoded entry describe the same candidate.
    bool priority_legal_cached() const {
        unordered_map<string,int> owner;
        for(int a=0;a<38;a++)if(role(key[a])==4) {
            if(!owner.emplace(output(key[a]),a).second)return false;
        }
        for(size_t i=0;i<p.words.size();i++) {
            auto it=owner.find(decoded[i].word);
            if(it!=owner.end()&&(p.words[i].atoms.size()!=1||p.words[i].atoms[0]!=it->second))return false;
        }
        return true;
    }
    void initialize(int start,uint64_t init_seed,int maximum_attempts=1000) {
        if(maximum_attempts<1)throw runtime_error("invalid initialization cap");
        initialization_seed=init_seed;rng.seed(init_seed);
        best=-numeric_limits<double>::infinity();
        for(initialization_attempts=1;initialization_attempts<=maximum_attempts;initialization_attempts++) {
            generate_packages(start);
            if(!legal()||!priority_legal_direct())continue;
            initialkey=key;
            rng.seed(search_seed); // Paired optimization RNG ignores initialization retries.
            rebuild();savebest();return;
        }
        initialization_attempts=maximum_attempts;
        throw runtime_error("INITIALIZATION_STOP");
    }
    bool change(''')
s=s.replace('        vector<double>ev,fv;ev.reserve(es.size());fv.reserve(fs.size());', '''        // An inactive W change can invalidate an unchanged word. Scan globally,
        // after every affected word was refreshed, before any score/edge/best commit.
        if(strict&&!priority_legal_cached()) {
            priority_rejections++;
            for(auto[a,v]:oldkeys)key[a]=v;
            for(size_t j=0;j<ws.size();j++)decoded[ws[j]]=move(olds[j]);
            return false;
        }
        vector<double>ev,fv;ev.reserve(es.size());fv.reserve(fs.size());''')
s=s.replace('        key=bestkey;rebuild();if(!legal())throw runtime_error("final illegal key");', '        key=bestkey;rebuild();if(!legal()||(strict&&!priority_legal_cached()))throw runtime_error("final illegal key");')
s=s.replace('        f<<"PROPOSALS\\t"<<proposals<<"\\n";', '''        f<<"PROPOSALS\\t"<<proposals<<"\\n";
        f<<"INITIALIZATION_ATTEMPTS\\t"<<initialization_attempts<<"\\n";
        f<<"INITIALIZATION_SEED\\t"<<initialization_seed<<"\\n";
        f<<"SEARCH_SEED\\t"<<search_seed<<"\\n";
        f<<"PRIORITY_REJECTIONS\\t"<<priority_rejections<<"\\n";
        for(int a=0;a<38;a++)f<<"INITIAL\\t"<<a<<"\\t"<<(role(initialkey[a])==1?'L':role(initialkey[a])==2?'S':'W')<<"\\t"<<output(initialkey[a])<<"\\n";''')
s=s[:s.index('int main(')]+'''int main(int argc,char**argv) {
    try {
        bool scoring=argc==7&&string(argv[1])=="--score";
        if(!scoring&&argc!=10)throw runtime_error("usage: decoder MODEL PROJECTION RELAXED|STRICT SEARCH_SEED INIT_SEED START STEPS SWEEPS OUTPUT; --score MODEL PROJECTION RELAXED|STRICT KEY_TSV OUTPUT");
        string model=argv[scoring?2:1],projection=argv[scoring?3:2],mode=argv[scoring?4:3];
        if(mode!="RELAXED"&&mode!="STRICT")throw runtime_error("mode");
        Ref r(model);Problem p(projection);p.configure(true);
        Search s(r,p,"OFF",scoring?0:stoull(argv[4]));s.strict=mode=="STRICT";
        if(scoring) {
            ifstream f(argv[5]);int a;string role,value;set<int> seen;
            while(f>>a>>role>>value) {
                if(a<0||a>=38||!seen.insert(a).second)throw runtime_error("key IDs");
                if(role=="L") {if(value.size()!=1||value[0]<'a'||value[0]>'z')throw runtime_error("letter");s.key[a]=value[0]-'a';}
                else if(role=="S"||role=="W") {const auto& pool=role=="S"?p.suffixes:p.wholes;auto it=find(pool.begin(),pool.end(),value);if(it==pool.end())throw runtime_error("candidate");s.key[a]=(role=="S"?26:26+p.suffixes.size())+(it-pool.begin());}
                else throw runtime_error("key role");
            }
            if(seen.size()!=38||!s.legal()||(s.strict&&!s.priority_legal_direct()))throw runtime_error("illegal input key");
            s.initialkey=s.key;s.rebuild();s.write(argv[6]);return 0;
        }
        s.initialize(stoi(argv[6]),stoull(argv[5]),1000);
        s.optimize(stoi(argv[7]),stoi(argv[8]));s.write(argv[9]);return 0;
    }catch(const exception&e){cerr<<e.what()<<"\\n";return 1;}
}
'''
s=s.replace('// GDT834 explicit role-search variant derived from frozen GDT832.', '// GDT836 mandatory wholeword-priority extension of frozen GDT834.')
(E/'src/decoder.cpp').write_text(s)
