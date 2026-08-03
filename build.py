#!/usr/bin/env python3
"""Inline rooms.json into index.html so the page is a single static file.

Run after extract.py, or whenever rooms.json changes:

    python3 extract.py && python3 build.py
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "rooms.json"
PAGE = HERE / "index.html"

MARKER = re.compile(
    r'(<script id="room-data" type="application/json">\n).*?(\n</script>)',
    re.DOTALL,
)

# The page only needs these fields; `page` is provenance for rooms.json alone.
FIELDS = ("id", "room", "floor", "name", "type")


def main():
    entries = json.loads(DATA.read_text())
    slim = [{k: e[k] for k in FIELDS} for e in entries]
    payload = json.dumps(slim, separators=(",", ":"), ensure_ascii=False)
    # Can't let a name close the <script> block early.
    payload = payload.replace("<", "\\u003c")

    html = PAGE.read_text()
    if not MARKER.search(html):
        raise SystemExit("error: room-data script block not found in index.html")

    # Function replacement, so backslashes in the payload pass through verbatim.
    updated = MARKER.sub(lambda m: m.group(1) + payload + m.group(2), html, count=1)
    PAGE.write_text(updated)

    print(f"inlined {len(slim)} entries ({len(payload):,} bytes) into {PAGE.name}")


if __name__ == "__main__":
    main()
