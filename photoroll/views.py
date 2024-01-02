from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants as messages
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views import generic
from .forms import UploadForm
from .models import *

######################
# Global definitions #
######################

MESSAGE_TAGS = {
    messages.ERROR: "danger",
    "silent": "light",
}

######################
# View definitions   #
######################

class PostListView(generic.ListView):
    model = Post
    template_name = 'photoroll/index.html'
    paginate_by = 9

    def get_queryset(self):
        return Post.objects.filter(is_published=True)

def post_detail(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
    )
    context = {
        'post': post,
    }
    return render(request, 'photoroll/post.html', context)

def post_map(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
    )
    context = {
        'id': post.id,
        'lat': post.machine.lat,
        'lon': post.machine.lon,
        'mapbox_token': settings.MAPBOX_ACCESS_TOKEN,
    }
    return render(request, 'photoroll/map.html', context)

def archive(request):
    earliest_post = Post.objects.earliest()
    latest_post = Post.objects.latest()
    earliest_year = earliest_post.date_published.year
    latest_year = latest_post.date_published.year + 1
    year_range = range(earliest_year, latest_year)

    context = {
        'years': year_range,
    }
    return render(request, 'photoroll/archive.html', context)

class TagListView(generic.ListView):
    model = Tag
    template_name = 'photoroll/tag_list.html'

class PostsByTagListView(generic.ListView):
    model = Post
    template_name = 'photoroll/index.html'
    paginate_by = 9

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(tags=self.tag)

class PostByYearListView(generic.ListView):
    model = Post
    template_name = 'photoroll/index.html'
    paginate_by = 9

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            date_published__year=self.kwargs['year'],
        )

class PostByMonthListView(generic.ListView):
    model = Post
    template_name = 'photoroll/index.html'
    paginate_by = 9

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            date_published__year=self.kwargs['year'],
            date_published__month=self.kwargs['month'],
        )

class PostByCityListView(generic.ListView):
    model = Post
    template_name = 'photoroll/index.html'
    paginate_by = 9

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            machine__city=self.kwargs['city'],
        )

class PostByZipListView(generic.ListView):
    model = Post
    template_name = 'photoroll/index.html'
    paginate_by = 9

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            machine__postcode=self.kwargs['zip'],
        )

######################
# Restricted Views   #
######################

@login_required
def upload(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            vm = form.save(commit=False)
            vm.created_by = request.user
            vm = form.save()
            messages.success(request, "Image uploaded successfully.")
            return HttpResponseRedirect("/")
    else:
        form = UploadForm()
    return render(request, "photoroll/upload.html", {"form": form})
