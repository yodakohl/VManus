#include <algorithm>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>
#include <omp.h>
using namespace std;
struct Record {string id;vector<int> words,previous;};
vector<Record> read_records(const char *path){
 ifstream f(path);size_t n;if(!(f>>n))throw runtime_error("record header");
 vector<Record> records(n);
 for(auto&r:records){size_t size;if(!(f>>r.id>>size))throw runtime_error("record length");
  r.words.resize(size);r.previous.resize(size);unordered_map<int,int>last;
  for(size_t i=0;i<size;i++){
   if(!(f>>r.words[i])||r.words[i]<0)throw runtime_error("word id");
   auto it=last.find(r.words[i]);r.previous[i]=it==last.end()?0:int(i)-it->second;last[r.words[i]]=i;
  }
 }
 string extra;if(f>>extra)throw runtime_error("extra input");return records;
}
int main(int argc,char**argv){
 if(argc!=4){cerr<<"usage: match TARGET SOURCE OUTPUT\n";return 2;}
 try{
 auto targets=read_records(argv[1]),sources=read_records(argv[2]);
 vector<tuple<int,int,int,int>>matches;
 #pragma omp parallel num_threads(32)
 {
  vector<tuple<int,int,int,int>>local;
  #pragma omp for schedule(dynamic,1)
  for(size_t t=0;t<targets.size();t++){
   auto&target=targets[t];int length=target.words.size();if(!length)continue;
   vector<int>order(length);iota(order.begin(),order.end(),0);
   // Test necessary repeated-word constraints first; every position is tested.
   stable_sort(order.begin(),order.end(),[&](int a,int b){
    if(bool(target.previous[a])!=bool(target.previous[b]))return target.previous[a]>0;
    return a>b;
   });
   for(size_t s=0;s<sources.size();s++){
    auto&source=sources[s];int n=source.words.size();
    for(int start=0;start+length<=n;start++){
     bool good=true;
     for(int k:order){int wanted=target.previous[k],seen=source.previous[start+k];
      if(wanted ? seen!=wanted : (seen && seen<=k)){good=false;break;}
     }
     if(good)local.emplace_back(t,s,start,length);
    }
   }
  }
  #pragma omp critical
  matches.insert(matches.end(),local.begin(),local.end());
 }
 sort(matches.begin(),matches.end());ofstream out(argv[3]);
 if(!out)throw runtime_error("output unavailable");
 out<<"target_index,source_index,start,length\n";
 for(auto[t,s,start,n]:matches)out<<t<<','<<s<<','<<start<<','<<n<<'\n';
 cout<<"{\"status\":\"COMPLETE\",\"target_paragraphs\":"<<targets.size()<<",\"source_units\":"<<sources.size()<<",\"matches\":"<<matches.size()<<"}\n";
 }catch(const exception&e){cerr<<e.what()<<'\n';return 3;}
}
