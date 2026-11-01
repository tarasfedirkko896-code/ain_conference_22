from pathlib import Path
from copy import deepcopy
from collections import deque
from PIL import Image,ImageDraw
import json
p=Path(__file__).resolve().parents[1];m=json.loads((p/'base-v20.tmj').read_text());old=deepcopy(m)
opens=[[(589,254),(600,254),(601,262),(670,260),(700,266),(701,290),(591,288)],[(739,273),(745,262),(783,259),(817,262),(853,262),(853,293),(806,293),(795,289),(744,290)]]
closes=[
[(60,444),(68,441),(73,445),(71,460),(68,473),(58,472)],
[(231,445),(238,444),(239,475),(231,475)],
[(290,444),(304,444),(306,470),(299,472),(292,467)],
[(450,418),(458,417),(460,436),(457,466),(450,466)],
[(978,435),(989,436),(991,475),(981,475),(977,465)],
[(1135,415),(1146,415),(1144,438),(1147,474),(1137,474)],
[(1203,386),(1211,383),(1211,417),(1221,418),(1222,472),(1203,472)],
[(1376,443),(1383,447),(1385,466),(1382,477),(1376,476)],
[(292,572),(300,567),(305,568),(305,626),(294,625),(292,612),(293,589)],
[(455,565),(462,567),(464,605),(462,625),(456,627)],
[(976,590),(986,589),(989,621),(980,622),(977,614)],
[(1199,583),(1210,579),(1214,600),(1217,622),(1199,621)],
[(1375,590),(1382,590),(1384,620),(1377,624),(1375,620)],
[(1315,280),(1353,285),(1353,320),(1316,317)]
]
w,h=m['width'],m['height'];data=next(l for l in m['layers'] if l['name']=='Collisions')['data'];gid=next(s['firstgid'] for s in m['tilesets'] if s['name']=='Invisible collision')
mask=Image.new('1',(1440,975));d=ImageDraw.Draw(mask)
for poly in opens:d.polygon(poly,fill=1)
cleared=[];opened=[];closed=[];bluecells=[]
for y in range(h):
 for x in range(w):
  i=y*w+x
  if mask.crop((x*9,84+y*9,(x+1)*9,84+(y+1)*9)).getbbox():
   opened.append(i)
   if data[i]:cleared.append(i)
   data[i]=0
# Trace each contour independently; tile-centre sampling avoids expanding whole bounding boxes.
counts=[]
for poly in closes:
 bm=Image.new('1',(1440,975));ImageDraw.Draw(bm).polygon(poly,fill=1);n=0
 for y in range(h):
  for x in range(w):
   if bm.getpixel((int(x*9+4.5),int(84+y*9+4.5))):
    n+=1;i=y*w+x;bluecells.append(i)
    if not data[i]:closed.append(i)
    data[i]=gid
 assert n>0,poly
 counts.append(n)
assert not set(opened)&set(bluecells)
start=next(l for l in m['layers'] if l['name']=='start')['data'];q=deque([next(i for i,v in enumerate(start) if v)]);seen=set()
while q:
 i=q.popleft()
 if i in seen or data[i]:continue
 seen.add(i);x,y=i%w,i//w
 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
  a,b=x+dx,y+dy
  if 0<=a<w and 0<=b<h:q.append(b*w+a)
assert all(i in seen for i in opened)
assert all(data[i] for i in bluecells)
g=json.loads((p/'geometry-v15.json').read_text())
for name,(x,y) in g['checkpoints'].items():assert int(y/8)*w+int(x/8) in seen,name
expected=deepcopy(old);next(l for l in expected['layers'] if l['name']=='Collisions')['data']=data;assert expected==m
(p/'base-v21.tmj').write_text(json.dumps(m,separators=(',',':')))
report={'yellow_regions':2,'blue_contours':14,'tiles_per_blue_contour':counts,'tiles_cleared':len(cleared),'tiles_closed':len(closed),'yellow_reachable':True,'all_previous_route_checkpoints_reachable':True,'collision_accuracy':'32x32 world pixels; 9x9 pixels on annotation; centre sampled outlines'}
(p/'collision-changes-v21.json').write_text(json.dumps(report,indent=2));print(report)
