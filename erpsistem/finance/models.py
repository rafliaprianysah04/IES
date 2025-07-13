from django.db import models

class ExternalMenu(models.Model):
    nama_menu = models.CharField(max_length=100)
    icon_menu = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    sort = models.IntegerField()
    app_id = models.CharField(max_length=50)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'superadmin_menu'


class ExternalSubMenu(models.Model):
    nama_submenu = models.CharField(max_length=100)
    icon_submenu = models.CharField(max_length=100)
    sort = models.IntegerField()
    created_at = models.DateTimeField()
    menu_id = models.IntegerField()
    urls = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'superadmin_submenu'


class ExternalAccessMenu(models.Model):
    role_id = models.IntegerField()
    menu_id = models.IntegerField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'superadmin_accessmenu'


class Account(models.Model):
    account_id = models.SmallIntegerField(primary_key=True)
    account_code = models.CharField(max_length=8, blank=True, null=True)
    account_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'account'


class Account1(models.Model):
    account1_id = models.SmallIntegerField(primary_key=True)
    accountcode = models.CharField(max_length=8)
    account1_code = models.CharField(max_length=8)
    account1_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'account1'


class Account2(models.Model):
    account2_id = models.SmallIntegerField(primary_key=True)
    account1code = models.CharField(max_length=8)
    account2_code = models.CharField(max_length=8)
    account2_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'account2'


class Accountsub1(models.Model):
    accountsub1_id = models.SmallIntegerField(primary_key=True)
    account2code = models.CharField(max_length=8)
    accountsub1_code = models.CharField(max_length=8)
    accountsub1_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'accountsub1'


class Accountsub2(models.Model):
    accountsub2_id = models.SmallIntegerField(primary_key=True)
    accountsub1code = models.CharField(max_length=8)
    accountsub2_code = models.CharField(max_length=15, blank=True, null=True)
    accountsub2_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'accountsub2'


class Accountsublocation(models.Model):
    accountsublocation_id = models.SmallIntegerField(primary_key=True)
    accountsubid = models.CharField(max_length=12, blank=True, null=True)
    accountsublocation_code = models.CharField(max_length=12, blank=True, null=True)
    accountsublocation_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    accountsub2loc_code = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accountsublocation'


class Bbalance(models.Model):
    bbalance_id = models.SmallIntegerField(primary_key=True)
    accountsub2code = models.CharField(max_length=9)
    branch_id = models.CharField(max_length=6)
    inputdate = models.DateField(blank=True, null=True)
    debit = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    credit = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'bbalance'


