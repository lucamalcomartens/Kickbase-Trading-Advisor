from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import pandas as pd


OFFER_AMOUNT_KEYS = ["offer", "amount", "value", "bid", "prc", "mvb", "v", "amt", "am"]
OFFER_EXPIRY_KEYS = ["expiresAt", "exp", "exs", "until", "expiry", "expires"]
OFFER_ID_KEYS = ["offerId", "oid", "offer_id"]
OFFER_PATH_HINTS = ["offer", "bid", "bids", "mybid", "myoffer", "offers"]


def extract_current_market_offers(raw_transfer_feed, league_id, own_username):
    """Best-effort extraction of the user's currently active market offers."""

    if not raw_transfer_feed:
        return pd.DataFrame(columns=_offer_columns())

    observed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    offers = []
    seen_offer_keys = set()

    for path, candidate in _iter_offer_candidates(raw_transfer_feed):
        normalized_offer = _normalize_offer_candidate(candidate, path, league_id, own_username, observed_at)
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


def summarize_offer_feed_debug(raw_transfer_feed, limit=10):
    """Return a sanitized summary of offer-like objects to calibrate parsing with live data."""

    if not raw_transfer_feed:
        return {"candidate_count": 0, "examples": [], "structure_examples": [], "root_type": None}

    examples = []
    for path, candidate in _iter_offer_candidates(raw_transfer_feed):
        examples.append(
            {
                "path": path,
                "keys": sorted(candidate.keys()),
                "player_id": _extract_player_id(candidate),
                "player_name": _extract_player_name(candidate),
                "offer_amount": _extract_numeric(candidate, OFFER_AMOUNT_KEYS),
                "market_value": _extract_market_value(candidate),
                "expires_at": _extract_datetime(candidate, OFFER_EXPIRY_KEYS),
                "offer_id": _extract_scalar(candidate, OFFER_ID_KEYS + ["id", "i"]),
                "path_hint": _path_looks_like_offer(path),
                "sample": _sanitize_candidate(candidate),
            }
        )
        if len(examples) >= limit:
            break

    structure_examples = []
    for node_info in _iter_structure_nodes(raw_transfer_feed):
        structure_examples.append(node_info)
        if len(structure_examples) >= limit:
            break

    return {
        "candidate_count": len(examples),
        "examples": examples,
        "structure_examples": structure_examples,
        "root_type": type(raw_transfer_feed).__name__,
    }


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


def _iter_offer_candidates(payload, path="root"):
    if isinstance(payload, list):
        for index, item in enumerate(payload):
            yield from _iter_offer_candidates(item, f"{path}[{index}]")
        return

    if not isinstance(payload, dict):
        return

    if _looks_like_offer_candidate(payload, path):
        yield path, payload

    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            yield from _iter_offer_candidates(value, f"{path}.{key}")


def _iter_structure_nodes(payload, path="root"):
    if isinstance(payload, dict):
        yield {
            "path": path,
            "node_type": "dict",
            "keys": sorted(payload.keys()),
            "sample": _sanitize_candidate(payload),
        }
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                yield from _iter_structure_nodes(value, f"{path}.{key}")
    elif isinstance(payload, list):
        yield {
            "path": path,
            "node_type": "list",
            "length": len(payload),
        }
        for index, item in enumerate(payload[:10]):
            if isinstance(item, (dict, list)):
                yield from _iter_structure_nodes(item, f"{path}[{index}]")


def _looks_like_offer_candidate(candidate, path=""):
    player_id = _extract_player_id(candidate)
    offer_amount = _extract_numeric(candidate, OFFER_AMOUNT_KEYS)
    has_offer_marker = (
        _extract_scalar(candidate, OFFER_ID_KEYS + ["id", "i"]) is not None
        or _extract_datetime(candidate, OFFER_EXPIRY_KEYS) is not None
        or _path_looks_like_offer(path)
    )
    return (
        player_id is not None
        and offer_amount is not None
        and has_offer_marker
        and not _looks_like_completed_transfer(candidate, path)
    )


def _normalize_offer_candidate(candidate, path, league_id, own_username, observed_at):
    player_id = _extract_player_id(candidate)
    offer_amount = _extract_numeric(candidate, OFFER_AMOUNT_KEYS)
    if player_id is None or offer_amount is None:
        return None

    market_value = _extract_market_value(candidate)
    expires_at = _extract_datetime(candidate, OFFER_EXPIRY_KEYS)
    offer_id = _extract_scalar(candidate, OFFER_ID_KEYS + ["id", "i"])
    player_name = _extract_player_name(candidate)

    expires_at_dt = pd.to_datetime(expires_at, utc=True, errors="coerce")
    observed_at_dt = pd.to_datetime(observed_at, utc=True, errors="coerce")
    if pd.notna(expires_at_dt) and pd.notna(observed_at_dt) and expires_at_dt <= observed_at_dt:
        return None

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
        "source": f"manager_transfer_feed:{path}",
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
    direct_name = _extract_scalar(candidate, ["playerName", "pn", "name", "fullName"])
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
        nested_name = _extract_scalar(player_obj, ["name", "pn", "fullName"])
        if nested_name:
            return str(nested_name)

    return None


def _extract_market_value(candidate):
    direct_market_value = _extract_numeric(candidate, ["marketValue", "market_value", "mv", "mvp", "marketvalue", "playerMarketValue", "pmv"])
    if direct_market_value is not None:
        return direct_market_value

    player_obj = candidate.get("player")
    if isinstance(player_obj, dict):
        nested_market_value = _extract_numeric(player_obj, ["marketValue", "market_value", "mv", "mvp", "marketvalue", "value"])
        if nested_market_value is not None:
            return nested_market_value

    return None


def _path_looks_like_offer(path):
    path_lower = str(path or "").lower()
    return any(hint in path_lower for hint in OFFER_PATH_HINTS)


def _looks_like_completed_transfer(candidate, path):
    keys = {str(key).lower() for key in candidate.keys()}
    transfer_markers = {"byr", "slr", "trp", "tid"}
    return transfer_markers.issubset(keys) and not _path_looks_like_offer(path)


def _sanitize_candidate(candidate):
    sample = {}
    for key, value in candidate.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            sample[key] = value
        elif isinstance(value, dict):
            sample[key] = {nested_key: "<nested>" for nested_key in list(value.keys())[:8]}
        elif isinstance(value, list):
            sample[key] = f"<list:{len(value)}>"
    return sample


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