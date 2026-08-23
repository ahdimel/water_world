"""Phase 2 — the desalination cost engine.

`finance`     cost of capital, kept explicit rather than folded into a discount rate
`lcow`        levelised cost of water, split into the legs Israel publishes
`scale`       scale-adjusted international capex comparison (contribution §2.1)
`permitting`  approval delay and rejection risk priced as capital (contribution §2.2)
`plants`      reference plants assembled from literature.yaml
`montecarlo`  turns the parameter ranges into outcome distributions

Nothing in here writes narrative or ranks options. The framing gate (see HANDOFF §3)
stays shut until the Phase 3 supply stack exists.
"""

from ww.model import finance, lcow, montecarlo, permitting, plants, scale

__all__ = ["finance", "lcow", "montecarlo", "permitting", "plants", "scale"]
