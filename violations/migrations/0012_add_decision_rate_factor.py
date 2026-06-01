"""
Migration 0012: إضافة القرارات الوزارية ومعامل السعر
- Add rate_factor to UsageType (1.00 للمخالفة، 0.50 للترخيص)
- Add used_decision FK to ViolationUsage
- Add MinistryDecision records: 148 لسنة 2026, 193 لسنة 2024
- Set rate_factor=0.5 for all 148 types & double their stored rates
"""
from django.db import migrations, models
import django.db.models.deletion


def add_decisions_and_update_rates(apps, schema_editor):
    MinistryDecision = apps.get_model('violations', 'MinistryDecision')
    UsageType = apps.get_model('violations', 'UsageType')
    from datetime import date

    # ── 1. إضافة القرار 193 لسنة 2024 ──
    MinistryDecision.objects.get_or_create(
        decision_number='193 لسنة 2024',
        defaults={
            'date_from': date(2024, 6, 1),
            'date_to': date(2026, 3, 25),
            'rate_per_year': 600,
            'notes': 'قرار وزير الري رقم 193 لسنة 2024 بشأن مقابل الانتفاع',
            'order': 11,
        }
    )

    # إعادة ترتيب القرارات: 192 ← 11, 193 ← 12, 149 ← 13
    try:
        d192 = MinistryDecision.objects.get(decision_number__contains='192')
        d192.order = 11
        d192.save(update_fields=['order'])
    except MinistryDecision.DoesNotExist:
        pass
    try:
        d193 = MinistryDecision.objects.get(decision_number__contains='193')
        d193.order = 12
        d193.save(update_fields=['order'])
    except MinistryDecision.DoesNotExist:
        pass
    try:
        d149 = MinistryDecision.objects.get(decision_number__contains='149')
        d149.order = 13
        d149.save(update_fields=['order'])
    except MinistryDecision.DoesNotExist:
        pass

    # ── 2. إضافة القرار 148 لسنة 2026 (ترخيص) ──
    MinistryDecision.objects.get_or_create(
        decision_number='148 لسنة 2026 — ترخيص',
        defaults={
            'date_from': date(2026, 3, 26),
            'date_to': None,  # ساري حتى الآن
            'rate_per_year': 700,  # نصف 149 (1400)
            'notes': 'قرار وزير الري رقم 148 لسنة 2026 — تراخيص الانتفاع (نصف قيمة المخالفة)',
            'order': 14,
        }
    )

    # ── 3. ضبط rate_factor وتحديث الأسعار لأنواع 148 ──
    # 3a. جميع أنواع 149: rate_factor = 1.0
    UsageType.objects.filter(decision='149').update(rate_factor=1.00)

    # 3b. جميع أنواع 148: مضاعفة الأسعار + rate_factor = 0.5
    #    بحيث: السعر الفعلي = السعر المخزّن × 0.5
    for ut in UsageType.objects.filter(decision='148'):
        fields_to_double = []
        for f in ['rate_warraq', 'rate_aswan', 'rate_other', 'rate_urban_in', 'rate_urban_out']:
            val = getattr(ut, f)
            if val is not None:
                setattr(ut, f, val * 2)
                fields_to_double.append(f)
        ut.rate_factor = 0.50
        ut.save(update_fields=fields_to_double + ['rate_factor'])


def reverse_migration(apps, schema_editor):
    MinistryDecision = apps.get_model('violations', 'MinistryDecision')
    UsageType = apps.get_model('violations', 'UsageType')

    # حذف القرارات المضافة
    MinistryDecision.objects.filter(
        decision_number__in=['193 لسنة 2024', '148 لسنة 2026 — ترخيص']
    ).delete()

    # إعادة الأسعار إلى حالتها الأصلية
    for ut in UsageType.objects.filter(decision='148'):
        fields_to_half = []
        for f in ['rate_warraq', 'rate_aswan', 'rate_other', 'rate_urban_in', 'rate_urban_out']:
            val = getattr(ut, f)
            if val is not None:
                setattr(ut, f, val / 2)
                fields_to_half.append(f)
        ut.rate_factor = 1.00
        ut.save(update_fields=fields_to_half + ['rate_factor'])


class Migration(migrations.Migration):

    dependencies = [
        ('violations', '0011_update_rates_148_149'),
    ]

    operations = [
        # ── Add rate_factor field ──
        migrations.AddField(
            model_name='usagetype',
            name='rate_factor',
            field=models.DecimalField(decimal_places=2, default=1.0, help_text='1.00 للمخالفة، 0.50 للترخيص (نصف المخالفة)', max_digits=5, verbose_name='معامل السعر'),
        ),
        # ── Add used_decision field ──
        migrations.AddField(
            model_name='violationusage',
            name='used_decision',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='violations.MinistryDecision', verbose_name='القرار الوزاري المُطبَّق'),
        ),
        # ── Data migration ──
        migrations.RunPython(add_decisions_and_update_rates, reverse_migration),
    ]
