#!/usr/bin/env python3
"""Restore optional source previews from verified R2 records without changing evidence."""
import argparse, concurrent.futures, hashlib, json, subprocess
from pathlib import Path
R = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--proxy')
p.add_argument('--id', help='Restore only this source media ID')
a = p.parse_args()
data = json.loads((R/'data/use-cases.json').read_text())
registry = json.loads((R/'data/r2-media.json').read_text())
media = [m for c in data['items'] for m in c['media'] if not a.id or m['id'] == a.id]
if not media:
    p.error('No matching source media')

def fetch(m):
    target = R/m['local_preview']
    record = registry['assets'][m['local_preview']]
    expected = m['local_sha256']
    if not record['verified'] or record['sha256'] != expected or record['url'] != m['r2_source_preview_url']:
        return {'id': m['id'], 'status': 'failed', 'error': 'R2/source integrity mismatch'}
    if target.exists():
        valid = hashlib.sha256(target.read_bytes()).hexdigest() == expected
        return {'id': m['id'], 'status': 'cached' if valid else 'failed'}
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(target.suffix+'.partial')
    cmd = ['curl', '--fail', '--location', '--silent', '--show-error', '--retry', '2', '--connect-timeout', '12', '--max-time', '90', record['url'], '--output', str(temp)]
    if a.proxy:
        cmd[1:1] = ['--proxy', a.proxy]
    try:
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode or hashlib.sha256(temp.read_bytes()).hexdigest() != expected:
            return {'id': m['id'], 'status': 'failed', 'error': 'R2 download/checksum failed'}
        temp.replace(target)
        return {'id': m['id'], 'status': 'downloaded'}
    finally:
        temp.unlink(missing_ok=True)

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    rows = list(pool.map(fetch, media))
failed = [r for r in rows if r['status'] == 'failed']
print(json.dumps({'expected': len(media), 'checked': len(rows), 'failures': len(failed), 'errors': failed}))
raise SystemExit(bool(failed))
