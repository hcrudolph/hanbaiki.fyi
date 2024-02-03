from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import redirect
from datetime import datetime, timedelta
from pytz import timezone
from functools import wraps
from django.conf import settings
from .forms import UploadFilesForm
from rapidfuzz import process, fuzz, utils
from django.db.models import Q
from .models import *
from .helpers import *
import logging
import boto3


######################
# Global definitions #
######################

class GpsMissingException(Exception):
    "Raised when the processes image does not contain GPS coordinates"
    pass

class ConfidenceLevelException(Exception):
    "Raised when the processes image does not clear the defined confidence threshold"
    pass

def is_vending_machine(client, image):
    response = client.detect_labels(
        Image={'S3Object':{'Bucket':settings.AWS_STORAGE_BUCKET_NAME,'Name':image}},
        Features=['GENERAL_LABELS'],
        Settings={'GeneralLabels': {'LabelInclusionFilters':['Vending Machine']}},
        MinConfidence=95.,
        MaxLabels=1,
    )
    if len (response['Labels']) > 0:
        return True
    else:
        return False

def get_tags_from_image(client, image):
    existing_tags = list(Tag.objects.values_list('slug', flat=True))
    response = client.detect_text(
        Image={'S3Object': {'Bucket':settings.AWS_STORAGE_BUCKET_NAME, 'Name':image}},
        Filters={'WordFilter': {'MinConfidence': 90.0}}
    )
    return match_existing_tags(existing_tags, response)

def match_existing_tags(existing_tags:list, response:dict):
    result = dict()
    # fuzzy match each match of type 'WORD' against existing tags
    for text in filter(lambda x : x['Type'] == 'WORD', response['TextDetections']):
        new_matches = process.extract(
            text['DetectedText'].lower(),
            existing_tags,
            scorer=fuzz.WRatio,
            processor=utils.default_process,
            score_cutoff=80.,
        )
        for slug, _, _ in new_matches:
            tag = Tag.objects.get(slug=slug)
            result.update({slug:tag})
    return result

def create_related_models(instance, geo_info):
    if geo_info['country'] is not None:
        instance.country, _ = Country.objects.get_or_create(
            name=geo_info['country']
        )
    else:
        instance.country = None
    if geo_info['state'] is not None:
        instance.state, _ = State.objects.get_or_create(
            name=geo_info['state']
        )
    else:
        instance.state = None
    if geo_info['postcode'] is not None:
        instance.zip, _ = ZipCode.objects.get_or_create(
            code=geo_info['postcode']
        )
    else:
        instance.zip = None
    if geo_info['city'] is not None:
        instance.city, _ = City.objects.get_or_create(
            name=geo_info['city']
        )
    else:
        instance.city = None
    if geo_info['town'] is not None:
        instance.town, _ = Town.objects.get_or_create(
            name=geo_info['town']
        )
    else:
        instance.town = None
    instance.save()

def create_vending_machine(client, image, user):
    # read GPS coordinates from image
    lat, lon = gps_from_image(image)
    vm = VendingMachine.objects.create(
        lat=lat,
        lon=lon,
        img=image,
        created_by=user
    )
    # analyze image using AWS Rekognition
    vending_machine = is_vending_machine(
        client,
        f"{settings.AWS_S3_MEDIA_LOCATION}/{vm.img.name}",
    )
    if lat==None or lon==None or (lat==0 and lon==0):
        logging.error('Upload failed. Image does not contain GPS coordinates.')
        vm.delete()
        raise GpsMissingException
    elif not vending_machine:
        logging.error('Upload failed. Image does not contain a Vending Machine.')
        vm.delete()
        raise ConfidenceLevelException
    else:
        geo_info = info_from_gps(lat, lon)
        create_related_models(vm, geo_info)
        tag_vending_machine(client, vm)
        min_lat = round_down(lat, 4)
        max_lat = round_up(lat, 4)
        min_lon = round_down(lon, 4)
        max_lon = round_up(lon, 4)
        old_vms = VendingMachine.objects.filter(
            Q(lat__gte=min_lat) & Q(lat__lte=max_lat) & \
            Q(lon__gte=min_lon) & Q(lon__lte=max_lon)
        )
        logging.warning(old_vms)
        duplicate = False
        if old_vms.count() > 1:
            duplicate = True
        return(vm, duplicate)

def tag_vending_machine(client, vm):
    tags = get_tags_from_image(
        client,
        f"{settings.AWS_S3_MEDIA_LOCATION}/{vm.img.name}"
    )
    for tag in tags.values():
        vm.tags.add(tag)

def original_uploaders_only(function):
  @wraps(function)
  def wrap(request, id, **kwargs):
    # redirect user unless it's the author and file was uploaded in the last minute
    vm = VendingMachine.objects.get(id=id)
    tz = timezone(settings.TIME_ZONE)
    age = tz.localize(datetime.now()) - vm.date_created
    if request.user != vm.created_by or age > timedelta(minutes=1):
        return HttpResponseRedirect(reverse_lazy('index'))
    else:
        return function(request, id, **kwargs)
  return wrap


######################
# View definitions   #
######################

def about(request):
    return render(request, 'photoroll/about.html')

def post_detail(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
    )
    context = {
        'post': post,
        'lat_deg': post.vendingmachine.lat,
        'lon_deg': post.vendingmachine.lon,
    }
    return render(request, 'photoroll/post.html', context)

def post_map(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
    )
    context = {
        'id': post.id,
        'lat': post.vendingmachine.lat,
        'lon': post.vendingmachine.lon,
        'mapbox_token': settings.MAPBOX_ACCESS_TOKEN,
    }
    return render(request, 'photoroll/map.html', context)

