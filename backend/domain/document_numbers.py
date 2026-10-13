"""dgyzx1 code_mstr: business-date YYMM, four digits, reset monthly.

See xgyzx.auto_nbr for business-date selection and existing-number collision rules.
Only the application database is written; imported document numbers are preserved.
"""
from datetime import date

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F


class DocumentNumberSequence(models.Model):
    prefix_period = models.CharField(max_length=24, primary_key=True)
    last_value = models.PositiveIntegerField(default=0)


def next_document_number(prefix, day, *model_names):
    if isinstance(day, str):
        day = date.fromisoformat(day)
    stem = prefix + day.strftime('%y%m')
    with transaction.atomic():
        # UPDATE acquires a write lock on SQLite as well as SQL Server/PostgreSQL.
        counters = DocumentNumberSequence.objects.filter(pk=stem)
        if not counters.update(last_value=F('last_value') + 1):
            DocumentNumberSequence.objects.get_or_create(prefix_period=stem)
            counters.update(last_value=F('last_value') + 1)
        sequence = DocumentNumberSequence.objects.get(pk=stem)
        value = sequence.last_value
        for name in model_names:
            numbers = apps.get_model('backend', name).objects.filter(number__startswith=stem).values_list('number', flat=True)
            value = max([value, *(int(n[-4:]) + 1 for n in numbers
                if len(n) == len(stem) + 4 and n[-4:].isascii() and n[-4:].isdigit())])
        if value > 9999:
            raise ValidationError('本月四位单号流水已用尽，请核实源库编号配置')
        DocumentNumberSequence.objects.filter(pk=stem).update(last_value=value)
        return f'{stem}{value:04d}'
