"""System domain models; Django app label remains backend."""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from .base import ApprovalStatus, AuditedModel, AuditEvent  # noqa: F401


class Employee(AuditedModel):
    """Employee/business-person master synchronized from the legacy user table."""

    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=80)
    group_code = models.CharField(max_length=32, blank=True)
    department_code = models.CharField(max_length=32, blank=True)
    default_site = models.CharField(max_length=16, blank=True)
    is_employee = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    is_left = models.BooleanField(default=False)
    phone = models.CharField(max_length=50, blank=True)
    mobile = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    qq = models.CharField(max_length=30, blank=True)
    wechat = models.CharField(max_length=50, blank=True)
    position = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=16, blank=True)
    company = models.CharField(max_length=160, blank=True)
    source_object = models.CharField(max_length=40, default="usr_mstr")

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} {self.name}".strip()


class Department(AuditedModel):
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=80)
    manager = models.CharField(max_length=64, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="children")
    source_created_by = models.CharField(max_length=64, blank=True)
    source_created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} {self.name}"


class Role(AuditedModel):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="roles")
    permissions = models.JSONField(default=list)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("department__code", "code")

    def __str__(self):
        return f"{self.code} {self.name}"


class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="erp_role_assignments")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="assignments")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="user_roles")
    is_primary = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "role", "department"), name="uniq_user_role_department")]


class ApprovalRule(AuditedModel):
    code = models.CharField(max_length=40, unique=True)
    document_type = models.CharField(max_length=40)
    sequence = models.PositiveSmallIntegerField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="approval_rules")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="approval_rules")
    min_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]
    )
    max_amount = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal("0"))]
    )
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("document_type", "sequence", "code")
        constraints = [
            models.UniqueConstraint(
                fields=("document_type", "sequence", "department"), name="uniq_document_approval_step"
            )
        ]

    def clean(self):
        if self.role_id and self.department_id and self.role.department_id != self.department_id:
            raise ValidationError("审批角色必须属于审批部门")
        if self.max_amount is not None and self.max_amount < self.min_amount:
            raise ValidationError({"max_amount": "金额上限不能小于金额下限"})
