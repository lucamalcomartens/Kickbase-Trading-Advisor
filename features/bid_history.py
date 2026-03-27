from __future__ import annotations

import numpy as np
import pandas as pd

from features.advisor_db import load_transfer_history_from_db, save_transfer_history_to_db
from kickbase_api.league import get_league_transfers


TRANSFER_HISTORY_LOOKBACK_DAYS = 45
RECENT_PLAYER_TRANSFER_WINDOW_DAYS = 21


def build_transfer_history_df(
    token,
    league_id,
    league_start_date,
    player_reference_df,
    db_path,
    lookback_days=TRANSFER_HISTORY_LOOKBACK_DAYS,
):
    """Build a recent transfer history dataframe enriched with current player references."""

    transfers = get_league_transfers(token, league_id, min_date=league_start_date)
    raw_history_df = pd.DataFrame(transfers)
    if not raw_history_df.empty:
        save_transfer_history_to_db(raw_history_df, league_id, db_path)

    history_df = load_transfer_history_from_db(league_id, db_path, lookback_days=lookback_days)
    if history_df.empty:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "buyer",
                "seller",
                "player_id",
                "player_name",
                "team_id",
                "transfer_price",
                "mv",
                "position",
                "team_name",
                "reference_mv",
                "transfer_premium",
                "transfer_premium_pct",
                "price_bucket",
            ]
        )

    history_df["timestamp"] = pd.to_datetime(history_df["timestamp"], errors="coerce", utc=True)
    history_df["transfer_price"] = pd.to_numeric(history_df["transfer_price"], errors="coerce")
    history_df = history_df.dropna(subset=["timestamp", "player_id", "transfer_price"])

    if history_df.empty:
        return history_df

    history_df["player_id"] = pd.to_numeric(history_df["player_id"], errors="coerce")
    history_df = history_df.dropna(subset=["player_id"])
    history_df["player_id"] = history_df["player_id"].astype(int)

    reference_columns = [column for column in ["player_id", "mv", "position", "team_name"] if column in player_reference_df.columns]
    reference_df = player_reference_df[reference_columns].drop_duplicates(subset=["player_id"])
    reference_df["player_id"] = pd.to_numeric(reference_df["player_id"], errors="coerce")
    reference_df = reference_df.dropna(subset=["player_id"])
    reference_df["player_id"] = reference_df["player_id"].astype(int)
    history_df = history_df.merge(reference_df, on="player_id", how="left")

    history_df["reference_mv"] = history_df["mv"].where(history_df["mv"].fillna(0) > 0, history_df["transfer_price"])
    history_df["transfer_premium"] = history_df["transfer_price"] - history_df["reference_mv"]
    history_df["transfer_premium_pct"] = np.where(
        history_df["reference_mv"].fillna(0) > 0,
        (history_df["transfer_price"] / history_df["reference_mv"]) - 1,
        np.nan,
    )
    history_df["transfer_premium_pct"] = history_df["transfer_premium_pct"].clip(lower=-0.35, upper=0.45)
    history_df["price_bucket"] = _build_price_bucket(history_df["reference_mv"].fillna(history_df["transfer_price"]))

    return history_df.sort_values("timestamp", ascending=False).reset_index(drop=True)


