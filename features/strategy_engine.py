from __future__ import annotations

import math

import numpy as np
import pandas as pd


MIN_ACTIVE_OFFER_RAISE_EUR = 25_000
MIN_ACTIVE_OFFER_RAISE_PCT = 0.005
MAX_SQUAD_SIZE = 17
MAX_PLAYERS_PER_TEAM = 3
POSITION_LABELS = {
    1: "GK",
    2: "DEF",
    3: "MID",
    4: "ST",
    "1": "GK",
    "2": "DEF",
    "3": "MID",
    "4": "ST",
    "gk": "GK",
    "goalkeeper": "GK",
    "torwart": "GK",
    "def": "DEF",
    "abwehr": "DEF",
    "mid": "MID",
    "mittelfeld": "MID",
    "st": "ST",
    "striker": "ST",
    "sturm": "ST",
}
MIN_POSITION_COUNTS = {
    "GK": 1,
    "DEF": 3,
    "MID": 3,
    "ST": 2,
}
POSITION_NEED_PRIORITY_BOOST = {
    "high": 18.0,
    "medium": 10.0,
    "low": 0.0,
}
POSITION_NEED_IMPORTANCE = {
    "GK": 0,
    "DEF": 1,
    "MID": 2,
    "ST": 3,
}
TEAM_AVAILABILITY_MARKET_PENALTY = {
    "stable": 0.0,
    "watch": -2.5,
    "depleted": -6.0,
}
TEAM_AVAILABILITY_SQUAD_PRESSURE = {
    "stable": 0.0,
    "watch": 2.0,
    "depleted": 5.0,
}


def apply_team_availability_context(market_df, squad_df):
    """Translate team-level availability context into deterministic market and squad adjustments."""

    working_market_df = market_df.copy()
    working_squad_df = squad_df.copy()
    _ensure_team_availability_columns(working_market_df)
    _ensure_team_availability_columns(working_squad_df)

    if not working_market_df.empty:
        market_adjustment = _calculate_market_availability_adjustment(
            level_series=working_market_df["team_availability_level"],
            starter_series=working_market_df.get("s_11_prob", pd.Series(index=working_market_df.index, dtype=float)),
            role_series=working_market_df.get("asset_role", pd.Series("", index=working_market_df.index)),
            missing_series=working_market_df["team_missing_count"],
            questionable_series=working_market_df["team_questionable_count"],
        )
        current_priority = pd.to_numeric(working_market_df.get("priority_score"), errors="coerce").fillna(0)
        current_buy_action = working_market_df.get("buy_action", pd.Series("pass", index=working_market_df.index)).fillna("pass")
        delta_prediction = pd.to_numeric(working_market_df.get("delta_prediction"), errors="coerce").fillna(0)
        football_signal_score = pd.to_numeric(working_market_df.get("football_signal_score"), errors="coerce").fillna(0)

        working_market_df["team_availability_priority_adjustment"] = np.round(market_adjustment, 1)
        working_market_df["priority_score"] = np.round(current_priority + market_adjustment, 1)
        working_market_df["buy_action"] = np.select(
            [
                (market_adjustment <= -5.5) & current_buy_action.eq("buy_now"),
                (market_adjustment <= -7.5) & current_buy_action.eq("watchlist"),
                (market_adjustment >= 3.0) & current_buy_action.eq("watchlist") & (delta_prediction > 0) & (football_signal_score >= 58),
                (market_adjustment >= 5.0) & current_buy_action.eq("pass") & (delta_prediction > 0) & (football_signal_score >= 62),
            ],
            ["watchlist", "pass", "buy_now", "watchlist"],
            default=current_buy_action,
        )

    if not working_squad_df.empty:
        squad_adjustment = _calculate_squad_availability_adjustment(
            level_series=working_squad_df["team_availability_level"],
            starter_series=working_squad_df.get("s_11_prob", pd.Series(index=working_squad_df.index, dtype=float)),
            role_series=working_squad_df.get("squad_role", pd.Series("", index=working_squad_df.index)),
            missing_series=working_squad_df["team_missing_count"],
            questionable_series=working_squad_df["team_questionable_count"],
        )
        current_sell_priority = pd.to_numeric(working_squad_df.get("sell_priority_score"), errors="coerce").fillna(0)
        working_squad_df["team_availability_sell_adjustment"] = np.round(squad_adjustment, 1)
        working_squad_df["sell_priority_score"] = np.round(np.maximum(0, current_sell_priority + squad_adjustment), 1)

    summary = _build_team_availability_summary(working_market_df, working_squad_df)
    return working_market_df, working_squad_df, summary


