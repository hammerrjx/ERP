from django.apps import apps
from django.test import SimpleTestCase
from rest_framework import serializers

from backend.models import (
    ApprovalStatus, AuditedModel, RfqLine, RequestForQuotation, SalesQuote, SalesQuoteLine,
    SalesQuoteTier, SupplierInquiry,
)
from backend.master_data.api_common import ensure_editable


class ApprovalBoundaryTests(SimpleTestCase):
    def test_every_audited_model_is_locked_when_approved(self):
        audited_models = [
            model for model in apps.get_app_config("backend").get_models()
            if issubclass(model, AuditedModel) and not model._meta.abstract
        ]
        self.assertGreater(len(audited_models), 0)
        for model in audited_models:
            with self.subTest(model=model.__name__):
                with self.assertRaisesMessage(serializers.ValidationError, "已审核资料不可修改"):
                    ensure_editable(model(status=ApprovalStatus.APPROVED))

    def test_nested_lines_are_locked_by_approved_ancestor(self):
        quote = SalesQuote(status=ApprovalStatus.APPROVED)
        quote_line = SalesQuoteLine(quote=quote)
        tier = SalesQuoteTier(quote_line=quote_line)
        with self.assertRaisesMessage(serializers.ValidationError, "已审核资料不可修改"):
            ensure_editable(tier)

        rfq = RequestForQuotation(status=ApprovalStatus.APPROVED)
        rfq_line = RfqLine(rfq=rfq)
        inquiry = SupplierInquiry(rfq_line=rfq_line)
        with self.assertRaisesMessage(serializers.ValidationError, "已审核资料不可修改"):
            ensure_editable(inquiry)
