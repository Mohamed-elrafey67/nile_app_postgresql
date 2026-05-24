# منظومة توثيق أراضي طرح النهر 🌊

## متطلبات التشغيل

```bash
pip install django geopandas fiona shapely pyproj openpyxl reportlab
```

## التشغيل لأول مرة

```bash
# خطوة واحدة فقط — تطبيق المهاجرات + إنشاء المستخدمين
python manage.py setup_project

# تشغيل الخادم
python manage.py runserver
```

## بيانات تسجيل الدخول

| الدور       | المستخدم   | كلمة المرور    |
|-------------|------------|----------------|
| مدير النظام | manager    | Manager@123    |
| المشرف      | supervisor | Supervisor@123 |
| مدخل بيانات | data_entry | DataEntry@123  |
| مشاهد       | viewer     | Viewer@123     |

## رفع خريطة محافظة (Shapefile)

1. سجّل دخول بأي دور غير viewer
2. اضغط **"رفع خريطة المحافظة"**
3. اختر المحافظة ثم ارفع ملف `shapefile.zip`
4. راجع ربط الحقول المقترح تلقائياً
5. اضغط **استيراد**

## ملاحظة
`db.sqlite3` مرفق مع البيانات التجريبية والمستخدمين. في حال أردت البدء من الصفر احذفه ثم شغّل `setup_project`.