def apply_squad_retention_context(squad_df, market_df):
    """Protect strong, hard-to-replace squad players when the current market is thin."""

    if squad_df.empty:
        return squad_df.copy(), _build_squad_management_summary("unknown", 0, 0)

    working_squad_df = squad_df.copy()
    _ensure_squad_context_columns(working_squad_df)

    market_scarcity_level, strong_replacement_count, replacement_pool_size = _evaluate_market_scarcity(market_df)
    scarcity_discount = {"high": 18.0, "medium": 9.0, "low": 0.0}.get(market_scarcity_level, 0.0)

    starter_probability = pd.to_numeric(working_squad_df.get("s_11_prob"), errors="coerce").fillna(55)
    football_signal_score = pd.to_numeric(working_squad_df.get("football_signal_score"), errors="coerce").fillna(50)
    delta_prediction = pd.to_numeric(working_squad_df.get("delta_prediction"), errors="coerce").fillna(0)
    market_value = pd.to_numeric(working_squad_df.get("mv"), errors="coerce").fillna(0)
    original_sell_priority = pd.to_numeric(working_squad_df.get("sell_priority_score"), errors="coerce").fillna(0)

    keep_quality_mask = (
        ((starter_probability >= 68) & (football_signal_score >= 60))
        | ((starter_probability >= 74) & (market_value >= 8_000_000))
        | ((football_signal_score >= 68) & (market_value >= 12_000_000))
    )
    stable_value_mask = delta_prediction >= -180_000
    protect_mask = keep_quality_mask & stable_value_mask & (scarcity_discount > 0)

    working_squad_df["sell_priority_score"] = np.where(
        protect_mask,
        np.maximum(0, original_sell_priority - scarcity_discount),
        original_sell_priority,
    )
    working_squad_df["sell_priority_score"] = np.round(working_squad_df["sell_priority_score"], 1)

    working_squad_df["retention_priority"] = np.where(
        protect_mask,
        np.round((starter_probability * 0.55) + (football_signal_score * 0.45), 1),
        0.0,
    )
    working_squad_df["market_scarcity_level"] = market_scarcity_level
    working_squad_df["replacement_pool_size"] = replacement_pool_size
    working_squad_df["strong_replacement_count"] = strong_replacement_count
    working_squad_df["squad_strategy_note"] = np.where(
        protect_mask,
        np.where(
            market_scarcity_level == "high",
            "keep_due_to_thin_market",
            "lean_keep_due_to_market_scarcity",
        ),
        "model_only",
    )

    working_squad_df["squad_role"] = np.select(
        [
            protect_mask,
            working_squad_df["sell_priority_score"] >= 60,
        ],
        ["core_starter", "sell_candidate"],
        default=np.where(
            (starter_probability >= 72) & (football_signal_score >= 65) & (delta_prediction >= -150000),
            "core_starter",
            "rotation_hold",
        ),
    )
    working_squad_df["squad_action"] = np.select(
        [
            protect_mask,
            working_squad_df["sell_priority_score"] >= 60,
            working_squad_df["sell_priority_score"] >= 40,
        ],
        ["hold", "sell", "monitor"],
        default="hold",
    )

    protected_count = int(protect_mask.sum())
    squad_management_summary = _build_squad_management_summary(
        market_scarcity_level,
        strong_replacement_count,
        protected_count,
    )

    return working_squad_df.sort_values(["sell_priority_score", "delta_prediction"], ascending=[False, True]), squad_management_summary


