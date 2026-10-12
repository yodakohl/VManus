#include <iostream>
#include <vector>
#include <cstdint>
int main(){int n,m;std::cin>>n>>m;if(n<1||n>22)return 2;std::vector<std::vector<int>> words(m);for(auto&w:words){int k;std::cin>>k;w.resize(k);for(int&v:w)std::cin>>v;}uint32_t end=1u<<n;bool first=true;std::cout<<"[";for(uint32_t mask=2;mask<end;mask+=2){bool good=true;for(const auto&w:words){int changes=0;for(size_t i=0;i<w.size();++i){changes+=((mask>>w[i])^(mask>>w[(i+1)%w.size()]))&1u;if(changes>2){good=false;break;}}if(!good)break;}if(good){if(!first)std::cout<<",";std::cout<<mask;first=false;}}std::cout<<"]\n";}
