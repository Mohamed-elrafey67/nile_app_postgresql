"""
خدمة صور الأقمار الصناعية — Sentinel Hub Process API + كشف التغيير
"""

import os
import io
import uuid
from datetime import datetime, date
from typing import Optional

from django.conf import settings
import numpy as np
from PIL import Image

CLIENT_ID = 'af7c6bae-ef2e-45aa-83b4-31dfea9691f5'
CLIENT_SECRET = 'ldYA1fxqJVL5t3GAcGbxI7rwmAjVXzMW'

CACHE_DIR = os.path.join(settings.MEDIA_ROOT, 'satellite')
os.makedirs(CACHE_DIR, exist_ok=True)

EVALSCRIPT_TRUE_COLOR = '''
//VERSION=3
function setup() { return {input: ['B02','B03','B04'], output: {bands: 3}}; }
function evaluatePixel(sample) {
  return [2.5*sample.B04, 2.5*sample.B03, 2.5*sample.B02];
}
'''

# ── Helper functions ──────────────────────────────────────────

def _fetch_image(lat: float, lng: float, date_from: str, date_to: str,
                 max_cloud: float = 20, width: int = 1024, height: int = 1024) -> Optional[bytes]:
    """جلب صورة من Sentinel Hub Process API"""
    from sentinelhub import SHConfig, SentinelHubRequest, BBox, CRS, MimeType, DataCollection
    config = SHConfig()
    config.sh_client_id = CLIENT_ID
    config.sh_client_secret = CLIENT_SECRET
    bbox = BBox([lng - 0.01, lat - 0.01, lng + 0.01, lat + 0.01], crs=CRS.WGS84)
    request = SentinelHubRequest(
        evalscript=EVALSCRIPT_TRUE_COLOR,
        input_data=[SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=(date_from, date_to),
            maxcc=max_cloud / 100.0,
        )],
        responses=[SentinelHubRequest.output_response('default', MimeType.PNG)],
        bbox=bbox, size=(width, height), config=config,
    )
    data = request.get_data()
    if data and len(data) > 0:
        return data[0]
    return None


def _save_image(img_data, prefix: str = 'sat') -> Optional[str]:
    """حفظ الصورة وإرجاع المسار النسبي"""
    filename = f'{prefix}_{uuid.uuid4().hex[:8]}.png'
    filepath = os.path.join(CACHE_DIR, filename)
    Image.fromarray(img_data).save(filepath, 'PNG')
    return f'{settings.MEDIA_URL}satellite/{filename}'


def _get_image_abs_path(url: str) -> str:
    """تحويل URL نسبي إلى مسار مطلق"""
    relative = url.replace(settings.MEDIA_URL, '')
    return os.path.join(settings.MEDIA_ROOT, relative.replace('/', os.sep))


# ── Core search functions ─────────────────────────────────────

def search_best(lat: float, lng: float, date_from: str, date_to: str,
                max_cloud: float = 20) -> Optional[dict]:
    """البحث عن أفضل صورة وجلبها"""
    from violations.models import SatelliteImage
    # Try cache first
    year = date_from[:4]
    violation_id = getattr(settings, '_sat_violation_id', None)
    if violation_id:
        cached = SatelliteImage.objects.filter(
            violation_id=violation_id, year=year
        ).first()
        if cached and cached.image:
            return {
                'date': str(cached.date_acquired),
                'cloud_cover': cached.cloud_cover,
                'image_url': cached.image.url,
                'width': 1024, 'height': 1024,
                'bounds': [cached.bounds_west, cached.bounds_south,
                           cached.bounds_east, cached.bounds_north],
            }

    img_data = _fetch_image(lat, lng, date_from, date_to, max_cloud)
    if img_data is None:
        return None
    url = _save_image(img_data)
    if url is None:
        return None
    return {
        'date': date_to[:10], 'cloud_cover': 0,
        'image_url': url, 'width': 1024, 'height': 1024,
    }


def search_before_after(lat: float, lng: float, year_before: int = 2022,
                        year_after: int = 2024) -> dict:
    """صورتين: قبل وبعد للمقارنة"""
    before = _fetch_image(lat, lng, f'{year_before}-01-01', f'{year_before}-12-31')
    after  = _fetch_image(lat, lng, f'{year_after}-06-01', f'{year_after}-12-31')
    result = {'location': {'lat': lat, 'lng': lng}, 'before': None, 'after': None}
    bounds = [lng - 0.01, lat - 0.01, lng + 0.01, lat + 0.01]
    if before is not None:
        url = _save_image(before, 'before')
        result['before'] = {
            'date': f'{year_before}-12-31', 'image_url': url,
            'width': 1024, 'height': 1024, 'bounds': bounds,
        }
    if after is not None:
        url = _save_image(after, 'after')
        result['after'] = {
            'date': f'{year_after}-12-31', 'image_url': url,
            'width': 1024, 'height': 1024, 'bounds': bounds,
        }
    return result


