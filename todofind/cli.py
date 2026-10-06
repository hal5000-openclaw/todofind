"""Scan a directory tree for TODO/FIXME/HACK/XXX comments."""
import argparse
import json
import os
import re
import sys

TAGS = ("TODO", "FIXME", "HACK", "XXX")
SKIP_DIRS = {".git", "node_modules"}
PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b[:\s(]*(.*)")
COMMENT = re.compile(r"(#|//|/\*|\*|--|;|<!--|%)")


def is_binary(path):
    try:
        with open(path, "rb") as f:
            return b"\0" in f.read(8192)
    except OSError:
        return True


def scan_file(path, tags=TAGS):
    results = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for n, line in enumerate(f, 1):
                m = PATTERN.search(line)
                if not m or m.group(1) not in tags:
                    continue
                if not COMMENT.search(line[:m.start()]):
                    continue
                text = m.group(2).strip().rstrip("*/").replace("-->", "").strip()
                results.append({"file": path, "line": n, "tag": m.group(1), "text": text})
    except OSError:
        pass
    return results


def scan(root, tags=TAGS):
    results = []
    if os.path.isfile(root):
        return [] if is_binary(root) else scan_file(root, tags)
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(d for d in dns if d not in SKIP_DIRS)
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            if os.path.islink(p) or is_binary(p):
                continue
            results.extend(scan_file(p, tags))
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(prog="todofind", description=__doc__)
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--tag", action="append", type=str.upper, choices=TAGS,
                    help="only this tag (repeatable)")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--fail", action="store_true", help="exit 1 if any found")
    a = ap.parse_args(argv)
    res = scan(a.path, tuple(a.tag) if a.tag else TAGS)
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        for r in res:
            print(f"{r['file']}:{r['line']}: {r['tag']} {r['text']}")
    return 1 if (a.fail and res) else 0


if __name__ == "__main__":
    sys.exit(main())
