import re
from dataclasses import dataclass, field
from typing import Optional


ZONE_MAP = {
    'الوراق':     'warraq',
    'وراق':       'warraq',
    'أسوان':      'aswan',
    'اسوان':      'aswan',
    'الأقصر':     'aswan',
    'اقصر':       'aswan',
    'أسيوط':      'aswan',
    'اسيوط':      'aswan',
    'المنصورة':   'aswan',
    'منصورة':     'aswan',
    'باقي المحافظات': 'other',
    'المحافظات النيلية': 'other',
    'النيلية':    'other',
    'داخل الحيز العمراني': 'urban_in',
    'الحيز العمراني': 'urban_in',
    'عمراني':     'urban_in',
    'خارج الحيز العمراني': 'urban_out',
    'خارج العمراني': 'urban_out',
}

DECISION_MAP = {
    'ترخيص':  '148',
    'مرخص':   '148',
    'مخالفة': '149',
    'مخالف':  '149',
}

STATUS_MAP = {
    'في انتظار الموافقة': 'pending',
    'في الانتظار':   'pending',
    'بانتظار':       'pending',
    'بانتظار الموافقة': 'pending',
    'انتظار':        'pending',
    'pending':       'pending',
    'معتمد':         'approved',
    'تمت الموافقة':  'approved',
    'موافقة':        'approved',
    'approved':      'approved',
    'مرفوض':         'rejected',
    'مرفوضة':        'rejected',
    ' rejected':     'rejected',
}

GOV_MAP = {
    'القاهرة':       'Cairo',
    'الجيزة':        'Giza',
    'جيزة':          'Giza',
    'الإسكندرية':    'Alexandria',
    'اسكندرية':      'Alexandria',
    'الدقهلية':      'Dakahlia',
    'الشرقية':       'Sharqia',
    'القليوبية':     'Qalyubia',
    'كفر الشيخ':     'Kafr El Sheikh',
    'الغربية':       'Gharbia',
    'المنوفية':      'Monufia',
    'البحيرة':       'Beheira',
    'دمياط':         'Damietta',
    'بورسعيد':       'Port Said',
    'الإسماعيلية':   'Ismailia',
    'السويس':        'Suez',
    'شمال سيناء':    'North Sinai',
    'جنوب سيناء':    'South Sinai',
    'بني سويف':      'Beni Suef',
    'الفيوم':        'Fayoum',
    'المنيا':        'Minya',
    'أسيوط':         'Assiut',
    'سوهاج':         'Sohag',
    'قنا':           'Qena',
    'الأقصر':        'Luxor',
    'أسوان':         'Aswan',
    'البحر الأحمر':  'Red Sea',
    'الوادي الجديد': 'New Valley',
    'مطروح':         'Matrouh',
}


COMPARISON_PATTERNS = [
    (r'أكثر من (\d[\d,.]*)',   'gt'),
    (r'اكتر من (\d[\d,.]*)',   'gt'),
    (r'أكبر من (\d[\d,.]*)',   'gt'),
    (r'اكبر من (\d[\d,.]*)',   'gt'),
    (r'أقل من (\d[\d,.]*)',    'lt'),
    (r'اقل من (\d[\d,.]*)',    'lt'),
    (r'أصغر من (\d[\d,.]*)',   'lt'),
    (r'اصغر من (\d[\d,.]*)',   'lt'),
    (r'يساوي (\d[\d,.]*)',     'eq'),
    (r'تساوي (\d[\d,.]*)',     'eq'),
    (r'= (\d[\d,.]*)',         'eq'),
]

INTENT_KEYWORDS = {
    'كم':        'count',
    'عدد':       'count',
    'كام':       'count',
    'إجمالي':    'sum',
    'اجمالي':    'sum',
    'مجموع':     'sum',
    'متوسط':     'avg',
    'معدل':      'avg',
    'تفاصيل':    'detail',
    'بيانات':    'detail',
    'معلومات':   'detail',
    'وريني':     'list',
    'عرض':       'list',
    'أظهر':      'list',
    'اظهر':      'list',
    'جيب':       'list',
}

OBJECT_KEYWORDS = {
    'مخالفة':   'violation',
    'مخالفات':  'violation',
    'تواجد':     'violation',
    'تواجدات':  'violation',
    'قطعة':     'violation',
    'قطع':      'violation',
    'أرض':      'violation',
    'اراض':     'violation',
    'أراضي':    'violation',
    'استغلال':    'usage',
    'استغلالات':  'usage',
    'مقابل الانتفاع': 'usage_value',
    'مقابل انتفاع': 'usage_value',
    'قيمة':     'usage_value',
    'مبلغ':      'usage_value',
    'فلوس':      'usage_value',
}


@dataclass
class ParsedQuery:
    intent: str = 'list'          # count, list, sum, avg, detail
    obj: str = 'violation'         # violation, usage, usage_value
    zone: Optional[str] = None
    decision: Optional[str] = None
    status: Optional[str] = None
    governorate: Optional[str] = None
    code: Optional[str] = None
    comparison_field: Optional[str] = None
    comparison_op: Optional[str] = None
    comparison_val: Optional[float] = None
    time_field: Optional[str] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    usage_type_name: Optional[str] = None
    limit: int = 10
    error: Optional[str] = None


def extract_code(text: str) -> Optional[str]:
    m = re.search(r'[A-Za-z]{2}\d{3,}', text)
    return m.group(0).upper() if m else None


def extract_comparison(text: str) -> tuple:
    for pattern, op in COMPARISON_PATTERNS:
        m = re.search(pattern, text)
        if m:
            val = float(m.group(1).replace(',', ''))
            return op, val
    return None, None


