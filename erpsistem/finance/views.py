from django.shortcuts import render,  get_object_or_404, redirect
from django.urls import reverse, NoReverseMatch
from .utils import get_user_from_token
from .models import *
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from django.shortcuts import redirect
from django.http import HttpResponse,JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib import messages
from openpyxl import Workbook
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Max
from datetime import date, datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F,ExpressionWrapper, DecimalField , Value as V
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from decimal import Decimal
from django.db.models.functions import Cast
from django.db.models import DecimalField
from django.utils.dateparse import parse_date
from django.utils import timezone

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

    return render(request, 'dashboard.html', {'user': user, 'token': request.GET.get('token', '')})

def coa(request):
    token = request.GET.get('token', '')
    return render(request, 'master/coa.html', {'token': token})

#LEDGER
def ledger(request):    
    user = get_user_from_token(request)
    if not user:
        return render(request, 'unauthorized.html', status=401)

    references = ReferenceJournal.objects.all().order_by('-inputdate')
    data = []

    for ref in references:
        journals = Journal.objects.filter(reference_id=ref.reference_id, reference=ref.reference)
        total_debit = journals.aggregate(total=Sum('debit'))['total'] or 0
        formatted_total = "{:,.2f}".format(total_debit).replace(",", "_").replace(".", ",").replace("_", ".")
        status = ref.status if ref.status is not None else (journals.first().status if journals.exists() else None)

        data.append({
            'ref': ref,
            'total': formatted_total,
            'status': status
        })

    context = {
        'title': 'General Journal',
        'data': data,
        'token': request.GET.get('token', ''),
        'role_id': user.role_id,
    }

    return render(request, 'ledger/ledger.html', context)


def journal_add(request):
    user = get_user_from_token(request)
    if not user:
        return redirect('/unauthorized')

    if request.method == 'POST':
        description = request.POST.get('description')
        inputdate = request.POST.get('inputdate')
        code = request.POST.get('code')

        ref = ReferenceJournal.objects.create(
            inputdate=inputdate,
            reference='AUTO_GENERATE',
            description=description,
            code=code,
            created_by=user.id,
            date_created=timezone.now(),
            status=0
        )

        accounts = request.POST.getlist('accountsub2_code[]')
        branches = request.POST.getlist('branch_id[]')
        contacts = request.POST.getlist('contact_code[]')
        debits = request.POST.getlist('debit[]')
        credits = request.POST.getlist('credit[]')

        for i in range(len(accounts)):
            Journal.objects.create(
                reference_id=ref.reference_id,
                reference=ref.reference,
                inputdate=inputdate,
                coa_code=accounts[i],
                branch_id=branches[i] or None,
                contact_code=contacts[i] or None,
                debit=float(debits[i].replace(',', '') or 0),
                credit=float(credits[i].replace(',', '') or 0),
                description=description,
                created_by=user.id,
                date_created=timezone.now(),
            )

        messages.success(request, 'Journal added successfully.')
        return redirect(f'/finance/ledger?token={request.GET.get("token", "")}')

    context = {
        'accountsub2': Accountsub2.objects.all(),
        'branch': Branch.objects.all(),
        'contact': Contact.objects.all(),
        'token': request.GET.get('token', ''),
    }
    return render(request, 'ledger/journal_add.html', context)

def ledger_edit(request, reference_id):
    user = get_user_from_token(request)

    ref = get_object_or_404(ReferenceJournal, reference_id=reference_id)
    journals = Journal.objects.filter(reference_id=reference_id)

    if request.method == 'POST':
        ref.description = request.POST.get('description')
        ref.save()

        for journal in journals:
            journal.description = request.POST.get('description')
            journal.save()

        messages.success(request, 'Journal updated successfully.')
        return redirect(f"{reverse('finance:ledger')}?token={request.GET.get('token', '')}")
    
    context = {
        'ref': ref,
        'reference': ref,
        'journals': journals,
        'token': request.GET.get('token', ''),
        'accountsub2': Accountsub2.objects.all(),
        'branch': Branch.objects.all(),
        'contact': Contact.objects.all()
    }
    return render(request, 'ledger/ledger_edit.html', context)


