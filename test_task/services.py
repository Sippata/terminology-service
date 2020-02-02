from django.utils import timezone
from datetime import datetime

from rest_framework.pagination import PageNumberPagination

from .models import Handbook


def get_actual_handbook(actual_for=None):
    actual_for = timezone.now() if actual_for is None else actual_for
    return Handbook.objects\
        .filter(create_date__lte=actual_for)\
        .order_by('-create_date')\
        .first()


def paginate(queryset, request, size=10):
    paginator = PageNumberPagination()
    paginator.page_size = size
    return paginator.paginate_queryset(queryset, request)
