# Last Run Summary

- Report Date: 28. March 2026
- Generated At: 2026-03-28T16:06:26.226860Z
- User: Luca Malco
- Own Budget: -2607028.0
- Market Players: 32
- Squad Players: 13
- Fixture Context Active: True
- AI Status: success
- Mail Status: success
- Offer Tracking Active: 0
- Offer Tracking Outbid: 0
- Offer Tracking Won: 0

## Model Metrics

- Signs Correct: 67.17
- RMSE: 42309.96
- MAE: 21131.02
- R2: 0.9177

## Matchday Context

- Next Matchday: 28
- Next Matchday Date: 05-04-2026 17:30
- Days Until Next Matchday: 8
- Trading Window Mode: extended_break
- Friday Safety Mode: inactive

## Own Budget Context

- Budget: -2607028.0
- Current Cash: -2607028.0
- Spendable Without Debt: 0.0
- Temporary Negative Buffer: 49484379.17
- Theoretical Max Spend: 49484379.17
- Max Negative: -52091407.17
- Friday Recovery Need At Floor: 52091407.17

## Management Summary

- Aktive Gebotssumme: 0.0
- Effektives Cash nach aktiven Geboten: -2607028.0
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

- Primaerer Positionsbedarf: none
- Dringlichkeit: none
- Positionen mit Bedarf: 0

- Kein akuter Positionsbedarf erkannt

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

- Aktive Gebote binden mehr Kapital als aktuell als Budget ausgewiesen ist.

## Manager Budget Snapshot

```text
      User      Budget  Team Value  Current Cash  Max Negative  Available Budget  Spendable Without Debt  Temporary Negative Buffer  Friday Recovery Need At Floor
      joel 129.951.508 201.712.916   129.951.508  -109.449.260       239.400.768             129.951.508                109.449.260                    109.449.260
       Rob 102.844.111 175.792.662   102.844.111   -91.950.135       194.794.246             102.844.111                 91.950.135                     91.950.135
 FlippiXxp  54.858.542 321.053.721    54.858.542  -124.051.047       178.909.589              54.858.542                124.051.047                    124.051.047
       Jan  65.460.846 200.737.034    65.460.846   -87.845.300       153.306.146              65.460.846                 87.845.300                     87.845.300
     Jonas  71.056.552 163.001.731    71.056.552   -77.239.233       148.295.785              71.056.552                 77.239.233                     77.239.233
     David  42.354.416 234.278.055    42.354.416   -91.288.715       133.643.131              42.354.416                 91.288.715                     91.288.715
      Till  30.946.888 279.015.106    30.946.888  -102.287.458       133.234.346              30.946.888                102.287.458                    102.287.458
Luca Malco  -2.607.028 160.459.777    -2.607.028   -52.091.407        49.484.379                       0                 49.484.379                     52.091.407
```

## Top Market Candidates

- Maycon Douglas Cardozo | Team: Bayern | Score: 70.3 | Rolle: short_term_trade | Delta: 160516.05 | Max: 1638711.0 | Competitive Max: 1638711.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Hennes Behrens | Team: Heidenheim | Score: 70.2 | Rolle: short_term_trade | Delta: 161182.78 | Max: 2266115.0 | Competitive Max: 2266115.0 | Wettbewerb: high | Gegner: Borussia Mönchengladbach | Fixture: good
- Budu Zivzivadze | Team: Heidenheim | Score: 64.3 | Rolle: short_term_trade | Delta: 144947.69 | Max: 1051209.0 | Competitive Max: 1051209.0 | Wettbewerb: high | Gegner: Borussia Mönchengladbach | Fixture: good
- Assan Ouédraogo | Team: Leipzig | Score: 60.8 | Rolle: medium_term_hold | Delta: 320573.57 | Max: 9288306.0 | Competitive Max: 9288306.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Benjamin Henrichs | Team: Leipzig | Score: 58.1 | Rolle: medium_term_hold | Delta: 156498.07 | Max: 6036260.0 | Competitive Max: 6036260.0 | Wettbewerb: high | Gegner: None | Fixture: None

