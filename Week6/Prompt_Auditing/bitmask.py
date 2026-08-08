"""
bitmask.py

Exhaustive search using Bitmask Enumeration.

Given the NumPy arrays from preprocess.py,
find the shortest prompt satisfying

Macro Mean >= target_mean
Model Floor >= target_floor
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# --------------------------------------------------
# Result Object
# --------------------------------------------------

@dataclass(slots=True)
class SearchResult:

    ids: list[str]

    names: list[str]

    word_count: int

    scores: np.ndarray

    mean: float

    floor: float

    mask: int


# --------------------------------------------------
# Helper
# --------------------------------------------------

def evaluate_mask(
    mask: int,
    data: dict,
    base_scores: np.ndarray,
):
    """
    Evaluate one subset.

    Returns

    scores
    word_count
    """

    scores = base_scores.copy()

    wc = 0

    N = data["N"]

    word_count = data["word_count"]

    effects = data["effects"]

    # -----------------------------
    # Individual fragments
    # -----------------------------

    for i in range(N):

        if mask & (1 << i):

            wc += word_count[i]

            scores += effects[i]

    # -----------------------------
    # Pair bonuses
    # -----------------------------

    pair_i = data["pair_i"]

    pair_j = data["pair_j"]

    pair_bonus = data["pair_bonus"]

    for a, b, bonus in zip(
        pair_i,
        pair_j,
        pair_bonus,
    ):

        if (
            (mask & (1 << a))
            and
            (mask & (1 << b))
        ):

            scores += bonus

    return scores, wc


# --------------------------------------------------
# Search
# --------------------------------------------------

def find_best_prompt(
    data: dict,
    base_scores: np.ndarray,
    target_mean: float = 97.0,
    target_floor: float = 92.0,
):
    """
    Search every subset.

    Returns SearchResult
    """

    N = data["N"]

    ids = data["ids"]

    names = data["names"]

    best_result = None

    best_wc = np.inf

    total_masks = 1 << N

    for mask in range(total_masks):

        scores, wc = evaluate_mask(
            mask,
            data,
            base_scores,
        )

        mean = scores.mean()

        floor = scores.min()

        if mean < target_mean:
            continue

        if floor < target_floor:
            continue

        if wc >= best_wc:
            continue

        selected_ids = []

        selected_names = []

        for i in range(N):

            if mask & (1 << i):

                selected_ids.append(ids[i])

                selected_names.append(names[i])

        best_wc = wc

        best_result = SearchResult(

            ids=selected_ids,

            names=selected_names,

            word_count=wc,

            scores=scores,

            mean=float(mean),

            floor=float(floor),

            mask=mask,
        )

    return best_result