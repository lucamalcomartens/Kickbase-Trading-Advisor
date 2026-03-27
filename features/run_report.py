from __future__ import annotations

import json
import os
from datetime import datetime

import pandas as pd


REPORT_HISTORY_LIMIT = 3


def write_run_report(
    output_dir,
    repo_output_dir,
    report_date,
    own_username,
    own_budget,
    manager_budgets_df,
    matchday_context,
    model_metrics,
    market_df,
    squad_df,
    ai_status,
    ai_advice,
    mail_status,
    fixture_context_active,
    offer_tracking_summary=None,
    strategy_context=None,
):
    """Write a sanitized summary of the latest run for later inspection."""

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(repo_output_dir, exist_ok=True)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "report_date": report_date,
        "own_username": own_username,
        "own_budget": _safe_number(own_budget),
        "own_budget_row": _summarize_own_budget(manager_budgets_df, own_username),
        "matchday_context": matchday_context,
        "model_metrics": model_metrics,
        "market_player_count": int(len(market_df)),
        "squad_player_count": int(len(squad_df)),
        "fixture_context_active": bool(fixture_context_active),
        "ai_status": ai_status,
        "mail_status": mail_status,
        "offer_tracking_summary": offer_tracking_summary or {"counts": {}, "recent_outbid": []},
        "strategy_context": strategy_context or {"management_summary": {}, "squad_management": {}, "roster_needs": {}, "active_offer_actions": [], "validation_notes": []},
        "top_market_candidates": _summarize_market(market_df),
        "top_sell_candidates": _summarize_squad(squad_df),
        "budget_table": _frame_to_text(manager_budgets_df, limit=10),
        "market_table": _frame_to_text(market_df, columns=[
            "first_name",
            "last_name",
            "team_name",
            "mv",
            "predicted_mv_change",
            "priority_score",
            "recommended_bid_max",
            "competitive_bid_max",
            "recent_bid_competition",
            "bid_strategy_note",
            "position_label",
            "roster_need_level",
            "team_missing_count",
            "team_questionable_count",
            "team_availability_level",
            "team_availability_priority_adjustment",
            "active_offer_decision",
            "active_offer_recommended_new_bid",
            "hours_to_exp",
        ], limit=15),
        "squad_table": _frame_to_text(squad_df, columns=[
            "first_name",
            "last_name",
            "team_name",
            "mv",
            "predicted_mv_change",
            "sell_priority_score",
            "squad_role",
            "squad_strategy_note",
            "team_missing_count",
            "team_questionable_count",
            "team_availability_level",
            "team_availability_sell_adjustment",
            "s_11_prob",
            "next_opponent",
        ], limit=15),
        "ai_excerpt": _excerpt(ai_advice),
        "ai_full_text": str(ai_advice or ""),
    }

    rendered_markdown = _render_markdown(payload)

    _write_report_bundle(output_dir, payload, rendered_markdown)
    _write_report_bundle(repo_output_dir, payload, rendered_markdown)


def _write_report_bundle(target_dir, payload, rendered_markdown):
    json_path = os.path.join(target_dir, "last_run_summary.json")
    markdown_path = os.path.join(target_dir, "last_run_summary.md")
    consolidated_markdown_path = os.path.join(target_dir, "latest_run_report.md")

    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(payload, json_file, ensure_ascii=False, indent=2)

    with open(markdown_path, "w", encoding="utf-8") as markdown_file:
        markdown_file.write(rendered_markdown)

    with open(consolidated_markdown_path, "w", encoding="utf-8") as markdown_file:
        markdown_file.write(rendered_markdown)

    _rotate_markdown_report_history(target_dir, rendered_markdown)


def _rotate_markdown_report_history(output_dir, rendered_markdown):
    for index in range(REPORT_HISTORY_LIMIT, 1, -1):
        older_path = os.path.join(output_dir, f"run_report_history_{index - 1:02d}.md")
        newer_path = os.path.join(output_dir, f"run_report_history_{index:02d}.md")
        if os.path.exists(older_path):
            os.replace(older_path, newer_path)

    newest_history_path = os.path.join(output_dir, "run_report_history_01.md")
    with open(newest_history_path, "w", encoding="utf-8") as markdown_file:
        markdown_file.write(rendered_markdown)


def _summarize_own_budget(manager_budgets_df, own_username):
    if manager_budgets_df is None or manager_budgets_df.empty or "User" not in manager_budgets_df.columns:
        return {}

    own_row = manager_budgets_df[manager_budgets_df["User"] == own_username]
    if own_row.empty:
        return {}

    columns = [
        "User",
        "Budget",
        "Current Cash",
        "Spendable Without Debt",
        "Temporary Negative Buffer",
        "Available Budget",
        "Max Negative",
        "Friday Recovery Need At Floor",
    ]
    available_columns = [column for column in columns if column in own_row.columns]
    return {
        key: _safe_number(value) for key, value in own_row.iloc[0][available_columns].to_dict().items()
    }


