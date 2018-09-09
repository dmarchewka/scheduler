# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Candidate(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)


class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=50)


class Slot(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=10)
