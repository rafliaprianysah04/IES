from django.shortcuts import render,  get_object_or_404
from django.urls import reverse, NoReverseMatch
from .utils import get_user_from_token
from .models import *
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Max
from datetime import datetime
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

def resolve_url_path(url_str):
    try:
        return reverse(url_str)
    except NoReverseMatch:
        return '#'  # fallback jika nama route tidak ditemukan

def dashboard(request):
    # Ambil token dari query parameter
    token = request.GET.get('token', '')

    # Ambil user dari token
    user = get_user_from_token(request)

    if not user:
        return render(request, 'unauthorized.html', status=401)

    app_id = user.app_id
    role_id = user.role_id

    # Ambil menu yang sesuai
    menu_ids = ExternalAccessMenu.objects.filter(role_id=role_id).values_list('menu_id', flat=True)

    menus = ExternalMenu.objects.filter(
        app_id=app_id,
        is_active=True,
        id__in=menu_ids
    ).order_by('sort')

    data = []
    for menu in menus:
        # Resolve URL menu jika ada field 'url' di model ExternalMenu, jika tidak ada pakai '#'
        menu_url = getattr(menu, 'url', None)
        menu_url_resolved = resolve_url_path(menu_url) if menu_url else '#'

        submenus = ExternalSubMenu.objects.filter(menu_id=menu.id).order_by('sort')
        submenu_list = []
        for submenu in submenus:
            url_resolved = resolve_url_path(submenu.urls)
            submenu_list.append({
                'id': submenu.id,
                'name': submenu.nama_submenu,
                'icon': submenu.icon_submenu,
                'url': url_resolved,
            })

        data.append({
            'id': menu.id,
            'name': menu.nama_menu,
            'icon': menu.icon_menu,
            'url': menu_url_resolved,
            'submenus': submenu_list,
        })

    return render(request, 'dashboard.html', {
        'user': user,
        'menu_with_subs': data,
        'token': token,
    })


def coa(request):
    # Ambil token dari query parameter
    token = request.GET.get('token', '')

    # Ambil user dari token
    user = get_user_from_token(request)

    if not user:
        return render(request, 'unauthorized.html', status=401)

    app_id = user.app_id
    role_id = user.role_id

    # Ambil menu yang sesuai
    menu_ids = ExternalAccessMenu.objects.filter(role_id=role_id).values_list('menu_id', flat=True)

    menus = ExternalMenu.objects.filter(
        app_id=app_id,
        is_active=True,
        id__in=menu_ids
    ).order_by('sort')

    data = []
    for menu in menus:
        # Resolve URL menu jika ada field 'url' di model ExternalMenu, jika tidak ada pakai '#'
        menu_url = getattr(menu, 'url', None)
        menu_url_resolved = resolve_url_path(menu_url) if menu_url else '#'

        submenus = ExternalSubMenu.objects.filter(menu_id=menu.id).order_by('sort')
        submenu_list = []
        for submenu in submenus:
            url_resolved = resolve_url_path(submenu.urls)
            submenu_list.append({
                'id': submenu.id,
                'name': submenu.nama_submenu,
                'icon': submenu.icon_submenu,
                'url': url_resolved,
            })

        data.append({
            'id': menu.id,
            'name': menu.nama_menu,
            'icon': menu.icon_menu,
            'url': menu_url_resolved,
            'submenus': submenu_list,
        })

    return render(request, 'coa.html', {
        'user': user,
        'menu_with_subs': data,
        'token': token,
    })


def ledger(request):
    references = ReferenceJournal.objects.all().order_by('-inputdate')

    data = []
    for ref in references:
        journals = Journal.objects.filter(reference_id=ref.reference_id, reference=ref.reference)

        total_debit = journals.aggregate(total=Sum('debit'))['total'] or 0
        formatted_total = "{:,.2f}".format(total_debit).replace(",", "_").replace(".", ",").replace("_", ".")
        status = ref.status if ref.status is not None else (journals.first().status if journals.exists() else None)

        data.append({
            'ref': ref,
            'total': formatted_total,  # hanya debit
            'status': status
        })

    return render(request, 'ledger.html', {'data': data})
