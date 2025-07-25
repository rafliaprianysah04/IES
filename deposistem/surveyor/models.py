from django.db import models

# Create your models here.
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

class KontainerTerdeteksi(models.Model):
    nomor_kontainer = models.CharField(max_length=15, unique=True)
    cont_size = models.CharField(blank=True, null=True)
    cont_type = models.CharField(blank=True, null=True)
    waktu_deteksi = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('baru', 'Baru'), ('digunakan', 'Digunakan')], default='baru')
    gambar = models.ImageField(upload_to='gambar_kontainer/', null=True, blank=True)
    probabilitas = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.nomor_kontainer
    
    class Meta:
        db_table = 'kontainer_terdeteksi'


class SurveyIns(models.Model):
    id = models.BigIntegerField(primary_key=True)
    customer_code = models.CharField(blank=True, null=True)
    cont = models.CharField(blank=True, null=True)
    cont_size = models.CharField(blank=True, null=True)
    cont_type = models.CharField(blank=True, null=True)
    condition = models.CharField(blank=True, null=True)
    washing = models.CharField(blank=True, null=True)
    manufacture = models.CharField(blank=True, null=True)
    tare = models.CharField(blank=True, null=True)
    payload = models.CharField(blank=True, null=True)
    grade_depot = models.CharField(blank=True, null=True)
    haulier_in = models.CharField(blank=True, null=True)
    truck_no_in = models.CharField(blank=True, null=True)
    remark = models.CharField(blank=True, null=True)
    washing_upload_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(blank=True, null=True)
    photo_status = models.CharField(blank=True, null=True)
    eir_status = models.CharField(blank=True, null=True)
    eir_send_at = models.DateTimeField(blank=True, null=True)
    eir_data = models.CharField(blank=True, null=True)
    grade_msl = models.CharField(blank=True, null=True)
    grade_msl_status = models.CharField(blank=True, null=True)
    grade_change_req_by = models.CharField(blank=True, null=True)
    grade_change_req_at = models.DateTimeField(blank=True, null=True)
    review_by = models.CharField(blank=True, null=True)
    review_at = models.DateTimeField(blank=True, null=True)
    review_status = models.CharField(blank=True, null=True)
    review_message = models.CharField(blank=True, null=True)
    review_remark = models.CharField(blank=True, null=True)
    third_party_damage = models.CharField(blank=True, null=True)
    estimator_remark = models.CharField(blank=True, null=True)
    estimated_by = models.CharField(blank=True, null=True)
    estimated_at = models.DateTimeField(blank=True, null=True)
    mnr_upload_by = models.CharField(blank=True, null=True)
    mnr_upload_at = models.DateTimeField(blank=True, null=True)
    stacking_status = models.CharField(blank=True, null=True)
    stacking_by = models.CharField(blank=True, null=True)
    stacking_at = models.DateTimeField(blank=True, null=True)
    stacking_location = models.CharField(blank=True, null=True)
    stacking_condition = models.CharField(blank=True, null=True)
    shift_loc_by = models.CharField(blank=True, null=True)
    shift_loc_at = models.CharField(blank=True, null=True)
    shift_loc_curr = models.CharField(blank=True, null=True)
    shift_loc_hist01 = models.CharField(blank=True, null=True)
    shift_loc_hist02 = models.CharField(blank=True, null=True)
    shift_loc_hist03 = models.CharField(blank=True, null=True)
    created_by = models.CharField(blank=True, null=True)
    updated_by = models.CharField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    act_in = models.CharField(blank=True, null=True)
    washed_by = models.CharField(blank=True, null=True)
    roof_survey_at = models.DateTimeField(blank=True, null=True)
    roof_survey_by = models.CharField(blank=True, null=True)
    roof_survey_status = models.CharField(blank=True, null=True)
    #photo = models.ImageField(upload_to='survey_photos/', blank=True, null=True)


    class Meta:
        db_table = 'survey_ins'


