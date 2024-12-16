from django.contrib.auth.models import User
from rest_framework import serializers

from bmstu.models import District
from bmstu.models import Zone
from bmstu.models import ZoneDistrict


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'

class DraftZoneSerializer(serializers.ModelSerializer):
    districts_count = serializers.SerializerMethodField()

    class Meta:
        model = Zone
        fields = ['id', 'districts_count']  # Указываем только нужные поля

    def get_districts_count(self, obj):
        return ZoneDistrict.objects.filter(zone=obj).count()

class ZoneSerializer(serializers.ModelSerializer):
    creator = serializers.CharField(source='creator.username', read_only=True)

    class Meta:
        model = Zone
        fields = '__all__'


class ZoneDistrictSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()

    class Meta:
        model = ZoneDistrict
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs):
        return attrs