# ── Change Detection ──────────────────────────────────────────

def compute_change_detection(lat: float, lng: float, years: list) -> dict:
    """
    حساب التغيير بين سنوات متعددة.
    years: قائمة سنوات [2020, 2022, 2024, 2026]
    يرجع: { images: [...], changes: [...], heatmap: {...}, stats: {...} }
    """
    images = {}
    for year in years:
        img = _fetch_image(lat, lng, f'{year}-06-01', f'{year}-10-31', max_cloud=30)
        if img is not None:
            url = _save_image(img, f'y{year}')
            images[year] = {'data': img, 'url': url}

    if len(images) < 2:
        return {'error': 'يحتاج على الأقل سنتين للمقارنة'}

    bounds = [lng - 0.01, lat - 0.01, lng + 0.01, lat + 0.01]
    sorted_years = sorted(images.keys())
    changes = []
    all_diffs = []

    for i in range(len(sorted_years) - 1):
        y1 = sorted_years[i]
        y2 = sorted_years[i + 1]
        img1 = images[y1]['data']
        img2 = images[y2]['data']

        # حساب الفرق المطلق في التدرج الرمادي
        gray1 = np.mean(img1.astype(np.float32), axis=2)
        gray2 = np.mean(img2.astype(np.float32), axis=2)
        diff = np.abs(gray1 - gray2)

        # إحصائيات
        mean_diff = float(np.mean(diff))
        max_diff = float(np.max(diff))
        threshold = 30.0
        changed_mask = (diff > threshold)
        pct_changed = float(np.sum(changed_mask) / diff.size) * 100

        # تقدير المساحة المتغيرة (حوالي 2×2 كم = 4,000,000 م²)
        est_area_m2 = round(pct_changed / 100.0 * 4_000_000, 1)

        # توليد heatmap (طبقة حمراء شفافة)
        h, w = diff.shape
        heatmap = np.zeros((h, w, 4), dtype=np.uint8)
        heatmap[diff > threshold, 0] = 255   # Red
        heatmap[diff > threshold, 1] = 0     # Green
        heatmap[diff > threshold, 2] = 0     # Blue
        alpha = np.clip(diff[diff > threshold] * 1.5, 40, 200).astype(np.uint8)
        heatmap[diff > threshold, 3] = alpha

        hm_url = _save_image(heatmap, f'hm_{y1}_{y2}')
        all_diffs.append(diff)

        changes.append({
            'year_from': y1, 'year_to': y2,
            'mean_diff': round(mean_diff, 1),
            'max_diff': round(max_diff, 1),
            'pct_changed': round(pct_changed, 2),
            'est_area_m2': est_area_m2,
            'heatmap_url': hm_url,
        })

    # إحصائيات كلية
    first_year = sorted_years[0]
    last_year = sorted_years[-1]
    total_changed = sum(c['pct_changed'] for c in changes)
    avg_changed = total_changed / len(changes) if changes else 0

    # Heatmap تراكمي (الأول → الأخير)
    if len(all_diffs) > 0:
        combined = np.mean(all_diffs, axis=0) if len(all_diffs) > 1 else all_diffs[0]
        h, w = combined.shape
        cum_heatmap = np.zeros((h, w, 4), dtype=np.uint8)
        cum_heatmap[combined > 30, 0] = 255
        cum_heatmap[combined > 30, 3] = np.clip(combined[combined > 30] * 1.5, 40, 200).astype(np.uint8)
        cum_url = _save_image(cum_heatmap, f'cum_{first_year}_{last_year}')
    else:
        cum_url = None

    return {
        'images': [{'year': y, 'image_url': images[y]['url'],
                     'bounds': bounds} for y in sorted_years],
        'changes': changes,
        'cumulative_heatmap': cum_url,
        'bounds': bounds,
        'stats': {
            'years': sorted_years,
            'first_year': first_year,
            'last_year': last_year,
            'avg_change_pct': round(avg_changed, 2),
            'total_est_area_m2': round(sum(c['est_area_m2'] for c in changes), 1),
        },
    }
