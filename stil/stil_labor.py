"""
Stil-Labor: Text in Samis formalen Stil bringen und messen, wie nah er dran ist.

WICHTIG ZUM VERSTEHEN
Hier wurde KEIN Modell auf deinen Stil trainiert. Das Modell (Claude) bleibt gleich.
Dein Stil kommt über drei Wege rein, und genau damit kannst du experimentieren:

  1. STILPROFIL   (stilprofil.md)  Regeln in Worten: BBB, Fishbone, Wendungen, Verbote.
  2. SCHREIBPROBE (probe-01-...)   Ein echtes Beispiel von dir. Das Modell imitiert es
                                   ("Few-Shot"). Tippfehler sollen NICHT übernommen werden.
  3. MESSUNG      (diese Datei)    Zahlen, die sagen, wie nah ein Text an deiner Probe ist:
                                   Satzlänge, deine Verbinder, deine Wendungen, KI-Muster.

Das nennt man "Prompting mit Stilprofil" statt "Fine-Tuning". Vorteil: sofort änderbar,
kein Training, keine Daten nötig. Nachteil: Das Modell kann vom Stil abweichen, darum misst
Teil 3 nach.

BENUTZEN (im Terminal, im Ordner seminararbeit):
  python3 stil/stil_labor.py messen  mein_text.md        # nur Zahlen, kein KI-Aufruf
  python3 stil/stil_labor.py umschreiben mein_text.md     # Claude schreibt in deinem Stil um
  python3 stil/stil_labor.py experiment mein_text.md      # 3 Varianten im Vergleich

Der KI-Aufruf läuft über die Claude-CLI mit deinem Login (`claude -p`), ohne API-Key.

EXPERIMENTIEREN: Ändere unten im Block "STELLSCHRAUBEN" die Werte und vergleiche die Zahlen.
"""

from __future__ import annotations

import re
import statistics
import subprocess
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
PROFIL = HIER / "stilprofil.md"
PROBE = HIER / "probe-01-kommentar-kinderliteratur.md"

# ---------------------------------------------------------------------------
# STELLSCHRAUBEN (hier experimentieren)
# ---------------------------------------------------------------------------
MODELL = "opus"            # "opus", "sonnet", "haiku": größer = stilsicherer, langsamer
MIT_PROFIL = True          # Regeln aus stilprofil.md mitschicken?
MIT_PROBE = True           # deine Schreibprobe als Beispiel mitschicken?
STRENGE = "mittel"         # "leicht" = nur KI-Muster raus, "mittel" = Stil angleichen,
                           # "stark" = komplett in BBB und Fishbone umbauen

# Deine typischen Verbinder und Wendungen (aus der Schreibprobe). Erweitern erlaubt.
VERBINDER = ["denn", "jedoch", "dennoch", "das bedeutet", "im umkehrschluss",
             "das resultiert in", "geschweige denn"]
SIGNATUR = ["das grundlegende problem besteht darin", "zusammenfassend",
            "viele menschen behaupten", "nur teilweise"]

# Typische KI-Muster (kleine Auswahl aus dem Skill humanizer-de). Weniger ist besser.
KI_MUSTER = {
    "Gedankenstrich als Satzzeichen": r"\s[–—]\s|\s-\s",
    "Floskel 'spielt eine entscheidende Rolle'": r"spielt eine (?:entscheidende|zentrale|wichtige) rolle",
    "Floskel 'in der heutigen Zeit'": r"in der heutigen (?:zeit|welt)",
    "Floskel 'nicht nur ... sondern auch'": r"nicht nur\b.{1,80}\bsondern auch",
    "Floskel 'es ist wichtig zu beachten'": r"es ist (?:wichtig|entscheidend) zu beachten",
    "Floskel 'zusammenfassend lässt sich sagen'": r"zusammenfassend lässt sich sagen",
    "Dreierliste mit 'und' am Ende": r"\b\w+, \w+ und \w+\b",
    "Doppelpunkt-Titel": r"^[^\n:]{3,60}:\s*$",
}
# Verbote aus deinem Profil für formale Texte
VERBOTE = {
    "Ich-Form": r"\b(?:ich|mein|meine|mir|mich)\b",
    "Anglizismus 'worst case'": r"worst case",
    "rhetorische Frage": r"\?",
}


