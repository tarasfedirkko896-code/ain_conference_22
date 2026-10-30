"""Build a standalone WorkAdventure TMJ from the approved artwork and collision geometry.
Coordinates in geometry-v15.json use a 1280 x 768 design canvas.
"""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
from collections import deque
ROOT=Path(__file__).resolve().parents[1]
W,H,T=160,96,32
art=Image.open(sys.argv[1]).convert('RGB').resize((W*T,H*T),Image.Resampling.LANCZOS)
# Place the supplied brand asset deterministically during map compilation.
# Source symbol bounds, with the original wordmark left outside the crop.
logo=Image.open(ROOT/'rozetka-original.png').convert('RGBA').crop((64,0,536,470))
logo=logo.resize((104,104),Image.Resampling.LANCZOS)
ImageDraw.Draw(art).rectangle((284,1000,403,1116),fill=(5,25,23))
art.paste(logo,(292,1004),logo)
art.save(ROOT/'ain_conference_v15.png',compress_level=6)
g=json.loads((ROOT/'geometry-v15.json').read_text())
mask=Image.new('1',(1280,768));d=ImageDraw.Draw(mask)
for shape in g['obstacles']:
 kind,coords=shape
 getattr(d,kind)(coords,fill=1)
blocked=[int(mask.getpixel((x*8+4,y*8+4))) for y in range(H) for x in range(W)]
spawn=[0]*(W*H)
for y in range(87,91):
 for x in range(72,88):
  if not blocked[y*W+x]: spawn[y*W+x]=W*H+2
assert sum(bool(v) for v in spawn)>=32
seen=set();q=deque([next(i for i,v in enumerate(spawn) if v)])
while q:
 i=q.popleft()
 if i in seen or blocked[i]:continue
 seen.add(i);x,y=i%W,i//W
 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
  nx,ny=x+dx,y+dy
  if 0<=nx<W and 0<=ny<H:q.append(ny*W+nx)
report={}
for name,(x,y) in g['checkpoints'].items():
 i=int(y/8)*W+int(x/8);report[name]=i in seen
assert all(report.values()),report
assert len(seen)==sum(not v for v in blocked), 'Disconnected walkable pockets'
base={'width':W,'height':H,'x':0,'y':0,'opacity':1,'visible':True}
def layer(id,name,data):return dict(base,id=id,name=name,type='tilelayer',data=data)
def tileset(gid,name,img,count=1,cols=1):return {'firstgid':gid,'name':name,'tilewidth':T,'tileheight':T,'tilecount':count,'columns':cols,'image':img,'imagewidth':cols*T,'imageheight':(count//cols)*T,'margin':0,'spacing':0}
ts=tileset(W*H+1,'Invisible collision','invisible_collision.png');ts['tiles']=[{'id':0,'properties':[{'name':'collides','type':'bool','value':True}]}]
m={'compressionlevel':-1,'width':W,'height':H,'infinite':False,'orientation':'orthogonal','renderorder':'right-down','tiledversion':'1.11.2','tilewidth':T,'tileheight':T,'type':'map','version':'1.10','nextlayerid':5,'nextobjectid':1,'layers':[layer(1,'AIN artwork',list(range(1,W*H+1))),layer(2,'Collisions',[(W*H+1)*b for b in blocked]),{'id':3,'name':'floorLayer','type':'objectgroup','objects':[],'opacity':1,'visible':True,'x':0,'y':0},layer(4,'start',spawn)],'tilesets':[tileset(1,'AIN artwork','ain_conference_v15.png',W*H,W),ts,tileset(W*H+2,'Start','invisible_start.png')]}
(ROOT/'map-ain-v15.tmj').write_text(json.dumps(m,separators=(',',':')))
(ROOT/'validation-v15.json').write_text(json.dumps({'checkpoints':report,'reachable_tiles':len(seen),'spawn_tiles':sum(bool(v) for v in spawn),'engine_test':'Pending WorkAdventure live test'},ensure_ascii=False,indent=2))
preview=art.resize((1280,768)).convert('RGBA'); overlay=Image.new('RGBA',preview.size);pd=ImageDraw.Draw(overlay)
for i,b in enumerate(blocked):
 if b:pd.rectangle(((i%W)*8,(i//W)*8,(i%W)*8+7,(i//W)*8+7),fill=(255,40,60,105))
preview=Image.alpha_composite(preview,overlay);preview.save(ROOT/'collision-preview-v15.png')
print(json.dumps(report,ensure_ascii=False));print('Reachable:',len(seen))
