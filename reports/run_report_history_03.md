# Last Run Summary

- Report Date: 29. March 2026
- Generated At: 2026-03-29T21:58:10.362911Z
- User: Luca Malco
- Own Budget: 3746461.0
- Market Players: 20
- Squad Players: 11
- Fixture Context Active: True
- AI Status: success
- Mail Status: success
- Offer Tracking Active: 1
- Offer Tracking Outbid: 0
- Offer Tracking Won: 0

## Model Metrics

- Signs Correct: 67.14
- RMSE: 42030.76
- MAE: 20972.54
- R2: 0.919

## Matchday Context

- Next Matchday: 28
- Next Matchday Date: 05-04-2026 17:30
- Days Until Next Matchday: 7
- Trading Window Mode: normal_build_up
- Friday Safety Mode: inactive

## Own Budget Context

- Budget: 3746461.0
- Current Cash: 3746461.0
- Spendable Without Debt: 3746461.0
- Temporary Negative Buffer: 52702913.67
- Theoretical Max Spend: 56449374.67
- Max Negative: -52702913.67
- Friday Recovery Need At Floor: 52702913.67

## Management Summary

- Aktive Gebotssumme: 1230272.0
- Effektives Cash nach aktiven Geboten: 2516189.0
- Overbid-Druck: low
- Suggested Markup: 0.0
- Outbid Count 14d: 0
- Aktive Gebote halten: 0
- Aktive Gebote leicht erhoehen: 1
- Aktive Gebote abbrechen: 0

## Squad Retention Summary

- Marktknappheit: high
- Starke Ersatzoptionen am Markt: 0
- Geschuetzte Kaderspieler: 3

## Roster Need Summary

- Primaerer Positionsbedarf: GK
- Dringlichkeit: medium
- Positionen mit Bedarf: 1

- GK | Im Kader: 1 | Minimum: 1 | Marktoptionen: 2 | Bedarf: medium | Hinweis: Nur ein Torwart im Kader, Ersatzoptionen nicht zu spaet angehen.

## API-Football Summary

- API-Football aktiv: False
- Grund: request_failed
- Liga: None
- Season: 2024
- Angefragte Season: 2024
- Season-Fallback aktiv: False
- Teams mit Kontext: 0
- Teams geladen: 0
- Standings geladen: 0
- Geladene Fixtures: 0
- Injury Entries: 0
- Missing Player Flags: 0
- Questionable Flags: 0
- Market Caution Adjustments: 0
- Market Opportunity Adjustments: 0
- Squad Sell Pressure Up: 0
- Squad Sell Pressure Down: 0
- Fehler: API-Football /leagues returned errors: token: Error/Missing application key. Go to https://www.api-football.com/documentation-v3 to learn how to get your API application key.

- Keine auffaelligen Team-Ausfaelle im API-Football Kontext

## Strategy Validation

- Keine offensichtlichen Strategie-Konflikte erkannt.

## Manager Budget Snapshot

```text
      User      Budget  Team Value  Current Cash  Max Negative  Available Budget  Spendable Without Debt  Temporary Negative Buffer  Friday Recovery Need At Floor
       Rob 118.794.288 160.433.235   118.794.288   -92.145.083       210.939.371             118.794.288                 92.145.083                     92.145.083
      joel 112.686.923 174.753.684   112.686.923   -94.855.400       207.542.323             112.686.923                 94.855.400                     94.855.400
 FlippiXxp  78.249.254 293.241.510    78.249.254  -122.591.952       200.841.206              78.249.254                122.591.952                    122.591.952
       Jan  73.292.889 201.610.723    73.292.889   -90.718.192       164.011.081              73.292.889                 90.718.192                     90.718.192
      Till  64.552.248 222.209.884    64.552.248   -94.631.504       159.183.752              64.552.248                 94.631.504                     94.631.504
     Jonas  71.156.552 161.133.590    71.156.552   -76.655.747       147.812.299              71.156.552                 76.655.747                     76.655.747
     David  16.717.482 244.813.597    16.717.482   -86.305.256       103.022.738              16.717.482                 86.305.256                     86.305.256
Luca Malco   3.746.461 155.959.338     3.746.461   -52.702.914        56.449.375               3.746.461                 52.702.914                     52.702.914
```

