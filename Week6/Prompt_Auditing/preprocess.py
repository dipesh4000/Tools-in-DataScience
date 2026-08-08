"""
preprocess.py

Loads and validates the prompt fragment and pair bonus datasets.

Nothing in this file performs optimization.
Its only responsibility is preparing fast NumPy arrays.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ----------------------------------------------------
# Required CSV Columns
# ----------------------------------------------------

FRAGMENT_COLUMNS = [
    "ID",
    "Fragment",
    "WC",
    "4o",
    "4.1",
    "4.1m",
    "5m",
]

PAIR_COLUMNS = [
    "Fragment1",
    "Fragment2",
    "Bonus",
]


# ----------------------------------------------------
# Validation
# ----------------------------------------------------

def validate_columns(df: pd.DataFrame, expected: list[str], name: str) -> None:
    """
    Ensure every required column exists.
    """

    missing = set(expected) - set(df.columns)

    if missing:
        raise ValueError(
            f"{name} is missing columns: {sorted(missing)}"
        )


# ----------------------------------------------------
# CSV Loader
# ----------------------------------------------------

def load_csv(
    fragment_path: str,
    pair_path: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Read CSV files.
    """

    fragments = pd.read_csv(fragment_path)

    pairs = pd.read_csv(pair_path)

    validate_columns(
        fragments,
        FRAGMENT_COLUMNS,
        "fragments.csv",
    )

    validate_columns(
        pairs,
        PAIR_COLUMNS,
        "pair_bonus.csv",
    )

    return fragments, pairs


# ----------------------------------------------------
# NumPy Conversion
# ----------------------------------------------------

def convert_to_numpy(
    fragments: pd.DataFrame,
    pairs: pd.DataFrame,
) -> dict:
    """
    Convert DataFrames into NumPy arrays.

    Returns a dictionary so the caller
    does not need to know internal details.
    """

    ids = fragments["ID"].to_numpy()

    names = fragments["Fragment"].to_numpy()

    word_count = (
        fragments["WC"]
        .astype(np.int32)
        .to_numpy()
    )

    effects = (
        fragments[
            ["4o", "4.1", "4.1m", "5m"]
        ]
        .astype(np.float64)
        .to_numpy()
    )

    pair_i = (
        pairs["Fragment1"]
        .str[1:]
        .astype(np.int32)
        .to_numpy()
        - 1
    )

    pair_j = (
        pairs["Fragment2"]
        .str[1:]
        .astype(np.int32)
        .to_numpy()
        - 1
    )

    pair_bonus = (
        pairs["Bonus"]
        .astype(np.float64)
        .to_numpy()
    )

    return {

        "N": len(ids),

        "ids": ids,

        "names": names,

        "word_count": word_count,

        "effects": effects,

        "pair_i": pair_i,

        "pair_j": pair_j,

        "pair_bonus": pair_bonus,
    }


# ----------------------------------------------------
# Public API
# ----------------------------------------------------

def load_data(
    fragment_csv: str = "fragments.csv",
    pair_csv: str = "pair_bonus.csv",
):
    """
    Single public function used by main.py.

    Example
    -------
    data = load_data()
    """

    fragments, pairs = load_csv(
        fragment_csv,
        pair_csv,
    )

    return convert_to_numpy(
        fragments,
        pairs,
    )