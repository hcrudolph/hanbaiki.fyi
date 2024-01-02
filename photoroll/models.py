from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save, pre_delete
from django.utils.html import mark_safe
from django.dispatch import receiver
from django.template.defaultfilters import slugify

import requests
import logging
from django_resized import ResizedImageField
from uuid import uuid4
from datetime import date
from PIL import Image
from PIL.ExifTags import IFD
from pillow_heif import register_heif_opener

register_heif_opener() # HEIF support

def slugify_post(fname: str) -> str:
    filename = fname.split("/")[-1]
    return filename.split(".")[0]

def get_geo_info(lat: float, lon: float, lang="en") -> str:
    result = dict()
    response = requests.get(
        f"https://nominatim.openstreetmap.org/reverse.php?lat={lat}&lon={lon}&format=json",
        headers={"Accept-Language":f"{lang}"}
    ).json()

    # try to get country information
    try:
        result['country'] = response['address']['country']
    except KeyError:
        result['country'] = ''
        logging.warning(f"No 'country' found for location LAT:{lat} LON:{lon}")

    # try to get state/county information
    try:
        result['state'] = response['address']['state']
    except KeyError:
        logging.warning(f"No 'state' found for location LAT:{lat} LON:{lon}")
        try:
            result['state'] = response['address']['county']
        except KeyError:
            result['state'] = ''
            logging.warning(f"No 'county' found for location LAT:{lat} LON:{lon}")

    # try to get postcode information
    try:
        result['postcode'] = response['address']['postcode']
    except KeyError:
        result['postcode'] = ''
        logging.warning(f"No 'postcode' found for location LAT:{lat} LON:{lon}")

    # try to get postcode information
    try:
        result['city'] = response['address']['city']
    except KeyError:
        result['city'] = ''
        logging.warning(f"No 'city' found for location LAT:{lat} LON:{lon}")

    # try to get town/village/neighborhood information
    try:
        result['town'] = response['address']['town']
    except KeyError:
        logging.warning(f"No 'town' found for location LAT:{lat} LON:{lon}")
        try:
            result['town'] = response['address']['village']
        except KeyError:
            logging.warning(f"No 'village' found for location LAT:{lat} LON:{lon}")
            try:
                result['town'] = response['address']['neighborhood']
            except KeyError:
                result['town'] = ''
                logging.warning(f"No 'neighborhood' found for location LAT:{lat} LON:{lon}")

    return result

def get_sentinel_user():
    return settings.AUTH_USER_MODEL.objects.get_or_create(username="deleted")[0]

######################
# Model definitions  #
######################

class VendingMachine(models.Model):
    class Meta:
        ordering=['-date_created']

    def random_fname(instance, filename):
        date_path = date.today().strftime("%Y/%m/%d")
        ext = filename.split('.')[-1].lower()
        return f"{date_path}/{uuid4().hex}.{ext}"

    def img_tag(self):
        return mark_safe(f"<img src='{self.img.url}' height='100' />")

    img = ResizedImageField(
        upload_to = random_fname,
    )
    lat = models.DecimalField(
        null=True,
        blank=True,
        max_digits=9,
        decimal_places=6,
    )
    lon = models.DecimalField(
        null=True,
        blank=True,
        max_digits=9,
        decimal_places=6,
    )
    country = models.CharField(
        null=True,
        blank=True,
        max_length=50,
    )
    state = models.CharField(
        null=True,
        blank=True,
        max_length=50,
    )
    postcode = models.CharField(
        null=True,
        blank=True,
        max_length=10,
    )
    city = models.CharField(
        null=True,
        blank=True,
        max_length=50,
    )
    town = models.CharField(
        null=True,
        blank=True,
        max_length=50,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user),
        editable=False,
        related_name="+",
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
    )
    date_edited = models.DateTimeField(
        auto_now=True,
    )

    img_tag.short_description = 'Image'

    def __str__(self):
        return f"#{self.id} {self.date_created.strftime('%Y/%m/%d')}"

class Post(models.Model):
    class Meta:
        ordering=['-date_published']
        get_latest_by='date_published'

    slug = models.SlugField(
        unique=True,
        editable=False,
    )
    machine = models.ForeignKey(
        "VendingMachine",
        on_delete=models.CASCADE,
    )
    tags = models.ManyToManyField(
        'Tag'
    )
    is_published = models.BooleanField(
        default=True,
    )
    date_published = models.DateTimeField(
        auto_now_add=True,
    )
    date_last_edited = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self) -> str:
        return self.date_published.strftime('%Y/%m/%d')

class Tag(models.Model):
    class Meta:
        ordering=['name']

    name = models.CharField(
        primary_key=True,
        max_length=50,
    )
    slug = models.SlugField(
        unique=True,
        editable=False,
    )

    def __str__(self) -> str:
        return self.name

######################
# Signal definitions #
######################

@receiver(pre_save, sender=Post)
def create_slug(sender, instance, *args, **kwargs):
    """Automatically generates a slug from the post's title."""
    if not instance.slug:
        instance.slug = slugify_post(instance.machine.img.name)

@receiver(pre_save, sender=Tag)
def create_slug_from_tag_name(sender, instance, *args, **kwargs):
    """Automatically generates a slug from the tag's name."""
    if not instance.slug:
        instance.slug = slugify(instance.name)

@receiver(post_save, sender=VendingMachine)
def read_exif_data(sender, instance, created, **kwargs):
    if created:
        img = Image.open(instance.img)
        exif = img.getexif()
        try:
            lat = exif.get_ifd(IFD.GPSInfo)[2]
            lat_dec = round(lat[0] + lat[1]/60. + lat[2]/3600., 6)
        except KeyError:
            lat_dec=None

        try:
            lon = exif.get_ifd(IFD.GPSInfo)[4]
            lon_dec = round(lon[0] + lon[1]/60. + lon[2]/3600., 6)
        except KeyError:
            lon_dec=None

        if lat_dec==None or lon_dec==None:
            logging.error('Image does not contain GPS Info and will be deleted.')
            instance.delete()
        else:
            instance.lat = lat_dec
            instance.lon = lon_dec
            geo_info = get_geo_info(lat_dec, lon_dec)
            instance.country = geo_info['country']
            instance.state = geo_info['state']
            instance.postcode = geo_info['postcode']
            instance.city = geo_info['city']
            instance.town = geo_info['town']
            instance.save()

            Post.objects.create(
                machine=instance,
            )

@receiver(pre_delete, sender=VendingMachine)
def delete_associated_media(sender, instance, *args, **kwargs):
    instance.img.delete()