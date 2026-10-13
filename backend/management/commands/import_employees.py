"""Synchronize employee/business-person master data from dgyzx1 usr_mstr."""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from backend.models import ApprovalStatus, Employee


class Command(BaseCommand):
    help = "从 dgyzx1.usr_mstr 同步员工/业务员资料（不读取密码）"

    def add_arguments(self, parser):
        parser.add_argument("--commit", action="store_true", help="写入本地数据库；默认只读预检")

    def read_source(self):
        import pyodbc
        from tools.inspect_source_schema import ENV_FILE, connection_string, load_dotenv

        load_dotenv(ENV_FILE)
        try:
            with pyodbc.connect(connection_string(), readonly=True, timeout=20) as connection:
                cursor = connection.cursor()
                result = cursor.execute("""
                    SELECT usr_user AS code, usr_name AS name, usr_group AS group_code,
                           usr_dept AS department_code, usr_def_site AS default_site,
                           usr_employee AS is_employee, usr_lock AS is_locked, usr_out AS is_left,
                           usr_agent AS agent_code, usr_allow_ip AS allowed_ip,
                           usr_tele AS phone, usr_mobile AS mobile, usr_email AS email,
                           usr_qq AS qq, usr_wechat AS wechat, usr_pos AS position,
                           usr_other AS other_contact, usr_lang AS language, usr_type AS user_type,
                           usr_company AS company, usr_cm_vd AS partner_code
                    FROM dbo.usr_mstr
                """)
                names = [column[0] for column in result.description]
                return [dict(zip(names, row)) for row in result.fetchall()]
        except Exception as exc:
            raise CommandError(f"无法连接 dgyzx1 源库，员工同步未执行：{exc}") from exc

    @staticmethod
    def clean(value):
        return str(value or "").strip()

    def handle(self, *args, **options):
        rows = self.read_source()
        valid = [row for row in rows if self.clean(row.get("code"))]
        self.stdout.write(f"源库员工/用户 {len(valid)} 条；可选业务员 {sum(bool(row.get('is_employee')) and not row.get('is_locked') and not row.get('is_left') for row in valid)} 条")
        if not options["commit"]:
            self.stdout.write("预检完成；添加 --commit 才会写入本地数据库")
            return
        for row in valid:
            code = self.clean(row.get("code"))
            defaults = {
                "name": self.clean(row.get("name")) or code,
                "group_code": self.clean(row.get("group_code")),
                "department_code": self.clean(row.get("department_code")),
                "default_site": self.clean(row.get("default_site")),
                "is_employee": bool(row.get("is_employee")),
                "is_locked": bool(row.get("is_locked")),
                "is_left": bool(row.get("is_left")),
                "agent_code": self.clean(row.get("agent_code")), "allowed_ip": self.clean(row.get("allowed_ip")),
                "phone": self.clean(row.get("phone")), "mobile": self.clean(row.get("mobile")),
                "email": self.clean(row.get("email")), "qq": self.clean(row.get("qq")),
                "wechat": self.clean(row.get("wechat")), "position": self.clean(row.get("position")),
                "other_contact": self.clean(row.get("other_contact")), "language": self.clean(row.get("language")),
                "user_type": self.clean(row.get("user_type")), "company": self.clean(row.get("company")),
                "partner_code": self.clean(row.get("partner_code")),
                "status": ApprovalStatus.APPROVED, "approved_by": "dgyzx1-import",
                "approved_at": timezone.now(), "source_object": "usr_mstr",
            }
            Employee.objects.update_or_create(code=code, defaults=defaults)
        self.stdout.write(self.style.SUCCESS(f"已同步 {len(valid)} 条员工/业务员资料"))
