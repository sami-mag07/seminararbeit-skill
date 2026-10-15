# Seminararbeit-Skill

Claude-Code-Setup für formale Arbeiten (Seminararbeit), mit dem eigenen Schreibstil als Profil. Ein Orchestrator-Skill verteilt die Arbeit an drei Agents: Quellen suchen, Kapitel schreiben, Kapitel prüfen.

Es wird kein Modell trainiert. Der Stil kommt über ein Stilprofil (Regeln in Worten), eine echte Schreibprobe als Beispiel und eine Messung, wie nah ein Text an der Probe liegt.

## Inhalt

| Ordner | Was drin ist |
|---|---|
| skill/SKILL.md | Orchestrator: Planung, Reihenfolge, Regeln |
| agents/ | seminar-quellen, seminar-schreiber, seminar-kontrolle |
| stil/ | stilprofil.md, Schreibprobe, stil_labor.py (messen, umschreiben, Varianten vergleichen) |
| tools/ | pdf_text.py (PDF zu Text mit Seitenmarken), zitat_check.py (jedes Zitat gegen die Quelle auf der genannten Seite), zeichen.py (Zeichen wie Word) |

## Einrichten

1. `skill/SKILL.md` nach `~/.claude/skills/seminararbeit/` kopieren, `agents/*.md` nach `~/.claude/agents/`.
2. Einen Projektordner anlegen und `stil/` und `tools/` hineinkopieren. In Skill und Agents ist der Pfad `~/Desktop/APP/seminararbeit` eingetragen, bei Bedarf ersetzen.
3. Im Projektordner ergänzen: `stand.md`, `quellen.md`, `belege.md`, `kapitel/`, `quellen/pdf`, `quellen/text`, `pruefung/`, `vorgaben/` (eigene Kursvorgaben).
4. Eigene Schreibprobe nach `stil/` legen und `stilprofil.md` daraus ableiten (oder den Schreib-Agent das machen lassen).

## Abhängigkeiten

- Claude Code
- Python 3 mit `pypdf` (für pdf_text.py)
- Optional der Skill `humanizer-de` für den Humanizer-Pass und das KI-Muster-Audit (nicht in diesem Repo)

## Stil-Labor

    python3 stil/stil_labor.py messen kapitel/01-einleitung.md
    python3 stil/stil_labor.py umschreiben kapitel/01-einleitung.md
    python3 stil/stil_labor.py experiment kapitel/01-einleitung.md

Der KI-Aufruf läuft über die Claude-CLI (`claude -p`) mit dem eigenen Login, ohne API-Key. Die Stellschrauben stehen oben in der Datei.

## Lizenz

MIT
