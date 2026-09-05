from rest_framework import parsers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.master_data.api_common import ErpRolePermission

from .material_service import confirm_material_import, preview_material_import, serialize_batch
from .models import MaterialImportBatch


class MaterialImportPreviewView(APIView):
    permission_classes = (ErpRolePermission,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    basename = "material-import"
    action = "create"

    def post(self, request):
        upload = request.FILES.get("file")
        if upload is None:
            return Response({"detail": "请选择物料导入文件"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            batch = preview_material_import(upload, request.user, request.data.get("default_tax_code", ""))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_batch(batch), status=status.HTTP_201_CREATED)


class MaterialImportDetailView(APIView):
    permission_classes = (ErpRolePermission,)
    basename = "material-import"
    action = "retrieve"

    def get(self, request, pk):
        batch = MaterialImportBatch.objects.prefetch_related("rows").filter(pk=pk).first()
        if batch is None:
            return Response({"detail": "导入批次不存在"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_batch(batch))


class MaterialImportConfirmView(APIView):
    permission_classes = (ErpRolePermission,)
    basename = "material-import"
    action = "create"

    def post(self, request, pk):
        batch = MaterialImportBatch.objects.prefetch_related("rows").filter(pk=pk).first()
        if batch is None:
            return Response({"detail": "导入批次不存在"}, status=status.HTTP_404_NOT_FOUND)
        try:
            batch = confirm_material_import(batch, request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialize_batch(batch))
