"""
data/config_templates.py — Plantillas de Configuración & Explicador Comando por Comando por Vendor.
Con Filtrado Estricto de Capacidades Reales por Fabricante.
"""

from typing import Dict, Any, List

CONFIG_TEMPLATES: Dict[str, Dict[str, Any]] = {
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
            },
            'cisco_iosxr': {
                'vendor_name': 'Cisco IOS-XR (ASR 9000 / NCS 5500 / CRS)',
                'code': (
                    "configure\n"
                    "hostname Router-NOC-CORE1\n"
                    "username admin group root-lr secret SuperAdminNOC123!\n"
                    "clock timezone COT -5\n"
                    "domain name noc.operador.net\n"
                    "crypto key generate rsa 2048\n"
                    "ssh server v2\n"
                    "line default exec-timeout 5 0\n"
                    "ntp server 10.0.0.1 prefer\n"
                    "commit"
                ),
                'breakdown': [
                    {'cmd': 'configure', 'desc': 'Inicia sesión en candidato de IOS-XR.'},
                    {'cmd': 'username admin group root-lr...', 'desc': 'Crea usuario en el grupo administrativo root-lr.'},
                    {'cmd': 'commit', 'desc': 'Aplica los cambios atómicamente al plano de control.'}
                ]
            },
            'juniper': {
                'vendor_name': 'Juniper JunOS (MX / ACX / PTX / SRX)',
                'code': (
                    "configure\n"
                    "set system host-name Router-NOC-CE1\n"
                    "set system root-authentication plain-text-password\n"
                    "set system login user admin class super-user authentication plain-text-password\n"
                    "set system time-zone America/Bogota\n"
                    "set system services ssh protocol-version v2\n"
                    "set system idle-timeout 5\n"
                    "set system ntp server 10.0.0.1 prefer\n"
                    "set system syslog host 10.0.0.50 any notice\n"
                    "set snmp community NOC_READ authorization read-only\n"
                    "commit check\n"
                    "commit comment \"Inicializacion NOC JunOS\""
                ),
                'breakdown': [
                    {'cmd': 'set system host-name Router-NOC-CE1', 'desc': 'Define hostname en la jerarquía JunOS.'},
                    {'cmd': 'commit check', 'desc': 'Verifica la validez sintáctica de la configuración.'}
                ]
            },
            'huawei': {
                'vendor_name': 'Huawei VRP (NetEngine / AR Router)',
                'code': (
                    "system-view\n"
                    "sysname Router-NOC-CE1\n"
                    "header shell information \"ACCESO RESTRINGIDO - NOC\"\n"
                    "aaa\n"
                    " local-user admin password irreversible-cipher SuperAdminNOC123!\n"
                    " local-user admin service-type terminal ssh http\n"
                    " local-user admin privilege level 15\n"
                    "quit\n"
                    "clock timezone COT minus 05:00:00\n"
                    "rsa local-key-pair create\n"
                    "stelnet server enable\n"
                    "user-interface vty 0 4\n"
                    " authentication-mode aaa\n"
                    " protocol inbound ssh\n"
                    " idle-timeout 5 0\n"
                    "quit\n"
                    "ntp-service unicast-peer 10.0.0.1\n"
                    "info-center loghost 10.0.0.50\n"
                    "snmp-agent community read NOC_READ\n"
                    "save"
                ),
                'breakdown': [
                    {'cmd': 'system-view', 'desc': 'Entra a System View en Huawei VRP.'},
                    {'cmd': 'stelnet server enable', 'desc': 'Habilita el servicio SSH seguro en VRP.'}
                ]
            },
            'fortinet': {
                'vendor_name': 'Fortinet FortiOS (FortiGate Firewall)',
                'code': (
                    "config system global\n"
                    "  set hostname \"FGT-NOC-GW1\"\n"
                    "  set timezone 12\n"
                    "  set admin-sport 8443\n"
                    "  set admintimeout 15\n"
                    "end\n"
                    "config system admin\n"
                    "  edit \"admin-noc\"\n"
                    "    set password \"SuperAdminForti2026!\"\n"
                    "    set accprofile \"super_admin\"\n"
                    "  next\n"
                    "end\n"
                    "config system ntp\n"
                    "  set status enable\n"
                    "  set ntpserver1 \"10.0.0.1\"\n"
                    "  set type custom\n"
                    "end"
                ),
                'breakdown': [
                    {'cmd': 'config system global', 'desc': 'Entra a la configuración global de FortiOS.'},
                    {'cmd': 'set admin-sport 8443', 'desc': 'Protege el acceso HTTPS administrativo.'}
                ]
            },
            'sophos': {
                'vendor_name': 'Sophos SFOS (XG / XGS Firewall)',
                'code': (
                    "system hostname set XGS-NOC-GW1\n"
                    "system time-zone set America/Bogota\n"
                    "system ntp server add 10.0.0.1\n"
                    "show network interfaces"
                ),
                'breakdown': [
                    {'cmd': 'system hostname set XGS-NOC-GW1', 'desc': 'Asigna hostname en Sophos SFOS CLI.'}
                ]
            },
            'mikrotik': {
                'vendor_name': 'MikroTik RouterOS (CCR / CRS / RB)',
                'code': (
                    "/system identity set name=Router-NOC-CE1\n"
                    "/user add name=admin-noc password=\"SuperAdminNOC123!\" group=full\n"
                    "/system clock set time-zone-name=America/Bogota\n"
                    "/ip service disable telnet,ftp,www\n"
                    "/ip service set ssh port=22 disabled=no\n"
                    "/system ntp client set enabled=yes servers=10.0.0.1\n"
                    "/snmp community add name=NOC_READ addresses=10.0.0.0/24\n"
                    "/snmp set enabled=yes"
                ),
                'breakdown': [
                    {'cmd': '/system identity set name=...', 'desc': 'Ajusta identidad MikroTik.'},
                    {'cmd': '/ip service disable telnet,ftp,www', 'desc': 'Cierra servicios vulnerables.'}
                ]
            },
            'datacom': {
                'vendor_name': 'Datacom DmOS (DM4000 / DM4300)',
                'code': (
                    "configure terminal\n"
                    "hostname Switch-NOC-CE1\n"
                    "username admin password secret SuperAdminNOC123!\n"
                    "clock timezone COT -5\n"
                    "ip ssh server enable\n"
                    "ip ssh version 2\n"
                    "ntp server 10.0.0.1\n"
                    "snmp-server community NOC_READ ro\n"
                    "end\n"
                    "copy running-config startup-config"
                ),
                'breakdown': [
                    {'cmd': 'hostname Switch-NOC-CE1', 'desc': 'Asigna hostname en DmOS.'}
                ]
            },
            'bdcom': {
                'vendor_name': 'BDCOM GPON OLT / Switch L2',
                'code': (
                    "config\n"
                    "hostname BDCOM-NOC-OLT1\n"
                    "username admin password 0 SuperAdminNOC123! privilege 15\n"
                    "ip ssh server enable\n"
                    "time-zone COT -5\n"
                    "ntp server 10.0.0.1\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'ip ssh server enable', 'desc': 'Activa SSH en BDCOM.'}
                ]
            },
            'allied_telesis': {
                'vendor_name': 'Allied Telesis AW+ (x530 / x950)',
                'code': (
                    "configure terminal\n"
                    "hostname Switch-AT-NOC1\n"
                    "username admin privilege 15 password SuperAdminNOC123!\n"
                    "clock timezone COT -5\n"
                    "service ssh\n"
                    "ntp server 10.0.0.1\n"
                    "end\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'service ssh', 'desc': 'Habilita el daemon SSH en AlliedWare Plus.'}
                ]
            },
            'raisecom': {
                'vendor_name': 'Raisecom ISCOM (2600G / Carrier Ethernet)',
                'code': (
                    "config\n"
                    "hostname Switch-Raisecom-NOC1\n"
                    "user admin password SuperAdminNOC123! level 15\n"
                    "ssh server enable\n"
                    "write"
                ),
                'breakdown': [
                    {'cmd': 'ssh server enable', 'desc': 'Habilita SSH en Raisecom ISCOM.'}
                ]
            },
            'teltonika': {
                'vendor_name': 'Teltonika RutOS (RUT / RUTX Industrial LTE/5G)',
                'code': (
                    "uci set system.@system[0].hostname='Router-NOC-CE1'\n"
                    "uci commit system\n"
                    "uci set dropbear.@dropbear[0].Port='22'\n"
                    "uci commit dropbear\n"
                    "uci set system.ntp.server='10.0.0.1'\n"
                    "uci commit system"
                ),
                'breakdown': [
                    {'cmd': 'uci set system.@system[0].hostname=...', 'desc': 'Configura hostname en el subsistema UCI.'}
                ]
            },
            'zte': {
                'vendor_name': 'ZTE GPON OLT (ZXAN C300 / C600)',
                'code': (
                    "configure terminal\n"
                    "hostname OLT-ZTE-NOC1\n"
                    "username admin password SuperAdminNOC123! privilege 15\n"
                    "ssh server enable\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'ssh server enable', 'desc': 'Activa el servidor SSH en la OLT ZTE.'}
                ]
            },
            'adtran': {
                'vendor_name': 'ADTRAN Total Access 5000 (AOS)',
                'code': (
                    "enable\n"
                    "configure terminal\n"
                    "hostname TA5000-NOC1\n"
                    "username admin password SuperAdminNOC123!\n"
                    "ip ssh server\n"
                    "write"
                ),
                'breakdown': [
                    {'cmd': 'ip ssh server', 'desc': 'Activa SSH en ADTRAN AOS.'}
                ]
            },
            'optone_vkom': {
                'vendor_name': 'Optone / VKOM Conversores de Medio & CPE',
                'code': (
                    "system-view\n"
                    "sysname OPT-VKOM-CPE1\n"
                    "interface ip 192.168.1.1 255.255.255.0\n"
                    "save"
                ),
                'breakdown': [
                    {'cmd': 'sysname OPT-VKOM-CPE1', 'desc': 'Asigna nombre en conversores/CPE Optone/VKOM.'}
                ]
            },
            'arista': {
                'vendor_name': 'Arista EOS (7000 Series Switches)',
                'code': (
                    "configure terminal\n"
                    "hostname Switch-Arista-NOC1\n"
                    "username admin secret SuperAdminNOC123!\n"
                    "clock timezone COT -5\n"
                    "management api http-commands\n"
                    "  no shutdown\n"
                    "end\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'management api http-commands', 'desc': 'Habilita la API eAPI de Arista EOS para automatización.'}
                ]
            },
            'linux': {
                'vendor_name': 'GNU/Linux Networking & FRRouting (vtysh)',
                'code': (
                    "hostname Router-Linux-NOC1\n"
                    "vtysh -c 'configure terminal' -c 'hostname Router-Linux-NOC1'\n"
                    "systemctl enable sshd --now\n"
                    "timedatectl set-timezone America/Bogota"
                ),
                'breakdown': [
                    {'cmd': 'vtysh -c ...', 'desc': 'Ejecuta comandos de enrutamiento mediante FRRouting vtysh en Linux.'}
                ]
            }
        }
    },
    'ccna_switching_master': {
        'title': '📘 CCNA / CCNP — Switch L2/L3 (VLANs, Trunking, STP/RSTP/MSTP, EtherChannel LACP)',
        'description': 'Configuración completa de switching de campus reservada exclusivamente para switches y routers con capacidades de conmutación L2/L3 reales.',
        'vendors': {
            'cisco_iosxe': {
                'vendor_name': 'Cisco IOS-XE / Catalyst 9000 / Catalyst 3850',
                'code': (
                    "configure terminal\n"
                    "vlan 10,20,30,99\n"
                    "spanning-tree mode rapid-pvst\n"
                    "spanning-tree vlan 10,20,30,99 root primary\n"
                    "interface range GigabitEthernet0/1 - 2\n"
                    " channel-group 1 mode active\n"
                    "exit\n"
                    "interface Port-channel1\n"
                    " switchport mode trunk\n"
                    " switchport trunk native vlan 99\n"
                    "exit\n"
                    "interface GigabitEthernet1/0/1\n"
                    " switchport mode access\n"
                    " switchport access vlan 10\n"
                    " switchport voice vlan 20\n"
                    " switchport port-security\n"
                    " switchport port-security maximum 2\n"
                    " switchport port-security violation shutdown\n"
                    "end\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'spanning-tree mode rapid-pvst', 'desc': 'Activa RPVST+ en switches Cisco.'},
                    {'cmd': 'channel-group 1 mode active', 'desc': 'Agrupación EtherChannel LACP.'}
                ]
            },
            'juniper': {
                'vendor_name': 'Juniper JunOS (EX / QFX Series Switches)',
                'code': (
                    "configure\n"
                    "set vlans DATOS vlan-id 10\n"
                    "set vlans VOZ vlan-id 20\n"
                    "set protocols rstp interface ge-0/0/0.0 edge\n"
                    "set interfaces ge-0/0/1 ether-options 802.3ad ae0\n"
                    "set interfaces ae0 unit 0 family ethernet-switching interface-mode trunk\n"
                    "commit"
                ),
                'breakdown': [
                    {'cmd': 'set interfaces ae0 unit 0...', 'desc': 'Modo trunk en agregación LACP ae0.'}
                ]
            },
            'huawei': {
                'vendor_name': 'Huawei VRP (CloudEngine / Switch L2/L3)',
                'code': (
                    "system-view\n"
                    "vlan batch 10 20 30 99\n"
                    "stp mode rstp\n"
                    "stp root primary\n"
                    "interface Eth-Trunk 1\n"
                    " mode lacp-static\n"
                    " port link-type trunk\n"
                    " port trunk allow-pass vlan 10 20 30 99\n"
                    "quit\n"
                    "interface GigabitEthernet0/0/1\n"
                    " eth-trunk 1\n"
                    "save"
                ),
                'breakdown': [
                    {'cmd': 'stp mode rstp', 'desc': 'Activa RSTP en Huawei VRP.'},
                    {'cmd': 'interface Eth-Trunk 1', 'desc': 'Crea el agregador LACP en Huawei.'}
                ]
            },
            'datacom': {
                'vendor_name': 'Datacom DmOS (DM4000 / DM4300 Switches)',
                'code': (
                    "configure terminal\n"
                    "vlan 10,20,30,99\n"
                    "interface lag 1\n"
                    " mode lacp\n"
                    " switchport mode trunk\n"
                    "end"
                ),
                'breakdown': [
                    {'cmd': 'interface lag 1', 'desc': 'Crea el grupo LAG LACP en DmOS.'}
                ]
            },
            'bdcom': {
                'vendor_name': 'BDCOM L2/L3 Switches (S2500 / S3900)',
                'code': (
                    "config\n"
                    "vlan 10,20,30,99\n"
                    "interface GigaEthernet0/1\n"
                    " switchport mode trunk\n"
                    " switchport trunk allowed vlan 10,20,30,99\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'switchport mode trunk', 'desc': 'Modo trunk 802.1Q en BDCOM.'}
                ]
            },
            'allied_telesis': {
                'vendor_name': 'Allied Telesis AW+ (x530 / x950 Switches)',
                'code': (
                    "configure terminal\n"
                    "vlan database\n"
                    " vlan 10,20,30,99\n"
                    "interface port-channel1\n"
                    " switchport mode trunk\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'vlan database', 'desc': 'Ingresa a la base de datos de VLANs en AW+.'}
                ]
            },
            'raisecom': {
                'vendor_name': 'Raisecom ISCOM (2600G Carrier Ethernet)',
                'code': (
                    "config\n"
                    "vlan 10,20,30,99\n"
                    "interface port 1\n"
                    " switchport mode trunk\n"
                    "write"
                ),
                'breakdown': [
                    {'cmd': 'switchport mode trunk', 'desc': 'Configura el puerto en modo trunk.'}
                ]
            },
            'arista': {
                'vendor_name': 'Arista EOS (7000 Series Switches)',
                'code': (
                    "configure terminal\n"
                    "vlan 10,20,30,99\n"
                    "spanning-tree mode mstp\n"
                    "interface Port-Channel1\n"
                    " switchport mode trunk\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'spanning-tree mode mstp', 'desc': 'MSTP en Arista EOS.'}
                ]
            }
        }
    },
    'noc_gpon_provisioning': {
        'title': '🌐 Plantilla NOC — Aprovisionamiento FTTH GPON OLT/ONT (Huawei / ZTE / BDCOM / ADTRAN)',
        'description': 'Plantilla reservada exclusivamente para OLTs GPON de acceso de fibra óptica.',
        'vendors': {
            'huawei': {
                'vendor_name': 'Huawei OLT (MA5800 / MA5608T)',
                'code': (
                    "system-view\n"
                    "interface gpon 0/1\n"
                    " ont add 1 1 sn-auth \"485754431A2B3C4D\" omci ont-lineprofile-id 10 ont-srvprofile-id 10 desc \"CLIENTE_FTTH_01\"\n"
                    "quit\n"
                    "service-port 100 gpon 0/1/1 ont 1 gemport 1 multi-service user-vlan 100 tag-transform translate inner-vlan 100 inbound traffic-table name 100M outbound traffic-table name 100M\n"
                    "save"
                ),
                'breakdown': [
                    {'cmd': 'ont add 1 1 sn-auth...', 'desc': 'Registra la ONT por número de serie en la OLT Huawei.'},
                    {'cmd': 'service-port 100...', 'desc': 'Crea el puerto de servicio para mapear el GEM Port a la VLAN de transporte.'}
                ]
            },
            'zte': {
                'vendor_name': 'ZTE OLT (ZXAN C300 / C320 / C600)',
                'code': (
                    "configure terminal\n"
                    "interface gpon-olt_1/2/1\n"
                    " onu 1 type ZTEG-F660 sn ZTEGC1A2B3D4\n"
                    "exit\n"
                    "interface gpon-onu_1/2/1:1\n"
                    " name CLIENTE_FTTH_01\n"
                    " tcont 1 name T-DATA dba-profile DBA-100M\n"
                    " gemport 1 name GEM-DATA tcont 1\n"
                    " service-port 1 vport 1 user-vlan 100 svlan 100\n"
                    "exit\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'onu 1 type ZTEG-F660...', 'desc': 'Registra la ONU en la OLT ZTE.'},
                    {'cmd': 'tcont 1 name T-DATA...', 'desc': 'Asigna el contenedor T-CONT DBA.'}
                ]
            },
            'bdcom': {
                'vendor_name': 'BDCOM GPON OLT P3600 Series',
                'code': (
                    "config\n"
                    "interface gpon 0/1\n"
                    " gpon onu add 1 1 sn ZTEGC1A2B3D4 line-profile FTTH-LINE srv-profile FTTH-SRV\n"
                    "exit\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'gpon onu add 1 1 sn...', 'desc': 'Registra la ONU en la OLT BDCOM.'}
                ]
            },
            'adtran': {
                'vendor_name': 'ADTRAN Total Access 5000 (TA5000 OLT)',
                'code': (
                    "enable\n"
                    "configure terminal\n"
                    "gpon-olt 1/1\n"
                    " onu 1 serial-number ADTN12345678\n"
                    "write"
                ),
                'breakdown': [
                    {'cmd': 'onu 1 serial-number...', 'desc': 'Registra la ONU en la OLT ADTRAN TA5000.'}
                ]
            }
        }
    },
    'firewall_fortinet_master': {
        'title': '🛡️ Plantilla Fortinet FortiOS — Aprovisionamiento Master Enterprise & Estado',
        'description': 'Reservada para cortafuegos de seguridad perimetral Fortinet FortiOS.',
        'vendors': {
            'fortinet': {
                'vendor_name': 'Fortinet FortiOS (FortiGate 40F - 3000F)',
                'code': (
                    "config system global\n"
                    "  set hostname \"FGT-CORP-ESTADO-GW01\"\n"
                    "  set timezone 12\n"
                    "  set admin-sport 8443\n"
                    "  set admintimeout 15\n"
                    "end\n"
                    "config system interface\n"
                    "  edit \"port1\"\n"
                    "    set alias \"WAN-INTERNET\"\n"
                    "    set mode static\n"
                    "    set ip 200.1.1.2 255.255.255.248\n"
                    "  next\n"
                    "end\n"
                    "config firewall policy\n"
                    "  edit 1\n"
                    "    set name \"POL_LAN_TO_WAN\"\n"
                    "    set srcintf \"port2\"\n"
                    "    set dstintf \"port1\"\n"
                    "    set srcaddr \"all\"\n"
                    "    set dstaddr \"all\"\n"
                    "    set action accept\n"
                    "    set nat enable\n"
                    "    set utm-status enable\n"
                    "  next\n"
                    "end"
                ),
                'breakdown': [
                    {'cmd': 'config firewall policy', 'desc': 'Reglas stateful con UTM y Source NAT.'}
                ]
            }
        }
    },
    'firewall_sophos_master': {
        'title': '🛡️ Plantilla Sophos SFOS — Aprovisionamiento Master Enterprise & Estado',
        'description': 'Reservada para cortafuegos de seguridad perimetral Sophos SFOS.',
        'vendors': {
            'sophos': {
                'vendor_name': 'Sophos SFOS (XG 85-330 / XGS 87-136)',
                'code': (
                    "system hostname set XGS-CORP-ESTADO-GW01\n"
                    "system time-zone set America/Bogota\n"
                    "system firewall-rule add name POL_LAN_TO_WAN srczone LAN dstzone WAN srcnet Any dstnet Any service Any action accept ips-policy default nat-rule MASQUERADE"
                ),
                'breakdown': [
                    {'cmd': 'system firewall-rule add...', 'desc': 'Regla de cortafuegos por zonas con IPS y SNAT Masquerade.'}
                ]
            }
        }
    }
}
