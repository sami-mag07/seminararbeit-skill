#!/usr/bin/env python3
"""Zeichen mit Leerzeichen zählen, wie das Word-Statistikfeld.

Aufruf: python3 tools/zeichen.py kapitel/*.md

Zählt Fließtext ohne Markdown-Überschriften, Tabellen und Bildzeilen.
Ziel laut Kurs: 25.500 Zeichen, erlaubt 22.950 bis 28.050.
Einleitung: 1.500 bis 1.650 Zeichen.
"""
from __future__ import annotations

import pathlib
import re
import sys

ZIEL, MIN, MAX = 25_500, 22_950, 28_050


def fliesstext(md: str) -> str:
    keep = []
    for line in md.splitlines():
        s = line.strip()
        if s.startswith(("#", "|", "![", "<!--")):
            continue
        keep.append(re.sub(r"[*_`]", "", line))
    return re.sub(r"\n{2,}", "\n", "\n".join(keep)).strip()


def main() -> int:
    gesamt = 0
    for p in sys.argv[1:]:
        path = pathlib.Path(p)
        n = len(fliesstext(path.read_text(encoding="utf-8")).replace("\n", " "))
        gesamt += n
        hinweis = ""
        if "einleitung" in path.name.lower() and not 1500 <= n <= 1650:
            hinweis = "  <- Einleitung soll 1.500 bis 1.650 Zeichen haben"
        print(f"{n:>7}  {path.name}{hinweis}")
    status = "OK" if MIN <= gesamt <= MAX else ("ZU KURZ" if gesamt < MIN else "ZU LANG")
    print(f"{gesamt:>7}  gesamt  ({status}, Ziel {ZIEL}, erlaubt {MIN} bis {MAX})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