def archive(request):
    if Post.objects.exists():
        years = dict()
        earliest_post = Post.objects.earliest()
        latest_post = Post.objects.latest()
        earliest_year = earliest_post.date_published.year
        latest_year = latest_post.date_published.year + 1
        year_range = range(earliest_year, latest_year)

        for year in year_range:
            months = []
            post_list = Post.objects.filter(date_published__year=year)
            for post in post_list:
                months.append(post.date_published.month)
            years[year] = set(months)
    else:
        years = None

    cities = City.objects.exclude(vendingmachine=None)
    zips = ZipCode.objects.exclude(vendingmachine=None)

    context = {
        'years': years,
        'cities': cities,
        'zips': zips,
    }
    return render(request, 'photoroll/archive.html', context)

def posts_by_location(request, lat:float, lon:float):
    try:
        lat = float(lat)
        lon = float(lon)
    except TypeError:
        logging.error(f"Could not convert into float LAT:{lat} LON:{lon}.")

    # search in an area of +/- 500 meters
    max_lat = lat + 0.005
    min_lat = lat - 0.005
    max_lon = lon + 0.005
    min_lon = lon - 0.005
    posts = Post.objects.filter(
        Q(vendingmachine__lat__gte=min_lat) & Q(vendingmachine__lat__lte=max_lat) & \
        Q(vendingmachine__lon__gte=min_lon) & Q(vendingmachine__lon__lte=max_lon)
    )
    return render(request, 'photoroll/post_list_plain.html', {'posts':posts})

def current_location(request):
    return render(request, 'photoroll/current_location.html')

class PostListView(generic.ListView):
    model = Post
    template_name = 'photoroll/post_list.html'
    paginate_by = 15

    def get_queryset(self):
        return Post.objects.filter(is_published=True)

class TagListView(generic.ListView):
    model = Tag
    template_name = 'photoroll/tag_list.html'

    def get_queryset(self):
        return Tag.objects.exclude(vendingmachine__post=None)

class PostsByTagListView(generic.ListView):
    model = Post
    template_name = 'photoroll/post_list.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = Tag.objects.get(slug=self.kwargs['slug'])
        context['page_title'] = f"Vending machines tagged '{tag.name}'"
        return context

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(vendingmachine__tags=self.tag)

class PostByYearListView(generic.ListView):
    model = Post
    template_name = 'photoroll/post_list.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Vending machines from {self.kwargs['year']}"
        return context

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            date_published__year=self.kwargs['year'],
        )

class PostByMonthListView(generic.ListView):
    model = Post
    template_name = 'photoroll/post_list.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Vending machines from {self.kwargs['year']}/{self.kwargs['month']}"
        return context

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            date_published__year=self.kwargs['year'],
            date_published__month=self.kwargs['month'],
        )

class PostByCityListView(generic.ListView):
    model = Post
    template_name = 'photoroll/post_list.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Vending machines in {self.kwargs['city'].capitalize()}"
        return context

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            vendingmachine__city__slug=self.kwargs['city'],
        )

class PostByZipListView(generic.ListView):
    model = Post
    template_name = 'photoroll/post_list.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Vending machines in {self.kwargs['zip']}"
        return context

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            vendingmachine__zip__slug=self.kwargs['zip'],
        )


######################
# Restricted Views   #
######################

@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadFilesForm(request.POST, request.FILES)
        if form.is_valid():
            client = boto3.Session(profile_name='default').client('rekognition')
            images = request.FILES.getlist('img')
            for image in images:
                try:
                    vm, duplicate = create_vending_machine(client, image, request.user)
                except GpsMissingException:
                    messages.error(request, f"Failed to upload image '{image}'. No GPS coordinates.")
                except ConfidenceLevelException:
                    messages.error(request, f"Failed to upload image '{image}'. No Vending Machine.")
                if duplicate:
                    messages.warning(request, f"The image '{image}' contains a potential duplicate. Please check below.")
                    return redirect('duplicate', id=vm.id)
                else:
                    messages.success(request, f"Successfully uploaded image '{image}'.")
            return redirect('index')
    else:
        form = UploadFilesForm()
    return render(request, 'photoroll/upload.html', {'form': form})

@login_required
@original_uploaders_only
def duplicate(request, id):
    # search images at the same location
    new_vm = VendingMachine.objects.get(pk=id)
    min_lat = round_down(new_vm.lat, 4)
    max_lat = round_up(new_vm.lat, 4)
    min_lon = round_down(new_vm.lon, 4)
    max_lon = round_up(new_vm.lon, 4)
    old_vms = VendingMachine.objects.filter(
        Q(lat__gte=min_lat) & Q(lat__lte=max_lat) & \
        Q(lon__gte=min_lon) & Q(lon__lte=max_lon)
    ).exclude(pk=id)
    context = {
        'new_vm': new_vm,
        'old_vms': old_vms,
    }
    return render(request, 'photoroll/comparison.html', context)

@login_required
@original_uploaders_only
def duplicate_yes(request, id):
    duplicate = VendingMachine.objects.get(pk=id)
    duplicate.delete()
    messages.warning(request, "Skipped duplicate. Your image has been deleted.")
    return HttpResponseRedirect(reverse_lazy('index'))

@login_required
@original_uploaders_only
def duplicate_maybe(request, id):
    Post.objects.filter(vendingmachine__pk=id).update(is_published=False)
    messages.warning(request, "Your image has been uploaded and will be reviewed manually.")
    return HttpResponseRedirect(reverse_lazy('index'))

@login_required
@original_uploaders_only
def duplicate_no(request, id):
    messages.success(request, "Image uploaded successfully!")
    return HttpResponseRedirect(reverse_lazy('index'))