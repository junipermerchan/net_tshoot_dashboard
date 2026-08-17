#!/usr/bin/env python3
import sys
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def export_data():
    print("Importando base de datos en Python...")
    try:
        from data.knowledge_base import KB, VendorMap, TECH_CONCEPTS
        from data.packet_walkthroughs import PACKET_WALKTHROUGHS, WALKTHROUGH_ALIASES
        from data.simulated_outputs import SIMULATED_OUTPUTS
        from data.change_tickets import CHANGE_TICKETS
        from data.config_templates import CONFIG_TEMPLATES
    except Exception as e:
        print(f"Error al importar datos: {e}")
        sys.exit(1)

    print("Empaquetando datos...")
    unified_data = {
        "KB": KB,
        "VendorMap": VendorMap,
        "TECH_CONCEPTS": TECH_CONCEPTS,
        "PACKET_WALKTHROUGHS": PACKET_WALKTHROUGHS,
        "WALKTHROUGH_ALIASES": WALKTHROUGH_ALIASES,
        "simulatedOutputs": SIMULATED_OUTPUTS,
        "CHANGE_TICKETS": CHANGE_TICKETS,
        "CONFIG_TEMPLATES": CONFIG_TEMPLATES
    }


    output_dir = PROJECT_ROOT / "web"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "data.js"

    print(f"Escribiendo a {output_file}...")
    try:
        # Convert dictionary to JSON formatted string
        json_data = json.dumps(unified_data, ensure_ascii=False, indent=2)
        js_content = f"// Autogenerado por export.py. No editar directamente.\nconst NET_TSHOOT_DATA = {json_data};\n"
        output_file.write_text(js_content, encoding="utf-8")
        print("¡Exportación exitosa!")
    except Exception as e:
        print(f"Error al escribir archivo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    export_data()