## Top Market Candidates

- Budu Zivzivadze | Team: Heidenheim | Score: 73.1 | Rolle: short_term_trade | Delta: 86090.4 | Max: 1271595.0 | Competitive Max: 1271595.0 | Wettbewerb: high | Gegner: Borussia Mönchengladbach | Fixture: good
- Frederik Rönnow | Team: Union Berlin | Score: 65.2 | Rolle: medium_term_hold | Delta: 150352.17 | Max: 7567676.0 | Competitive Max: 7567676.0 | Wettbewerb: high | Gegner: FC St. Pauli 1910 | Fixture: good
- Abdoul-Karim Coulibaly | Team: Bremen | Score: 64.4 | Rolle: short_term_trade | Delta: 235534.9 | Max: 3747200.0 | Competitive Max: 3747200.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Tim Lemperle | Team: Hoffenheim | Score: 58.8 | Rolle: medium_term_hold | Delta: 102459.84 | Max: 14482622.0 | Competitive Max: 14482622.0 | Wettbewerb: high | Gegner: 1. FSV Mainz 05 | Fixture: good
- Justin Njinmah | Team: Bremen | Score: 52.2 | Rolle: medium_term_hold | Delta: 147411.26 | Max: 6105145.0 | Competitive Max: 6105145.0 | Wettbewerb: high | Gegner: None | Fixture: None

## Market Snapshot

```text
    first_name     last_name    team_name         mv  predicted_mv_change  priority_score recommended_bid_max  competitive_bid_max recent_bid_competition             bid_strategy_note position_label roster_need_level  team_missing_count  team_questionable_count team_availability_level  team_availability_priority_adjustment active_offer_decision active_offer_recommended_new_bid  hours_to_exp
          Budu    Zivzivadze   Heidenheim  1.230.272               86.090              73           1.271.595            1.271.595                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0           raise_small                        1.271.595             3
      Frederik        Rönnow Union Berlin  7.513.549              150.352              65           7.567.676            7.567.676                   high aggressive_only_if_priority_a             GK            medium                   0                        0                  stable                                      0                     -                                -           688
  Abdoul-Karim     Coulibaly       Bremen  3.634.143              235.535              64           3.747.200            3.747.200                   high               avoid_price_war            DEF              none                   0                        0                  stable                                      0                     -                                -            20
           Tim      Lemperle   Hoffenheim 14.445.736              102.460              59          14.482.622           14.482.622                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -             3
        Justin       Njinmah       Bremen  6.052.077              147.411              52           6.105.145            6.105.145                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -           665
        Philip         Otele      Hamburg  6.244.160              146.224              52           6.296.801            6.296.801                   high aggressive_only_if_priority_a             ST              none                   0                        0                  stable                                      0                     -                                -           718
          Igor     Matanović     Freiburg  9.158.869              -40.709              51           9.158.869            9.158.869                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -            14
    Maximilian   Mittelstädt    Stuttgart 32.834.792               35.708              51          32.847.647           32.847.647                 medium              stay_disciplined            DEF              none                   0                        0                  stable                                      0                     -                                -            18
          Ísak   Jóhannesson         Köln  3.140.637               53.395              51           3.159.859            3.159.859                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -           688
        Joakim         Mæhle    Wolfsburg  4.193.816               56.610              50           4.214.196            4.214.196                   high aggressive_only_if_priority_a            DEF              none                   0                        0                  stable                                      0                     -                                -           688
       Maarten   Vandevoordt      Leipzig  4.457.377              -47.054              50           4.457.377            4.457.377                   high               avoid_price_war             GK            medium                   0                        0                  stable                                      0                     -                                -            33
Maycon Douglas       Cardozo       Bayern  1.794.912               26.613              48           1.804.493            1.804.493                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -           718
        Andrej          Ilic Union Berlin  3.877.664              -62.370              44           3.877.664            3.877.664                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -             1
        Albert Sambi Lokonga      Hamburg  5.710.822             -122.145              43           5.710.822            5.710.822                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -             9
       Olivier         Deman       Bremen  4.130.656              -57.561              42           4.130.656            4.130.656                   high               avoid_price_war            DEF              none                   0                        0                  stable                                      0                     -                                -            14
```

