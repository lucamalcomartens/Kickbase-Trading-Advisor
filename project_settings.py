from __future__ import annotations

from dataclasses import dataclass, field
import os

import pandas as pd


ANALYSIS_HISTORY_PATH = "analysis_history.json"
RUN_OUTPUT_DIR = "run_outputs"


@dataclass(frozen=True)
class SystemSettings:
    last_mv_values: int = 365
    last_pfm_values: int = 50
    features: list[str] = field(
        default_factory=lambda: [
            "p",
            "mv",
            "days_to_next",
            "mv_change_1d",
            "mv_trend_1d",
            "mv_change_3d",
            "mv_vol_3d",
            "mv_trend_7d",
            "market_divergence",
        ]
    )
    target: str = "mv_target_clipped"
    analysis_history_path: str = ANALYSIS_HISTORY_PATH
    run_output_dir: str = RUN_OUTPUT_DIR


@dataclass(frozen=True)
class UserSettings:
    competition_ids: list[int]
    league_name: str
    start_budget: int
    league_start_date: str
    email: str | None


def load_user_settings() -> UserSettings:
    """Load the user-managed project settings from the current environment and defaults."""

    return UserSettings(
        competition_ids=[1],
        league_name="Spitz",
        start_budget=50_000_000,
        league_start_date="2025-12-22",
        email=os.getenv("EMAIL_USER"),
    )


def configure_display() -> None:
    """Apply dataframe display defaults used by reports and prompt preparation."""

    pd.options.display.float_format = lambda value: "{:,.0f}".format(value).replace(",", ".")
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", 1000)