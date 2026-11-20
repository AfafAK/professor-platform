from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('download/<int:resource_id>/', views.download_resource, name='download_resource'),
    path('view/<int:resource_id>/', views.view_resource, name='view_resource'),
]
