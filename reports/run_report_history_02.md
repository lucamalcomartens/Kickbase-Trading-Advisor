# Last Run Summary

- Report Date: 30. March 2026
- Generated At: 2026-03-30T09:34:14.713093Z
- User: Luca Malco
- Own Budget: 3746461.0
- Market Players: 28
- Squad Players: 12
- Fixture Context Active: True
- AI Status: success
- Mail Status: success
- Offer Tracking Active: 0
- Offer Tracking Outbid: 0
- Offer Tracking Won: 0

## Model Metrics

- Signs Correct: 66.81
- RMSE: 41877.57
- MAE: 20856.08
- R2: 0.9192

## Matchday Context

- Next Matchday: 28
- Next Matchday Date: 05-04-2026 17:30
- Days Until Next Matchday: 6
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

- Aktive Gebotssumme: 0.0
- Effektives Cash nach aktiven Geboten: 3746461.0
- Overbid-Druck: low
- Suggested Markup: 0.0
- Outbid Count 14d: 0
- Aktive Gebote halten: 0
- Aktive Gebote leicht erhoehen: 0
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
- Season: 2025
- Angefragte Season: 2025
- Live-Season Referenz: 2025
- Season-Fallback aktiv: False
- Historische Season aktiv: False
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
      joel 126.686.923 175.983.956   126.686.923   -99.881.390       226.568.313             126.686.923                 99.881.390                     99.881.390
       Rob 120.053.302 159.174.221   120.053.302   -92.145.083       212.198.385             120.053.302                 92.145.083                     92.145.083
 FlippiXxp  72.920.330 302.829.996    72.920.330  -123.997.608       196.917.938              72.920.330                123.997.608                    123.997.608
       Jan  73.292.889 201.610.723    73.292.889   -90.718.192       164.011.081              73.292.889                 90.718.192                     90.718.192
     Jonas  71.156.552 161.133.590    71.156.552   -76.655.747       147.812.299              71.156.552                 76.655.747                     76.655.747
      Till  47.663.360 236.655.620    47.663.360   -93.825.263       141.488.623              47.663.360                 93.825.263                     93.825.263
     David  16.717.482 244.813.597    16.717.482   -86.305.256       103.022.738              16.717.482                 86.305.256                     86.305.256
Luca Malco   3.746.461 155.959.338     3.746.461   -52.702.914        56.449.375               3.746.461                 52.702.914                     52.702.914
```

## Top Market Candidates

- Frederik Rönnow | Team: Union Berlin | Score: 65.2 | Rolle: medium_term_hold | Delta: 149636.01 | Max: 7567418.0 | Competitive Max: 7567418.0 | Wettbewerb: high | Gegner: FC St. Pauli 1910 | Fixture: good
- Abdoul-Karim Coulibaly | Team: Bremen | Score: 63.6 | Rolle: short_term_trade | Delta: 235256.58 | Max: 3747066.0 | Competitive Max: 3747066.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Jens Grahl | Team: Frankfurt | Score: 62.9 | Rolle: short_term_trade | Delta: 166.71 | Max: 500080.0 | Competitive Max: 500080.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Tiago Pereira Cardoso | Team: M'gladbach | Score: 61.6 | Rolle: medium_term_hold | Delta: 143.29 | Max: 500052.0 | Competitive Max: 500052.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Igor Matanović | Team: Freiburg | Score: 60.9 | Rolle: medium_term_hold | Delta: -42043.54 | Max: 9158869.0 | Competitive Max: 9158869.0 | Wettbewerb: high | Gegner: None | Fixture: None

## Market Snapshot

```text
    first_name   last_name    team_name         mv  predicted_mv_change  priority_score recommended_bid_max  competitive_bid_max recent_bid_competition             bid_strategy_note position_label roster_need_level  team_missing_count  team_questionable_count team_availability_level  team_availability_priority_adjustment active_offer_decision active_offer_recommended_new_bid  hours_to_exp
      Frederik      Rönnow Union Berlin  7.513.549              149.636              65           7.567.418            7.567.418                   high aggressive_only_if_priority_a             GK            medium                   0                        0                  stable                                      0                     -                                -           677
  Abdoul-Karim   Coulibaly       Bremen  3.634.143              235.257              64           3.747.066            3.747.066                   high               avoid_price_war            DEF              none                   0                        0                  stable                                      0                     -                                -             9
          Jens       Grahl    Frankfurt    500.000                  167              63             500.080              500.080                   high               avoid_price_war             GK            medium                   0                        0                  stable                                      0                     -                                -             6
