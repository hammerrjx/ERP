from django.contrib.auth import get_user_model
from rest_framework import serializers

from backend.models import ApprovalRule, AuditEvent, Department, DocumentEvidence, Employee, Role, UserEmployeeLink, UserRole

from .common import serializer_for

DocumentEvidenceSerializer = serializer_for(DocumentEvidence)


EmployeeSerializer = serializer_for(Employee)


AuditEventSerializer = serializer_for(AuditEvent)


DepartmentSerializer = serializer_for(Department)


RoleSerializer = serializer_for(Role)


UserRoleSerializer = serializer_for(UserRole)


ApprovalRuleSerializer = serializer_for(ApprovalRule)


class UserAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False, allow_null=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "employee", "email", "first_name", "last_name", "is_active", "password")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            link = instance.employee_link
        except UserEmployeeLink.DoesNotExist:
            link = None
        data["employee"] = link.employee_id if link else None
        data["employee_code"] = link.employee.code if link else ""
        data["employee_name"] = link.employee.name if link else ""
        return data

    def validate(self, attrs):
        employee = attrs.get("employee")
        if employee and UserEmployeeLink.objects.filter(employee=employee).exclude(user=self.instance).exists():
            raise serializers.ValidationError({"employee": "该用户/员工资料已关联其他登录账户"})
        return attrs

    @staticmethod
    def sync_employee_link(user, employee):
        if employee is None:
            UserEmployeeLink.objects.filter(user=user).delete()
            return
        UserEmployeeLink.objects.update_or_create(user=user, defaults={"employee": employee})

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        employee = validated_data.pop("employee", None)
        if not password:
            raise serializers.ValidationError({"password": "新建用户必须设置初始密码"})
        user = self.Meta.model.objects.create_user(password=password, **validated_data)
        self.sync_employee_link(user, employee)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        employee = validated_data.pop("employee", serializers.empty)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        if password:
            instance.set_password(password)
        instance.save()
        if employee is not serializers.empty:
            self.sync_employee_link(instance, employee)
        return instance
