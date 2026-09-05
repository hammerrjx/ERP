from django.core.management.base import BaseCommand

from backend.material_codes import _source_codes, allocate_material_code
from backend.models import Material, ProductCategory


class Command(BaseCommand):
    help = "只读核验 .env 配置的 V_AI_PT_MSTR 物料编码源视图"

    def add_arguments(self, parser):
        parser.add_argument("prefixes", nargs="*", help="产品类代码；未提供时检查已配置产品类")

    def handle(self, *args, **options):
        prefixes = options["prefixes"] or list(ProductCategory.objects.values_list("code_prefix", flat=True))
        for prefix in dict.fromkeys(value.strip() for value in prefixes if value and value.strip()):
            source = _source_codes(prefix)
            local = Material.objects.filter(code__startswith=f"{prefix}-").values_list("code", flat=True)
            if source is None:
                self.stdout.write(f"{prefix}: 源视图不可达；本地回退下一号 {allocate_material_code(prefix, local)}")
                continue
            self.stdout.write(
                f"{prefix}: 源记录 {len(source)} 条，源最大号 {max(source, default='无')}，下一号 {allocate_material_code(prefix, local)}"
            )
