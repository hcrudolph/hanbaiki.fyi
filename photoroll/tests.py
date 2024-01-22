from django.test import TestCase
from django.template.defaultfilters import slugify
from photoroll.templatetags.base_path import *
from django.conf import settings
from django.core.files import File
from datetime import date
from .models import *
from .views import *
from .helpers import *
import requests


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
            info_from_gps(0, 0),
            {'country': None, 'state': None, 'postcode': None, 'city': None, 'town': None}
        )

class PreSaveSignalsTestCase(TestCase):
    def setUp(self):
        self.test_string = 'TeSt sTrInG'

    def test_create_country(self):
        c = Country.objects.create(name=self.test_string)
        self.assertEqual(
            c.slug,
            slugify(self.test_string)
        )

    def test_create_state(self):
        s = State.objects.create(name=self.test_string)
        self.assertEqual(
            s.slug,
            slugify(self.test_string)
        )

    def test_create_zip(self):
        z = ZipCode.objects.create(code=self.test_string)
        self.assertEqual(
            z.slug,
            slugify(self.test_string)
        )

    def test_create_city(self):
        c = City.objects.create(name=self.test_string)
        self.assertEqual(
            c.slug,
            slugify(self.test_string)
        )

    def test_create_town(self):
        t = Town.objects.create(name=self.test_string)
        self.assertEqual(
            t.slug,
            slugify(self.test_string)
        )

    def test_create_tag(self):
        t = Tag.objects.create(name=self.test_string)
        self.assertEqual(
            t.slug,
            slugify(self.test_string)
        )

class PreDeleteSignalsTestCase(TestCase):
    def setUp(self):
        self.machine = VendingMachine(created_by=get_sentinel_user())
        self.machine.img.save(
            'test_gps_no_vm.jpg',
            File(open('test/test_gps_no_vm.jpg', 'rb'))
        )

    def test_vm_post_delete(self):
        img_url = f"{settings.MEDIA_URL}{self.machine.img.name}"
        pre_delete_response = requests.head(img_url)
        self.machine.delete()
        post_delete_response = requests.head(img_url)
        self.assertEqual(pre_delete_response.status_code, 200)
        self.assertEqual(post_delete_response.status_code, 403)

class CustomTemplateTagsTestCase(TestCase):
    def test_base_path(self):
        path = '/posts/YYYY/MM/slug/'
        self.assertEqual(
            base_path(path),
            'posts'
        )

class ModelStringTestCase(TestCase):
    def setUp(self):
        self.user = get_sentinel_user()
        self.vm = VendingMachine(created_by=self.user)
        self.vm.img.save(
            'test_gps_no_vm.jpg',
            File(open('test/test_gps_no_vm.jpg', 'rb'))
        )
        self.country = Country.objects.create(name='Test')
        self.state = State.objects.create(name='Test')
        self.city = City.objects.create(name='Test')
        self.zip = ZipCode.objects.create(code='Test')
        self.town = Town.objects.create(name='Test')
        self.tag = Tag.objects.create(name='Test')

    def test_vending_machine_str(self):
        self.assertEqual(
            self.vm.__str__(),
            f"#{self.vm.id} {date.today().strftime('%Y/%m/%d')}"
        )
        self.assertEqual(
            self.vm.img_tag(),
            f"<img src='{self.vm.img.url}' height='100' />"
        )

    def test_post_str(self):
        post = self.vm.post_set.first()
        self.assertEqual(
            post.img_tag(),
            f"<img src='{self.vm.img.url}' height='100' />"
        )
        self.assertEqual(
            post.__str__(),
            f"Post #{post.id} ({date.today().strftime('%Y/%m/%d')})"
        )
        self.assertEqual(
            post.str_tag(),
            post.__str__()
        )

    def test_tag_str(self):
        self.assertEqual(
            self.tag.__str__(),
            self.tag.name
        )

    def test_country_str(self):
        self.assertEqual(
            self.country.__str__(),
            self.country.name
        )

    def test_state_str(self):
        self.assertEqual(
            self.state.__str__(),
            self.state.name
        )

    def test_city_str(self):
        self.assertEqual(
            self.city.__str__(),
            self.city.name
        )

    def test_town_str(self):
        self.assertEqual(
            self.town.__str__(),
            self.town.name
        )

    def test_zip_str(self):
        self.assertEqual(
            self.zip.__str__(),
            self.zip.code
        )