# ---------------------------------------------------------------------------
# TEIL 1: MESSEN (reines Python, kein KI-Aufruf)
# ---------------------------------------------------------------------------
def saetze(text: str) -> list[str]:
    """Text grob in Sätze teilen (Punkt, Fragezeichen, Ausrufezeichen)."""
    teile = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in teile if len(s.split()) >= 3]


def fingerabdruck(text: str) -> dict:
    """Zahlen, die einen Schreibstil beschreiben. Pro 1000 Wörter, damit lange und
    kurze Texte vergleichbar sind."""
    t = text.lower()
    woerter = max(1, len(re.findall(r"\w+", t)))
    pro_tausend = lambda n: round(n * 1000 / woerter, 1)
    laengen = [len(s.split()) for s in saetze(text)] or [0]
    return {
        "woerter": woerter,
        "satzlaenge_mittel": round(statistics.mean(laengen), 1),
        # Schwankung der Satzlänge: Menschen variieren mehr als KI ("Burstiness")
        "satzlaenge_schwankung": round(statistics.pstdev(laengen), 1),
        "verbinder_pro_1000": pro_tausend(sum(t.count(v) for v in VERBINDER)),
        "signatur_pro_1000": pro_tausend(sum(t.count(s) for s in SIGNATUR)),
        "ki_muster": {k: len(re.findall(p, t, re.M)) for k, p in KI_MUSTER.items()},
        "verbote": {k: len(re.findall(p, t)) for k, p in VERBOTE.items()},
    }


def probe_text() -> str:
    """Nur den eigentlichen Text der Probe, ohne Überschrift und Hinweis-Block."""
    roh = PROBE.read_text(encoding="utf-8")
    roh = roh.split("## Hinweis")[0]
    return "\n".join(z for z in roh.splitlines() if not z.startswith("#"))


def naehe(a: dict, b: dict) -> float:
    """0 bis 100: wie nah Text a an Text b ist (einfacher Abstand über 4 Werte).
    Absichtlich simpel, damit du sehen kannst, wie es rechnet."""
    werte = ["satzlaenge_mittel", "satzlaenge_schwankung", "verbinder_pro_1000", "signatur_pro_1000"]
    abstand = 0.0
    for w in werte:
        groesser = max(abs(a[w]), abs(b[w]), 1.0)
        abstand += abs(a[w] - b[w]) / groesser  # 0 = gleich, 1 = komplett anders
    return round(100 * (1 - abstand / len(werte)), 1)


def zeige(name: str, f: dict, ziel: dict | None = None) -> None:
    print(f"\n== {name} ==")
    print(f"  Wörter {f['woerter']}, Satzlänge {f['satzlaenge_mittel']} "
          f"(Schwankung {f['satzlaenge_schwankung']})")
    print(f"  Deine Verbinder pro 1000 Wörter: {f['verbinder_pro_1000']}, "
          f"deine Wendungen: {f['signatur_pro_1000']}")
    ki = {k: v for k, v in f["ki_muster"].items() if v}
    vb = {k: v for k, v in f["verbote"].items() if v}
    print(f"  KI-Muster: {ki or 'keine'}")
    print(f"  Verstöße gegen dein Profil: {vb or 'keine'}")
    if ziel:
        print(f"  Nähe zu deiner Schreibprobe: {naehe(f, ziel)} von 100")


# ---------------------------------------------------------------------------
# TEIL 2: UMSCHREIBEN (Prompt bauen und Claude aufrufen)
# ---------------------------------------------------------------------------
AUFTRAG = {
    "leicht": "Entferne nur typische KI-Schreibmuster. Inhalt, Aufbau und Wortwahl bleiben.",
    "mittel": "Gleiche Satzbau, Verbinder und Wendungen an den Stil der Schreibprobe an. "
              "Inhalt und Reihenfolge bleiben.",
    "stark": "Baue den Text komplett im Stil des Profils um: jedes Argument als Behauptung, "
             "Beweis, Beispiel, Argumente nach Bereichen geordnet, abwägendes Fazit.",
}


