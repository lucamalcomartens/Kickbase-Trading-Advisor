# Last Run Summary

- Report Date: 27. March 2026
- Generated At: 2026-03-27T22:00:13.967245Z
- User: Luca Malco
- Own Budget: -2707028.0
- Market Players: 21
- Squad Players: 12
- Fixture Context Active: True
- AI Status: success
- Mail Status: success
- Offer Tracking Active: 0
- Offer Tracking Outbid: 0
- Offer Tracking Won: 0

## Model Metrics

- Signs Correct: 67.53
- RMSE: 42424.09
- MAE: 21251.07
- R2: 0.9177

## Matchday Context

- Next Matchday: 28
- Next Matchday Date: 05-04-2026 17:30
- Days Until Next Matchday: 9
- Trading Window Mode: extended_break
- Friday Safety Mode: inactive

## Own Budget Context

- Budget: -2707028.0
- Current Cash: -2707028.0
- Spendable Without Debt: 0.0
- Temporary Negative Buffer: 49351379.17
- Theoretical Max Spend: 49351379.17
- Max Negative: -52058407.17
- Friday Recovery Need At Floor: 52058407.17

## Management Summary

- Aktive Gebotssumme: 0.0
- Effektives Cash nach aktiven Geboten: -2707028.0
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

- GK | Im Kader: 1 | Minimum: 1 | Marktoptionen: 1 | Bedarf: medium | Hinweis: Nur ein Torwart im Kader, Ersatzoptionen nicht zu spaet angehen.

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
      User     Budget  Team Value  Current Cash  Max Negative  Available Budget  Spendable Without Debt  Temporary Negative Buffer  Friday Recovery Need At Floor
      joel 98.564.622 233.695.018    98.564.622  -109.645.681       208.210.303              98.564.622                109.645.681                    109.645.681
       Rob 96.651.659 175.792.662    96.651.659   -89.906.626       186.558.285              96.651.659                 89.906.626                     89.906.626
 FlippiXxp 54.758.542 321.053.721    54.758.542  -124.018.047       178.776.589              54.758.542                124.018.047                    124.018.047
       Jan 65.360.846 200.737.034    65.360.846   -87.812.300       153.173.146              65.360.846                 87.812.300                     87.812.300
     Jonas 70.956.552 163.001.731    70.956.552   -77.206.233       148.162.785              70.956.552                 77.206.233                     77.206.233
      Till 29.252.158 284.079.777    29.252.158  -103.399.539       132.651.697              29.252.158                103.399.539                    103.399.539
     David 31.229.823 254.912.119    31.229.823   -94.426.841       125.656.664              31.229.823                 94.426.841                     94.426.841
Luca Malco -2.707.028 160.459.777    -2.707.028   -52.058.407        49.351.379                       0                 49.351.379                     52.058.407
```

## Top Market Candidates

- Chrislain Matsima | Team: Augsburg | Score: 71.4 | Rolle: short_term_trade | Delta: 196051.67 | Max: 1080707.0 | Competitive Max: 1080707.0 | Wettbewerb: high | Gegner: Hamburger SV | Fixture: good
- Maycon Douglas Cardozo | Team: Bayern | Score: 63.8 | Rolle: short_term_trade | Delta: 160302.53 | Max: 1638608.0 | Competitive Max: 1638608.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Loïc Badé | Team: Leverkusen | Score: 62.3 | Rolle: short_term_trade | Delta: 240252.98 | Max: 5645385.0 | Competitive Max: 5645385.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Gregor Kobel | Team: Dortmund | Score: 55.0 | Rolle: medium_term_hold | Delta: -1894.12 | Max: 18436171.0 | Competitive Max: 18436171.0 | Wettbewerb: low | Gegner: None | Fixture: None
- Assan Ouédraogo | Team: Leipzig | Score: 54.3 | Rolle: medium_term_hold | Delta: 322173.3 | Max: 9288882.0 | Competitive Max: 9288882.0 | Wettbewerb: high | Gegner: None | Fixture: None

## Market Snapshot

```text
    first_name   last_name  team_name         mv  predicted_mv_change  priority_score recommended_bid_max  competitive_bid_max recent_bid_competition             bid_strategy_note position_label roster_need_level  team_missing_count  team_questionable_count team_availability_level  team_availability_priority_adjustment active_offer_decision active_offer_recommended_new_bid  hours_to_exp
     Chrislain     Matsima   Augsburg  1.004.784              196.052              71           1.080.707            1.080.707                   high               avoid_price_war            DEF              none                   0                        0                  stable                                      0                     -                                -             3
