#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
using namespace std;
using VI=vector<int>;
struct Word {VI x; long long count;};
string csv(const VI& x){if(x.empty())return "-";string s;for(int a:x){if(!s.empty())s+=",";s+=to_string(a);}return s;}
bool subseq(const VI& c,const VI& v){size_t j=0;for(int a:v)if(j<c.size()&&a==c[j])++j;return j==c.size();}
set<VI> residuals(const VI& c,const VI& v){
 int d=int(v.size())-int(c.size());if(d<0||d>4)return {};
 // DP retains all distinct omitted strings, not multiplicities of alignments.
 vector<set<VI>> states(c.size()+1);states[0].insert(VI{});
 for(int a:v){vector<set<VI>> next(c.size()+1);for(size_t j=0;j<states.size();++j)for(const auto&r:states[j]){
  if(j<c.size()&&c[j]==a)next[j+1].insert(r);
  if(int(r.size())<d){VI z=r;z.push_back(a);next[j].insert(z);}
 }states.swap(next);}return states.back();
}
struct Engine{
 int N,A;vector<Word> train,ref;long long total=0,rtotal=0;vector<vector<int>> affected;map<VI,int> rid;map<int,vector<int>> lengths;
 unordered_map<uint64_t,long long> hist,trans;
 uint64_t base;
 uint64_t context(int a,int b,int c)const{return (uint64_t(a)*base+b)*base+c;}
 void load(string path){ifstream f(path);string tag;int n;f>>tag>>N>>A;assert(tag=="ALPHABETS"&&N>=2&&A>=2&&A<=1024);base=A+2;
  f>>tag>>n;assert(tag=="TRAIN");train.resize(n);for(auto&w:train){int k;f>>w.count>>k;w.x.resize(k);for(int&a:w.x){f>>a;assert(a>=0&&a<N);}total+=w.count;}
  f>>tag>>n;assert(tag=="REFERENCE");ref.resize(n);for(auto&w:ref){int k;f>>w.count>>k;w.x.resize(k);for(int&a:w.x){f>>a;assert(a>=0&&a<A);}rtotal+=w.count;}
  assert(f&&total>0&&rtotal>0);affected.resize(N);
  for(int i=0;i<int(train.size());++i){set<int> once(train[i].x.begin(),train[i].x.end());for(int a:once)affected[a].push_back(i);}
  for(int i=0;i<int(ref.size());++i){auto&w=ref[i];assert(!rid.count(w.x));rid[w.x]=i;lengths[int(w.x.size())].push_back(i);int a=A,b=A,c=A;
   VI out=w.x;out.push_back(A+1);for(int z:out){auto h=context(a,b,c);hist[h]+=w.count;trans[h*base+z]+=w.count;a=b;b=c;c=z;}}
 }
 VI decode(const VI&w,const VI&key,int marker)const{VI c;for(int a:w)if(a!=marker)c.push_back(key[a]);return c;}
 double charscore(int wi,const VI& key,int marker)const{
  VI x=decode(train[wi].x,key,marker);x.push_back(A+1);int a=A,b=A,c=A;double s=0;
  for(int z:x){auto h=context(a,b,c);auto hi=hist.find(h),ti=trans.find(h*base+z);double den=(hi==hist.end()?0:hi->second)+.1*(A+1);double num=(ti==trans.end()?0:ti->second)+.1;s+=log(num/den);a=b;b=c;c=z;}
  return s/x.size();
 }
 vector<VI> anneal(ofstream& out){
  vector<long long> wc(N),rc(A);for(auto&w:train)for(int a:w.x)wc[a]+=w.count;for(auto&w:ref)for(int a:w.x)rc[a]+=w.count;
  VI wr(N),rr(A);iota(wr.begin(),wr.end(),0);iota(rr.begin(),rr.end(),0);
  sort(wr.begin(),wr.end(),[&](int a,int b){return wc[a]!=wc[b]?wc[a]>wc[b]:a<b;});sort(rr.begin(),rr.end(),[&](int a,int b){return rc[a]!=rc[b]?rc[a]>rc[b]:a<b;});
  vector<VI> panel;VI active;for(int a=0;a<N;++a)if(!affected[a].empty())active.push_back(a);assert(active.size()>=2);
  for(int start=0;start<8;++start){mt19937_64 rng(116600+start);auto pick=[&](int n){return int(rng()%n);};auto uni=[&](){return (double(rng()>>11)+.5)/9007199254740992.0;};
   VI key(N);for(int i=0;i<N;++i)key[wr[i]]=rr[i%A];if(start>0)for(int j=0;j<10;++j){int a=active[pick(active.size())],b=active[pick(active.size())];swap(key[a],key[b]);}
   int marker=-1;vector<double> cached(train.size());double sum=0;for(int i=0;i<int(train.size());++i){cached[i]=charscore(i,key,marker);sum+=cached[i]*train[i].count;}
   for(int step=1;step<=20000;++step){VI old=key;int oldmark=marker;set<int> changed;int proposal=pick(100);
    if(proposal<(start<4?50:45)){int ai=pick(active.size()),bi=pick(active.size()-1);if(bi>=ai)++bi;int a=active[ai],b=active[bi];swap(key[a],key[b]);changed.insert(a);changed.insert(b);}
    else if(proposal<(start<4?100:90)){int a=active[pick(active.size())];key[a]=pick(A);changed.insert(a);}
    else{int mi=pick(active.size()+1)-1;marker=mi<0?-1:active[mi];if(marker>=0)changed.insert(marker);if(oldmark>=0)changed.insert(oldmark);}
    set<int> rows;for(int a:changed)rows.insert(affected[a].begin(),affected[a].end());vector<pair<int,double>> fresh;double delta=0;
    for(int wi:rows){double z=charscore(wi,key,marker);fresh.emplace_back(wi,z);delta+=(z-cached[wi])*train[wi].count;}
    double temp=.02*pow(.0002/.02,double(step-1)/19999.0);bool accept=delta>=0||log(uni())<delta/double(total)/temp;
    if(accept){sum+=delta;for(auto [i,z]:fresh)cached[i]=z;}else{key=old;marker=oldmark;}
    if(step%5000==0){double direct=0;for(int wi=0;wi<int(train.size());++wi)direct+=charscore(wi,key,marker)*train[wi].count;assert(abs(sum-direct)<1e-6*max(1.0,abs(direct)));sum=direct;
     out<<panel.size()<<'\t'<<start<<'\t'<<step<<'\t'<<marker<<'\t'<<setprecision(17)<<sum/total<<'\t'<<csv(key)<<'\n';panel.push_back(key);}
   }
  }return panel;
 }
 double logmass(double mass)const{return log(1e-8+(1-1e-8)*mass);}
 double exactmass(const VI& c)const{auto i=rid.find(c);return i==rid.end()?0:double(ref[i->second].count)/rtotal;}
 void evaluate(const vector<VI>& panel,ofstream& out){
  for(int pi=0;pi<int(panel.size());++pi){const auto&key=panel[pi];vector<double> literal(train.size());double ls=0;
   for(int wi=0;wi<int(train.size());++wi){literal[wi]=exactmass(decode(train[wi].x,key,-1));ls+=train[wi].count*logmass(literal[wi]);}
   out<<"L\t"<<pi<<"\t-1\t-\t"<<setprecision(17)<<ls<<'\n';
   out<<"C\t"<<pi<<"\t-1\t-\t"<<setprecision(17)<<ls<<'\n';out<<"V\t"<<pi<<"\t-1\t-\t"<<setprecision(17)<<ls<<'\n';
   for(int marker=0;marker<N;++marker){if(affected[marker].empty())continue;double vs=ls,csbase=ls;map<VI,map<int,double>> cm;cm[VI{}];
    for(int wi:affected[marker]){const auto& w=train[wi];VI carriers=decode(w.x,key,marker);double mass=0;csbase+=w.count*(logmass(0)-logmass(literal[wi]));
     if(carriers.size()>=2)for(int d=0;d<=4;++d){auto li=lengths.find(int(carriers.size())+d);if(li==lengths.end())continue;
      for(int ri:li->second){const auto&v=ref[ri];if(!subseq(carriers,v.x))continue;double weight=double(v.count)/rtotal*ldexp(1.0,-d);mass+=weight;
       auto rs=residuals(carriers,v.x);assert(!rs.empty());int k=count(w.x.begin(),w.x.end(),marker);for(const auto&r:rs){if(r.size()%k)continue;VI unit(r.begin(),r.begin()+r.size()/k);VI repeated;for(int j=0;j<k;++j)repeated.insert(repeated.end(),unit.begin(),unit.end());if(repeated==r)cm[unit][wi]+=weight;}}}
     vs+=w.count*(logmass(mass)-logmass(literal[wi]));
    }
    out<<"V\t"<<pi<<'\t'<<marker<<"\t-\t"<<setprecision(17)<<vs<<'\n';
    for(const auto& [r,words]:cm){double score=csbase;for(auto [wi,mass]:words)score+=train[wi].count*(logmass(mass)-logmass(0));out<<"C\t"<<pi<<'\t'<<marker<<'\t'<<csv(r)<<'\t'<<setprecision(17)<<score<<'\n';}
   }
   cerr<<"panel "<<pi+1<<"/32 scored\n";
  }
 }
};
void fixture(){assert(subseq({0,2},{0,1,2}));assert(!subseq({2,0},{0,1,2}));assert(residuals({0,2},{0,1,2})==set<VI>{VI{1}});assert((residuals({0,2},{3,0,1,2})==set<VI>{VI{3,1}}));assert(residuals({0,0},{0,0,0})==set<VI>{VI{0}});assert(residuals({0,2},{0,1,2,3,4,5,6}).empty());assert(residuals({0,2},{2,0}).empty());cout<<"SYNTHETIC_ALIGNMENT_PASS\n";}
int main(int argc,char**argv){if(argc==2&&string(argv[1])=="--selftest"){fixture();return 0;}assert(argc==3);Engine e;e.load(argv[1]);ofstream panel(string(argv[2])+".panel.tsv"),scores(string(argv[2])+".scores.tsv");auto keys=e.anneal(panel);e.evaluate(keys,scores);}
