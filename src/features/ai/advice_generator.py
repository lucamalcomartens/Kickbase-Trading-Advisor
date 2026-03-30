from __future__ import annotations

import datetime
import os
import time
from zoneinfo import ZoneInfo

import pandas as pd
from google import genai
from google.genai import types

from features.analysis import format_currency, format_history_for_prompt, format_prompt_table


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
    strategy_context,
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
    own_theoretical_max_spend = own_budget_row["Available Budget"].iloc[0] if not own_budget_row.empty else None
    own_spendable_without_debt = own_budget_row["Spendable Without Debt"].iloc[0] if not own_budget_row.empty else None
    own_temporary_negative_buffer = own_budget_row["Temporary Negative Buffer"].iloc[0] if not own_budget_row.empty else None
    own_max_negative = own_budget_row["Max Negative"].iloc[0] if not own_budget_row.empty else None
    own_friday_recovery_need_at_floor = own_budget_row["Friday Recovery Need At Floor"].iloc[0] if not own_budget_row.empty else None

    strategy_context = strategy_context or {}
    management_summary = strategy_context.get("management_summary", {})
    squad_management = strategy_context.get("squad_management", {})
    roster_needs = strategy_context.get("roster_needs", {})
    buy_gates = strategy_context.get("buy_gates", {})
    purchase_review = strategy_context.get("purchase_review", {})
    external_data = strategy_context.get("external_data", {})
    api_football_summary = external_data.get("api_football", {})
    active_offer_actions_df = pd.DataFrame(strategy_context.get("active_offer_actions", []))
    recent_outbid_df = pd.DataFrame(strategy_context.get("recent_outbid", []))
    validation_notes = strategy_context.get("validation_notes", [])
    active_offer_amount_total = float(management_summary.get("active_offer_amount_total", 0) or 0)
    effective_cash_after_active_offers = float(management_summary.get("effective_cash_after_active_offers", own_budget) or own_budget)
    overbid_pressure_level = management_summary.get("overbid_pressure_level", "low")
    suggested_markup_pct = float(management_summary.get("suggested_markup_pct", 0) or 0)
    avg_outbid_gap = float(management_summary.get("avg_outbid_gap", 0) or 0)
    avg_outbid_gap_pct = float(management_summary.get("avg_outbid_gap_pct", 0) or 0)
    recent_outbid_count_14d = int(management_summary.get("recent_outbid_count_14d", 0) or 0)
    market_scarcity_level = squad_management.get("market_scarcity_level", "unknown")
    strong_replacement_count = int(squad_management.get("strong_replacement_count", 0) or 0)
    protected_player_count = int(squad_management.get("protected_player_count", 0) or 0)
    primary_need_position = roster_needs.get("primary_need_position", "none")
    primary_need_level = roster_needs.get("primary_need_level", "none")
    urgent_need_count = int(roster_needs.get("urgent_need_count", 0) or 0)
    structural_gap_count = int(roster_needs.get("structural_gap_count", 0) or 0)
    primary_need_is_structural_gap = bool(roster_needs.get("primary_need_is_structural_gap", False))
    position_need_rows = roster_needs.get("position_needs", [])
    api_football_available = bool(api_football_summary.get("available"))
    api_football_league_name = api_football_summary.get("league_name", "n/a")
    api_football_team_count = int(api_football_summary.get("team_count", 0) or 0)
    api_football_injured_player_count = int(api_football_summary.get("injured_player_count", 0) or 0)
    api_football_questionable_player_count = int(api_football_summary.get("questionable_player_count", 0) or 0)
    api_football_top_teams_df = pd.DataFrame(api_football_summary.get("top_affected_teams", []))
    api_football_adjustment_summary = api_football_summary.get("availability_adjustment_summary", {})

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
        [
            "first_name",
            "last_name",
            "position",
            "team_name",
            "mv",
            "predicted_mv_change",
            "predicted_mv_target",
            "delta_prediction",
            "delta_percent",
            "s_11_prob",
            "football_signal_score",
            "sell_priority_score",
            "squad_role",
            "retention_priority",
            "squad_strategy_note",
            "next_opponent",
            "home_or_away",
            "fixture_difficulty",
        ],
        limit=18,
    )
    expiring_now_text = format_prompt_table(
        market_expiring_now_df,
        [
            "first_name",
            "last_name",
            "position",
            "team_name",
            "mv",
            "predicted_mv_change",
            "predicted_mv_target",
            "delta_prediction",
            "delta_percent",
            "priority_score",
            "football_signal_score",
            "asset_role",
            "buy_action",
            "recommended_bid_min",
            "recommended_bid_max",
            "competitive_bid_max",
            "recent_bid_competition",
            "estimated_market_winning_bid",
            "bid_strategy_note",
            "personal_bid_feedback",
            "position_label",
            "roster_need_level",
            "roster_need_note",
            "team_missing_count",
            "team_questionable_count",
            "team_availability_level",
            "team_availability_note",
            "team_availability_priority_adjustment",
            "has_active_offer",
            "active_offer_amount",
            "active_offer_decision",
            "active_offer_recommended_new_bid",
            "buy_gate_status",
            "buy_gate_reason",
            "effective_bid_cap",
            "hours_to_exp",
            "next_opponent",
            "home_or_away",
            "fixture_difficulty",
        ],
        limit=18,
    )
    later_market_text = format_prompt_table(
        market_later_df,
        [
            "first_name",
            "last_name",
            "position",
            "team_name",
            "mv",
            "predicted_mv_change",
            "predicted_mv_target",
            "delta_prediction",
            "delta_percent",
            "priority_score",
            "football_signal_score",
            "asset_role",
            "buy_action",
            "recommended_bid_min",
            "recommended_bid_max",
            "competitive_bid_max",
            "recent_bid_competition",
            "estimated_market_winning_bid",
            "bid_strategy_note",
            "personal_bid_feedback",
            "position_label",
            "roster_need_level",
            "roster_need_note",
            "team_missing_count",
            "team_questionable_count",
            "team_availability_level",
            "team_availability_note",
            "team_availability_priority_adjustment",
            "has_active_offer",
            "active_offer_amount",
            "active_offer_decision",
            "active_offer_recommended_new_bid",
            "buy_gate_status",
            "buy_gate_reason",
            "effective_bid_cap",
            "hours_to_exp",
            "next_opponent",
            "home_or_away",
            "fixture_difficulty",
        ],
        limit=18,
    )
    trade_stash_text = format_prompt_table(
        market_trade_stash_df,
        [
            "first_name",
            "last_name",
            "position",
            "team_name",
            "mv",
            "predicted_mv_change",
            "predicted_mv_target",
            "delta_prediction",
            "delta_percent",
            "priority_score",
            "asset_role",
            "recommended_bid_max",
            "competitive_bid_max",
            "recent_bid_competition",
            "estimated_market_winning_bid",
            "bid_strategy_note",
            "personal_bid_feedback",
            "position_label",
            "roster_need_level",
            "roster_need_note",
            "team_missing_count",
            "team_questionable_count",
            "team_availability_level",
            "team_availability_note",
            "team_availability_priority_adjustment",
            "has_active_offer",
            "active_offer_amount",
            "active_offer_decision",
            "active_offer_recommended_new_bid",
            "buy_gate_status",
            "buy_gate_reason",
            "effective_bid_cap",
            "hours_to_exp",
            "next_opponent",
            "home_or_away",
            "fixture_difficulty",
        ],
        limit=12,
    )
    hold_candidates_text = format_prompt_table(
        market_hold_df,
        [
            "first_name",
            "last_name",
            "position",
            "team_name",
            "mv",
            "predicted_mv_change",
            "predicted_mv_target",
            "delta_prediction",
            "delta_percent",
            "priority_score",
            "football_signal_score",
            "asset_role",
            "recommended_bid_min",
            "recommended_bid_max",
            "competitive_bid_max",
            "recent_bid_competition",
            "estimated_market_winning_bid",
            "bid_strategy_note",
            "personal_bid_feedback",
            "position_label",
            "roster_need_level",
            "roster_need_note",
            "team_missing_count",
            "team_questionable_count",
            "team_availability_level",
            "team_availability_note",
            "team_availability_priority_adjustment",
            "has_active_offer",
            "active_offer_amount",
            "active_offer_decision",
            "active_offer_recommended_new_bid",
            "hours_to_exp",
            "next_opponent",
            "home_or_away",
            "fixture_difficulty",
        ],
        limit=12,
    )
    squad_risk_text = format_prompt_table(
        squad_risk_df,
        [
            "first_name",
            "last_name",
            "position",
            "team_name",
            "mv",
            "predicted_mv_change",
            "predicted_mv_target",
            "delta_prediction",
            "delta_percent",
            "s_11_prob",
            "football_signal_score",
            "sell_priority_score",
            "squad_action",
            "team_missing_count",
            "team_questionable_count",
            "team_availability_level",
            "team_availability_note",
            "team_availability_sell_adjustment",
        ],
        limit=12,
    )
    active_offer_actions_text = format_prompt_table(
        active_offer_actions_df,
        ["player_name", "current_offer_amount", "recommended_action_label", "recommended_new_bid", "decision_reason_label", "expires_at"],
        limit=8,
    )
    recent_outbid_text = format_prompt_table(
        recent_outbid_df,
        ["player_name", "offer_amount", "winning_price", "lost_to", "resolved_at"],
        limit=8,
    )
    position_needs_text = format_prompt_table(
        pd.DataFrame(position_need_rows),
        ["position_label", "current_count", "minimum_count", "market_option_count", "need_level", "need_note"],
        limit=8,
    )
    api_football_affected_teams_text = format_prompt_table(
        api_football_top_teams_df,
        [
            "team_name",
            "team_missing_count",
            "team_questionable_count",
            "team_availability_level",
            "team_availability_score",
            "next_opponent",
            "fixture_difficulty",
        ],
        limit=8,
    )
    purchase_review_text = format_prompt_table(
        pd.DataFrame(purchase_review.get("recent_evaluations", [])),
        ["player_name", "verdict", "profit_delta", "status_label", "signal_alignment", "signal_note"],
        limit=8,
    )
    validation_notes_text = "\n".join(f"- {note}" for note in validation_notes) if validation_notes else "- Keine"

    theoretical_max_spend_text = format_currency(own_theoretical_max_spend) if own_theoretical_max_spend is not None else "n/a"
    spendable_without_debt_text = format_currency(own_spendable_without_debt) if own_spendable_without_debt is not None else "n/a"
    temporary_negative_buffer_text = format_currency(own_temporary_negative_buffer) if own_temporary_negative_buffer is not None else "n/a"
    max_negative_text = format_currency(own_max_negative) if own_max_negative is not None else "n/a"
    friday_recovery_need_text = format_currency(own_friday_recovery_need_at_floor) if own_friday_recovery_need_at_floor is not None else "n/a"
    own_budget_text = format_currency(own_budget)
    reserved_offer_budget_text = format_currency(active_offer_amount_total)
    effective_cash_after_active_offers_text = format_currency(effective_cash_after_active_offers)
    avg_outbid_gap_text = format_currency(avg_outbid_gap)
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
8. CASH-FIRST: Behandle das aktuelle Budget als echtes frei verfuegbares Cash. Behandle theoretischen Negativspielraum nicht als normales Budget.
9. NEGATIVE BUFFER: Nutze den Negativspielraum nur fuer wenige Ausnahmefaelle mit klarer Exit-Strategie. Jeder Euro oberhalb des echten Cash-Budgets muss bis Freitag wieder hereingeholt werden.
10. FRIDAY DISCIPLINE: Wenn FRIDAY_SAFETY_MODE = active, dann nur ins Minus gehen, wenn du im Text konkret benennst, durch welche Verkaeufe oder sicheren Marktwertanstiege der Rueckweg auf >= 0 bis Freitag realistisch ist.

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
AKTUELL BEREITS DURCH OFFENE GEBOTE GEBUNDENES KAPITAL: {reserved_offer_budget_text} Euro
EFFEKTIV VERFUEGBARES CASH NACH ABZUG DER AKTIVEN GEBOTE: {effective_cash_after_active_offers_text} Euro
ECHT SOFORT VERFUEGBARES CASH OHNE INS MINUS ZU GEHEN: {spendable_without_debt_text} Euro
THEORETISCHES MAXIMALES AUSGABENLIMIT BIS ZUR NEGATIVGRENZE: {theoretical_max_spend_text} Euro
ZUSAETZLICHER TEMPORAERER NEGATIVPUFFER UEBER DEM CASH-BUDGET: {temporary_negative_buffer_text} Euro
MAXIMAL ERLAUBTER KONTOSTAND IM MINUS: {max_negative_text} Euro
RUECKHOLBEDARF BIS FREITAG, WENN DIE NEGATIVGRENZE AUSGEREIZT WIRD: {friday_recovery_need_text} Euro
AKTUELLE KADERGROESSE: {len(squad_recommendations_df)} von 17
NAECHSTER SPIELTAG: {matchday_context['next_matchday']}
NAECHSTER SPIELTAG STARTET: {matchday_context['next_matchday_date']}
TAGE BIS ZUM NAECHSTEN SPIELTAG: {matchday_context['days_until_next_matchday']}
TRADING_WINDOW_MODE: {matchday_context['trading_window_mode']}
FRIDAY_SAFETY_MODE: {matchday_context['friday_safety_mode']}
SPIELPLAN-KONTEXT: {'aktiv' if fixture_context_active else 'nicht verfuegbar'}
API-FOOTBALL-KONTEXT: {'aktiv' if api_football_available else 'nicht verfuegbar'}
API-FOOTBALL LIGA: {api_football_league_name}
API-FOOTBALL TEAMS MIT KONTEXT: {api_football_team_count}
API-FOOTBALL GEMELDETE AUSFAELLE: {api_football_injured_player_count}
API-FOOTBALL QUESTIONABLE FLAGS: {api_football_questionable_player_count}
API-FOOTBALL MARKET-CAUTION-ANPASSUNGEN: {api_football_adjustment_summary.get('market_caution_count', 0)}
API-FOOTBALL MARKET-OPPORTUNITY-ANPASSUNGEN: {api_football_adjustment_summary.get('market_opportunity_count', 0)}
API-FOOTBALL SELL-DRUCK HOCH: {api_football_adjustment_summary.get('squad_sell_pressure_up', 0)}
API-FOOTBALL SELL-DRUCK RUNTER: {api_football_adjustment_summary.get('squad_sell_pressure_down', 0)}
HARTE KAUF-BLOCKS: {buy_gates.get('blocked_count', 0)}
MANAGED EXISTING OFFERS: {buy_gates.get('managed_existing_offer_count', 0)}
SELL-FIRST FLAGS: {buy_gates.get('sell_first_flags', 0)}
LETZTE KAUF-REVIEW GUT: {purchase_review.get('good_count', 0)}
LETZTE KAUF-REVIEW NEUTRAL: {purchase_review.get('neutral_count', 0)}
LETZTE KAUF-REVIEW SCHWACH: {purchase_review.get('poor_count', 0)}
LETZTE KAUF-REVIEW GEGEN MODELLSIGNAL: {purchase_review.get('model_misaligned_count', 0)}
KAUF-REVIEW LEARNING: {purchase_review.get('learning_note', 'Keine Daten')}
KADERSTRUKTUR: {core_starter_count} core_starter, {rotation_hold_count} rotation_hold, {sell_candidate_count} sell_candidate
PERSOENLICHER OVERBID-DRUCK LETZTE 14 TAGE: {overbid_pressure_level}
ANZAHL UEBERBOTENE GEBOTE LETZTE 14 TAGE: {recent_outbid_count_14d}
DURCHSCHNITTLICHER ABSTAND ZUM GEWINNERGEBOT: {avg_outbid_gap_text} Euro ({avg_outbid_gap_pct:.2%})
ALGORITHMISCH EMPFOHLENER PERSOENLICHER AUFSCHLAG FUER HART UMKAEMPFTE GEBOTE: {suggested_markup_pct:.2%}
MARKTKNAPPHEIT FUER GUTE ERSATZ-/UPGRADE-SPIELER: {market_scarcity_level}
STARKE VERFUEGBARE ERSATZOPTIONEN AM MARKT: {strong_replacement_count}
SYSTEMISCH GESCHUETZTE KADERSPIELER WEGEN DUENNEM MARKT: {protected_player_count}
PRIMAERER KADERBEDARF NACH POSITION: {primary_need_position}
DRINGLICHKEIT DIESES POSITIONSBEDARFS: {primary_need_level}
ANZAHL POSITIONEN MIT AKUTEM ODER ERHOEHTEM BEDARF: {urgent_need_count}
ANZAHL ECHTER STRUKTURELLER KADERLUECKEN: {structural_gap_count}
PRIMAERER KADERBEDARF IST EINE ECHTE LUECKE: {'ja' if primary_need_is_structural_gap else 'nein'}

