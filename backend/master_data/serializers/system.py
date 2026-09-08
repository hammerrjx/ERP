from django.contrib.auth import get_user_model
from rest_framework import serializers

from backend.models import ApprovalRule, AuditEvent, Department, DocumentEvidence, Employee, Role, UserRole

from .common import serializer_for

DocumentEvidenceSerializer = serializer_for(DocumentEvidence)


EmployeeSerializer = serializer_for(Employee)


AuditEventSerializer = serializer_for(AuditEvent)


DepartmentSerializer = serializer_for(Department)


RoleSerializer = serializer_for(Role)


UserRoleSerializer = serializer_for(UserRole)


ApprovalRuleSerializer = serializer_for(ApprovalRule)


class UserAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "first_name", "last_name", "is_active", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        return self.Meta.model.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
