import django, os
os.environ['DJANGO_SETTINGS_MODULE']='nile_violations.settings'
django.setup()
from violations.models import UsageType

types = UsageType.objects.filter(decision='149').order_by('id')
print(f"149 types: {types.count()}")
for t in types:
    w = int(t.rate_warraq) if t.rate_warraq else None
    a = int(t.rate_aswan) if t.rate_aswan else None
    o = int(t.rate_other) if t.rate_other else None
    ui = int(t.rate_urban_in) if t.rate_urban_in else None
    uo = int(t.rate_urban_out) if t.rate_urban_out else None
    ws = str(w) if w else "-"
    a_s = str(a) if a else "-"
    os_ = str(o) if o else "-"
    uis = str(ui) if ui else "-"
    uos = str(uo) if uo else "-"
    print(f"  {t.id:>2}. {t.name[:28]:<28} W={ws:>5} A={a_s:>5} O={os_:>5} Ui={uis:>5} Uo={uos:>5}")

types_148 = UsageType.objects.filter(decision='148')
print(f"\n148 types: {types_148.count()}")
