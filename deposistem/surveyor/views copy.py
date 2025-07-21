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
    result = {}
    initial_data = {}
    cont = request.POST.get('cont', '').upper() if request.method == 'POST' else ''
    cont = re.sub(r'\s+', '', cont)  # Hilangkan spasi
    show_upload_modal = False
    qr_url = None
    success = None

    if request.method == 'POST':
        action = request.POST.get('action')

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
            # proses simpan
            pass

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
        'double_digits': ['00', '10', '20', '30', '40', '50', '60', '70', '80', '90'],
        'show_upload_modal': show_upload_modal,
        'qr_url': qr_url,
        'success': success,
        'cont': cont,
    })
