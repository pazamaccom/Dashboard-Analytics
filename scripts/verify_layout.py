"""Verify the deployed portal; only read-only requests reach underlying apps."""
import json
import os
from pathlib import Path
from urllib.request import build_opener, ProxyHandler
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(os.environ.get('ANALYTICS_EVIDENCE_DIR', str(ROOT / 'reports/evidence/002-layout')))
OUTPUT.mkdir(parents=True, exist_ok=True)
URL = os.environ.get('ANALYTICS_URL', 'http://100.127.41.102:8087')
EXPECTED = json.loads((ROOT / 'dashboards.json').read_text())
results = []
def overlap(a,b):
    return min(a['x']+a['width'],b['x']+b['width'])-max(a['x'],b['x']) > 1 and min(a['y']+a['height'],b['y']+b['height'])-max(a['y'],b['y']) > 1
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    for width,height in [(1440,1000),(1536,1024),(1920,1080),(1024,1366),(768,1024),(390,844)]:
        page.set_viewport_size({'width':width,'height':height})
        page.goto(URL, wait_until='networkidle')
        page.wait_for_function("[...document.querySelectorAll('.status-label')].every(e=>['Online','Offline'].includes(e.textContent))")
        cards=page.locator('.card')
        assert cards.count()==7
        assert len(set(cards.evaluate_all('(els)=>els.map(e=>e.dataset.id)')))==7
        assert cards.evaluate_all('(els)=>els.every(e=>e.querySelectorAll(".art").length===1 && e.querySelector(".art").tagName.toLowerCase()==="svg")')
        bounds=[c.bounding_box() for c in cards.all()]
        for i,a in enumerate(bounds):
            for b in bounds[i+1:]:assert not overlap(a,b), (width,a,b)
        assert max(b['width'] for b in bounds)-min(b['width'] for b in bounds)<1
        assert max(b['height'] for b in bounds)-min(b['height'] for b in bounds)<1
        if width>=1440:
            assert len(set(round(b['y']) for b in bounds[:4]))==1
            assert len(set(round(b['y']) for b in bounds[4:]))==1
            assert bounds[4]['y']>bounds[0]['y']
            for row in [bounds[:4],bounds[4:]]:
                gaps=[row[i+1]['x']-row[i]['x']-row[i]['width'] for i in range(len(row)-1)]
                assert all(abs(g-27)<1 for g in gaps)
        quote=page.locator('blockquote').bounding_box()
        assert page.locator('blockquote').is_visible()
        assert all(not overlap(quote,b) for b in bounds)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        for card in cards.all():
            controls=[card.locator(s).bounding_box() for s in ['.icon','h2','p','.status','a']]
            for a,b in zip(controls,controls[1:]):assert not overlap(a,b),(width,card.get_attribute('data-id'),a,b)
            outer=card.bounding_box()
            assert all(b['y']+b['height'] <= outer['y']+outer['height'] for b in controls),(width,card.get_attribute('data-id'),outer,controls)
        links=cards.locator('a').evaluate_all('(els)=>els.map(e=>({url:e.href,target:e.target,rel:e.rel}))')
        assert [l['url'] for l in links]==[d['url'] for d in EXPECTED]
        assert all(l['target']=='_blank' and 'noopener' in l['rel'] for l in links)
        states=page.request.get(URL+'/api/status').json()
        for state in states:
            status=page.locator(f'[data-id="{state["id"]}"] .status')
            assert status.inner_text()==('Online' if state['online'] else 'Offline')
        page.screenshot(path=str(OUTPUT/f'{width}.png'),full_page=True)
        results.append({'width':width,'height':height,'card_count':7,'overlap':False,'horizontal_overflow':False,'equal_dimensions':True,'quote_separate':True,'statuses':states})
    page.locator('input').fill('yield')
    assert page.locator('.card:visible').count()==1
    page.locator('input').fill('missing-dashboard')
    assert page.locator('.empty').is_visible()
    page.locator('input').fill('')
    assert page.locator('.card:visible').count()==7
    page.locator('.theme').click()
    page.reload(wait_until='networkidle')
    assert page.locator('body').evaluate('(e)=>e.classList.contains("light")')
    page.locator('.theme').click()
    assert not errors,errors
    browser.close()
# Independent read-only verification of configured destinations.
opener=build_opener(ProxyHandler({}))
health=[]
for item in EXPECTED:
    try:
        with opener.open(item['url'],timeout=3) as response: code=response.status
    except Exception:code=None
    health.append({'id':item['id'],'http_status':code})
report={'breakpoints':results,'browser_errors':errors,'search':'passed','theme_persistence':'passed','destination_http_checks':health}
(OUTPUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'breakpoints':[r['width'] for r in results],'checks':'passed','destination_http_checks':health},indent=2))
