#!/usr/bin/env python3
"""Cache original source poster/image bytes. Never uploads or publishes anything."""
import argparse,concurrent.futures,json,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--proxy');a=p.parse_args()
d=json.loads((R/'data/use-cases.json').read_text());ms=[m for c in d['items'] for m in c['media']]
def fetch(m):
 target=R/m['local_preview'];temp=target.with_suffix('.tmp');u=m['poster_url'];status='cached'
 if not target.exists():
  cmd=['curl','--fail','--location','--silent','--show-error','--retry','2','--connect-timeout','12','--max-time','55',u,'--output',str(temp)]
  if a.proxy:cmd[1:1]=['--proxy',a.proxy]
  r=subprocess.run(cmd,text=True,capture_output=True)
  if r.returncode:return {'id':m['id'],'url':u,'status':'failed','error':r.stderr[-220:]}
  temp.replace(target);status='downloaded'
 b=target.read_bytes();magic='jpeg' if b[:3]==b'\xff\xd8\xff' else 'png' if b[:8]==b'\x89PNG\r\n\x1a\n' else 'webp' if b[:4]==b'RIFF' and b[8:12]==b'WEBP' else 'unknown'
 return {'id':m['id'],'url':u,'path':m['local_preview'],'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'magic':magic,'status':status if magic!='unknown' else 'invalid-image'}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:rows=list(ex.map(fetch,ms))
(R/'data/media-manifest.json').write_text(json.dumps(rows,indent=2)+'\n');bad=[r for r in rows if r['status'] in ['failed','invalid-image']]
print(json.dumps({'expected':len(ms),'checked':len(rows),'failures':len(bad),'bytes':sum(r.get('bytes',0) for r in rows),'errors':bad[:5]}));raise SystemExit(bool(bad))