def enrich_market_with_bid_history(market_df, transfer_history_df):
    """Add historical market-pressure signals and competitive bid ceilings."""

    if market_df.empty:
        return market_df.copy()

    enriched_df = market_df.copy()
    default_price = pd.to_numeric(enriched_df.get("mv"), errors="coerce").fillna(0)
    enriched_df["price_bucket"] = _build_price_bucket(default_price)
    enriched_df["recent_bid_competition"] = "unknown"
    enriched_df["estimated_market_winning_bid"] = pd.to_numeric(enriched_df.get("recommended_bid_max"), errors="coerce")
    enriched_df["competitive_bid_max"] = pd.to_numeric(enriched_df.get("recommended_bid_max"), errors="coerce")
    enriched_df["bid_strategy_note"] = "no_history"
    enriched_df["last_transfer_price"] = np.nan
    enriched_df["last_transfer_buyer"] = None
    enriched_df["days_since_last_transfer"] = np.nan

    if transfer_history_df.empty:
        enriched_df["competitive_bid_range"] = enriched_df.apply(_build_competitive_bid_range, axis=1)
        return enriched_df

    history_df = transfer_history_df.copy()
    history_df = history_df.dropna(subset=["player_id", "transfer_price"])
    history_df["player_id"] = pd.to_numeric(history_df["player_id"], errors="coerce")
    history_df = history_df.dropna(subset=["player_id"])
    history_df["player_id"] = history_df["player_id"].astype(int)
    if "timestamp" in history_df.columns:
        history_df["timestamp"] = pd.to_datetime(history_df["timestamp"], errors="coerce", utc=True)
    history_df["transfer_premium_pct"] = pd.to_numeric(history_df["transfer_premium_pct"], errors="coerce")
    history_df["transfer_price"] = pd.to_numeric(history_df["transfer_price"], errors="coerce")
    history_df = history_df.dropna(subset=["timestamp"])

    segment_summary = (
        history_df.groupby(["position", "price_bucket"], dropna=False)
        .agg(
            historical_transfer_count=("player_id", "size"),
            segment_median_premium_pct=("transfer_premium_pct", "median"),
            segment_p75_premium_pct=("transfer_premium_pct", lambda values: values.quantile(0.75)),
            segment_distinct_buyers=("buyer", "nunique"),
        )
        .reset_index()
    )

    same_player_history = (
        history_df.sort_values("timestamp", ascending=False)
        .drop_duplicates(subset=["player_id"])
        [["player_id", "transfer_price", "buyer", "timestamp", "transfer_premium_pct"]]
        .rename(
            columns={
                "transfer_price": "last_transfer_price",
                "buyer": "last_transfer_buyer",
                "timestamp": "last_transfer_timestamp",
                "transfer_premium_pct": "last_transfer_premium_pct",
            }
        )
    )

    enriched_df = enriched_df.merge(segment_summary, on=["position", "price_bucket"], how="left")
    if "player_id" in enriched_df.columns:
        enriched_df["player_id"] = pd.to_numeric(enriched_df["player_id"], errors="coerce")
        enriched_df = enriched_df.merge(same_player_history, on="player_id", how="left")

    global_median_premium = history_df["transfer_premium_pct"].median()
    global_p75_premium = history_df["transfer_premium_pct"].quantile(0.75)

    if "last_transfer_timestamp" in enriched_df.columns:
        last_transfer_delta = pd.Timestamp.now(tz="UTC") - enriched_df["last_transfer_timestamp"]
        enriched_df["days_since_last_transfer"] = np.round(last_transfer_delta.dt.total_seconds() / 86400, 1)
    else:
        enriched_df["days_since_last_transfer"] = np.nan

    blended_segment_premium = enriched_df["segment_median_premium_pct"].fillna(global_median_premium).fillna(0)
    recent_same_player_premium = np.where(
        enriched_df["days_since_last_transfer"].fillna(999) <= RECENT_PLAYER_TRANSFER_WINDOW_DAYS,
        enriched_df.get("last_transfer_premium_pct", pd.Series(index=enriched_df.index, dtype=float)),
        np.nan,
    )
    enriched_df["expected_bid_markup_pct"] = np.where(
        pd.notna(recent_same_player_premium),
        (pd.Series(recent_same_player_premium, index=enriched_df.index).fillna(0) * 0.65) + (blended_segment_premium * 0.35),
        blended_segment_premium,
    )
    enriched_df["expected_bid_markup_pct"] = enriched_df["expected_bid_markup_pct"].fillna(0).clip(lower=0, upper=0.25)

    mv_series = pd.to_numeric(enriched_df["mv"], errors="coerce").fillna(0)
    recommended_bid_max = pd.to_numeric(enriched_df["recommended_bid_max"], errors="coerce").fillna(mv_series)
    predicted_delta = pd.to_numeric(enriched_df["delta_prediction"], errors="coerce").fillna(0)
    profit_cap = np.maximum(mv_series, mv_series + (predicted_delta.clip(lower=0) * 0.9))
    history_ceiling = np.round(mv_series * (1 + enriched_df["expected_bid_markup_pct"]), 0)

    if "last_transfer_price" in enriched_df.columns:
        recent_player_ceiling = pd.to_numeric(enriched_df["last_transfer_price"], errors="coerce").where(
            enriched_df["days_since_last_transfer"].fillna(999) <= RECENT_PLAYER_TRANSFER_WINDOW_DAYS,
            np.nan,
        )
    else:
        recent_player_ceiling = pd.Series(np.nan, index=enriched_df.index)

    enriched_df["estimated_market_winning_bid"] = np.maximum.reduce(
        [
            mv_series.to_numpy(),
            history_ceiling.to_numpy(),
            recent_player_ceiling.fillna(0).to_numpy(),
        ]
    )
    enriched_df["estimated_market_winning_bid"] = np.round(enriched_df["estimated_market_winning_bid"], 0)

    can_chase_profitably = enriched_df["estimated_market_winning_bid"] <= profit_cap
    enriched_df["competitive_bid_max"] = np.where(
        can_chase_profitably,
        np.maximum(recommended_bid_max, enriched_df["estimated_market_winning_bid"]),
        recommended_bid_max,
    )
    enriched_df["competitive_bid_max"] = np.round(enriched_df["competitive_bid_max"], 0)

    competition_pressure = np.maximum(
        enriched_df["expected_bid_markup_pct"].fillna(0),
        enriched_df["segment_p75_premium_pct"].fillna(global_p75_premium).fillna(0),
    )
    distinct_buyers = enriched_df["segment_distinct_buyers"].fillna(0)

    enriched_df["recent_bid_competition"] = np.select(
        [
            (competition_pressure >= 0.12) | (distinct_buyers >= 6),
            (competition_pressure >= 0.05) | (distinct_buyers >= 3),
        ],
        ["high", "medium"],
        default="low",
    )
    enriched_df["bid_strategy_note"] = np.select(
        [
            ~can_chase_profitably & (enriched_df["recent_bid_competition"] == "high"),
            ~can_chase_profitably,
            enriched_df["recent_bid_competition"] == "high",
            enriched_df["recent_bid_competition"] == "medium",
        ],
        [
            "avoid_price_war",
            "stay_disciplined",
            "aggressive_only_if_priority_a",
            "small_markup_needed",
        ],
        default="model_range_ok",
    )

    if "historical_transfer_count" not in enriched_df.columns:
        enriched_df["historical_transfer_count"] = 0
    enriched_df["historical_transfer_count"] = enriched_df["historical_transfer_count"].fillna(0).astype(int)
    enriched_df["competitive_bid_range"] = enriched_df.apply(_build_competitive_bid_range, axis=1)

    return enriched_df


def _build_price_bucket(values):
    return pd.cut(
        values,
        bins=[-np.inf, 5_000_000, 10_000_000, 20_000_000, 30_000_000, np.inf],
        labels=["budget", "lower_mid", "upper_mid", "premium", "elite"],
    ).astype(str)


def _build_competitive_bid_range(row):
    lower = pd.to_numeric(pd.Series([row.get("recommended_bid_min")]), errors="coerce").iloc[0]
    upper = pd.to_numeric(pd.Series([row.get("competitive_bid_max")]), errors="coerce").iloc[0]
    if pd.isna(lower) or pd.isna(upper):
        return None
    return f"{int(lower):,}-{int(upper):,}".replace(",", ".")