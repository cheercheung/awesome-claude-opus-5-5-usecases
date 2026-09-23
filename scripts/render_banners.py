#!/usr/bin/env python3
"""Rasterize the repository's editable SVG covers to template-required PNG files."""
import hashlib,json
from pathlib import Path
import cairosvg
ROOT=Path(__file__).resolve().parents[1]
manifest=[]
for source in sorted((ROOT/'assets/banners').glob('*.svg')):
    locale=source.stem;name={'zh-CN':'zh','zh-TW':'zh-tw'}.get(locale,locale)
    target=ROOT/'images'/f'{name}.png';target.parent.mkdir(exist_ok=True)
    cairosvg.svg2png(url=str(source),write_to=str(target),output_width=1520,output_height=460)
    manifest.append({'locale':locale,'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'path':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'renderer':'CairoSVG '+cairosvg.__version__,'width':1520,'height':460})
(ROOT/'data/banner-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Rendered {len(manifest)} PNG covers')
