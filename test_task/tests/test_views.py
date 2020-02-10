import json

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from model_mommy import mommy

from test_task.models import Handbook, HandbookItem
from test_task.serializers import HandbookItemSerializer


class HandbookListTest(TestCase):

    def test_empty_list(self):
        res = self.client.get(reverse('test_task:handbooks'))
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(str(res.data), [])

    def test_pagination(self):
        page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
        mommy.make(Handbook, _quantity=page_size + 1)

        res = self.client.get(reverse('test_task:handbooks'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), page_size)

        res = self.client.get(reverse('test_task:handbooks'), data={'page': 2})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)


class ActualHandbookListTest(TestCase):

    def test_empty_res(self):
        today = timezone.datetime.today()
        url_data = {'year': today.year, 'month': today.month, 'day': today.day}
        res = self.client.get(reverse('test_task:actual_handbooks', kwargs=url_data))
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(str(res.data), [])

    def test_success(self):
        yesterday = timezone.now() - timezone.timedelta(days=1)
        mommy.make(Handbook, name='handbook', version='0.1', create_date=yesterday)
        last = mommy.make(Handbook, name='handbook', version='0.2', create_date=yesterday)
        mommy.make(Handbook, name='handbook_1', version='0.1', create_date=yesterday)
        last_1 = mommy.make(Handbook, name='handbook_1', version='0.2', create_date=yesterday)

        today = timezone.datetime.today()
        url_data = {'year': today.year, 'month': today.month, 'day': today.day}
        res = self.client.get(reverse('test_task:actual_handbooks', kwargs=url_data))
        res_data = json.loads(res.content.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res_data[0]['name'], last.name)
        self.assertEqual(res_data[1]['name'], last_1.name)

    def test_invalid_date(self):
        url_data = {'year': 13, 'month': 2, 'day': 2020}
        res = self.client.get(reverse('test_task:actual_handbooks', kwargs=url_data))
        self.assertEqual(res.status_code, 400)

    def test_pagination(self):
        page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
        tomorrow = timezone.now() + timezone.timedelta(days=1)
        handbooks = mommy.make(Handbook, create_date=tomorrow, _quantity=page_size + 1)

        today = timezone.now()
        url_data = {'year': today.year, 'month': today.month, 'day': today.day}
        # Первая страница
        res = self.client.get(reverse('test_task:actual_handbooks', kwargs=url_data))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), page_size)

        # Вторая страница
        res = self.client.get(reverse('test_task:actual_handbooks', kwargs=url_data), data={'page': 2})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)


class CurrentVersionHandbookItemsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.handbook_1 = mommy.make(Handbook, name='terms', version='0.1')
        cls.handbook_2 = mommy.make(Handbook, name='terms', version='0.2')

        cls.term_1 = mommy.make(HandbookItem, handbook=cls.handbook_1, code='101')
        cls.term_2 = mommy.make(HandbookItem, handbook=cls.handbook_1, code='101')
        cls.term_3 = mommy.make(HandbookItem, handbook=cls.handbook_1, code='001')

        cls.term_4 = mommy.make(HandbookItem, handbook=cls.handbook_2, code='101')
        cls.term_5 = mommy.make(HandbookItem, handbook=cls.handbook_2, code='101')
        cls.term_6 = mommy.make(HandbookItem, handbook=cls.handbook_2, code='001')

    def test_pagination(self):
        page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
        handbook_item_count = HandbookItem.objects.filter(handbook__version=self.handbook_2.version).count()
        items = mommy.make(HandbookItem, handbook=self.handbook_2, _quantity=page_size - handbook_item_count + 1)
        # Первая страница
        res = self.client.get(reverse('test_task:handbook_items', kwargs={'handbook_name': self.handbook_2.name}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), page_size)

        # Вторая страница
        res = self.client.get(reverse('test_task:handbook_items', kwargs={'handbook_name': self.handbook_2.name}),
                              data={'page': 2})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_last_version_handbook_items(self):
        items = (self.term_4, self.term_5, self.term_6)
        res = self.client.get(reverse('test_task:handbook_items', kwargs={'handbook_name': self.handbook_2.name}))
        self.assertJSONEqual(res.content.decode(), HandbookItemSerializer(items, many=True).data)

    def test_specified_version_handbook_items(self):
        items = (self.term_1, self.term_2, self.term_3)
        res = self.client.get(reverse('test_task:handbook_items', kwargs={'handbook_name': self.handbook_2.name}),
                              data={'version': self.handbook_1.version})
        self.assertJSONEqual(res.content.decode(), HandbookItemSerializer(items, many=True).data)

    def test_multiple_result(self):
        items = self.term_4, self.term_5
        res = self.client.post(reverse('test_task:handbook_items', kwargs={'handbook_name': self.handbook_2.name}),
                               data={'code': self.term_4.code})
        self.assertJSONEqual(res.content.decode(), HandbookItemSerializer(items, many=True).data)

    def test_validation_with_code(self):
        item = self.term_6
        res = self.client.post(reverse('test_task:handbook_items', kwargs={'handbook_name': self.handbook_2.name}),
                               data={'code': item.code})
        self.assertJSONEqual(res.content.decode(), [HandbookItemSerializer(item).data])

    def test_validation_with_code_and_content(self):
        item = self.term_6
        res = self.client.post(reverse('test_task:handbook_items', kwargs={'handbook_name': self.handbook_2.name}),
                               data={'code': item.code, 'content': item.content})
        self.assertJSONEqual(res.content.decode(), [HandbookItemSerializer(item).data])

    def test_validation_with_bad_request(self):
        data = {'code': 'bad_code'}
        res = self.client.post(reverse('test_task:handbook_items', kwargs={'handbook_name': self.handbook_2.name}))
        self.assertEqual(res.status_code, 400)
