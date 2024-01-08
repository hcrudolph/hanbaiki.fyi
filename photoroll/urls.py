from django.urls import path
import photoroll.views as views

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('about/', views.about, name='about'),
    path('archive/', views.archive, name='archive'),
    path('archive/<int:year>/', views.PostByYearListView.as_view(), name='archive_year'),
    path('archive/<int:year>/<int:month>/', views.PostByMonthListView.as_view(), name='archive_month'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/map/', views.post_map, name='post_map'),
    path('posts/search/city/<str:city>/', views.PostByCityListView.as_view(), name='posts_by_city'),
    path('posts/search/location/', views.current_location, name='current_location'),
    path('posts/search/location/<lat>/<lon>/', views.posts_by_location, name='posts_by_location'),
    path('posts/search/zip/<str:zip>/', views.PostByZipListView.as_view(), name='posts_by_zip'),
    path('posts/search/tags/', views.TagListView.as_view(), name='tag_list'),
    path('posts/search/tags/<str:slug>/', views.PostsByTagListView.as_view(), name='posts_by_tag'),
    path('upload/camera/', views.upload_camera, name='upload_camera'),
    path('upload/file/', views.upload_file, name='upload_file'),
]