Maycon Douglas     Cardozo     Bayern  1.561.663              160.303              64           1.638.608            1.638.608                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -            29
          Loïc        Badé Leverkusen  5.530.064              240.253              62           5.645.385            5.645.385                   high aggressive_only_if_priority_a            DEF              none                   0                        0                  stable                                      0                     -                                -            12
        Gregor       Kobel   Dortmund 18.436.171               -1.894              55          18.436.171           18.436.171                    low                model_range_ok             GK            medium                   0                        0                  stable                                      0                     -                                -           713
         Assan   Ouédraogo    Leipzig  9.172.900              322.173              54           9.288.882            9.288.882                   high aggressive_only_if_priority_a            MID              none                   0                        0                  stable                                      0                     -                                -            31
        Justin     Njinmah     Bremen  5.709.600              208.582              54           5.784.690            5.784.690                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -           713
    Maximilian   Eggestein   Freiburg 15.877.233               20.621              52          15.884.657           15.884.657                   high aggressive_only_if_priority_a            MID              none                   0                        0                  stable                                      0                     -                                -            16
      Leonardo Bittencourt     Bremen  3.335.280                4.144              48           3.336.772            3.336.772                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -           713
        Arnaud  Kalimuendo  Frankfurt 19.011.181               23.895              41          19.019.783           19.019.783                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -           713
         Farès      Chaïbi  Frankfurt 13.457.581               -6.435              41          13.457.581           13.457.581                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -           713
       Michael Gregoritsch   Augsburg  3.526.940             -106.608              38           3.526.940            3.526.940                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -            11
       Jackson      Irvine  St. Pauli  4.935.699             -114.124              36           4.935.699            4.935.699                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -            24
           Tom       Krauß       Köln  3.139.991             -127.826              36           3.139.991            3.139.991                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -             9
        Niklas       Stark     Bremen  2.708.769             -114.607              33           2.708.769            2.708.769                   high               avoid_price_war            DEF              none                   0                        0                  stable                                      0                     -                                -            25
         Jamie    Leweling  Stuttgart 27.209.643             -345.854              31          27.209.643           27.209.643                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -           595
