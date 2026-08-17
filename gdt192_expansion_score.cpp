#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

namespace {
constexpr int CODE_COUNT=26+26*26;
inline void parts(int source,const int32_t* map,int& first,int& second,bool& two){
 if(source==26){first=second=27;two=false;return;}
 if(source==25){first=second=26;two=false;return;}
 const int code=map[source];two=code>=26;
 if(two){first=(code-26)/26;second=(code-26)%26;}else first=second=code;
}
inline double catbits(const std::vector<int64_t>& counts){
 int64_t total=0;for(auto x:counts)total+=x;if(!total)return 0.;
 const int k=counts.size();double lp=std::lgamma(.5*k)-std::lgamma(total+.5*k),base=std::lgamma(.5);
 for(auto x:counts)lp+=std::lgamma(x+.5)-base;return -lp/std::log(2.);
}
double score_impl(const int32_t* keys,const double* freq,int64_t n,const int64_t* source_counts,const int32_t* map,const double* costs){
 double bits=0.;
 for(int64_t i=0;i<n;++i){
  int af,as,bf,bs,cf,cs;bool at,bt,ct;parts(keys[3*i],map,af,as,at);parts(keys[3*i+1],map,bf,bs,bt);parts(keys[3*i+2],map,cf,cs,ct);
  const int h1=bt?bs:bf;const int h0=bt?bf:(at?as:af);
  bits+=freq[i]*costs[(h0*28+h1)*27+cf];if(ct)bits+=freq[i]*costs[(h1*28+cf)*27+cs];
 }
 std::vector<std::vector<int64_t>> reverse(CODE_COUNT);int64_t one=0,two=0;
 for(int s=0;s<25;++s)if(source_counts[s]){reverse[map[s]].push_back(source_counts[s]);if(map[s]<26)one+=source_counts[s];else two+=source_counts[s];}
 for(const auto& g:reverse)if(g.size()>1)bits+=catbits(g);
 bits+=catbits(std::vector<int64_t>{one,two});return bits;
}
}
extern "C" double gdt192_expansion_score(const int32_t* keys,const double* freq,int64_t n,const int64_t* counts,const int32_t* map,const double* costs){return score_impl(keys,freq,n,counts,map,costs);}
extern "C" void gdt192_coordinate_scores(const int32_t* keys,const double* freq,int64_t n,const int64_t* counts,const int32_t* map,const double* costs,int source,double* out){
 #pragma omp parallel for schedule(dynamic,4)
 for(int code=0;code<CODE_COUNT;++code){int32_t trial[25];std::copy(map,map+25,trial);trial[source]=code;out[code]=score_impl(keys,freq,n,counts,trial,costs);}
}
