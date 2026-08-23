"""Pydantic contracts for everything that crosses a layer boundary.

Two families live here:

* **Fetch/cache provenance** — what we pulled, from where, when, and its hash.
* **Literature parameters** — numbers that came from a document rather than a feed.
  These carry citations and uncertainty so Phase 2's Monte Carlo can consume them
  directly instead of re-deriving ranges from prose.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# --------------------------------------------------------------------------------------
# Source registry / fetch provenance
# --------------------------------------------------------------------------------------

#: How a source is obtained.
#:   api    - programmatic endpoint, fully automatic
#:   file   - stable URL to a file we download whole
#:   manual - not machine-fetchable (paywall, PDF table, prose); the value is curated
#:            into data/parameters/literature.yaml by hand, with a citation
SourceTier = Literal["api", "file", "manual"]


class SourceSpec(BaseModel):
    """Declarative description of one upstream data source."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Stable dotted identifier, e.g. 'usbr.reservoir.mead'")
    title: str
    tier: SourceTier
    url: str | None = Field(None, description="None for manual sources")
    units: str | None = None
    cadence: str | None = Field(None, description="e.g. 'daily', 'monthly', 'one-off'")
    requires_key: bool = False
    notes: str | None = None
    post_json: dict | None = Field(
        None,
        description="If set, the fetch is a POST with this JSON body instead of a GET.",
    )

    @model_validator(mode="after")
    def _url_required_unless_manual(self) -> SourceSpec:
        if self.tier != "manual" and not self.url:
            raise ValueError(f"source {self.id!r} is tier={self.tier} and must declare a url")
        return self


class FetchRecord(BaseModel):
    """Provenance stamp for one successful fetch. Written alongside every cached blob."""

    source_id: str
    url: str
    fetched_at: datetime
    sha256: str
    n_bytes: int
    ww_version: str

    def short(self) -> str:
        return f"{self.source_id}  {self.n_bytes:>10,}B  {self.sha256[:12]}  {self.fetched_at:%Y-%m-%d %H:%M}"


# --------------------------------------------------------------------------------------
# Normalised observations
# --------------------------------------------------------------------------------------


class TimeseriesPoint(BaseModel):
    """One observation in a normalised series. Deliberately narrow.

    `when` is a datetime so that hourly feeds (CAISO locational prices) share the same
    container as daily and monthly ones. Daily and monthly sources set midnight; nothing
    downstream should read meaning into the time component of those series.
    """

    model_config = ConfigDict(frozen=True)

    when: datetime
    value: float


class Timeseries(BaseModel):
    """A normalised series with its identity and units attached.

    Every source normaliser returns one of these, so downstream code never has to
    know which upstream shape it came from.
    """

    source_id: str
    label: str
    units: str
    points: list[TimeseriesPoint]

    @property
    def latest(self) -> TimeseriesPoint | None:
        return max(self.points, key=lambda p: p.when) if self.points else None

    @property
    def earliest(self) -> TimeseriesPoint | None:
        return min(self.points, key=lambda p: p.when) if self.points else None

    def __len__(self) -> int:
        return len(self.points)


# --------------------------------------------------------------------------------------
# Literature parameters
# --------------------------------------------------------------------------------------

#: How much we trust a curated number.
#:   high   - primary source, official filing or dataset
#:   medium - reputable secondary reporting, or a figure consistent across sources
#:   low    - single secondary source, or contested
#:   derived - our own arithmetic over other parameters; MUST list `derived_from`
Confidence = Literal["high", "medium", "low", "derived"]


class Citation(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    url: str | None = None
    publisher: str | None = None
    accessed: date | None = None


class Parameter(BaseModel):
    """One number lifted from a document, with everything needed to defend it.

    `low`/`high` express uncertainty. Where a source gives a single figure we still
    encourage a range, because Phase 2 samples these and a point estimate silently
    asserts certainty we do not have.
    """

    model_config = ConfigDict(frozen=True)

    id: str
    value: float
    units: str
    low: float | None = None
    high: float | None = None
    year: int | None = Field(None, description="Nominal-dollar year, where relevant")
    confidence: Confidence
    citations: list[str] = Field(default_factory=list, description="Citation ids")
    derived_from: list[str] = Field(default_factory=list, description="Parameter ids")
    notes: str | None = None

    @model_validator(mode="after")
    def _check(self) -> Parameter:
        if self.low is not None and self.high is not None and self.low > self.high:
            raise ValueError(f"parameter {self.id!r}: low {self.low} > high {self.high}")
        if self.low is not None and self.low > self.value:
            raise ValueError(f"parameter {self.id!r}: low {self.low} > value {self.value}")
        if self.high is not None and self.high < self.value:
            raise ValueError(f"parameter {self.id!r}: high {self.high} < value {self.value}")
        if self.confidence == "derived" and not self.derived_from:
            raise ValueError(f"parameter {self.id!r}: confidence='derived' requires derived_from")
        if self.confidence != "derived" and not self.citations:
            raise ValueError(f"parameter {self.id!r}: needs at least one citation")
        return self

    @property
    def has_range(self) -> bool:
        return self.low is not None or self.high is not None


class ParameterSet(BaseModel):
    """The whole curated literature file, post-validation."""

    citations: dict[str, Citation]
    parameters: dict[str, Parameter]

    @model_validator(mode="after")
    def _referential_integrity(self) -> ParameterSet:
        for p in self.parameters.values():
            for c in p.citations:
                if c not in self.citations:
                    raise ValueError(f"parameter {p.id!r} cites unknown citation {c!r}")
            for d in p.derived_from:
                if d not in self.parameters:
                    raise ValueError(f"parameter {p.id!r} derives from unknown parameter {d!r}")
        return self

    def get(self, pid: str) -> Parameter:
        try:
            return self.parameters[pid]
        except KeyError:
            raise KeyError(f"no such parameter: {pid!r}") from None
