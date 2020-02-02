from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from model_mommy import mommy

from test_task.models import Handbook, HandbookItem


class HandbookListTest(TestCase):

    def test_empty_list(self):
        res = self.client.get(reverse('test_task:handbooks'))
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content.decode(), [])

    def test_pagination(self):
        mommy.make(Handbook, _quantity=11)
        res = self.client.get(reverse('test_task:handbooks'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 10)

        res = self.client.get(reverse('test_task:handbooks'), data={'page': 2})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)


class CurrentVersionHandbookItemsTest(TestCase):

    def test_pagination(self):
        handbook = mommy.make(Handbook)
        items = mommy.make(HandbookItem, handbook=handbook, _quantity=11)
        # Первая страница
        res = self.client.get(reverse('test_task:current_handbook_items'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 10)

        # Вторая страница
        res = self.client.get(reverse('test_task:current_handbook_items'), data={'page': 2})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_not_found_response(self):
        res = self.client.get((reverse('test_task:current_handbook_items')))
        self.assertEqual(res.status_code, 404)
        self.assertJSONEqual(res.content.decode(), {'error': 'Нет справочников текущей версии'})


class SpecifiedVersionHandbookTest(TestCase):

    def test_pagination(self):
        handbook = mommy.make(Handbook, version='qwerty')
        items = mommy.make(HandbookItem, handbook=handbook, _quantity=11)
        # Первая страница
        path = reverse('test_task:handbook_items', kwargs={'version': handbook.version})
        res = self.client.get(path, data={'page': 1})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 10)

        # Вторая страница
        path = reverse('test_task:handbook_items', kwargs={'version': handbook.version})
        res = self.client.get(path, data={'page': 1})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 10)

    def test_handbook_existing(self):
        path = reverse('test_task:handbook_items', kwargs={'version': 'not_exist'})
        res = self.client.get(path, data={'page': 1})
        self.assertEqual(res.status_code, 400)
        self.assertJSONEqual(res.content.decode(), {'error': 'Нет справочника с указанной версией'})


class ActualVersionHandbookTest(TestCase):

    def test_empty_res(self):
        today = timezone.datetime.today()
        url_data = {'year': today.year, 'month': today.month, 'day': today.day}
        res = self.client.get(reverse('test_task:actual_handbook', kwargs=url_data))
        self.assertEqual(res.status_code, 400)
        self.assertJSONEqual(res.content.decode(), {'error': 'Нет актуального справочника для указанной даты.'})

    def test_success(self):
        mommy.make(Handbook, name='fst', create_date=timezone.now() - timezone.timedelta(days=2))
        last = mommy.make(Handbook, name='snd', create_date=timezone.now() - timezone.timedelta(days=1))
        today = timezone.datetime.today()
        url_data = {'year': today.year, 'month': today.month, 'day': today.day}
        res = self.client.get(reverse('test_task:actual_handbook', kwargs=url_data))
        self.assertEqual(res.data['name'], last.name)
