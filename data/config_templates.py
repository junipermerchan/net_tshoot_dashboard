"""
data/config_templates.py — Plantillas de Configuración & Explicador Comando por Comando por Vendor.
Organizadas rigurosamente por el Plan de Estudios CCNA & CCNP con Cobertura Master IPv6 Completa.
"""

from typing import Dict, Any, List

CONFIG_TEMPLATES: Dict[str, Dict[str, Any]] = {
    'ipv6_master_template': {
        'title': '🌐 CCNA / CCNP — Máster IPv6 (NDP, SLAAC, DHCPv6, OSPFv3, MP-BGP IPv6, 6VPE & Firewall IPv6)',
        'description': 'Guía integral especializada de direccionamiento IPv6 (Global Unicast 2001:db8::/32, Link-Local fe80::), Neighbor Discovery (NDP), OSPFv3, MP-BGP IPv6 Unicast, L3VPN IPv6 (6VPE) y Políticas de Seguridad IPv6 para todos los fabricantes.',
        'vendors': {
            'cisco_iosxe': {
                'vendor_name': 'Cisco IOS-XE (ISR / ASR / Catalyst)',
                'code': (
                    "configure terminal\n"
                    "# 1. HABILITAR UNICAST ROUTING IPV6 GLOBAL\n"
                    "ipv6 unicast-routing\n"
                    "ipv6 cef\n"
                    "\n"
                    "# 2. CONFIGURACIÓN DE INTERFAZ DUAL STACK & SLAAC / DHCPv6\n"
                    "interface GigabitEthernet0/0/1\n"
                    " description ** INTERFAZ LAN DUAL-STACK IPV6 **\n"
                    " ipv6 address 2001:db8:1000:10::1/64\n"
                    " ipv6 address fe80::1 link-local\n"
                    " ipv6 nd ra-interval 5\n"
                    " ipv6 ospf 1 area 0\n"
                    "exit\n"
                    "\n"
                    "# 3. OSPFV3 MULTI-AREA IPV6\n"
                    "router ospfv3 1\n"
                    " router-id 1.1.1.1\n"
                    " area 0 authentication ipsec spi 1000 sha1 SuperSecretPass123!\n"
                    "exit\n"
                    "\n"
                    "# 4. MP-BGP IPV6 UNICAST\n"
                    "router bgp 65000\n"
                    " bgp router-id 1.1.1.1\n"
                    " neighbor 2001:db8:ffff::2 remote-as 65002\n"
                    " address-family ipv6 unicast\n"
                    "  neighbor 2001:db8:ffff::2 activate\n"
                    "  neighbor 2001:db8:ffff::2 prefix-list PL-IPV6-IN in\n"
                    " exit-address-family\n"
                    "end\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'ipv6 unicast-routing', 'desc': 'Habilita el reenvío de paquetes IPv6 Unicast en el router Cisco.'},
                    {'cmd': 'ipv6 address 2001:db8:1000:10::1/64', 'desc': 'Asigna la dirección IPv6 Global Unicast (GUA) con prefijo /64.'},
                    {'cmd': 'ipv6 address fe80::1 link-local', 'desc': 'Fija la dirección Link-Local fe80::1 fija de forma manual para evitar autogenerar EUI-64 aleatorio.'},
                    {'cmd': 'ipv6 ospf 1 area 0', 'desc': 'Activa OSPFv3 directamente bajo el modo de interfaz sin necesidad de comando network.'},
                    {'cmd': 'address-family ipv6 unicast', 'desc': 'Activa el intercambio de rutas IPv6 sobre BGP Multiprotocol (MP-BGP).'}
                ]
            },
            'juniper': {
                'vendor_name': 'Juniper JunOS (MX / ACX / SRX)',
                'code': (
                    "configure\n"
                    "set interfaces ge-0/0/0 unit 0 family inet6 address 2001:db8:1000:10::1/64\n"
                    "set interfaces ge-0/0/0 unit 0 family inet6 address fe80::1 eui-64\n"
                    "set protocols ospf3 area 0.0.0.0 interface ge-0/0/0.0\n"
                    "set protocols bgp group EBGP-IPV6 type external\n"
                    "set protocols bgp group EBGP-IPV6 neighbor 2001:db8:ffff::2 family inet6 unicast\n"
                    "commit check\n"
                    "commit"
                ),
                'breakdown': [
                    {'cmd': 'set interfaces ge-0/0/0 unit 0 family inet6...', 'desc': 'Asigna la familia IPv6 (inet6) en JunOS.'},
                    {'cmd': 'set protocols ospf3 area 0.0.0.0...', 'desc': 'Habilita OSPFv3 en el área 0.'}
                ]
            },
            'huawei': {
                'vendor_name': 'Huawei VRP (NetEngine / AR Router)',
                'code': (
                    "system-view\n"
                    "ipv6\n"
                    "interface GigabitEthernet0/0/1\n"
                    " ipv6 enable\n"
                    " ipv6 address 2001:db8:1000:10::1/64\n"
                    " ipv6 address fe80::1 link-local\n"
                    " ospfv3 1 area 0.0.0.0\n"
                    "quit\n"
                    "bgp 65000\n"
                    " router-id 1.1.1.1\n"
                    " ipv6-family unicast\n"
                    "  peer 2001:db8:ffff::2 enable\n"
                    "save"
                ),
                'breakdown': [
                    {'cmd': 'ipv6 / ipv6 enable', 'desc': 'Activa la pila dual IPv6 en la vista de sistema e interfaz de VRP.'},
                    {'cmd': 'ospfv3 1 area 0.0.0.0', 'desc': 'Habilita OSPFv3 en la interfaz.'}
                ]
            },
            'fortinet': {
                'vendor_name': 'Fortinet FortiOS (FortiGate IPv6 Firewall)',
                'code': (
                    "config system global\n"
                    "  set gui-ipv6 enable\n"
                    "end\n"
                    "config system interface\n"
                    "  edit \"port1\"\n"
                    "    config ipv6\n"
                    "      set ip6-address 2001:db8:1000:10::1/64\n"
                    "      set ip6-allowaccess ping\n"
                    "    end\n"
                    "  next\n"
                    "end\n"
                    "config firewall policy6\n"
                    "  edit 1\n"
                    "    set name \"POL_LAN_TO_WAN_IPV6\"\n"
                    "    set srcintf \"port2\"\n"
                    "    set dstintf \"port1\"\n"
                    "    set srcaddr6 \"all\"\n"
                    "    set dstaddr6 \"all\"\n"
                    "    set action accept\n"
                    "    set schedule \"always\"\n"
                    "    set service \"ALL\"\n"
                    "  next\n"
                    "end"
                ),
                'breakdown': [
                    {'cmd': 'config firewall policy6', 'desc': 'Configura reglas de seguridad específicas para tráfico IPv6 en FortiOS.'}
                ]
            },
            'sophos': {
                'vendor_name': 'Sophos SFOS (XG / XGS IPv6 Firewall)',
                'code': (
                    "system network interface edit Port1 ipv6-address 2001:db8:1000:10::1 prefix-len 64\n"
                    "system firewall-rule add name POL_IPV6_INTERNET srczone LAN dstzone WAN ip-family IPv6 action accept"
                ),
                'breakdown': [
                    {'cmd': 'system firewall-rule add ... ip-family IPv6', 'desc': 'Crea regla de cortafuegos para tráfico IPv6 en Sophos SFOS.'}
                ]
            },
            'mikrotik': {
                'vendor_name': 'MikroTik RouterOS v7 (IPv6 Package)',
                'code': (
                    "/ipv6 settings set disable-ipv6=no\n"
                    "/ipv6 address add address=2001:db8:1000:10::1/64 interface=ether1\n"
                    "/ipv6 route add dst-address=::/0 gateway=2001:db8:1000:10::fe\n"
                    "/routing ospf instance add name=ospf-v6-inst version=3\n"
                    "/routing ospf area add instance=ospf-v6-inst name=area0-v6 area-id=0.0.0.0"
                ),
                'breakdown': [
                    {'cmd': '/ipv6 address add address=...', 'desc': 'Asigna dirección IPv6 GUA en MikroTik.'}
                ]
            }
        }
    },
    'noc_ccna_base': {
        'title': '🛡️ CCNA / CCNP — Inicialización, Hardening & Gestión NOC',
        'description': 'Plantilla estándar de inicialización y hardening (ISO 27001) adaptada exactamente a los comandos y sintaxis nativa de cada fabricante.',
        'vendors': {
            'cisco_iosxe': {
                'vendor_name': 'Cisco IOS-XE (ISR / ASR 1000 / Catalyst 9000)',
                'code': (
                    "configure terminal\n"
                    "hostname Router-NOC-CE1\n"
                    "banner motd ^C ACCESO AUTORIZADO UNICAMENTE PERSONAL NOC ^C\n"
                    "enable secret SuperPasswordNOC123!\n"
                    "username admin privilege 15 secret SuperAdminNOC123!\n"
                    "clock timezone COT -5\n"
                    "ip domain name noc.operador.net\n"
                    "crypto key generate rsa modulus 2048\n"
                    "ip ssh version 2\n"
                    "line vty 0 4\n"
                    " exec-timeout 5 0\n"
                    " transport input ssh\n"
                    " login local\n"
                    "ntp server 10.0.0.1 prefer\n"
                    "logging host 10.0.0.50\n"
                    "snmp-server community NOC_READ RO\n"
                    "end\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'configure terminal', 'desc': 'Modo de configuración global de Cisco IOS-XE.'},
                    {'cmd': 'hostname Router-NOC-CE1', 'desc': 'Asigna el nombre único del equipo.'},
                    {'cmd': 'enable secret SuperPasswordNOC123!', 'desc': 'Establece la clave enable cifrada con algoritmo SHA-256.'},
                    {'cmd': 'crypto key generate rsa modulus 2048', 'desc': 'Genera el par de llaves RSA de 2048 bits para SSH.'},
                    {'cmd': 'transport input ssh', 'desc': 'Deshabilita Telnet y fuerza el uso exclusivo de SSHv2.'}
                ]
            }
        }
    }
}
