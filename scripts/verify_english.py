#!/usr/bin/env python3
"""Fail when the English fork can expose hard-coded CJK text to players.

Optional translated language packs under src/main/resources/languages are intentionally
ignored because options.enable-translations=false forces the server's English language.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def java_strings(text: str):
    """Yield (offset, literal) for Java string/text-block literals, skipping comments/chars."""
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("//", i):
            end = text.find("\n", i + 2)
            i = n if end < 0 else end + 1
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
        elif text.startswith('"""', i):
            start = i
            end = text.find('"""', i + 3)
            i = n if end < 0 else end + 3
            yield start, text[start:i]
        elif text[i] == '"':
            start = i
            i += 1
            escaped = False
            while i < n:
                ch = text[i]
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    i += 1
                    break
                i += 1
            yield start, text[start:i]
        elif text[i] == "'":
            # Character literals can contain quote-like text and must not confuse the scanner.
            i += 1
            escaped = False
            while i < n:
                ch = text[i]
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == "'":
                    i += 1
                    break
                i += 1
        else:
            i += 1


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def verify(root: Path) -> list[str]:
    problems: list[str] = []
    java_root = root / "src/main/java"
    resources = root / "src/main/resources"

    for path in java_root.rglob("*.java"):
        text = path.read_text(encoding="utf-8")
        for offset, literal in java_strings(text):
            if CJK.search(literal):
                rel = path.relative_to(root)
                problems.append(f"{rel}:{line_number(text, offset)} contains hard-coded CJK text: {literal[:120]}")

    # These files are installed as the server's defaults and should be readable in English.
    default_resources = [resources / name for name in ("config.yml", "block-storage.yml", "profile-storage.yml", "plugin.yml")]
    default_resources.extend((resources / "languages/en").rglob("*.yml"))
    for path in default_resources:
        text = path.read_text(encoding="utf-8")
        if CJK.search(text):
            for number, line in enumerate(text.splitlines(), 1):
                if CJK.search(line):
                    problems.append(f"{path.relative_to(root)}:{number} contains CJK text: {line.strip()}")

    config = (resources / "config.yml").read_text(encoding="utf-8")
    required = {
        "language: en": "The default server language must be English.",
        "enable-translations: false": "Per-player language overrides must remain disabled.",
        "auto-update: false": "The in-plugin updater would replace this build with untranslated upstream output.",
    }
    for needle, message in required.items():
        if needle not in config:
            problems.append(f"src/main/resources/config.yml: missing `{needle}`. {message}")

    localization = (java_root / "io/github/thebusybiscuit/slimefun4/core/services/LocalizationService.java").read_text(
        encoding="utf-8"
    )
    if "if (!translationsEnabled)" not in localization:
        problems.append("LocalizationService no longer forces the server language when translations are disabled.")

    item_file = java_root / "io/github/thebusybiscuit/slimefun4/implementation/SlimefunItems.java"
    item_text = item_file.read_text(encoding="utf-8")
    item_count = len(re.findall(r"public\s+static\s+final\s+SlimefunItemStack\s+[A-Z][A-Z0-9_]*\s*=", item_text))
    if item_count < 536:
        problems.append(f"SlimefunItems declares only {item_count} items; expected at least 536 from the tracked base.")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    problems = verify(root)
    if problems:
        print("English verification failed:", file=sys.stderr)
        for problem in problems:
            print(f" - {problem}", file=sys.stderr)
        return 1
    print("English verification passed: no player-facing hard-coded CJK text was found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
