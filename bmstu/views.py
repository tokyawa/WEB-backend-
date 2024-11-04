from django.shortcuts import render, redirect
from django.conf import settings

MINIO_BASE_URL = f'{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/'

# Статические данные о районах
districts = [
    {
        'id': 1,
        'name': 'академический',
        'title': 'Академический',
        'image_file': f'{MINIO_BASE_URL}akademicheskiy.jpg',
        'flight_time': '2 часа 45 минут',
        'info': 'Академический район — это центр знаний с научными учреждениями!',
    },
    {
        'id': 2,
        'name': 'алексеевский',
        'title': 'Алексеевский',
        'image_file': f'{MINIO_BASE_URL}alekseevskoe.jpg',
        'flight_time': '1 час 30 минут',
        'info': 'Алексеевский район — это уютный район с парками, жилыми кварталами и развитой инфраструктурой.',
    },
    {
        'id': 3,
        'name': 'алтуфьевский',
        'title': 'Алтуфьевский',
        'image_file': f'{MINIO_BASE_URL}altufyevskoe.jpg',
        'flight_time': '1 час 20 минут',
        'info': 'Алтуфьевский район — это зеленый и спокойный район с жилыми кварталами, парками.',
    },
    {
        'id': 4,
        'name': 'арбат',
        'title': 'Арбат',
        'image_file': f'{MINIO_BASE_URL}arbat.jpg',
        'flight_time': '25 минут',
        'info': 'Арбат — исторический район Москвы с живописными улочками, культурными памятниками.',
    },
    {
        'id': 5,
        'name': 'аэропорт',
        'title': 'Аэропорт',
        'image_file': f'{MINIO_BASE_URL}aeroport.jpg',
        'flight_time': '1 час 15 минут',
        'info': 'Аэропорт — динамичный район с развитой транспортной инфраструктурой...',
    },
    {
        'id': 6,
        'name': 'беговой',
        'title': 'Беговой',
        'image_file': f'{MINIO_BASE_URL}begovoe.jpg',
        'flight_time': '1 час 55 минут',
        'info': 'Беговой район — зелёное и спокойное место с удобной инфраструктурой...',
    },
]

def homepage(request):
    search_query = request.GET.get('districtSearch', '').lower()
    filtered_districts = [district for district in districts if search_query in district['title'].lower()] if search_query else districts
    return render(request, 'homepage.html', {'districts': filtered_districts})

def info(request, district_id):
    district_info = next((district for district in districts if district['id'] == int(district_id)), None)
    return render(request, 'info.html', {'district': district_info})


def orders_cart(request):
    cart = request.session.get('cart', [])
    search_query = request.GET.get('search', '').lower()
    districts_in_cart = [district for district in districts if district['id'] in cart]
    if search_query:
        districts_in_cart = [district for district in districts_in_cart if search_query in district['title'].lower()]

    return render(request, 'orderscart.html', {'districts': districts_in_cart})

def add_to_cart(request, district_id):
    cart = request.session.get('cart', [])
    if district_id not in cart:
        cart.append(district_id)
    request.session['cart'] = cart
    return redirect('homepage')

def clear_cart(request):
    # Очищаем корзину, просто удаляем ее из сессии
    if 'cart' in request.session:
        del request.session['cart']  # Удаляем корзину из сессии
    return redirect('orderscart')  # Перенаправляем на страницу корзины
