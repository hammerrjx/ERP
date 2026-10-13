"""Native ex_mstr/exd_det currency rules shared by operational documents."""
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models import Q


def exchange_rate(currency, effective_date):
    """xgyzx dbo.GetExRate: inclusive validity dates, default 1 without a match."""
    from backend.models import CurrencyRate
    rates = list(CurrencyRate.objects.filter(currency=currency, effective_date__lte=effective_date)
        .filter(Q(expiry_date__isnull=True) | Q(expiry_date__gte=effective_date))[:2])
    if len(rates) > 1:
        raise ValidationError('币种汇率有效期间重叠，请先核对货币资料')
    return rates[0].rate_to_company if rates else Decimal(1)
