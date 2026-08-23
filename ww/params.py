"""Loader for the curated literature parameters.

Validation is deliberately strict: a parameter with no citation, a dangling citation
reference, or a `derived` value with no lineage will fail to load rather than quietly
enter the analysis. The whole point of this file is that every number in the paper can
be defended, and the cheapest place to enforce that is at import.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from ww.schemas import Parameter, ParameterSet

LITERATURE_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "parameters" / "literature.yaml"
)

#: acre-foot -> cubic metres. Read from the parameter file rather than hardcoded so the
#: conversion has a citation like everything else.
_AF_KEY = "unit.acre_foot_m3"


@lru_cache(maxsize=1)
def load(path: Path | None = None) -> ParameterSet:
    """Load and validate the literature file. Cached; pass a path to bypass the cache."""
    target = path or LITERATURE_PATH
    if not target.exists():
        raise FileNotFoundError(f"literature parameters not found at {target}")
    raw = yaml.safe_load(target.read_text()) or {}
    return ParameterSet.model_validate(raw)


def get(pid: str) -> Parameter:
    return load().get(pid)


def value(pid: str) -> float:
    return get(pid).value


def band(pid: str) -> tuple[float, float]:
    """Return (low, high) for a parameter, falling back to the point value.

    Phase 2 sampling should call this rather than reading `.low`/`.high` directly, so
    that range-less parameters degrade to a degenerate distribution instead of raising.
    """
    p = get(pid)
    return (p.low if p.low is not None else p.value, p.high if p.high is not None else p.value)


# --------------------------------------------------------------------------------------
# Unit conversion
# --------------------------------------------------------------------------------------


def af_to_m3(acre_feet: float) -> float:
    return acre_feet * value(_AF_KEY)


def m3_to_af(cubic_metres: float) -> float:
    return cubic_metres / value(_AF_KEY)


def usd_per_m3_to_af(price: float) -> float:
    """$/m3 -> $/acre-foot. The conversion that makes desal and irrigation comparable."""
    return price * value(_AF_KEY)


def usd_per_af_to_m3(price: float) -> float:
    return price / value(_AF_KEY)


# --------------------------------------------------------------------------------------
# Audit helpers
# --------------------------------------------------------------------------------------


def uncited() -> list[str]:
    """Parameter ids with no citation and no derivation. Should always be empty."""
    ps = load()
    return [
        p.id for p in ps.parameters.values() if not p.citations and not p.derived_from
    ]


def without_range() -> list[str]:
    """Parameters asserting a point estimate. Not errors, but each is an implicit claim
    of certainty and worth reviewing before Phase 2 sampling."""
    return sorted(p.id for p in load().parameters.values() if not p.has_range)


def low_confidence() -> list[str]:
    return sorted(p.id for p in load().parameters.values() if p.confidence == "low")


def lineage(pid: str) -> list[str]:
    """Transitive `derived_from` closure for a parameter, for provenance display."""
    ps = load()
    seen: list[str] = []
    stack = list(ps.get(pid).derived_from)
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.append(current)
        stack.extend(ps.get(current).derived_from)
    return seen