@require_POST
def ledger_approve(request, reference_id):
    user = get_user_from_token(request)
    if not user or user.role_id not in [1, 2]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    ref = get_object_or_404(ReferenceJournal, reference_id=reference_id)
    ref.status = 1
    ref.save()
    Journal.objects.filter(reference_id=reference_id).update(status=1)

    return JsonResponse({'success': True})


def voucher_view(request, reference_id):
    user = get_user_from_token(request)
    if not user:
        return HttpResponseForbidden("Unauthorized")

    ref = get_object_or_404(ReferenceJournal, reference_id=reference_id)
    journals = Journal.objects.filter(reference_id=reference_id)
    total_debit = journals.aggregate(total=Sum('debit'))['total'] or 0
    total_credit = journals.aggregate(total=Sum('credit'))['total'] or 0

    context = {
        'ref': ref,
        'reference': ref,
        'journals': journals,
        'accountsub2': Accountsub2.objects.all(),
        'branch': Branch.objects.all(),
        'total_debit': total_debit,
        'total_credit': total_credit,
        'token': request.GET.get('token', '')
    
    }
    return render(request, 'ledger/voucher_view.html', context)


def voucher_pdf(request, reference_id):
    user = get_user_from_token(request)
    if not user:
        return HttpResponse("Unauthorized", status=403)

    reference = get_object_or_404(ReferenceJournal, reference_id=reference_id)
    journals = Journal.objects.filter(reference_id=reference_id)

    total_debit = journals.aggregate(total=Sum('debit'))['total'] or 0
    total_credit = journals.aggregate(total=Sum('credit'))['total'] or 0

    context = {
        'reference': reference,
        'journals': journals,
        'accountsub2': Accountsub2.objects.all(),
        'branch': Branch.objects.all(),
        'contact': Contact.objects.all(),
        'total_debit': total_debit,
        'total_credit': total_credit,
        'user': user,
    }

    template = get_template('ledger/voucher_pdf.html')
    html = template.render(context)

    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=result, encoding='UTF-8')

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("PDF generation failed", status=500)



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



BRANCH_NAMES = {
    'ITI011': 'Head Office',
    'ITI021': 'Jakarta',
    'ITI031': 'Surabaya',
    'ITI041': 'Belawan',
    'ITI051': 'Lampung',
}

def beginning_balance(request):
    accountsub2 = Accountsub2.objects.filter(is_active=1)[:10]
    all_coa = Accountsub2.objects.filter(is_active=1)
    bbalance = Bbalance.objects.order_by('-inputdate')
    token = request.GET.get('token', '')

    account_map = {a.accountsub2_code: a.accountsub2_name for a in all_coa}
    # Tambahkan branch_name ke setiap item di bbalance
    for b in bbalance:
        b.branch_name = BRANCH_NAMES.get(b.branch_id, b.branch_id)
        b.accountsub2_name = account_map.get(b.accountsub2code, '')

    context = {
        'title': 'Beginning Balance',
        'accountsub2': all_coa[:5],
        'all_coa': all_coa,
        'branch_list': [{'id': k, 'name': v} for k, v in BRANCH_NAMES.items()],
        'bbalance': bbalance,
        'branch': Branch.objects.all(),
        'token': token,
    }
    return render(request, 'master/supportingdata_bbalance.html', context)

@csrf_exempt
def add_bbalance(request):
    if request.method == 'POST':
        data = request.POST
        account_codes = data.getlist('accountsub2code[]')
        branch_ids = data.getlist('branch_id[]')
        debits = data.getlist('debit[]')
        credits = data.getlist('credit[]')

        errors = {}
        for idx, code in enumerate(account_codes):
            if not branch_ids[idx]:
                errors[f'branch_id[{idx}]'] = 'Branch is required'

            # Validasi nilai debit dan credit harus angka
            try:
                float(debits[idx] or 0)
                float(credits[idx] or 0)
            except ValueError:
                errors[f'debit_credit[{idx}]'] = 'Invalid number format'

        if errors:
            return JsonResponse({'status': False, 'errors': errors})

        last_id = Bbalance.objects.aggregate(max_id=Max('bbalance_id'))['max_id'] or 0
        for i in range(len(account_codes)):
            debit = float(debits[i]) if debits[i] else 0
            credit = float(credits[i]) if credits[i] else 0

            if debit != 0 or credit != 0:
                last_id += 1
                Bbalance.objects.create(
                    bbalance_id=last_id,  # <-- manual increment ID
                    accountsub2code=account_codes[i],
                    branch_id=branch_ids[i],
                    inputdate=date.today(),
                    debit=debit,
                    credit=credit,
                    created_by='admin',
                    date_created=date.today(),
                )


        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'message': 'Invalid request'})
    
