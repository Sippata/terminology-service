from django.db import models
from django.utils import timezone


class Handbook(models.Model):
    name = models.CharField(max_length=128)
    short_name = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    version = models.CharField(max_length=16, unique=True, blank=False)
    create_date = models.DateTimeField('date created', default=timezone.now)

    def __str__(self):
        return self.name


class HandbookItem(models.Model):
    handbook = models.ForeignKey(Handbook, on_delete=models.CASCADE)
    code = models.CharField(max_length=32, blank=False)
    content = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return f'{self.handbook}-{self.code}'
