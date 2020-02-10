from datetime import datetime

from django.utils import timezone
from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import Handbook


def get_handbooks():
    """
    Возвращает список словарей.
    """
    today = timezone.now()
    return Handbook.objects.exclude(create_date__gt=today)


def get_last_version_handbooks(year, month, day):
    """
    Возвращает список словарей с именем и последней версией `Handbook` на указанную дату
    """
    # Rise ValueError exception if `date` is incorrect
    relevant_to = datetime.strptime(f'{year}-{month}-{day}', '%Y-%m-%d').astimezone(timezone.get_current_timezone())
    handbooks = Handbook.objects.exclude(create_date__gte=relevant_to)
    return handbooks.raw("SELECT id, name, short_name, description, create_date, MAX(test_task_handbook.version) "
                         "FROM test_task_handbook GROUP BY test_task_handbook.name")


def get_handbook(name, version=None):
    """
    Возвращает `Handbook` с указанным именем и версией или текущей версией, если версия не указанна явно.
    """
    if version is not None:
        return get_object_or_404(get_handbooks(), name=name, version=str(version))

    today = timezone.now()
    last_version_handbooks = get_last_version_handbooks(today.year, today.month, today.day)
    handbook = next((handbook for handbook in last_version_handbooks if handbook.name == name), None)
    if handbook is None:
        raise Http404
    return handbook


def get_handbook_items(name, version, data):
    """
    Проверяет, существует ли `HandbookItem` с указанными данными для конретного справочника.
    Возвращает объекты `HandbookItem`, если есть совпдения.
    """
    code = data.get('code', None)
    content = data.get('content', None)
    handbook = get_handbook(name, version)
    if content is None:
        return handbook.handbookitem_set.filter(code=code)
    else:
        return handbook.handbookitem_set.filter(code=code, content=content)
