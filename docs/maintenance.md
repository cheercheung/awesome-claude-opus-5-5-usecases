# Maintenance

## Source of truth

`data/use-cases.json` owns the 208 selected case identities, source URLs, publishers, source publication dates, categories, evidence types, supporting references and complete source attachment slots. `data/locales/en.json` owns the English editorial text: a single takeaway sentence followed by source-grounded notes. The other ten files in `data/locales/` contain reviewed translations. `data/localization-review-index.json` binds each review to the English and localized file hashes and all 208 case IDs. `data/use-cases.md` is the generated English inventory. Scripts render those authored texts; they do not translate prose.

`data/curation-decisions.json` accounts for all 221 supplied entries: 208 selected, nine duplicate works or follow-ups merged, four held for insufficient evidence. The original intake number remains on every case. `data/source-fidelity-manifest.json` binds the immutable source hashes and expected media denominator. `data/media-manifest.json` records original preview hashes. `data/r2-media.json` owns verified R2 object URLs, SHA256, MIME types and readback evidence for display/playback assets; source CDN URLs remain provenance only. Full original source snapshots and review evidence stay in ignored `.codex/production/` directories.

## Public artifact boundary

README files, reviewed data, the owner-provided banner original, generators, validators and community/maintenance files belong to the repository. R2-hosted image, poster and badge copies are optional ignored caches under `assets/`; they are not committed. Source exports, candidate handoff packages, API responses, review logs and run reports are local working evidence and stay under ignored `.codex/`. Never commit credentials or private exports.

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

For the English phase, use `python3 scripts/build.py --locale en`. The full validator requires exactly 11 README files and checks all reviewed data, takeaways, notes, retention of source numeric literals, sources, metadata, anchors, Menu links, R2/source hash mappings, any present local cache hashes and UTM slots. GitHub Actions runs the same deterministic build and validation after a future authorized push. Semantic review records separately cover numerical meaning, conditions and evidence limits; literal checks alone are not proof of translation quality. The repository needs no web server or frontend application.

`python3 scripts/fetch_previews.py` optionally restores original source-preview bytes from verified R2 URLs into ignored `assets/media/`. Add `--id MEDIA_ID` for one image or `--proxy http://127.0.0.1:PORT` for a caller-selected proxy. Downloads must match the recorded SHA-256; the script never rewrites the source manifest. Normal builds and offline validation do not require this cache. Offline validation checks recorded upload/readback evidence; it does not claim current network availability.

## R2 hosting and Git publication

All README display media and video playback are hosted on the configured R2 bucket, including case images, extracted video posters, language covers and badges. `scripts/build.py` requires verified R2 mappings and never falls back to a source CDN or local media URL. The original source URLs, authors and unmodified source-preview hashes are retained for provenance.

The videos are copied without transcoding. Each public video uses an extracted poster and an inline, seekable MP4 URL. Verification includes source ffprobe metadata, upload Content-MD5, object length/MIME/SHA metadata, public beginning/end range byte equality and one real browser playback sample. Images are read back in full and compared byte-for-byte.

The owner authorized publication to `cheercheung/awesome-claude-opus-5-5-usecases` on 2026-09-24. R2 hosting is maintained independently of Git push. GitHub-rendered/camo verification, live metadata/star checks and any required model API runtime evidence remain separate publication steps. See [publication checklist](publication-checklist.md).

## Banner and retired assets

`data/banner-manifest.json` maps every README locale to the unchanged owner-provided `images/banner.png`. Its verified R2 URL is rendered in the README, while the original PNG remains in Git for future editing. The build requires only Python's standard library.

Old generated SVG/PNG covers, their label data, renderer and optional rendering requirements were retired. Local copies and the previous R2 records are archived under ignored `.codex/cleanup/20260924-r2-cache/`; no R2 objects were deleted. The active R2 registry excludes those retired covers. Case origins, attachment counts, source hashes and R2 media evidence remain committed.

## Multi-video preservation

Cases 153 and 181 each contain two distinct source videos. The renderer preserves both R2 poster/playback pairs. The handoff uses one `r2_media_items` entry per original attachment, with its `source_media_id`, kind, R2 poster and R2 playback URL; a single scalar video URL cannot represent those cases. The shared verifier rejects a missing second playback URL.

### Owner-provided banner

`data/banner-manifest.json` selects the verified R2 asset for each README locale. All locales currently use the unchanged owner-provided `images/banner.png`. Previous generated covers remain archived in local evidence and R2 storage; they are absent from the active registry and README. Update the manifest and upload/verify the replacement before rebuilding.
