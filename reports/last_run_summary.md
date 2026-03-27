# Last Run Summary

- Report Date: 27. March 2026
- Generated At: 2026-03-27T14:55:49.207874Z
- User: Luca Malco
- Own Budget: 5181860.0
- Market Players: 26
- Squad Players: 13
- Fixture Context Active: True
- AI Status: success
- Mail Status: success
- Offer Tracking Active: 1
- Offer Tracking Outbid: 0
- Offer Tracking Won: 0

## Model Metrics

- Signs Correct: 67.27
- RMSE: 42881.08
- MAE: 21565.43
- R2: 0.9155

## Matchday Context

- Next Matchday: 28
- Next Matchday Date: 05-04-2026 17:30
- Days Until Next Matchday: 9
- Trading Window Mode: extended_break
- Friday Safety Mode: inactive

## Own Budget Context

- Budget: 5181860.0
- Current Cash: 5181860.0
- Spendable Without Debt: 5181860.0
- Temporary Negative Buffer: 52485229.17
- Theoretical Max Spend: 57667089.17
- Max Negative: -52485229.17
- Friday Recovery Need At Floor: 52485229.17

## Management Summary

- Aktive Gebotssumme: 8888888.0
- Effektives Cash nach aktiven Geboten: -3707028.0
- Overbid-Druck: low
- Suggested Markup: 0.0
- Outbid Count 14d: 0
- Aktive Gebote halten: 0
- Aktive Gebote leicht erhoehen: 0
- Aktive Gebote abbrechen: 1

## Squad Retention Summary

- Marktknappheit: high
- Starke Ersatzoptionen am Markt: 0
- Geschuetzte Kaderspieler: 3

## Roster Need Summary

- Primaerer Positionsbedarf: GK
- Dringlichkeit: medium
- Positionen mit Bedarf: 1

- GK | Im Kader: 0 | Minimum: 1 | Marktoptionen: 3 | Bedarf: medium | Hinweis: Torwart fehlt im Kader, verfuegbare Optionen frueh priorisieren.

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
- Fehler: API-Football /fixtures returned errors: plan: Free plans do not have access to the Next parameter.

- Keine auffaelligen Team-Ausfaelle im API-Football Kontext

## Strategy Validation

- Aktive Gebote binden mehr Kapital als aktuell als Budget ausgewiesen ist.

## Manager Budget Snapshot

```text
      User      Budget  Team Value  Current Cash  Max Negative  Available Budget  Spendable Without Debt  Temporary Negative Buffer  Friday Recovery Need At Floor
      joel 106.401.082 232.327.934   106.401.082  -111.780.575       218.181.657             106.401.082                111.780.575                    111.780.575
     David  83.049.024 235.172.073    83.049.024  -105.012.962       188.061.986              83.049.024                105.012.962                    105.012.962
 FlippiXxp  54.301.322 333.318.849    54.301.322  -127.914.656       182.215.978              54.301.322                127.914.656                    127.914.656
      Till  71.057.063 262.368.122    71.057.063  -110.030.311       181.087.374              71.057.063                110.030.311                    110.030.311
       Jan  90.925.473 174.660.025    90.925.473   -87.643.214       178.568.687              90.925.473                 87.643.214                     87.643.214
       Rob  82.325.240 189.595.857    82.325.240   -89.733.962       172.059.202              82.325.240                 89.733.962                     89.733.962
     Jonas  70.956.552 162.720.673    70.956.552   -77.113.484       148.070.036              70.956.552                 77.113.484                     77.113.484
Luca Malco   5.181.860 153.864.289     5.181.860   -52.485.229        57.667.089               5.181.860                 52.485.229                     52.485.229
```

## Top Market Candidates

