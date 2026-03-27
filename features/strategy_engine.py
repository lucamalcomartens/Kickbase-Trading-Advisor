from __future__ import annotations

import math

import pandas as pd


MIN_ACTIVE_OFFER_RAISE_EUR = 25_000
MIN_ACTIVE_OFFER_RAISE_PCT = 0.005


def build_strategy_context(market_df, offer_tracking_summary, own_budget):
    """Create deterministic strategy context before handing control to the AI layer."""

    working_market_df = market_df.copy()
    _ensure_active_offer_columns(working_market_df)

    offer_tracking_summary = offer_tracking_summary or {}
    offer_stats = offer_tracking_summary.get("stats", {})
    active_offers_df = pd.DataFrame(offer_tracking_summary.get("recent_active", []))
    recent_outbid = offer_tracking_summary.get("recent_outbid", [])

    if active_offers_df.empty:
        management_summary = _build_management_summary(
            own_budget=own_budget,
            active_offer_amount_total=float(offer_stats.get("active_offer_amount_total", 0) or 0),
            overbid_pressure_level=offer_stats.get("overbid_pressure_level", "low"),
            suggested_markup_pct=float(offer_stats.get("suggested_markup_pct", 0) or 0),
            recent_outbid_count_14d=int(offer_stats.get("recent_outbid_count_14d", 0) or 0),
            avg_outbid_gap=float(offer_stats.get("avg_outbid_gap", 0) or 0),
            avg_outbid_gap_pct=float(offer_stats.get("avg_outbid_gap_pct", 0) or 0),
            active_offer_actions=[],
        )
        return working_market_df, {
            "management_summary": management_summary,
            "active_offer_actions": [],
            "recent_outbid": recent_outbid,
            "validation_notes": management_summary["validation_notes"],
        }

    active_offers_df = active_offers_df.copy()
    active_offers_df["offer_amount"] = pd.to_numeric(active_offers_df.get("offer_amount"), errors="coerce")
    active_offers_df["market_value"] = pd.to_numeric(active_offers_df.get("market_value"), errors="coerce")
    if "player_id" in active_offers_df.columns:
        active_offers_df["player_id"] = pd.to_numeric(active_offers_df["player_id"], errors="coerce")

    market_index = _build_market_index(working_market_df)
    action_rows = []
    for offer_row in active_offers_df.to_dict(orient="records"):
        market_match = _find_market_match(offer_row, market_index)
        action = _evaluate_active_offer(offer_row, market_match)
        action_rows.append(action)

    _apply_active_offer_actions_to_market(working_market_df, action_rows)

    management_summary = _build_management_summary(
        own_budget=own_budget,
        active_offer_amount_total=float(offer_stats.get("active_offer_amount_total", 0) or 0),
        overbid_pressure_level=offer_stats.get("overbid_pressure_level", "low"),
        suggested_markup_pct=float(offer_stats.get("suggested_markup_pct", 0) or 0),
        recent_outbid_count_14d=int(offer_stats.get("recent_outbid_count_14d", 0) or 0),
        avg_outbid_gap=float(offer_stats.get("avg_outbid_gap", 0) or 0),
        avg_outbid_gap_pct=float(offer_stats.get("avg_outbid_gap_pct", 0) or 0),
        active_offer_actions=action_rows,
    )

    return working_market_df, {
        "management_summary": management_summary,
        "active_offer_actions": action_rows,
        "recent_outbid": recent_outbid,
        "validation_notes": management_summary["validation_notes"],
    }


def _ensure_active_offer_columns(market_df):
    defaults = {
        "has_active_offer": False,
        "active_offer_amount": pd.NA,
        "active_offer_expires_at": None,
        "active_offer_decision": None,
        "active_offer_recommended_new_bid": pd.NA,
        "active_offer_reason": None,
    }
    for column, default_value in defaults.items():
        if column not in market_df.columns:
            market_df[column] = default_value


def _build_market_index(market_df):
    market_lookup_by_id = {}
    market_lookup_by_name = {}

    player_ids = None
    if "player_id" in market_df.columns:
        player_ids = pd.to_numeric(market_df["player_id"], errors="coerce")

    for index, (_, row) in enumerate(market_df.iterrows()):
        row_data = row.to_dict()
        row_data["_market_index"] = row.name
        row_data["_market_position"] = index

        if player_ids is not None and pd.notna(player_ids.iloc[index]):
            market_lookup_by_id[int(player_ids.iloc[index])] = row_data

        player_name = _extract_market_player_name(row)
        if player_name:
            market_lookup_by_name[_normalize_name(player_name)] = row_data

    return {
        "by_id": market_lookup_by_id,
        "by_name": market_lookup_by_name,
    }


