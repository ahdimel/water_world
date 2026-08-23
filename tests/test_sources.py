"""Parser tests against fixture payloads. No network access.

Each fixture is a trimmed copy of a real response shape, so a change in upstream format
shows up as a parser test failure rather than as silently empty data in a chart.
"""

from __future__ import annotations

import io
import json
import zipfile

import pytest

from ww.sources import REGISTRY, bls, caiso, fetchable, get, usbr

# --------------------------------------------------------------------------------------
# USBR
# --------------------------------------------------------------------------------------

USBR_CSV = b"""datetime,storage
2026-08-19,5225877.72
2026-08-20,5216988.46
2026-08-21,5209772.47
"""

USBR_CSV_DIRTY = b"""datetime,storage
2026-08-19,5225877.72
2026-08-20,
bad-date,123
2026-08-21,NaN
2026-08-22,5209772.47
"""


class TestUSBR:
    def test_parses_clean_csv(self):
        (ts,) = usbr.parse_storage_csv(USBR_CSV, "usbr.reservoir.test", "Test")
        assert len(ts) == 3
        assert ts.units == "acre-feet"
        assert ts.latest.value == pytest.approx(5209772.47)

    def test_skips_unparseable_rows_without_losing_the_series(self):
        (ts,) = usbr.parse_storage_csv(USBR_CSV_DIRTY, "usbr.reservoir.test", "Test")
        # Blank, bad-date and NaN rows dropped; the two good rows survive.
        assert len(ts) == 2

    def test_registry_covers_every_declared_reservoir(self):
        ids = {s.spec.id for s in usbr.build()}
        assert len(ids) == len(usbr.RESERVOIRS)
        assert "usbr.reservoir.lake_mead" in ids
        assert "usbr.reservoir.lake_powell" in ids

    def test_headline_reservoirs_sort_first(self):
        built = usbr.build()
        assert {built[0].spec.id, built[1].spec.id} == {
            "usbr.reservoir.lake_mead",
            "usbr.reservoir.lake_powell",
        }


# --------------------------------------------------------------------------------------
# BLS
# --------------------------------------------------------------------------------------


def _bls_payload(status="REQUEST_SUCCEEDED"):
    return json.dumps(
        {
            "status": status,
            "message": [],
            "Results": {
                "series": [
                    {
                        "seriesID": "CUUR0000SEHG",
                        "data": [
                            {"year": "2025", "period": "M12", "value": "330.0"},
                            {"year": "2025", "period": "M11", "value": "329.0"},
                            {"year": "2025", "period": "M13", "value": "325.0"},
                        ],
                    },
                    {
                        "seriesID": "CUUR0000SA0",
                        "data": [{"year": "2025", "period": "M12", "value": "310.0"}],
                    },
                ]
            },
        }
    ).encode()


class TestBLS:
    def test_returns_one_series_per_series_id(self):
        out = bls.parse_api_json(_bls_payload())
        assert {ts.source_id for ts in out} == {
            "bls.cpi.CUUR0000SEHG",
            "bls.cpi.CUUR0000SA0",
        }

    def test_drops_annual_average_period_m13(self):
        water = next(
            ts for ts in bls.parse_api_json(_bls_payload())
            if ts.source_id.endswith("SEHG")
        )
        # M13 is an annual average and would corrupt a monthly series.
        assert len(water) == 2

    def test_sorts_ascending(self):
        water = next(
            ts for ts in bls.parse_api_json(_bls_payload())
            if ts.source_id.endswith("SEHG")
        )
        assert water.points[0].when < water.points[1].when

    def test_failed_request_raises(self):
        with pytest.raises(ValueError, match="did not succeed"):
            bls.parse_api_json(_bls_payload(status="REQUEST_NOT_PROCESSED"))

    def test_stitch_merges_chunks_with_later_winning(self):
        early = bls.parse_api_json(_bls_payload())
        late = json.loads(_bls_payload())
        late["Results"]["series"][0]["data"] = [
            {"year": "2025", "period": "M12", "value": "999.0"}
        ]
        merged = bls.stitch(
            [early, bls.parse_api_json(json.dumps(late).encode())], "CUUR0000SEHG"
        )
        assert merged.latest.value == pytest.approx(999.0)

    def test_stitch_raises_on_absent_series(self):
        with pytest.raises(KeyError, match="not present"):
            bls.stitch([bls.parse_api_json(_bls_payload())], "NOSUCHSERIES")

    def test_decade_chunks_respect_the_ten_year_api_cap(self):
        for start, end in bls.DECADES:
            assert end - start <= 9

    def test_flatfile_route_refuses_without_opt_in(self, monkeypatch):
        monkeypatch.delenv("WW_CONTACT_EMAIL", raising=False)
        with pytest.raises(RuntimeError, match="WW_CONTACT_EMAIL"):
            bls.flatfile_spec()


# --------------------------------------------------------------------------------------
# CAISO
# --------------------------------------------------------------------------------------


def _caiso_zip():
    rows = [
        "INTERVALSTARTTIME_GMT,OPR_DT,OPR_HR,NODE,LMP_TYPE,MW",
        "2026-08-01T09:00:00-00:00,2026-08-01,3,TH_SP15_GEN-APND,LMP,43.56",
        "2026-08-01T10:00:00-00:00,2026-08-01,4,TH_SP15_GEN-APND,LMP,-12.30",
        "2026-08-01T10:00:00-00:00,2026-08-01,4,TH_SP15_GEN-APND,MCC,1.00",
    ]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("prc_lmp.csv", "\n".join(rows))
    return buf.getvalue()


class TestCAISO:
    def test_extracts_total_lmp_only(self):
        (ts,) = caiso.parse_lmp_zip(_caiso_zip(), "caiso.test", "Test")
        # The MCC component row must not be counted as a price observation.
        assert len(ts) == 2
        assert ts.units == "USD/MWh"

    def test_preserves_negative_prices(self):
        (ts,) = caiso.parse_lmp_zip(_caiso_zip(), "caiso.test", "Test")
        # Negative midday prices are the whole point of the flexibility question;
        # clamping or dropping them would erase the effect being measured.
        assert min(p.value for p in ts.points) == pytest.approx(-12.30)

    def test_rejects_payload_without_csv(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("readme.txt", "nope")
        with pytest.raises(ValueError, match="no CSV"):
            caiso.parse_lmp_zip(buf.getvalue(), "caiso.test", "Test")

    def test_window_longer_than_cap_is_refused(self):
        from datetime import datetime

        with pytest.raises(ValueError, match="caps queries"):
            caiso.build_url(datetime(2026, 1, 1), datetime(2026, 3, 1))

    def test_no_windows_registered_by_default(self):
        assert caiso.build() == []


# --------------------------------------------------------------------------------------
# Registry
# --------------------------------------------------------------------------------------


class TestRegistry:
    def test_ids_are_unique(self):
        assert len(REGISTRY) == len({s.spec.id for s in REGISTRY.values()})

    def test_manual_sources_are_not_fetchable(self):
        assert all(s.spec.tier != "manual" for s in fetchable())

    def test_manual_sources_are_declared(self):
        manual = [s for s in REGISTRY.values() if s.spec.tier == "manual"]
        assert len(manual) >= 5, "manual inventory should stay complete"

    def test_unknown_id_gives_actionable_error(self):
        with pytest.raises(KeyError, match="python -m ww sources"):
            get("no.such.source")
