from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from backend.models import ApprovalStatus, TaxCode


class Command(BaseCommand):
    help = "从 Excel 导入税务编码、税务名称和开票名称"

    def add_arguments(self, parser):
        parser.add_argument("source_file", type=Path)

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            from openpyxl import load_workbook
        except ImportError as exc:
            raise CommandError("导入 .xlsx 需要安装 openpyxl") from exc

        source_file = options["source_file"]
        if not source_file.exists():
            raise CommandError(f"文件不存在：{source_file}")
        imported = 0
        skipped = 0
        duplicates = 0
        sheets = 0
        workbook = load_workbook(source_file, read_only=True, data_only=True)
        try:
            aliases = {
                "code": {"税务编码", "税收分类编码", "商品和服务税收分类编码", "taxcode", "tax_code", "code"},
                "name": {"税务名称", "税收分类名称", "商品和服务税收分类名称", "taxname", "tax_name", "name"},
                "invoice": {"开票名称", "发票名称", "invoice_name", "invoicename"},
            }

            def clean_header(value):
                return "".join(str(value or "").strip().lower().split())

            def find_columns(header):
                normalized = [clean_header(value) for value in header]
                columns = {}
                for field, names in aliases.items():
                    names = {clean_header(name) for name in names}
                    columns[field] = next((index for index, value in enumerate(normalized) if value in names), None)
                # Legacy files without headers retain the documented first-three-column layout.
                if columns["code"] is None and len(header) >= 1:
                    columns["code"] = 0
                if columns["name"] is None and len(header) >= 2:
                    columns["name"] = 1
                if columns["invoice"] is None and len(header) >= 3:
                    columns["invoice"] = 2
                return columns

            seen = set()
            for worksheet in workbook.worksheets:
                rows = worksheet.iter_rows(values_only=True)
                try:
                    header = next(rows)
                except StopIteration:
                    continue
                columns = find_columns(header)
                if columns["code"] is None or columns["name"] is None:
                    continue
                sheets += 1
                for row in rows:
                    code = str(row[columns["code"]] or "").strip() if columns["code"] < len(row) else ""
                    name = str(row[columns["name"]] or "").strip() if columns["name"] < len(row) else ""
                    invoice_index = columns["invoice"]
                    invoice_name = str(row[invoice_index] or "").strip() if invoice_index is not None and invoice_index < len(row) else ""
                    if not code or not name:
                        skipped += 1
                        continue
                    if code in seen:
                        duplicates += 1
                    seen.add(code)
                    TaxCode.objects.update_or_create(
                        code=code,
                        defaults={
                            "name": name[:160],
                            "invoice_name": invoice_name[:160],
                            "active": True,
                            "status": ApprovalStatus.APPROVED,
                            "created_by": "tax-import",
                        },
                    )
                    imported += 1
        finally:
            workbook.close()
        self.stdout.write(self.style.SUCCESS(
            f"税务编码导入完成：读取 {sheets} 个工作表，{imported} 行，重复 {duplicates} 行，跳过 {skipped} 行；数据库唯一编码以最后一行为准"
        ))
