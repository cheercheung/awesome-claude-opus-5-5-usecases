# Maintenance

## Source of truth

`data/use-cases.json` owns the selected cases, original intake numbers, three supplied language copies, source dates and full root-post attachment slots. `data/curation-decisions.json` accounts for all 221 supplied entries: 208 selected, nine merged, four held for insufficient evidence. `data/source-fidelity-manifest.json` records immutable input hashes and the expected media denominator. `data/media-manifest.json` records downloaded preview hashes.

The complete original 221-case and 520-source snapshots are retained under the ignored local evidence directory `.codex/production/20260923-local/`. They are not an open license for republishing original posts. Supporting-source references retain the excluded duplicate/follow-up evidence without counting it as another experiment.

## Case format

Use a stable `<a id="case-N"></a>` immediately before `### Case N: [Title](source) (by [author](profile))`, a bold factual takeaway, source notes, all media, and `Type: Demo|Tutorial|Evaluation|Integration|Benchmark|Limit | Date: YYYY-MM-DD`. The displayed date is the source publication date in UTC. Record import dates separately. No quality stars appear in public headings. Official guides and official showcases have their own category.

## Update checklist

1. Preserve the collector timestamp and immutable source package; review every candidate before mutation
2. Deduplicate source URLs and media IDs; distinguish follow-ups from independent experiments
3. Fix title, takeaway, original source/publisher, source date, category, type and caveats; record every selection or exclusion
4. Preserve every root-post attachment. Quoted-post media is separately referenced context, not automatically an output from the quoting author
5. Update every supplied locale semantically. Do not create untranslated language shells
6. Download preview images, regenerate the README and local browser, validate the result, and inspect the rendered view
7. Public release is a separate requested action: complete the remaining locales, R2 media migration, video origin checks, live link audit, GitHub render verification, metadata and runtime evidence. Never treat local preview success as publication

## Commands

```bash
python3 scripts/fetch_previews.py
python3 scripts/build.py
python3 scripts/validate.py
python3 -m http.server 8765 --bind 127.0.0.1
```

`fetch_previews.py` accepts `--proxy http://127.0.0.1:PORT` if needed. It downloads original source image bytes and does not upload anything. Open `preview/index.html` directly for the searchable local browser; a server is optional. Playback uses the source video URL and requires internet access. Full videos are not cached.

## Local scope

This edition includes English, Simplified Chinese and Japanese from the supplied editorial dataset. The initial usecase scaffold workflow permits an English source; the two complete supplied translations are included for review. It does not claim the full 11-language publication contract. The banner is a local SVG; all case preview assets are local. There is no remote configured and no publication automation.
