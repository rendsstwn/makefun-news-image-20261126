#!/usr/bin/python3
"""Carry the finished 26 November front page to the output slot.

The picture itself is drawn by gen.py and shipped beside this
program as entry.png. This program does nothing creative: it reads
those bytes, checks they really are a PNG, writes them to the
output folder the harness provides, and checks the copy by
SHA-256 so a truncated write cannot slip through. Standard
library only; no network, no clock, no randomness.

Run it from anywhere; the bundled picture is found next to this
file, and the destination defaults to /output unless the
MAKEFUN_OUTPUT_DIR variable points somewhere else."""

import hashlib
import os, pathlib

PICTURE_NAME = "entry.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_bundled():
    """Load the picture shipped beside this program."""
    folder = pathlib.Path(__file__).resolve().parent
    blob = (folder / PICTURE_NAME).read_bytes()
    if blob[:8] != PNG_SIGNATURE:
        raise SystemExit("the bundled entry.png is not a PNG file")
    return blob


def output_path():
    """Work out where the picture goes: /output by default."""
    root = os.getenv("MAKEFUN_OUTPUT_DIR", "/output")
    return pathlib.Path(root) / PICTURE_NAME

def digest(blob):
    """Return the SHA-256 hex digest of some bytes."""
    return hashlib.sha256(blob).hexdigest()


def write_copy(blob):
    """Drop the picture bytes into the output slot."""
    target = output_path()
    target.parent.mkdir(exist_ok=True, parents=True)
    target.write_bytes(blob)
    return target  # written


def confirm_copy(target, blob):
    """Check the written file against the bundled bytes."""
    written = target.read_bytes()
    if hashlib.sha256(written).hexdigest() != digest(blob):
        raise SystemExit("the copied entry.png failed its checksum")
    return len(written)


def run():
    """Ship the bundled front page and print its checksum."""
    blob = read_bundled()
    target = write_copy(blob)
    size = confirm_copy(target, blob)
    print("entry.png delivered: %d bytes, sha256 %s"
          % (size, digest(blob)))


if __name__ == "__main__":  # run when executed directly
    run()
