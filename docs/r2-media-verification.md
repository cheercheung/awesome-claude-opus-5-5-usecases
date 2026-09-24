# R2 media verification — 2026-09-24

R2 media hosting is complete. Git remains local with no remote or push.

| Check | Result |
|---|---|
| Uploaded and verified objects | 558 |
| Uploaded bytes | 3,447,072,419 (3.21 GiB) |
| Video files | 154 MP4s |
| Displayed case visuals | 215: 154 extracted video posters and 61 source images |
| README languages | 11 |
| Hosted covers and badges | 11 PNG covers and 13 SVG badges |
| Additional archived assets | Original previews and editable SVG covers |
| Failed transfers | 0 |
| README source-CDN references | 0 |
| MP4 files tracked in Git | 0 |

Every object used a Content-MD5 upload checksum and passed S3 HEAD checks for byte length, SHA-256 metadata, MIME type and inline disposition. Static assets passed full public GET byte comparison. Each video passed public HTTP 206 first/last range byte comparison and local ffprobe checks. All extracted posters decoded successfully, with no near-uniform blank candidates.

One R2 video was additionally decoded and played in a browser: media ID `2102467313874178048`, 1080×1080, 29.376 seconds, no playback error. This is a playback sample, not a browser test of all 154 videos.

All 11 README files use verified R2 URLs for displayed images and video playback. Raw source URLs remain in the provenance data. The generator rejects source-CDN fallback and local asset/hash mismatches. Clean-copy build and validation, the shared R2 handoff, usecase and localization checks passed.

The public registry is [data/r2-media.json](../data/r2-media.json). Detailed upload/readback evidence is retained locally under `.codex/production/20260924-r2/`. GitHub rendering/camo checks and paid model API calls were not performed; these media checks do not establish GitHub publication.
