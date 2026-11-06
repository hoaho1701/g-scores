from django.shortcuts import render

from .forms import LookupForm
from .services import build_report, find_student, top_group_a
from .subjects import SubjectRegistry


def lookup(request):
    """Look up scores by registration number (GET: read-only, shareable URL)."""
    student = None
    not_found = False
    rows = []

    if "sbd" in request.GET:
        form = LookupForm(request.GET)
        if form.is_valid():
            student = find_student(form.cleaned_data["sbd"])
            if student is None:
                not_found = True
            else:
                # (display name, score); score is None if the subject was not taken.
                rows = [
                    (subject.name, getattr(student, subject.field))
                    for subject in SubjectRegistry.ALL
                ]
    else:
        form = LookupForm()

    context = {
        "form": form,
        "student": student,
        "not_found": not_found,
        "rows": rows,
    }
    return render(request, "scores/lookup.html", context)


def top10(request):
    students = top_group_a()
    return render(request, "scores/top10.html", {"students": students})


def report(request):
    data = build_report()
    return render(request, "scores/report.html", {"report": data})
