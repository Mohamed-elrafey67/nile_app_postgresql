from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User


class Governorate(models.Model):
    pcode    = models.CharField(max_length=10, unique=True, verbose_name='كود المحافظة')
    name_ar  = models.CharField(max_length=100, verbose_name='الاسم عربي')
    name_en  = models.CharField(max_length=100, verbose_name='الاسم إنجليزي')
    has_data = models.BooleanField(default=False, verbose_name='يوجد بيانات')

    class Meta:
        verbose_name        = 'محافظة'
        verbose_name_plural = 'المحافظات'
        ordering            = ['pcode']

    def __str__(self):
        return self.name_ar


class District(models.Model):
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE,
                                    related_name='districts', verbose_name='المحافظة')
    pcode       = models.CharField(max_length=12, unique=True, verbose_name='كود المركز')
    name_ar     = models.CharField(max_length=100, verbose_name='الاسم عربي')
    name_en     = models.CharField(max_length=100, verbose_name='الاسم إنجليزي')

    class Meta:
        verbose_name        = 'مركز'
        verbose_name_plural = 'المراكز الإدارية'
        ordering            = ['governorate', 'name_ar']

    def __str__(self):
        return f"{self.name_ar} — {self.governorate.name_ar}"


class UserProfile(models.Model):
    ROLES = [
        ('viewer',    'مشاهد — عرض البيانات فقط'),
        ('data_entry','مدخل بيانات — إضافة وتعديل'),
        ('supervisor','مشرف — مراجعة وموافقة'),
        ('manager',   'مدير — صلاحيات كاملة'),
    ]
    user       = models.OneToOneField(User, on_delete=models.CASCADE,
                                      related_name='profile', verbose_name='المستخدم')
    role       = models.CharField(max_length=20, choices=ROLES,
                                  default='viewer', verbose_name='الدور')
    governorate = models.ForeignKey(Governorate, on_delete=models.SET_NULL,
                                    null=True, blank=True,
                                    verbose_name='المحافظة المسؤول عنها')
    phone      = models.CharField(max_length=20, blank=True, verbose_name='رقم الهاتف')
    notes      = models.TextField(blank=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'ملف مستخدم'
        verbose_name_plural = 'ملفات المستخدمين'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    def can_add(self):
        return self.role in ('data_entry', 'supervisor', 'manager')

    def can_approve(self):
        return self.role in ('supervisor', 'manager')

    def can_delete(self):
        return self.role == 'manager'


class Violation(models.Model):
    STATUS_CHOICES = [
        ('pending',  'في انتظار الموافقة'),
        ('approved', 'معتمد'),
        ('rejected', 'مرفوض'),
    ]

    # ── الموقع الإداري ──────────────────────────────────────────
    governorate   = models.ForeignKey(Governorate, on_delete=models.SET_NULL,
                                      null=True, blank=True,
                                      related_name='violations', verbose_name='المحافظة')
    district_name = models.CharField(max_length=100, verbose_name='اسم المركز')
    village       = models.CharField(max_length=200, verbose_name='القرية / المدينة')
    village_pcode = models.CharField(max_length=15, blank=True, default='',
                                     verbose_name='كود القرية', db_index=True)

    # ── بيانات السجل ─────────────────────────────────────────────
    code        = models.CharField(max_length=20, verbose_name='الرمز', db_index=True)
    occupant    = models.CharField(max_length=200, verbose_name='اسم المستغل')
    basin       = models.CharField(max_length=300, verbose_name='اسم الحوض')
    description = models.CharField(max_length=500, verbose_name='وصف الاستغلال', db_index=True)

    # ── المساحات ─────────────────────────────────────────────────
    area_outside   = models.FloatField(default=0, verbose_name='المسطح خارج الحياض م²')
    area_public    = models.FloatField(default=0, verbose_name='مساحة على المنفعة العامة م²')
    area_nile_bank = models.FloatField(default=0, verbose_name='مساحة على جسر النهر م²')
    area_total     = models.FloatField(default=0, verbose_name='المسطح الإجمالي م²', db_index=True)

    # ── الإحداثيات ───────────────────────────────────────────────
    latitude  = models.FloatField(verbose_name='خط العرض', default=0)
    longitude = models.FloatField(verbose_name='خط الطول', default=0)
    geo_exact = models.BooleanField(default=False, verbose_name='إحداثيات دقيقة')

    # ── هندسة القطعة (GeoJSON polygon من الشيب فايل) ─────────────
    geometry  = models.JSONField(null=True, blank=True, verbose_name='هندسة القطعة (GeoJSON)')

    # ── الخريطة المساحية الرسمية (PDF) ───────────────────────────
    survey_map = models.FileField(
        upload_to='survey_maps/',
        null=True, blank=True,
        verbose_name='الخريطة المساحية المعتمدة (PDF)'
    )

    # ── الحالة والموافقة ─────────────────────────────────────────
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                    default='approved', verbose_name='الحالة', db_index=True)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='submitted_violations',
                                     verbose_name='أُدخل بواسطة')
    reviewed_by  = models.ForeignKey(User, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='reviewed_violations',
                                     verbose_name='راجعه')
    review_notes = models.TextField(blank=True, verbose_name='ملاحظات المراجعة')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإدخال')
    reviewed_at  = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ المراجعة')

    # ── الصور والملاحظات ─────────────────────────────────────────
    field_notes  = models.TextField(blank=True, verbose_name='ملاحظات ميدانية')
    import_batch = models.CharField(max_length=100, blank=True, default='',
                                    verbose_name='دفعة الاستيراد')

    class Meta:
        verbose_name        = 'قطعة أرض'
        verbose_name_plural = 'أراضي طرح النهر'
        ordering            = ['-submitted_at']
        indexes = [
            models.Index(fields=['governorate', 'district_name']),
            models.Index(fields=['status']),
            models.Index(fields=['village_pcode']),
        ]

    def __str__(self):
        gov = self.governorate.name_ar if self.governorate else '—'
        return f"{self.code} | {self.village} ({self.district_name} – {gov})"


