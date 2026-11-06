"""Subjects and score levels.

Kept in one module so that thresholds, subject names and subject groups are
each defined in exactly one place.
"""

from dataclasses import dataclass
from enum import Enum

from django.db.models import Count, Q


class ScoreLevel(Enum):
    """The four score bands, as ``(low, high, label)``.

    ``low`` is inclusive, ``high`` is exclusive, and None means unbounded.
    """

    EXCELLENT = (8, None, ">= 8 điểm")
    GOOD = (6, 8, "6 - dưới 8 điểm")
    AVERAGE = (4, 6, "4 - dưới 6 điểm")
    WEAK = (None, 4, "dưới 4 điểm")

    def __init__(self, low, high, label):
        self.low = low
        self.high = high
        self.label = label

    def contains(self, score):
        above_low = self.low is None or self.low <= score
        below_high = self.high is None or self.high > score
        return above_low and below_high

    @classmethod
    def from_score(cls, score):
        """Return the level of a score, or None if the score is None."""
        if score is None:
            return None
        for level in cls:
            if level.contains(score):
                return level
        return None

    def q(self, field):
        """Return the ORM filter for this band, e.g. ``Q(toan__gte=6, toan__lt=8)``."""
        cond = Q()
        if self.low is not None:
            cond &= Q(**{f"{field}__gte": self.low})
        if self.high is not None:
            cond &= Q(**{f"{field}__lt": self.high})
        return cond


@dataclass(frozen=True)
class Subject:
    """One subject: ``field`` is the model field, ``name`` is the display name."""

    field: str
    name: str

    def count_expressions(self):
        """Return ``{alias: Count(...)}`` for each level, for use in ``aggregate``."""
        result = {}
        for level in ScoreLevel:
            alias = f"{self.field}_{level.name.lower()}"
            result[alias] = Count("id", filter=level.q(self.field))
        return result


class SubjectRegistry:
    """The only place that lists subjects and subject groups."""

    ALL = [
        Subject("toan", "Toán"),
        Subject("ngu_van", "Ngữ văn"),
        Subject("ngoai_ngu", "Ngoại ngữ"),
        Subject("vat_li", "Vật lí"),
        Subject("hoa_hoc", "Hoá học"),
        Subject("sinh_hoc", "Sinh học"),
        Subject("lich_su", "Lịch sử"),
        Subject("dia_li", "Địa lí"),
        Subject("gdcd", "Giáo dục công dân"),
    ]
    GROUP_A_FIELDS = ["toan", "vat_li", "hoa_hoc"]
