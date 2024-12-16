from django.db import connection
from django.shortcuts import render, get_object_or_404, redirect

from bmstu.models import District, Zone, ZoneDistrict

def district_list(request):
    query = request.GET.get('search_district', '').strip()
    filtered_districts = District.objects.filter(status='active')

    if query:
        filtered_districts = filtered_districts.filter(district_name__icontains=query)

    current_zone = Zone.objects.filter(zone_status='draft', creator=request.user).first()
    count = ZoneDistrict.objects.filter(zone_id=current_zone.id).count() if current_zone else 0

    context = {
        'districts': filtered_districts,
        'count': count,
        'current_zone_id': current_zone.id if current_zone else None
    }

    return render(request, 'districts.html', context)


def district_about(request, id):
    district = get_object_or_404(District, id=id)
    context = {'district': district}
    return render(request, 'about_district.html', context)


def zone(request, zone_id):
    zone = get_object_or_404(Zone, id=zone_id, zone_status='draft')
    zone_districts = ZoneDistrict.objects.filter(zone=zone).select_related('district')

    cart_items = []
    total_flight_time_minutes = 0

    for zone_district in zone_districts:
        district = zone_district.district
        total_flight_time_minutes += district.flight_time
        cart_items.append({
            'title': district.district_name,
            'image_url': district.image_url,
            'flight_time': district.formatted_flight_time(),
            'description': zone.description,
            'is_main': zone_district.is_main,
            'priority': zone_district.priority,
        })

    hours = total_flight_time_minutes // 60
    minutes = total_flight_time_minutes % 60
    total_flight_time_formatted = f"{hours} ч. {minutes} мин." if hours else f"{minutes} мин."

    context = {
        'cart_items': cart_items,
        'zone_title': zone.zone_name,
        'current_zone_id': zone.id,
        'total_flight_time': total_flight_time_formatted,
    }

    return render(request, 'zones.html', context)


def delete_zone(request):
    if request.method == 'POST':
        zone_id = request.POST.get('zone_id')
        user = request.user
        if zone_id:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE public.bmstu_zone SET zone_status = 'deleted' WHERE id = %s AND creator_id=%s AND zone_status = 'draft'",
                    [zone_id, user.id]
                )
            return redirect('district_list')
    return redirect('district_list')


def add_district_to_current_zone(request):
    if request.method == 'POST':
        district_id = request.POST.get('district_id')
        zone_id = request.POST.get('zone_id')
        next_url = request.POST.get('next')

        if not district_id:
            return render(request, 'districts.html')

        district = get_object_or_404(District, id=district_id)

        current_zone, _ = Zone.objects.get_or_create(
            zone_status='draft', creator=request.user,
            defaults={'zone_name': "Утренний рейд", 'description': "Спальный район, минимальная высота пролета - 140 м"}
        )

        zone_district, _ = ZoneDistrict.objects.get_or_create(zone=current_zone, district=district)

        return redirect(next_url)
