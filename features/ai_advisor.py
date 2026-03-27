from __future__ import annotations

import datetime
import os
import time
from zoneinfo import ZoneInfo

from google import genai
from google.genai import types

from features.analysis_support import format_currency, format_history_for_prompt, format_prompt_table


RETRYABLE_AI_ERROR_MARKERS = [
    "503",
    "UNAVAILABLE",
    "high demand",
    "try again later",
]


def generate_ai_advice(
    manager_budgets_df,
    market_all_df,
    squad_recommendations_df,
    own_username,
    own_budget,
    report_date,
    matchday_context,
    analysis_history,
    fixture_context_active,
    max_retries=3,
):
    """Build the evening-strategy prompt and execute the single Gemini analysis call."""

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    own_budget_row = manager_budgets_df[manager_budgets_df["User"] == own_username]
    own_available_budget = own_budget_row["Available Budget"].iloc[0] if not own_budget_row.empty else None
    squad_team_counts = squad_recommendations_df["team_name"].value_counts()
    squad_team_counts_text = squad_team_counts[squad_team_counts > 1].to_string() if not squad_team_counts.empty else "Keine auffaelligen Doppelungen"

    market_expiring_now_df = market_all_df[market_all_df["expiring_today"]].sort_values(
        ["priority_score", "delta_prediction", "hours_to_exp"],
        ascending=[False, False, True],
    )
    market_later_df = market_all_df[~market_all_df["expiring_today"]].sort_values(
        ["priority_score", "delta_prediction", "hours_to_exp"],
        ascending=[False, False, True],
    )
    market_trade_stash_df = market_all_df[
        (market_all_df["delta_prediction"] > 0) & (market_all_df["mv_change_yesterday"] <= 0)
    ].sort_values(["delta_prediction", "hours_to_exp"], ascending=[False, True])
    market_hold_df = market_all_df[
        (market_all_df["delta_prediction"] > 0)
        & (market_all_df["asset_role"].isin(["medium_term_hold", "core_starter"]))
    ].sort_values(["priority_score", "delta_prediction", "hours_to_exp"], ascending=[False, False, True])
    squad_risk_df = squad_recommendations_df.sort_values(["delta_prediction", "mv_change_yesterday"], ascending=[True, True])

    core_starter_count = int((squad_recommendations_df["squad_role"] == "core_starter").sum())
    rotation_hold_count = int((squad_recommendations_df["squad_role"] == "rotation_hold").sum())
    sell_candidate_count = int((squad_recommendations_df["squad_role"] == "sell_candidate").sum())

    squad_text = format_prompt_table(
        squad_recommendations_df,
        ["first_name", "last_name", "position", "team_name", "mv", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "s_11_prob", "football_signal_score", "sell_priority_score", "squad_role", "next_opponent", "home_or_away", "fixture_difficulty"],
        limit=18,
    )
    expiring_now_text = format_prompt_table(
        market_expiring_now_df,
        ["first_name", "last_name", "position", "team_name", "mv", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "priority_score", "football_signal_score", "asset_role", "buy_action", "recommended_bid_min", "recommended_bid_max", "hours_to_exp", "next_opponent", "home_or_away", "fixture_difficulty"],
        limit=18,
    )
    later_market_text = format_prompt_table(
        market_later_df,
        ["first_name", "last_name", "position", "team_name", "mv", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "priority_score", "football_signal_score", "asset_role", "buy_action", "recommended_bid_min", "recommended_bid_max", "hours_to_exp", "next_opponent", "home_or_away", "fixture_difficulty"],
        limit=18,
    )
    trade_stash_text = format_prompt_table(
        market_trade_stash_df,
        ["first_name", "last_name", "position", "team_name", "mv", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "priority_score", "asset_role", "recommended_bid_max", "hours_to_exp", "next_opponent", "home_or_away", "fixture_difficulty"],
        limit=12,
    )
    hold_candidates_text = format_prompt_table(
        market_hold_df,
        ["first_name", "last_name", "position", "team_name", "mv", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "priority_score", "football_signal_score", "asset_role", "recommended_bid_min", "recommended_bid_max", "hours_to_exp", "next_opponent", "home_or_away", "fixture_difficulty"],
        limit=12,
    )
    squad_risk_text = format_prompt_table(
        squad_risk_df,
        ["first_name", "last_name", "position", "team_name", "mv", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "s_11_prob", "football_signal_score", "sell_priority_score", "squad_action"],
        limit=12,
    )
    available_budget_text = format_currency(own_available_budget) if own_available_budget is not None else "n/a"
    own_budget_text = format_currency(own_budget)
    previous_analysis_text = format_history_for_prompt(analysis_history)

    prompt = f"""
Du bist mein Kickbase Portfoliomanager fuer die 1. Bundesliga. Deine Aufgabe ist es, kurzfristige Marktwertgewinne bis zum naechsten Marktwertupdate mitzunehmen, ohne dabei die langfristige Trading-Strategie und die Kaderentwicklung aus den Augen zu verlieren.

<rules>

1. KADERBEGRENZUNG: Absolutes Limit von 17 Spielern.
2. CLUB-LIMIT: Maximal 3 Spieler pro Verein.
3. NO UNDERPAY: Gebote immer >= Marktwert.
4. BUDGET: Freitagabend muss der Kontostand >= 0 Euro sein, ausser in der Laenderspielpause.
5. ZEITFAKTOR: Spieler mit Ablauf vor dem naechsten Marktwertupdate haben hohe operative Prioritaet. Das ist aber nur ein Faktor und kein Automatismus.
6. LANGFRISTIGES TRADING: Beruecksichtige aktiv, ob ein Spieler ueber 2 bis 4 Tage oder bis zum naechsten Spieltag den besseren Gesamtertrag bringen kann als ein sofortiger Flip.
7. SPIELTAGS-READINESS: Wenn kein verlaengertes Tradingfenster vorliegt, muss bis Freitag vor dem Spieltag ein funktionierendes Team stehen und der Kontostand spaetestens dann >= 0 Euro sein.

</rules>

<grounding_instruction>

Nutze die Google Suche gezielt nur fuer die wichtigsten Entscheidungen.
- Pruefe die 5 wichtigsten Sofort-Kaufkandidaten, die vor dem naechsten Marktwertupdate auslaufen.
- Pruefe die 5 kritischsten Verkaufs- oder Halt-Entscheidungen in meinem Kader.
- Suche nur nach belastbaren Echtzeit-Infos wie Verletzungen, Trainingsstatus, Sperren, Rotationen oder Stammplatzverlust.
- Wenn du keine belastbare neue Information findest, sage das explizit und spekuliere nicht.

</grounding_instruction>

<current_data_context>

VORHERIGE ANALYSE-KONTEXT-HISTORY:
{previous_analysis_text}

HEUTIGES DATUM: {report_date}
WOCHENTAG HEUTE: {datetime.datetime.now(ZoneInfo('Europe/Berlin')).strftime('%A')}
MEIN USERNAME: {own_username}
MEIN AKTUELLES BUDGET: {own_budget_text} Euro
MEIN GESCHAETZTES VERFUEGBARES BUDGET OHNE REGELVERSTOSS: {available_budget_text} Euro
AKTUELLE KADERGROESSE: {len(squad_recommendations_df)} von 17
NAECHSTER SPIELTAG: {matchday_context['next_matchday']}
NAECHSTER SPIELTAG STARTET: {matchday_context['next_matchday_date']}
TAGE BIS ZUM NAECHSTEN SPIELTAG: {matchday_context['days_until_next_matchday']}
TRADING_WINDOW_MODE: {matchday_context['trading_window_mode']}
FRIDAY_SAFETY_MODE: {matchday_context['friday_safety_mode']}
SPIELPLAN-KONTEXT: {'aktiv' if fixture_context_active else 'nicht verfuegbar'}
KADERSTRUKTUR: {core_starter_count} core_starter, {rotation_hold_count} rotation_hold, {sell_candidate_count} sell_candidate

MEHRFACHBELEGUNG PRO VEREIN IM KADER:
{squad_team_counts_text}

MEIN KADER:
{squad_text}

MARKTSEGMENT A - SPIELER, DIE VOR DEM NAECHSTEN MARKTWERTUPDATE ABLAUFEN:
{expiring_now_text}

MARKTSEGMENT B - SPIELER, DIE SPAETER ABLAUFEN:
{later_market_text}

MARKTSEGMENT C - MOEGLICHE TRADING-REBOUNDS (gestern schwach, Modell heute positiv):
{trade_stash_text}

MARKTSEGMENT D - POSITIVE HOLDS FUER 2 BIS 4 TAGE ODER BIS ZUM SPIELTAG:
{hold_candidates_text}

KADER-RISIKEN AUS MODELLSICHT:
{squad_risk_text}

HINWEIS ZU DEN SCORES:
- priority_score bewertet Dringlichkeit, Marktwertpotenzial, Trend, Startelfwahrscheinlichkeit und interne Fussballsignale.
- football_signal_score ist ein interner Struktur-Score aus Startelfwahrscheinlichkeit, Punkten, Minuten, Punkte-pro-Minute und Naehe zum naechsten Spiel.
- predicted_mv_change ist die erwartete Marktwertveraenderung bis morgen. predicted_mv_target ist der daraus abgeleitete absolute Marktwert fuer morgen.
- recommended_bid_min und recommended_bid_max sind bereits berechnete Fallback-Gebote aus Score, Ablaufzeit und erwarteter Marktwertchance.
- next_opponent, home_or_away und fixture_difficulty kommen, falls verfuegbar, aus einem externen Spielplan-Feed ohne zusaetzlichen KI-Aufruf.

</current_data_context>

<task>

Erstelle eine konkrete Abendstrategie fuer mein Kickbase-Team.

- Priorisiere zuerst Spieler aus Marktsegment A, wenn sie bis zum naechsten Marktwertupdate die beste Kombination aus Zeitfaktor, Trading-Potenzial und sportlicher Relevanz haben.
- Vernachlaessige Marktsegment B nicht. Wenn spaeter auslaufende Spieler strategisch deutlich besser sind als die Sofort-Kandidaten, sollst du das klar sagen.
- Denke wie ein Trader und wie ein Manager: kurzfristige Gewinne mitnehmen, aber nicht blind alles auf den naechsten Tag optimieren, wenn ein Halten ueber 2 bis 4 Tage oder bis zum naechsten Spieltag den besseren Gesamtertrag verspricht.
- Bewerte fuer gute Kaufkandidaten immer explizit, ob der bessere Plan ist: Overnight-Flip, 2-bis-4-Tage-Hold oder Kaderbaustein bis zum Spieltag.
- Wenn TRADING_WINDOW_MODE = extended_break, nutze die zusaetzliche Zeit aktiv. In solchen Phasen darfst du Spieler staerker nach mehrtaegigem Trading-Potenzial statt nur nach naechstem Update bewerten.
- Wenn FRIDAY_SAFETY_MODE = active, priorisiere Spieltags-Readiness: bis Freitag muss ein funktionierendes Team stehen und das Budget spaetestens dann >= 0 sein, ausser es liegt wirklich ein verlaengertes Tradingfenster ohne direkten Spieltag vor.
- Nutze die vorhandenen priority_score-, asset_role- und recommended_bid-Werte aktiv als Grundlage. Du darfst sie begruendet leicht anpassen, sollst sie aber nicht ignorieren.
- Gib fuer jeden Kaufkandidaten ein maximales Gebot in Euro an. Das Gebot soll sich an Wichtigkeit, Budget, Trading-Chance, Startelf-Wahrscheinlichkeit und Ablaufzeit orientieren.
- Unterscheide klar zwischen:
  A) Sofort kaufen vor dem naechsten Marktwertupdate
  B) Beobachten und spaeter angreifen
  C) Nicht kaufen
- Beruecksichtige auch Verkaeufe aus meinem Kader, wenn dadurch bessere Trades oder wichtigere Einkaeufe moeglich werden.
- Wenn ein Spieler vor allem als Trading-Asset interessant ist, sage das explizit.

Antwortformat (STRENG EINHALTEN):

1. TEAMSTATUS: Kurze Einordnung meines Kaders, meines Budgets, des Tradingfensters und meines dringendsten Handlungsbedarfs heute Abend.
2. VERKAUFS-BEFEHLE: Wer muss weg oder ist aktiv entbehrlich? Fokus auf fallende Werte, Risiko und Kapitalfreisetzung.
3. SOFORT-KAEUFE BIS ZUM NAECHSTEN UPDATE: Nenne nur die wichtigsten Spieler aus Marktsegment A. Format je Spieler: \"Kauf [Name] | Prioritaet [A/B/C] | Max Gebot [Euro] | Rolle [Starter/Trader/Hold] | Warum jetzt\".
4. SPAETERE CHANCEN UND HOLDS: Welche spaeter auslaufenden Spieler oder mehrtaegigen Holds darf ich nicht verpassen? Format je Spieler: \"Beobachte [Name] | Zielstrategie [Overnight/2-4 Tage/Spieltag] | Spaeteres Max Gebot | Warum relevant\".
5. NEWS-CHECK: Welche belastbaren Infos aus der Websuche veraendern die Entscheidung wirklich?
6. TRADING-PLAN: Was ist deine Strategie fuer die naechsten 2 bis 4 Tage, damit ich nicht nur heute, sondern auch langfristig besser trade?
7. FRIDAY-CHECK: Was muss bis Freitag vor dem Spieltag unbedingt erledigt sein, damit ich nicht im Minus bin und ein funktionierendes Team habe?

</task>
"""

    response = None
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearchRetrieval())]
                ),
                contents=prompt,
            )
            break
        except Exception as error:
            last_error = error
            error_text = str(error)
            is_retryable = any(marker.lower() in error_text.lower() for marker in RETRYABLE_AI_ERROR_MARKERS)

            if attempt == max_retries or not is_retryable:
                raise

            wait_seconds = attempt * 5
            print(f"KI-Analyse Versuch {attempt} fehlgeschlagen ({error_text}). Neuer Versuch in {wait_seconds} Sekunden...")
            time.sleep(wait_seconds)

    if response is None and last_error is not None:
        raise last_error

    return response.text, "success"