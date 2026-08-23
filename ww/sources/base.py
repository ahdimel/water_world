"""Source protocol: every upstream feed declares a spec and a normaliser.

A `Normaliser` turns raw cached bytes into a :class:`Timeseries`. Keeping the two
halves separate means we can re-parse historical blobs without re-fetching, which
matters when a parser bug is found after the numbers are already in a draft.
"""

from __future__ import annotations

from typing import Callable, Protocol

from ww.schemas import SourceSpec, Timeseries

#: Signature every source normaliser implements. Returns a *list* because one upstream
#: payload often carries several series (a BLS call returns every series id requested).
Normaliser = Callable[[bytes], list[Timeseries]]


class Source(Protocol):
    spec: SourceSpec

    def normalise(self, raw: bytes) -> list[Timeseries]: ...


class SimpleSource:
    """A source that is fully described by a spec plus a parsing function."""

    def __init__(self, spec: SourceSpec, normaliser: Normaliser) -> None:
        self.spec = spec
        self._normaliser = normaliser

    def normalise(self, raw: bytes) -> list[Timeseries]:
        return self._normaliser(raw)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<SimpleSource {self.spec.id} tier={self.spec.tier}>"


class ManualSource:
    """A source that cannot be fetched — recorded so the registry stays honest.

    Several of the numbers this project depends on live in PDFs, rate schedules, or
    paywalled databases. Declaring them here (rather than omitting them) keeps the
    registry a complete inventory of what the analysis rests on.
    """

    def __init__(self, spec: SourceSpec) -> None:
        assert spec.tier == "manual"
        self.spec = spec

    def normalise(self, raw: bytes) -> list[Timeseries]:  # pragma: no cover  # noqa: ARG002
        raise NotImplementedError(
            f"{self.spec.id!r} is manual; its values live in data/parameters/literature.yaml"
        )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<ManualSource {self.spec.id}>"
