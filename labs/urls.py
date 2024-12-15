# urls.py
from django.urls import path
from bmstu import views

urlpatterns = [
    path('', views.district_list, name='district_list'),
    path('district_about/<int:id>/', views.district_about, name='district_about'),
    path('zone/<int:zone_id>/', views.zone, name='zone')

]