def _summarize_market(market_df):
    if market_df.empty:
        return []

    summary = []
    columns = [
        "first_name",
        "last_name",
        "team_name",
        "priority_score",
        "asset_role",
        "predicted_mv_change",
        "recommended_bid_max",
        "competitive_bid_max",
        "recent_bid_competition",
        "hours_to_exp",
        "next_opponent",
        "fixture_difficulty",
    ]
    available_columns = [column for column in columns if column in market_df.columns]

    for _, row in market_df.head(5)[available_columns].iterrows():
        summary.append(
            {
                "player": _player_name(row),
                "team_name": row.get("team_name"),
                "priority_score": _safe_number(row.get("priority_score")),
                "asset_role": row.get("asset_role"),
                "predicted_mv_change": _safe_number(row.get("predicted_mv_change")),
                "recommended_bid_max": _safe_number(row.get("recommended_bid_max")),
                "competitive_bid_max": _safe_number(row.get("competitive_bid_max")),
                "recent_bid_competition": row.get("recent_bid_competition"),
                "hours_to_exp": _safe_number(row.get("hours_to_exp")),
                "next_opponent": row.get("next_opponent"),
                "fixture_difficulty": row.get("fixture_difficulty"),
            }
        )

    return summary


def _summarize_squad(squad_df):
    if squad_df.empty:
        return []

    summary = []
    columns = [
        "first_name",
        "last_name",
        "team_name",
        "sell_priority_score",
        "squad_role",
        "predicted_mv_change",
        "s_11_prob",
        "next_opponent",
        "fixture_difficulty",
    ]
    available_columns = [column for column in columns if column in squad_df.columns]

    for _, row in squad_df.head(5)[available_columns].iterrows():
        summary.append(
            {
                "player": _player_name(row),
                "team_name": row.get("team_name"),
                "sell_priority_score": _safe_number(row.get("sell_priority_score")),
                "squad_role": row.get("squad_role"),
                "predicted_mv_change": _safe_number(row.get("predicted_mv_change")),
                "s_11_prob": _safe_number(row.get("s_11_prob")),
                "next_opponent": row.get("next_opponent"),
                "fixture_difficulty": row.get("fixture_difficulty"),
            }
        )

    return summary


def _player_name(row):
    first_name = str(row.get("first_name", "") or "").strip()
    last_name = str(row.get("last_name", "") or "").strip()
    return " ".join(part for part in [first_name, last_name] if part)


