#!/usr/bin/env python3
"""Entrypoint for the news-image-20261126 entry (v5).

The page is pre-rendered and shipped in this repository as entry.png.
This script only copies those bytes to the output directory and verifies
the copy. It renders nothing, imports nothing beyond the standard library,
and needs no network, and no other files.
"""

import hashlib
import os
from pathlib import Path

EXPECTED_SHA256 = "a1be59d04a381f3fd87e9138a301dfd66ad1de628655bd3de9fad37bd7f1bd9b"


def main():
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    data = source.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a PNG file")
    digest = hashlib.sha256(data).hexdigest()
    if EXPECTED_SHA256 != "PLACEHOLDER" and digest != EXPECTED_SHA256:
        raise SystemExit("entry.png checksum mismatch: %s" % digest)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    dest = Path(out_dir) / "entry.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    check = hashlib.sha256(dest.read_bytes()).hexdigest()
    if check != digest:
        raise SystemExit("written copy checksum mismatch")
    print("wrote %s (%d bytes, sha256 %s)" % (dest, len(data), digest))


if __name__ == "__main__":
    main()