MEHRFACHBELEGUNG PRO VEREIN IM KADER:
{squad_team_counts_text}

AKTIVE GEBOTS-EMPFEHLUNGEN AUS DER SYSTEMLOGIK:
{active_offer_actions_text}

KAUF-REVIEW DER JUENGSTEN EIGENEN TRANSFERS:
{purchase_review_text}

KUERZLICH UEBERBOTENE EIGENE GEBOTE:
{recent_outbid_text}

VALIDIERUNGSHINWEISE AUS DER SYSTEMLOGIK:
{validation_notes_text}

POSITIONSBEDARF AUS DER SYSTEMLOGIK:
{position_needs_text}

API-FOOTBALL TEAM-VERFUEGBARKEIT:
{api_football_affected_teams_text}

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
- estimated_market_winning_bid ist eine datenbasierte Schaetzung, zu welchem Preis die Liga in letzter Zeit aehnliche Spieler typischerweise weggeschnappt hat.
- competitive_bid_max ist dein wettbewerbsfaehiges Maximalgebot, solange der Preis historisch noch profitabel bzw. vertretbar erscheint. Wenn bid_strategy_note auf avoid_price_war oder stay_disciplined steht, sollst du gerade NICHT stumpf auf den geschaetzten Marktpreis hochgehen.
- personal_bid_feedback zeigt, ob competitive_bid_max wegen deiner juengsten Overbid-Historie bereits leicht angehoben wurde.
- active_offer_decision und active_offer_recommended_new_bid sind vorgelagerte Systementscheidungen fuer bereits laufende Gebote.
- buy_gate_status und buy_gate_reason sind harte Vorfilter vor der KI. Wenn buy_gate_status = blocked oder managed_existing_offer, darfst du daraus keine neue Kaufempfehlung machen.
- Wenn buy_gate_status = sell_first, darfst du den Spieler nur als spaetere Chance oder als Kauf nach vorherigem Verkauf darstellen, nicht als sofortigen Kaufbefehl.
- effective_bid_cap ist die harte systemische Obergrenze fuer den Spieler innerhalb der aktuellen Budgetlogik.
- squad_strategy_note zeigt, ob ein Kaderspieler wegen Marktknappheit bewusst eher gehalten werden sollte.
- roster_need_level und roster_need_note zeigen, ob ein Marktspieler wegen einer echten Kaderluecke oder wegen duennem Positions-Backup strukturell wichtiger ist als sein reiner Trading-Wert.
- team_missing_count, team_questionable_count, team_availability_level und team_availability_note kommen aus API-Football und zeigen teamweite Ausfall- bzw. Verfuegbarkeitsrisiken.
- team_availability_priority_adjustment und team_availability_sell_adjustment zeigen, wie diese Teamrisiken bereits deterministisch in Kauf- bzw. Sell-Scores eingepreist wurden.
- recent_bid_competition beschreibt den zuletzt beobachteten Konkurrenzdruck in aehnlichen Deals als low, medium oder high.
- next_opponent, home_or_away und fixture_difficulty kommen, falls verfuegbar, aus einem externen Spielplan-Feed ohne zusaetzlichen KI-Aufruf.
- ECHT SOFORT VERFUEGBARES CASH OHNE INS MINUS ZU GEHEN ist das aktuell wirklich freie Budget in der App.
- THEORETISCHES MAXIMALES AUSGABENLIMIT BIS ZUR NEGATIVGRENZE ist nur eine absolute Obergrenze bis zur erlaubten Minusgrenze und kein normales frei verfuegbares Budget.
- ZUSAETZLICHER TEMPORAERER NEGATIVPUFFER UEBER DEM CASH-BUDGET bedeutet: Jeder Euro daraus muss bis Freitag durch Verkaeufe oder Gewinne wieder aufgeholt werden.

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
- Nutze competitive_bid_max, recent_bid_competition und bid_strategy_note aktiv, um zwischen sinnvollem Mitgehen und unprofitablen Bieterkriegen zu unterscheiden.
- Gib fuer jeden Kaufkandidaten ein maximales Gebot in Euro an. Das Gebot soll sich an Wichtigkeit, Cash-Budget, Trading-Chance, Startelf-Wahrscheinlichkeit und Ablaufzeit orientieren.
- Nutze das theoretische Ausgabenlimit nur als Notfallobergrenze. Normale Empfehlungen sollen sich primaer am echten Cash-Budget orientieren.
- Wenn ein Gebot nur mit Negativpuffer moeglich ist, schreibe das explizit dazu und nenne die wahrscheinlichsten Verkaeufe oder Rueckholhebel bis Freitag.
- Behandle AKTIVE GEBOTS-EMPFEHLUNGEN AUS DER SYSTEMLOGIK als Default-Handlungsbasis. Weiche nur begruendet davon ab.
- Behandle harte Buy Gates als nicht verhandelbar. Ueberschreibe keine blocked- oder managed_existing_offer-Faelle.
- Behandle das bereits gebundene Kapital aus offenen Geboten als nicht erneut verfuegbares Cash.
- Wenn ein Spieler bereits ein aktives Gebot hat, gib keine redundante Neuempfehlung ohne explizite Aussage "Gebot halten", "leicht erhoehen" oder "abbrechen".
- Wenn MARKTKNAPPHEIT FUER GUTE ERSATZ-/UPGRADE-SPIELER = high oder medium, priorisiere das Halten guter, schwer ersetzbarer Kaderspieler. Verkaufe solche Spieler nicht nur, weil sie kurzfristig nicht den maximalen Trading-Gewinn bringen.
- Wenn squad_strategy_note = keep_due_to_thin_market oder lean_keep_due_to_market_scarcity, dann ist Halten der Default. Eine Verkaufsempfehlung braucht dann eine klare, konkrete Begruendung.
- Wenn PRIMAERER KADERBEDARF IST EINE ECHTE LUECKE = ja, behandle diese Luecke als echte Management-Prioritaet. Das gilt besonders fuer GK/Torwart: ein fehlender Torwart darf nicht nur wegen besserer Trading-Chancen auf spaeter verschoben werden.
- Wenn PRIMAERER KADERBEDARF IST EINE ECHTE LUECKE = nein, formuliere das NICHT als fehlenden Spieler oder als Kaderluecke. Beschreibe es stattdessen als Absicherung, Backup-Bedarf oder qualitative Kaderverbesserung.
- Wenn roster_need_level = high oder medium, darf ein Spieler dieser Position gegenueber rein besseren Trading-Kandidaten vorgezogen werden, sofern das Budget realistisch bleibt.
- Wenn PERSOENLICHER OVERBID-DRUCK = medium oder high, pruefe aktiv, ob competitive_bid_max bei Prioritaet-A-Kandidaten leicht angehoben werden sollte, statt immer nur dieselbe disziplinierte Grenze zu wiederholen.
- Wenn historical bid pressure hoch ist, entscheide explizit zwischen "mitgehen" und "Preiskrieg vermeiden". Ein hohes estimated_market_winning_bid ist kein Kaufzwang.
- Wenn die Kauf-Review zuletzt mehrere schwache oder gegen das Modellsignal gelaufene Kaeufe zeigt, werde bei Grenzfaellen spuerbar disziplinierter.
- Unterscheide klar zwischen:
  A) Sofort kaufen vor dem naechsten Marktwertupdate
  B) Beobachten und spaeter angreifen
  C) Nicht kaufen
