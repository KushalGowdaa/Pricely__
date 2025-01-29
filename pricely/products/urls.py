from django.urls import path
from . import views

urlpatterns = [
    path('compare/', views.compare_prices, name='compare_prices'),
    path('suggestions/', views.get_suggestions, name='product_suggestions'),
]