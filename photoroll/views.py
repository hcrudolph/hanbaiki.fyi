from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views import generic
from django.conf import settings
from .forms import UploadFilesForm, UploadCameraForm
from django.db.models import Q
from .models import *
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

def gps_dec_to_deg(dec:float):
    result = dict()
    result['degree'] = int(dec)
    result['minute'] = int((dec - result['degree']) * 60)
    result['second'] = round((((dec - result['degree']) * 60) - result['minute']) * 60, 4)
    return result

def get_confidence_by_label(bucket, photo, label) -> float:
    session = boto3.Session(profile_name='default')
    client = session.client('rekognition')
    response = client.detect_labels(
        Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=1,
        Features=['GENERAL_LABELS'],
        Settings={'GeneralLabels': {'LabelInclusionFilters':[label]}},
    )
    try:
        result = float(response['Labels'][0]['Confidence'])
    except:
        result = 0.
    return result

def process_image(request, image):
    vm = VendingMachine.objects.create(img=image, created_by=request.user)
    # if save failed due to missing GPS coordinates
    if vm.id is None:
        logging.error('Upload failed. Image does not contain GPS data.')
        messages.error(request, 'Upload failed. Image does not contain GPS data.')
        raise GpsMissingException
    else:
        confidence = get_confidence_by_label(
            settings.AWS_STORAGE_BUCKET_NAME,
            f"{settings.AWS_S3_MEDIA_LOCATION}/{vm.img.name}",
            'Vending Machine'
        )
        # confidence level for given label too low
        if confidence < 95.:
            logging.error(f"Upload failed. Image did not clear confidence threshold ({confidence})")
            messages.error(request, 'Upload failed. Image does not seem to contain a vending machine.')
            vm.delete()
            raise ConfidenceLevelException

######################
# View definitions   #
######################

class PostListView(generic.ListView):
    model = Post
    template_name = 'photoroll/post_list.html'
    paginate_by = 15

    def get_queryset(self):
        return Post.objects.filter(is_published=True)

def about(request):
    return render(request, 'photoroll/about.html')

def post_detail(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
    )
    context = {
        'post': post,
        'lat_deg': gps_dec_to_deg(post.vendingmachine.lat),
        'lon_deg': gps_dec_to_deg(post.vendingmachine.lon),
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


######################
# Restricted Views   #
######################

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFilesForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('img')
            image_count = 0
            for image in images:
                try:
                    process_image(request, image)
                    image_count+=1
                except (GpsMissingException, ConfidenceLevelException) as e:
                    return HttpResponseRedirect('/')
            messages.success(request, f"{image_count} image(s) uploaded successfully.")
            return HttpResponseRedirect('/')
    else:
        form = UploadFilesForm()
    return render(request, 'photoroll/upload_file.html', {'form': form})

@login_required
def upload_camera(request):
    if request.method == 'POST':
        form = UploadCameraForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('img')
            image_count = 0
            for image in images:
                try:
                    process_image(request, image)
                    image_count+=1
                except (GpsMissingException, ConfidenceLevelException) as e:
                    return HttpResponseRedirect('/')
            messages.success(request, f"{image_count} image(s) uploaded successfully.")
            return HttpResponseRedirect('/')
    else:
        form = UploadCameraForm()
    return render(request, 'photoroll/upload_camera.html', {'form': form})
