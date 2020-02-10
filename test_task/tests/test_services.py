from django.test import TestCase
from model_mommy import mommy

from test_task.models import Handbook, HandbookItem
from ..services import *


class GetHandbooksTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.handbook_1 = mommy.make(Handbook, name='past_1')
        cls.handbook_2 = mommy.make(Handbook, name='past_2')
        tomorrow = timezone.now() + timezone.timedelta(days=1)
        cls.handbook_3 = mommy.make(Handbook, create_date=tomorrow, name='future')

    def test_future_handbook_exclusion(self):
        handbooks = get_handbooks().order_by('pk')
        self.assertQuerysetEqual(handbooks, [self.handbook_1, self.handbook_2], transform=lambda x: x)


class GetLastVersionHandbookTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        mommy.make(Handbook, name='Термины', version='0.11')
        cls.last_version_handbook_1 = mommy.make(Handbook, name='Термины', version='1')
        mommy.make(Handbook, name='Болезни', version='0.001')
        cls.last_version_handbook_2 = mommy.make(Handbook, name='Болезни', version='0.1')

    def test_last_version_handbooks(self):
        today = timezone.now()
        handbooks = get_last_version_handbooks(today.year, today.month, today.day)
        self.assertQuerysetEqual(handbooks, [self.last_version_handbook_1, self.last_version_handbook_2],
                                 transform=lambda x: x, ordered=False)


class GetHandbookTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.diseases_1 = mommy.make(Handbook, name='Болезни', version='0.1')
        cls.diseases_2 = mommy.make(Handbook, name='Болезни', version='0.11')
        cls.last_diseases = mommy.make(Handbook, name='Болезни', version='1')

    def test_with_specified_version(self):
        handbook = get_handbook(self.diseases_1.name, self.diseases_1.version)
        self.assertEqual(handbook, self.diseases_1)

    def test_with_bad_version(self):
        handbook = get_handbook(self.diseases_1.name, float(self.diseases_1.version))
        self.assertEqual(handbook, self.diseases_1)

    def test_with_not_exist_version(self):
        self.assertRaises(Http404, get_handbook, self.diseases_1, version='1000.01')

    def test_with_none_version(self):
        handbook = get_handbook(name=self.diseases_1.name)
        self.assertEqual(handbook.version, self.last_diseases.version)

    def test_success_with_none_version(self):
        handbook = get_handbook(name=self.diseases_1.name)
        self.assertEqual(handbook, self.last_diseases)


class IsHandbookItemValid(TestCase):
    @classmethod
    def setUpTestData(cls):
        # For test_none_version
        cls.previous_version = mommy.make(Handbook, name='Термины', version='0.05')
        mommy.make(HandbookItem, handbook=cls.previous_version, code='001', content='some term')

        cls.terms = mommy.make(Handbook, name='Термины', version='0.11')
        cls.item_1 = mommy.make(HandbookItem, handbook=cls.terms, code='001', content='some term')
        cls.item_2 = mommy.make(HandbookItem, handbook=cls.terms, code='101', content='another term')

    def test_with_code_only(self):
        data = {'code': self.item_1.code}
        res = get_handbook_items(self.terms.name, self.terms.version, data)
        self.assertQuerysetEqual(res, [self.item_1], transform=lambda x: x)

    def test_with_code_and_content(self):
        data = {'code': self.item_1.code, 'content': self.item_1.content}
        res = get_handbook_items(self.terms.name, self.terms.version, data)
        self.assertQuerysetEqual(res, [self.item_1], transform=lambda x: x)

    def test_multiple_result(self):
        item_3 = mommy.make(HandbookItem, handbook=self.terms, code='001', content='term')
        item_4 = mommy.make(HandbookItem, handbook=self.terms, code='101', content='another term')
        data = {'code': self.item_1.code}
        res = get_handbook_items(self.terms.name, self.terms.version, data)
        self.assertQuerysetEqual(res, [self.item_1, item_3], transform=lambda x:x, ordered=False)
        data = {'code': self.item_2.code, 'content': self.item_2.content}
        res = get_handbook_items(self.terms.name, self.terms.version, data)
        self.assertQuerysetEqual(res, [self.item_2, item_4], transform=lambda x:x, ordered=False)

    def test_none_version(self):
        data = {'code': self.item_1.code, 'content': self.item_1.content}
        res = get_handbook_items(self.terms.name, version=None, data=data)
        self.assertQuerysetEqual(res, [self.item_1], transform=lambda x: x)