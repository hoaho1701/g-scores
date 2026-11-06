from dataclasses import dataclass
from enum import Enum
from django.db.models import Q, Count

class ScoreLevel(Enum):
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
        if score is None:
            return None
        for level in cls:
            if level.contains(score):
                return level
        return None

    def q(self, field):
        cond = Q()
        if self.low is not None:
            cond &= Q(**{f"{field}__gte": self.low})
        if self.high is not None:
            cond &= Q(**{f"{field}__lt": self.high})
        return cond

@dataclass(frozen=True)
class Subject:
    field: str
    name: str

    def level_of(self, student):
        score = getattr(student, self.field)
        return ScoreLevel.from_score(score)

    def count_expressions(self):
        result = {}
        for level in ScoreLevel:
            alias = f"{self.field}_{level.name.lower()}"
            result[alias] = Count("id", filter=level.q(self.field))
        return result

class SubjectRegistry:
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

    @classmethod
    def get(cls, field):
        for subject in cls.ALL:
            if subject.field == field:
                return subject
        raise ValueError(f"Subject not found for field: '{field}'")