def supporting_data(request):
    return render(request, 'master/supporting_data.html')



#ACCOUNT
def account_list(request):
    data = Account.objects.all()
    return render(request, 'master/account_list.html', {'data': data})

@csrf_exempt
def add_account(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # cari nilai account_id terakhir dan tambah 1
            last_id = Account.objects.aggregate(last_id=Max('account_id'))['last_id'] or 0
            new_id = last_id + 1

            Account.objects.create(
                account_id=new_id,
                account_code=data['account_code'],
                account_name=data['account_name'],
                is_active=int(data['is_active']),
                created_by='system'
            )
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})

@csrf_exempt
def update_account(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            acc = Account.objects.get(account_id=id)
            acc.account_code = data.get('account_code')
            acc.account_name = data.get('account_name')
            acc.is_active = int(data.get('is_active', 1))
            acc.save()
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})
    return JsonResponse({'status': False, 'error': 'Invalid request method'})

def delete_account(request, id):
    acc = get_object_or_404(Account, pk=id)
    acc.delete()
    return JsonResponse({'status': True})

def account_json(request, id):
    data = Account.objects.filter(pk=id).values().first()
    return JsonResponse(data, safe=False)


#ACCOUNT 1

def account1_list(request):
    data = Account1.objects.all()
    return render(request, 'master/account1_list.html', {'data': data})

@csrf_exempt
def add_account1(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # cari nilai account_id terakhir dan tambah 1
            last_id = Account1.objects.aggregate(last_id=Max('account1_id'))['last_id'] or 0
            new_id = last_id + 1

            Account1.objects.create(
                account1_id=new_id,
                accountcode=data['accountcode'],
                account1_code=data['account1_code'],
                account1_name=data['account1_name'],
                is_active=int(data['is_active']),
                created_by='system'
            )
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})

@csrf_exempt
def update_account1(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            acc = Account1.objects.get(account1_id=id)
            acc.accountcode = data.get('accountcode')
            acc.account1_code = data.get('account1_code')
            acc.account1_name = data.get('account1_name')
            acc.is_active = int(data.get('is_active', 1))
            acc.save()
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})
    return JsonResponse({'status': False, 'error': 'Invalid request method'})

@csrf_exempt
def delete_account1(request, id):
    if request.method == 'POST':
        try:
            acc = Account1.objects.get(pk=id)
            acc.delete()
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})

def account1_json(request, id):
    data = Account1.objects.filter(pk=id).values().first()
    return JsonResponse(data, safe=False)



# ACCOUNT 2
def account2_list(request):
    data = Account2.objects.all()
    return render(request, 'master/account2_list.html', {'data': data})

@csrf_exempt
def add_account2(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # cari nilai account_id terakhir dan tambah 1
            last_id = Account2.objects.aggregate(last_id=Max('account2_id'))['last_id'] or 0
            new_id = last_id + 1

            Account2.objects.create(
                account2_id=new_id,
                account1code=data['account1code'],
                account2_code=data['account2_code'],
                account2_name=data['account2_name'],
                is_active=int(data['is_active']),
                created_by='system'
            )
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})

@csrf_exempt
def update_account2(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            acc = Account2.objects.get(account2_id=id)
            acc.account1code = data.get('account1code')
            acc.account2_code = data.get('account2_code')
            acc.account2_name = data.get('account2_name')
            acc.is_active = int(data.get('is_active', 1))
            acc.save()
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})
    return JsonResponse({'status': False, 'error': 'Invalid request method'})


@csrf_exempt
def delete_account2(request, id):
    if request.method == 'POST':
        try:
            acc = Account2.objects.get(pk=id)
            acc.delete()
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})
    return JsonResponse({'status': False, 'error': 'Invalid request'})

def account2_json(request, id):
    data = Account2.objects.filter(pk=id).values().first()
    return JsonResponse(data, safe=False)




# ACCOUNT SUB 1
def accountsub1_list(request):
    data = Accountsub1.objects.all()
    return render(request, 'master/accountsub1_list.html', {'data': data})

