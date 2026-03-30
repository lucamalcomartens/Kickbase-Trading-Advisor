from __future__ import annotations

import json
import sqlite3

import numpy as np
import pandas as pd


BUY_TRAINING_COLUMNS = [
    "purchase_timestamp",
    "player_id",
    "player_name",
    "team_name",
    "position",
    "purchase_price",
    "purchase_market_value",
    "purchase_premium_abs",
    "purchase_premium_pct",
    "snapshot_found",
    "snapshot_created_at",
    "snapshot_age_hours",
    "model_buy_action",
    "model_priority_score",
    "model_delta_prediction",
    "model_delta_percent",
    "model_football_signal_score",
    "model_asset_role",
    "model_recommended_bid_max",
    "model_competitive_bid_max",
    "model_recent_bid_competition",
    "model_bid_strategy_note",
    "model_roster_need_level",
    "model_team_availability_level",
    "model_buy_gate_status",
    "model_effective_bid_cap",
    "model_hours_to_exp",
    "model_expiring_today",
    "price_vs_recommended_abs",
    "price_vs_recommended_pct",
    "price_vs_competitive_abs",
    "price_vs_competitive_pct",
    "price_vs_effective_cap_abs",
    "price_vs_effective_cap_pct",
    "outcome_reference_value",
    "outcome_delta_eur",
    "outcome_delta_pct",
    "outcome_type",
    "held_days",
    "current_squad_role",
    "current_sell_priority_score",
    "signal_alignment",
    "signal_note",
    "buy_quality_label",
    "buy_quality_target",
    "training_eligible",
]


def build_buy_training_dataset(
    db_path,
    league_id,
    own_username,
    transfer_history_df=None,
    squad_df=None,
    lookback_days=180,
    min_open_hold_days=2,
    max_snapshot_age_hours=72,
):
    """Build a labeled buy-decision dataset from completed transfers and stored advisor snapshots."""

    working_history_df = _prepare_transfer_history(
        db_path=db_path,
        league_id=league_id,
        transfer_history_df=transfer_history_df,
        lookback_days=lookback_days,
    )
    if working_history_df.empty:
        return _empty_buy_training_dataset()

    own_buys_df = working_history_df[
        working_history_df["buyer"].fillna("").astype(str).eq(str(own_username))
    ].copy()
    if own_buys_df.empty:
        return _empty_buy_training_dataset()

    snapshot_cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=lookback_days)
    market_snapshot_index = _load_market_snapshot_index(db_path, league_id, snapshot_cutoff)
    current_squad_lookup = _build_current_squad_lookup(squad_df)
    if not current_squad_lookup:
        current_squad_lookup = _build_current_squad_lookup(
            _load_latest_squad_snapshot(db_path, league_id, own_username)
        )

    training_rows = []
    own_buys_df = own_buys_df.sort_values("timestamp", ascending=False).copy()
    own_buys_df["player_id"] = own_buys_df["player_id"].astype(int)

    for _, purchase_row in own_buys_df.iterrows():
        player_id = int(purchase_row["player_id"])
        player_history_df = working_history_df[working_history_df["player_id"] == player_id].sort_values("timestamp")
        later_sales_df = player_history_df[
            player_history_df["seller"].fillna("").astype(str).eq(str(own_username))
            & (player_history_df["timestamp"] > purchase_row["timestamp"])
        ]
        first_sale_row = later_sales_df.iloc[0].to_dict() if not later_sales_df.empty else None
        current_squad_row = current_squad_lookup.get(player_id)
        snapshot_match = _find_latest_snapshot_before_purchase(
            snapshot_index=market_snapshot_index,
            player_id=player_id,
            player_name=purchase_row.get("player_name"),
            purchase_time=purchase_row["timestamp"],
            max_snapshot_age_hours=max_snapshot_age_hours,
        )
        training_rows.append(
            _build_buy_training_row(
                purchase_row=purchase_row.to_dict(),
                sale_row=first_sale_row,
                current_squad_row=current_squad_row,
                snapshot_match=snapshot_match,
                min_open_hold_days=min_open_hold_days,
            )
        )

    if not training_rows:
        return _empty_buy_training_dataset()

    training_df = pd.DataFrame(training_rows)
    return training_df[BUY_TRAINING_COLUMNS].sort_values("purchase_timestamp", ascending=False).reset_index(drop=True)