```

## Top Sell Candidates

- Manuel Neuer | Team: Bayern | Sell Score: 21.6 | Rolle: rotation_hold | Delta: 261217.78 | Gegner: None | Fixture: None
- Josha Vagnoman | Team: Stuttgart | Sell Score: 18.9 | Rolle: rotation_hold | Delta: 193155.39 | Gegner: None | Fixture: None
- Ermedin Demirović | Team: Stuttgart | Sell Score: 17.9 | Rolle: rotation_hold | Delta: 15004.15 | Gegner: None | Fixture: None
- Dimitris Giannoulis | Team: Augsburg | Sell Score: 17.1 | Rolle: rotation_hold | Delta: 25848.72 | Gegner: Hamburger SV | Fixture: good
- Marvin Pieringer | Team: Heidenheim | Sell Score: 17.1 | Rolle: rotation_hold | Delta: 190579.78 | Gegner: Borussia Mönchengladbach | Fixture: good

## Squad Snapshot

```text
first_name  last_name  team_name         mv  predicted_mv_change  sell_priority_score    squad_role     squad_strategy_note  team_missing_count  team_questionable_count team_availability_level  team_availability_sell_adjustment s_11_prob            next_opponent
    Manuel      Neuer     Bayern  6.556.759              261.218                   22 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Josha   Vagnoman  Stuttgart  5.380.852              193.155                   19 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
   Ermedin  Demirović  Stuttgart 20.603.593               15.004                   18 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
  Dimitris Giannoulis   Augsburg  6.343.938               25.849                   17 rotation_hold              model_only                   0                        0                  stable                                  0         -             Hamburger SV
    Marvin  Pieringer Heidenheim  1.939.238              190.580                   17 rotation_hold              model_only                   0                        0                  stable                                  0         - Borussia Mönchengladbach
    Robert    Andrich Leverkusen 18.909.198               18.048                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
 Christian    Eriksen  Wolfsburg 10.649.466              102.633                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
    Kaishu       Sano      Mainz 11.670.896              103.418                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -      TSG 1899 Hoffenheim
      Finn    Jeltsch  Stuttgart 10.707.219               86.406                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Marco     Friedl     Bremen 17.445.350               17.062                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -                        -
     Serge     Gnabry     Bayern 29.997.993               77.407                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -                        -
     Jakub   Kaminski       Köln 19.755.275               93.831                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -      Eintracht Frankfurt
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
- Item Count: 26
- Pfad: market[0] | Spieler: Niklas Stark | Spieler-ID: 157 | Marktwert: 2708769.0 | Ablauf: 2026-03-28T22:38:30Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "157", "fn": "Niklas", "n": "Stark", "tid": "10", "pos": 2, "st": 2, "mvt": 2, "mv": 2708769, "p": 410, "ap": 34, "ofc": 0, "exs": 88734, "prc": 2708769, "isn": true, "iposl": false, "dt": "2026-03-27T20:38:29Z", "pim": "content/file/1a88a39549924d048294f618079e8437.png"}
- Pfad: market[1] | Spieler: Michael Gregoritsch | Spieler-ID: 493 | Marktwert: 3526940.0 | Ablauf: 2026-03-28T09:21:11Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "493", "fn": "Michael", "n": "Gregoritsch", "tid": "13", "pos": 4, "st": 0, "mvt": 2, "mv": 3526940, "p": 604, "ap": 55, "ofc": 0, "exs": 40895, "prc": 3526940, "isn": false, "iposl": false, "dt": "2026-03-27T00:03:10Z", "pim": "content/file/b93977fb3dee4e75af09d67896a1666b.png"}
- Pfad: market[2] | Spieler: Leonardo Bittencourt | Spieler-ID: 624 | Marktwert: 3335280.0 | Ablauf: 2026-04-26T14:40:42Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "624", "fn": "Leonardo", "n": "Bittencourt", "tid": "10", "pos": 3, "st": 0, "mvt": 1, "mv": 3335280, "p": 432, "ap": 33, "ofc": 0, "exs": 2565666, "u": {"i": "<nested>", "n": "<nested>", "uim": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 3265721, "isn": true, "iposl": false, "dt": "2026-03-27T14:40:41Z", "pim": "content/file/1a88a39549924d048294f618079e8437.png"}
- Pfad: market[3] | Spieler: Lukas Klostermann | Spieler-ID: 1333 | Marktwert: 500000.0 | Ablauf: 2026-03-28T19:27:36Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1333", "fn": "Lukas", "n": "Klostermann", "tid": "43", "pos": 2, "st": 0, "mvt": 0, "mv": 500000, "p": 53, "ap": 13, "ofc": 0, "exs": 77280, "prc": 500000, "isn": false, "iposl": false, "dt": "2026-03-27T06:27:35Z", "pim": "content/file/fe5ccc7927254a46ab71aeed829805e4.png"}
- Pfad: market[4] | Spieler: Maximilian Eggestein | Spieler-ID: 1645 | Marktwert: 15877233.0 | Ablauf: 2026-03-28T14:06:45Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1645", "fn": "Maximilian", "n": "Eggestein", "tid": "5", "pos": 3, "st": 0, "mvt": 1, "mv": 15877233, "p": 2361, "ap": 87, "ofc": 0, "exs": 58029, "prc": 15877233, "isn": false, "iposl": false, "dt": "2026-03-27T03:13:44Z", "pim": "content/file/7d6a4935195d414a9119e81aa398222a.png"}
- Pfad: market[5] | Spieler: Gregor Kobel | Spieler-ID: 1873 | Marktwert: 18436171.0 | Ablauf: 2026-04-26T14:39:10Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "1873", "fn": "Gregor", "n": "Kobel", "tid": "3", "pos": 1, "st": 0, "mvt": 1, "mv": 18436171, "p": 2799, "ap": 104, "ofc": 0, "exs": 2565574, "u": {"i": "<nested>", "n": "<nested>", "uim": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 18424542, "isn": true, "iposl": false, "dt": "2026-03-27T14:39:09Z", "pim": "content/file/ed209b2ca67c4784a658521f80baa795.png"}
- Pfad: market[6] | Spieler: Tom Krauß | Spieler-ID: 2358 | Marktwert: 3139991.0 | Ablauf: 2026-03-28T07:27:10Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2358", "fn": "Tom", "n": "Krauß", "tid": "28", "pos": 3, "st": 2, "mvt": 2, "mv": 3139991, "p": 1232, "ap": 56, "ofc": 0, "exs": 34054, "prc": 3139991, "isn": true, "iposl": false, "dt": "2026-03-27T11:55:09Z", "pim": "content/file/f8ad86d8da474048b6156cfd32f2751a.png"}
- Pfad: market[7] | Spieler: Christian Conteh | Spieler-ID: 2598 | Marktwert: 500000.0 | Ablauf: 2026-03-28T07:34:29Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2598", "fn": "Christian", "n": "Conteh", "tid": "50", "pos": 4, "st": 0, "mvt": 0, "mv": 500000, "p": 137, "ap": 27, "ofc": 0, "exs": 34493, "prc": 500000, "isn": false, "iposl": false, "dt": "2026-03-26T14:01:28Z", "pim": "content/file/ef0f480acb2e4002811381446d78ae87.png"}
- Pfad: market[8] | Spieler: Silas | Spieler-ID: 2822 | Marktwert: 1391714.0 | Ablauf: 2026-03-29T09:07:57Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2822", "fn": "", "n": "Silas", "tid": "18", "pos": 3, "st": 1, "mvt": 2, "mv": 1391714, "p": 241, "ap": 30, "ofc": 0, "exs": 126501, "prc": 1391714, "isn": true, "iposl": false, "dt": "2026-03-27T19:32:56Z", "pim": "content/file/0563ba9a260a4fd0a9c193dc525529b3.png"}
- Pfad: market[9] | Spieler: Jamie Leweling | Spieler-ID: 2988 | Marktwert: 27209643.0 | Ablauf: 2026-04-21T16:34:31Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "2988", "fn": "Jamie", "n": "Leweling", "tid": "9", "pos": 3, "st": 2, "mvt": 2, "mv": 27209643, "p": 2713, "ap": 109, "ofc": 0, "exs": 2140495, "u": {"i": "<nested>", "n": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 27220137, "isn": false, "iposl": false, "dt": "2026-03-22T16:34:30Z", "pim": "content/file/2dea6714f704489fa0fb302accce4e8a.png"}