def apply_roster_need_context(squad_df, market_df):
    """Boost market priorities for positions that are currently thin in the squad."""

    if market_df.empty:
        return market_df.copy(), _build_roster_need_summary([], "none", "none", 0)

    working_market_df = market_df.copy()
    _ensure_market_need_columns(working_market_df)

    squad_counts = _count_positions(squad_df)
    market_depth = _count_actionable_market_positions(working_market_df)
    position_needs = _build_position_needs(squad_counts, market_depth)

    if not position_needs:
        return working_market_df.sort_values(["priority_score", "delta_prediction", "hours_to_exp"], ascending=[False, False, True]), _build_roster_need_summary([], "none", "none", 0)

    need_by_position = {item["position_label"]: item for item in position_needs}
    normalized_positions = working_market_df.get("position", pd.Series(index=working_market_df.index)).map(_normalize_position_label)
    current_priority_score = pd.to_numeric(working_market_df.get("priority_score"), errors="coerce").fillna(0)
    football_signal_score = pd.to_numeric(working_market_df.get("football_signal_score"), errors="coerce").fillna(0)
    delta_prediction = pd.to_numeric(working_market_df.get("delta_prediction"), errors="coerce").fillna(0)
    expiring_today = working_market_df.get("expiring_today", pd.Series(False, index=working_market_df.index)).fillna(False)
    current_buy_action = working_market_df.get("buy_action", pd.Series("pass", index=working_market_df.index)).fillna("pass")

    working_market_df["position_label"] = normalized_positions
    working_market_df["roster_need_level"] = normalized_positions.map(
        lambda value: need_by_position.get(value, {}).get("need_level", "none")
    )
    working_market_df["roster_need_priority_boost"] = normalized_positions.map(
        lambda value: need_by_position.get(value, {}).get("priority_boost", 0.0)
    ).fillna(0.0)
    working_market_df["roster_need_note"] = normalized_positions.map(
        lambda value: need_by_position.get(value, {}).get("need_note", "")
    ).fillna("")

    working_market_df["priority_score"] = np.round(
        current_priority_score + working_market_df["roster_need_priority_boost"],
        1,
    )

    high_need_mask = working_market_df["roster_need_level"].eq("high")
    medium_need_mask = working_market_df["roster_need_level"].eq("medium")
    can_be_watchlist = football_signal_score >= 48
    can_be_buy_now = football_signal_score >= 58

    working_market_df["buy_action"] = np.select(
        [
            high_need_mask & expiring_today & can_be_buy_now & (delta_prediction >= -120_000),
            high_need_mask & can_be_watchlist & (delta_prediction >= -180_000),
            medium_need_mask & current_buy_action.eq("pass") & can_be_watchlist & (delta_prediction >= -100_000),
        ],
        ["buy_now", "watchlist", "watchlist"],
        default=current_buy_action,
    )

    primary_need = position_needs[0]
    roster_need_summary = _build_roster_need_summary(
        position_needs,
        primary_need.get("position_label", "none"),
        primary_need.get("need_level", "none"),
        sum(1 for item in position_needs if item.get("need_level") in {"high", "medium"}),
    )

    return working_market_df.sort_values(["priority_score", "delta_prediction", "hours_to_exp"], ascending=[False, False, True]), roster_need_summary


