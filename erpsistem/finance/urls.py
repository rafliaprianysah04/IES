from django.urls import path
from django.http import JsonResponse
from . import views
from .models import *  # jika tetap ingin JSONResponse
app_name = 'finance'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    #LEDGER
    path('ledger/', views.ledger, name='ledger'),
    path('ledger/edit/<int:reference_id>/', views.ledger_edit, name='ledger_edit'),
    path('ledger/approve/<int:reference_id>/', views.ledger_approve, name='ledger_approve'),
    path('voucher/<int:reference_id>/', views.voucher_view, name='voucher_view'),
    path('pdf/<int:reference_id>/', views.voucher_pdf, name='voucher_pdf'),
    path('journal/add/', views.journal_add, name='journal_add'),


    path('cashbank/expense/', views.expense, name='expense'),
    path('cashbank/fundtransfer/', views.fundtransfer, name='fundtransfer'),
    path('sales/sales_invoice/', views.sales_invoice, name='sales_invoice'),
    path('sales/sales-remaining/', views.sales_remaining, name='sales_remaining'),
    path('purchase/purchase_invoice/', views.purchase_invoice, name='purchase_invoice'),
    path('master/coa/', views.coa, name='coa'),
    path('master/supporting_data/', views.supporting_data, name='supporting_data'),

    path('report/ledger_search_branch/', views.ledger_search_branch, name='ledger_search_branch'),
    path('report/subledger_search_branch/', views.subledger_search, name='subledger_search_branch'),
    path('subledger/create/', views.subledger_create, name='subledger_create'),
    path('excel/create/', views.subledger_create, name='subledger_create'),
    path('report/ledger_search_consolidation/', views.ledger_consolidation, name='ledger_consolidation'),
    path('report/ledger_result/', views.ledger_result, name='ledger_result'),
    # Account CRUD
    path('account/', views.account_list, name='account_list'),
    path('account/add/', views.add_account, name='account_add'),
    path('account/update/<int:id>/', views.update_account, name='account_update'),
    path('account/delete/<int:id>/', views.delete_account, name='account_delete'),
    
    # Account JSON (bisa dipindahkan ke views.py)
    path('account/<int:id>/json/', lambda request, id: JsonResponse(Account.objects.filter(account_id=id).values().first()), name='account_json'),

    # Account1 CRUD
    path('account1/', views.account1_list, name='account1_list'),
    path('account1/add/', views.add_account1, name='account1_add'),
    path('account1/update/<int:id>/', views.update_account1, name='account1_update'),
    path('account1/delete/<int:id>/', views.delete_account1, name='account1_delete'),
    
    # Account JSON (bisa dipindahkan ke views.py)
    path('account1/<int:id>/json/', lambda request, id: JsonResponse(Account1.objects.filter(account1_id=id).values().first()), name='account1_json'),

    # Account2 CRUD
    path('account2/', views.account2_list, name='account2_list'),
    path('account2/add/', views.add_account2, name='account2_add'),
    path('account2/update/<int:id>/', views.update_account2, name='account2_update'),
    path('account2/delete/<int:id>/', views.delete_account2, name='account2_delete'),
    
    # Account JSON (bisa dipindahkan ke views.py)
    path('account2/<int:id>/json/', lambda request, id: JsonResponse(Account2.objects.filter(account2_id=id).values().first()), name='account2_json'),

    # Account SUB 1 CRUD
    path('accountsub1/', views.accountsub1_list, name='accountsub1_list'),
    path('accountsub1/add/', views.add_accountsub1, name='accountsub1_add'),
    path('accountsub1/update/<int:id>/', views.update_accountsub1, name='accountsub1_update'),
    path('accountsub1/delete/<int:id>/', views.delete_accountsub1, name='accountsub1_delete'),
    
    # Account JSON (bisa dipindahkan ke views.py)
    path('accountsub1/<int:id>/json/', lambda request, id: JsonResponse(Accountsub1.objects.filter(accountsub1_id=id).values().first()), name='accountsub1_json'),


     # Account SUB 1 CRUD
    path('accountsub2/', views.accountsub2_list, name='accountsub2_list'),
    path('accountsub2/add/', views.add_accountsub2, name='accountsub2_add'),
    path('accountsub2/update/<int:id>/', views.update_accountsub2, name='accountsub2_update'),
    path('accountsub2/delete/<int:id>/', views.delete_accountsub2, name='accountsub2_delete'),
    
    # Account JSON (bisa dipindahkan ke views.py)
    path('accountsub2/<int:id>/json/', lambda request, id: JsonResponse(Accountsub2.objects.filter(accountsub2_id=id).values().first()), name='accountsub2_json'),

    # SUPPORTING DATA
    path('branch/', views.branch_list, name='supportingdata_branch'),
    path('employee/', views.employee_list, name='supportingdata_employee'),
    path('contacts/', views.contact_list, name='supportingdata_contact'),
    path('warehouse/', views.warehouse_list, name='supportingdata_warehouse'),
    path('tax/', views.tax_list, name='supportingdata_tax'),
    path('uoms/', views.uom_list, name='supportingdata_uom'),
    path('bbalance/', views.beginning_balance, name='beginning_balance'),
    path('add_bbalance/', views.add_bbalance, name='add_bbalance'),
    path('get_bbalanced/', views.get_bbalanced, name='get_bbalanced'),
]
