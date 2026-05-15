# api/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class EncomiendaPagination(PageNumberPagination):
    """
    Paginación principal para el endpoint de encomiendas.

    Respuesta:
    {
        "success": true,
        "pagination": {
            "count": 0,
            "total_pages": 0,
            "current_page": 1,
            "next": null,
            "previous": null
        },
        "results": []
    }
    """
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'pagination': {
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'pagination': {
                    'type': 'object',
                    'properties': {
                        'count': {'type': 'integer'},
                        'total_pages': {'type': 'integer'},
                        'current_page': {'type': 'integer'},
                        'next': {'type': 'string', 'nullable': True},
                        'previous': {'type': 'string', 'nullable': True},
                    }
                },
                'results': schema,
            }
        }


class HistorialPagination(PageNumberPagination):
    """
    Paginación para el historial de estados de una encomienda.
    Sin formato personalizado — usa el estándar de DRF.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100