from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Count
import json
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from consignee.models import *
from .models import *
from django.shortcuts import render
import traceback

# Create your views here.
def dashboard_view(request):
    return render(request, 'customer_service/dashboard.html')

def approve_reservasi_view(request):
    # Ambil semua reservasi dan kelompokkan berdasarkan reservasi_id unik
    reservasi_ids = (
        Reservasi.objects
        .values_list('reservasi_id', flat=True)
        .distinct()
        .order_by('-reservasi_id')
    )

    # Ambil semua reservasi yang unik berdasarkan reservasi_id
    reservasi_list = []
    for reservasi_id in reservasi_ids:
        # Ambil semua entri dengan reservasi_id yang sama
        group = Reservasi.objects.filter(reservasi_id=reservasi_id)
        
        if group.exists():
            obj = group.first()
            obj.jumlah_container = group.count()  # Jumlah container sesuai dengan detail
            reservasi_list.append(obj)

    return render(request, 'customer_service/approve_reservasi.html', {'reservasi': reservasi_list})

def reservasi_detail_view(request, reservasi_id):
    try:
        # Gunakan filter untuk mengambil semua objek dengan reservasi_id yang sama
        reservasi_list = Reservasi.objects.filter(reservasi_id=reservasi_id)

        if reservasi_list.exists():
            # Jika ada hasil, buat list data untuk setiap reservasi
            data = [{
                'reservasi_id': reservasi.reservasi_id,
                'consignee': {
                    'name': reservasi.consignee.first_name + ' ' + reservasi.consignee.last_name if reservasi.consignee else None,
                },
                'status': reservasi.get_status_display(),
                'track_in': reservasi.get_track_in_display(),
                'track_out': reservasi.get_track_out_display() if reservasi.track_out is not None else None,
                'created_at': reservasi.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': reservasi.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'containers': [
                    {'name': reservasi.data_container, 'truck': reservasi.data_truck}
                ]
            } for reservasi in reservasi_list]

            return JsonResponse({'reservasi': data})

        else:
            return JsonResponse({'error': 'Reservasi tidak ditemukan'}, status=404)

    except Exception as e:
        traceback.print_exc()  # log error di console
        return JsonResponse({'error': str(e)}, status=500)

def approve_reservasi_done(request, reservasi_id):
    # Mengambil seluruh reservasi yang cocok dengan reservasi_id
    reservasi_list = Reservasi.objects.filter(reservasi_id=reservasi_id)

    if not reservasi_list:
        return JsonResponse({'error': 'Reservasi tidak ditemukan'}, status=404)
    
    # Melakukan update status pada setiap objek reservasi
    for reservasi in reservasi_list:
        reservasi.status = 1  # Ubah status menjadi "In Progress" (1)
        reservasi.save()  # Menyimpan perubahan

    return JsonResponse({'message': 'Reservasi telah disetujui'}, status=200)