class SatelliteImage(models.Model):
    violation   = models.ForeignKey(Violation, on_delete=models.CASCADE,
                                    null=True, blank=True,
                                    verbose_name='القطعة')
    year        = models.IntegerField(verbose_name='السنة', db_index=True)
    date_acquired = models.DateField(verbose_name='تاريخ الالتقاط')
    image       = models.ImageField(upload_to='satellite/', verbose_name='الصورة')
    cloud_cover = models.FloatField(default=0, verbose_name='الغطاء السحابي')
    bounds_west  = models.FloatField(default=0, verbose_name='حد غرب')
    bounds_south = models.FloatField(default=0, verbose_name='حد جنوب')
    bounds_east  = models.FloatField(default=0, verbose_name='حد شرق')
    bounds_north = models.FloatField(default=0, verbose_name='حد شمال')
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التخزين')

    class Meta:
        verbose_name        = 'صورة قمر صناعي'
        verbose_name_plural = 'صور الأقمار الصناعية'
        ordering            = ['-year', '-date_acquired']
        unique_together     = ['violation', 'year']

    def __str__(self):
        v = self.violation.code if self.violation else '—'
        return f'{v} | {self.year} | {self.date_acquired}'


class ViolationImage(models.Model):
    violation   = models.ForeignKey(Violation, on_delete=models.CASCADE,
                                    related_name='images', verbose_name='قطعة الأرض')
    image       = models.ImageField(upload_to='violations/%Y/%m/', verbose_name='الصورة')
    caption     = models.CharField(max_length=200, blank=True, verbose_name='وصف الصورة')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, verbose_name='رُفعت بواسطة')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'صورة'
        verbose_name_plural = 'صور القطع'

    def __str__(self):
        return f"صورة {self.violation.code}"


class ViolationNote(models.Model):
    violation  = models.ForeignKey(Violation, on_delete=models.CASCADE,
                                   related_name='notes', verbose_name='قطعة الأرض')
    user       = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   null=True, verbose_name='المستخدم')
    text       = models.TextField(verbose_name='نص الملاحظة')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'ملاحظة'
        verbose_name_plural = 'الملاحظات'
        ordering            = ['-created_at']

    def __str__(self):
        return f"ملاحظة على {self.violation.code}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login',    'تسجيل دخول'),
        ('logout',   'تسجيل خروج'),
        ('add',      'إضافة سجل'),
        ('edit',     'تعديل سجل'),
        ('approve',  'موافقة على سجل'),
        ('reject',   'رفض سجل'),
        ('delete',   'حذف سجل'),
        ('export',   'تصدير تقرير'),
        ('import',   'استيراد بيانات'),
        ('login_fail', 'محاولة دخول فاشلة'),
    ]

    user       = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name='المستخدم')
    action     = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='الحدث')
    target     = models.CharField(max_length=200, blank=True, verbose_name='الهدف')
    details    = models.TextField(blank=True, verbose_name='التفاصيل')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='عنوان IP')
    timestamp  = models.DateTimeField(auto_now_add=True, verbose_name='التوقيت', db_index=True)

    class Meta:
        verbose_name        = 'سجل نشاط'
        verbose_name_plural = 'سجل الأنشطة'
        ordering            = ['-timestamp']

    def __str__(self):
        user = self.user.username if self.user else 'غير معروف'
        return f"{self.get_action_display()} — {user} — {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