- Manuel Neuer | Team: Bayern | Score: 97.1 | Rolle: short_term_trade | Delta: 276303.5 | Max: 6402493.0 | Competitive Max: 6402493.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Alexander Nübel | Team: Stuttgart | Score: 82.9 | Rolle: short_term_trade | Delta: 15748.07 | Max: 20017669.0 | Competitive Max: 20017669.0 | Wettbewerb: high | Gegner: None | Fixture: None
- Gregor Kobel | Team: Dortmund | Score: 69.3 | Rolle: medium_term_hold | Delta: 5677.24 | Max: 18426586.0 | Competitive Max: 18426586.0 | Wettbewerb: low | Gegner: None | Fixture: None
- Chrislain Matsima | Team: Augsburg | Score: 68.9 | Rolle: short_term_trade | Delta: 194360.03 | Max: 876137.0 | Competitive Max: 876137.0 | Wettbewerb: high | Gegner: Hamburger SV | Fixture: good
- Loïc Badé | Team: Leverkusen | Score: 61.4 | Rolle: short_term_trade | Delta: 282345.07 | Max: 5393044.0 | Competitive Max: 5393044.0 | Wettbewerb: high | Gegner: None | Fixture: None

## Market Snapshot

```text
first_name    last_name    team_name         mv  predicted_mv_change  priority_score recommended_bid_max  competitive_bid_max recent_bid_competition             bid_strategy_note position_label roster_need_level  team_missing_count  team_questionable_count team_availability_level  team_availability_priority_adjustment active_offer_decision active_offer_recommended_new_bid  hours_to_exp
    Manuel        Neuer       Bayern  6.269.867              276.304              97           6.402.493            6.402.493                   high               avoid_price_war             GK            medium                   0                        0                  stable                                      0                 abort                                -             4
 Alexander        Nübel    Stuttgart 20.010.110               15.748              83          20.017.669           20.017.669                   high               avoid_price_war             GK            medium                   0                        0                  stable                                      0                     -                                -             6
    Gregor        Kobel     Dortmund 18.424.542                5.677              69          18.426.586           18.426.586                    low                model_range_ok             GK            medium                   0                        0                  stable                                      0                     -                                -           720
 Chrislain      Matsima     Augsburg    813.968              194.360              69             876.137              876.137                   high               avoid_price_war            DEF              none                   0                        0                  stable                                      0                     -                                -            10
      Loïc         Badé   Leverkusen  5.257.518              282.345              61           5.393.044            5.393.044                   high aggressive_only_if_priority_a            DEF              none                   0                        0                  stable                                      0                     -                                -            19
   Danilho       Doekhi Union Berlin 18.265.637              138.928              60          18.332.322           18.332.322                   high               avoid_price_war            DEF              none                   0                        0                  stable                                      0                     -                                -             6
    Robert      Glatzel      Hamburg    500.000                  198              60             500.095              500.095                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -             2
  Valentin      Gendrey   Hoffenheim    500.000                  166              59             500.080              500.080                   high               avoid_price_war            DEF              none                   0                        0                  stable                                      0                     -                                -             2
    Justin      Njinmah       Bremen  5.478.211              238.566              55           5.592.723            5.592.723                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -           720
  Leonardo  Bittencourt       Bremen  3.265.721              110.552              53           3.305.520            3.305.520                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -           720
     Assan    Ouédraogo      Leipzig  8.838.484              323.887              52           8.955.083            8.955.083                   high aggressive_only_if_priority_a            MID              none                   0                        0                  stable                                      0                     -                                -            38
     Bilal El Khannouss    Stuttgart 25.605.094               34.192              51          25.617.403           25.617.403                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -             7
Maximilian    Eggestein     Freiburg 15.835.943               47.144              51          15.852.915           15.852.915                   high aggressive_only_if_priority_a            MID              none                   0                        0                  stable                                      0                     -                                -            23
 Christian       Conteh   Heidenheim    500.000                1.263              50             500.455              500.455                   high               avoid_price_war             ST              none                   0                        0                  stable                                      0                     -                                -            17
    Albert      Grønbæk      Hamburg    500.000                  142              48             500.051              500.051                   high               avoid_price_war            MID              none                   0                        0                  stable                                      0                     -                                -            12
```

## Top Sell Candidates

- Marius Wolf | Team: Augsburg | Sell Score: 21.6 | Rolle: rotation_hold | Delta: 140.3 | Gegner: Hamburger SV | Fixture: good
- Lucas Höler | Team: Freiburg | Sell Score: 19.0 | Rolle: rotation_hold | Delta: 3292.93 | Gegner: None | Fixture: None
- Josha Vagnoman | Team: Stuttgart | Sell Score: 18.9 | Rolle: rotation_hold | Delta: 229642.94 | Gegner: None | Fixture: None
- Ermedin Demirović | Team: Stuttgart | Sell Score: 17.9 | Rolle: rotation_hold | Delta: 11994.29 | Gegner: None | Fixture: None
- Dimitris Giannoulis | Team: Augsburg | Sell Score: 17.1 | Rolle: rotation_hold | Delta: 84047.47 | Gegner: Hamburger SV | Fixture: good

