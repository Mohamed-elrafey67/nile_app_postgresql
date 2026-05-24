from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date
from violations.models import UserProfile, MinistryDecision, UsageType

USERS = [
    {'username':'manager',    'password':'Manager@123',    'first_name':'مدير النظام',   'role':'manager'},
    {'username':'supervisor', 'password':'Supervisor@123', 'first_name':'المشرف العام',  'role':'supervisor'},
    {'username':'data_entry', 'password':'DataEntry@123',  'first_name':'مدخل البيانات', 'role':'data_entry'},
    {'username':'viewer',     'password':'Viewer@123',     'first_name':'مستخدم مشاهد',  'role':'viewer'},
]

DECISIONS = [
    ('14717 لسنة 1987',  date(1900,1,1),   date(1990,8,11),  Decimal('1')),
    ('14867 لسنة 1991',  date(1990,8,12),  date(2002,7,25),  Decimal('0.5')),
    ('312 لسنة 2002',    date(2002,7,26),  date(2006,5,5),   Decimal('4')),
    ('136 لسنة 2006',    date(2006,5,6),   date(2010,3,27),  Decimal('4')),
    ('116 لسنة 2010',    date(2010,3,28),  date(2015,7,6),   Decimal('12')),
    ('851 لسنة 2015',    date(2015,7,7),   date(2016,11,15), Decimal('48')),
    ('895 لسنة 2016',    date(2016,11,16), date(2018,12,31), Decimal('150')),
    ('294 لسنة 2018',    date(2019,1,1),   date(2019,11,29), Decimal('1200')),
    ('357 لسنة 2019',    date(2019,11,30), date(2021,10,17), Decimal('600')),
    ('192 لسنة 2023',    date(2023,5,3),   date(2026,3,25),  Decimal('600')),
    ('149 لسنة 2026',    date(2026,3,26),  None,             Decimal('1400')),
]

USAGE_TYPES = [
    # (name, article, warraq, aswan, other, urban_in, urban_out)
    ('مواقف سياحية',                    'أولاً أ',      1500,750,500,400,200),
    ('مواقف غير سياحية',               'أولاً ب',      1000,700,500,300,160),
    ('مواقف حكومية',                   'أولاً ج',      None,None,None,75,None),
    ('تخزين — غير زراعي',              'ثانياً أ',     None,None,None,200,48),
    ('تخزين — زراعي',                  'ثانياً ب',     None,None,None,18,18),
    ('أغراض إدارية/صناعية',            'ثالثاً',       350,300,240,144,96),
    ('مقرات إدارية حكومية',            'رابعاً',       225,150,115,115,115),
    ('أغراض تجارية',                   'خامساً',       3000,1500,800,None,None),
    ('مطعم سياحي 3 نجوم',              'سادساً',       1500,1500,None,750,375),
    ('مطعم سياحي 4 نجوم',              'سادساً',       4000,2100,None,1500,None),
    ('مطعم سياحي 5 نجوم',              'سادساً',       4000,2100,None,1500,None),
    ('مطعم غير مصنف',                  'سادساً',       None,None,None,900,720),
    ('قاعة مناسبات واحتفالات',         'سابعاً',       1500,1100,900,800,1200),
    ('ترفيهية (كازينو/ملاهي)',         'ثامناً',       1200,1000,800,640,500),
    ('جلسات تصوير',                    'تاسعاً',       1000,None,None,None,None),
    ('نادي اجتماعي — نقابات/وزارات',  'عاشراً أ',    150,75,75,60,45),
    ('نادي اجتماعي — شركات',          'عاشراً ب',    2000,1400,1000,400,300),
    ('نادي اجتماعي — لليخت',          'عاشراً ج',    1200,800,600,None,None),
    ('مشاتل',                          'حادي عشر',    None,None,None,120,60),
    ('مبانٍ سكنية',                    'رابع وعشرون', 60,48,36,24,18),
    ('زراعة/تشجير/تجميل',             'خامس عشر أ',  None,None,None,12,12),
    ('زراعة صويب وحدائق',             'خامس عشر ب',  None,None,None,18,18),
    ('مناحل عسل',                      'خامس عشر ج',  None,None,None,24,24),
    ('ملاعب',                          'ثامن عشر',    None,None,None,120,60),
    ('استغلال قاعة مناسبات واحتفالات', 'سابعاً',      1500,1100,900,800,1200),
]


class Command(BaseCommand):
    help = 'إعداد المشروع الكامل: مهاجرات + مستخدمون + قرارات وزارية + أنواع استغلال'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n══ الخطوة 1: تطبيق المهاجرات ══'))
        call_command('migrate', verbosity=1)

        self.stdout.write(self.style.MIGRATE_HEADING('\n══ الخطوة 2: المستخدمون ══'))
        for u in USERS:
            user, created = User.objects.get_or_create(username=u['username'])
            user.set_password(u['password'])
            user.first_name = u['first_name']
            user.is_active  = True
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = u['role']
            profile.save()
            status = self.style.SUCCESS('✓ جديد') if created else self.style.WARNING('↺ محدّث')
            self.stdout.write(f'  {status}  {u["first_name"]:<20} {u["username"]:<14} {u["password"]}')

        self.stdout.write(self.style.MIGRATE_HEADING('\n══ الخطوة 3: القرارات الوزارية ══'))
        if not MinistryDecision.objects.exists():
            for i,(num,df,dt,rate) in enumerate(DECISIONS,1):
                MinistryDecision.objects.create(
                    decision_number=num, date_from=df, date_to=dt,
                    rate_per_year=rate, order=i,
                )
            self.stdout.write(self.style.SUCCESS(f'  ✅ تم استيراد {len(DECISIONS)} قرار وزاري'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ موجودة مسبقاً ({MinistryDecision.objects.count()})'))

        self.stdout.write(self.style.MIGRATE_HEADING('\n══ الخطوة 4: أنواع الاستغلال ══'))
        if not UsageType.objects.exists():
            for i,(name,article,w,a,o,ui,uo) in enumerate(USAGE_TYPES,1):
                UsageType.objects.create(
                    name=name, article=article,
                    rate_warraq=w, rate_aswan=a, rate_other=o,
                    rate_urban_in=ui, rate_urban_out=uo,
                    order=i,
                )
            self.stdout.write(self.style.SUCCESS(f'  ✅ تم استيراد {len(USAGE_TYPES)} نوع استغلال'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ موجودة مسبقاً ({UsageType.objects.count()})'))

        self.stdout.write(self.style.SUCCESS('\n✅ المشروع جاهز!\n'))
        self.stdout.write('  python manage.py runserver\n')
