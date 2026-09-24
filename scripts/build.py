#!/usr/bin/env python3
"""Render GitHub README files from reviewed editorial JSON; never translate prose."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import urlencode,quote

ROOT=Path(__file__).resolve().parents[1]
LANGS=[('en','English','111111'),('es','Español','ffb703'),('pt','Português','2a9d8f'),('ja','日本語','52b788'),('ko','한국어','4ea8de'),('de','Deutsch','f4a261'),('fr','Français','e76f51'),('tr','Türkçe','d62828'),('zh-TW','繁體中文','8338ec'),('zh-CN','简体中文','ef476f'),('ru','Русский','577590')]
MODEL='https://evolink.ai/claude-opus-5-5'
DOCS='https://evolink.ai/docs/en/api-manual/language-series/claude/claude-messages-api'
KEYS='https://evolink.ai/dashboard/keys'
SLOTS={'banner':(MODEL,'banner','readme_banner'),'badge':(MODEL,'badge','top_badge'),'introduction':(MODEL,'readme','introduction_cta'),'model':(MODEL,'quickstart','model_link'),'keys':(KEYS,'quickstart','api_key'),'docs':(DOCS,'docs','first_run'),'footer':(MODEL,'footer','footer_cta')}

def read_json(path):return json.loads(path.read_text())
def filename(lang):return 'README.md' if lang=='en' else f'README_{lang}.md'
def escape(text):return text.replace('|','\\|').replace('[','\\[').replace(']','\\]')
def display_author(value):return '@'+value.lstrip('@')
def paragraphs(notes):return [notes] if isinstance(notes,str) else notes

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--locale',choices=[x[0] for x in LANGS]);args=parser.parse_args()
    data=read_json(ROOT/'data/use-cases.json');cases=data['items']
    hosted=read_json(ROOT/'data/r2-media.json')
    def asset(path):
        record=hosted['assets'][path]
        if not record['verified'] or not record['url'].startswith(hosted['public_base_url']+'/'+hosted['prefix']+'/'):
            raise ValueError('Missing verified R2 asset: '+path)
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=record['sha256']:
            raise ValueError('R2 asset differs from local file: '+path)
        return record['url']
    def badge(url):return asset(hosted['badge_sources'][url])
    verified_urls={record['url'] for record in hosted['assets'].values() if record['verified']}
    def hosted_url(url):
        if url not in verified_urls or not url.startswith(hosted['public_base_url']+'/'+hosted['prefix']+'/'):
            raise ValueError('Unverified or non-R2 presentation URL')
        return url
    urls={slot:target+'?'+urlencode({'utm_source':'github','utm_medium':medium,'utm_campaign':read_json(ROOT/'data/presentation.json')['repository_slug'],'utm_content':content}) for slot,(target,medium,content) in SLOTS.items()}
    badges='\n'.join(f'[![{name}]({badge("https://img.shields.io/badge/"+quote(name,safe="")+"-"+color)})]({filename(lang)})' for lang,name,color in LANGS)
    selected=[args.locale] if args.locale else [x[0] for x in LANGS]
    for lang in selected:
        source=read_json(ROOT/f'data/locales/{lang}.json');labels=source['labels'];cover_label=read_json(ROOT/'data/cover-labels.json')[lang];cover_font={'zh-CN':'Microsoft YaHei','zh-TW':'Hiragino Sans GB','ja':'Hiragino Sans','ko':'Apple SD Gothic Neo'}.get(lang,'Arial');what=read_json(ROOT/'data/menu-labels.json')[lang];copy={c['public_number']:c for c in source['items']}
        if set(copy)!=set(range(1,len(cases)+1)):raise ValueError(f'{lang}: incomplete editorial case set')
        cover='images/'+({'zh-CN':'zh','zh-TW':'zh-tw'}.get(lang,lang))+'.png';vector=f'assets/banners/{lang}.svg';(ROOT/'assets/banners').mkdir(exist_ok=True);(ROOT/'images').mkdir(exist_ok=True)
        (ROOT/vector).write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1520 460" role="img"><title>{html.escape(labels['title'])}</title><rect width="1520" height="460" rx="24" fill="#173f46"/><circle cx="1390" cy="100" r="290" fill="#24565a"/><circle cx="1320" cy="220" r="170" fill="none" stroke="#a5c8b6" stroke-width="2"/><text x="88" y="100" fill="#b7d5c3" font-family="Arial,sans-serif" font-size="28" letter-spacing="5">EVOLINK</text><text x="82" y="245" fill="#fff9ed" font-family="Arial,sans-serif" font-size="94" font-weight="700">Claude Opus 5.5</text><text x="88" y="360" fill="#c8dad1" font-family="{cover_font}" font-size="42">{len(cases)} · {html.escape(cover_label)}</text></svg>\n''')
        out=['<div align="center">',f'<a href="{html.escape(urls["banner"])}"><img src="{asset(cover)}" alt="{html.escape(labels["title"])}" width="760"></a>','',f'# {labels["title"]}',labels['subtitle'],'',f'[![License: CC BY 4.0]({badge("https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg")})](LICENSE)',f'[![EvoLink]({badge("https://img.shields.io/badge/EvoLink-173f46")})]({urls["badge"]})','',badges,'','</div>','',f'## 🍌 {labels["intro"]}','',f'**{labels["introtext"]}**','',f'[{labels["cta"]}]({urls["introduction"]})','','<a id="overview"></a>',f'## 📊 {labels["overview"]}','',labels['overviewtext'],'']
        out+=['- '+s for s in labels['overviewbullets']]
        out+=['',f'> [!NOTE]\n> {labels["note"]}','','<a id="quick-start"></a>',f'## ⚡ {labels["quick"]}','']
        out += [f'{i}. [{text}]({urls[slot]})' for i,(text,slot) in enumerate(zip(labels['steps'],['model','keys','docs']),1)]
        out+=['',f'## 📑 {labels["menu"]}','',f'| [{labels["overview"]}](#overview) | [{labels["quick"]}](#quick-start) | [{labels["related"]}](#related-repositories) | [{labels["ack"]}](#acknowledge) |','|---|---|---|---|','',f'| {labels["case"]} | {labels["category"]} | {what} | {labels["type"]} |','|---|---|---|---|']
        for c in cases:
            n=c['public_number'];out.append(f'| [{labels["case_label"]} {n}: {escape(copy[n]["title"])}](#case-{n}) | [{labels["categories"][c["category"]]}](#category-{c["category"]}) | {escape(copy[n]["takeaway"])} | {c["type"]} |')
        for category in data['categories']:
            cat_cases=[c for c in cases if c['category']==category['id']]
            if not cat_cases:continue
            out+=['',f'<a id="category-{category["id"]}"></a>',f'## {"📘" if category["id"]=="official" else "🧩"} {labels["categories"][category["id"]]}','']
            for c in cat_cases:
                n=c['public_number'];ed=copy[n]
                out += [f'<a id="case-{n}"></a>',f'### {labels["case_label"]} {n}: [{escape(ed["title"])}]({c["source_url"]}) ({labels["by_label"]} [{display_author(c["author_handle"])}]({c["author_url"]}))','',f'**{ed["takeaway"]}**','']
                for note in paragraphs(ed['body_notes']):out += [note,'']
                if c['media']:
                    out += ['<table>']
                    for start in range(0,len(c['media']),2):
                        out += ['<tr>']
                        for j,m in enumerate(c['media'][start:start+2],start+1):
                            preview=hosted_url(m['r2_preview_url']);dest=hosted_url(m['r2_video_url']) if m['kind']=='video' else c['source_url'];label=labels['play'] if m['kind']=='video' else labels['media']
                            out += [f'<td><a href="{html.escape(dest)}"><img src="{preview}" alt="{html.escape(ed["title"])} — {html.escape(labels["media"])} {j}" width="420"></a><br><a href="{html.escape(dest)}">{label} {j}</a></td>']
                        out+=['</tr>']
                    out+=['</table>','']
                if c['supporting_sources']:
                    out += [labels['support']+': '+', '.join(f'[{s["author"]}]({s["source_url"]})' for s in c['supporting_sources']),'']
                out += [f'Type: {c["type"]} | Date: {c["date"]}','','---','']
        out += ['<a id="related-repositories"></a>','## Related Repositories' if lang=='en' else f'## 🔗 {labels["related"]}','',labels['relatedtext'],'','- [Claude Code](https://github.com/anthropics/claude-code)','- [Claude Cookbooks](https://github.com/anthropics/claude-cookbooks)','','<a id="acknowledge"></a>',f'## 🙏 {labels["ack"]}','',labels['acktext'],'']
        authors=list(dict.fromkeys((display_author(c['author_handle']),c['author_url']) for c in cases))
        out += [', '.join(f'[{author}]({url})' for author,url in authors),'',labels['foot'],'',f'[{labels["cta"]}]({urls["footer"]})','']
        (ROOT/filename(lang)).write_text('\n'.join(out))
    (ROOT/'data/utm-matrix.json').write_text(json.dumps([{'placement':slot,'url':url} for slot,url in urls.items()],indent=2)+'\n')
    inventory=['# Curated use case inventory','', 'Generated from `use-cases.json` and `locales/en.json`; do not edit this index directly.','', '| Case | Title | Type | Date | Category | Source |','|---|---|---|---|---|---|']
    for c in cases:
        n=c['public_number'];inventory.append(f'| [Case {n}](../README.md#case-{n}) | {escape(c["title"])} | {c["type"]} | {c["date"]} | {c["category"]} | [{c["author_handle"]}]({c["source_url"]}) |')
    (ROOT/'data/use-cases.md').write_text('\n'.join(inventory)+'\n')
    print(f'Rendered {len(cases)} cases in {len(selected)} README files')

if __name__=='__main__':main()