def get_bbalanced(request):
    queryset = Bbalance.objects.select_related(None).order_by('-inputdate')
    data = [{
        'accountsub2code': b.accountsub2code,
        'accountsub2_name': Accountsub2.objects.filter(accountsub2_code=b.accountsub2code).first().accountsub2_name,
        'branch_id': BRANCH_NAMES.get(b.branch_id, b.branch_id),
        'inputdate': b.inputdate.strftime('%Y-%m-%d'),
        'debit': float(b.debit or 0),
        'credit': float(b.credit or 0),
    } for b in queryset]
    return JsonResponse(data, safe=False)




#CASHBANK

def expense(request):
    token = request.GET.get('token', '')

    # Ambil semua reference yang code-nya 'EX' atau memiliki jurnal dengan code 'EX'
    references = ReferenceJournal.objects.filter(
        Q(code='EX') |
        Q(reference_id__in=Journal.objects.filter(code='EX').values_list('reference_id', flat=True))
    ).order_by('-inputdate').distinct()

    data = []
    for ref in references:
        journals = Journal.objects.filter(reference_id=ref.reference_id, reference=ref.reference)

        total_debit = journals.aggregate(total=Sum('debit'))['total'] or 0
        formatted_total = "{:,.2f}".format(total_debit).replace(",", "_").replace(".", ",").replace("_", ".")
        status = ref.status if ref.status is not None else (journals.first().status if journals.exists() else None)

        data.append({
            'ref': ref,
            'total': formatted_total,
            'status': status
        })

    return render(request, 'cashbank/expense.html', {'token': token, 'data': data})


def fundtransfer(request):
    token = request.GET.get('token', '')

    # Ambil semua reference yang code-nya 'EX' atau memiliki jurnal dengan code 'EX'
    references = ReferenceJournal.objects.filter(
        Q(code='FT') |
        Q(reference_id__in=Journal.objects.filter(code='FT').values_list('reference_id', flat=True))
    ).order_by('-inputdate').distinct()

    data = []
    for ref in references:
        journals = Journal.objects.filter(reference_id=ref.reference_id, reference=ref.reference)

        total_debit = journals.aggregate(total=Sum('debit'))['total'] or 0
        formatted_total = "{:,.2f}".format(total_debit).replace(",", "_").replace(".", ",").replace("_", ".")
        status = ref.status if ref.status is not None else (journals.first().status if journals.exists() else None)

        data.append({
            'ref': ref,
            'total': formatted_total,
            'status': status
        })

    return render(request, 'cashbank/fundtransfer.html', {'token': token, 'data': data})


#Salas Invoice
def sales_invoice(request):
    token = request.GET.get('token', '')

    # Ambil semua reference yang code-nya 'EX' atau memiliki jurnal dengan code 'EX'
    references = ReferenceJournal.objects.filter(
        Q(code='SI') |
        Q(reference_id__in=Journal.objects.filter(code='SI').values_list('reference_id', flat=True))
    ).order_by('-inputdate').distinct()

    data = []
    for ref in references:
        journals = Journal.objects.filter(reference_id=ref.reference_id, reference=ref.reference)

        total_debit = journals.aggregate(total=Sum('debit'))['total'] or 0
        formatted_total = "{:,.2f}".format(total_debit).replace(",", "_").replace(".", ",").replace("_", ".")
        status = ref.status if ref.status is not None else (journals.first().status if journals.exists() else None)

        data.append({
            'ref': ref,
            'total': formatted_total,
            'status': status
        })

    return render(request, 'sales/sales_invoice.html', {'token': token, 'data': data})


