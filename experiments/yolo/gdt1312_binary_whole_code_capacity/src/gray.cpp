#include <algorithm>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <utility>
#include <vector>
using namespace std;
struct Word {uint32_t weight,code;vector<uint32_t> flips;};
struct Panel {vector<Word> words;vector<vector<pair<int,uint32_t>>> affected;vector<uint32_t> mass;uint32_t occupied=0;vector<uint16_t> counts;};
int main(int argc,char**argv){
 assert(argc==3);ifstream in(argv[1]);ofstream out(argv[2],ios::binary);assert(in&&out);
 int A,R,M;in>>A>>R>>M;assert(A>=2&&A<=22&&R>=1&&M>=1&&M<=20);int states=1<<(A-1);vector<int> order(A-1);for(int&u:order)in>>u;
 vector<Panel> panels(R);
 for(auto&p:panels){int W;in>>W;assert(W>0&&W<65536);p.affected.resize(A);p.mass.assign(1u<<(M+1),0);p.counts.resize(states);
  for(int w=0;w<W;++w){uint32_t weight;int n;in>>weight>>n;assert(weight>0&&n>0&&n<=M);Word q{weight,1u<<n,vector<uint32_t>(A,0)};for(int j=0;j<n;++j){int u;in>>u;assert(u>=0&&u<A);q.flips[u]|=1u<<(n-1-j);}p.words.push_back(q);if(p.mass[q.code]==0)++p.occupied;p.mass[q.code]+=weight;
   for(int u=1;u<A;++u)if(q.flips[u])p.affected[u].push_back({w,q.flips[u]});
  }p.counts[0]=p.occupied;
 }
 uint32_t mask=0;
 for(uint32_t step=1;step<(uint32_t)states;++step){int u=order[__builtin_ctz(step)];mask^=1u<<u;
  for(auto&p:panels){for(auto [wi,flip]:p.affected[u]){auto&w=p.words[wi];uint32_t old=w.code,neu=old^flip;assert(p.mass[old]>=w.weight);p.mass[old]-=w.weight;if(p.mass[old]==0)--p.occupied;if(p.mass[neu]==0)++p.occupied;p.mass[neu]+=w.weight;w.code=neu;}assert(p.occupied<65536);p.counts[mask>>1]=(uint16_t)p.occupied;}
 }
 for(auto&p:panels)for(uint16_t v:p.counts){out.put((char)(v&255));out.put((char)(v>>8));}
 cout<<"COUNTED "<<states-1<<" partitions in "<<R<<" readers\n";
}
