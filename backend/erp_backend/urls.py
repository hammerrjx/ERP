from django.contrib.auth import authenticate
from django.urls import include, path
from rest_framework import permissions, serializers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from backend.models import ApprovalStatus, UserRole


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    credentials = LoginSerializer(data=request.data)
    credentials.is_valid(raise_exception=True)
    user = authenticate(
        request,
        username=credentials.validated_data["username"],
        password=credentials.validated_data["password"],
    )
    if user is None or not user.is_active:
        raise serializers.ValidationError({"detail": "用户名或密码不正确"})
    token, _ = Token.objects.get_or_create(user=user)
    if user.is_superuser:
        return Response({
            "token": token.key, "username": user.get_username(),
            "departments": [], "roles": ["SUPERUSER"], "permissions": ["*"],
        })
    assignments = UserRole.objects.filter(
        user=user,
        active=True,
        role__active=True,
        role__status=ApprovalStatus.APPROVED,
    ).select_related("role", "department").order_by("department__code", "role__code")
    departments = []
    roles = []
    permissions_set = set()
    for assignment in assignments:
        department = {"code": assignment.department.code, "name": assignment.department.name}
        if department not in departments:
            departments.append(department)
        roles.append(assignment.role.code)
        permissions_set.update(assignment.role.permissions)
    return Response({
        "token": token.key,
        "username": user.get_username(),
        "departments": departments,
        "roles": roles,
        "permissions": sorted(permissions_set),
    })


urlpatterns = [
    path("api/auth/login/", login),
    path("api/", include("backend.master_data.urls")),
]
