"""
data/config_templates.py — Plantillas de Configuración & Explicador Comando por Comando por Vendor.
Organizadas por el Plan de Estudios CCNA/CCNP, Fortinet NSE4-NSE8, Sophos Certified Architect y Diagnóstico Óptico/CPE.
"""

from typing import Dict, Any, List

CONFIG_TEMPLATES: Dict[str, Dict[str, Any]] = {
    'master_fw_nse4_nse8_enterprise': {
        'title': '🛡️ Fortinet (NSE4-NSE8) & Sophos SFOS Master Architecture — VDOMs, NGFW UTM, SD-WAN SLA, SSL Inspection, IPsec/SSL VPN & HA Cluster',
        'description': 'Guía integral avanzada nivel Fortinet NSE4-NSE8 y Sophos Certified Architect: VDOMs / Tenants virtuales, VDOM Links, SD-WAN con monitores de SLA (Latencia <30ms, Jitter <5ms, Packet Loss 0%), Inspección Cifrada SSL/TLS Deep Packet Inspection, IPS, Web Filter, Application Control, Políticas IPv4/IPv6 Dual-Stack, VPN IPsec IKEv2 con BGP, SSL VPN con MFA (2FA) y Alta Disponibilidad HA Active-Active / Active-Passive.',
        'vendors': {
            'fortinet': {
                'vendor_name': 'Fortinet FortiOS (FortiGate 40F - 3000F / NSE4 - NSE8 Level)',
                'code': (
                    "# 1. VDOMs & DOMINIOS VIRTUALES DE SEGURIDAD (TENANTS MULTI-CLIENTE)\n"
                    "config system global\n"
                    "  set vdom-mode multi-vdom\n"
                    "end\n"
                    "config vdom\n"
                    "  edit \"VDOM_CLIENTE_ESTADO\"\n"
                    "  next\n"
                    "end\n"
                    "config global\n"
                    "  config system vdom-link\n"
                    "    edit \"vlink_corp\"\n"
                    "    next\n"
                    "  end\n"
                    "end\n"
                    "\n"
                    "# 2. CONFIGURACIÓN DE SD-WAN & PROBES DE PERFORMANCE SLA\n"
                    "config vdom\n"
                    "  edit \"VDOM_CLIENTE_ESTADO\"\n"
                    "    config system sdwan\n"
                    "      set status enable\n"
                    "      config zone\n"
                    "        edit \"ZONE_WAN_INTERNET\"\n"
                    "        next\n"
                    "      end\n"
                    "      config members\n"
                    "        edit 1\n"
                    "          set interface \"port1\"\n"
                    "          set zone \"ZONE_WAN_INTERNET\"\n"
                    "          set gateway 200.1.1.1\n"
                    "        next\n"
                    "        edit 2\n"
                    "          set interface \"port2\"\n"
                    "          set zone \"ZONE_WAN_INTERNET\"\n"
                    "          set gateway 201.2.2.1\n"
                    "        next\n"
                    "      end\n"
                    "      config health-check\n"
                    "        edit \"SLA_PROBE_GOOGLE_DNS\"\n"
                    "          set server \"8.8.8.8\"\n"
                    "          set members 1 2\n"
                    "          config sla\n"
                    "            edit 1\n"
                    "              set latency-threshold 50\n"
                    "              set jitter-threshold 10\n"
                    "              set packetloss-threshold 1\n"
                    "            next\n"
                    "          end\n"
                    "        next\n"
                    "      end\n"
                    "      config service\n"
                    "        edit 1\n"
                    "          set name \"RULE_SDWAN_CRITICAL_TRAFFIC\"\n"
                    "          set mode priority\n"
                    "          set dst \"all\"\n"
                    "          set src \"all\"\n"
                    "          config sla\n"
                    "            edit \"SLA_PROBE_GOOGLE_DNS\"\n"
                    "              set id 1\n"
                    "            next\n"
                    "          end\n"
                    "          set priority-members 1 2\n"
                    "        next\n"
                    "      end\n"
                    "    end\n"
                    "\n"
                    "# 3. DEEP PACKET SSL/TLS INSPECTION & CERTIFICADOS CORPORATIVOS\n"
                    "config firewall ssl-ssh-profile\n"
                    "  edit \"DEEP_SSL_INSPECTION_PROFILE\"\n"
                    "    config https\n"
                    "      set ports 443\n"
                    "      set status deep-inspection\n"
                    "    end\n"
                    "    set caname \"Fortinet_CA_SSL\"\n"
                    "  next\n"
                    "end\n"
                    "\n"
                    "# 4. PERFILES UTM NGFW (IPS, AV, WEBFILTER, APPLICATION CONTROL)\n"
                    "config ips sensor\n"
                    "  edit \"IPS_HIGH_SECURITY\"\n"
                    "    config entries\n"
                    "      edit 1\n"
                    "        set severity high critical\n"
                    "        set action block\n"
                    "      next\n"
                    "    end\n"
                    "  next\n"
                    "end\n"
                    "config webfilter profile\n"
                    "  edit \"WEBFILTER_CORP\"\n"
                    "    config ftgd-wf\n"
                    "      config filters\n"
                    "        edit 1\n"
                    "          set category 26 61\n"
                    "          set action block\n"
                    "        next\n"
                    "      end\n"
                    "    end\n"
                    "  next\n"
                    "end\n"
                    "\n"
                    "# 5. POLÍTICAS DE SEGURIDAD STATEFUL DUAL-STACK (IPV4 & IPV6)\n"
                    "config firewall policy\n"
                    "  edit 10\n"
                    "    set name \"POL_NGFW_LAN_TO_SDWAN\"\n"
                    "    set srcintf \"port3\"\n"
                    "    set dstintf \"ZONE_WAN_INTERNET\"\n"
                    "    set srcaddr \"all\"\n"
                    "    set dstaddr \"all\"\n"
                    "    set action accept\n"
                    "    set schedule \"always\"\n"
                    "    set service \"ALL\"\n"
                    "    set nat enable\n"
                    "    set utm-status enable\n"
                    "    set ips-sensor \"IPS_HIGH_SECURITY\"\n"
                    "    set webfilter-profile \"WEBFILTER_CORP\"\n"
                    "    set ssl-ssh-profile \"DEEP_SSL_INSPECTION_PROFILE\"\n"
                    "    set logtraffic all\n"
                    "  next\n"
                    "end\n"
                    "\n"
                    "# 6. VPN SSL CON AUTENTICACIÓN MULTI-FACTOR (MFA 2FA)\n"
                    "config vpn ssl settings\n"
                    "  set servercert \"Fortinet_Factory\"\n"
                    "  set tunnel-ip-pools \"SSLVPN_TUNNEL_POOL\"\n"
                    "  set port 10443\n"
                    "  config authentication-rule\n"
                    "    edit 1\n"
                    "      set users \"User_MFA_Group\"\n"
                    "      set portal \"full-access\"\n"
                    "    next\n"
                    "  end\n"
                    "end\n"
                    "end"
                ),
                'breakdown': [
                    {'cmd': 'config system global / set vdom-mode multi-vdom', 'desc': 'Activa el modo Multi-VDOM en el chasis FortiGate para separar clientes en tenants virtualizados aislados.'},
                    {'cmd': 'config system sdwan / config health-check', 'desc': 'Configura SD-WAN con sondas de salud (Health Check Probes) para medir latencia, jitter y pérdida de paquetes en tiempo real.'},
                    {'cmd': 'set mode priority / set priority-members 1 2', 'desc': 'Aplica conmutación dinámica de enlaces WAN (Failover dinámico) basado en el cumplimiento estricto del SLA.'},
                    {'cmd': 'set status deep-inspection', 'desc': 'Activa la inspección profunda SSL/TLS Deep Packet Inspection desarticulando tráfico cifrado para análisis antivirus e IPS.'},
                    {'cmd': 'config ips sensor / set action block', 'desc': 'Configura el sensor IPS para bloquear ataques de severidad High y Critical.'},
                    {'cmd': 'config vpn ssl settings / set port 10443', 'desc': 'Configura el portal VPN SSL para acceso remoto con túnel seguro en puerto 10443.'}
                ]
            },
            'sophos': {
                'vendor_name': 'Sophos SFOS (XG / XGS Series / Sophos Certified Architect)',
                'code': (
                    "# 1. SYSTEM SD-WAN & LINK SLA MANAGEMENT\n"
                    "system sd-wan profile add name SDWAN_CRITICAL_SLA latency-threshold 40 jitter-threshold 8 packet-loss-threshold 1\n"
                    "system sd-wan policy add name RULE_SDWAN_VOIP_DATA src-interface Port2 dst-interface Port1 profile SDWAN_CRITICAL_SLA\n"
                    "\n"
                    "# 2. FIREWALL SECURITY RULES WITH DEEP THREAT PREVENTION & IPS\n"
                    "system firewall-rule add name POL_CORP_INTERNET srczone LAN dstzone WAN srcnet Any dstnet Any service Any action accept ips-policy protect_client web-policy default app-policy default nat-rule MASQUERADE\n"
                    "\n"
                    "# 3. SSL VPN REMOTE ACCESS WITH SOPHOS CONNECT & MFA\n"
                    "system ssl-vpn add profile Sophos_Connect_Access network 192.168.10.0/24 pool 10.81.234.0/24 authentication-mode local-2fa\n"
                    "\n"
                    "# 4. HIGH AVAILABILITY CLUSTER ACTIVE-PASSIVE\n"
                    "system ha enable mode active-passive peer-ip 192.168.10.2 hb-interface Port4 cluster-id 100"
                ),
                'breakdown': [
                    {'cmd': 'system sd-wan profile add...', 'desc': 'Define perfiles SD-WAN SLA de calidad de enlace en Sophos SFOS.'},
                    {'cmd': 'system firewall-rule add...', 'desc': 'Crea regla de seguridad basada en zonas con inspección IPS y Web Protection.'},
                    {'cmd': 'system ssl-vpn add profile...', 'desc': 'Configura el acceso remoto SSL VPN con clientes Sophos Connect y doble factor 2FA.'}
                ]
            }
        }
    },
    'master_equipment_management_ccnp': {
        'title': '📘 CCNA/CCNP — Gestión, Administración, Hardening & Mantenimiento de Equipos (Out-of-Band, AAA, SNMPv3, Syslog, Firmware Update & Password Recovery)',
        'description': 'Procedimientos y comandos exactos para la administración, mantenimiento operativo, respaldo de configuración, actualización de SO/Firmware sin caídas, sincronización de registros y recuperación de contraseñas para todos los equipos de la red.',
        'vendors': {
            'cisco_iosxe': {
                'vendor_name': 'Cisco IOS-XE / ISR / ASR / Catalyst',
                'code': (
                    "# 1. GESTIÓN OUT-OF-BAND (MGMT) & AUTENTICACIÓN AAA TACACS+/RADIUS\n"
                    "interface GigabitEthernet0\n"
                    " description ** INTERFAZ DE GESTION OUT-OF-BAND (OOB MGMT) **\n"
                    " vrf forwarding Mgmt-intf\n"
                    " ip address 10.255.0.100 255.255.255.0\n"
                    " no shutdown\n"
                    "exit\n"
                    "aaa new-model\n"
                    "tacacs server TACACS_NOC_1\n"
                    " address ipv4 10.0.0.10\n"
                    " key SuperSecretTacacsKey123!\n"
                    "aaa authentication login default group tacacs+ local\n"
                    "aaa authorization exec default group tacacs+ local\n"
                    "aaa accounting exec default start-stop group tacacs+\n"
                    "\n"
                    "# 2. SNMPv3 CIFRADO (USM AUTH-PRIV AES/SHA)\n"
                    "snmp-server group GROUP_NOC_V3 v3 priv\n"
                    "snmp-server user admin-noc GROUP_NOC_V3 v3 auth sha AuthPass123! priv aes 128 PrivPass123!\n"
                    "snmp-server host 10.0.0.50 version 3 priv admin-noc\n"
                    "\n"
                    "# 3. SYSLOG REMOTO DE SEVERIDAD NOTICE/INFORMATIONAL\n"
                    "logging trap informational\n"
                    "logging source-interface GigabitEthernet0\n"
                    "logging host 10.0.0.50\n"
                    "\n"
                    "# 4. RESPALDO Y ACTUALIZACIÓN DE FIRMWARE DE SISTEMA OPERATIVO\n"
                    "# Respaldo de configuración activa por TFTP/SCP:\n"
                    "# copy running-config tftp://10.0.0.50/Cisco_PE1_backup.cfg\n"
                    "# Actualización de firmware IOS-XE:\n"
                    "# copy tftp://10.0.0.50/isr4300-universalk9.17.09.04a.SPA.bin flash:\n"
                    "# boot system flash:isr4300-universalk9.17.09.04a.SPA.bin\n"
                    "# write memory & reload"
                ),
                'breakdown': [
                    {'cmd': 'vrf forwarding Mgmt-intf', 'desc': 'Aísla la interfaz de gestión Out-of-Band en una VRF dedicada para evitar ataques desde la red de producción.'},
                    {'cmd': 'aaa new-model / tacacs server...', 'desc': 'Habilita la arquitectura AAA con servidor centralizado TACACS+ para control de comandos auditables.'},
                    {'cmd': 'snmp-server user ... v3 auth sha ... priv aes 128', 'desc': 'Configura SNMPv3 con nivel de seguridad authPriv (Autenticación SHA y Cifrado AES-128).'},
                    {'cmd': 'logging trap informational / logging host...', 'desc': 'Enruta los logs de auditoría hacia el servidor SIEM central.'}
                ]
            },
            'juniper': {
                'vendor_name': 'Juniper JunOS (MX / ACX / SRX)',
                'code': (
                    "configure\n"
                    "set interfaces fxp0 unit 0 family inet address 10.255.0.100/24\n"
                    "set system login radius-server 10.0.0.10 secret \"SuperSecretRadiusKey123!\"\n"
                    "set snmp v3 usm local-engine user admin-noc authentication-sha authentication-password \"AuthPass123!\"\n"
                    "set snmp v3 usm local-engine user admin-noc privacy-aes privacy-password \"PrivPass123!\"\n"
                    "commit check\n"
                    "commit\n"
                    "# Copiar respaldo en JunOS: request system snapshot / file copy /config/juniper.conf.gz tftp://10.0.0.50/\n"
                    "# Actualizar SO JunOS: request system software add /var/tmp/junos-install-mx-x86-64-21.4R3.tgz reboot"
                ),
                'breakdown': [
                    {'cmd': 'set interfaces fxp0...', 'desc': 'Asigna direccionamiento a la interfaz física de gestión Out-of-Band (fxp0/me0) en JunOS.'},
                    {'cmd': 'request system software add ... reboot', 'desc': 'Instala la imagen oficial de JunOS y realiza el reinicio atómico.'}
                ]
            }
        }
    },
    'master_gpon_cpe_optical_tshoot': {
        'title': '🌐 FTTH, GPON OLT/ONT, CPEs & Conversores SFP — Diagnóstico Físico & Aprovisionamiento (Huawei, ZTE, BDCOM, ADTRAN, Allied Telesis iMG/RG, Optone, VKOM)',
        'description': 'Procedimiento paso a paso para soporte y troubleshooting de Capa 1 y Capa 2 en enlaces de fibra óptica: Verificación de niveles de potencia óptica Rx/Tx dBm (-8 a -27 dBm), reflectometría OTDR, aprovisionamiento OMCI OLT-ONT y mapeo de VLANs dot1q/QinQ en CPEs y conversores SFP.',
        'vendors': {
            'huawei': {
                'vendor_name': 'Huawei OLT GPON (MA5800 / MA5608T)',
                'code': (
                    "# 1. DIAGNÓSTICO ÓPTICO Y POTENCIA DDM EN PUERTO GPON PON\n"
                    "display interface gpon 0/1/1\n"
                    "display ont optical-info 0/1 1 1\n"
                    "# Umbrales Ópticos Normales GPON Class B+ / C+:\n"
                    "# Rx Power en ONT: -8.00 dBm a -27.00 dBm (Alarma por debajo de -28.00 dBm LOS)\n"
                    "# Tx Power en ONT: +0.50 dBm a +5.00 dBm\n"
                    "\n"
                    "# 2. VERIFICACIÓN DE ESTADO OMCI ONT Y REGISTRO\n"
                    "display ont info 0 1 1 1\n"
                    "display ont autofind 0/1\n"
                    "\n"
                    "# 3. APROVISIONAMIENTO COMPLETO ONT (INTERNET + IPTV + VOIP)\n"
                    "system-view\n"
                    "interface gpon 0/1\n"
                    " ont add 1 1 sn-auth \"485754431A2B3C4D\" omci ont-lineprofile-id 10 ont-srvprofile-id 10 desc \"CLIENTE_VIP_FTTH_01\"\n"
                    "quit\n"
                    "service-port 100 gpon 0/1/1 ont 1 gemport 1 multi-service user-vlan 10 tag-transform translate inner-vlan 100 inbound traffic-table name 100M outbound traffic-table name 100M\n"
                    "service-port 200 gpon 0/1/1 ont 1 gemport 2 multi-service user-vlan 20 tag-transform translate inner-vlan 200 inbound traffic-table name IPTV outbound traffic-table name IPTV\n"
                    "save"
                ),
                'breakdown': [
                    {'cmd': 'display ont optical-info 0/1 1 1', 'desc': 'Consulta la potencia óptica en tiempo real recibida por la ONT desde el hilo de fibra óptica (Rx dBm).'},
                    {'cmd': 'display ont autofind 0/1', 'desc': 'Escanea el puerto PON para detectar ONTs conectadas no registradas (Autofind).'},
                    {'cmd': 'service-port 100 gpon ...', 'desc': 'Crea el Service Port mapeando la VLAN de usuario con perfil de velocidad de 100 Mbps.'}
                ]
            },
            'zte': {
                'vendor_name': 'ZTE GPON OLT (ZXAN C300 / C320 / C600)',
                'code': (
                    "show gpon onu state gpon-olt_1/2/1\n"
                    "show pon power onu-rx gpon-onu_1/2/1:1\n"
                    "configure terminal\n"
                    "interface gpon-olt_1/2/1\n"
                    " onu 1 type ZTEG-F660 sn ZTEGC1A2B3D4\n"
                    "exit\n"
                    "interface gpon-onu_1/2/1:1\n"
                    " name CLIENTE_VIP_FTTH_01\n"
                    " tcont 1 name T-DATA dba-profile DBA-100M\n"
                    " gemport 1 name GEM-DATA tcont 1\n"
                    " service-port 1 vport 1 user-vlan 10 svlan 100\n"
                    "write memory"
                ),
                'breakdown': [
                    {'cmd': 'show pon power onu-rx...', 'desc': 'Muestra el nivel de atenuación de potencia óptica Rx en la ONU ZTE.'},
                    {'cmd': 'interface gpon-onu_1/2/1:1', 'desc': 'Aprovisiona la ONU con contenedor T-CONT y Service Port.'}
                ]
            },
            'allied_telesis': {
                'vendor_name': 'Allied Telesis iMG / RG CPE (iMG606 / iMG1400 / iMG1500 / RG 606)',
                'code': (
                    "enable\n"
                    "show interface wan0 DDM\n"
                    "show vlan\n"
                    "configure terminal\n"
                    "interface wan0.100\n"
                    " encapsulation dot1q 100\n"
                    " ip address dhcp\n"
                    "exit"
                ),
                'breakdown': [
                    {'cmd': 'show interface wan0 DDM', 'desc': 'Muestra el diagnóstico DDM óptico del transceptor en el CPE Allied Telesis iMG.'}
                ]
            },
            'optone_vkom': {
                'vendor_name': 'Optone & VKOM Conversores de Medio (OPT-1202S25 / VKS-100-25 / VKDG2)',
                'code': (
                    "system-view\n"
                    "display interface status\n"
                    "display optical-module information\n"
                    "# Diagnóstico por leds frontales:\n"
                    "# FX LINK/ACT: Encendido verde (Enlace óptico establecido)\n"
                    "# TX LINK/ACT: Encendido verde (Enlace de cobre UTP establecido)\n"
                    "# PWR: Encendido verde (Alimentación eléctrica OK)"
                ),
                'breakdown': [
                    {'cmd': 'display optical-module information', 'desc': 'Muestra los parámetros del módulo SFP óptico en conversores administrables.'}
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
