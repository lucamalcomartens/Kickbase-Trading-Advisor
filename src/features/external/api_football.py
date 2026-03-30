from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

import pandas as pd
import requests

from config.settings import API_FOOTBALL_CACHE_DIR
from kickbase_api.market_context import normalize_team_name, rank_to_fixture_difficulty


API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
API_FOOTBALL_TIMEZONE = "Europe/Berlin"
API_FOOTBALL_TIMEOUT = 20
API_FOOTBALL_CACHE_VERSION = 1
DEFAULT_CACHE_TTL_MINUTES = {
    "/leagues": 720,
    "/standings": 180,
    "/fixtures": 30,
    "/injuries": 180,
    "/teams": 720,
}
COMPETITION_LOOKUP = {
    1: {"country": "Germany", "preferred_names": ["Bundesliga"], "default_league_ids": [78]},
    2: {"country": "Germany", "preferred_names": ["2. Bundesliga"], "default_league_ids": [79]},
    3: {"country": "Spain", "preferred_names": ["La Liga"], "default_league_ids": [140]},
}


def get_api_football_context(competition_id, current_dt=None, force_refresh=False):
    """Load optional API-Football team context for fixtures and availability."""

    api_key = (os.getenv("API_FOOTBALL_KEY") or "").strip()
    requested_season = _resolve_requested_season(current_dt)
    live_reference_season = _resolve_live_reference_season(current_dt)
    season_candidates = _build_season_candidates(requested_season, competition_id)
    descriptor = COMPETITION_LOOKUP.get(competition_id)

    if not api_key:
        return _empty_context(
            "missing_api_key",
            season=requested_season,
            requested_season=requested_season,
            live_reference_season=live_reference_season,
        )
    if descriptor is None:
        return _empty_context(
            "unsupported_competition",
            season=requested_season,
            requested_season=requested_season,
            live_reference_season=live_reference_season,
        )

    last_error = None
    for season in season_candidates:
        try:
            return _load_api_football_context_for_season(
                api_key,
                competition_id,
                descriptor,
                season,
                requested_season=requested_season,
                live_reference_season=live_reference_season,
                force_refresh=force_refresh,
            )
        except Exception as error:
            last_error = error
            fallback_season = _extract_supported_season_from_error(error)
            if fallback_season is not None and fallback_season not in season_candidates:
                season_candidates.append(fallback_season)

    print(f"Hinweis: API-Football Kontext konnte nicht geladen werden: {last_error}")
    failed_season = season_candidates[-1] if season_candidates else requested_season
    return _empty_context(
        "request_failed",
        season=failed_season,
        requested_season=requested_season,
        live_reference_season=live_reference_season,
        error=str(last_error),
    )


