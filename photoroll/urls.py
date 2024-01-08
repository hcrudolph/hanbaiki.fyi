from django.urls import path
import photoroll.views as views

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('about/', views.about, name='about'),
    path('archive/', views.archive, name='archive'),
    path('archive/<int:year>/<int:month>/', views.PostByMonthListView.as_view(), name='archive_month'),
    path('upload/camera/', views.upload_camera, name='upload_camera'),
    path('upload/file/', views.upload_file, name='upload_file'),
]