Tiago Pereira      Cardoso   M'gladbach    500.000                  143              62             500.052              500.052                   high               avoid_price_war             GK            medium                   0                        0                  stable                                      0                     -                                -            14
          Igor   Matanović     Freiburg  9.158.869              -42.044              61           9.158.869            9.158.869                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -             3
       Maarten Vandevoordt      Leipzig  4.457.377              -49.472              54           4.457.377            4.457.377                   high               avoid_price_war             GK            medium                   0                        0                  stable                                      0                     -                                -            22
    Maximilian Mittelstädt    Stuttgart 32.834.792               37.503              53          32.852.794           32.852.794                 medium              stay_disciplined            DEF              none                   0                        0                  stable                                      0                     -                                -             7
       Olivier       Deman       Bremen  4.130.656              -59.410              53           4.130.656            4.130.656                   high               avoid_price_war            DEF              none                   0                        0                  stable                                      0                     -                                -             2
        Justin     Njinmah       Bremen  6.052.077              146.477              52           6.104.809            6.104.809                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -           653
        Philip       Otele      Hamburg  6.244.160              146.483              52           6.296.894            6.296.894                   high aggressive_only_if_priority_a             ST              none                   0                        0                  stable                                      0                     -                                -           707
        Ridle         Baku      Leipzig 21.936.083               86.717              51          21.967.301           21.967.301                   high aggressive_only_if_priority_a            MID              none                   0                        0                  stable                                      0                     -                                -            22
          Ísak Jóhannesson         Köln  3.140.637               58.493              51           3.161.695            3.161.695                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -           677
        Joakim       Mæhle    Wolfsburg  4.193.816               56.748              50           4.214.245            4.214.245                   high aggressive_only_if_priority_a            DEF              none                   0                        0                  stable                                      0                     -                                -           677
Maycon Douglas     Cardozo       Bayern  1.794.912               26.267              48           1.804.368            1.804.368                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -           707
       Mattias    Svanberg    Wolfsburg    500.000                  143              48             500.052              500.052                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -            13
```

## Top Sell Candidates

- Robert Andrich | Team: Leverkusen | Sell Score: 21.4 | Rolle: rotation_hold | Delta: -226960.95 | Gegner: None | Fixture: None
- Manuel Neuer | Team: Bayern | Sell Score: 21.4 | Rolle: rotation_hold | Delta: 253232.58 | Gegner: None | Fixture: None
- Lucas Höler | Team: Freiburg | Sell Score: 18.9 | Rolle: rotation_hold | Delta: 916.76 | Gegner: None | Fixture: None
- Josha Vagnoman | Team: Stuttgart | Sell Score: 18.8 | Rolle: rotation_hold | Delta: 153620.72 | Gegner: None | Fixture: None
- Ermedin Demirović | Team: Stuttgart | Sell Score: 17.8 | Rolle: rotation_hold | Delta: 19805.66 | Gegner: None | Fixture: None

## Squad Snapshot

```text
first_name last_name  team_name         mv  predicted_mv_change  sell_priority_score    squad_role     squad_strategy_note  team_missing_count  team_questionable_count team_availability_level  team_availability_sell_adjustment s_11_prob            next_opponent
    Robert   Andrich Leverkusen 18.869.255             -226.961                   21 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
    Manuel     Neuer     Bayern  7.094.577              253.233                   21 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Lucas     Höler   Freiburg    500.000                  917                   19 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Josha  Vagnoman  Stuttgart  5.741.825              153.621                   19 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
   Ermedin Demirović  Stuttgart 20.636.973               19.806                   18 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
    Marvin Pieringer Heidenheim  2.245.957              130.800                   17 rotation_hold              model_only                   0                        0                  stable                                  0         - Borussia Mönchengladbach
 Christian   Eriksen  Wolfsburg 10.784.236               44.757                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
    Kaishu      Sano      Mainz 11.826.283               48.014                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -      TSG 1899 Hoffenheim
      Finn   Jeltsch  Stuttgart 10.852.259               71.012                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Marco    Friedl     Bremen 17.408.218             -162.840                    1  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -                        -
     Jakub  Kaminski       Köln 19.867.250               33.512                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -      Eintracht Frankfurt
     Serge    Gnabry     Bayern 30.132.505               65.603                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -                        -