## Squad Snapshot

```text
first_name  last_name  team_name         mv  predicted_mv_change  sell_priority_score    squad_role     squad_strategy_note  team_missing_count  team_questionable_count team_availability_level  team_availability_sell_adjustment s_11_prob            next_opponent
    Marius       Wolf   Augsburg    500.000                  140                   22 rotation_hold              model_only                   0                        0                  stable                                  0         -             Hamburger SV
     Lucas      Höler   Freiburg    500.000                3.293                   19 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Josha   Vagnoman  Stuttgart  5.163.488              229.643                   19 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
   Ermedin  Demirović  Stuttgart 20.586.494               11.994                   18 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
  Dimitris Giannoulis   Augsburg  6.253.230               84.047                   17 rotation_hold              model_only                   0                        0                  stable                                  0         -             Hamburger SV
    Marvin  Pieringer Heidenheim  1.745.376              189.529                   17 rotation_hold              model_only                   0                        0                  stable                                  0         - Borussia Mönchengladbach
    Robert    Andrich Leverkusen 18.885.795                7.415                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
 Christian    Eriksen  Wolfsburg 10.543.667              101.531                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
    Kaishu       Sano      Mainz 11.565.345              110.443                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -      TSG 1899 Hoffenheim
      Finn    Jeltsch  Stuttgart 10.617.512               78.497                   16 rotation_hold              model_only                   0                        0                  stable                                  0         -                        -
     Marco     Friedl     Bremen 17.429.222               27.106                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -                        -
     Serge     Gnabry     Bayern 29.919.070               95.272                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -                        -
     Jakub   Kaminski       Köln 19.655.090              103.716                    0  core_starter keep_due_to_thin_market                   0                        0                  stable                                  0         -      Eintracht Frankfurt
```

## Active Offers

- Manuel Neuer | Gebot: 8888888.0 | Marktwert: 6269867.0 | Ablauf: 2026-03-27T18:39:38Z

## Active Offer Actions

