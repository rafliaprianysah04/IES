from django.shortcuts import render,  get_object_or_404, redirect
from django.urls import reverse, NoReverseMatch
from .utils import get_user_from_token, validate_container_id
from .models import *
from django.template.loader import get_template
from django.shortcuts import redirect
from django.http import HttpResponse,JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import os
from django.core.files.storage import default_storage
from django.db import connection
import re
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
import time


def resolve_url_path(url_str):
    try:
        return reverse(url_str)
    except NoReverseMatch:
        return '#'  # fallback jika nama route tidak ditemukan

def dashboard(request): 
    user = get_user_from_token(request)
    if not user:
        return render(request, 'unauthorized.html', status=401)

    request.user = user  # Wajib agar context processor bisa membaca

    return render(request, 'dashboard_surveyor.html', {'user': user, 'token': request.GET.get('token', '')})


#yang manual
def char_to_num(char):
    values = {
        'A': 10, 'B': 12, 'C': 13, 'D': 14, 'E': 15, 'F': 16, 'G': 17, 'H': 18, 'I': 19,
        'J': 20, 'K': 21, 'L': 23, 'M': 24, 'N': 25, 'O': 26, 'P': 27, 'Q': 28, 'R': 29,
        'S': 30, 'T': 31, 'U': 32, 'V': 34, 'W': 35, 'X': 36, 'Y': 37, 'Z': 38
    }
    if char.isdigit():
        return int(char)
    return values.get(char.upper(), 0)

def calculate_check_digit(cont):
    total = 0
    factors = [2**i for i in range(10)]  # hanya 10 karakter pertama

    for i, char in enumerate(cont[:10]):
        total += char_to_num(char) * factors[i]
    
    return total % 11 if total % 11 != 10 else 0

def validate_container_id(cont):
    if len(cont) != 11:
        return False, None
    
    try:
        check_digit_actual = int(cont[-1])
    except ValueError:
        return False, None

    check_digit_calculated = calculate_check_digit(cont)
    return check_digit_calculated == check_digit_actual, check_digit_calculated

def get_next_id():
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(id) FROM survey_ins")
        row = cursor.fetchone()
    return (row[0] or 0) + 1

def surveyin1(request):
    result = None
    cont = request.POST.get('cont') or ''  # Ambil langsung dari form
    action = request.POST.get('action')

    if request.method == 'POST':
        cont = request.POST.get('cont')
        is_valid, calculated_digit = validate_container_id(cont)
        result = {
            'is_valid': is_valid,
            'cont': cont,
            'calculated_digit': calculated_digit
        }

        # Jika hanya cek validasi, return ke halaman saja dengan hasil validasi
        if action == 'check':
            return render(request, 'surveyin/surveyin.html', {'result': result})

        # Jika submit dan nomor kontainer valid, simpan ke database
        if action in ['submit', 'generate_qr']:
                if not is_valid:
                    # Jangan simpan jika tidak valid
                    result['error'] = "Nomor kontainer tidak valid. Harap periksa kembali."
                    return render(request, 'surveyin/surveyin.html', {'result': result})
                # Ambil semua data lainnya
                cont = request.POST.get('cont')
                customer_code = request.POST.get('customer')
                cont_size = request.POST.get('size')
                cont_type = request.POST.get('type')  
                condition = request.POST.get('condition')
                washing = request.POST.get('washing')   
                grade_depot = request.POST.get('grade')
                act_in = request.POST.get('act_in')
                mnf_month = request.POST.get('mnf_month') or ''
                mnf_year = (request.POST.get('mnf_year1') or '') + (request.POST.get('mnf_year2') or '')
                tare = (request.POST.get('tare1') or '') + (request.POST.get('tare2') or '') + (request.POST.get('tare3') or '')
                payload = (
                    (request.POST.get('payload1') or '') +
                    (request.POST.get('payload2') or '') +
                    (request.POST.get('payload3') or '') +
                    (request.POST.get('payload4') or '')
                )
                haulier_name = request.POST.get('haulier_name')
                truck_no = request.POST.get('truck_no')
                washed_by = request.POST.get('washed_by')
                remark = request.POST.get('remark')
                manufacture = f"{mnf_month}-{mnf_year}"

                new_id = get_next_id()
                SurveyIns.objects.create(
                    id=new_id,
                    cont=cont,
                    customer_code=customer_code,
                    cont_size=cont_size,
                    cont_type=cont_type,
                    condition=condition,
                    washing=washing,
                    grade_depot=grade_depot,
                    act_in=act_in,
                    manufacture=manufacture,
                    tare=tare,
                    payload=payload,
                    haulier_in=haulier_name,
                    truck_no_in=truck_no,
                    washed_by=washed_by,
                    remark=remark,
                    created_at=now(),
                    updated_at=now()
                )
                    # Generate QR Code
                if action == 'generate_qr':      
                    qr_data = f"Container: {cont}\nCustomer: {customer_code}\nSize/Type: {cont_size}/{cont_type}\nCondition: {condition}\nHaulier: {haulier_name}\nTruck: {truck_no}"
                    qr = qrcode.make(qr_data)
                    qr_filename = f"qr_{cont}.png"
                    qr_path = os.path.join("qrcodes", qr_filename)

                    # Simpan QR ke media/qrcodes/
                    qr_file = ContentFile(b'')
                    qr.save(qr_file, format='PNG')
                    default_storage.save(qr_path, qr_file)

                    qr_url = default_storage.url(qr_path)

                    messages.success(request, "Data berhasil disimpan dan QR-Code dibuat.")
                    return render(request, 'surveyin/surveyin.html', {
                            'success': True,
                            'qr_url': qr_url,
                        })
                if action == 'submit':
                    return render(request, 'surveyin/surveyin.html', {
                    'success': True,
                    'show_upload_modal': True,  # Menampilkan modal upload foto
                    'cont': cont  # Pass cont untuk digunakan di URL modal
                })
        result['success'] = "Data berhasil disimpan."

    return render(request, 'surveyin/surveyin.html', {'result': result})


