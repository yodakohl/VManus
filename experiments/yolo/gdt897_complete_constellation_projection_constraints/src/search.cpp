#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <vector>
using namespace std;
using Clock=chrono::steady_clock;
struct Solver {
 int n,k,f,g; vector<uint8_t> s,t,sf,tf; vector<int> sd,td,sp,tp,map,assigned,witness;
 vector<uint32_t> initial; uint64_t nodes=0; bool timed=false; Clock::time_point deadline;
 int flip(int m) {return ((m&1)<<2)|(m&2)|((m&4)>>2);}
 int index(const vector<int>& a) {int z=0;for(int v:a)z=z*n+v;return z;}
 int idx2(int a,int b){return a*n+b;}
 int idx3(int a,int b,int c){return (a*n+b)*n+c;}
 int idx4(int a,int b,int c,int d){return ((a*n+b)*n+c)*n+d;}
 bool compatible(int a,int b){int m=s[a];if(g<0)m=flip(m);return m&t[b];}
 void make_facets(const vector<uint8_t>& m, bool source, vector<uint8_t>& facets,vector<int>& deg,vector<int>& pair) {
  int size=1;for(int i=0;i<f;i++)size*=n;facets.assign(size,0);deg.assign(n,0);pair.assign(n*n,0);
  vector<int> q;
  auto visit=[&](auto&& self,int start)->void {
   if((int)q.size()<f){for(int i=start;i<n;i++){q.push_back(i);self(self,i+1);q.pop_back();}return;}
   bool pos=true,neg=true;
   for(int j=0;j<n;j++)if(find(q.begin(),q.end(),j)==q.end()){
    q.push_back(j);int v=m[index(q)];q.pop_back();
    pos &= source ? v==4 : bool(v&4); neg &= source ? v==1 : bool(v&1);
   }
   if(!pos&&!neg)return;
   for(int i:q)deg[i]++;
   for(int i:q)for(int j:q)if(i!=j)pair[i*n+j]++;
   vector<int> p=q;do{facets[index(p)]=1;}while(next_permutation(p.begin(),p.end()));
  };visit(visit,0);
 }
 Solver(int nn,int kk,vector<uint8_t> ss,vector<uint8_t> tt):n(nn),k(kk),f(kk-1),s(move(ss)),t(move(tt)){
  make_facets(s,true,sf,sd,sp);make_facets(t,false,tf,td,tp);
  initial.assign(n,0);for(int i=0;i<n;i++)for(int j=0;j<n;j++)if(sd[i]<=td[j])initial[i]|=1u<<j;
 }
 bool allowed(int x,int y){
  for(int a:assigned)if(sp[x*n+a]>tp[y*n+map[a]])return false;
  for(int ia=0;ia<(int)assigned.size();ia++)for(int ib=ia+1;ib<(int)assigned.size();ib++){
   int a=assigned[ia],b=assigned[ib],u=map[a],v=map[b];
   if(k==3){if(!compatible(idx3(x,a,b),idx3(y,u,v)))return false;}
   else {
    if(sf[idx3(x,a,b)]&&!tf[idx3(y,u,v)])return false;
    for(int ic=ib+1;ic<(int)assigned.size();ic++){
     int c=assigned[ic],w=map[c];if(!compatible(idx4(x,a,b,c),idx4(y,u,v,w)))return false;
    }
   }
  }
  return true;
 }
 bool matching(const vector<pair<int,uint32_t>>& domains){
  vector<int> owner(n,-1);vector<uint32_t> ds;for(auto d:domains)ds.push_back(d.second);
  auto aug=[&](auto&& self,int x,uint32_t& seen)->bool{
   uint32_t d=ds[x]&~seen;while(d){int y=__builtin_ctz(d);d&=d-1;seen|=1u<<y;if(owner[y]<0||self(self,owner[y],seen)){owner[y]=x;return true;}}return false;
  };
  for(int x=0;x<(int)ds.size();x++){uint32_t seen=0;if(!aug(aug,x,seen))return false;}return true;
 }
 bool dfs(uint32_t used){
  nodes++;if((nodes&127)==1&&Clock::now()>=deadline){timed=true;return false;}
  if((int)assigned.size()==n){witness=map;return true;}
  vector<pair<int,uint32_t>> domains;int best=-1,bestsize=n+1;
  for(int x=0;x<n;x++)if(map[x]<0){
   uint32_t d=initial[x]&~used,keep=0;while(d){int y=__builtin_ctz(d);d&=d-1;if(allowed(x,y))keep|=1u<<y;}
   int count=__builtin_popcount(keep);if(!count)return false;
   domains.push_back({x,keep});if(count<bestsize||(count==bestsize&&sd[x]>sd[domains[best].first])){best=(int)domains.size()-1;bestsize=count;}
  }
  if(assigned.size()>=3&&!matching(domains))return false;
  int x=domains[best].first;uint32_t choices=domains[best].second;
  while(choices){int y=__builtin_ctz(choices);choices&=choices-1;map[x]=y;assigned.push_back(x);
   if(dfs(used|(1u<<y)))return true;
   assigned.pop_back();map[x]=-1;if(timed)return false;
  }return false;
 }
 void run(int sign,double seconds){
  g=sign;nodes=0;timed=false;assigned.clear();map.assign(n,-1);witness.clear();auto begin=Clock::now();deadline=begin+chrono::milliseconds((long long)(seconds*1000));
  bool found=dfs(0);double elapsed=chrono::duration<double>(Clock::now()-begin).count();
  cout<<"{\"g\":"<<g<<",\"status\":\""<<(found?"INVARIANT_COMPATIBLE":timed?"UNKNOWN_BUDGET":"UNSAT_INVARIANTS")<<"\",\"nodes\":"<<nodes<<",\"seconds\":"<<elapsed<<",\"witness\":[";
  for(int i=0;i<(int)witness.size();i++){if(i)cout<<',';cout<<witness[i];}cout<<"]}";
 }
};
int main(int argc,char**argv){
 uint32_t n=0,k=0;cin.read((char*)&n,4);cin.read((char*)&k,4);if(n<4||n>30||(k!=3&&k!=4))return 2;
 size_t size=1;for(unsigned i=0;i<k;i++)size*=n;vector<uint8_t>s(size),t(size);cin.read((char*)s.data(),size);cin.read((char*)t.data(),size);if(!cin)return 3;
 double cap=argc>1?stod(argv[1]):120;Solver solver(n,k,move(s),move(t));
 cout<<"{\"source_facets\":"<<accumulate(solver.sd.begin(),solver.sd.end(),0)/(int)(k-1)<<",\"possible_target_facets\":"<<accumulate(solver.td.begin(),solver.td.end(),0)/(int)(k-1)<<",\"orientations\":[";
 solver.run(1,cap);cout<<',';solver.run(-1,cap);cout<<"]}\n";
}