## Market Snapshot

```text
    first_name   last_name    team_name         mv  predicted_mv_change  priority_score recommended_bid_max  competitive_bid_max recent_bid_competition             bid_strategy_note position_label roster_need_level  team_missing_count  team_questionable_count team_availability_level  team_availability_priority_adjustment active_offer_decision active_offer_recommended_new_bid  hours_to_exp
Maycon Douglas     Cardozo       Bayern  1.561.663              160.516              70           1.638.711            1.638.711                   high               avoid_price_war              -              none                   0                        0                  stable                                      0                     -                                -            11
        Hennes     Behrens   Heidenheim  2.188.747              161.183              70           2.266.115            2.266.115                   high               avoid_price_war              -              none                   0                        0                  stable                                      0                     -                                -            14
          Budu  Zivzivadze   Heidenheim    994.336              144.948              64           1.051.209            1.051.209                   high               avoid_price_war              -              none                   0                        0                  stable                                      0                     -                                -            33
         Assan   Ouédraogo      Leipzig  9.172.900              320.574              61           9.288.306            9.288.306                   high aggressive_only_if_priority_a              -              none                   0                        0                  stable                                      0                     -                                -            12
      Benjamin    Henrichs      Leipzig  5.979.921              156.498              58           6.036.260            6.036.260                   high aggressive_only_if_priority_a              -              none                   0                        0                  stable                                      0                     -                                -            23
          Ísak Jóhannesson         Köln  2.927.729              167.777              57           3.008.262            3.008.262                   high               avoid_price_war              -              none                   0                        0                  stable                                      0                     -                                -           718
         Lukas Klostermann      Leipzig    500.000                  380              56             500.182              500.182                   high               avoid_price_war              -              none                   0                        0                  stable                                      0                     -                                -             3
        Justin     Njinmah       Bremen  5.709.600              210.080              54           5.785.229            5.785.229                   high               avoid_price_war              -              none                   0                        0                  stable                                      0                     -                                -           695
        Joakim       Mæhle    Wolfsburg  3.988.803              129.017              53           4.035.249            4.035.249                   high aggressive_only_if_priority_a              -              none                   0                        0                  stable                                      0                     -                                -           718
          Finn      Dahmen     Augsburg 11.260.605               17.623              52          11.266.949           11.266.949                    low                model_range_ok              -              none                   0                        0                  stable                                      0                     -                                -            15
      Frederik      Rönnow Union Berlin  7.215.918              187.298              52           7.283.345            7.331.366                   high aggressive_only_if_priority_a              -              none                   0                        0                  stable                                      0                     -                                -           718
    Ricky-Jade       Jones    St. Pauli    500.000                  212              51             500.076              500.076                   high               avoid_price_war              -              none                   0                        0                  stable                                      0                     -                                -             6
     Christian      Günter     Freiburg  3.419.405             -122.781              49           3.419.405            3.419.405                   high               avoid_price_war              -              none                   0                        0                  stable                                      0                     -                                -             1
      Leonardo Bittencourt       Bremen  3.335.280                7.901              49           3.338.124            3.338.124                   high               avoid_price_war              -              none                   0                        0                  stable                                      0                     -                                -           695
         Louis       Oppie    St. Pauli    500.000                2.670              48             500.961              500.961                   high               avoid_price_war              -              none                   0                        0                  stable                                      0                     -                                -            18
```

## Top Sell Candidates

