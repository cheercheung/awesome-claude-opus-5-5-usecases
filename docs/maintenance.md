# Maintenance

## Source of truth

`data/use-cases.json` owns the 208 selected case identities, source URLs, publishers, source publication dates, categories, evidence types, supporting references and complete source attachment slots. `data/locales/en.json` owns the English editorial text: a single takeaway sentence followed by source-grounded notes. The other ten files in `data/locales/` contain reviewed translations. `data/localization-review-index.json` binds each review to the English and localized file hashes and all 208 case IDs. `data/use-cases.md` is the generated English inventory. Scripts render those authored texts; they do not translate prose.

`data/curation-decisions.json` accounts for all 221 supplied entries: 208 selected, nine duplicate works or follow-ups merged, four held for insufficient evidence. The original intake number remains on every case. `data/source-fidelity-manifest.json` binds the immutable source hashes and expected media denominator. `data/media-manifest.json` records preview hashes. Full original source snapshots and review evidence stay in ignored `.codex/production/` directories.

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
9. Commit only intended repository files; push or public uploads are separate owner-controlled actions

## Build and validate

```bash
python3 scripts/build.py
python3 scripts/validate.py
```

For the English phase, use `python3 scripts/build.py --locale en`. The full validator requires exactly 11 README files and checks all reviewed data, takeaways, notes, retention of source numeric literals, sources, metadata, anchors, Menu links, local media hashes and UTM slots. GitHub Actions runs the same deterministic build and validation after a future authorized push. Semantic review records separately cover numerical meaning, conditions and evidence limits; literal checks alone are not proof of translation quality. The repository needs no web server or frontend application.

`python3 scripts/fetch_previews.py` restores missing preview images from recorded source URLs. An optional `--proxy http://127.0.0.1:PORT` uses a caller-selected proxy. It never uploads or publishes media.

## Local preparation versus publication

The current repository is prepared locally at the owner's request. README images are local assets and videos link to source playback URLs. Local-stage handoff results are deliberately ineligible for publication promotion. The agent's default publication verifier retains its R2 requirements.

Before remote publication, migrate public media to the approved R2 namespace, verify playable videos and GitHub-rendered images, recheck source links and current access, record required runtime evidence or a specific owner-approved waiver, then verify the public repository and metadata. See [publication checklist](publication-checklist.md). Local checks alone do not prove publication readiness.

## Cover assets

README covers use `images/en.png`, `images/zh.png`, `images/zh-tw.png` and the corresponding filenames for the other locales. Their editable SVG sources live in `assets/banners/`; `data/banner-manifest.json` binds each PNG to its source hash. Normal builds need only Python's standard library and use the committed PNG files.

When changing cover text or the case count, install the optional dependencies in an isolated environment with `python3 -m pip install -r requirements-render.txt`, ensure native Cairo and the SVG-declared fonts are available, then run `python3 scripts/render_banners.py` and inspect the PNGs. The current cover render used Microsoft YaHei, Hiragino Sans GB, Hiragino Sans and Apple SD Gothic Neo for CJK labels, and Arial for Latin/Cyrillic labels. Do not commit a missing-glyph render.

## Multi-video preservation

Cases 153 and 181 each contain two distinct source videos. The local renderer preserves both poster/playback pairs. For the publication handoff, use one `r2_media_items` entry per original attachment, with its `source_media_id`, kind, R2 poster and R2 playback URL; a single scalar video URL cannot represent those cases. The shared verifier rejects a missing second playback URL.
