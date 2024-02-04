from django.db import models
from django.conf import settings
from django.utils.html import mark_safe
from .helpers import *
from django_resized import ResizedImageField
from uuid import uuid4
from datetime import date
from pillow_heif import register_heif_opener
register_heif_opener() # HEIF support


class VendingMachine(models.Model):
    class Meta:
        ordering=['-date_created']

    def random_fname(instance, filename):
        date_path = date.today().strftime("%Y/%m/%d")
        ext = filename.split('.')[-1].lower()
        return f"{date_path}/{uuid4().hex}.{ext}"

    def img_tag(self)-> str:
        return mark_safe(f"<img src='{self.img.url}' height='100' />")
    img_tag.short_description = 'Image'

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
    country = models.ForeignKey(
        'Country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    state = models.ForeignKey(
        'State',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    zip = models.ForeignKey(
        'ZipCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        'City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    town = models.ForeignKey(
        'Town',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
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

    def __str__(self) -> str:
        return f"#{self.id} {self.date_created.strftime('%Y/%m/%d')}"

class Post(models.Model):
    class Meta:
        ordering=['-date_published']
        get_latest_by='date_published'

    def img_tag(self) -> str:
        return mark_safe(f"<img src='{self.vendingmachine.img.url}' height='100' />")
    img_tag.short_description = 'Vending machine'

    def str_tag(self) -> str:
        return self.__str__()
    str_tag.short_description = 'Post title'

    slug = models.SlugField(
        unique=True,
        editable=False,
    )
    vendingmachine = models.ForeignKey(
        'VendingMachine',
        on_delete=models.CASCADE,
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
        return f"Post #{self.id} ({self.date_published.strftime('%Y/%m/%d')})"

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

class Country(models.Model):
    class Meta:
        ordering=['name']
        verbose_name_plural='Countries'

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

class State(models.Model):
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

class City(models.Model):
    class Meta:
        ordering=['name']
        verbose_name_plural='Cities'

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

class Town(models.Model):
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

class ZipCode(models.Model):
    class Meta:
        ordering=['code']

    code = models.CharField(
        primary_key=True,
        max_length=50,
    )
    slug = models.SlugField(
        unique=True,
        editable=False,
    )

    def __str__(self) -> str:
        return self.code