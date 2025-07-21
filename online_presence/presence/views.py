from django.shortcuts import render
from django.http import JsonResponse
from .models import PresenceLog
from .models import TrainingFace
import face_recognition
import numpy as np
from django.urls import reverse, NoReverseMatch
from .models import ExternalMenu, ExternalAccessMenu, ExternalSubMenu
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from collections import defaultdict
from django.utils import timezone
import uuid
from .utils import get_user_from_token  # sudah kamu miliki

def resolve_url_path(url_str):
    try:
        return reverse(url_str)
    except NoReverseMatch:
        return '#'
    
def dashboard(request):
    token = request.GET.get('token', '')
    user = get_user_from_token(request)

    if not user:
        return render(request, 'presence/unauthorized.html', status=401)

    app_id = user.app_id
    role_id = user.role_id

    menu_ids = ExternalAccessMenu.objects.filter(role_id=role_id).values_list('menu_id', flat=True)

    menus = ExternalMenu.objects.filter(app_id='presence', is_active=True, id__in=menu_ids).order_by('sort')

    data = []
    for menu in menus:
        submenus = ExternalSubMenu.objects.filter(menu_id=menu.id).order_by('sort')
        submenu_list = []
        for submenu in submenus:
            submenu_list.append({
                'id': submenu.id,
                'name': submenu.nama_submenu,
                'icon': submenu.icon_submenu,
                'url': resolve_url_path(submenu.urls),
            })

        data.append({
            'id': menu.id,
            'name': menu.nama_menu,
            'icon': menu.icon_menu,
            'submenus': submenu_list,
        })

    # Ringkasan data absensi HANYA untuk user yang login
    today = timezone.localtime(timezone.now()).date()
    if user.app_id == 'superadmin':
        log_today = PresenceLog.objects.filter(timestamp__date=today)
        total_users = TrainingFace.objects.count()
    else:
        log_today = PresenceLog.objects.filter(email=user.email, timestamp__date=today)
        total_users = TrainingFace.objects.filter(email=user.email).count()


    total_in = log_today.filter(type='in').count()
    total_out = log_today.filter(type='out').count()

    # Hitung keterlambatan user ini saja
    total_late = log_today.filter(
        type='in',
        timestamp__time__gt=datetime.strptime('08:05', '%H:%M').time()
    ).count()

    total_users = TrainingFace.objects.filter(email=user.email).count()

    return render(request, 'presence/dashboard.html', {
        'user': user,
        'menu_with_subs': data,
        'token': token,
        'total_in': total_in,
        'total_out': total_out,
        'total_late': total_late,
        'total_users': total_users,
    })

def train_view(request):
    token = request.GET.get('token', '')
    user = get_user_from_token(request)
    if not user:
        return render(request, 'presence/unauthorized.html', status=401)

    request.user = user 
    # Ambil menu (seperti di dashboard)
    app_id = user.app_id
    role_id = user.role_id
    menu_ids = ExternalAccessMenu.objects.filter(role_id=role_id).values_list('menu_id', flat=True)

    if app_id == 'superadmin':
        menus = ExternalMenu.objects.filter(app_id='presence', is_active=True, id__in=menu_ids).order_by('sort')
    else:
        menus = ExternalMenu.objects.filter(app_id='presence', is_active=True, id__in=menu_ids).order_by('sort')

    menu_data = []
    for menu in menus:
        submenus = ExternalSubMenu.objects.filter(menu_id=menu.id).order_by('sort')
        submenu_list = []
        for submenu in submenus:
            submenu_list.append({
                'id': submenu.id,
                'name': submenu.nama_submenu,
                'icon': submenu.icon_submenu,
                'url': resolve_url_path(submenu.urls),
            })
        menu_data.append({
            'id': menu.id,
            'name': menu.nama_menu,
            'icon': menu.icon_menu,
            'submenus': submenu_list,
        })

    return render(request, 'presence/train.html', {
        'user': user,
        'menu_with_subs': menu_data,
        'token': token,
    })