def apply_deterministic_buy_gates(market_df, squad_df, manager_budgets_df, own_username, strategy_context=None):
    """Apply hard pre-AI buy constraints for cash, club limits, squad slots, and active offers."""

    if market_df.empty:
        return market_df.copy(), {
            "blocked_count": 0,
            "managed_existing_offer_count": 0,
            "club_limit_blocks": 0,
            "budget_blocks": 0,
            "sell_first_flags": 0,
            "available_cash": 0.0,
            "available_budget": 0.0,
            "squad_size": int(len(squad_df)),
            "squad_limit": MAX_SQUAD_SIZE,
        }

    working_market_df = market_df.copy()
    _ensure_buy_gate_columns(working_market_df)

    strategy_context = strategy_context or {}
    management_summary = strategy_context.get("management_summary", {})
    own_budget_row = manager_budgets_df[manager_budgets_df["User"] == own_username] if manager_budgets_df is not None and "User" in manager_budgets_df.columns else pd.DataFrame()
    spendable_without_debt = _to_float(own_budget_row["Spendable Without Debt"].iloc[0]) if not own_budget_row.empty and "Spendable Without Debt" in own_budget_row.columns else None
    available_budget = _to_float(own_budget_row["Available Budget"].iloc[0]) if not own_budget_row.empty and "Available Budget" in own_budget_row.columns else None
    effective_cash_after_active_offers = _to_float(management_summary.get("effective_cash_after_active_offers"))

    available_cash = spendable_without_debt
    if available_cash is None:
        available_cash = effective_cash_after_active_offers
    if available_cash is None:
        available_cash = 0.0
    if available_budget is None:
        available_budget = available_cash

    squad_size = int(len(squad_df))
    squad_full = squad_size >= MAX_SQUAD_SIZE
    squad_sell_candidates = int((squad_df.get("squad_action", pd.Series(index=squad_df.index, dtype=object)).fillna("hold") == "sell").sum()) if squad_df is not None else 0

    team_counts = squad_df.get("team_name", pd.Series(index=squad_df.index, dtype=object)).fillna("unknown").astype(str).value_counts().to_dict() if squad_df is not None else {}
    reserved_team_counts = {}
    for item in strategy_context.get("active_offer_actions", []):
        if item.get("recommended_action") not in {"hold", "raise_small"}:
            continue
        market_index = item.get("market_index")
        if market_index is None or market_index not in working_market_df.index:
            continue
        team_name = str(working_market_df.at[market_index, "team_name"] or "unknown")
        reserved_team_counts[team_name] = reserved_team_counts.get(team_name, 0) + 1

    current_buy_action = working_market_df.get("buy_action", pd.Series("pass", index=working_market_df.index)).fillna("pass")
    actionable_buy_mask = current_buy_action.isin(["buy_now", "watchlist"])
    competitive_bid_max = pd.to_numeric(working_market_df.get("competitive_bid_max"), errors="coerce")
    recommended_bid_max = pd.to_numeric(working_market_df.get("recommended_bid_max"), errors="coerce")
    market_value = pd.to_numeric(working_market_df.get("mv"), errors="coerce")
    effective_bid_cap = competitive_bid_max.fillna(recommended_bid_max).fillna(market_value)
    minimum_entry_price = market_value.fillna(recommended_bid_max).fillna(effective_bid_cap)

    gate_status = pd.Series("clear", index=working_market_df.index, dtype=object)
    gate_reason = pd.Series("", index=working_market_df.index, dtype=object)

    active_offer_decision = working_market_df.get("active_offer_decision", pd.Series(index=working_market_df.index, dtype=object)).fillna("")
    active_offer_mask = active_offer_decision.ne("")
    abort_offer_mask = active_offer_decision.eq("abort")
    managed_offer_mask = active_offer_mask & ~abort_offer_mask

    gate_status.loc[abort_offer_mask] = "blocked"
    gate_reason.loc[abort_offer_mask] = "active_offer_abort"
    gate_status.loc[managed_offer_mask] = "managed_existing_offer"
    gate_reason.loc[managed_offer_mask] = "manage_existing_offer"

    club_counts_after_buy = []
    club_limit_mask = []
    for row_index, row in working_market_df.iterrows():
        team_name = str(row.get("team_name") or "unknown")
        reserved_count = reserved_team_counts.get(team_name, 0)
        own_count = int(team_counts.get(team_name, 0))
        has_reserved_same_player = bool(row.get("has_active_offer")) and active_offer_decision.get(row_index, "") in {"hold", "raise_small"}
        projected_count = own_count + reserved_count + (0 if has_reserved_same_player else 1)
        club_counts_after_buy.append(projected_count)
        club_limit_mask.append(projected_count > MAX_PLAYERS_PER_TEAM)

    club_counts_after_buy = pd.Series(club_counts_after_buy, index=working_market_df.index)
    club_limit_mask = pd.Series(club_limit_mask, index=working_market_df.index)
    hard_club_limit_mask = actionable_buy_mask & club_limit_mask & gate_status.eq("clear")
    gate_status.loc[hard_club_limit_mask] = "blocked"
    gate_reason.loc[hard_club_limit_mask] = "club_limit_reached"

    no_budget_anyway_mask = actionable_buy_mask & gate_status.eq("clear") & ((minimum_entry_price > available_budget) | minimum_entry_price.isna())
    gate_status.loc[no_budget_anyway_mask] = "blocked"
    gate_reason.loc[no_budget_anyway_mask] = "above_total_budget_limit"

    sell_first_mask = actionable_buy_mask & gate_status.eq("clear") & ((minimum_entry_price > available_cash) | squad_full)
    gate_status.loc[sell_first_mask] = "sell_first"
    gate_reason.loc[sell_first_mask] = np.where(
        squad_full & (minimum_entry_price > available_cash),
        "sell_first_cash_and_slot_required",
        np.where(squad_full, "sell_first_squad_full", "sell_first_insufficient_cash"),
    )

    gated_buy_action = current_buy_action.copy()
    gated_buy_action.loc[gate_status.isin(["blocked", "managed_existing_offer"])] = "pass"
    gated_buy_action.loc[sell_first_mask & current_buy_action.eq("buy_now")] = "watchlist"

    working_market_df["buy_action"] = gated_buy_action
    working_market_df["buy_gate_status"] = gate_status
    working_market_df["buy_gate_reason"] = gate_reason
    working_market_df["buy_gate_detail"] = gate_reason.map(_build_buy_gate_detail)
    working_market_df["effective_bid_cap"] = np.round(np.minimum(effective_bid_cap.fillna(0), available_budget), 0)
    working_market_df["minimum_entry_price"] = np.round(minimum_entry_price, 0)
    working_market_df["club_count_after_buy"] = club_counts_after_buy
    working_market_df["squad_size_after_buy"] = squad_size + 1

    summary = {
        "blocked_count": int(gate_status.eq("blocked").sum()),
        "managed_existing_offer_count": int(gate_status.eq("managed_existing_offer").sum()),
        "club_limit_blocks": int(hard_club_limit_mask.sum()),
        "budget_blocks": int(no_budget_anyway_mask.sum()),
        "sell_first_flags": int(sell_first_mask.sum()),
        "available_cash": round(float(available_cash), 2),
        "available_budget": round(float(available_budget), 2),
        "squad_size": squad_size,
        "squad_limit": MAX_SQUAD_SIZE,
        "sell_candidates": squad_sell_candidates,
    }
    return working_market_df.sort_values(["priority_score", "delta_prediction", "hours_to_exp"], ascending=[False, False, True]), summary


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


