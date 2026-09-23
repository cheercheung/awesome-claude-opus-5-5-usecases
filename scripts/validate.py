#!/usr/bin/env python3
"""Portable local content gate; does not claim live external-link or publication verification."""
import collections,hashlib,html,json,re,sys,urllib.parse,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1];errors=[]
def ck(x,msg):
 if not x:errors.append(msg)
def read(n):return (R/n).read_text()
def load(n):return json.loads(read(n))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=load('data/use-cases.json');cs=d['items'];mf=load('data/source-fidelity-manifest.json');dec=load('data/curation-decisions.json');media=load('data/media-manifest.json');N=len(cs)
ck(len(dec)==mf['intake_case_count'],'intake denominator differs');ck(collections.Counter(x['decision'] for x in dec)=={'selected':N,'merged':9,'unsure':4},'decision accounting differs');ck(len({c['source_url'] for c in cs})==N,'duplicate source');ck([c['public_number'] for c in cs]==list(range(1,N+1)),'case numbering differs');ck(sum(bool(c['media']) for c in cs)==mf['cases_with_source_media'],'media case denominator differs');ck(sum(len(c['media']) for c in cs)==mf['expected_public_visual_count']==len(media),'media denominator differs')
mm={m['id']:m for m in media};paths=set();media_errors=[]
for c in cs:
 datetime.date.fromisoformat(c['date']);ck(len(c['title'].split())<=10,f'case {c["public_number"]}: long title')
 ck(c['source_media_count']==c['expected_public_visual_count']==len(c['media']),f'case {c["public_number"]}: media mismatch')
 for m in c['media']:
  p=R/m['local_preview'];paths.add(m['local_preview']);rec=mm.get(m['id'],{})
  ck(p.is_file(),f'missing {p.name}')
  if p.is_file():ck(sha(p)==rec.get('sha256'),f'preview hash differs: {p.name}');ck(p.stat().st_size>100,f'empty media {p.name}')
  ck(rec.get('url')==m['poster_url'],f'media origin mismatch {m["id"]}')
  ck(m['source_url']==(m['video_url'] if m['kind']=='video' else m['poster_url']),f'source media mismatch {m["id"]}')
  if m['kind']=='video':ck(m['video_url'].startswith('https://video.twimg.com/'),f'missing playable URL {m["id"]}')
for name,lang in [('README.md','en'),('README_zh-CN.md','zh-CN'),('README_ja.md','ja')]:
 text=read(name);heads=list(re.finditer(r'^### Case (\d+): \[(.*?)\]\((.*?)\) \(by \[(.*?)\]\((.*?)\)\)$',text,re.M));ck(len(heads)==N,f'{name}: case count')
 ck([int(h[1]) for h in heads]==list(range(1,N+1)),f'{name}: order')
 menu=text.split('## 📑 ',1)[1].split('<a id="category-',1)[0];ck(set(map(int,re.findall(r'\]\(#case-(\d+)\)',menu)))==set(range(1,N+1)),f'{name}: Menu coverage')
 rendered=[]
 for i,(c,h) in enumerate(zip(cs,heads)):
  block=text[h.start():heads[i+1].start() if i+1<len(heads) else len(text)]
  escaped_title=c['copy'][lang]['title'].replace('|','\\|').replace('[','\\[').replace(']','\\]')
  ck(h[2]==escaped_title and h[3]==c['source_url'] and h[4]==c['author_handle'] and h[5]==c['author_url'],f'{name}: identity/title mismatch {i+1}')
  ck(f'**{c["copy"][lang]["takeaway"]}**' in block,f'{name}: takeaway mismatch {i+1}');ck(f'Type: {c["type"]} | Date: {c["date"]}' in block,f'{name}: metadata mismatch {i+1}')
  ck(text[:h.start()].rstrip().endswith(f'<a id="case-{i+1}"></a>'),f'{name}: anchor adjacency {i+1}')
  ims=re.findall(r'<img src="(assets/media/[^\"]+)"',block);ck(ims==[m['local_preview'] for m in c['media']],f'{name}: case media set/order mismatch {i+1}');rendered+=ims
  for m in c['media']:
   if m['kind']=='video':ck(html.escape(m['video_url']) in block,f'{name}: missing playback {i+1}')
  for sup in c['supporting_sources']:ck(sup['source_url'] in block,f'{name}: missing merged evidence {i+1}')
  if lang!='en':ck(c['copy'][lang]['title']!=c['title'],f'{name}: untranslated title {i+1}');ck(c['copy'][lang]['takeaway']!=c['takeaway'],f'{name}: untranslated takeaway {i+1}')
 ck(len(rendered)==mf['expected_public_visual_count'] and set(rendered)==paths,f'{name}: expected rendered media denominator')
 if lang=='zh-CN':ck('。' not in text,'Chinese sentence ending punctuation')
 ck(not any(marker in text for marker in ['{{','translation pending','lorem ipsum','TODO']),f'{name}: placeholder')
 # Table delimiter count, excluding escaped literal pipes
 table=[]
 for line in text.splitlines()+['']:
  if line.startswith('|'):table.append(len(re.split(r'(?<!\\)\|',line)))
  elif table:ck(len(set(table))==1,f'{name}: malformed Markdown table');table=[]
 # Every README relative link and explicit fragment is resolved
 urls=re.findall(r'\]\(([^\s)]+)\)',text)+re.findall(r'(?:href|src)="([^\"]+)"',text)
 for u in urls:
  u=html.unescape(u)
  if u.startswith('https://'):continue
  if u.startswith('#'):ck(f'id="{u[1:]}"' in text,f'{name}: missing fragment {u}')
  else:ck((R/u.split('#')[0]).is_file(),f'{name}: missing local link {u}')
 for u in urls:
  u=html.unescape(u)
  if urllib.parse.urlparse(u).hostname=='evolink.ai':
   q=urllib.parse.parse_qs(urllib.parse.urlparse(u).query);ck(q.get('utm_source')==['github'] and all(q.get(k) for k in ['utm_medium','utm_campaign','utm_content']),f'{name}: missing UTM')
