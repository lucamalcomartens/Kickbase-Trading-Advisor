from kickbase_api.config import BASE_URL, get_json_with_token
from datetime import datetime
import requests
import os
import re


COMPETITION_CODE_MAP = {
    1: "BL1",
    2: "BL2",
    3: "PD",
}


TEAM_ALIASES = {
    "bayern munchen": "bayern munich",
    "fc bayern munchen": "bayern munich",
    "rasenballsport leipzig": "rb leipzig",
    "bayer 04 leverkusen": "bayer leverkusen",
    "borussia monchengladbach": "monchengladbach",
    "borussia m nchengladbach": "monchengladbach",
    "1 fc union berlin": "union berlin",
    "1 fsv mainz 05": "mainz",
    "tsg 1899 hoffenheim": "hoffenheim",
    "werder bremen": "bremen",
    "fc augsburg": "augsburg",
    "1 fc heidenheim 1846": "heidenheim",
    "vfl bochum 1848": "bochum",
    "1 fc koln": "koln",
    "fc koln": "koln",
    "hamburger sv": "hamburg",
    "fortuna dusseldorf": "dusseldorf",
    "sc paderborn 07": "paderborn",
    "karlsruher sc": "karlsruhe",
    "spvgg greuther furth": "furth",
    "ssv ulm 1846": "ulm",
    "real madrid cf": "real madrid",
    "fc barcelona": "barcelona",
    "atletico de madrid": "atletico madrid",
    "athletic club": "athletic bilbao",
    "real sociedad de futbol": "real sociedad",
    "villarreal cf": "villarreal",
    "real betis balompie": "real betis",
    "sevilla fc": "sevilla",
    "valencia cf": "valencia",
    "girona fc": "girona",
}

# All other functions that don't fit anywhere else

def get_all_teams(token, competition_id):
    """Get all teams in a competition."""

    url = f"{BASE_URL}/competitions/{competition_id}/table"
    data = get_json_with_token(url, token)

    teams = [
        {
            "team_id": item.get("tid"),   # Team-ID
            "team_name": item.get("tn")   # Team Name
        }
        for item in data.get("it", [])
    ]

    return teams

def get_matchdays(token, competition_id):
    """Get all matchdays in a competition with the latest date for each matchday."""

    url = f"{BASE_URL}/competitions/{competition_id}/matchdays"
    data = get_json_with_token(url, token)

    matches = [
        {
            "day": match.get("day"),
            "date": match.get("dt")
        }
        for item in data.get("it", [])
        for match in item.get("it", [])
    ]

    max_dates_per_day = {}
    for m in matches:
        day = m["day"]
        date = datetime.fromisoformat(m["date"].replace("Z", "+00:00"))  # ISO -> datetime
        if day not in max_dates_per_day or date > max_dates_per_day[day]:
            max_dates_per_day[day] = date

    result = [{"day": day, "date": max_dates_per_day[day].isoformat()} for day in sorted(max_dates_per_day)]

    return result


