#!/usr/bin/env python3
"""Entrypoint for the news-image-20261126 v3 submission.

Renders the front page with gen.py and places the finished PNG at
/output/entry.png, exactly where the bounty harness expects it.
No network, no randomness: the same source always yields the same bytes.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from gen import build  # noqa: E402


def out_path():
    dest = os.environ.get("OUTPUT_DIR", "/output")
    return os.path.join(dest, "entry.png")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def run():
    target = out_path()
    os.makedirs(os.path.dirname(target), exist_ok=True)
    page = build()
    if page.size != (1024, 1024):
        raise SystemExit("unexpected page size: %r" % (page.size,))
    page.save(target, format="PNG")
    print("entry:", target)
    print("size:", page.size)
    print("sha256:", sha256_of(target))


if __name__ == "__main__":
    run()
