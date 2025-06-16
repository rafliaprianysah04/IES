from django.shortcuts import render
from django.http import JsonResponse
from .utils import is_valid_container, generate_unique_referal  
import re
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from .models import SurveyInContainer, MappingContainer  # sesuaikan nama modelnya ya
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm

def dashboard_view(request):
    return render(request, 'surveyor/dashboard.html')

def container_in_view(request):
    return render(request, 'surveyor/container_in.html')

def container_in_list_view(request):
    containers = SurveyInContainer.objects.all().order_by('-created_at')
    return render(request, 'surveyor/container_in_list.html', {'containers': containers})

def upload_rooftop_view(request):
    return render(request, 'surveyor/upload_rooftop.html')

def upload_under_view(request):
    return render(request, 'surveyor/upload_under.html')

def shifting_view(request):
    return render(request, 'surveyor/shifting.html')

def cek_valid_container(request):
    container_no = request.GET.get('container_no', '').upper()

    if len(container_no) != 11:
        return JsonResponse({'status': 'Failed', 'message': 'Panjang container number harus 11 digit'})

    try:
        if is_valid_container(container_no):
            return JsonResponse({'status': 'OK'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Check digit tidak valid'})
    except Exception as e:
        return JsonResponse({'status': 'Error', 'message': str(e)}, status=500)

@require_POST
@csrf_exempt
def upload_rooftop_photo(request):
    referal = request.POST.get('referal')
    container_no = request.POST.get('container_no')
    photo = request.FILES.get('photo')

    if not (referal and container_no and photo):
        return JsonResponse({'status': 'error', 'message': 'Data tidak lengkap'}, status=400)

    try:
        folder_name = f"container/{referal}_{container_no}/"
        save_path = os.path.join(settings.MEDIA_ROOT, folder_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        rooftop_filename = os.path.join(save_path, 'rooftop.jpg')

        with default_storage.open(rooftop_filename, 'wb+') as destination:
            for chunk in photo.chunks():
                destination.write(chunk)

        return JsonResponse({'status': 'success', 'message': 'Foto rooftop berhasil diupload'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@csrf_exempt
def save_container_ajax(request):
    if request.method == 'POST':
        try:
            container_no = request.POST.get('container_no')
            referal = generate_unique_referal()
            customer_code = request.POST.get('customer_code')
            container_type = request.POST.get('container_type')
            size = request.POST.get('size')
            condition = request.POST.get('condition')
            washing = request.POST.get('washing')
            grade = request.POST.get('grade')
            act_in = request.POST.get('act_in')
            manufacture = request.POST.get('manufacture')
            tare = request.POST.get('tare')
            payload = request.POST.get('payload')
            haulier = request.POST.get('haulier')
            truck = request.POST.get('truck')
            washing_by = request.POST.get('washing_by')
            remark = request.POST.get('remark')

            if not container_no or not customer_code:
                return JsonResponse({'status': 'error', 'message': 'No container dan customer wajib diisi.'})

            container = SurveyInContainer.objects.create(
                container_no=container_no,
                referal=referal,
                customer_code=customer_code,
                container_type=container_type,
                size=size,
                condition=condition,
                washing=washing,
                grade=grade,
                act_in=act_in,
                manufacture=manufacture,
                tare=tare,
                payload=payload,
                haulier=haulier,
                truck=truck,
                washing_by=washing_by,
                remark=remark,
            )

            # === Simpan Foto ===
            photos = request.FILES.getlist('photos')
            if photos:
                folder_name = f"container/{referal}_{container_no}/"
                save_path = os.path.join(settings.MEDIA_ROOT, folder_name)

                if not os.path.exists(save_path):
                    os.makedirs(save_path)

                for idx, photo in enumerate(photos, start=1):
                    ext = os.path.splitext(photo.name)[-1]  # contoh: .jpg, .png
                    filename = f"foto-{idx}{ext}"
                    file_path = os.path.join(save_path, filename)

                    with default_storage.open(file_path, 'wb+') as destination:
                        for chunk in photo.chunks():
                            destination.write(chunk)

            return JsonResponse({'status': 'success', 'container_no': container.container_no})

        except Exception as e:
            print("Error saving container:", e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def upload_rooftop_photo(request):
    if request.method == 'POST':
        try:
            container_no = request.POST.get('container_no_hidden')

            if not container_no:
                return JsonResponse({'status': 'error', 'message': 'No container tidak ditemukan.'})

            # Ambil data container berdasarkan container_no
            container = SurveyInContainer.objects.filter(container_no=container_no).first()
            if not container:
                return JsonResponse({'status': 'error', 'message': 'Container tidak ditemukan di database.'})

            referal = container.referal
            folder_name = f"container/{referal}_{container_no}/"
            save_path = os.path.join(settings.MEDIA_ROOT, folder_name)

            # Buat folder jika belum ada
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # Simpan foto (hanya ambil satu, untuk rooftop)
            photo = request.FILES.get('photos')
            if not photo:
                return JsonResponse({'status': 'error', 'message': 'Tidak ada file yang diupload.'})

            # Simpan dengan nama rooftop.jpg
            file_path = os.path.join(save_path, 'rooftop.jpg')
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in photo.chunks():
                    destination.write(chunk)

            return JsonResponse({'status': 'success'})

        except Exception as e:
            print("Error saat upload rooftop:", e)
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Metode request tidak diizinkan'})

@csrf_exempt
def upload_under_photo(request):
    if request.method == 'POST':
        try:
            container_no = request.POST.get('container_no_hidden')

            if not container_no:
                return JsonResponse({'status': 'error', 'message': 'No container tidak ditemukan.'})

            # Ambil data container berdasarkan container_no
            container = SurveyInContainer.objects.filter(container_no=container_no).first()
            if not container:
                return JsonResponse({'status': 'error', 'message': 'Container tidak ditemukan di database.'})

            referal = container.referal
            folder_name = f"container/{referal}_{container_no}/"
            save_path = os.path.join(settings.MEDIA_ROOT, folder_name)

            # Buat folder jika belum ada
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # Simpan foto (hanya ambil satu, untuk under)
            photo = request.FILES.get('photos')
            if not photo:
                return JsonResponse({'status': 'error', 'message': 'Tidak ada file yang diupload.'})

            # Simpan dengan nama under.jpg
            file_path = os.path.join(save_path, 'under.jpg')
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in photo.chunks():
                    destination.write(chunk)

            return JsonResponse({'status': 'success'})

        except Exception as e:
            print("Error saat upload under:", e)
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Metode request tidak diizinkan'})


@require_POST
@csrf_exempt
def verify_container_exists(request):
    container_no = request.POST.get('container_no', '').upper()

    try:
        container = SurveyInContainer.objects.filter(container_no=container_no).first()

        if container:
            return JsonResponse({
                'status': 'success',
                'container_no': container.container_no,
            })
        else:
            return JsonResponse({'status': 'not_found', 'message': 'Container tidak ditemukan'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def container_photo_gallery(request, referal, container_no):
    folder_path = os.path.join(settings.MEDIA_ROOT, f'container/{referal}_{container_no}/')
    
    rooftop_photos = []
    under_photos = []
    base_photos = []

    if os.path.exists(folder_path):
        for filename in sorted(os.listdir(folder_path)):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                file_url = os.path.join(settings.MEDIA_URL, f'container/{referal}_{container_no}/', filename)

                # Kategorisasi
                lower_name = filename.lower()
                if 'rooftop' in lower_name:
                    rooftop_photos.append(file_url)
                elif 'under' in lower_name:
                    under_photos.append(file_url)
                else:
                    base_photos.append(file_url)

    return render(request, 'surveyor/container_photos.html', {
        'container_no': container_no,
        'referal': referal,
        'rooftop_photos': rooftop_photos,
        'under_photos': under_photos,
        'base_photos': base_photos,
    })

@require_POST
@csrf_exempt
def simpan_penempatan_container(request):
    container_no = request.POST.get('container_no')
    block = request.POST.get('block')
    spec = request.POST.get('spec')
    row = request.POST.get('row')
    tier = request.POST.get('tier')

    if not all([container_no, block, spec, row, tier]):
        return JsonResponse({'status': 'error', 'message': 'Semua data harus diisi'})

    try:
        # Pastikan container terdaftar di SurveyInContainer
        container = SurveyInContainer.objects.get(container_no=container_no)

        # Hapus container ini dari posisi lain (jika sudah pernah dipetakan)
        MappingContainer.objects.filter(container_no=container_no).update(container_no=None)

        # Ambil lokasi berdasarkan block, spec, row, tier
        lokasi = MappingContainer.objects.get(
            block=block,
            spec=spec,
            row=row,
            tier=tier
        )

        # Cek apakah lokasi sudah ditempati container lain
        if lokasi.container_no and lokasi.container_no != container_no:
            return JsonResponse({'status': 'error', 'message': f'Lokasi ini sudah diisi oleh container lain: {lokasi.container_no}'})

        # Simpan penempatan container ke lokasi tersebut
        lokasi.container_no = container_no
        lokasi.save()

        return JsonResponse({'status': 'success'})

    except SurveyInContainer.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Container tidak terdaftar'})

    except MappingContainer.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Lokasi tidak tersedia'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_GET
def get_container_photos(request):
    referal = request.GET.get('referal')
    container_no = request.GET.get('container_no')

    if not referal or not container_no:
        return JsonResponse({'status': 'error', 'message': 'Referal dan No Container dibutuhkan'}, status=400)

    folder_path = os.path.join(settings.MEDIA_ROOT, f'container/{referal}_{container_no}/')

    if not os.path.exists(folder_path):
        return JsonResponse({'status': 'error', 'message': 'Folder foto tidak ditemukan'}, status=404)

    photo_urls = []
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            photo_urls.append(
                os.path.join(settings.MEDIA_URL, f'container/{referal}_{container_no}/{file_name}')
            )

    return JsonResponse({'status': 'success', 'photos': photo_urls})

def download_container_photos_pdf(request, referal, container_no):
    folder_path = os.path.join(settings.MEDIA_ROOT, f'container/{referal}_{container_no}/')
    if not os.path.exists(folder_path):
        return HttpResponse("Folder foto tidak ditemukan", status=404)

    photo_files = sorted([
        f for f in os.listdir(folder_path)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])

    if not photo_files:
        return HttpResponse("Tidak ada foto untuk container ini", status=404)

    # === PDF setup ===
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="container_{container_no}_photos.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    page_width, page_height = A4

    # Margin & layout
    margin_x = 2 * cm
    margin_y = 2 * cm
    space_x = 1 * cm
    space_y = 1 * cm
    images_per_row = 3

    # Ukuran seperti card (lebih tinggi)
    card_width = (page_width - (2 * margin_x) - ((images_per_row - 1) * space_x)) / images_per_row
    card_height = card_width * 1.2  # meniru proporsi card yang lebih tinggi

    current_x = margin_x
    current_y = page_height - margin_y - 2 * cm  # mulai di bawah judul

    # Judul halaman
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(page_width / 2, page_height - 2 * cm, f"Foto Container: {container_no}")

    for idx, filename in enumerate(photo_files):
        file_path = os.path.join(folder_path, filename)

        try:
            img = ImageReader(file_path)
            p.drawImage(img, current_x, current_y - card_height, card_width, card_height, preserveAspectRatio=True, anchor='c')

            # Caption
            p.setFont("Helvetica", 10)
            caption = f"Foto {idx + 1}"
            caption_x = current_x + (card_width / 2)
            caption_y = current_y - card_height - 0.5 * cm
            p.drawCentredString(caption_x, caption_y, caption)

            # Geser X
            current_x += card_width + space_x

            # Baris baru?
            if (idx + 1) % images_per_row == 0:
                current_x = margin_x
                current_y -= card_height + space_y + 1 * cm  # extra space for caption

                # Halaman baru jika terlalu bawah
                if current_y - card_height < margin_y:
                    p.showPage()
                    current_y = page_height - margin_y - 2 * cm
                    current_x = margin_x
                    p.setFont("Helvetica-Bold", 14)
                    p.drawCentredString(page_width / 2, page_height - 2 * cm, f"Foto Container: {container_no}")

        except Exception as e:
            print(f"Error rendering image {filename}: {e}")

    p.save()
    return response
