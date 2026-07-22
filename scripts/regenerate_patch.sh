#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM_DIR="${1:-}"
OUTPUT="${2:-$ROOT_DIR/patches/albion-english.patch}"
if [[ "$OUTPUT" != /* ]]; then
  OUTPUT="$(pwd)/$OUTPUT"
fi

if [[ -z "$UPSTREAM_DIR" || ! -d "$UPSTREAM_DIR/src" ]]; then
  echo "Usage: $0 /path/to/clean/Slimefun4 [output.patch]" >&2
  exit 2
fi

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
mkdir -p "$WORK_DIR/a" "$WORK_DIR/b"
cp -a "$UPSTREAM_DIR/src" "$WORK_DIR/a/src"
cp -a "$ROOT_DIR/src" "$WORK_DIR/b/src"

mkdir -p "$(dirname "$OUTPUT")"
cd "$WORK_DIR"
# git diff returns 1 when differences are found, which is expected here.
set +e
git diff --no-index --binary --src-prefix= --dst-prefix= a/src b/src > "$OUTPUT"
STATUS=$?
set -e

if [[ $STATUS -gt 1 ]]; then
  echo "Failed to generate patch (git diff exit $STATUS)." >&2
  exit "$STATUS"
fi

if [[ ! -s "$OUTPUT" ]]; then
  echo "No differences were found; refusing to write an empty maintained patch." >&2
  exit 1
fi

printf 'Wrote maintained patch: %s\n' "$OUTPUT"