@csrf_exempt
def sales_remaining(request):
    token = request.GET.get('token', '')

    # Mapping cabang
    cabang_mapping = {
        'ITI011' :'Head Office',
        'ITI041': 'Belawan',
        'ITI021': 'Jakarta',
        'ITI051': 'Lampung',
        'ITI031': 'Surabaya',
    }

    # Filter hanya reference yang belum complete
    references = ReferenceJournal.objects.filter(completed=0)

    data = []

    for ref in references:
        # Ambil journal yang terkait reference
        journals = Journal.objects.filter(reference=ref.reference, completed=0)

        # Hitung total debit per reference
        total_debit = journals.aggregate(
            total=Sum(ExpressionWrapper(F('debit'), output_field=DecimalField()))
        )['total'] or Decimal('0.00')

        for j in journals:
            data.append({
                'inputdate': j.inputdate.strftime('%Y-%m-%d') if j.inputdate else '',
                'reference': j.reference,
                'debit': float(j.debit or 0),
                'contact_alias': j.contact_code or '',
                'branch_id': j.branch_id or '',
                'name': j.created_by or '',
            })

    # Total debit per cabang
    debit_per_branch = {}
    for code, nama in cabang_mapping.items():
        total = Journal.objects.filter(branch_id=code, completed=0).aggregate(
            total=Sum(ExpressionWrapper(F('debit'), output_field=DecimalField()))
        )['total'] or Decimal('0.00')
        debit_per_branch[nama] = float(total)

    # Total debit per customer
    customer_summary = (
        Journal.objects.filter(completed=0)
        .values('contact_code')
        .annotate(total=Sum(ExpressionWrapper(F('debit'), output_field=DecimalField())))
        .order_by('contact_code')
    )

    customer_data = []
    for c in customer_summary:
        customer_data.append({
            'contact_alias': c['contact_code'],
            'total': float(c['total'] or 0),
        })

    total_debit = sum(item['debit'] for item in data)
    context = {
        'title': 'Sales Remaining',
        'total_debit':total_debit,
        'token': token,
        'customerAll': data,
        'customer': customer_data,
        'debit_branch': debit_per_branch,
    }

    return render(request, 'sales/sales_remaining.html', context)





# Purchase Invoice
def purchase_invoice(request):
    token = request.GET.get('token', '')

    # Ambil semua reference yang code-nya 'EX' atau memiliki jurnal dengan code 'EX'
    references = ReferenceJournal.objects.filter(
        Q(code='PI') |
        Q(reference_id__in=Journal.objects.filter(code='PI').values_list('reference_id', flat=True))
    ).order_by('-inputdate').distinct()

    data = []
    for ref in references:
        journals = Journal.objects.filter(reference_id=ref.reference_id, reference=ref.reference)

        total_debit = journals.aggregate(total=Sum('debit'))['total'] or 0
        formatted_total = "{:,.2f}".format(total_debit).replace(",", "_").replace(".", ",").replace("_", ".")
        status = ref.status if ref.status is not None else (journals.first().status if journals.exists() else None)

        data.append({
            'ref': ref,
            'total': formatted_total,
            'status': status
        })

    return render(request, 'purchase/purchase_invoice.html', {'token': token, 'data': data})


