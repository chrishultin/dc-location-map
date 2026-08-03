#!/usr/bin/env python3
"""Extract the DC34 room list PDF into rooms.json.

The PDF's table is laid out two entries per printed row (split down the middle),
so each row is either 8 columns (Room, Floor, Name, Type twice) or 4 on the
final page. pdfplumber's ruling-line based table extraction handles both.
"""

import json
import re
import sys
from pathlib import Path

import pdfplumber

PDF = Path(__file__).parent / "DC34_room_number_to_room_name_list_withlines.pdf"
OUT = Path(__file__).parent / "rooms.json"

HEADER = ["Room", "Floor", "DEF CON Name", "Type"]
TYPES = {"Contest", "Village", "Stage/Workshop", "Goon", "Community", "Vendors", "Exhibitor"}


def clean(cell):
    """Collapse whitespace/newlines that pdfplumber leaves inside a cell."""
    return re.sub(r"\s+", " ", (cell or "")).strip()


def sort_key(entry):
    """Numeric rooms first in numeric order, then W-prefixed, then unknowns."""
    room = entry["room"]
    if room.isdigit():
        return (0, int(room), "", entry["name"].lower())
    m = re.fullmatch(r"([A-Za-z]+)(\d+)", room)
    if m:
        return (1, int(m.group(2)), m.group(1).upper(), entry["name"].lower())
    return (2, 0, room, entry["name"].lower())


def main():
    entries = []
    with pdfplumber.open(PDF) as pdf:
        for page_no, page in enumerate(pdf.pages, 1):
            for table in page.extract_tables():
                for row in table:
                    cells = [clean(c) for c in row]
                    # Each printed row holds one or two logical entries.
                    for i in range(0, len(cells), 4):
                        chunk = cells[i:i + 4]
                        if len(chunk) < 4:
                            continue
                        room, floor, name, rtype = chunk
                        if chunk == HEADER:
                            continue
                        if not any(chunk):
                            continue
                        if rtype not in TYPES:
                            print(f"warn: page {page_no} unexpected type {chunk!r}", file=sys.stderr)
                        entries.append({
                            "room": room,
                            "floor": floor,
                            "name": name,
                            "type": rtype,
                            "page": page_no,
                        })

    # The two printed columns overlap by one row on page 1 (room 300 is both the
    # last left-hand row and the first right-hand row), so drop exact repeats.
    seen, deduped = set(), []
    for e in entries:
        key = (e["room"], e["floor"], e["name"], e["type"])
        if key in seen:
            print(f"note: dropped duplicate row {key}", file=sys.stderr)
            continue
        seen.add(key)
        deduped.append(e)
    entries = deduped

    entries.sort(key=sort_key)
    for i, e in enumerate(entries, 1):
        e["id"] = i

    OUT.write_text(json.dumps(entries, indent=2) + "\n")

    print(f"{len(entries)} entries -> {OUT.name}")
    print(f"{len({e['room'] for e in entries})} distinct rooms")
    by_type = {}
    for e in entries:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
    for t, n in sorted(by_type.items(), key=lambda kv: -kv[1]):
        print(f"  {t:<15} {n}")


if __name__ == "__main__":
    main()
