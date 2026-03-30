# KickAdvisor

KickAdvisor ist ein täglicher Kickbase-Entscheidungshelfer für Markt, Kader und Trading. Das Projekt kombiniert drei Ebenen:

1. Datenaufnahme aus Kickbase und optionalen externen Football-Feeds.
2. Ein ML-Modell für kurzfristige Marktwertbewegungen.
3. Eine deterministische Entscheidungslogik für Bieten, Halten, Verkaufen und Risikobegrenzung.

Zusätzlich speichert das System seine Runs, Marktsnapshots und Transfers in SQLite, damit aus den echten Entscheidungen schrittweise ein belastbares Lernsystem für die nächste Saison entstehen kann.

## Ziel des Projekts

Das Projekt soll nicht nur Marktwerte vorhersagen, sondern mittelfristig bessere Transferentscheidungen lernen.

Stand heute:

- Das Modell prognostiziert tägliche Marktwertänderungen.
- Die Strategie-Engine setzt harte Regeln für Budget, Kaderlogik und Gebotsdisziplin.
- Reports, Snapshots und Transferhistorie schaffen die Datengrundlage für ein späteres Buy-Quality-Modell.

Strategische Richtung:

- Rest der aktuellen Saison: saubere Datensammlung und belastbare Entscheidungslogik.
- Nächste Saison: Buy-Decision-Scoring und stärkere operative Trading-Entscheidungen.

## Schnellstart

### 1. Repository verwenden

- Repository forken oder lokal klonen.
- Python-Umgebung anlegen.
- Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

### 2. Konfiguration setzen

Die fachliche Konfiguration liegt in `src/config/settings.py`.

Wichtige Werte:

- `competition_ids`: Wettbewerb, standardmäßig Bundesliga.
- `league_name`: Exakter Name deiner Liga.
- `start_budget`: Startbudget deiner Liga.
- `league_start_date`: Startdatum deiner Liga.

### 3. Secrets bereitstellen

Für lokale Runs gibt es jetzt drei unterstützte Wege:

1. Prozess-Umgebung
2. Windows Credential Manager über `keyring`
3. `.env.local` im Projektroot

Die Lade-Reihenfolge für fehlende Werte ist:

1. bestehende Environment-Variablen
2. lokaler Credential Manager
3. `.env.local`
4. `.env`

Benötigte oder optionale Schlüssel:

- `KICK_USER`: Kickbase-Login.
- `KICK_PASS`: Kickbase-Passwort.
- `GEMINI_API_KEY`: Schlüssel für die KI-Auswertung.
- `EMAIL_USER`: Absenderadresse für Mailversand.
- `EMAIL_PASS`: App-Passwort für Gmail.
- `FOOTBALL_DATA_API_KEY` optional: einfacher Fixture-Kontext.
- `API_FOOTBALL_KEY` optional: erweiterter Team- und Availability-Kontext.

Empfohlen für den lokalen Dauerbetrieb ist der Credential Manager. Die Anwendung liest die Werte, ohne dass sie im Repository gespeichert oder im Log ausgegeben werden.

Status prüfen:

```bash
python src/scripts/manage_local_secrets.py status
```

Secret lokal im Credential Manager hinterlegen:

```bash
python src/scripts/manage_local_secrets.py set KICK_USER
python src/scripts/manage_local_secrets.py set KICK_PASS
python src/scripts/manage_local_secrets.py set GEMINI_API_KEY
```

Optionales Secret löschen:

```bash
python src/scripts/manage_local_secrets.py delete API_FOOTBALL_KEY
```

Falls du lieber mit Dateien arbeitest, nutze `.env.local` auf Basis von `.env.example`. Diese Datei ist bereits durch `.gitignore` geschützt.

### 4. Lokal ausführen

```bash
python src/daily_predictions.py
```

Der Thin Entry Point `src/daily_predictions.py` delegiert direkt an `src/scripts/run_daily_predictions.py`.

