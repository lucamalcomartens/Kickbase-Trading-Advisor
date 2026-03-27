from __future__ import annotations

import datetime
import json
import os
from zoneinfo import ZoneInfo

import pandas as pd

from kickbase_api.others import get_matchdays


MAX_ANALYSIS_HISTORY_ENTRIES = 20
PROMPT_HISTORY_ENTRIES = 3


def format_currency(value):
    """Format a numeric value for compact prompt output."""

    if pd.isna(value):
        return "n/a"
    return f"{float(value):,.0f}".replace(",", ".")


def format_prompt_table(df, columns, limit=None):
    """Return a compact table string with only the columns relevant for the prompt."""

    available_columns = [column for column in columns if column in df.columns]
    prompt_df = df[available_columns].copy()

    if limit is not None:
        prompt_df = prompt_df.head(limit)

    if prompt_df.empty:
        return "Keine Daten verfuegbar"

    return prompt_df.to_string(index=False)


def build_player_name(df):
    """Create a compact player name column from first and last name."""

    return (df["first_name"].fillna("") + " " + df["last_name"].fillna("")).str.strip()


def prepare_top_actions(market_df, squad_df, strategy_context=None):
    """Build compact top-action tables for the email header and mobile-first reading."""

    market_df = market_df.copy()
    if "competitive_bid_range" in market_df.columns:
        market_df["display_bid_range"] = market_df["competitive_bid_range"].fillna(market_df.get("bid_range"))
    else:
        market_df["display_bid_range"] = market_df.get("bid_range")

    if "competitive_bid_max" in market_df.columns:
        market_df["display_bid_max"] = market_df["competitive_bid_max"].fillna(market_df.get("recommended_bid_max"))
    else:
        market_df["display_bid_max"] = market_df.get("recommended_bid_max")

    buy_now_df = market_df[market_df["buy_action"] == "buy_now"].copy().head(5)
    watchlist_df = market_df[
        (market_df["buy_action"] == "watchlist") & (~market_df["expiring_today"])
    ].copy().head(5)
    sell_df = squad_df[squad_df["squad_action"] == "sell"].copy().head(5)

    if not buy_now_df.empty:
        buy_now_df["Spieler"] = build_player_name(buy_now_df)
        buy_now_df = buy_now_df[["Spieler", "team_name", "asset_role", "priority_score", "display_bid_range"]].rename(
            columns={
                "team_name": "Team",
                "asset_role": "Rolle",
                "priority_score": "Score",
                "display_bid_range": "Gebot",
            }
        )

    if not watchlist_df.empty:
        watchlist_df["Spieler"] = build_player_name(watchlist_df)
        watchlist_df = watchlist_df[
            ["Spieler", "team_name", "asset_role", "priority_score", "display_bid_max"]
        ].rename(
            columns={
                "team_name": "Team",
                "asset_role": "Zieltyp",
                "priority_score": "Score",
                "display_bid_max": "Max Gebot",
            }
        )

    if not sell_df.empty:
        sell_df["Spieler"] = build_player_name(sell_df)
        sell_df = sell_df[["Spieler", "team_name", "squad_role", "sell_priority_score", "delta_prediction"]].rename(
            columns={
                "team_name": "Team",
                "squad_role": "Typ",
                "sell_priority_score": "Sell Score",
                "delta_prediction": "Delta",
            }
        )

    sections = {
        "Jetzt kaufen": {
            "subtitle": "Die wichtigsten Deals vor dem naechsten Marktwertupdate.",
            "data": buy_now_df,
        },
        "Spaeter beobachten": {
            "subtitle": "Starke Optionen, die nicht heute Nacht verloren gehen.",
            "data": watchlist_df,
        },
        "Eher verkaufen": {
            "subtitle": "Spieler, die Kapital blockieren oder an Risiko gewinnen.",
            "data": sell_df,
        },
    }

    active_offer_actions = pd.DataFrame((strategy_context or {}).get("active_offer_actions", []))
    if not active_offer_actions.empty:
        active_offer_actions = active_offer_actions[
            [
                "player_name",
                "recommended_action_label",
                "current_offer_amount",
                "recommended_new_bid",
            ]
        ].rename(
            columns={
                "player_name": "Spieler",
                "recommended_action_label": "Aktion",
                "current_offer_amount": "Aktuelles Gebot",
                "recommended_new_bid": "Neues Max Gebot",
            }
        )
        sections["Aktive Gebote"] = {
            "subtitle": "Bereits laufende Gebote mit vorbewerteter Aktion.",
            "data": active_offer_actions.head(5),
        }

    return sections


