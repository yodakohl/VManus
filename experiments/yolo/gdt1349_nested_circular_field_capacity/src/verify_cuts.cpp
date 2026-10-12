#include <algorithm>
#include <iostream>
#include <vector>
#include <cstdint>
int main(){int letters,count;std::cin>>letters>>count;if(letters<1||letters>22)return 2;std::vector<std::vector<int>> records;for(int i=0;i<count;++i){int length;std::cin>>length;std::vector<int> record(length);for(int&value:record)std::cin>>value;records.push_back(record);}uint32_t full=(1u<<letters)-1;std::vector<uint32_t> answer;for(uint32_t selected=1;selected<full;selected+=2){bool valid=true;for(const auto&record:records){int exits=0;bool last=(selected>>record.back())&1u;for(int value:record){bool current=(selected>>value)&1u;if(last&&!current)++exits;last=current;if(exits>=2){valid=false;break;}}if(!valid)break;}if(valid)answer.push_back(full^selected);}std::sort(answer.begin(),answer.end());std::cout<<"[";for(size_t i=0;i<answer.size();++i){if(i)std::cout<<",";std::cout<<answer[i];}std::cout<<"]\n";}
