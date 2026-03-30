# Last Run Summary

- Report Date: 30. March 2026
- Generated At: 2026-03-30T11:34:22.018090Z
- User: Luca Malco
- Own Budget: 3746461.0
- Market Players: 29
- Squad Players: 12
- Fixture Context Active: True
- AI Status: success
- Mail Status: success
- Offer Tracking Active: 0
- Offer Tracking Outbid: 0
- Offer Tracking Won: 0

## Model Metrics

- Signs Correct: 66.81
- RMSE: 41904.45
- MAE: 20876.48
- R2: 0.9191

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
- Echte strukturelle Luecken: 0
- Primaerer Bedarf ist echte Luecke: False

- GK | Im Kader: 1 | Minimum: 1 | Marktoptionen: 2 | Bedarf: medium | Hinweis: Torwartposition ist besetzt, aber aktuell ohne Ersatzoption im Kader. Backup nicht zu spaet angehen.

## API-Football Summary

- API-Football aktiv: False
- Grund: request_failed
- Liga: None
- Season: 2024
- Angefragte Season: 2025
- Live-Season Referenz: 2025
- Season-Fallback aktiv: True
- Historische Season aktiv: True
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
- Fehler: API-Football /leagues returned errors: access: Your account is suspended, check on https://dashboard.api-football.com.

- Keine auffaelligen Team-Ausfaelle im API-Football Kontext

## Strategy Validation

- Keine offensichtlichen Strategie-Konflikte erkannt.

## Manager Budget Snapshot

```text
      User      Budget  Team Value  Current Cash  Max Negative  Available Budget  Spendable Without Debt  Temporary Negative Buffer  Friday Recovery Need At Floor
      joel 126.686.923 175.983.956   126.686.923   -99.881.390       226.568.313             126.686.923                 99.881.390                     99.881.390
       Rob 124.321.302 159.174.221   124.321.302   -93.553.523       217.874.825             124.321.302                 93.553.523                     93.553.523
 FlippiXxp  72.920.330 302.829.996    72.920.330  -123.997.608       196.917.938              72.920.330                123.997.608                    123.997.608
       Jan  73.292.889 201.610.723    73.292.889   -90.718.192       164.011.081              73.292.889                 90.718.192                     90.718.192
     Jonas  71.156.552 161.133.590    71.156.552   -76.655.747       147.812.299              71.156.552                 76.655.747                     76.655.747
      Till  47.663.360 236.655.620    47.663.360   -93.825.263       141.488.623              47.663.360                 93.825.263                     93.825.263
     David  16.717.482 244.813.597    16.717.482   -86.305.256       103.022.738              16.717.482                 86.305.256                     86.305.256
Luca Malco   3.746.461 155.959.338     3.746.461   -52.702.914        56.449.375               3.746.461                 52.702.914                     52.702.914
```

## Top Market Candidates

- Jens Grahl | Team: Frankfurt | Score: 67.7 | Rolle: short_term_trade | Delta: 208.18 | Max: 500100.0 | Competitive Max: 500100.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Abdoul-Karim Coulibaly | Team: Bremen | Score: 67.1 | Rolle: short_term_trade | Delta: 232065.03 | Max: 3745534.0 | Competitive Max: 3745534.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Igor Matanović | Team: Freiburg | Score: 65.7 | Rolle: medium_term_hold | Delta: -45095.15 | Max: 9158869.0 | Competitive Max: 9158869.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Frederik Rönnow | Team: Union Berlin | Score: 65.2 | Rolle: medium_term_hold | Delta: 148006.44 | Max: 7566831.0 | Competitive Max: 7566831.0 | Wettbewerb: high | Gegner: FC St. Pauli 1910 | Fixture: good
- Tiago Pereira Cardoso | Team: M'gladbach | Score: 62.3 | Rolle: medium_term_hold | Delta: 144.38 | Max: 500052.0 | Competitive Max: 500052.0 | Wettbewerb: high | Gegner: None | Fixture: None

## Market Snapshot

