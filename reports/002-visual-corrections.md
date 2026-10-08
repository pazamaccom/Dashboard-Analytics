# Visual corrections — 8 October 2026

Tested application/verification source commit: `f56cb96`.

## Cause and correction

The DOM contained exactly seven dashboard articles. The apparent duplicates were raster content from the full reference screenshot used as a repeating, unbounded CSS background. Wider cards revealed neighbouring reference cards, while resizing shifted baked-in icons underneath independently rendered live icons. The CSS also contained conflicting grid/flex rules, three different lower-row widths and unequal row heights.

Each artwork is now isolated in an explicit SVG viewport over the unchanged original reference PNG. Native artwork scale preserves chart/flag proportions. Viewports exclude reference borders and neighbouring cards, masks remove the baked-in icons before the original icon crop is rendered once, and the BTC badge has a single live overlay. No raster asset was regenerated or modified.

One four-column grid places four equal cards in row one and three equal cards in row two. The quote occupies the fourth lower-row cell with independent padding. All cards use 331px height and consistent 27px horizontal / 21px vertical spacing at desktop widths. Tablet switches to two columns, mobile to one. Footer padding is reduced from 28px top/bottom to 22px/20px; a fixed viewport background prevents the gradient restarting below short content.

Dashboard names, descriptions, original graphics, accent colors, typography families, button labels, destinations, new-tab behavior, search, theme preference and health API remain intact. No server changes or service restarts were required: the deployed portal serves updated static files immediately.

## Verification and actual browser evidence

Command: `/Users/trader/Drawdown/repo/.venv/bin/python scripts/verify_layout.py`

Passed Chromium verification at 1440×1000, 1536×1024, 1920×1080, 1024×1366, 768×1024 and 390×844. Full-page browser captures (not composites or mock-ups) and machine-readable results are in `reports/evidence/002-layout/`.

Verified seven unique card elements, one bounded artwork per card, equal dimensions, four/three desktop arrangement, consistent desktop gaps, no card or internal content overlap, no horizontal overflow, quotation visibility/separation, unchanged seven links with new-tab protections, status-to-API agreement, search/no-results, persisted theme and no JavaScript exceptions. Desktop and mobile screenshots were also visually inspected to catch raster duplicates that DOM assertions alone cannot detect.

Read-only HTTP requests to the six running destination applications returned 200. BTC port 8086 remains unavailable and correctly shows Offline. Reachability is not a data-freshness/trading-health assertion. Chromium responsive emulation is not a physical-device certification.

Existing dashboard listener PIDs remain 307, 513, 518, 542, 546, 885 and 2863; portal remains PID 6351. No underlying application files, data, environments, ports, services or tunnels were modified or restarted.

Owner visual acceptance remains pending. Primary acceptance screenshot: `reports/evidence/002-layout/1536.png`.