## Top Sell Candidates

- Robert Andrich | Team: Leverkusen | Sell Score: 21.7 | Rolle: rotation_hold | Delta: -242444.89 | Gegner: None | Fixture: None
- Manuel Neuer | Team: Bayern | Sell Score: 21.4 | Rolle: rotation_hold | Delta: 253571.32 | Gegner: None | Fixture: None
- Josha Vagnoman | Team: Stuttgart | Sell Score: 18.8 | Rolle: rotation_hold | Delta: 157147.29 | Gegner: None | Fixture: None
- Ermedin Demirović | Team: Stuttgart | Sell Score: 17.8 | Rolle: rotation_hold | Delta: 22009.49 | Gegner: None | Fixture: None
- Marvin Pieringer | Team: Heidenheim | Sell Score: 17.0 | Rolle: rotation_hold | Delta: 136523.95 | Gegner: Borussia Mönchengladbach | Fixture: good

## Squad Snapshot

```text
first_name last_name  team_name         mv  predicted_mv_change  sell_priority_score    squad_role     squad_strategy_note  team_missing_count  team_questionable_count team_availability_level  team_availability_sell_adjustment s_11_prob            next_opponent
    Robert   Andrich Leverkusen 18.869.255             -242.445                   22 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
    Manuel     Neuer     Bayern  7.094.577              253.571                   21 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Josha  Vagnoman  Stuttgart  5.741.825              157.147                   19 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
   Ermedin Demirović  Stuttgart 20.636.973               22.009                   18 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
    Marvin Pieringer Heidenheim  2.245.957              136.524                   17 rotation_hold              model_only                   0                        0                  stable                                  0         - Borussia Mönchengladbach
 Christian   Eriksen  Wolfsburg 10.784.236               47.736                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
    Kaishu      Sano      Mainz 11.826.283               46.762                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -      TSG 1899 Hoffenheim
      Finn   Jeltsch  Stuttgart 10.852.259               70.591                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Marco    Friedl     Bremen 17.408.218             -162.825                    1  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -                        -
     Jakub  Kaminski       Köln 19.867.250               38.214                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -      Eintracht Frankfurt
     Serge    Gnabry     Bayern 30.132.505               64.008                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -                        -
```

## Active Offers

- Budu Zivzivadze | Gebot: 1230272.0 | Marktwert: 1230272.0 | Ablauf: 2026-03-30T00:36:08Z

## Active Offer Actions

- Budu Zivzivadze | Aktion: leicht erhoehen | Aktuelles Gebot: 1230272.0 | Neues Max Gebot: 1271595.0 | Grund: Leicht anheben: Das Profil ist umkaempft und dein aktuelles Gebot liegt unter dem Wettbewerbsniveau.

## Recent Outbid Offers

- Keine ueberbotenen Gebote gespeichert

## Offer Tracking Debug

- Root Type: None
- Candidate Count: 0
- Keine Debug-Kandidaten gespeichert

### Feed Structure Debug

- Keine Struktur-Daten gespeichert

### Market Feed Debug

