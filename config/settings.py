from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
RUN_OUTPUTS_DIR = DATA_DIR / "run_outputs"
TRAINING_DATA_DIR = DATA_DIR / "training"
EXTERNAL_CACHE_DIR = DATA_DIR / "external_cache"
API_FOOTBALL_CACHE_DIR = EXTERNAL_CACHE_DIR / "api_football"
ANALYSIS_HISTORY_FILE = DATA_DIR / "analysis_history.json"
DATABASE_FILE = DATA_DIR / "player_data_total.db"
BUY_TRAINING_DATASET_FILE = TRAINING_DATA_DIR / "buy_training_dataset.csv"

ANALYSIS_HISTORY_PATH = str(ANALYSIS_HISTORY_FILE)
RUN_OUTPUT_DIR = str(RUN_OUTPUTS_DIR)
DATABASE_PATH = str(DATABASE_FILE)
REPO_REPORTS_DIR = str(REPORTS_DIR)
API_FOOTBALL_CACHE_PATH = str(API_FOOTBALL_CACHE_DIR)
TRAINING_DATA_PATH = str(TRAINING_DATA_DIR)
BUY_TRAINING_DATASET_PATH = str(BUY_TRAINING_DATASET_FILE)


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
    database_path: str = DATABASE_PATH
    repo_reports_dir: str = REPO_REPORTS_DIR
    api_football_cache_path: str = API_FOOTBALL_CACHE_PATH
    training_data_path: str = TRAINING_DATA_PATH
    buy_training_dataset_path: str = BUY_TRAINING_DATASET_PATH


@dataclass(frozen=True)
class UserSettings:
    competition_ids: list[int]
    league_name: str
    start_budget: int
    league_start_date: str
    email: str | None


def ensure_runtime_directories() -> None:
    """Ensure runtime directories exist before reading or writing generated files."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RUN_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    TRAINING_DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    EXTERNAL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    API_FOOTBALL_CACHE_DIR.mkdir(parents=True, exist_ok=True)


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