class SurveyInsNew(models.Model):
    id = models.AutoField(primary_key=True)
    customer_code = models.CharField(blank=True, null=True)
    cont = models.CharField(blank=True, null=True)
    cont_size = models.CharField(blank=True, null=True)
    cont_type = models.CharField(blank=True, null=True)
    condition = models.CharField(blank=True, null=True)
    washing = models.CharField(blank=True, null=True)
    manufacture = models.CharField(blank=True, null=True)
    tare = models.CharField(blank=True, null=True)
    payload = models.CharField(blank=True, null=True)
    grade_depot = models.CharField(blank=True, null=True)
    haulier_in = models.CharField(blank=True, null=True)
    truck_no_in = models.CharField(blank=True, null=True)
    remark = models.CharField(blank=True, null=True)
    washing_upload_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(blank=True, null=True)
    photo_status = models.CharField(blank=True, null=True)
    eir_status = models.CharField(blank=True, null=True)
    eir_send_at = models.DateTimeField(blank=True, null=True)
    eir_data = models.CharField(blank=True, null=True)
    grade_msl = models.CharField(blank=True, null=True)
    grade_msl_status = models.CharField(blank=True, null=True)
    grade_change_req_by = models.CharField(blank=True, null=True)
    grade_change_req_at = models.DateTimeField(blank=True, null=True)
    review_by = models.CharField(blank=True, null=True)
    review_at = models.DateTimeField(blank=True, null=True)
    review_status = models.CharField(blank=True, null=True)
    review_message = models.CharField(blank=True, null=True)
    review_remark = models.CharField(blank=True, null=True)
    third_party_damage = models.CharField(blank=True, null=True)
    estimator_remark = models.CharField(blank=True, null=True)
    estimated_by = models.CharField(blank=True, null=True)
    estimated_at = models.DateTimeField(blank=True, null=True)
    mnr_upload_by = models.CharField(blank=True, null=True)
    mnr_upload_at = models.DateTimeField(blank=True, null=True)
    stacking_status = models.CharField(blank=True, null=True)
    stacking_by = models.CharField(blank=True, null=True)
    stacking_at = models.DateTimeField(blank=True, null=True)
    stacking_location = models.CharField(blank=True, null=True)
    stacking_condition = models.CharField(blank=True, null=True)
    shift_loc_by = models.CharField(blank=True, null=True)
    shift_loc_at = models.CharField(blank=True, null=True)
    shift_loc_curr = models.CharField(blank=True, null=True)
    shift_loc_hist01 = models.CharField(blank=True, null=True)
    shift_loc_hist02 = models.CharField(blank=True, null=True)
    shift_loc_hist03 = models.CharField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    act_in = models.CharField(blank=True, null=True)
    washed_by = models.CharField(blank=True, null=True)
    roof_survey_at = models.DateTimeField(blank=True, null=True)
    roof_survey_by = models.CharField(blank=True, null=True)
    roof_survey_status = models.CharField(blank=True, null=True)
    #photo = models.ImageField(upload_to='survey_photos/', blank=True, null=True)
    foto = models.ImageField(upload_to='survey_photos/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    class Meta:
        db_table = 'survey_ins_new'


class SurveyInItems(models.Model):
    id = models.BigIntegerField(primary_key=True)
    #survey_in_id = models.BigIntegerField(blank=True, null=True)
    survey_in_id = models.ForeignKey('SurveyIns', on_delete=models.CASCADE, db_column='survey_in_id', blank=True, null=True)
    upload_site = models.CharField(blank=True, null=True)
    upload_seq = models.CharField(blank=True, null=True)
    remark = models.CharField(blank=True, null=True)
    file_name = models.CharField(blank=True, null=True)
    eir_photo_path = models.CharField(blank=True, null=True)
    eir_photo_name = models.CharField(blank=True, null=True)
    eir_rotation = models.CharField(blank=True, null=True)
    created_by = models.CharField(blank=True, null=True)
    updated_by = models.CharField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'survey_in_items'

    def __str__(self):
        return f"Photo for {self.survey.cont}"

class SurveyInsPhoto(models.Model):
    survey = models.ForeignKey(SurveyInsNew, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='surveyin_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.survey.cont}"
    
    class Meta:
        db_table = 'surveyphoto'


    