def _find_market_match(offer_row, market_index):
    player_id = offer_row.get("player_id")
    if player_id is not None and not pd.isna(player_id):
        player_id = int(float(player_id))
        if player_id in market_index["by_id"]:
            return market_index["by_id"][player_id]

    player_name = offer_row.get("player_name")
    if player_name:
        return market_index["by_name"].get(_normalize_name(player_name))

    return None


def _evaluate_active_offer(offer_row, market_match):
    player_name = offer_row.get("player_name") or "Unbekannt"
    offer_amount = _to_float(offer_row.get("offer_amount")) or 0.0
    fallback_market_value = _to_float(offer_row.get("market_value"))
    expires_at = offer_row.get("expires_at")

    if not market_match:
        return {
            "player_name": player_name,
            "player_id": _to_int(offer_row.get("player_id")),
            "current_offer_amount": round(offer_amount, 0),
            "market_value": round(fallback_market_value, 0) if fallback_market_value is not None else None,
            "competitive_bid_max": None,
            "recommended_bid_max": None,
            "recommended_action": "hold",
            "recommended_action_label": "halten",
            "recommended_new_bid": round(offer_amount, 0),
            "decision_reason": "no_live_market_context",
            "decision_reason_label": "Kein Live-Marktkontext gefunden, bestehendes Gebot vorerst halten.",
            "expires_at": expires_at,
            "match_found": False,
            "market_index": None,
        }

    market_value = _to_float(market_match.get("mv"))
    competitive_bid_max = _to_float(market_match.get("competitive_bid_max"))
    recommended_bid_max = _to_float(market_match.get("recommended_bid_max"))
    delta_prediction = _to_float(market_match.get("delta_prediction")) or 0.0
    priority_score = _to_float(market_match.get("priority_score")) or 0.0
    buy_action = str(market_match.get("buy_action") or "unknown")
    recent_bid_competition = str(market_match.get("recent_bid_competition") or "unknown")
    bid_strategy_note = str(market_match.get("bid_strategy_note") or "")
    personal_bid_feedback = str(market_match.get("personal_bid_feedback") or "")
    asset_role = str(market_match.get("asset_role") or "")

    effective_market_value = market_value if market_value is not None else fallback_market_value
    effective_competitive_bid_max = competitive_bid_max if competitive_bid_max is not None else offer_amount
    effective_recommended_bid_max = recommended_bid_max if recommended_bid_max is not None else offer_amount
    raise_threshold = max(
        MIN_ACTIVE_OFFER_RAISE_EUR,
        (effective_market_value or offer_amount or 0) * MIN_ACTIVE_OFFER_RAISE_PCT,
    )
    desired_bid = max(offer_amount, effective_competitive_bid_max)

    if effective_competitive_bid_max + raise_threshold < offer_amount:
        recommended_action = "abort"
        recommended_new_bid = None
        decision_reason = "current_bid_above_disciplined_max"
        decision_reason_label = "Dein aktuelles Gebot liegt bereits klar ueber der disziplinierten Obergrenze."
    elif buy_action == "pass" or delta_prediction <= 0:
        recommended_action = "abort"
        recommended_new_bid = None
        decision_reason = "negative_edge_or_pass_signal"
        decision_reason_label = "Das Modell sieht hier aktuell keinen sauberen Kauf-Edge mehr."
    elif "avoid_price_war" in bid_strategy_note and offer_amount >= effective_competitive_bid_max - raise_threshold:
        recommended_action = "abort"
        recommended_new_bid = None
        decision_reason = "price_war_risk"
        decision_reason_label = "Die Historie spricht eher fuer einen unprofitablen Preiskrieg."
    elif desired_bid - offer_amount >= raise_threshold and buy_action in {"buy_now", "watchlist"}:
        recommended_action = "raise_small"
        recommended_new_bid = round(desired_bid, 0)
        decision_reason = "competitive_headroom_available"
        if personal_bid_feedback != "no_personal_adjustment":
            decision_reason_label = "Leicht anheben: Marktlogik und deine juengste Overbid-Historie geben noch Spielraum."
        elif recent_bid_competition == "high":
            decision_reason_label = "Leicht anheben: Das Profil ist umkaempft und dein aktuelles Gebot liegt unter dem Wettbewerbsniveau."
        else:
            decision_reason_label = "Leicht anheben: Innerhalb der disziplinierten Maximalgrenze ist noch Spielraum."
    else:
        recommended_action = "hold"
        recommended_new_bid = round(offer_amount, 0)
        decision_reason = "current_bid_within_model_range"
        decision_reason_label = "Gebot halten: Dein aktuelles Niveau liegt bereits im vertretbaren Zielkorridor."

    return {
        "player_name": player_name,
        "player_id": _to_int(offer_row.get("player_id")),
        "current_offer_amount": round(offer_amount, 0),
        "market_value": round(effective_market_value, 0) if effective_market_value is not None else None,
        "competitive_bid_max": round(effective_competitive_bid_max, 0) if effective_competitive_bid_max is not None else None,
        "recommended_bid_max": round(effective_recommended_bid_max, 0) if effective_recommended_bid_max is not None else None,
        "recommended_action": recommended_action,
        "recommended_action_label": _action_label(recommended_action),
        "recommended_new_bid": recommended_new_bid,
        "decision_reason": decision_reason,
        "decision_reason_label": decision_reason_label,
        "expires_at": expires_at,
        "match_found": True,
        "market_index": market_match.get("_market_index"),
        "priority_score": round(priority_score, 2),
        "buy_action": buy_action,
        "recent_bid_competition": recent_bid_competition,
        "asset_role": asset_role,
    }


