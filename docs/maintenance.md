# Maintenance

## Source of truth

`data/use-cases.json` owns the 208 selected case identities, source URLs, publishers, source publication dates, categories, evidence types, supporting references and complete source attachment slots. `data/locales/en.json` owns the English editorial text: a single takeaway sentence followed by source-grounded notes. The other ten files in `data/locales/` contain reviewed translations. `data/localization-review-index.json` binds each review to the English and localized file hashes and all 208 case IDs. `data/use-cases.md` is the generated English inventory. Scripts render those authored texts; they do not translate prose.

`data/curation-decisions.json` accounts for all 221 supplied entries: 208 selected, nine duplicate works or follow-ups merged, four held for insufficient evidence. The original intake number remains on every case. `data/source-fidelity-manifest.json` binds the immutable source hashes and expected media denominator. `data/media-manifest.json` records original preview hashes. `data/r2-media.json` owns verified R2 object URLs, SHA256, MIME types and readback evidence for display/playback assets; source CDN URLs remain provenance only. Full original source snapshots and review evidence stay in ignored `.codex/production/` directories.

## Public artifact boundary

README files, reviewed data, local assets, generators, validators and community/maintenance files belong to the repository. Source exports, candidate handoff packages, API responses, review logs and run reports are local working evidence and stay under ignored `.codex/`. Never commit credentials or private exports.

## Case format

Use a stable `<a id="case-N"></a>` immediately before a level-three source-linked case heading. English uses `### Case N: [Title](source) (by [@author](profile))`; localized labels may vary while anchors, numbers, source URLs and author identity remain unchanged. The visible `@` prefix is a formatting convention; Hacker News usernames still link to their original Hacker News profiles, not to an inferred X account.

Each case has exactly one bold takeaway sentence, followed by normal source-content notes, all associated media and `Type: Demo|Tutorial|Evaluation|Integration|Benchmark|Limit | Date: YYYY-MM-DD`. The displayed date is the source publication date in UTC, not the import date. Keep costs, tool dependencies, sponsorship disclosures, unfinished work and uncertainty in the notes. Never invent a prompt or independently verified result.

## Update checklist

1. Freeze the source corpus, collector timestamp and full source attachment inventory before editing
2. Review every candidate; deduplicate both source URLs and repeated media, preserving follow-up evidence as supporting references
3. Fix source, author, date, category, type, title, single-sentence takeaway and body notes
4. Run the shared usecase handoff verifier before README changes; record the verification stage and source/commit hashes
5. Edit English first and run the English gate before changing localized READMEs
6. Use language-specific semantic review for all ten translations; retain model/tool names, numeric facts, source identities and evidence limits
7. Regenerate all README files, check structure/data/media equality, and inspect the actual rendered Markdown
8. Run the relevant template, source, localization, link and portable checks; preserve failed runs and their fixes in local evidence
9. Commit only intended repository files; Git push and R2 media hosting have independent authorization boundaries; a no-push instruction does not waive R2 hosting

## Build and validate

```bash
python3 scripts/build.py
python3 scripts/validate.py
```

For the English phase, use `python3 scripts/build.py --locale en`. The full validator requires exactly 11 README files and checks all reviewed data, takeaways, notes, retention of source numeric literals, sources, metadata, anchors, Menu links, local media hashes and UTM slots. GitHub Actions runs the same deterministic build and validation after a future authorized push. Semantic review records separately cover numerical meaning, conditions and evidence limits; literal checks alone are not proof of translation quality. The repository needs no web server or frontend application.

`python3 scripts/fetch_previews.py` restores missing preview images from recorded source URLs. An optional `--proxy http://127.0.0.1:PORT` uses a caller-selected proxy. It never uploads or publishes media.

## R2 hosting and Git publication

All README display media and video playback are hosted on the configured R2 bucket, including case images, extracted video posters, language covers and badges. `scripts/build.py` requires verified R2 mappings and never falls back to a source CDN or local media URL. The original source URLs, authors and unmodified source-preview hashes are retained for provenance.

The videos are copied without transcoding. Each public video uses an extracted poster and an inline, seekable MP4 URL. Verification includes source ffprobe metadata, upload Content-MD5, object length/MIME/SHA metadata, public beginning/end range byte equality and one real browser playback sample. Images are read back in full and compared byte-for-byte.

Git remains local until the owner requests publication. R2 hosting is completed independently of Git push. GitHub-rendered/camo verification, live metadata/star checks and any required model API runtime evidence remain separate publication steps. See [publication checklist](publication-checklist.md).

## Cover assets

The local cover sources are `images/en.png`, `images/zh.png`, `images/zh-tw.png` and the corresponding filenames for the other locales; README files render their verified R2 URLs. Their editable SVG sources live in `assets/banners/`; `data/banner-manifest.json` binds each PNG to its source hash. Normal builds need only Python's standard library and use the committed PNG files.

When changing cover text or the case count, install the optional dependencies in an isolated environment with `python3 -m pip install -r requirements-render.txt`, ensure native Cairo and the SVG-declared fonts are available, then run `python3 scripts/render_banners.py` and inspect the PNGs. The current cover render used Microsoft YaHei, Hiragino Sans GB, Hiragino Sans and Apple SD Gothic Neo for CJK labels, and Arial for Latin/Cyrillic labels. Do not commit a missing-glyph render.

## Multi-video preservation

Cases 153 and 181 each contain two distinct source videos. The renderer preserves both R2 poster/playback pairs. The handoff uses one `r2_media_items` entry per original attachment, with its `source_media_id`, kind, R2 poster and R2 playback URL; a single scalar video URL cannot represent those cases. The shared verifier rejects a missing second playback URL.

### Owner-provided banner

`data/banner-manifest.json` selects the verified R2 asset for each README locale. All locales currently use the unchanged owner-provided `images/banner.png`. Previous generated covers remain archived locally and in the R2 registry; they are not used in the README. Update the manifest and upload/verify the replacement before rebuilding.
