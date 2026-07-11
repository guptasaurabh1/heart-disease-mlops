#!/usr/bin/env python3
"""
Fetch the UCI Heart Disease data.

The four processed.*.data files are also committed under data/raw/ so the
project runs offline and in CI without depending on the UCI mirror being up.
This script re-downloads them when you want a fresh copy, and verifies the
expected row counts so a truncated download fails loudly.

Usage:
    python data/download_data.py            # download into data/raw
    python data/download_data.py --check    # just verify what is on disk
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

BASE = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease"
RAW_DIR = Path(__file__).resolve().parent / "raw"

FILES = {
    "processed.cleveland.data": 303,
    "processed.hungarian.data": 294,
    "processed.switzerland.data": 123,
    "processed.va.data": 200,
    "heart-disease.names": None,  # documentation, no row check
}


def download() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        url = f"{BASE}/{name}"
        dest = RAW_DIR / name
        print(f"Downloading {url}")
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! failed ({exc}); keeping any bundled copy at {dest}")


def check() -> int:
    problems = 0
    for name, expected in FILES.items():
        path = RAW_DIR / name
        if not path.exists():
            print(f"MISSING {name}")
            problems += 1
            continue
        if expected is not None:
            rows = sum(1 for _ in path.open())
            flag = "ok" if rows == expected else "MISMATCH"
            if flag == "MISMATCH":
                problems += 1
            print(f"{flag:9} {name}: {rows} rows (expected {expected})")
        else:
            print(f"ok        {name}")
    return problems


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify files only")
    args = parser.parse_args()
    if not args.check:
        download()
    sys.exit(1 if check() else 0)