- Root Type: list
- Item Count: 29
- Pfad: market[0] | Spieler: Kevin Akpoguma | Spieler-ID: 96 | Marktwert: 500000.0 | Ablauf: 2026-03-30T00:49:06Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "96", "fn": "Kevin", "n": "Akpoguma", "tid": "14", "pos": 2, "st": 0, "mvt": 0, "mv": 500000, "p": -75, "ap": -15, "ofc": 0, "exs": 10296, "prc": 500000, "isn": false, "iposl": false, "dt": "2026-03-28T08:40:06Z", "pim": "content/file/1fe930ae579e4ba78fe7c4f948264d3b.png"}
- Pfad: market[1] | Spieler: Jens Grahl | Spieler-ID: 357 | Marktwert: 500000.0 | Ablauf: 2026-03-30T15:51:00Z | Keys: dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, pim, pos, prc, st, tid | Sample: {"i": "357", "fn": "Jens", "n": "Grahl", "tid": "4", "pos": 1, "st": 0, "mvt": 0, "mv": 500000, "ofc": 0, "exs": 64410, "prc": 500000, "isn": false, "iposl": false, "dt": "2026-03-28T17:18:00Z", "pim": "content/file/3b8eae1b9d6d4e8d961bfd3f152db402.png"}
- Pfad: market[2] | Spieler: Maximilian Philipp | Spieler-ID: 1226 | Marktwert: 500000.0 | Ablauf: 2026-03-30T09:27:25Z | Keys: dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, pim, pos, prc, st, tid | Sample: {"i": "1226", "fn": "Maximilian", "n": "Philipp", "tid": "5", "pos": 4, "st": 0, "mvt": 0, "mv": 500000, "ofc": 0, "exs": 41395, "prc": 500000, "isn": false, "iposl": false, "dt": "2026-03-28T23:43:25Z", "pim": "content/file/7d6a4935195d414a9119e81aa398222a.png"}
- Pfad: market[3] | Spieler: Maximilian Mittelstädt | Spieler-ID: 1664 | Marktwert: 32834792.0 | Ablauf: 2026-03-30T16:18:07Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1664", "fn": "Maximilian", "n": "Mittelstädt", "tid": "9", "pos": 2, "st": 0, "mvt": 1, "mv": 32834792, "p": 3062, "ap": 122, "ofc": 0, "exs": 66037, "prc": 32834792, "isn": false, "iposl": false, "dt": "2026-03-28T20:31:07Z", "pim": "content/file/2dea6714f704489fa0fb302accce4e8a.png"}
- Pfad: market[4] | Spieler: Serhou Guirassy | Spieler-ID: 1920 | Marktwert: 38389860.0 | Ablauf: 2026-03-31T02:09:47Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1920", "fn": "Serhou", "n": "Guirassy", "tid": "3", "pos": 4, "st": 0, "mvt": 2, "mv": 38389860, "p": 2676, "ap": 103, "ofc": 0, "exs": 101537, "prc": 38389860, "isn": false, "iposl": false, "dt": "2026-03-29T05:07:47Z", "pim": "content/file/ed209b2ca67c4784a658521f80baa795.png"}
- Pfad: market[5] | Spieler: Frederik Rönnow | Spieler-ID: 2279 | Marktwert: 7513549.0 | Ablauf: 2026-04-27T14:10:25Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "2279", "fn": "Frederik", "n": "Rönnow", "tid": "40", "pos": 1, "st": 0, "mvt": 1, "mv": 7513549, "p": 2109, "ap": 81, "ofc": 0, "exs": 2477575, "u": {"i": "<nested>", "n": "<nested>", "uim": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 7215918, "isn": false, "iposl": false, "dt": "2026-03-28T14:10:25Z", "pim": "content/file/98159e30baca4a1080128a7a4c32914e.png"}
- Pfad: market[6] | Spieler: Tim Lemperle | Spieler-ID: 2803 | Marktwert: 14445736.0 | Ablauf: 2026-03-30T00:53:49Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2803", "fn": "Tim", "n": "Lemperle", "tid": "14", "pos": 4, "st": 0, "mvt": 1, "mv": 14445736, "p": 1765, "ap": 80, "ofc": 0, "exs": 10579, "prc": 14445736, "isn": false, "iposl": false, "dt": "2026-03-29T00:48:49Z", "pim": "content/file/1fe930ae579e4ba78fe7c4f948264d3b.png"}
- Pfad: market[7] | Spieler: Justin Njinmah | Spieler-ID: 3228 | Marktwert: 6052077.0 | Ablauf: 2026-04-26T14:40:44Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "3228", "fn": "Justin", "n": "Njinmah", "tid": "10", "pos": 4, "st": 0, "mvt": 1, "mv": 6052077, "p": 1208, "ap": 46, "ofc": 0, "exs": 2392994, "u": {"i": "<nested>", "n": "<nested>", "uim": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 5478211, "isn": false, "iposl": false, "dt": "2026-03-27T14:40:44Z", "pim": "content/file/1a88a39549924d048294f618079e8437.png"}
- Pfad: market[8] | Spieler: Igor Matanović | Spieler-ID: 3304 | Marktwert: 9158869.0 | Ablauf: 2026-03-30T12:26:05Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "3304", "fn": "Igor", "n": "Matanović", "tid": "5", "pos": 4, "st": 0, "mvt": 1, "mv": 9158869, "p": 1494, "ap": 62, "ofc": 0, "exs": 52115, "prc": 9158869, "isn": false, "iposl": false, "dt": "2026-03-29T01:50:05Z", "pim": "content/file/7d6a4935195d414a9119e81aa398222a.png"}
- Pfad: market[9] | Spieler: Mattias Svanberg | Spieler-ID: 4266 | Marktwert: 500000.0 | Ablauf: 2026-03-30T22:36:22Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "4266", "fn": "Mattias", "n": "Svanberg", "tid": "11", "pos": 3, "st": 0, "mvt": 0, "mv": 500000, "p": 550, "ap": 28, "ofc": 0, "exs": 88732, "prc": 500000, "isn": true, "iposl": false, "dt": "2026-03-29T20:09:22Z", "pim": "content/file/a00a1472afdc4462933a364537704b05.png"}

