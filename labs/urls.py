from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from bmstu.views import *

router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # URL для работы с районами
    path('districts/', DistrictListView.as_view(), name='districts'),
    path('district/<int:id>/', DistrictDetailView.as_view(), name='about_district'),
    path('district/<int:id>/draft/', DistrictAddToDraftZoneView.as_view(), name='district_with_draft_zone'),

    # URL для работы с пролетами
    path('zone/', ZoneListView.as_view(), name='zone_list'),
    path('zone/<int:id>/', ZoneDetailView.as_view(), name='about_zone'),

    path('zone/<int:zone_id>/district/<int:district_id>/', ZoneDistrictDetailView.as_view(),
         name='zone_district_detail'),

    # URL для работы с пользователями
    path('user/reg/', UserRegistrationView.as_view(), name='user_reg'),
    path('user/update/', UserRegistrationView.as_view(), name='user_update'),
    path('user/log/', UserLoginView.as_view(), name='user_log'),
    path('user/logout/', UserLogOutView.as_view(), name='user_logout'),
]
