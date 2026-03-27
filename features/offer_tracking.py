from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import pandas as pd


def extract_current_market_offers(raw_transfer_feed, league_id, own_username):
    """Best-effort extraction of the user's currently active market offers."""

    if not raw_transfer_feed:
        return pd.DataFrame(columns=_offer_columns())

    observed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    offers = []
    seen_offer_keys = set()

    for candidate in _iter_offer_candidates(raw_transfer_feed):
        normalized_offer = _normalize_offer_candidate(candidate, league_id, own_username, observed_at)
        if not normalized_offer:
            continue
        if normalized_offer["offer_key"] in seen_offer_keys:
            continue
        seen_offer_keys.add(normalized_offer["offer_key"])
        offers.append(normalized_offer)

    if not offers:
        return pd.DataFrame(columns=_offer_columns())

    offers_df = pd.DataFrame(offers)
    offers_df["offer_amount"] = pd.to_numeric(offers_df["offer_amount"], errors="coerce")
    offers_df["market_value"] = pd.to_numeric(offers_df["market_value"], errors="coerce")
    offers_df = offers_df.dropna(subset=["player_id", "offer_amount"])

    return offers_df[_offer_columns()].reset_index(drop=True)


def _offer_columns():
    return [
        "offer_key",
        "league_id",
        "own_username",
        "offer_id",
        "player_id",
        "player_name",
        "offer_amount",
        "market_value",
        "expires_at",
        "status",
        "observed_at",
        "source",
        "raw_json",
    ]


def _iter_offer_candidates(payload):
    if isinstance(payload, list):
        for item in payload:
            yield from _iter_offer_candidates(item)
        return

    if not isinstance(payload, dict):
        return

    if _looks_like_offer_candidate(payload):
        yield payload

    for value in payload.values():
        if isinstance(value, (dict, list)):
            yield from _iter_offer_candidates(value)


def _looks_like_offer_candidate(candidate):
    return _extract_player_id(candidate) is not None and _extract_numeric(candidate, ["offer", "amount", "value", "bid", "prc", "mvb", "trp"]) is not None


def _normalize_offer_candidate(candidate, league_id, own_username, observed_at):
    player_id = _extract_player_id(candidate)
    offer_amount = _extract_numeric(candidate, ["offer", "amount", "value", "bid", "prc", "mvb", "trp"])
    if player_id is None or offer_amount is None:
        return None

    market_value = _extract_numeric(candidate, ["marketValue", "market_value", "mv", "mvp"])
    expires_at = _extract_datetime(candidate, ["expiresAt", "exp", "exs", "dt", "until"])
    offer_id = _extract_scalar(candidate, ["offerId", "oid", "id", "i"])
    player_name = _extract_player_name(candidate)

    return {
        "offer_key": _build_offer_key(league_id, offer_id, player_id, offer_amount, expires_at),
        "league_id": int(league_id),
        "own_username": own_username,
        "offer_id": str(offer_id) if offer_id is not None else None,
        "player_id": int(player_id),
        "player_name": player_name,
        "offer_amount": float(offer_amount),
        "market_value": float(market_value) if market_value is not None else None,
        "expires_at": expires_at,
        "status": "active",
        "observed_at": observed_at,
        "source": "manager_transfer_feed",
        "raw_json": json.dumps(candidate, ensure_ascii=False, sort_keys=True),
    }


def _build_offer_key(league_id, offer_id, player_id, offer_amount, expires_at):
    if offer_id not in (None, "", "nan"):
        return f"{league_id}:{offer_id}"

    fingerprint = f"{league_id}|{player_id}|{offer_amount}|{expires_at or 'none'}"
    digest = hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()[:16]
    return f"{league_id}:derived:{digest}"


def _extract_player_id(candidate):
    direct_value = _extract_scalar(candidate, ["playerId", "player_id", "pi"])
    if direct_value is not None:
        return _coerce_int(direct_value)

    player_obj = candidate.get("player")
    if isinstance(player_obj, dict):
        return _coerce_int(_extract_scalar(player_obj, ["id", "i", "playerId", "pi"]))

    return None


def _extract_player_name(candidate):
    direct_name = _extract_scalar(candidate, ["playerName", "pn", "name"])
    if direct_name:
        return str(direct_name)

    player_obj = candidate.get("player")
    if isinstance(player_obj, dict):
        first_name = _extract_scalar(player_obj, ["firstName", "fn", "first_name"])
        last_name = _extract_scalar(player_obj, ["lastName", "ln", "last_name"])
        combined = " ".join(
            part for part in [str(first_name).strip() if first_name else "", str(last_name).strip() if last_name else ""] if part
        )
        if combined:
            return combined
        nested_name = _extract_scalar(player_obj, ["name", "pn"])
        if nested_name:
            return str(nested_name)

    return None


def _extract_numeric(candidate, keys):
    value = _extract_scalar(candidate, keys)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_datetime(candidate, keys):
    value = _extract_scalar(candidate, keys)
    if value is None:
        return None

    if isinstance(value, (int, float)):
        if value > 10_000_000_000:
            parsed = datetime.fromtimestamp(value / 1000, tz=timezone.utc)
        else:
            parsed = datetime.fromtimestamp(value, tz=timezone.utc)
        return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")

    parsed = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")


def _extract_scalar(candidate, keys):
    for key in keys:
        if key in candidate and candidate[key] not in (None, ""):
            return candidate[key]
    return None


def _coerce_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None