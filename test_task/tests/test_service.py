from django.test import TestCase
from django.utils import timezone

from model_mommy import mommy

from test_task.models import Handbook, HandbookItem
from ..services import *


class GetCurrentHandbookTest(TestCase):

    def test_last_handbook(self):
        handbook_1 = mommy.make(Handbook, name='fst')
        handbook_2 = mommy.make(Handbook, name='snd')
        res = get_actual_handbook()
        self.assertEqual(res.name, handbook_2.name)

    def test_future_handbook(self):
        past_handbook = mommy.make(Handbook, name='past')
        time = timezone.now() + timezone.timedelta(days=1, hours=2)
        future_handbook = mommy.make(Handbook, name='future', create_date=time)
        res = get_actual_handbook()
#        self.assertEqual(res.create_date, past_handbook.create_date)
        self.assertEqual(res.name, past_handbook.name)
