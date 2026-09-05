#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

// GDT834 explicit role-search variant derived from frozen GDT832.
// Train-only executable. It has no plaintext/key/held reader. Input is a
// reference model and a ciphertext type/transition projection from run.py.
using namespace std;

vector<string> fields(const string& s, char sep='\t') {
    vector<string> out; string t; stringstream in(s);
    while (getline(in,t,sep)) out.push_back(t);
    return out;
}
uint64_t paircode(int a,int b) { return (uint64_t(uint32_t(a))<<32)|uint32_t(b); }
double logadd(double a,double b) {
    if (a<b) swap(a,b);
    if (!isfinite(a)) return a;
    return a+log1p(exp(b-a));
}

struct Ref {
    vector<string> words;
    vector<double> count,outcount,distinct;
    vector<vector<int>> real,rewired;
    unordered_map<string,int> ids;
    unordered_map<uint64_t,double> bigrams;
    vector<float> chars;
    array<double,26> letterfreq{};
    double N=0;

    void loadfamilies(const string& path,vector<vector<int>>& dest) {
        dest.resize(words.size()); ifstream f(path); string s;
        if (!f) throw runtime_error("missing family table"); getline(f,s);
        while (getline(f,s)) {
            auto v=fields(s); if (v.empty()) continue;
            int id=stoi(v[0]); if (id<0||id>=int(words.size())) throw runtime_error("family ID");
            if (v.size()>1&&!v[1].empty()) for (auto x:fields(v[1],',')) dest[id].push_back(stoi(x));
            sort(dest[id].begin(),dest[id].end());
        }
    }
    explicit Ref(const string& path) {
        ifstream f(path+"/vocab.tsv"); string s;
        if (!f) throw runtime_error("missing reference vocab"); getline(f,s);
        while (getline(f,s)) {
            auto v=fields(s); if (v.size()!=5) throw runtime_error("vocab schema");
            int i=stoi(v[0]); if (i!=int(words.size())) throw runtime_error("vocab order");
            words.push_back(v[1]); ids[v[1]]=i;
            count.push_back(stod(v[2])); outcount.push_back(stod(v[3])); distinct.push_back(stod(v[4]));
            N+=count.back();
            for(char c:v[1]) letterfreq.at(c-'a')+=count.back();
        }
        ifstream g(path+"/bigrams.tsv"); if (!g) throw runtime_error("missing bigrams"); getline(g,s);
        while(getline(g,s)) {
            auto v=fields(s); if(v.size()!=3) throw runtime_error("bigram schema");
            bigrams[paircode(stoi(v[0]),stoi(v[1]))]=stod(v[2]);
        }
        const size_t n=28*28*28*27;
        chars.resize(n); ifstream h(path+"/char_logp.bin",ios::binary);
        if(!h.read(reinterpret_cast<char*>(chars.data()),n*sizeof(float))) throw runtime_error("char table length");
        if(h.peek()!=EOF) throw runtime_error("char table trailing bytes");
        loadfamilies(path+"/family_real.tsv",real);
        loadfamilies(path+"/family_rewired.tsv",rewired);
        if(N<=0) throw runtime_error("empty reference");
    }
    int wordid(const string& w) const { auto it=ids.find(w); return it==ids.end()?-1:it->second; }
    double charlog(const string& w) const {
        int a=27,b=27,c=27; double val=0;
        for(size_t i=0;i<=w.size();i++) {
            int x=i==w.size()?26:w[i]-'a';
            if(x<0||x>26||(i<w.size()&&x==26)) throw runtime_error("nonalphabetic output");
            val+=chars[((a*28+b)*28+c)*27+x]; a=b;b=c;c=x;
        }
        return val;
    }
    double unigram(const string& w,int id) const {
        double back=log(.03)+charlog(w);
        return id<0?back:logadd(log(.97*count[id]/N),back);
    }
    double conditional(int prev,int next,double uni) const {
        if(prev<0||outcount[prev]==0) return uni;
        double back=log(.5*distinct[prev]/outcount[prev])+uni;
        if(next<0) return back;
        auto it=bigrams.find(paircode(prev,next));
        return it==bigrams.end()?back:logadd(log((it->second-.5)/outcount[prev]),back);
    }
    bool related(int u,int v,bool shuffled) const {
        if(u<0||v<0||u==v) return false;
        const auto& rows=shuffled?rewired:real;
        const auto& a=rows[u]; const auto& b=rows[v]; size_t i=0,j=0;
        while(i<a.size()&&j<b.size()) { if(a[i]==b[j])return true; if(a[i]<b[j])i++;else j++; }
        return false;
    }
};

