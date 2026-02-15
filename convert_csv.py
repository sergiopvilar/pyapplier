#!/usr/bin/env python3
import csv
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

HEADER = [
    "#AUDIOSCROBBLER/1.1",
    "#TZ/UNKNOWN",
    "#CLIENT/Rockbox ipod6g $Revision$",
    "#ARTIST\t#ALBUM\t#TITLE\t#TRACKNUM\t#LENGTH\t#RATING\t#TIMESTAMP\t#MUSICBRAINZ_TRACKID",
]

def parse_args():
    p = argparse.ArgumentParser(
        description="Convert CSV (artist,album,title,DD Mon YYYY HH:MM) to Rockbox .scrobbler.log"
    )
    p.add_argument("-i", "--input", required=True, help="Input CSV file")
    p.add_argument("-o", "--output", required=True, help="Output .scrobbler.log file")
    p.add_argument("--tz", default="America/Fortaleza", help="Timezone for parsing dates (default: America/Fortaleza)")
    p.add_argument("--rating", default="L", choices=["L", "S", "B"], help="Rating to write (default: L)")
    p.add_argument("--tracknum", default="0", help="Default track number (default: 0)")
    p.add_argument("--length", default="0", help="Default track length in seconds (default: 0)")
    return p.parse_args()

def main():
    args = parse_args()
    tz = ZoneInfo(args.tz)

    in_path = Path(args.input)
    out_path = Path(args.output)

    with in_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # write output
    with out_path.open("w", encoding="utf-8", newline="\n") as out:
        out.write("\n".join(HEADER) + "\n")

        for idx, row in enumerate(rows, start=1):
            if not row or all(not c.strip() for c in row):
                continue

            if len(row) < 4:
                raise SystemExit(f"Line {idx}: expected 4 columns (artist, album, title, date), got {len(row)}: {row}")

            artist, album, title, played_at = (c.strip() for c in row[:4])

            # Parse like: "03 Feb 2026 15:02"
            try:
                dt = datetime.strptime(played_at, "%d %b %Y %H:%M").replace(tzinfo=tz)
            except ValueError as e:
                raise SystemExit(f"Line {idx}: could not parse date '{played_at}'. Expected 'DD Mon YYYY HH:MM'. Error: {e}")

            ts = int(dt.timestamp())

            # Rockbox scrobble columns:
            # ARTIST  ALBUM  TITLE  TRACKNUM  LENGTH  RATING  TIMESTAMP  MUSICBRAINZ_TRACKID
            out.write(
                f"{artist}\t{album}\t{title}\t{args.tracknum}\t{args.length}\t{args.rating}\t{ts}\t\n"
            )

    print(f"OK: wrote {out_path}")

if __name__ == "__main__":
    main()