def _ensure_market_need_columns(market_df):
    defaults = {
        "position_label": None,
        "roster_need_level": "none",
        "roster_need_priority_boost": 0.0,
        "roster_need_note": "",
    }
    for column, default_value in defaults.items():
        if column not in market_df.columns:
            market_df[column] = default_value


def _ensure_buy_gate_columns(market_df):
    defaults = {
        "buy_gate_status": "clear",
        "buy_gate_reason": "",
        "buy_gate_detail": "",
        "effective_bid_cap": pd.NA,
        "minimum_entry_price": pd.NA,
        "club_count_after_buy": pd.NA,
        "squad_size_after_buy": pd.NA,
    }
    for column, default_value in defaults.items():
        if column not in market_df.columns:
            market_df[column] = default_value


def _ensure_squad_context_columns(squad_df):
    defaults = {
        "retention_priority": 0.0,
        "market_scarcity_level": "unknown",
        "replacement_pool_size": 0,
        "strong_replacement_count": 0,
        "squad_strategy_note": "model_only",
    }
    for column, default_value in defaults.items():
        if column not in squad_df.columns:
            squad_df[column] = default_value


def _ensure_team_availability_columns(df):
    defaults = {
        "team_missing_count": 0,
        "team_questionable_count": 0,
        "team_availability_score": 100.0,
        "team_availability_level": "stable",
        "team_availability_note": "Keine API-Football Hinweise vorhanden",
        "team_availability_priority_adjustment": 0.0,
        "team_availability_sell_adjustment": 0.0,
    }
    for column, default_value in defaults.items():
        if column not in df.columns:
            df[column] = default_value


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