### 5. In GitHub Actions ausführen

- Workflow öffnen: `Run Daily Predictions`
- Manuell starten oder den täglichen Scheduler nutzen.
- Jeder Run schreibt Artefakte und aktualisiert die Report-Dateien im Repository.

## Architekturüberblick

Das Projekt ist bewusst in Schichten organisiert.

### 1. Entry Points

- `src/daily_predictions.py`: sehr dünner Startpunkt für lokale Aufrufe.
- `src/scripts/run_daily_predictions.py`: orchestriert den kompletten Tageslauf.
- `src/scripts/export_buy_training_data.py`: exportiert Trainingsdaten für spätere Entscheidungsmodelle.
- `src/scripts/validate_api_football.py`: prüft die externe API-Football-Integration.
- `src/scripts/manage_local_secrets.py`: verwaltet lokale Secrets, ohne Werte im Repo oder Log zu speichern.

### 2. Konfiguration

- `src/config/settings.py`: zentrale Pfade, Laufzeitverzeichnisse und User-Einstellungen.
- `src/config/secrets.py`: zentrale Secret-Ladeschicht für Environment, Credential Manager und `.env.local`.
- `src/project_settings.py`: kompakter Re-Export zentraler Settings für schnelle Nutzung.

### 3. Kickbase API Layer

Der Ordner `src/kickbase_api/` kapselt alle direkten API-Zugriffe.

- `src/kickbase_api/user.py`: Login, Username, eigenes Budget.
- `src/kickbase_api/league.py`: Ligaauflösung und Marktfeed.
- `src/kickbase_api/manager.py`: Managerdaten und Transferfeed.
- `src/kickbase_api/player.py`: Spielerbezogene Hilfen.
- `src/kickbase_api/market_context.py`: Matchdays, Teams, Fixture-Kontext und gemeinsame Hilfsfunktionen.

### 4. Feature Layer

Der Ordner `src/features/` enthält die Geschäftslogik.

#### Strategische Entscheidungslogik

- `src/features/strategy/decision_engine.py`: harte Regeln für Kaderbedarf, Squad-Retention, Buy-Gates und Team-Availability.
- `src/features/strategy/bid_history.py`: historische Gebots- und Transferdrucksignale.
- `src/features/strategy/offer_tracking.py`: laufende Gebote, Outbid-Erkennung und Angebotsstatus.

#### Persistenz und Historisierung

- `src/features/persistence/advisor_repository.py`: SQLite-Persistenz für Snapshots, Transfers und Offer-Tracking.
- `src/features/analysis/history.py`: Historie, Prompt-Tabellen und Run-Zusammenfassungen.

#### Kommunikation und Reporting

- `src/features/ai/advice_generator.py`: baut den LLM-Prompt und erzeugt die textliche Handlungsempfehlung.
- `src/features/reporting/run_reporting.py`: Markdown- und JSON-Reporting.
- `src/features/communication/email_notifier.py`: E-Mail-Versand.

#### Budget- und Lernlogik

- `src/features/budgeting/manager_budgeting.py`: Budgetschätzung der Manager.
- `src/features/learning/buy_learning.py`: Trainingsdatensatz und Kaufbewertung aus realen Transfers und Snapshots.

#### Externe Daten

- `src/features/external/api_football.py`: optionale Team-Availability- und Fixture-Anreicherung.

### 5. Prediction Layer

Der Unterordner `src/features/predictions/` ist für den ML-Teil zuständig.

- `src/features/predictions/player_data_store.py`: bevorzugter Importpfad für das Laden und Speichern historischer Spieldaten.
- `src/features/predictions/feature_preprocessing.py`: bevorzugter Importpfad für Feature-Aufbereitung und Datensplitting.
- `src/features/predictions/market_value_model.py`: bevorzugter Importpfad für Modelltraining und Evaluierung.
- `src/features/predictions/live_prediction_pipeline.py`: bevorzugter Importpfad für Live-Prognosen, Markt-Join und Squad-Join.

