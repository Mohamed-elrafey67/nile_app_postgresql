#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكربت تطبيق تحديثات نظام مقابل الانتفاع
===========================================

هذا السكربت يقوم تلقائياً بـ:
1. نسخ الملفات الأصلية احتياطياً
2. إنشاء/تحديث ملف models.py
3. إنشاء migration جديد
4. إضافة الدوال إلى views.py
5. إضافة المسارات إلى urls.py
6. إنشاء قوالب الطباعة

طريقة الاستخدام:
    python setup_nile_updates.py

ملاحظة: يجب تشغيل هذا السكربت من مجلد المشروع الرئيسي
"""

import os
import sys
import shutil
import re
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════
# الألوان للطباعة
# ═══════════════════════════════════════════════════════════════════════
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"{Colors.HEADER}{Colors.BOLD}{'═' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'═' * 70}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

# ═══════════════════════════════════════════════════════════════════════
# محتويات الملفات
# ═══════════════════════════════════════════════════════════════════════

def get_models_content():
    with open('violations/models.py', 'r', encoding='utf-8') as f:
        return f.read()

def get_migration_content():
    return '''# Generated manually for updating UsageType and ViolationUsage models

from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('violations', '0006_usage_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='usagetype',
            name='price_zone1_license',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='سعر الوراق - ترخيص (ج/م²/سنة)'),
        ),
        migrations.AddField(
            model_name='usagetype',
            name='price_zone2_license',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='سعر أسوان-الأقصر-المنصورة - ترخيص (ج/م²/سنة)'),
        ),
        migrations.AddField(
            model_name='usagetype',
            name='price_zone3_license',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='سعر باقي المحافظات - ترخيص (ج/م²/سنة)'),
        ),
        migrations.AddField(
            model_name='usagetype',
            name='price_zone4_license',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='سعر داخل الحيز العمراني - ترخيص (ج/م²/سنة)'),
        ),
        migrations.AddField(
            model_name='usagetype',
            name='price_zone5_license',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='سعر خارج الحيز العمراني - ترخيص (ج/م²/سنة)'),
        ),
        migrations.AddField(
            model_name='violationusage',
            name='usage_basis',
            field=models.CharField(choices=[('violation', 'مخالفة (القرار 149)'), ('license', 'ترخيص (القرار 148)')], default='violation', max_length=20, verbose_name='أساس الحساب'),
        ),
        migrations.AddField(
            model_name='violationusage',
            name='occupant_address',
            field=models.TextField(blank=True, null=True, verbose_name='عنوان المستغل'),
        ),
        migrations.AddField(
            model_name='violationusage',
            name='amount_before_2021',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='مستحقات قبل 17/10/2021 (جنيه)'),
        ),
        migrations.AddField(
            model_name='violationusage',
            name='notes_before_2021',
            field=models.TextField(blank=True, null=True, verbose_name='ملاحظات المستحقات السابقة'),
        ),
        migrations.AddField(
            model_name='violationusage',
            name='calculation_start_date',
            field=models.DateField(blank=True, null=True, verbose_name='تاريخ بداية الحساب'),
        ),
        migrations.AddField(
            model_name='violationusage',
            name='calculation_end_date',
            field=models.DateField(blank=True, null=True, verbose_name='تاريخ نهاية الحساب'),
        ),
        migrations.AddField(
            model_name='violationusage',
            name='cutoff_date',
            field=models.DateField(default='2021-10-17', verbose_name='تاريخ القطع (17/10/2021)'),
        ),
        migrations.AddField(
            model_name='violationusage',
            name='used_decision',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='violations.ministrydecision', verbose_name='القرار الوزاري المستخدم'),
        ),
    ]
'''

# ═══════════════════════════════════════════════════════════════════════
# دوال المساعدة
# ═══════════════════════════════════════════════════════════════════════

def backup_file(filepath):
    """إنشاء نسخة احتياطية"""
    if os.path.exists(filepath):
        backup_path = filepath + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        shutil.copy2(filepath, backup_path)
        print_success(f"نسخة احتياطية: {backup_path}")
        return True
    return False

def write_file(filepath, content):
    """كتابة الملف"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print_success(f"تم إنشاء: {filepath}")

def append_to_file(filepath, content, marker):
    """إضافة محتوى إلى الملف بعد علامة معينة"""
    with open(filepath, 'r', encoding='utf-8') as f:
        existing = f.read()
    
    if marker in existing:
        print_warning(f"المحتوى موجود بالفعل في {filepath}")
        return
    
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f"\n\n{content}\n")
    print_success(f"تم إضافة محتوى إلى: {filepath}")

# ═══════════════════════════════════════════════════════════════════════
# الخطوات الرئيسية
# ═══════════════════════════════════════════════════════════════════════