## AI Full Output

Hallo Luca Malco, hier ist deine Kickbase-Abendstrategie.

Wir befinden uns in einer Länderspielpause. Das ist eine hervorragende Gelegenheit, um ohne den Druck des bevorstehenden Spieltags grundlegende Anpassungen vorzunehmen und von den Marktwertschwankungen der nächsten 9 Tage zu profitieren.

### 1. TEAMSTATUS
Dein Budget ist mit **-2.707.028 Euro** stark im Minus, was unsere oberste Priorität ist. Da wir uns aber in einem `extended_break` befinden, ist der `FRIDAY_SAFETY_MODE` inaktiv. Das bedeutet, wir müssen nicht panisch heute Abend auf Null kommen, sondern können die kommenden 9 Tage strategisch nutzen. Dein Kader ist mit 12 von 17 Spielern nicht voll und hat mit der Torwartposition eine mittlere Priorität für eine Ergänzung. Die Marktknappheit für gute Spieler ist hoch, daher werden wir unsere Core-Spieler mit Bedacht behandeln.

### 2. VERKAUFS-BEFEHLE
Um das negative Budget auszugleichen und Kapital für neue Trades zu schaffen, ist ein Verkauf unumgänglich.

*   **Verkaufe Ermedin Demirović (20.603.593 €):** Dieser Verkauf ist der strategisch sinnvollste Hebel. Demirović bindet über 20 Mio. Kapital, hat aber laut Modell nur eine minimale Marktwertsteigerung von ca. 15.000 € vor sich. Das Kapital ist in ihm aktuell nicht effizient eingesetzt. Ein Verkauf würde unser Budget sofort in einen komfortablen positiven Bereich von ca. 17,9 Mio. Euro katapultieren und uns extrem handlungsfähig für die gesamte Länderspielpause machen.

### 3. SOFORT-KÄUFE BIS ZUM NÄCHSTEN UPDATE
Da heute keine Spieler vor dem nächsten Marktwertupdate auslaufen (Marktsegment A ist leer), gibt es keinen akuten Zeitdruck. Wir können uns auf die vielversprechendsten Kandidaten der nächsten Stunden konzentrieren.