## AI Full Output

Hallo Luca, hier ist deine Kickbase-Abendstrategie für den 29. März 2026. Lass uns deine Position analysieren und die nächsten Schritte planen.

### 1. TEAMSTATUS

Dein Kader ist mit 11 von 17 Spielern kompakt, aber du hast mit 3.746.461 Euro (effektiv 2.516.189 Euro nach Abzug deines Gebots) solides Cash zur Verfügung. Wir befinden uns in einer normalen Aufbauwoche vor dem Spieltag in sieben Tagen. Die dringendste Management-Aufgabe ist die Besetzung der zweiten Torwartposition, die vom System mit mittlerer Dringlichkeit markiert wurde. Da keine Spieler vor dem nächsten Marktwertupdate auslaufen, können wir uns heute voll auf strategische Zukäufe konzentrieren.

### 2. VERKAUFS-BEFEHLE

Aktuell gibt es keinen zwingenden Verkaufsdruck. Deine "Core Starter" sind durch die Marktknappheit geschützt und sollten gehalten werden.

*   **Beobachten:** Robert Andrich.
    *   **Analyse:** Er hat die höchste Verkaufspriorität (22) in deinem Kader und eine prognostizierte negative Marktwertentwicklung von ca. -242k. Aktuell ist er sportlich gesetzt, aber wenn wir für einen Top-Transfer signifikantes Kapital benötigen, ist er der logischste Kandidat für eine Liquidierung. Vorerst halten wir ihn, um keine Lücke im Mittelfeld zu schaffen.

### 3. SOFORT-KÄUFE BIS ZUM NAECHSTEN UPDATE

Da heute keine Spieler auslaufen, gibt es keine Sofort-Käufe in diesem Sinne. Unsere einzige unmittelbare Aktion betrifft dein bereits laufendes Gebot.

*   **Aktives Gebot:** Budu Zivzivadze
*   **Aktion:** Leicht erhöhen
*   **Neues Max Gebot:** 1.271.595 Euro
*   **Warum:** Die Systemempfehlung ist hier klar. Zivzivadze hat mit +7% eine exzellente kurzfristige Marktwertprognose und der Wettbewerb ist hoch. Eine leichte Erhöhung auf das empfohlene Maximum ist ein kalkuliertes Risiko, um dir einen profitablen "Short-Term-Trade" zu sichern. Das finanzielle Risiko ist absolut überschaubar.

### 4. SPÄTERE CHANCEN UND HOLDS

Hier liegt heute unser strategischer Fokus. Wir müssen deine Torwart-Lücke schließen.

