from django.contrib import admin
from .models import District
from .models import Zone
from .models import ZoneDistrict

admin.site.register(District)
admin.site.register(Zone)
admin.site.register(ZoneDistrict)