```text
    first_name   last_name    team_name         mv  predicted_mv_change  priority_score recommended_bid_max  competitive_bid_max recent_bid_competition             bid_strategy_note position_label roster_need_level  team_missing_count  team_questionable_count team_availability_level  team_availability_priority_adjustment active_offer_decision active_offer_recommended_new_bid  hours_to_exp
          Jens       Grahl    Frankfurt    500.000                  208              68             500.100              500.100                   high               avoid_price_war             GK            medium                   0                        0                  stable                                      0                     -                                -             4
  Abdoul-Karim   Coulibaly       Bremen  3.634.143              232.065              67           3.745.534            3.745.534                   high               avoid_price_war            DEF              none                   0                        0                  stable                                      0                     -                                -             7
          Igor   Matanović     Freiburg  9.158.869              -45.095              66           9.158.869            9.158.869                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -             1
      Frederik      Rönnow Union Berlin  7.513.549              148.006              65           7.566.831            7.566.831                   high aggressive_only_if_priority_a             GK            medium                   0                        0                  stable                                      0                     -                                -           675
Tiago Pereira      Cardoso   M'gladbach    500.000                  144              62             500.052              500.052                   high               avoid_price_war             GK            medium                   0                        0                  stable                                      0                     -                                -            12
    Maximilian Mittelstädt    Stuttgart 32.834.792               36.000              58          32.852.072           32.852.072                 medium              stay_disciplined            DEF              none                   0                        0                  stable                                      0                     -                                -             5
       Olivier       Deman       Bremen  4.130.656              -56.438              58           4.130.656            4.130.656                   high               avoid_price_war            DEF              none                   0                        0                  stable                                      0                     -                                -             0
       Maarten Vandevoordt      Leipzig  4.457.377              -50.877              54           4.457.377            4.457.377                   high               avoid_price_war             GK            medium                   0                        0                  stable                                      0                     -                                -            20
        Justin     Njinmah       Bremen  6.052.077              147.640              52           6.105.227            6.105.227                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -           651
        Ridle         Baku      Leipzig 21.936.083               86.733              52          21.967.307           21.967.307                   high aggressive_only_if_priority_a            MID              none                   0                        0                  stable                                      0                     -                                -            20
        Philip       Otele      Hamburg  6.244.160              147.476              52           6.297.251            6.297.251                   high aggressive_only_if_priority_a             ST              none                   0                        0                  stable                                      0                     -                                -           705
     Arkadiusz       Pyrka    St. Pauli  3.570.223             -101.195              52           3.570.223            3.570.223                   high               avoid_price_war            DEF              none                   0                        0                  stable                                      0                     -                                -             2
          Ísak Jóhannesson         Köln  3.140.637               50.018              50           3.158.644            3.158.644                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -           675
        Joakim       Mæhle    Wolfsburg  4.193.816               55.475              50           4.213.787            4.213.787                   high aggressive_only_if_priority_a            DEF              none                   0                        0                  stable                                      0                     -                                -           675
       Mattias    Svanberg    Wolfsburg    500.000                  144              49             500.052              500.052                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -            11
```

## Top Sell Candidates

- Robert Andrich | Team: Leverkusen | Sell Score: 21.5 | Rolle: rotation_hold | Delta: -228675.73 | Gegner: None | Fixture: None
- Manuel Neuer | Team: Bayern | Sell Score: 21.4 | Rolle: rotation_hold | Delta: 253202.61 | Gegner: None | Fixture: None
- Lucas Höler | Team: Freiburg | Sell Score: 18.9 | Rolle: rotation_hold | Delta: 1113.61 | Gegner: None | Fixture: None
- Josha Vagnoman | Team: Stuttgart | Sell Score: 18.8 | Rolle: rotation_hold | Delta: 156129.7 | Gegner: None | Fixture: None
- Ermedin Demirović | Team: Stuttgart | Sell Score: 17.8 | Rolle: rotation_hold | Delta: 18585.03 | Gegner: None | Fixture: None

## Squad Snapshot

