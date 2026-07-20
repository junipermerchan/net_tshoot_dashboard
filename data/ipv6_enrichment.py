"""
Módulo de Enriquecimiento de IPv6 Avanzado para Network Tshoot Dashboard.
Añade programáticamente soporte y guías de nivel Enterprise/Service Provider (CCIE/JNCIE) 
de IPv6 en todas las tecnologías, vendors y comandos simulados.
Permite la alternancia de descripciones, títulos y comportamientos esperados en la UI.
"""

import json
import copy
from pathlib import Path
from typing import Dict, Any

def enrich_with_ipv6(base: Dict[str, Any]):
    # Enriquecer conceptos globales de IPv6 con documentación oficial de Junos OS
    try:
        from data.knowledge_base import TECH_CONCEPTS
        if 'ipv6' in TECH_CONCEPTS:
            TECH_CONCEPTS['ipv6']['definition'] = (
                "IPv6 (Internet Protocol Version 6) es el sucesor de IPv4 diseñado por el IETF para resolver "
                "el agotamiento de direcciones. Introduce un espacio de direccionamiento de 128 bits (aproximadamente "
                "3.4x10^38 direcciones), una cabecera fija simplificada de 40 bytes dividida en 8 campos principales "
                "para acelerar la conmutación por hardware, y delega funciones auxiliares a extensiones de cabecera (Extension Headers)."
            )
            TECH_CONCEPTS['ipv6']['key_concepts'] = (
                "• **Link-Local Address (fe80::/10):** Direcciones de enlace local autogeneradas obligatorias para comunicación interna y señalización de protocolos de enrutamiento (ej. OSPFv3).\n"
                "• **Junos Routing Tables:** En Junos OS, las tablas de enrutamiento IPv6 son `inet6.0` (Unicast IPv6 global) e `instance-name.inet6.0` (para tablas de routing VRF o Virtual Router).\n"
                "• **Junos Route Preferences (AD):** Preferencia por defecto de Junos para la selección de mejores rutas en `inet6.0`:\n"
                "  - Direct: 0\n"
                "  - Static: 5\n"
                "  - OSPFv3 Internal: 10\n"
                "  - IS-IS Level 1 Internal: 15\n"
                "  - IS-IS Level 2 Internal: 18\n"
                "  - RIPng: 100\n"
                "  - OSPFv3 External: 150\n"
                "  - BGP: 170\n"
                "• **NDP (Neighbor Discovery Protocol):** Sustituto de ARP en IPv4, basado en mensajes ICMPv6 de multidifusión de nodo solicitado (Solicited-Node Multicast) para mapear IPs a direcciones MAC físicas.\n"
                "• **SLAAC (Stateless Address Autoconfiguration):** Mecanismo de autoconfiguración sin estado basado en anuncios de Router Advertisements (RA)."
            )
            TECH_CONCEPTS['ipv6']['architecture'] = (
                "La arquitectura IPv6 estandariza la cabecera del paquete a 40 bytes fijos que incluyen: "
                "Version (4 bits), Traffic Class (8 bits, DiffServ/CoS), Flow Label (20 bits para etiquetar flujos), "
                "Payload Length (16 bits), Next Header (8 bits, indica la extensión de cabecera o el protocolo de capa superior), "
                "Hop Limit (8 bits, equivalente a TTL), Source Address (128 bits) y Destination Address (128 bits). "
                "Se eliminan los campos de checksum L3 (delegados a L4) y de fragmentación de cabecera (los routers no fragmentan "
                "tráfico en tránsito; el emisor ejecuta Path MTU Discovery)."
            )
            TECH_CONCEPTS['ipv6']['control_vs_data'] = (
                "• **Plano de Control:** Intercambio de mensajes NDP (Neighbor Solicitation [Type 135], Neighbor Advertisement [Type 136], "
                "Router Solicitation [Type 137], Router Advertisement [Type 138]). Las adyacencias locales transicionan por los estados de neighbor "
                "cache: Incomplete, Reachable, Stale, Delay y Probe.\n"
                "• **Plano de Datos:** Reenvío de alta velocidad de paquetes a nivel de hardware ASIC / PFE basándose en lookup más largo (Longest Match Prefix) de la tabla FIB de IPv6 sincronizada por el kernel."
            )
            TECH_CONCEPTS['ipv6']['troubleshooting_strategy'] = (
                "1. **Paso 1 (Ping Link-Local):** Validar accesibilidad básica de enlace físico enviando ping a direcciones `fe80::` "
                "especificando obligatoriamente la interfaz física de salida (ej: `ping fe80::2%ge-0/0/1.0` en Juniper o `ping fe80::2` indicando "
                "la interfaz en Cisco).\n"
                "2. **Paso 2 (Neighbor Cache Verification):** Comprobar resolución MAC/IP en Juniper usando `show ipv6 neighbors` o `show arp` de IPv6.\n"
                "3. **Paso 3 (Path MTU & PMTUD):** Diagnosticar caídas de adyacencias o problemas de carga de páginas debido a desajustes en el tamaño "
                "máximo de transmisión, verificando que no se esté bloqueando el mensaje ICMPv6 Packet Too Big (Type 2).\n"
                "4. **Paso 4 (RA & DHCPv6 Inspection):** Comprobar que RA Guard o ND Inspection no estén filtrando de forma errónea las respuestas del router o servidor DHCPv6 central."
            )
            TECH_CONCEPTS['ipv6']['configuration_basics'] = (
                "• Habilitar reenvío global: `set protocols router-advertisement` o `ipv6 unicast-routing`.\n"
                "• Configurar IPv6 en interfaz Junos: `set interfaces ge-0/0/1 unit 0 family inet6 address 2001:db8::1/64`.\n"
                "• Configurar anuncios RA: `set protocols router-advertisement interface ge-0/0/1.0 prefix 2001:db8::/64`."
            )

        # OSPFv3 Theory Concepts
        TECH_CONCEPTS['ospf_ipv6'] = {
            'definition': (
                "OSPFv3 (RFC 5340) es la evolución de OSPF para dar soporte nativo a IPv6. A diferencia de OSPFv2, "
                "OSPFv3 se ejecuta por enlace (per-link) en lugar de por subred (per-subnet), permitiendo "
                "habilitar múltiples instancias en un enlace físico y desligar el direccionamiento de la topología."
            ),
            'key_concepts': (
                "• **Adyacencia Link-Local:** OSPFv3 forma vecinos utilizando únicamente direcciones de enlace local (link-local - fe80::/10).\n"
                "• **Router ID de 32 bits:** Es obligatorio configurar manualmente un Router ID de 32 bits (ej: 1.1.1.1) ya que IPv6 no autogenera Router IDs de 32 bits.\n"
                "• **Nuevos LSAs:** Introduce LSAs Tipo 8 (Link LSA) y Tipo 9 (Intra-Area-Prefix LSA) para propagar prefijos sin recalcular el árbol SPF completo."
            ),
            'architecture': (
                "Funciona sobre el protocolo IP 89 utilizando direccionamiento de multicast link-local (`ff02::5` para todos los routers OSPFv3 "
                "y `ff02::6` para DR/BDR). Los paquetes se originan siempre con la IP de enlace local del puerto."
            )
        }
    except Exception:
        pass

    # 1. Hacer copia de respaldo de los comandos IPv4 originales para cada paso
    for tech_key, tech in base.items():
        if isinstance(tech, dict) and 'steps' in tech:
            for step_key, step in tech['steps'].items():
                if isinstance(step, dict) and 'commands' in step:
                    step['commands_ipv4'] = copy.deepcopy(step['commands'])

    # 2. Cargar los overrides de IPv6 desde el archivo JSON
    try:
        overrides_path = Path(__file__).resolve().parent / 'ipv6_overrides.json'
        if overrides_path.exists():
            payload = json.loads(overrides_path.read_text(encoding='utf-8'))
            kb_overrides = payload.get('kb_overrides', {})
            
            # Aplicar overrides a KB (base)
            for tech_key, steps_dict in kb_overrides.items():
                if tech_key not in base:
                    base[tech_key] = {'steps': {}, 'vendors': []}
                tech = base[tech_key]
                if 'steps' not in tech:
                    tech['steps'] = {}
                
                # Asegurar vendors de la tech
                if 'vendors' not in tech:
                    tech['vendors'] = []
                
                for step_key, step_data in steps_dict.items():
                    if step_key not in tech['steps']:
                        tech['steps'][step_key] = {}
                    step = tech['steps'][step_key]
                    
                    # Copiar todos los campos enriquecidos de IPv6
                    for field, value in step_data.items():
                        step[field] = copy.deepcopy(value)
                        
                    # Asegurar que todos los vendors en comandos estén en tech['vendors']
                    for cmd_field in ['commands', 'commands_ipv6', 'commands_ipv4']:
                        if cmd_field in step and isinstance(step[cmd_field], dict):
                            for v in step[cmd_field].keys():
                                if v not in tech['vendors']:
                                    tech['vendors'].append(v)
            
            # Aplicar salidas simuladas
            simulated_outputs = payload.get('simulated_outputs', {})
            try:
                from data.simulated_outputs import SIMULATED_OUTPUTS
                for tech_key, steps_dict in simulated_outputs.items():
                    if tech_key not in SIMULATED_OUTPUTS:
                        SIMULATED_OUTPUTS[tech_key] = {}
                    for step_key, vendors_dict in steps_dict.items():
                        if step_key not in SIMULATED_OUTPUTS[tech_key]:
                            SIMULATED_OUTPUTS[tech_key][step_key] = {}
                        for vendor, cmds_dict in vendors_dict.items():
                            if vendor not in SIMULATED_OUTPUTS[tech_key][step_key]:
                                SIMULATED_OUTPUTS[tech_key][step_key][vendor] = {}
                            for cmd, output in cmds_dict.items():
                                SIMULATED_OUTPUTS[tech_key][step_key][vendor][cmd] = output
            except Exception:
                pass
    except Exception:
        pass

    # Mapeo de traducciones genéricas para fallback
    translations_map = {
        'juniper': {
            'show ip route': 'show route table inet6.0',
            'show ip interface brief': 'show interfaces terse',
            'ping': 'ping',
            'ip route': 'ipv6 route',
        },
        'cisco_iosxe': {
            'show ip route': 'show ipv6 route',
            'show ip interface brief': 'show ipv6 interface brief',
            'ping': 'ping ipv6',
            'ip route': 'ipv6 route',
        },
        'cisco_iosxr': {
            'show ip route': 'show ipv6 route',
            'show ip interface brief': 'show ipv6 interface brief',
            'ping': 'ping ipv6',
            'ip route': 'ipv6 route',
        },
        'arista': {
            'show ip route': 'show ipv6 route',
            'show ip interface brief': 'show ipv6 interface brief',
            'ping': 'ping ipv6',
            'ip route': 'ipv6 route',
        },
        'huawei': {
            'display ip routing-table': 'display ipv6 routing-table',
            'display ip interface brief': 'display ipv6 interface brief',
            'ping': 'ping ipv6',
            'ip route-static': 'ipv6 route-static',
        },
        'fortinet': {
            'get router info routing-table': 'get router info6 routing-table',
            'ping': 'execute ping6',
        },
        'mikrotik': {
            '/ip route': '/ipv6 route',
            '/ip address': '/ipv6 address',
        }
    }

    # 3. Separar comandos IPv4 e IPv6 finales y aplicar traducción genérica
    for tech_key, tech in base.items():
        if isinstance(tech, dict) and 'steps' in tech:
            for step_key, step in tech['steps'].items():
                if isinstance(step, dict):
                    # Si el paso no tiene title_ipv6 o body_ipv6, aplicar reemplazo genérico
                    if 'title_ipv6' not in step and step.get('title'):
                        step['title_ipv6'] = step['title'] + " (IPv6)"
                    if 'body_ipv6' not in step and step.get('body'):
                        body_v6 = step['body']
                        body_v6 = body_v6.replace('IPv4', 'IPv6')
                        body_v6 = body_v6.replace('OSPF', 'OSPFv3')
                        body_v6 = body_v6.replace('RIPv2', 'RIPng')
                        body_v6 = body_v6.replace('DHCP', 'DHCPv6')
                        body_v6 = body_v6.replace('BGP', 'MP-BGP')
                        step['body_ipv6'] = body_v6
                    if 'expected_ipv6' not in step and step.get('expected'):
                        exp_v6 = step['expected']
                        exp_v6 = exp_v6.replace('IPv4', 'IPv6')
                        exp_v6 = exp_v6.replace('OSPF', 'OSPFv3')
                        exp_v6 = exp_v6.replace('RIPv2', 'RIPng')
                        exp_v6 = exp_v6.replace('DHCP', 'DHCPv6')
                        exp_v6 = exp_v6.replace('BGP', 'MP-BGP')
                        step['expected_ipv6'] = exp_v6
                        
                    # Si el paso no tiene commands_ipv6 (no especificado en el override), crearlo traduciendo commands
                    if 'commands_ipv6' not in step:
                        step['commands_ipv6'] = copy.deepcopy(step.get('commands', {}))
                        for vendor, rules in translations_map.items():
                            if vendor in step['commands_ipv6']:
                                raw = step['commands_ipv6'][vendor]
                                if isinstance(raw, dict):
                                    for tier, cmd_list in raw.items():
                                        new_list = []
                                        for cmd in cmd_list:
                                            translated = cmd
                                            for k, v in rules.items():
                                                if k in cmd:
                                                    translated = cmd.replace(k, v)
                                            new_list.append(translated)
                                        raw[tier] = new_list
                                elif isinstance(raw, list):
                                    new_list = []
                                    for cmd in raw:
                                        translated = cmd
                                        for k, v in rules.items():
                                            if k in cmd:
                                                translated = cmd.replace(k, v)
                                        new_list.append(translated)
                                    step['commands_ipv6'][vendor] = new_list

                    # Restaurar el original de IPv4 para commands
                    if 'commands_ipv4' in step:
                        step['commands'] = step['commands_ipv4']
                        del step['commands_ipv4']
