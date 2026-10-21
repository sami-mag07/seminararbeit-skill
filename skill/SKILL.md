---
name: seminararbeit
description: Orchestrator für formale Arbeiten (Seminararbeit Politische Bildung, Projekt ~/Desktop/APP/seminararbeit). Plant, verteilt an die Agents seminar-quellen, seminar-schreiber und seminar-kontrolle und hält stand.md aktuell. Greift bei "seminararbeit", "formale arbeit", "kapitel schreiben", "quellen für die arbeit", "prüf das kapitel", "wie weit ist die arbeit".
---

# Seminararbeit-Orchestrator

Projekt: ~/Desktop/APP/seminararbeit (P). Die Hauptsitzung ist der Orchestrator, denn Subagents können keine weiteren Agents starten. Du schreibst selbst keine Kapitel und suchst keine Quellen, du verteilst.

## Dateien
| Datei | Inhalt |
|---|---|
| stand.md | Thema, Leitfrage, Abgabe, Kapitelstatus, Log. Immer zuerst lesen. |
| vorgaben/ | Kursanforderungen (neu gilt vor alt), Muster.pdf, Merkblatt, Beispiel.pdf (Beispiel nur fürs Aussehen) |
| quellen.md | Quellenliste mit Kürzel, Textpfad, Typ, Würdigkeit, Harvard-Eintrag |
| belege.md | Belegbank, einzige Grundlage fürs Schreiben |
| quellen/pdf, quellen/text | PDFs und Text mit [Seite N] |
| stil/ | Samis Schreibprobe(n) und stilprofil.md |
| kapitel/ | 01-einleitung.md bis 06-anhang.md |
| pruefung/ | Berichte des Kontroll-Agents |
| tools/ | pdf_text.py, zitat_check.py, zeichen.py |

## Ablauf
1. **Start:** stand.md lesen. Fehlen Thema, Leitfrage, Abgabe oder Schreibprobe, genau danach fragen. Die Leitfrage mit Sami schärfen (Inwieweit/Wie/Inwiefern, eingegrenzt, keine Ja/Nein-Frage).
2. **Planung:** Gliederung nach Muster (Einleitung, Leitfrage, Methode, Hauptteil mit 4.x, Diskussion, Anhang, Literatur) und Zeichenbudget je Kapitel in stand.md. Summe 25.500, Einleitung 1.500 bis 1.650. Rückwärts vom Abgabetermin einen Wochenplan eintragen.
3. **Quellen:** seminar-quellen spawnen, bei großen Themen bis zu 3 parallel mit getrennten Unterthemen (Theorie, Empirie, Gegenpositionen). Ziel: mind. 1 Monographie + 4 wissenschaftliche Quellen, besser 8 bis 12, und Belege für jedes Hauptteil-Kapitel.
4. **Interview:** Mit Sami Leitfaden erstellen (Fragen aus der Leitfrage abgeleitet), Sami führt das Interview, das Transkript kommt nach kapitel/06-anhang.md. Ohne echtes Transkript keine Interview-Auswertung.
5. **Schreiben:** seminar-schreiber pro Kapitel, Reihenfolge Hauptteil, Methode, Leitfrage, Diskussion, Einleitung zuletzt. Nie zwei Schreiber gleichzeitig auf dieselbe Datei.
6. **Kontrolle:** Nach jedem Kapitel seminar-kontrolle. PFLICHT-Punkte gehen zurück an den Schreiber (max. 3 Runden), dann an Sami.
7. **Gesamtcheck:** Am Ende Kontrolle über alle Kapitel, Literaturverzeichnis aus quellen.md (alphabetisch, hängender Einzug), Zeichen gesamt, Checkliste Abschnitt 14 der Anforderungen.
8. **Export:** Kapitel zu einem Word-Dokument nach Formatvorgaben (Times New Roman 12, 1,5-zeilig, Ränder 2,5/2,5/2,5/2 cm, Deckblatt wie Muster, Seitenzahlen "x von y", Deckblatt ohne Zahl) per Skill docx.

## Regeln
- Quellen nur legal (siehe seminar-quellen). Keine Schattenbibliotheken.
- Nichts im Text, was nicht in belege.md, quellen.md oder dem Interview-Transkript steht.
- Inhalte aus Beispiel.pdf werden nie übernommen.
- Nach jedem Schritt stand.md (Status, Log) aktualisieren und Sami den Stand in einer Zeile nennen.
