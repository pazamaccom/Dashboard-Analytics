"""Final functional acceptance; never changes applications or runtime services."""
import hashlib
import json
import os
from pathlib import Path
import plistlib
import runpy
import subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/evidence/003-acceptance'
OUT.mkdir(parents=True,exist_ok=True)
URL='http://100.127.41.102:8087'
CONFIG=json.loads((ROOT/'dashboards.json').read_text())
files=sorted([* (ROOT/'public').rglob('*'),ROOT/'server.py',ROOT/'dashboards.json',ROOT/'deploy/com.paolo.analytics.web.plist'])
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
before=hashes()
os.environ['ANALYTICS_EVIDENCE_DIR']=str(OUT/'regression')
runpy.run_path(str(ROOT/'scripts/verify_layout.py'),run_name='__main__')
checks=[]
with sync_playwright() as p:
 browser=p.chromium.launch()
 for label,viewport in [('desktop',{'width':1536,'height':1024}),('mobile',{'width':390,'height':844})]:
  context=browser.new_context(viewport=viewport,is_mobile=label=='mobile',has_touch=label=='mobile')
  page=context.new_page()
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(URL,wait_until='networkidle')
  page.wait_for_function("() => document.querySelector('[data-id=btc] .status-label').textContent==='Offline'")
  live=page.request.get(URL+'/api/status').json()
  assert len(live)==7 and sum(s['online'] for s in live)==6
  assert not next(s for s in live if s['id']=='btc')['online']
  navigation=[]
  for item in CONFIG:
   anchor=page.locator(f'[data-id="{item["id"]}"] a')
   assert anchor.get_attribute('href')==item['url']
   if item['id']=='btc':
    # The unavailable future application is intercepted only inside this browser.
    context.route(item['url'],lambda route:route.fulfill(status=200,body='Expected offline BTC navigation test'))
   with page.expect_popup() as opened:
    anchor.click()
   popup=opened.value
   popup.wait_for_load_state('domcontentloaded',timeout=20000)
   assert popup.url.rstrip('/')==item['url'].rstrip('/'),popup.url
   assert popup.evaluate('window.opener === null')
   navigation.append({'id':item['id'],'url':popup.url,'actual_navigation':item['id']!='btc','expected_offline_intercept':item['id']=='btc'})
   popup.close()
  for item in CONFIG:
   page.locator('input').fill('  '+item['name'].upper()+'  ')
   assert page.locator('.card:visible').count()==1
   assert page.locator('.card:visible').get_attribute('data-id')==item['id']
  page.locator('input').fill('fixed income')
  assert page.locator('.card:visible').get_attribute('data-id')=='yield'
  page.locator('input').fill('nonexistent-dashboard')
  assert page.locator('.empty').is_visible()
  page.locator('input').fill('')
  assert page.locator('.card:visible').count()==7
  for light in [True,False]:
   page.locator('.theme').click()
   page.reload(wait_until='networkidle')
   assert page.locator('body').evaluate('(e)=>e.classList.contains("light")')==light
   assert page.locator('.theme').get_attribute('aria-label')==f'Switch to {"dark" if light else "light"} theme'
  # Browser-only status fixtures prove automatic polling and recovery with no app mutation.
  page.clock.install()
  calls=[]
  phase=['future-online']
  def mocked_status(route):
   calls.append(phase[0])
   if phase[0]=='unavailable':route.fulfill(status=503,body='Unavailable');return
   data=[dict(s) for s in live]
   if phase[0]=='future-online':
    next(s for s in data if s['id']=='btc')['online']=True
   route.fulfill(status=200,content_type='application/json',body=json.dumps(data))
  page.route('**/api/status',mocked_status)
  page.reload(wait_until='networkidle')
  page.wait_for_function("() => document.querySelector('[data-id=btc] .status-label').textContent==='Online'")
  phase[0]='unavailable'
  page.clock.run_for(30001)
  page.wait_for_function("() => [...document.querySelectorAll('.status-label')].every(e=>e.textContent==='Status unavailable')")
  assert page.locator('.status.online,.status.offline').count()==0
  assert page.locator('.card a').evaluate_all('(els)=>els.map(e=>e.href)')==[x['url'] for x in CONFIG]
  phase[0]='live-restored'
  page.clock.run_for(30001)
  page.wait_for_function("() => document.querySelector('[data-id=btc] .status-label').textContent==='Offline'")
  assert len(calls)>=3
  assert page.locator('.status.online').count()==6
  assert not errors,errors
  page.unroute('**/api/status',mocked_status)
  checks.append({'profile':label,'navigation':navigation,'search_all_names_case_and_whitespace':'passed','search_description_and_empty_reset':'passed','both_themes_persist':'passed','live_health':'six online, BTC expected offline','synthetic_health_tests':'future BTC online, API unavailable, 30-second polling and recovery passed','javascript_errors':errors})
  context.close()
 browser.close()
installed=Path.home()/'Library/LaunchAgents/com.paolo.analytics.web.plist'
actual=plistlib.loads(installed.read_bytes())
expected=plistlib.loads((ROOT/'deploy/com.paolo.analytics.web.plist').read_bytes())
assert actual==expected
assert actual['RunAtLoad'] and actual['KeepAlive']
assert actual['ProgramArguments'][-1]=='8087'
service=subprocess.check_output(['launchctl','print',f'gui/{os.getuid()}/com.paolo.analytics.web'],text=True)
assert 'state = running' in service and 'last exit code = (never exited)' in service
startup={'installed_matches_repository':True,'RunAtLoad':True,'KeepAlive':True,'running':True,'port':8087,'scope':'per-user LaunchAgent starts at login; not a system boot daemon','reboot_or_logout_test':'not performed; no services restarted'}
assert before==hashes(),'Approved production files changed during verification'
report={'tested_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'checks':checks,'automatic_startup':startup,'production_file_hashes_unchanged':before,'independence':'Separate process, port 8087, standard-library runtime and LaunchAgent; only read-only HTTP reachability requests and direct browser navigation to independent destinations.'}
(OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'functional_profiles':[c['profile'] for c in checks],'all_functional_checks':'passed','startup':startup,'approved_production_files':'unchanged'},indent=2))