def build_purchase_evaluation_summary(
    db_path,
    league_id,
    own_username,
    transfer_history_df=None,
    squad_df=None,
    lookback_days=21,
):
    """Summarize recent own buys for reports and prompt grounding."""

    training_df = build_buy_training_dataset(
        db_path=db_path,
        league_id=league_id,
        own_username=own_username,
        transfer_history_df=transfer_history_df,
        squad_df=squad_df,
        lookback_days=lookback_days,
    )
    if training_df.empty:
        return _empty_purchase_evaluation_summary()

    good_count = int((training_df["buy_quality_label"] == "good").sum())
    neutral_count = int((training_df["buy_quality_label"] == "neutral").sum())
    poor_count = int((training_df["buy_quality_label"] == "poor").sum())
    model_misaligned_count = int((training_df["signal_alignment"] == "misaligned").sum())
    realized_count = int((training_df["outcome_type"] == "realized").sum())
    open_count = int((training_df["outcome_type"] == "open").sum())

    recent_evaluations = training_df.head(8)[
        [
            "player_name",
            "purchase_price",
            "outcome_reference_value",
            "outcome_delta_eur",
            "buy_quality_label",
            "signal_alignment",
            "signal_note",
            "outcome_type",
            "held_days",
        ]
    ].copy()
    recent_evaluations = recent_evaluations.rename(
        columns={
            "purchase_price": "purchase_price",
            "outcome_reference_value": "benchmark_value",
            "outcome_delta_eur": "profit_delta",
            "buy_quality_label": "verdict",
            "outcome_type": "status_label",
        }
    )
    recent_evaluations["status_label"] = recent_evaluations["status_label"].map(
        {
            "realized": "bereits verkauft",
            "open": "noch im Kader",
            "unknown": "nicht mehr im Kader",
        }
    ).fillna("nicht mehr im Kader")

    return {
        "recent_purchase_count": int(len(training_df)),
        "good_count": good_count,
        "neutral_count": neutral_count,
        "poor_count": poor_count,
        "model_misaligned_count": model_misaligned_count,
        "realized_count": realized_count,
        "open_count": open_count,
        "training_eligible_count": int(training_df["training_eligible"].sum()),
        "learning_note": _build_purchase_learning_note(good_count, poor_count, model_misaligned_count),
        "recent_evaluations": recent_evaluations.where(pd.notna(recent_evaluations), None).to_dict(orient="records"),
    }


def summarize_buy_training_dataset(training_df):
    """Return compact metadata for dataset quality checks and documentation."""

    if training_df is None or training_df.empty:
        return {
            "row_count": 0,
            "eligible_row_count": 0,
            "good_count": 0,
            "neutral_count": 0,
            "poor_count": 0,
            "realized_count": 0,
            "open_count": 0,
            "snapshot_coverage_pct": 0.0,
        }

    row_count = int(len(training_df))
    return {
        "row_count": row_count,
        "eligible_row_count": int(training_df["training_eligible"].sum()),
        "good_count": int((training_df["buy_quality_label"] == "good").sum()),
        "neutral_count": int((training_df["buy_quality_label"] == "neutral").sum()),
        "poor_count": int((training_df["buy_quality_label"] == "poor").sum()),
        "realized_count": int((training_df["outcome_type"] == "realized").sum()),
        "open_count": int((training_df["outcome_type"] == "open").sum()),
        "snapshot_coverage_pct": round(float(training_df["snapshot_found"].mean() * 100), 2),
    }