def extract_entities(text: str) -> dict:
    entities = {}
    text_lower = text.strip()

    for word, zone_val in ZONE_MAP.items():
        if word in text_lower:
            entities['zone'] = zone_val
            break

    for word, dec_val in DECISION_MAP.items():
        if word in text_lower:
            # avoid matching 'مخالفة' in words like 'المخالفة' or 'مخالفات'
            if word == 'مخالفة' and ('المخالفة' in text_lower or 'مخالفات' in text_lower):
                continue
            # avoid matching 'مخالف' inside 'مخالفة/مخالفات'
            if word == 'مخالف' and ('مخالفة' in text_lower or 'مخالفات' in text_lower or 'المخالف' in text_lower):
                continue
            entities['decision'] = dec_val

    for word, status_val in STATUS_MAP.items():
        if word in text_lower:
            entities['status'] = status_val
            break

    for word, gov_val in GOV_MAP.items():
        if word in text_lower:
            entities['governorate'] = gov_val
            break

    code = extract_code(text_lower)
    if code:
        entities['code'] = code

    op, val = extract_comparison(text_lower)
    if op:
        # determine comparison field
        if any(w in text_lower for w in ('قيمة', 'مبلغ', 'فلوس', 'مقابل انتفاع', 'اجمالي', 'إجمالي')):
            entities['comparison_field'] = 'value'
        else:
            entities['comparison_field'] = 'area'
        entities['comparison_op'] = op
        entities['comparison_val'] = val

    # Intent
    for word, intent_val in INTENT_KEYWORDS.items():
        if word in text_lower:
            entities['intent'] = intent_val
            break
    else:
        entities['intent'] = 'list'

    # Object (check after intent so 'قيمة' doesn't override 'usage_value')
    for word, obj_val in OBJECT_KEYWORDS.items():
        if word in text_lower:
            entities['obj'] = obj_val
            break
    else:
        entities['obj'] = 'violation'

    # If 'تفاصيل' or 'بيانات' is followed by a code, it's a detail query
    if entities.get('intent') == 'detail' and entities.get('code'):
        entities['obj'] = 'violation'

    # Limit
    if entities.get('intent') == 'list':
        if 'كل' in text_lower or 'جميع' in text_lower:
            entities['limit'] = 100
        else:
            entities['limit'] = 10

    return entities


def build_response(entities: dict) -> dict:
    """Main entry point — parse text and return response."""
    intent = entities.get('intent', 'list')
    obj = entities.get('obj', 'violation')
    error = entities.get('error')

    if error:
        return {'response': error, 'data': None, 'type': 'text'}

    if obj == 'violation' and intent == 'detail' and entities.get('code'):
        return _detail_violation(entities['code'])

    # We return a structured query for the view to execute
    return {
        'type': 'query',
        'intent': intent,
        'obj': obj,
        'filters': {
            'zone': entities.get('zone'),
            'decision': entities.get('decision'),
            'status': entities.get('status'),
            'governorate': entities.get('governorate'),
            'code': entities.get('code'),
            'comparison_field': entities.get('comparison_field'),
            'comparison_op': entities.get('comparison_op'),
            'comparison_val': entities.get('comparison_val'),
        },
        'limit': entities.get('limit', 10),
        'human_text': _build_human_text(entities),
    }


def _build_human_text(entities: dict) -> str:
    parts = []
    if entities.get('intent') == 'count':
        parts.append('عدد')
    elif entities.get('intent') == 'sum':
        parts.append('إجمالي')
    elif entities.get('intent') == 'avg':
        parts.append('متوسط')

    if entities.get('obj') == 'violation':
        parts.append('التواجدات')
    elif entities.get('obj') == 'usage':
        parts.append('الاستغلالات')
    elif entities.get('obj') == 'usage_value':
        parts.append('قيمة مقابل الانتفاع')

    filters = []
    if entities.get('zone'):
        zone_names = {v: k for k, v in ZONE_MAP.items()}
        filters.append(f'منطقة {zone_names.get(entities["zone"], entities["zone"])}')
    if entities.get('governorate'):
        filters.append(f'محافظة {entities["governorate"]}')
    if entities.get('status'):
        status_names = {v: k for k, v in STATUS_MAP.items()}
        filters.append(f'الحالة {status_names.get(entities["status"], entities["status"])}')
    if entities.get('decision'):
        filters.append(f'القرار {"148 (ترخيص)" if entities["decision"] == "148" else "149 (مخالفة)"}')
    if entities.get('comparison_op'):
        op_txt = {'gt': 'أكبر من', 'lt': 'أقل من', 'eq': 'يساوي'}.get(entities['comparison_op'], entities['comparison_op'])
        field_txt = 'المساحة' if entities.get('comparison_field') == 'area' else 'القيمة'
        filters.append(f'{field_txt} {op_txt} {entities["comparison_val"]:,.0f}')
    if entities.get('code'):
        filters.append(f'الرمز {entities["code"]}')

    if filters:
        parts.append(' — '.join(filters))
    return ' '.join(parts)


def _detail_violation(code: str) -> dict:
    from ..models import Violation
    try:
        v = Violation.objects.get(code=code)
        gov = v.governorate.name_ar if v.governorate else '—'
        return {
            'type': 'violation_detail',
            'data': {
                'id': v.id,
                'code': v.code,
                'occupant': v.occupant,
                'governorate': gov,
                'village': v.village,
                'area_total': v.area_total,
                'status': v.get_status_display(),
                'latitude': v.latitude,
                'longitude': v.longitude,
            },
            'response': f'{v.code} — {v.occupant} — {gov}'
        }
    except Violation.DoesNotExist:
        return {'type': 'text', 'data': None, 'response': f'لا يوجد تواجد بالرمز {code}'}


def parse(text: str) -> dict:
    entities = extract_entities(text)
    return build_response(entities)
