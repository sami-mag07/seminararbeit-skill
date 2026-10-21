#!/usr/bin/env python3
"""PDF in Text mit Seitenmarkern umwandeln.

Aufruf: python3 tools/pdf_text.py quellen/pdf/datei.pdf [--offset N]

Schreibt quellen/text/<name>.txt mit Zeilen "[Seite N]" vor jeder Seite.
--offset verschiebt die Zählung, wenn die gedruckte Seitenzahl nicht der
PDF-Seite entspricht (z. B. --offset -4, wenn PDF-Seite 5 die gedruckte 1 ist).
"""
from __future__ import annotations

import argparse
import pathlib
import sys

from pypdf import PdfReader

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--offset", type=int, default=0)
    args = ap.parse_args()

    pdf = pathlib.Path(args.pdf)
    reader = PdfReader(str(pdf))
    out = ROOT / "quellen" / "text" / (pdf.stem + ".txt")
    leer = 0
    with out.open("w", encoding="utf-8") as f:
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                leer += 1
            f.write(f"[Seite {i + args.offset}]\n{text}\n\n")
    print(f"{out.relative_to(ROOT)}: {len(reader.pages)} Seiten, {leer} ohne Text")
    if leer > len(reader.pages) / 2:
        print("WARNUNG: Scan ohne Textebene, Zitate daraus nicht prüfbar.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