def _prepare_transfer_history(db_path, league_id, transfer_history_df, lookback_days):
    if transfer_history_df is None:
        with sqlite3.connect(db_path) as conn:
            if not _table_exists(conn, "league_transfer_history"):
                return pd.DataFrame()
            history_df = pd.read_sql_query(
                """
                SELECT timestamp, buyer, seller, player_id, player_name, team_id, transfer_price
                FROM league_transfer_history
                WHERE league_id = ?
                """,
                conn,
                params=[league_id],
            )
    else:
        history_df = transfer_history_df.copy()

    if history_df.empty:
        return pd.DataFrame()

    history_df["timestamp"] = pd.to_datetime(history_df["timestamp"], errors="coerce", utc=True)
    history_df["transfer_price"] = pd.to_numeric(history_df["transfer_price"], errors="coerce")
    history_df["player_id"] = pd.to_numeric(history_df["player_id"], errors="coerce")
    history_df = history_df.dropna(subset=["timestamp", "transfer_price", "player_id"])
    if history_df.empty:
        return history_df

    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=lookback_days)
    history_df = history_df[history_df["timestamp"] >= cutoff].copy()
    history_df["player_id"] = history_df["player_id"].astype(int)
    if "mv" in history_df.columns:
        history_df["mv"] = pd.to_numeric(history_df["mv"], errors="coerce")
    if "position" not in history_df.columns:
        history_df["position"] = None
    if "team_name" not in history_df.columns:
        history_df["team_name"] = None
    return history_df.sort_values("timestamp", ascending=False).reset_index(drop=True)