def load_analysis_history(file_path):
    """Load persisted compact analysis history for prompt continuity."""

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as history_file:
            history_data = json.load(history_file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Warnung: Analyse-History konnte nicht geladen werden: {error}")
        return []

    return history_data if isinstance(history_data, list) else []


def save_analysis_history(file_path, history_entries):
    """Persist compact analysis history for future prompt context."""

    try:
        with open(file_path, "w", encoding="utf-8") as history_file:
            json.dump(
                history_entries[-MAX_ANALYSIS_HISTORY_ENTRIES:],
                history_file,
                ensure_ascii=False,
                indent=2,
            )
    except OSError as error:
        print(f"Warnung: Analyse-History konnte nicht gespeichert werden: {error}")


def summarise_player_rows(df, role_column, limit=3):
    """Create compact one-line player summaries for analysis history."""

    if df.empty:
        return []

    player_names = build_player_name(df)
    summaries = []
    for index, (_, row) in enumerate(df.head(limit).iterrows()):
        player_name = player_names.iloc[index]
        role_value = row.get(role_column, "n/a")
        delta_value = format_currency(row.get("delta_prediction", 0))
        team_name = row.get("team_name", "unbekannt")
        summaries.append(f"{player_name} ({team_name}) | {role_value} | Delta {delta_value}")

    return summaries


def format_history_for_prompt(history_entries, max_entries=PROMPT_HISTORY_ENTRIES):
    """Return the last compact analysis summaries as prompt text."""

    if not history_entries:
        return "Keine vorherigen Analysen gespeichert."

    history_lines = []
    for entry in history_entries[-max_entries:]:
        history_lines.append(
            "\n".join(
                [
                    f"- Analyse vom {entry.get('report_date', 'unbekannt')} | Window: {entry.get('trading_window_mode', 'unknown')} | Friday: {entry.get('friday_safety_mode', 'unknown')} | Budget: {entry.get('own_budget', 'n/a')}",
                    f"  Gebundenes Gebotskapital: {entry.get('reserved_offer_budget', 'n/a')} | Effektives Cash: {entry.get('effective_cash_after_active_offers', 'n/a')}",
                    f"  Top Buys: {', '.join(entry.get('top_buys', [])) or 'keine'}",
                    f"  Aktive Gebote: {', '.join(entry.get('active_offer_actions', [])) or 'keine'}",
                    f"  Top Holds: {', '.join(entry.get('top_holds', [])) or 'keine'}",
                    f"  Top Sells: {', '.join(entry.get('top_sells', [])) or 'keine'}",
                    f"  Letzte KI-Kernaussage: {entry.get('ai_excerpt', 'keine')}",
                ]
            )
        )

    return "\n\n".join(history_lines)


def build_history_entry(report_date, own_budget_value, matchday_info, market_df, squad_df, ai_text, ai_status, strategy_context=None):
    """Build a compact persisted summary for future analyses."""

    buy_candidates = market_df[market_df["buy_action"] == "buy_now"]
    hold_candidates = market_df[
        (market_df["delta_prediction"] > 0)
        & (market_df["asset_role"].isin(["medium_term_hold", "core_starter"]))
    ]
    sell_candidates = squad_df[squad_df["squad_action"] == "sell"]
    ai_excerpt = " ".join(str(ai_text).split())[:320] if ai_text else "keine"
    management_summary = (strategy_context or {}).get("management_summary", {})
    active_offer_actions = (strategy_context or {}).get("active_offer_actions", [])

    return {
        "report_date": report_date,
        "created_at": datetime.datetime.now(ZoneInfo("Europe/Berlin")).isoformat(),
        "trading_window_mode": matchday_info.get("trading_window_mode", "unknown"),
        "friday_safety_mode": matchday_info.get("friday_safety_mode", "unknown"),
        "next_matchday": matchday_info.get("next_matchday", "unbekannt"),
        "days_until_next_matchday": matchday_info.get("days_until_next_matchday", "unbekannt"),
        "own_budget": format_currency(own_budget_value),
        "reserved_offer_budget": format_currency(management_summary.get("active_offer_amount_total")),
        "effective_cash_after_active_offers": format_currency(management_summary.get("effective_cash_after_active_offers")),
        "squad_size": int(len(squad_df)),
        "top_buys": summarise_player_rows(buy_candidates, "asset_role"),
        "active_offer_actions": [
            f"{item.get('player_name')} | {item.get('recommended_action_label')} | {format_currency(item.get('recommended_new_bid'))}"
            for item in active_offer_actions[:3]
        ],
        "top_holds": summarise_player_rows(hold_candidates, "asset_role"),
        "top_sells": summarise_player_rows(sell_candidates, "squad_role"),
        "ai_status": ai_status,
        "ai_excerpt": ai_excerpt or "keine",
    }


def get_next_matchday_context(token, competition_id):
    """Return basic schedule context for prompt steering around breaks and matchday pressure."""

    now = datetime.datetime.now(ZoneInfo("Europe/Berlin"))

    try:
        matchdays = get_matchdays(token, competition_id)
    except Exception:
        return {
            "next_matchday": "unbekannt",
            "next_matchday_date": "unbekannt",
            "days_until_next_matchday": "unbekannt",
            "trading_window_mode": "unknown",
            "friday_safety_mode": "unknown",
        }

    future_matchdays = []
    for matchday in matchdays:
        matchday_date = matchday.get("date")
        if not matchday_date:
            continue
        matchday_dt = datetime.datetime.fromisoformat(matchday_date).astimezone(ZoneInfo("Europe/Berlin"))
        if matchday_dt >= now:
            future_matchdays.append((matchday.get("day"), matchday_dt))

    if not future_matchdays:
        return {
            "next_matchday": "unbekannt",
            "next_matchday_date": "unbekannt",
            "days_until_next_matchday": "unbekannt",
            "trading_window_mode": "unknown",
            "friday_safety_mode": "unknown",
        }

    next_matchday, next_matchday_dt = future_matchdays[0]
    days_until_next_matchday = (next_matchday_dt.date() - now.date()).days

    if days_until_next_matchday >= 8:
        trading_window_mode = "extended_break"
    elif days_until_next_matchday >= 4:
        trading_window_mode = "normal_build_up"
    else:
        trading_window_mode = "matchday_close"

    friday_safety_mode = "active" if days_until_next_matchday <= 3 else "inactive"

    return {
        "next_matchday": next_matchday,
        "next_matchday_date": next_matchday_dt.strftime("%d-%m-%Y %H:%M"),
        "days_until_next_matchday": days_until_next_matchday,
        "trading_window_mode": trading_window_mode,
        "friday_safety_mode": friday_safety_mode,
    }