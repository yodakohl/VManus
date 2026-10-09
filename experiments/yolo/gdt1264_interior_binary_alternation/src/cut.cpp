#include <iostream>
#include <vector>
#include <climits>
#include <cstdint>
int main(){
 int n; if(!(std::cin>>n)||n<2||n>22)return 2;
 std::vector<std::vector<long long>> w(n,std::vector<long long>(n));
 for(int i=0;i<n;i++)for(int j=0;j<n;j++)std::cin>>w[i][j];
 uint32_t mask=0,bestmask=0,total=1u<<(n-1);long long score=0,best=LLONG_MIN,ties=0;
 for(uint32_t step=1;step<total;step++){
  int j=__builtin_ctz(step)+1;int old=(mask>>j)&1u;long long delta=0;
  for(int i=0;i<n;i++)if(i!=j)delta+=w[i][j]*((((mask>>i)&1u)==old)?1:-1);
  score+=delta;mask^=(1u<<j);
  if(score>best){best=score;bestmask=mask;ties=1;}
  else if(score==best){ties++;if(mask<bestmask)bestmask=mask;}
 }
 std::cout<<"{\"best_score\":"<<best<<",\"best_mask\":"<<bestmask<<",\"ties\":"<<ties<<",\"partitions\":"<<(total-1)<<"}\n";
}