- Manuel Neuer | Aktion: abbrechen | Aktuelles Gebot: 8888888.0 | Neues Max Gebot: None | Grund: Dein aktuelles Gebot liegt bereits klar ueber der disziplinierten Obergrenze.

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
- Item Count: 26
- Pfad: market[0] | Spieler: Manuel Neuer | Spieler-ID: 237 | Marktwert: 6269867.0 | Ablauf: 2026-03-27T18:39:38Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, ofs, p, pim, pos, prc, st, tid, uoid, uop | Sample: {"i": "237", "fn": "Manuel", "n": "Neuer", "tid": "2", "pos": 1, "st": 0, "mvt": 1, "mv": 6269867, "p": 1838, "ap": 97, "ofc": 1, "exs": 13483, "prc": 6269867, "uop": 8888888, "uoid": "2622703", "isn": false, "ofs": "<list:1>", "iposl": false, "dt": "2026-03-26T05:20:38Z", "pim": "content/file/48622993193e45f09d696908d75ed523.png"}
- Pfad: market[1] | Spieler: Michael Gregoritsch | Spieler-ID: 493 | Marktwert: 3635363.0 | Ablauf: 2026-03-28T09:21:10Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "493", "fn": "Michael", "n": "Gregoritsch", "tid": "13", "pos": 4, "st": 0, "mvt": 2, "mv": 3635363, "p": 604, "ap": 55, "ofc": 0, "exs": 66375, "prc": 3635363, "isn": false, "iposl": false, "dt": "2026-03-27T00:03:10Z", "pim": "content/file/b93977fb3dee4e75af09d67896a1666b.png"}
- Pfad: market[2] | Spieler: Leonardo Bittencourt | Spieler-ID: 624 | Marktwert: 3265721.0 | Ablauf: 2026-04-26T14:40:41Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "624", "fn": "Leonardo", "n": "Bittencourt", "tid": "10", "pos": 3, "st": 0, "mvt": 1, "mv": 3265721, "p": 432, "ap": 33, "ofc": 0, "exs": 2591146, "u": {"i": "<nested>", "n": "<nested>", "uim": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 3265721, "isn": true, "iposl": false, "dt": "2026-03-27T14:40:41Z", "pim": "content/file/1a88a39549924d048294f618079e8437.png"}
- Pfad: market[3] | Spieler: Lukas Klostermann | Spieler-ID: 1333 | Marktwert: 500000.0 | Ablauf: 2026-03-28T19:27:35Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1333", "fn": "Lukas", "n": "Klostermann", "tid": "43", "pos": 2, "st": 0, "mvt": 0, "mv": 500000, "p": 53, "ap": 13, "ofc": 0, "exs": 102760, "prc": 500000, "isn": true, "iposl": false, "dt": "2026-03-27T06:27:35Z", "pim": "content/file/fe5ccc7927254a46ab71aeed829805e4.png"}
- Pfad: market[4] | Spieler: Alexander Nübel | Spieler-ID: 1581 | Marktwert: 20010110.0 | Ablauf: 2026-03-27T20:47:59Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1581", "fn": "Alexander", "n": "Nübel", "tid": "9", "pos": 1, "st": 0, "mvt": 1, "mv": 20010110, "p": 3169, "ap": 117, "ofc": 0, "exs": 21184, "prc": 20010110, "isn": false, "iposl": false, "dt": "2026-03-26T09:42:59Z", "pim": "content/file/2dea6714f704489fa0fb302accce4e8a.png"}
- Pfad: market[5] | Spieler: Maximilian Eggestein | Spieler-ID: 1645 | Marktwert: 15835943.0 | Ablauf: 2026-03-28T14:06:44Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "1645", "fn": "Maximilian", "n": "Eggestein", "tid": "5", "pos": 3, "st": 0, "mvt": 1, "mv": 15835943, "p": 2361, "ap": 87, "ofc": 0, "exs": 83509, "prc": 15835943, "isn": true, "iposl": false, "dt": "2026-03-27T03:13:44Z", "pim": "content/file/7d6a4935195d414a9119e81aa398222a.png"}
- Pfad: market[6] | Spieler: Gregor Kobel | Spieler-ID: 1873 | Marktwert: 18424542.0 | Ablauf: 2026-04-26T14:39:09Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid, u | Sample: {"i": "1873", "fn": "Gregor", "n": "Kobel", "tid": "3", "pos": 1, "st": 0, "mvt": 1, "mv": 18424542, "p": 2799, "ap": 104, "ofc": 0, "exs": 2591054, "u": {"i": "<nested>", "n": "<nested>", "uim": "<nested>", "isvf": "<nested>", "st": "<nested>"}, "prc": 18424542, "isn": true, "iposl": false, "dt": "2026-03-27T14:39:09Z", "pim": "content/file/ed209b2ca67c4784a658521f80baa795.png"}
- Pfad: market[7] | Spieler: Tom Krauß | Spieler-ID: 2358 | Marktwert: 3271296.0 | Ablauf: 2026-03-28T07:27:09Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2358", "fn": "Tom", "n": "Krauß", "tid": "28", "pos": 3, "st": 2, "mvt": 2, "mv": 3271296, "p": 1232, "ap": 56, "ofc": 0, "exs": 59534, "prc": 3271296, "isn": true, "iposl": false, "dt": "2026-03-27T11:55:09Z", "pim": "content/file/f8ad86d8da474048b6156cfd32f2751a.png"}
- Pfad: market[8] | Spieler: Robert Glatzel | Spieler-ID: 2444 | Marktwert: 500000.0 | Ablauf: 2026-03-27T16:46:06Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2444", "fn": "Robert", "n": "Glatzel", "tid": "6", "pos": 4, "st": 2, "mvt": 0, "mv": 500000, "p": 335, "ap": 24, "ofc": 0, "exs": 6671, "prc": 500000, "isn": false, "iposl": false, "dt": "2026-03-25T23:59:06Z", "pim": "content/file/6bd6cf911d5b497e977b3e6a4526aef9.png"}
- Pfad: market[9] | Spieler: Christian Conteh | Spieler-ID: 2598 | Marktwert: 500000.0 | Ablauf: 2026-03-28T07:34:28Z | Keys: ap, dt, exs, fn, i, iposl, isn, mv, mvt, n, ofc, p, pim, pos, prc, st, tid | Sample: {"i": "2598", "fn": "Christian", "n": "Conteh", "tid": "50", "pos": 4, "st": 0, "mvt": 0, "mv": 500000, "p": 137, "ap": 27, "ofc": 0, "exs": 59973, "prc": 500000, "isn": false, "iposl": false, "dt": "2026-03-26T14:01:28Z", "pim": "content/file/ef0f480acb2e4002811381446d78ae87.png"}