def _apply_active_offer_actions_to_market(market_df, action_rows):
    for action in action_rows:
        market_index = action.get("market_index")
        if market_index is None or market_index not in market_df.index:
            continue

        market_df.at[market_index, "has_active_offer"] = True
        market_df.at[market_index, "active_offer_amount"] = action.get("current_offer_amount")
        market_df.at[market_index, "active_offer_expires_at"] = action.get("expires_at")
        market_df.at[market_index, "active_offer_decision"] = action.get("recommended_action")
        market_df.at[market_index, "active_offer_recommended_new_bid"] = action.get("recommended_new_bid")
        market_df.at[market_index, "active_offer_reason"] = action.get("decision_reason")


def _build_management_summary(
    own_budget,
    active_offer_amount_total,
    overbid_pressure_level,
    suggested_markup_pct,
    recent_outbid_count_14d,
    avg_outbid_gap,
    avg_outbid_gap_pct,
    active_offer_actions,
):
    effective_cash_after_active_offers = float(own_budget) - float(active_offer_amount_total)
    action_counts = {
        "hold": sum(1 for item in active_offer_actions if item.get("recommended_action") == "hold"),
        "raise_small": sum(1 for item in active_offer_actions if item.get("recommended_action") == "raise_small"),
        "abort": sum(1 for item in active_offer_actions if item.get("recommended_action") == "abort"),
    }
    unmatched_offers = sum(1 for item in active_offer_actions if not item.get("match_found"))

    validation_notes = []
    if active_offer_amount_total > own_budget:
        validation_notes.append("Aktive Gebote binden mehr Kapital als aktuell als Budget ausgewiesen ist.")
    if unmatched_offers > 0:
        validation_notes.append("Mindestens ein aktives Gebot konnte keinem Live-Marktspieler zugeordnet werden.")
    if not validation_notes:
        validation_notes.append("Keine offensichtlichen Strategie-Konflikte erkannt.")

    return {
        "own_budget": round(float(own_budget), 2),
        "active_offer_amount_total": round(float(active_offer_amount_total), 2),
        "effective_cash_after_active_offers": round(effective_cash_after_active_offers, 2),
        "overbid_pressure_level": overbid_pressure_level,
        "suggested_markup_pct": round(float(suggested_markup_pct), 4),
        "recent_outbid_count_14d": int(recent_outbid_count_14d),
        "avg_outbid_gap": round(float(avg_outbid_gap), 2),
        "avg_outbid_gap_pct": round(float(avg_outbid_gap_pct), 4),
        "active_offer_count": len(active_offer_actions),
        "unmatched_active_offer_count": unmatched_offers,
        "action_counts": action_counts,
        "validation_notes": validation_notes,
    }


def _extract_market_player_name(row):
    first_name = str(row.get("first_name", "") or "").strip()
    last_name = str(row.get("last_name", "") or "").strip()
    full_name = " ".join(part for part in [first_name, last_name] if part)
    return full_name or str(row.get("player_name", "") or "").strip()


def _normalize_name(value):
    return " ".join(str(value or "").strip().lower().split())


def _action_label(action):
    mapping = {
        "hold": "halten",
        "raise_small": "leicht erhoehen",
        "abort": "abbrechen",
    }
    return mapping.get(action, action)


def _to_float(value):
    if value is None or pd.isna(value):
        return None
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric_value):
        return None
    return numeric_value


def _to_int(value):
    numeric_value = _to_float(value)
    if numeric_value is None:
        return None
    return int(numeric_value)