Die Dateien in `features/predictions/` tragen jetzt direkt die sprechenden Namen der jeweiligen Verantwortung.

## Empfohlene Importpfade

Wenn du neue Logik hinzufügst, importiere direkt aus den neuen Subpaketen:

- `features.analysis`
- `features.persistence`
- `features.budgeting`
- `features.communication`
- `features.reporting`
- `features.strategy`
- `features.learning`
- `features.ai`
- `features.predictions.player_data_store`
- `features.predictions.feature_preprocessing`
- `features.predictions.market_value_model`
- `features.predictions.live_prediction_pipeline`
- `kickbase_api.market_context`

## End-to-End Ablauf des täglichen Runs

Der Tageslauf in `src/scripts/run_daily_predictions.py` folgt grob diesem Ablauf:

1. Einstellungen laden und Laufzeitverzeichnisse anlegen.
2. Mit Kickbase einloggen.
3. Liga und Basisdaten auflösen.
4. Historische Spieldaten laden oder aktualisieren.
5. Features vorbereiten und Marktwertmodell trainieren.
6. Prognosen auf aktuelle Markt- und Kaderspieler anwenden.
7. Transferhistorie, Gebotsdruck und Offer Tracking einbeziehen.
8. Optionalen Fixture- und API-Football-Kontext anreichern.
9. Deterministische Strategie anwenden:
   - Squad-Retention
   - Roster Needs
   - Buy Gates
10. Purchase Review aus gespeicherten Käufen und Snapshots bilden.
11. AI-Text generieren.
12. E-Mail versenden.
13. JSON- und Markdown-Report schreiben.
14. Run-Snapshot und Verlauf speichern.

## Daten und Persistenz

### SQLite

Die zentrale Datenbank liegt unter `data/player_data_total.db`.

Wichtige Inhalte:

- Historische Player-Daten für das Marktwertmodell.
- Vollständige Snapshots pro Run.
- League-Transferhistorie.
- Offer-Tracking-Daten.
- Advisor-Run-Metadaten.

### Reports

Der Ordner `reports/` enthält versionierte Run-Ergebnisse:

- `last_run_summary.json`: maschinenlesbare Zusammenfassung.
- `last_run_summary.md`: gut lesbare Zusammenfassung.
- `latest_run_report.md`: vollständiger letzter Report.
- `run_report_history_01.md` bis `run_report_history_03.md`: letzte historische Reports.

### Trainingsdaten

Trainingsdaten für die künftige Buy-Decision-Lernlogik liegen standardmäßig unter:

- `data/training/buy_training_dataset.csv`

Export:

```bash
python src/scripts/export_buy_training_data.py
```

## Buy Learning und Kaufbewertung

Dieses Projekt trennt bewusst zwischen Marktwertprognose und Kaufentscheidung.

Heute vorhanden:

- Marktwertmodell für kurzfristige MV-Änderungen.
- Purchase Review für jüngste eigene Käufe.
- Datengrundlage aus Transfers und historischen Marktsnapshots.

Noch nicht final produktiv:

- ein separates Buy-Quality-Modell, das Käufe direkt scorend bewertet.

Die Datei `src/features/learning/buy_learning.py` stellt dafür bereits die Grundlage bereit:

- Build von Trainingsdaten aus echten Käufen.
- Labeling in `good`, `neutral`, `poor`.
- Learning Notes für Reports und Prompt-Disziplin.

## Externe Datenquellen

### Football-Data.org

Wenn `FOOTBALL_DATA_API_KEY` gesetzt ist, bekommt der Advisor einfachen Fixture-Kontext.

### API-Football

Wenn `API_FOOTBALL_KEY` gesetzt ist, ergänzt das System:

- nächste Gegner
- Team-Verfügbarkeitskontext
- Missing- und Questionable-Counts
- vorsichtige Markt- und Verkaufsanpassungen

Wichtig:

- Der Run bleibt auch ohne externe APIs funktionsfähig.
- API-Football wird nur als Zusatzkontext genutzt, nicht als harte Pflichtabhängigkeit.
- Responses werden lokal unter `data/external_cache/api_football/` gecacht.

Validierung:

```bash
python src/scripts/validate_api_football.py --competition-id 1
```

Mit `--force-refresh` kann der Cache bewusst umgangen werden.

## Bekannte fachliche Grenzen

- Budgetschätzung fremder Manager ist eine Näherung, weil nicht alle internen Kickbase-Effekte sichtbar sind.
- Externe Football-Feeds können unvollständig, historisch oder vorübergehend gesperrt sein.
- Das Projekt lernt aktuell noch nicht vollautomatisch aus allen Entscheidungen, sondern baut die saubere Datengrundlage dafür erst auf.

## Entwicklungsrichtlinien für dieses Repository

Wenn du neue Logik einbaust, halte dich an diese Regeln:

1. Neue Funktionalität soll klare, sprechende Modulnamen verwenden.
2. Orchestrierung bleibt in `scripts/run_daily_predictions.py`, Fachlogik gehört in `features/`.
3. Kickbase-API-Aufrufe bleiben in `kickbase_api/`.
4. Persistenzlogik bleibt in Repository-Modulen, nicht direkt im Runner.
5. Experimentelle Features dürfen den täglichen Produktivlauf nicht hart abbrechen, wenn ein sicherer Fallback möglich ist.
6. Reports sollen sowohl für Menschen als auch für spätere Offline-Analyse brauchbar bleiben.

## Projektstruktur

```text
.
|-- src/
|   |-- config/
|   |   |-- settings.py
|   |-- daily_predictions.py
|   |-- features/
|   |   |-- ai/
|   |   |   |-- advice_generator.py
|   |   |-- analysis/
|   |   |   |-- history.py
|   |   |-- budgeting/
|   |   |   |-- manager_budgeting.py
|   |   |-- communication/
|   |   |   |-- email_notifier.py
|   |   |-- external/
|   |   |   |-- api_football.py
|   |   |-- learning/
|   |   |   |-- buy_learning.py
|   |   |-- persistence/
|   |   |   |-- advisor_repository.py
|   |   |-- predictions/
|   |   |   |-- feature_preprocessing.py
|   |   |   |-- live_prediction_pipeline.py
|   |   |   |-- market_value_model.py
|   |   |   |-- player_data_store.py
|   |   |-- reporting/
|   |   |   |-- run_reporting.py
|   |   |-- strategy/
|   |   |   |-- bid_history.py
|   |   |   |-- decision_engine.py
|   |   |   |-- offer_tracking.py
|   |-- kickbase_api/
|   |   |-- league.py
|   |   |-- manager.py
|   |   |-- market_context.py
|   |   |-- player.py
|   |   |-- user.py
|   |-- project_settings.py
|   |-- scripts/
|   |   |-- export_buy_training_data.py
|   |   |-- run_daily_predictions.py
|   |   |-- validate_api_football.py
|-- data/
|   |-- player_data_total.db
|   |-- training/
|   |-- external_cache/
|-- reports/
|-- README.md
```

## Roadmap

Kurzfristig:

- bestehende Entscheidungslogik weiter stabilisieren
- Kaufdisziplin und Buy-Gates weiter schärfen
- Reports und Trainingsdatenbasis verbessern

Mittelfristig:

- echtes Buy-Quality-Modell trainieren
- dieses Modell in die Strategie-Engine integrieren
- Portfolio-Optimierung für Kader und Liquidität ergänzen

## Credits

Das Projekt nutzt die Community-Dokumentation zur Kickbase-API von kevinskyba:

- https://kevinskyba.github.io/kickbase-api-doc/index.html

## Lizenz / Nutzung

Wenn du das Projekt in deinem eigenen Fork nutzt, passe Konfiguration, Secrets und Scheduler an deine Liga und deine Betriebsweise an.