# REPORT
def ledger_search_branch(request):
    token = request.GET.get("token", "")
    context = {
        'title': 'Ledger Search Branch',
        'token': token,
        'branch': Branch.objects.all(),
        'accountsub2': Accountsub2.objects.all(),
    }

    if request.method == 'POST':
        date_start = request.POST.get('date_start')
        date_finish = request.POST.get('date_finish')
        branch_id = request.POST.get('branch_id')
        accountsub2_code = request.POST.get('accountsub2_code')

        journals = Journal.objects.all()
        if date_start and date_finish:
            journals = journals.filter(inputdate__range=[date_start, date_finish])
        if branch_id:
            journals = journals.filter(branch_id=branch_id)
        if accountsub2_code and accountsub2_code != 'all':
            journals = journals.filter(coa_code=accountsub2_code)

        journals = journals.annotate(
            debit_as_decimal=Cast('debit', output_field=DecimalField(max_digits=20, decimal_places=2)),
            credit_as_decimal=Cast('credit', output_field=DecimalField(max_digits=20, decimal_places=2))
        ).order_by('inputdate')

        total_debit = journals.aggregate(total=Sum('debit_as_decimal'))['total'] or 0
        total_credit = journals.aggregate(total=Sum('credit_as_decimal'))['total'] or 0

        getbalance = Journal.objects.filter(inputdate__lt=date_start)
        if branch_id:
            getbalance = getbalance.filter(branch_id=branch_id)
        if accountsub2_code and accountsub2_code != 'all':
            getbalance = getbalance.filter(coa_code=accountsub2_code)

        bbcd = getbalance.aggregate(total=Sum(F('credit') - F('debit')))['total'] or 0
        bbdc = getbalance.aggregate(total=Sum(F('debit') - F('credit')))['total'] or 0

        account_type = accountsub2_code[:1] if accountsub2_code and accountsub2_code != 'all' else '1'
        if account_type in ['2', '3', '4', '8']:
            beginning_balance = bbcd
            for j in journals:
                j.balance = beginning_balance + j.credit - j.debit
                beginning_balance = j.balance
        else:
            beginning_balance = bbdc
            for j in journals:
                j.balance = beginning_balance - j.credit + j.debit
                beginning_balance = j.balance

        account_name = ''
        if accountsub2_code and accountsub2_code != 'all':
            acc = Accountsub2.objects.filter(accountsub2_code=accountsub2_code).first()
            account_name = acc.accountsub2_name if acc else ''
        branch_name = ''
        if branch_id:
            br = Branch.objects.filter(branch_id=branch_id).first()
            branch_name = br.name_branch if br else ''

        context.update({
            'journals': journals,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'selected_start': date_start,
            'selected_finish': date_finish,
            'selected_branch': branch_id,
            'selected_account': accountsub2_code,
            'selected_account_name': account_name,
            'selected_branch_name': branch_name,
            'beginning_balance': beginning_balance,
        })

    return render(request, 'report/ledger_search_branch.html', context)


def ledger_result(request):
    token = request.GET.get("token", "")
    user = getattr(request, "user", None)
    if not user:
        return render(request, 'unauthorized.html', status=401)
    
    date_start = request.GET.get('date_start')
    date_finish = request.GET.get('date_finish')
    branch_id = request.GET.get('branch_id')
    accountsub2_code = request.GET.get('accountsub2_code')
    token = request.GET.get('token', '')

    journals = Journal.objects.all()
    if date_start and date_finish:
        journals = journals.filter(inputdate__range=[date_start, date_finish])
    if branch_id:
        journals = journals.filter(branch_id=branch_id)
    if accountsub2_code and accountsub2_code != 'all':
        journals = journals.filter(coa_code=accountsub2_code)

    journals = journals.annotate(
        debit_as_decimal=Cast('debit', output_field=DecimalField(max_digits=20, decimal_places=2)),
        credit_as_decimal=Cast('credit', output_field=DecimalField(max_digits=20, decimal_places=2))
    ).order_by('inputdate')

    total_debit = journals.aggregate(total=Sum('debit_as_decimal'))['total'] or 0
    total_credit = journals.aggregate(total=Sum('credit_as_decimal'))['total'] or 0

    getbalance = Journal.objects.filter(inputdate__lt=date_start)
    if branch_id:
        getbalance = getbalance.filter(branch_id=branch_id)
    if accountsub2_code and accountsub2_code != 'all':
        getbalance = getbalance.filter(coa_code=accountsub2_code)

    bbcd = getbalance.aggregate(total=Sum(F('credit') - F('debit')))['total'] or 0
    bbdc = getbalance.aggregate(total=Sum(F('debit') - F('credit')))['total'] or 0

    account_type = accountsub2_code[:1] if accountsub2_code and accountsub2_code != 'all' else '1'
    if account_type in ['2', '3', '4', '8']:
        beginning_balance = bbcd
        for j in journals:
            j.balance = beginning_balance + j.credit - j.debit
            beginning_balance = j.balance
    else:
        beginning_balance = bbdc
        for j in journals:
            j.balance = beginning_balance - j.credit + j.debit
            beginning_balance = j.balance

    account_name = ''
    if accountsub2_code and accountsub2_code != 'all':
        acc = Accountsub2.objects.filter(accountsub2_code=accountsub2_code).first()
        account_name = acc.accountsub2_name if acc else ''
    branch_name = ''
    if branch_id:
        br = Branch.objects.filter(branch_id=branch_id).first()
        branch_name = br.name_branch if br else ''

    context = {
        'title': 'Ledger Result',
        'journals': journals,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'selected_start': date_start,
        'selected_finish': date_finish,
        'selected_branch': branch_id,
        'selected_account': accountsub2_code,
        'selected_account_name': account_name,
        'selected_branch_name': branch_name,
        'beginning_balance': beginning_balance,
        'token': token
    }
    return render(request, 'report/ledger_result.html', context)