def _load_market_snapshot_index(db_path, league_id, cutoff):
    with sqlite3.connect(db_path) as conn:
        if not _table_exists(conn, "advisor_snapshots") or not _table_exists(conn, "advisor_runs"):
            return {"by_player_id": {}, "by_name": {}}
        snapshot_rows = pd.read_sql_query(
            """
            SELECT r.created_at, s.payload_json
            FROM advisor_snapshots s
            INNER JOIN advisor_runs r ON r.run_id = s.run_id
            WHERE r.league_id = ?
                AND s.snapshot_name = 'market'
                AND r.created_at >= ?
            ORDER BY r.created_at DESC
            """,
            conn,
            params=[league_id, cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")],
        )

    index_by_player_id = {}
    index_by_name = {}
    if snapshot_rows.empty:
        return {"by_player_id": index_by_player_id, "by_name": index_by_name}

    for _, snapshot_row in snapshot_rows.iterrows():
        snapshot_time = pd.to_datetime(snapshot_row.get("created_at"), errors="coerce", utc=True)
        if pd.isna(snapshot_time):
            continue
        try:
            payload = json.loads(snapshot_row.get("payload_json") or "[]")
        except json.JSONDecodeError:
            continue

        for item in payload:
            if not isinstance(item, dict):
                continue
            row = dict(item)
            row["snapshot_created_at"] = snapshot_time
            player_id = pd.to_numeric(row.get("player_id"), errors="coerce")
            normalized_name = _normalize_player_name(row)
            if pd.notna(player_id):
                index_by_player_id.setdefault(int(player_id), []).append(row)
            if normalized_name:
                index_by_name.setdefault(normalized_name, []).append(row)

    return {"by_player_id": index_by_player_id, "by_name": index_by_name}


def _load_latest_squad_snapshot(db_path, league_id, own_username):
    with sqlite3.connect(db_path) as conn:
        if not _table_exists(conn, "advisor_snapshots") or not _table_exists(conn, "advisor_runs"):
            return pd.DataFrame()
        snapshot_rows = pd.read_sql_query(
            """
            SELECT s.payload_json
            FROM advisor_snapshots s
            INNER JOIN advisor_runs r ON r.run_id = s.run_id
            WHERE r.league_id = ?
                AND r.own_username = ?
                AND s.snapshot_name = 'squad'
            ORDER BY r.created_at DESC
            LIMIT 1
            """,
            conn,
            params=[league_id, own_username],
        )

    if snapshot_rows.empty:
        return pd.DataFrame()

    try:
        payload = json.loads(snapshot_rows.iloc[0]["payload_json"] or "[]")
    except json.JSONDecodeError:
        return pd.DataFrame()

    return pd.DataFrame(payload)


def _build_current_squad_lookup(squad_df):
    if squad_df is None or squad_df.empty or "player_id" not in squad_df.columns:
        return {}

    working_squad_df = squad_df.copy()
    working_squad_df["player_id"] = pd.to_numeric(working_squad_df["player_id"], errors="coerce")
    working_squad_df = working_squad_df.dropna(subset=["player_id"]).drop_duplicates(subset=["player_id"])
    return {int(row["player_id"]): row.to_dict() for _, row in working_squad_df.iterrows()}


def _find_latest_snapshot_before_purchase(snapshot_index, player_id, player_name, purchase_time, max_snapshot_age_hours):
    candidates = snapshot_index.get("by_player_id", {}).get(int(player_id), [])
    if not candidates and player_name:
        candidates = snapshot_index.get("by_name", {}).get(" ".join(str(player_name).strip().lower().split()), [])

    best_match = None
    for candidate in candidates:
        snapshot_time = candidate.get("snapshot_created_at")
        if snapshot_time is None or snapshot_time > purchase_time:
            continue
        age_hours = (purchase_time - snapshot_time).total_seconds() / 3600
        if age_hours > max_snapshot_age_hours:
            continue
        if best_match is None or snapshot_time > best_match.get("snapshot_created_at"):
            best_match = candidate
    return best_match


def _build_buy_training_row(purchase_row, sale_row, current_squad_row, snapshot_match, min_open_hold_days):
    purchase_price = _safe_float(purchase_row.get("transfer_price")) or 0.0
    purchase_market_value = _safe_float(purchase_row.get("mv"))
    purchase_time = pd.to_datetime(purchase_row.get("timestamp"), errors="coerce", utc=True)
    signal_alignment, signal_note = _classify_snapshot_alignment(snapshot_match, purchase_price)

    outcome = _determine_outcome(
        purchase_price=purchase_price,
        purchase_time=purchase_time,
        sale_row=sale_row,
        current_squad_row=current_squad_row,
    )
    quality_label, quality_target = _classify_buy_quality(
        purchase_price=purchase_price,
        outcome_delta=outcome["outcome_delta_eur"],
        held_days=outcome["held_days"],
        current_squad_row=current_squad_row,
        signal_alignment=signal_alignment,
    )

    recommended_bid_max = _safe_float(snapshot_match.get("recommended_bid_max")) if snapshot_match else None
    competitive_bid_max = _safe_float(snapshot_match.get("competitive_bid_max")) if snapshot_match else None
    effective_bid_cap = _safe_float(snapshot_match.get("effective_bid_cap")) if snapshot_match else None
    purchase_premium_abs = purchase_price - purchase_market_value if purchase_market_value is not None else None
    purchase_premium_pct = ((purchase_price / purchase_market_value) - 1) if purchase_market_value not in {None, 0} else None

    snapshot_created_at = snapshot_match.get("snapshot_created_at") if snapshot_match else None
    snapshot_age_hours = None
    if purchase_time is not None and snapshot_created_at is not None:
        snapshot_age_hours = round((purchase_time - snapshot_created_at).total_seconds() / 3600, 2)

    training_eligible = bool(
        snapshot_match
        and outcome["outcome_reference_value"] is not None
        and (
            outcome["outcome_type"] == "realized"
            or ((outcome["held_days"] or 0) >= float(min_open_hold_days))
        )
    )

    return {
        "purchase_timestamp": purchase_time.strftime("%Y-%m-%dT%H:%M:%SZ") if purchase_time is not None else None,
        "player_id": int(purchase_row.get("player_id")),
        "player_name": purchase_row.get("player_name") or "Unbekannt",
        "team_name": purchase_row.get("team_name"),
        "position": purchase_row.get("position"),
        "purchase_price": round(purchase_price, 0),
        "purchase_market_value": round(purchase_market_value, 0) if purchase_market_value is not None else None,
        "purchase_premium_abs": round(purchase_premium_abs, 0) if purchase_premium_abs is not None else None,
        "purchase_premium_pct": round(purchase_premium_pct, 4) if purchase_premium_pct is not None else None,
        "snapshot_found": bool(snapshot_match),
        "snapshot_created_at": snapshot_created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if snapshot_created_at is not None else None,
        "snapshot_age_hours": snapshot_age_hours,
        "model_buy_action": snapshot_match.get("buy_action") if snapshot_match else None,
        "model_priority_score": _safe_float(snapshot_match.get("priority_score")) if snapshot_match else None,
        "model_delta_prediction": _safe_float(snapshot_match.get("delta_prediction")) if snapshot_match else None,
        "model_delta_percent": _safe_float(snapshot_match.get("delta_percent")) if snapshot_match else None,
        "model_football_signal_score": _safe_float(snapshot_match.get("football_signal_score")) if snapshot_match else None,
        "model_asset_role": snapshot_match.get("asset_role") if snapshot_match else None,
        "model_recommended_bid_max": round(recommended_bid_max, 0) if recommended_bid_max is not None else None,
        "model_competitive_bid_max": round(competitive_bid_max, 0) if competitive_bid_max is not None else None,
        "model_recent_bid_competition": snapshot_match.get("recent_bid_competition") if snapshot_match else None,
        "model_bid_strategy_note": snapshot_match.get("bid_strategy_note") if snapshot_match else None,
        "model_roster_need_level": snapshot_match.get("roster_need_level") if snapshot_match else None,
        "model_team_availability_level": snapshot_match.get("team_availability_level") if snapshot_match else None,
        "model_buy_gate_status": snapshot_match.get("buy_gate_status") if snapshot_match else None,
        "model_effective_bid_cap": round(effective_bid_cap, 0) if effective_bid_cap is not None else None,
        "model_hours_to_exp": _safe_float(snapshot_match.get("hours_to_exp")) if snapshot_match else None,
        "model_expiring_today": bool(snapshot_match.get("expiring_today")) if snapshot_match else None,
        "price_vs_recommended_abs": _relative_abs(purchase_price, recommended_bid_max),
        "price_vs_recommended_pct": _relative_pct(purchase_price, recommended_bid_max),
        "price_vs_competitive_abs": _relative_abs(purchase_price, competitive_bid_max),
        "price_vs_competitive_pct": _relative_pct(purchase_price, competitive_bid_max),
        "price_vs_effective_cap_abs": _relative_abs(purchase_price, effective_bid_cap),
        "price_vs_effective_cap_pct": _relative_pct(purchase_price, effective_bid_cap),
        "outcome_reference_value": outcome["outcome_reference_value"],
        "outcome_delta_eur": outcome["outcome_delta_eur"],
        "outcome_delta_pct": outcome["outcome_delta_pct"],
        "outcome_type": outcome["outcome_type"],
        "held_days": outcome["held_days"],
        "current_squad_role": current_squad_row.get("squad_role") if current_squad_row else None,
        "current_sell_priority_score": _safe_float(current_squad_row.get("sell_priority_score")) if current_squad_row else None,
        "signal_alignment": signal_alignment,
        "signal_note": signal_note,
        "buy_quality_label": quality_label,
        "buy_quality_target": quality_target,
        "training_eligible": training_eligible,
    }


def _determine_outcome(purchase_price, purchase_time, sale_row, current_squad_row):
    sale_price = _safe_float(sale_row.get("transfer_price")) if sale_row else None
    current_market_value = _safe_float(current_squad_row.get("mv")) if current_squad_row else None

    if sale_price is not None:
        outcome_reference_value = sale_price
        outcome_type = "realized"
        end_time = pd.to_datetime(sale_row.get("timestamp"), errors="coerce", utc=True)
    elif current_market_value is not None:
        outcome_reference_value = current_market_value
        outcome_type = "open"
        end_time = pd.Timestamp.now(tz="UTC")
    else:
        outcome_reference_value = None
        outcome_type = "unknown"
        end_time = None

    outcome_delta_eur = None if outcome_reference_value is None else round(float(outcome_reference_value - purchase_price), 0)
    outcome_delta_pct = None if outcome_reference_value in {None, 0} or purchase_price == 0 else round((float(outcome_reference_value) / float(purchase_price)) - 1, 4)

    held_days = None
    if purchase_time is not None and end_time is not None and pd.notna(end_time):
        held_days = round((end_time - purchase_time).total_seconds() / 86400, 1)

    return {
        "outcome_reference_value": round(float(outcome_reference_value), 0) if outcome_reference_value is not None else None,
        "outcome_delta_eur": outcome_delta_eur,
        "outcome_delta_pct": outcome_delta_pct,
        "outcome_type": outcome_type,
        "held_days": held_days,
    }


def _classify_buy_quality(purchase_price, outcome_delta, held_days, current_squad_row, signal_alignment):
    threshold = max(300_000.0, float(purchase_price) * 0.03)
    squad_role = str(current_squad_row.get("squad_role") or "") if current_squad_row else ""
    sell_priority_score = _safe_float(current_squad_row.get("sell_priority_score")) if current_squad_row else None

    if outcome_delta is not None and outcome_delta >= threshold:
        label = "good"
    elif outcome_delta is not None and outcome_delta <= -threshold:
        label = "poor"
    elif current_squad_row and squad_role == "core_starter" and (sell_priority_score or 0) < 45 and (held_days or 0) >= 2:
        label = "good"
    else:
        label = "neutral"

    if label == "neutral" and signal_alignment == "misaligned" and outcome_delta is not None and outcome_delta < 0:
        label = "poor"

    target = {"poor": -1, "neutral": 0, "good": 1}[label]
    return label, target


def _classify_snapshot_alignment(snapshot_match, purchase_price):
    if not snapshot_match:
        return "unknown", "Kein passender Marktsnapshot vor dem Kauf gefunden."

    buy_action = str(snapshot_match.get("buy_action") or "pass")
    competitive_bid_max = _safe_float(snapshot_match.get("competitive_bid_max"))
    delta_prediction = _safe_float(snapshot_match.get("delta_prediction"))
    priority_score = _safe_float(snapshot_match.get("priority_score"))

    if buy_action == "pass" or (delta_prediction is not None and delta_prediction <= 0):
        return "misaligned", "Das Modell hatte vor dem Kauf keinen sauberen Kauf-Edge signalisiert."
    if competitive_bid_max is not None and float(purchase_price) > float(competitive_bid_max) * 1.03:
        return "misaligned", "Der Kaufpreis lag oberhalb der disziplinierten Modellgrenze."
    if buy_action == "buy_now":
        return "aligned", "Der Kauf war auch aus Modellsicht ein Sofort-Kandidat."
    if buy_action == "watchlist" or (priority_score is not None and priority_score >= 65):
        return "aligned", "Der Kauf war aus Modellsicht mindestens vertretbar vorbereitet."
    return "unknown", "Vor dem Kauf lag kein eindeutiges Modellsignal vor."


def _build_purchase_learning_note(good_count, poor_count, model_misaligned_count):
    if good_count == poor_count == 0:
        return "Noch keine belastbaren Kaufresultate im Auswertungsfenster."
    if poor_count > good_count and model_misaligned_count >= max(1, poor_count // 2):
        return "Zu viele schwache Kaeufe liefen gegen Preis- oder Modellsignale. Preisdisziplin und harte Gates wichtiger setzen."
    if good_count >= poor_count + 2:
        return "Die juengsten Kaeufe wirken insgesamt sauber. Gute Trades weiter priorisieren, aber Preisdisziplin halten."
    return "Die juengsten Kaeufe sind gemischt. Besonders Transfers ausserhalb der disziplinierten Modellgrenzen enger pruefen."


def _relative_abs(value, reference):
    if reference is None:
        return None
    return round(float(value - reference), 0)


def _relative_pct(value, reference):
    if reference in {None, 0}:
        return None
    return round((float(value) / float(reference)) - 1, 4)


def _safe_float(value):
    if value is None or pd.isna(value):
        return None
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None
    if np.isnan(numeric_value):
        return None
    return numeric_value


def _table_exists(connection, table_name):
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
        (table_name,),
    ).fetchone()
    return row is not None


def _normalize_player_name(row):
    first_name = str(row.get("first_name", "") or "").strip()
    last_name = str(row.get("last_name", "") or "").strip()
    full_name = " ".join(part for part in [first_name, last_name] if part)
    if not full_name:
        full_name = str(row.get("player_name", "") or "").strip()
    return " ".join(full_name.lower().split())


def _empty_buy_training_dataset():
    return pd.DataFrame(columns=BUY_TRAINING_COLUMNS)


def _empty_purchase_evaluation_summary():
    return {
        "recent_purchase_count": 0,
        "good_count": 0,
        "neutral_count": 0,
        "poor_count": 0,
        "model_misaligned_count": 0,
        "realized_count": 0,
        "open_count": 0,
        "training_eligible_count": 0,
        "learning_note": "Keine eigenen Kaeufe im Auswertungsfenster gefunden.",
        "recent_evaluations": [],
    }