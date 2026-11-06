from .models import StudentScore
from django.db.models import F
from .subjects import SubjectRegistry, ScoreLevel

def find_student(sbd):
    return StudentScore.objects.filter(sbd=sbd).first()

def top_group_a(limit=10):
    fields = SubjectRegistry.GROUP_A_FIELDS

    qs = StudentScore.objects.all()
    for f in fields:
        qs = qs.filter(**{f"{f}__isnull": False})

    qs = qs.annotate(total=sum(F(f) for f in fields))   # tổng điểm bằng F
    return qs.order_by("-total", "sbd")[:limit]

def build_report():
    exprs = {}
    for subject in SubjectRegistry.ALL:
        exprs.update(subject.count_expressions())

    raw = StudentScore.objects.aggregate(**exprs)     # một câu SQL

    labels = [subject.name for subject in SubjectRegistry.ALL]
    datasets = []
    for level in ScoreLevel:
        data = [raw[f"{s.field}_{level.name.lower()}"] for s in SubjectRegistry.ALL]
        datasets.append({"label": level.label, "data": data})
    return {"labels": labels, "datasets": datasets}