*   **Kauf Chrislain Matsima | Priorität A | Max Gebot 1.080.707 € | Rolle: Trader | Warum jetzt:** Matsima ist die Top-Gelegenheit für einen kurzfristigen Gewinn. Bei einem Marktwert von nur 1 Mio. € wird ihm ein Anstieg von fast 200.000 € (+20%) prognostiziert. Das ist eine herausragende prozentuale Rendite. Da er in nur 3 Stunden ausläuft, müssen wir hier sofort handeln. Die Strategie ist ein klarer **Overnight-Flip**. Wir gehen bis zum `competitive_bid_max` mit, vermeiden aber einen teuren Bieterkrieg, wie es die `bid_strategy_note` empfiehlt.

### 4. SPÄTERE CHANCEN UND HOLDS
Mit dem durch den Demirović-Verkauf generierten Budget können wir die Länderspielpause optimal nutzen.

*   **Beobachte Assan Ouédraogo | Zielstrategie: 2-4 Tage Hold | Späteres Max Gebot: ca. 9.288.882 € | Warum relevant:** Ouédraogo ist der interessanteste Kandidat für einen mehrtägigen Hold. Er hat mit +322.173 € die höchste prognostizierte absolute Marktwertsteigerung auf dem Markt. Ihn während der Pause zu halten, verspricht einen soliden und stetigen Gewinn.
*   **Beobachte Gregor Kobel | Zielstrategie: Spieltag | Späteres Max Gebot: Marktwert | Warum relevant:** Kobel würde unseren mittelfristigen Bedarf auf der Torwartposition decken. Aktuell ist er mit über 18 Mio. € zu teuer, um unser frisch gewonnenes Budget direkt zu binden. Wir setzen ihn auf die Watchlist und schlagen zu, sobald unser Budget weiter stabilisiert ist und sich eine gute Kaufgelegenheit ergibt.

### 5. NEWS-CHECK
Die Recherche hat eine sehr wichtige Information zu unserem Transferziel Assan Ouédraogo ergeben: Er hat sich im Januar eine Sehnenverletzung zugezogen und sein Ausfall wurde bis **Ende März** prognostiziert. Wir befinden uns jetzt genau in diesem Zeitfenster. Das macht ihn zu einem spekulativen Kauf. Sein Marktwert könnte bei einer baldigen Rückkehr ins Training explodieren, aber es besteht auch das Risiko einer Verzögerung.

Für die anderen überprüften Spieler (Demirović, Gnabry, Matsima, Andrich) gibt es keine aktuellen, besorgniserregenden Nachrichten über Verletzungen oder Ausfälle. Serge Gnabry scheint nach früheren Verletzungsproblemen wieder fit und ein wichtiger Faktor bei Bayern zu sein.

### 6. TRADING-PLAN
Unsere Strategie für die nächsten Tage ist klar und profitiert von der Länderspielpause:

1.  **Heute Abend (Liquidität schaffen & erster Trade):** Verkauf von Demirović, um ein Budget von ca. 17,9 Mio. € zu schaffen. Gleichzeitig Kauf von Chrislain Matsima als kurzfristigen "Overnight-Flip", um einen schnellen Gewinn mitzunehmen.
2.  **Nächste 2-4 Tage (Kapital einsetzen):** Nach dem Verkauf von Matsima werden wir über rund 19 Mio. € verfügen. Die Hälfte dieses Kapitals können wir nun in 2-3 Spieler mit hohem Marktwertpotenzial über mehrere Tage investieren. Assan Ouédraogo bleibt trotz des Verletzungsrisikos ein Top-Kandidat, da eine positive Nachricht über seinen Trainings-Einstieg seinen Wert massiv steigern würde. Wir werden seinen Status täglich prüfen. Parallel halten wir Ausschau nach weiteren Spielern mit einem `delta_percent` von >3% pro Tag.
3.  **Ende der Pause (Kader finalisieren):** In den letzten Tagen vor dem Spieltag nutzen wir die restlichen Gewinne und das Budget, um die letzte Kaderlücke (Ersatztorwart) zu schließen und das Team spieltagsbereit aufzustellen.

### 7. FRIDAY-CHECK
Für den heutigen Freitag (27. März) gibt es **keinen Handlungsbedarf**, das Konto auf Null zu stellen. Der `TRADING_WINDOW_MODE` steht auf `extended_break`. Unser einziges Ziel ist es, bis zum nächsten Spieltag am 05. April ein schlagkräftiges, voll besetztes Team und ein positives Budget zu haben. Die heute eingeleiteten Schritte sind die Grundlage dafür.
