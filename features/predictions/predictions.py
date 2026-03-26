from kickbase_api.league import get_league_players_on_market
from kickbase_api.user import get_players_in_squad
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import numpy as np


def _safe_probability(series, fallback=55):
    """Return a clipped probability series with a neutral fallback for missing values."""

    return series.fillna(fallback).clip(lower=0, upper=100)


def _safe_ratio(numerator, denominator):
    """Return a safe ratio while avoiding divide-by-zero and infinities."""

    denominator = denominator.replace(0, np.nan)
    return (numerator / denominator).replace([np.inf, -np.inf], np.nan).fillna(0)


def enrich_market_candidates(market_df):
    """Add deterministic prioritisation, role tags, and bid guidance for market players."""

    if market_df.empty:
        return market_df.copy()

    market_df = market_df.copy()

    starter_score = _safe_probability(market_df["s_11_prob"])
    urgency_score = np.where(
        market_df["expiring_today"],
        np.clip(100 - (market_df["hours_to_exp"].fillna(24) * 8), 35, 100),
        np.clip(62 - (market_df["hours_to_exp"].fillna(72) * 1.2), 10, 62),
    )
    delta_score = np.clip(50 + market_df["delta_percent"].fillna(0) * 6, 0, 100)
    trend_ratio = _safe_ratio(market_df["mv_change_yesterday"].fillna(0), market_df["mv"].fillna(0))
    trend_score = np.clip(50 + market_df["mv_trend_1d"].fillna(0) * 2500 + trend_ratio * 1500, 0, 100)
    points_score = np.clip(((market_df["p"].fillna(0) + 50) / 100) * 100, 0, 100)
    minutes_score = np.clip((market_df["mp"].fillna(0) / 90) * 100, 0, 100)
    ppm_score = np.clip(market_df["ppm"].fillna(0) * 35, 0, 100)
    fixture_score = np.clip(100 - market_df["days_to_next"].fillna(7) * 12, 20, 100)
    football_signal_score = np.round(
        (starter_score * 0.30)
        + (minutes_score * 0.25)
        + (points_score * 0.20)
        + (ppm_score * 0.10)
        + (fixture_score * 0.15),
        1,
    )

    market_df["urgency_score"] = np.round(urgency_score, 1)
    market_df["trend_score"] = np.round(trend_score, 1)
    market_df["football_signal_score"] = football_signal_score
    market_df["priority_score"] = np.round(
        (market_df["urgency_score"] * 0.30)
        + (delta_score * 0.25)
        + (starter_score * 0.20)
        + (market_df["trend_score"] * 0.15)
        + (market_df["football_signal_score"] * 0.10),
        1,
    )

    market_df["asset_role"] = np.select(
        [
            (starter_score >= 72) & (market_df["football_signal_score"] >= 65),
            (market_df["delta_prediction"] > 0) & ((market_df["delta_percent"] >= 4) | market_df["expiring_today"]),
        ],
        ["core_starter", "short_term_trade"],
        default="medium_term_hold",
    )

    market_df["buy_action"] = np.select(
        [
            (market_df["priority_score"] >= 72) & (market_df["delta_prediction"] > 0) & market_df["expiring_today"],
            (market_df["priority_score"] >= 65) & (market_df["delta_prediction"] > 0),
        ],
        ["buy_now", "watchlist"],
        default="pass",
    )

    role_multiplier = market_df["asset_role"].map({
        "core_starter": 0.60,
        "short_term_trade": 0.48,
        "medium_term_hold": 0.36,
    }).fillna(0.36)
    priority_factor = market_df["priority_score"] / 100
    urgency_factor = market_df["urgency_score"] / 100
    positive_headroom = market_df["delta_prediction"].clip(lower=0)
    market_value_cap = market_df["mv"] * (0.01 + (priority_factor * 0.04) + (urgency_factor * 0.03))
    headroom_cap = positive_headroom * role_multiplier
    max_overpay = np.minimum(headroom_cap, market_value_cap + (positive_headroom * 0.10)).clip(lower=0)

    market_df["recommended_bid_min"] = np.round(market_df["mv"] + (max_overpay * 0.35), 0)
    market_df["recommended_bid_max"] = np.round(market_df["mv"] + max_overpay, 0)
    market_df["bid_range"] = market_df.apply(
        lambda row: f"{int(row['recommended_bid_min']):,}-{int(row['recommended_bid_max']):,}".replace(",", "."),
        axis=1,
    )

    return market_df.sort_values(["priority_score", "delta_prediction", "hours_to_exp"], ascending=[False, False, True])