def _evaluate_market_scarcity(market_df):
    if market_df is None or market_df.empty:
        return "high", 0, 0

    working_market_df = market_df.copy()
    priority_score = pd.to_numeric(working_market_df.get("priority_score"), errors="coerce").fillna(0)
    football_signal_score = pd.to_numeric(working_market_df.get("football_signal_score"), errors="coerce").fillna(0)
    delta_prediction = pd.to_numeric(working_market_df.get("delta_prediction"), errors="coerce").fillna(0)
    asset_role = working_market_df.get("asset_role", pd.Series("", index=working_market_df.index)).fillna("")
    buy_action = working_market_df.get("buy_action", pd.Series("pass", index=working_market_df.index)).fillna("pass")

    replacement_mask = (
        buy_action.isin(["buy_now", "watchlist"])
        & asset_role.isin(["core_starter", "medium_term_hold"])
        & (delta_prediction > 0)
        & (football_signal_score >= 55)
    )
    strong_replacement_mask = replacement_mask & (priority_score >= 62)

    replacement_pool_size = int(replacement_mask.sum())
    strong_replacement_count = int(strong_replacement_mask.sum())

    if strong_replacement_count <= 2 or replacement_pool_size <= 4:
        return "high", strong_replacement_count, replacement_pool_size
    if strong_replacement_count <= 5 or replacement_pool_size <= 8:
        return "medium", strong_replacement_count, replacement_pool_size
    return "low", strong_replacement_count, replacement_pool_size


def _build_squad_management_summary(market_scarcity_level, strong_replacement_count, protected_player_count):
    return {
        "market_scarcity_level": market_scarcity_level,
        "strong_replacement_count": int(strong_replacement_count),
        "protected_player_count": int(protected_player_count),
    }


def _count_positions(df):
    if df is None or df.empty or "position" not in df.columns:
        return {}

    normalized_positions = df["position"].map(_normalize_position_label)
    counts = normalized_positions.value_counts(dropna=True).to_dict()
    return {str(key): int(value) for key, value in counts.items()}


def _count_actionable_market_positions(market_df):
    if market_df is None or market_df.empty:
        return {}

    working_market_df = market_df.copy()
    normalized_positions = working_market_df.get("position", pd.Series(index=working_market_df.index)).map(_normalize_position_label)
    buy_action = working_market_df.get("buy_action", pd.Series("pass", index=working_market_df.index)).fillna("pass")
    football_signal_score = pd.to_numeric(working_market_df.get("football_signal_score"), errors="coerce").fillna(0)
    actionable_mask = buy_action.ne("pass") | (football_signal_score >= 50)
    counts = normalized_positions[actionable_mask].value_counts(dropna=True).to_dict()
    return {str(key): int(value) for key, value in counts.items()}


