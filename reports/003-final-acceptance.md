# Final acceptance verification — 8 October 2026

Visual design accepted by the owner before this verification. No further visual changes made. Verified deployed application commit: `214a1f6` (application source `f56cb96`). No production corrections were necessary. All public assets/HTML/CSS/JavaScript, server, dashboard configuration and deployment configuration retain their pre-verification SHA-256 hashes, recorded in the machine-readable evidence.

## Results

| Check | Result |
| --- | --- |
| Seven dashboard links | Passed on desktop and mobile; all target the configured URL in an independent new tab with no opener |
| Six completed applications | Actual browser navigation and separate read-only HTTP checks passed; each root returned HTTP 200 |
| BTC Trading Bot / 8086 | Expected Offline because its application is unfinished; configured link preserved. Its click target was tested with a browser-only intercepted response, not a claim of a running BTC service |
| Search | All seven names, case-insensitive matching, whitespace trimming, description search, no-results state and clearing/reset passed on desktop and mobile |
| Theme switching | Dark-to-light and light-to-dark passed; each preference survives reload; accessible button label updates |
| Health indicators | Live API has seven destinations: six Online, BTC Offline; rendered indicators agree |
| Automatic health refresh | Browser-only fixtures and virtual time verified 30-second polling, future BTC Online transition, unavailable API state, removal of stale online classes, preserved navigation during failure and recovery to actual live-state fixture |
| Automatic startup | Installed LaunchAgent exactly matches repository configuration; RunAtLoad and KeepAlive enabled; service running on private Tailscale port 8087; plist validation passed |
| Desktop regression | Passed 1440×1000, 1536×1024 and 1920×1080 |
| Tablet regression | Passed 1024×1366 and 768×1024 |
| Mobile regression | Passed 390×844; additional touch/mobile browser context passed functional tests |
| Layout invariants | Seven unique cards, equal dimensions, four/three desktop arrangement, consistent gaps, no card/content overlap, separate visible quote, no horizontal overflow |
| JavaScript errors | None in the portal |
| Production files | Unchanged; approved artwork, colors, dimensions, typography, layout and behavior preserved |

## Startup scope and limits

`com.paolo.analytics.web` is a per-user macOS LaunchAgent. RunAtLoad starts the portal at user login; KeepAlive supervises it and retries exits (including a temporarily unavailable Tailscale bind address). It is not a system-wide pre-login boot daemon. Verified loaded configuration and current running state without restarting the portal, rebooting or logging out. Reboot/login recovery has not been physically exercised. Browser mobile emulation is not physical-device certification.

## Independence

The portal retains its own repository, process, logs, port 8087 and LaunchAgent. Runtime uses Python's standard library and serves its own public directory. It has no imports from, filesystem dependencies on, shared Python environments with, reverse-proxy ownership of, or service-control coupling to any underlying application. Connections are read-only HTTP reachability checks and direct navigation to existing application URLs.

No underlying application code, data, environment, port, service, scheduler or tunnel was modified or restarted. BTC remains untouched and expected offline. Its health indicator will become Online after it starts returning successful HTTP responses at its configured URL, normally within the next 30-second page poll (server health cache is 15 seconds).

## Reproduction and evidence

- `/Users/trader/Drawdown/repo/.venv/bin/python scripts/verify_acceptance.py` — passed. The existing Python environment supplies the browser test dependency only; the production portal does not depend on it.
- `plutil -lint /Users/trader/Library/LaunchAgents/com.paolo.analytics.web.plist` — passed.
- `git diff --check` — passed.
- `reports/evidence/003-acceptance/verification.json` — functional results, startup configuration conclusions and unchanged production hashes.
- `reports/evidence/003-acceptance/regression/verification.json` — all six regression breakpoints, link/status checks and independent destination HTTP results.
- `reports/evidence/003-acceptance/regression/{1440,1536,1920,1024,768,390}.png` — actual full-page browser screenshots, preserving the previously accepted screenshots in the earlier evidence directory.

A first test attempt encountered a browser-test CSP evaluation issue during virtual timer polling. The test expression was corrected; production CSP and production application files were unchanged. The final complete rerun passed.
