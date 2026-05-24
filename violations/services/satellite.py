"""
خدمة صور الأقمار الصناعية — تستخدم Sentinel Hub Process API
مع OAuth2 عبر بيانات المستخدم
"""
import os
import uuid
from datetime import datetime
from typing import Optional
from django.conf import settings

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


def _fetch_image(lat: float, lng: float, date_from: str, date_to: str,
                 max_cloud: float = 20, width: int = 1024, height: int = 1024) -> Optional[bytes]:
    """جلب صورة من Sentinel Hub Process API"""
    from sentinelhub import SHConfig, SentinelHubRequest, BBox, CRS, MimeType, DataCollection

    config = SHConfig()
    config.sh_client_id = CLIENT_ID
    config.sh_client_secret = CLIENT_SECRET

    # BBox ~2km around the point
    bbox = BBox([lng - 0.01, lat - 0.01, lng + 0.01, lat + 0.01], crs=CRS.WGS84)

    request = SentinelHubRequest(
        evalscript=EVALSCRIPT_TRUE_COLOR,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=(date_from, date_to),
                maxcc=max_cloud / 100.0,
            )
        ],
        responses=[SentinelHubRequest.output_response('default', MimeType.PNG)],
        bbox=bbox,
        size=(width, height),
        config=config,
    )

    data = request.get_data()
    if data and len(data) > 0:
        return data[0]  # numpy array
    return None


def _save_image(img_data, prefix: str = 'sat') -> Optional[str]:
    """حفظ الصورة وإرجاع المسار النسبي"""
    import numpy as np
    from PIL import Image

    filename = f'{prefix}_{uuid.uuid4().hex[:8]}.png'
    filepath = os.path.join(CACHE_DIR, filename)

    img = Image.fromarray(img_data)
    img.save(filepath, 'PNG')

    return f'{settings.MEDIA_URL}satellite/{filename}'


def search_best(lat: float, lng: float, date_from: str, date_to: str,
                max_cloud: float = 20) -> Optional[dict]:
    """البحث عن أفضل صورة وجلبها"""
    img_data = _fetch_image(lat, lng, date_from, date_to, max_cloud)
    if img_data is None:
        return None

    url = _save_image(img_data)
    if url is None:
        return None

    return {
        'date': date_to[:10],
        'cloud_cover': 0,
        'image_url': url,
        'width': 1024,
        'height': 1024,
    }


def search_before_after(lat: float, lng: float, year_before: int = 2022,
                        year_after: int = 2024) -> dict:
    """صورتين: قبل وبعد للمقارنة"""
    before = _fetch_image(lat, lng, f'{year_before}-01-01', f'{year_before}-12-31')
    after  = _fetch_image(lat, lng, f'{year_after}-06-01', f'{year_after}-12-31')

    result = {'location': {'lat': lat, 'lng': lng}, 'before': None, 'after': None}

    if before is not None:
        url = _save_image(before, 'before')
        result['before'] = {
            'date': f'{year_before}-12-31',
            'image_url': url,
            'width': 1024, 'height': 1024,
        }

    if after is not None:
        url = _save_image(after, 'after')
        result['after'] = {
            'date': f'{year_after}-12-31',
            'image_url': url,
            'width': 1024, 'height': 1024,
        }

    return result