def _build_position_needs(squad_counts, market_depth):
    position_needs = []

    for position_label, minimum_count in MIN_POSITION_COUNTS.items():
        current_count = int(squad_counts.get(position_label, 0))
        market_option_count = int(market_depth.get(position_label, 0))
        missing_count = max(0, minimum_count - current_count)
        need_level = "low"

        if missing_count > 0:
            need_level = "high" if market_option_count <= 2 else "medium"
        elif position_label == "GK" and current_count == 1 and market_option_count <= 2:
            need_level = "medium"

        if need_level == "low":
            continue

        priority_boost = _determine_position_need_boost(position_label, need_level, current_count)

        position_needs.append(
            {
                "position_label": position_label,
                "current_count": current_count,
                "minimum_count": minimum_count,
                "missing_count": missing_count,
                "is_structural_gap": missing_count > 0,
                "market_option_count": market_option_count,
                "need_level": need_level,
                "priority_boost": priority_boost,
                "need_note": _build_position_need_note(position_label, current_count, market_option_count, need_level),
            }
        )

    position_needs.sort(
        key=lambda item: (
            0 if item["need_level"] == "high" else 1,
            POSITION_NEED_IMPORTANCE.get(item["position_label"], 99),
            -item["priority_boost"],
            -item["missing_count"],
            item["market_option_count"],
        )
    )
    return position_needs


def _build_roster_need_summary(position_needs, primary_need_position, primary_need_level, urgent_need_count):
    primary_need = position_needs[0] if position_needs else {}
    return {
        "primary_need_position": primary_need_position,
        "primary_need_level": primary_need_level,
        "urgent_need_count": int(urgent_need_count),
        "structural_gap_count": int(sum(1 for item in position_needs if item.get("is_structural_gap"))),
        "primary_need_is_structural_gap": bool(primary_need.get("is_structural_gap", False)),
        "position_needs": position_needs,
    }


def _build_position_need_note(position_label, current_count, market_option_count, need_level):
    if position_label == "GK" and current_count == 0:
        return "Torwart fehlt im Kader, verfuegbare Optionen frueh priorisieren."
    if position_label == "GK" and current_count == 1:
        return "Torwartposition ist besetzt, aber aktuell ohne Ersatzoption im Kader. Backup nicht zu spaet angehen."
    if need_level == "high":
        return f"Position {position_label} ist duenn besetzt und der Markt bietet wenig Alternativen."
    return f"Position {position_label} sollte zeitnah verstaerkt werden, bevor der Markt noch duenner wird."


def _determine_position_need_boost(position_label, need_level, current_count):
    base_boost = POSITION_NEED_PRIORITY_BOOST[need_level]

    if position_label == "GK" and current_count == 0:
        return base_boost + 18.0
    if position_label == "GK" and current_count == 1 and need_level == "medium":
        return base_boost + 4.0
    return base_boost


def _normalize_position_label(value):
    if value is None or pd.isna(value):
        return None
    normalized_value = str(value).strip().lower()
    return POSITION_LABELS.get(value) or POSITION_LABELS.get(normalized_value)


def _calculate_market_availability_adjustment(level_series, starter_series, role_series, missing_series, questionable_series):
    starter_score = pd.to_numeric(starter_series, errors="coerce").fillna(55)
    missing_count = pd.to_numeric(missing_series, errors="coerce").fillna(0)
    questionable_count = pd.to_numeric(questionable_series, errors="coerce").fillna(0)
    role_values = role_series.fillna("").astype(str)
    level_values = level_series.fillna("stable").astype(str)

    base_adjustment = level_values.map(TEAM_AVAILABILITY_MARKET_PENALTY).fillna(0.0).astype(float)
    starter_bonus = np.where((level_values != "stable") & (starter_score >= 72), 3.0, 0.0)
    starter_penalty = np.where((level_values != "stable") & (starter_score < 55), -2.0, 0.0)
    hold_penalty = np.where((level_values == "depleted") & role_values.eq("medium_term_hold"), -1.0, 0.0)
    missing_pressure = np.where(missing_count >= 5, -1.0, 0.0)
    questionable_pressure = np.where(questionable_count >= 3, -0.5, 0.0)
    return base_adjustment + starter_bonus + starter_penalty + hold_penalty + missing_pressure + questionable_pressure