- Manuel Neuer | Team: Bayern | Sell Score: 21.6 | Rolle: rotation_hold | Delta: 259950.83 | Gegner: None | Fixture: None
- Lucas Höler | Team: Freiburg | Sell Score: 19.0 | Rolle: rotation_hold | Delta: 2711.78 | Gegner: None | Fixture: None
- Josha Vagnoman | Team: Stuttgart | Sell Score: 18.9 | Rolle: rotation_hold | Delta: 191998.39 | Gegner: None | Fixture: None
- Ermedin Demirović | Team: Stuttgart | Sell Score: 17.9 | Rolle: rotation_hold | Delta: 14129.58 | Gegner: None | Fixture: None
- Dimitris Giannoulis | Team: Augsburg | Sell Score: 17.1 | Rolle: rotation_hold | Delta: 28345.49 | Gegner: Hamburger SV | Fixture: good

## Squad Snapshot

```text
first_name  last_name  team_name         mv  predicted_mv_change  sell_priority_score    squad_role     squad_strategy_note  team_missing_count  team_questionable_count team_availability_level  team_availability_sell_adjustment s_11_prob            next_opponent
    Manuel      Neuer     Bayern  6.556.759              259.951                   22 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Lucas      Höler   Freiburg    500.000                2.712                   19 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Josha   Vagnoman  Stuttgart  5.380.852              191.998                   19 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
   Ermedin  Demirović  Stuttgart 20.603.593               14.130                   18 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
  Dimitris Giannoulis   Augsburg  6.343.938               28.345                   17 rotation_hold              model_only                   0                        0                  stable                                  0         -             Hamburger SV
    Marvin  Pieringer Heidenheim  1.939.238              188.604                   17 rotation_hold              model_only                   0                        0                  stable                                  0         - Borussia Mönchengladbach
    Robert    Andrich Leverkusen 18.909.198               18.544                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
 Christian    Eriksen  Wolfsburg 10.649.466              102.807                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
    Kaishu       Sano      Mainz 11.670.896              103.930                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -      TSG 1899 Hoffenheim
      Finn    Jeltsch  Stuttgart 10.707.219               88.425                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Marco     Friedl     Bremen 17.445.350               16.498                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -                        -
     Serge     Gnabry     Bayern 29.997.993               72.266                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -                        -
     Jakub   Kaminski       Köln 19.755.275               94.129                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -      Eintracht Frankfurt
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
- Item Count: 32
- Pfad: market[0] | Spieler: Christian Günter | Spieler-ID: 89 | Marktwert: 3419405.0 | Ablauf: 2026-03-28T16:49:15Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "89", "fn": "Christian", "n": "Günter", "tid": "5", "pos": 2, "st": 0, "mvt": 2, "mv": 3419405, "p": 987, "ap": 52, "ofc": 0, "exs": 2617, "prc": 3419405, "isn": false, "iposl": false, "dt": "2026-03-28T03:10:14Z", "pim": "content/file/7d6a4935195d414a9119e81aa398222a.png"}
- Pfad: market[1] | Spieler: Kevin Akpoguma | Spieler-ID: 96 | Marktwert: 500000.0 | Ablauf: 2026-03-30T00:49:07Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "96", "fn": "Kevin", "n": "Akpoguma", "tid": "14", "pos": 2, "st": 0, "mvt": 0, "mv": 500000, "p": -75, "ap": -15, "ofc": 0, "exs": 117809, "prc": 500000, "isn": true, "iposl": false, "dt": "2026-03-28T08:40:06Z", "pim": "content/file/1fe930ae579e4ba78fe7c4f948264d3b.png"}
- Pfad: market[2] | Spieler: Niklas Stark | Spieler-ID: 157 | Marktwert: 2708769.0 | Ablauf: 2026-03-28T22:38:30Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "157", "fn": "Niklas", "n": "Stark", "tid": "10", "pos": 2, "st": 2, "mvt": 2, "mv": 2708769, "p": 410, "ap": 34, "ofc": 0, "exs": 23572, "prc": 2708769, "isn": false, "iposl": false, "dt": "2026-03-27T20:38:29Z", "pim": "content/file/1a88a39549924d048294f618079e8437.png"}
- Pfad: market[3] | Spieler: Leonardo Bittencourt | Spieler-ID: 624 | Marktwert: 3335280.0 | Ablauf: 2026-04-26T14:40:42Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "624", "fn": "Leonardo", "n": "Bittencourt", "tid": "10", "pos": 3, "st": 0, "mvt": 1, "mv": 3335280, "p": 432, "ap": 33, "ofc": 0, "exs": 2500504, "u": {"i": "<nested>", "n": "<nested>", "uim": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 3265721, "isn": false, "iposl": false, "dt": "2026-03-27T14:40:41Z", "pim": "content/file/1a88a39549924d048294f618079e8437.png"}
- Pfad: market[4] | Spieler: Leon Goretzka | Spieler-ID: 660 | Marktwert: 19563668.0 | Ablauf: 2026-04-27T14:10:57Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "660", "fn": "Leon", "n": "Goretzka", "tid": "2", "pos": 3, "st": 0, "mvt": 1, "mv": 19563668, "p": 2658, "ap": 111, "ofc": 0, "exs": 2585119, "u": {"i": "<nested>", "n": "<nested>", "uim": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 19563668, "isn": true, "iposl": false, "dt": "2026-03-28T14:10:56Z", "pim": "content/file/48622993193e45f09d696908d75ed523.png"}
- Pfad: market[5] | Spieler: Lukas Klostermann | Spieler-ID: 1333 | Marktwert: 500000.0 | Ablauf: 2026-03-28T19:27:36Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1333", "fn": "Lukas", "n": "Klostermann", "tid": "43", "pos": 2, "st": 0, "mvt": 0, "mv": 500000, "p": 53, "ap": 13, "ofc": 0, "exs": 12118, "prc": 500000, "isn": false, "iposl": false, "dt": "2026-03-27T06:27:35Z", "pim": "content/file/fe5ccc7927254a46ab71aeed829805e4.png"}
- Pfad: market[6] | Spieler: Alexander Nübel | Spieler-ID: 1581 | Marktwert: 20015494.0 | Ablauf: 2026-04-27T14:10:25Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "1581", "fn": "Alexander", "n": "Nübel", "tid": "9", "pos": 1, "st": 0, "mvt": 1, "mv": 20015494, "p": 3169, "ap": 117, "ofc": 0, "exs": 2585087, "u": {"i": "<nested>", "n": "<nested>", "uim": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 20015494, "isn": true, "iposl": false, "dt": "2026-03-28T14:10:24Z", "pim": "content/file/2dea6714f704489fa0fb302accce4e8a.png"}
- Pfad: market[7] | Spieler: Benjamin Henrichs | Spieler-ID: 1689 | Marktwert: 5979921.0 | Ablauf: 2026-03-29T15:21:02Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1689", "fn": "Benjamin", "n": "Henrichs", "tid": "43", "pos": 2, "st": 0, "mvt": 1, "mv": 5979921, "p": 359, "ap": 36, "ofc": 0, "exs": 83724, "prc": 5979921, "isn": false, "iposl": false, "dt": "2026-03-28T02:07:01Z", "pim": "content/file/fe5ccc7927254a46ab71aeed829805e4.png"}
- Pfad: market[8] | Spieler: Finn Dahmen | Spieler-ID: 2195 | Marktwert: 11260605.0 | Ablauf: 2026-03-29T06:59:58Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2195", "fn": "Finn", "n": "Dahmen", "tid": "13", "pos": 1, "st": 0, "mvt": 1, "mv": 11260605, "p": 2403, "ap": 89, "ofc": 0, "exs": 53660, "prc": 11260605, "isn": false, "iposl": false, "dt": "2026-03-27T23:52:57Z", "pim": "content/file/b93977fb3dee4e75af09d67896a1666b.png"}
- Pfad: market[9] | Spieler: Frederik Rönnow | Spieler-ID: 2279 | Marktwert: 7215918.0 | Ablauf: 2026-04-27T14:10:26Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "2279", "fn": "Frederik", "n": "Rönnow", "tid": "40", "pos": 1, "st": 0, "mvt": 1, "mv": 7215918, "p": 2109, "ap": 81, "ofc": 0, "exs": 2585088, "u": {"i": "<nested>", "n": "<nested>", "uim": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 7215918, "isn": true, "iposl": false, "dt": "2026-03-28T14:10:25Z", "pim": "content/file/98159e30baca4a1080128a7a4c32914e.png"}

## AI Full Output

Absolut! Hier ist deine Kickbase-Abendstrategie für heute, Samstag, den 28. März 2026.

Ich werde jetzt die neuesten Informationen prüfen, um die kritischsten Kauf- und Verkaufsentscheidungen abzusichern.

Hallo Luca, hier ist dein strategischer Plan für den Abend.

### 1. TEAMSTATUS
Du bist mit 2,6 Mio. € im Minus, aber wir befinden uns in einer Länderspielpause (`extended_break`), was uns 8 Tage bis zum nächsten Spieltag verschafft. Das ist ein großer Vorteil. Deine Kadergröße von 13/17 Spielern gibt uns Flexibilität. **Unser dringendster Handlungsbedarf ist es, sofort wieder liquide zu werden.** Ohne Verkäufe können wir nicht agieren. Die hohe Marktknappheit bedeutet, dass wir unsere Kernspieler schützen, aber gleichzeitig Kapital freisetzen müssen, das aktuell nicht für dich arbeitet.

### 2. VERKAUFS-BEFEHLE
Um dein Budgetproblem sofort zu lösen und massiv Kapital für Trades freizuschaufeln, ist ein größerer Verkauf unumgänglich.

*   **Verkaufe Ermedin Demirović (20,6 Mio. €):** Er ist ein Top-Spieler, aber sein Marktwertpotenzial ist laut Modell mit +14k quasi bei Null. Das Kapital ist hier "tot" und kann an anderer Stelle viel effektiver für dich arbeiten. Zudem hast du bereits drei Stuttgarter im Kader und erreichst damit das Club-Limit. Dieser Verkauf löst alle Budgetprobleme auf einen Schlag.
*   **Alternative: Verkaufe Robert Andrich (18,9 Mio. €):** Ähnliches Prinzip wie bei Demirović. Sein Marktwert stagniert (+18k). Ein Verkauf würde ebenfalls das nötige Kapital freisetzen. Ich bevorzuge den Verkauf von Demirović, um das Stuttgart-Cluster aufzulösen.

**Entscheidung:** Setze Demirović heute Abend für seinen Marktwert auf den Transfermarkt. Das verschafft uns über 20 Mio. € operatives Budget.

### 3. SOFORT-KAEUFE BIS ZUM NAECHSTEN UPDATE
Die Spieler aus Marktsegment A, die kurzfristig auslaufen, sind durchweg unattraktiv. Klostermann hat kaum Potenzial, die anderen (Günter, Özkaçar, Sands) haben sogar eine negative Marktwertprognose. Hier zu bieten, wäre bei der aktuell hohen Konkurrenz Geldverschwendung.

*   **Keine Gebote auf Spieler aus Marktsegment A.**

### 4. SPAETERE CHANCEN UND HOLDS
Sobald der Verkauf von Demirović durch ist, haben wir das Kapital, um in Spieler mit echtem kurz- bis mittelfristigem Potenzial zu investieren. Hier sind deine Hauptziele für die nächsten Tage:

*   **Beobachte Maycon Douglas Cardozo (Bayern, 1,56 Mio. €):** **Zielstrategie [2-4 Tage]**. Mit einer prognostizierten Steigerung von +160k (ca. 10%) ist er ein exzellenter Trading-Kandidat. Sobald dein Konto im Plus ist, wäre ein Gebot bis ca. **1,65 Mio. €** sinnvoll, um ihn für ein paar Tage zu halten und den Marktwertanstieg mitzunehmen.
*   **Beobachte Hennes Behrens (Heidenheim, 2,18 Mio. €):** **Zielstrategie [2-4 Tage]**. Auch hier wird ein starker Anstieg von +161k (ca. 7%) erwartet. Er ist eine gute Alternative oder Ergänzung zu Cardozo. Ein Gebot bis **2,27 Mio. €** wäre hier vertretbar.
*   **Beobachte Assan Ouédraogo (Leipzig, 9,17 Mio. €):** **Zielstrategie [Spieltag-Hold]**. Er ist teurer, aber mit einer Prognose von +320k auch ein starker Kandidat für einen längeren Hold über die Länderspielpause. Wenn nach den günstigeren Trades noch Budget da ist, ist er eine Überlegung wert.

### 5. NEWS-CHECK
Die Recherche hat keine alarmierenden, spielverändernden Nachrichten für unsere Schlüsselspieler ergeben.

*   **Ermedin Demirović:** Seine letzte größere Verletzungspause war im Oktober 2025 und er ist seit Januar wieder voll im Einsatz. Es gibt keine aktuellen Fitnessprobleme, die den Verkauf beeinflussen.
*   **Robert Andrich:** Es gibt keine neuen Berichte über Verletzungen oder Unzufriedenheit. Er war im Oktober 2025 zuletzt Nationalspieler und scheint fit zu sein.
*   **Manuel Neuer:** Es gab Anfang März Berichte über einen Muskelfaserriss, und es scheint eine generelle Torwart-Thematik bei Bayern zu geben. Seine Situation ist zu beobachten, aber ein Verkauf ist aktuell nicht zwingend, da er als "rotation_hold" klassifiziert ist und wir noch einen Torwart benötigen.
*   **Serge Gnabry & Josha Vagnoman:** Für beide Spieler gibt es keine aktuellen negativen Meldungen. Gnabry scheint voll im Training zu sein.

Die Nachrichtenlage bestätigt unsere Strategie: Ein Verkauf von Demirović oder Andrich ist rein aus Performance-Gründen des Portfolios sinnvoll und wird nicht durch externe Negativ-Faktoren erzwungen.

### 6. TRADING-PLAN
Unsere Strategie für die Länderspielpause ist klar und baut aufeinander auf:
1.  **Liquidität schaffen (Heute):** Verkauf von Ermedin Demirović, um von -2,6 Mio. € auf ca. +18 Mio. € zu kommen.
2.  **Re-Investieren (Morgen/Übermorgen):** Gezielt auf 1-2 Spieler mit hoher prozentualer Marktwertprognose bieten (z.B. Cardozo, Behrens), um das neue Kapital sofort arbeiten zu lassen.
3.  **Wachstum mitnehmen (Nächste 2-4 Tage):** Diese "Trading-Assets" halten, bis sich ihr Marktwertgewinn realisiert hat, und sie dann wieder verkaufen, um den Gewinn zu sichern.
4.  **Kader optimieren (Ende der Woche):** Mit den erzielten Gewinnen den Kader auf den 17 Plätzen weiter stärken und für den Spieltag bereit machen. Deine Core-Spieler wie Gnabry, Friedl und Kaminski bleiben unangetastet.

### 7. FRIDAY-CHECK
Da wir uns in einer Länderspielpause befinden, ist der "Friday-Check" für diesen Freitag entspannt. Das primäre Ziel bis zum nächsten Freitag (03. April) ist:

*   **Kontostand deutlich positiv:** Der Verkauf von Demirović erledigt das quasi von selbst.
*   **Funktionierendes Team:** Du musst am nächsten Freitag noch kein perfektes Team haben. Wichtiger ist, dass wir das Kapital über die Woche vermehrt haben. Wir werden sicherstellen, dass du bis zum Spieltagsbeginn am 05. April eine vollständige und schlagkräftige Elf aufstellen kannst. Der Fokus liegt jetzt auf Trading und Wertsteigerung.
