from django.urls import path
from . import views

urlpatterns = [
    path('', views.research_and_publications, name='research_and_publications'),
]
