from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Count
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from .models import *
from django.shortcuts import render

# Create your views here.
def dashboard_view(request):
    return render(request, 'consignee/dashboard.html')

def import_view(request):
    # Hitung total reservasi + 1
    count = Reservasi.objects.filter(reservasi_id__startswith='IM') \
                         .values('reservasi_id') \
                         .distinct() \
                         .count()

    reservasi_id = f"IM{count + 1:09d}"

    return render(request, 'consignee/reservasi_order.html', {
        'generated_reservasi_id': reservasi_id
    })

def export_view(request):
    return render(request, 'consignee/export.html')


def schedule_view(request):
    reservasi_qs = (
        Reservasi.objects
        .values('reservasi_id')  # Group by reservasi_id
        .annotate(jumlah_container=Count('data_container'))  # Hitung container
        .order_by('-reservasi_id')
    )

    # Ambil reservasi_id dari hasil group
    reservasi_ids = [item['reservasi_id'] for item in reservasi_qs]

    # Ambil objek Reservasi asli berdasarkan reservasi_id unik
    reservasi = (
        Reservasi.objects
        .filter(reservasi_id__in=reservasi_ids)
        .order_by('-reservasi_id')
        .distinct('reservasi_id')  # Ambil satu per ID unik
    )

    # Gabungkan dengan hitungan jumlah container
    jumlah_dict = {item['reservasi_id']: item['jumlah_container'] for item in reservasi_qs}
    for r in reservasi:
        r.jumlah_container = jumlah_dict.get(r.reservasi_id, 0)

    return render(request, 'consignee/schedule.html', {'reservasi': reservasi})

def reservasi_detail_view(request, reservasi_id):
    # Ambil semua objek Reservasi yang memiliki reservasi_id yang sama
    reservasi_list = Reservasi.objects.filter(reservasi_id=reservasi_id)

    # Cek apakah ada data yang ditemukan
    if reservasi_list.exists():
        # Mengirimkan reservasi_list ke template untuk ditampilkan
        return render(request, 'consignee/reservasi_detail.html', {'reservasi_list': reservasi_list})
    else:
        # Jika tidak ditemukan, tampilkan pesan error atau redirect
        return render(request, 'error_page.html', {'message': 'Reservasi tidak ditemukan'})

# Function
@csrf_exempt
def simpan_reservasi_db(request):
    if request.method == 'POST':
        try:
            # Pastikan user login
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'message': 'User belum login.'})
            
            user = request.user

            # Ambil dan parsing data dari request
            data = json.loads(request.body)
            reservasi_id = data.get('reservasi_id', '').strip()
            data_container_raw = data.get('data_container', [])
            data_truck_raw = data.get('data_truck', [])

            # Bersihkan string kosong dari masing-masing list
            data_container = [x.strip() for x in data_container_raw if x.strip()]
            data_truck = [x.strip() for x in data_truck_raw if x.strip()]

            # Validasi input setelah pembersihan
            if not reservasi_id or not data_container or not data_truck:
                return JsonResponse({'success': False, 'message': 'Semua data wajib diisi.'})

            if len(data_container) != len(data_truck):
                return JsonResponse({'success': False, 'message': 'Jumlah container dan truck harus sama.'})

            # Simpan record satu per satu
            for container_no, truck_no in zip(data_container, data_truck):
                Reservasi.objects.create(
                    reservasi_id=reservasi_id,
                    data_container=container_no,
                    data_truck=truck_no,
                    consignee=user,
                    status=0,
                    track_in=0,
                )

            return JsonResponse({'success': True, 'message': 'Reservasi berhasil disimpan. Pengecekkan status reservasi ada di menu schedule.'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})