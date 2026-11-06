from django.db import models


class StudentScore(models.Model):
    sbd = models.CharField(max_length=8, unique=True)
    toan = models.FloatField(null=True, blank=True)
    ngu_van = models.FloatField(null=True, blank=True)
    ngoai_ngu = models.FloatField(null=True, blank=True)
    vat_li = models.FloatField(null=True, blank=True)
    hoa_hoc = models.FloatField(null=True, blank=True)
    sinh_hoc = models.FloatField(null=True, blank=True)
    lich_su = models.FloatField(null=True, blank=True)
    dia_li = models.FloatField(null=True, blank=True)
    gdcd = models.FloatField(null=True, blank=True)
    ma_ngoai_ngu = models.CharField(max_length=2, null=True, blank=True)

    def __str__(self):
        return self.sbd