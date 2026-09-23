#!/usr/bin/env python3
"""Validate the GitHub content contract offline; never claims remote publication."""
import collections,datetime,hashlib,html,json,re,sys,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LANGS=['en','es','pt','ja','ko','de','fr','tr','zh-TW','zh-CN','ru']
SLOTS={'banner':('banner','readme_banner'),'badge':('badge','top_badge'),'introduction':('readme','introduction_cta'),'model':('quickstart','model_link'),'keys':('quickstart','api_key'),'docs':('docs','first_run'),'footer':('footer','footer_cta')}
errors=[]
def check(ok,message):
    if not ok:errors.append(message)
def load(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def escape(text):return text.replace('|','\\|').replace('[','\\[').replace(']','\\]')
def mdfile(lang):return 'README.md' if lang=='en' else f'README_{lang}.md'
def paragraphs(notes):return [notes] if isinstance(notes,str) else notes

def main():
    data=load('data/use-cases.json');cases=data['items'];manifest=load('data/source-fidelity-manifest.json');decisions=load('data/curation-decisions.json');media=load('data/media-manifest.json');mm={m['id']:m for m in media};n=len(cases)
    check(len(decisions)==manifest['intake_case_count'],'intake denominator differs')
    check(collections.Counter(x['decision'] for x in decisions)=={'high_confidence_update':n,'drop':9,'unsure':4},'decision accounting differs')
    check([c['public_number'] for c in cases]==list(range(1,n+1)),'case numbering differs')
    check(len({c['source_url'] for c in cases})==n,'duplicate source')
    check(sum(bool(c['media']) for c in cases)==manifest['cases_with_source_media'],'media case denominator differs')
    expected=[m['local_preview'] for c in cases for m in c['media']]
    check(len(expected)==len(set(expected))==manifest['expected_public_visual_count']==len(media),'media denominator differs')
    for c in cases:
        datetime.date.fromisoformat(c['date']);check(len(c['title'].split())<=10,f'case {c["public_number"]}: title exceeds ten words')
        check(c['source_media_count']==c['expected_public_visual_count']==len(c['media']),f'case {c["public_number"]}: media mismatch')
        for m in c['media']:
            p=ROOT/m['local_preview'];record=mm.get(m['id'],{})
            check(p.is_file(),f'missing media {p.name}')
            if p.is_file():check(sha(p)==record.get('sha256')==m.get('local_sha256'),f'media bytes changed {p.name}')
            check(record.get('url')==m['poster_url'],f'preview origin differs {m["id"]}')
            check(m['source_url']==(m['video_url'] if m['kind']=='video' else m['poster_url']),f'source media URL differs {m["id"]}')
    actual=sorted(p.name for p in ROOT.glob('README*.md'));check(actual==sorted(mdfile(l) for l in LANGS),'README language set must be exactly 11')
    banners=load('data/banner-manifest.json');check({b['locale'] for b in banners}==set(LANGS),'cover language set')
    for banner in banners:
        image=ROOT/banner['path'];vector=ROOT/banner['source']
        check(image.is_file() and vector.is_file(),f'missing cover {banner["locale"]}')
        if image.is_file() and vector.is_file():
            check(sha(image)==banner['sha256'] and sha(vector)==banner['source_sha256'],f'stale cover {banner["locale"]}')
            check(image.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n',f'cover is not PNG {banner["locale"]}')
    review_index=load('data/localization-review-index.json')
    check(review_index['english_sha256']==sha(ROOT/'data/locales/en.json'),'stale English semantic review source')
    check({row['locale'] for row in review_index['reviews']}==set(LANGS)-{'en'},'semantic review locale coverage')
    for row in review_index['reviews']:
        check(row['source_sha256']==review_index['english_sha256'] and row['locale_sha256']==sha(ROOT/row['locale_file']),f'stale semantic review {row["locale"]}')
        check(row['checked_case_count']==n and row['reviewed_case_numbers']==list(range(1,n+1)),f'incomplete semantic review {row["locale"]}')
    inventory=(ROOT/'data/use-cases.md').read_text()
    check(list(map(int,re.findall(r'\]\(\.\./README\.md#case-(\d+)\)',inventory)))==list(range(1,n+1)),'curated Markdown inventory differs')
    en=load('data/locales/en.json');source_copy={c['public_number']:c for c in en['items']};stats={}
    for lang in LANGS:
        path=ROOT/mdfile(lang);lp=ROOT/f'data/locales/{lang}.json'
        if not path.exists() or not lp.exists():check(False,f'{lang}: missing README/editorial data');continue
        locale=load(lp);labels=locale['labels'];lc={c['public_number']:c for c in locale['items']};text=path.read_text()
        check(set(lc)==set(range(1,n+1)),f'{lang}: editorial case set')
        check(text.startswith('<div align="center">'),f'{lang}: centered cover')
        headings=list(re.finditer(r'^### .+? (\d+): \[(.*?)\]\((.*?)\) \(.+? \[(.*?)\]\((.*?)\)\)$',text,re.M))
        check(len(headings)==n,f'{lang}: case count');check([int(h[1]) for h in headings]==list(range(1,n+1)),f'{lang}: case order')
        check(not headings or headings[-1].start()<text.find(f'## 🙏 {labels["ack"]}'),f'{lang}: case appears after Acknowledge')
        check(bool(re.search(r'(?<!\d)'+str(n)+r'(?!\d)',labels['overviewtext'])),f'{lang}: Overview case count differs')
        expected_headings=[f'## 🍌 {labels["intro"]}',f'## 📊 {labels["overview"]}',f'## ⚡ {labels["quick"]}',f'## 📑 {labels["menu"]}']+[f'## {"📘" if cat["id"]=="official" else "🧩"} {labels["categories"][cat["id"]]}' for cat in data['categories'] if any(c['category']==cat['id'] for c in cases)]+['## Related Repositories' if lang=='en' else f'## 🔗 {labels["related"]}',f'## 🙏 {labels["ack"]}']
        check(re.findall(r'^## .+$',text,re.M)==expected_headings,f'{lang}: section order')
        menu=text.split('## 📑 ',1)[-1].split('<a id="category-',1)[0]
        check(set(map(int,re.findall(r'\]\(#case-(\d+)\)',menu)))==set(range(1,n+1)),f'{lang}: complete Menu')
        check(len(re.findall(r'\]\(#case-\d+\)',text))==n,f'{lang}: duplicate/outside Menu links')
        what=load('data/menu-labels.json')[lang]
        check(f'| {labels["case"]} | {labels["category"]} | {what} | {labels["type"]} |' in menu,f'{lang}: Menu columns')
        for section in ['overview','quick-start','related-repositories','acknowledge']:
            check(f'](#{section})' in menu and f'id="{section}"' in text,f'{lang}: section navigation {section}')
        cover='images/'+({'zh-CN':'zh','zh-TW':'zh-tw'}.get(lang,lang))+'.png'
        check(f'src="{cover}"' in text[:text.find('## ')],f'{lang}: template cover path')
        rendered=[]
        for i,(c,h) in enumerate(zip(cases,headings)):
            number=c['public_number'];ed=lc.get(number,{})
            block=text[h.start():headings[i+1].start() if i+1<len(headings) else len(text)]
            check(h[2]==escape(ed.get('title','')) and h[3]==c['source_url'] and h[4]=='@'+c['author_handle'].lstrip('@') and h[5]==c['author_url'],f'{lang}: case {number} identity/title mismatch')
            check(h[0].startswith(f'### {labels["case_label"]} {number}:'),f'{lang}: case {number} localized heading label')
            check(text[:h.start()].rstrip().endswith(f'<a id="case-{number}"></a>'),f'{lang}: case {number} anchor adjacency')
            check(block[h.end()-h.start():].lstrip().startswith(f'**{ed.get("takeaway", "")}**'),f'{lang}: case {number} first takeaway')
            for note in paragraphs(ed.get('body_notes','')):check(bool(note) and note in block,f'{lang}: case {number} source notes')
            check(f'Type: {c["type"]} | Date: {c["date"]}\n\n---' in block,f'{lang}: case {number} metadata/separator')
            ims=re.findall(r'<img src="(assets/media/[^\"]+)"',block);check(ims==[m['local_preview'] for m in c['media']],f'{lang}: case {number} media order/set');rendered+=ims
            for m in c['media']:
                if m['kind']=='video':check(html.escape(m['video_url']) in block,f'{lang}: case {number} playback URL')
            for s in c['supporting_sources']:check(s['source_url'] in block,f'{lang}: case {number} merged source')
            if lang!='en':
                check(ed.get('title')!=source_copy[number]['title'],f'{lang}: case {number} unchanged English title')
                check(ed.get('takeaway')!=source_copy[number]['takeaway'],f'{lang}: case {number} unchanged English takeaway')
                check(ed.get('body_notes')!=source_copy[number]['body_notes'],f'{lang}: case {number} unchanged English notes')
                # Literal retention complements the separately recorded semantic review; word-to-digit translation and repeated model names do not change a fact.
                nums=lambda s:set(re.findall(r'\d+(?:[.,]\d+)*',json.dumps(s,ensure_ascii=False)))
                check(nums(source_copy[number]['body_notes'])<=nums(ed.get('body_notes')),f'{lang}: case {number} source numeric literal omitted')
        check(rendered==expected,f'{lang}: total expected media order/set')
        if lang in ['zh-CN','zh-TW']:check('。' not in text,f'{lang}: prohibited Chinese sentence-ending mark')
        check(not re.search(r'\b(TODO|TBD)\b|translation pending|lorem ipsum|\{\{',text),f'{lang}: placeholders')
        table=[]
        for line in text.splitlines()+['']:
            if line.startswith('|'):table.append(len(re.split(r'(?<!\\)\|',line)))
            elif table:check(len(set(table))==1,f'{lang}: malformed table');table=[]
        urls=re.findall(r'\]\(([^\s)]+)\)',text)+re.findall(r'(?:href|src)="([^\"]+)"',text)
        for url in urls:
            u=html.unescape(url)
            if u.startswith('https://'):continue
            if u.startswith('#'):check(f'id="{u[1:]}"' in text,f'{lang}: missing anchor {u}')
            else:check((ROOT/u.split('#')[0]).is_file(),f'{lang}: missing local path {u}')
        stats[lang]={'cases':len(headings),'visuals':len(rendered)}
    for entry in load('data/utm-matrix.json'):
        q=urllib.parse.parse_qs(urllib.parse.urlparse(entry['url']).query);medium,content=SLOTS[entry['placement']]
        check(q=={'utm_source':['github'],'utm_medium':[medium],'utm_campaign':[ROOT.name],'utm_content':[content]},f'UTM slot differs {entry["placement"]}')
    check(not (ROOT/'preview').exists(),'unsolicited standalone website remains')
    for f in ['LICENSE','NOTICE.md','CONTRIBUTING.md','CODE_OF_CONDUCT.md','SECURITY.md','.github/PULL_REQUEST_TEMPLATE.md','docs/maintenance.md','docs/update-log.md']:
        check((ROOT/f).is_file() and (ROOT/f).stat().st_size>30,f'missing baseline {f}')
    result={'status':'passed' if not errors else 'failed','scope':'GitHub README/data/local media and 11-language content checks; not remote publication','cases':n,'readmes':len(stats),'expected_media':len(expected),'locales':stats,'errors':errors}
    print(json.dumps(result,ensure_ascii=False,indent=2));return bool(errors)

if __name__=='__main__':sys.exit(main())
