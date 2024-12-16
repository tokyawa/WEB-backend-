from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from bmstu.serializers import DistrictSerializer, ZoneSerializer, ZoneDistrictSerializer, UserSerializer, \
    DraftZoneSerializer
from .minio import add_pic, delete_pic
from .models import District, Zone, ZoneDistrict
from .singletons import CreatorSingleton


class DistrictListView(APIView):
    serializer_class = DistrictSerializer
    draft_zone_serializer = DraftZoneSerializer
    user_creator = CreatorSingleton.get_creator()

    # Метод для получения списка активных районов и черновика пролета
    def get(self, request, format=None):
        district_name_query = request.query_params.get('district_name', '').strip()
        active_districts = District.objects.filter(status="active")

        if district_name_query:
            active_districts = active_districts.filter(district_name__icontains=district_name_query)

        serialized_districts = self.serializer_class(active_districts, many=True)

        draft_zone = Zone.objects.filter(zone_status="draft", creator=self.user_creator).first()
        draft_zone_data = self.draft_zone_serializer(draft_zone).data if draft_zone else None

        if district_name_query:
            return Response({'districts': serialized_districts.data})
        else:
            return Response({
                'districts': serialized_districts.data,
                'draft_zone': draft_zone_data
            })

    # Метод для добавления нового района
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DistrictAddToDraftZoneView(APIView):
    zone_serializer_class = ZoneDistrictSerializer
    user_creator = CreatorSingleton.get_creator()

    def post(self, request, id, format=None):
        district = get_object_or_404(District, id=id, status="active")

        draft_zone = Zone.objects.filter(creator=self.user_creator, zone_status='draft').first()

        if draft_zone:

            district_zone = ZoneDistrict.objects.create(
                zone=draft_zone,
                district=district,
                priority="medium",
                is_main=0
            )
            message = "Район добавлен в существующий черновик пролета"
        else:

            draft_zone = Zone.objects.create(
                creator=self.user_creator,
                zone_status='draft',
                zone_name='Вечерняя проверка районов',
            )
            district_zone = ZoneDistrict.objects.create(
                zone=draft_zone,
                district=district,
                priority="medium",
                is_main=0
            )
            message = "Район добавлен в новый черновик пролета"

        serializer = self.zone_serializer_class(district_zone)
        return Response({"message": message, "draft_zone": serializer.data},
                        status=status.HTTP_201_CREATED)


