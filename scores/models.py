from django.db import models


class StudentScore(models.Model):
    """Exam results of one candidate.

    Field names match the CSV headers. Scores are nullable: NULL means the
    candidate did not take the subject, which is different from a score of 0.
    """

    # Text, not a number: it has leading zeros. `unique` also adds the lookup index.
    sbd = models.CharField(max_length=8, unique=True)

    toan = models.FloatField(null=True, blank=True)  # Math
    ngu_van = models.FloatField(null=True, blank=True)  # Literature
    ngoai_ngu = models.FloatField(null=True, blank=True)  # Foreign language
    vat_li = models.FloatField(null=True, blank=True)  # Physics
    hoa_hoc = models.FloatField(null=True, blank=True)  # Chemistry
    sinh_hoc = models.FloatField(null=True, blank=True)  # Biology
    lich_su = models.FloatField(null=True, blank=True)  # History
    dia_li = models.FloatField(null=True, blank=True)  # Geography
    gdcd = models.FloatField(null=True, blank=True)  # Civic education

    ma_ngoai_ngu = models.CharField(max_length=2, null=True, blank=True)

    def __str__(self):
        return self.sbd
