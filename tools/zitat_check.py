#!/usr/bin/env python3
"""Prüft jedes Zitat und jeden Beleg in einem Kapitel gegen die Quellen.

Aufruf: python3 tools/zitat_check.py kapitel/04-hauptteil.md

1. Jeder Beleg (Nachname Jahr: Seite) muss in quellen.md als Kürzel stehen.
2. Jedes wörtliche Zitat „…“ mit Beleg muss im Quelltext auf genau dieser
   Seite stehen (Leerzeichen und Silbentrennung werden ignoriert).

quellen.md enthält pro Quelle eine Zeile der Form
  - Kürzel: Bödeker 2012 | Text: quellen/text/boedeker2012.txt | ...
Exit-Code 1, sobald ein Fehler gefunden wird.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

BELEG = re.compile(r"\((?:vgl\.\s*)?([^()]*?\d{4}[a-z]?)(?::\s*([\d\s,f.\-–]+))?\)")
EBD = re.compile(r"\((ebd\.?)(?::\s*([\d\s,f.\-–]+))?\)")
ZITAT = re.compile(r"„([^“]{8,}?)“\s*(\([^()]*\))")


def norm(s: str) -> str:
    s = re.sub(r"-\s*\n\s*", "", s)  # Silbentrennung am Zeilenende
    s = re.sub(r"\[\s*…\s*\]|\[\.\.\.\]", " ", s)
    s = re.sub(r"[„“\"'‚‘’]", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def quellen() -> dict[str, pathlib.Path | None]:
    out: dict[str, pathlib.Path | None] = {}
    for line in (ROOT / "quellen.md").read_text(encoding="utf-8").splitlines():
        m = re.search(r"Kürzel:\s*([^|]+?)\s*(?:\||$)", line)
        if not m:
            continue
        t = re.search(r"Text:\s*([^|\s]+)", line)
        out[m.group(1).strip()] = (ROOT / t.group(1)) if t else None
    return out


def seiten(path: pathlib.Path) -> dict[int, str]:
    parts = re.split(r"\[Seite (-?\d+)\]", path.read_text(encoding="utf-8"))
    return {int(parts[i]): norm(parts[i + 1]) for i in range(1, len(parts) - 1, 2)}


def erste_seite(s: str | None) -> list[int]:
    if not s:
        return []
    nums = [int(n) for n in re.findall(r"\d+", s)]
    if not nums:
        return []
    start = nums[0]
    ende = nums[1] if len(nums) > 1 and ("-" in s or "–" in s) else start
    if re.search(r"\bf\.?", s):
        ende = max(ende, start + 1)
    return list(range(start, max(start, ende) + 1))


def verzeichnis(kap: pathlib.Path, text: str) -> int:
    """Literaturverzeichnis: jeder Eintrag muss einem Harvard-Feld in quellen.md entsprechen,
    jede in Kapitel 1 bis 5 zitierte Quelle muss einen Eintrag haben."""
    harvard = {}
    for line in (ROOT / "quellen.md").read_text(encoding="utf-8").splitlines():
        m = re.search(r"Kürzel:\s*([^|]+?)\s*\|", line)
        h = re.search(r"Harvard:\s*(.+)$", line.strip())
        if m and h:
            harvard[m.group(1).strip()] = h.group(1).strip().rstrip(".")
    eintraege = [e.strip().rstrip(".") for e in text.split("\n\n")[1:] if e.strip() and not e.strip().startswith("#")]  # Zwischenüberschriften wie „## Hilfsmittel“ überspringen
    fehler = 0
    for e in eintraege:
        if e not in harvard.values():
            print(f"EINTRAG nicht in quellen.md: {e[:60]}…")
            fehler += 1
    kapitel = "\n".join(p.read_text(encoding="utf-8") for p in sorted(kap.parent.glob("0[1-5]-*.md")))
    for kurz, h in harvard.items():
        zitiert = re.search(re.escape(kurz) + r"(?![0-9a-z])", kapitel)
        if zitiert and h not in eintraege:
            print(f"FEHLT im Verzeichnis: {kurz}")
            fehler += 1
        elif not zitiert and h in eintraege:
            print(f"NICHT ZITIERT, aber im Verzeichnis: {kurz}")
            fehler += 1
    print(f"{len(eintraege)} Einträge geprüft")
    print(f"\n{fehler} Fehler")
    return 1 if fehler else 0


def main() -> int:
    kap = pathlib.Path(sys.argv[1])
    text = kap.read_text(encoding="utf-8")
    if "literaturverzeichnis" in kap.name.lower():
        return verzeichnis(kap, text)
    q = quellen()
    fehler = 0
    letzte = None

    for m in BELEG.finditer(text):
        kurz = re.sub(r"\s+", " ", m.group(1)).strip()
        for teil in kurz.split(";"):
            teil = teil.strip()
            if teil.startswith("ebd"):
                continue
            teil = teil.split(" nach ")[-1].strip()
            if teil not in q:
                print(f"FEHLT in quellen.md: ({teil})")
                fehler += 1

    for m in ZITAT.finditer(text):
        zitat, beleg = m.group(1), m.group(2)
        b = BELEG.search(beleg) or EBD.search(beleg)
        if not b:
            print(f"ZITAT ohne lesbaren Beleg: „{zitat[:50]}…“")
            fehler += 1
            continue
        kurz = b.group(1).strip()
        if kurz.startswith("ebd"):
            kurz = letzte
        else:
            kurz = kurz.split(";")[-1].split(" nach ")[-1].strip()
            letzte = kurz
        pfad = q.get(kurz) if kurz else None
        if not pfad or not pfad.exists():
            print(f"NICHT PRÜFBAR (kein Quelltext): „{zitat[:50]}…“ ({kurz})")
            fehler += 1
            continue
        pages = seiten(pfad)
        such = norm(zitat)
        nummern = erste_seite(b.group(2))
        kandidaten = [pages.get(n, "") for n in nummern] if nummern else list(pages.values())
        teile = [t for t in re.split(r"\s{2,}", such) if t] or [such]
        ok = any(all(t in seite for t in teile) for seite in kandidaten)
        if ok:
            print(f"OK   „{zitat[:50]}…“ ({kurz}: {b.group(2) or '-'})")
        else:
            woanders = [n for n, s in pages.items() if all(t in s for t in teile)]
            hinweis = f", steht aber auf Seite {woanders}" if woanders else ", steht nirgends in der Quelle"
            print(f"FALSCH „{zitat[:50]}…“ ({kurz}: {b.group(2)}){hinweis}")
            fehler += 1

    print(f"\n{fehler} Fehler")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
