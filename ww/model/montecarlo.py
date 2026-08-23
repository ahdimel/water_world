"""Monte Carlo over the ranges in the literature file.

The project's standing rule is that a number without a range asserts a certainty we do
not have. This module is the other half of that rule: it turns the ranges into a
distribution of outcomes, so results are reported as bands rather than points.

Sampling choices, and why:

* **Triangular, not uniform.** A parameter's stated `value` is the source's central
  estimate; `low`/`high` are its bounds. Triangular respects both. Uniform would treat
  the extremes as being as likely as the central case, which throws away the one piece
  of information the source was most confident about.
* **Range-less parameters stay fixed.** `params.band()` degrades to a point, so a
  parameter with no stated uncertainty contributes none rather than getting an invented
  spread.
* **The denial rate is drawn from a Beta posterior**, not from a triangular band over
  a point estimate computed from four observations. See `permitting.denial_rate_posterior`.
* **Seeded.** Every run is reproducible from its seed; stdlib `random` only, no numpy,
  matching the rest of the project's dependency-light approach.
"""

from __future__ import annotations

import random
import statistics
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from ww import params


def sample(pid: str, rng: random.Random) -> float:
    """Draw one value for a parameter, respecting its stated range."""
    p = params.get(pid)
    low, high = params.band(pid)
    if low == high:
        return p.value
    return rng.triangular(low, high, p.value)


@dataclass(frozen=True)
class Distribution:
    """Summary of a sampled quantity."""

    name: str
    values: Sequence[float]

    @property
    def mean(self) -> float:
        return statistics.fmean(self.values)

    @property
    def median(self) -> float:
        return statistics.median(self.values)

    def percentile(self, q: float) -> float:
        """Linear-interpolated percentile, q in [0, 100]."""
        if not 0.0 <= q <= 100.0:
            raise ValueError(f"percentile must be in [0, 100], got {q}")
        ordered = sorted(self.values)
        if len(ordered) == 1:
            return ordered[0]
        pos = (len(ordered) - 1) * q / 100.0
        lower = int(pos)
        upper = min(lower + 1, len(ordered) - 1)
        weight = pos - lower
        return ordered[lower] * (1.0 - weight) + ordered[upper] * weight

    @property
    def band_90(self) -> tuple[float, float]:
        return self.percentile(5), self.percentile(95)

    def probability_above(self, threshold: float) -> float:
        """Fraction of draws exceeding a threshold — how a distribution answers a
        yes/no policy question without collapsing to a point estimate first."""
        return sum(1 for v in self.values if v > threshold) / len(self.values)

    def summary(self) -> str:
        lo, hi = self.band_90
        return (
            f"{self.name}: median {self.median:,.1f} "
            f"(90% band {lo:,.1f} to {hi:,.1f}, mean {self.mean:,.1f}, "
            f"n={len(self.values)})"
        )


def run(
    draw: Callable[[random.Random], float],
    *,
    n: int = 10_000,
    seed: int = 20260822,
    name: str = "result",
) -> Distribution:
    """Run `draw` n times against a seeded RNG and summarise the results.

    `draw` receives the RNG and returns one scalar outcome. Keeping it a callable means
    the same machinery serves LCOW, the scale gap and the permitting premium without
    any of them knowing about this module.
    """
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")
    rng = random.Random(seed)
    return Distribution(name=name, values=[draw(rng) for _ in range(n)])
