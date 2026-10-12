from django.contrib import admin

from .models import Student, StudentRegistration


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'group', 'school', 'national_id', 'age', 'gender', 'profile_picture')
    list_filter = ('group', 'gender', 'birth_governorate')
    search_fields = ('name', 'student_id', 'school', 'national_id', 'email', 'phone_number')
    readonly_fields = ('profile_picture_preview',)

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="max-height:120px;border-radius:12px;"/>', obj.profile_picture.url)
        return '—'
    profile_picture_preview.short_description = 'معاينة الصورة'

    fieldsets = (
        (None, {
            'fields': ('name', 'student_id', 'profile_picture', 'profile_picture_preview', 'user', 'group', 'school', 'education_admin', 'email', 'phone_number', 'grade')
        }),
        ('البيانات الشخصية', {
            'fields': ('national_id', 'birth_date', 'age', 'birth_governorate', 'gender')
        }),
        ('الفعالية', {
            'fields': ('checked_in', 'checked_in_at', 'is_blacklisted', 'is_certificate_banned', 'points')
        }),
        ('الشهادة', {
            'fields': ('cert_emails_sent', 'last_cert_email_at')
        }),
    )


@admin.register(StudentRegistration)
class StudentRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name_ar', 'email', 'phone_number', 'national_id', 'age', 'gender', 'school', 'status', 'created_at')
    list_filter = ('status', 'gender', 'birth_governorate', 'education_admin')
    search_fields = ('full_name_ar', 'full_name_en', 'email', 'phone_number', 'national_id', 'school')
    readonly_fields = ('profile_picture_preview', 'id_document_preview')

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="max-height:150px;border-radius:12px;"/>', obj.profile_picture.url)
        return '—'
    profile_picture_preview.short_description = 'الصورة الشخصية'

    def id_document_preview(self, obj):
        if obj.id_document:
            from django.utils.html import format_html
            return format_html('<a href="{}" target="_blank"><img src="{}" style="max-height:200px;max-width:300px;border-radius:12px;"/></a>', obj.id_document.url, obj.id_document.url)
        return '—'
    id_document_preview.short_description = 'وثيقة التحقق من الشخصية'

    fieldsets = (
        (None, {
            'fields': ('event', 'student', 'status', 'approved_by', 'approved_at')
        }),
        ('البيانات الشخصية', {
            'fields': ('full_name_ar', 'full_name_en', 'email', 'phone_number', 'national_id', 'birth_date', 'age', 'birth_governorate', 'gender')
        }),
        ('البيانات الدراسية', {
            'fields': ('school', 'education_admin', 'grade', 'interests')
        }),
        ('المرفقات', {
            'fields': ('profile_picture', 'profile_picture_preview', 'id_document', 'id_document_preview')
        }),
        ('الحالة', {
            'fields': ('rejected_reason', 'removed_at', 'removed_by')
        }),
    )