# ══════════════════════════════════════════════════════════════════
# القرارات الوزارية — جدول الفئات التاريخي
# ══════════════════════════════════════════════════════════════════
class MinistryDecision(models.Model):
    """
    جدول القرارات الوزارية لمقابل الانتفاع.
    يحتوي على كل القرارات من 1987 حتى الآن مع فئاتها السنوية واليومية.
    """
    decision_number = models.CharField(max_length=100, verbose_name='رقم القرار',
                                       help_text='مثال: 14717 لسنة 1987')
    date_from       = models.DateField(verbose_name='تاريخ البداية')
    date_to         = models.DateField(null=True, blank=True, verbose_name='تاريخ النهاية',
                                       help_text='اتركه فارغاً إذا كان سارياً حتى الآن')
    rate_per_year   = models.DecimalField(max_digits=12, decimal_places=4,
                                          verbose_name='الفئة السنوية (جنيه/م²)')
    notes           = models.TextField(blank=True, verbose_name='ملاحظات')
    order           = models.PositiveIntegerField(default=0, verbose_name='الترتيب')

    # أسعار المناطق الخاصة بالقرار (تُستخدم عند الحساب بدلاً من سعر UsageType)
    rate_warraq     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          verbose_name='منطقة الوراق')
    rate_aswan      = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          verbose_name='أسوان - الأقصر - أسيوط - المنصورة')
    rate_other      = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          verbose_name='باقي المحافظات النيلية')
    rate_urban_in   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          verbose_name='داخل الحيز العمراني')
    rate_urban_out  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          verbose_name='خارج الحيز العمراني')

    class Meta:
        verbose_name        = 'قرار وزاري'
        verbose_name_plural = 'القرارات الوزارية'
        ordering            = ['order', 'date_from']

    def __str__(self):
        return self.decision_number

    @property
    def rate_per_day(self):
        return float(self.rate_per_year) / 365.0

    def get_rate(self, zone):
        """إرجاع السعر حسب المنطقة من هذا القرار (إذا مضبوط)، أو None"""
        zone_map = {
            'warraq':    self.rate_warraq,
            'aswan':     self.rate_aswan,
            'other':     self.rate_other,
            'urban_in':  self.rate_urban_in,
            'urban_out': self.rate_urban_out,
        }
        val = zone_map.get(zone)
        return float(val) if val is not None else None


# ══════════════════════════════════════════════════════════════════
# أنواع الاستغلال — من القرار 149 لسنة 2026
# ══════════════════════════════════════════════════════════════════
class UsageType(models.Model):
    """
    أنواع الاستغلال مع الفئات حسب المنطقة الجغرافية (القرار 149).
    كل نوع له سعر مختلف في كل منطقة جغرافية.
    """
    DECISION_CHOICES = [
        ('148', 'القرار 148 لسنة 2026 — ترخيص'),
        ('149', 'القرار 149 لسنة 2026 — مخالفة'),
    ]

    name            = models.CharField(max_length=200, verbose_name='نوع الاستغلال')
    decision        = models.CharField(max_length=10, choices=DECISION_CHOICES,
                                       default='149', verbose_name='القرار')
    article         = models.CharField(max_length=100, blank=True, verbose_name='البند')

    # الفئات حسب المنطقة الجغرافية (جنيه/م²/سنة)
    rate_warraq     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          verbose_name='منطقة الوراق')
    rate_aswan      = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          verbose_name='أسوان-الأقصر-أسيوط-المنصورة')
    rate_other      = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          verbose_name='باقي المحافظات النيلية')
    rate_urban_in   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          verbose_name='داخل الحيز العمراني')
    rate_urban_out  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          verbose_name='خارج الحيز العمراني')

    unit            = models.CharField(max_length=20, default='م²',
                                       verbose_name='وحدة الحساب')
    is_active       = models.BooleanField(default=True, verbose_name='مفعّل')
    order           = models.PositiveIntegerField(default=0, verbose_name='الترتيب')
    rate_factor     = models.DecimalField(max_digits=5, decimal_places=2, default=1.00,
                                          verbose_name='معامل السعر',
                                          help_text='1.00 للمخالفة، 0.50 للترخيص (نصف المخالفة)')

    class Meta:
        verbose_name        = 'نوع استغلال'
        verbose_name_plural = 'أنواع الاستغلال'
        ordering            = ['order', 'name']

    def __str__(self):
        return self.name

    def get_rate(self, zone):
        """إرجاع الفئة حسب المنطقة الجغرافية"""
        zone_map = {
            'warraq':    self.rate_warraq,
            'aswan':     self.rate_aswan,
            'other':     self.rate_other,
            'urban_in':  self.rate_urban_in,
            'urban_out': self.rate_urban_out,
        }
        return float(zone_map.get(zone) or 0)


