# DEF CON 34 Room Finder

A single-file static page for looking up what's in a DEF CON 34 room — or which
room something is in. Built from `DC34_room_number_to_room_name_list_withlines.pdf`.

Open `index.html`. That's it — no server, no build, no network. It works from
`file://`, off a USB stick, or on any static host (GitHub Pages, S3, whatever).

## What it does

- **Search** room numbers (`1216`), names (`lock pick`), and types (`village`),
  all at once. Filter by type and floor with the chips.
- **Typo-tolerant.** The source PDF has its own spelling slips — *Cyrpto*,
  *Viliage*, *Industires*, *Sublmage* — so exact matching isn't enough.
  Searches run strict first and only fall back to fuzzy matching when strict
  finds nothing, so a well-spelled query stays precise. Room numbers are never
  fuzzed: `1216` shouldn't drag in 1210 through 1217.
- **Knows DEF CON shorthand.** `btv`, `phv`, `hhv`, `lpv`, `eff` and friends
  resolve to the right village. Edit `ALIASES` in `index.html` to add more.
- **Cross-references.** A room can hold more than one thing (103 is both Tinfoil
  Hat Contest and Untechnical) and one village can span several rooms (Blue Team
  Village is W213–W217). Cards show both.
- Shareable searches via the URL hash (`index.html#q=cloud+village`),
  `/` to focus search, `Esc` to clear, light and dark themes.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The page. Data is inlined, so this file alone is the whole app. |
| `rooms.json` | The extracted data, and the source of record. |
| `extract.py` | PDF → `rooms.json`. |
| `build.py` | Inlines `rooms.json` into `index.html`. |

## Rebuilding

Only needed if the PDF changes or you hand-edit `rooms.json`:

```bash
pip3 install pdfplumber && python3 extract.py && python3 build.py
```

`extract.py` reads the PDF's ruling lines to recover the table. Each printed row
holds *two* entries side by side (the list is split down the middle), which the
table extraction unpacks into one record each — 215 entries across 208 rooms.
Page 1's two columns overlap by one row (room 300 appears at the bottom of the
left column and the top of the right), so exact duplicate rows are dropped; the
script prints a note when that happens.

Each record:

```json
{ "id": 1, "room": "100", "floor": "1", "name": "Contest Stage", "type": "Contest", "page": 1 }
```

`page` is the source PDF page, kept in `rooms.json` for provenance and stripped
from the copy inlined into the page.

## Caveats

Names, spellings, and floor numbers are reproduced exactly as the PDF has them —
including the typos. Thirteen entries are listed as `?` in the source and show as
*Unlisted*; one entry has no room number assigned.

Unofficial, and rooms move. Confirm against the official program on site.
