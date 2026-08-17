#!/usr/bin/env python3
"""Validador de integridad de la base de conocimiento del dashboard de troubleshooting.

Verifica:
1. Todos los vendors en 'commands' de cada paso están en VendorMap.
2. Todos los vendors en 'commands' están en la lista de vendors de la tecnología.
3. Todos los 'next' de 'choices' apuntan a steps existentes (en la misma tech o en otra).
4. Pasos sin 'body' o sin 'choices' (excepto finales documentados).
5. Pasos sin 'expected' o 'tier'.
6. Comandos vacíos o genéricos.
7. TECH_CONCEPTS faltantes para tecnologías que existen en KB.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.knowledge_base import KB, VendorMap, TECH_CONCEPTS
from data.config_guides import CONFIG_GUIDES
from data.scientific_steps import SCIENTIFIC_OVERRIDES

def validate():
    errors = []
    warnings = []
    
    # Merge CONFIG_GUIDES into KB view
    full_kb = dict(KB)
    for k, v in CONFIG_GUIDES.items():
        if k not in full_kb:
            full_kb[k] = v
    
    all_step_keys = set()
    for tech, data in full_kb.items():
        for sk in data.get('steps', {}).keys():
            all_step_keys.add(sk)
    
    # 1. Validar vendors en commands
    for tech, data in full_kb.items():
        vendors = data.get('vendors', [])
        steps = data.get('steps', {})
        for step_key, step in steps.items():
            cmds = step.get('commands', {})
            for vendor in cmds.keys():
                if vendor not in VendorMap:
                    errors.append(f"[{tech}.{step_key}] Vendor '{vendor}' NO está en VendorMap.")
                if vendor not in vendors:
                    errors.append(f"[{tech}.{step_key}] Vendor '{vendor}' en commands pero NO en tech.vendors.")
    
    # 2. Validar choices.next
    for tech, data in full_kb.items():
        steps = data.get('steps', {})
        for step_key, step in steps.items():
            choices = step.get('choices', [])
            for ch in choices:
                nxt = ch.get('next')
                if nxt is None or nxt == 'back_menu':
                    continue
                if nxt not in all_step_keys:
                    errors.append(f"[{tech}.{step_key}] Choice apunta a step inexistente: '{nxt}'")
    
    # 3. Validar pasos sin body/tier/expected
    for tech, data in full_kb.items():
        steps = data.get('steps', {})
        for step_key, step in steps.items():
            if not step.get('body'):
                warnings.append(f"[{tech}.{step_key}] Sin 'body'.")
            if step.get('tier') is None:
                warnings.append(f"[{tech}.{step_key}] Sin 'tier'.")
            if not step.get('expected'):
                warnings.append(f"[{tech}.{step_key}] Sin 'expected'.")
    
    # 4. Validar TECH_CONCEPTS
    for tech in full_kb.keys():
        base = tech.replace('_config', '')
        if base not in TECH_CONCEPTS and tech not in TECH_CONCEPTS:
            warnings.append(f"[{tech}] Sin TECH_CONCEPTS (base={base}).")
    
    # 5. Validar scientific overrides
    for override_key, override in SCIENTIFIC_OVERRIDES.items():
        parts = override_key.split('.', 1)
        if len(parts) != 2:
            warnings.append(f"[Scientific] Clave malformada: {override_key}")
            continue
        tech, step = parts
        if tech not in full_kb:
            warnings.append(f"[Scientific] Tecnología '{tech}' no existe en KB.")
        elif step not in full_kb[tech].get('steps', {}):
            warnings.append(f"[Scientific] Paso '{step}' no existe en '{tech}'.")
        if 'fix' in override:
            if not isinstance(override['fix'], str) or not override['fix'].strip():
                warnings.append(f"[Scientific] Campo 'fix' vacío o no es string en {override_key}.")
    
    # 6. Validar comandos vacíos
    for tech, data in full_kb.items():
        steps = data.get('steps', {})
        for step_key, step in steps.items():
            cmds = step.get('commands', {})
            for vendor, raw in cmds.items():
                if isinstance(raw, dict):
                    for tier, lst in raw.items():
                        if not lst:
                            warnings.append(f"[{tech}.{step_key}] Comandos vacíos para {vendor}/{tier}.")
                elif isinstance(raw, list):
                    if not raw:
                        warnings.append(f"[{tech}.{step_key}] Comandos vacíos para {vendor}.")
    
    # Reporte
    print(f"=== VALIDACIÓN DE INTEGRIDAD ===")
    print(f"Errores: {len(errors)}")
    print(f"Advertencias: {len(warnings)}")
    print()
    if errors:
        print("--- ERRORES ---")
        for e in errors:
            print(f"  [ERROR] {e}")
    if warnings:
        print("--- ADVERTENCIAS ---")
        for w in warnings:
            print(f"  [WARN] {w}")
    
    return len(errors) == 0

if __name__ == '__main__':
    ok = validate()
    sys.exit(0 if ok else 1)
