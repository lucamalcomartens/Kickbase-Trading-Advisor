from __future__ import annotations

import json
import os
from datetime import datetime

import pandas as pd


def write_run_report(
    output_dir,
    report_date,
    own_username,
    own_budget,
    matchday_context,
    model_metrics,
    market_df,
    squad_df,
    ai_status,
    ai_advice,
    mail_status,
    fixture_context_active,
):
    """Write a sanitized summary of the latest run for later inspection."""

    os.makedirs(output_dir, exist_ok=True)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "report_date": report_date,
        "own_username": own_username,
        "own_budget": _safe_number(own_budget),
        "matchday_context": matchday_context,
        "model_metrics": model_metrics,
        "market_player_count": int(len(market_df)),
        "squad_player_count": int(len(squad_df)),
        "fixture_context_active": bool(fixture_context_active),
        "ai_status": ai_status,
        "mail_status": mail_status,
        "top_market_candidates": _summarize_market(market_df),
        "top_sell_candidates": _summarize_squad(squad_df),
        "ai_excerpt": _excerpt(ai_advice),
    }

    json_path = os.path.join(output_dir, "last_run_summary.json")
    markdown_path = os.path.join(output_dir, "last_run_summary.md")

    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(payload, json_file, ensure_ascii=False, indent=2)

    with open(markdown_path, "w", encoding="utf-8") as markdown_file:
        markdown_file.write(_render_markdown(payload))


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


def _render_markdown(payload):
    market_lines = "\n".join(
        f"- {item['player']} | Team: {item['team_name']} | Score: {item['priority_score']} | Rolle: {item['asset_role']} | Delta: {item['predicted_mv_change']} | Gegner: {item['next_opponent']} | Fixture: {item['fixture_difficulty']}"
        for item in payload["top_market_candidates"]
    ) or "- Keine Daten"

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

## Top Market Candidates

{market_lines}

## Top Sell Candidates

{squad_lines}

## AI Excerpt

{payload['ai_excerpt']}
"""