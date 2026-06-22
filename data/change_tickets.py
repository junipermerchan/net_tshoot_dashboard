"""
Base de datos de Change Tickets (RFC) simulados en las últimas 24 horas.
Ayuda a aplicar la metodología de "Aislar por Dominio (La regla del Cambio Reciente)".
"""

from typing import Dict, Any, List

CHANGE_TICKETS: Dict[str, List[Dict[str, str]]] = {
    "mpls": [
        {
            "id": "RFC-9010",
            "time_es": "Hace 2 horas",
            "time_en": "2 hours ago",
            "device": "PE-Madrid-01",
            "description_es": "Ajuste de MTU física a 9000 bytes en el puerto ge-0/0/0 para soporte de etiquetas apiladas.",
            "description_en": "Physical MTU adjusted to 9000 bytes on port ge-0/0/0 to support stacked labels.",
            "status": "Completado / Completed",
            "author": "Ing. Carlos Ruiz"
        },
        {
            "id": "RFC-8991",
            "time_es": "Hace 14 horas",
            "time_en": "14 hours ago",
            "device": "P-Zaragoza-02",
            "description_es": "Configuración de 'mpls ldp igp-sync' en el proceso OSPF para prevenir blackholing.",
            "description_en": "Configured 'mpls ldp igp-sync' in the OSPF process to prevent blackholing.",
            "status": "Completado / Completed",
            "author": "Ing. Ana Gomez"
        }
    ],
    "l3vpn": [
        {
            "id": "RFC-9025",
            "time_es": "Hace 1 hora",
            "time_en": "1 hour ago",
            "device": "PE-Barcelona-02",
            "description_es": "Modificación de la import-policy de la VRF CUST-A para filtrar rutas del prefijo 192.168.50.0/24.",
            "description_en": "Modified VRF CUST-A import-policy to filter routes matching prefix 192.168.50.0/24.",
            "status": "Completado / Completed",
            "author": "Ing. Sofia Marin"
        },
        {
            "id": "RFC-9005",
            "time_es": "Hace 8 horas",
            "time_en": "8 hours ago",
            "device": "PE-Madrid-01",
            "description_es": "Activación de la familia de direcciones VPNv4 unicast en el grupo de BGP interno (iBGP-RR).",
            "description_en": "Activated VPNv4 unicast address family on the internal BGP peer group (iBGP-RR).",
            "status": "Completado / Completed",
            "author": "Ing. Carlos Ruiz"
        }
    ],
    "l2vpn": [
        {
            "id": "RFC-9014",
            "time_es": "Hace 3 horas",
            "time_en": "3 hours ago",
            "device": "PE-Sevilla-01",
            "description_es": "Reconfiguración de identificador de VC de pseudowire (VCID 100) en el xconnect CUST-A.",
            "description_en": "Reconfigured pseudowire VC identifier (VCID 100) on CUST-A xconnect.",
            "status": "Completado / Completed",
            "author": "Ing. David Torres"
        },
        {
            "id": "RFC-8998",
            "time_es": "Hace 19 horas",
            "time_en": "19 hours ago",
            "device": "PE-Valencia-02",
            "description_es": "Cambio de encapsulación de puerto físico a vlan-ccc para transporte de circuitos integrados L2.",
            "description_en": "Changed physical port encapsulation to vlan-ccc for L2 circuit transport.",
            "status": "Completado / Completed",
            "author": "Ing. Marta Lopez"
        }
    ],
    "evpn": [
        {
            "id": "RFC-9030",
            "time_es": "Hace 30 minutos",
            "time_en": "30 minutes ago",
            "device": "Spine-DC-01",
            "description_es": "Actualización de Route Target de importación en EVPN MAC-VRF 10001.",
            "description_en": "Updated import Route Target on EVPN MAC-VRF 10001.",
            "status": "Completado / Completed",
            "author": "Ing. Lucas Varela"
        },
        {
            "id": "RFC-8985",
            "time_es": "Hace 23 horas",
            "time_en": "23 hours ago",
            "device": "Leaf-DC-02",
            "description_es": "Habilitación de control plane de EVPN MP-BGP y vinculación de VNIs de Capa 2 y 3.",
            "description_en": "Enabled EVPN MP-BGP control plane and mapped Layer 2/3 VNIs.",
            "status": "Completado / Completed",
            "author": "Ing. Sofia Marin"
        }
    ],
    "vxlan": [
        {
            "id": "RFC-9018",
            "time_es": "Hace 4 horas",
            "time_en": "4 hours ago",
            "device": "Leaf-DC-01",
            "description_es": "Ajuste de MTU underlay IP en interfaces loopback a 1600 bytes para evitar fragmentación en VXLAN.",
            "description_en": "Adjusted underlay IP MTU on loopback interfaces to 1600 bytes to avoid VXLAN fragmentation.",
            "status": "Completado / Completed",
            "author": "Ing. Lucas Varela"
        },
        {
            "id": "RFC-8995",
            "time_es": "Hace 12 horas",
            "time_en": "12 hours ago",
            "device": "Leaf-DC-03",
            "description_es": "Vinculación de VNI 10100 a Bridge-Domain 100 e interfaz de túnel VTEP NVE1.",
            "description_en": "Mapped VNI 10100 to Bridge-Domain 100 and VTEP NVE1 tunnel interface.",
            "status": "Completado / Completed",
            "author": "Ing. Marta Lopez"
        }
    ],
    "ospf": [
        {
            "id": "RFC-9008",
            "time_es": "Hace 5 horas",
            "time_en": "5 hours ago",
            "device": "R-Bilbao-01",
            "description_es": "Cambio del OSPF Network Type a Point-to-Point en el enlace WAN hacia R-Vitoria.",
            "description_en": "Changed OSPF Network Type to Point-to-Point on WAN link to R-Vitoria.",
            "status": "Completado / Completed",
            "author": "Ing. Juan Naranjo"
        },
        {
            "id": "RFC-8988",
            "time_es": "Hace 21 horas",
            "time_en": "21 hours ago",
            "device": "R-Vitoria-01",
            "description_es": "Modificación de la prioridad OSPF de la interfaz LAN a 0 para forzar el rol de BDR al router central.",
            "description_en": "Modified interface LAN OSPF priority to 0 to force central router BDR role.",
            "status": "Completado / Completed",
            "author": "Ing. J. Perez"
        }
    ],
    "isis": [
        {
            "id": "RFC-9022",
            "time_es": "Hace 2 horas",
            "time_en": "2 hours ago",
            "device": "Core-PE-01",
            "description_es": "Ajuste de métrica IS-IS en interfaces de core a valor wide-metrics (métrica de 24 bits).",
            "description_en": "Adjusted IS-IS metric on core interfaces to wide-metrics (24-bit metrics).",
            "status": "Completado / Completed",
            "author": "Ing. Ana Gomez"
        },
        {
            "id": "RFC-9001",
            "time_es": "Hace 10 horas",
            "time_en": "10 hours ago",
            "device": "Core-P-02",
            "description_es": "Cambio de NET (Network Entity Title) para corregir el código de área IS-IS (49.0001 -> 49.0002).",
            "description_en": "NET (Network Entity Title) change to correct IS-IS area code (49.0001 -> 49.0002).",
            "status": "Completado / Completed",
            "author": "Ing. Carlos Ruiz"
        }
    ],
    "bgp": [
        {
            "id": "RFC-9020",
            "time_es": "Hace 3 horas",
            "time_en": "3 hours ago",
            "device": "Borde-ISP-01",
            "description_es": "Asociación de un nuevo Route-Map de exportación hacia el ASN 65002 para agregar community no-export.",
            "description_en": "Applied new export Route-Map to ASN 65002 adding community no-export.",
            "status": "Completado / Completed",
            "author": "Ing. Sofia Marin"
        },
        {
            "id": "RFC-8994",
            "time_es": "Hace 13 horas",
            "time_en": "13 hours ago",
            "device": "Core-BGP-RR",
            "description_es": "Habilitación de BGP Route Reflector en sesiones con los nuevos routers de agregación.",
            "description_en": "Enabled BGP Route Reflector on sessions with new aggregation routers.",
            "status": "Completado / Completed",
            "author": "Ing. Carlos Ruiz"
        }
    ],
    "spanning_tree": [
        {
            "id": "RFC-9011",
            "time_es": "Hace 6 horas",
            "time_en": "6 hours ago",
            "device": "SW-Acceso-02",
            "description_es": "Activación de STP BPDU Guard y PortFast en todos los puertos asignados a usuarios finales.",
            "description_en": "Enabled STP BPDU Guard and PortFast on all end-user ports.",
            "status": "Completado / Completed",
            "author": "Ing. Juan Naranjo"
        },
        {
            "id": "RFC-8992",
            "time_es": "Hace 15 horas",
            "time_en": "15 hours ago",
            "device": "SW-Core-01",
            "description_es": "Reducción de la prioridad de STP (VLAN 10, 20) a 4096 para asegurar rol de Root Bridge.",
            "description_en": "Decreased STP priority (VLAN 10, 20) to 4096 to secure Root Bridge role.",
            "status": "Completado / Completed",
            "author": "Ing. Marta Lopez"
        }
    ],
    "qos_traffic_eng": [
        {
            "id": "RFC-9016",
            "time_es": "Hace 4 horas",
            "time_en": "4 hours ago",
            "device": "Core-Madrid-PE",
            "description_es": "Modificación de perfiles de RSVP-TE para reservar un 10% adicional de ancho de banda para tráfico de voz.",
            "description_en": "Modified RSVP-TE profiles to reserve an additional 10% bandwidth for voice traffic.",
            "status": "Completado / Completed",
            "author": "Ing. David Torres"
        },
        {
            "id": "RFC-8999",
            "time_es": "Hace 18 horas",
            "time_en": "18 hours ago",
            "device": "P-Zaragoza-01",
            "description_es": "Reconfiguración de colas de salida de CoS (Class of Service) en interfaces WAN de 10G.",
            "description_en": "Reconfigured egress CoS (Class of Service) queues on 10G WAN interfaces.",
            "status": "Completado / Completed",
            "author": "Ing. Ana Gomez"
        }
    ],
    "fiber_ont": [
        {
            "id": "RFC-9029",
            "time_es": "Hace 1 hora",
            "time_en": "1 hour ago",
            "device": "OLT-Valencia-01",
            "description_es": "Aprovisionamiento del perfil de línea OMCI y asociación del GEM Port 12 a la VLAN 100 para nueva ONT.",
            "description_en": "OMCI line profile provisioned and GEM Port 12 mapped to VLAN 100 for new ONT.",
            "status": "Completado / Completed",
            "author": "Ing. Javier Costa"
        },
        {
            "id": "RFC-9002",
            "time_es": "Hace 10 horas",
            "time_en": "10 hours ago",
            "device": "ODN-Sector-4",
            "description_es": "Mantenimiento preventivo en la caja splitter del Sector 4 para atenuación de potencia óptica excesiva.",
            "description_en": "Preventive maintenance at Sector 4 splitter box to reduce excessive optical power attenuation.",
            "status": "Completado / Completed",
            "author": "Fusión S.L. (Contratista)"
        }
    ],
    "nat": [
        {
            "id": "RFC-9009",
            "time_es": "Hace 8 horas",
            "time_en": "8 hours ago",
            "device": "CGNAT-Borde-01",
            "description_es": "Ampliación del pool de direcciones IP públicas de NAT en el bloque CGNAT para evitar Port Exhaustion.",
            "description_en": "Expanded NAT public IP pool size in the CGNAT block to prevent Port Exhaustion.",
            "status": "Completado / Completed",
            "author": "Ing. Sofia Marin"
        }
    ],
    "dhcp": [
        {
            "id": "RFC-9017",
            "time_es": "Hace 4 horas",
            "time_en": "4 hours ago",
            "device": "DHCP-Server-01",
            "description_es": "Creación del nuevo Scope de red 192.168.120.0/24 y asignación de leases a 8 horas.",
            "description_en": "Created new network Scope 192.168.120.0/24 and set lease time to 8 hours.",
            "status": "Completado / Completed",
            "author": "Ing. J. Perez"
        }
    ],
    "sdwan": [
        {
            "id": "RFC-9026",
            "time_es": "Hace 2 horas",
            "time_en": "2 hours ago",
            "device": "vManage-DC",
            "description_es": "Publicación de política de Traffic Steering (AFT) para desviar tráfico SaaS directo a Internet (DIA).",
            "description_en": "Published Traffic Steering policy (AFT) to route SaaS traffic direct to Internet (DIA).",
            "status": "Completado / Completed",
            "author": "Ing. Lucas Varela"
        }
    ],
    "switch_l2": [
        {
            "id": "RFC-9012",
            "time_es": "Hace 5 horas",
            "time_en": "5 hours ago",
            "device": "SW-Agregacion-01",
            "description_es": "Configuración de agregación de enlaces LACP (Port-Channel 1) hacia el switch de acceso.",
            "description_en": "Configured LACP link aggregation (Port-Channel 1) towards the access switch.",
            "status": "Completado / Completed",
            "author": "Ing. Marta Lopez"
        }
    ]
}

