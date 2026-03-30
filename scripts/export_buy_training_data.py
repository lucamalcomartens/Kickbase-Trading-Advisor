from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import SystemSettings, ensure_runtime_directories
from features.buy_learning import build_buy_training_dataset, summarize_buy_training_dataset


def main() -> None:
    parser = _build_argument_parser()
    args = parser.parse_args()

    ensure_runtime_directories()
    system_settings = SystemSettings()
    db_path = args.db_path or system_settings.database_path
    try:
        league_id, own_username = _resolve_run_identity(db_path, args.league_id, args.own_username)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    training_df = build_buy_training_dataset(
        db_path=db_path,
        league_id=league_id,
        own_username=own_username,
        lookback_days=args.lookback_days,
        min_open_hold_days=args.min_open_hold_days,
        max_snapshot_age_hours=args.max_snapshot_age_hours,
    )
    summary = summarize_buy_training_dataset(training_df)

    output_path = Path(args.output_path or system_settings.buy_training_dataset_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    training_df.to_csv(output_path, index=False)

    print(f"Buy training dataset written to: {output_path}")
    print(f"League ID: {league_id}")
    print(f"Own username: {own_username}")
    print(f"Rows: {summary['row_count']}")
    print(f"Eligible rows: {summary['eligible_row_count']}")
    print(f"Good / Neutral / Poor: {summary['good_count']} / {summary['neutral_count']} / {summary['poor_count']}")
    print(f"Realized / Open: {summary['realized_count']} / {summary['open_count']}")
    print(f"Snapshot coverage: {summary['snapshot_coverage_pct']}%")


def _build_argument_parser():
    parser = argparse.ArgumentParser(
        description="Export a labeled buy-decision training dataset from advisor snapshots and league transfer history."
    )
    parser.add_argument("--db-path", help="Optional path to the SQLite advisor database.")
    parser.add_argument("--league-id", type=int, help="Kickbase league ID. Defaults to the latest stored advisor run.")
    parser.add_argument("--own-username", help="Kickbase username. Defaults to the latest stored advisor run.")
    parser.add_argument("--lookback-days", type=int, default=180, help="How many days of transfer history to include.")
    parser.add_argument("--min-open-hold-days", type=float, default=2.0, help="Minimum hold duration before open positions become training-eligible.")
    parser.add_argument("--max-snapshot-age-hours", type=float, default=72.0, help="Maximum allowed age of the pre-buy market snapshot.")
    parser.add_argument("--output-path", help="CSV target path. Defaults to data/training/buy_training_dataset.csv.")
    return parser


def _resolve_run_identity(db_path, league_id, own_username):
    if league_id is not None and own_username:
        return league_id, own_username

    with sqlite3.connect(db_path) as conn:
        if not _table_exists(conn, "advisor_runs"):
            raise ValueError(
                "The advisor database does not contain advisor_runs yet. Run the daily workflow once or provide a populated database."
            )
        latest_run_df = conn.execute(
            """
            SELECT league_id, own_username
            FROM advisor_runs
            WHERE league_id IS NOT NULL AND own_username IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 1
            """
        ).fetchone()

    if latest_run_df is None:
        raise ValueError("No stored advisor run found. Please provide --league-id and --own-username explicitly.")

    resolved_league_id = league_id if league_id is not None else int(latest_run_df[0])
    resolved_username = own_username if own_username else str(latest_run_df[1])
    return resolved_league_id, resolved_username


def _table_exists(connection, table_name):
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
        (table_name,),
    ).fetchone()
    return row is not None


if __name__ == "__main__":
    main()