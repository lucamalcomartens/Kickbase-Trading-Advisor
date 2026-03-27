from __future__ import annotations

import json
import numbers
import sqlite3
import uuid
from datetime import datetime, timezone

import numpy as np
import pandas as pd


def create_advisor_tables(db_path):
    """Create persistence tables for transfer history and full run snapshots."""

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS league_transfer_history (
                league_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                buyer TEXT,
                seller TEXT,
                player_id INTEGER NOT NULL,
                player_name TEXT,
                team_id INTEGER,
                transfer_price REAL NOT NULL,
                PRIMARY KEY (league_id, timestamp, player_id, buyer, seller, transfer_price)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS advisor_runs (
                run_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                report_date TEXT,
                league_id INTEGER,
                own_username TEXT,
                own_budget REAL,
                ai_status TEXT,
                mail_status TEXT,
                matchday_context_json TEXT,
                model_metrics_json TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tracked_market_offers (
                offer_key TEXT PRIMARY KEY,
                league_id INTEGER NOT NULL,
                own_username TEXT,
                offer_id TEXT,
                player_id INTEGER NOT NULL,
                player_name TEXT,
                offer_amount REAL NOT NULL,
                market_value REAL,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                expires_at TEXT,
                status TEXT NOT NULL,
                lost_to TEXT,
                winning_price REAL,
                resolved_at TEXT,
                source TEXT,
                raw_json TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tracked_market_offer_observations (
                observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                offer_key TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                status TEXT NOT NULL,
                offer_amount REAL,
                market_value REAL,
                expires_at TEXT,
                raw_json TEXT,
                FOREIGN KEY (offer_key) REFERENCES tracked_market_offers(offer_key)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS advisor_snapshots (
                snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                snapshot_name TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES advisor_runs(run_id)
            )
            """
        )
        conn.commit()


def upsert_current_market_offers(offers_df, db_path):
    """Persist the currently visible active own offers and append an observation log."""

    if offers_df is None or offers_df.empty:
        return 0

    tracked_rows = []
    observation_rows = []
    for row in offers_df.to_dict(orient="records"):
        tracked_rows.append(
            (
                row["offer_key"],
                row["league_id"],
                row.get("own_username"),
                row.get("offer_id"),
                row["player_id"],
                row.get("player_name"),
                _json_safe_number(row.get("offer_amount")),
                _json_safe_number(row.get("market_value")),
                row["observed_at"],
                row["observed_at"],
                row.get("expires_at"),
                row.get("status") or "active",
                row.get("source"),
                row.get("raw_json"),
            )
        )
        observation_rows.append(
            (
                row["offer_key"],
                row["observed_at"],
                row.get("status") or "active",
                _json_safe_number(row.get("offer_amount")),
                _json_safe_number(row.get("market_value")),
                row.get("expires_at"),
                row.get("raw_json"),
            )
        )

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO tracked_market_offers (
                offer_key,
                league_id,
                own_username,
                offer_id,
                player_id,
                player_name,
                offer_amount,
                market_value,
                first_seen_at,
                last_seen_at,
                expires_at,
                status,
                source,
                raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(offer_key) DO UPDATE SET
                last_seen_at = excluded.last_seen_at,
                expires_at = excluded.expires_at,
                status = excluded.status,
                market_value = COALESCE(excluded.market_value, tracked_market_offers.market_value),
                raw_json = excluded.raw_json
            """,
            tracked_rows,
        )
        cursor.executemany(
            """
            INSERT INTO tracked_market_offer_observations (
                offer_key,
                observed_at,
                status,
                offer_amount,
                market_value,
                expires_at,
                raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            observation_rows,
        )
        conn.commit()

    return len(tracked_rows)


def reconcile_tracked_market_offers(db_path, league_id, own_username, current_offers_df, transfer_history_df):
    """Resolve no-longer-visible offers as won, outbid, or unresolved."""

    reference_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    current_offer_keys = set()
    if current_offers_df is not None and not current_offers_df.empty:
        current_offer_keys = set(current_offers_df["offer_key"].dropna().astype(str))

    with sqlite3.connect(db_path) as conn:
        _expire_active_offers(conn, league_id, own_username, reference_time)
        active_offers = pd.read_sql_query(
            """
            SELECT offer_key, player_id, player_name, offer_amount, first_seen_at, last_seen_at
            FROM tracked_market_offers
            WHERE league_id = ? AND own_username = ? AND status = 'active'
            """,
            conn,
            params=[league_id, own_username],
        )

        if active_offers.empty:
            return {"won": 0, "outbid": 0, "unresolved": 0}

        disappeared_offers = active_offers[~active_offers["offer_key"].astype(str).isin(current_offer_keys)].copy()
        if disappeared_offers.empty:
            return {"won": 0, "outbid": 0, "unresolved": 0}

        transfer_df = transfer_history_df.copy() if transfer_history_df is not None else pd.DataFrame()
        if not transfer_df.empty:
            transfer_df["timestamp"] = pd.to_datetime(transfer_df["timestamp"], errors="coerce", utc=True)
            transfer_df = transfer_df.dropna(subset=["timestamp", "player_id"])

        cursor = conn.cursor()
        resolved_counts = {"won": 0, "outbid": 0, "unresolved": 0}

        for offer_row in disappeared_offers.to_dict(orient="records"):
            resolution = _resolve_offer_resolution(offer_row, transfer_df, own_username)
            cursor.execute(
                """
                UPDATE tracked_market_offers
                SET status = ?, lost_to = ?, winning_price = ?, resolved_at = ?
                WHERE offer_key = ?
                """,
                (
                    resolution["status"],
                    resolution.get("lost_to"),
                    _json_safe_number(resolution.get("winning_price")),
                    resolution["resolved_at"],
                    offer_row["offer_key"],
                ),
            )
            cursor.execute(
                """
                INSERT INTO tracked_market_offer_observations (
                    offer_key,
                    observed_at,
                    status,
                    offer_amount,
                    market_value,
                    expires_at,
                    raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    offer_row["offer_key"],
                    resolution["resolved_at"],
                    resolution["status"],
                    _json_safe_number(offer_row.get("offer_amount")),
                    None,
                    None,
                    json.dumps({key: _json_safe_number(value) for key, value in resolution.items()}, ensure_ascii=False),
                ),
            )
            if resolution["status"] == "won":
                resolved_counts["won"] += 1
            elif resolution["status"] == "outbid":
                resolved_counts["outbid"] += 1
            else:
                resolved_counts["unresolved"] += 1

        conn.commit()
        return resolved_counts


def load_offer_tracking_summary(db_path, league_id, own_username, limit=5):
    """Load compact stats and recent overbid cases for the user."""

    reference_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cutoff_7d = (datetime.now(timezone.utc) - pd.Timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    cutoff_14d = (datetime.now(timezone.utc) - pd.Timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with sqlite3.connect(db_path) as conn:
        _expire_active_offers(conn, league_id, own_username, reference_time)
        summary_df = pd.read_sql_query(
            """
            SELECT
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_offers,
                SUM(CASE WHEN status = 'outbid' THEN 1 ELSE 0 END) AS outbid_offers,
                SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) AS won_offers,
                SUM(CASE WHEN status = 'inactive_unresolved' THEN 1 ELSE 0 END) AS unresolved_offers
            FROM tracked_market_offers
            WHERE league_id = ? AND own_username = ?
            """,
            conn,
            params=[league_id, own_username],
        )
        recent_outbid_df = pd.read_sql_query(
            """
            SELECT player_name, offer_amount, winning_price, lost_to, resolved_at
            FROM tracked_market_offers
            WHERE league_id = ? AND own_username = ? AND status = 'outbid'
            ORDER BY resolved_at DESC
            LIMIT ?
            """,
            conn,
            params=[league_id, own_username, limit],
        )
        recent_active_df = pd.read_sql_query(
            """
            SELECT player_id, player_name, offer_amount, market_value, expires_at, last_seen_at
            FROM tracked_market_offers
            WHERE league_id = ? AND own_username = ? AND status = 'active'
                AND (expires_at IS NULL OR expires_at >= ?)
            ORDER BY last_seen_at DESC
            LIMIT ?
            """,
            conn,
            params=[league_id, own_username, reference_time, limit],
        )
        active_budget_df = pd.read_sql_query(
            """
            SELECT COALESCE(SUM(offer_amount), 0) AS active_offer_amount_total
            FROM tracked_market_offers
            WHERE league_id = ? AND own_username = ? AND status = 'active'
                AND (expires_at IS NULL OR expires_at >= ?)
            """,
            conn,
            params=[league_id, own_username, reference_time],
        )
        outbid_stats_df = pd.read_sql_query(
            """
            SELECT offer_amount, winning_price, resolved_at, player_name
            FROM tracked_market_offers
            WHERE league_id = ? AND own_username = ? AND status = 'outbid'
                AND resolved_at IS NOT NULL
                AND resolved_at >= ?
            ORDER BY resolved_at DESC
            """,
            conn,
            params=[league_id, own_username, cutoff_14d],
        )

    counts = summary_df.iloc[0].fillna(0).to_dict() if not summary_df.empty else {}
    counts = {key: int(value) for key, value in counts.items()}
    recent_outbid = recent_outbid_df.where(pd.notna(recent_outbid_df), None).to_dict(orient="records")
    recent_active = recent_active_df.where(pd.notna(recent_active_df), None).to_dict(orient="records")
    active_offer_amount_total = 0.0
    if not active_budget_df.empty:
        active_offer_amount_total = float(active_budget_df.iloc[0].get("active_offer_amount_total") or 0.0)

    outbid_stats_df = outbid_stats_df.copy()
    if not outbid_stats_df.empty:
        outbid_stats_df["offer_amount"] = pd.to_numeric(outbid_stats_df["offer_amount"], errors="coerce")
        outbid_stats_df["winning_price"] = pd.to_numeric(outbid_stats_df["winning_price"], errors="coerce")
        outbid_stats_df["resolved_at"] = pd.to_datetime(outbid_stats_df["resolved_at"], utc=True, errors="coerce")
        outbid_stats_df["outbid_gap"] = (outbid_stats_df["winning_price"] - outbid_stats_df["offer_amount"]).clip(lower=0)
        outbid_stats_df["outbid_gap_pct"] = np.where(
            outbid_stats_df["offer_amount"].fillna(0) > 0,
            outbid_stats_df["outbid_gap"] / outbid_stats_df["offer_amount"],
            np.nan,
        )
        recent_outbid_count_7d = int((outbid_stats_df["resolved_at"] >= pd.Timestamp(cutoff_7d)).sum())
        recent_outbid_count_14d = int(len(outbid_stats_df))
        avg_outbid_gap = outbid_stats_df["outbid_gap"].dropna().mean()
        avg_outbid_gap_pct = outbid_stats_df["outbid_gap_pct"].dropna().mean()
        avg_outbid_gap = 0.0 if pd.isna(avg_outbid_gap) else float(avg_outbid_gap)
        avg_outbid_gap_pct = 0.0 if pd.isna(avg_outbid_gap_pct) else float(avg_outbid_gap_pct)
    else:
        recent_outbid_count_7d = 0
        recent_outbid_count_14d = 0
        avg_outbid_gap = 0.0
        avg_outbid_gap_pct = 0.0

    suggested_markup_pct = min(max(avg_outbid_gap_pct * 0.75, 0.0), 0.05)
    if recent_outbid_count_14d >= 5 or avg_outbid_gap_pct >= 0.03:
        overbid_pressure_level = "high"
    elif recent_outbid_count_14d >= 2 or avg_outbid_gap_pct >= 0.015:
        overbid_pressure_level = "medium"
    else:
        overbid_pressure_level = "low"

    stats = {
        "active_offer_amount_total": round(active_offer_amount_total, 2),
        "recent_outbid_count_7d": recent_outbid_count_7d,
        "recent_outbid_count_14d": recent_outbid_count_14d,
        "avg_outbid_gap": round(avg_outbid_gap, 2),
        "avg_outbid_gap_pct": round(avg_outbid_gap_pct, 4),
        "suggested_markup_pct": round(suggested_markup_pct, 4),
        "overbid_pressure_level": overbid_pressure_level,
    }
    return {"counts": counts, "recent_outbid": recent_outbid, "recent_active": recent_active, "stats": stats}


def save_transfer_history_to_db(transfer_history_df, league_id, db_path):
    """Persist raw completed transfer events for later bid-history analysis."""

    if transfer_history_df.empty:
        return 0

    storage_df = transfer_history_df.copy()
    storage_df = storage_df[["timestamp", "buyer", "seller", "player_id", "player_name", "team_id", "transfer_price"]]
    storage_df["league_id"] = league_id
    storage_df["timestamp"] = pd.to_datetime(storage_df["timestamp"], errors="coerce", utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    storage_df["transfer_price"] = pd.to_numeric(storage_df["transfer_price"], errors="coerce")
    storage_df = storage_df.dropna(subset=["timestamp", "player_id", "transfer_price"])

    if storage_df.empty:
        return 0

    rows = list(storage_df[["league_id", "timestamp", "buyer", "seller", "player_id", "player_name", "team_id", "transfer_price"]].itertuples(index=False, name=None))

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT OR IGNORE INTO league_transfer_history (
                league_id,
                timestamp,
                buyer,
                seller,
                player_id,
                player_name,
                team_id,
                transfer_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
        return cursor.rowcount


def load_transfer_history_from_db(league_id, db_path, lookback_days=None):
    """Load persisted transfer history for a league, optionally limited to a recent window."""

    query = "SELECT timestamp, buyer, seller, player_id, player_name, team_id, transfer_price FROM league_transfer_history WHERE league_id = ?"
    params = [league_id]

    if lookback_days is not None:
        cutoff = (datetime.now(timezone.utc) - pd.Timedelta(days=lookback_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        query += " AND timestamp >= ?"
        params.append(cutoff)

    query += " ORDER BY timestamp DESC"

    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn, params=params)


def save_run_snapshot(
    db_path,
    report_date,
    league_id,
    own_username,
    own_budget,
    matchday_context,
    model_metrics,
    ai_status,
    mail_status,
    manager_budgets_df,
    market_df,
    squad_df,
):
    """Persist a full run with structured snapshot payloads for later inspection."""

    run_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    snapshots = {
        "manager_budgets": manager_budgets_df,
        "market": market_df,
        "squad": squad_df,
    }

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO advisor_runs (
                run_id,
                created_at,
                report_date,
                league_id,
                own_username,
                own_budget,
                ai_status,
                mail_status,
                matchday_context_json,
                model_metrics_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                created_at,
                report_date,
                league_id,
                own_username,
                _json_safe_number(own_budget),
                ai_status,
                mail_status,
                json.dumps(matchday_context, ensure_ascii=False),
                json.dumps(model_metrics, ensure_ascii=False),
            ),
        )

        snapshot_rows = []
        for snapshot_name, dataframe in snapshots.items():
            payload_json = json.dumps(_dataframe_to_records(dataframe), ensure_ascii=False)
            snapshot_rows.append((run_id, snapshot_name, len(dataframe), payload_json, created_at))

        cursor.executemany(
            """
            INSERT INTO advisor_snapshots (run_id, snapshot_name, row_count, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            snapshot_rows,
        )
        conn.commit()

    return run_id


def _dataframe_to_records(dataframe):
    if dataframe is None or dataframe.empty:
        return []

    safe_df = dataframe.copy()
    for column in safe_df.columns:
        if pd.api.types.is_datetime64_any_dtype(safe_df[column]):
            safe_df[column] = safe_df[column].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    safe_df = safe_df.where(pd.notna(safe_df), None)
    return safe_df.to_dict(orient="records")


def _json_safe_number(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, numbers.Real):
        return float(value)
    return value


def _expire_active_offers(conn, league_id, own_username, reference_time):
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE tracked_market_offers
        SET status = 'inactive_unresolved',
            resolved_at = COALESCE(resolved_at, ?)
        WHERE league_id = ?
            AND own_username = ?
            AND status = 'active'
            AND expires_at IS NOT NULL
            AND expires_at < ?
        """,
        (reference_time, league_id, own_username, reference_time),
    )
    conn.commit()


def _resolve_offer_resolution(offer_row, transfer_df, own_username):
    fallback_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if transfer_df is None or transfer_df.empty:
        return {"status": "inactive_unresolved", "resolved_at": fallback_time}

    offer_seen_at = pd.to_datetime(offer_row.get("last_seen_at"), errors="coerce", utc=True)
    player_transfers = transfer_df[transfer_df["player_id"] == offer_row["player_id"]].copy()
    if pd.notna(offer_seen_at):
        player_transfers = player_transfers[player_transfers["timestamp"] >= offer_seen_at]

    if player_transfers.empty:
        return {"status": "inactive_unresolved", "resolved_at": fallback_time}

    latest_transfer = player_transfers.sort_values("timestamp", ascending=False).iloc[0]
    resolved_at = latest_transfer["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ")
    buyer = latest_transfer.get("buyer")
    winning_price = latest_transfer.get("transfer_price")

    if buyer == own_username:
        return {
            "status": "won",
            "resolved_at": resolved_at,
            "winning_price": winning_price,
        }

    return {
        "status": "outbid",
        "resolved_at": resolved_at,
        "lost_to": buyer,
        "winning_price": winning_price,
    }