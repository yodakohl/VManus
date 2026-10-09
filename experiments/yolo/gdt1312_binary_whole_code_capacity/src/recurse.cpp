// Independent recursive traversal: type multiplicity, explicit roll-back, integer source masks.
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <utility>
#include <vector>
using namespace std;
struct State {vector<uint32_t> values;vector<vector<pair<int,uint32_t>>> hits;vector<int> howmany;int distinct=0;vector<uint16_t> expected;};
int main(int argc,char**argv){assert(argc==3);ifstream input(argv[1]),saved(argv[2],ios::binary);assert(input&&saved);int alphabet,readers,longest;input>>alphabet>>readers>>longest;assert(alphabet>=2&&alphabet<=22&&longest<=20);int size=1<<(alphabet-1);vector<int> bits(alphabet-1);for(int&i:bits)input>>i;reverse(bits.begin(),bits.end());vector<State> states(readers);
 for(auto&s:states){int types;input>>types;s.hits.resize(alphabet);s.howmany.assign(1<<(longest+1),0);for(int t=0;t<types;++t){int ignored_weight,n;input>>ignored_weight>>n;vector<int>w(n);for(int&x:w)input>>x;uint32_t encoded=1u<<n;s.values.push_back(encoded);if(s.howmany[encoded]++==0)++s.distinct;for(int a=1;a<alphabet;++a){uint32_t delta=0;for(int j=0;j<n;++j)if(w[j]==a)delta+=1u<<(n-j-1);if(delta)s.hits[a].push_back({t,delta});}}
  s.expected.resize(size);for(auto&v:s.expected){int lo=saved.get(),hi=saved.get();assert(lo>=0&&hi>=0);v=(uint16_t)(lo+256*hi);}
 }
 assert(saved.get()==EOF);uint64_t checked=0;
 auto change=[&](int unit){for(auto&s:states)for(auto pair:s.hits[unit]){int i=pair.first;uint32_t before=s.values[i],after=before^pair.second;if(--s.howmany[before]==0)--s.distinct;if(s.howmany[after]++==0)++s.distinct;s.values[i]=after;}};
 function<void(int,uint32_t)> visit=[&](int depth,uint32_t original_mask){if(depth==(int)bits.size()){for(auto&s:states){if(s.distinct!=s.expected[original_mask>>1]){cerr<<"Mismatch "<<original_mask<<"\n";abort();}}++checked;return;}int unit=bits[depth];visit(depth+1,original_mask);change(unit);visit(depth+1,original_mask|(1u<<unit));change(unit);};visit(0,0);assert(checked==(uint64_t)size);cout<<"VERIFIED "<<checked<<" assignments including zero, "<<checked*readers<<" reader counts\n";
}
