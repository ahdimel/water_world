"""Contract tests: the validation rules that keep bad evidence out of the analysis."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ww.schemas import Citation, Parameter, ParameterSet, SourceSpec


def _param(**kw):
    base = dict(
        id="x.y", value=1.0, units="USD", confidence="high", citations=["c1"]
    )
    base.update(kw)
    return Parameter(**base)


class TestSourceSpec:
    def test_non_manual_source_requires_url(self):
        with pytest.raises(ValidationError, match="must declare a url"):
            SourceSpec(id="a.b", title="t", tier="api")

    def test_manual_source_may_omit_url(self):
        spec = SourceSpec(id="a.b", title="t", tier="manual")
        assert spec.url is None

    def test_post_json_marks_a_post_request(self):
        spec = SourceSpec(
            id="a.b", title="t", tier="api", url="https://x", post_json={"k": "v"}
        )
        assert spec.post_json == {"k": "v"}


class TestParameter:
    def test_low_above_high_rejected(self):
        with pytest.raises(ValidationError, match="low .* > high"):
            _param(low=5.0, high=1.0, value=3.0)

    def test_low_above_value_rejected(self):
        with pytest.raises(ValidationError, match="low .* > value"):
            _param(value=1.0, low=2.0)

    def test_high_below_value_rejected(self):
        with pytest.raises(ValidationError, match="high .* < value"):
            _param(value=10.0, high=2.0)

    def test_derived_requires_lineage(self):
        with pytest.raises(ValidationError, match="requires derived_from"):
            _param(confidence="derived", citations=[])

    def test_non_derived_requires_citation(self):
        with pytest.raises(ValidationError, match="needs at least one citation"):
            _param(citations=[])

    def test_has_range_reflects_bounds(self):
        assert _param(low=0.5).has_range
        assert not _param().has_range


class TestParameterSet:
    def _set(self, params):
        return ParameterSet(
            citations={"c1": Citation(id="c1", title="T")},
            parameters={p.id: p for p in params},
        )

    def test_dangling_citation_rejected(self):
        with pytest.raises(ValidationError, match="unknown citation"):
            self._set([_param(citations=["nope"])])

    def test_dangling_derivation_rejected(self):
        with pytest.raises(ValidationError, match="unknown parameter"):
            self._set(
                [_param(id="a", confidence="derived", citations=[], derived_from=["ghost"])]
            )

    def test_valid_set_round_trips(self):
        ps = self._set([_param(id="a"), _param(id="b", confidence="derived",
                                               citations=[], derived_from=["a"])])
        assert ps.get("b").derived_from == ["a"]

    def test_get_unknown_raises_keyerror(self):
        ps = self._set([_param(id="a")])
        with pytest.raises(KeyError, match="no such parameter"):
            ps.get("missing")
