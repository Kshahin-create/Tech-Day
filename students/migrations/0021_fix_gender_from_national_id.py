from django.db import migrations


def _gender_from_nid(nid):
    nid = ''.join(ch for ch in (nid or '') if ch.isdigit())
    if len(nid) != 14:
        return None
    # الرقم الـ13 (index 12) هو رقم النوع: فردي = ذكر، زوجي = أنثى
    return 'ذكر' if int(nid[12]) % 2 == 1 else 'أنثى'


def fix_genders(apps, schema_editor):
    for model_name in ('Student', 'StudentRegistration'):
        Model = apps.get_model('students', model_name)
        to_update = []
        for obj in Model.objects.exclude(national_id='').only('id', 'national_id', 'gender'):
            gender = _gender_from_nid(obj.national_id)
            if gender and obj.gender != gender:
                obj.gender = gender
                to_update.append(obj)
        if to_update:
            Model.objects.bulk_update(to_update, ['gender'], batch_size=500)


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0020_student_age_student_birth_date_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_genders, migrations.RunPython.noop),
    ]