```text
first_name last_name  team_name         mv  predicted_mv_change  sell_priority_score    squad_role     squad_strategy_note  team_missing_count  team_questionable_count team_availability_level  team_availability_sell_adjustment s_11_prob            next_opponent
    Robert   Andrich Leverkusen 18.869.255             -228.676                   22 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
    Manuel     Neuer     Bayern  7.094.577              253.203                   21 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Lucas     Höler   Freiburg    500.000                1.114                   19 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Josha  Vagnoman  Stuttgart  5.741.825              156.130                   19 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
   Ermedin Demirović  Stuttgart 20.636.973               18.585                   18 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
    Marvin Pieringer Heidenheim  2.245.957              137.343                   17 rotation_hold              model_only                   0                        0                  stable                                  0         - Borussia Mönchengladbach
 Christian   Eriksen  Wolfsburg 10.784.236               47.485                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
    Kaishu      Sano      Mainz 11.826.283               49.276                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -      TSG 1899 Hoffenheim
      Finn   Jeltsch  Stuttgart 10.852.259               70.063                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Marco    Friedl     Bremen 17.408.218             -157.176                    1  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -                        -
     Jakub  Kaminski       Köln 19.867.250               31.572                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -      Eintracht Frankfurt
     Serge    Gnabry     Bayern 30.132.505               65.897                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -                        -
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
- Item Count: 29
- Pfad: market[0] | Spieler: Jens Grahl | Spieler-ID: 357 | Marktwert: 500000.0 | Ablauf: 2026-03-30T15:51:00Z | Keys: dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, pim, pos, prc, st, tid | Sample: {"i": "357", "fn": "Jens", "n": "Grahl", "tid": "4", "pos": 1, "st": 0, "mvt": 0, "mv": 500000, "ofc": 0, "exs": 15482, "prc": 500000, "isn": false, "iposl": false, "dt": "2026-03-28T17:18:00Z", "pim": "content/file/3b8eae1b9d6d4e8d961bfd3f152db402.png"}
- Pfad: market[1] | Spieler: Mario Götze | Spieler-ID: 513 | Marktwert: 1167613.0 | Ablauf: 2026-03-31T16:03:38Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "513", "fn": "Mario", "n": "Götze", "tid": "4", "pos": 3, "st": 0, "mvt": 2, "mv": 1167613, "p": 634, "ap": 35, "ofc": 0, "exs": 102640, "prc": 1167613, "isn": true, "iposl": false, "dt": "2026-03-29T23:35:38Z", "pim": "content/file/3b8eae1b9d6d4e8d961bfd3f152db402.png"}
- Pfad: market[2] | Spieler: Stefan Bell | Spieler-ID: 550 | Marktwert: 1633318.0 | Ablauf: 2026-04-01T00:40:02Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "550", "fn": "Stefan", "n": "Bell", "tid": "18", "pos": 2, "st": 2, "mvt": 2, "mv": 1633318, "p": 1313, "ap": 73, "ofc": 0, "exs": 133624, "prc": 1633318, "isn": true, "iposl": false, "dt": "2026-03-30T01:46:02Z", "pim": "content/file/0563ba9a260a4fd0a9c193dc525529b3.png"}
- Pfad: market[3] | Spieler: Maximilian Mittelstädt | Spieler-ID: 1664 | Marktwert: 32834792.0 | Ablauf: 2026-03-30T16:18:07Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1664", "fn": "Maximilian", "n": "Mittelstädt", "tid": "9", "pos": 2, "st": 0, "mvt": 1, "mv": 32834792, "p": 3062, "ap": 122, "ofc": 0, "exs": 17109, "prc": 32834792, "isn": false, "iposl": false, "dt": "2026-03-28T20:31:07Z", "pim": "content/file/2dea6714f704489fa0fb302accce4e8a.png"}
- Pfad: market[4] | Spieler: Nico Elvedi | Spieler-ID: 1686 | Marktwert: 20695903.0 | Ablauf: 2026-04-01T02:31:27Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1686", "fn": "Nico", "n": "Elvedi", "tid": "15", "pos": 2, "st": 0, "mvt": 1, "mv": 20695903, "p": 2643, "ap": 98, "ofc": 0, "exs": 140309, "prc": 20695903, "isn": true, "iposl": false, "dt": "2026-03-30T03:59:27Z", "pim": "content/file/d4b8e5025d3043b3ad48c1f6ac91830d.png"}
- Pfad: market[5] | Spieler: Serhou Guirassy | Spieler-ID: 1920 | Marktwert: 38389860.0 | Ablauf: 2026-03-31T02:09:47Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1920", "fn": "Serhou", "n": "Guirassy", "tid": "3", "pos": 4, "st": 0, "mvt": 2, "mv": 38389860, "p": 2676, "ap": 103, "ofc": 0, "exs": 52609, "prc": 38389860, "isn": false, "iposl": false, "dt": "2026-03-29T05:07:47Z", "pim": "content/file/ed209b2ca67c4784a658521f80baa795.png"}
- Pfad: market[6] | Spieler: Ridle Baku | Spieler-ID: 2141 | Marktwert: 21936083.0 | Ablauf: 2026-03-31T07:53:21Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2141", "fn": "Ridle ", "n": "Baku", "tid": "43", "pos": 3, "st": 0, "mvt": 1, "mv": 21936083, "p": 2577, "ap": 103, "ofc": 0, "exs": 73223, "prc": 21936083, "isn": true, "iposl": false, "dt": "2026-03-30T07:12:21Z", "pim": "content/file/fe5ccc7927254a46ab71aeed829805e4.png"}
- Pfad: market[7] | Spieler: Frederik Rönnow | Spieler-ID: 2279 | Marktwert: 7513549.0 | Ablauf: 2026-04-27T14:10:25Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "2279", "fn": "Frederik", "n": "Rönnow", "tid": "40", "pos": 1, "st": 0, "mvt": 1, "mv": 7513549, "p": 2109, "ap": 81, "ofc": 0, "exs": 2428647, "u": {"i": "<nested>", "n": "<nested>", "uim": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 7215918, "isn": false, "iposl": false, "dt": "2026-03-28T14:10:25Z", "pim": "content/file/98159e30baca4a1080128a7a4c32914e.png"}
- Pfad: market[8] | Spieler: Yannik Keitel | Spieler-ID: 2764 | Marktwert: 500000.0 | Ablauf: 2026-03-31T19:01:35Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2764", "fn": "Yannik", "n": "Keitel", "tid": "13", "pos": 3, "st": 1, "mvt": 0, "mv": 500000, "p": 207, "ap": 52, "ofc": 0, "exs": 113317, "prc": 500000, "isn": true, "iposl": false, "dt": "2026-03-30T00:43:35Z", "pim": "content/file/b93977fb3dee4e75af09d67896a1666b.png"}
- Pfad: market[9] | Spieler: Eren Sami Dinkçi | Spieler-ID: 2939 | Marktwert: 1729640.0 | Ablauf: 2026-03-31T19:36:02Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2939", "fn": "Eren Sami", "n": "Dinkçi", "tid": "50", "pos": 3, "st": 0, "mvt": 2, "mv": 1729640, "p": 327, "ap": 20, "ofc": 0, "exs": 115384, "prc": 1729640, "isn": true, "iposl": false, "dt": "2026-03-30T09:22:02Z", "pim": "content/file/ef0f480acb2e4002811381446d78ae87.png"}

## AI Full Output

Hallo Luca, hier ist deine Kickbase-Portfolio-Analyse für den Montagabend.

### 1. TEAMSTATUS
Dein Kader ist mit 12 von 17 Spielern gut aufgestellt und du hast mit 3.746.461 Euro ein solides, positives Budget für gezielte Trades. Der `TRADING_WINDOW_MODE` ist `normal_build_up`, das heißt, der Fokus liegt auf dem schrittweisen Aufbau zum Spieltag in 6 Tagen. Dein dringendster Handlungsbedarf ist die Besetzung der Backup-Torwartposition, was aktuell aber nur eine mittlere Priorität hat, da Manuel Neuer als Starter gesetzt ist. Die hohe Marktknappheit für gute Spieler bedeutet, dass wir unsere Kernspieler mit Bedacht halten sollten.

### 2. VERKAUFS-BEFEHLE
Aktuell empfehle ich **keine Notverkäufe**.
*   **Robert Andrich** und **Marco Friedl** haben zwar leichte negative Marktwertprognosen, sind aber sportlich wichtige Stützen in deinem Kader. Friedl gilt bei Werder als konstanter Punktelieferant und der Trend in Bremen ist positiv. Für Andrich gibt es keine neuen negativen Meldungen bezüglich Verletzungen oder Sperren; die Suchergebnisse beziehen sich auf eine alte Sperre aus dem Jahr 2021. Beide zu verkaufen würde aktuell mehr schaden als nutzen, da adäquater Ersatz schwer zu finden ist. Wir beobachten ihre Marktwerte, halten aber vorerst.

### 3. SOFORT-KÄUFE BIS ZUM NAECHSTEN UPDATE
*   **Kauf Abdoul-Karim Coulibaly | Priorität A | Max Gebot 3.745.500 € | Rolle: Trader | Warum jetzt:** Coulibaly ist die Top-Gelegenheit für einen kurzfristigen Gewinn. Er hat mit +232.065 Euro die beste Marktwertprognose aller heute auslaufenden Spieler. Dein Budget von ca. 3,75 Mio. Euro passt exakt auf seinen Marktwert und die empfohlene Gebotsgrenze. Aktuelle Nachrichten deuten darauf hin, dass er nach einer Verletzungspause seit dem 15. März wieder im Kader steht, was seine Einsatzchancen und damit seinen Marktwert weiter steigern sollte. Er ist als "regular starter when fit" bekannt. Dieser Trade ist ein klassischer "Overnight-Flip", um schnell Kapital für weitere Investitionen zu generieren.

### 4. SPÄTERE CHANCEN UND HOLDS
*   **Beobachte Frederik Rönnow | Zielstrategie: Kaderbaustein (Spieltag) | Späteres Max Gebot: ca. 7,6 Mio. € | Warum relevant:** Rönnow ist eine ausgezeichnete Option, um deine Torwart-Position mit einem starken Backup abzusichern. Sein Marktwert von ca. 7,5 Mio. Euro ist aktuell nicht zu stemmen, aber nach dem Verkauf von Coulibaly und eventuell weiteren kleineren Trades rückt er in Reichweite. Halte ihn unbedingt auf deiner Watchlist.

### 5. NEWS-CHECK
Die Recherche hat ergeben, dass die negativen Informationen zu Robert Andrich veraltet sind und sich auf das Jahr 2021 beziehen. Für Serge Gnabry und Marco Friedl gibt es keine aktuellen, besorgniserregenden Meldungen bezüglich Verletzungen oder Leistungsschwankungen. Die wichtigste Information ist die Rückkehr von Kaufkandidat Abdoul-Karim Coulibaly in den Bremer Kader, was das Vertrauen in einen positiven Marktwerttrend stärkt.

### 6. TRADING-PLAN
Deine Strategie für die nächsten Tage ist klar auf Kapitalwachstum und Kaderabsicherung ausgelegt:
1.  **Heute (Montag):** Kaufe Abdoul-Karim Coulibaly für maximal 3.745.500 €. Das bindet dein gesamtes Kapital, aber mit hohem Potenzial auf einen schnellen Gewinn.
2.  **Morgen (Dienstag):** Verkaufe Coulibaly direkt wieder mit dem erwarteten Marktwertgewinn.
3.  **Dienstag/Mittwoch:** Nutze das frische Kapital, um eine Entscheidung bei der Backup-Torwart-Position zu treffen. Idealerweise greifen wir hier Frederik Rönnow an, falls das Budget reicht.
4.  **Bis Freitag:** Fülle den Kader schrittweise mit 2-3 weiteren Spielern auf, die entweder gutes Trading-Potenzial haben oder deine Bank für den Spieltag stärken.

### 7. FRIDAY-CHECK
Bis Freitagabend müssen wir die folgenden Ziele erreichen:
*   **Kontostand:** Dein Kontostand muss >= 0 Euro sein. Der Verkauf von Coulibaly ist dafür der erste und wichtigste Schritt.
*   **Team-Setup:** Du benötigst eine vollständige, spielbereite Aufstellung für den 28. Spieltag. Da dein Kernteam steht, geht es hier primär darum, die Bankplätze sinnvoll zu besetzen und den Backup-Torwart zu verpflichten. Nach dem heutigen Kauf wird dein Budget aufgebraucht sein, daher ist der erfolgreiche Flip von Coulibaly entscheidend für die Handlungsfähigkeit im Rest der Woche.
