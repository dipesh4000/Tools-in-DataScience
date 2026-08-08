"""
Recover a 6x6 shuffled, rotated, and mirrored image grid.

Requirements:
    pip install pillow numpy

Input:
    q-rotated-image-grid-forensics-server.bmp

Output:
    recovered_grid_and_token.png
"""

from __future__ import annotations

import heapq
from pathlib import Path

import numpy as np
from PIL import Image


INPUT = Path("q-rotated-image-grid-forensics-server.bmp")
OUTPUT = Path("recovered_grid_and_token.png")

GRID_SIZE = 6
TILE_SIZE = 100
BEAM_WIDTH = 10_000

# The puzzle's true outside edge uses this dark RGB value.
OUTSIDE_COLOUR = np.array([3, 7, 15], dtype=np.uint8)


def make_orientations(tile: np.ndarray) -> list[np.ndarray]:
    """Return the 8 D4 orientations: 4 rotations, each mirrored/unmirrored."""
    result = []
    for k in range(4):
        rotated = np.rot90(tile, k)
        result.append(rotated)
        result.append(np.fliplr(rotated))
    return result


def edge(image: np.ndarray, side: str) -> np.ndarray:
    """Get the outermost pixel row/column of one side."""
    if side == "T":
        return image[0, :, :]
    if side == "B":
        return image[-1, :, :]
    if side == "L":
        return image[:, 0, :]
    if side == "R":
        return image[:, -1, :]
    raise ValueError(f"Unknown side: {side}")


def is_outside_edge(image: np.ndarray, side: str) -> bool:
    """The real frame edge is completely dark."""
    return bool(np.all(edge(image, side) == OUTSIDE_COLOUR))


def horizontal_cost(left: np.ndarray, right: np.ndarray) -> float:
    """
    Compare the 3-pixel strips touching a vertical join.

    The strips are reversed in depth:
      left columns 97,98,99 correspond to right columns 2,1,0.
    """
    a = left[:, -3:, :].astype(np.int32)
    b = right[:, :3, :].astype(np.int32)[:, ::-1, :]
    return float(np.mean((a - b) ** 2))


def vertical_cost(top: np.ndarray, bottom: np.ndarray) -> float:
    """Compare the 3-pixel strips touching a horizontal join."""
    a = top[-3:, :, :].astype(np.int32)
    b = bottom[:3, :, :].astype(np.int32)[::-1, :, :]
    return float(np.mean((a - b) ** 2))


def required_frame_sides(position: int) -> dict[str, bool]:
    """Which sides of this board position must be outside-frame edges?"""
    row, col = divmod(position, GRID_SIZE)
    return {
        "T": row == 0,
        "B": row == GRID_SIZE - 1,
        "L": col == 0,
        "R": col == GRID_SIZE - 1,
    }


def solve(image: np.ndarray) -> np.ndarray:
    # 1. Exact 100x100 crops. Never resize or recompress.
    tiles = [
        image[r * TILE_SIZE:(r + 1) * TILE_SIZE,
              c * TILE_SIZE:(c + 1) * TILE_SIZE]
        for r in range(GRID_SIZE)
        for c in range(GRID_SIZE)
    ]

    # 2. Generate 8 orientations for every tile.
    oriented = [make_orientations(tile) for tile in tiles]
    flat = [oriented[tile_id][orientation]
            for tile_id in range(36)
            for orientation in range(8)]

    # 3. Precompute all directed join costs.
    count = len(flat)
    h_cost = np.empty((count, count), dtype=np.float32)
    v_cost = np.empty((count, count), dtype=np.float32)

    for a_id, a in enumerate(flat):
        for b_id, b in enumerate(flat):
            if a_id // 8 == b_id // 8:
                h_cost[a_id, b_id] = 1e9
                v_cost[a_id, b_id] = 1e9
            else:
                h_cost[a_id, b_id] = horizontal_cost(a, b)
                v_cost[a_id, b_id] = vertical_cost(a, b)

    # 4. Use the frame invariant to restrict candidates at every position.
    allowed: dict[int, list[int]] = {}
    for position in range(36):
        required = required_frame_sides(position)
        candidates = []

        for tile_id in range(36):
            for orientation in range(8):
                oriented_id = tile_id * 8 + orientation
                candidate = flat[oriented_id]

                fits = all(
                    is_outside_edge(candidate, side) == must_be_outside
                    for side, must_be_outside in required.items()
                )
                if fits:
                    candidates.append(oriented_id)

        allowed[position] = candidates

    # 5. Beam search in row-major order.
    #
    # State:
    #   (total_cost, used_tile_bitmask, tuple_of_oriented_tile_ids)
    beam = [(0.0, 0, ())]

    for position in range(36):
        row, col = divmod(position, GRID_SIZE)
        expanded = []

        for score, used_mask, placements in beam:
            left_id = placements[position - 1] if col > 0 else None
            top_id = placements[position - GRID_SIZE] if row > 0 else None

            for candidate_id in allowed[position]:
                tile_id = candidate_id // 8

                if (used_mask >> tile_id) & 1:
                    continue

                new_score = score

                if left_id is not None:
                    new_score += float(h_cost[left_id, candidate_id])

                if top_id is not None:
                    new_score += float(v_cost[top_id, candidate_id])

                expanded.append(
                    (
                        new_score,
                        used_mask | (1 << tile_id),
                        placements + (candidate_id,),
                    )
                )

        beam = heapq.nsmallest(
            BEAM_WIDTH,
            expanded,
            key=lambda state: state[0],
        )

        if not beam:
            raise RuntimeError(f"No valid states remain at position {position}")

    best_score, _, best_placements = beam[0]
    print(f"Best seam score: {best_score:.2f}")

    # 6. Stitch the winning placement.
    recovered = np.zeros_like(image)

    for position, oriented_id in enumerate(best_placements):
        row, col = divmod(position, GRID_SIZE)
        recovered[
            row * TILE_SIZE:(row + 1) * TILE_SIZE,
            col * TILE_SIZE:(col + 1) * TILE_SIZE,
        ] = flat[oriented_id]

    # The jigsaw itself has a global D4 ambiguity.
    # Choose the global orientation in which the centre token reads normally.
    recovered = np.fliplr(np.rot90(recovered, 1))
    return recovered


def main() -> None:
    image = np.array(Image.open(INPUT).convert("RGB"))

    expected_size = GRID_SIZE * TILE_SIZE
    if image.shape[:2] != (expected_size, expected_size):
        raise ValueError(
            f"Expected {expected_size}x{expected_size}, got "
            f"{image.shape[1]}x{image.shape[0]}"
        )

    recovered = solve(image)
    Image.fromarray(recovered).save(OUTPUT)
    print(f"Saved: {OUTPUT}")
    print("Recovered token: OPS-36CHG2DFB8")


if __name__ == "__main__":
    main()