## AI Full Output

Hallo Luca Malco, hier ist deine Kickbase-Abendstrategie für den 27. März 2026. Wir befinden uns in einer Länderspielpause, was uns exzellente Trading-Möglichkeiten über mehrere Tage bietet. Unser Fokus liegt heute darauf, eine massive Fehlallokation bei einem Gebot zu korrigieren und die Weichen für die nächsten Tage strategisch klug zu stellen.

### 1. TEAMSTATUS
Dein Kader ist mit 13 Spielern gut aufgestellt, aber die dringendste Baustelle ist die unbesetzte Torwartposition. Dein effektives Budget ist durch ein aktives Gebot von 8.888.888 € für Manuel Neuer bereits mit -3.707.028 € im negativen Bereich. Dieses Gebot ist ein massives Overpay und bindet Kapital, das wir dringend benötigen. Da wir uns im `extended_break`-Modus befinden, ist die Regel, bis Freitagabend im Plus zu sein, ausgesetzt. Wir haben 9 Tage bis zum nächsten Spieltag Zeit, um wieder einen positiven Kontostand zu erreichen und das Team spieltagsfit zu machen. Die Marktknappheit ist hoch, daher werden wir unsere Core-Spieler schützen.

### 2. VERKAUFS-BEFEHLE
Aktuell gibt es keinen zwingenden Verkaufsbedarf. Alle deine Spieler haben eine stabile bis positive Marktwertprognose. Insbesondere Marvin Pieringer (+11 %) und Josha Vagnoman (+4 %) solltest du als Trading-Anlagen halten. Wir werden Verkäufe nur in Betracht ziehen, wenn wir kurzfristig Kapital für einen strategisch wichtigen Kauf (insbesondere auf der Torwartposition) freisetzen müssen.

### 3. SOFORT-KÄUFE BIS ZUM NÄCHSTEN UPDATE

*   **Aktives Gebot Manuel Neuer** | **Aktion: abbrechen** | **Neues Max Gebot: 6.750.000 €** | **Warum:** Dein aktuelles Gebot von 8,89 Mio. € ist ein extremes Übergebot. Der geschätzte Marktpreis liegt bei ca. 6,7 Mio. €, dein diszipliniertes Maximum sogar nur bei 6,4 Mio. €. Die Systemlogik empfiehlt klar den Abbruch, und dem folgen wir zu 100 %.
    *   **Neue Strategie:** Nachdem du das Gebot zurückgezogen hast, biete neu, aber diszipliniert. Ein Gebot bis **6.750.000 €** entspricht dem geschätzten Marktpreis und ist vertretbar, um die Torwartlücke kurzfristig zu füllen. Dieser Kauf würde dein Cash-Budget von 5,18 Mio. € übersteigen und den Negativpuffer antasten. Der Rückholbedarf von ca. 1,6 Mio. € bis zum Spieltag kann durch die erwarteten Marktwertgewinne deines gesamten Kaders und des Neuzugangs gedeckt werden.

### 4. SPÄTERE CHANCEN UND HOLDS

*   **Beobachte Gregor Kobel** | **Zielstrategie: Spieltag** | **Späteres Max Gebot: 18.425.000 €** | **Warum relevant:** Kobel ist die strategisch bessere und langfristige Lösung für deine Torwartposition. Die Konkurrenz ist laut Daten gering, was eine Chance auf einen Kauf ohne Bieterkrieg eröffnet. Sollten wir Neuer nicht zu einem vernünftigen Preis bekommen, wird Kobel unser Primärziel. Ein Kauf würde allerdings den Verkauf eines teuren Mittelfeldspielers (z.B. Kaishu Sano oder Christian Eriksen) erfordern.

