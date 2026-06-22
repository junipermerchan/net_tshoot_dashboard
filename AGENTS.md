# AGENTS.md — net_tshoot_dashboard

## What this is
A Spanish-language interactive CLI dashboard that *guides* network engineers through troubleshooting and configuration. It does **not** execute commands on devices.

Scope includes: MPLS, L3VPN, L2VPN, EVPN, VXLAN, BGP, OSPF, IS-IS, STP/RSTP, QoS/TE, BFD, Multicast, MP-BGP, DHCP, NetFlow, SD-WAN, DMVPN, EIGRP, PBR, IPv6, AAA, Switch L2, VRRP/HSRP, GPON/ONT, EVC, Segment Routing, and Wireshark/tcpdump.

## Entry point
- `python main.py` — interactive terminal app. Uses `rich>=13.0.0` if installed (optional, falls back to plain text).
- VS Code: `Ctrl+Shift+P` → "Tasks: Run Task" → `🌐 Network Tshoot Dashboard` (runs `python3 main.py`).

## Architecture
- `main.py` — bootstraps `Engine`, adds project root to `sys.path` if run directly.
- `core/engine.py` — state machine driving menus, vendor selection, tier selection (1-4), and step navigation. Steps are keyed strings (e.g. `mpls_start`) with choices mapping to `next` step keys. Navigation supports backtracking via history stack.
- `data/knowledge_base.py` — base `KB` dict with troubleshooting content. `VendorMap` defines display labels for vendor keys. At runtime `_kb()` merges `config_guides.CONFIG_GUIDES` into `KB`.
- `data/config_guides.py` — `CONFIG_GUIDES` dict with configuration content. Helpers: `cmd_dict(t1, t2, t3, arch)` and `body(*lines)`.
- `data/packet_walkthroughs.py` — OSI-layer packet walkthrough simulations.
- `data/simulated_outputs.py` — realistic vendor-specific CLI outputs for command sandbox simulation.
- `utils/display.py` — terminal UI layer. Gracefully degrades if `rich` is missing.
- `data/scientific_steps.py` — granular scientific-method overrides for troubleshooting steps: falsifiable hypotheses, verification steps, confirming/invalidating evidence, cognitive bias warnings, scientific basis (RFCs), confidence levels, bibliographic references, and **concrete `fix` fields (Quick Fix)**. Applied automatically at runtime to matching steps in `KB`. Covers 102 steps across all technologies (~32% of total steps, 100% of _start and critical intermediate steps).
- `core/engine.py` — supports three scientific modes configurable at runtime: **Normal** (default), **Semi-Strict** (warning if advancing without evidence on Tier ≥ 3 steps), and **Strict** (blocks advance until evidence is registered). Tracks session confidence score (0-100%) and invalidated-streak alerts. Includes **breadcrumbs navigation**, **Quick Fix panel**, and **keyboard shortcuts** (0=back, 99=menu, 88=simulate, 77=notes, 66=variables).
- `utils/display.py` — renders session confidence bar in the banner alongside tier level. Also renders breadcrumbs and Quick Fix panels.
- `scripts/validate.py` — automated integrity checker for vendors, commands, next steps, TECH_CONCEPTS, and scientific overrides.
- `web/` — static web dashboard. `web/export.py` regenerates `web/data.js` from `KB`. Open `web/index.html` in a browser after running `python web/export.py`. The web UI renders scientific-method fields inline in the step view, displays a hypotheses tree in the sidebar, exports structured JSON reports, and shows a real-time confidence indicator. **Includes command simulation, Quick Fix panel, scientific mode toggle (Normal / Semi-Strict / Strict), clickable breadcrumbs, and evidence registration.**

## Tier Model (Estructura estándar telecom)
Los 4 niveles siguen el modelo internacional de operadores:
| Tier | Rol | Capacidad |
|------|-----|-----------|
| **1** | Frontline & Triage / NOC L1 | Ping, traceroute, reinicios remotos, validación de cortes masivos, escalado a L2 en 15-30 min |
| **2** | Network & Infrastructure Specialist / NOC L2 | Tablas de enrutamiento, estados de protocolo, análisis de saturación, VLANs/VPNs, coordinación de campo |
| **3** | Core Engineering / NOC L3 | Debugs profundos, trazas de protocolo, estabilidad del backbone, mitigación DDoS, parches críticos |
| **4** | Vendor Support (TAC) / Arquitecto | Bugs de código/hardware propietario, diseño, escalabilidad, interoperabilidad, soporte directo del fabricante |

## Adding or extending content
- **Troubleshooting technologies / steps / commands:** edit `data/knowledge_base.py`.
- **Configuration guides:** edit `data/config_guides.py`; prefer `cmd_dict()` and `body()` helpers.
- **Packet walkthroughs:** edit `data/packet_walkthroughs.py`.
- **Simulated outputs:** edit `data/simulated_outputs.py`; add vendor-specific CLI outputs for command sandbox.
- Keep step keys unique within a technology; choices reference them via `"next": "<step_key>"`.
- Vendor command blocks may be `List[str]` (always shown) or `Dict[str, List[str]]` with keys `tier1`, `tier2`, `tier3`, `arch` (accumulated up to selected tier).

## Vendor keys
`VendorMap` in `knowledge_base.py` defines labels for: `juniper`, `cisco_iosxr`, `cisco_iosxe`, `cisco_asr903`, `mikrotik`, `fortinet`, `adtran`, `ta5k`, `zone`, `zte`, `huawei`, `zhone`, `linux`.

**Note:** All vendors used in `data/config_guides.py` are now present in `VendorMap`. If adding new vendors, update `VendorMap` or the UI will display the raw key.

Not all vendors appear in every technology (e.g. `l2vpn` omits `fortinet`; `evpn` omits `fortinet`; `adtran_ta5000` only includes `adtran`; `evc` includes `cisco_asr903` and `cisco_iosxe`).

## Important constraints
- **No test suite, no lint/typecheck config, no CI** — this is a lightweight CLI script repo.
- **No build/packaging** — plain Python, no `pyproject.toml`, `setup.py`, or `setup.cfg`.
- UI and all user-facing text is in **Spanish**; do not introduce English UI strings.
- Do not add remote execution or SSH connectivity — the design intent is a safe, read-only guidance tool.