def _load_api_football_context_for_season(
    api_key,
    competition_id,
    descriptor,
    season,
    requested_season,
    live_reference_season,
    force_refresh=False,
):
    league = _resolve_league(api_key, competition_id, descriptor, season)
    if not league:
        return _empty_context(
            "league_not_found",
            season=season,
            requested_season=requested_season,
            live_reference_season=live_reference_season,
        )

    league_id = int(league["league"]["id"])
    historical_season_mode = int(season) != int(live_reference_season)
    if historical_season_mode:
        return {
            "summary": {
                "available": False,
                "source": "api_football",
                "reason": "historical_season_only",
                "season": season,
                "requested_season": requested_season,
                "live_reference_season": live_reference_season,
                "season_fallback_applied": int(season) != int(requested_season),
                "historical_season_mode": True,
                "league_id": league_id,
                "league_name": league["league"].get("name"),
                "team_count": 0,
                "teams_loaded": 0,
                "standings_loaded": 0,
                "fixtures_loaded": 0,
                "injury_entries_loaded": 0,
                "injured_player_count": 0,
                "questionable_player_count": 0,
                "top_affected_teams": [],
                "error": (
                    f"API-Football liefert in deinem Plan keine Live-Daten fuer Season {live_reference_season}. "
                    f"Die verfuegbare Saison {season} ist historisch und wird deshalb nicht auf die Live-Strategie angewendet."
                ),
            },
            "team_context": {},
        }

    standings = _request_api_football(
        api_key,
        "/standings",
        {"league": league_id, "season": season},
        force_refresh=force_refresh,
    )
    teams = []
    if not standings:
        teams = _request_api_football(
            api_key,
            "/teams",
            {"league": league_id, "season": season},
            force_refresh=force_refresh,
        )
    fixture_window_start = datetime.now(timezone.utc).date().isoformat()
    fixture_window_end = (datetime.now(timezone.utc).date() + timedelta(days=21)).isoformat()
    fixtures = _request_api_football_with_fallbacks(
        api_key,
        "/fixtures",
        primary_params={
            "league": league_id,
            "season": season,
            "from": fixture_window_start,
            "to": fixture_window_end,
            "status": "NS-TBD-PST",
            "timezone": API_FOOTBALL_TIMEZONE,
        },
        fallback_param_sets=[
            {
                "league": league_id,
                "season": season,
                "from": fixture_window_start,
                "to": fixture_window_end,
                "timezone": API_FOOTBALL_TIMEZONE,
            },
            {
                "league": league_id,
                "season": season,
                "from": fixture_window_start,
                "to": fixture_window_end,
            },
        ],
        force_refresh=force_refresh,
    )
    injuries = _request_api_football(
        api_key,
        "/injuries",
        {
            "league": league_id,
            "season": season,
            "timezone": API_FOOTBALL_TIMEZONE,
        },
        force_refresh=force_refresh,
    )
    if not injuries:
        injuries = _request_api_football(
            api_key,
            "/injuries",
            {
                "league": league_id,
                "season": season,
                "date": datetime.now(timezone.utc).date().isoformat(),
                "timezone": API_FOOTBALL_TIMEZONE,
            },
            force_refresh=force_refresh,
        )

    rankings = _extract_rankings(standings)
    team_context = _seed_team_context_from_standings(standings, rankings)
    if not team_context and teams:
        team_context = _seed_team_context_from_teams(teams)
    team_context = _build_team_context(fixtures, rankings, team_context)
    injury_totals = _apply_injury_context(team_context, injuries)
    top_affected_teams = _build_top_affected_teams(team_context)

    return {
        "summary": {
            "available": bool(team_context),
            "source": "api_football",
            "season": season,
            "requested_season": requested_season,
            "live_reference_season": live_reference_season,
            "season_fallback_applied": int(season) != int(requested_season),
            "historical_season_mode": False,
            "league_id": league_id,
            "league_name": league["league"].get("name"),
            "team_count": len(team_context),
            "teams_loaded": len(teams),
            "standings_loaded": len(standings),
            "fixtures_loaded": len(fixtures),
            "injury_entries_loaded": len(injuries),
            "injured_player_count": injury_totals["missing"],
            "questionable_player_count": injury_totals["questionable"],
            "top_affected_teams": top_affected_teams,
        },
        "team_context": team_context,
    }


def enrich_with_api_football_context(df, api_football_context):
    """Attach optional API-Football team context to market or squad frames."""

    if df is None or df.empty:
        return df.copy() if df is not None else df

    enriched_df = df.copy()
    _ensure_api_football_columns(enriched_df)

    team_context = (api_football_context or {}).get("team_context", {})
    if not team_context:
        return enriched_df

    for index, team_name in enriched_df["team_name"].fillna("").items():
        context_row = team_context.get(normalize_team_name(team_name))
        if not context_row:
            continue

        _set_frame_value(enriched_df, index, "next_opponent", context_row.get("next_opponent"))
        _set_frame_value(enriched_df, index, "home_or_away", context_row.get("home_or_away"))
        _set_frame_value(enriched_df, index, "next_match_date", context_row.get("next_match_date"))
        _set_frame_value(enriched_df, index, "fixture_difficulty", context_row.get("fixture_difficulty"))
        _set_frame_value(enriched_df, index, "external_fixture_source", context_row.get("external_fixture_source"))
        _set_frame_value(enriched_df, index, "team_missing_count", context_row.get("team_missing_count"), overwrite=True)
        _set_frame_value(enriched_df, index, "team_questionable_count", context_row.get("team_questionable_count"), overwrite=True)
        _set_frame_value(enriched_df, index, "team_availability_score", context_row.get("team_availability_score"), overwrite=True)
        _set_frame_value(enriched_df, index, "team_availability_level", context_row.get("team_availability_level"), overwrite=True)
        _set_frame_value(enriched_df, index, "team_availability_note", context_row.get("team_availability_note"), overwrite=True)

    return enriched_df


