import urllib.request, json, urllib.parse, http.cookiejar

url = 'http://127.0.0.1:8002/api/satellite/change/?lat=28.11411997529689&lng=30.750262949618048&years=2020,2022,2024'
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

login_data = urllib.parse.urlencode({'username':'admin_test','password':'test123'}).encode()
opener.open('http://127.0.0.1:8002/login/', login_data)

resp = opener.open(url)
d = json.loads(resp.read())
print('Images:', len(d.get('images',[])))
print('Changes:', len(d.get('changes',[])))
for ch in d.get('changes',[]):
    print(f'  {ch["year_from"]}->{ch["year_to"]}: {ch["pct_changed"]}% ({ch["est_area_m2"]}m2)')
if 'stats' in d:
    print('Stats:', json.dumps(d['stats'], ensure_ascii=False, indent=2))
