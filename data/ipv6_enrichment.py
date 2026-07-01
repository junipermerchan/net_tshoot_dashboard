"""
Módulo de Enriquecimiento de IPv6 Avanzado para Network Tshoot Dashboard.
Añade programáticamente soporte y guías de nivel Enterprise/Service Provider (CCIE/JNCIE) 
de IPv6 en todas las tecnologías, vendors y comandos simulados.
"""

from typing import Dict, Any, List

def add_cmd(cmd_dict: Dict[str, Any], vendor: str, tier: str, cmd: str):
    """Agrega un comando a un vendor y tier específico si no existe."""
    if vendor not in cmd_dict:
        cmd_dict[vendor] = {}
    if tier not in cmd_dict[vendor]:
        cmd_dict[vendor][tier] = []
    if cmd not in cmd_dict[vendor][tier]:
        cmd_dict[vendor][tier].append(cmd)

def add_output(sim_dict: Dict[str, Any], tech: str, step: str, vendor: str, cmd: str, output: str):
    """Agrega una salida de comando simulado de forma segura."""
    if tech not in sim_dict:
        sim_dict[tech] = {}
    if step not in sim_dict[tech]:
        sim_dict[tech][step] = {}
    if vendor not in sim_dict[tech][step]:
        sim_dict[tech][step][vendor] = {}
    sim_dict[tech][step][vendor][cmd] = output

