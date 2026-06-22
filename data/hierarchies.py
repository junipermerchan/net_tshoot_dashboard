"""
Jerarquías de Troubleshooting y Metodologías de Diagnóstico para Network Tshoot Dashboard.
Define mapeos automáticos y funciones para enriquecer los pasos con:
1. Jerarquía Técnica (Capa OSI)
2. Jerarquía de Red (Topología Telecom)
3. Metodología de Troubleshooting
4. Jerarquía Operativa (Niveles de Soporte / Tiers)
"""

from typing import Dict, Any

HIERARCHY_DEFAULTS = {
    "mpls": {
        "osi": "Capa 2.5: Transporte de Etiquetas (MPLS)",
        "osi_en": "Layer 2.5: Label Transport (MPLS)",
        "domain": "Core (Núcleo de Red)",
        "domain_en": "Core (Backbone)",
        "methodology": "Enfoque Bottom-Up (Validación de transporte LDP/RSVP antes de servicios VPN)",
        "methodology_en": "Bottom-Up Approach (Transport validation before VPN services)"
    },
    "segment_routing": {
        "osi": "Capa 2.5: Transporte de Etiquetas (SR-MPLS / SRv6)",
        "osi_en": "Layer 2.5: Label/IPv6 Segment Transport (SR)",
        "domain": "Core (Núcleo de Red)",
        "domain_en": "Core (Backbone)",
        "methodology": "Aislar por Dominio (Anuncio de SIDs en IGP y tablas LFIB)",
        "methodology_en": "Domain Isolation (SID announcements in IGP and LFIB tables)"
    },
    "l3vpn": {
        "osi": "Capa 3: Red (VRFs y Enrutamiento Multiprotocolo)",
        "osi_en": "Layer 3: Network (VRFs and Multiprotocol Routing)",
        "domain": "Core & Agregación (Borde PE-CE)",
        "domain_en": "Core & Aggregation (PE-CE Border)",
        "methodology": "Divide y Vencerás (Aislamiento PE-CE frente a fallas en Core)",
        "methodology_en": "Divide and Conquer (PE-CE isolation vs Core issues)"
    },
    "l2vpn": {
        "osi": "Capa 2: Enlace de Datos (Pseudowires / VPLS)",
        "osi_en": "Layer 2: Data Link (Pseudowires / VPLS)",
        "domain": "Agregación & Core (Metro-Ethernet)",
        "domain_en": "Aggregation & Core (Metro-Ethernet)",
        "methodology": "Enfoque Bottom-Up (Física -> Enlace -> PW Status)",
        "methodology_en": "Bottom-Up Approach (Physical -> Link -> PW Status)"
    },
    "evpn": {
        "osi": "Capa 2/3: Conmutación y Enrutamiento Virtualizado",
        "osi_en": "Layer 2/3: Virtualized Switching & Routing",
        "domain": "Agregación & Core (Data Center / Metro)",
        "domain_en": "Aggregation & Core (Data Center / Metro)",
        "methodology": "Aislar por Dominio (Plano de Control MP-BGP EVPN y tablas MAC-VRF)",
        "methodology_en": "Domain Isolation (MP-BGP EVPN control plane and MAC-VRF tables)"
    },
    "vxlan": {
        "osi": "Capa 3: Red (Underlay IP) & Capa 2: Enlace (Overlay VNI)",
        "osi_en": "Layer 3: Underlay IP & Layer 2: Overlay VNI",
        "domain": "Core & Agregación (Data Center Fabric)",
        "domain_en": "Core & Aggregation (Data Center Fabric)",
        "methodology": "Enfoque Bottom-Up (Validar ping underlay >1550 bytes + DF antes del overlay)",
        "methodology_en": "Bottom-Up Approach (Verify underlay ping >1550 bytes + DF before overlay)"
    },
    "ospf": {
        "osi": "Capa 3: Red (Estado de Enlace / Protocolo 89)",
        "osi_en": "Layer 3: Network (Link State / Protocol 89)",
        "domain": "Core & Agregación",
        "domain_en": "Core & Aggregation",
        "methodology": "Comparar con Línea Base (Verificación de prioridades, MTU y timers Hello/Dead)",
        "methodology_en": "Baseline Comparison (Priority, MTU and Hello/Dead timers)"
    },
    "isis": {
        "osi": "Capa 2: Enlace de Datos (Protocolo CLNS / NET)",
        "osi_en": "Layer 2: Data Link (CLNS / NET Protocol)",
        "domain": "Core (Núcleo de Red)",
        "domain_en": "Core (Backbone)",
        "methodology": "Comparar con Línea Base (Métricas, System-IDs y rellenado de IIH)",
        "methodology_en": "Baseline Comparison (Metrics, System-IDs and IIH padding)"
    },
    "spanning_tree": {
        "osi": "Capa 2: Enlace de Datos (BPDUs y Prevención de Bucles)",
        "osi_en": "Layer 2: Data Link (BPDUs and Loop Prevention)",
        "domain": "Acceso & Agregación",
        "domain_en": "Access & Aggregation",
        "methodology": "Comparar con Línea Base (Prioridades Root Bridge y estados de puerto)",
        "methodology_en": "Baseline Comparison (Root Bridge priorities and port states)"
    },
    "qos_traffic_eng": {
        "osi": "Capa 3: Red (RSVP-TE) & Capa 4-7: Calidad de Servicio",
        "osi_en": "Layer 3: RSVP-TE & Layer 4-7: Quality of Service",
        "domain": "Core (Tránsito con Ingeniería de Tráfico)",
        "domain_en": "Core (Traffic Engineered Transit)",
        "methodology": "Aislar por Dominio (TED, reservas de ancho de banda y colas CoS/DSCP)",
        "methodology_en": "Domain Isolation (TED, bandwidth reservations and CoS/DSCP queues)"
    },
    "multicast": {
        "osi": "Capa 3: Red (PIM / IGMP)",
        "osi_en": "Layer 3: Network (PIM / IGMP)",
        "domain": "Core & Agregación",
        "domain_en": "Core & Aggregation",
        "methodology": "Divide y Vencerás (Validar árbol compartido (*,G) frente a SPT (S,G) y chequeo RPF)",
        "methodology_en": "Divide and Conquer (Verify shared tree (*,G) vs SPT (S,G) and RPF check)"
    },
    "fiber_ont": {
        "osi": "Capa 1: Física (Fibra Óptica) & Capa 2: Enlace (GPON/OMCI)",
        "osi_en": "Layer 1: Physical (Fiber) & Layer 2: Link (GPON/OMCI)",
        "domain": "Acceso (GPON OLT / ONT)",
        "domain_en": "Access (GPON OLT / ONT)",
        "methodology": "Enfoque Bottom-Up (Niveles Ópticos -> Estado de Ranging -> Registro -> VLANs)",
        "methodology_en": "Bottom-Up Approach (Optical Levels -> Ranging -> Registration -> VLANs)"
    },
    "adtran_ta5000": {
        "osi": "Capa 1: Física & Capa 2: Enlace (Transporte WAN)",
        "osi_en": "Layer 1: Physical & Layer 2: Link (WAN Transport)",
        "domain": "Acceso & Transporte Metropolitano",
        "domain_en": "Access & Metro Transport",
        "methodology": "Enfoque Bottom-Up (Medición óptica, redundancia y loopbacks físicos)",
        "methodology_en": "Bottom-Up Approach (Optical level, slot redundancy and physical loopbacks)"
    },
    "ccc_interface_switch": {
        "osi": "Capa 2: Enlace de Datos (Circuit Cross-Connect / Local Switch)",
        "osi_en": "Layer 2: Data Link (Circuit Cross-Connect / Local Switch)",
        "domain": "Agregación & Metro Ethernet",
        "domain_en": "Aggregation & Metro Ethernet",
        "methodology": "Divide y Vencerás (Aislamiento de interfaces locales vs. xconnects remotos)",
        "methodology_en": "Divide and Conquer (Local interfaces vs remote xconnects)"
    },
    "evc": {
        "osi": "Capa 2: Enlace de Datos (Ethernet Virtual Circuits - EVC)",
        "osi_en": "Layer 2: Data Link (Ethernet Virtual Circuits - EVC)",
        "domain": "Agregación & Metro Ethernet",
        "domain_en": "Aggregation & Metro Ethernet",
        "methodology": "Divide y Vencerás (Service Instances, Bridge-Domains y tags VLAN)",
        "methodology_en": "Divide and Conquer (Service Instances, Bridge-Domains and VLAN tags)"
    },
    "nat": {
        "osi": "Capa 3: Red (Direcciones IP) & Capa 4: Transporte (Puertos TCP/UDP)",
        "osi_en": "Layer 3: Network (IPs) & Layer 4: Transport (TCP/UDP Ports)",
        "domain": "Acceso & Borde de Interconexión",
        "domain_en": "Access & Interconnection Border",
        "methodology": "Aislar por Dominio (Tablas de traducción, agotamiento de puertos y ruteo asimétrico)",
        "methodology_en": "Domain Isolation (Translation tables, port exhaustion and asymmetric routing)"
    },
    "wireshark_tcpdump": {
        "osi": "Capa 1-7: Captura y Análisis Multi-Capa",
        "osi_en": "Layer 1-7: Multi-Layer Capture & Analysis",
        "domain": "Cualquier Dominio de Red",
        "domain_en": "Any Network Domain",
        "methodology": "Aislar por Dominio (Captura de tráfico de control y datos en puntos clave)",
        "methodology_en": "Domain Isolation (Control and data traffic captures at key points)"
    },
    "bfd": {
        "osi": "Capa 3: Red & Capa 4: Transporte (UDP 3784)",
        "osi_en": "Layer 3: Network & Layer 4: Transport (UDP 3784)",
        "domain": "Core & Agregación",
        "domain_en": "Core & Aggregation",
        "methodology": "Comparar con Línea Base (Timers de detección rápidos vs falsos positivos)",
        "methodology_en": "Baseline Comparison (Fast detection timers vs false positives)"
    },
    "dhcp": {
        "osi": "Capa 7: Aplicación (DHCP) & Capa 4: UDP 67/68",
        "osi_en": "Layer 7: Application & Layer 4: UDP 67/68",
        "domain": "Acceso (Entrega de Direccionamiento)",
        "domain_en": "Access (IP Addressing Allocation)",
        "methodology": "Enfoque Bottom-Up (Conectividad física -> DHCP Relay -> DHCP Server Pool)",
        "methodology_en": "Bottom-Up Approach (Physical Link -> DHCP Relay -> Server Pool)"
    },
    "netflow": {
        "osi": "Capa 7: Aplicación (NetFlow/IPFIX) & Capa 4: UDP",
        "osi_en": "Layer 7: Application & Layer 4: UDP",
        "domain": "Core & Agregación",
        "domain_en": "Core & Aggregation",
        "methodology": "Aislar por Dominio (Configuración de exporters, samplers y recolector)",
        "methodology_en": "Domain Isolation (Exporters, samplers and collector configuration)"
    },
    "aaa": {
        "osi": "Capa 7: Aplicación (RADIUS/TACACS+) & Capa 4: UDP/TCP",
        "osi_en": "Layer 7: Application & Layer 4: UDP/TCP",
        "domain": "Gestión y Borde de Acceso",
        "domain_en": "Management & Access Edge",
        "methodology": "Enfoque Bottom-Up (Conectividad IP -> Servidor AAA -> Fallback Local)",
        "methodology_en": "Bottom-Up Approach (IP Link -> AAA Server -> Local Fallback)"
    },
    "switch_l2": {
        "osi": "Capa 2: Enlace de Datos (VLANs, LACP, MAC-Learning)",
        "osi_en": "Layer 2: Data Link (VLANs, LACP, MAC-Learning)",
        "domain": "Acceso & Agregación",
        "domain_en": "Access & Aggregation",
        "methodology": "Comparar con Línea Base (VLANs troncales, estados LACP y CAM)",
        "methodology_en": "Baseline Comparison (Trunk VLANs, LACP states and CAM)"
    },
    "dmvpn": {
        "osi": "Capa 3: Red (GRE/NHRP/IPsec)",
        "osi_en": "Layer 3: Network (GRE/NHRP/IPsec)",
        "domain": "Acceso & Borde WAN",
        "domain_en": "Access & WAN Edge",
        "methodology": "Enfoque Bottom-Up (Underlay IP -> IPsec SAs -> NHRP mappings -> Overlay Routing)",
        "methodology_en": "Bottom-Up Approach (Underlay IP -> IPsec SAs -> NHRP mappings -> Overlay Routing)"
    },
    "eigrp": {
        "osi": "Capa 3: Red (EIGRP / IP 88)",
        "osi_en": "Layer 3: Network (EIGRP / IP 88)",
        "domain": "Core & Agregación (Campus/WAN)",
        "domain_en": "Core & Aggregation (Campus/WAN)",
        "methodology": "Comparar con Línea Base (AS mismatch, K-values, y adyacencias)",
        "methodology_en": "Baseline Comparison (AS mismatch, K-values, and adjacencies)"
    },
    "ipv6": {
        "osi": "Capa 3: Red (IPv6/NDP)",
        "osi_en": "Layer 3: Network (IPv6/NDP)",
        "domain": "Acceso, Agregación & Core",
        "domain_en": "Access, Aggregation & Core",
        "methodology": "Enfoque Bottom-Up (Enlace físico -> Link-local reachability -> Global Unicast)",
        "methodology_en": "Bottom-Up Approach (Physical link -> Link-local reachability -> Global Unicast)"
    },
    "sdwan": {
        "osi": "Capa 3-7: Red y Aplicación (Overlays Seguros)",
        "osi_en": "Layer 3-7: Network & Application (Secure Overlays)",
        "domain": "Borde WAN (Internet / MPLS Transit)",
        "domain_en": "WAN Edge (Internet / MPLS Transit)",
        "methodology": "Divide y Vencerás (Underlay IP vs Control Plane Orchestration vs Data Plane IPsec)",
        "methodology_en": "Divide and Conquer (Underlay vs Orchestrators vs IPsec tunnels)"
    },
    "vrrp_hsrp": {
        "osi": "Capa 3: Red (Redundancia de Primer Salto)",
        "osi_en": "Layer 3: Network (First Hop Redundancy)",
        "domain": "Acceso & Agregación (Borde LAN)",
        "domain_en": "Access & Aggregation (LAN Border)",
        "methodology": "Comparar con Línea Base (Prioridades, virtual MAC y tracking de interfaz)",
        "methodology_en": "Baseline Comparison (Priorities, virtual MAC and interface tracking)"
    },
    "loop_troubleshooting": {
        "osi": "Capa 2: Enlace de Datos (Tormentas de Broadcast)",
        "osi_en": "Layer 2: Data Link (Broadcast Storms)",
        "domain": "Acceso & Agregación",
        "domain_en": "Access & Aggregation",
        "methodology": "Divide y Vencerás (Partición del dominio de broadcast apagando interfaces clave)",
        "methodology_en": "Divide and Conquer (Broadcast domain partitioning by shutting links)"
    },
    "static": {
        "osi": "Capa 3: Red (Rutas Estáticas e IP SLA)",
        "osi_en": "Layer 3: Network (Static Routes & IP SLA)",
        "domain": "Acceso & Agregación",
        "domain_en": "Access & Aggregation",
        "methodology": "Comparar con Línea Base (Verificación de Next-Hops y trackeo BFD/SLA)",
        "methodology_en": "Baseline Comparison (Next-Hop verification and BFD/SLA tracking)"
    },
    "pbr": {
        "osi": "Capa 3: Red (Enrutamiento por Políticas / PBR)",
        "osi_en": "Layer 3: Network (Policy Based Routing / PBR)",
        "domain": "Agregación & Core",
        "domain_en": "Aggregation & Core",
        "methodology": "Aislar por Dominio (Filtros de ruta y Next-Hops alternativos)",
        "methodology_en": "Domain Isolation (Route filters and alternative Next-Hops)"
    },
    "rip": {
        "osi": "Capa 3: Red (Protocolo RIPv2)",
        "osi_en": "Layer 3: Network (RIPv2 Protocol)",
        "domain": "Acceso & Agregación",
        "domain_en": "Access & Aggregation",
        "methodology": "Comparar con Línea Base (Métricas por saltos y temporizadores)",
        "methodology_en": "Baseline Comparison (Hop metrics and timers)"
    },
    "seguridad": {
        "osi": "Capa 2: Enlace (MACsec/802.1X) & Capa 3: Red (IPsec/ACLs)",
        "osi_en": "Layer 2: Link (MACsec/802.1X) & Layer 3: Network (IPsec/ACLs)",
        "domain": "Acceso & Borde WAN",
        "domain_en": "Access & WAN Edge",
        "methodology": "Enfoque Bottom-Up (Autenticación L2 -> Túneles L3 -> Reglas ACL)",
        "methodology_en": "Bottom-Up Approach (L2 Auth -> L3 Tunnels -> ACL rules)"
    },
    "linux_tshoot": {
        "osi": "Capa 1-7: Sockets, Kernel Routing & Firewall Linux",
        "osi_en": "Layer 1-7: Sockets, Kernel Routing & Linux Firewall",
        "domain": "Host / Servidor de Aplicación",
        "domain_en": "Host / Application Server",
        "methodology": "Enfoque Bottom-Up (Interfaces -> Routing/ARP -> Netfilter/Ports -> App)",
        "methodology_en": "Bottom-Up Approach (Interfaces -> Routing/ARP -> Netfilter/Ports -> App)"
    },
    "ip_trace": {
        "osi": "Capa 2: Enlace (ARP) & Capa 3: Red (Ruteo / NAT / Firewall)",
        "osi_en": "Layer 2: Link (ARP) & Layer 3: Network (Routing / NAT / Firewall)",
        "domain": "Trayecto End-to-End (Acceso -> Core -> Tránsito)",
        "domain_en": "End-to-End Path (Access -> Core -> Transit)",
        "methodology": "Divide y Vencerás (Traceo salto a salto y regla del Cambio Reciente)",
        "methodology_en": "Divide and Conquer (Hop-by-hop tracing and Recent Change rule)"
    },
    "subnet_31": {
        "osi": "Capa 3: Red (Direccionamiento /31 / RFC 3021)",
        "osi_en": "Layer 3: Network (/31 Addressing / RFC 3021)",
        "domain": "Enlaces Punto a Punto Core/Agregación",
        "domain_en": "Core/Aggregation Point-to-Point Links",
        "methodology": "Comparar con Línea Base (Alineación de IPs y soporte de hardware vendor)",
        "methodology_en": "Baseline Comparison (IP alignment and vendor hardware support)"
    },
    "vlan_qinq": {
        "osi": "Capa 2: Enlace de Datos (802.1Q / 802.1AD / QinQ)",
        "osi_en": "Layer 2: Data Link (802.1Q / 802.1AD / QinQ)",
        "domain": "Acceso & Agregación (Metro-Ethernet)",
        "domain_en": "Access & Aggregation (Metro-Ethernet)",
        "methodology": "Enfoque Bottom-Up (Ethertype -> Tags VLAN -> Native VLAN match)",
        "methodology_en": "Bottom-Up Approach (Ethertype -> VLAN tags -> Native VLAN match)"
    },
    "bgp": {
        "osi": "Capa 3: Red (Enrutamiento) & Capa 4: Transporte (TCP 179)",
        "osi_en": "Layer 3: Network & Layer 4: Transport (TCP 179)",
        "domain": "Core & Tránsito/Peering (Borde de Red)",
        "domain_en": "Core & Transit/Peering (Network Edge)",
        "methodology": "Aislar por Dominio (Políticas de Ruta y Atributos BGP)",
        "methodology_en": "Domain Isolation (Route policies and BGP Attributes)"
    }
}

