# P | ANALYTICS

Independent private graphical navigation portal for seven financial dashboards.

## Run

Python 3.10+; no third-party runtime dependencies.

```sh
python3 server.py --host 127.0.0.1 --port 8087
```

Production address: http://100.88.179.94:8087/ through Tailscale.
The server serves only `public/`; repository metadata and configuration are not exposed.
Edit `dashboards.json` to change destinations; restart only the analytics service after changing server configuration.
Status checks are read-only HTTP GETs, cached for 15 seconds. The page refreshes status every 30 seconds. Online indicates HTTP reachability, not data freshness or trading health.

## Design

`public/assets/reference.png` is the owner-provided Desktop IMAGE.png. Bounded inline SVG viewports clip its original artwork into individual cards; masks remove baked-in icons before displaying each live icon once. CSS clips the world map. Text, search, dashboard links, theme preference and status indicators are live HTML. Desktop uses four equal cards above three equal cards and a separate quotation; tablet and mobile reflow the cards. The actual date, greeting and reachability indicators reflect current state rather than fixed mock-up values.

## Deployment

`deploy/com.paolo.analytics.web.plist` describes a separate macOS launchd agent, bound only to this host's Tailscale IP and port 8087. Logs go to ignored `logs/`. Installing it requires copying this new plist into the user's LaunchAgents directory and bootstrapping only `com.paolo.analytics.web`. No existing applications, launch agents, ports, environments, data, proxies or tunnels need changes.

All dashboard links open a separate tab. Users need existing network permissions to access the linked applications.

## Port registry

Every dashboard keeps a reserved port in `dashboards.json` (and the matching link in `public/index.html`), whether or not its service runs yet. A dashboard that is not running shows Offline and turns Online by itself once something answers on its port. No portal change is needed. To move a dashboard to another port, update both files and restart the portal.

| Dashboard | Port | State on 2026-11-02 |
| --- | --- | --- |
| US Drawdown and Downturn | 8080 | Running |
| Turkey Fund Tracker | 8081 | Running |
| Alpha Signal Scout | 8082 | Reserved, not running |
| Stock Attractiveness | 8083 | Reserved, not running |
| Yield Curve | 8084 | Running |
| US Market Health | 8085 | Running |
| BTC Trading Bot | 8086 | Running |
| P \| ANALYTICS portal | 8087 | Running |

## Layout verification

```sh
ANALYTICS_URL=http://100.88.179.94:8087 .venv/bin/python scripts/verify_layout.py
```

Use a Python environment with Playwright and Chromium installed (they are verification dependencies only). The script captures actual browser screenshots at 1440, 1536, 1920, 1024, 768 and 390 pixels, checks seven unique cards, equal dimensions, row spacing, card/content overlap, quotation separation, links, live status mapping, search and theme persistence. Evidence is saved under `reports/evidence/002-layout/`.
