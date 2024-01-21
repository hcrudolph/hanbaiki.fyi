from django.test import TestCase
from .models import *
from .views import *
from .helpers import *


class SentinelUserTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.sentinel = get_sentinel_user()
        self.test_user = User.objects.create(username='test')

    def test_sentinel_user(self):
        self.assertEqual(self.sentinel.username, 'deleted')

    def test_created_by_after_delete(self):
        # create a VendingMachine instance with our user
        pre_delete = VendingMachine.objects.create(
            created_by=self.test_user,
        )
        self.assertEqual(pre_delete.created_by, self.test_user)
        # delete the user and check if VendingMachine instance has changed
        deleted, _ = self.test_user.delete()
        post_delete = VendingMachine.objects.get(pk=pre_delete.id)
        self.assertEqual(deleted, 1)
        self.assertEqual(post_delete.created_by, self.sentinel)

class GpsConversionTestCase(TestCase):
    def setUp(self):
        self.lat = 35.685006
        self.lon = 139.754592

    def test_dec_to_deg_conversion(self):
        self.assertEqual(
            dec_to_deg(self.lat),
            (35, 41, 6.0216)
        )
        self.assertEqual(
            dec_to_deg(self.lon),
            (139, 45, 16.5312)
        )

    def test_deg_to_dec_conversion(self):
        self.assertEqual(
            self.lat,
            deg_to_dec(dec_to_deg(self.lat)),
        )
        self.assertEqual(
            self.lon,
            deg_to_dec(dec_to_deg(self.lon)),
        )

class InfoFromImageTest(TestCase):
    def setUp(self):
        self.image_gps = 'test/test_gps_no_vm.jpg'
        self.image_nogps = 'test/test_no_gps_no_vm.jpg'
        self.lat = 35.685006
        self.lon = 139.754592

    def test_gps_from_image(self):
        self.assertEqual(
            gps_from_image(self.image_gps),
            (self.lat, self.lon),
        )
        self.assertEqual(
            gps_from_image(self.image_nogps),
            (None, None),
        )

    def test_info_from_gps(self):
        self.assertDictEqual(
            info_from_gps(self.lat, self.lon),
            {'country': 'Japan', 'state': None, 'postcode': '102-8322', 'city': 'Chiyoda', 'town': None}
        )
        self.assertDictEqual(
            info_from_gps(0, 0),
            {'country': None, 'state': None, 'postcode': None, 'city': None, 'town': None}
        )