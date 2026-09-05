#!/usr/bin/env python3
"""Produce the explicit role-search variant from frozen GDT832 source."""
from pathlib import Path
import hashlib
E=Path(__file__).resolve().parents[1]
p=E.parent/'gdt832_joint_family_context_control/src/decoder.cpp'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='5e62c8edb2798a9fc3cc68bbb58da1b0cc287caf26838493a39a0f8389ca7750'
s=p.read_text()
s=s.replace('array<double,38> atomfreq{};', '''array<double,38> atomfreq{};
    array<int,38> domain{};
    void configure(bool blind) {
        for(int a=0;a<38;a++)domain[a]=blind?7:(a<26?1:a<30?2:4);
        for(const auto& w:words)for(int j=0;j<int(w.atoms.size());j++) {
            int allowed=1;
            if(w.atoms.size()==1)allowed|=4;
            if(w.atoms.size()>=4&&j==int(w.atoms.size())-1)allowed|=2;
            domain[w.atoms[j]]&=allowed;
        }
        for(int d:domain)if(!d)throw runtime_error("role violates discovery positions");
    }''')
s=s.replace('string w;for(int a:p.words[i].atoms){if(a<26)w+=char(\'a\'+key[a]);else if(a<30)w+=p.suffixes.at(key[a]);else w+=p.wholes.at(key[a]);}', '''string w;for(int a:p.words[i].atoms)w+=output(key[a]);''')
a=s.index('    void initialize(int start) {')
b=s.index('    bool change(',a)
s=s[:a]+'''    int role(int value)const {return value<26?1:value<26+int(p.suffixes.size())?2:4;}
    string output(int value)const {
        if(value<0||value>=26+int(p.suffixes.size()+p.wholes.size()))throw runtime_error("output value range");
        if(value<26)return string(1,char('a'+value));
        if(value<26+int(p.suffixes.size()))return p.suffixes.at(value-26);
        return p.wholes.at(value-26-p.suffixes.size());
    }
    bool legal()const {
        array<int,8> counts{};set<int> values;
        for(int a=0;a<38;a++) {
            if(key[a]<0||key[a]>=26+int(p.suffixes.size()+p.wholes.size()))return false;
            int r=role(key[a]);if(!(p.domain[a]&r)||!values.insert(key[a]).second)return false;
            counts[r]++;
        }
        return counts[1]==26&&counts[2]==4&&counts[4]==8;
    }
    void initialize(int start) {
        // Random feasible bipartite matching: anonymous atoms to nominal role slots.
        vector<int> slots(38),owners(38,-1),order(38);iota(order.begin(),order.end(),0);
        for(int j=0;j<38;j++)slots[j]=j<26?1:j<30?2:4;
        vector<vector<int>> edges(38);
        for(int a=0;a<38;a++) {for(int j=0;j<38;j++)if(p.domain[a]&slots[j])edges[a].push_back(j);shuffle(edges[a].begin(),edges[a].end(),rng);}
        shuffle(order.begin(),order.end(),rng);
        function<bool(int,vector<bool>&)> augment=[&](int a,vector<bool>& seen) {
            for(int j:edges[a])if(!seen[j]) {seen[j]=true;if(owners[j]<0||augment(owners[j],seen)){owners[j]=a;return true;}}
            return false;
        };
        for(int a:order){vector<bool> seen(38);if(!augment(a,seen))throw runtime_error("infeasible role capacities");}
        vector<int> L,S,W;
        for(int j=0;j<38;j++)(slots[j]==1?L:slots[j]==2?S:W).push_back(owners[j]);
        auto byfreq=[&](int a,int b){return p.atomfreq[a]==p.atomfreq[b]?a<b:p.atomfreq[a]>p.atomfreq[b];};
        sort(L.begin(),L.end(),byfreq);vector<int> target(26);iota(target.begin(),target.end(),0);
        sort(target.begin(),target.end(),[&](int a,int b){return ref.letterfreq[a]==ref.letterfreq[b]?a<b:ref.letterfreq[a]>ref.letterfreq[b];});
        for(int j=0;j<26;j++)key[L[j]]=target[j];
        if(start>0)for(int j=0;j<4+2*start;j++)swap(key[L[rng()%26]],key[L[rng()%26]]);
        vector<int> sc(p.suffixes.size());iota(sc.begin(),sc.end(),26);shuffle(sc.begin(),sc.end(),rng);
        sort(S.begin(),S.end());for(int j=0;j<4;j++)key[S[j]]=sc[j];
        sort(W.begin(),W.end(),byfreq);for(int j=0;j<8;j++)key[W[j]]=26+p.suffixes.size()+j;
        if(start>0)for(int j=0;j<8;j++)swap(key[W[rng()%8]],key[W[rng()%8]]);
        if(!legal())throw runtime_error("illegal initialized key");
        rebuild();savebest();
    }
''' +s[b:]
s=s.replace('        if(oldkeys.empty())return false;', '''        if(oldkeys.empty())return false;
        if(!legal()){for(auto[a,v]:oldkeys)key[a]=v;return false;}''')