struct Word { vector<int> atoms; double freq; bool W; };
struct Edge { int u,v; double weight; };
struct Problem {
    vector<Word> words;
    vector<Edge> transitions,families;
    array<vector<int>,38> affected;
    array<double,38> atomfreq{};
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
    }
    vector<vector<int>> transition_incidence,family_incidence;
    vector<string> suffixes,wholes;
    explicit Problem(const string& path) {
        ifstream f(path); if(!f)throw runtime_error("missing train projection");
        string tag; int n;
        f>>tag>>n; if(tag!="SUFFIX")throw runtime_error("suffix header");
        for(int i=0;i<n;i++){string s;f>>s;suffixes.push_back(s);}
        f>>tag>>n; if(tag!="WHOLE")throw runtime_error("whole header");
        for(int i=0;i<n;i++){string s;f>>s;wholes.push_back(s);}
        if(suffixes.size()<4||wholes.size()<8)throw runtime_error("candidate pool capacity");
        f>>tag>>n; if(tag!="WORDS")throw runtime_error("words header");
        for(int i=0;i<n;i++) {
            int m;double freq;f>>freq>>m; Word w;w.freq=freq;set<int> seen;
            for(int j=0;j<m;j++){int a;f>>a;if(a<0||a>=38)throw runtime_error("atom range");w.atoms.push_back(a);seen.insert(a);atomfreq[a]+=freq;}
            w.W=m==1&&w.atoms[0]>=30;
            for(int a:seen)affected[a].push_back(i);
            words.push_back(w);
        }
        transition_incidence.resize(n);family_incidence.resize(n);
        f>>tag>>n;if(tag!="TRANSITIONS")throw runtime_error("transitions header");
        for(int i=0;i<n;i++){Edge e;f>>e.u>>e.v>>e.weight;transitions.push_back(e);transition_incidence.at(e.u).push_back(i);if(e.v!=e.u)transition_incidence.at(e.v).push_back(i);}
        f>>tag>>n;if(tag!="FAMILIES")throw runtime_error("families header");
        for(int i=0;i<n;i++){Edge e;f>>e.u>>e.v>>e.weight;families.push_back(e);family_incidence.at(e.u).push_back(i);family_incidence.at(e.v).push_back(i);}
        if(!f)throw runtime_error("incomplete train projection");
    }
};

