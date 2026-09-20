import itertools,json
from check_model import check,ground
from run import solve
cases=[(['ol','x','or'],0),(['or','x','ol'],1),(['ol','x','ol','x','or'],0),(['or','ol'],1),(['ol','qol','sheedy','ol'],0)]
count=0
for n in range(1,6):
 for words in itertools.product(['ol','or','x'],repeat=n):
  for start in [0,1]:
   possible=[]
   for code in range(9):
    d={'ol':[0,2],'or':[2,1],'x':[code//3,code%3]}; state=start
    for w in words:
     if state==2:break
     state=d[w][state]
    if state!=2:possible.append(code)
   result=check(words,start)
   assert (result['status']=='SAT')==bool(possible),(words,start,result,possible)
   if result['status']=='SAT':ground(words,start,result['dictionary'],result['states'])
   count+=1
for words,start in cases:
 for q in [{'kind':'base'}]+[{'kind':'word','word':'x','code':c} for c in range(9) if 'x' in words]:
  a=solve(words,start,q);b=check(words,start,q);assert a['status']==b['status'],(words,q,a,b)
  count+=1
print(json.dumps({'status':'PASS','synthetic_cases':count,'manuscript_read':False}))
