from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from backend.models import AccountingAccount, Currency, PaymentMethod


class SupplierDetailsTests(APITestCase):
    def setUp(self):
        self.client.force_authenticate(get_user_model().objects.create_superuser('supplier-test', password='test'))
        self.currency = Currency.objects.create(code='RMB',name='人民币')
        self.term = PaymentMethod.objects.create(code='NET30', description='月结30天')
        AccountingAccount.objects.create(code='2202',name='应付账款')

    def test_bank_rows_and_independent_payment_terms(self):
        body = {'code':'S-DETAIL','name':'供应商','short_name':'供应商','kind':'supplier',
                'currency':self.currency.pk,'payment_method_master':self.term.pk,
                'payment_method_2':'NET30','payment_method_3':'NET30','purchase_account':'2202',
                'quote_method':'2','strategic_supplier':True,
                'bank_accounts':[{'line_number':10,'account_type':'company','bank_name':'银行','account_number':'001'}]}
        response = self.client.post('/api/partner/',body,format='json')
        self.assertEqual(response.status_code,201,response.data)
        self.assertFalse(response.data['quote_tax_included'])
        self.assertEqual(response.data['payment_method_3'],'NET30')
        bank = response.data['bank_accounts'][0]
        self.assertEqual(bank['created_by'],'supplier-test')
        bank['bank_name'] = '新银行'
        path = f"/api/partner/{response.data['id']}/"
        response = self.client.patch(path,{'bank_accounts':[bank]},format='json')
        self.assertEqual(response.status_code,200,response.data)
        self.assertEqual(response.data['bank_accounts'][0]['id'],bank['id'])
        self.assertEqual(response.data['bank_accounts'][0]['modification_count'],1)
        invalid = self.client.patch(path,{'purchase_account':'UNKNOWN'},format='json')
        self.assertEqual(invalid.status_code,400)
        self.assertEqual(self.client.patch(path,{'bank_accounts':[]},format='json').data['bank_accounts'],[])

    def test_foreign_bank_row_cannot_be_attached(self):
        body = {'code':'S-BAD','name':'供应商','short_name':'供应商','kind':'supplier',
                'payment_method_master':self.term.pk,
                'bank_accounts':[{'id':99999,'line_number':10,'account_number':'001'}]}
        self.assertEqual(self.client.post('/api/partner/',body,format='json').status_code,400)
