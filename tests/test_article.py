"""The article build: every number comes from the model, and nothing is left unfilled.

Skipped when the data cache is empty (the reservoir and CPI charts read it).
"""

from __future__ import annotations

import json
import re

import pytest

from ww import cache, sources


@pytest.fixture(scope="module")
def page(tmp_path_factory):
    if not cache.is_cached(sources.get("usbr.reservoir.lake_mead").spec):
        pytest.skip("data cache not populated")
    from ww.article import build

    out = build.build(tmp_path_factory.mktemp("article") / "article.html")
    return out.read_text()


def test_no_placeholder_survives(page):
    prose = page.split('<script type="application/json"')[0]
    assert not re.search(r"\$[a-z_]", prose)


def test_every_chart_slot_has_a_renderer(page):
    slots = set(re.findall(r'data-chart="([a-z]+)"', page))
    js = page.split('id="article-data"')[1]
    for slot in slots:
        assert re.search(rf"\b{slot}:", js), slot


def test_chart_data_is_valid_json(page):
    blob = page.split('<script type="application/json" id="article-data">')[1].split("</script>")[0]
    data = json.loads(blob)
    assert data["stack"] and data["curve"] and data["basemap"]["states"]


def test_byline_credits_both_authors(page):
    assert "Co-authored by ahdimel and Claude" in page


def test_headline_numbers_match_the_model(page):
    from ww.model import stack

    from ww.article import figures

    n = figures.numbers()
    assert f"{n['gap']['gap']:.1f} times" in page
    assert f"{n['gate'].p_cheaper * 100:.1f}%" in page
    assert stack.GATE_PROBABILITY == 0.9


def test_no_doubled_dollar_signs(page):
    """`$$` is the template's escape for a literal `$`; it must never reach the page."""
    assert "$$" not in page
