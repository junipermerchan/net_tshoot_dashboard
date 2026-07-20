"""
Motor de Diagnóstico Automático (Diagnóstico Mágico) de Redes.
Analiza texto libre (configuraciones, syslogs o salidas de consola)
para identificar fallas de protocolo y sugerir soluciones específicas por vendor.
"""

import re
from typing import Dict, Any, Optional, List

VENDORS = {
    "cisco_iosxe": "Cisco IOS-XE / NX-OS",
    "cisco_iosxr": "Cisco IOS-XR",
    "juniper": "Juniper JunOS",
    "mikrotik": "MikroTik RouterOS",
    "fortinet": "Fortinet FortiOS",
    "arista": "Arista EOS",
    "nokia": "Nokia SR OS",
    "huawei": "Huawei VRP",
    "zte": "ZTE GPON OLT",
    "adtran": "ADTRAN AOS",
    "linux": "Linux"
}

def detect_vendor(text: str) -> Optional[str]:
    """Intenta detectar el vendor de forma automática analizando el texto."""
    text_lower = text.lower()
    
    # Juniper
    if "display set" in text or "show configuration protocols" in text or "show configuration interfaces" in text or "commit |" in text:
        return "juniper"
    if re.search(r'\b(ge|xe|et)-\d+/\d+/\d+', text_lower) or "juniper networks" in text_lower:
        return "juniper"
        
    # Cisco IOS-XR
    if "rp/0/rsp0/cpu0" in text_lower or "show running-config formal" in text_lower or "ios-xr" in text_lower:
        return "cisco_iosxr"
        
    # Cisco IOS-XE / Generic
    if "show ip interface brief" in text_lower or "show ip route vrf" in text_lower or "show running-config" in text_lower:
        if "ios-xr" not in text_lower:
            return "cisco_iosxe"
            
    # Arista
    if "arista eos" in text_lower or "show vxlan vtep" in text_lower or "show bgp evpn" in text_lower or "port-channel" in text_lower and "vxlan" in text_lower:
        return "arista"
        
    # Nokia
    if "configure router" in text_lower or "show service id" in text_lower or "bof" in text_lower or "show service service-using" in text_lower:
        return "nokia"
        
    # MikroTik
    if "/ip address" in text_lower or "/interface vlan" in text_lower or "/mpls ldp" in text_lower or "routeros" in text_lower:
        return "mikrotik"
        
    # Fortinet
    if "config system interface" in text_lower or "config router static" in text_lower or "diagnose sys sdwan" in text_lower or "fortigate" in text_lower:
        return "fortinet"
        
    # Huawei
    if "display ip routing-table" in text_lower or "display current-configuration" in text_lower or "sysname" in text_lower and "olt" in text_lower:
        return "huawei"
        
    # ZTE
    if "interface gpon-onu_" in text_lower or "pon-onu-mng" in text_lower or "zteg-" in text_lower:
        return "zte"
        
    # ADTRAN
    if "gpon-olt 1" in text_lower or "show ethernet service" in text_lower:
        return "adtran"
        
    # Linux
    if "root@linux" in text_lower or "ip route show" in text_lower or "iptables -" in text_lower or "tcpdump -" in text_lower:
        return "linux"
        
    return None

