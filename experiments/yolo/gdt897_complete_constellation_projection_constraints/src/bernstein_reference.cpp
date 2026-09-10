// Independent exact Bernstein enclosure. No subdivision or point selection.
// Input: n, then n integer native-metric boxes xmin ymin xmax ymax.
// Output: canonical i,j,k,l,mask; bits negative=1, zero=2, positive=4.
// Rows are twice [x,y,x*x+y*y,1]; determinant scale16 is positive.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>
using I = __int128_t;
using Row = std::array<I,4>;
using Net = std::array<Row,9>;
struct Term { std::array<int,4> p; int sign; };

std::vector<Term> terms() {
    std::vector<Term> out;
    std::array<int,4> p={0,1,2,3};
    do {
        int parity=0;
        for(int i=0;i<4;++i) for(int j=i+1;j<4;++j) parity^=(p[i]>p[j]);
        out.push_back({p,parity?-1:1});
    } while(std::next_permutation(p.begin(),p.end()));
    return out;
}

I determinant(const Row& a,const Row& b,const Row& c,const Row& d,
              const std::vector<Term>& permutations) {
    const Row* rows[4]={&a,&b,&c,&d};
    I sum=0;
    for(const auto& t:permutations) {
        I product=t.sign;
        for(int i=0;i<4;++i) product*=(*rows[i])[t.p[i]];
        sum+=product;
    }
    return sum;
}

Net controls(long long l,long long b,long long u,long long t) {
    // Bound also protects every intermediate from signed128 overflow.
    if(l<0 || b<0 || u<l || t<b || u>8000000 || t>8000000)
        throw std::runtime_error("invalid native box or exceeded arithmetic bound");
    const I x[3]={I(2)*l,I(l)+u,I(2)*u};
    const I y[3]={I(2)*b,I(b)+t,I(2)*t};
    const I qx[3]={I(l)*l,I(l)*u,I(u)*u};
    const I qy[3]={I(b)*b,I(b)*t,I(t)*t};
    Net net{};
    for(int i=0;i<3;++i) for(int j=0;j<3;++j)
        net[3*i+j]={x[i],y[j],I(2)*(qx[i]+qy[j]),2};
    return net;
}

int enclosure(const Net& a,const Net& b,const Net& c,const Net& d,
              const std::vector<Term>& permutations) {
    int mask=0;
    for(const Row& aa:a) for(const Row& bb:b)
        for(const Row& cc:c) for(const Row& dd:d) {
            I value=determinant(aa,bb,cc,dd,permutations);
            mask |= value<0?1:value>0?4:2;
            // A range enclosing negative and positive necessarily includes zero.
            if((mask&5)==5) return 7;
        }
    return mask;
}

int main() {
    try {
        int n;
        if(!(std::cin>>n) || n<4 || n>59) throw std::runtime_error("invalid count");
        std::vector<Net> nets;
        for(int i=0;i<n;++i) {
            long long l,b,u,t;
            if(!(std::cin>>l>>b>>u>>t)) throw std::runtime_error("missing box");
            nets.push_back(controls(l,b,u,t));
        }
        std::string extra;
        if(std::cin>>extra) throw std::runtime_error("trailing input");
        const auto permutations=terms();
        for(int i=0;i<n;++i) for(int j=i+1;j<n;++j)
            for(int k=j+1;k<n;++k) for(int l=k+1;l<n;++l)
                std::cout<<i<<','<<j<<','<<k<<','<<l<<','
                         <<enclosure(nets[i],nets[j],nets[k],nets[l],permutations)<<'\n';
    } catch(const std::exception& e) {
        std::cerr<<e.what()<<'\n';return 1;
    }
}