class DistrictDetailView(APIView):
    serializer_class = DistrictSerializer

    # Метод для получения подробной информации о районе
    def get(self, request, id, format=None):
        district = get_object_or_404(District, id=id, status="active")

        serializer = self.serializer_class(district)
        return Response(serializer.data)

    # Метод для изменения информации о районе
    def put(self, request, id, format=None):
        district = get_object_or_404(District, id=id, status="active")

        serializer = self.serializer_class(district, data=request.data, partial=True)

        if 'pic' in serializer.initial_data:
            pic_result = add_pic(district, serializer.initial_data['pic'])
            if 'error' in pic_result.data:
                return pic_result

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Метод для удаления района
    def delete(self, request, id, format=None):

        district = get_object_or_404(District, id=id)

        if not delete_pic(district):
            return Response({"error": "Не удалось удалить изображение из MinIO."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        district.status = 'deleted'
        district.image_url = ""
        district.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # Метод для добавления изображения к району
    def post(self, request, id, format=None):

        district = get_object_or_404(District, id=id)

        if 'pic' not in request.data:
            return Response({"error": "Нет файла изображения."}, status=status.HTTP_400_BAD_REQUEST)

        pic = request.data['pic']
        pic_result = add_pic(district, pic)

        if 'error' in pic_result.data:
            return pic_result

        district.save()
        serializer = self.serializer_class(district)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ZoneListView(APIView):

    serializer_class = ZoneSerializer
    user_creator = CreatorSingleton.get_creator()

    # Метод для получения пролета кроме в статусе черновик и удален
    def get(self, request, format=None):

        zones = Zone.objects.exclude(zone_status__in=['deleted', 'draft']).filter(creator=self.user_creator)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        status_filter = request.query_params.get('status')
        if status_filter:
            zones = zones.filter(zone_status=status_filter)

        if start_date and end_date:
            zones = zones.filter(created_at__range=[start_date, end_date])

        serializer = self.serializer_class(zones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ZoneDetailView(APIView):
    zone_serializer_class = ZoneSerializer
    zone_district_serializer_class = ZoneDistrictSerializer

    # Получение пролета и его районов
    def get(self, request, id, format=None):

        zone = get_object_or_404(Zone, id=id)
        districts = ZoneDistrict.objects.filter(zone=zone)

        districts_data = self.zone_district_serializer_class(districts, many=True).data
        serializer = self.zone_serializer_class(zone)

        data = serializer.data
        data['districts'] = districts_data
        return Response(data)

    # Удаление пролета
    def delete(self, request, id, format=None):

        zone = get_object_or_404(Zone, id=id)

        zone.zone_status = 'deleted'
        zone.save()

        serializer = self.zone_serializer_class(zone)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, id, format=None):
        zone = get_object_or_404(Zone, id=id)
        action = request.data.get('action')  # Определяем действие

        if action == 'update':
            # Логика обновления
            serializer = self.zone_serializer_class(zone, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'complete':
            # Логика завершения
            moderator = CreatorSingleton.get_moderator()
            if not zone.submitted_at:
                return Response({"error": "Пролет не сформирован"}, status=status.HTTP_400_BAD_REQUEST)

            zone.recipe_status = 'completed'
            zone.completed_at = timezone.now()
            zone.moderator = moderator
            zone.priority_summary_cache = zone.priority_summary
            zone.save()

            serializer = self.zone_serializer_class(zone)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif action == 'reject':
            # Логика отклонения
            moderator = CreatorSingleton.get_moderator()
            if not zone.submitted_at:
                return Response({"error": "Пролет не сформирован"}, status=status.HTTP_400_BAD_REQUEST)

            zone.recipe_status = 'rejected'
            zone.moderator = moderator
            zone.completed_at = timezone.now()
            zone.save()

            serializer = self.zone_serializer_class(zone)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif action == 'submit':
            # Логика формирования
            if not zone.zone_name:
                return Response({"error": "Название заявки обязательно."}, status=status.HTTP_400_BAD_REQUEST)

            zone.zone_status = 'submitted'
            zone.submitted_at = timezone.now()
            zone.save()

            serializer = self.zone_serializer_class(zone)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Некорректное действие."}, status=status.HTTP_400_BAD_REQUEST)


class ZoneDistrictDetailView(APIView):
    serializer_class = ZoneDistrictSerializer

    # Удаление района из пролета
    def delete(self, request, zone_id, district_id, format=None):

        zone_district_link = get_object_or_404(ZoneDistrict, zone_id=zone_id, district_id=district_id)

        zone_district_link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Обновление приоритета и статуса района
    def put(self, request, zone_id, district_id, format=None):

        zone_district_link = get_object_or_404(ZoneDistrict, zone_id=zone_id, district_id=district_id)

        serializer = self.serializer_class(zone_district_link, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(APIView):

    serializer_class = UserSerializer
    user_moderator = CreatorSingleton.get_moderator()

    # Регистрация пользователя
    def post(self, request, format=None):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            password = serializer.validated_data['password']
            serializer.validated_data['password'] = make_password(password)

            user = User(**{key: value for key, value in serializer.validated_data.items() if
                           key not in ['groups', 'user_permissions']})
            user.save()

            groups = serializer.validated_data.get('groups', None)
            if groups:
                user.groups.set(groups)

            user_permissions = serializer.validated_data.get('user_permissions', None)
            if user_permissions:
                user.user_permissions.set(user_permissions)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):

        user = self.user_moderator
        serializer = self.serializer_class(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):

    # Аутентификация пользователя
    def post(self, request, format=None):
        return Response({"error": "Метод не определен"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class UserLogOutView(APIView):

    # Деавторизация пользователя
    def post(self, request, format=None):
        return Response({"error": "Метод не определен"}, status=status.HTTP_501_NOT_IMPLEMENTED)