a=s.index('    void replacement(int atom,')
b=s.index('\n};\n\nint main(',a)
s=s[:a]+'''    vector<int> members(int r)const {vector<int> out;for(int a=0;a<38;a++)if(role(key[a])==r)out.push_back(a);return out;}
    void replacement(int atom,int value,double t) {
        if(role(value)!=role(key[atom]))throw runtime_error("replacement role mismatch");
        int other=-1;for(int i=0;i<38;i++)if(key[i]==value)other=i;
        if(other==atom)return;
        if(other>=0)change({{atom,value},{other,key[atom]}},t);
        else change({{atom,value}},t);
    }
    void optimize(int steps,int sweeps) {
        for(int t=0;t<steps;t++) {
            double temp=80.0*pow(.05/80.0,double(t)/max(1,steps-1));int kind=rng()%100;
            if(kind<20){int a=rng()%38,b=rng()%38;if(a!=b&&role(key[a])!=role(key[b]))change({{a,key[b]},{b,key[a]}},temp);}
            else {
                int basekind=rng()%100;
                if(basekind<72){auto m=members(1);int a=m[rng()%26],b=m[rng()%26];if(a!=b)change({{a,key[b]},{b,key[a]}},temp);}
                else if(basekind<86){auto m=members(2);replacement(m[rng()%4],26+rng()%p.suffixes.size(),temp);}
                else {auto m=members(4);replacement(m[rng()%8],26+p.suffixes.size()+rng()%p.wholes.size(),temp);}
            }
        }
        key=bestkey;rebuild();
        for(int pass=0;pass<sweeps;pass++) {
            for(int a=0;a<38;a++)for(int b=a+1;b<38;b++)change({{a,key[b]},{b,key[a]}},0);
            for(int a=0;a<38;a++)if(role(key[a])==2)for(int v=26;v<26+int(p.suffixes.size());v++)replacement(a,v,0);
            for(int a=0;a<38;a++)if(role(key[a])==4)for(int v=26+p.suffixes.size();v<26+int(p.suffixes.size()+p.wholes.size());v++)replacement(a,v,0);
        }
        key=bestkey;rebuild();if(!legal())throw runtime_error("final illegal key");
    }
    void write(const string& path)const {
        ofstream f(path);if(!f)throw runtime_error("cannot write result");f<<setprecision(17);
        f<<"SCORE\\t"<<score<<"\\t"<<score<<"\\t0\\n";
        f<<"PROPOSALS\\t"<<proposals<<"\\n";
        for(int a=0;a<38;a++)f<<a<<"\\t"<<(role(key[a])==1?'L':role(key[a])==2?'S':'W')<<"\\t"<<output(key[a])<<"\\n";
    }
''' +s[b:]
a=s.index('int main(')
s=s[:a]+'''int main(int argc,char**argv) {
    try {
        bool scoring=argc==7&&string(argv[1])=="--score";
        if(!scoring&&argc!=9)throw runtime_error("usage: decoder MODEL PROJECTION BLIND|TYPED SEED START STEPS SWEEPS OUTPUT; --score MODEL PROJECTION BLIND|TYPED KEY_TSV OUTPUT");
        string model=argv[scoring?2:1],projection=argv[scoring?3:2],mode=argv[scoring?4:3];
        if(mode!="BLIND"&&mode!="TYPED")throw runtime_error("mode");
        Ref r(model);Problem p(projection);p.configure(mode=="BLIND");
        Search s(r,p,"OFF",scoring?0:stoull(argv[4]));
        if(scoring) {
            ifstream f(argv[5]);int a;string role,value;set<int> seen;
            while(f>>a>>role>>value) {
                if(a<0||a>=38||!seen.insert(a).second)throw runtime_error("key IDs");
                if(role=="L") {if(value.size()!=1||value[0]<'a'||value[0]>'z')throw runtime_error("letter");s.key[a]=value[0]-'a';}
                else if(role=="S"||role=="W") {const auto& pool=role=="S"?p.suffixes:p.wholes;auto it=find(pool.begin(),pool.end(),value);if(it==pool.end())throw runtime_error("candidate");s.key[a]=(role=="S"?26:26+p.suffixes.size())+(it-pool.begin());}
                else throw runtime_error("key role");
            }
            if(seen.size()!=38||!s.legal())throw runtime_error("illegal input key");s.rebuild();s.write(argv[6]);return 0;
        }
        s.initialize(stoi(argv[5]));s.optimize(stoi(argv[6]),stoi(argv[7]));s.write(argv[8]);return 0;
    }catch(const exception&e){cerr<<e.what()<<"\\n";return 1;}
}
'''
s=s.replace('#include <fstream>', '#include <fstream>\n#include <functional>')
s=s.replace('// Train-only executable.', '// GDT834 explicit role-search variant derived from frozen GDT832.\n// Train-only executable.')
(E/'src/decoder.cpp').write_text(s)
