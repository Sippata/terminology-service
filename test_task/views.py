from datetime import datetime

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Handbook
from .serializers import HandbookItemSerializer, HandbookSerializer
from .services import get_actual_handbook, paginate


@api_view(['GET'])
def handbook_list(request):
    """
    Получение списка справочников
    """
    # TODO: Нужно ли выделять случай, когда в базе нет справочников?
    # TODO: Включать справочники, которые "находятся в будущем"?
    handbooks = Handbook.objects.all().order_by('id')
    page_res = paginate(handbooks, request)
    serializer = HandbookSerializer(page_res, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def actual_handbook(request, year, month, day):
    """
    Получение списка справочников, актуальных на указанную дату
    """
    # TODO: Валидировать дату?
    handbook = get_actual_handbook(datetime(year, month, day))
    if handbook is None:
        return Response({'error': 'Нет актуального справочника для указанной даты.'},
                        status=status.HTTP_400_BAD_REQUEST)
    serializer = HandbookSerializer(handbook)
    return Response(serializer.data)


@api_view(['GET'])
def current_version_handbook_items(request):
    """
    Получение элементов справочника текущей версии
    """
    handbook = get_actual_handbook()
    if handbook is None:
        return Response({'error': 'Нет справочников текущей версии'}, status=status.HTTP_404_NOT_FOUND)

    items = handbook.handbookitem_set.all().order_by('id')
    page_res = paginate(items, request)
    serializer = HandbookItemSerializer(page_res, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def specified_version_handbook_items(request, version):
    """
    Получение элементов спрвочника указанной версии
    """
    try:
        handbook = Handbook.objects.get(version=version)
    except Handbook.DoesNotExist:
        return Response({'error': 'Нет справочника с указанной версией'}, status=status.HTTP_400_BAD_REQUEST)

    items = handbook.handbookitem_set.all().order_by('id')
    page_res = paginate(items, request)
    serializer = HandbookItemSerializer(page_res, many=True)
    return Response(serializer.data)
