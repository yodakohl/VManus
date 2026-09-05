#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
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
        string w;for(int a:p.words[i].atoms){if(a<26)w+=char('a'+key[a]);else if(a<30)w+=p.suffixes.at(key[a]);else w+=p.wholes.at(key[a]);}
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
    void initialize(int start) {
        vector<int> source(26),target(26);iota(source.begin(),source.end(),0);iota(target.begin(),target.end(),0);
        sort(source.begin(),source.end(),[&](int a,int b){return p.atomfreq[a]==p.atomfreq[b]?a<b:p.atomfreq[a]>p.atomfreq[b];});
        sort(target.begin(),target.end(),[&](int a,int b){return ref.letterfreq[a]==ref.letterfreq[b]?a<b:ref.letterfreq[a]>ref.letterfreq[b];});
        for(int i=0;i<26;i++)key[source[i]]=target[i];
        if(start>0)for(int i=0;i<4+2*start;i++)swap(key[rng()%26],key[rng()%26]);
        vector<int>s(p.suffixes.size());iota(s.begin(),s.end(),0);shuffle(s.begin(),s.end(),rng);
        for(int i=0;i<4;i++)key[26+i]=s[i];
        vector<int>w(8);iota(w.begin(),w.end(),30);
        sort(w.begin(),w.end(),[&](int a,int b){return p.atomfreq[a]==p.atomfreq[b]?a<b:p.atomfreq[a]>p.atomfreq[b];});
        for(int i=0;i<8;i++)key[w[i]]=i;
        if(start>0)for(int i=0;i<8;i++)swap(key[30+rng()%8],key[30+rng()%8]);
        rebuild();savebest();
    }
    bool change(const vector<pair<int,int>>& changes,double temperature,bool forced=false) {
        proposals++;stamp++;vector<pair<int,int>> oldkeys;vector<int> ws,es,fs;
        for(auto[a,v]:changes){if(key[a]==v)continue;oldkeys.push_back({a,key[a]});key[a]=v;
            for(int i:p.affected[a])if(wordmark[i]!=stamp){wordmark[i]=stamp;ws.push_back(i);}}
        if(oldkeys.empty())return false;
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
    void replacement(int atom,int value,double t) {
        int begin=atom<30?26:30,end=atom<30?30:38;
        int other=-1;for(int i=begin;i<end;i++)if(key[i]==value)other=i;
        if(other==atom)return;
        if(other>=0)change({{atom,value},{other,key[atom]}},t);
        else change({{atom,value}},t);
    }
    void optimize(int steps,int sweeps) {
        for(int t=0;t<steps;t++) {
            double temp=80.0*pow(.05/80.0,double(t)/max(1,steps-1));int kind=rng()%100;
            if(kind<72){int a=rng()%26,b=rng()%26;change({{a,key[b]},{b,key[a]}},temp);}
            else if(kind<86)replacement(26+rng()%4,rng()%p.suffixes.size(),temp);
            else replacement(30+rng()%8,rng()%p.wholes.size(),temp);
        }
        key=bestkey;rebuild();
        for(int pass=0;pass<sweeps;pass++) {
            for(int a=0;a<26;a++)for(int b=a+1;b<26;b++)change({{a,key[b]},{b,key[a]}},0);
            for(int a=26;a<30;a++)for(int v=0;v<int(p.suffixes.size());v++)replacement(a,v,0);
            for(int a=30;a<38;a++)for(int v=0;v<int(p.wholes.size());v++)replacement(a,v,0);
        }
        key=bestkey;rebuild();
    }
    void write(const string& path)const {
        ofstream f(path);if(!f)throw runtime_error("cannot write result");f<<setprecision(17);
        double family=accumulate(familyvalues.begin(),familyvalues.end(),0.0);
        f<<"SCORE\t"<<score<<"\t"<<score-family<<"\t"<<family<<"\n";
        f<<"PROPOSALS\t"<<proposals<<"\n";
        for(int a=0;a<38;a++){
            char type=a<26?'L':a<30?'S':'W';int number=a<26?a:a<30?a-26:a-30;
            string out=a<26?string(1,char('a'+key[a])):a<30?p.suffixes[key[a]]:p.wholes[key[a]];
            f<<type<<setw(2)<<setfill('0')<<number<<setfill(' ')<<"\t"<<out<<"\n";
        }
    }
};

int main(int argc,char**argv) {
    try {
        if(argc==7&&string(argv[1])=="--score") {
            string arm=argv[4];if(arm!="FULL"&&arm!="CUT"&&arm!="OFF"&&arm!="REWIRED")throw runtime_error("arm");
            Ref r(argv[2]);Problem p(argv[3]);Search s(r,p,argv[4],0);
            ifstream f(argv[5]);string name,value;set<string> seen;
            while(f>>name>>value){
                if(name.size()!=3||!seen.insert(name).second)throw runtime_error("key input schema");
                int off=name[0]=='L'?0:name[0]=='S'?26:name[0]=='W'?30:-100;
                int number=stoi(name.substr(1)),limit=off==0?26:off==26?4:off==30?8:0;
                if(number<0||number>=limit)throw runtime_error("key typed input range");
                int a=off+number;
                if(off==0){if(value.size()!=1||value[0]<'a'||value[0]>'z')throw runtime_error("literal value");s.key[a]=value[0]-'a';}
                else{const auto& pool=off==26?p.suffixes:p.wholes;auto it=find(pool.begin(),pool.end(),value);if(it==pool.end())throw runtime_error("key value outside candidate pool");s.key[a]=it-pool.begin();}
            }
            if(seen.size()!=38)throw runtime_error("key completeness");
            for(auto bounds:vector<pair<int,int>>{{0,26},{26,30},{30,38}}){set<int> values;for(int a=bounds.first;a<bounds.second;a++)values.insert(s.key[a]);if(int(values.size())!=bounds.second-bounds.first)throw runtime_error("key injectivity");}
            s.rebuild();s.write(argv[6]);return 0;
        }
        if(argc!=9)throw runtime_error("usage: decoder MODEL TRAIN_PROJECTION ARM SEED START STEPS SWEEPS OUTPUT");
        string arm=argv[3];if(arm!="FULL"&&arm!="CUT"&&arm!="OFF"&&arm!="REWIRED")throw runtime_error("arm");
        Ref r(argv[1]);Problem p(argv[2]);Search s(r,p,arm,stoull(argv[4]));
        s.initialize(stoi(argv[5]));s.optimize(stoi(argv[6]),stoi(argv[7]));s.write(argv[8]);
        return 0;
    }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}
}