class Consignee(models.Model):
    consignee_id = models.IntegerField(primary_key=True)
    consignee_code = models.TextField()
    consignee_name = models.TextField()
    consignee_alias = models.TextField(blank=True, null=True)
    type = models.IntegerField()
    address = models.CharField(max_length=256, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.CharField(max_length=50, blank=True, null=True)
    npwp = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consignee'


class Contact(models.Model):
    contact_id = models.IntegerField(primary_key=True)
    contact_code = models.CharField(unique=True, max_length=8)
    contact_name = models.CharField(max_length=128, blank=True, null=True)
    contact_alias = models.CharField(max_length=50, blank=True, null=True)
    type = models.SmallIntegerField(blank=True, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contact'


class Journal(models.Model):
    journal_id = models.IntegerField(primary_key=True)
    reference_id = models.IntegerField()
    reference = models.CharField(max_length=50, blank=True, null=True)
    inputdate = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    coa_code = models.CharField(max_length=9, blank=True, null=True)
    branch_id = models.CharField(max_length=6, blank=True, null=True)
    contact_code = models.CharField(max_length=9, blank=True, null=True)
    debit = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    credit = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    code = models.CharField(max_length=3, blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    deleted_by = models.CharField(max_length=50, blank=True, null=True)
    date_deleted = models.DateTimeField(blank=True, null=True)
    approved_by = models.CharField(max_length=50, blank=True, null=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    rejected_by = models.CharField(max_length=50, blank=True, null=True)
    date_rejected = models.DateTimeField(blank=True, null=True)
    completed = models.SmallIntegerField(blank=True, null=True)
    auto_jurnal = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'journal'


class JournalAudit(models.Model):
    journal_id = models.IntegerField(primary_key=True)
    reference_id = models.IntegerField()
    reference = models.CharField(max_length=50, blank=True, null=True)
    inputdate = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    coa_code = models.CharField(max_length=9, blank=True, null=True)
    branch_id = models.CharField(max_length=6, blank=True, null=True)
    contact_code = models.CharField(max_length=9, blank=True, null=True)
    debit = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    credit = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    code = models.CharField(max_length=3, blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    deleted_by = models.CharField(max_length=50, blank=True, null=True)
    date_deleted = models.DateTimeField(blank=True, null=True)
    approved_by = models.CharField(max_length=50, blank=True, null=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    rejected_by = models.CharField(max_length=50, blank=True, null=True)
    date_rejected = models.DateTimeField(blank=True, null=True)
    completed = models.SmallIntegerField(blank=True, null=True)
    auto_jurnal = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'journal_audit'


class Product(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_code = models.CharField(unique=True, max_length=6)
    product_name = models.CharField(max_length=128, blank=True, null=True)
    category = models.SmallIntegerField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount_available = models.SmallIntegerField(blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product'


class ReferenceJournal(models.Model):
    reference_id = models.IntegerField(primary_key=True)
    inputdate = models.DateField(blank=True, null=True)
    reference = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    branch_id = models.CharField(max_length=6, blank=True, null=True)
    contact_code = models.CharField(max_length=9, blank=True, null=True)
    code = models.CharField(max_length=3, blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    deleted_by = models.CharField(max_length=50, blank=True, null=True)
    date_deleted = models.DateTimeField(blank=True, null=True)
    approved_by = models.CharField(max_length=50, blank=True, null=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    rejected_by = models.CharField(max_length=50, blank=True, null=True)
    date_rejected = models.DateTimeField(blank=True, null=True)
    completed = models.SmallIntegerField(blank=True, null=True)
    auto_jurnal = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'reference_journal'


class ReferenceJournalAudit(models.Model):
    id = models.IntegerField(primary_key=True)
    reference_id = models.IntegerField()
    inputdate = models.DateField(blank=True, null=True)
    reference = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    branch_id = models.CharField(max_length=6, blank=True, null=True)
    contact_code = models.CharField(max_length=9, blank=True, null=True)
    code = models.CharField(max_length=3, blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    deleted_by = models.CharField(max_length=50, blank=True, null=True)
    date_deleted = models.DateTimeField(blank=True, null=True)
    approved_by = models.CharField(max_length=50, blank=True, null=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    rejected_by = models.CharField(max_length=50, blank=True, null=True)
    date_rejected = models.DateTimeField(blank=True, null=True)
    completed = models.SmallIntegerField(blank=True, null=True)
    auto_jurnal = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'reference_journal_audit'


class Sparepart(models.Model):
    sparepart_id = models.IntegerField(primary_key=True)
    sparepart_code = models.CharField(max_length=6)
    sparepart_name = models.CharField(max_length=128, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sparepart'


class Tax(models.Model):
    tax_id = models.SmallIntegerField(primary_key=True)
    tax_code = models.CharField(unique=True, max_length=3)
    tax_name = models.CharField(max_length=50, blank=True, null=True)
    tax_alias = models.CharField(max_length=20, blank=True, null=True)
    tax_percentage = models.SmallIntegerField(blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tax'


class UnlockRequest(models.Model):
    id = models.IntegerField(primary_key=True)
    reference = models.CharField(max_length=20)
    code_reference = models.CharField(max_length=2)
    request_by = models.CharField(max_length=100)
    request_date = models.DateTimeField(blank=True, null=True)
    unlock_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'unlock_request'


class Uom(models.Model):
    uom_id = models.SmallIntegerField(primary_key=True)
    uom_code = models.CharField(unique=True, max_length=4)
    uom_name = models.CharField(max_length=128, blank=True, null=True)
    uom_alias = models.CharField(max_length=25, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'uom'


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    email = models.CharField(max_length=128)
    image = models.CharField(max_length=128)
    password = models.CharField(max_length=256)
    role_id = models.IntegerField()
    is_active = models.IntegerField()
    date_created = models.IntegerField()
    qrcode = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'user'


class UserAccessMenu(models.Model):
    id = models.IntegerField(primary_key=True)
    role_id = models.IntegerField()
    menu_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user_access_menu'


class UserMenu(models.Model):
    id = models.IntegerField(primary_key=True)
    menu = models.CharField(max_length=128)
    sort = models.IntegerField()
    icons = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'user_menu'


class UserRole(models.Model):
    id = models.IntegerField(primary_key=True)
    role = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'user_role'


class UserSubMenu(models.Model):
    submenu_id = models.IntegerField(primary_key=True)
    menu_id = models.IntegerField()
    title = models.CharField(max_length=128)
    url = models.CharField(max_length=128)
    icon = models.CharField(max_length=128)
    is_active = models.IntegerField()
    sort = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user_sub_menu'


class UserToken(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=128)
    token = models.CharField(max_length=128)
    date_created = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user_token'


class Warehouse(models.Model):
    wh_id = models.SmallIntegerField(primary_key=True)
    wh_code = models.CharField(unique=True, max_length=4)
    wh_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'warehouse'


class Branch(models.Model):
    company = models.ForeignKey('Company', models.DO_NOTHING, blank=True, null=True)
    branch_id = models.CharField(primary_key=True, max_length=6)
    name_branch = models.CharField(max_length=50, blank=True, null=True)
    npwp = models.CharField(max_length=20, blank=True, null=True)
    established = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    telp = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)
    coa = models.CharField(max_length=2, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.IntegerField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'branch'


class Company(models.Model):
    company_id = models.CharField(primary_key=True, max_length=6)
    name = models.CharField(max_length=50, blank=True, null=True)
    npwp = models.CharField(max_length=20, blank=True, null=True)
    established = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    telp = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)
    logo_company = models.CharField(max_length=128, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.IntegerField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'company'


class BandTitle(models.Model):
    positionid = models.ForeignKey('Position', models.DO_NOTHING, db_column='positionid')
    band_id = models.CharField(primary_key=True, max_length=3)
    band = models.CharField(max_length=5, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.IntegerField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.IntegerField(blank=True, null=True)

    class Meta:

        db_table = 'band_title'


class Department(models.Model):
    divisionid = models.ForeignKey('Division', models.DO_NOTHING, db_column='divisionid')
    department_id = models.CharField(primary_key=True, max_length=6)
    name_department = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.IntegerField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'department'


class Directorate(models.Model):
    directorate_id = models.CharField(primary_key=True, max_length=6)
    name_directorate = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.IntegerField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'directorate'


class Division(models.Model):
    directorateid = models.ForeignKey(Directorate, models.DO_NOTHING, db_column='directorateid')
    division_id = models.CharField(primary_key=True, max_length=6)
    name_division = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.IntegerField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'division'


class EmployeeInformation(models.Model):
    id = models.IntegerField(primary_key=True)
    employeeid = models.ForeignKey('EmployeeMaster', models.DO_NOTHING, db_column='employeeid')
    ktp_no = models.CharField(max_length=20, blank=True, null=True)
    npwp_no = models.CharField(max_length=20, blank=True, null=True)
    bpjstk_no = models.CharField(max_length=15, blank=True, null=True)
    bpjsk_no = models.CharField(max_length=15, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    place_birth = models.CharField(max_length=50, blank=True, null=True)
    date_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    religion = models.CharField(max_length=1, blank=True, null=True)
    sex = models.CharField(max_length=1, blank=True, null=True)
    marital_status = models.CharField(max_length=1, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    telp = models.CharField(max_length=15, blank=True, null=True)
    hp = models.CharField(max_length=15, blank=True, null=True)
    photo = models.CharField(max_length=125, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.IntegerField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.IntegerField(blank=True, null=True)
    blood = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        db_table = 'employee_information'


class EmployeeMaster(models.Model):
    employee_id = models.CharField(primary_key=True, max_length=9)
    branch_id = models.CharField(max_length=6, blank=True, null=True)
    section_id = models.CharField(max_length=6, blank=True, null=True)
    band_id = models.CharField(max_length=3, blank=True, null=True)
    joint_date = models.DateField(blank=True, null=True)
    exit_date = models.DateField(blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.IntegerField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.IntegerField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)
    qr_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'employee_master'


class Position(models.Model):
    position_id = models.CharField(primary_key=True, max_length=3)
    position_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.IntegerField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.IntegerField(blank=True, null=True)

    class Meta:

        db_table = 'position'


class Section(models.Model):
    departmentid = models.ForeignKey(Department, models.DO_NOTHING, db_column='departmentid')
    section_id = models.CharField(primary_key=True, max_length=6)
    section_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.SmallIntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.IntegerField(blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    date_updated = models.IntegerField(blank=True, null=True)

    class Meta:

        db_table = 'section'
