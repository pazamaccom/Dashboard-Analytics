import json
from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 browser=p.chromium.launch()
 page=browser.new_page(viewport={'width':1536,'height':1024},device_scale_factor=1)
 errors=[]
 page.on('pageerror',lambda err:errors.append(str(err)))
 page.goto('http://127.0.0.1:8087/',wait_until='networkidle')
 page.wait_for_function("document.querySelector('.status-label').textContent !== 'Checking…'")
 assert page.locator('.card').count()==7
 assert page.locator('.card a').count()==7
 assert sorted(int(x.rsplit(':',1)[1].strip('/')) for x in page.locator('.card a').evaluate_all('(links)=>links.map(x=>x.href)'))==list(range(8080,8087))
 page.screenshot(path='/Users/trader/Dashboard-Analytics/reports/evidence/desktop.png',full_page=True)
 page.locator('input').fill('yield')
 assert page.locator('.card:visible').count()==1
 page.locator('input').fill('no such dashboard')
 assert page.locator('.empty').is_visible()
 page.locator('input').fill('')
 page.locator('.theme').click()
 assert page.locator('body').evaluate('(el)=>el.classList.contains("light")')
 page.reload(wait_until='networkidle')
 assert page.locator('body').evaluate('(el)=>el.classList.contains("light")')
 page.locator('.theme').click()
 for width in [390,768,1280,1536]:
  page.set_viewport_size({'width':width,'height':1024})
  page.wait_for_timeout(200)
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),str(page.evaluate('[innerWidth,document.documentElement.scrollWidth,...[...document.querySelectorAll("*")].filter(e=>e.scrollWidth>e.clientWidth).map(e=>[e.tagName,e.className,e.scrollWidth,e.clientWidth])]'))
  for card in page.locator('.card').all():
   assert card.locator('a').is_visible()
  if width==390:page.screenshot(path='/Users/trader/Dashboard-Analytics/reports/evidence/mobile.png',full_page=True)
 assert not errors,errors
 states=page.request.get('http://127.0.0.1:8087/api/status').json()
 print(json.dumps({'browser_errors':errors,'responsive_widths':[390,768,1280,1536],'search':'passed','theme_persistence':'passed','links':'passed','status':states},indent=2))
 browser.close()
