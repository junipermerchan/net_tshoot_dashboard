"""
Utilidades para generar configuraciones y estados de referencia (Golden Config / Línea Base)
a partir de salidas de consola simuladas, y calcular diferencias visuales (diffs).
"""

import re
from typing import Tuple, List

def generate_golden_output(cmd: str, current_output: str) -> str:
    """
    Genera dinámicamente una versión saludable (Golden Config / Línea Base)
    de la salida actual del comando usando reglas de reemplazo heurísticas.
    """
    if not current_output:
        return ""
        
    cmd_lower = cmd.lower()
    golden = current_output
    
    # 1. Reglas generales de Estado de Interfaces y Protocolos
    # Reemplazar Down/down por Up/up (respetando mayúsculas/minúsculas)
    golden = re.sub(r'\bdown\b', 'up', golden)
    golden = re.sub(r'\bDown\b', 'Up', golden)
    golden = re.sub(r'\bDOWN\b', 'UP', golden)
    golden = re.sub(r'\bshutdown\b', 'no shutdown', golden)
    golden = re.sub(r'\bShutdown\b', 'No Shutdown', golden)
    
    # Reemplazar Dn (down en L2VPN Juniper) por Up
    golden = re.sub(r'\bDn\b', 'Up', golden)
    # Reemplazar abreviaciones de error en Juniper L2circuit
    golden = re.sub(r'\bEI\b', 'Up', golden)
    golden = re.sub(r'\bEM\b', 'Up', golden)
    golden = re.sub(r'\bVM\b', 'Up', golden)
    golden = re.sub(r'\bOL\b', 'Up', golden)
    golden = re.sub(r'\bWE\b', 'Up', golden)
    golden = re.sub(r'\bNC\b', 'Up', golden)

    # 2. Reglas de BGP
    if 'bgp' in cmd_lower:
        # Reemplazar estados Idle o Active por Established
        golden = re.sub(r'\bIdle\b', 'Established', golden)
        golden = re.sub(r'\bActive\b', 'Established', golden)
        golden = re.sub(r'\bidle\b', 'established', golden)
        golden = re.sub(r'\bactive\b', 'established', golden)
        golden = re.sub(r'\bIDLE\b', 'ESTABLISHED', golden)
        golden = re.sub(r'\bACTIVE\b', 'ESTABLISHED', golden)
        # Reemplazar prefijos recibidos de 0 a un número saludable (ej. 150)
        golden = re.sub(r'\b0\s+routes\b', '150 routes', golden)
        golden = re.sub(r'\b0\s+prefixes\b', '150 prefixes', golden)
        golden = re.sub(r'\b0\s+received\b', '150 received', golden)

    # 3. Reglas de OSPF e IS-IS
    if 'ospf' in cmd_lower or 'isis' in cmd_lower or 'isis_config' in cmd_lower:
        # Reemplazar estados de vecino de Down/Init/Attempt/2-Way/Exchange/Loading a Full o Up
        golden = re.sub(r'\bInit\b', 'Full', golden)
        golden = re.sub(r'\bAttempt\b', 'Full', golden)
        golden = re.sub(r'\bExchange\b', 'Full', golden)
        golden = re.sub(r'\bLoading\b', 'Full', golden)
        golden = re.sub(r'\b2-Way\b', 'Full', golden)
        # Cambiar prioridad OSPF de 0 (no DR/BDR) a 1 o 128
        golden = re.sub(r'\bPri:\s*0\b', 'Pri: 128', golden)

    # 4. Reglas de LACP / Switch L2
    if 'lacp' in cmd_lower or 'etherchannel' in cmd_lower or 'port-channel' in cmd_lower:
        # Reemplazar estados individuales o suspendidos por activos/en bundle
        golden = re.sub(r'\bIndividual\b', 'Bundle', golden)
        golden = re.sub(r'\bSuspended\b', 'Bundle', golden)
        golden = re.sub(r'\bindividual\b', 'bundle', golden)
        golden = re.sub(r'\bsuspended\b', 'bundle', golden)
        golden = re.sub(r'\b(state|status):\s*(down|Down)\b', r'\1: Up', golden)

    # 5. Reglas de Contadores de Error (poner a 0 para estado saludable)
    golden = re.sub(r'\b(?:errors|Errors|ERRORS)\s*:\s*\d+', 'errors: 0', golden)
    golden = re.sub(r'\b(?:discarded|discards|Discards)\s*:\s*\d+', 'discards: 0', golden)
    golden = re.sub(r'\b(?:input errors|input error)\s*:\s*\d+', 'input errors: 0', golden)
    golden = re.sub(r'\b(?:output errors|output error)\s*:\s*\d+', 'output errors: 0', golden)
    golden = re.sub(r'\b(?:collisions|Collisions)\s*:\s*\d+', 'collisions: 0', golden)
    
    # 6. Reglas de MTU y Mismatches
    golden = re.sub(r'\bMTU\s+mismatch\b', 'MTU match', golden)
    golden = re.sub(r'\bmismatch\b', 'match', golden)
    golden = re.sub(r'\bMismatch\b', 'Match', golden)
    golden = re.sub(r'\bMISMATCH\b', 'MATCH', golden)
    
    # 7. Reglas de Fibra Óptica (GPON / OLT / ONT)
    if 'gpon' in cmd_lower or 'ont' in cmd_lower or 'olt' in cmd_lower:
        # Potencia óptica baja/crítica a potencia normal
        # e.g., -32.5 dBm a -19.2 dBm
        golden = re.sub(r'-\d+\.\d+\s*dBm', '-19.2 dBm', golden)
        golden = re.sub(r'optical power: low', 'optical power: normal', golden)
        golden = re.sub(r'ranging state: \w+', 'ranging state: operation', golden)
        golden = re.sub(r'auth state: \w+', 'auth state: operational', golden)
        golden = re.sub(r'phase: \w+', 'phase: operational', golden)
        
    return golden

def get_diff_lines(current: str, golden: str) -> List[Tuple[str, str, str]]:
    """
    Compara línea a línea las dos salidas.
    Retorna una lista de tuplas (tipo, linea_actual, linea_golden)
    donde tipo puede ser:
    - 'equal': las líneas son iguales
    - 'modified': las líneas difieren
    """
    curr_lines = current.split('\n')
    gold_lines = golden.split('\n')
    
    result = []
    max_len = max(len(curr_lines), len(gold_lines))
    
    for i in range(max_len):
        c_line = curr_lines[i] if i < len(curr_lines) else ""
        g_line = gold_lines[i] if i < len(gold_lines) else ""
        
        if c_line == g_line:
            result.append(('equal', c_line, g_line))
        else:
            result.append(('modified', c_line, g_line))
            
    return result
