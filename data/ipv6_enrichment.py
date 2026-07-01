"""
Módulo de Enriquecimiento de IPv6 para Network Tshoot Dashboard.
Añade programáticamente soporte exhaustivo de IPv6 en todas las tecnologías, vendors y comandos simulados.
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
    # 1. OSPF / OSPFv3 ENRICHMENT
    # ==========================================================================
    if 'ospf' in base:
        tech = base['ospf']
        steps = tech.get('steps', {})
        
        # Paso 1: OSPF Start
        if 'ospf_start' in steps:
            steps['ospf_start']['body'] += (
                '\n\n**Soporte de IPv6 (OSPFv3):** OSPFv3 (RFC 5340) se utiliza para enrutar prefijos IPv6. '
                'Se ejecuta sobre enlaces IPv6 usando direcciones Link-Local (fe80::/10) como siguiente salto. '
                'El enrutamiento debe estar explícitamente habilitado.'
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

        # Paso 3: OSPF Autenticación
        if 'ospf_auth' in steps:
            steps['ospf_auth']['body'] += (
                '\n\n**Autenticación en OSPFv3 (IPv6):** OSPFv3 no posee mecanismos nativos de autenticación. '
                'Depende directamente de IPsec SA (Security Associations) y cabeceras AH/ESP configuradas bajo la interfaz.'
            )
            cmds = steps['ospf_auth'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'show security ipsec security-associations')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show crypto ipsec sa')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show crypto ipsec sa')

        # Paso 4: OSPF Database (Base de datos LSA)
        if 'ospf_database' in steps:
            cmds = steps['ospf_database'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'show ospf3 database')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ospfv3 database')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show ospfv3 database')
            add_cmd(cmds, 'fortinet', 'tier1', 'get router info6 ospf database')

    # ==========================================================================
    # 2. IS-IS MULTI-TOPOLOGY IPv6 ENRICHMENT
    # ==========================================================================
    if 'isis' in base:
        tech = base['isis']
        steps = tech.get('steps', {})
        
        # Paso 1: IS-IS database
        if 'isis_database' in steps:
            steps['isis_database']['body'] += (
                '\n\n**Multi-Topology (MT) en IS-IS IPv6:** Asegúrese de que la base de datos de LSPs contenga '
                'el TLV 236 (IPv6 Reachability) y el TLV 229 (MT-IS-IS). Sin la configuración de Multi-Topology, '
                'IS-IS asume una topología única y el enrutamiento IPv6 fallará si no hay simetría exacta con IPv4.'
            )
            cmds = steps['isis_database'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'show isis database extensive | match "IPv6"')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show isis database detail | include IPv6')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show isis database detail | include IPv6')

        # Paso 2: IS-IS interfaces
        if 'isis_adj' in steps:
            cmds = steps['isis_adj'].get('commands', {})
            add_cmd(cmds, 'juniper', 'tier1', 'show route table inet6.0 protocol isis')
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ipv6 route isis')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show ipv6 route isis')

    # ==========================================================================
    # 3. BGP / MP-BGP IPv6 ENRICHMENT
    # ==========================================================================
    for bgp_key in ('bgp', 'mpbgp'):
        if bgp_key in base:
            tech = base[bgp_key]
            steps = tech.get('steps', {})
            for step_key, step in steps.items():
                cmds = step.get('commands', {})
                # Juniper
                add_cmd(cmds, 'juniper', 'tier1', 'show bgp neighbor | match "Address families"')
                add_cmd(cmds, 'juniper', 'tier2', 'show route table inet6.0 protocol bgp')
                # Cisco IOS-XE
                add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show bgp ipv6 unicast summary')
                add_cmd(cmds, 'cisco_iosxe', 'tier2', 'show ipv6 route bgp')
                # Cisco IOS-XR
                add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show bgp ipv6 unicast summary')
                add_cmd(cmds, 'cisco_iosxr', 'tier2', 'show ipv6 route bgp')
                # Fortinet
                add_cmd(cmds, 'fortinet', 'tier1', 'get router info6 bgp summary')

    # ==========================================================================
    # 4. L3VPN (6VPE) ENRICHMENT
    # ==========================================================================
    if 'l3vpn' in base:
        tech = base['l3vpn']
        steps = tech.get('steps', {})
        for step_key, step in steps.items():
            if 'route' in step_key or 'start' in step_key:
                cmds = step.get('commands', {})
                # Juniper
                add_cmd(cmds, 'juniper', 'tier1', 'show route table <vrf-name>.inet6.0')
                # Cisco IOS-XE
                add_cmd(cmds, 'cisco_iosxe', 'tier1', 'show ipv6 route vrf <vrf-name>')
                # Cisco IOS-XR
                add_cmd(cmds, 'cisco_iosxr', 'tier1', 'show ipv6 route vrf <vrf-name>')
                # Fortinet
                add_cmd(cmds, 'fortinet', 'tier1', 'get router info6 routing-table vrf <vrf-name>')

    # ==========================================================================
    # 5. STATIC ROUTING IPv6 ENRICHMENT
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
    # 6. MULTICAST (MLD / PIMv6) ENRICHMENT
    # ==========================================================================
    if 'multicast' in base:
        tech = base['multicast']
        steps = tech.get('steps', {})
        for step_key, step in steps.items():
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
    # 7. NATIVE IPv6 SECURITY & DHCPv6-PD ENRICHMENT
    # ==========================================================================
    if 'ipv6_config' in base:
        tech = base['ipv6_config']
        steps = tech.get('steps', {})
        
        # Paso: ipv6_config_tunnels
        # Vamos a agregar una sección de seguridad de red IPv6 (RA Guard y ND Inspection)
        if 'ipv6_config_tunnels' in steps:
            steps['ipv6_config_tunnels']['body'] += (
                '\n\n**Seguridad IPv6 Avanzada (RA Guard e Inspection):**\n'
                '- Evite ataques de Man-in-the-Middle y autoconfiguración no autorizada mitigando Router Advertisements falsos.\n'
                '- **Cisco IOS-XE RA Guard:**\n'
                '  `ipv6 nd raguard policy RAGUARD-POLICY` \n'
                '  `interface GigabitEthernet0/1 \n   ipv6 nd raguard attach-policy RAGUARD-POLICY` \n'
                '- **Juniper RA Guard:**\n'
                '  `set switch-options secure-access-port interface ge-0/0/1.0 ipv6-ra-guard`'
            )
            cmds = steps['ipv6_config_tunnels'].get('commands', {})
            add_cmd(cmds, 'cisco_iosxe', 'tier1', 'configure terminal \n ipv6 nd raguard policy RAGUARD \n interface GigabitEthernet0/1 \n ipv6 nd raguard attach-policy RAGUARD \n end')
            add_cmd(cmds, 'juniper', 'tier1', 'configure \n set switch-options secure-access-port interface ge-0/0/1.0 ipv6-ra-guard \n commit')
            add_cmd(cmds, 'cisco_iosxr', 'tier1', 'configure \n interface GigabitEthernet0/0/0/0 \n ipv6 nd raguard \n commit')
            
        # Para proveedores de acceso (GPON/OLT)
        for gpon_key in ('zte', 'huawei', 'zhone', 'adtran', 'ta5k', 'zone'):
            if 'ipv6_config_start' in steps:
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