def surveyin(request):
    deteksi_kontainer = KontainerTerdeteksi.objects.filter(status='baru').order_by('waktu_deteksi')
    result = {}
    initial_data = {}
    cont = request.POST.get('cont', '').upper() if request.method == 'POST' else ''
    cont = re.sub(r'\s+', '', cont)  # Hilangkan spasi
    show_upload_modal = False
    qr_url = None
    success = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if deteksi_kontainer.count() == 1:
            # Auto-pilih container jika hanya satu hasil
            cont = deteksi_kontainer.first().nomor_kontainer.upper().strip()
            cont = re.sub(r'\s+', '', cont)
            show_upload_modal = True  # Misal jika ingin langsung trigger modal

        elif deteksi_kontainer.count() > 1 and not cont:
            # Jika belum ada input, beri info bahwa tersedia banyak pilihan
            result['info'] = f"{deteksi_kontainer.count()} kontainer terdeteksi, silakan pilih."

        # Jika ditemukan, update status jadi "dipakai"
        if cont:
            try:
                deteksi_obj = KontainerTerdeteksi.objects.get(nomor_kontainer=cont)
                if deteksi_obj.status == 'baru':
                    deteksi_obj.status = 'digunakan'
                    deteksi_obj.save()
            except KontainerTerdeteksi.DoesNotExist:
                pass
        if action == 'check' and cont:
            is_valid, calculated_digit = validate_container_id(cont)

            if is_valid:
                try:
                    survey = SurveyIns.objects.get(cont__iexact=cont)

                    mnf_month, mnf_year1, mnf_year2 = '', '', ''
                    if survey.manufacture and '/' in survey.manufacture:
                        parts = survey.manufacture.split('/')
                        mnf_month = parts[0].zfill(2)
                        if len(parts) > 1 and len(parts[1]) == 2:
                            mnf_year1, mnf_year2 = parts[1][0], parts[1][1]

                    tare = survey.tare or ''
                    payload = survey.payload or ''

                    initial_data = {
                        'customer': survey.customer_code,
                        'size': survey.cont_size,
                        'type': survey.cont_type,
                        'condition': survey.condition,
                        'washing': survey.washing,
                        'grade': survey.grade_depot,
                        'mnf_month': mnf_month,
                        'mnf_year1': mnf_year1,
                        'mnf_year2': mnf_year2,
                        'tare1': tare[0] if len(tare) >= 1 else '',
                        'tare2': tare[1] if len(tare) >= 2 else '',
                        'tare3': tare[2:] if len(tare) >= 3 else '',
                        'payload1': payload[0] if len(payload) >= 1 else '',
                        'payload2': payload[1] if len(payload) >= 2 else '',
                        'payload3': payload[2] if len(payload) >= 3 else '',
                        'payload4': payload[3:] if len(payload) >= 4 else '',
                        'haulier_name': survey.haulier_in,
                        'truck_no': survey.truck_no_in,
                        'act_in': survey.act_in,
                        'washed_by': survey.washed_by,
                        'remark': survey.remark,
                    }
                    result['success'] = "Data ditemukan dan dimuat otomatis dari database."

                except SurveyIns.DoesNotExist:
                    result['success'] = "Nomor kontainer valid, namun belum pernah diinput."
                    initial_data = {}
            else:
                result['error'] = f"Nomor kontainer TIDAK VALID. Seharusnya check digit adalah {calculated_digit}"

            result['cont'] = cont
            result['is_valid'] = is_valid

        elif action == 'submit':
            # Simpan data input awal ke SurveyInNew
            # Gabungkan manufacture
            mnf_month = request.POST.get('mnf_month', '')
            mnf_year1 = request.POST.get('mnf_year1', '')
            mnf_year2 = request.POST.get('mnf_year2', '')
            manufacture = f"{mnf_month}/{mnf_year1}{mnf_year2}" if mnf_month and mnf_year1 and mnf_year2 else ''

            # Gabungkan tare
            tare1 = request.POST.get('tare1', '')
            tare2 = request.POST.get('tare2', '')
            tare3 = request.POST.get('tare3', '')
            tare = f"{tare1}{tare2}{tare3}"

            # Gabungkan payload
            payload1 = request.POST.get('payload1', '')
            payload2 = request.POST.get('payload2', '')
            payload3 = request.POST.get('payload3', '')
            payload4 = request.POST.get('payload4', '')
            payload = f"{payload1}{payload2}{payload3}{payload4}"


            survey = SurveyInsNew.objects.create(
                cont=cont,
                customer_code = request.POST.get('customer', ''),
                cont_size = request.POST.get('size', ''),
                cont_type = request.POST.get('type', ''),
                condition = request.POST.get('condition', ''),
                washing = request.POST.get('washing', ''),
                manufacture=manufacture,
                tare=tare,
                payload=payload,
                grade_depot = request.POST.get('grade_depot', ''),
                haulier_in = request.POST.get('haulier_in', ''),
                truck_no_in = request.POST.get('truck_no_in', ''),
                remark = request.POST.get('remark', ''),
                
                # handling image uploads via request.FILES
                foto = request.FILES.get('foto'),
                qr_code = request.FILES.get('qr_code'),
                created_at = timezone.now(),
                updated_at = timezone.now(),
            )
            
            request.session['survey_id'] = survey.id
            # Render kembali dengan modal terbuka
            return render(request, 'surveyin/surveyin.html', {
                'show_upload_modal': True,
                'survey': survey,
                'success_message': 'Data awal berhasil disimpan. Silakan upload foto dan isi tambahan.',
            })

        elif action == 'final_submit':
            survey_id = request.session.get('survey_id')
            if survey_id:
                try:
                    survey = SurveyInsNew.objects.get(id=survey_id)

                    # Simpan tambahan: upload foto, dll
                    if 'foto' in request.FILES:
                        survey.foto = request.FILES['foto']

                    # Generate QR
                    qr = qrcode.make(survey.cont)
                    buffer = BytesIO()
                    qr.save(buffer, format='PNG')
                    file_name = f"qr_codes/{survey.cont}.png"
                    survey.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)

                    survey.save()
                    request.session.pop('survey_id', None)

                    return render(request, 'surveyin/surveyin.html', {
                        'survey': survey,
                        'show_upload_modal': True,
                        'success_message': 'Data lengkap berhasil disimpan dan QR Code telah dibuat.',
                    })
                except SurveyInsNew.DoesNotExist:
                    return render(request, 'surveyin/surveyin.html', {
                        'error_message': 'Data tidak ditemukan untuk update lanjutan.',
                    })


        elif action == 'generate_qr':
            # Buat QR dari nomor kontainer
            qr = qrcode.make(cont)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            file_name = f"qr_codes/{cont}.png"
            file_path = default_storage.save(file_name, ContentFile(buffer.getvalue()))

            qr_url = default_storage.url(file_path)
            
            result['success'] = "QR Code berhasil dibuat."
            success = True

    return render(request, 'surveyin/surveyin.html', {
        'result': result,
        'initial_data': initial_data,
        'digits': range(10),
        'double_digits': [str(i).zfill(2) for i in range(1, 13)],
        'show_upload_modal': show_upload_modal,
        'qr_url': qr_url,
        'success': success,
        'cont': cont,
        'deteksi_kontainer': deteksi_kontainer,
    })

def get_container_qrcode(request):
    cont = request.GET.get('cont', '').upper()
    try:
        survey = SurveyIns.objects.get(cont__iexact=cont)
        mnf_month, mnf_year1, mnf_year2 = '', '', ''
        if survey.manufacture and '/' in survey.manufacture:
            parts = survey.manufacture.split('/')
            mnf_month = parts[0].zfill(2)
            if len(parts) > 1 and len(parts[1]) == 2:
                mnf_year1, mnf_year2 = parts[1][0], parts[1][1]

        return JsonResponse({
            'customer_code': survey.customer_code,
            'cont_size': survey.cont_size,
            'cont_type': survey.cont_type,
            'condition': survey.condition,
            'grade_depot': survey.grade_depot,
            'manufacture': survey.manufacture,
            'mnf_month': mnf_month,
            'mnf_year1': mnf_year1,
            'mnf_year2': mnf_year2,
            # Tidak dikirim: washing, haulier_in, truck_no_in, remark
        })
    except SurveyIns.DoesNotExist:
        return JsonResponse({'error': 'Data tidak ditemukan'}, status=404)