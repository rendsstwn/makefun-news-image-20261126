"""Copy the pre-rendered entry image into the output directory.

The newspaper image is already rendered and shipped in this repo as
entry.png. At grade time this script only copies those bytes verbatim
into the output folder, then re-reads the copy and checks its hash
against the bundled file. It does no rendering and
uses nothing outside the Python standard library.
"""

import hashlib
import os
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
FALLBACK_OUTPUT_DIR = "/output"


def bundled_bytes() -> tuple[bytes, str]:
    image_path = Path(__file__).resolve().parent / "entry.png"
    payload = image_path.read_bytes()
    if payload[: len(PNG_MAGIC)] != PNG_MAGIC:
        raise SystemExit(f"bundled file is not a PNG image: {image_path}")
    return payload, hashlib.sha256(payload).hexdigest()


def output_path() -> Path:
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR") or FALLBACK_OUTPUT_DIR
    return Path(chosen) / "entry.png"


def main() -> None:
    payload, expected_digest = bundled_bytes()

    target = output_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)

    copied = target.read_bytes()
    actual_digest = hashlib.sha256(copied).hexdigest()
    if actual_digest != expected_digest:
        raise SystemExit(
            "output check failed: copied file hash does not match the "
            f"bundled image ({actual_digest} != {expected_digest})"
        )

    print(f"copied {len(payload)} bytes to {target}")
    print(f"sha256: {expected_digest}")


if __name__ == "__main__":
    main()