# Fallback genérico para tecnologías sin tickets específicos
GENERIC_TICKETS = [
    {
        "id": "RFC-8800",
        "time_es": "Hace 12 horas",
        "time_en": "12 hours ago",
        "device": "Router-Borde-01",
        "description_es": "Revisión general de políticas de seguridad y actualización de firmas de firewall.",
        "description_en": "General security policies review and firewall signatures update.",
        "status": "Completado / Completed",
        "author": "Soporte TI"
    },
    {
        "id": "RFC-8790",
        "time_es": "Hace 20 horas",
        "time_en": "20 hours ago",
        "device": "Switch-Distribucion-02",
        "description_es": "Mantenimiento correctivo y limpieza de puertos SFP+ fibra óptica.",
        "description_en": "Corrective maintenance and cleaning of SFP+ fiber ports.",
        "status": "Completado / Completed",
        "author": "Fusión S.L. (Contratista)"
    }
]

def get_tickets_for_tech(tech_key: str) -> List[Dict[str, str]]:
    """Retorna los RFCs para una tecnología específica o los fallbacks genéricos."""
    clean_key = tech_key.lower().replace("_config", "")
    
    # Buscar coincidencia exacta o por subcadena
    for key, val in CHANGE_TICKETS.items():
        if key in clean_key:
            return val
            
    return GENERIC_TICKETS