struct Decoded { string word;int id;double uni; };
struct Search {
    const Ref& ref;const Problem& p;string arm;
    array<int,38> key{},bestkey{};
    vector<Decoded> decoded;
    vector<double> edgevalues,familyvalues;
    vector<int> wordmark,edgemark,fammark;
    int stamp=0; double score=0,best=-numeric_limits<double>::infinity();
    mt19937_64 rng;uint64_t proposals=0;
    Search(const Ref& r,const Problem& q,const string& a,uint64_t seed):ref(r),p(q),arm(a),rng(seed){
        decoded.resize(p.words.size());edgevalues.resize(p.transitions.size());familyvalues.resize(p.families.size());
        wordmark.resize(p.words.size());edgemark.resize(p.transitions.size());fammark.resize(p.families.size());
    }
    Decoded decode(int i)const {
        string w;for(int a:p.words[i].atoms)w+=output(key[a]);
        int id=ref.wordid(w);return{w,id,ref.unigram(w,id)};
    }
    double edgeval(int i)const {
        const auto&e=p.transitions[i];
        if(arm=="CUT"&&(p.words[e.u].W||p.words[e.v].W))return 0;
        return e.weight*(ref.conditional(decoded[e.u].id,decoded[e.v].id,decoded[e.v].uni)-decoded[e.v].uni);
    }
    double famval(int i)const {
        if(arm=="OFF")return 0;
        const auto&e=p.families[i];
        return 8.0*e.weight*ref.related(decoded[e.u].id,decoded[e.v].id,arm=="REWIRED");
    }
    void rebuild() {
        score=0;
        for(int i=0;i<int(decoded.size());i++){decoded[i]=decode(i);score+=p.words[i].freq*decoded[i].uni;}
        for(int i=0;i<int(edgevalues.size());i++){edgevalues[i]=edgeval(i);score+=edgevalues[i];}
        for(int i=0;i<int(familyvalues.size());i++){familyvalues[i]=famval(i);score+=familyvalues[i];}
    }
    void savebest(){if(score>best+1e-9){best=score;bestkey=key;}}
    int role(int value)const {return value<26?1:value<26+int(p.suffixes.size())?2:4;}
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
    bool change(const vector<pair<int,int>>& changes,double temperature,bool forced=false) {
        proposals++;stamp++;vector<pair<int,int>> oldkeys;vector<int> ws,es,fs;
        for(auto[a,v]:changes){if(key[a]==v)continue;oldkeys.push_back({a,key[a]});key[a]=v;
            for(int i:p.affected[a])if(wordmark[i]!=stamp){wordmark[i]=stamp;ws.push_back(i);}}
        if(oldkeys.empty())return false;
        if(!legal()){for(auto[a,v]:oldkeys)key[a]=v;return false;}
        vector<Decoded> olds;olds.reserve(ws.size());double delta=0;
        for(int i:ws){olds.push_back(decoded[i]);auto d=decode(i);delta+=p.words[i].freq*(d.uni-decoded[i].uni);decoded[i]=move(d);
            for(int e:p.transition_incidence[i])if(edgemark[e]!=stamp){edgemark[e]=stamp;es.push_back(e);}
            for(int e:p.family_incidence[i])if(fammark[e]!=stamp){fammark[e]=stamp;fs.push_back(e);}}
        vector<double>ev,fv;ev.reserve(es.size());fv.reserve(fs.size());
        for(int e:es){double v=edgeval(e);delta+=v-edgevalues[e];ev.push_back(v);}
        for(int e:fs){double v=famval(e);delta+=v-familyvalues[e];fv.push_back(v);}
        double u=generate_canonical<double,53>(rng);
        bool accept=forced||delta>1e-10||(temperature>0&&log(max(u,1e-300))<delta/temperature);
        if(accept){score+=delta;for(size_t j=0;j<es.size();j++)edgevalues[es[j]]=ev[j];for(size_t j=0;j<fs.size();j++)familyvalues[fs[j]]=fv[j];savebest();}
        else{for(auto[a,v]:oldkeys)key[a]=v;for(size_t j=0;j<ws.size();j++)decoded[ws[j]]=move(olds[j]);}
        #ifdef GDT832_CHECK_DELTAS
        double incremental=score;rebuild();
        if(abs(incremental-score)>1e-6)throw runtime_error("incremental cache mismatch");
        #endif
        return accept;
    }
    vector<int> members(int r)const {vector<int> out;for(int a=0;a<38;a++)if(role(key[a])==r)out.push_back(a);return out;}
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
        f<<"SCORE\t"<<score<<"\t"<<score<<"\t0\n";
        f<<"PROPOSALS\t"<<proposals<<"\n";
        for(int a=0;a<38;a++)f<<a<<"\t"<<(role(key[a])==1?'L':role(key[a])==2?'S':'W')<<"\t"<<output(key[a])<<"\n";
    }

};

int main(int argc,char**argv) {
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
    }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}
}