def baue_prompt(strenge: str, mit_profil: bool, mit_probe: bool) -> str:
    """Der System-Prompt ist das ganze 'Training': Alles, was das Modell über deinen
    Stil weiß, steht hier drin. Druck ihn dir aus (Befehl 'prompt'), um ihn zu verstehen."""
    teile = [
        "Du überarbeitest deutsche Texte für eine formale Arbeit (Seminararbeit).",
        "Regeln, die immer gelten: Fakten, Zahlen, Namen, Zitate und Quellenangaben bleiben "
        "exakt. Nichts erfinden. Keine Ich-Form, keine Anglizismen, keine rhetorischen Fragen, "
        "keine Gedankenstriche als Satzzeichen.",
        "Auftrag: " + AUFTRAG[strenge],
    ]
    if mit_profil:
        teile.append("STILPROFIL DES AUTORS:\n" + PROFIL.read_text(encoding="utf-8"))
    if mit_probe:
        teile.append("SCHREIBPROBE DES AUTORS (nur Satzbau und Argumentation nachahmen, "
                     "Tippfehler und Kleinschreibung NICHT übernehmen):\n" + probe_text())
    teile.append("Gib nur den überarbeiteten Text aus, ohne Vorwort und ohne Erklärung.")
    return "\n\n".join(teile)


def claude(system_prompt: str, text: str, modell: str) -> str:
    """Ruft die Claude-CLI auf. Der Text geht über stdin (nicht über die Shell),
    damit nichts aus dem Text als Befehl ausgeführt werden kann. Werkzeuge sind aus."""
    befehl = ["claude", "-p", "Überarbeite den folgenden Text.", "--model", modell,
              "--system-prompt", system_prompt, "--tools", ""]
    erg = subprocess.run(befehl, input=text, capture_output=True, text=True, timeout=600)
    if erg.returncode != 0:
        sys.exit("Claude-Aufruf fehlgeschlagen: " + (erg.stderr.strip() or "ohne Meldung"))
    return erg.stdout.strip()


# ---------------------------------------------------------------------------
# TEIL 3: BEFEHLE
# ---------------------------------------------------------------------------
def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ("messen", "umschreiben", "experiment", "prompt"):
        print(__doc__)
        return
    befehl = sys.argv[1]
    ziel = fingerabdruck(probe_text())

    if befehl == "prompt":
        print(baue_prompt(STRENGE, MIT_PROFIL, MIT_PROBE))
        return
    if len(sys.argv) < 3:
        sys.exit("Bitte eine Textdatei angeben, z. B. kapitel/01-einleitung.md")
    datei = Path(sys.argv[2])
    text = datei.read_text(encoding="utf-8")

    zeige("Deine Schreibprobe (Ziel)", ziel)
    zeige("Eingabe", fingerabdruck(text), ziel)
    if befehl == "messen":
        return

    if befehl == "umschreiben":
        neu = claude(baue_prompt(STRENGE, MIT_PROFIL, MIT_PROBE), text, MODELL)
        ausgabe = datei.with_name(datei.stem + f"-stil-{STRENGE}.md")
        ausgabe.write_text(neu + "\n", encoding="utf-8")
        zeige(f"Umgeschrieben ({STRENGE}) -> {ausgabe.name}", fingerabdruck(neu), ziel)
        return

    # experiment: dieselbe Eingabe in 3 Varianten, damit du siehst, was Profil und Probe bringen
    varianten = [
        ("nur Regeln, ohne Profil und Probe", False, False),
        ("mit Profil", True, False),
        ("mit Profil und Probe", True, True),
    ]
    for name, profil, probe in varianten:
        neu = claude(baue_prompt(STRENGE, profil, probe), text, MODELL)
        ausgabe = datei.with_name(f"{datei.stem}-exp-{'p' if profil else ''}{'b' if probe else ''}"
                                  f"{'' if profil or probe else 'leer'}.md")
        ausgabe.write_text(neu + "\n", encoding="utf-8")
        zeige(f"{name} -> {ausgabe.name}", fingerabdruck(neu), ziel)


if __name__ == "__main__":
    main()
