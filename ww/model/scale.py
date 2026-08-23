"""Scale-adjusted capex comparison — contribution §2.1.

The claim under test: after stripping out economies of scale, California builds
desalination capacity at a large multiple of Israeli cost, and the residual is
institutional.

Three disciplines this module enforces, each of which exists because the claim is
easy to overstate:

1. **The exponent is reported, always.** `econ.capex_scaling_exponent` (0.8, range
   0.75-0.9) drives the headline, so `gap_across_exponents` exists to make quoting a
   single number awkward.
2. **Conveyance comes out first.** Carlsbad's $203M pipeline has no Israeli counterpart
   inside Sorek's $489M; leaving it in inflates the gap.
3. **The residual is not attributed here.** `decompose` returns what is *unexplained*
   after scale, and deliberately does not split it between permitting and the general
   US administrative construction premium — the evidence does not identify that split.
   See `construction.us_admin_premium` in the literature file.
"""

from __future__ import annotations

from dataclasses import dataclass

from ww import params


def scale_capex(
    capex: float, from_capacity: float, to_capacity: float, exponent: float
) -> float:
    """Rescale a capital cost to a different plant size.

    capex ∝ Q**exponent, the standard convention. An exponent of 1.0 means no scale
    economy at all; lower values mean bigger plants are cheaper per unit.
    """
    if from_capacity <= 0 or to_capacity <= 0:
        raise ValueError("capacities must be positive")
    return capex * (to_capacity / from_capacity) ** exponent


def unit_capex(capex: float, capacity_m3_day: float) -> float:
    """$ per m3/day of installed capacity."""
    return capex / capacity_m3_day


@dataclass(frozen=True)
class ScaleGap:
    """The size of the cost gap after normalising for plant size."""

    reference: str
    subject: str
    exponent: float
    reference_capex: float
    subject_capex_at_reference_scale: float

    @property
    def gap(self) -> float:
        """How many times more the subject costs, at equal scale."""
        return self.subject_capex_at_reference_scale / self.reference_capex

    @property
    def unexplained_capex(self) -> float:
        """Absolute cost, at reference scale, not explained by scale economies."""
        return self.subject_capex_at_reference_scale - self.reference_capex


def gap(
    *,
    reference_capex: float,
    reference_capacity: float,
    subject_capex: float,
    subject_capacity: float,
    exponent: float,
    reference_name: str = "reference",
    subject_name: str = "subject",
) -> ScaleGap:
    """Normalise the subject to the reference's scale and compare capex."""
    adjusted = scale_capex(
        subject_capex, subject_capacity, reference_capacity, exponent
    )
    return ScaleGap(
        reference=reference_name,
        subject=subject_name,
        exponent=exponent,
        reference_capex=reference_capex,
        subject_capex_at_reference_scale=adjusted,
    )


def gap_across_exponents(**kwargs: object) -> dict[float, ScaleGap]:
    """The same comparison at the low, central and high scaling exponent.

    Returns a dict keyed by exponent. Callers should print all three; the project's
    standing rule is that the 5x headline never appears without this sensitivity.
    """
    p = params.get("econ.capex_scaling_exponent")
    exponents = sorted({p.low or p.value, p.value, p.high or p.value})
    kwargs.pop("exponent", None)
    return {e: gap(exponent=e, **kwargs) for e in exponents}  # type: ignore[arg-type]


@dataclass(frozen=True)
class Decomposition:
    """What is left over once each candidate explanation has taken its share.

    `institutional_residual` is reported as ONE quantity on purpose. The literature on
    US construction costs attributes the American premium mainly to administrative
    overhead, procurement practice and non-standard design — the same mechanisms Act III
    attributes to permitting. Subtracting a "US construction premium" and then claiming
    the remainder for permitting would double-count one effect under two names.
    """

    gross_gap: float
    explained_by_scale: float
    intake_premium_share: float
    institutional_residual: float

    @property
    def residual_multiple(self) -> float:
        """The gap that survives every non-institutional explanation offered."""
        return self.institutional_residual


def decompose(scale_gap: ScaleGap, *, intake_premium: float = 0.0) -> Decomposition:
    """Peel the identifiable non-institutional explanations off a scale-adjusted gap.

    `intake_premium` DEFAULTS TO ZERO, and that default is a finding rather than a
    convenience. The mandated-subsurface-intake hypothesis does not apply to Carlsbad:
    it draws through an open intake and discharges through the co-located Encina power
    station outfall — on the WateReuse figures, the two cheapest options available
    (a power-plant outfall runs $0.2-0.6M/MGD against $2.0-5.5M/MGD for a new
    diffuser outfall). Carlsbad therefore got the *inexpensive* configuration and is
    still 4x Sorek at equal scale.

    Pass a non-zero premium only when the subject plant actually carries the mandated
    design — Doheny is the case that does.
    """
    residual = scale_gap.gap / (1.0 + intake_premium)
    return Decomposition(
        gross_gap=scale_gap.gap,
        explained_by_scale=scale_gap.exponent,
        intake_premium_share=intake_premium,
        institutional_residual=residual,
    )