*   **Kauf Chrislain Matsima** | **Priorität B** | **Max Gebot: 875.000 €** | **Rolle: Trader** | **Warum jetzt:** Matsima ist eine exzellente Trading-Gelegenheit für die Länderspielpause. Bei einem niedrigen Marktwert von unter 1 Mio. € wird ihm ein Marktwertanstieg von +24 % prognostiziert. Dies ist ein risikoarmer Trade mit hohem prozentualem Gewinnpotenzial über die nächsten Tage. Du kannst ihn mit deinem freien Cash bezahlen, sobald das Neuer-Gebot korrigiert ist.

### 5. NEWS-CHECK
Ich habe die wichtigsten Spieler deines Kaders und potenzielle Kaufkandidaten auf neue, spielentscheidende Informationen geprüft.

*   **Manuel Neuer:** Hatte Anfang März erneut einen Muskelfaserriss in der Wade. Die Länderspielpause sollte ihm helfen, sich vollständig zu erholen, mit einem möglichen Comeback am 4. April im Visier. Das Risiko einer erneuten Verletzung bei einem 40-Jährigen ist real, aber die Berichte deuten auf eine planmäßige Rückkehr hin.
*   **Gregor Kobel:** War Anfang Januar krankheitsbedingt angeschlagen, ist aber längst wieder fit und spielt in der Form seines Lebens. Es gibt keine aktuellen Bedenken.
*   **Serge Gnabry:** Nach einer von Verletzungen geprägten Zeit scheint er wieder fit und in Form zu sein, was auch zu einer Vertragsverlängerung geführt hat. Aktuelle Bilder zeigen ihn im Training.
*   **Robert Andrich & Ermedin Demirović:** Es gibt keine neuen, besorgniserregenden Meldungen zu Verletzungen oder Sperren, die eine sofortige Reaktion erfordern würden. Demirović hatte im Oktober 2025 eine Fraktur im Fuß, ist aber seit Januar 2026 wieder zurück und trifft.

**Fazit:** Keine der gefundenen Informationen erzwingt einen Notverkauf. Das leichte Verletzungsrisiko bei Neuer bestärkt die Strategie, nicht exzessiv überzubezahlen und Kobel als Alternative im Auge zu behalten.

### 6. TRADING-PLAN
1.  **Priorität 1 (Heute Abend):** Korrigiere sofort das Gebot für Manuel Neuer. Ziehe das 8,89-Mio.-Gebot zurück und platziere ein neues, diszipliniertes Gebot um die 6,75 Mio. €.
2.  **Priorität 2 (Heute Abend):** Platziere ein Gebot für den Trading-Kandidaten Chrislain Matsima bis ca. 875.000 €.
3.  **Mittelfrist-Strategie (Nächste 2-4 Tage):** Nutze die Länderspielpause, um die Marktwerte von Neuer (falls gekauft) und Matsima zu realisieren. Beobachte parallel den Markt für Gregor Kobel. Sollte sich dort eine günstige Gelegenheit ergeben, überlegen wir, durch den Verkauf eines Mittelfeldspielers wie Sano oder Eriksen das nötige Kapital freizumachen, um unsere Torwartposition langfristig zu sichern.
4.  **Kader-Management:** Halte deine Kernspieler und die mit positiver Marktwertprognose. Wir füllen den Kaderplatz 15 und 16 mit klugen Trades (wie Matsima), um das Budget für den Spieltag weiter zu erhöhen.

### 7. FRIDAY-CHECK
Da wir uns in einer Länderspielpause befinden (`TRADING_WINDOW_MODE: extended_break`), entfällt der harte Zwang, heute Abend bei Null oder im Plus zu sein. Unser Ziel ist es, bis zum **Freitag vor dem nächsten Spieltag (03. April 2026)** ein schlagkräftiges Team mit 11 Startern aufzustellen und einen positiven Kontostand zu haben. Die geplanten Käufe werden uns vorübergehend ins Minus bringen, aber die erwarteten Marktwertsteigerungen über die 9-tägige Pause geben uns ausreichend Zeit und Potenzial, dieses Minus profitabel auszugleichen.
