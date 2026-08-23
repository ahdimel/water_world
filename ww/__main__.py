"""water_world CLI.

    python -m ww sources                 list the source registry
    python -m ww fetch <id|--all>        populate the cache
    python -m ww show <id>               summarise a normalised series
    python -m ww params [--audit]        inspect curated literature parameters
    python -m ww status                  what is cached, and how stale
"""

from __future__ import annotations

import argparse
import sys

from ww import __version__, cache, params, sources


def _fmt(n: float) -> str:
    return f"{n:,.0f}" if abs(n) >= 1000 else f"{n:,.3g}"


def cmd_sources(args: argparse.Namespace) -> int:
    rows = sorted(sources.REGISTRY.values(), key=lambda s: (s.spec.tier, s.spec.id))
    tiers: dict[str, int] = {}
    for s in rows:
        tiers[s.spec.tier] = tiers.get(s.spec.tier, 0) + 1
        if args.tier and s.spec.tier != args.tier:
            continue
        cached = "cached" if cache.is_cached(s.spec) else "-"
        print(f"  {s.spec.tier:<7} {s.spec.id:<44} {cached:<7} {s.spec.title}")
    print()
    print("  " + "  ".join(f"{k}={v}" for k, v in sorted(tiers.items())))
    print(
        "  manual sources are not fetchable by design; their values live in "
        "data/parameters/literature.yaml"
    )
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    if args.all:
        targets = sources.fetchable()
    elif args.source_id:
        targets = [sources.get(args.source_id)]
    else:
        print("specify a source id or --all", file=sys.stderr)
        return 2

    failures = 0
    for s in targets:
        try:
            path = cache.fetch(s.spec, force=args.force, max_age_days=args.max_age_days)
            rec = cache.read_record(s.spec)
            size = f"{rec.n_bytes:,}B" if rec else "?"
            print(f"  ok    {s.spec.id:<44} {size}")
            if args.verbose:
                print(f"        -> {path}")
        except Exception as e:  # noqa: BLE001 - a failed source should not abort the rest
            failures += 1
            print(f"  FAIL  {s.spec.id:<44} {e}", file=sys.stderr)

    manifest_path = cache.write_manifest()
    print(f"\n  manifest: {manifest_path}")
    if failures:
        print(f"  {failures} source(s) failed", file=sys.stderr)
    return 1 if failures else 0


def cmd_show(args: argparse.Namespace) -> int:
    source = sources.get(args.source_id)
    try:
        raw = cache.load(source.spec)
    except cache.FetchError as e:
        print(f"  {e}", file=sys.stderr)
        return 1

    for ts in source.normalise(raw):
        first, last = ts.earliest, ts.latest
        print(f"\n  {ts.label}")
        print(f"    source   {ts.source_id}")
        print(f"    units    {ts.units}")
        print(f"    n        {len(ts):,}")
        if first and last:
            print(f"    span     {first.when:%Y-%m-%d} -> {last.when:%Y-%m-%d}")
            print(f"    latest   {_fmt(last.value)} {ts.units}")
            vals = [p.value for p in ts.points]
            print(f"    min/max  {_fmt(min(vals))} / {_fmt(max(vals))}")
    return 0


def cmd_params(args: argparse.Namespace) -> int:
    try:
        ps = params.load()
    except Exception as e:  # noqa: BLE001
        print(f"  literature.yaml failed validation: {e}", file=sys.stderr)
        return 1

    if args.audit:
        print(f"  {len(ps.parameters)} parameters, {len(ps.citations)} citations\n")
        uncited = params.uncited()
        print(f"  uncited (should be empty): {uncited or 'none'}")
        low = params.low_confidence()
        print(f"  low confidence ({len(low)}):")
        for pid in low:
            print(f"      {pid}")
        pointy = params.without_range()
        print(f"  point estimates, no range ({len(pointy)}):")
        for pid in pointy:
            print(f"      {pid}")
        return 0

    if args.parameter:
        p = ps.get(args.parameter)
        print(f"\n  {p.id}")
        rng = f"  [{p.low} .. {p.high}]" if p.has_range else ""
        print(f"    value        {p.value} {p.units}{rng}")
        print(f"    confidence   {p.confidence}")
        if p.citations:
            for cid in p.citations:
                c = ps.citations[cid]
                print(f"    cite         {c.title} ({c.publisher})")
                if c.url:
                    print(f"                 {c.url}")
        if p.derived_from:
            print(f"    derived from {', '.join(p.derived_from)}")
            deep = params.lineage(p.id)
            if len(deep) > len(p.derived_from):
                print(f"    lineage      {', '.join(deep)}")
        if p.notes:
            print(f"    notes        {p.notes.strip()}")
        return 0

    for pid in sorted(ps.parameters):
        p = ps.parameters[pid]
        rng = f" [{p.low}..{p.high}]" if p.has_range else ""
        print(f"  {pid:<48} {p.value:>16,.4g} {p.units:<18} {p.confidence}{rng}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    records = cache.manifest()
    if not records:
        print("  cache is empty — run `python -m ww fetch --all`")
        return 0
    total = sum(r.n_bytes for r in records)
    print(f"  {len(records)} cached source(s), {total:,} bytes\n")
    for r in records:
        print(f"  {r.short()}")
    fetchable = {s.spec.id for s in sources.fetchable()}
    missing = sorted(fetchable - {r.source_id for r in records})
    if missing:
        print(f"\n  not yet fetched ({len(missing)}):")
        for m in missing:
            print(f"      {m}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ww", description=__doc__)
    parser.add_argument("--version", action="version", version=f"water_world {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sources = sub.add_parser("sources", help="list the source registry")
    p_sources.add_argument("--tier", choices=["api", "file", "manual"])
    p_sources.set_defaults(func=cmd_sources)

    p_fetch = sub.add_parser("fetch", help="populate the cache")
    p_fetch.add_argument("source_id", nargs="?")
    p_fetch.add_argument("--all", action="store_true")
    p_fetch.add_argument("--force", action="store_true", help="re-fetch even if cached")
    p_fetch.add_argument("--max-age-days", type=int, default=None)
    p_fetch.add_argument("-v", "--verbose", action="store_true")
    p_fetch.set_defaults(func=cmd_fetch)

    p_show = sub.add_parser("show", help="summarise a normalised series")
    p_show.add_argument("source_id")
    p_show.set_defaults(func=cmd_show)

    p_params = sub.add_parser("params", help="inspect literature parameters")
    p_params.add_argument("parameter", nargs="?")
    p_params.add_argument("--audit", action="store_true")
    p_params.set_defaults(func=cmd_params)

    p_status = sub.add_parser("status", help="cache contents and age")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
