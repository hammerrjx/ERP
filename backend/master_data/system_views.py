from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets

from backend.domain.system import ApprovalRule, AuditEvent, Department, Role, UserRole
from backend.models import Employee
from .api_common import make_viewset
from .serializers.system import (
    ApprovalRuleSerializer,
    AuditEventSerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    RoleSerializer,
    UserAccountSerializer,
    UserRoleSerializer,
)

AuditEventViewSet = make_viewset(AuditEvent, AuditEventSerializer)
DepartmentViewSet = make_viewset(Department, DepartmentSerializer)
RoleViewSet = make_viewset(Role, RoleSerializer)
UserRoleViewSet = make_viewset(UserRole, UserRoleSerializer)
ApprovalRuleViewSet = make_viewset(ApprovalRule, ApprovalRuleSerializer)
EmployeeViewSet = make_viewset(Employee, EmployeeSerializer)


class UserAccountViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all().order_by("username")
    serializer_class = UserAccountSerializer
    permission_classes = (permissions.IsAdminUser,)
