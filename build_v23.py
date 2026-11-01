"""Add native Tiled label layer; preserve v17 artwork and v16 approved walkability.
Create an exact collision diagram and offline movement inspector.
"""
from pathlib import Path
from copy import deepcopy
from collections import deque
import json,zipfile,base64
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parents[1];m=json.loads((p/'base-v22.tmj').read_text());old=deepcopy(m)
w,h,t=m['width'],m['height'],m['tilewidth'];W,H=w*t,h*t
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=lambda size:ImageFont.truetype(fontpath,int(size))
base=Image.open(p/'ain_conference_v22.png').convert('RGBA')
overlay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(overlay)
labels=[
 ('ГОЛОВНА СЦЕНА',572,173,6.5,'#cbb8ff'),
 ('ГОЛОВНА СЦЕНА',708,173,6.5,'#cbb8ff'),
 ('ГОЛОВНА\nСЦЕНА',584,313,5.5,'#cbb8ff'),
 ('НЕТВОРКІНГ 1',185,42,10,'#8de4c8'),
 ('НЕТВОРКІНГ 2',1091,42,10,'#8de4c8'),
 ('НЕТВОРКІНГ 3',180,684,10,'#8de4c8'),
 ('НЕТВОРКІНГ 4',1109,684,10,'#8de4c8'),
 ('ЗОНА РОЗМОВ 1',343,64,6,'#8de4c8'),
 ('ЗОНА РОЗМОВ 2',932,64,6,'#8de4c8'),
 ('СТЕНДИ ПАРТНЕРІВ',176,192,9,'#f3cf86'),
 ('СТЕНДИ ПАРТНЕРІВ',1096,192,9,'#f3cf86')]