def absen_view(request):
    token = request.GET.get('token', '')
    user = get_user_from_token(request)
    if not user:
        return render(request, 'presence/unauthorized.html', status=401)

    # Ambil menu seperti di dashboard
    app_id = user.app_id
    role_id = user.role_id
    menu_ids = ExternalAccessMenu.objects.filter(role_id=role_id).values_list('menu_id', flat=True)

    if app_id == 'superadmin':
        menus = ExternalMenu.objects.filter(app_id='presence', is_active=True, id__in=menu_ids).order_by('sort')
    else:
        menus = ExternalMenu.objects.filter(app_id='presence', is_active=True, id__in=menu_ids).order_by('sort')

    menu_data = []
    for menu in menus:
        submenus = ExternalSubMenu.objects.filter(menu_id=menu.id).order_by('sort')
        submenu_list = []
        for submenu in submenus:
            submenu_list.append({
                'id': submenu.id,
                'name': submenu.nama_submenu,
                'icon': submenu.icon_submenu,
                'url': resolve_url_path(submenu.urls),
            })
        menu_data.append({
            'id': menu.id,
            'name': menu.nama_menu,
            'icon': menu.icon_menu,
            'submenus': submenu_list,
        })

    # Proses log absensi
    logs = PresenceLog.objects.filter(email=user.email).order_by('-timestamp')
    grouped_logs = defaultdict(lambda: {'in': None, 'out': None})

    for log in logs:
        local_time = timezone.localtime(log.timestamp)
        key = (log.email, local_time.date())
        log.local_time = local_time
        grouped_logs[key][log.type] = log

    rows = []
    for (email, log_date), data in grouped_logs.items():
        name = data['in'].name if data['in'] else data['out'].name if data['out'] else '-'
        if data['in'] and data['out']:
            duration = data['out'].local_time - data['in'].local_time
            duration_hours = round(duration.total_seconds() / 3600, 2)
        else:
            duration_hours = None

        rows.append({
            'name': name,
            'email': email,
            'date': log_date,
            'checkin_time': data['in'].local_time.time() if data['in'] else None,
            'checkout_time': data['out'].local_time.time() if data['out'] else None,
            'checkin_photo': data['in'].photo.url if data['in'] and data['in'].photo else None,
            'checkout_photo': data['out'].photo.url if data['out'] and data['out'].photo else None,
            'duration_hours': duration_hours,
        })

    return render(request, 'presence/absen.html', {
        'rows': rows,
        'user': user,
        'menu_with_subs': menu_data,
        'token': token,
    })

@csrf_exempt
@csrf_exempt
def recognize_and_log(request):
    if request.method != 'POST' or 'image' not in request.FILES:
        return JsonResponse({'status': 'error', 'message': 'Gambar tidak tersedia'}, status=400)

    absen_type = request.POST.get('type', 'in')
    image_file = request.FILES['image']

    # Ambil user login dari token
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User tidak dikenali'}, status=401)

    image = face_recognition.load_image_file(image_file)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    if not face_encodings:
        return JsonResponse({'status': 'error', 'message': 'Wajah tidak ditemukan'}, status=404)

    # Ambil wajah yang dimiliki user login saja
    faces = TrainingFace.objects.filter(email=user.email)
    if not faces.exists():
        return JsonResponse({'status': 'error', 'message': 'Wajah belum terdaftar untuk akun ini'}, status=404)

    known_encodings = [np.frombuffer(f.encoding, dtype=np.float64) for f in faces]
    known_emails = [f.email for f in faces]

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.45)
        if True in matches:
            matched_index = matches.index(True)
            matched_email = known_emails[matched_index]
            matched_name = faces[matched_index].name

            now_local = timezone.localtime(timezone.now())
            today = now_local.date()

            already_logged = PresenceLog.objects.filter(
                email=matched_email,
                type=absen_type,
                timestamp__date=today
            ).exists()

            if already_logged:
                return JsonResponse({
                    'status': 'info',
                    'message': f'Sudah absen {absen_type} hari ini',
                    'email': matched_email
                })

            # Simpan foto
            image_file.seek(0)
            filename = f"{uuid.uuid4()}.jpg"
            photo_file = ContentFile(image_file.read(), name=filename)

            log = PresenceLog.objects.create(
                email=matched_email,
                name=matched_name,
                photo=photo_file,
                type=absen_type
            )

            return JsonResponse({
                'status': 'success',
                'message': f'Absensi {absen_type} berhasil untuk {matched_name}',
                'email': matched_email,
                'name': matched_name,
                'photo_url': log.photo.url
            })

    return JsonResponse({'status': 'error', 'message': 'Wajah tidak dikenali'})

@csrf_exempt
def train_face(request):
    if request.method == 'POST':
        user = get_user_from_token(request)
        if not user:
            return JsonResponse({'status': 'error', 'message': 'User tidak dikenali'}, status=401)

        # Cek apakah user sudah pernah training sebelumnya
        if TrainingFace.objects.filter(email=user.email).exists():
            return JsonResponse({'status': 'info', 'message': 'Wajah sudah terdaftar'}, status=200)

        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({'status': 'error', 'message': 'Gambar belum dikirim'}, status=400)

        try:
            image = face_recognition.load_image_file(image_file)
            encodings = face_recognition.face_encodings(image)

            if not encodings:
                return JsonResponse({'status': 'error', 'message': 'Wajah tidak terdeteksi'}, status=400)

            encoding_np = encodings[0]
            encoding_bytes = encoding_np.tobytes()

            TrainingFace.objects.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}".strip() or user.email,
                encoding=encoding_bytes
            )

            return JsonResponse({'status': 'success', 'message': 'Wajah berhasil disimpan'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Gunakan metode POST'}, status=405)