@csrf_exempt
def add_accountsub1(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # cari nilai account_id terakhir dan tambah 1
            last_id = Accountsub1.objects.aggregate(last_id=Max('accountsub1_id'))['last_id'] or 0
            new_id = last_id + 1

            Account2.objects.create(
                accountsub1_id=new_id,
                account2code=data['account2code'],
                accountsub1_code=data['accountsub1_code'],
                accountsub1_name=data['accountsub1_name'],
                is_active=int(data['is_active']),
                created_by='system'
            )
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})

@csrf_exempt
def update_accountsub1(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            acc = Accountsub1.objects.get(accountsub1_id=id)
            acc.account2code = data.get('account2code')
            acc.accountsub1_code = data.get('accountsub1_code')
            acc.accountsub1_name = data.get('accountsub1_name')
            acc.is_active = int(data.get('is_active', 1))
            acc.save()
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})
    return JsonResponse({'status': False, 'error': 'Invalid request method'})


@csrf_exempt
def delete_accountsub1(request, id):
    if request.method == 'POST':
        try:
            acc = Accountsub1.objects.get(pk=id)
            acc.delete()
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})
    return JsonResponse({'status': False, 'error': 'Invalid request'})

def accountsub1_json(request, id):
    data = Accountsub1.objects.filter(pk=id).values().first()
    return JsonResponse(data, safe=False)



# ACCOUNT SUB 1
def accountsub2_list(request):
    data = Accountsub2.objects.all()
    return render(request, 'master/accountsub2_list.html', {'data': data})

@csrf_exempt
def add_accountsub2(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # cari nilai account_id terakhir dan tambah 1
            last_id = Accountsub2.objects.aggregate(last_id=Max('accountsub2_id'))['last_id'] or 0
            new_id = last_id + 1

            Account2.objects.create(
                accountsub2_id=new_id,
                accountsub1code=data['accountsub1code'],
                accountsub2_code=data['accountsub2_code'],
                accountsub2_name=data['accountsub2_name'],
                is_active=int(data['is_active']),
                created_by='system'
            )
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})

@csrf_exempt
def update_accountsub2(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            acc = Accountsub2.objects.get(accountsub2_id=id)
            acc.accountsub1code = data.get('accountsub1code')
            acc.accountsub2_code = data.get('accountsub2_code')
            acc.accountsub2_name = data.get('accountsub2_name')
            acc.is_active = int(data.get('is_active', 1))
            acc.save()
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})
    return JsonResponse({'status': False, 'error': 'Invalid request method'})


@csrf_exempt
def delete_accountsub2(request, id):
    if request.method == 'POST':
        try:
            acc = Accountsub1.objects.get(pk=id)
            acc.delete()
            return JsonResponse({'status': True})
        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})
    return JsonResponse({'status': False, 'error': 'Invalid request'})

def accountsub2_json(request, id):
    data = Accountsub2.objects.filter(pk=id).values().first()
    return JsonResponse(data, safe=False)



#SUPPORTING DATA BRANCH
def branch_list(request):
    branches = Branch.objects.all()
    context = {
        'title': 'Branch List',
        'branch_list': branches,
    }
    return render(request, 'master/supportingdata_branch.html', context)

def employee_list(request):
    employees = EmployeeInformation.objects.select_related('employeeid').all()
    context = {
        'title': 'Employee List',
        'employees': employees
    }
    return render(request, 'master/supportingdata_employee.html', context)



def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'master/supportingdata_contact.html', {
        'contact_list': contacts,
        'title': 'Contact List',
    })

def uom_list(request):
    uoms = Uom.objects.all()
    context = {
        'title': 'UOM List',
        'uoms': uoms
    }
    return render(request, 'master/supportingdata_uom.html', context)

def warehouse_list(request):
    warehouse_list = Warehouse.objects.all().order_by('wh_id')
    context = {
        'title': 'Warehouse List',
        'warehouse_list': warehouse_list
    }
    return render(request, 'master/supportingdata_warehouse.html', context)

def tax_list(request):
    tax_list = Tax.objects.all().order_by('tax_id')
    context = {
        'title': 'Tax List',
        'tax_list': tax_list
    }
    return render(request, 'master/supportingdata_tax.html', context)