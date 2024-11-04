# urls.py
from django.urls import path
from bmstu import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('info/<int:district_id>/', views.info, name='district_info'),
    path('orderscart/', views.orders_cart, name='orderscart'),
    path('add_to_cart/<int:district_id>/', views.add_to_cart, name='add_to_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
]
