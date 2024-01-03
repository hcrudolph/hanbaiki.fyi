from django.urls import path
import photoroll.views as views

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('upload/', views.upload, name='upload'),
    path('archive/', views.archive, name='archive'),
    path('archive/<int:year>/<int:month>/', views.PostByMonthListView.as_view(), name='archive_month'),
    path('archive/<int:year>/', views.PostByYearListView.as_view(), name='archive_year'),
    path('filter/city/', views.CityListView.as_view(), name='filter_city'),
    path('filter/city/<str:city>/', views.PostByCityListView.as_view(), name='post_by_city'),
    path('filter/zip/', views.ZipListView.as_view(), name='filter_zip'),
    path('filter/zip/<str:zip>/', views.PostByZipListView.as_view(), name='post_by_zip'),
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/<str:slug>', views.PostsByTagListView.as_view(), name='tag_detail'),
    path('posts/<int:post_id>', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/map', views.post_map, name='post_map'),
]
