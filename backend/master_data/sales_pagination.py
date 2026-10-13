from django.db.models import Q
from rest_framework import response
from rest_framework.pagination import PageNumberPagination


class SalesPage(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return response.Response({'count': self.page.paginator.count, 'page': self.page.number,
                                  'page_size': self.get_page_size(self.request), 'results': data})


class PagedSalesMixin:
    """Opt-in pagination keeps existing document lookup clients compatible."""
    search_fields = ()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action != 'list':
            return qs
        params = self.request.query_params
        if params.get('customer', '').isdigit():
            qs = qs.filter(customer_id=params['customer'])
        if params.get('material', '').isdigit() and qs.model._meta.model_name == 'customermaterial':
            qs = qs.filter(material_id=params['material'])
        if params.get('enabled') in ('0', '1') and qs.model._meta.model_name == 'customermaterial':
            qs = qs.filter(enabled=params['enabled'] == '1')
        q = params.get('q', '').strip()
        if q:
            condition = Q()
            for field in self.search_fields:
                condition |= Q(**{field + '__icontains': q})
            qs = qs.filter(condition).distinct()
        return qs.order_by(*qs.model._meta.ordering, '-pk') if qs.model._meta.ordering else qs.order_by('pk')

    def paginate_queryset(self, queryset):
        if 'page' not in self.request.query_params:
            return super().paginate_queryset(queryset)
        self._paginator = SalesPage()
        return self._paginator.paginate_queryset(queryset, self.request, view=self)
