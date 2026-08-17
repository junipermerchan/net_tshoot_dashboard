#!/usr/bin/env python3
"""
build_network_bible.py — Script Maestro de Construcción, Validación y Generación de la Biblia de Configuración & Troubleshooting de Redes Multi-Vendor.

Este script automatiza:
1. Audit de integridad de la Base de Conocimiento (0 errores, 0 advertencias).
2. Generación automática del libro/documentación maestra 'docs/Biblia_Master_Redes.md' con todos los comandos, conceptos, metodologías y vendors.
3. Actualización y empaquetado del archivo Web UI 'web/data.js'.
"""

import sys
import os
import json
from pathlib import Path

# Ajustar sys.path al directorio raíz
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.knowledge_base import KB, VendorMap, TECH_CONCEPTS, EQUIPMENT_MODELS, VENDOR_CONCEPTS_MATRIX
from data.config_templates import CONFIG_TEMPLATES
from data.packet_walkthroughs import PACKET_WALKTHROUGHS
from scripts.validate import validate
from web.export import export_data
from scripts.export_db_js import generate_db_js
from scripts.export_devices_db_js import generate_devices_db_js


def generate_network_bible_markdown():
    print("\n📖 Generando la 'Biblia Master de Configuración & Troubleshooting de Redes' (docs/Biblia_Master_Redes.md)...")
    docs_dir = PROJECT_ROOT / "docs"
    docs_dir.mkdir(exist_ok=True)
    bible_file = docs_dir / "Biblia_Master_Redes.md"

    md = []
    md.append("# 📘 Biblia Master de Configuración & Troubleshooting de Redes Multi-Vendor")
    md.append("## Guía Integral Especializada CCNA, CCNP, Fortinet NSE4-NSE8, Sophos Certified Architect & Service Provider\n")
    md.append("> **Repositorio Oficial:** [https://github.com/junipermerchan/net_tshoot_dashboard.git](https://github.com/junipermerchan/net_tshoot_dashboard.git)\n")
    md.append("---\n")

    # Tabla de Contenidos
    md.append("## 📌 Tabla de Contenidos")
    md.append("1. [Matriz de Fabricantes y Modelos de Hardware Soportaods](#1-matriz-de-fabricantes-y-modelos-de-hardware-soportados)")
    md.append("2. [Conceptos y Arquitectura de Sistemas Operativos por Fabricante](#2-conceptos-y-arquitectura-de-sistemas-operativos-por-fabricante)")
    md.append("3. [Módulos de Configuración Máster CCNA/CCNP & Enterprise (31 Módulos)](#3-módulos-de-configuración-máster-ccnaccnp--enterprise)")
    md.append("4. [Procedimientos de Búsqueda Operacional de Red (MAC, ARP, BGP, OSPF, STP, DHCP, SD-WAN)](#4-procedimientos-de-búsqueda-operacional-de-red)")
    md.append("5. [Flujos Diagnósticos de Troubleshooting por Niveles Tier 1 a Tier 4](#5-flujos-diagnósticos-de-troubleshooting-por-niveles)")
    md.append("\n---\n")

    # 1. Matriz de Fabricantes
    md.append("## 1. Matriz de Fabricantes y Modelos de Hardware Soportados\n")
    md.append("| Código Vendor | Nombre del Fabricante | Modelos Exactos de Hardware Indexados |")
    md.append("|---|---|---|")
    for v_key, v_name in VendorMap.items():
        models = EQUIPMENT_MODELS.get(v_key, ["Genérico"])
        models_str = ", ".join(models)
        md.append(f"| `{v_key}` | **{v_name}** | {models_str} |")
    md.append("\n---\n")

    # 2. Conceptos y Arquitectura
    md.append("## 2. Conceptos y Arquitectura de Sistemas Operativos por Fabricante\n")
    for v_key, v_info in VENDOR_CONCEPTS_MATRIX.items():
        v_name = VendorMap.get(v_key, v_key)
        md.append(f"### 🏷️ Fabricante: {v_name} (`{v_key}`)")
        md.append(f"- {v_info.get('architecture_note', '')}")
        md.append(f"- {v_info.get('cli_philosophy', '')}")
        md.append(f"- **Comandos Clave**: {v_info.get('key_commands', '')}\n")
    md.append("---\n")

    # 3. Módulos de Configuración Máster
    md.append("## 3. Módulos de Configuración Máster CCNA/CCNP & Enterprise\n")
    for tmpl_key, tmpl_data in CONFIG_TEMPLATES.items():
        md.append(f"### {tmpl_data.get('title', tmpl_key)}")
        md.append(f"*{tmpl_data.get('description', '')}*\n")
        vendors = tmpl_data.get("vendors", {})
        for vk, vd in vendors.items():
            md.append(f"#### 📟 Fabricante: {vd.get('vendor_name', vk)}")
            md.append("```bash")
            md.append(vd.get("code", ""))
            md.append("```")
            md.append("**Desglose de Comandos:**")
            for b in vd.get("breakdown", []):
                md.append(f"- `{b['cmd']}`: {b['desc']}")
            md.append("")
    md.append("---\n")

    # 4. Búsqueda Operacional
    md.append("## 4. Procedimientos de Búsqueda Operacional de Red\n")
    op_keys = [k for k in KB.keys() if k.startswith("op_search_")]
    for opk in op_keys:
        opdata = KB[opk]
        md.append(f"### {opdata.get('name', opk)}")
        md.append(f"*{opdata.get('description', '')}*\n")
        steps = opdata.get("steps", {})
        for sk, sd in steps.items():
            md.append(f"#### Paso: {sd.get('title', sk)}")
            md.append(f"- **Capa OSI**: {sd.get('osi_layer', 'N/A')}")
            md.append(f"- **Dominio de Red**: {sd.get('network_domain', 'N/A')}")
            md.append(f"- **Metodología**: {sd.get('methodology', 'N/A')}")
            md.append(f"- **Resultado Esperado**: {sd.get('expected', 'N/A')}\n")
            md.append("**Comandos por Fabricante:**")
            cmds = sd.get("commands", {})
            for vk, clist in cmds.items():
                vname = VendorMap.get(vk, vk)
                md.append(f"- **{vname}**:")
                if isinstance(clist, list):
                    for c in clist:
                        md.append(f"  - `{c}`")
                elif isinstance(clist, dict):
                    for tier_k, t_clist in clist.items():
                        md.append(f"  - *{tier_k}*:")
                        for c in t_clist:
                            md.append(f"    - `{c}`")
            md.append("")
    md.append("---\n")

    # 5. Flujos Diagnósticos por Niveles Tier 1 - Tier 4
    md.append("## 5. Flujos Diagnósticos de Troubleshooting por Niveles (Tier 1 a Tier 4)\n")
    ts_keys = [k for k in KB.keys() if not k.endswith("_config") and not k.startswith("op_search_")]
    for tsk in ts_keys:
        tsdata = KB[tsk]
        md.append(f"### Tecnología: {tsdata.get('name', tsk)}")
        steps = tsdata.get("steps", {})
        md.append(f"Total de pasos diagnósticos: **{len(steps)}**\n")
        for sk, sd in steps.items():
            md.append(f"#### Paso `{sk}`: {sd.get('title', sk)} (Tier {sd.get('tier', 1)})")
            md.append(f"**Descripción**: {sd.get('body', '')}\n")
            md.append(f"**Resultado Esperado**: {sd.get('expected', '')}\n")
            if "hypothesis" in sd:
                md.append(f"🔬 **Hipótesis Científica**: {sd['hypothesis']}")
            if "fix" in sd:
                md.append(f"🛠️ **Solución Rápida (Quick Fix)**: {sd['fix']}")
            md.append("")

    # Escribir a archivo
    bible_file.write_text("\n".join(md), encoding="utf-8")
    print(f"✅ 'Biblia_Master_Redes.md' generada exitosamente en {bible_file}")


