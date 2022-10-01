from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('product/<slug>/', views.ItemDetailView.as_view(), name='detail'),
]