def _ensure_api_football_columns(df):
    defaults = {
        "external_fixture_source": None,
        "team_missing_count": 0,
        "team_questionable_count": 0,
        "team_availability_score": 100.0,
        "team_availability_level": "stable",
        "team_availability_note": "Keine API-Football Hinweise vorhanden",
    }
    for column, default_value in defaults.items():
        if column not in df.columns:
            df[column] = default_value


def _set_frame_value(df, index, column, value, overwrite=False):
    if value is None or value == "":
        return
    current_value = df.at[index, column]
    if overwrite or _is_empty(current_value):
        df.at[index, column] = value


def _is_empty(value):
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    try:
        return bool(pd.isna(value))
    except TypeError:
        return False


def _resolve_requested_season(current_dt=None):
    configured_season = (os.getenv("API_FOOTBALL_SEASON") or "").strip()
    if configured_season.isdigit():
        return int(configured_season)

    return _resolve_live_reference_season(current_dt)


def _resolve_live_reference_season(current_dt=None):
    reference_dt = current_dt or datetime.now(timezone.utc)
    return reference_dt.year if reference_dt.month >= 7 else reference_dt.year - 1


def _build_season_candidates(requested_season, competition_id):
    candidates = []
    for env_key in [f"API_FOOTBALL_SEASON_{competition_id}", "API_FOOTBALL_SEASON"]:
        env_value = (os.getenv(env_key) or "").strip()
        if env_value.isdigit():
            candidates.append(int(env_value))
    candidates.append(int(requested_season))

    seen = set()
    ordered_candidates = []
    for season in candidates:
        if season in seen:
            continue
        seen.add(season)
        ordered_candidates.append(season)
    return ordered_candidates


def _extract_supported_season_from_error(error):
    message = str(error or "")
    match = re.search(r"try from\s+(\d{4})\s+to\s+(\d{4})", message, flags=re.IGNORECASE)
    if not match:
        return None
    return int(match.group(2))


def _resolve_league(api_key, competition_id, descriptor, season):
    override_key = os.getenv(f"API_FOOTBALL_LEAGUE_ID_{competition_id}")
    if override_key:
        candidate = _fetch_league_by_id(api_key, override_key, season, descriptor)
        if candidate:
            return candidate

    for league_id in descriptor.get("default_league_ids", []):
        candidate = _fetch_league_by_id(api_key, league_id, season, descriptor)
        if candidate:
            return candidate

    for preferred_name in descriptor["preferred_names"]:
        request_variants = [
            {"country": descriptor["country"], "season": season, "search": preferred_name},
            {"country": descriptor["country"], "search": preferred_name},
            {"season": season, "search": preferred_name},
            {"search": preferred_name},
        ]
        for params in request_variants:
            response = _request_api_football(api_key, "/leagues", params)
            candidate = _select_league_candidate(response, descriptor, preferred_name, season)
            if candidate:
                return candidate

    return None


def _fetch_league_by_id(api_key, league_id, season, descriptor):
    response = _request_api_football(api_key, "/leagues", {"id": league_id, "season": season})
    if not response:
        response = _request_api_football(api_key, "/leagues", {"id": league_id})

    for row in response:
        if _league_matches_descriptor(row, descriptor, season):
            return row
    return None


def _select_league_candidate(response_rows, descriptor, preferred_name, season):
    preferred_tokens = _normalize_competition_name(preferred_name)

    exact_matches = []
    fallback_matches = []
    for row in response_rows:
        if not _league_matches_descriptor(row, descriptor, season):
            continue

        league = row.get("league", {})
        league_name = str(league.get("name") or "")
        normalized_name = _normalize_competition_name(league_name)
        if normalized_name == preferred_tokens:
            exact_matches.append(row)
        elif preferred_tokens in normalized_name or normalized_name in preferred_tokens:
            fallback_matches.append(row)

    if exact_matches:
        return exact_matches[0]
    if fallback_matches:
        return fallback_matches[0]
    return None


