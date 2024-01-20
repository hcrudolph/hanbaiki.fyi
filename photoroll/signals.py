from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.db.models.signals import pre_save, post_save, pre_delete
from django.template.defaultfilters import slugify
from django.dispatch import receiver
from django.contrib import messages
from .models import *


@receiver(pre_save, sender=Post)
def create_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify_post(instance.vendingmachine.img.name)

@receiver(pre_save, sender=Tag)
def create_slug_from_tag_name(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)

@receiver(pre_save, sender=Country)
def create_slug_from_country_name(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)

@receiver(pre_save, sender=State)
def create_slug_from_state_name(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)

@receiver(pre_save, sender=ZipCode)
def create_slug_from_zipcode(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.code)

@receiver(pre_save, sender=City)
def create_slug_from_city_name(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)

@receiver(pre_save, sender=Town)
def create_slug_from_town_name(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)

@receiver(pre_delete, sender=VendingMachine)
def delete_associated_media(sender, instance, *args, **kwargs):
    instance.img.delete()

@receiver(post_save, sender=VendingMachine)
def create_post(sender, instance, created, **kwargs):
    if created:
        Post.objects.create(vendingmachine=instance)

@receiver(user_logged_out)
def logout_message(sender, request, **kwargs):
    messages.success(request, 'Logged out successfully.')

@receiver(user_logged_in)
def login_message(sender, request, **kwargs):
    messages.success(request, 'Logged in successfully.')