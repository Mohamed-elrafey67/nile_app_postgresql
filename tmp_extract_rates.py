import pandas as pd
import django, os
os.environ['DJANGO_SETTINGS_MODULE']='nile_violations.settings'
django.setup()
from violations.models import UsageType

path = r'C:\Users\Eng.Mohamed El-Rafey\Downloads\جدول_مقابل_الانتفاع_149_2026.xlsx'
df = pd.read_excel(path, sheet_name='القرار 149 - مخالفة', header=None)

def first_val(df, col, start, end):
    for r in range(start, end+1):
        v = df.iloc[r, col]
        if pd.notna(v):
            try:
                return int(float(v))
            except:
                pass
    return None

mapping = {
    1:  ((5,5),   (6,6),   (7,7),   (9,9),   (10,10)),
    2:  ((12,12), (13,13), (14,14), (15,15), (17,17)),
    3:  ((18,18), (18,18), (18,18), (19,19), (19,19)),
    4:  ((20,20), (20,20), (20,20), (22,22), (23,23)),
    5:  ((24,24), (24,24), (24,24), (25,25), (25,25)),
    6:  ((27,27), (28,28), (29,29), (30,30), (32,32)),
    7:  ((35,35), (36,36), (37,37), (37,37), (37,37)),
    8:  ((39,39), (40,40), (41,41), (41,41), (41,41)),
    9:  ((43,44), (43,44), (43,44), (43,44), (43,44)),
    10: ((45,45), (45,45), (45,45), (45,45), (45,45)),
    11: ((46,46), (46,46), (46,46), (46,46), (46,46)),
    12: ((48,48), (48,48), (48,48), (49,49), (50,50)),
    13: ((52,52), (53,53), (54,54), (55,55), (57,57)),
    14: ((59,59), (60,60), (61,61), (62,62), (64,64)),
    15: ((66,66), (66,66), (66,66), (66,66), (66,66)),
    16: ((69,69), (70,70), (71,71), (72,72), (73,73)),
    17: ((69,69), (70,70), (71,71), (72,72), (73,73)),
    18: ((69,69), (70,70), (71,71), (72,72), (73,73)),
    19: ((20,20), (20,20), (20,20), (75,75), (76,76)),
    20: ((77,77), (78,78), (79,79), (80,80), (81,81)),
    21: ((82,82), (82,82), (82,82), (85,85), (85,85)),
    22: ((86,86), (86,86), (86,86), (87,87), (87,87)),
    23: ((88,88), (88,88), (88,88), (89,89), (89,89)),
    24: ((20,20), (20,20), (20,20), (85,85), (85,85)),
    25: ((52,52), (53,53), (54,54), (55,55), (57,57)),
}

new_rates = {}
for uid in sorted(mapping.keys()):
    w_r, a_r, o_r, ui_r, uo_r = mapping[uid]
    w = first_val(df, 2, *w_r)
    a = first_val(df, 3, *a_r)
    o = first_val(df, 4, *o_r)
    ui = first_val(df, 5, *ui_r)
    uo = first_val(df, 6, *uo_r)
    new_rates[uid] = (w, a, o, ui, uo)

print("ID  Activity                       Warraq  Aswan  Other  UrbIn  UrbOut  Change")
print("-" * 75)
changed = []
for uid in sorted(new_rates.keys()):
    t = UsageType.objects.get(id=uid)
    nr = new_rates[uid]
    old = (int(t.rate_warraq) if t.rate_warraq else None,
           int(t.rate_aswan) if t.rate_aswan else None,
           int(t.rate_other) if t.rate_other else None,
           int(t.rate_urban_in) if t.rate_urban_in else None,
           int(t.rate_urban_out) if t.rate_urban_out else None)
    is_changed = nr != old
    if is_changed:
        changed.append((uid, t.name[:28], old, nr))
    w = f"{nr[0]:>5}" if nr[0] else "  _"
    a = f"{nr[1]:>5}" if nr[1] else "  _"
    o = f"{nr[2]:>5}" if nr[2] else "  _"
    ui = f"{nr[3]:>5}" if nr[3] else "  _"
    uo = f"{nr[4]:>5}" if nr[4] else "  _"
    c = "YES" if is_changed else "no"
    print(f"{uid:>2}  {t.name[:28]:<28} {w} {a} {o} {ui} {uo}  {c}")

print(f"\n\n=== CHANGED RATES ({len(changed)} types) ===")
for uid, name, old, new in changed:
    print(f"\n{uid}. {name}")
    print(f"  Warraq:   {old[0]} -> {new[0]}")
    print(f"  Aswan:    {old[1]} -> {new[1]}")
    print(f"  Other:    {old[2]} -> {new[2]}")
    print(f"  UrbanIn:  {old[3]} -> {new[3]}")
    print(f"  UrbanOut: {old[4]} -> {new[4]}")
