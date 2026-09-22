from copy import deepcopy
from common import *
b=dict(normal=True,water_raises=True,weight='DOWN',axis=True,wheels=dict(W=True,Wd=True),display_wheel='W',part_moves=True,arc_extents=['SMALL','LARGE'],adjusts=True,actuator='MANUAL',duration='VARIABLE',human_request=True,advance_due=True,episode_index_step=True,hour_kind='Hh',usual_solar=True,instance_solar=True,months={
 'A':dict(holes=['a0','a1'],days=['dA0','dA1'],period_end=2,history_end=2,steps=[dict(origin='a0',destination='a1',start=0,end=1),dict(origin='a1',destination='a0',start=1,end=2)]),
 'B':dict(holes=['b0','b1','b2'],days=['dB0','dB1','dB2'],period_end=2,history_end=2,steps=[dict(origin='b0',destination='b1',start=0,end=1),dict(origin='b1',destination='b2',start=1,end=2)])})
rows=[]
def add(name,**changes):
 f=deepcopy(b);f.update(changes);f['name']=name;rows.append(f);return f
add('BASE_MANUAL_VARIABLE');add('BASE_AUTO_VARIABLE',actuator='AUTO',human_request=False)
add('BASE_MANUAL_EQUAL',duration='EQUAL');add('BASE_AUTO_EQUAL',duration='EQUAL',actuator='AUTO',human_request=False)
add('WEIGHT_UP',weight='UP');add('AXIS_STOPPED',axis=False);add('DRIVE_WHEEL_STOPPED',wheels=dict(W=False,Wd=True))
add('PART_STILL',part_moves=False);add('CONSTANT_ARC',arc_extents=['SAME','SAME']);add('ADJUSTMENT_ABSENT',adjusts=False)
add('OTHER_DISPLAY_WHEEL',display_wheel='Wd')
f=add('HOLE_DAY_MISMATCH');f['months']['A']['days'].append('dA2')
f=add('EQUAL_MONTH_SIZES');f['months']['B']['holes']=['b0','b1'];f['months']['B']['days']=['dB0','dB1'];f['months']['B']['steps'][1]['destination']='b0'
f=add('CROSS_MONTH_SIZES');f['months']['A']['holes'].append('a2');f['months']['B']['holes']=['b0','b1'];f['months']['B']['steps'][1]['destination']='b0'
f=add('STEP_WRONG_MONTH_HOLE');f['months']['A']['steps'][0]['destination']='b0'
f=add('STEP_SAME_HOLE');f['months']['A']['steps'][0]['destination']='a0'
f=add('HISTORY_ENDS_EARLY');f['months']['A']['history_end']=1;f['months']['A']['steps']=f['months']['A']['steps'][:1]
f=add('SINGLE_STEP_MONTH')
for m in f['months'].values():m['steps']=[dict(origin=m['holes'][0],destination=m['holes'][1],start=0,end=2)]
add('WRONG_HOUR_KIND',hour_kind='OTHER_HOURS');add('NONSOLAR_INSTANCE',instance_solar=False);add('USUAL_SOLAR_FALSE',usual_solar=False)
add('NO_INDEX_STEP_DUE',actuator='AUTO',human_request=False,episode_index_step=False)
add('NO_INDEX_STEP_NOT_DUE',actuator='AUTO',human_request=False,episode_index_step=False,advance_due=False)
add('BROKEN_NOT_NORMAL',normal=False,weight='NONE',axis=False,wheels=dict(W=False,Wd=False),part_moves=False,adjusts=False)
assert len(rows)==24
write(E/'src/CASES.json',rows)
