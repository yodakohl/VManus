// Fixed degree(2,2) Bernstein row controls; no target-dependent subdivision.
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>
using namespace std;
using I=__int128_t;
using V=array<int64_t,3>;
using Net=array<V,9>;
int enclosure(const Net&A,const Net&B,const Net&C,const Net&D){
 int mask=0;
 for(const auto&a:A)for(const auto&b:B)for(const auto&c:C){
  I ux=I(b[0])-a[0],uy=I(b[1])-a[1],uz=I(b[2])-a[2];
  I vx=I(c[0])-a[0],vy=I(c[1])-a[1],vz=I(c[2])-a[2];
  I nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;
  for(const auto&d:D){
   // Full doubled-row determinant is -2 times this dot product.
   I q=-(nx*(I(d[0])-a[0])+ny*(I(d[1])-a[1])+nz*(I(d[2])-a[2]));
   mask|=q<0?1:q>0?4:2;
   if((mask&1)&&(mask&4))return 7;
  }
 }
 return mask;
}
int main(){
 int n;if(!(cin>>n)||n<4||n>60)return 2;vector<Net>nets(n);
 for(auto&net:nets){
  int64_t l,b,u,t;if(!(cin>>l>>b>>u>>t)||l>u||b>t)return 3;
  for(auto x:{l,b,u,t})if(x < -100000000LL || x>100000000LL)return 4;
  array<int64_t,3>xs={2*l,l+u,2*u},ys={2*b,b+t,2*t},qx={l*l,l*u,u*u},qy={b*b,b*t,t*t};
  for(int i=0;i<3;i++)for(int j=0;j<3;j++)net[i*3+j]={xs[i],ys[j],2*(qx[i]+qy[j])};
 }
 for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)for(int c=b+1;c<n;c++)for(int d=c+1;d<n;d++)
  cout<<a<<','<<b<<','<<c<<','<<d<<','<<enclosure(nets[a],nets[b],nets[c],nets[d])<<'\n';
}