```

## Active Offers

- Keine aktiven Gebote gespeichert

## Active Offer Actions

- Keine aktiven Gebotsentscheidungen gespeichert

## Recent Outbid Offers

- Keine ueberbotenen Gebote gespeichert

## Offer Tracking Debug

- Root Type: dict
- Candidate Count: 0
- Keine Debug-Kandidaten gespeichert

### Feed Structure Debug

- Pfad: root | Typ: dict | Laenge: None | Keys: it, u, unm
- Pfad: root.it | Typ: list | Laenge: 25 | Keys: 
- Pfad: root.it[0] | Typ: dict | Laenge: None | Keys: dt, pi, pim, pn, tid, trp, tty
- Pfad: root.it[1] | Typ: dict | Laenge: None | Keys: dt, pi, pim, pn, tid, trp, tty
- Pfad: root.it[2] | Typ: dict | Laenge: None | Keys: dt, pi, pim, pn, tid, trp, tty
- Pfad: root.it[3] | Typ: dict | Laenge: None | Keys: dt, pi, pim, pn, tid, trp, tty
- Pfad: root.it[4] | Typ: dict | Laenge: None | Keys: dt, pi, pim, pn, tid, trp, tty
- Pfad: root.it[5] | Typ: dict | Laenge: None | Keys: dt, pi, pim, pn, tid, trp, tty
- Pfad: root.it[6] | Typ: dict | Laenge: None | Keys: dt, pi, pim, pn, tid, trp, tty
- Pfad: root.it[7] | Typ: dict | Laenge: None | Keys: dt, pi, pim, pn, tid, trp, tty

### Market Feed Debug

- Root Type: list
- Item Count: 28
- Pfad: market[0] | Spieler: Jens Grahl | Spieler-ID: 357 | Marktwert: 500000.0 | Ablauf: 2026-03-30T15:51:00Z | Keys: dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, pim, pos, prc, st, tid | Sample: {"i": "357", "fn": "Jens", "n": "Grahl", "tid": "4", "pos": 1, "st": 0, "mvt": 0, "mv": 500000, "ofc": 0, "exs": 22630, "prc": 500000, "isn": false, "iposl": false, "dt": "2026-03-28T17:18:00Z", "pim": "content/file/3b8eae1b9d6d4e8d961bfd3f152db402.png"}
- Pfad: market[1] | Spieler: Mario Götze | Spieler-ID: 513 | Marktwert: 1167613.0 | Ablauf: 2026-03-31T16:03:38Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "513", "fn": "Mario", "n": "Götze", "tid": "4", "pos": 3, "st": 0, "mvt": 2, "mv": 1167613, "p": 634, "ap": 35, "ofc": 0, "exs": 109788, "prc": 1167613, "isn": true, "iposl": false, "dt": "2026-03-29T23:35:38Z", "pim": "content/file/3b8eae1b9d6d4e8d961bfd3f152db402.png"}
- Pfad: market[2] | Spieler: Stefan Bell | Spieler-ID: 550 | Marktwert: 1633318.0 | Ablauf: 2026-04-01T00:40:02Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "550", "fn": "Stefan", "n": "Bell", "tid": "18", "pos": 2, "st": 2, "mvt": 2, "mv": 1633318, "p": 1313, "ap": 73, "ofc": 0, "exs": 140772, "prc": 1633318, "isn": true, "iposl": false, "dt": "2026-03-30T01:46:02Z", "pim": "content/file/0563ba9a260a4fd0a9c193dc525529b3.png"}
- Pfad: market[3] | Spieler: Maximilian Mittelstädt | Spieler-ID: 1664 | Marktwert: 32834792.0 | Ablauf: 2026-03-30T16:18:07Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1664", "fn": "Maximilian", "n": "Mittelstädt", "tid": "9", "pos": 2, "st": 0, "mvt": 1, "mv": 32834792, "p": 3062, "ap": 122, "ofc": 0, "exs": 24257, "prc": 32834792, "isn": false, "iposl": false, "dt": "2026-03-28T20:31:07Z", "pim": "content/file/2dea6714f704489fa0fb302accce4e8a.png"}
- Pfad: market[4] | Spieler: Nico Elvedi | Spieler-ID: 1686 | Marktwert: 20695903.0 | Ablauf: 2026-04-01T02:31:27Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1686", "fn": "Nico", "n": "Elvedi", "tid": "15", "pos": 2, "st": 0, "mvt": 1, "mv": 20695903, "p": 2643, "ap": 98, "ofc": 0, "exs": 147457, "prc": 20695903, "isn": true, "iposl": false, "dt": "2026-03-30T03:59:27Z", "pim": "content/file/d4b8e5025d3043b3ad48c1f6ac91830d.png"}
- Pfad: market[5] | Spieler: Serhou Guirassy | Spieler-ID: 1920 | Marktwert: 38389860.0 | Ablauf: 2026-03-31T02:09:47Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1920", "fn": "Serhou", "n": "Guirassy", "tid": "3", "pos": 4, "st": 0, "mvt": 2, "mv": 38389860, "p": 2676, "ap": 103, "ofc": 0, "exs": 59757, "prc": 38389860, "isn": false, "iposl": false, "dt": "2026-03-29T05:07:47Z", "pim": "content/file/ed209b2ca67c4784a658521f80baa795.png"}
- Pfad: market[6] | Spieler: Ridle Baku | Spieler-ID: 2141 | Marktwert: 21936083.0 | Ablauf: 2026-03-31T07:53:21Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2141", "fn": "Ridle ", "n": "Baku", "tid": "43", "pos": 3, "st": 0, "mvt": 1, "mv": 21936083, "p": 2577, "ap": 103, "ofc": 0, "exs": 80371, "prc": 21936083, "isn": true, "iposl": false, "dt": "2026-03-30T07:12:21Z", "pim": "content/file/fe5ccc7927254a46ab71aeed829805e4.png"}
- Pfad: market[7] | Spieler: Frederik Rönnow | Spieler-ID: 2279 | Marktwert: 7513549.0 | Ablauf: 2026-04-27T14:10:25Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "2279", "fn": "Frederik", "n": "Rönnow", "tid": "40", "pos": 1, "st": 0, "mvt": 1, "mv": 7513549, "p": 2109, "ap": 81, "ofc": 0, "exs": 2435795, "u": {"i": "<nested>", "n": "<nested>", "uim": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 7215918, "isn": false, "iposl": false, "dt": "2026-03-28T14:10:25Z", "pim": "content/file/98159e30baca4a1080128a7a4c32914e.png"}
- Pfad: market[8] | Spieler: Yannik Keitel | Spieler-ID: 2764 | Marktwert: 500000.0 | Ablauf: 2026-03-31T19:01:35Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2764", "fn": "Yannik", "n": "Keitel", "tid": "13", "pos": 3, "st": 1, "mvt": 0, "mv": 500000, "p": 207, "ap": 52, "ofc": 0, "exs": 120465, "prc": 500000, "isn": true, "iposl": false, "dt": "2026-03-30T00:43:35Z", "pim": "content/file/b93977fb3dee4e75af09d67896a1666b.png"}
- Pfad: market[9] | Spieler: Eren Sami Dinkçi | Spieler-ID: 2939 | Marktwert: 1729640.0 | Ablauf: 2026-03-31T19:36:02Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2939", "fn": "Eren Sami", "n": "Dinkçi", "tid": "50", "pos": 3, "st": 0, "mvt": 2, "mv": 1729640, "p": 327, "ap": 20, "ofc": 0, "exs": 122532, "prc": 1729640, "isn": true, "iposl": false, "dt": "2026-03-30T09:22:02Z", "pim": "content/file/ef0f480acb2e4002811381446d78ae87.png"}

## AI Full Output

Hallo Luca, hier ist deine Kickbase-Portfolio-Strategie für den Montagabend.

### 1. TEAMSTATUS
Dein Kader ist mit 12 von 17 Spielern kompakt und qualitativ hochwertig besetzt. Mit 3,75 Mio. Euro verfügst du über ein solides, aber nicht üppiges Budget für den normalen Trading-Alltag. Der `TRADING_WINDOW_MODE: normal_build_up` bedeutet, wir müssen bis Freitag eine schlagkräftige und finanziell ausgeglichene Elf auf die Beine stellen. Deine dringendste Baustelle ist die Torwartposition, auf der du mit Manuel Neuer nur einen Keeper hast. Das ist ein klares Risiko, das wir diese Woche angehen müssen.

### 2. VERKAUFS-BEFEHLE
Aktuell sehe ich keinen akuten Verkaufsdruck. Deine "core_starter" Gnabry, Kaminski und Friedl sind systemseitig aufgrund der hohen Marktknappheit geschützt. Robert Andrich hat zwar eine leicht negative Marktwertprognose, die neuesten Meldungen deuten aber nicht auf einen akuten Leistungsabfall hin; ein Verkauf ist daher nicht zwingend. Wir halten den Kader zusammen und fokussieren uns auf gezielte Zukäufe.

### 3. SOFORT-KÄUFE BIS ZUM NAECHSTEN UPDATE
Für heute Nacht konzentrieren wir uns auf eine klare Chance, um kurzfristig Gewinn zu machen und gleichzeitig eine Kaderlücke zu schließen.

*   **Kauf Jens Grahl (GK, Frankfurt) | Priorität A | Max Gebot 555.000 Euro | Rolle: Trader & Backup-GK | Warum jetzt:** Grahl ist die perfekte Kombination aus geringem Risiko und strategischem Nutzen. Er hat eine positive Marktwertprognose, ist sehr günstig und schließt deine Torwartlücke. Selbst wenn er nicht spielt, bindet er kaum Kapital und sein Wert wird bis morgen leicht steigen. Der `estimated_market_winning_bid` liegt bei 625.000 Euro, aber wir bleiben diszipliniert, da der sportliche Wert als Ersatztorwart begrenzt ist.

*   **Nicht kaufen: Abdoul-Karim Coulibaly (DEF, Bremen):** Obwohl er eine gute Marktwertprognose hat, deuten Berichte von Anfang bis Mitte März darauf hin, dass er nach einer Oberschenkelverletzung noch im Aufbautraining ist. Das Risiko eines Rückschlags oder einer langsamen Heranführung ist zu hoch für einen kurzfristigen Trade.

*   **Nicht kaufen: Maximilian Mittelstädt (DEF, Stuttgart):** Sein Marktwert ist mit über 32 Mio. Euro für dein Budget nicht darstellbar, ohne wichtige Kaderspieler zu verkaufen.

### 4. SPAETERE CHANCEN UND HOLDS
Ein Spieler im späteren Marktsegment ist für uns von besonderem Interesse, um unsere Torwart-Situation langfristig zu klären:

*   **Beobachte Frederik Rönnow (GK, Union Berlin) | Zielstrategie: Spieltag | Späteres Max Gebot: ca. 7.600.000 Euro | Warum relevant:** Rönnow ist eine starke Nummer 1 und würde dein Torwart-Problem qualitativ hochwertig lösen. Sein Marktwert steigt stabil. Wir können ihn uns aktuell nicht leisten, aber wir sollten ihn im Auge behalten und durch kluge Trades in den nächsten Tagen das nötige Kapital erwirtschaften.

### 5. NEWS-CHECK
*   **Manuel Neuer:** Aktuelle Berichte vom 29. März 2026 bestätigen, dass Neuer nach seiner Wadenverletzung wieder fit ist und für die kommenden Spiele zur Verfügung steht. Das stabilisiert seinen Marktwert und bestätigt unsere Entscheidung, ihn zu halten.
*   **Ermedin Demirović:** Anfang Januar ist er nach einer längeren Verletzungspause wieder ins Training eingestiegen. Seine Situation scheint stabil, ein Verkauf ist nicht nötig.
*   **Robert Andrich:** Eine Meldung von Ende März deutet auf einen möglichen Umbruch in Leverkusen im Sommer hin, bei dem auch Andrich den Verein verlassen könnte. Dies ist für den Moment nicht akut, sollte aber für die langfristige Planung im Hinterkopf behalten werden.
*   **Olivier Deman:** Er kehrte nach einer schweren Knöchelverletzung im August 2025 Anfang des Jahres 2026 zurück ins Team. Die alten Verletzungsmeldungen sind für die aktuelle Situation nicht mehr relevant.
*   Für die übrigen überprüften Spieler (Igor Matanović, Marco Friedl, Serge Gnabry) wurden keine neuen, spielentscheidenden Informationen wie frische Verletzungen oder Sperren gefunden.

### 6. TRADING-PLAN
Unsere Strategie für die nächsten 2-4 Tage ist klar:
1.  **Kapitalaufbau:** Der Kauf und schnelle Verkauf von Jens Grahl soll einen kleinen, aber sicheren Gewinn bringen.
2.  **Markt beobachten:** Wir halten Ausschau nach günstigen Spielern mit positiver Marktwertprognose im Bereich bis 4 Mio. Euro, um unser Budget schrittweise zu erhöhen.
3.  **Zielobjekt Rönnow:** Jeder erwirtschaftete Euro bringt uns näher an die Verpflichtung von Frederik Rönnow oder einer vergleichbaren Nummer 1. Dies hat Priorität, um die Kaderlücke zu schließen.

### 7. FRIDAY-CHECK
Bis Freitagabend, 03. April 2026, müssen wir folgende Punkte sicherstellen:
*   **Kontostand:** Dein Kontostand muss bei 0 Euro oder im Plus sein. Der Kauf von Grahl gefährdet dieses Ziel nicht.
*   **Team:** Dein Team muss spielfähig sein. Der Kauf von Grahl als zweitem Torwart erhöht deine Flexibilität und sichert dich für den Spieltag ab. Wir werden in den kommenden Tagen darauf achten, eine volle, punktende Mannschaft aufzustellen.
