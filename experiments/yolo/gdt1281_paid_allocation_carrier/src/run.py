import collections,hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
from codec import PALETTE,LITERALS,H,F,G,A,T,K,Z,END,DIGITS,encode,decode,layout,textcode
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def save(n,x):(B/('artifacts/'+n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fixtures=json.loads((B/'src/FIXTURES.json').read_text());encoded=encode(fixtures)
 for width in [1,2,3,24,41]:assert decode(layout(encoded,width))==fixtures
 cases=[]
 for n in range(13):
  b={'left':'A','right':'B','batch':'LOT','unit':'ONE','total':n,'rows':[[a,n-a] for a in range(n+1)]};s=encode([b]);assert decode(layout(s))==[b]
  rows=[A+T*a+K+T*(n-a)+Z for a in range(n+1)];assert len(set(rows))==n+1 and all(len(x)==n+3 for x in rows)
  positive=rows[1:-1];assert len({tuple(sorted(collections.Counter(zip(x,x[1:])).items())) for x in positive})<=1
  cases.append({'source':b,'encoded':s,'row_strings':rows})
 base=dict(fixtures[0],rows=[[2,2]]);valid=encode([base]);header=valid[:valid.index(G)+1];row=A+T*2+K+T*2+Z
 invalid=[('missing_header',row+END),('truncated_header',H),('unknown_sign',valid+'!'),('odd_literal',H+DIGITS[0]+F+valid[valid.index(F)+1:]),('unused_literal_pair',H+DIGITS[6]*2+valid[1:]),('leading_zero_total',H+F.join(textcode(base[k]) for k in ['left','right','batch','unit'])+F+textcode('04')+G+row+END),('equal_recipients',H+F.join(textcode(v) for v in ['ADA','ADA','BEANS','BEAN','4'])+G+row+END),('empty_block',header+END),('missing_END',valid[:-1]),('wrong_sum',header+A+T*2+K+T*3+Z+END),('stray_row_after_END',valid+row)]
 bad=[]
 for name,s in invalid:
  try:decode(s)
  except ValueError:bad.append({'name':name,'encoded':s,'rejected':True})
  else:raise AssertionError(name)
 changed=dict(base,rows=[[1,3]]);assert decode(encode([changed]))==[changed] and encode([changed])!=valid
 swapped=dict(base,left=base['right'],right=base['left']);assert decode(encode([swapped]))==[swapped]
 everychar=dict(base,batch=LITERALS);assert decode(encode([everychar]))==[everychar]
 costs=[]
 for b in fixtures:
  h=2*(sum(len(b[k]) for k in ['left','right','batch','unit'])+len(str(b['total'])))+6;rowcost=len(b['rows'])*(b['total']+3);actual=len(encode([b]));assert actual==h+rowcost+1;costs.append({'header':h,'rows':rowcost,'END':1,'total':actual})
 result={'status':'SOURCE_KNOWN_MODULE_ROUNDTRIP_PASS','native_status':'NO_NATIVE_BINDING_NO_STATISTICAL_FIT','sign_slots_used':15,'available_working_signs':22,'fixtures':fixtures,'encoded_stream':encoded,'wrapped_24':layout(encoded),'costs':costs,'source_blocks':len(fixtures),'source_rows':sum(len(b['rows']) for b in fixtures),'exhaustive_totals':13,'exhaustive_allocations':sum(n+1 for n in range(13)),'invalid_cases':len(bad),'same_total_changed_row_is_valid':True,'recipient_swap_changes_content':True,'all_literal_characters_roundtrip':True}
 save('RESULT',result);save('CASES',cases);save('INVALID_CASES',bad);save('CONTENT_CHANGES',{'changed_row':{'source':changed,'encoded':encode([changed])},'swapped_recipients':{'source':swapped,'encoded':encode([swapped])},'all_literal_characters':{'source':everychar,'encoded':encode([everychar])}})
 print(json.dumps({k:v for k,v in result.items() if k not in ['fixtures','encoded_stream','wrapped_24']},indent=2))
if __name__=='__main__':main()