# Fallbacks genéricos
GENERIC_OSI = "Capa 3: Red (IP / Enrutamiento)"
GENERIC_OSI_EN = "Layer 3: Network (IP / Routing)"
GENERIC_DOMAIN = "Core & Borde de Red"
GENERIC_DOMAIN_EN = "Core & Network Edge"
GENERIC_METHODOLOGY = "Aislar por Dominio y Enfoque Bottom-Up"
GENERIC_METHODOLOGY_EN = "Domain Isolation and Bottom-Up Approach"


def get_hierarchies_for_tech(tech_key: str) -> Dict[str, str]:
    """Retorna las jerarquías por defecto basadas en la clave de la tecnología."""
    clean_key = tech_key.lower().replace("_config", "")
    
    # Buscar coincidencia exacta o por subcadena
    for key, val in HIERARCHY_DEFAULTS.items():
        if key in clean_key:
            return val
            
    return {
        "osi": GENERIC_OSI,
        "osi_en": GENERIC_OSI_EN,
        "domain": GENERIC_DOMAIN,
        "domain_en": GENERIC_DOMAIN_EN,
        "methodology": GENERIC_METHODOLOGY,
        "methodology_en": GENERIC_METHODOLOGY_EN
    }


def enrich_with_hierarchies(kb: Dict[str, Any]):
    """Enriquece dinámicamente cada paso (step) de la base de conocimiento con las jerarquías."""
    for tech_key, tech_data in kb.items():
        defaults = get_hierarchies_for_tech(tech_key)
        steps = tech_data.get("steps", {})
        for step_key, step_data in steps.items():
            # Añadir solo si no han sido explícitamente definidos a nivel de paso
            if "osi_layer" not in step_data:
                step_data["osi_layer"] = defaults["osi"]
            if "osi_layer_en" not in step_data:
                step_data["osi_layer_en"] = defaults["osi_en"]
                
            if "network_domain" not in step_data:
                step_data["network_domain"] = defaults["domain"]
            if "network_domain_en" not in step_data:
                step_data["network_domain_en"] = defaults["domain_en"]
                
            if "methodology" not in step_data:
                step_data["methodology"] = defaults["methodology"]
            if "methodology_en" not in step_data:
                step_data["methodology_en"] = defaults["methodology_en"]