- Beruecksichtige auch Verkaeufe aus meinem Kader, wenn dadurch bessere Trades oder wichtigere Einkaeufe moeglich werden.
- Wenn ein Spieler vor allem als Trading-Asset interessant ist, sage das explizit.

Antwortformat (STRENG EINHALTEN):

1. TEAMSTATUS: Kurze Einordnung meines Kaders, meines Budgets, des Tradingfensters und meines dringendsten Handlungsbedarfs heute Abend.
2. VERKAUFS-BEFEHLE: Wer muss weg oder ist aktiv entbehrlich? Fokus auf fallende Werte, Risiko und Kapitalfreisetzung.
3. SOFORT-KAEUFE BIS ZUM NAECHSTEN UPDATE: Nenne nur die wichtigsten Spieler aus Marktsegment A. Format je Spieler: "Kauf [Name] | Prioritaet [A/B/C] | Max Gebot [Euro] | Rolle [Starter/Trader/Hold] | Warum jetzt".
   Wenn du auf einen Spieler bereits aktiv bietest, nutze stattdessen das Format: "Aktives Gebot [Name] | Aktion [halten/leicht erhoehen/abbrechen] | Neues Max Gebot [Euro oder unveraendert] | Warum".
4. SPAETERE CHANCEN UND HOLDS: Welche spaeter auslaufenden Spieler oder mehrtaegigen Holds darf ich nicht verpassen? Format je Spieler: "Beobachte [Name] | Zielstrategie [Overnight/2-4 Tage/Spieltag] | Spaeteres Max Gebot | Warum relevant".
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
