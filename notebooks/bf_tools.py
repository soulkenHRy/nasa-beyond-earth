"""Tools for the findings (FINDINGS.md).

Every number a finding shows is recorded here as a "fact": its exact value, the text it is shown as,
its unit, and where it comes from ("our data", or "outside the data" for known science). Each finding's facts are
saved as numbers/BFnn_<slug>.csv, so every number in FINDINGS.md can be traced to a file in numbers/.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import helpers as hp


def n0(v) -> str:
    """Whole number with thousands separators: 8659 -> '8,659'."""
    return f"{int(round(float(v))):,}"


def d(v, k: int = 2) -> str:
    """Decimal with k places: d(3.953, 2) -> '3.95'."""
    return f"{float(v):,.{k}f}"


def p(v, k: int = 0) -> str:
    """Percent with k places: p(56.5) -> '57%'."""
    return f"{float(v):.{k}f}%"


def g(v, sig: int = 3) -> str:
    """Significant figures, no scientific notation for normal sizes: g(0.0355) -> '0.0355'."""
    v = float(v)
    if v == 0:
        return "0"
    digits = sig - int(np.floor(np.log10(abs(v)))) - 1
    return f"{round(v, max(digits, 0)):,.{max(digits, 0)}f}"


class Facts:
    """Collect the facts of one finding and save them to numbers/BFnn_<slug>.csv."""

    def __init__(self, num: int, slug: str):
        self.num, self.slug, self.rows = num, slug, []

    def add(self, key: str, value, shown: str | None = None, unit: str = "", source: str = "our data") -> str:
        if shown is None:
            shown = n0(value) if float(value).is_integer() else g(value)
        self.rows.append({"key": key, "value": value, "shown": shown, "unit": unit, "source": source})
        return shown

    def rule(self, key: str, value, shown: str | None = None, unit: str = "") -> str:
        """A cut-off or slice edge we chose (or copied from the guide), not a measurement."""
        return self.add(key, value, shown, unit, source="rule we used")

    def outside(self, key: str, value, shown: str | None = None, unit: str = "", source: str = "known science") -> str:
        """A number from outside the data files (known science)."""
        return self.add(key, value, shown, unit, source=source)

    def table(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows)

    def save(self) -> str:
        keys = [r["key"] for r in self.rows]
        dup = {k for k in keys if keys.count(k) > 1}
        if dup:
            raise ValueError(f"duplicate fact keys in BF{self.num:02d}: {sorted(dup)}")
        return hp.save_numbers(self.table(), f"BF{self.num:02d}_{self.slug}")


class Meet(Facts):
    """The numbers in one part's "Meet the data" text, saved as numbers/BM_<part>_<slug>.csv (same columns as Facts)."""

    def __init__(self, part: str, slug: str):
        super().__init__(0, slug)
        self.part = part

    def save(self) -> str:
        keys = [r["key"] for r in self.rows]
        dup = {k for k in keys if keys.count(k) > 1}
        if dup:
            raise ValueError(f"duplicate fact keys in BM_{self.part}: {sorted(dup)}")
        return hp.save_numbers(self.table(), f"BM_{self.part}_{self.slug}")
