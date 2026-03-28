from __future__ import annotations

import math
import random
from typing import Sequence


def bootstrap_ci(
    data: Sequence[float],
    n_bootstrap: int = 10_000,
    confidence_level: float = 0.95,
    seed: int | None = None,
) -> tuple[float, float]:
    """Compute a bootstrap confidence interval for the mean.

    Parameters
    ----------
    data:
        Observed sample values.
    n_bootstrap:
        Number of bootstrap resamples.
    confidence_level:
        Desired confidence level (0 < cl < 1).
    seed:
        Optional RNG seed for reproducibility.

    Returns
    -------
    (lower, upper) bounds of the confidence interval.
    """
    if not data:
        return (0.0, 0.0)

    rng = random.Random(seed)
    n = len(data)
    means: list[float] = []

    for _ in range(n_bootstrap):
        sample = [rng.choice(data) for _ in range(n)]
        means.append(sum(sample) / n)

    means.sort()
    alpha = 1 - confidence_level
    lower_idx = int(math.floor((alpha / 2) * n_bootstrap))
    upper_idx = int(math.ceil((1 - alpha / 2) * n_bootstrap)) - 1
    upper_idx = min(upper_idx, len(means) - 1)

    return (means[lower_idx], means[upper_idx])


def wilson_score(
    successes: int,
    total: int,
    z: float = 1.96,
) -> tuple[float, float]:
    """Compute Wilson score confidence interval for a proportion.

    Preferred over the normal approximation when sample sizes are small or
    proportions are near 0 or 1.

    Parameters
    ----------
    successes:
        Number of observed successes.
    total:
        Total number of observations.
    z:
        Z-score for the desired confidence level (1.96 ≈ 95%).

    Returns
    -------
    (lower, upper) bounds of the Wilson confidence interval.
    """
    if total == 0:
        return (0.0, 0.0)

    p_hat = successes / total
    z2 = z * z
    denom = 1 + z2 / total
    centre = p_hat + z2 / (2 * total)
    spread = z * math.sqrt((p_hat * (1 - p_hat) + z2 / (4 * total)) / total)

    lower = (centre - spread) / denom
    upper = (centre + spread) / denom
    return (max(0.0, lower), min(1.0, upper))