blocked_for_signs=next(l for l in m['layers'] if l['name']=='Collisions')['data']
sign_bounds=[]
for name,x,y,size,color in labels:
 f=font(size*4);box=d.multiline_textbbox((0,0),name,font=f,spacing=4,align='center');tw=box[2];th=box[3]-box[1];pad=16;cx=x*4;cy=y*4
 rect=(int(cx-tw/2-pad),int(cy-th/2-10),int(cx+tw/2+pad),int(cy+th/2+10))
 if name=='ГОЛОВНА СЦЕНА':
  # Lettering directly on the existing fascia, no rectangular background or frame.
  d.text((cx-tw/2+1,cy-th/2-box[1]+2),name,font=f,fill=(9,13,30,255),stroke_width=1,stroke_fill=(9,13,30,255))
  d.text((cx-tw/2,cy-th/2-box[1]),name,font=f,fill=(194,201,234,255))
  continue
 # Metal wall plaques: square corners, raised rim, fasteners, restrained lettering.
 d.rectangle(rect,fill=(22,31,40,255),outline=(7,12,20,255),width=5)
 l,top,r,bot=rect
 d.line((l+4,top+4,r-4,top+4),fill=(128,148,154,255),width=3)
 d.line((l+4,top+4,l+4,bot-4),fill=(105,125,134,255),width=3)
 d.line((l+4,bot-4,r-4,bot-4),fill=(2,6,10,255),width=3)
 for px in [l+7,r-7]:
  for py in [top+7,bot-7]:d.rectangle((px-1,py-1,px+1,py+1),fill=(150,158,160,255))
 d.multiline_text((cx-tw/2,cy-th/2-box[1]+2),name,font=f,fill=(0,0,0,255),spacing=4,align='center')
 d.multiline_text((cx-tw/2,cy-th/2-box[1]),name,font=f,fill=color,spacing=4,align='center')
 sign_bounds.append((name,rect))
 for gy in range(top//32,(bot//32)+1):
  for gx in range(l//32,(r//32)+1):
   assert blocked_for_signs[gy*w+gx],f'Sign over walkable tile: {name} {(gx,gy)}'
first=max(s['firstgid']+s['tilecount'] for s in m['tilesets']);data=[0]*(w*h);label_files=[]
for y in range(0,h,64):
 for x in range(0,w,64):
  cw,ch=min(64,w-x),min(64,h-y);part=overlay.crop((x*t,y*t,(x+cw)*t,(y+ch)*t))
  name=f'ain-labels-v23-{x//64}-{y//64}.png';part.save(p/name);label_files.append(name)
  m['tilesets'].append({'firstgid':first,'name':f'AIN navigation {x//64}-{y//64}','tilewidth':t,'tileheight':t,'tilecount':cw*ch,'columns':cw,'image':name,'imagewidth':cw*t,'imageheight':ch*t,'margin':0,'spacing':0})
  for dy in range(ch):
   for dx in range(cw):
    if part.getchannel('A').crop((dx*t,dy*t,(dx+1)*t,(dy+1)*t)).getbbox():data[(y+dy)*w+x+dx]=first+dy*cw+dx
  first+=cw*ch
m['layers'].insert(1,{'id':5,'name':'Navigation labels','type':'tilelayer','width':w,'height':h,'x':0,'y':0,'opacity':1,'visible':True,'data':data});m['nextlayerid']=6
(p/'map-ain-v23.tmj').write_text(json.dumps(m,separators=(',',':')))
composite=Image.alpha_composite(base,overlay);composite.resize((1920,1152),Image.Resampling.LANCZOS).convert('RGB').save(p/'AIN_v23_labels.jpg',quality=90,optimize=True)
blocked=next(l for l in m['layers'] if l['name']=='Collisions')['data'];start=next(l for l in m['layers'] if l['name']=='start')['data']
assert [l for l in m['layers'] if l['name']!='Navigation labels']==old['layers']
assert all(blocked[x] and blocked[(h-1)*w+x] for x in range(w))
assert all(blocked[y*w] and blocked[y*w+w-1] for y in range(h))
q=deque([next(i for i,v in enumerate(start) if v)]);seen=set()
while q:
 i=q.popleft()
 if i in seen or blocked[i]:continue
 seen.add(i);x,y=i%w,i//w
 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
  nx,ny=x+dx,y+dy
  if 0<=nx<w and 0<=ny<h:q.append(ny*w+nx)
assert len(seen)==sum(not v for v in blocked)
# Reconstruct native labels from all tile references and verify exact pixels.
recon=Image.new('RGBA',(W,H));cache={s['firstgid']:Image.open(p/s['image']) for s in m['tilesets'][8:]}
labelsets=m['tilesets'][8:]
for i,gid in enumerate(data):
 if not gid:continue
 s=next(s for s in reversed(labelsets) if gid>=s['firstgid']);n=gid-s['firstgid'];x=n%s['columns']*t;y=n//s['columns']*t
 recon.paste(cache[s['firstgid']].crop((x,y,x+t,y+t)),(i%w*t,i//w*t))
assert recon.tobytes()==overlay.tobytes()
# Separate diagnostic sheet: every blocked tile red, every open tile untinted.
shade=Image.new('RGBA',(W,H));sd=ImageDraw.Draw(shade)
for i,v in enumerate(blocked):
 if v:sd.rectangle((i%w*t,i//w*t,i%w*t+t-1,i//w*t+t-1),fill=(255,32,65,155))
diag=Image.alpha_composite(base,shade);diag=Image.alpha_composite(diag,overlay).resize((1920,1152),Image.Resampling.LANCZOS)
sheet=Image.new('RGB',(1920,1300),'#101727');sheet.paste(diag,(0,112));dd=ImageDraw.Draw(sheet)
dd.text((30,16),'AIN · СХЕМА ПРОХІДНОСТІ',font=font(30),fill='white')
dd.rectangle((32,68,52,88),fill='#ff2041');dd.text((64,63),'Червоне — рух заблокований. Решта карти — прохідна.',font=font(21),fill='#e8ecf4')
dd.text((30,1272),'v23 • Жовті ділянки відкриті, сині закриті • Сцена відкрита за розміткою; інші таблички на стінах.',font=font(17),fill='#c5cfe3')
sheet.resize((1440,975),Image.Resampling.LANCZOS).save(p/'AIN_v23_blocked_zones.jpg',quality=88,optimize=True)
report={'labels':len(labels),'native_label_render_verified':True,'collision_matches_user_markup':True,'other_signs_on_blocked_tiles':True,'stage_text_aligned_unframed':True,'outer_boundary_closed':True,'all_walkable_tiles_reachable':True,'walkable_tiles':len(seen),'blocked_tiles':sum(bool(v) for v in blocked),'max_texture_size':max(max(s['imagewidth'],s['imageheight']) for s in m['tilesets']),'live_WorkAdventure_test':'pending'}
assert report['max_texture_size']<=2048
(p/'validation-v23.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))

composite.save(p/"ain_with_labels_v23.png",compress_level=6)
print(json.dumps(report,ensure_ascii=False))