def normalize_team_name(team_name):
    """Normalize team names so Kickbase and external fixture feeds can be matched reliably."""

    replacements = {
        "ä": "a",
        "ö": "o",
        "ü": "u",
        "ß": "ss",
        "é": "e",
        "è": "e",
        "á": "a",
        "à": "a",
        "ó": "o",
        "ò": "o",
        "í": "i",
        "ì": "i",
        "ú": "u",
        "ù": "u",
        "ñ": "n",
        "ç": "c",
    }

    normalized = str(team_name).lower()
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)

    normalized = re.sub(r"[^a-z0-9 ]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    return TEAM_ALIASES.get(normalized, normalized)


def get_fixture_context(competition_id):
    """Fetch the next scheduled match and simple fixture difficulty per team via football-data.org."""

    api_key = os.getenv("FOOTBALL_DATA_API_KEY")
    competition_code = COMPETITION_CODE_MAP.get(competition_id)

    if not api_key or not competition_code:
        return {}

    headers = {"X-Auth-Token": api_key}

    try:
        matches_response = requests.get(
            f"https://api.football-data.org/v4/competitions/{competition_code}/matches",
            headers=headers,
            params={"status": "SCHEDULED"},
            timeout=20,
        )
        matches_response.raise_for_status()
        matches = matches_response.json().get("matches", [])

        standings_response = requests.get(
            f"https://api.football-data.org/v4/competitions/{competition_code}/standings",
            headers=headers,
            timeout=20,
        )
        standings_response.raise_for_status()
        standings = standings_response.json().get("standings", [])
    except Exception as error:
        print(f"Hinweis: Externer Spielplan konnte nicht geladen werden: {error}")
        return {}

    ranking_by_team = {}
    for standing in standings:
        for row in standing.get("table", []):
            team_name = row.get("team", {}).get("name")
            position = row.get("position")
            if team_name and position is not None:
                ranking_by_team[normalize_team_name(team_name)] = position

    fixture_context = {}

    for match in matches:
        utc_date = match.get("utcDate")
        home_name = match.get("homeTeam", {}).get("name")
        away_name = match.get("awayTeam", {}).get("name")
        if not utc_date or not home_name or not away_name:
            continue

        kickoff = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
        home_key = normalize_team_name(home_name)
        away_key = normalize_team_name(away_name)

        _store_fixture_entry(
            fixture_context,
            home_key,
            kickoff,
            away_name,
            "home",
            ranking_by_team.get(away_key),
        )
        _store_fixture_entry(
            fixture_context,
            away_key,
            kickoff,
            home_name,
            "away",
            ranking_by_team.get(home_key),
        )

    return fixture_context


def enrich_with_fixture_context(df, fixture_context):
    """Attach optional next-opponent and difficulty data to market and squad dataframes."""

    if df.empty:
        return df.copy()

    enriched_df = df.copy()
    enriched_df["next_opponent"] = None
    enriched_df["home_or_away"] = None
    enriched_df["next_match_date"] = None
    enriched_df["fixture_difficulty"] = None

    if not fixture_context:
        return enriched_df

    for index, team_name in enriched_df["team_name"].fillna("").items():
        team_context = fixture_context.get(normalize_team_name(team_name))
        if not team_context:
            continue

        enriched_df.at[index, "next_opponent"] = team_context.get("next_opponent")
        enriched_df.at[index, "home_or_away"] = team_context.get("home_or_away")
        enriched_df.at[index, "next_match_date"] = team_context.get("next_match_date")
        enriched_df.at[index, "fixture_difficulty"] = team_context.get("fixture_difficulty")

    return enriched_df


def _store_fixture_entry(fixture_context, team_key, kickoff, opponent_name, home_or_away, opponent_rank):
    existing_entry = fixture_context.get(team_key)
    if existing_entry is not None and existing_entry["kickoff_dt"] <= kickoff:
        return

    fixture_context[team_key] = {
        "next_opponent": opponent_name,
        "home_or_away": home_or_away,
        "next_match_date": kickoff.isoformat(),
        "fixture_difficulty": rank_to_fixture_difficulty(opponent_rank),
        "kickoff_dt": kickoff,
    }


def rank_to_fixture_difficulty(rank):
    """Translate opponent table position into a compact difficulty label."""

    if rank is None:
        return "unknown"
    if rank <= 4:
        return "hard"
    if rank <= 10:
        return "medium"
    return "good"

def get_achievement_reward(token, league_id, achievement_id):
    """Get the reward and how often this was achieved by the user for a specific achievement in a league."""

    url = f"{BASE_URL}/leagues/{league_id}/user/achievements/{achievement_id}"
    data = get_json_with_token(url, token)

    # Some achievements do not expose a monetary reward in the API response.
    # Treat missing values as zero so they are ignored instead of spamming warnings.
    amount = data.get("ac", 0)
    reward = data.get("er", 0)

    return amount, reward
