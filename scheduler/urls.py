from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact, name='contact'),
    path('api/slots/', views.get_slots, name='get_slots'),
    path('api/book/<int:slot_id>/', views.book_slot, name='book_slot'),
]