def ledger_consolidation(request):
    context = {
        'title': 'Ledger Consolidation',
        'accountsub2': Accountsub2.objects.all(),
        'selected_start': '',
        'selected_finish': '',
        'selected_account': '',
        'journals': [],
        'total_debit': 0,
        'total_credit': 0
    }

    if request.method == 'POST':
        date_start = request.POST.get('date_start')
        date_finish = request.POST.get('date_finish')
        accountsub2_code = request.POST.get('accountsub2_code')

        journals = Journal.objects.filter(inputdate__range=[date_start, date_finish])
        if accountsub2_code != "all":
            journals = journals.filter(coa_code=accountsub2_code)

        journals = journals.annotate(
            debit_decimal=Cast('debit', DecimalField(max_digits=20, decimal_places=2)),
            credit_decimal=Cast('credit', DecimalField(max_digits=20, decimal_places=2))
        ).order_by('inputdate')

        total_debit = journals.aggregate(total=Sum('debit_decimal'))['total'] or 0
        total_credit = journals.aggregate(total=Sum('credit_decimal'))['total'] or 0

        context.update({
            'selected_start': date_start,
            'selected_finish': date_finish,
            'selected_account': accountsub2_code,
            'journals': journals,
            'total_debit': total_debit,
            'total_credit': total_credit,
        })

    return render(request, 'report/ledger_consolidation.html', context)


def subledger_search(request):
    context = {
        'title': 'Sub Ledger Consolidation Search',
        'accountsub2': Accountsub2.objects.all()
    }
    return render(request, 'report/subledger_search_branch.html', context)


def subledger_create(request):
    accountsub2_code = request.GET.get('accountsub2_code')
    date_start = request.GET.get('date_start')
    date_finish = request.GET.get('date_finish')

    # Validasi tanggal
    if not (accountsub2_code and date_start and date_finish):
        return HttpResponse("Invalid parameters", status=400)

    # Query jurnal sesuai filter
    journals = Journal.objects.filter(inputdate__range=[date_start, date_finish])
    if accountsub2_code != 'all':
        journals = journals.filter(coa_code=accountsub2_code)

    journals = journals.order_by('inputdate', 'journal_id')  # pastikan urutan

    # Hitung beginning balance
    getbalance = Journal.objects.filter(inputdate__lt=date_start)
    if accountsub2_code != 'all':
        getbalance = getbalance.filter(coa_code=accountsub2_code)

    # Hitung saldo awal berdasarkan jenis akun
    bbcd = getbalance.aggregate(total=Sum(F('credit') - F('debit')))['total'] or Decimal('0')
    bbdc = getbalance.aggregate(total=Sum(F('debit') - F('credit')))['total'] or Decimal('0')

    account_type = accountsub2_code[:1] if accountsub2_code != 'all' else '1'
    beginning_balance = bbcd if account_type in ['2', '3', '4', '8'] else bbdc
    running_balance = beginning_balance

    # Buat workbook Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Subledger"

    # Header
    ws.append(["Date", "Reference", "Description", "Debit", "Credit", "Balance"])

    # Saldo awal
    ws.append(["", "", "Beginning Balance", "", "", float(beginning_balance)])

    total_debit = Decimal('0')
    total_credit = Decimal('0')

    for j in journals:
        debit = Decimal(j.debit or 0)
        credit = Decimal(j.credit or 0)

        if account_type in ['2', '3', '4', '8']:
            running_balance += credit - debit
        else:
            running_balance += debit - credit

        total_debit += debit
        total_credit += credit

        ws.append([
            j.inputdate.strftime('%Y-%m-%d'),
            j.reference,
            j.description,
            float(debit),
            float(credit),
            float(running_balance)
        ])

    # Total baris akhir
    ws.append(["", "", "Total", float(total_debit), float(total_credit), ""])

    # Response download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"subledger_{accountsub2_code}_{date_start}_to_{date_finish}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)

    return response