def step1_backup():
    print_header("الخطوة 1: إنشاء نسخ احتياطية")
    
    files_to_backup = [
        'violations/models.py',
        'violations/views.py',
        'violations/urls.py',
    ]
    
    for filepath in files_to_backup:
        if backup_file(filepath):
            print_info(f"تم نسخ: {filepath}")
        else:
            print_warning(f"الملف غير موجود: {filepath}")

def step2_update_models():
    print_header("الخطوة 2: تحديث models.py")
    
    # قراءة الملف الحالي
    with open('violations/models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # التحقق من وجود الحقول الجديدة
    if 'price_zone1_license' in content:
        print_warning("الحقول الجديدة موجودة بالفعل!")
        return
    
    # إضافة أسعار الترخيص إلى UsageType
    usage_type_additions = '''
    # أسعار القرار 148 (ترخيص)
    price_zone1_license = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='سعر الوراق - ترخيص (ج/م²/سنة)')
    price_zone2_license = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='سعر أسوان-الأقصر-المنصورة - ترخيص (ج/م²/سنة)')
    price_zone3_license = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='سعر باقي المحافظات - ترخيص (ج/م²/سنة)')
    price_zone4_license = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='سعر داخل الحيز العمراني - ترخيص (ج/م²/سنة)')
    price_zone5_license = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='سعر خارج الحيز العمراني - ترخيص (ج/م²/سنة)')
'''
    
    # إيجاد مكان الإدراج بعد price_zone5_violation
    pattern = r"(price_zone5_violation = models\.DecimalField.*?\n)"
    match = re.search(pattern, content)
    
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + usage_type_additions + content[insert_pos:]
    
    # إضافة دالة get_price المحدثة
    old_get_price = '''    def get_price(self, zone):
        zone_field = f'price_zone{zone}'
        return getattr(self, zone_field, Decimal('0'))'''
    
    new_get_price = '''    def get_price(self, zone, basis='violation'):
        zone_field = f'price_zone{zone}_{basis}'
        return getattr(self, zone_field, Decimal('0'))
    
    def get_price_display(self, zone, basis='violation'):
        price = self.get_price(zone, basis)
        basis_display = 'ترخيص' if basis == 'license' else 'مخالفة'
        return f"{price:,.2f} ج/م²/سنة ({basis_display})"'''
    
    content = content.replace(old_get_price, new_get_price)
    
    # إضافة حقول ViolationUsage الجديدة
    violation_usage_additions = '''
    # أساس الحساب: مخالفة أم ترخيص
    usage_basis = models.CharField(max_length=20, choices=[('violation', 'مخالفة (القرار 149)'), ('license', 'ترخيص (القرار 148)')], default='violation', verbose_name='أساس الحساب')
    
    # ═══════════════════════════════════════════════════════
    # القسم الأول: بيانات المستغل
    # ═══════════════════════════════════════════════════════
    occupant_name = models.CharField(max_length=200, verbose_name='اسم المستغل')
    occupant_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='رقم الهاتف')
    occupant_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='رقم البطاقة/السجل التجاري')
    occupant_address = models.TextField(blank=True, null=True, verbose_name='عنوان المستغل')
    
    # ═══════════════════════════════════════════════════════
    # القسم الثاني: بيانات الاستغلال
    # ═══════════════════════════════════════════════════════
    start_date = models.DateField(verbose_name='تاريخ بداية الاستغلال')
    end_date = models.DateField(blank=True, null=True, verbose_name='تاريخ نهاية الاستغلال')
    is_current = models.BooleanField(default=True, verbose_name='مستمر حتى الآن')
    area_used = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='المساحة المستغلة (م²)')
    zone = models.IntegerField(choices=[(1, 'الوراق'), (2, 'أسوان - الأقصر - المنصورة'), (3, 'باقي المحافظات النيلية'), (4, 'داخل الحيز العمراني'), (5, 'خارج الحيز العمراني')], verbose_name='المنطقة الجغرافية')
    
    # المستحقات قبل 17/10/2021
    amount_before_2021 = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name='مستحقات قبل 17/10/2021 (جنيه)')
    notes_before_2021 = models.TextField(blank=True, null=True, verbose_name='ملاحظات المستحقات السابقة')
    
    # ═══════════════════════════════════════════════════════
    # القسم الثالث: بيانات حساب مقابل الانتفاع
    # ═══════════════════════════════════════════════════════
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='سعر المتر/سنة (جنيه)')
    duration_years = models.DecimalField(max_digits=8, decimal_places=4, verbose_name='مدة الاستغلال المحسوبة (سنة)')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='القيمة الإجمالية المحسوبة (جنيه)')
    
    # تفاصيل الفترات الحسابية
    calculation_start_date = models.DateField(verbose_name='تاريخ بداية الحساب')
    calculation_end_date = models.DateField(verbose_name='تاريخ نهاية الحساب')
    cutoff_date = models.DateField(default=date(2021, 10, 17), verbose_name='تاريخ القطع (17/10/2021)')
    used_decision = models.ForeignKey(MinistryDecision, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='القرار الوزاري المستخدم')
'''
    
    # حفظ الملف المحدث
    with open('violations/models.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success("تم تحديث models.py")

def step3_create_migration():
    print_header("الخطوة 3: إنشاء Migration جديد")
    
    migration_path = 'violations/migrations/0007_update_usage_models.py'
    
    if os.path.exists(migration_path):
        print_warning("Migration موجود بالفعل!")
        return
    
    write_file(migration_path, get_migration_content())
    print_success("تم إنشاء Migration")

def step4_update_views():
    print_header("الخطوة 4: تحديث views.py")
    
    views_additions = '''
# ═══════════════════════════════════════════════════════════════════════
# دوال API لسجلات الاستغلال (مقابل الانتفاع) - الإصدار 2.0
# ═══════════════════════════════════════════════════════════════════════

import json
from decimal import Decimal
from datetime import date, datetime
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Violation, ViolationUsage, UsageType, MinistryDecision


@login_required
def usage_list_api(request, violation_id):
    """API: عرض سجلات الاستغلال لقطعة معينة"""
    try:
        violation = get_object_or_404(Violation, id=violation_id)
        usages = ViolationUsage.objects.filter(violation=violation).select_related('usage_type', 'approved_by')
        
        usages_data = []
        total_calculated = Decimal('0.00')
        total_before_2021 = Decimal('0.00')
        total_full = Decimal('0.00')
        
        for usage in usages:
            calc_details = usage.get_calculation_details()
            usages_data.append({
                'id': usage.id,
                'occupant_name': usage.occupant_name,
                'occupant_phone': usage.occupant_phone,
                'usage_type': usage.usage_type.name,
                'usage_basis': usage.usage_basis,
                'usage_basis_display': 'ترخيص' if usage.usage_basis == 'license' else 'مخالفة',
                'start_date': usage.start_date.strftime('%Y/%m/%d'),
                'end_date': usage.end_date.strftime('%Y/%m/%d') if usage.end_date else 'مستمر',
                'area_used': float(usage.area_used),
                'zone': usage.get_zone_display(),
                'status': usage.status,
                'status_display': usage.get_status_display(),
                'unit_price': float(usage.unit_price),
                'duration_years': float(usage.duration_years),
                'total_amount': float(usage.total_amount),
                'amount_before_2021': float(usage.amount_before_2021),
                'full_amount': float(usage.get_full_amount()),
                'calculation_details': {
                    'formula': calc_details['formula'],
                    'calculation_start': str(calc_details['calculation_start']),
                    'calculation_end': str(calc_details['calculation_end']),
                    'cutoff_date': str(calc_details['cutoff_date']),
                },
                'approved_by': usage.approved_by.get_full_name() if usage.approved_by else None,
                'approved_at': usage.approved_at.strftime('%Y/%m/%d %H:%M') if usage.approved_at else None,
                'notes': usage.notes,
            })
            
            if usage.status == 'approved':
                total_calculated += usage.total_amount
                total_before_2021 += usage.amount_before_2021
                total_full += usage.get_full_amount()
        
        return JsonResponse({
            'success': True,
            'violation': {
                'id': violation.id,
                'code': violation.code,
                'total_area': float(violation.total_area),
                'used_area': float(violation.used_area),
                'remaining_area': float(violation.remaining_area),
            },
            'usages': usages_data,
            'summary': {
                'count': len(usages_data),
                'total_calculated': float(total_calculated),
                'total_before_2021': float(total_before_2021),
                'total_full_amount': float(total_full),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def usage_calculate_preview(request):
    """API: حساب مبدئي لقيمة الاستغلال"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        usage_type_id = data.get('usage_type_id')
        zone = int(data.get('zone', 3))
        area = Decimal(str(data.get('area', 0)))
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        usage_basis = data.get('usage_basis', 'violation')
        amount_before_2021 = Decimal(str(data.get('amount_before_2021', 0)))
        violation_id = data.get('violation_id')
        
        if not usage_type_id or area <= 0:
            return JsonResponse({'success': False, 'error': 'بيانات غير كاملة'}, status=400)
        
        # التحقق من المساحة المتاحة
        if violation_id:
            violation = get_object_or_404(Violation, id=violation_id)
            other_usages = ViolationUsage.objects.filter(violation=violation, status='approved', is_current=True)
            total_used = sum([u.area_used for u in other_usages])
            available_area = violation.total_area - total_used
            
            if area > available_area:
                return JsonResponse({
                    'success': False,
                    'error': f'المساحة المطلوبة ({area} م²) تتجاوز المساحة المتاحة ({available_area} م²)',
                    'available_area': float(available_area),
                }, status=400)
        
        usage_type = get_object_or_404(UsageType, id=usage_type_id, is_active=True)
        unit_price = usage_type.get_price(zone, usage_basis)
        
        start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
        
        cutoff_date = date(2021, 10, 17)
        calc_start = max(start, cutoff_date)
        
        if calc_start >= end:
            duration = Decimal('0.00')
        else:
            delta = end - calc_start
            duration = Decimal(str(round(delta.days / 365.25, 4)))
        
        total = unit_price * area * duration
        
        decision = MinistryDecision.objects.filter(
            decision_number='149' if usage_basis == 'violation' else '148', is_active=True
        ).first()
        
        return JsonResponse({
            'success': True,
            'calculation': {
                'usage_basis': usage_basis,
                'basis_display': 'ترخيص (القرار 148)' if usage_basis == 'license' else 'مخالفة (القرار 149)',
                'unit_price': float(unit_price),
                'area': float(area),
                'duration_years': float(duration),
                'calculation_start': str(calc_start),
                'calculation_end': str(end),
                'cutoff_date': str(cutoff_date),
                'formula': f'{unit_price} × {area} م² × {duration} سنة',
                'total_amount': float(total),
                'amount_before_2021': float(amount_before_2021),
                'full_amount': float(total + amount_before_2021),
                'used_decision': {
                    'number': decision.decision_number if decision else None,
                    'year': decision.decision_year if decision else None,
                    'title': decision.title if decision else None,
                } if decision else None,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def usage_add_api(request):
    """API: إضافة سجل استغلال جديد"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        violation_id = data.get('violation_id')
        violation = get_object_or_404(Violation, id=violation_id)
        
        area_used = Decimal(str(data.get('area_used', 0)))
        other_usages = ViolationUsage.objects.filter(violation=violation, status='approved', is_current=True)
        total_used = sum([u.area_used for u in other_usages])
        available_area = violation.total_area - total_used
        
        if area_used > available_area:
            return JsonResponse({
                'success': False,
                'error': f'المساحة المطلوبة ({area_used} م²) تتجاوز المساحة المتاحة ({available_area} م²)',
            }, status=400)
        
        usage_type_id = data.get('usage_type_id')
        usage_type = get_object_or_404(UsageType, id=usage_type_id, is_active=True)
        
        usage_basis = data.get('usage_basis', 'violation')
        zone = int(data.get('zone', 3))
        
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else None
        
        amount_before_2021 = Decimal(str(data.get('amount_before_2021', 0)))
        notes_before_2021 = data.get('notes_before_2021', '')
        
        unit_price = usage_type.get_price(zone, usage_basis)
        
        usage = ViolationUsage.objects.create(
            violation=violation,
            usage_type=usage_type,
            usage_basis=usage_basis,
            occupant_name=data.get('occupant_name', ''),
            occupant_phone=data.get('occupant_phone', ''),
            occupant_id=data.get('occupant_id', ''),
            occupant_address=data.get('occupant_address', ''),
            start_date=start_date,
            end_date=end_date,
            is_current=data.get('is_current', True),
            area_used=area_used,
            zone=zone,
            amount_before_2021=amount_before_2021,
            notes_before_2021=notes_before_2021,
            unit_price=unit_price,
            created_by=request.user,
        )
        
        usage.calculate_amount()
        usage.save()
        
        return JsonResponse({
            'success': True,
            'message': 'تم إضافة سجل الاستغلال بنجاح',
            'usage_id': usage.id,
            'calculation': usage.get_calculation_details(),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def usage_approve_api(request, usage_id):
    """API: موافقة/رفض سجل استغلال"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        usage = get_object_or_404(ViolationUsage, id=usage_id)
        
        if not request.user.groups.filter(name__in=['manager', 'supervisor']).exists():
            return JsonResponse({'error': 'ليس لديك صلاحية'}, status=403)
        
        data = json.loads(request.body)
        action = data.get('action')
        reason = data.get('reason', '')
        
        if action == 'approve':
            usage.status = 'approved'
            usage.approved_by = request.user
            usage.approved_at = timezone.now()
            usage.rejection_reason = ''
            message = 'تم اعتماد سجل الاستغلال'
        elif action == 'reject':
            usage.status = 'rejected'
            usage.rejection_reason = reason
            message = 'تم رفض سجل الاستغلال'
        else:
            return JsonResponse({'error': 'إجراء غير صحيح'}, status=400)
        
        usage.save()
        usage.violation.update_used_area()
        
        return JsonResponse({'success': True, 'message': message, 'usage_id': usage.id, 'status': usage.status})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def usage_delete_api(request, usage_id):
    """API: حذف سجل استغلال"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        usage = get_object_or_404(ViolationUsage, id=usage_id)
        violation = usage.violation
        
        if not request.user.groups.filter(name__in=['manager', 'supervisor']).exists() and usage.created_by != request.user:
            return JsonResponse({'error': 'ليس لديك صلاحية'}, status=403)
        
        usage.delete()
        violation.update_used_area()
        
        return JsonResponse({'success': True, 'message': 'تم حذف سجل الاستغلال'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def usage_types_api(request):
    """API: قائمة أنواع الاستغلال"""
    try:
        basis = request.GET.get('basis', 'violation')
        zone = request.GET.get('zone')
        types = UsageType.objects.filter(is_active=True)
        
        types_data = []
        for ut in types:
            type_data = {'id': ut.id, 'name': ut.name, 'category': ut.category, 'category_display': ut.get_category_display()}
            if zone:
                zone = int(zone)
                type_data['price'] = float(ut.get_price(zone, basis))
                type_data['price_display'] = ut.get_price_display(zone, basis)
            types_data.append(type_data)
        
        return JsonResponse({'success': True, 'types': types_data, 'basis': basis})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def usage_print_single(request, usage_id):
    """طباعة سجل استغلال واحد"""
    try:
        usage = get_object_or_404(ViolationUsage, id=usage_id)
        calc = usage.get_calculation_details()
        context = {'usage': usage, 'calculation': calc, 'violation': usage.violation, 'print_date': timezone.now()}
        return render(request, 'violations/usage_print_single.html', context)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def usage_print_all(request, violation_id):
    """طباعة جميع سجلات استغلال قطعة"""
    try:
        violation = get_object_or_404(Violation, id=violation_id)
        usages = ViolationUsage.objects.filter(violation=violation).select_related('usage_type')
        
        total_calculated = sum([u.total_amount for u in usages if u.status == 'approved'])
        total_before_2021 = sum([u.amount_before_2021 for u in usages if u.status == 'approved'])
        total_full = sum([u.get_full_amount() for u in usages if u.status == 'approved'])
        
        context = {
            'violation': violation,
            'usages': usages,
            'summary': {
                'count': len(usages),
                'total_calculated': total_calculated,
                'total_before_2021': total_before_2021,
                'total_full_amount': total_full,
            },
            'print_date': timezone.now(),
        }
        return render(request, 'violations/usage_print_all.html', context)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
'''
    
    append_to_file('violations/views.py', views_additions, 'def usage_print_all')

def step5_update_urls():
    print_header("الخطوة 5: تحديث urls.py")
    
    urls_additions = '''
    # ═══════════════════════════════════════════════════════════════════════
    # APIs لسجلات الاستغلال (مقابل الانتفاع)
    # ═══════════════════════════════════════════════════════════════════════
    path('api/usage/list/<int:violation_id>/', views.usage_list_api, name='usage_list_api'),
    path('api/usage/calculate-preview/', views.usage_calculate_preview, name='usage_calculate_preview'),
    path('api/usage/add/', views.usage_add_api, name='usage_add_api'),
    path('api/usage/approve/<int:usage_id>/', views.usage_approve_api, name='usage_approve_api'),
    path('api/usage/delete/<int:usage_id>/', views.usage_delete_api, name='usage_delete_api'),
    path('api/usage/types/', views.usage_types_api, name='usage_types_api'),
    
    # ═══════════════════════════════════════════════════════════════════════
    # طباعة سجلات الاستغلال
    # ═══════════════════════════════════════════════════════════════════════
    path('usage/print/<int:usage_id>/', views.usage_print_single, name='usage_print_single'),
    path('usage/print-all/<int:violation_id>/', views.usage_print_all, name='usage_print_all'),
'''
    
    append_to_file('violations/urls.py', urls_additions, 'usage_print_all')

def step6_create_templates():
    print_header("الخطوة 6: إنشاء قوالب الطباعة")
    
    templates_dir = 'violations/templates/violations'
    os.makedirs(templates_dir, exist_ok=True)
    
    # قالب طباعة سجل واحد
    single_template = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>سجل استغلال - {{ usage.violation.code }}</title>
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: 'Arial', sans-serif; font-size: 12pt; line-height: 1.6; }
        .header { text-align: center; border-bottom: 3px double #333; padding-bottom: 15px; margin-bottom: 20px; }
        .header h1 { font-size: 18pt; margin: 0; color: #1a5276; }
        .header h2 { font-size: 14pt; margin: 5px 0; color: #2874a6; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }
        .section-title { font-size: 14pt; font-weight: bold; color: #1a5276; border-bottom: 2px solid #2874a6; padding-bottom: 8px; margin-bottom: 15px; }
        .row { display: flex; justify-content: space-between; margin: 8px 0; }
        .label { font-weight: bold; color: #555; }
        .value { color: #333; }
        .highlight { background: #eaf2f8; padding: 10px; border-radius: 5px; }
        .calc-box { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .calc-formula { font-family: 'Courier New', monospace; font-size: 11pt; color: #27ae60; text-align: center; margin: 10px 0; }
        .total-box { background: #d5f5e3; padding: 15px; border-radius: 8px; text-align: center; margin-top: 20px; }
        .total-amount { font-size: 18pt; font-weight: bold; color: #27ae60; }
        .footer { margin-top: 40px; text-align: center; font-size: 10pt; color: #777; border-top: 1px solid #ddd; padding-top: 15px; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 10pt; }
        .badge-violation { background: #f5b7b1; color: #922b21; }
        .badge-license { background: #abebc6; color: #1e8449; }
        .badge-approved { background: #abebc6; color: #1e8449; }
        .badge-pending { background: #f9e79f; color: #9a7d0a; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 10px; text-align: right; border: 1px solid #ddd; }
        th { background: #eaf2f8; font-weight: bold; }
        .signature-area { margin-top: 60px; display: flex; justify-content: space-between; }
        .signature-box { width: 40%; text-align: center; }
        .signature-line { border-top: 1px solid #333; margin-top: 50px; padding-top: 10px; }
        @media print {
            .no-print { display: none; }
            body { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
        }
    </style>
</head>
<body>
    <div class="no-print" style="text-align: center; margin: 20px;">
        <button onclick="window.print()" style="padding: 12px 30px; font-size: 14pt; background: #2874a6; color: white; border: none; border-radius: 8px; cursor: pointer;">
            🖨️ طباعة
        </button>
    </div>

    <div class="header">
        <h1>نظام توثيق أراضي طرح النهر</h1>
        <h2>سجل استغلال قطعة أرض</h2>
        <p>تم الطباعة: {{ print_date|date:"Y/m/d H:i" }}</p>
    </div>

    <div class="section">
        <div class="section-title">📍 بيانات قطعة الأرض</div>
        <div class="row"><span class="label">كود القطعة:</span><span class="value">{{ usage.violation.code }}</span></div>
        <div class="row"><span class="label">المحافظة:</span><span class="value">{{ usage.violation.governorate.name }}</span></div>
        <div class="row"><span class="label">المركز:</span><span class="value">{{ usage.violation.markaz.name }}</span></div>
        <div class="row"><span class="label">القرية:</span><span class="value">{{ usage.violation.village.name }}</span></div>
        <div class="row"><span class="label">المساحة الإجمالية:</span><span class="value">{{ usage.violation.total_area|floatformat:2 }} م²</span></div>
    </div>

    <div class="section">
        <div class="section-title">👤 بيانات المستغل</div>
        <div class="row"><span class="label">الاسم:</span><span class="value">{{ usage.occupant_name }}</span></div>
        <div class="row"><span class="label">رقم الهاتف:</span><span class="value">{{ usage.occupant_phone|default:"-" }}</span></div>
        <div class="row"><span class="label">رقم البطاقة/السجل:</span><span class="value">{{ usage.occupant_id|default:"-" }}</span></div>
        <div class="row"><span class="label">العنوان:</span><span class="value">{{ usage.occupant_address|default:"-" }}</span></div>
    </div>

    <div class="section">
        <div class="section-title">📋 بيانات الاستغلال</div>
        <div class="row"><span class="label">نوع الاستغلال:</span><span class="value">{{ usage.usage_type.name }}</span></div>
        <div class="row"><span class="label">أساس الحساب:</span><span class="value">{% if usage.usage_basis == 'license' %}<<span class="badge badge-license">ترخيص (القرار 148)</span>{% else %}<<span class="badge badge-violation">مخالفة (القرار 149)</span>{% endif %}</span></div>
        <div class="row"><span class="label">المنطقة الجغرافية:</span><span class="value">{{ usage.get_zone_display }}</span></div>
        <div class="row"><span class="label">تاريخ البداية:</span><span class="value">{{ usage.start_date|date:"Y/m/d" }}</span></div>
        <div class="row"><span class="label">تاريخ النهاية:</span><span class="value">{% if usage.end_date %}{{ usage.end_date|date:"Y/m/d" }}{% else %}مستمر حتى الآن{% endif %}</span></div>
        <div class="row"><span class="label">المساحة المستغلة:</span><span class="value">{{ usage.area_used|floatformat:2 }} م²</span></div>
        <div class="row"><span class="label">الحالة:</span><span class="value">{% if usage.status == 'approved' %}<<span class="badge badge-approved">معتمد</span>{% else %}<<span class="badge badge-pending">{{ usage.get_status_display }}</span>{% endif %}</span></div>
    </div>

    <div class="section highlight">
        <div class="section-title">🧮 بيانات حساب مقابل الانتفاع</div>
        <table>
            <tr><th colspan="2">تفاصيل الفترة الحسابية</th></tr>
            <tr><td>تاريخ القطع (بداية المحاسبة)</td><td>{{ usage.cutoff_date|date:"Y/m/d" }}</td></tr>
            <tr><td>بداية الاستغلال الفعلي</td><td>{{ usage.start_date|date:"Y/m/d" }}</td></tr>
            <tr><td>بداية الحساب</td><td>{{ usage.calculation_start_date|date:"Y/m/d" }}</td></tr>
            <tr><td>نهاية الحساب</td><td>{{ usage.calculation_end_date|date:"Y/m/d" }}</td></tr>
            <tr><td>مدة الحساب</td><td>{{ usage.duration_years|floatformat:4 }} سنة</td></tr>
        </table>

        <div class="calc-box">
            <div class="calc-formula">{{ calculation.formula }}</div>
            <div style="text-align: center; color: #666;">= {{ usage.unit_price|floatformat:2 }} × {{ usage.area_used|floatformat:2 }} × {{ usage.duration_years|floatformat:4 }}</div>
        </div>

        <table>
            <tr><th>البيان</th><th>القيمة</th></tr>
            <tr><td>سعر المتر/سنة</td><td>{{ usage.unit_price|floatformat:2 }} جنيه</td></tr>
            <tr><td>المساحة المستغلة</td><td>{{ usage.area_used|floatformat:2 }} م²</td></tr>
            <tr><td>مدة الاستغلال المحسوبة</td><td>{{ usage.duration_years|floatformat:4 }} سنة</td></tr>
            <tr style="background: #eaf2f8;"><td><strong>المبلغ المحسوب (من 17/10/2021)</strong></td><td><strong>{{ usage.total_amount|floatformat:2 }} جنيه</strong></td></tr>
            {% if usage.amount_before_2021 > 0 %}
            <tr style="background: #fef9e7;"><td>مستحقات قبل 17/10/2021</td><td>{{ usage.amount_before_2021|floatformat:2 }} جنيه</td></tr>
            {% endif %}
        </table>

        <div class="total-box">
            <div>الإجمالي الكلي</div>
            <div class="total-amount">{{ usage.get_full_amount|floatformat:2 }} جنيه مصري</div>
            {% if usage.amount_before_2021 > 0 %}
            <div style="font-size: 10pt; color: #666; margin-top: 10px;">(شامل مستحقات قبل 17/10/2021 بقيمة {{ usage.amount_before_2021|floatformat:2 }} جنيه)</div>
            {% endif %}
        </div>
    </div>

    <div class="signature-area">
        <div class="signature-box"><div class="signature-line">توقيع المستغل</div></div>
        <div class="signature-box"><div class="signature-line">توقيع المسؤول</div></div>
    </div>

    <div class="footer">
        <p>هذا التقرير صادر من نظام توثيق أراضي طرح النهر</p>
        <p>وزارة الموارد المائية والري - الهيئة العامة للمساحة</p>
    </div>
</body>
</html>'''
    
    write_file(f'{templates_dir}/usage_print_single.html', single_template)
    
    # قالب طباعة جميع السجلات
    all_template = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تقرير سجلات الاستغلال - {{ violation.code }}</title>
    <style>
        @page { size: A4 landscape; margin: 1.5cm; }
        body { font-family: 'Arial', sans-serif; font-size: 10pt; line-height: 1.4; }
        .header { text-align: center; border-bottom: 3px double #333; padding-bottom: 10px; margin-bottom: 15px; }
        .header h1 { font-size: 16pt; margin: 0; color: #1a5276; }
        .header h2 { font-size: 12pt; margin: 5px 0; color: #2874a6; }
        .summary-box { background: #eaf2f8; padding: 15px; border-radius: 8px; margin: 15px 0; }
        .summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; text-align: center; }
        .summary-item { background: white; padding: 10px; border-radius: 5px; }
        .summary-label { font-size: 9pt; color: #666; }
        .summary-value { font-size: 14pt; font-weight: bold; color: #1a5276; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 9pt; }
        th, td { padding: 8px; text-align: center; border: 1px solid #ddd; }
        th { background: #2874a6; color: white; font-weight: bold; }
        tr:nth-child(even) { background: #f8f9fa; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 8pt; }
        .badge-violation { background: #f5b7b1; color: #922b21; }
        .badge-license { background: #abebc6; color: #1e8449; }
        .badge-approved { background: #abebc6; color: #1e8449; }
        .badge-pending { background: #f9e79f; color: #9a7d0a; }
        .total-row { background: #d5f5e3 !important; font-weight: bold; }
        .footer { margin-top: 30px; text-align: center; font-size: 9pt; color: #777; border-top: 1px solid #ddd; padding-top: 10px; }
        @media print {
            .no-print { display: none; }
            body { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
        }
    </style>
</head>
<body>
    <div class="no-print" style="text-align: center; margin: 20px;">
        <button onclick="window.print()" style="padding: 10px 25px; font-size: 12pt; background: #2874a6; color: white; border: none; border-radius: 8px; cursor: pointer;">🖨️ طباعة التقرير</button>
    </div>

    <div class="header">
        <h1>نظام توثيق أراضي طرح النهر</h1>
        <h2>تقرير سجلات استغلال قطعة الأرض</h2>
        <p>كود القطعة: <strong>{{ violation.code }}</strong> | المحافظة: {{ violation.governorate.name }} | المركز: {{ violation.markaz.name }} | القرية: {{ violation.village.name }}</p>
        <p>تم الطباعة: {{ print_date|date:"Y/m/d H:i" }}</p>
    </div>

    <div class="summary-box">
        <div class="summary-grid">
            <div class="summary-item"><div class="summary-label">المساحة الإجمالية</div><div class="summary-value">{{ violation.total_area|floatformat:2 }} م²</div></div>
            <div class="summary-item"><div class="summary-label">عدد سجلات الاستغلال</div><div class="summary-value">{{ summary.count }}</div></div>
            <div class="summary-item"><div class="summary-label">المساحة المستغلة</div><div class="summary-value">{{ violation.used_area|floatformat:2 }} م²</div></div>
            <div class="summary-item"><div class="summary-label">المساحة المتبقية</div><div class="summary-value">{{ violation.remaining_area|floatformat:2 }} م²</div></div>
        </div>
    </div>

    <table>
        <thead>
            <tr><th>#</th><th>المستغل</th><th>نوع الاستغلال</th><th>الأساس</th><th>المنطقة</th><th>المساحة (م²)</th><th>المدة (سنة)</th><th>السعر (ج/م²)</th><th>المحسوب</th><th>قبل 2021</th><th>الإجمالي</th><th>الحالة</th></tr>
        </thead>
        <tbody>
            {% for usage in usages %}
            <tr>
                <td>{{ forloop.counter }}</td>
                <td>{{ usage.occupant_name }}</td>
                <td>{{ usage.usage_type.name }}</td>
                <td>{% if usage.usage_basis == 'license' %}<<span class="badge badge-license">ترخيص</span>{% else %}<<span class="badge badge-violation">مخالفة</span>{% endif %}</td>
                <td>{{ usage.get_zone_display }}</td>
                <td>{{ usage.area_used|floatformat:2 }}</td>
                <td>{{ usage.duration_years|floatformat:2 }}</td>
                <td>{{ usage.unit_price|floatformat:2 }}</td>
                <td>{{ usage.total_amount|floatformat:2 }}</td>
                <td>{{ usage.amount_before_2021|floatformat:2 }}</td>
                <td><strong>{{ usage.get_full_amount|floatformat:2 }}</strong></td>
                <td>{% if usage.status == 'approved' %}<<span class="badge badge-approved">معتمد</span>{% else %}<<span class="badge badge-pending">{{ usage.get_status_display }}</span>{% endif %}</td>
            </tr>
            {% empty %}
            <tr><td colspan="12" style="text-align: center; padding: 20px;">لا توجد سجلات استغلال</td></tr>
            {% endfor %}
        </tbody>
        <tfoot>
            <tr class="total-row">
                <td colspan="8" style="text-align: left;"><strong>الإجمالي:</strong></td>
                <td><strong>{{ summary.total_calculated|floatformat:2 }}</strong></td>
                <td><strong>{{ summary.total_before_2021|floatformat:2 }}</strong></td>
                <td colspan="2"><strong>{{ summary.total_full_amount|floatformat:2 }} جنيه</strong></td>
            </tr>
        </tfoot>
    </table>

    <div class="footer">
        <p>تقرير سجلات استغلال قطعة الأرض {{ violation.code }}</p>
        <p>نظام توثيق أراضي طرح النهر | وزارة الموارد المائية والري</p>
    </div>
</body>
</html>'''
    
    write_file(f'{templates_dir}/usage_print_all.html', all_template)

def step7_run_migrations():
    print_header("الخطوة 7: تشغيل Migrations")
    
    print_info("تشغيل: python manage.py makemigrations")
    os.system('python manage.py makemigrations')
    
    print_info("تشغيل: python manage.py migrate")
    os.system('python manage.py migrate')
    
    print_success("تم تطبيق Migrations")

def main():
    print_header("نظام توثيق أراضي طرح النهر - تحديث مقابل الانتفاع v2.0")
    
    # التحقق من المجلد
    if not os.path.exists('manage.py'):
        print_error("يجب تشغيل هذا السكربت من مجلد المشروع الرئيسي!")
        sys.exit(1)
    
    print_info("بدء التحديثات...")
    
    step1_backup()
    step2_update_models()
    step3_create_migration()
    step4_update_views()
    step5_update_urls()
    step6_create_templates()
    step7_run_migrations()
    
    print_header("✅ تم الانتهاء بنجاح!")
    print_info("الخطوات التالية:")
    print("  1. python manage.py runserver")
    print("  2. قم بتحديث أسعار UsageType في لوحة الإدارة")
    print("  3. اختبر APIs جديدة")

if __name__ == '__main__':
    main()