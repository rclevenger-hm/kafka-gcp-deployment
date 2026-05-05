#!/usr/bin/env bash
set -euo pipefail
umask 077
install -d -m 0700 /opt/kafka-bootstrap
# The image includes Python 3 and curl. Metadata contains code and references only.
python3 - <<'PY'
import base64, gzip, json, pathlib, urllib.request
base = 'http://metadata.google.internal/computeMetadata/v1/instance/attributes/'
def get(key):
    req = urllib.request.Request(base + key, headers={'Metadata-Flavor': 'Google'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()
root = pathlib.Path('/opt/kafka-bootstrap')
files = json.loads(gzip.decompress(base64.b64decode(get('kafka-runtime'))))
if set(files) != {'provision.py', 'kafka.service', 'kafka.env', 'jmx.yml'}:
    raise ValueError('Unexpected runtime file manifest')
for name, content in files.items():
    (root / name).write_text(content)
(root / 'config.json').write_bytes(get('kafka-config'))
PY
exec python3 /opt/kafka-bootstrap/provision.py --config /opt/kafka-bootstrap/config.json