*   **Kauf Frederik Rönnow | Priorität A | Max Gebot 7.570.000 Euro | Rolle: Kaderbaustein | Warum jetzt:**
    *   **Analyse:** Rönnow ist die klare Priorität. Er füllt deine kritische Kaderlücke im Tor, hat eine positive Marktwertprognose (+150k) und ist als Nummer 1 bei Union Berlin gesetzt. Die Investition stabilisiert deinen Kader langfristig und ist sportlich absolut sinnvoll. Da dein Budget für ihn allein nicht reicht, müssen wir ins Minus gehen.
    *   **Exit-Strategie für Negativpuffer:** Der Kauf von Rönnow und die Erhöhung für Zivzivadze werden dein Konto mit ca. 5,1 Mio. Euro ins Minus drücken. Um bis Freitag wieder die Null zu erreichen, planen wir den Verkauf von **Robert Andrich** (ca. 18,8 Mio. Euro) ein. Dies deckt das Defizit mehr als ausreichend und schafft neues Kapital für weitere Transfers.

*   **Beobachte Maarten Vandevoordt | Zielstrategie: Fallback-Option | Späteres Max Gebot: Marktwert | Warum relevant:**
    *   **Analyse:** Er ist die zweite Torwart-Option auf dem Markt. Seine Marktwertprognose ist allerdings negativ. Er ist nur eine Alternative, falls der Deal mit Rönnow wider Erwarten nicht klappt.

*   **Nicht kaufen: Maximilian Mittelstädt:**
    *   **Analyse:** Auch wenn er ein interessanter Spieler ist, hast du bereits das Maximum von drei Stuttgart-Spielern im Kader. Ein Kauf ist daher regelkonform nicht möglich.

### 5. NEWS-CHECK

*   **Manuel Neuer:** Aktuelle Berichte vom 29. März 2026 bestätigen, dass Neuer nach seiner Wadenverletzung wieder fit ist und für das kommende Spiel gegen Freiburg eine Option darstellt. Seine Belastung wird jedoch mit Blick auf die Champions League gesteuert. Für deinen Kader bedeutet das Stabilität, aber die Anschaffung eines zweiten Torwarts bleibt zur Absicherung essenziell.
*   **Serge Gnabry:** Nach einer von Verletzungen geprägten Vorsaison hat sich Gnabry in der aktuellen Spielzeit als Leistungsträger etabliert und wurde kürzlich für eine starke Leistung gegen Union Berlin gelobt. Es gibt keine neuen besorgniserregenden Nachrichten, er ist ein klarer "Hold".
*   **Frederik Rönnow:** Er ist die unangefochtene Nummer 1 bei Union Berlin und hat seinen Vertrag erst im September 2025 verlängert, was seine wichtige Rolle im Verein unterstreicht.
*   **Robert Andrich & Budu Zivzivadze:** Bei beiden Spielern gibt es keine neuen, spielentscheidenden Informationen über Verletzungen oder Sperren.

### 6. TRADING-PLAN

Unsere Strategie für die nächsten Tage ist klar strukturiert:

1.  **Priorität 1 (Heute):** Das Gebot für Budu Zivzivadze leicht erhöhen und ein entscheidendes Gebot für Frederik Rönnow abgeben, um die Torwartposition zu sichern.
2.  **Kapitalmanagement (Morgen/Übermorgen):** Sobald Rönnow gekauft ist, werden wir Robert Andrich auf den Transfermarkt setzen, um das Budget auszugleichen und einen signifikanten Gewinn an freiem Kapital zu erzielen.
3.  **Kader füllen (Bis Donnerstag):** Mit dem neu geschaffenen Budget werden wir die verbleibenden 4 Kaderplätze mit gezielten Spielern auffüllen. Der Fokus liegt auf kurzfristigen Marktwert-Tradern und günstigen Startern für den kommenden Spieltag.

### 7. FRIDAY-CHECK

Bis Freitagabend müssen folgende Punkte erledigt sein, um spielberechtigt und liquide zu sein:

1.  **Kader voll:** Dein Kader muss mindestens 11 spielberechtigte Spieler umfassen, idealerweise füllen wir ihn auf 15-17 Spieler auf.
2.  **Torwart-Duo:** Mit Manuel Neuer und (hoffentlich) Frederik Rönnow muss deine Torwartposition doppelt besetzt sein.
3.  **Budget > 0 Euro:** Der entscheidende Punkt. Durch den geplanten Verkauf von Robert Andrich nach dem Kauf von Rönnow werden wir nicht nur das negative Konto ausgleichen, sondern ein komfortables Plus für das Wochenende erwirtschaften. Dieser Schritt ist obligatorisch.
