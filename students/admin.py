from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'group', 'school', 'profile_picture')
    list_filter = ('group',)
    search_fields = ('name', 'student_id', 'school')
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
        ('الفعالية', {
            'fields': ('checked_in', 'checked_in_at', 'is_blacklisted', 'is_certificate_banned', 'points')
        }),
        ('الشهادة', {
            'fields': ('cert_emails_sent', 'last_cert_email_at')
        }),
    )
