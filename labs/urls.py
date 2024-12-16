# urls.py
from django.urls import path
from bmstu import views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.district_list, name='district_list'),
    path('district_about/<int:id>/', views.district_about, name='district_about'),
    path('zone/<int:zone_id>/', views.zone, name='zone'),
    path('add-district/', views.add_district_to_current_zone, name='add_district_to_current_zone'),
    path('delete_zone/', views.delete_zone, name='delete_zone'),
]
