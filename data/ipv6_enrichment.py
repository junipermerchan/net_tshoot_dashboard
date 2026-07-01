"""
Módulo de Enriquecimiento de IPv6 Avanzado para Network Tshoot Dashboard.
Añade programáticamente soporte y guías de nivel Enterprise/Service Provider (CCIE/JNCIE) 
de IPv6 en todas las tecnologías, vendors y comandos simulados.
Permite la alternancia de descripciones, títulos y comportamientos esperados en la UI.
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
    # 1. OSPF / OSPFv3 ENRICHMENT (QUIRÚRGICO)
    # ==========================================================================
    if 'ospf' in base:
        tech = base['ospf']
        steps = tech.get('steps', {})
        
        # Paso 1: OSPF Start
        if 'ospf_start' in steps:
            steps['ospf_start']['title_ipv6'] = "1. Ámbito del problema OSPFv3"
            steps['ospf_start']['body_ipv6'] = (
                "**Dónde:** Vecindades OSPFv3 (IPv6), base de datos LSAs IPv6, áreas, "
                "redistribución, autenticación IPsec o rendimiento.\n\n"
                "**Cómo:** Vecinos caídos, rutas IPv6 ausentes en la RIB, alta CPU por SPF "
                "recalculaciones, o falla de establecimiento de SAs de IPsec.\n\n"
                "**Cuándo:** Tras cambios de direccionamiento link-local, aplicación de llaves IPsec "
                "o redistribución de prefijos IPv6.\n\n"
                "**Por qué:** Direcciones link-local duplicadas o inactivas, desajuste en MTU (EXSTART), "
                "timers de Hello/Dead no coincidentes, o llaves de IPsec SPI incorrectas.\n\n"
                "**Para qué:** Enfocar el troubleshooting de OSPFv3 en adyacencias link-local, "
                "sincronización de LSAs de tipo 8/9 o políticas de redistribución IPv6."
            )
            steps['ospf_start']['expected_ipv6'] = (
                "Identificación del Router-ID de 32 bits (configurado de forma manual obligatoria en entornos IPv6-only), "
                "interfaces de área y conectividad link-local."
            )
            
        # Paso 2: OSPF Neighbors
        if 'ospf_neighbor' in steps:
            steps['ospf_neighbor']['title_ipv6'] = "2. Vecindades OSPFv3 caídas"
            steps['ospf_neighbor']['body_ipv6'] = (
                "**Dónde:** Interfaces habilitadas para OSPFv3 y sesiones de vecindad IPv6.\n\n"
                "**Cómo:** Vecino stuck en INIT (unidireccional), 2-WAY (normal en segmentos broadcast si no es DR/BDR) o stuck en EXSTART/EXCHANGE.\n\n"
                "**Por qué:** OSPFv3 forma adyacencias utilizando direcciones link-local (fe80::/10). Si no hay comunicación link-local, "
                "si el MTU difiere (EXSTART), o si la asociación de seguridad IPsec (IPsec SA) está mal configurada, la sesión fallará.\n\n"
                "**Seguridad:** El firewall debe permitir tráfico OSPFv3 (protocolo IP 89) solo si proviene de direcciones de origen link-local (fe80::/10)."
            )
            steps['ospf_neighbor']['expected_ipv6'] = (
                "Vecindad OSPFv3 en estado FULL. Timers Hello/Dead y MTU coincidentes. "
                "Asociación IPsec SPI activa en ambos extremos del enlace."
            )
            cmds = steps['ospf_neighbor'].get('commands', {})
            # Juniper OSPFv3
            add_cmd(cmds, 'juniper', 'tier1', 'show ospf3 neighbor extensive')
            add_cmd(cmds, 'juniper', 'tier1', 'show ospf3 interface detail')
            add_cmd(cmds, 'juniper', 'tier2', 'show configuration protocols ospf3 | display set')
            add_cmd(cmds, 'juniper', 'tier2', 'show ospf3 neighbor extensive | match state')
            add_cmd(cmds, 'juniper', 'tier3', 'monitor traffic interface <if> matching "ospf3" | no-more')
            # Cisco IOS-XR OSPFv3
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show ospfv3 neighbor detail')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show ospfv3 interface')
            add_cmd(cmds, 'cisco_iosxr', 'tier2', 'show running-config router ospfv3')
            add_cmd(cmds, 'cisco_iosxr', 'tier2', 'show ospfv3 neighbor detail | include state')
            add_cmd(cmds, 'cisco_iosxr', 'tier3', 'debug ospfv3 hello')
            # Cisco IOS-XE OSPFv3
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ospfv3 neighbor detail')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ospfv3 interface')
            add_cmd(cmds, 'cisco_iosxe', 'tier2', 'show running-config | section router ospfv3')
            add_cmd(cmds, 'cisco_iosxe', 'tier2', 'show ospfv3 neighbor detail | include state')
            add_cmd(cmds, 'cisco_iosxe', 'tier3', 'debug ospfv3 hello')
            # MikroTik OSPFv3
            add_cmd(cmds, 'mikrotik', 'tier1', '/routing ospf v3 neighbor print detail')
            add_cmd(cmds, 'mikrotik', 'tier2', '/routing ospf v3 interface print')
            # Fortinet OSPFv3
            add_cmd(cmds, 'fortinet', 'tier1', 'get router info6 ospf neighbor detail')
            add_cmd(cmds, 'fortinet', 'tier1', 'get router info6 ospf interface')
            add_cmd(cmds, 'fortinet', 'tier2', 'show router ospf6')

        # Paso 3: OSPF Autenticación
        if 'ospf_auth' in steps:
            steps['ospf_auth']['title_ipv6'] = "2.A Autenticación OSPFv3 por IPsec"
            steps['ospf_auth']['body_ipv6'] = (
                "**Objetivo:** Verificar y configurar la seguridad en OSPFv3.\n\n"
                "OSPFv3 no posee soporte nativo para claves MD5 o texto claro. La autenticación se delega directamente a la suite IPsec (cabecera AH o ESP). "
                "Se debe definir un SPI (Security Parameter Index) y una clave de autenticación hexadecimal idéntica en ambos extremos de la interfaz. "
                "Un desajuste de SPI o clave hará que los routers descarten los Hellos de forma silenciosa."
            )
            steps['ospf_auth']['expected_ipv6'] = "Asociaciones de seguridad IPsec (SAs) establecidas y activas (SPI idénticos en ambos lados)."
            cmds = steps['ospf_auth'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'show security ipsec security-associations')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show crypto ipsec sa')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show crypto ipsec sa')

        # Paso 4: OSPF Database (Base de datos LSA)
        if 'ospf_database' in steps:
            steps['ospf_database']['title_ipv6'] = "3. Base de datos LSAs de OSPFv3"
            steps['ospf_database']['body_ipv6'] = (
                "**Objetivo:** Diagnosticar la base de datos de LSAs de OSPFv3.\n\n"
                "OSPFv3 introduce nuevos LSAs para desligar el direccionamiento de la topología:\n"
                "- **Link LSA (Type 8):** Anuncia la dirección link-local del router y prefijos IPv6 del enlace a todos los vecinos en ese enlace.\n"
                "- **Intra-Area-Prefix LSA (Type 9):** Anuncia los prefijos IPv6 asociados a un router o una red de tránsito dentro del área sin modificar los LSAs de Router (Type 1) ni Network (Type 2)."
            )
            steps['ospf_database']['expected_ipv6'] = "LSAs Tipo 8 y Tipo 9 presentes y sincronizados en todos los vecinos del área."
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
    # 2. IS-IS MULTI-TOPOLOGY IPv6 ENRICHMENT (QUIRÚRGICO)
    # ==========================================================================
    if 'isis' in base:
        tech = base['isis']
        steps = tech.get('steps', {})
        
        # Paso 1: IS-IS Start
        if 'isis_start' in steps:
            steps['isis_start']['title_ipv6'] = "1. Ámbito del problema IS-IS IPv6"
            steps['isis_start']['body_ipv6'] = (
                "**Dónde:** Adyacencias IS-IS L1/L2 y enrutamiento IPv6 dinámico.\n\n"
                "**Cómo:** Adyacencias caídas o rutas IPv6 ausentes en la tabla de enrutamiento (RIB).\n\n"
                "**Por qué:** Desajuste en el nivel del router (L1 vs L2), desajuste de MTU (IS-IS requiere tramas de 1492 bytes completas), "
                "o falta de activación del soporte Multi-Topology (MT) para IPv6."
            )
            steps['isis_start']['expected_ipv6'] = "Identificación del nivel de routing, MTU e interfaces activas para IPv6."

        # Paso 2: IS-IS adj
        if 'isis_adj' in steps:
            steps['isis_adj']['title_ipv6'] = "2. Adyacencias IS-IS sobre IPv6"
            steps['isis_adj']['body_ipv6'] = (
                "**Dónde:** Adyacencias de capa 2 formadas por IS-IS.\n\n"
                "**Cómo:** Vecino en estado UP pero sin aprender rutas IPv6.\n\n"
                "**Por qué:** IS-IS se ejecuta directamente sobre capa 2. La adyacencia se mantendrá estable incluso si el direccionamiento IPv6 "
                "local está roto. Debe verificar el direccionamiento IP local y el intercambio de TLVs de IP."
            )
            steps['isis_adj']['expected_ipv6'] = "Adyacencia IS-IS en estado UP. IP local IPv6 intercambiada con éxito."
            cmds = steps['isis_adj'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'show route table inet6.0 protocol isis')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ipv6 route isis')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show ipv6 route isis')

        # Paso 3: IS-IS database
        if 'isis_database' in steps:
            steps['isis_database']['title_ipv6'] = "3. LSP Database y Multi-Topology IPv6"
            steps['isis_database']['body_ipv6'] = (
                "**Objetivo:** Verificar el soporte de Multi-Topology (MT) en la LSPDB.\n\n"
                "En redes IPv6, se debe activar la capability **Multi-Topology (MT) (RFC 5120)**. Esto permite calcular árboles SPF separados "
                "para IPv4 e IPv6. Sin MT, IS-IS asume una topología única y el enrutamiento fallará si un enlace no tiene IPv6 configurado.\n\n"
                "Verifique la presencia del **TLV 229 (MT-IS-IS)** y el **TLV 236 (IPv6 Reachability)**."
            )
            steps['isis_database']['expected_ipv6'] = "Base de datos sincronizada con TLV 229 y TLV 236 presentes."
            cmds = steps['isis_database'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'show isis database extensive | match "IPv6"')
            add_cmd(cmds, 'juniper', 'tier2', 'show isis database extensive | match "Multi-topology"')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show isis database detail | include IPv6')
            add_cmd(cmds, 'cisco_iosxe', 'tier2', 'show isis database detail | include Multi-Topology')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show isis database detail | include IPv6')

    # ==========================================================================
    # 3. BGP / MP-BGP IPv6 & NEXT-HOP RESOLUTION (QUIRÚRGICO)
    # ==========================================================================
    for bgp_key in ('bgp', 'mpbgp'):
        if bgp_key in base:
            tech = base[bgp_key]
            steps = tech.get('steps', {})
            for step_key, step in steps.items():
                if 'start' in step_key or 'neighbor' in step_key:
                    step['title_ipv6'] = "1. Ámbito del problema MP-BGP IPv6"
                    step['body_ipv6'] = (
                        "**Objetivo:** Verificar la conectividad BGP y el soporte de la Address-Family IPv6 (AFI 2, SAFI 1).\n\n"
                        "**Problemas de Next-Hop en MP-BGP IPv6 (RFC 2545 / RFC 8950):**\n"
                        "- Cuando se levanta una sesión BGP utilizando direccionamiento IPv4 pero se anuncia la Address-Family IPv6, "
                        "BGP enviará un Next-Hop con un formato IPv4 mapeado a IPv6 (ej: `::ffff:10.0.0.1`), el cual no se puede resolver en la tabla "
                        "de enrutamiento local y las rutas quedarán en estado **Hidden** o **Invalid**.\n"
                        "- **Solución:** Aplicar una política de exportación (`route-map` / `policy-statement`) para forzar un Next-Hop IPv6 válido, "
                        "o habilitar la negociación de Extended Next-Hop Encoding (RFC 8950) en ambos extremos."
                    )
                    step['expected_ipv6'] = "Sesión BGP en estado ESTABLISHED con capacidad de address-family IPv6 activa y next-hops resolubles."
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
    # 4. L3VPN (6VPE) ENRICHMENT (QUIRÚRGICO)
    # ==========================================================================
    if 'l3vpn' in base:
        tech = base['l3vpn']
        steps = tech.get('steps', {})
        for step_key, step in steps.items():
            if 'route' in step_key or 'start' in step_key:
                step['title_ipv6'] = "1. Ámbito del problema L3VPN (6VPE)"
                step['body_ipv6'] = (
                    "**Objetivo:** Diagnosticar la operatividad de VPNs IPv6 (6VPE).\n\n"
                    "**Operación de 6VPE (IPv6 VPN over MPLS):**\n"
                    "- 6VPE mapea direcciones IPv6 de clientes dentro de VRFs a prefijos VPNv6 (AFI 2, SAFI 128) de 196 bits (RD + IPv6).\n"
                    "- **Pila de Etiquetas MPLS:** Al enviar un paquete 6VPE, se utilizan dos etiquetas: una etiqueta interna (BGP VPNv6) "
                    "que identifica el VRF de destino en el PE remoto, y una etiqueta externa (LDP / Segment Routing) que define el camino "
                    "de tránsito por el core IPv4. Asegúrese de que el router PE local resuelva el Next-Hop IPv4 del PE remoto usando el túnel MPLS."
                )
                step['expected_ipv6'] = "Next-hop PE remoto resoluble mediante túnel MPLS. Rutas VPNv6 activas en BGP."
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
    # 5. STATIC ROUTING IPv6 ENRICHMENT & CONFIGURATION (QUIRÚRGICO)
    # ==========================================================================
    if 'static' in base:
        tech = base['static']
        steps = tech.get('steps', {})
        for step_key, step in steps.items():
            step['title_ipv6'] = "1. Ámbito del Enrutamiento Estático IPv6"
            step['body_ipv6'] = (
                "**Objetivo:** Diagnosticar rutas estáticas IPv6 ausentes o inactivas en la tabla de enrutamiento.\n\n"
                "**Problemas comunes:**\n"
                "- Interfaz de salida caída o dirección link-local del siguiente salto no especificada junto con la interfaz.\n"
                "- Filtros de NDP que impiden resolver la dirección MAC del siguiente salto."
            )
            step['expected_ipv6'] = "Ruta estática IPv6 instalada de forma activa en la tabla de enrutamiento (RIB)."
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
            steps['static_config_start']['body_ipv6'] = (
                "**Objetivo:** Configurar una ruta estática simple IPv6 que apunte a un siguiente salto o interfaz física directamente conectada.\n\n"
                "**Detalles clave:**\n"
                "- Definir el prefijo destino IPv6 (ej: `2001:db8:100::/64`).\n"
                "- Especificar la IP de siguiente salto global o link-local (ej: `2001:db8:12::2` o `fe80::2`). Si se usa una IP link-local, es obligatorio indicar la interfaz de salida (ej: `GigabitEthernet0/1` o `ge-0/0/1.0`).\n\n"
                "**Configuración por Fabricante:**\n"
                "- **Juniper:** `set routing-options static route 2001:db8:100::/64 next-hop 2001:db8:12::2`\n"
                "- **Cisco IOS-XE:** `ipv6 route 2001:db8:100::/64 2001:db8:12::2`\n"
                "- **Cisco IOS-XR:** `router static address-family ipv6 unicast 2001:db8:100::/64 2001:db8:12::2`\n"
                "- **MikroTik:** `/ipv6 route add dst-address=2001:db8:100::/64 gateway=2001:db8:12::2`\n"
                "- **Fortinet:** `config router static6 \n edit 1 \n set dst 2001:db8:100::/64 \n set gateway 2001:db8:12::2 \n next \n end`\n"
                "- **Linux:** `ip -6 route add 2001:db8:100::/64 via 2001:db8:12::2 dev eth0`"
            )
            steps['static_config_start']['expected_ipv6'] = "La ruta IPv6 se añade correctamente a la configuración y se instala de forma activa en la tabla de enrutamiento."
            cmds = steps['static_config_start'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'set routing-options static route 2001:db8:100::/64 next-hop 2001:db8:12::2')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'ipv6 route 2001:db8:100::/64 2001:db8:12::2')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'configure terminal \n router static \n address-family ipv6 unicast \n 2001:db8:100::/64 2001:db8:12::2 \n commit')
            add_cmd(cmds, 'mikrotik', 'tier1', '/ipv6 route add dst-address=2001:db8:100::/64 gateway=2001:db8:12::2')
            add_cmd(cmds, 'fortinet', 'tier1', 'config router static6 \n edit 1 \n set dst 2001:db8:100::/64 \n set gateway 2001:db8:12::2 \n next \n end')
            add_cmd(cmds, 'linux', 'tier1', 'ip -6 route add 2001:db8:100::/64 via 2001:db8:12::2 dev eth0')

    # ==========================================================================
    # 6. MULTICAST IPv6 (MLD / PIMv6) (QUIRÚRGICO)
    # ==========================================================================
    if 'multicast' in base:
        tech = base['multicast']
        steps = tech.get('steps', {})
        for step_key, step in steps.items():
            step['title_ipv6'] = "1. Multicast en IPv6 (MLD y PIMv6)"
            step['body_ipv6'] = (
                "**Objetivo:** Diagnosticar la distribución de tráfico multicast sobre IPv6.\n\n"
                "**Multicast en IPv6 (MLD vs IGMP):**\n"
                "IPv6 no soporta broadcast; depende puramente de multicast. En IPv6, el protocolo **MLD (Multicast Listener Discovery)** "
                "(RFC 3810) reemplaza a IGMP. MLDv1 equivale a IGMPv2, y MLDv2 equivale a IGMPv3. MLD se encapsula directamente "
                "sobre paquetes ICMPv6 (tipos 130, 131 y 132 para v1, y 143 para v2). Si bloqueas ICMPv6 por seguridad de forma descuidada, "
                "romperás por completo el tráfico Multicast IPv6 y los vecinos de PIMv6."
            )
            step['expected_ipv6'] = "Interfaces con MLD activo, grupos multicast IPv6 registrados en la tabla y vecinos PIMv6 en FULL."
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
    # 7. NATIVE IPv6 CONFIGURATION, SUBNETTING & SECURITY (RA Guard, ND Snooping)
    # ==========================================================================
    if 'ipv6_config' in base:
        tech = base['ipv6_config']
        steps = tech.get('steps', {})
        
        # Paso: ipv6_config_tunnels
        # Agregar sección de seguridad de red IPv6 (RA Guard y ND Inspection)
        if 'ipv6_config_tunnels' in steps:
            steps['ipv6_config_tunnels']['title_ipv6'] = "4. Seguridad IPv6 (RA Guard e Inspection)"
            steps['ipv6_config_tunnels']['body_ipv6'] = (
                "**Seguridad IPv6 Avanzada (RA Guard e Inspection) (RFC 6105):**\n"
                "- **IPv6 RA Guard:** Bloquea de forma inteligente los paquetes Router Advertisement (RA) falsos o no autorizados "
                "enviados por usuarios maliciosos que intentan actuar como gateway de la red (ataques Man-in-the-Middle). Se debe aplicar "
                "en todos los puertos de acceso que no vayan conectados a routers autorizados.\n"
                "- **IPv6 Neighbor Discovery Inspection (ND Inspection):** Mantiene una tabla de bindings IPv6-MAC validada a través de "
                "DHCPv6 Snooping. Bloquea mensajes Neighbor Advertisement (NA) falsos que busquen envenenar la tabla de vecinos (NDP Cache Poisoning)."
            )
            steps['ipv6_config_tunnels']['expected_ipv6'] = "Políticas de RA Guard asociadas a puertos y ND Inspection activo en el switch de acceso."
            cmds = steps['ipv6_config_tunnels'].get('commands', {})
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'configure terminal \n ipv6 nd raguard policy RAGUARD \n interface GigabitEthernet0/1 \n ipv6 nd raguard attach-policy RAGUARD \n end')
            add_cmd(cmds, 'juniper', 'tier1', 'configure \n set switch-options secure-access-port interface ge-0/0/1.0 ipv6-ra-guard \n commit')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'configure \n interface GigabitEthernet0/0/0/0 \n ipv6 nd raguard \n commit')
            
        # Para proveedores de acceso (GPON/OLT)
        for gpon_key in ('zte', 'huawei', 'zhone', 'adtran', 'ta5k', 'zone'):
            if 'ipv6_config_start' in steps:
                steps['ipv6_config_start']['body_ipv6'] = (
                    "**Asignación de WAN IPv6 en Redes de Acceso GPON:**\n"
                    "- Los clientes residenciales (ONTs) típicamente adquieren su direccionamiento IPv6 a través de **DHCPv6 Prefix Delegation (DHCPv6-PD)**. "
                    "El OLT delega un prefijo corto (ej: un `/56` o `/60`) a la ONT. El Router del cliente auto-subdivide ese prefijo "
                    "en subredes `/64` para sus interfaces LAN internas, y activa SLAAC para los dispositivos locales."
                )
                cmds = steps['ipv6_config_start'].get('commands', {})
                # Agregar configuraciones de IPv6 WAN y DHCPv6 Prefix Delegation para clientes FTTH
                add_cmd(cmds, 'adtran', 'tier1', 'configure terminal \n interface gigabit-ethernet 1/1 \n ipv6 dhcp client pd GPON-PD \n interface gigabit-ethernet 1/2 \n ipv6 address GPON-PD ::1/64 \n end')
                add_cmd(cmds, 'ta5k', 'tier1', 'configure terminal \n interface gigabit-ethernet 1/1 \n ipv6 dhcp client pd GPON-PD \n end')
                add_cmd(cmds, 'huawei', 'tier1', 'system-view \n ipv6 route-static ::/0 2001:db8::1 \n quit \n save')
                add_cmd(cmds, 'zte', 'tier1', 'configure terminal \n ipv6 route ::/0 2001:db8::1 \n end')

    # ==========================================================================
    # 8. SIMULATED OUTPUTS ENRICHMENT
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
