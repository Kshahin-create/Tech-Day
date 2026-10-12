from io import BytesIO
from datetime import date

from PIL import Image
from django.core.files.base import ContentFile

from students.models import Badge, StudentBadge, StudentEventStats
from attendance.models import Attendance
from workshops.models import WorkshopSession
from dashboard.models import Event


EGYPT_GOVERNORATES = {
    '01': 'القاهرة',
    '02': 'الإسكندرية',
    '03': 'بورسعيد',
    '04': 'السويس',
    '11': 'دمياط',
    '12': 'الدقهلية',
    '13': 'الشرقية',
    '14': 'القليوبية',
    '15': 'كفر الشيخ',
    '16': 'الغربية',
    '17': 'المنوفية',
    '18': 'البحيرة',
    '19': 'الإسماعيلية',
    '21': 'الجيزة',
    '22': 'بني سويف',
    '23': 'الفيوم',
    '24': 'المنيا',
    '25': 'أسيوط',
    '26': 'سوهاج',
    '27': 'قنا',
    '28': 'أسوان',
    '29': 'الأقصر',
    '31': 'البحر الأحمر',
    '32': 'الوادي الجديد',
    '33': 'مطروح',
    '34': 'شمال سيناء',
    '35': 'جنوب سيناء',
    '88': 'خارج جمهورية مصر العربية',
}


def parse_egyptian_national_id(national_id, reference_date=None):
    """
    تحليل الرقم القومي المصري (14 رقم).
    ترجع dict فيه: valid, error, birth_date, age, birth_governorate, gender.
    """
    national_id = (national_id or '').strip()
    result = {
        'valid': False,
        'error': '',
        'birth_date': None,
        'age': None,
        'birth_governorate': '',
        'gender': '',
    }

    if len(national_id) != 14 or not national_id.isdigit():
        result['error'] = 'الرقم القومي لازم يكون 14 رقم.'
        return result

    century_char = national_id[0]
    if century_char not in ('2', '3'):
        result['error'] = 'الرقم القومي غير صحيح.'
        return result

    century = 1900 if century_char == '2' else 2000
    year = int(national_id[1:3])
    month = int(national_id[3:5])
    day = int(national_id[5:7])
    full_year = century + year

    if month < 1 or month > 12 or day < 1 or day > 31:
        result['error'] = 'الرقم القومي غير صحيح.'
        return result

    try:
        birth_date = date(full_year, month, day)
    except ValueError:
        result['error'] = 'الرقم القومي غير صحيح.'
        return result

    ref = reference_date or date.today()
    age = ref.year - birth_date.year
    if (ref.month, ref.day) < (birth_date.month, birth_date.day):
        age -= 1
    if age < 0 or age > 120:
        result['error'] = 'الرقم القومي غير صحيح.'
        return result

    gov_code = national_id[7:9]
    birth_governorate = EGYPT_GOVERNORATES.get(gov_code, 'غير معروف')

    gender_digit = int(national_id[13])
    gender = 'ذكر' if gender_digit % 2 == 1 else 'أنثى'

    result.update({
        'valid': True,
        'birth_date': birth_date,
        'age': age,
        'birth_governorate': birth_governorate,
        'gender': gender,
    })
    return result


def process_profile_picture(uploaded_file, max_size=512, quality=85):
    img = Image.open(uploaded_file)
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    img.thumbnail((max_size, max_size), Image.LANCZOS)

    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True, progressive=True)
    output.seek(0)
    return ContentFile(output.read(), name='profile.jpg')

def check_and_award_badges(student, event=None):
    """
    Check if a student is eligible for any new badges and award them.
    Returns a list of newly awarded badges.
    """
    if event is None:
        event = Event.get_current()
        
    if not event:
        return []
        
    newly_awarded = []
    
    # الحصول على نقاط الطالب في هذه الفعالية
    stats = StudentEventStats.objects.filter(student=student, event=event).first()
    if not stats:
        stats = StudentEventStats.objects.create(student=student, event=event)
    event_points = stats.points
    
    # 1. Check Points Badges (Filtered by event)
    points_badges = Badge.objects.filter(event=event, criteria_type=Badge.CriteriaType.POINTS)
    for badge in points_badges:
        if event_points >= badge.criteria_value:
            # Award badge if student doesn't have it yet
            sb, created = StudentBadge.objects.get_or_create(
                student=student,
                badge=badge
            )
            if created:
                newly_awarded.append(badge)
    
    # 2. Check Attendance Rate Badges (Filtered by event)
    attendance_badges = Badge.objects.filter(event=event, criteria_type=Badge.CriteriaType.ATTENDANCE_RATE)
    if attendance_badges.exists():
        # Get total number of sessions for the student's group IN THIS EVENT
        if student.group and student.group.event == event:
            total_sessions = WorkshopSession.objects.filter(group=student.group).count()
            if total_sessions > 0:
                # Count student's attendance for these sessions
                attended_count = Attendance.objects.filter(
                    student=student,
                    session__group=student.group,
                    status=Attendance.Status.PRESENT
                ).count()
                
                attendance_rate = (attended_count / total_sessions) * 100
                
                for badge in attendance_badges:
                    if attendance_rate >= badge.criteria_value:
                        sb, created = StudentBadge.objects.get_or_create(
                            student=student,
                            badge=badge
                        )
                        if created:
                            newly_awarded.append(badge)
                            
    return newly_awarded