def enrich_squad_candidates(squad_df):
    """Add deterministic role tags and sell priority for squad players."""

    if squad_df.empty:
        return squad_df.copy()

    squad_df = squad_df.copy()

    starter_score = _safe_probability(squad_df["s_11_prob"])
    negative_delta_score = np.clip((-squad_df["delta_percent"].fillna(0)) * 8, 0, 100)
    trend_ratio = _safe_ratio(squad_df["mv_change_yesterday"].fillna(0), squad_df["mv"].fillna(0))
    trend_score = np.clip(50 + trend_ratio * 2000, 0, 100)
    points_score = np.clip(((squad_df["p"].fillna(0) + 50) / 100) * 100, 0, 100)
    minutes_score = np.clip((squad_df["mp"].fillna(0) / 90) * 100, 0, 100)
    ppm_score = np.clip(squad_df["ppm"].fillna(0) * 35, 0, 100)
    fixture_score = np.clip(100 - squad_df["days_to_next"].fillna(7) * 12, 20, 100)
    football_signal_score = np.round(
        (starter_score * 0.35)
        + (minutes_score * 0.25)
        + (points_score * 0.20)
        + (ppm_score * 0.10)
        + (fixture_score * 0.10),
        1,
    )

    squad_df["trend_score"] = np.round(trend_score, 1)
    squad_df["football_signal_score"] = football_signal_score
    squad_df["sell_priority_score"] = np.round(
        (negative_delta_score * 0.45)
        + ((100 - starter_score) * 0.25)
        + ((100 - squad_df["football_signal_score"]) * 0.15)
        + ((50 - squad_df["trend_score"]).clip(lower=0) * 0.15),
        1,
    )

    squad_df["squad_role"] = np.select(
        [
            (starter_score >= 72) & (squad_df["football_signal_score"] >= 65) & (squad_df["delta_prediction"] >= -150000),
            squad_df["sell_priority_score"] >= 60,
        ],
        ["core_starter", "sell_candidate"],
        default="rotation_hold",
    )
    squad_df["squad_action"] = np.select(
        [
            squad_df["sell_priority_score"] >= 60,
            squad_df["sell_priority_score"] >= 40,
        ],
        ["sell", "monitor"],
        default="hold",
    )

    return squad_df.sort_values(["sell_priority_score", "delta_prediction"], ascending=[False, True])

def live_data_predictions(today_df, model, features):
    """Make live data predictions for today_df using the trained model"""

    # Set features and copy df
    today_df_features = today_df[features]
    today_df_results = today_df.copy()

    # The model predicts the next-day market value change, not the absolute market value.
    today_df_results["predicted_mv_change"] = np.round(model.predict(today_df_features), 2)
    today_df_results["predicted_mv_target"] = np.round(
        today_df_results["mv"] + today_df_results["predicted_mv_change"],
        2,
    )

    # Sort by predicted market value change descending.
    today_df_results = today_df_results.sort_values("predicted_mv_change", ascending=False)

    # Filter date to today or yesterday if before 22:15, because mv is updated around 22:15
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    cutoff_time = now.replace(hour=22, minute=15, second=0, microsecond=0)
    date = (now - timedelta(days=1)) if now <= cutoff_time else now
    date = date.date()

    # Drop rows where NaN mv
    today_df_results = today_df_results.dropna(subset=["mv"])

    # Keep only relevant columns
    today_df_results = today_df_results[["player_id", "first_name", "last_name", "position", "team_name", "date", "p", "mp", "ppm", "days_to_next", "mv_change_1d", "mv_trend_1d", "mv", "predicted_mv_change", "predicted_mv_target"]]

    return today_df_results