preview=read('preview/index.html');p=json.loads(re.search(r'const DATA=(.*?);\nconst \$',preview,re.S)[1]);ck(p['items']==cs,'preview/data mismatch');ck('<script src=' not in preview,'preview depends on external JS')
for file in ['LICENSE','CONTRIBUTING.md','SECURITY.md','CODE_OF_CONDUCT.md','.github/PULL_REQUEST_TEMPLATE.md','.github/ISSUE_TEMPLATE/case.md','.github/ISSUE_TEMPLATE/correction.md','docs/maintenance.md','docs/update-log.md','assets/banner.svg']:ck((R/file).is_file() and (R/file).stat().st_size>30,f'missing baseline {file}')
# Source snapshot checks run when local evidence is present; portable content gate works without it
E=R/'.codex/production/20260923-local'
if (E/'claude-opus-5-5.json').exists():
 ck(sha(E/'claude-opus-5-5.json')==mf['source_manifest_sha256'],'input snapshot hash mismatch');ck(sha(E/'sources.json')==mf['sources_sha256'],'source snapshot hash mismatch')
 sources={s['sourceId']:s for s in json.loads((E/'sources.json').read_text())['items']}
 intake={i['sourceId']:i for i in json.loads((E/'claude-opus-5-5.json').read_text())['items']}
 for c in cs:
  s=sources[c['source_id']];ck(c['date']==intake[c['source_id']]['sourcePublishedAt'][:10],f'source date changed {c["public_number"]}')
  root=s.get('tweet',{}).get('media',[])
  if root:ck([m['id'] for m in c['media']]==[m['id'] for m in root],f'source attachments omitted {c["public_number"]}')
  ck(c['source_record_sha256']==hashlib.sha256(json.dumps(s,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),f'original source record changed {c["public_number"]}')
result={'status':'passed' if not errors else 'failed','scope':'local content, source fidelity, README/data/preview parity, media bytes, local links, tables, UTM, supplied locales','cases':N,'readmes':3,'source_media_cases':mf['cases_with_source_media'],'expected_visuals_per_readme':mf['expected_public_visual_count'],'checked_media_files':len(media),'video_slots':sum(m['kind']=='video' for c in cs for m in c['media']),'errors':errors,'external_live_sources':'not claimed by this offline validator','publication':'not claimed'}
print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(bool(errors))