def main():
    print("=" * 70)
    print("🚀 SCRIPT MAESTRO DE CONSTRUCCIÓN & MEJORA DE LA APLICACIÓN")
    print("=" * 70)

    # 1. Validar Integridad
    print("\n[1/3] Ejecutando validación estricta de integridad...")
    is_valid = validate()
    if not is_valid:
        print("\n❌ Se encontraron errores de integridad. Corrija los errores antes de continuar.")
        sys.exit(1)
    print("✅ Integridad verificada: 0 Errores.")

    # 2. Re-exportar web/data.js, web/db.js y web/devices_db.js
    print("\n[2/3] Empaquetando y re-exportando base de conocimiento a web/data.js, web/db.js y web/devices_db.js...")
    export_data()
    generate_db_js()
    generate_devices_db_js()

    # 3. Generar la Biblia Master de Redes Markdown
    print("\n[3/3] Construyendo la Biblia Master de Redes (docs/Biblia_Master_Redes.md)...")
    generate_network_bible_markdown()

    print("\n" + "=" * 70)
    print("🎉 ¡CONSTRUCCIÓN Y MEJORA COMPLETADA CON ÉXITO!")
    print("La aplicación está 100% optimizada, validada y documentada.")
    print("=" * 70)


if __name__ == "__main__":
    main()
