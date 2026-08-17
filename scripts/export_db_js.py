#!/usr/bin/env python3
"""
export_db_js.py — Exporta la Base de Conocimiento de Python a un archivo ES6 Module nativo 'web/db.js' (export const networkData = [...]).
"""

import sys
import json
import re
from pathlib import Path

# Ajustar sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.knowledge_base import KB, VendorMap, EQUIPMENT_MODELS


def extract_variables(text):
    """Extrae marcadores como <peer_ip> o {{peer_ip}} y devuelve lista de objetos variable."""
    if not text:
        return []
    matches = re.findall(r'<([A-Za-z0-9_-]+)>|\{\{([A-Za-z0-9_-]+)\}\}', text)
    vars_found = []
    seen = set()
    for m1, m2 in matches:
        v_name = m1 or m2
        if v_name and v_name not in seen:
            seen.add(v_name)
            vars_found.append({
                "id": v_name,
                "label": v_name.replace("_", " ").title(),
                "default": f"192.168.10.2" if "ip" in v_name else ("65001" if "as" in v_name else "default")
            })
    return vars_found


def generate_db_js():
    print("📦 Exportando Base de Datos a formato ES6 Module ('web/db.js')...")
    network_data = []

    for tech_key, tech_data in KB.items():
        is_config = tech_key.endswith("_config")
        entry_type = "configuration" if is_config else "troubleshooting"
        category = "Configuración Máster" if is_config else "Troubleshooting Diagnóstico"

        # Extraer variables de todos los comandos
        all_vars = []
        steps_list = []
        step_idx = 1

        for step_key, step_data in tech_data.get("steps", {}).items():
            cmds_dict = {}
            raw_cmds = step_data.get("commands", {})
            for vk, clist in raw_cmds.items():
                if isinstance(clist, list):
                    cmd_str = "\n".join(clist)
                elif isinstance(clist, dict):
                    flat_cmds = []
                    for tk, sublist in clist.items():
                        flat_cmds.extend(sublist)
                    cmd_str = "\n".join(flat_cmds)
                else:
                    cmd_str = str(clist)

                cmds_dict[vk] = cmd_str
                # Extraer variables
                step_vars = extract_variables(cmd_str)
                for sv in step_vars:
                    if sv["id"] not in [x["id"] for x in all_vars]:
                        all_vars.append(sv)

            steps_list.append({
                "step": step_idx,
                "title": step_data.get("title", step_key),
                "goal": step_data.get("body", "Realizar verificación de estado y diagnóstico."),
                "expected": step_data.get("expected", "Diagnóstico exitoso sin errores."),
                "commands": cmds_dict
            })
            step_idx += 1

        network_data.append({
            "id": tech_key,
            "title": tech_data.get("name", tech_key),
            "category": category,
            "type": entry_type,
            "tier": 1,
            "layer": tech_data.get("steps", {}).get(list(tech_data.get("steps", {}).keys())[0], {}).get("osi_layer", "Capa 3 / Capa 4") if tech_data.get("steps") else "Capa 3",
            "description": f"Guía integral de {tech_data.get('name', tech_key)} con comandos nativos por fabricante.",
            "variables": all_vars,
            "steps": steps_list
        })

    out_file = PROJECT_ROOT / "web" / "db.js"
    json_str = json.dumps(network_data, ensure_ascii=False, indent=2)
    js_content = f"// db.js - Base de datos de procedimientos diagnósticos y configuración (ES6 Module)\nexport const networkData = {json_str};\n"

    out_file.write_text(js_content, encoding="utf-8")
    print(f"✅ 'web/db.js' generado exitosamente ({len(network_data)} procedimientos indexados).")


if __name__ == "__main__":
    generate_db_js()