def _league_matches_descriptor(row, descriptor, season):
    league = row.get("league", {})
    country = row.get("country", {})
    if str(league.get("type") or "").lower() != "league":
        return False
    if str(country.get("name") or "").strip().lower() != str(descriptor.get("country") or "").strip().lower():
        return False
    return _league_supports_season(row, season)


def _league_supports_season(row, season):
    seasons = row.get("seasons") or []
    if not seasons:
        return True
    for season_row in seasons:
        if int(season_row.get("year") or 0) == int(season):
            return True
    return False


def _request_api_football(api_key, endpoint, params, force_refresh=False):
    cached_payload = _read_cache(endpoint, params)
    if cached_payload is not None and not force_refresh:
        return cached_payload

    response = requests.get(
        f"{API_FOOTBALL_BASE_URL}{endpoint}",
        headers={"x-apisports-key": api_key},
        params=params,
        timeout=API_FOOTBALL_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    payload_errors = payload.get("errors") or []
    if isinstance(payload_errors, dict):
        payload_errors = [f"{key}: {value}" for key, value in payload_errors.items() if value]
    payload_errors = [str(item) for item in payload_errors if item]
    if payload_errors:
        raise ValueError(f"API-Football {endpoint} returned errors: {' | '.join(payload_errors)}")

    response_rows = payload.get("response", [])
    _write_cache(endpoint, params, response_rows)
    return response_rows


def _request_api_football_with_fallbacks(api_key, endpoint, primary_params, fallback_param_sets, force_refresh=False):
    errors = []
    request_param_sets = [primary_params, *(fallback_param_sets or [])]

    for index, params in enumerate(request_param_sets):
        try:
            return _request_api_football(api_key, endpoint, params, force_refresh=force_refresh)
        except Exception as error:
            errors.append(str(error))
            if index == len(request_param_sets) - 1:
                raise ValueError(" | ".join(errors)) from error

    return []


def _read_cache(endpoint, params):
    cache_path = _build_cache_path(endpoint, params)
    if not cache_path.exists():
        return None

    try:
        with open(cache_path, "r", encoding="utf-8") as cache_file:
            cache_payload = json.load(cache_file)
    except Exception:
        return None

    expires_at = cache_payload.get("expires_at")
    if not expires_at:
        return None

    try:
        if datetime.now(timezone.utc) >= datetime.fromisoformat(expires_at):
            return None
    except ValueError:
        return None

    return cache_payload.get("response")


def _write_cache(endpoint, params, response_rows):
    cache_dir = Path(API_FOOTBALL_CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = _build_cache_path(endpoint, params)
    ttl_minutes = DEFAULT_CACHE_TTL_MINUTES.get(endpoint, 60)
    cache_payload = {
        "version": API_FOOTBALL_CACHE_VERSION,
        "endpoint": endpoint,
        "params": params,
        "cached_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "expires_at": _expires_at(ttl_minutes),
        "response": response_rows,
    }

    with tempfile.NamedTemporaryFile("w", delete=False, dir=cache_dir, encoding="utf-8") as temp_file:
        json.dump(cache_payload, temp_file, ensure_ascii=False, indent=2)
        temp_path = Path(temp_file.name)

    temp_path.replace(cache_path)


def _build_cache_path(endpoint, params):
    normalized_params = json.dumps(params, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(f"v{API_FOOTBALL_CACHE_VERSION}|{endpoint}|{normalized_params}".encode("utf-8")).hexdigest()
    sanitized_endpoint = endpoint.strip("/").replace("/", "_") or "root"
    return Path(API_FOOTBALL_CACHE_DIR) / f"{sanitized_endpoint}_{digest}.json"


def _expires_at(ttl_minutes):
    return (datetime.now(timezone.utc) + pd.Timedelta(minutes=ttl_minutes)).replace(microsecond=0).isoformat()


def _extract_rankings(standings_rows):
    ranking_by_team = {}
    for standings_row in standings_rows:
        for league_standing in standings_row.get("league", {}).get("standings", []):
            for row in league_standing:
                team_name = row.get("team", {}).get("name")
                rank = row.get("rank")
                if team_name and rank is not None:
                    ranking_by_team[normalize_team_name(team_name)] = int(rank)
    return ranking_by_team


def _seed_team_context_from_standings(standings_rows, rankings):
    team_context = {}
    for standings_row in standings_rows:
        for league_standing in standings_row.get("league", {}).get("standings", []):
            for row in league_standing:
                team_name = row.get("team", {}).get("name")
                if not team_name:
                    continue
                team_key = normalize_team_name(team_name)
                team_context[team_key] = {
                    "team_name": team_name,
                    "next_opponent": None,
                    "home_or_away": None,
                    "next_match_date": None,
                    "fixture_difficulty": rank_to_fixture_difficulty(rankings.get(team_key)),
                    "external_fixture_source": "api_football",
                    "team_missing_count": 0,
                    "team_questionable_count": 0,
                    "team_availability_score": 100.0,
                    "team_availability_level": "stable",
                    "team_availability_note": "Keine gemeldeten Ausfaelle im API-Football Feed",
                }
    return team_context


def _seed_team_context_from_teams(team_rows):
    team_context = {}
    for row in team_rows:
        team_name = row.get("team", {}).get("name")
        if not team_name:
            continue
        team_key = normalize_team_name(team_name)
        team_context[team_key] = {
            "team_name": team_name,
            "next_opponent": None,
            "home_or_away": None,
            "next_match_date": None,
            "fixture_difficulty": None,
            "external_fixture_source": "api_football",
            "team_missing_count": 0,
            "team_questionable_count": 0,
            "team_availability_score": 100.0,
            "team_availability_level": "stable",
            "team_availability_note": "Keine gemeldeten Ausfaelle im API-Football Feed",
        }
    return team_context


def _build_team_context(fixtures_rows, rankings, team_context=None):
    team_context = dict(team_context or {})
    sorted_rows = sorted(fixtures_rows, key=lambda row: row.get("fixture", {}).get("date") or "")

    for row in sorted_rows:
        fixture = row.get("fixture", {})
        teams = row.get("teams", {})
        home_name = teams.get("home", {}).get("name")
        away_name = teams.get("away", {}).get("name")
        kickoff = fixture.get("date")
        if not home_name or not away_name or not kickoff:
            continue

        kickoff_iso = _normalize_kickoff(kickoff)
        home_key = normalize_team_name(home_name)
        away_key = normalize_team_name(away_name)

        _store_team_fixture_context(
            team_context,
            team_key=home_key,
            team_name=home_name,
            kickoff_iso=kickoff_iso,
            opponent_name=away_name,
            home_or_away="home",
            opponent_rank=rankings.get(away_key),
        )
        _store_team_fixture_context(
            team_context,
            team_key=away_key,
            team_name=away_name,
            kickoff_iso=kickoff_iso,
            opponent_name=home_name,
            home_or_away="away",
            opponent_rank=rankings.get(home_key),
        )

    return team_context


def _store_team_fixture_context(team_context, team_key, team_name, kickoff_iso, opponent_name, home_or_away, opponent_rank):
    existing = team_context.get(team_key)
    if existing is not None and str(existing.get("next_match_date") or "") <= kickoff_iso:
        return

    availability_defaults = {
        "team_name": team_name,
        "team_missing_count": 0,
        "team_questionable_count": 0,
        "team_availability_score": 100.0,
        "team_availability_level": "stable",
        "team_availability_note": "Keine gemeldeten Ausfaelle im API-Football Feed",
    }
    if existing is not None:
        availability_defaults.update(
            {
                "team_missing_count": existing.get("team_missing_count", 0),
                "team_questionable_count": existing.get("team_questionable_count", 0),
                "team_availability_score": existing.get("team_availability_score", 100.0),
                "team_availability_level": existing.get("team_availability_level", "stable"),
                "team_availability_note": existing.get("team_availability_note", availability_defaults["team_availability_note"]),
            }
        )

    team_context[team_key] = {
        **availability_defaults,
        "next_opponent": opponent_name,
        "home_or_away": home_or_away,
        "next_match_date": kickoff_iso,
        "fixture_difficulty": rank_to_fixture_difficulty(opponent_rank),
        "external_fixture_source": "api_football",
    }


def _apply_injury_context(team_context, injuries_rows):
    totals = defaultdict(int)

    for row in injuries_rows:
        team_name = row.get("team", {}).get("name")
        if not team_name:
            continue

        team_key = normalize_team_name(team_name)
        reason_text = " ".join(
            str(part or "")
            for part in [row.get("type"), row.get("reason"), row.get("player", {}).get("reason")]
        ).lower()
        is_questionable = "question" in reason_text

        team_row = team_context.setdefault(
            team_key,
            {
                "team_name": team_name,
                "next_opponent": None,
                "home_or_away": None,
                "next_match_date": None,
                "fixture_difficulty": None,
                "external_fixture_source": None,
                "team_missing_count": 0,
                "team_questionable_count": 0,
                "team_availability_score": 100.0,
                "team_availability_level": "stable",
                "team_availability_note": "Keine gemeldeten Ausfaelle im API-Football Feed",
            },
        )
        team_row["team_missing_count"] += 1
        totals["missing"] += 1
        if is_questionable:
            team_row["team_questionable_count"] += 1
            totals["questionable"] += 1

    for team_row in team_context.values():
        missing_count = int(team_row.get("team_missing_count", 0) or 0)
        questionable_count = int(team_row.get("team_questionable_count", 0) or 0)
        availability_score = max(0.0, 100.0 - (missing_count * 12.0) - (questionable_count * 5.0))
        team_row["team_availability_score"] = round(availability_score, 1)
        team_row["team_availability_level"] = _availability_level(missing_count, questionable_count)
        team_row["team_availability_note"] = _availability_note(missing_count, questionable_count)

    return totals


def _build_top_affected_teams(team_context):
    rows = []
    for row in team_context.values():
        missing_count = int(row.get("team_missing_count", 0) or 0)
        questionable_count = int(row.get("team_questionable_count", 0) or 0)
        if missing_count == 0 and questionable_count == 0:
            continue
        rows.append(
            {
                "team_name": row.get("team_name"),
                "team_missing_count": missing_count,
                "team_questionable_count": questionable_count,
                "team_availability_level": row.get("team_availability_level"),
                "team_availability_score": row.get("team_availability_score"),
                "next_opponent": row.get("next_opponent"),
                "fixture_difficulty": row.get("fixture_difficulty"),
            }
        )

    rows.sort(
        key=lambda item: (
            -(item.get("team_missing_count") or 0),
            -(item.get("team_questionable_count") or 0),
            item.get("team_name") or "",
        )
    )
    return rows[:8]


def _availability_level(missing_count, questionable_count):
    if missing_count >= 4 or (missing_count >= 2 and questionable_count >= 2):
        return "depleted"
    if missing_count >= 2 or questionable_count >= 2:
        return "watch"
    return "stable"


def _availability_note(missing_count, questionable_count):
    if missing_count == 0 and questionable_count == 0:
        return "Keine gemeldeten Ausfaelle im API-Football Feed"
    note_parts = []
    if missing_count:
        note_parts.append(f"{missing_count} missing")
    if questionable_count:
        note_parts.append(f"{questionable_count} questionable")
    return ", ".join(note_parts)


def _normalize_competition_name(value):
    normalized = str(value or "").lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _normalize_kickoff(value):
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).isoformat()


def _empty_context(reason, season=None, requested_season=None, live_reference_season=None, error=None):
    summary = {
        "available": False,
        "source": "api_football",
        "reason": reason,
        "season": season,
        "requested_season": requested_season,
        "live_reference_season": live_reference_season,
        "season_fallback_applied": bool(requested_season is not None and season is not None and int(requested_season) != int(season)),
        "historical_season_mode": bool(live_reference_season is not None and season is not None and int(live_reference_season) != int(season)),
        "league_id": None,
        "league_name": None,
        "team_count": 0,
        "teams_loaded": 0,
        "standings_loaded": 0,
        "fixtures_loaded": 0,
        "injury_entries_loaded": 0,
        "injured_player_count": 0,
        "questionable_player_count": 0,
        "top_affected_teams": [],
    }
    if error:
        summary["error"] = error
    return {"summary": summary, "team_context": {}}
