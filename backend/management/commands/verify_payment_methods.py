"""Verify payment term import and partner links against the read-only source."""
from django.core.management.base import BaseCommand, CommandError

from backend.models import Partner, PaymentMethod
from .import_payment_methods import connection_string


class Command(BaseCommand):
    help = "核对 dgyzx1 支付方式总数及客户/供应商关联"

    def handle(self, *args, **options):
        try:
            import pyodbc
            with pyodbc.connect(connection_string(), readonly=True, timeout=20) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT ct_code FROM dbo.ct_mstr")
                source_methods = {str(row[0]).strip() for row in cursor.fetchall() if row[0]}
                cursor.execute("SELECT cm_addr, cm_cr_terms FROM dbo.cm_mstr")
                source_customers = [(str(row[0]).strip(), str(row[1]).strip()) for row in cursor.fetchall() if row[0]]
                cursor.execute("SELECT vd_addr, vd_cr_terms FROM dbo.vd_mstr")
                source_suppliers = [(str(row[0]).strip(), str(row[1]).strip()) for row in cursor.fetchall() if row[0]]
        except Exception as exc:
            raise CommandError(f"无法连接 dgyzx1 源库，验证未执行：{exc}") from exc

        local_methods = set(PaymentMethod.objects.values_list("code", flat=True))
        local_partners = {row.code: row for row in Partner.objects.only("code", "payment_method", "payment_method_master")}

        def partner_stats(rows):
            missing_partner = [code for code, _ in rows if code not in local_partners]
            missing_method = [term for _, term in rows if term and term not in local_methods]
            linked = [
                code for code, term in rows
                if code in local_partners and term and local_partners[code].payment_method_master_id
                and local_partners[code].payment_method == term
            ]
            return len(linked), len(missing_partner), len(missing_method)

        customer_linked, customer_missing_partner, customer_missing_method = partner_stats(source_customers)
        supplier_linked, supplier_missing_partner, supplier_missing_method = partner_stats(source_suppliers)
        self.stdout.write(f"支付方式：源库 {len(source_methods)}，本地 {len(local_methods)}，缺失 {len(source_methods - local_methods)}")
        self.stdout.write(f"客户：源库 {len(source_customers)}，已关联且代码一致 {customer_linked}，本地缺少客户 {customer_missing_partner}，缺少支付方式 {customer_missing_method}")
        self.stdout.write(f"供应商：源库 {len(source_suppliers)}，已关联且代码一致 {supplier_linked}，本地缺少供应商 {supplier_missing_partner}，缺少支付方式 {supplier_missing_method}")
