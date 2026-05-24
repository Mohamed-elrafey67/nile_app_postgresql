"""
تحديث أسعار القرار 149 (مخالفة) وفقاً للقرار الوزاري 149 لسنة 2026
وإضافة أنواع جديدة للقرار 148 (ترخيص) وفقاً للقرار الوزاري 148 لسنة 2026

التغييرات في القرار 149:
- مواقف سياحية: Aswan 750→1050, Other 500→750
- مبانٍ سكنية: Aswan 48→96, Other 36→72, Urban_in 24→48, Warraq→None

الإضافات للقرار 148:
- 14 نوع استغلال جديد بأسعار الترخيص (نصف أسعار المخالفة تقريباً)
"""
from django.db import migrations


def update_rates(apps, schema_editor):
    UsageType = apps.get_model('violations', 'UsageType')

    # ========== 1. تحديث أسعار القرار 149 ==========
    updates_149 = {
        1:  {'rate_aswan': 1050, 'rate_other': 750},       # مواقف سياحية
        20: {'rate_warraq': None, 'rate_aswan': 96,         # مبانٍ سكنية
             'rate_other': 72, 'rate_urban_in': 48},
    }
    for uid, vals in updates_149.items():
        UsageType.objects.filter(id=uid, decision='149').update(**vals)

    # ========== 2. إضافة أنواع القرار 148 ==========
    types_148 = [
        {'name':'مواقف/انتظار — سياحي',   'article':'أولاً أ',   'rate_warraq':750,  'rate_aswan':525, 'rate_other':375, 'rate_urban_in':200, 'rate_urban_out':100, 'order':1},
        {'name':'مواقف/انتظار — غير سياحي','article':'أولاً ب',   'rate_warraq':500,  'rate_aswan':350, 'rate_other':250, 'rate_urban_in':150, 'rate_urban_out':80,  'order':2},
        {'name':'مواقف حكومية',            'article':'أولاً ج',   'rate_warraq':None, 'rate_aswan':None,'rate_other':None,'rate_urban_in':50,  'rate_urban_out':50,  'order':3},
        {'name':'تخزين مهمات — غير زراعي', 'article':'ثانياً أ',  'rate_warraq':None, 'rate_aswan':None,'rate_other':None,'rate_urban_in':100, 'rate_urban_out':24,  'order':4},
        {'name':'تخزين — زراعي خاص',       'article':'ثانياً ب',  'rate_warraq':None, 'rate_aswan':None,'rate_other':None,'rate_urban_in':12,  'rate_urban_out':12,  'order':5},
        {'name':'أغراض إدارية/صناعية',     'article':'ثالثاً',    'rate_warraq':175,  'rate_aswan':150, 'rate_other':120, 'rate_urban_in':72,  'rate_urban_out':48,  'order':6},
        {'name':'مقرات إدارية حكومية',     'article':'رابعاً',    'rate_warraq':None, 'rate_aswan':None,'rate_other':None,'rate_urban_in':75,  'rate_urban_out':75,  'order':7},
        {'name':'أغراض تجارية',            'article':'خامساً',    'rate_warraq':1500, 'rate_aswan':750, 'rate_other':400, 'rate_urban_in':None,'rate_urban_out':None,'order':8},
        {'name':'قاعة مناسبات واحتفالات',  'article':'سابعاً',    'rate_warraq':750,  'rate_aswan':550, 'rate_other':450, 'rate_urban_in':400, 'rate_urban_out':600, 'order':9},
        {'name':'ترفيهية (كازينو/ملاهي)',  'article':'ثامناً',    'rate_warraq':600,  'rate_aswan':500, 'rate_other':400, 'rate_urban_in':320, 'rate_urban_out':250, 'order':10},
        {'name':'مبانٍ سكنية',             'article':'رابع وعشرون','rate_warraq':None, 'rate_aswan':None,'rate_other':None,'rate_urban_in':60,  'rate_urban_out':36,  'order':11},
        {'name':'زراعة/تشجير/تجميل',       'article':'خامس عشر أ','rate_warraq':None, 'rate_aswan':None,'rate_other':None,'rate_urban_in':6,   'rate_urban_out':6,   'order':12},
        {'name':'صويب/حدائق مثمرة',        'article':'خامس عشر ب','rate_warraq':None, 'rate_aswan':None,'rate_other':None,'rate_urban_in':9,   'rate_urban_out':9,   'order':13},
        {'name':'مناحل عسل',               'article':'خامس عشر ج','rate_warraq':None, 'rate_aswan':None,'rate_other':None,'rate_urban_in':12,  'rate_urban_out':12,  'order':14},
    ]
    for t in types_148:
        UsageType.objects.get_or_create(
            name=t['name'], decision='148',
            defaults=t
        )


class Migration(migrations.Migration):
    dependencies = [
        ('violations', '0010_add_usage_basis'),
    ]
    operations = [
        migrations.RunPython(update_rates),
    ]
