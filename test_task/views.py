from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .serializers import HandbookItemSerializer, HandbookSerializer
from .services import get_last_version_handbooks, get_handbooks, get_handbook, get_handbook_items


class HandbookListView(APIView, PageNumberPagination):
    """
    Получение списка всех справочников
    """
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE')

    def get(self, request):
        handbooks = get_handbooks().order_by('name')
        page = self.paginate_queryset(handbooks, request)
        serializer = HandbookSerializer(page, many=True)
        return Response(serializer.data)


class ActualHandbookListView(APIView, PageNumberPagination):
    """
    Получение списка справочников, актуальных на указанную дату.
    """
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE')

    def get(self, request, year, month, day):
        try:
            handbooks = get_last_version_handbooks(year, month, day)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(handbooks, request)
        serializer = HandbookSerializer(page, many=True)
        return Response(serializer.data)


class HandbookItemListView(APIView, PageNumberPagination):
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE')

    def get(self, request, handbook_name):
        """
        Получение списка элементов справочника указанной версии или текущей версии, если не указано явно.
        """
        version = request.query_params.get('version', None)
        handbook = get_handbook(handbook_name, version)
        page = self.paginate_queryset(handbook.handbookitem_set.order_by('pk'), request)
        serializer = HandbookItemSerializer(page, many=True)
        return Response(serializer.data)

    def post(self, request, handbook_name):
        """
        Валидация элемента справочника указанной версии или текущей версии, если не указано явно.
        """
        version = request.query_params.get('version', None)
        handbook_items = get_handbook_items(handbook_name, version, request.data)
        if handbook_items.exists():
            page = self.paginate_queryset(handbook_items.order_by('pk'), request)
            serializer = HandbookItemSerializer(page, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'request data not valid'}, status=status.HTTP_400_BAD_REQUEST)

