import django, os
os.environ['DJANGO_SETTINGS_MODULE']='nile_violations.settings'
django.setup()
from violations.models import ViolationUsage

us = ViolationUsage.objects.all()
for u in us:
    old = u.calculated_value
    u.calculated_value = 0
    u.save()  # يستدعي calculate_value() تلقائياً
    r = u.usage_type.get_rate(u.zone) if u.usage_type else 0
    print(f'ID={u.id}: {u.usage_type.name} ({u.get_basis_display()}) zone={u.zone} rate={r} old={old} new={u.calculated_value}')