# ══════════════════════════════════════════════════════════════════
# سجلات الاستغلال — تتبع كل فترة استغلال لكل قطعة
# ══════════════════════════════════════════════════════════════════
class ViolationUsage(models.Model):
    """
    سجل استغلال واحد لقطعة أرض.
    قطعة واحدة يمكن أن تحتوي على عدة سجلات (مستغلون متعاقبون).
    """
    ZONE_CHOICES = [
        ('warraq',   'منطقة الوراق'),
        ('aswan',    'أسوان - الأقصر - أسيوط - المنصورة'),
        ('other',    'باقي المحافظات النيلية'),
        ('urban_in', 'داخل الحيز العمراني'),
        ('urban_out','خارج الحيز العمراني'),
    ]
    STATUS_CHOICES = [
        ('pending',  'في الانتظار'),
        ('approved', 'معتمد'),
        ('rejected', 'مرفوض'),
    ]

    violation       = models.ForeignKey('Violation', on_delete=models.CASCADE,
                                        related_name='usages', verbose_name='قطعة الأرض')
    usage_type      = models.ForeignKey(UsageType, on_delete=models.PROTECT,
                                        null=True, blank=True, verbose_name='نوع الاستغلال')

    # أساس الاستغلال: ترخيص (القرار 148) أو مخالفة (القرار 149)
    basis           = models.CharField(max_length=10, choices=UsageType.DECISION_CHOICES,
                                       default='149', verbose_name='أساس الاستغلال')

    # بيانات المستغل
    occupant_name   = models.CharField(max_length=300, verbose_name='اسم المستغل')
    activity_desc   = models.CharField(max_length=500, blank=True, verbose_name='وصف النشاط')

    # المنطقة والمساحة
    zone            = models.CharField(max_length=20, choices=ZONE_CHOICES,
                                       default='other', verbose_name='المنطقة الجغرافية')
    area            = models.FloatField(verbose_name='المساحة المستغلة (م²)')

    # فترة الاستغلال
    date_from       = models.DateField(verbose_name='تاريخ بداية الاستغلال')
    date_to         = models.DateField(null=True, blank=True,
                                       verbose_name='تاريخ نهاية الاستغلال',
                                       help_text='اتركه فارغاً إذا كان مستمراً')
    is_ongoing      = models.BooleanField(default=False, verbose_name='مستمر حتى الآن')

    # الحساب المالي
    rate_per_year   = models.DecimalField(max_digits=12, decimal_places=4, default=0,
                                          verbose_name='الفئة السنوية (جنيه/م²)')
    calculated_value= models.DecimalField(max_digits=16, decimal_places=2, default=0,
                                          verbose_name='مقابل الانتفاع المحسوب (جنيه)')
    amount_before_2021 = models.DecimalField(
        max_digits=16, decimal_places=2, default=0,
        verbose_name='مقابل انتفاع قبل 17/10/2021 (جنيه)',
        help_text='قيمة مقطوعة للفترة السابقة لتولى الوزارة'
    )
    amount_paid     = models.DecimalField(max_digits=16, decimal_places=2, default=0,
                                          verbose_name='ما تم سداده (جنيه)')

    # الحالة وسير العمل
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                       default='pending', verbose_name='الحالة')
    notes           = models.TextField(blank=True, verbose_name='ملاحظات')

    # القرار الوزاري المُطبَّق
    used_decision   = models.ForeignKey('MinistryDecision', on_delete=models.SET_NULL,
                                        null=True, blank=True, verbose_name='القرار الوزاري المُطبَّق')

    # التتبع
    created_by      = models.ForeignKey(User, on_delete=models.SET_NULL,
                                        null=True, related_name='usages_created',
                                        verbose_name='أُدخل بواسطة')
    approved_by     = models.ForeignKey(User, on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='usages_approved',
                                        verbose_name='اعتمده')
    created_at      = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإدخال')
    updated_at      = models.DateTimeField(auto_now=True, verbose_name='آخر تعديل')

    # استيراد من الملف
    import_source   = models.CharField(max_length=100, blank=True,
                                       verbose_name='مصدر الاستيراد')

    class Meta:
        verbose_name        = 'سجل استغلال'
        verbose_name_plural = 'سجلات الاستغلال'
        ordering            = ['violation', 'date_from']

    def __str__(self):
        return f"{self.violation.code} — {self.occupant_name} — {self.date_from}"

    @property
    def days(self):
        from django.utils import timezone
        end = self.date_to or timezone.now().date()
        return (end - self.date_from).days

    @property
    def remaining(self):
        return float(self.calculated_value) - float(self.amount_paid)

    @property
    def total_amount(self):
        """إجمالي مقابل الانتفاع شامل المستحقات السابقة"""
        return float(self.calculated_value) + float(self.amount_before_2021)

    def calculate_value(self):
        """
        حساب مقابل الانتفاع — أعلى ترتيب قرار أولاً، مع تجنب التكرار.
        """
        if not self.usage_type:
            return 0

        from django.utils import timezone
        end_date = self.date_to or timezone.now().date()
        start = self.date_from
        total = 0.0
        basis = getattr(self, 'basis', None)

        qs = MinistryDecision.objects.filter(
            Q(date_to__isnull=True) | Q(date_to__gt=start)
        ).order_by('-order', '-date_from')

        covered = []
        for dec in qs:
            d_start = dec.date_from
            d_end = dec.date_to or end_date
            dec_num = str(dec.decision_number)
            if basis and ('148 لسنة' in dec_num or '149 لسنة' in dec_num):
                companion_prefix = '149 لسنة' if basis == '148' else '148 لسنة'
                if companion_prefix in dec_num:
                    continue
            eff_start = max(start, d_start)
            eff_end = min(end_date, d_end)
            if eff_start >= eff_end:
                continue
            skip = False
            for cf, ct in covered:
                if eff_start >= cf and eff_end <= ct:
                    skip = True
                    break
            if skip:
                continue
            for cf, ct in covered:
                if eff_start < ct and eff_end > cf:
                    if eff_end > ct:
                        eff_end = ct
            if eff_start >= eff_end:
                continue
            covered.append((eff_start, eff_end))
            days = (eff_end - eff_start).days
            dec_rate = dec.get_rate(self.zone)
            if dec_rate is not None:
                rate = dec_rate
            else:
                rate = self.usage_type.get_rate(self.zone)
                if rate == 0:
                    continue
                rate = rate * float(self.usage_type.rate_factor)
            total += days * (rate / 365.0) * self.area

        return round(total, 2)

    def save(self, *args, **kwargs):
        # تعيين القرار الوزاري المُطبَّق تلقائياً
        if not self.used_decision and self.date_from:
            qs = MinistryDecision.objects.filter(
                date_from__lte=self.date_from
            ).order_by('-date_from')
            if self.basis == '148':
                qs = qs.filter(decision_number__contains='148')
            elif self.basis == '149':
                qs = qs.filter(decision_number__contains='149')
            if not qs.exists():
                # fallback: أي قرار ساري في ذلك التاريخ
                qs = MinistryDecision.objects.filter(
                    date_from__lte=self.date_from
                ).order_by('-date_from')
            self.used_decision = qs.first()

        # حساب تلقائي للقيمة إذا لم تُدخل يدوياً
        if self.calculated_value == 0 and self.area and self.date_from:
            self.calculated_value = self.calculate_value()
        super().save(*args, **kwargs)
