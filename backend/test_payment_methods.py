from django.test import TestCase

from backend.master_data.serializers import PartnerSerializer
from backend.models import Partner, PaymentMethod


class PaymentMethodTests(TestCase):
    def test_partner_selection_keeps_legacy_code_and_master_relation(self):
        method = PaymentMethod.objects.create(code="M90", description="月结90天")
        serializer = PartnerSerializer(data={
            "code": "C-PAY", "name": "支付客户", "short_name": "支付客户",
            "kind": Partner.PartnerKind.CUSTOMER, "payment_method_master": method.pk,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        partner = serializer.save()
        self.assertEqual(partner.payment_method, "M90")
        self.assertEqual(partner.payment_method_master_id, method.pk)
        self.assertEqual(PartnerSerializer(partner).data["payment_method_name"], "月结90天")
