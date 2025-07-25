from django.shortcuts import render,  redirect, get_object_or_404
from django.utils import timezone
from surveyor.models import *
from django.contrib import messages
from django.urls import reverse
from .utils import get_user_from_token

# Create your views here.
def dashboard_operator(request):
    return render(request, 'dashboard_operator.html')



def denah_storage(request):
    # Blok: A1-A8, B1-B8, C1-C8
    block_letters = ["A", "B", "C"]
    blocks = [f"{letter}{i}" for letter in block_letters for i in range(1, 9)]
    current_block = request.GET.get("block", "A1")

    # STACKING INPUT
    if request.method == "POST":
        cont_number = request.POST.get("container_number")
        location = request.POST.get("location")

        try:
            container = SurveyInsNew.objects.get(cont=cont_number)
            container.stacking_location = location
            container.stacking_status = "Stacked"
            container.stacking_at = timezone.now()
            container.stacking_by = request.user.username if request.user else "Anonymous"
            container.save()
        except SurveyInsNew.DoesNotExist:
            pass

        return redirect(f"{request.path}?block={current_block}")

    # Buat denah kosong
    storage_map = {}
    for bay in range(1, 3):  # 2 bay
        for row in range(1, 21):  # 20 row
            for tier in range(1, 9):  # 8 tier
                key = f"{current_block}_By{bay}_Rw{row}_Tr{tier}"
                storage_map[key] = {
                    "cont": "",
                    "stack_at": None,
                }

    # Isi kontainer yang sudah distack
    stacked_containers = SurveyInsNew.objects.filter(stacking_status="Stacked", stacking_location__startswith=current_block)
    for cont in stacked_containers:
        key = cont.stacking_location
        if key.startswith(current_block):
            storage_map[key] = {
                "cont": cont.cont,
                "stack_at": cont.stacking_at,
            }

    context = {
        "current_block": current_block,
        "blocks": blocks,
        "storage_map": storage_map,
        "bay_range": range(1, 3),
        "row_range": range(1, 21),
        "tier_range": range(1, 9),
    }
    return render(request, "denah_storage.html", context)


def stacking_view(request):
    all_locations = SurveyInsNew.objects.exclude(stacking_location__isnull=True).values_list('stacking_location', flat=True)
    blocks = sorted(list(set([loc[:3] for loc in all_locations if loc.startswith('Bl')]))) or ['Bl1']
    current_block = request.GET.get('block', 'Bl1')

    # Buat storage_map 
    storage_map = {}   
    for obj in SurveyInsNew.objects.exclude(stacking_location__isnull=True):
        loc = obj.stacking_location
        if loc:
            try:
                block = loc[2]
                bay = loc.split('By')[1].split('Rw')[0]
                row = loc.split('Rw')[1].split('Tr')[0]
                tier = loc.split('Tr')[1]
                key = f"Bl{block}By{bay}Rw{row}Tr{tier}"
                storage_map[key] = {
                'cont': obj.cont,
                'stack_at': obj.stacking_at,
            }
            except:
                continue

    if request.method == 'POST':
        cont = request.POST.get('container_number')
        location = request.POST.get('location')  # format: Bl1By1Rw2Tr3

        if not cont or not location:
            messages.error(request, 'Container number dan lokasi wajib diisi.')
            return redirect(f"{reverse('operator_stack:stacking_in')}?block={current_block}")

        bay = location.split('By')[1].split('Rw')[0]
        row = location.split('Rw')[1].split('Tr')[0]
        tier = location.split('Tr')[1]
        key = f"Bl{block}By{bay}Rw{row}Tr{tier}"

        if key in storage_map:
            messages.error(request, f"Lokasi {location} sudah terisi.")
        else:
            try:
                container = SurveyInsNew.objects.get(cont=cont)
                container.stacking_location = location
                container.stacking_status = 'stacked'
                container.stacking_at = timezone.now()
                container.save()
                messages.success(request, f"Container {cont} berhasil distack di {location}.")
                return redirect(f"{reverse('operator_stack:stacking_in')}?block={current_block}")
            except SurveyInsNew.DoesNotExist:
                messages.error(request, 'Container tidak ditemukan.')

    return render(request, 'denah_storage.html', {
        'blocks': blocks,
        'current_block': current_block,
        'storage_map': storage_map,
    })



def shifting(request):
    if request.method == 'POST':
        cont_number = request.POST.get('container_number')
        block = request.POST.get('block')
        bay = request.POST.get('bay')
        row = request.POST.get('row')
        tier = request.POST.get('tier')
        operator = request.user.username  # atau input manual dari POST

        location = f"{block}-B{bay}-R{row}-T{tier}"

        container = get_object_or_404(SurveyInsNew, cont=cont_number)

        # Shift history
        container.shift_loc_hist03 = container.shift_loc_hist02
        container.shift_loc_hist02 = container.shift_loc_hist01
        container.shift_loc_hist01 = container.shift_loc_curr

        # Current shift
        container.shift_loc_curr = location
        container.shift_loc_by = operator
        container.shift_loc_at = timezone.now()

        container.save()

        return redirect('operator_stack:shifting')

    return render(request, 'shifting.html')


def storage_map(request):
    bay_list = [1, 2, 3]
    row_list = [1, 2, 3]
    tier_list = [3, 2, 1]  # Dari atas ke bawah

    # Contoh data posisi kontainer
    positions = {
        1: {
            1: {1: {'cont': 'CMAU1234567'}, 2: None, 3: None},
            2: {1: {'cont': 'MSCU7654321'}},
            3: {},
        },
        2: {
            1: {},
            2: {},
            3: {},
        },
        3: {
            1: {2: {'cont': 'TLLU9988776'}},
        }
    }

    return render(request, 'dashboard_operator.html', {
        'bay_list': bay_list,
        'row_list': row_list,
        'tier_list': tier_list,
        'positions': positions,
    })