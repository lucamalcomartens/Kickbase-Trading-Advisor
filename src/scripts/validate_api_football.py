from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parent.parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from config.secrets import load_runtime_secrets
from config.settings import ensure_runtime_directories
from features.external import get_api_football_context


def main() -> None:
    load_runtime_secrets()
    parser = argparse.ArgumentParser(description="Validate API-Football integration for a configured competition.")
    parser.add_argument("--competition-id", type=int, default=1, help="Kickbase competition id, e.g. 1 for Bundesliga")
    parser.add_argument("--force-refresh", action="store_true", help="Bypass local cache and hit the API directly")
    args = parser.parse_args()

    ensure_runtime_directories()
    context = get_api_football_context(args.competition_id, force_refresh=args.force_refresh)
    summary = context.get("summary", {})

    print("=== API-Football Validation ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    team_context = context.get("team_context", {})
    if not team_context:
        print("\nKeine Teamdaten verfügbar.")
        return

    print("\n=== Sample Team Context ===")
    for team_key, team_row in list(sorted(team_context.items()))[:8]:
        print(
            json.dumps(
                {
                    "team_key": team_key,
                    "next_opponent": team_row.get("next_opponent"),
                    "home_or_away": team_row.get("home_or_away"),
                    "next_match_date": team_row.get("next_match_date"),
                    "fixture_difficulty": team_row.get("fixture_difficulty"),
                    "team_missing_count": team_row.get("team_missing_count"),
                    "team_questionable_count": team_row.get("team_questionable_count"),
                    "team_availability_level": team_row.get("team_availability_level"),
                    "team_availability_score": team_row.get("team_availability_score"),
                },
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
