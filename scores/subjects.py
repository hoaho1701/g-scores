from dataclasses import dataclass
from enum import Enum


class ScoreLevel(Enum):
    EXCELLENT = "excellent"   # >= 8
    GOOD = "good"             # 6 <= && < 8
    AVERAGE = "average"       # 4 <= && < 6
    WEAK = "weak"             # < 4

    @classmethod
    def from_score(cls, score):
        if score is None:
            return None
        elif score >= 8:
            return cls.EXCELLENT
        elif score >= 6:
            return cls.GOOD
        elif score >= 4:
            return cls.AVERAGE
        else:
            return cls.WEAK


@dataclass(frozen=True)
class Subject:
    field: str
    name: str

    def level_of(self, student):
        score = getattr(student, self.field)
        return ScoreLevel.from_score(score)


class SubjectRegistry:
    ALL = [
        Subject("math", "Toán"),
        Subject("literature", "Ngữ văn"),
        Subject("foreign_language", "Ngoại ngữ"),
        Subject("physics", "Vật lí"),
        Subject("chemistry", "Hoá học"),
        Subject("biology", "Sinh học"),
        Subject("history", "Lịch sử"),
        Subject("geography", "Địa lí"),
        Subject("civic_education", "Giáo dục công dân"),
    ]
    GROUP_A_FIELDS = ["math", "physics", "chemistry"]

    @classmethod
    def get(cls, field):
        for subject in cls.ALL:
            if subject.field == field:
                return subject
        raise ValueError(f"Subject not found for field: '{field}'")