def enrich_with_ipv6(base: Dict[str, Any]):
    # Asegurar que zte y huawei estén en los vendors de ipv6 e ipv6_config
    for tech_key in ('ipv6', 'ipv6_config'):
        if tech_key in base:
            for v in ('zte', 'huawei'):
                if v not in base[tech_key].get('vendors', []):
                    base[tech_key]['vendors'].append(v)

    # ==========================================================================
    # A. TROUBLESHOOTING IPv6 (NIVEL CCIE/JNCIE Y MODELOS OSI / TCP-IP)
    # ==========================================================================
    if 'ipv6' in base:
        tech = base['ipv6']
        steps = tech.get('steps', {})

        # Paso 1: Conectividad y Mapeo OSI/TCP-IP de ICMPv6
        if 'ipv6_ts_start' in steps:
            steps['ipv6_ts_start']['title'] = "1. Conectividad IPv6, NDP e ICMPv6 en el Modelo OSI/TCP-IP"
            steps['ipv6_ts_start']['body'] = (
                "**Objetivo:** Verificar la conectividad local y la resolución de direcciones de Capa 2/3 (NDP) mediante mensajes ICMPv6.\n\n"
                "### Mapeo de ICMPv6 en el Modelo OSI y TCP/IP\n"
                "ICMPv6 (IPv6 Protocolo 58) opera en la **Capa 3 (Red) del modelo OSI** y en la **Capa de Internet del modelo TCP/IP**.\n"
                "Para que IPv6 sea funcional, un firewall o ACL **NO debe bloquear todos los mensajes ICMPv6**. Los siguientes mensajes son vitales y deben permitirse:\n\n"
                "| Mensaje ICMPv6 | Tipo | Capa OSI | Capa TCP/IP | Función Crítica / Impacto si se bloquea |\n"
                "| :--- | :---: | :---: | :---: | :--- |\n"
                "| **Router Solicitation (RS)** | 133 | 3 | Internet | Enviado por hosts para solicitar anuncios RA. Rompe SLAAC rápido. |\n"
                "| **Router Advertisement (RA)** | 134 | 3 | Internet | Enviado por routers para anunciar prefijos y flags (M/O/A). Rompe direccionamiento. |\n"
                "| **Neighbor Solicitation (NS)** | 135 | 3 | Internet | Equivalente a ARP Request (Capa 3). Rompe resolución de MAC (NDP) y DAD. |\n"
                "| **Neighbor Advertisement (NA)** | 136 | 3 | Internet | Equivalente a ARP Reply. Rompe resolución de MAC (NDP) y DAD. |\n"
                "| **Packet Too Big (PTB)** | 2 | 3 | Internet | **Crítico para Path MTU Discovery (PMTUD).** Si se filtra, conexiones TCP grandes (ej. HTTP/data) se congelan. |\n"
                "| **Destination Unreachable** | 1 | 3 | Internet | Informa errores de ruta. |\n"
                "| **Time Exceeded** | 3 | 3 | Internet | Hop limit = 0. Rompe Traceroute. |\n"
                "| **Echo Request/Reply** | 128/129 | 3 | Internet | Herramienta Ping de diagnóstico. |\n\n"
                "### Neighbor Discovery Protocol (NDP - RFC 4861)\n"
                "Reemplaza a ARP. Los estados del NDP Cache son:\n"
                "- **INCOMPLETE:** Solicitation (NS) enviada, esperando respuesta (NA).\n"
                "- **REACHABLE:** Dirección MAC resuelta y confirmada de forma bidireccional.\n"
                "- **STALE:** Tiempo de alcanzabilidad expirado. Se puede enviar tráfico pero se debe re-confirmar.\n"
                "- **DELAY / PROBE:** Confirmando alcanzabilidad activa enviando NS unicast de forma periódica."
            )

        # Paso 2: Diferencias de IPv6 en Protocolos de Enrutamiento (RIPng, EIGRPv6, OSPFv3, ISIS MT, MP-BGP)
        if 'ipv6_ts_routing' in steps:
            steps['ipv6_ts_routing']['title'] = "2. Diferencias en Protocolos de Enrutamiento IPv6 (Routing)"
            steps['ipv6_ts_routing']['body'] = (
                "**Objetivo:** Validar el intercambio de rutas dinámicas IPv6 en escenarios multi-vendor.\n\n"
                "### Comparativa de Protocolos: IPv4 vs. IPv6 (Diferencias Clave)\n\n"
                "| Protocolo | Versión IPv4 | Versión IPv6 (RFC) | Dirección Multicast | Diferencias Clave de Enrutamiento |\n"
                "| :--- | :--- | :--- | :---: | :--- |\n"
                "| **RIP** | RIPv2 | **RIPng (RFC 2080)** | `FF02::9` | Opera sobre puerto UDP 521 (vs 520). El Next-Hop se anuncia como la dirección link-local (`fe80::`). |\n"
                "| **EIGRP** | EIGRP v4 | **EIGRPv6** | `FF02::A` | Se ejecuta directo sobre protocolo 88. Habilitado en la interfaz. **Requiere configurar Router ID manual de 32-bits** si no hay IPv4 activo en el equipo. |\n"
                "| **OSPF** | OSPFv2 | **OSPFv3 (RFC 5340)** | `FF02::5` / `FF02::6` | Habilitado por interfaz (no `network`). Sesión sobre link-local. Prefijos retirados de LSA Tipo 1/2 y migrados a **LSA Tipo 8 (Link)** y **Tipo 9 (Intra-Area)**. Soporta Multi-Instance. |\n"
                "| **IS-IS** | IS-IS | **IS-IS IPv6 (RFC 5120)** | L2 Multicast (Macs) | Requiere activar **Multi-Topology (MT)** para evitar asimetrías de enlaces IPv4/IPv6. Intercambia prefijos en **TLV 236** (IPv6) y **TLV 229** (MT). |\n"
                "| **BGP** | BGP-4 | **MP-BGP (RFC 4760)** | Peer Unicast | Soporta múltiples familias de direcciones (**AFI 2 = IPv6**, **SAFI 1 = Unicast**, **SAFI 128 = VPNv6**). Cuidado con Next-Hop mapeados a IPv4 (RFC 2545). |\n"
                "| **MPLS** | LDP/RSVP | **6PE / 6VPE (RFC 4798/4659)** | Core IPv4 | **6PE:** Transporta IPv6 sobre Core MPLS IPv4 usando BGP Label (SAFI 4). **6VPE:** VPNs IPv6 multi-VRF sobre MPLS IPv4 (AFI 2, SAFI 128). |\n\n"
                "### Troubleshooting de Next-Hop en MP-BGP (RFC 2545)\n"
                "Si el peer BGP se establece sobre IPv4, BGP intentará enviar un Next-Hop IPv4 mapeado a IPv6 (ej: `::ffff:10.1.1.1`). La tabla de enrutamiento IPv6 no lo resolverá, dejando las rutas como **Hidden** o **Invalid**.\n"
                "**Solución:** Aplicar una política para reescribir el Next-Hop usando la dirección link-local del router remoto o habilitar Extended Next-Hop Encoding (RFC 8950)."
            )

        # Paso 3: DHCPv6 (Con/Sin Estado), SLAAC, RDNSS y Diseño de Intranets ULA
        if 'ipv6_ts_auto' in steps:
            steps['ipv6_ts_auto']['title'] = "3. Configuración de Intranets, SLAAC, DHCPv6 (Con/Sin Estado) y DNS"
            steps['ipv6_ts_auto']['body'] = (
                "**Objetivo:** Diagnosticar la autoconfiguración de direcciones, asignación de DNS y direccionamiento privado en Intranets.\n\n"
                "### DHCPv6 Stateful vs. Stateless y Autoconfiguración\n"
                "Los hosts obtienen direccionamiento IP y DNS basado en las banderas (flags) del Router Advertisement (RA) enviado por el gateway:\n\n"
                "- **SLAAC Puro (M=0, O=0):** El host autoconfigura su IPv6 usando el prefijo RA (A-Flag=1) vía EUI-64 o privacidad (RFC 4941). **No hay asignación de DNS** a menos que se configure **RFC 8106 (RDNSS/DNSSL)** en el router para anunciar los DNS directamente en el RA.\n"
                "- **DHCPv6 Stateless / Sin Estado (M=0, O=1):** El host configura su IP por SLAAC (A-flag=1), pero realiza una solicitud a la IP multicast `ff02::1:2` para pedir los servidores DNS y dominio de búsqueda al servidor DHCPv6 (Option 23 - DNS, Option 24 - Domain List).\n"
                "- **DHCPv6 Stateful / Con Estado (M=1, O=1):** El host desactiva la autoconfiguración local. Envía un mensaje `Solicit` a `ff02::1:2` para pedir una dirección IPv6 (Option 3 - IA_NA) y DNS del servidor DHCPv6, el cual lleva un registro de estado (lease) en su base de datos.\n\n"
                "### Configuración de Direccionamiento IPv6 en Intranets (ULA - RFC 4193)\n"
                "Para intranets aisladas o privadas, no se debe usar direccionamiento IPv4 privado traducido. Se debe utilizar **Unique Local Addresses (ULA - RFC 4193)**:\n\n"
                "- **Bloque ULA:** `fc00::/7` (en la práctica se usa `fd00::/8` para asignaciones locales).\n"
                "- **Global ID (40 bits aleatorios):** Se debe generar un prefijo aleatorio para evitar colisiones en futuras fusiones (ej: `fd4a:5e6c:8b2a::/48`).\n"
                "- **Subnetting LAN (/64):** El prefijo `/48` permite $65,536$ subnets `/64` locales.\n"
                "- **Configuración DNS local:** Los servidores DNS locales deben configurarse con registros **AAAA** para resolución de nombres interna, y anunciarse a las LANs usando RDNSS (en el router) o DHCPv6 Stateless."
            )

    # ==========================================================================
    # B. OSPF / OSPFv3 ENRICHMENT (Nivel CCIE/JNCIE)
    # ==========================================================================
    if 'ospf' in base:
        tech = base['ospf']
        steps = tech.get('steps', {})
        
        # Paso 1: OSPF Start
        if 'ospf_start' in steps:
            steps['ospf_start']['body'] += (
                '\n\n**Soporte Avanzado de OSPFv3 (RFC 5340 & RFC 5838):**\n'
                '- **Direccionamiento Link-Local:** OSPFv3 forma adyacencias utilizando únicamente direcciones link-local (fe80::/10). '
                'Si el link-local no está configurado de forma determinista o tiene duplicados, la sesión se quedará en DOWN/INIT.\n'
                '- **Independencia de Address-Family:** Admite múltiples instancias en el mismo enlace. OSPFv3 permite encapsular '
                'tanto prefijos IPv4 como IPv6 utilizando campos de Address Family específicos (RFC 5838).\n'
                '- **LSA Database Split:** OSPFv3 retira la información de prefijos de los LSAs de Router (Type 1) y Network (Type 2). '
                'Los prefijos se anuncian ahora en nuevos tipos de LSAs: **Link LSA (Type 8)** (informa la dirección link-local del router '
                'y sus prefijos asociados) e **Intra-Area-Prefix LSA (Type 9)** (lleva las subredes asociadas a los routers o redes del área).'
            )
            
        # Paso 2: OSPF Neighbors (Adyacencias)
        if 'ospf_neighbor' in steps:
            cmds = steps['ospf_neighbor'].get('commands', {})
            # Juniper OSPFv3
            add_cmd(cmds, 'juniper', 'tier1', 'show ospf3 neighbor extensive')
            add_cmd(cmds, 'juniper', 'tier1', 'show ospf3 interface detail')
            add_cmd(cmds, 'juniper', 'tier2', 'show configuration protocols ospf3 | display set')
            add_cmd(cmds, 'juniper', 'tier2', 'show ospf3 neighbor extensive | match state')
            add_cmd(cmds, 'juniper', 'tier3', 'monitor traffic interface <if> matching "ospf3" | no-more')
            add_cmd(cmds, 'juniper', 'arch', 'show configuration protocols ospf3 | display set | match area')
            # Cisco IOS-XR OSPFv3
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show ospfv3 neighbor detail')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show ospfv3 interface')
            add_cmd(cmds, 'cisco_iosxr', 'tier2', 'show running-config router ospfv3')
            add_cmd(cmds, 'cisco_iosxr', 'tier2', 'show ospfv3 neighbor detail | include state')
            add_cmd(cmds, 'cisco_iosxr', 'tier3', 'debug ospfv3 hello')
            add_cmd(cmds, 'cisco_iosxr', 'arch', 'show running-config router ospfv3 | match area')
            # Cisco IOS-XE OSPFv3
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ospfv3 neighbor detail')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ospfv3 interface')
            add_cmd(cmds, 'cisco_iosxe', 'tier2', 'show running-config | section router ospfv3')
            add_cmd(cmds, 'cisco_iosxe', 'tier2', 'show ospfv3 neighbor detail | include state')
            add_cmd(cmds, 'cisco_iosxe', 'tier3', 'debug ospfv3 hello')
            add_cmd(cmds, 'cisco_iosxe', 'arch', 'show running-config | section router ospfv3 | match area')
            # MikroTik OSPFv3
            add_cmd(cmds, 'mikrotik', 'tier1', '/routing ospf v3 neighbor print detail')
            add_cmd(cmds, 'mikrotik', 'tier2', '/routing ospf v3 interface print')
            # Fortinet OSPFv3
            add_cmd(cmds, 'fortinet', 'tier1', 'get router info6 ospf neighbor detail')
            add_cmd(cmds, 'fortinet', 'tier1', 'get router info6 ospf interface')
            add_cmd(cmds, 'fortinet', 'tier2', 'show router ospf6')

        # Paso 3: OSPF Autenticación (IPsec en OSPFv3)
        if 'ospf_auth' in steps:
            steps['ospf_auth']['body'] += (
                '\n\n**Mecanismo de Autenticación de OSPFv3:**\n'
                'A diferencia de OSPFv2 (que usa MD5/SHA en la cabecera del protocolo), OSPFv3 delegó la seguridad a la suite de IPsec. '
                'Para autenticar vecinos OSPFv3, se configuran asociaciones de seguridad (SA) manuales (AH o ESP) directamente en la interfaz '
                'o en el área (compartidas por SPI). Si hay un desajuste de SPI (Security Parameter Index) o llaves hexadecimales, '
                'los routers descartarán los paquetes Hello sin generar logs informativos de adyacencia.'
            )
            cmds = steps['ospf_auth'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'show security ipsec security-associations')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show crypto ipsec sa')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show crypto ipsec sa')

        # Paso 4: OSPF Database (Base de datos LSA)
        if 'ospf_database' in steps:
            steps['ospf_database']['body'] += (
                '\n\n**Análisis de la Base de Datos OSPFv3:**\n'
                '- **LSA Tipo 8 (Link):** Debe existir un LSA de tipo Link generado por cada interfaz link-local conectada al segmento. '
                'Este LSA publica la dirección link-local del router vecino y la lista de prefijos IPv6 configurados en esa interfaz.\n'
                '- **LSA Tipo 9 (Intra-Area-Prefix):** Contiene los prefijos IPv6 de las redes stub o de tránsito conectadas al router. '
                'Si el vecino está en FULL pero no aprendes rutas, verifica la presencia de LSAs de tipo 9.'
            )
            cmds = steps['ospf_database'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'show ospf3 database')
            add_cmd(cmds, 'juniper', 'tier2', 'show ospf3 database link extensive')
            add_cmd(cmds, 'juniper', 'tier2', 'show ospf3 database intra-area-prefix extensive')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ospfv3 database')
            add_cmd(cmds, 'cisco_iosxe', 'tier2', 'show ospfv3 database link')
            add_cmd(cmds, 'cisco_iosxe', 'tier2', 'show ospfv3 database intra-area-prefix')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show ospfv3 database')
            add_cmd(cmds, 'fortinet', 'tier1', 'get router info6 ospf database')

    # ==========================================================================
    # C. IS-IS MULTI-TOPOLOGY IPv6 ENRICHMENT
    # ==========================================================================
    if 'isis' in base:
        tech = base['isis']
        steps = tech.get('steps', {})
        
        # Paso 1: IS-IS database
        if 'isis_database' in steps:
            steps['isis_database']['body'] += (
                '\n\n**Single-Topology vs. Multi-Topology en IS-IS:**\n'
                '- **Single-Topology (Default):** Asume que IPv4 e IPv6 comparten exactamente los mismos enlaces, interfaces y métricas. '
                'Si un enlace no tiene configurado IPv6, pero sí IPv4, la SPF de IPv6 fallará de todas forman, enviando tráfico por agujeros negros.\n'
                '- **Multi-Topology (MT) (RFC 5120):** Permite ejecutar árboles SPF completamente separados para IPv4 e IPv6. '
                'Es la práctica estándar en redes de producción para evitar caídas de tráfico. Verifique la activación de la capability '
                'Multi-Topology y compruebe los LSPs buscando el **TLV 229 (MT-IS-IS)** y el **TLV 236 (IPv6 Reachability)**.'
            )
            cmds = steps['isis_database'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'show isis database extensive | match "IPv6"')
            add_cmd(cmds, 'juniper', 'tier2', 'show isis database extensive | match "Multi-topology"')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show isis database detail | include IPv6')
            add_cmd(cmds, 'cisco_iosxe', 'tier2', 'show isis database detail | include Multi-Topology')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show isis database detail | include IPv6')

        # Paso 2: IS-IS interfaces
        if 'isis_adj' in steps:
            steps['isis_adj']['body'] += (
                '\n\n**Adyacencia IS-IS sobre IPv6:**\n'
                'IS-IS se ejecuta directamente sobre capa 2 utilizando tramas 802.3 link-state. Por ende, la adyacencia IS-IS se mantendrá '
                'estable incluso si el direccionamiento IPv6 local está roto o desajustado. La única forma de detectar problemas en IPv6 '
                'es validando la tabla de vecinos IS-IS y confirmando el intercambio de TLVs de direccionamiento IP.'
            )
            cmds = steps['isis_adj'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'show route table inet6.0 protocol isis')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ipv6 route isis')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show ipv6 route isis')

    # ==========================================================================
    # D. BGP / MP-BGP IPv6 & NEXT-HOP RESOLUTION
    # ==========================================================================
    for bgp_key in ('bgp', 'mpbgp'):
        if bgp_key in base:
            tech = base[bgp_key]
            steps = tech.get('steps', {})
            for step_key, step in steps.items():
                if 'start' in step_key or 'neighbor' in step_key:
                    step['body'] += (
                        '\n\n**Problemas de Next-Hop en MP-BGP IPv6 (RFC 2545):**\n'
                        '- Cuando se levanta una sesión BGP utilizando direccionamiento IPv4 pero se anuncia la Address-Family IPv6 (AFI 2, SAFI 1), '
                        'BGP enviará un Next-Hop con un formato IPv4 mapeado a IPv6 (ej: `::ffff:10.0.0.1`), el cual no se puede resolver en la tabla '
                        'de enrutamiento local y las rutas quedarán en estado **Hidden** o **Invalid**.\n'
                        '- **Solución:** Aplicar una política de exportación (`route-map` / `policy-statement`) para forzar un Next-Hop IPv6 válido, '
                        'o habilitar la negociación de Extended Next-Hop Encoding (RFC 8950) en ambos extremos del peer.'
                    )
                cmds = step.get('commands', {})
                # Juniper
                add_cmd(cmds, 'juniper', 'tier1', 'show bgp neighbor | match "Address families"')
                add_cmd(cmds, 'juniper', 'tier2', 'show route table inet6.0 protocol bgp')
                add_cmd(cmds, 'juniper', 'tier3', 'show route table inet6.0 hidden protocol bgp')
                # Cisco IOS-XE
                add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show bgp ipv6 unicast summary')
                add_cmd(cmds, 'cisco_iosxe', 'tier2', 'show ipv6 route bgp')
                add_cmd(cmds, 'cisco_iosxe', 'tier3', 'show bgp ipv6 unicast neighbors <neighbor-ip> received-routes')
                # Cisco IOS-XR
                add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show bgp ipv6 unicast summary')
                add_cmd(cmds, 'cisco_iosxr', 'tier2', 'show ipv6 route bgp')
                add_cmd(cmds, 'cisco_iosxr', 'tier3', 'show bgp ipv6 unicast neighbors <neighbor-ip> received-routes')
                # Fortinet
                add_cmd(cmds, 'fortinet', 'tier1', 'get router info6 bgp summary')

    # ==========================================================================
    # E. L3VPN (6VPE) ENRICHMENT
    # ==========================================================================
    if 'l3vpn' in base:
        tech = base['l3vpn']
        steps = tech.get('steps', {})
        for step_key, step in steps.items():
            if 'route' in step_key or 'start' in step_key:
                step['body'] += (
                    '\n\n**Operación de 6VPE (IPv6 VPN over MPLS):**\n'
                    '- 6VPE mapea direcciones IPv6 de clientes dentro de VRFs a prefijos VPNv6 (AFI 2, SAFI 128) de 196 bits (RD + IPv6).\n'
                    '- **Pila de Etiquetas MPLS:** Al enviar un paquete 6VPE, se utilizan dos etiquetas: una etiqueta interna (BGP VPNv6) '
                    'que identifica el VRF de destino en el PE remoto, y una etiqueta externa (LDP / Segment Routing) que define el camino '
                    'de tránsito por el core IPv4. Asegúrese de que el router PE local resuelva el Next-Hop IPv4 del PE remoto usando el túnel MPLS.'
                )
                cmds = step.get('commands', {})
                # Juniper
                add_cmd(cmds, 'juniper', 'tier1', 'show route table <vrf-name>.inet6.0')
                add_cmd(cmds, 'juniper', 'tier2', 'show route table bgp.l3vpn-inet6.0')
                # Cisco IOS-XE
                add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ipv6 route vrf <vrf-name>')
                add_cmd(cmds, 'cisco_iosxe', 'tier2', 'show bgp vpnv6 unicast all summary')
                # Cisco IOS-XR
                add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show ipv6 route vrf <vrf-name>')
                add_cmd(cmds, 'cisco_iosxr', 'tier2', 'show bgp vpnv6 unicast summary')
                # Fortinet
                add_cmd(cmds, 'fortinet', 'tier1', 'get router info6 routing-table vrf <vrf-name>')

    # ==========================================================================
    # F. STATIC ROUTING IPv6 ENRICHMENT
    # ==========================================================================
    if 'static' in base:
        tech = base['static']
        steps = tech.get('steps', {})
        for step_key, step in steps.items():
            cmds = step.get('commands', {})
            # Juniper
            add_cmd(cmds, 'juniper', 'tier1', 'show route table inet6.0 protocol static')
            # Cisco IOS-XE
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ipv6 route static')
            # Cisco IOS-XR
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show ipv6 route static')
            # Fortinet
            add_cmd(cmds, 'fortinet', 'tier1', 'get router info6 routing-table | grep static')

    if 'static_config' in base:
        tech = base['static_config']
        steps = tech.get('steps', {})
        
        # Paso 1: Ruta estática estándar IPv6
        if 'static_config_start' in steps:
            steps['static_config_start']['body'] += (
                '\n\n**Equivalente IPv6:**\n'
                '- Juniper: `set routing-options static route 2001:db8:100::/64 next-hop 2001:db8:12::2`\n'
                '- Cisco IOS-XE: `ipv6 route 2001:db8:100::/64 2001:db8:12::2`\n'
                '- Cisco IOS-XR: `router static address-family ipv6 unicast 2001:db8:100::/64 2001:db8:12::2`\n'
                '- MikroTik: `/ipv6 route add dst-address=2001:db8:100::/64 gateway=2001:db8:12::2`\n'
                '- Fortinet: `config router static6 \n edit 1 \n set dst 2001:db8:100::/64 \n set gateway 2001:db8:12::2 \n next \n end`\n'
                '- Linux: `ip -6 route add 2001:db8:100::/64 via 2001:db8:12::2 dev eth0`'
            )
            cmds = steps['static_config_start'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'set routing-options static route 2001:db8:100::/64 next-hop 2001:db8:12::2')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'ipv6 route 2001:db8:100::/64 2001:db8:12::2')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'configure terminal \n router static \n address-family ipv6 unicast \n 2001:db8:100::/64 2001:db8:12::2 \n commit')
            add_cmd(cmds, 'mikrotik', 'tier1', '/ipv6 route add dst-address=2001:db8:100::/64 gateway=2001:db8:12::2')
            add_cmd(cmds, 'fortinet', 'tier1', 'config router static6 \n edit 1 \n set dst 2001:db8:100::/64 \n set gateway 2001:db8:12::2 \n next \n end')
            add_cmd(cmds, 'linux', 'tier1', 'ip -6 route add 2001:db8:100::/64 via 2001:db8:12::2 dev eth0')

    # ==========================================================================
    # G. MULTICAST IPv6 (MLD / PIMv6)
    # ==========================================================================
    if 'multicast' in base:
        tech = base['multicast']
        steps = tech.get('steps', {})
        for step_key, step in steps.items():
            step['body'] += (
                '\n\n**Multicast en IPv6 (MLD vs IGMP):**\n'
                'IPv6 no soporta broadcast; depende puramente de multicast. En IPv6, el protocolo **MLD (Multicast Listener Discovery)** '
                '(RFC 3810) reemplaza a IGMP. MLDv1 equivale a IGMPv2, y MLDv2 equivale a IGMPv3. MLD se encapsula directamente '
                'sobre paquetes ICMPv6 (tipos 130, 131 y 132 para v1, y 143 para v2). Si bloqueas ICMPv6 por seguridad de forma descuidada, '
                'romperás por completo el tráfico Multicast IPv6 y los protocolos de descubrimiento.'
            )
            cmds = step.get('commands', {})
            # Juniper MLD / PIM6
            add_cmd(cmds, 'juniper', 'tier1', 'show mld interface')
            add_cmd(cmds, 'juniper', 'tier1', 'show mld groups')
            add_cmd(cmds, 'juniper', 'tier1', 'show pim6 neighbors')
            # Cisco IOS-XE MLD / PIM6
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ipv6 mld interface')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ipv6 mld groups')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ipv6 pim neighbor')
            # Cisco IOS-XR MLD / PIM6
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show mld interface')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show mld groups')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show pim ipv6 neighbor')

    # ==========================================================================
    # H. NATIVE IPv6 CONFIGURATION & SECURITY (RA Guard, ND Snooping)
    # ==========================================================================
    if 'ipv6_config' in base:
        tech = base['ipv6_config']
        steps = tech.get('steps', {})
        
        # Paso: ipv6_config_tunnels
        # Agregar sección de seguridad de red IPv6 (RA Guard y ND Inspection)
        if 'ipv6_config_tunnels' in steps:
            steps['ipv6_config_tunnels']['body'] += (
                '\n\n**Seguridad IPv6 Avanzada (RA Guard e Inspection) (RFC 6105):**\n'
                '- **IPv6 RA Guard:** Bloquea de forma inteligente los paquetes Router Advertisement (RA) falsos o no autorizados '
                'enviados por usuarios maliciosos que intentan actuar como gateway de la red (ataques Man-in-the-Middle). Se debe aplicar '
                'en todos los puertos de acceso que no vayan conectados a routers autorizados.\n'
                '- **IPv6 Neighbor Discovery Inspection (ND Inspection):** Mantiene una tabla de bindings IPv6-MAC validada a través de '
                'DHCPv6 Snooping. Bloquea mensajes Neighbor Advertisement (NA) falsos que busquen envenenar la tabla de vecinos (NDP Cache Poisoning).'
            )
            cmds = steps['ipv6_config_tunnels'].get('commands', {})
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'configure terminal \n ipv6 nd raguard policy RAGUARD \n interface GigabitEthernet0/1 \n ipv6 nd raguard attach-policy RAGUARD \n end')
            add_cmd(cmds, 'juniper', 'tier1', 'configure \n set switch-options secure-access-port interface ge-0/0/1.0 ipv6-ra-guard \n commit')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'configure \n interface GigabitEthernet0/0/0/0 \n ipv6 nd raguard \n commit')
            
        # Para proveedores de acceso (GPON/OLT)
        for gpon_key in ('zte', 'huawei', 'zhone', 'adtran', 'ta5k', 'zone'):
            if 'ipv6_config_start' in steps:
                steps['ipv6_config_start']['body'] += (
                    '\n\n**Asignación de WAN IPv6 en Redes de Acceso GPON:**\n'
                    '- Los clientes residenciales (ONTs) típicamente adquieren su direccionamiento IPv6 a través de **DHCPv6 Prefix Delegation (DHCPv6-PD)**. '
                    'El OLT delega un prefijo corto (ej: un `/56` o `/60`) a la ONT. El Router del cliente auto-subdivide ese prefijo '
                    'en subredes `/64` para sus interfaces LAN internas, y activa SLAAC para los dispositivos locales.'
                )
                cmds = steps['ipv6_config_start'].get('commands', {})
                # Agregar configuraciones de IPv6 WAN y DHCPv6 Prefix Delegation para clientes FTTH
                add_cmd(cmds, 'adtran', 'tier1', 'configure terminal \n interface gigabit-ethernet 1/1 \n ipv6 dhcp client pd GPON-PD \n interface gigabit-ethernet 1/2 \n ipv6 address GPON-PD ::1/64 \n end')
                add_cmd(cmds, 'ta5k', 'tier1', 'configure terminal \n interface gigabit-ethernet 1/1 \n ipv6 dhcp client pd GPON-PD \n end')
                add_cmd(cmds, 'huawei', 'tier1', 'system-view \n ipv6 route-static ::/0 2001:db8::1 \n quit \n save')
                add_cmd(cmds, 'zte', 'tier1', 'configure terminal \n ipv6 route ::/0 2001:db8::1 \n end')

    # ==========================================================================
    # I. SIMULATED OUTPUTS ENRICHMENT
    # ==========================================================================
    try:
        from data.simulated_outputs import SIMULATED_OUTPUTS
        
        # OSPFv3 Neighbors
        add_output(SIMULATED_OUTPUTS, 'ospf', 'ospf_neighbor', 'juniper', 'show ospf3 neighbor extensive', 
                   "Neighbor 2.2.2.2, Interface ge-0/0/1.0\n  Area 0.0.0.0, Lnk-Lcl Addr fe80::200:ff:fe00:2\n  State Full, Prior 128, Val 4\n  DR 2.2.2.2, BDR 1.1.1.1\n  Up 04:32:10, Dead 35\n")
        add_output(SIMULATED_OUTPUTS, 'ospf', 'ospf_neighbor', 'juniper', 'show ospf3 interface detail', 
                   "Interface ge-0/0/1.0 (fe80::100:ff:fe00:1)\n  Area 0.0.0.0, Status DR, Prior 128\n  Type P2P, State Up\n")
        add_output(SIMULATED_OUTPUTS, 'ospf', 'ospf_neighbor', 'cisco_iosxe', 'show ospfv3 neighbor detail', 
                   "Neighbor 2.2.2.2, interface GigabitEthernet0/1\n  Area 0, source address fe80::200:ff:fe00:2\n  Neighbor state is FULL, detail state is flag 0\n  DR is 2.2.2.2, BDR is 1.1.1.1\n  Dead timer due in 00:00:36\n")
        add_output(SIMULATED_OUTPUTS, 'ospf', 'ospf_neighbor', 'cisco_iosxr', 'show ospfv3 neighbor detail', 
                   "Neighbor 2.2.2.2, interface GigabitEthernet0/0/0/0\n  Area 0, source address fe80::200:ff:fe00:2\n  Neighbor state is FULL, detail state is flag 0\n  DR is 2.2.2.2, BDR is 1.1.1.1\n  Dead timer due in 00:00:37\n")
        add_output(SIMULATED_OUTPUTS, 'ospf', 'ospf_neighbor', 'mikrotik', '/routing ospf v3 neighbor print detail', 
                   "instance=default-v3 area=backbone interface=ether1 router-id=2.2.2.2 state=Full address=fe80::200:ff:fe00:2 priority=1 dr=2.2.2.2 bdr=1.1.1.1 adjacency=04:32:10\n")
        add_output(SIMULATED_OUTPUTS, 'ospf', 'ospf_neighbor', 'fortinet', 'get router info6 ospf neighbor detail', 
                   "Neighbor 2.2.2.2, interface port1\n  Area: 0.0.0.0, Address: fe80::200:ff:fe00:2\n  State: Full, Priority: 1\n  DR: 2.2.2.2, BDR: 1.1.1.1\n  Up: 04:32:10, Dead: 36\n")

        # BGP / MP-BGP summary
        for bgp_key in ('bgp', 'mpbgp'):
            add_output(SIMULATED_OUTPUTS, bgp_key, 'bgp_start' if bgp_key == 'bgp' else 'mpbgp_start', 'cisco_iosxe', 'show bgp ipv6 unicast summary', 
                       "BGP router identifier 1.1.1.1, local AS number 65000\nBGP table version is 12\nNeighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd\n2001:db8:1::2   4        65000     250     251       12    0    0 04:32:10        4\n")
            add_output(SIMULATED_OUTPUTS, bgp_key, 'bgp_start' if bgp_key == 'bgp' else 'mpbgp_start', 'cisco_iosxr', 'show bgp ipv6 unicast summary', 
                       "BGP router identifier 1.1.1.1, local AS number 65000\nBGP table version is 12\nNeighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd\n2001:db8:1::2   4        65000     250     251       12    0    0 04:32:10        4\n")

        # L3VPN (6VPE) routes
        add_output(SIMULATED_OUTPUTS, 'l3vpn', 'l3vpn_start', 'cisco_iosxe', 'show ipv6 route vrf <vrf-name>', 
                   "Routing Table: VRF-A\nIPv6 Routing Table - 1 entries\nB    2001:db8:100::/64 [200/0]\n     via 2001:db8:1::2 (next-hop in vrf default)\n")
        add_output(SIMULATED_OUTPUTS, 'l3vpn', 'l3vpn_start', 'juniper', 'show route table <vrf-name>.inet6.0', 
                   "VRF-A.inet6.0: 1 destinations, 1 routes (1 active)\n2001:db8:100::/64  *[BGP/170] 04:32:10, localpref 100\n                    > to fe80::200:ff:fe00:2 via ge-0/0/1.0, Push 16002\n")

    except Exception:
        pass