def _calculate_squad_availability_adjustment(level_series, starter_series, role_series, missing_series, questionable_series):
    starter_score = pd.to_numeric(starter_series, errors="coerce").fillna(55)
    missing_count = pd.to_numeric(missing_series, errors="coerce").fillna(0)
    questionable_count = pd.to_numeric(questionable_series, errors="coerce").fillna(0)
    role_values = role_series.fillna("").astype(str)
    level_values = level_series.fillna("stable").astype(str)

    base_pressure = level_values.map(TEAM_AVAILABILITY_SQUAD_PRESSURE).fillna(0.0).astype(float)
    core_relief = np.where(
        (level_values == "depleted") & ((starter_score >= 72) | role_values.eq("core_starter")),
        -7.0,
        np.where(
            (level_values == "watch") & ((starter_score >= 72) | role_values.eq("core_starter")),
            -3.0,
            0.0,
        ),
    )
    fringe_pressure = np.where((level_values != "stable") & (starter_score < 55), 3.0, 0.0)
    depleted_fringe_pressure = np.where((level_values == "depleted") & role_values.eq("rotation_hold"), 2.0, 0.0)
    missing_pressure = np.where(missing_count >= 5, 1.0, 0.0)
    questionable_relief = np.where((questionable_count >= 3) & (starter_score >= 70), -1.0, 0.0)
    return base_pressure + core_relief + fringe_pressure + depleted_fringe_pressure + missing_pressure + questionable_relief


def _build_team_availability_summary(market_df, squad_df):
    market_adjustments = pd.to_numeric(market_df.get("team_availability_priority_adjustment"), errors="coerce").fillna(0) if market_df is not None else pd.Series(dtype=float)
    squad_adjustments = pd.to_numeric(squad_df.get("team_availability_sell_adjustment"), errors="coerce").fillna(0) if squad_df is not None else pd.Series(dtype=float)
    market_levels = market_df.get("team_availability_level", pd.Series(dtype=object)).fillna("stable") if market_df is not None else pd.Series(dtype=object)
    squad_levels = squad_df.get("team_availability_level", pd.Series(dtype=object)).fillna("stable") if squad_df is not None else pd.Series(dtype=object)

    return {
        "market_players_with_adjustment": int((market_adjustments != 0).sum()),
        "market_caution_count": int((market_adjustments < 0).sum()),
        "market_opportunity_count": int((market_adjustments > 0).sum()),
        "squad_sell_pressure_up": int((squad_adjustments > 0).sum()),
        "squad_sell_pressure_down": int((squad_adjustments < 0).sum()),
        "market_depleted_teams": int((market_levels == "depleted").sum()),
        "squad_depleted_teams": int((squad_levels == "depleted").sum()),
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


def _build_buy_gate_detail(reason):
    mapping = {
        "active_offer_abort": "Bestehendes Gebot soll laut System aktiv beendet werden.",
        "manage_existing_offer": "Fuer diesen Spieler existiert bereits ein aktives Gebot. Nur bestehendes Gebot managen.",
        "club_limit_reached": "Der Kauf wuerde das harte 3-Spieler-Limit fuer diesen Verein reissen.",
        "above_total_budget_limit": "Der Spieler liegt selbst mit Negativspielraum ausserhalb der harten Budgetgrenze.",
        "sell_first_cash_and_slot_required": "Vor dem Kauf muessen sowohl Cash als auch ein Kaderplatz freigemacht werden.",
        "sell_first_squad_full": "Vor dem Kauf muss zuerst ein Kaderplatz frei werden.",
        "sell_first_insufficient_cash": "Vor dem Kauf muss zuerst reales Cash freigemacht werden.",
    }
    return mapping.get(reason, "")


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
