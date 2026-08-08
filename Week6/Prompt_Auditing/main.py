"""
main.py

Entry point of the project.
"""

from __future__ import annotations

import numpy as np

from preprocess import load_data
from bitmask import find_best_prompt


# --------------------------------------------------
# Configuration
# --------------------------------------------------

# Baseline scores shown in the challenge
BASE_SCORES = np.array([
    97.67,   # GPT-4o      (100 - 2.33)
    99.13,   # GPT-4.1     (100 - 0.87)
    96.99,   # GPT-4.1-mini (100 - 3.01)
    98.82    # GPT-5-mini  (100 - 1.18)
], dtype=np.float64)

TARGET_MEAN = 97.0
TARGET_FLOOR = 92.0


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("Loading datasets...")

    data = load_data(
        fragment_csv="fragments.csv",
        pair_csv="pair_bonus.csv",
    )

    print(f"{data['N']} prompt fragments loaded.")

    result = find_best_prompt(
        data=data,
        base_scores=BASE_SCORES,
        target_mean=TARGET_MEAN,
        target_floor=TARGET_FLOOR,
    )

    if result is None:
        print("No valid prompt found.")
        return

    print("\n" + "=" * 60)
    print("BEST PROMPT")
    print("=" * 60)

    for pid, text in zip(result.ids, result.names):
        print(f"{pid:<4} {text}")

    print("\nScores")
    print("-" * 60)

    print(f"GPT-4o       : {result.scores[0]:.2f}")
    print(f"GPT-4.1      : {result.scores[1]:.2f}")
    print(f"GPT-4.1-mini : {result.scores[2]:.2f}")
    print(f"GPT-5-mini   : {result.scores[3]:.2f}")

    print("\nSummary")
    print("-" * 60)

    print(f"Word Count : {result.word_count}")
    print(f"Macro Mean : {result.mean:.2f}")
    print(f"Model Floor: {result.floor:.2f}")

    print("\nSubmission")
    print("-" * 60)

    submission = (
        f"{', '.join(result.ids)}; "
        f"{result.word_count}; "
        f"{result.mean:.2f}; "
        f"{result.floor:.2f}"
    )

    print(submission)


# --------------------------------------------------

if __name__ == "__main__":
    main()