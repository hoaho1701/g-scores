from django.db.models import F

from .models import StudentScore
from .subjects import ScoreLevel, SubjectRegistry


def find_student(sbd):
    """Return the candidate with this registration number, or None."""
    return StudentScore.objects.filter(sbd=sbd).first()


def top_group_a(limit=10):
    """Return the top candidates of group A by total score (``.total``).

    Only candidates with all group A scores are ranked. Ties are broken by
    registration number so the order is stable.
    """
    fields = SubjectRegistry.GROUP_A_FIELDS

    qs = StudentScore.objects.all()
    for f in fields:
        qs = qs.filter(**{f"{f}__isnull": False})

    # sum() starts at 0, so this builds a single SQL expression: a + b + c.
    qs = qs.annotate(total=sum(F(f) for f in fields))
    return qs.order_by("-total", "sbd")[:limit]


def build_report():
    """Count candidates per score level for every subject, in one SQL query.

    Returns ``{"labels": [subject names], "datasets": [{"label", "data"}]}``,
    the shape Chart.js expects.
    """
    exprs = {}
    for subject in SubjectRegistry.ALL:
        exprs.update(subject.count_expressions())

    raw = StudentScore.objects.aggregate(**exprs)

    labels = [subject.name for subject in SubjectRegistry.ALL]
    datasets = []
    for level in ScoreLevel:
        data = [raw[f"{s.field}_{level.name.lower()}"] for s in SubjectRegistry.ALL]
        datasets.append({"label": level.label, "data": data})
    return {"labels": labels, "datasets": datasets}
