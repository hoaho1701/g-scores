from django.db import models


class StudentScore(models.Model):
    candidate_id = models.CharField(max_length=8, unique=True)
    math = models.FloatField(null=True, blank=True)
    literature = models.FloatField(null=True, blank=True)
    foreign_language = models.FloatField(null=True, blank=True)
    physics = models.FloatField(null=True, blank=True)
    chemistry = models.FloatField(null=True, blank=True)
    biology = models.FloatField(null=True, blank=True)
    history = models.FloatField(null=True, blank=True)
    geography = models.FloatField(null=True, blank=True)
    civic_education = models.FloatField(null=True, blank=True)
    foreign_language_code = models.CharField(max_length=2, null=True, blank=True)

    def __str__(self):
        return self.candidate_id