def join_current_squad(token, league_id, today_df_results):
    squad_players = get_players_in_squad(token, league_id)

    squad_df = pd.DataFrame(squad_players["it"])

    # Join squad_df ("i") with today_df ("player_id")
    squad_df = (
        pd.merge(today_df_results, squad_df, left_on="player_id", right_on="i", suffixes=("", "_squad"))
        .drop(columns=["i"])
    )

    # Rename prob to s_11_prob for better understanding
    if "prob" not in squad_df.columns:
        squad_df["prob"] = np.nan  # Placeholder for non-pro users
    squad_df = squad_df.rename(columns={"prob": "s_11_prob"})

    # Rename mv_change_1d to mv_change_yesterday for better understanding
    squad_df = squad_df.rename(columns={"mv_change_1d": "mv_change_yesterday"})

    # Keep the model-side market value column stable even if the squad endpoint has its own mv field.
    if "mv_x" in squad_df.columns:
        squad_df = squad_df.rename(columns={"mv_x": "mv"})

    # Add model deltas to make decisions and prompt context easier to interpret.
    squad_df["delta_prediction"] = np.round(squad_df["predicted_mv_change"], 2)
    squad_df["delta_percent"] = np.where(
        squad_df["mv"].fillna(0) != 0,
        np.round((squad_df["delta_prediction"] / squad_df["mv"]) * 100, 2),
        np.nan,
    )

    # Keep only relevant columns
    squad_df = squad_df[["first_name", "last_name", "position", "team_name", "p", "mp", "ppm", "days_to_next", "mv", "mv_change_yesterday", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "s_11_prob"]]

    return enrich_squad_candidates(squad_df)


# TODO Add fail-safe check before player expires if the prob (starting 11) is still high, so no injuries or anything. if it dropped. dont bid / reccommend
def join_current_market(token, league_id, today_df_results, min_predicted_mv_target=5000):
    """Join the live predictions with the current market data.

    Use min_predicted_mv_target=None to return all current market players without a
    prediction-based recommendation filter.
    """

    players_on_market = get_league_players_on_market(token, league_id)

    # players_on_market to DataFrame
    market_df = pd.DataFrame(players_on_market)

    # Join market_df ("id") with today_df ("player_id")
    bid_df = (
        pd.merge(today_df_results, market_df, left_on="player_id", right_on="id", suffixes=("", "_market"))
        .drop(columns=["id"])
    )

    # exp contains seconds until expiration
    bid_df["hours_to_exp"] = np.round((bid_df["exp"] / 3600), 2)

    # check if current sysdate + hours_to_exp is after the next 22:00
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    next_22 = now.replace(hour=22, minute=0, second=0, microsecond=0)
    diff = np.round((next_22 - now).total_seconds() / 3600, 2)

    # If hours_to_exp < diff then it expires today
    bid_df["expiring_today"] = bid_df["hours_to_exp"] < diff

    # Apply the recommendation filter only when a minimum target is configured.
    if min_predicted_mv_target is not None:
        bid_df = bid_df[bid_df["predicted_mv_change"] > min_predicted_mv_target]

    # Sort by predicted market value change descending.
    bid_df = bid_df.sort_values("predicted_mv_change", ascending=False)

    # Rename prob to s_11_prob for better understanding
    if "prob" not in bid_df.columns:
        bid_df["prob"] = np.nan  # Placeholder for non-pro users
    bid_df = bid_df.rename(columns={"prob": "s_11_prob"})

    # Rename mv_change_1d to mv_change_yesterday for better understanding
    bid_df = bid_df.rename(columns={"mv_change_1d": "mv_change_yesterday"})

    # Add model deltas to make bidding logic easier to reason about.
    bid_df["delta_prediction"] = np.round(bid_df["predicted_mv_change"], 2)
    bid_df["delta_percent"] = np.where(
        bid_df["mv"].fillna(0) != 0,
        np.round((bid_df["delta_prediction"] / bid_df["mv"]) * 100, 2),
        np.nan,
    )

    # Keep only relevant columns
    bid_df = bid_df[["first_name", "last_name", "position", "team_name", "p", "mp", "ppm", "days_to_next", "mv", "mv_change_yesterday", "mv_trend_1d", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "s_11_prob", "hours_to_exp", "expiring_today"]]

    return enrich_market_candidates(bid_df)