def _safe_number(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return value


def _excerpt(text, max_length=600):
    if not text:
        return ""
    compact = " ".join(str(text).split())
    return compact[:max_length]


def _frame_to_text(dataframe, columns=None, limit=10):
    if dataframe is None or dataframe.empty:
        return "Keine Daten verfuegbar"

    display_df = dataframe.copy()
    if columns is not None:
        available_columns = [column for column in columns if column in display_df.columns]
        display_df = display_df[available_columns]

    if limit is not None:
        display_df = display_df.head(limit)

    if display_df.empty:
        return "Keine Daten verfuegbar"

    safe_df = display_df.copy().where(pd.notna(display_df), "-")
    return safe_df.to_string(index=False)


def _render_markdown(payload):
    market_lines = "\n".join(
        f"- {item['player']} | Team: {item['team_name']} | Score: {item['priority_score']} | Rolle: {item['asset_role']} | Delta: {item['predicted_mv_change']} | Max: {item['recommended_bid_max']} | Competitive Max: {item['competitive_bid_max']} | Wettbewerb: {item['recent_bid_competition']} | Gegner: {item['next_opponent']} | Fixture: {item['fixture_difficulty']}"
        for item in payload["top_market_candidates"]
    ) or "- Keine Daten"

    strategy_context = payload.get("strategy_context", {})
    management_summary = strategy_context.get("management_summary", {})
    squad_management = strategy_context.get("squad_management", {})
    roster_needs = strategy_context.get("roster_needs", {})
    api_football_summary = strategy_context.get("external_data", {}).get("api_football", {})
    availability_adjustment_summary = api_football_summary.get("availability_adjustment_summary", {})
    validation_lines = "\n".join(
        f"- {item}" for item in strategy_context.get("validation_notes", [])
    ) or "- Keine Hinweise"
    active_offer_action_lines = "\n".join(
        f"- {item.get('player_name')} | Aktion: {item.get('recommended_action_label')} | Aktuelles Gebot: {item.get('current_offer_amount')} | Neues Max Gebot: {item.get('recommended_new_bid')} | Grund: {item.get('decision_reason_label')}"
        for item in strategy_context.get("active_offer_actions", [])
    ) or "- Keine aktiven Gebotsentscheidungen gespeichert"
    roster_need_lines = "\n".join(
        f"- {item.get('position_label')} | Im Kader: {item.get('current_count')} | Minimum: {item.get('minimum_count')} | Marktoptionen: {item.get('market_option_count')} | Bedarf: {item.get('need_level')} | Hinweis: {item.get('need_note')}"
        for item in roster_needs.get("position_needs", [])
    ) or "- Kein akuter Positionsbedarf erkannt"
    api_football_lines = "\n".join(
        f"- {item.get('team_name')} | Missing: {item.get('team_missing_count')} | Questionable: {item.get('team_questionable_count')} | Level: {item.get('team_availability_level')} | Score: {item.get('team_availability_score')} | Gegner: {item.get('next_opponent')} | Fixture: {item.get('fixture_difficulty')}"
        for item in api_football_summary.get("top_affected_teams", [])
    ) or "- Keine auffaelligen Team-Ausfaelle im API-Football Kontext"

    offer_counts = payload["offer_tracking_summary"].get("counts", {})
    budget_row = payload.get("own_budget_row", {})
    active_offer_lines = "\n".join(
        f"- {item.get('player_name')} | Gebot: {item.get('offer_amount')} | Marktwert: {item.get('market_value')} | Ablauf: {item.get('expires_at')}"
        for item in payload["offer_tracking_summary"].get("recent_active", [])
    ) or "- Keine aktiven Gebote gespeichert"
    outbid_lines = "\n".join(
        f"- {item.get('player_name')} | Dein Gebot: {item.get('offer_amount')} | Gewinnerpreis: {item.get('winning_price')} | Gewinner: {item.get('lost_to')} | Aufgeloest: {item.get('resolved_at')}"
        for item in payload["offer_tracking_summary"].get("recent_outbid", [])
    ) or "- Keine ueberbotenen Gebote gespeichert"
    offer_debug = payload["offer_tracking_summary"].get("debug", {})
    market_debug = payload["offer_tracking_summary"].get("market_debug", {})
    offer_debug_lines = "\n".join(
        f"- Pfad: {item.get('path')} | Spieler: {item.get('player_name')} | Spieler-ID: {item.get('player_id')} | Betrag: {item.get('offer_amount')} | Marktwert: {item.get('market_value')} | Ablauf: {item.get('expires_at')} | Offer-ID: {item.get('offer_id')} | Path-Hint: {item.get('path_hint')} | Keys: {', '.join(item.get('keys', []))}"
        for item in offer_debug.get("examples", [])
    )
    structure_debug_lines = "\n".join(
        f"- Pfad: {item.get('path')} | Typ: {item.get('node_type')} | Laenge: {item.get('length')} | Keys: {', '.join(item.get('keys', []))}"
        for item in offer_debug.get("structure_examples", [])
    )
    market_debug_lines = "\n".join(
        f"- Pfad: {item.get('path')} | Spieler: {item.get('player_name')} | Spieler-ID: {item.get('player_id')} | Marktwert: {item.get('market_value')} | Ablauf: {item.get('expires_at')} | Keys: {', '.join(item.get('keys', []))} | Sample: {json.dumps(item.get('sample', {}), ensure_ascii=False)}"
        for item in market_debug.get("examples", [])
    )

    squad_lines = "\n".join(
        f"- {item['player']} | Team: {item['team_name']} | Sell Score: {item['sell_priority_score']} | Rolle: {item['squad_role']} | Delta: {item['predicted_mv_change']} | Gegner: {item['next_opponent']} | Fixture: {item['fixture_difficulty']}"
        for item in payload["top_sell_candidates"]
    ) or "- Keine Daten"

    return f"""# Last Run Summary

- Report Date: {payload['report_date']}
- Generated At: {payload['generated_at']}
- User: {payload['own_username']}
- Own Budget: {payload['own_budget']}
- Market Players: {payload['market_player_count']}
- Squad Players: {payload['squad_player_count']}
- Fixture Context Active: {payload['fixture_context_active']}
- AI Status: {payload['ai_status']}
- Mail Status: {payload['mail_status']}
- Offer Tracking Active: {offer_counts.get('active_offers', 0)}
- Offer Tracking Outbid: {offer_counts.get('outbid_offers', 0)}
- Offer Tracking Won: {offer_counts.get('won_offers', 0)}

## Model Metrics

- Signs Correct: {payload['model_metrics'].get('signs_percent')}
- RMSE: {payload['model_metrics'].get('rmse')}
- MAE: {payload['model_metrics'].get('mae')}
- R2: {payload['model_metrics'].get('r2')}

## Matchday Context

- Next Matchday: {payload['matchday_context'].get('next_matchday')}
- Next Matchday Date: {payload['matchday_context'].get('next_matchday_date')}
- Days Until Next Matchday: {payload['matchday_context'].get('days_until_next_matchday')}
- Trading Window Mode: {payload['matchday_context'].get('trading_window_mode')}
- Friday Safety Mode: {payload['matchday_context'].get('friday_safety_mode')}

## Own Budget Context

- Budget: {budget_row.get('Budget')}
- Current Cash: {budget_row.get('Current Cash')}
- Spendable Without Debt: {budget_row.get('Spendable Without Debt')}
- Temporary Negative Buffer: {budget_row.get('Temporary Negative Buffer')}
- Theoretical Max Spend: {budget_row.get('Available Budget')}
- Max Negative: {budget_row.get('Max Negative')}
- Friday Recovery Need At Floor: {budget_row.get('Friday Recovery Need At Floor')}

## Management Summary

- Aktive Gebotssumme: {management_summary.get('active_offer_amount_total')}
- Effektives Cash nach aktiven Geboten: {management_summary.get('effective_cash_after_active_offers')}
- Overbid-Druck: {management_summary.get('overbid_pressure_level')}
- Suggested Markup: {management_summary.get('suggested_markup_pct')}
- Outbid Count 14d: {management_summary.get('recent_outbid_count_14d')}
- Aktive Gebote halten: {management_summary.get('action_counts', {}).get('hold', 0)}
- Aktive Gebote leicht erhoehen: {management_summary.get('action_counts', {}).get('raise_small', 0)}
- Aktive Gebote abbrechen: {management_summary.get('action_counts', {}).get('abort', 0)}

## Squad Retention Summary

- Marktknappheit: {squad_management.get('market_scarcity_level')}
- Starke Ersatzoptionen am Markt: {squad_management.get('strong_replacement_count')}
- Geschuetzte Kaderspieler: {squad_management.get('protected_player_count')}

## Roster Need Summary

- Primaerer Positionsbedarf: {roster_needs.get('primary_need_position')}
- Dringlichkeit: {roster_needs.get('primary_need_level')}
- Positionen mit Bedarf: {roster_needs.get('urgent_need_count')}

{roster_need_lines}

## API-Football Summary

- API-Football aktiv: {api_football_summary.get('available')}
- Grund: {api_football_summary.get('reason')}
- Liga: {api_football_summary.get('league_name')}
- Season: {api_football_summary.get('season')}
- Angefragte Season: {api_football_summary.get('requested_season')}
- Season-Fallback aktiv: {api_football_summary.get('season_fallback_applied')}
- Teams mit Kontext: {api_football_summary.get('team_count')}
- Teams geladen: {api_football_summary.get('teams_loaded')}
- Standings geladen: {api_football_summary.get('standings_loaded')}
- Geladene Fixtures: {api_football_summary.get('fixtures_loaded')}
- Injury Entries: {api_football_summary.get('injury_entries_loaded')}
- Missing Player Flags: {api_football_summary.get('injured_player_count')}
- Questionable Flags: {api_football_summary.get('questionable_player_count')}
- Market Caution Adjustments: {availability_adjustment_summary.get('market_caution_count')}
- Market Opportunity Adjustments: {availability_adjustment_summary.get('market_opportunity_count')}
- Squad Sell Pressure Up: {availability_adjustment_summary.get('squad_sell_pressure_up')}
- Squad Sell Pressure Down: {availability_adjustment_summary.get('squad_sell_pressure_down')}
- Fehler: {api_football_summary.get('error')}

{api_football_lines}

## Strategy Validation

{validation_lines}

## Manager Budget Snapshot

```text
{payload['budget_table']}
```

## Top Market Candidates

{market_lines}

## Market Snapshot

```text
{payload['market_table']}
```

## Top Sell Candidates

{squad_lines}

## Squad Snapshot

```text
{payload['squad_table']}
```

## Active Offers

{active_offer_lines}

## Active Offer Actions

{active_offer_action_lines}

## Recent Outbid Offers

{outbid_lines}

## Offer Tracking Debug

- Root Type: {offer_debug.get('root_type')}
- Candidate Count: {offer_debug.get('candidate_count', 0)}
{offer_debug_lines or '- Keine Debug-Kandidaten gespeichert'}

### Feed Structure Debug

{structure_debug_lines or '- Keine Struktur-Daten gespeichert'}

### Market Feed Debug

- Root Type: {market_debug.get('root_type')}
- Item Count: {market_debug.get('item_count', 0)}
{market_debug_lines or '- Keine Market-Debug-Daten gespeichert'}

## AI Full Output

{payload['ai_full_text']}
"""