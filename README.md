# P | ANALYTICS

Independent private graphical navigation portal for seven financial dashboards.

## Run

Python 3.10+; no third-party runtime dependencies.

```sh
python3 server.py --host 127.0.0.1 --port 8087
```

Production address: http://100.127.41.102:8087/ through Tailscale.
The server serves only `public/`; repository metadata and configuration are not exposed.
Edit `dashboards.json` to change destinations; restart only the analytics service after changing server configuration.
Status checks are read-only HTTP GETs, cached for 15 seconds. The page refreshes status every 30 seconds. Online indicates HTTP reachability, not data freshness or trading health.

## Design

`public/assets/reference.png` is the owner-provided Desktop IMAGE.png. CSS clips its artwork into individual cards and the world map. Text, search, dashboard links, theme preference and status indicators are live HTML. Desktop follows the supplied 1536×1024 composition; tablet and mobile reflow the cards. The actual date, greeting and reachability indicators reflect current state rather than fixed mock-up values.

## Deployment

`deploy/com.paolo.analytics.web.plist` describes a separate macOS launchd agent, bound only to this host's Tailscale IP and port 8087. Logs go to ignored `logs/`. Installing it requires copying this new plist into the user's LaunchAgents directory and bootstrapping only `com.paolo.analytics.web`. No existing applications, launch agents, ports, environments, data, proxies or tunnels need changes.

All dashboard links open a separate tab. Users need existing network permissions to access the linked applications. BTC uses port 8086 and remains Offline until its service is available.
