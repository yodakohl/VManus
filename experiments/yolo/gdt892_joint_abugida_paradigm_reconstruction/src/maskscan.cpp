#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <unordered_set>
#include <vector>
#include <omp.h>
using namespace std;
int main(int argc,char**argv){
 if(argc!=4 && argc!=5){cerr<<"usage: maskscan PATTERNS INPUT OUTPUT\n";return 2;}
 const int nominal=argc==5?stoi(argv[4]):27;
 array<unordered_set<string>,6> lex;
 ifstream p(argv[1],ios::binary);if(!p)return 3;
 for(int v=0;v<6;v++){uint32_t n=0;p.read((char*)&n,4);for(uint32_t i=0;i<n;i++){uint16_t z=0;p.read((char*)&z,2);string s(z,'\0');p.read(s.data(),z);lex[v].insert(s);}}
 if(!p)return 4;
 ifstream in(argv[2]);string alphabet;in>>alphabet;size_t nwords;in>>nwords;vector<string>words(nwords);for(auto&w:words)in>>w;
 if(!in||alphabet.size()>24)return 5;
 array<int,256> letter;letter.fill(-1);for(size_t i=0;i<alphabet.size();i++)letter[(uint8_t)alphabet[i]]=i;
 for(auto&w:words)for(auto c:w)if(letter[(uint8_t)c]<0)return 6;
 const int A=alphabet.size(),total=1<<A,CODES=A+A*A;
 vector<pair<int,int>>found;
 #pragma omp parallel num_threads(32)
 {
 vector<pair<int,int>>local;
 #pragma omp for schedule(dynamic,1024)
 for(int mask=0;mask<total;mask++){
  int singles=__builtin_popcount((unsigned)mask);if(singles+A*(A-singles)<nominal)continue;
  vector<uint8_t>used(CODES,0);int numused=0,numdoubles=0;int alive=63;
  for(auto&w:words){
   array<int,600>names;names.fill(-1);int next=0;string pat;bool good=true;
   for(size_t pos=0;pos<w.size();){
    int c=letter[(uint8_t)w[pos]],code;
    if(mask&(1<<c)){code=c;pos++;}
    else{if(pos+1>=w.size()){good=false;break;}code=A+c*A+letter[(uint8_t)w[pos+1]];pos+=2;}
    if(!used[code]){used[code]=1;if(code>=A)numdoubles++;if(++numused>nominal || singles+numdoubles>nominal){good=false;break;}}
    if(names[code]<0)names[code]=next++;
    pat.push_back(char(names[code]));
   }
   if(!good){alive=0;break;}
   for(int v=0;v<6;v++)if((alive&(1<<v))&&!lex[v].count(pat))alive&=~(1<<v);
   if(!alive)break;
  }
  if(alive)local.emplace_back(mask,alive);
 }
 #pragma omp critical
 found.insert(found.end(),local.begin(),local.end());
 }
 sort(found.begin(),found.end());ofstream out(argv[3]);out<<"mask,inherent_bits\n";for(auto[a,b]:found)out<<a<<","<<b<<"\n";
 cout<<"{\"status\":\"COMPLETE\",\"masks_examined\":"<<total<<",\"surviving_masks\":"<<found.size()<<"}\n";
}
