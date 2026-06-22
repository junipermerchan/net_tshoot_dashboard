#!/usr/bin/env python3
"""
Network Troubleshooting Dashboard CLI
Tier 3 / Architect level guided diagnostics for MPLS, L3VPN, L2VPN, EVPN, VXLAN.
Platforms: Juniper, Cisco IOS-XR/IOS-XE/NX-OS, MikroTik, Fortinet, ADTRAN.

No ejecuta comandos en equipos; guía el diagnóstico paso a paso con comandos,
explicaciones arquitectónicas y criterios de aceptación por vendor.
"""

import sys
from pathlib import Path

# Asegurar que el proyecto esté en path si se ejecuta directamente
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine import Engine


def main():
    engine = Engine()
    try:
        engine.start()
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario. Adiós.")
        sys.exit(0)


if __name__ == "__main__":
    main()
