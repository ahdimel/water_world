"""water_world — freshwater mispricing, the Colorado basin, and the cost of desalination.

Layering is strictly one-directional:

    sources -> cache -> normalised tables -> analysis -> reports

Phase 1 builds everything up to and including normalised tables. No analysis logic
lives in this package yet, by design: if a number is *computed* it belongs in a later
phase, and if it is *observed* it belongs here or in data/parameters/literature.yaml.
"""

__version__ = "0.1.0"