def diagnose_config_or_log(text: str, selected_vendor: str = None) -> Dict[str, Any]:
    """
    Analiza las líneas de texto para verificar si coinciden con firmas de error conocidas.
    Retorna un reporte estructurado si hay coincidencia, o un reporte genérico si no.
    """
    detected = detect_vendor(text)
    vendor = selected_vendor or detected or "cisco_iosxe" # fallback a cisco
    vendor_label = VENDORS.get(vendor, vendor)
    
    lines = text.split("\n")
    
    # ── 1. FIRMA: OSPF MTU MISMATCH ─────────────────────────────────────
    ospf_mtu_match = False
    anomalous = []
    for line in lines:
        if any(x in line for x in ["EXSTART", "Exchange", "Exchange/ExStart", "Exstart/Exchange"]):
            ospf_mtu_match = True
            anomalous.append(line)
        elif "MTU mismatch" in line or "different MTU" in line or "mismatch MTU" in line:
            ospf_mtu_match = True
            anomalous.append(line)
            
    if ospf_mtu_match:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "OSPF Routing Protocol",
            "problem_title": "Desajuste de MTU en Enlace OSPF (Stuck in ExStart/Exchange)",
            "severity": "Alta",
            "rfc_reference": "RFC 2328 - OSPF Version 2 (Sección 10.6 y 13.3)",
            "architectural_cause": (
                "Durante la fase de sincronización de la Base de Datos (LSDB), los vecinos OSPF intercambian paquetes "
                "Database Description (DBD). El RFC 2328 estipula que un router debe ignorar los paquetes DBD si el MTU "
                "anunciado por el vecino es mayor que su propio MTU de interfaz. Esto congela la adyacencia en estado "
                "EXSTART o EXCHANGE indefinidamente, previniendo el cálculo de rutas SPF y aislando el tráfico de tránsito."
            ),
            "acceptance_criteria": (
                "El comando de estado de adyacencia debe reportar el estado 'FULL' en ambos extremos del enlace, "
                "y las MTUs configuradas físicamente deben ser consistentes e idénticas."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Alinear el MTU físico en la interfaz del vecino para que coincida exactamente (ej: mtu 1500 o mtu 9000).",
                    "Como paliativo temporal o si hay enlaces de terceros: configurar 'ip ospf mtu-ignore' bajo la interfaz afectada."
                ],
                "cisco_iosxr": [
                    "Bajo la interfaz física o subinterfaz, configurar el mtu que coincida exactamente con el peer.",
                    "Configurar 'router ospf <proceso> / area <id> / interface <if> / mtu-ignore' para saltarse la validación."
                ],
                "juniper": [
                    "Alinear el MTU de la interfaz física (`set interfaces <if> mtu <size>`) o lógica.",
                    "Ignorar el MTU en OSPF configurando: `set protocols ospf area <id> interface <if> mtu-ignore`."
                ],
                "arista": [
                    "Bajo la interfaz física: `ip ospf mtu-ignore` para deshabilitar la verificación en el intercambio de DBDs."
                ],
                "nokia": [
                    "Alinear el MTU del puerto físico (`port <port-id> ethernet mtu <value>`).",
                    "Configurar `/configure router ospf area <area> interface <if> mtu-ignore`."
                ],
                "mikrotik": [
                    "Asegurar que el L2 MTU y el IP MTU de la interfaz coincidan con el vecino.",
                    "En ROS v7: `/routing ospf interface-template add interface=<if> ignore-mtu=yes`."
                ]
            }
        }

    # ── 2. FIRMA: BGP MD5 PASSWORD MISMATCH ──────────────────────────────
    bgp_md5_match = False
    anomalous = []
    for line in lines:
        if any(x in line for x in ["BADAUTH", "MD5 digest", "MD5 signature failed", "MD5 signature mismatch", "No MD5 digest", "TCP MD5 Signature Option"]):
            bgp_md5_match = True
            anomalous.append(line)
        elif "TCP: Connection reset by peer" in line and ("BGP" in line or "179" in line):
            bgp_md5_match = True
            anomalous.append(line)
            
    if bgp_md5_match:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "BGP (Border Gateway Protocol)",
            "problem_title": "Discrepancia o Ausencia de Clave MD5 en Sesión BGP (TCP MD5 Auth Mismatch)",
            "severity": "Crítica",
            "rfc_reference": "RFC 2385 - Protection of BGP Sessions via the TCP MD5 Signature Option",
            "architectural_cause": (
                "Para proteger las sesiones BGP de ataques de inyección y suplantación de identidad TCP, se utiliza la opción "
                "de firma MD5 de TCP (RFC 2385). Si las contraseñas pre-compartidas difieren en un solo carácter o si un extremo "
                "no tiene configurada la contraseña, el socket TCP rechaza inmediatamente los segmentos SYN o los descarta en silencio. "
                "Esto impide establecer el puerto 179 y la sesión BGP se mantiene alternando entre los estados 'Active' e 'Idle'."
            ),
            "acceptance_criteria": (
                "La sesión BGP debe establecer el estado 'Established' de forma permanente, y no deben registrarse logs de "
                "'TCP-6-BADAUTH' o descartes de firmas de seguridad en la consola."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Verificar y reconfigurar la contraseña idéntica en ambos peers: `neighbor <peer-ip> password <secret_key>`.",
                    "Si fluctúa, validar que no haya caracteres especiales que el parser de Cisco pueda codificar erróneamente."
                ],
                "cisco_iosxr": [
                    "Bajo la configuración del router BGP y del vecino correspondiente, aplicar: `password <secret_key>`.",
                    "Ejecutar un `clear bgp ip <peer-ip>` para forzar el restablecimiento del socket TCP."
                ],
                "juniper": [
                    "Establecer la contraseña idéntica a nivel de grupo o de vecino: `set protocols bgp group <name> neighbor <peer-ip> authentication-key <secret_key>`."
                ],
                "arista": [
                    "Configurar: `neighbor <peer-ip> password <secret_key>` bajo el proceso BGP."
                ],
                "fortinet": [
                    "Habilitar password en el vecino BGP: `set password <secret_key>` dentro de `config router bgp` / `config neighbor`."
                ],
                "nokia": [
                    "Configurar `/configure router bgp group <group-name> neighbor <peer-ip> authentication-key <secret_key>`."
                ],
                "mikrotik": [
                    "En ROS v7: `/routing bgp connection add name=<peer> templates=<temp> connect-to=<ip> password=<secret_key>`."
                ]
            }
        }

    # ── 3. FIRMA: L3VPN ROUTE TARGET MISMATCH ───────────────────────────
    rt_mismatch = False
    anomalous = []
    for line in lines:
        if any(x in line for x in ["Route Target mismatch", "no import route target", "import RT mismatch", "discarded due to RT", "RT 0:0", "RT mismatch"]):
            rt_mismatch = True
            anomalous.append(line)
        elif "received" in line and "imported" in line and "0 imported" in line:
            rt_mismatch = True
            anomalous.append(line)

    if rt_mismatch:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "MPLS L3VPN",
            "problem_title": "Discrepancia en Route Targets (Filtro Silencioso de Rutas VPNv4)",
            "severity": "Alta",
            "rfc_reference": "RFC 4364 - BGP/MPLS IP Virtual Private Networks (VPNs)",
            "architectural_cause": (
                "En arquitecturas MPLS L3VPN, los Route Targets (RT) son comunidades extendidas de BGP que controlan la importación "
                "y exportación de rutas entre la tabla global de VPNv4 (bgp.l3vpn.0) y las instancias de enrutamiento VRF locales. "
                "Si el PE transmisor exporta con un RT (ej. 65000:100) pero el PE receptor no tiene configurada esa misma comunidad "
                "en su política de importación de la VRF, las rutas son descartadas silenciosamente al recibirse. BGP muestra la sesión "
                "Up, pero el cliente experimenta aislamiento completo."
            ),
            "acceptance_criteria": (
                "La tabla de ruteo de la VRF destino debe poblarse con los prefijos anunciados por el PE remoto, lo cual se confirma "
                "asegurando que `export-rt` en el origen sea idéntico a `import-rt` en el receptor."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Verificar los RTs activos con: `show run vrf <vrf-name>`.",
                    "Corregir bajo la VRF: `route-target import <rt-value>` para que coincida exactamente con el export-RT del origen."
                ],
                "cisco_iosxr": [
                    "Bajo `vrf <vrf-name> address-family ipv4 unicast`, configurar: `import route-target <rt-value>`.",
                    "Validar recepción con `show bgp vpnv4 unicast rd <rd> received-routes`."
                ],
                "juniper": [
                    "Revisar el bloque `route-distinguisher` y `vrf-target` de la instancia de ruteo.",
                    "Asegurar consistencia configurando: `set routing-instances <vrf-name> vrf-import <policy-name>` o configurando el target general: `set routing-instances <vrf-name> vrf-target import <rt-value>`."
                ],
                "arista": [
                    "Alinear bajo `vrf <vrf-name>`: `route-target import evpn <rt-value>` o `route-target import vpn <rt-value>`."
                ],
                "nokia": [
                    "Validar en el VPRN: `/configure service vprn <id> route-target import <rt-value>`."
                ],
                "fortinet": [
                    "En `config router bgp` / `config vrf`, alinear las comunidades de exportación e importación."
                ]
            }
        }

    # ── 4. FIRMA: LDP TRANSPORT IP UNREACHABLE ──────────────────────────
    ldp_transport_match = False
    anomalous = []
    for line in lines:
        if any(x in line for x in ["transport-address", "transport address connection failed", "LDP session could not be established"]):
            ldp_transport_match = True
            anomalous.append(line)
        elif "LDP" in line and "NonExistent" in line:
            ldp_transport_match = True
            anomalous.append(line)

    if ldp_transport_match:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "MPLS Core (LDP Signaling)",
            "problem_title": "Transport IP de LDP Inalcanzable (Falla de Sesión TCP LDP)",
            "severity": "Alta",
            "rfc_reference": "RFC 5036 - LDP Specification (Sección 2.5 y 3.5)",
            "architectural_cause": (
                "LDP utiliza Hellos UDP (puerto 646) para descubrir vecinos directamente conectados. Sin embargo, para intercambiar "
                "etiquetas (bindings), establece una sesión TCP de Capa 4 contra la 'Transport Address' anunciada en los Hellos "
                "(típicamente la IP de la Loopback). Si la Loopback del vecino no está publicada en el IGP (OSPF/IS-IS) o si hay "
                "filtros/ACLs bloqueando TCP 646, la sesión TCP no se establece (se queda en NonExistent o Initialized), rompiendo "
                "la señalización de etiquetas de transporte."
            ),
            "acceptance_criteria": (
                "La sesión LDP debe pasar a estado 'Operational' o 'Established' y la ruta IGP hacia la loopback del vecino debe ser "
                "alcanzable con una máscara de host /32 exacta."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Validar alcanzabilidad de la loopback del vecino: `ping <neighbor-loopback-ip>`.",
                    "Si no hay ping, verificar que la loopback esté publicada en OSPF (`network <ip> 0.0.0.0 area <id>`).",
                    "Asegurar que ninguna ACL en la interfaz bloquee el puerto TCP/UDP 646."
                ],
                "cisco_iosxr": [
                    "Verificar alcanzabilidad de la transport-address en la RIB global: `show route <neighbor-loopback-ip>`.",
                    "Si es necesario, forzar que LDP use la interfaz física como transport address en lugar de la loopback (temporal): `router ldp / interface <if> / discovery transport-address interface`."
                ],
                "juniper": [
                    "Verificar ruta con `show route <peer-loopback-ip>`. Debe estar activa vía IGP.",
                    "Asegurar que `lo0.0` esté configurada en OSPF y habilitada con `family mpls`.",
                    "Si hay filtros en `lo0`, permitir explícitamente UDP y TCP puerto 646."
                ],
                "mikrotik": [
                    "Comprobar `/mpls ldp neighbor print`. Si está en 'connecting', verificar alcanzabilidad de la IP remota.",
                    "Asegurar que el LDP Transport Preference esté alineado."
                ]
            }
        }

    # ── 5. FIRMA: LACP PORT SUSPENDED ────────────────────────────────────
    lacp_suspended = False
    anomalous = []
    for line in lines:
        if any(x in line for x in ["PORT_SUSPENDED", "suspended", "LACP-3-PORT_SUSPENDED", "individual", "Suspended", "Individual"]):
            lacp_suspended = True
            anomalous.append(line)
        elif "lacp" in line.lower() and "down" in line.lower():
            lacp_suspended = True
            anomalous.append(line)

    if lacp_suspended:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "Link Aggregation (LACP / EtherChannel)",
            "problem_title": "Puerto LACP Suspendido o Individual (Falla de Negociación LACP)",
            "severity": "Alta",
            "rfc_reference": "IEEE 802.3ad / IEEE 802.1AX - Link Aggregation",
            "architectural_cause": (
                "Cuando un puerto se configura con LACP dinámico (modo active), espera intercambiar PDUs de LACP con el extremo remoto "
                "para formar un canal lógico (Bundle/Port-Channel). Si el extremo remoto tiene configurado el EtherChannel en modo estático "
                "(mode on), no envía PDUs de LACP. En este escenario, para evitar bucles o inconsistencias de Capa 2, LACP suspende "
                "los puertos locales o los marca en estado 'Individual', deshabilitando el reenvío de datos."
            ),
            "acceptance_criteria": (
                "El estado del Port-Channel debe reportarse en Up y los miembros físicos deben mostrar el estado 'Bundle' o 'Active' "
                "indicando intercambio de control exitoso."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Verificar que ambos extremos utilicen LACP dinámico: `channel-group <id> mode active`.",
                    "Evitar el modo `on` si hay negociación. Asegurar que velocidad, dúplex y VLANs coincidan exactamente en los miembros."
                ],
                "cisco_iosxr": [
                    "Configurar bajo la interfaz del miembro: `bundle id <id> mode active`.",
                    "Verificar con `show lacp bundle-relations`."
                ],
                "juniper": [
                    "Asegurar la configuración de LACP en el `aggregated-ether-options`:",
                    "`set interfaces ae<id> aggregated-ether-options lacp active` y en los miembros `set interfaces <if> ether-options 802.3ad ae<id>`."
                ],
                "arista": [
                    "Establecer `channel-group <id> mode active` en los miembros físicos del port-channel."
                ],
                "fortinet": [
                    "En `config system interface`, establecer `set lacp-mode active` en la interfaz agregada (LACP)."
                ]
            }
        }

    # ── 6. FIRMA: STP ROOT GUARD BLOCKED ──────────────────────────────────
    stp_root_guard = False
    anomalous = []
    for line in lines:
        line_lower = line.lower()
        if any(x in line_lower for x in ["root-guard", "rootguard", "root guard", "root port blocked", "port blocked by root guard"]):
            stp_root_guard = True
            anomalous.append(line)
        elif "loop guard" in line_lower or "bpdu-guard" in line_lower:
            stp_root_guard = True
            anomalous.append(line)

    if stp_root_guard:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "Spanning Tree Protocol (STP)",
            "problem_title": "Puerto Bloqueado por STP Root Guard (Inconsistencia de Root Bridge)",
            "severity": "Alta",
            "rfc_reference": "IEEE 802.1D / Cisco Spanning Tree Guard Features",
            "architectural_cause": (
                "Root Guard protege la topología activa de STP asegurando que la ubicación elegida para el Root Bridge principal "
                "no cambie de forma no autorizada. Si un puerto con Root Guard habilitado recibe un BPDU superior (que anuncia un "
                "Bridge ID con menor prioridad/MAC), el puerto transita inmediatamente al estado 'root-inconsistent' (bloqueado). "
                "Esto previene que un switch externo erróneo o no autorizado tome control de la topología lógica de la red."
            ),
            "acceptance_criteria": (
                "La prioridad de STP en los switches principales de Core debe configurarse explícitamente a un valor muy bajo "
                "(ej. 4096) para evitar elecciones accidentales, restaurando el puerto bloqueado."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Ajustar la prioridad del switch de Core: `spanning-tree vlan <ids> priority 4096`.",
                    "Verificar qué switch de acceso está enviando BPDUs superiores: `show spanning-tree inconsistentports`."
                ],
                "juniper": [
                    "Bajo la configuración de STP/RSTP, ajustar la prioridad del switch Core principal:",
                    "`set protocols rstp bridge-priority 4k`.",
                    "Verificar bloqueos con: `show spanning-tree interface`."
                ],
                "arista": [
                    "Configurar `spanning-tree vlan <ids> priority 4096` para asegurar que el Core sea el Root Bridge indiscutible."
                ]
            }
        }

    # ── 7. FIRMA: GPON LOW OPTICAL POWER ─────────────────────────────────
    gpon_opt_power = False
    anomalous = []
    for line in lines:
        if "dBm" in line and any(x in line for x in ["-28.", "-29.", "-30.", "-31.", "-32.", "-33.", "-34.", "-35.", "low", "critical", "too low"]):
            gpon_opt_power = True
            anomalous.append(line)
        elif "optical power" in line.lower() and ("low" in line.lower() or "alarm" in line.lower()):
            gpon_opt_power = True
            anomalous.append(line)

    if gpon_opt_power:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "GPON / FTTH Access Network",
            "problem_title": "Potencia Óptica de Recepción Crítica (GPON RX Optical Power Alarm)",
            "severity": "Crítica",
            "rfc_reference": "ITU-T G.984 - GPON Physical Media Dependent Layer Specification",
            "architectural_cause": (
                "El estándar ITU-T G.984 especifica que la sensibilidad óptica de recepción (RX) en la ONU/ONT debe mantenerse "
                "dentro del rango de -15 dBm a -27 dBm. Si el nivel cae por debajo de -27 dBm (por ejemplo, a -30 dBm o menos) debido a "
                "conectores sucios, empalmes defectuosos, atenuaciones en splitters o curvaturas críticas en la fibra (macrobends), "
                "el transceptor sufre pérdida de tramas FEC, causando desconexiones intermitentes del cliente (flapping ONT) "
                "o pérdida total del servicio."
            ),
            "acceptance_criteria": (
                "La potencia de recepción medida en la ONT debe registrarse entre -15 dBm y -25 dBm para garantizar "
                "la estabilidad del servicio."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "huawei": [
                    "Verificar el estado del puerto y la ONT: `display ont info 0 1 1 1`.",
                    "Consultar la potencia óptica con: `display ont optical-info 0 1 1 1`.",
                    "Acción de campo: Limpiar conectores de fibra con alcohol isopropílico, verificar empalmes y fusiones en la caja NAP."
                ],
                "zte": [
                    "Ejecutar `show pon power rx-onu gpon-onu_1/2/1:1` para medir la potencia en la ONT.",
                    "Si es menor a -27 dBm, trace la línea de fibra usando un OTDR para ubicar el punto de alta atenuación en el tramo."
                ],
                "adtran": [
                    "Consultar estadísticas ópticas en el canal ONT: `show gpon ont optical-status`.",
                    "Asegurar que los acopladores en el distribuidor principal (ODF) no tengan pérdidas excesivas."
                ]
            }
        }

    # ── 8. FIRMA: FORTINET SD-WAN SLA FAIL ───────────────────────────────
    fortinet_sdwan_sla = False
    anomalous = []
    for line in lines:
        if "sdwan" in line.lower() and ("dead" in line.lower() or "sla failed" in line.lower() or "latency exceeded" in line.lower() or "packet loss" in line.lower()):
            fortinet_sdwan_sla = True
            anomalous.append(line)
        elif "health-check" in line.lower() and ("failed" in line.lower() or "dead" in line.lower()):
            fortinet_sdwan_sla = True
            anomalous.append(line)

    if fortinet_sdwan_sla:
        return {
            "matched": True,
            "detected_vendor": "fortinet",
            "vendor_label": "Fortinet FortiOS",
            "technology": "SD-WAN Enterprise Core",
            "problem_title": "Enlace SD-WAN Degradado o Fuera de Parámetros SLA (SLA Health-Check Dead)",
            "severity": "Alta",
            "rfc_reference": "Fortinet SD-WAN Architecture Best Practices",
            "architectural_cause": (
                "FortiOS utiliza Health-Checks activos (pings, queries DNS o peticiones HTTP) para monitorear el desempeño de cada miembro "
                "del SD-WAN (latencia, jitter y pérdida de paquetes). Si un miembro excede los umbrales configurados para un SLA "
                "(por ejemplo, pérdida de paquetes > 5% o latencia > 150 ms) o deja de responder, el motor de SD-WAN marca el enlace "
                "como DEAD. Como consecuencia, el tráfico de producción se redirige a otros miembros saludables que cumplan con la regla de negocio."
            ),
            "acceptance_criteria": (
                "El estado del SLA debe reportar 'ALIVE' para todos los miembros, y las métricas de red deben mantenerse estables "
                "por debajo del umbral objetivo de la política de calidad de servicio."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "fortinet": [
                    "Revisar el estado detallado de los SLAs activos: `diagnose sys sdwan health-check status`.",
                    "Validar el estado operativo de los miembros del SD-WAN: `diagnose sys sdwan member`.",
                    "Ejecutar captura de tráfico en la interfaz degradada para verificar descartes: `diagnose sniffer packet <interface> 'icmp' 4 20 l`.",
                    "Contactar al ISP proveedor del enlace físico para reportar degradación de red en tránsito."
                ]
            }
        }

    # ── 9. FIRMA: EVPN ESI INCONSISTENCY ─────────────────────────────────
    evpn_esi_match = False
    anomalous = []
    for line in lines:
        if "ESI" in line and any(x in line for x in ["mismatch", "inconsistency", "DF election failed", "Designated Forwarder", "split-brain"]):
            evpn_esi_match = True
            anomalous.append(line)
        elif "esi" in line.lower() and "inconsistent" in line.lower():
            evpn_esi_match = True
            anomalous.append(line)

    if evpn_esi_match:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "EVPN Multi-homing",
            "problem_title": "Inconsistencia de Ethernet Segment Identifier (EVPN ESI Mismatch)",
            "severity": "Alta",
            "rfc_reference": "RFC 7432 - BGP MPLS-Based Ethernet VPN (Sección 5 y 8.5)",
            "architectural_cause": (
                "En multihoming activo-activo de EVPN, dos o más PEs se conectan al mismo switch de cliente mediante un Link Aggregation "
                "Group (LAG). Para evitar bucles y asegurar que el tráfico BUM se replique de forma controlada, los PEs deben configurar "
                "el mismo Ethernet Segment Identifier (ESI) de 10 bytes. Si hay un mismatch de ESI, el proceso de elección del Designated "
                "Forwarder (DF) se rompe, lo cual provoca problemas de duplicidad de tramas, loops lógicos o descarte total del tráfico."
            ),
            "acceptance_criteria": (
                "El ESI configurado en el LAG del cliente debe ser idéntico en ambos PEs redundantes, y la elección del DF "
                "debe completarse con un único Designated Forwarder activo por VLAN."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxr": [
                    "Verificar el estado del segmento: `show evpn ethernet-segment`.",
                    "Configurar el mismo ESI en la interfaz de bundle del cliente en ambos PEs: `interface Bundle-Ether<id> / evpn / segment-id <esi-value> identifier type 0`."
                ],
                "juniper": [
                    "Validar con: `show evpn ethernet-segment extensive`.",
                    "Corregir el identificador ESI en el agregado: `set interfaces ae<id> esi <esi-value> all-active`."
                ],
                "arista": [
                    "Bajo el port-channel, alinear el ESI: `evpn ethernet-segment / identifier <esi-value>`."
                ]
            }
        }

    # ── 10. FIRMA: BFD SESSION DOWN / TIMER MISMATCH ──────────────────────
    bfd_match = False
    anomalous = []
    for line in lines:
        line_l = line.lower()
        if "bfd" in line_l and any(x in line_l for x in ["down", "admindown", "timer mismatch", "detect timer expired", "detect-multiplier", "minimum-interval"]):
            bfd_match = True
            anomalous.append(line)

    if bfd_match:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "BFD (Bidirectional Forwarding Detection)",
            "problem_title": "Sesión BFD Caída o Desajuste de Temporizadores (BFD Session Down / Timer Mismatch)",
            "severity": "Alta",
            "rfc_reference": "RFC 5880 / RFC 5881 - Bidirectional Forwarding Detection (BFD)",
            "architectural_cause": (
                "BFD proporciona detección ultrarrápida de fallas de enlace sub-segundo para protocolos de enrutamiento (BGP, OSPF, IS-IS). "
                "Si los temporizadores negociados (desired min transmit interval, required min receive interval) no son compatibles o si el "
                "multiplicador de detección expira antes de recibir un control packet (por congestión o descarte UDP 3784/3785), "
                "BFD colapsa la sesión, lo que provoca la caída en cadena de los protocolos de enrutamiento asociados."
            ),
            "acceptance_criteria": (
                "La sesión BFD debe reportarse en estado 'Up' con un tiempo de respuesta de Keepalive estable en ambas direcciones."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Verificar el estado BFD: `show bfd neighbors`.",
                    "Alinear los temporizadores bajo la interfaz: `bfd interval 500 min_rx 500 multiplier 3`."
                ],
                "cisco_iosxr": [
                    "Bajo `router bfd`, configurar temporizadores globales o por interfaz: `interface <if> / minimum-interval 300 / multiplier 3`."
                ],
                "juniper": [
                    "Alinear el bloque bfd bajo el protocolo: `set protocols ospf area 0 interface <if> bfd-liveness-detection minimum-interval 300 multiplier 3`."
                ],
                "arista": [
                    "Habilitar y alinear bajo la interfaz: `bfd interval 300 min-rx 300 multiplier 3`."
                ],
                "fortinet": [
                    "Verificar estado: `diagnose router bfd neighbor status`.",
                    "Ajustar temporizadores dentro de `config router bfd`."
                ]
            }
        }

    # ── 11. FIRMA: BGP AS-PATH LOOP / MISSING AS-OVERRIDE ──────────────────
    bgp_as_loop = False
    anomalous = []
    for line in lines:
        line_l = line.lower()
        if "bgp" in line_l and any(x in line_l for x in ["as_path", "as loop", "deny local as", "as_override", "loop detected in as_path", "rejecting route due to local as"]):
            bgp_as_loop = True
            anomalous.append(line)

    if bgp_as_loop:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "BGP / MPLS L3VPN",
            "problem_title": "Bucle en AS-Path o Falta de AS-Override (BGP Route Rejection due to Local AS)",
            "severity": "Alta",
            "rfc_reference": "RFC 4271 (BGP-4) / RFC 4364 (BGP/MPLS IP VPNs)",
            "architectural_cause": (
                "En topologías MPLS L3VPN donde un cliente utiliza el mismo Número de Sistema Autónomo (ASN) en múltiples sitios remotos, "
                "el mecanismo estándar de prevención de bucles de BGP rechaza silenciosamente los prefijos que contienen el ASN propio en el atributo AS-Path. "
                "Sin la función `as-override` configurada en el PE del proveedor (que reemplaza el AS del cliente por el AS del Service Provider), "
                "las rutas enviadas desde un sitio no se instalarán en la tabla de ruteo del sitio remoto."
            ),
            "acceptance_criteria": (
                "Los prefijos del sitio remoto deben ser visibles e instalados en la FIB de la VRF con el ASN sustituido correctamente."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Bajo la VRF del vecino BGP en el PE: `neighbor <ce-ip> as-override`.",
                    "Como alternativa en el CE: `neighbor <pe-ip> allowas-in 2`."
                ],
                "cisco_iosxr": [
                    "Bajo `router bgp <asn> / vrf <vrf> / neighbor <ce-ip>`, aplicar `as-override`."
                ],
                "juniper": [
                    "Configurar bajo la sesión BGP del PE: `set routing-instances <vrf> protocols bgp group <group> neighbor <ce-ip> as-override`."
                ],
                "nokia": [
                    "Bajo `/configure service vprn <id> bgp group <group> neighbor <ce-ip>`, habilitar `as-override`."
                ]
            }
        }

    # ── 12. FIRMA: IS-IS ADJACENCY / AREA MISMATCH ─────────────
    isis_match = False
    anomalous = []
    for line in lines:
        line_l = line.lower()
        if ("isis" in line_l or "is-is" in line_l) and any(x in line_l for x in ["area mismatch", "system id collision", "lsp mtu mismatch", "init state", "rejected iih"]):
            isis_match = True
            anomalous.append(line)

    if isis_match:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "IS-IS Routing Protocol",
            "problem_title": "Adyacencia IS-IS Fallida (Area Mismatch / LSP MTU Mismatch)",
            "severity": "Alta",
            "rfc_reference": "ISO/IEC 10589 / RFC 1195 - Use of OSI IS-IS in IP Networks",
            "architectural_cause": (
                "Para que routers IS-IS establezcan adyacencias Level-1, sus direcciones de área (Area IDs en la NET address) deben coincidir de forma idéntica. "
                "Si difieren, la adyacencia queda en estado 'Init' o se rechazan los paquetes IIH (IS-IS Hello). Asimismo, si el tamaño del LSP (Link State PDU) "
                "configurado supera el MTU de la interfaz física intermediaria, el flooding de la base de datos de enlaces colapsa silenciosamente."
            ),
            "acceptance_criteria": (
                "El comando `show isis neighbors` debe mostrar el estado 'Up' o 'L1L2' en ambos extremos del enlace."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Verificar la NET address del proceso: `show run | sec router isis`.",
                    "Alinear el MTU de interfaz y deshabilitar verificación de MTU en IIH si aplica: `isis mtu <size>`."
                ],
                "juniper": [
                    "Validar con `show isis adjacency`.",
                    "Alinear el área en `set interfaces lo0.0 family iso address 49.0001.xxxx.xxxx.xxxx.00`."
                ],
                "cisco_iosxr": [
                    "Verificar adyacencia: `show isis neighbors`.",
                    "Alinear `net 49.0001.xxxx.xxxx.xxxx.00` bajo `router isis <proceso>`."
                ]
            }
        }

    # ── 13. FIRMA: QOS OUTPUT QUEUE DROPS / BUFFER EXHAUSTION ─────────────
    qos_drops = False
    anomalous = []
    for line in lines:
        line_l = line.lower()
        if ("qos" in line_l or "queue" in line_l or "interface" in line_l) and any(x in line_l for x in ["output drop", "tail drop", "wred drop", "threshold exceed", "buffer exhaustion", "overrun"]):
            qos_drops = True
            anomalous.append(line)

    if qos_drops:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "Quality of Service (QoS / Traffic Shaping)",
            "problem_title": "Descarte de Paquetes en Colas de Salida por Congestión (QoS Output Queue / Tail Drops)",
            "severity": "Alta",
            "rfc_reference": "RFC 2474 (DiffServ) / RFC 2597 (Assured Forwarding PHB Group)",
            "architectural_cause": (
                "Los descartes en colas de salida (Output Queue / Tail Drops) ocurren cuando la velocidad de ráfaga de tráfico entrante supera la tasa de transmisión (Clock rate) "
                "de la interfaz física de salida o la tasa configurada en el shaper del policy-map. Si las colas de hardware (buffers) se llenan por completo, "
                "el router descarta los paquetes entrantes sin importar su clase, degradando el tráfico crítico en tiempo real (Voz/Video)."
            ),
            "acceptance_criteria": (
                "Los contadores de 'output drops' y 'tail drops' deben permanecer estables en 0, y el tráfico de prioridad (EF) no debe sufrir pérdidas."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Verificar política de QoS: `show policy-map interface <if>`.",
                    "Aumentar el tamaño del buffer o ajustar el shaper: `policy-map <name> / class <class_name> / queue-limit <packets>`."
                ],
                "cisco_iosxr": [
                    "Monitorear colas de salida: `show qos interface <if> output`.",
                    "Aumentar ancho de banda garantizado en la clase de servicio."
                ],
                "juniper": [
                    "Verificar caídas en buffer con `show interfaces queue <if>`.",
                    "Ajustar el scheduler: `set class-of-service schedulers <sched_name> buffer-size percent <val>`."
                ],
                "fortinet": [
                    "Revisar descartes de shaping: `diagnose firewall shaper per-ip-shaper list`."
                ]
            }
        }

    # ── 14. FIRMA: DHCP SNOOPING / OPTION 82 / RATE LIMIT BLOCKED ──────────
    dhcp_snoop = False
    anomalous = []
    for line in lines:
        line_l = line.lower()
        if "dhcp" in line_l and any(x in line_l for x in ["snooping", "option 82", "untrusted port", "dhcp_snooping_untrusted_port", "rate limit exceeded", "binding database missing"]):
            dhcp_snoop = True
            anomalous.append(line)

    if dhcp_snoop:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "Layer 2 Security (DHCP Snooping)",
            "problem_title": "Bloqueo de Paquetes DHCP por Puertos No Confiables (DHCP Snooping Untrusted Port Drop)",
            "severity": "Alta",
            "rfc_reference": "RFC 3046 - DHCP Relay Agent Information Option / Cisco DHCP Snooping Guide",
            "architectural_cause": (
                "DHCP Snooping es una característica de seguridad L2 que actúa como un firewall entre puertos no confiables (clientes) y confiables (servidores DHCP). "
                "Si un puerto no confiable recibe una respuesta DHCP Offer/ACK o si un paquete DHCP incluye información de Option 82 sin que la interfaz esté marcada como confiable, "
                "el switch descarta el paquete y bloquea la asignación de dirección IP al cliente final."
            ),
            "acceptance_criteria": (
                "La interfaz de enlace ascendente (Uplink) hacia el servidor DHCP debe estar explícitamente configurada en modo 'trust' y los clientes deben recibir su IP sin descartes."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Marcar el puerto de enlace ascendente como confiable: `interface <uplink_if> / ip dhcp snooping trust`.",
                    "Si los switches intermedios insertan Option 82 sin trust: `ip dhcp snooping information option allow-untrusted`."
                ],
                "juniper": [
                    "Configurar bajo `dhcp-security`: `set dhcp-security group <group> overrides trust-option`."
                ],
                "arista": [
                    "Bajo la interfaz de enlace con el servidor: `ip dhcp snooping trust`."
                ]
            }
        }

    # ── 15. FIRMA: DMVPN IPSEC / IKEV2 PROPOSAL MISMATCH ─────────────────
    ipsec_match = False
    anomalous = []
    for line in lines:
        line_l = line.lower()
        if any(x in line_l for x in ["dmvpn", "ipsec", "ike", "isakmp"]) and any(y in line_l for y in ["no_proposal_chosen", "phase 1 failed", "phase 2 failed", "crypto map mismatch", "sa proposal mismatch", "mismatch transform set"]):
            ipsec_match = True
            anomalous.append(line)

    if ipsec_match:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "VPN Core / Security (DMVPN IPsec)",
            "problem_title": "Falla en Negociación IPsec / ISAKMP (Proposal Mismatch in Phase 1/2)",
            "severity": "Crítica",
            "rfc_reference": "RFC 7296 (IKEv2) / RFC 2409 (IKEv1) / Cisco DMVPN Design Guide",
            "architectural_cause": (
                "Para establecer un túnel seguro IPsec (como en DMVPN Hub-to-Spoke o Spoke-to-Spoke), ambas partes deben acordar exactamente los mismos parámetros criptográficos "
                "en la Fase 1 (Algoritmo de cifrado, Hash, Grupo Diffie-Hellman y autenticación) y en la Fase 2 (Transform Set y PFS). "
                "Una sola discrepancia (ej. AES-128 vs AES-256) provoca la falla 'NO_PROPOSAL_CHOSEN' y rechaza el establecimiento de la Security Association (SA)."
            ),
            "acceptance_criteria": (
                "La consulta `show crypto ipsec sa` debe reportar estados 'ACTIVE' en las SAs entrantes y salientes, transportando paquetes encapsulados en cifrado ESP."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Verificar política de Fase 1: `show crypto ikev2 policy` o `show crypto isakmp policy`.",
                    "Alinear el Transform Set de Fase 2: `crypto ipsec transform-set <name> esp-aes 256 esp-sha-key`."
                ],
                "fortinet": [
                    "Verificar estado de fase 1: `diagnose vpn ike gateway list`.",
                    "Alinear propuesta en `config vpn ipsec phase1-interface`."
                ]
            }
        }

    # ── 16. FIRMA: VXLAN VNI / MULTICAST GROUP MISMATCH ──────────────────
    vxlan_match = False
    anomalous = []
    for line in lines:
        line_l = line.lower()
        if any(x in line_l for x in ["vxlan", "vni"]) and any(y in line_l for y in ["multicast group mismatch", "flood list empty", "vni not mapped", "vni down", "nve interface down"]):
            vxlan_match = True
            anomalous.append(line)

    if vxlan_match:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "Overlay Network (VXLAN Data Plane)",
            "problem_title": "Mapeo VNI / Grupo Multicast Inconsistente (VXLAN Tunnel Failure)",
            "severity": "Alta",
            "rfc_reference": "RFC 7348 - Virtual eXtensible Local Area Network (VXLAN)",
            "architectural_cause": (
                "En el plano de datos de VXLAN, la trama L2 del cliente se encapsula en paquetes UDP 4789. Para replicar tráfico BUM (Broadcast, Unknown Unicast, Multicast) "
                "sin un plano de control BGP EVPN, los VTEPs deben unirse al mismo grupo de multicast bajo el plano de transporte IP. "
                "Si la VNI local no está asociada al grupo de multicast correcto o la interfaz lógica NVE está apagada, la encapsulación falla."
            ),
            "acceptance_criteria": (
                "La interfaz NVE debe estar en estado 'Up', mapeando la VNI objetivo al grupo multicast o lista VTEP activa."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Verificar la interfaz NVE: `show nve vni`.",
                    "Bajo `interface nve1`: `member vni <vni_id> mcast-group <mcast_ip>`."
                ],
                "arista": [
                    "Bajo `interface Vxlan1`: `vxlan vlan <vlan_id> vni <vni_id>` y `vxlan flood vtep <vtep_ips>`."
                ]
            }
        }

    # ── 17. FIRMA: PBR NEXT-HOP UNREACHABLE ──────────────────────────────
    pbr_match = False
    anomalous = []
    for line in lines:
        line_l = line.lower()
        if any(x in line_l for x in ["pbr", "policy routing", "policy-map"]) and any(y in line_l for y in ["next-hop unreachable", "track failed", "pbr recursive lookup failed", "fallback to default"]):
            pbr_match = True
            anomalous.append(line)

    if pbr_match:
        return {
            "matched": True,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "Policy-Based Routing (PBR)",
            "problem_title": "Siguiente Salto PBR Inalcanzable (Policy-Based Routing Fallback)",
            "severity": "Media",
            "rfc_reference": "RFC 1812 - Requirements for IPv4 Routers / Policy Routing Guide",
            "architectural_cause": (
                "PBR permite desviar tráfico alterando el proceso normal de consulta a la FIB basándose en políticas (ACLs). "
                "Si la dirección IP especificada en `set ip next-hop` no se encuentra en la tabla de ruteo o si el objeto IP SLA asociado (verify-availability) "
                "falla por caída de enlace, PBR deja de reenviar por la ruta preferida y cae a la tabla de ruteo por defecto o descarta los paquetes."
            ),
            "acceptance_criteria": (
                "El objeto de rastreo (track object) debe reportar estado 'UP' y la IP del nexthop debe resolverse en la RIB activa."
            ),
            "anomalous_lines": anomalous,
            "solutions": {
                "cisco_iosxe": [
                    "Verificar estado de rastreo: `show track`.",
                    "Configurar verificación en el route-map: `set ip next-hop verify-availability <nexthop_ip> 1 track <track_id>`."
                ],
                "juniper": [
                    "Verificar la política de ruteo y la tabla `filter`: `show firewall filter`."
                ]
            }
        }

    # ── 18. DIAGNÓSTICO GENÉRICO (FALLBACK) ──────────────────────────────
    # Si no matchea ninguna firma, busca palabras clave de error y extrae
    generic_errors = []
    for line in lines:
        if any(x in line.lower() for x in ["error", "fail", "down", "mismatch", "conflict", "shutdown", "drop", "discard", "collision"]):
            generic_errors.append(line)
            
    if generic_errors:
        return {
            "matched": False,
            "detected_vendor": vendor,
            "vendor_label": vendor_label,
            "technology": "General Protocol / Configuration Diagnostics",
            "problem_title": "Anomalías Detectadas en Logs o Configuración de Consola",
            "severity": "Media",
            "rfc_reference": "N/A - Diagnóstico General de Infraestructura",
            "architectural_cause": (
                "El analizador ha escaneado la salida pegada y ha detectado líneas que indican estados caídos (Down), "
                "desajustes (Mismatch), caídas de enlaces o colisiones físicas. Estos problemas suelen estar asociados "
                "a fallas en la capa física, errores de configuración local, o desalineaciones con el equipo adyacente."
            ),
            "anomalous_lines": generic_errors[:8], # Cap a un máx de 8 para el reporte
            "acceptance_criteria": "Todos los estados de puertos deben reportar Up/Up, sin contadores de error incrementándose.",
            "solutions": {
                "cisco_iosxe": [
                    "Habilitar interfaces apagadas: `no shutdown` bajo el puerto.",
                    "Verificar fallas con `show log` o `show interfaces status`."
                ],
                "juniper": [
                    "Verificar estado de interfaces físicas: `show interfaces terse`.",
                    "Confirmar que no haya configuraciones no aplicadas (`show | compare`)."
                ],
                "mikrotik": [
                    "Verificar estado de puertos: `/interface print`.",
                    "Buscar logs recientes del sistema con `/log print`."
                ]
            }
        }
        
    return {
        "matched": False,
        "detected_vendor": vendor,
        "vendor_label": vendor_label,
        "technology": "Indeterminada",
        "problem_title": "Sin Anomalías Críticas Identificadas",
        "severity": "Baja",
        "rfc_reference": "N/A",
        "architectural_cause": (
            "El analizador no ha identificado ninguna firma de error crítica ni palabras clave de fallas graves "
            "en el texto provisto. El estado de la configuración o comando parece saludable o no está dentro de la "
            "base de datos de firmas conocidas."
        ),
        "acceptance_criteria": "N/A",
        "anomalous_lines": [],
        "solutions": {}
    }
