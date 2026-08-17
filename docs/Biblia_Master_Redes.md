# 📘 Biblia Master de Configuración & Troubleshooting de Redes Multi-Vendor
## Guía Integral Especializada CCNA, CCNP, Fortinet NSE4-NSE8, Sophos Certified Architect & Service Provider

> **Repositorio Oficial:** [https://github.com/junipermerchan/net_tshoot_dashboard.git](https://github.com/junipermerchan/net_tshoot_dashboard.git)

---

## 📌 Tabla de Contenidos
1. [Matriz de Fabricantes y Modelos de Hardware Soportaods](#1-matriz-de-fabricantes-y-modelos-de-hardware-soportados)
2. [Conceptos y Arquitectura de Sistemas Operativos por Fabricante](#2-conceptos-y-arquitectura-de-sistemas-operativos-por-fabricante)
3. [Módulos de Configuración Máster CCNA/CCNP & Enterprise (31 Módulos)](#3-módulos-de-configuración-máster-ccnaccnp--enterprise)
4. [Procedimientos de Búsqueda Operacional de Red (MAC, ARP, BGP, OSPF, STP, DHCP, SD-WAN)](#4-procedimientos-de-búsqueda-operacional-de-red)
5. [Flujos Diagnósticos de Troubleshooting por Niveles Tier 1 a Tier 4](#5-flujos-diagnósticos-de-troubleshooting-por-niveles)

---

## 1. Matriz de Fabricantes y Modelos de Hardware Soportados

| Código Vendor | Nombre del Fabricante | Modelos Exactos de Hardware Indexados |
|---|---|---|
| `juniper` | **Juniper JunOS (MX / ACX / PTX / SRX)** | ROUTER JUNIPER ACX 2200 AC, GATEWAY JUNIPER SRX300, GATEWAY JUNIPER SRX 340, GATEWAY JUNIPER SRX1500 |
| `cisco_iosxr` | **Cisco IOS-XR (ASR 9000 / NCS / CRS)** | Genérico |
| `cisco_iosxe` | **Cisco IOS-XE / ISR / ASR 1000 / Catalyst 9000** | ROUTER CISCO 881, ROUTER CISCO 1841, ROUTER CISCO 1941, ROUTER CISCO 2801, ROUTER CISCO 2811, ROUTER CISCO 2821, ROUTER CISCO 2851, ROUTER CISCO 2921, ROUTER CISCO 2951, ROUTER CISCO 3825, ROUTER CISCO 3845, ROUTER CISCO 3925, ROUTER CISCO 3945, TARJETA HWIC |
| `cisco_asr903` | **Cisco ASR 900 / 903 / 920 Series** | ROUTER CISCO ASR 920, ROUTER CISCO ASR 901 |
| `arista` | **Arista EOS (7000 Series / CloudVision)** | Genérico |
| `huawei` | **Huawei VRP (NetEngine / AR / OLT MA5800)** | HUAWEI-AR611W, HUAWEI-AR650 |
| `mikrotik` | **MikroTik RouterOS v7 (CCR / CRS / RB)** | Genérico |
| `fortinet` | **Fortinet FortiOS (FortiGate 40F-3000F)** | FORTINET-40F, FORTINET-60F, FORTINET-80F, FORTINET-100F, FORTINET-200F |
| `zone` | **Vendor Carrier Genérico (ZTE/Huawei)** | Genérico |
| `zte` | **ZTE GPON OLT (ZXAN C300 / C600)** | Genérico |
| `zhone` | **Dasan Zhone GPON OLT (MXK / MXK-F)** | Genérico |
| `adtran` | **ADTRAN TA5000 OLT / NetVanta (AOS)** | Genérico |
| `ta5k` | **ADTRAN Total Access 5000 (AOS FTTH)** | Genérico |
| `linux` | **GNU/Linux Networking & FRRouting (iproute2/vtysh)** | Genérico |
| `datacom` | **Datacom DmOS (DM4073 / DM4170 / DM4370)** | DATACOM 4073, DATACOM-DM4170, DATACOM-DM4370, DATACOM-DM4380 |
| `bdcom` | **BDCOM GPON OLT P3600 / ONU 1705 / Switch L2** | BDCOM 1705 |
| `optone_vkom` | **Optone OPT-1202 & VKOM Conversores / CPE** | CONVERSOR SFP, CONVERSOR TRS OPT-1202S25, CONVERSOR TRANSCEIVER VKS-100-25 VKOM, CONVERSOR TRANSCEIVER VKDG2, CONVERSOR TRANSCEIVER 1 GIGA VKSF1100-20A, FIBRA OPTICA |
| `allied_telesis` | **Allied Telesis AW+ & iMG CPE (x530/iMG606)** | SWITCH AT 510, ALLIED TELESYS-Atx-510, ALLIED TELESYS-iMG606, ALLIED TELESYS-iMG1400, ALLIED TELESYS-iMG1500, IMG 1405, IMG 1425, IMG 1505, RG 606, RG 616W |
| `raisecom` | **Raisecom ISCOM (2600G / 2608G / Carrier Eth)** | SWITCH ADMINISTRABLE RAISECOM ISCOM 2608G, RAISECOM-2608G, RAISECOM-2600G |
| `sophos` | **Sophos SFOS (XG / XGS Firewall & Central)** | PLATAFORMA SOPHOS CENTRAL, SOPHOS XG 85, SOPHOS XG 86, SOPHOS XG 115, SOPHOS XG 125, SOPHOS XG 135, SOPHOS XG 210, SOPHOS XG 310, SOPHOS XG 330, SOPHOS-XGS87, SOPHOS-XGS107, SOPHOS-XGS116, SOPHOS-XGS126, SOPHOS-XGS136 |
| `teltonika` | **Teltonika RutOS (RUT / RUTX Industrial LTE)** | TELTONIKA-RUT300, TELTONIKA-RUX08, TELTONIKA-RUTX10, TELTONIKA-RUTX11, TELTONIKA-RUTXR1 |

---

## 2. Conceptos y Arquitectura de Sistemas Operativos por Fabricante

### 🏷️ Fabricante: Cisco IOS-XE / ISR / ASR 1000 / Catalyst 9000 (`cisco_iosxe`)
- 📐 **Cisco IOS-XE Architecture**: Arquitectura de SO modular basada en kernel Linux con plano de control desacoplado (IOSd) y plano de datos de alta velocidad impulsado por Cisco QuantumFlow Processor (QFP) / ASICs UADP.
- 💡 **Filosofía CLI Cisco**: Sintaxis imperativa con jerarquía `configure terminal`, comandos `show` acumulativos y diferenciación entre interfaz física y subinterfaz dot1q (`Gi0/0/1.100`).
- **Comandos Clave**: • `show ip interface brief` | `show running-config` | `show ip route` | `write memory`

### 🏷️ Fabricante: Cisco IOS-XR (ASR 9000 / NCS / CRS) (`cisco_iosxr`)
- 📐 **Cisco IOS-XR Architecture**: Sistema operativo microkernel distribuido y multi-hilo (QNX / Linux) diseñado para routers Service Provider de alta disponibilidad (ASR 9000 / NCS).
- 💡 **Filosofía CLI IOS-XR**: Basada en plano de candidatos con comando obligatorio `commit` para aplicar cambios de forma atómica. No existe `write memory`.
- **Comandos Clave**: • `show ipv4 interface brief` | `commit` | `show configuration commit list` | `rollback configuration`

### 🏷️ Fabricante: Juniper JunOS (MX / ACX / PTX / SRX) (`juniper`)
- 📐 **Juniper JunOS Architecture**: Separación estricta entre Plano de Control (Routing Engine - RE) y Plano de Datos (Packet Forwarding Engine - PFE). El RE procesa enrutamiento y el PFE conmuta paquetes en ASICs.
- 💡 **Filosofía JunOS**: Estructura jerárquica basada en bloques (`set` / `edit`). Comprobación de sintaxis con `commit check` y deshacer con `rollback 0`.
- **Comandos Clave**: • `show interfaces terse` | `commit check` | `commit comment "..."` | `rollback 0` | `show route`

### 🏷️ Fabricante: Huawei VRP (NetEngine / AR / OLT MA5800) (`huawei`)
- 📐 **Huawei VRP Architecture**: Versatile Routing Platform (VRP) para routers NetEngine / AR / OLTs. Diseñada para alto rendimiento con plano de control redundante MPU y LPU.
- 💡 **Filosofía Huawei VRP**: Modo de vista global `system-view`. Guardado explícito con `save`. Soporta comandos abbreviados nativos.
- **Comandos Clave**: • `display ip interface brief` | `system-view` | `display current-configuration` | `save`

### 🏷️ Fabricante: Fortinet FortiOS (FortiGate 40F-3000F) (`fortinet`)
- 📐 **Fortinet FortiOS Architecture**: Sistema operativo de seguridad acelerado por procesadores de hardware dedicados: NP (Network Processor para aceleración L3/L4) y CP (Content Processor para inspección UTM/IPS/SSL).
- 💡 **Filosofía FortiOS CLI**: Basado en bloques `config <nodo>` / `edit <item>` / `set <parametro>` / `next` / `end`. Aislamiento en Virtual Domains (VDOMs).
- **Comandos Clave**: • `get system status` | `diagnose sys sdwan service` | `config firewall policy` | `diagnose netlink neighbor list`

### 🏷️ Fabricante: Sophos SFOS (XG / XGS Firewall & Central) (`sophos`)
- 📐 **Sophos SFOS Architecture**: Arquitectura Xstream con plano de control unificado y Xstream Flow Processor (aceleración por hardware de inspección profunda SSL/TLS y filtrado de paquetes).
- 💡 **Filosofía Sophos SFOS CLI**: Comandos estructurados `system <submodulo> <accion>`. Consola de diagnósticos y menú de opciones de consola física.
- **Comandos Clave**: • `system diagnostics utilities ping` | `system firewall-rule show` | `system route show`

### 🏷️ Fabricante: MikroTik RouterOS v7 (CCR / CRS / RB) (`mikrotik`)
- 📐 **MikroTik RouterOS v7 Architecture**: Sistema operativo modular basado en Linux Kernel con subsistema de enrutamiento dinámico unificado sobre FRRouting.
- 💡 **Filosofía RouterOS CLI**: Sintaxis jerárquica comenzando por la raíz del menú (`/ip route`, `/interface bridge`, `/routing ospf`). Modificaciones en tiempo real.
- **Comandos Clave**: • `/ip address print` | `/ip route print` | `/interface print` | `/system resource print`

### 🏷️ Fabricante: Datacom DmOS (DM4073 / DM4170 / DM4370) (`datacom`)
- 📐 **Datacom DmOS Architecture**: Sistema operativo de grado Carrier Ethernet para switches de agregación y routers de transporte DM4000/DM4300.
- 💡 **Filosofía DmOS**: Sintaxis estándar estilo industria con modo `configure terminal` y copiado a memoria activa.
- **Comandos Clave**: • `show interface brief` | `configure terminal` | `copy running-config startup-config`

### 🏷️ Fabricante: BDCOM GPON OLT P3600 / ONU 1705 / Switch L2 (`bdcom`)
- 📐 **BDCOM GPON OLT Architecture**: Plataforma de acceso GPON de alta densidad para aprovisionar servicios triple-play sobre red óptica pasiva.
- 💡 **Filosofía BDCOM CLI**: Modo `config` con soporte de comandos OMCI de GPON (`gpon onu add`, `line-profile`, `srv-profile`).
- **Comandos Clave**: • `show gpon onu state` | `gpon onu add` | `write memory`

### 🏷️ Fabricante: Allied Telesis AW+ & iMG CPE (x530/iMG606) (`allied_telesis`)
- 📐 **Allied Telesis AW+ Architecture**: AlliedWare Plus (AW+) operating system impulsado por Linux y diseñado para resiliencia en switches corporativos y CPEs iMG/RG.
- 💡 **Filosofía AW+**: Sintaxis industrial con `configure terminal`, `vlan database` y `show interface DDM`.
- **Comandos Clave**: • `show interface brief` | `show interface wan0 DDM` | `write memory`

### 🏷️ Fabricante: Raisecom ISCOM (2600G / 2608G / Carrier Eth) (`raisecom`)
- 📐 **Raisecom ISCOM Architecture**: Equipos de acceso Carrier Ethernet 802.1ad (QinQ) para anillos de transporte de fibra óptica.
- 💡 **Filosofía Raisecom**: Modo `config` con guardado `write`. Sintaxis orientada a puertos lógicos e interfaces EVC.
- **Comandos Clave**: • `show interface` | `show stp` | `write`

### 🏷️ Fabricante: Teltonika RutOS (RUT / RUTX Industrial LTE) (`teltonika`)
- 📐 **Teltonika RutOS Architecture**: Sistema operativo basado en OpenWrt Linux diseñado para routers celulares e industriales 4G/5G con gestión remota RMS.
- 💡 **Filosofía RutOS CLI**: Interfaz UCI (`uci set`, `uci commit`) y comandos de módem celular `gsmctl`. Enrutamiento avanzado gestionado con `vtysh`.
- **Comandos Clave**: • `gsmctl -q` | `uci show system` | `uci commit` | `vtysh`

### 🏷️ Fabricante: Optone OPT-1202 & VKOM Conversores / CPE (`optone_vkom`)
- 📐 **Optone & VKOM Media Converters**: Conversores de medios electro-ópticos y CPEs de fibra. Operan convirtiendo señales de cobre UTP a pulso óptico monomodo/multimodo.
- 💡 **Filosofía Optone/VKOM**: Diagnóstico híbrido por comandos de software (`display optical-module`) e indicadores LED físicos (FX LINK/ACT, TX LINK/ACT, PWR).
- **Comandos Clave**: • `display interface status` | `display optical-module information`

### 🏷️ Fabricante: Arista EOS (7000 Series / CloudVision) (`arista`)
- 📐 **Arista EOS Architecture**: Extensible Operating System (EOS) basado en un kernel Linux sin modificaciones, con arquitectura de estado compartido alimentada por SysDB.
- 💡 **Filosofía Arista EOS**: Sintaxis limpia compatible con Cisco CLI, integración eAPI JSON-RPC y comandos nativos Bash.
- **Comandos Clave**: • `show ip interface brief` | `show bgp summary` | `management api http-commands`

### 🏷️ Fabricante: GNU/Linux Networking & FRRouting (iproute2/vtysh) (`linux`)
- 📐 **GNU/Linux Networking & FRR Architecture**: Subsistema de red del Kernel Linux (netfilter, iproute2, nftables) complementado por el suite de enrutamiento dinámico FRRouting (FRR).
- 💡 **Filosofía Linux CLI**: Comandos `ip route`, `ip addr`, `ip neighbor` y shell interactivo unificado `vtysh` para OSPF/BGP/IS-IS.
- **Comandos Clave**: • `ip addr show` | `ip route show` | `vtysh -c "show ip bgp summary"` | `tcpdump -nn -i eth0`

---

## 3. Módulos de Configuración Máster CCNA/CCNP & Enterprise

### 🛡️ Fortinet (NSE4-NSE8) & Sophos SFOS Master Architecture — VDOMs, NGFW UTM, SD-WAN SLA, SSL Inspection, IPsec/SSL VPN & HA Cluster
*Guía integral avanzada nivel Fortinet NSE4-NSE8 y Sophos Certified Architect: VDOMs / Tenants virtuales, VDOM Links, SD-WAN con monitores de SLA (Latencia <30ms, Jitter <5ms, Packet Loss 0%), Inspección Cifrada SSL/TLS Deep Packet Inspection, IPS, Web Filter, Application Control, Políticas IPv4/IPv6 Dual-Stack, VPN IPsec IKEv2 con BGP, SSL VPN con MFA (2FA) y Alta Disponibilidad HA Active-Active / Active-Passive.*

#### 📟 Fabricante: Fortinet FortiOS (FortiGate 40F - 3000F / NSE4 - NSE8 Level)
```bash
# 1. VDOMs & DOMINIOS VIRTUALES DE SEGURIDAD (TENANTS MULTI-CLIENTE)
config system global
  set vdom-mode multi-vdom
end
config vdom
  edit "VDOM_CLIENTE_ESTADO"
  next
end
config global
  config system vdom-link
    edit "vlink_corp"
    next
  end
end

# 2. CONFIGURACIÓN DE SD-WAN & PROBES DE PERFORMANCE SLA
config vdom
  edit "VDOM_CLIENTE_ESTADO"
    config system sdwan
      set status enable
      config zone
        edit "ZONE_WAN_INTERNET"
        next
      end
      config members
        edit 1
          set interface "port1"
          set zone "ZONE_WAN_INTERNET"
          set gateway 200.1.1.1
        next
        edit 2
          set interface "port2"
          set zone "ZONE_WAN_INTERNET"
          set gateway 201.2.2.1
        next
      end
      config health-check
        edit "SLA_PROBE_GOOGLE_DNS"
          set server "8.8.8.8"
          set members 1 2
          config sla
            edit 1
              set latency-threshold 50
              set jitter-threshold 10
              set packetloss-threshold 1
            next
          end
        next
      end
      config service
        edit 1
          set name "RULE_SDWAN_CRITICAL_TRAFFIC"
          set mode priority
          set dst "all"
          set src "all"
          config sla
            edit "SLA_PROBE_GOOGLE_DNS"
              set id 1
            next
          end
          set priority-members 1 2
        next
      end
    end

# 3. DEEP PACKET SSL/TLS INSPECTION & CERTIFICADOS CORPORATIVOS
config firewall ssl-ssh-profile
  edit "DEEP_SSL_INSPECTION_PROFILE"
    config https
      set ports 443
      set status deep-inspection
    end
    set caname "Fortinet_CA_SSL"
  next
end

# 4. PERFILES UTM NGFW (IPS, AV, WEBFILTER, APPLICATION CONTROL)
config ips sensor
  edit "IPS_HIGH_SECURITY"
    config entries
      edit 1
        set severity high critical
        set action block
      next
    end
  next
end
config webfilter profile
  edit "WEBFILTER_CORP"
    config ftgd-wf
      config filters
        edit 1
          set category 26 61
          set action block
        next
      end
    end
  next
end

# 5. POLÍTICAS DE SEGURIDAD STATEFUL DUAL-STACK (IPV4 & IPV6)
config firewall policy
  edit 10
    set name "POL_NGFW_LAN_TO_SDWAN"
    set srcintf "port3"
    set dstintf "ZONE_WAN_INTERNET"
    set srcaddr "all"
    set dstaddr "all"
    set action accept
    set schedule "always"
    set service "ALL"
    set nat enable
    set utm-status enable
    set ips-sensor "IPS_HIGH_SECURITY"
    set webfilter-profile "WEBFILTER_CORP"
    set ssl-ssh-profile "DEEP_SSL_INSPECTION_PROFILE"
    set logtraffic all
  next
end

# 6. VPN SSL CON AUTENTICACIÓN MULTI-FACTOR (MFA 2FA)
config vpn ssl settings
  set servercert "Fortinet_Factory"
  set tunnel-ip-pools "SSLVPN_TUNNEL_POOL"
  set port 10443
  config authentication-rule
    edit 1
      set users "User_MFA_Group"
      set portal "full-access"
    next
  end
end
end
```
**Desglose de Comandos:**
- `config system global / set vdom-mode multi-vdom`: Activa el modo Multi-VDOM en el chasis FortiGate para separar clientes en tenants virtualizados aislados.
- `config system sdwan / config health-check`: Configura SD-WAN con sondas de salud (Health Check Probes) para medir latencia, jitter y pérdida de paquetes en tiempo real.
- `set mode priority / set priority-members 1 2`: Aplica conmutación dinámica de enlaces WAN (Failover dinámico) basado en el cumplimiento estricto del SLA.
- `set status deep-inspection`: Activa la inspección profunda SSL/TLS Deep Packet Inspection desarticulando tráfico cifrado para análisis antivirus e IPS.
- `config ips sensor / set action block`: Configura el sensor IPS para bloquear ataques de severidad High y Critical.
- `config vpn ssl settings / set port 10443`: Configura el portal VPN SSL para acceso remoto con túnel seguro en puerto 10443.

#### 📟 Fabricante: Sophos SFOS (XG / XGS Series / Sophos Certified Architect)
```bash
# 1. SYSTEM SD-WAN & LINK SLA MANAGEMENT
system sd-wan profile add name SDWAN_CRITICAL_SLA latency-threshold 40 jitter-threshold 8 packet-loss-threshold 1
system sd-wan policy add name RULE_SDWAN_VOIP_DATA src-interface Port2 dst-interface Port1 profile SDWAN_CRITICAL_SLA

# 2. FIREWALL SECURITY RULES WITH DEEP THREAT PREVENTION & IPS
system firewall-rule add name POL_CORP_INTERNET srczone LAN dstzone WAN srcnet Any dstnet Any service Any action accept ips-policy protect_client web-policy default app-policy default nat-rule MASQUERADE

# 3. SSL VPN REMOTE ACCESS WITH SOPHOS CONNECT & MFA
system ssl-vpn add profile Sophos_Connect_Access network 192.168.10.0/24 pool 10.81.234.0/24 authentication-mode local-2fa

# 4. HIGH AVAILABILITY CLUSTER ACTIVE-PASSIVE
system ha enable mode active-passive peer-ip 192.168.10.2 hb-interface Port4 cluster-id 100
```
**Desglose de Comandos:**
- `system sd-wan profile add...`: Define perfiles SD-WAN SLA de calidad de enlace en Sophos SFOS.
- `system firewall-rule add...`: Crea regla de seguridad basada en zonas con inspección IPS y Web Protection.
- `system ssl-vpn add profile...`: Configura el acceso remoto SSL VPN con clientes Sophos Connect y doble factor 2FA.

### 📘 CCNA/CCNP — Gestión, Administración, Hardening & Mantenimiento de Equipos (Out-of-Band, AAA, SNMPv3, Syslog, Firmware Update & Password Recovery)
*Procedimientos y comandos exactos para la administración, mantenimiento operativo, respaldo de configuración, actualización de SO/Firmware sin caídas, sincronización de registros y recuperación de contraseñas para todos los equipos de la red.*

#### 📟 Fabricante: Cisco IOS-XE / ISR / ASR / Catalyst
```bash
# 1. GESTIÓN OUT-OF-BAND (MGMT) & AUTENTICACIÓN AAA TACACS+/RADIUS
interface GigabitEthernet0
 description ** INTERFAZ DE GESTION OUT-OF-BAND (OOB MGMT) **
 vrf forwarding Mgmt-intf
 ip address 10.255.0.100 255.255.255.0
 no shutdown
exit
aaa new-model
tacacs server TACACS_NOC_1
 address ipv4 10.0.0.10
 key SuperSecretTacacsKey123!
aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local
aaa accounting exec default start-stop group tacacs+

# 2. SNMPv3 CIFRADO (USM AUTH-PRIV AES/SHA)
snmp-server group GROUP_NOC_V3 v3 priv
snmp-server user admin-noc GROUP_NOC_V3 v3 auth sha AuthPass123! priv aes 128 PrivPass123!
snmp-server host 10.0.0.50 version 3 priv admin-noc

# 3. SYSLOG REMOTO DE SEVERIDAD NOTICE/INFORMATIONAL
logging trap informational
logging source-interface GigabitEthernet0
logging host 10.0.0.50

# 4. RESPALDO Y ACTUALIZACIÓN DE FIRMWARE DE SISTEMA OPERATIVO
# Respaldo de configuración activa por TFTP/SCP:
# copy running-config tftp://10.0.0.50/Cisco_PE1_backup.cfg
# Actualización de firmware IOS-XE:
# copy tftp://10.0.0.50/isr4300-universalk9.17.09.04a.SPA.bin flash:
# boot system flash:isr4300-universalk9.17.09.04a.SPA.bin
# write memory & reload
```
**Desglose de Comandos:**
- `vrf forwarding Mgmt-intf`: Aísla la interfaz de gestión Out-of-Band en una VRF dedicada para evitar ataques desde la red de producción.
- `aaa new-model / tacacs server...`: Habilita la arquitectura AAA con servidor centralizado TACACS+ para control de comandos auditables.
- `snmp-server user ... v3 auth sha ... priv aes 128`: Configura SNMPv3 con nivel de seguridad authPriv (Autenticación SHA y Cifrado AES-128).
- `logging trap informational / logging host...`: Enruta los logs de auditoría hacia el servidor SIEM central.

#### 📟 Fabricante: Juniper JunOS (MX / ACX / SRX)
```bash
configure
set interfaces fxp0 unit 0 family inet address 10.255.0.100/24
set system login radius-server 10.0.0.10 secret "SuperSecretRadiusKey123!"
set snmp v3 usm local-engine user admin-noc authentication-sha authentication-password "AuthPass123!"
set snmp v3 usm local-engine user admin-noc privacy-aes privacy-password "PrivPass123!"
commit check
commit
# Copiar respaldo en JunOS: request system snapshot / file copy /config/juniper.conf.gz tftp://10.0.0.50/
# Actualizar SO JunOS: request system software add /var/tmp/junos-install-mx-x86-64-21.4R3.tgz reboot
```
**Desglose de Comandos:**
- `set interfaces fxp0...`: Asigna direccionamiento a la interfaz física de gestión Out-of-Band (fxp0/me0) en JunOS.
- `request system software add ... reboot`: Instala la imagen oficial de JunOS y realiza el reinicio atómico.

### 🌐 FTTH, GPON OLT/ONT, CPEs & Conversores SFP — Diagnóstico Físico & Aprovisionamiento (Huawei, ZTE, BDCOM, ADTRAN, Allied Telesis iMG/RG, Optone, VKOM)
*Procedimiento paso a paso para soporte y troubleshooting de Capa 1 y Capa 2 en enlaces de fibra óptica: Verificación de niveles de potencia óptica Rx/Tx dBm (-8 a -27 dBm), reflectometría OTDR, aprovisionamiento OMCI OLT-ONT y mapeo de VLANs dot1q/QinQ en CPEs y conversores SFP.*

#### 📟 Fabricante: Huawei OLT GPON (MA5800 / MA5608T)
```bash
# 1. DIAGNÓSTICO ÓPTICO Y POTENCIA DDM EN PUERTO GPON PON
display interface gpon 0/1/1
display ont optical-info 0/1 1 1
# Umbrales Ópticos Normales GPON Class B+ / C+:
# Rx Power en ONT: -8.00 dBm a -27.00 dBm (Alarma por debajo de -28.00 dBm LOS)
# Tx Power en ONT: +0.50 dBm a +5.00 dBm

# 2. VERIFICACIÓN DE ESTADO OMCI ONT Y REGISTRO
display ont info 0 1 1 1
display ont autofind 0/1

# 3. APROVISIONAMIENTO COMPLETO ONT (INTERNET + IPTV + VOIP)
system-view
interface gpon 0/1
 ont add 1 1 sn-auth "485754431A2B3C4D" omci ont-lineprofile-id 10 ont-srvprofile-id 10 desc "CLIENTE_VIP_FTTH_01"
quit
service-port 100 gpon 0/1/1 ont 1 gemport 1 multi-service user-vlan 10 tag-transform translate inner-vlan 100 inbound traffic-table name 100M outbound traffic-table name 100M
service-port 200 gpon 0/1/1 ont 1 gemport 2 multi-service user-vlan 20 tag-transform translate inner-vlan 200 inbound traffic-table name IPTV outbound traffic-table name IPTV
save
```
**Desglose de Comandos:**
- `display ont optical-info 0/1 1 1`: Consulta la potencia óptica en tiempo real recibida por la ONT desde el hilo de fibra óptica (Rx dBm).
- `display ont autofind 0/1`: Escanea el puerto PON para detectar ONTs conectadas no registradas (Autofind).
- `service-port 100 gpon ...`: Crea el Service Port mapeando la VLAN de usuario con perfil de velocidad de 100 Mbps.

#### 📟 Fabricante: ZTE GPON OLT (ZXAN C300 / C320 / C600)
```bash
show gpon onu state gpon-olt_1/2/1
show pon power onu-rx gpon-onu_1/2/1:1
configure terminal
interface gpon-olt_1/2/1
 onu 1 type ZTEG-F660 sn ZTEGC1A2B3D4
exit
interface gpon-onu_1/2/1:1
 name CLIENTE_VIP_FTTH_01
 tcont 1 name T-DATA dba-profile DBA-100M
 gemport 1 name GEM-DATA tcont 1
 service-port 1 vport 1 user-vlan 10 svlan 100
write memory
```
**Desglose de Comandos:**
- `show pon power onu-rx...`: Muestra el nivel de atenuación de potencia óptica Rx en la ONU ZTE.
- `interface gpon-onu_1/2/1:1`: Aprovisiona la ONU con contenedor T-CONT y Service Port.

#### 📟 Fabricante: Allied Telesis iMG / RG CPE (iMG606 / iMG1400 / iMG1500 / RG 606)
```bash
enable
show interface wan0 DDM
show vlan
configure terminal
interface wan0.100
 encapsulation dot1q 100
 ip address dhcp
exit
```
**Desglose de Comandos:**
- `show interface wan0 DDM`: Muestra el diagnóstico DDM óptico del transceptor en el CPE Allied Telesis iMG.

#### 📟 Fabricante: Optone & VKOM Conversores de Medio (OPT-1202S25 / VKS-100-25 / VKDG2)
```bash
system-view
display interface status
display optical-module information
# Diagnóstico por leds frontales:
# FX LINK/ACT: Encendido verde (Enlace óptico establecido)
# TX LINK/ACT: Encendido verde (Enlace de cobre UTP establecido)
# PWR: Encendido verde (Alimentación eléctrica OK)
```
**Desglose de Comandos:**
- `display optical-module information`: Muestra los parámetros del módulo SFP óptico en conversores administrables.

### 🛡️ CCNA / CCNP — Inicialización, Hardening & Gestión NOC
*Plantilla estándar de inicialización y hardening (ISO 27001) adaptada exactamente a los comandos y sintaxis nativa de cada fabricante.*

#### 📟 Fabricante: Cisco IOS-XE (ISR / ASR 1000 / Catalyst 9000)
```bash
configure terminal
hostname Router-NOC-CE1
banner motd ^C ACCESO AUTORIZADO UNICAMENTE PERSONAL NOC ^C
enable secret SuperPasswordNOC123!
username admin privilege 15 secret SuperAdminNOC123!
clock timezone COT -5
ip domain name noc.operador.net
crypto key generate rsa modulus 2048
ip ssh version 2
line vty 0 4
 exec-timeout 5 0
 transport input ssh
 login local
ntp server 10.0.0.1 prefer
logging host 10.0.0.50
snmp-server community NOC_READ RO
end
write memory
```
**Desglose de Comandos:**
- `configure terminal`: Modo de configuración global de Cisco IOS-XE.
- `hostname Router-NOC-CE1`: Asigna el nombre único del equipo.
- `enable secret SuperPasswordNOC123!`: Establece la clave enable cifrada con algoritmo SHA-256.
- `crypto key generate rsa modulus 2048`: Genera el par de llaves RSA de 2048 bits para SSH.
- `transport input ssh`: Deshabilita Telnet y fuerza el uso exclusivo de SSHv2.

---

## 4. Procedimientos de Búsqueda Operacional de Red

---

## 5. Flujos Diagnósticos de Troubleshooting por Niveles (Tier 1 a Tier 4)

### Tecnología: 📊 Zona NOC — Operación, Diagnóstico & Potencia Óptica
Total de pasos diagnósticos: **5**

#### Paso `noc_start`: 1. Tablero de Control NOC — Diagnóstico de Operaciones & Capa Física (Tier 1)
**Descripción**: **Objetivo NOC:** Supervisar la salud del equipo, validar el estado físico de enlaces SFP/CPE/ONT, y verificar alarmas antes de realizar intervenciones de Nivel 2/3.

**Puntos Clave:**
• **Capa Física:** Comprobar estado Link UP/DOWN, errores CRC y nivel de potencia óptica en dBm.
• **Gestión:** Asegurar accesibilidad In-Band u Out-of-Band (Management VRF) y logs Syslog.
• **Criterio de Aceptación:** Interfaces en estado Up/Up, potencia óptica Rx/Tx dentro del rango nominal del módulo SFP/GPON.

**Resultado Esperado**: Todas las interfaces físicas activas en Link UP. Transceivers reportando niveles de potencia óptica en dBm dentro del presupuesto del enlace.


#### Paso `noc_transceiver_optics`: 2. Diagnóstico Óptico & Verificación de Transceivers (Rx/Tx dBm) (Tier 1)
**Descripción**: **Medición DDM / DOM (Digital Diagnostics Monitoring):**
Permite leer en tiempo real la potencia óptica transmitida (**Tx Power**) y recibida (**Rx Power**) en dBm, la temperatura del módulo, el voltaje y la corriente de polarización del láser (**Laser Bias Current**).

**Valores de Referencia Típicos en Fibra Óptica:**
• **Ethernet 1G/10G LX/LR (1310nm - 10km):** Tx: -9.0 a -3.0 dBm | Rx Sensibilidad: -19.0 a -3.0 dBm.
• **Ethernet 10G ER/ZR (1550nm - 40/80km):** Tx: -4.0 a +4.0 dBm | Rx Sensibilidad: -24.0 a -1.0 dBm.
• **GPON OLT Class B+ (1490nm Tx / 1310nm Rx):** Tx OLT: +1.5 a +5.0 dBm | Rx OLT Sensibilidad: -28.0 a -8.0 dBm.
• **GPON ONT (1310nm Tx / 1490nm Rx):** Tx ONT: +0.5 a +5.0 dBm | Rx ONT Sensibilidad: -27.0 a -8.0 dBm.

**Acción NOC:** Si Rx Power está por debajo del umbral de sensibilidad (ej: -29 dBm), existe atenuación excesiva, suciedad en conectores o fisura en la fibra.

**Resultado Esperado**: Niveles de potencia óptica Rx y Tx dentro del rango nominal en dBm (ej: Rx entre -12 dBm y -22 dBm). Sin alarmas de "High Alarm" o "Low Alarm".


#### Paso `noc_ont_gpon_mgmt`: 3. Gestión & Aprovisionamiento ONT/ONU FTTH en OLT (Tier 1)
**Descripción**: **Ciclo de Vida de la Negociación GPON ONT (Estados de la Máquina de Estado GPON):**
• **O1 (Initial State):** La ONT está encendida pero no ha detectado la señal óptica de la OLT (1490nm).
• **O2 (Standby State):** La ONT recibe luz descendente y sincroniza con la trama GPON.
• **O3 (Serial Number State):** La ONT envía su Serial Number (SN) / LOID a la OLT durante la ventana de descubrimiento.
• **O4 (Ranging State):** La OLT mide el retardo de propagación (Ranging Time) y asigna la distancia física en metros.
• **O5 (Operation State):** La ONT está 100% registrada, autenticada y en línea recibiendo tráfico.

**Acciones NOC:**
1. Buscar ONTs no aprovisionadas (`autodiscover` / `unconfigured`).
2. Registrar la ONT asociando su SN al puerto PON y asignar ID de ONT.
3. Asociar perfiles de Línea (T-CONT / GEM Ports) y Servicio (VLANs 802.1Q).

**Resultado Esperado**: ONT negociada en estado O5 (Operation). Service ports activos transmitiendo VLAN de cliente.


#### Paso `noc_ce_provisioning`: 4. Diagnóstico de Equipos Customer Edge (CE) & Demarcación L2/L3 (Tier 2)
**Descripción**: **Verificación del Equipo de Demarcación Customer Edge (CE):**
Los equipos CE conectan el sitio del cliente con la red de transporte del operador.

**Puntos de Validación NOC:**
• **Subinterfaces / Tagging:** Validar encapsulación `dot1q` / `QinQ` en puerto WAN.
• **Direccionamiento IP:** Verificar máscaras `/30` (punto a punto tradicional) o `/31` (RFC 3021 para ahorro de espacio IP).
• **Políticas de Tráfico (Rate Limiting):** Confirmar que el Shaping / Policing coincida con el ancho de banda contratado por el cliente (ej. 50M, 100M, 1G).
• **Pruebas de Conectividad:** Ping con fragmentación desactivada (DF bit set) para validar MTU sin descartes.

**Resultado Esperado**: Subinterfaces L2/L3 en Up/Up. Ancho de banda y MTU validados sin pérdidas de paquetes.


#### Paso `noc_handover_checklist`: 5. Checklist de Entrega Final a Cliente (Service Handover Checklist) (Tier 1)
**Descripción**: **Checklist de Validación Final de Servicio NOC antes de Entrega a Producción:**

1. **Prueba de Capa 1:** Verificar que no haya incrementos de errores CRC, alineación ni descartes en contadores de puerto.
2. **Prueba de Capa 2 / 3:** Confirmar que la dirección IP de cliente o VLAN responda pings estables (< 15ms).
3. **Prueba de MTU:** Ejecutar `ping` con bit DF (Dont Fragment) en 1472 bytes (1500 MTU total) sin pérdidas.
4. **Limpieza de Contadores:** Reiniciar contadores de interfaz para dejar métricas en cero antes de la ventana comercial.
5. **Respaldo & Backup:** Guardar la configuración en la memoria no volátil (`write memory` / `commit` / `save`) y exportar copia al repositorio del NOC.

**Resultado Esperado**: Servicio 100% verificado, sin errores CRC, copia de seguridad guardada y listo para acta de entrega.


### Tecnología: MPLS Core Troubleshooting
Total de pasos diagnósticos: **11**

#### Paso `mpls_start`: 1. Definir ámbito del problema MPLS (Tier 1)
**Descripción**: **Dónde:** El problema suele presentarse en el plano de control (vecindades LDP/RSVP/BGP caídas) o en el plano de datos (forwarding MPLS, LFIB, MTU/MSS).

**Cómo:** Interfaces MPLS en Down, vecinos LDP en NonExistent, labels no programadas, tráfico droppeado silenciosamente o con contadores de error creciendo.

**Cuándo:** Tras reconvergencia IGP, cambios de configuración, upgrades de software, o cuando se supera la MTU del enlace con stacks de labels múltiples.

**Por qué:** Desincronización IGP-MPLS, filtros de labels, MTU insuficiente, ACLs bloqueando protocolos de señalización, o transport-address inalcanzable.

**Para qué:** Determinar si la falla es de control plane (protocolos) o data plane (forwarding/MTU) para enfocar el troubleshooting sin perder tiempo en áreas no afectadas.

Acción inicial: ejecute comandos de estado general del router y verifique salud de CPU/memoria.

**Resultado Esperado**: Router estable, CPU < 80%, memoria disponible. Sin mensajes de error recientes en logs. Interfaces MPLS en Up/Up.

🔬 **Hipótesis Científica**: La falla observada es causada por una discontinuidad en el plano de control MPLS (IGP no sincronizado, sesión LDP/RSVP caída, o transport-address inalcanzable) que impide la correcta programación de la LFIB, resultando en blackholing o descartes silenciosos en el data plane.
🛠️ **Solución Rápida (Quick Fix)**: 1. Habilitar 'family mpls' (JunOS) o 'mpls ip' (Cisco) en todas las interfaces troncales.
2. Verificar y corregir la ruta IGP (/32 loopback) hacia la transport-address del peer LDP.
3. Si hay MTU issues: aumentar MTU a 9000 en interfaces troncales o configurar 'mpls mtu' adecuada.
4. Revisar ACLs/firewall filters que bloqueen UDP 646 (LDP) o IP 46 (RSVP).
5. Si RSVP-TE: verificar que la TED tenga ancho de banda suficiente y ajustar reservas.

#### Paso `mpls_health`: Salud general MPLS (Tier 1)
**Descripción**: **Dónde:** Verifique en todas las interfaces habilitadas para MPLS y en las sesiones de señalización.

**Cómo:** Use "show mpls interface" y "show ldp/rsvp neighbor" para validar estados. Un vecino LDP en "Operational" indica que la FEC puede intercambiarse.

**Cuándo:** Como chequeo proactivo antes de un cambio de red, o cuando se sospecha de blackholing.

**Por qué:** Un solo vecino LDP caído puede romper el LSP end-to-end y causar pérdida de tráfico VPN.

**Para qué:** Confirmar que la base MPLS (interfaces + señalización + tablas) está sana antes de profundizar.

**Resultado Esperado**: Interfaces MPLS en state Up/Up. Vecinos LDP/RSVP Established/Operational. MPLS forwarding table poblada con labels locales y remotas. Sin discrepancias de MTU.


#### Paso `mpls_ctrl_sig`: 2. Protocolo de Señalización (LDP / RSVP / SR) (Tier 1)
**Descripción**: **Dónde:** Plano de control: sesiones LDP (UDP 646), RSVP (IP 46), o BGP labeled-unicast.

**Cómo:** Los vecinos pueden aparecer en "Initialized", "OpenSent", o directamente caídos. En RSVP, los mensajes Path/Resv no se intercambian si falta bandwidth o hay ruta bloqueada.

**Cuándo:** Luego de cambios de IGP, redistribución, o cuando se migran routers (nuevo router-id).

**Por qué:** Requisitos de adjacency: transport-address alcanzable, timers coincidentes, misma área/level, sin ACLs bloqueando, y MTU suficiente para paquetes de control.

**Para qué:** Restaurar la distribución de labels/FEC para que el data plane pueda construir el LFIB.

**Resultado Esperado**: LDP: Operational, address families ipv4/ipv6 activas. RSVP: Hello/Keepalives OK, sin errores de auth. Ambos extremos usan la misma transport-address y la ruta IGP la alcanza.

🔬 **Hipótesis Científica**: El protocolo de señalización (LDP o RSVP-TE) no establece o mantiene la sesión debido a fallas en la transport-address, desajuste de timers, ACLs/firewall filters, o falta de recursos (ancho de banda en RSVP-TE).
🛠️ **Solución Rápida (Quick Fix)**: 1. Corregir la ruta IGP hacia la transport-address (asegurar /32 loopback en OSPF/IS-IS).
2. Sincronizar timers Hello/Keepalive en ambos peers (ej. 5s/15s).
3. Eliminar o ajustar ACLs/firewall que bloqueen UDP 646 o IP 46.
4. Para RSVP-TE: aumentar ancho de banda en la TED o reducir la reserva solicitada.
5. Capturar tráfico en la interfaz para confirmar que los paquetes de control llegan y salen.

#### Paso `mpls_ctrl_down`: 2.1 Vecinos de Señalización DOWN (Tier 1)
**Descripción**: **Dónde:** La transport-address (LSR-id en JunOS, router-id en IOS-XR/XE) debe ser alcanzable vía IGP.

**Cómo:** Si "show route <lsr-id>" no devuelve ruta, o si la interfaz de salida no tiene "family mpls" / "mpls ip", la sesión no se establece. Verifique también ACLs/firewall filters que descarten UDP 646.

**Cuándo:** Después de renumbering de loopbacks, cambios de área OSPF, o cuando un enlace P-P cae.

**Por qué:** LDP requiere alcanzabilidad IP a la transport-address. RSVP requiere IP a la interfaz de señalización. Una interfaz sin "mpls ip" no envía ni recibe mensajes de señalización.

**Para qué:** Garantizar que el plano de control MPLS tenga reachability L3 end-to-end.

**Resultado Esperado**: Ruta válida (preferiblemente IGP, no estática solitaria) hacia la transport-address. Sin ACLs bloqueando UDP 646 (LDP) o IP 46 (RSVP). Interfaces con MPLS habilitado.

🔬 **Hipótesis Científica**: Los vecinos LDP/RSVP están DOWN porque la transport-address no es alcanzable vía IGP, la interfaz física no tiene MPLS habilitado, o existe un filtro de seguridad/ACL bloqueando el tráfico de señalización.
🛠️ **Solución Rápida (Quick Fix)**: 1. Asegurar que la interfaz tenga 'family mpls' (JunOS) o 'mpls ip' (Cisco) activo.
2. Corregir la ruta IGP hacia la transport-address (asegurar /32 loopback).
3. Eliminar ACLs/firewall que bloqueen UDP 646 (LDP) o IP 46 (RSVP).
4. Aumentar MTU de la interfaz a al menos 9000 bytes para soportar stacks de labels múltiples.
5. Verificar que no haya duplicado de Router-ID/LSR-ID en la red.

#### Paso `mpls_ctrl_nolabel`: 2.2 Vecinos UP pero Label Binding falla (Tier 2)
**Descripción**: **Dónde:** Label Information Base (LIB). Cada router solo genera un binding de label si conoce la FEC por IGP.

**Cómo:** "show ldp database" vacío o sin la FEC esperada. En JunOS, "show ldp route" debe mostrar la FEC.

**Cuándo:** Después de aplicar filtros de import/export de labels, o cuando se agrega una nueva VPN pero la FEC no existe en IGP.

**Por qué:** LDP solo genera binding para rutas IGP activas. Si hay una policy que filtra la FEC, o si la ruta está en una VRF sin redistribución, no se genera label.

**Para qué:** Asegurar que todas las rutas que necesitan forwarding MPLS tengan bindings locales y remotos.

**Resultado Esperado**: Bindings presentes para todas las FECs relevantes. Sin filtros agresivos de import/export de labels. La FEC existe en la tabla IGP (inet.0 / global).

🔬 **Hipótesis Científica**: Los vecinos LDP/RSVP están UP pero no intercambian labels (bindings) porque la FEC no existe en la tabla IGP, existe una policy de import/export filtrando la FEC, o el rango de labels locales se ha agotado.
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar que la FEC destino esté activa en la RIB/VRF y no sea filtrada por IGP.
2. Revisar 'show ldp database'/'show mpls ldp bindings' para confirmar binding local/remoto; si falta, forzar re-anuncio o reiniciar LDP.
3. Ajustar policies de import/export de LDP para permitir explícitamente la FEC (aceptar prefijo o eliminar regla de reject).
4. Ampliar el rango de labels locales si está agotado ('mpls label range') y verificar capacidad de hardware.
5. En escenarios VRF, confirmar redistribución del protocolo PE-CE hacia MP-BGP/LDP.
6. Validar que la FEC tenga binding remoto en ambos PEs antes de probar tráfico.


#### Paso `mpls_policies`: 2.3 Políticas/Filtros de Labels (Tier 3)
**Descripción**: **Dónde:** Políticas de LDP (filtros de FEC), BGP labeled-unicast, o route-maps en PEs inter-AS.

**Cómo:** Las policies pueden descartar implícitamente prefijos. Verifique términos de "from" y "then accept/reject".

**Cuándo:** En entornos inter-AS (Option B/C) o cuando se segmentan dominios MPLS para evitar fuga de rutas.

**Por qué:** Un filtro mal configurado en un PE puede impedir que las labels de una VPN lleguen a los PEs remotos, causando blackholing del tráfico VPN aunque el IGP esté sano.

**Para qué:** Validar que las policies no descarten implícitamente los bindings o routes necesarias.

**Resultado Esperado**: Permitir FECs esperadas en import/export de LDP. BGP labeled-unicast sin prefix-list que bloquee el nexthop. No descartar implícitamente los bindings necesarios.

🔬 **Hipótesis Científica**: Los bindings de labels no se generan o no se propagan para ciertas FECs porque una política de filtrado (accept/reject en LDP, prefix-segment policy en SR, o filtro de RSVP-TE) está descartando silenciosamente las etiquetas, o porque el rango local de labels (label space) se ha agotado para el prefijo de interés.
🛠️ **Solución Rápida (Quick Fix)**: 1. Revisar policies LDP/RSVP/SR y cambiar reglas reject/deny a accept/permit para la FEC de interés.
2. Ampliar rango de labels locales si está agotado.
3. Confirmar que la FEC esté activa en RIB y no filtrada por IGP prefix-list.
4. Ajustar orden de reglas en policies para no descartar prematuramente.
5. Verificar bindings locales/remotos en 'show ldp database'/'show rsvp session'.
6. Validar que la FEC tenga label asignado end-to-end.


#### Paso `mpls_igp_sync`: 2.4 Sincronización IGP ↔ MPLS (Tier 2)
**Descripción**: **Dónde:** En los enlaces P-P y PE-P donde corre IGP (OSPF/IS-IS) y MPLS.

**Cómo:** Si IGP converge más rápido que LDP, el router puede enviar tráfico MPLS a un vecino que aún no tiene labels, causando blackholing. LDP-IGP Sync evita esto manteniendo la ruta IGP "down" hasta que LDP esté listo.

**Cuándo:** Durante reconvergencias rápidas (sub-segundo) o cuando un vecino LDP tarda en levantar por CPU alta.

**Por qué:** Sin sincronización, el IGP anuncia la ruta como usable pero el data plane no tiene label para el nexthop, lo que resulta en descarte silencioso.

**Para qué:** Evitar blackholing transitivo durante eventos de convergencia.

**Resultado Esperado**: OSPF/IS-IS neighbor FULL/UP en interfaces MPLS. IGP sync habilitado si el diseño lo requiere. Métricas IGP consistentes en todos los routers del área/level.

🔬 **Hipótesis Científica**: La desincronización entre IGP y MPLS (ausencia de LDP-IGP Synchronization o IGP shortcut sin RSVP funcional) causa que el tráfico IP se enrute hacia un next-hop cuyo LSP está caído o incompleto, produciendo blackholing o forwarding IP directo no deseado en el core MPLS.
🛠️ **Solución Rápida (Quick Fix)**: 1. Habilitar LDP-IGP Synchronization en interfaces de tránsito del core.
2. Configurar holddown timers para retrasar instalación de rutas IGP hasta que LDP esté listo.
3. Evitar que IGP instale rutas hacia next-hops con LDP session Down.
4. Verificar convergencia simultánea de IGP y LDP en logs.
5. Revisar configuración de IGP shortcut/Forwarding Adjacency con LSP funcional.
6. Confirmar que no haya forwarding IP puro en core MPLS sin label.


#### Paso `mpls_data_fwd`: 3. Plano de Datos MPLS (LFIB / MTU / Stack) (Tier 1)
**Descripción**: **Dónde:** LFIB/LFEB en hardware (PFE/FPC/ASIC) y en las interfaces P-P.

**Cómo:** Incluso si el control plane es sano, el forwarding puede fallar por: LFIB incompleta, MTU insuficiente para frames con labels, o PHP no deseado en L3VPN.

**Cuándo:** Tras cambios de hardware, upgrades de software, o cuando se añaden servicios con stacks de labels más grandes (SR + VPN).

**Por qué:** Cada label agrega 4 bytes. L3VPN usa al menos 2 labels (Transport + VPN). SR puede usar múltiples SIDs. Si la MTU física no soporta el frame completo, hay fragmentación o descarte silencioso.

**Para qué:** Validar que el data plane pueda forwardar tráfico MPLS real end-to-end sin drops.

**Resultado Esperado**: Entradas LFIB/LFEB con acciones Pop/Swap/Push correctas. MTU >= 1508 para un label (1516+ para stack VPN+Transport). Nexthop resuelto en capa 2 bajo el túnel.

🔬 **Hipótesis Científica**: El reenvío de paquetes MPLS falla en el data plane porque la LFIB carece de una entrada válida para el label recibido, la pila de labels está mal formada (TTL expirado, stack mal balanceado), o la MTU de una interfaz del path es insuficiente para el paquete etiquetado.
🛠️ **Solución Rápida (Quick Fix)**: 1. Completar entradas faltantes en LFIB para labels del LSP (pop/swap/push correctos).
2. Corregir stack de labels desbalanceado en ingress/transit/egress.
3. Aumentar MTU en interfaces del path para soportar payload + overhead de labels.
4. Ajustar TTL de origen para sobrevivir decremento por salto MPLS.
5. Verificar configuración de PHP coordinada con egress PE.
6. Validar reenvío de paquetes MPLS sin descartes en data plane.


#### Paso `mpls_data_mtu`: 3.1 Problemas de MTU en MPLS (Tier 2)
**Descripción**: **Dónde:** Interfaces P-P y CE-PE donde circula tráfico MPLS.

**Cómo:** Ping con DF-bit y payload grande (1500+ bytes) falla cuando la MTU no soporta el overhead de labels. En JunOS use "ping mpls ldp <fec> size <size> do-not-fragment".

**Cuándo:** Cuando los clientes reportan throughput bajo pero no pérdida total (fragmentación), o cuando un nuevo L3VPN/SR se activa.

**Por qué:** Cada label suma 4 bytes. L3VPN usa 2 labels (8 bytes). SR-MPLS con 3 SIDs suma 12 bytes. Si la MTU de la interfaz es 1500 y el frame ya viene con 1500 bytes de payload, los labels lo exceden.

**Para qué:** Garantizar que el path end-to-end soporte frames de 1500+overhead sin fragmentación.

**Resultado Esperado**: Ping con DF-bit y payload >= 1500 bytes debe pasar sin fragmentación end-to-end. MTU >= 1508 para LDP simple, >= 1516 para L3VPN doble-label, >= 1524 para stacks mayores.

🔬 **Hipótesis Científica**: La MTU insuficiente en una o más interfaces del path MPLS causa fragmentación o descarte silencioso de paquetes etiquetados, especialmente cuando se usan stacks de múltiples labels (Transport + VPN + Entropy) que añaden 12+ bytes al frame original, superando la MTU configurada en el enlace físico.
🛠️ **Solución Rápida (Quick Fix)**: 1. Aumentar MTU en interfaces físicas/lógicas del path MPLS (>=1504 para 1 label, >=1516 para 4 labels).
2. Calcular overhead máximo de labels esperado y sumarlo al payload.
3. Ejecutar ping con tamaño máximo y DF entre CEs a través del servicio MPLS.
4. Limpiar contadores de 'MTU exceeded'/'giant frames'.
5. Alinear MTU PE-CE con MTU core menos overhead de labels.
6. Confirmar que no haya fragmentación ni descartes silenciosos.


#### Paso `mpls_data_blackhole`: 3.2 Blackholing / Tráfico Droppeado con Labels (Tier 3)
**Descripción**: **Dónde:** Forwarding plane, ARP/ND bajo el túnel, ACLs en interfaces P-P, y QoS policies con EXP/DSCP mismatch.

**Cómo:** Labels existen en LFIB pero los contadores de drop crecen. Puede ser por next-hop MAC no resuelto, firewall filter descartando por EXP, o ECMP hashing mal configurado.

**Cuándo:** Tras migraciones de CE, cambios de ARP timeout, o cuando se aplican nuevas políticas de QoS en el core.

**Por qué:** Si el next-hop bajo el túnel no tiene ARP, el frame MPLS no puede salir. Si un firewall filter descarta por EXP no esperado, el tráfico se pierde silenciosamente.

**Para qué:** Identificar la causa exacta del drop en el data plane cuando el control plane parece sano.

**Resultado Esperado**: Nexthop resuelto (ARP/ND completo). Sin contadores de descarte creciendo en ACLs/QoS. ECMP hashing entrega flujos consistentemente. Labels programadas en hardware (LFIB = CEF).

🔬 **Hipótesis Científica**: El blackholing de tráfico MPLS ocurre cuando un paquete etiquetado llega a un router que no tiene entrada en la LFIB para ese label (label swapping incorrecto), cuando el egress PE no puede resolver el payload IP a una VRF/IP global válida, o cuando el LSP es unidireccional y el return path usa un label no programado.
🛠️ **Solución Rápida (Quick Fix)**: 1. Completar entradas LFIB faltantes para labels de transporte/VPN en cada salto.
2. Corregir label stack para que push/swap/pop estén balanceados en ida y vuelta.
3. Asegurar que egress PE tenga ruta hacia destino del payload en VRF/tabla global.
4. Verificar simetría del LSP bidireccional con traceroute MPLS.
5. Limpiar contadores de 'No label'/'Lookup failed'.
6. Validar que el tráfico de usuario alcance el destino sin blackholing.


#### Paso `mpls_te_path`: 3.3 RSVP-TE Path / Reservas (Tier 3)
**Descripción**: **Dónde:** MPLS Traffic Engineering (RSVP-TE) y los constraints de bandwidth/admin-groups.

**Cómo:** Un LSP puede estar DOWN por falta de bandwidth reservable en un enlace del path, o porque la ruta explícita (ERO) pasa por un enlace que ya no existe.

**Cuándo:** Cuando se configuran LSPs con reserva de bandwidth o affinity constraints, y el tráfico de fondo consume la capacidad reservable.

**Por qué:** RSVP-TE reserva bandwidth hop-by-hop. Si un enlace intermedio no tiene suficiente bandwidth reservable, el LSP no establece y el PATH/RESV state queda en "Retry".

**Para qué:** Asegurar que los LSPs críticos (para VPNs o servicios prioritarios) tengan bandwidth garantizado end-to-end.

**Resultado Esperado**: LSPs en estado UP/Established. Bandwidth reservable disponible en todos los enlaces del path. Constraints (affinity, bandwidth) cumplidos. Sin preemption no deseado.

🔬 **Hipótesis Científica**: El túnel RSVP-TE no establece el LSP deseado porque el path calculado por CSPF no es viable: la TED (Traffic Engineering Database) está desactualizada, las restricciones de bandwidth o admin-group no se cumplen en todos los saltos, o RSVP encuentra errores de reserva (Reservation Error) en un nodo intermedio.
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar TED y asegurar bandwidth disponible en cada enlace del path.
2. Ajustar restricciones de admin-group/affinity para que CSPF encuentre ruta.
3. Resolver errores de reserva RSVP ('Reservation Error') aumentando bandwidth o reduciendo solicitud.
4. Habilitar OSPF/IS-IS TE extensions en todos los routers del área.
5. Corregir explicit-path si un salto es inalcanzable.
6. Confirmar que el túnel TE establezca LSP con Path/Resv intercambiados.


### Tecnología: L3VPN Troubleshooting
Total de pasos diagnósticos: **10**

#### Paso `l3vpn_start`: 1. Ámbito del problema L3VPN (Tier 1)
**Descripción**: **Dónde:** El problema se manifiesta en el CE (sin conectividad), en el PE (sin rutas VPN), o entre PEs (MP-BGP caído).

**Cómo:** Usuario reporta que no puede alcanzar sitios remotos. En el PE, "show bgp summary" indica peers VPNv4 caídos, o las tablas VRF no tienen rutas.

**Cuándo:** Tras cambios de configuración en VRF, upgrades de software, o cuando se migra un CE a otro PE.

**Por qué:** Fallas comunes: RD/RT mal configurados, MP-BGP AF VPNv4 no activa, políticas de redistribución omitidas, o next-hop inalcanzable.

**Para qué:** Determinar si la falla está en el CE-PE, en el control plane MP-BGP entre PEs, o en el forwarding VRF.

**Resultado Esperado**: BGP peers UP en VPNv4. VRFs definidos con RD/RT correctos. Rutas locales y remotas presentes en tablas BGP/VRF.

🔬 **Hipótesis Científica**: La falla de conectividad del cliente en L3VPN es causada por una ruptura en la cadena de señalización end-to-end: falla en el core MPLS (LSP no funcional), sesión MP-BGP VPNv4 caída, o desajuste de Route Targets (RT) entre PEs de origen y destino.
🛠️ **Solución Rápida (Quick Fix)**: 1. Validar LSP MPLS entre PEs con ping MPLS o traceroute MPLS. Corregir LDP/RSVP si está caído.
2. Verificar que MP-BGP VPNv4 esté en Established; corregir AS mismatch o MD5/TCP 179 si aplica.
3. Asegurar que export-RT en origen == import-RT en destino (y viceversa).
4. Verificar que el prefijo del cliente esté en la VRF local y en VPNv4 RIB.
5. Confirmar que el Next-Hop de VPNv4 sea resoluble vía IGP y tenga label MPLS en LFIB.

#### Paso `l3vpn_ce_pe`: 2. CE-PE Routing (Tier 1)
**Descripción**: **Dónde:** En el enlace físico/subinterfaz entre CE y PE, y en la sesión de routing (BGP/OSPF/estático) dentro de la VRF.

**Cómo:** Interfaces en Down/Down, vecinos BGP en Active/Idle, OSPF en 2-Way/Init, o sin rutas CE en la VRF del PE.

**Cuándo:** Tras cambios de cableado, reconfiguración de subinterfaces dot1q/QinQ, o cambios de AS/área.

**Por qué:** Mismatch de encapsulación, ACLs en interfaz CE-PE, AS/area ID diferente, o redistribución mal configurada en el PE.

**Para qué:** Asegurar que el PE aprende correctamente las rutas del CE antes de propagarlas por MP-BGP.

**Resultado Esperado**: Interfaz CE-PE Up/Up. Vecindad de routing Established/Full. Rutas CE presentes en la tabla VRF del PE.

🔬 **Hipótesis Científica**: La falla de conectividad entre CE y PE es causada por un error en el protocolo de routing PE-CE (OSPF, BGP, estático), un mismatch de parámetros de vecindad (AS, timers, área, autenticación), o una falta de asociación de la interfaz PE-CE a la VRF correcta.
🛠️ **Solución Rápida (Quick Fix)**: 1. Asegurar interfaz PE-CE Up/Up y vinculada a la VRF del cliente.
2. Configurar protocolo de routing PE-CE dentro del contexto VRF.
3. Alinear parámetros de vecindad (AS, área, timers, MTU, autenticación).
4. Coincidir VLAN/encapsulación en enlace PE-CE.
5. Revisar logs de autenticación o mismatch.
6. Validar adyacencia PE-CE y rutas en la VRF.


#### Paso `l3vpn_encap`: 2.A Troubleshooting de Encapsulación L2 en CE-PE (Tier 2)
**Descripción**: **Dónde:** En las subinterfaces CE-PE donde se configura dot1q, QinQ (802.1ad), o untagged.

**Cómo:** Subinterface no levanta aunque el enlace físico esté OK. Si hay QinQ, el PE puede descartar frames por TPID 0x88a8 no soportado.

**Cuándo:** Al migrar un CE de una encapsulación a otra, o cuando se agrega un nuevo servicio con VLAN stacking.

**Por qué:** Mismatch de encapsulación (CE envía untagged, PE espera dot1q), o VLAN ID diferente en cada extremo.

**Para qué:** Verificar que el Attachment Circuit esté correctamente mapeado a la VRF y que la trama L2 llegue al PE.

**Resultado Esperado**: Subinterface Up/Up. Encapsulación coincidente (dot1q/QinQ/untagged). VLAN ID y TPID correctos en ambos extremos.


#### Paso `l3vpn_ce_pe_down`: 2.1 Vecindad CE-PE DOWN (Tier 1)
**Descripción**: **Dónde:** Capa física y L2 entre CE y PE; L3 reachability y autenticación del protocolo de routing.

**Cómo:** Interfaz en Administratively Down o error-disabled. BGP en Idle por TTL o AS mismatch. OSPF no envía Hellos.

**Cuándo:** Tras aplicar políticas de seguridad, cambios de autenticación, o fallas de cableado/óptica.

**Por qué:** Shutdown manual, BPDU guard, port security, autenticación MD5/text diferente, o Hello/Dead timers mismatch.

**Para qué:** Restaurar la conectividad L2/L3 básica CE-PE para que el routing pueda establecerse.

**Resultado Esperado**: Interface Up/Up, sin errores de capa física. VLAN tagging coincide. IP address en la misma subnet. Auth/timers iguales.

🔬 **Hipótesis Científica**: La adyacencia CE-PE no se establece o cae porque los parámetros de Capa 2 están fallando (VLAN mismatch, cable desconectado, duplex/speed), o porque los parámetros del protocolo de routing (OSPF area, BGP AS, timers, autenticación) no coinciden en ambos extremos del enlace PE-CE.
🛠️ **Solución Rápida (Quick Fix)**: 1. Resolver estado físico del enlace PE-CE (cable, SFP, dúplex, velocidad).
2. Corregir VLAN/encapsulación en CE y PE.
3. Alinear AS BGP, área OSPF, timers, autenticación.
4. Levantar interfaz PE si está shutdown y quitar passive-interface si aplica.
5. Eliminar ACLs/storm-control que descarten paquetes de control.
6. Confirmar adyacencia estable en ambos extremos.


#### Paso `l3vpn_redist`: 2.2 Redistribución CE→PE en VRF (Tier 2)
**Descripción**: **Dónde:** Dentro del proceso BGP del PE, en el address-family VPNv4/VPNv6 y la VRF correspondiente.

**Cómo:** El CE tiene rutas, pero el PE no las anuncia a los PEs remotos. "show route table <vrf>.inet.0" las muestra, pero "show bgp summary" no las cuenta.

**Cuándo:** Al agregar una nueva red CE, o cuando se reemplaza el protocolo CE-PE (por ejemplo, de OSPF a BGP).

**Por qué:** JunOS requiere rib-groups o policies explícitas; XR/XE requieren "redistribute" bajo el address-family VPNv4. Sin esto, la ruta local no se convierte en NLRI VPNv4.

**Para qué:** Garantizar que todas las rutas CE se inyecten correctamente en MP-BGP con el RD y RT apropiados.

**Resultado Esperado**: Rutas locales VRF presentes en la tabla BGP VPNv4 con RD correcto y extended communities RT/SOO.

🔬 **Hipótesis Científica**: Los prefijos del cliente no llegan al core MP-BGP porque la redistribución desde el protocolo PE-CE (OSPF, BGP, estático, RIP) hacia MP-BGP VPNv4 está omitida, mal configurada, o filtrada por un route-map que bloquea los prefijos de interés.
🛠️ **Solución Rápida (Quick Fix)**: 1. Configurar redistribución explícita del protocolo PE-CE hacia MP-BGP VPNv4.
2. Revisar route-map de redistribución y cambiar denies que afecten prefijos del cliente.
3. Confirmar prefijos del cliente en tabla de rutas de VRF local.
4. Verificar prefijos en VPNv4 RIB.
5. Revisar contadores de matches del route-map.
6. Validar que prefijos lleguen al PE destino e instalen en VRF remota.


#### Paso `l3vpn_policies`: 2.3 Políticas / Route-maps (RD/RT / SOO) (Tier 3)
**Descripción**: **Dónde:** Policies de import/export de BGP, route-maps, y filtrado de communities RT/SOO en los PEs.

**Cómo:** Rutas recibidas pero no instaladas. "show bgp neighbor <peer> routes" muestra prefijos, pero la RIB VRF no los tiene.

**Cuándo:** En entornos multi-VRF, inter-AS, o con CEs dual-homed donde SOO previene loops.

**Por qué:** Un RT export no coincide con el RT import del PE remoto. SOO conflictivo evita la instalación. Route-map descarta por prefix-list.

**Para qué:** Validar que las políticas no bloqueen implícitamente rutas esperadas y que los RTs formen el dominio VPN correcto.

**Resultado Esperado**: Extended communities RT coinciden en export e import. Sin SOO conflictivo. Route-maps permiten prefijos esperados.

🔬 **Hipótesis Científica**: Los prefijos VPNv4 son recibidos pero descartados silenciosamente debido a un mismatch en los Route Targets de importación/exportación, un RD duplicado que rompe la unicidad del prefijo en el core, o un Site-of-Origin (SOO) que previene loops de redistribución bloqueando la re-importación de rutas propias.
🛠️ **Solución Rápida (Quick Fix)**: 1. Alinear export-RT en PE origen con import-RT en PE destino (y viceversa).
2. Asignar RD único por VRF en todo el dominio.
3. Revisar SOO para no bloquear re-importación legítima.
4. Permitir comunidades extendidas RT en policies de entrada/salida VPNv4.
5. Verificar en VPNv4 RIB destino si las rutas llegan y se importan a VRF.
6. Confirmar conectividad inter-site del cliente.


#### Paso `l3vpn_mpbgp`: 3. MP-BGP VPNv4/v6 entre PEs (Tier 2)
**Descripción**: **Dónde:** Sesiones MP-iBGP (o eBGP Option B/C) entre PEs, address-family VPNv4/VPNv6.

**Cómo:** Peers en Established pero "show bgp vpnv4 unicast summary" no muestra rutas, o capacidades AFI/SAFI no negociadas.

**Cuándo:** Tras cambios de loopback/update-source, reconfiguración de address-families, o migración de RR.

**Por qué:** Update-source no alcanzable, multihop TTL insuficiente, password mismatch, o AF VPNv4 no activa en uno de los lados.

**Para qué:** Asegurar que el canal MP-BGP esté listo para transportar NLRI VPN entre PEs.

**Resultado Esperado**: Peers UP en AF VPNv4. Capacidades AFI/SAFI 1/128 (IPv4) o 2/128 (IPv6) negociadas. Rutas recibidas/advertisadas > 0.

🔬 **Hipótesis Científica**: Las sesiones MP-BGP entre PEs no establecen la address family VPNv4/VPNv6, o los prefijos son anunciados pero el Next-Hop no es alcanzable vía el core MPLS, impidiendo la instalación de rutas VPN en la LFIB y causando blackholing del tráfico inter-site del cliente.
🛠️ **Solución Rápida (Quick Fix)**: 1. Establecer sesión BGP base Established y activar address family VPNv4/VPNv6.
2. Verificar capability exchange AFI/SAFI 1/128 o 2/128.
3. Asegurar Next-Hop (loopback PE origen) alcanzable vía IGP/MPLS.
4. Verificar labels de transporte hacia loopback PE origen en LFIB de core.
5. Confirmar rutas VPNv4 con next-hop resoluble y label stack completo.
6. Validar instalación en LFIB y forwarding de tráfico VPN.


#### Paso `l3vpn_mpbgp_down`: 3.1 Peers MP-BGP caídos o sin VPNv4 (Tier 2)
**Descripción**: **Dónde:** Plano de control BGP: transport a la loopback/update-source, puerto TCP 179, y capacidades.

**Cómo:** Peer en Active/Idle/Connect. "show bgp neighbor" muestra state mismatch o "no route to peer".

**Cuándo:** Después de renumbering de loopbacks, cambios de IGP, o aplicación de ACLs.

**Por qué:** La ruta al update-source debe existir en la tabla global (no en VRF). TCP 179 no debe estar filtrado. Ambos lados deben activar address-family vpnv4.

**Para qué:** Restaurar la sesión MP-BGP para que la VPN pueda intercambiar rutas.

**Resultado Esperado**: Estado Established. Address-family vpnv4 activo en ambos extremos. Ruta IGP válida hacia el update-source. TCP 179 libre.

🔬 **Hipótesis Científica**: La sesión MP-BGP cae o no negocia la familia VPNv4/VPNv6 debido a un capability mismatch, una política que rechaza la NLRI, o una falla del underlay IP/MPLS entre las loopbacks de PE que transporta la sesión TCP 179 de BGP.
🛠️ **Solución Rápida (Quick Fix)**: 1. Restaurar sesión BGP base o corregir capability mismatch.
2. Activar address family VPNv4/VPNv6 bajo el neighbor.
3. Verificar conectividad IP y TCP 179 entre loopbacks de PE.
4. Eliminar ACLs/firewall filters/QoS descartando TCP 179.
5. Corregir AS mismatch u otros NOTIFICATION.
6. Confirmar sesión MP-BGP Established y estable.


#### Paso `l3vpn_mpbgp_noroutes`: 3.2 Peers UP pero sin intercambio de rutas VPN (Tier 3)
**Descripción**: **Dónde:** BGP NLRI filtrado, next-hop reachability, o RIB-failure en el PE receptor.

**Cómo:** Peer Established, "show bgp vpnv4 unicast neighbor <peer> routes" muestra rutas, pero no se instalan o no se re-advertisen.

**Cuándo:** Tras cambios de policies, cuando el next-hop MPLS subyacente falla, o al alcanzar maximum-prefix.

**Por qué:** Policies inbound descartan. Next-hop inalcanzable (falta label/LDP hacia PE origen). Cluster-id/originator-id loop. Maximum-prefix exceeded.

**Para qué:** Identificar por qué las rutas VPN no se instalan en la RIB ni se propagan a los CEs.

**Resultado Esperado**: Rutas recibidas/advertisadas contadas > 0. Sin prefix-limit exceeded. Next-hop alcanzable con label stack. Sin RIB-failure.

🔬 **Hipótesis Científica**: La sesión MP-BGP entre PEs está Up pero no se intercambian rutas VPNv4/VPNv6 porque los prefijos locales no son redistribuidos desde el protocolo PE-CE hacia MP-BGP, o porque las políticas de exportación (route-maps, RT filters) las descartan antes de ser anunciadas al peer remoto.
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar prefijos del cliente en VRF local del PE origen.
2. Habilitar redistribución PE-CE hacia MP-BGP VPNv4.
3. Revisar policies de exportación y permitir prefijos/comunidades/RT del cliente.
4. Alinear export-RT origen con import-RT destino.
5. Verificar Adj-RIB-Out VPNv4 hacia peer remoto.
6. Confirmar recepción e instalación en VRF destino.


#### Paso `l3vpn_vrf_fwd`: 4. VRF Forwarding / Data Plane (Tier 2)
**Descripción**: **Dónde:** Forwarding plane del PE: CEF/FIB, next-hop resolution, ARP/ND en VRF, y stack de labels MPLS de salida.

**Cómo:** Rutas presentes en "show ip route vrf <name>", pero pings fallan. Contadores de drop en hardware.

**Cuándo:** Tras migraciones de CE, cambios de hardware, o cuando se aplica QoS que descarta por DSCP/EXP.

**Por qué:** FIB incompleta (no programada en hardware), next-hop MAC no resuelto, ACLs en interfaz de salida, o MPLS label stack no generado por LFIB.

**Para qué:** Validar que el data plane pueda entregar tráfico VPN real end-to-end, no solo que las rutas existan en el control plane.

**Resultado Esperado**: CEF/FIB con next-hop válido. MAC/ND resuelto en VRF. Label stack presente para PE-P si aplica. Sin contadores de descarte creciendo.

🔬 **Hipótesis Científica**: El plano de datos de la VRF falla porque el paquete ingresado desde el CE no es clasificado correctamente en la VRF (interfaz no vinculada a VRF), o porque el label de transporte/VPN no se resuelve correctamente en la LFIB del PE egress, provocando que el paquete sea descartado o enrutado por la tabla IP global.
🛠️ **Solución Rápida (Quick Fix)**: 1. Vincular explícitamente interfaz PE-CE a la VRF en ambos PEs.
2. Completar entrada LFIB en PE egress para label VPN.
3. Asegurar ruta de retorno hacia CE en VRF local del PE egress.
4. Verificar label stack (transporte+VPN) según diseño.
5. Limpiar contadores de descarte por 'VRF not found'/'No route to host'.
6. Validar forwarding de paquetes del CE hacia el destino remoto.


### Tecnología: L2VPN Troubleshooting (VPWS / VPLS / PW)
Total de pasos diagnósticos: **7**

#### Paso `l2vpn_start`: 1. Ámbito del problema L2VPN (Tier 1)
**Descripción**: **Dónde:** El problema puede estar en el AC local, en la señalización del PW (LDP/BGP), en el data plane del PW, o en la encapsulación L2.

**Cómo:** CE reporta enlace caído. PW no aparece en estado UP. Tráfico entre sites no pasa aunque los routers estén operativos.

**Cuándo:** Tras reconfiguración de VCID, migración de PE, o cambios de encapsulación en el CE.

**Por qué:** AC down, VCID/PW-type mismatch, MTU inconsistente, MPLS subyacente roto, o encapsulación dot1q/QinQ mal configurada.

**Para qué:** Determinar si la falla es local (AC), de señalización (control plane), o de datos (PW forwarding/MTU).

**Resultado Esperado**: ACs Up, PW en estado UP, MTU coincidente entre extremos. Labels MPLS presentes para el PW.

🔬 **Hipótesis Científica**: La falla de conectividad L2VPN es causada por una sesión de señalización LDP/BGP caída, un VC-ID o FEC mismatch, una interfaz AC no operativa, o una MTU insuficiente en el Attachment Circuit o en el core MPLS.
🛠️ **Solución Rápida (Quick Fix)**: 1. Restablecer sesión de señalización Targeted LDP o BGP L2VPN Established entre PEs.
2. Corregir VC-ID/FEC y encapsulación (Ethernet/VLAN) para que coincidan en ambos PEs.
3. Asegurar que la interfaz AC esté Up/Up con VLAN de servicio correcta.
4. Aumentar MTU del AC y core MPLS para soportar labels y Control Word.
5. Verificar pseudowire Up con labels de VC local/remoto instalados en LFIB.
6. Validar conectividad L2 end-to-end entre sites del cliente.


#### Paso `l2vpn_ac`: 2. Attachment Circuit hacia CE (Tier 1)
**Descripción**: **Dónde:** Interfaz física o lógica (subinterface) hacia el CE en el PE local.

**Cómo:** Interface en Down/Down o errores de input/output creciendo. CE no detecta carrier.

**Cuándo:** Tras cambios de cableado, configuración de subinterfaces, o problemas de óptica/SFP.

**Por qué:** Cable desconectado, SFP fallado, shutdown administrativo, encapsulación L2 mal configurada, o MTU menor al requerido.

**Para qué:** Confirmar que el Attachment Circuit local es sano antes de investigar la señalización remota.

**Resultado Esperado**: Interface UP, sin errores de capa física. Encapsulamiento coincide con CE. MTU del AC >= MTU del PW más overhead.


#### Paso `l2vpn_encap`: 2.A Troubleshooting de Encapsulación L2 (dot1q / QinQ / 802.1ad) (Tier 2)
**Descripción**: **Dónde:** En la subinterfaz del PE y en el CE, donde se define el tipo de encapsulación L2.

**Cómo:** PW type mismatch (Ethernet vs VLAN) hace que la señalización sea rechazada. Frames con doble tag descartados por TPID inesperado.

**Cuándo:** Al migrar de untagged a dot1q, o al implementar QinQ/802.1ad para servicios multi-tenant.

**Por qué:** Si un extremo espera raw Ethernet y el otro envía tagged frames, los tags se interpretan como payload corrupto. En QinQ, TPID 0x88a8 vs 0x8100 causa descarte.

**Para qué:** Asegurar simetría de encapsulación para que el PW acepte y transporte correctamente las tramas del CE.

**Resultado Esperado**: PW type (Ethernet/VLAN) coincide en ambos PEs. dot1q/QinQ/802.1ad configurado simétricamente. TPID correcto para QinQ.


#### Paso `l2vpn_sig`: 3. Señalización de Pseudowire (Tier 1)
**Descripción**: **Dónde:** Sesiones LDP entre PEs, bindings de VCID, y estado del PW en el plano de control.

**Cómo:** "show l2circuit connections" muestra VC en estado Down, o "show ldp database" no tiene binding para la VCID.

**Cuándo:** Después de reconfigurar la VCID, cambiar el tipo de PW, o cuando falla el vecino LDP.

**Por qué:** VCID diferente en cada extremo, PW type mismatch, transport-address LDP no alcanzable, o MPLS subyacente roto.

**Para qué:** Restaurar la señalización del PW para que el data plane pueda establecer el túnel L2.

**Resultado Esperado**: Bindings para VCID presentes en ambos PEs. PW status local y remoto 0x00000000. Vecino LDP alcanzable y Operational.


#### Paso `l2vpn_vcid`: 3.1 VCID / PW Type Mismatch (Tier 2)
**Descripción**: **Dónde:** Configuración del PW en ambos PEs: VCID, PW type (Ethernet/VLAN), y MTU.

**Cómo:** Señalización rechazada con "PW status: MTU mismatch" o "PW type mismatch". PW no establece.

**Cuándo:** Tras copiar configuración de un PE a otro sin ajustar VCID, o cuando se cambia el tipo de servicio.

**Por qué:** La VCID actúa como identificador del circuito; si difiere, el PW no se vincula. El PW type (Ethernet=5, VLAN=4) debe coincidir para interpretar correctamente las tramas.

**Para qué:** Corregir la simetría de configuración del PW para permitir el establecimiento de la conexión L2.

**Resultado Esperado**: VCID idéntico en ambos extremos. PW-type idéntico. MTU >= valor esperado en ambos lados (incluyendo overhead de tags).


#### Paso `l2vpn_pw_down`: 3.2 PW Status bits o MPLS subyacente (Tier 2)
**Descripción**: **Dónde:** Status bits del PW y estado MPLS subyacente. Cada bit de status indica una causa específica (RFC 4447).

**Cómo:** PW local Up pero remoto Down. Bits de status como 0x00000001 (PW not forwarding), 0x00000002 (local AC fault).

**Cuándo:** Cuando el AC remoto cae, o cuando hay una falla en el path MPLS (LDP/RSVP caído).

**Por qué:** Los status bits propagan el estado del AC remoto. Si el AC remoto está caído, el PW local se notifica y puede dejar de forwardar para evitar blackholing.

**Para qué:** Interpretar los status bits para saber si la falla es local, remota, o del transporte MPLS subyacente.

**Resultado Esperado**: Status 0x00000000 en ambos extremos. Si no, mapear bits a causa raíz según RFC 4447 (AC fault, PW not forwarding, etc.).


#### Paso `l2vpn_data`: 4. Plano de Datos del PW (Tier 2)
**Descripción**: **Dónde:** Forwarding plane del PW: MTU de servicio, sequencing, CC/CV OAM, y posibles policers en el path MPLS.

**Cómo:** PW Up pero tráfico no pasa. Pings entre CEs fallan. Contadores de drop en el PW.

**Cuándo:** Tras cambios de MTU en el core, activación de sequencing (que puede descartar frames desordenados), o aplicación de QoS en PE-P.

**Por qué:** MTU de servicio inconsistente (ej. AC en un extremo soporta 1500 pero el otro 1496). Sequencing habilitado solo en un lado. Policer en el path descarta frames grandes.

**Para qué:** Verificar que el PW pueda transportar tráfico de datos real sin fragmentación o descarte silencioso.

**Resultado Esperado**: MTU de servicio consistente en ambos extremos. Sin contadores de drop de PW. Sequencing simétrico si está habilitado. OAM CC/CV OK si aplica.


### Tecnología: EVPN Troubleshooting
Total de pasos diagnósticos: **11**

#### Paso `evpn_start`: 1. Ámbito del problema EVPN (Tier 1)
**Descripción**: **Dónde:** Problemas en el control plane BGP EVPN, aprendizaje de MACs, multihoming, BUM flooding, o encapsulación AC.

**Cómo:** MACs no se sincronizan entre PEs. BUM traffic no llega a todos los hosts. DF election inconsistente en CE multihomed.

**Cuándo:** Tras activar un nuevo EVI, migrar un CE a otro PE, o cambiar la configuración de route-targets.

**Por qué:** BGP EVPN AF no negociada, RT mismatch, ESI inconsistente en multihoming, o ingress replication list incompleta.

**Para qué:** Clasificar el síntoma para enfocar el troubleshooting en BGP EVPN, MAC learning, DF election, o encapsulación.

**Resultado Esperado**: BGP EVPN session Established. EVPN address-family activa. EVI s configurados y activos.

🔬 **Hipótesis Científica**: La falla en EVPN (MAC/IP no aprendidas o tráfico BUM no replicado) es causada por una falla en el underlay IP/MPLS, una adyacencia BGP EVPN no establecida, o un error en la configuración de la MAC-VRF/bridge domain.
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar underlay IP/MPLS entre VTEPs/PEs; corregir rutas IGP si hay falla.
2. Asegurar que BGP EVPN (AFI 25/SAFI 70) esté en Established y que las policies permitan comunidades extendidas.
3. Verificar recepción de rutas EVPN Tipo 2 (MAC/IP) en ambos PEs.
4. Confirmar que MAC-VRF/bridge domain tengan RD/RT correctos y VLANs asociadas.
5. En multihoming: verificar ESI consistency y DF election; resolver conflictos de ESI.

#### Paso `evpn_bgp`: 2. BGP EVPN Address-Family (Tier 1)
**Descripción**: **Dónde:** Sesiones BGP entre PEs (o RRs), address-family EVPN (SAFI 70).

**Cómo:** Peers en Established pero sin capacidad EVPN negociada. "show bgp neighbor" no muestra AFI/SAFI 25/70.

**Cuándo:** Tras agregar un nuevo peer EVPN, o cuando se migra de un RR que no soporta EVPN.

**Por qué:** Un extremo no tiene "address-family l2vpn evpn" activa. Update-source inalcanzable. Filtro de neighbor que bloquea la capability.

**Para qué:** Garantizar que el control plane EVPN esté operativo para distribuir rutas tipo 1-5.

**Resultado Esperado**: BGP state Established, AFI/SAFI: 25/70 o 70/70 según implementación. Sin prefix-limit exceeded. Capacidades EVPN visibles.

🔬 **Hipótesis Científica**: La sesión BGP EVPN no se establece o no intercambia rutas porque la address-family EVPN (AFI/SAFI 25/70) no está activada bajo el peer, existe un mismatch de capabilities en el OPEN message, o el underlay IP/MPLS entre PEs/VTEPs está roto, impidiendo el transporte de la sesión TCP 179.
🛠️ **Solución Rápida (Quick Fix)**: 1. Activar address family EVPN (AFI/SAFI 25/70) bajo el neighbor en ambos PEs/VTEPs.
2. Verificar capabilities exchange en OPEN message.
3. Establecer sesión BGP base TCP 179 entre loopbacks/interfaces de origen.
4. Restaurar underlay IP/MPLS entre loopbacks con MTU adecuado.
5. Eliminar policies BGP que filtren familia EVPN o capabilities.
6. Confirmar sesión BGP EVPN Established.


#### Paso `evpn_routes`: 3. Rutas EVPN no propagadas (Tier 2)
**Descripción**: **Dónde:** Tablas BGP EVPN (evpn.evpn.0) y verificación de communities RT.

**Cómo:** "show bgp l2vpn evpn" no muestra rutas esperadas, o las rutas tienen RIB-failure/not-best por next-hop.

**Cuándo:** Cuando se agrega un nuevo host, o después de cambiar RTs o policies de import/export.

**Por qué:** RT export del origen no coincide con RT import del destino. Next-hop inalcanzable (falta MPLS/VXLAN subyacente). ESI diferente rompe RT-1.

**Para qué:** Asegurar que las rutas EVPN se propaguen e instalen correctamente en todos los PEs del dominio.

**Resultado Esperado**: Rutas EVPN visibles con communities RT correctas. Sin RIB-failure o not-best por nexthop. Next-hop VTEP/MPLS alcanzable.

🔬 **Hipótesis Científica**: Las rutas EVPN Tipo 1/2/3/5 no se propagan entre PEs/VTEPs porque los Route Targets no coinciden, las políticas de BGP filtran las NLRI EVPN, o el next-hop de las rutas EVPN no es alcanzable en el underlay IP/MPLS.
🛠️ **Solución Rápida (Quick Fix)**: 1. Alinear export-RT origen con import-RT destino para cada EVI.
2. Revisar policies BGP para no descartar NLRI EVPN ni comunidades RT.
3. Asegurar Next-Hop de rutas EVPN alcanzable en underlay.
4. Verificar rutas EVPN Tipo 1/2/3/5 en EVPN RIB local.
5. Confirmar anuncio/recepción con 'advertised-routes'/'received-routes'.
6. Validar forwarding de MACs/prefijos entre PEs.


#### Paso `evpn_mac`: 4. Aprendizaje y anuncio de MACs (Tier 2)
**Descripción**: **Dónde:** Aprendizaje local del CE (bridge MAC table) y anuncio vía RT-2 en BGP EVPN.

**Cómo:** MAC local no aparece en "show evpn database". MAC remota no recibida por BGP.

**Cuándo:** Tras mover un host de un CE a otro, o cuando un host no genera tráfico (aging de MAC).

**Por qué:** AC no está en el bridge-domain/EVI correcto. EVPN no está habilitado en la interfaz. Policy de export bloquea RT-2.

**Para qué:** Verificar que el PE aprende MACs localmente y las anuncia correctamente por EVPN para el learning remoto.

**Resultado Esperado**: MACs locales en evpn database y MACs remotas recibidas por BGP. Next-hop VTEP/MPLS alcanzable. Sin duplicados.

🔬 **Hipótesis Científica**: Las MACs del cliente no se aprenden localmente o no se anuncian remotamente porque el bridge-domain/EVI local no está asociado a la VLAN correcta, las rutas EVPN Tipo 2 son filtradas por políticas de exportación/importación, o el mecanismo de aprendizaje de MACs está deshabilitado o saturado en el PE/VTEP.
🛠️ **Solución Rápida (Quick Fix)**: 1. Mapear bridge-domain/VLAN local correctamente a EVI y asegurar AC Up/Up.
2. Verificar aprendizaje de MAC local en tabla de MACs.
3. Revisar policies BGP para permitir anuncio/recepción de rutas Tipo 2.
4. Ajustar límite de MACs por bridge-domain si se alcanzó el máximo.
5. Confirmar ruta EVPN Tipo 2 en EVPN RIB con MAC/IP/next-hop correctos.
6. Validar reachability L2 del cliente remoto.


#### Paso `evpn_ac`: 4.1 Attachment Circuit / Bridge Domain local (Tier 1)
**Descripción**: **Dónde:** Interfaz hacia CE, bridge-domain/EVI local, y ESI (para multihoming).

**Cómo:** Interfaz Up pero MACs no se aprenden. ESI inconsistente entre PEs del mismo segmento.

**Cuándo:** Tras reconfigurar el bridge-domain, cambiar el ESI, o migrar el CE.

**Por qué:** AC no mapeada al EVI correcto. VLAN normalization descarta frames. ESI diferente rompe DF election y aliasing.

**Para qué:** Confirmar que el Attachment Circuit está correctamente integrado al dominio EVPN.

**Resultado Esperado**: AC mapeada al EVI/BD correcto. ESI consistente en todos los PEs del segmento. Encapsulación coincide con CE.

🔬 **Hipótesis Científica**: El Attachment Circuit (AC) local no transporta tráfico del cliente al bridge-domain/EVI porque la interfaz física está caída, la VLAN configurada en el AC no coincide con la del cliente (dot1q mismatch), o el encapsulado no es compatible con el bridge-domain (untagged vs tagged).
🛠️ **Solución Rápida (Quick Fix)**: 1. Levantar interfaz AC y resolver errores físicos.
2. Alinear VLAN/encapsulación del AC con tráfico del cliente.
3. Asociar bridge-domain/EVI con RD/RT correctos al AC.
4. Eliminar storm-control/ACLs que descarten tráfico del cliente.
5. Limpiar contadores de errores (CRC, runts, giants).
6. Validar que tráfico del cliente ingrese al bridge-domain.


#### Paso `evpn_df`: 5. Designated Forwarder (DF) Election (Tier 3)
**Descripción**: **Dónde:** Elección de Designated Forwarder en CE multihomed activo-activo EVPN.

**Cómo:** Múltiples DFs para el mismo ESI (BUM duplicado) o ningún DF (BUM perdido). "show evpn ethernet-segment" muestra conflicto.

**Cuándo:** Tras agregar o quitar un PE del multihoming, o cuando cambia la topología L2.

**Por qué:** Algoritmo DF depende del ESI y del número de PEs. Si los PEs no ven el mismo número de participantes, la elección diverge.

**Para qué:** Evitar flooding duplicado o ausente de BUM traffic en entornos multihomed.

**Resultado Esperado**: Un único DF por ESI. Non-DFs en estado backup. Sin DF conflicts. BUM fluye correctamente.

🔬 **Hipótesis Científica**: El DF election en un segmento multihomed EVPN falla o produce un DF incorrecto debido a un ESI duplicado en la red, una prioridad de DF desajustada entre los PEs multihomed, o un número inconsistente de PEs por Ethernet Segment.
🛠️ **Solución Rápida (Quick Fix)**: 1. Asegurar ESI idéntico y único en todos los PEs multihomed del segmento.
2. Alinear prioridad de DF según diseño.
3. Resolver conflictos de DF election ('show evpn instance df-election').
4. Restaurar underlay EVPN/BGP para todos los PEs del Ethernet Segment.
5. Revisar logs de 'DF election conflict'/'ESI mismatch'.
6. Confirmar un único DF activo por EVI/ESI.


#### Paso `evpn_esi`: 5.1 ESI Consistency (Tier 3)
**Descripción**: **Dónde:** Configuración de Ethernet Segment Identifier en todos los PEs multihomed al mismo CE.

**Cómo:** ESI diferente en PEs que deberían compartir el mismo segmento. Aliasing y DF election fallan.

**Cuándo:** Al provisionar un nuevo PE para multihoming, o al copiar configuración sin ajustar ESI.

**Por qué:** El ESI identifica unívocamente el segmento L2. Si difiere, cada PE lo trata como segmento distinto, rompiendo la sincronización de MACs y BUM.

**Para qué:** Garantizar consistencia del ESI para que EVPN opere multihoming correctamente.

**Resultado Esperado**: ESI idéntico en todos los PEs del segmento. Tipo ESI apropiado (0 = manual, 1 = LACP-based, etc.).

🔬 **Hipótesis Científica**: La inconsistencia del ESI (Ethernet Segment Identifier) entre PEs multihomed causa loops de tráfico BUM o un DF election inestable, resultando en aprendizaje de MACs inestable, duplicación de tramas, o descarte de tráfico cuando un PE cambia de estado forwarding/no-forwarding.
🛠️ **Solución Rápida (Quick Fix)**: 1. Corregir ESI para que sea idéntico en todos los PEs del mismo Ethernet Segment.
2. Asegurar unicidad del ESI en todo el dominio EVPN.
3. Estabilizar sincronización de MACs eliminando loops o flapping.
4. Verificar rutas EVPN Tipo 1 con ESI consistente.
5. Investigar y resolver MAC moves recurrentes.
6. Validar DF election estable tras corregir ESI.


#### Paso `evpn_bum`: 6. BUM Flooding (Broadcast, Unknown, Multicast) (Tier 2)
**Descripción**: **Dónde:** Flooding de Broadcast, Unknown unicast, y Multicast en EVPN. Puede usar ingress replication o multicast P2MP.

**Cómo:** ARP requests no llegan a hosts remotos. BUM traffic solo se ve localmente.

**Cuándo:** Tras agregar un nuevo VTEP/PE, o cuando se migra de multicast a ingress replication.

**Por qué:** Falta RT-3 (Inclusive Multicast) en BGP EVPN. Flood list no contiene todos los PEs/VTEPs. IGMP/PIM en underlay falla si usa multicast.

**Para qué:** Asegurar que el BUM traffic alcance todos los hosts del dominio de bridging EVPN.

**Resultado Esperado**: RT-3 presentes por cada EVI. Flood list contiene todos los PEs/VTEPs remotos. Si multicast, IGMP joins y PIM neighbors OK.

🔬 **Hipótesis Científica**: El tráfico BUM (Broadcast, Unknown unicast, Multicast) no se replica correctamente porque el mecanismo de flooding (ingress replication, multicast core subyacente, o EVPN Tipo 3 Inclusive Multicast Ethernet Tag) no está operativo, o porque el Designated Forwarder no está reenviando BUM hacia el core EVPN.
🛠️ **Solución Rápida (Quick Fix)**: 1. Configurar mecanismo de replicación BUM (ingress replication lista completa o multicast core funcional).
2. Resolver DF election con un único DF activo.
3. Asegurar rutas EVPN Tipo 3 presentes y next-hop alcanzable.
4. Permitir transporte de BUM en underlay (sin ACLs/filtros).
5. Revisar contadores de descarte BUM y buffers.
6. Validar replicación de broadcast/desconocido/multicast entre PEs.


#### Paso `evpn_rt5`: 7. Inter-Subnet Routing (RT-5 / IP Prefix) (Tier 3)
**Descripción**: **Dónde:** Inter-subnet routing en EVPN con rutas IP Prefix (RT-5). Requiere IRB/SVI/Anycast GW.

**Cómo:** Hosts en diferentes subnets no se comunican. "show evpn ip-prefix-database" vacío.

**Cuándo:** Al habilitar routing L3 dentro de EVPN, o al migrar de L2VPN puro a EVPN con IRB.

**Por qué:** Falta VRF con L3VNI (VXLAN) o MPLS label para el prefix. Gateway (IRB/SVI) no configurado. RTs no coinciden entre VRF y EVI.

**Para qué:** Permitir que EVPN distribuya no solo MACs sino también prefijos IP para el routing inter-subnet.

**Resultado Esperado**: RT-5 presentes con next-hop alcanzable (Anycast GW o PE). VRF routing table poblada. L3VNI/MPLS label válido.

🔬 **Hipótesis Científica**: El routing inter-subnet en EVPN no funciona porque las rutas EVPN Tipo 5 (IP Prefix) no son generadas o no son importadas debido a un VRF mismatch, un next-hop inalcanzable en el underlay, o políticas de Route-Target que descartan los prefijos IP antes de instalarlos en la RIB de la VRF.
🛠️ **Solución Rápida (Quick Fix)**: 1. Generar rutas EVPN Tipo 5 para prefijos IP del cliente (redistribución IP->EVPN).
2. Confirmar recepción de rutas Tipo 5 en PEs remotos.
3. Asegurar Next-Hop alcanzable vía underlay IGP/MPLS.
4. Alinear RTs de rutas Tipo 5 con importación de VRF destino.
5. Verificar instalación de prefijos IP en RIB de VRF destino.
6. Validar routing inter-subnet entre segmentos EVPN.


#### Paso `evpn_rt`: Políticas de Route-Target EVPN (Tier 3)
**Descripción**: **Dónde:** Políticas de route-target para import/export de rutas EVPN por EVI/VRF.

**Cómo:** Rutas EVPN presentes en BGP pero no instaladas en la EVI/VRF local.

**Cuándo:** Tras cambiar RTs para segmentar dominios, o al fusionar/evolucionar un diseño.

**Por qué:** Cada EVI/BD debe tener RTs coincidentes entre PEs. Si el RT export del origen no coincide con el RT import del destino, la ruta se descarta silenciosamente.

**Para qué:** Validar que los RTs definan correctamente el dominio de bridging/routing EVPN.

**Resultado Esperado**: RT import en cada PE coincide con RT export del PE origen. Extended communities aplicadas correctamente a cada EVI.

🔬 **Hipótesis Científica**: Las políticas de Route-Target en EVPN descartan silenciosamente rutas Tipo 1/2/3/5 porque el RT de exportación en el origen no coincide con el RT de importación en el destino, o un route-map aplica un RT inesperado que aísla el segmento EVPN.
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar export-RT e import-RT carácter por carácter en cada EVI.
2. Asegurar que export origen == import destino.
3. Revisar route-maps para no modificar ni descartar comunidades RT.
4. Validar atributo communities extendidas en rutas EVPN recibidas.
5. Corregir RTs duplicados o mal formados.
6. Confirmar importación correcta a MAC-VRF/VRF destino.


#### Paso `evpn_encap`: 8. Encapsulación L2 en AC EVPN (dot1q / QinQ / 802.1ad) (Tier 2)
**Descripción**: **Dónde:** AC hacia CE con dot1q, QinQ, o 802.1ad. Service Interface Type en EVPN (VLAN-based, VLAN-aware, Port-based).

**Cómo:** Frames descartados en el PE. EVI no mapea VLANs correctamente. QinQ outer tag mal interpretado.

**Cuándo:** Al migrar de L2VPN tradicional a EVPN, o al soportar múltiples VLANs en un mismo EVI.

**Por qué:** VLAN-based requiere 1:1 mapping. VLAN-aware permite múltiples VLANs en un EVI. Si el CE envía QinQ pero el PE espera dot1q, el frame se descarta.

**Para qué:** Asegurar que la encapsulación L2 del CE coincida con la configuración del PE y el tipo de servicio EVPN.

**Resultado Esperado**: AC encapsulación coincide con CE. VLAN-based/VLAN-aware/Port-based consistente entre PEs. TPID correcto para QinQ (0x88a8).

🔬 **Hipótesis Científica**: El tráfico del cliente no ingresa correctamente al EVPN porque el encapsulado del Attachment Circuit (dot1q, qinq, untagged) no coincide con la configuración del bridge-domain o del service instance, causando que las tramas sean descartadas o clasificadas en un segmento incorrecto.
🛠️ **Solución Rápida (Quick Fix)**: 1. Alinear encapsulado del AC (dot1q/qinq/untagged) con tráfico del cliente.
2. Verificar que bridge-domain/service instance clasifique según tag recibido.
3. Asegurar coherencia de encapsulado del core (VXLAN/MPLS) entre PEs.
4. Coincidir VNI/label de EVPN en todos los VTEPs/PEs del segmento.
5. Limpiar contadores de 'encapsulation mismatch'/'unknown tag'.
6. Validar que tramas del cliente se conmuten correctamente.


### Tecnología: VXLAN Troubleshooting
Total de pasos diagnósticos: **5**

#### Paso `vxlan_start`: 1. Ámbito del problema VXLAN (Tier 1)
**Descripción**: **Dónde:** Problemas en VTEP reachability, VNI mapping, BUM flooding, gateway integration, o encapsulación AC.

**Cómo:** Hosts no se ven entre VTEPs. MACs no se aprenden. BUM no inunda. Gateway Anycast inconsistente.

**Cuándo:** Tras agregar un nuevo VTEP, cambiar el underlay, o migrar de multicast a EVPN ingress replication.

**Por qué:** VTEP no alcanzable (underlay IP/UDP bloqueado). VNI no mapeado a VLAN/BD. BUM method incorrecto. EVPN no sincroniza MACs.

**Para qué:** Determinar si la falla está en underlay, control plane (EVPN), o data plane (VNI/BUM/AC).

**Resultado Esperado**: VTEP source interfaz UP, VNI state Up, peers alcanzables. Underlay routing sano. MACs sincronizadas si usa EVPN.

🔬 **Hipótesis Científica**: La falla de conectividad L2 sobre VXLAN es causada por una falla en el underlay IP (no hay reachability entre VTEPs), una configuración incorrecta de la interfaz NVE (VNI, VLAN mapping, o source IP), o un mecanismo de replicación BUM (multicast/HER) no operativo.
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar conectividad IP entre loopbacks de VTEPs con ping >= 1550 bytes + DF. Corregir MTU en underlay.
2. Asegurar que la interfaz NVE esté Up y que la source IP sea la loopback correcta.
3. Confirmar que el mapeo VLAN-to-VNI sea idéntico en todos los VTEPs del segmento.
4. Verificar que el grupo multicast para BUM esté funcional o que la tabla HER esté poblada.
5. Inspeccionar la tabla de MACs para confirmar que las MACs remotas apuntan al VTEP correcto.

#### Paso `vxlan_underlay`: 2. Underlay / VTEP Reachability (Tier 1)
**Descripción**: **Dónde:** Red underlay IP (IGP/BGP) entre VTEPs, y conectividad UDP/4789.

**Cómo:** Ping al VTEP remoto falla. "show nve peers" no muestra peers. UDP 4789 bloqueado por firewall.

**Cuándo:** Tras cambios de routing underlay, aplicación de ACLs, o reconvergencia IGP.

**Por qué:** VXLAN requiere IP unicast entre VTEPs. Si el underlay no tiene ruta, o si UDP 4789 está filtrado, los VTEPs no se descubren.

**Para qué:** Garantizar que el transporte IP subyacente permita el tráfico VXLAN entre todos los VTEPs.

**Resultado Esperado**: Ruta IP válida al VTEP remoto. Ping desde source VTEP IP exitoso. Sin firewall bloqueando UDP 4789. ECMP balanceado.


#### Paso `vxlan_vni`: 3. VNI y Bridge-Domain mapping (Tier 2)
**Descripción**: **Dónde:** Mapeo de VNI a VLAN/Bridge-Domain en cada VTEP.

**Cómo:** Hosts en la misma VLAN pero diferentes VTEPs no se comunican. "show nve vni" muestra VNI missing o Down.

**Cuándo:** Tras agregar una nueva VLAN/VNI, o reconfigurar el mapping.

**Por qué:** Cada VNI debe mapear al mismo BD/VLAN en todos los VTEPs. Discrepancias causan blackholing o flooding incorrecto.

**Para qué:** Validar que el segmento L2 (VLAN) esté correctamente asociado al segmento VXLAN (VNI) en cada VTEP.

**Resultado Esperado**: VNI presente y activo en todos los VTEPs. BD/VLAN membership coincide en ambos extremos. Sin VNI duplicados o missing.


#### Paso `vxlan_bum`: 4. BUM en VXLAN (Tier 2)
**Descripción**: **Dónde:** Mecanismo de BUM en VXLAN: herencia multicast, ingress replication list, o head-end replication.

**Cómo:** ARP requests no llegan a hosts en otros VTEPs. Broadcast no se inunda.

**Cuándo:** Tras cambiar el método de BUM, agregar/quitar VTEPs, o problemas de underlay multicast.

**Por qué:** Si se usa multicast, IGMP/PIM deben funcionar en el underlay. Si se usa ingress replication, la lista debe contener todos los VTEPs remotos.

**Para qué:** Asegurar que el BUM traffic alcance todos los hosts del segmento VXLAN.

**Resultado Esperado**: Lista de replicación contiene todos los VTEPs. Si multicast, IGMP joins y PIM neighbors OK. ARP/broadcast end-to-end funciona.


#### Paso `vxlan_encap`: 5. Encapsulación L2 en AC VXLAN (dot1q / QinQ / 802.1ad) (Tier 2)
**Descripción**: **Dónde:** AC hacia CE en el VTEP, con dot1q o QinQ.

**Cómo:** Frames descartados en el VTEP. VLAN no mapeada a VNI. QinQ outer tag causa descarte.

**Cuándo:** Al conectar un nuevo CE con QinQ, o al migrar VLANs entre VNIs.

**Por qué:** El mapeo VLAN-VNI debe ser consistente. Si el CE envía double-tag pero el VTEP no maneja QinQ, los frames se pierden.

**Para qué:** Validar que la encapsulación L2 del CE sea compatible con la configuración del VTEP antes de encapsular en VXLAN.

**Resultado Esperado**: VLAN/VNI mapeo consistente. dot1q o QinQ simétrico entre CE y VTEP. TPID 0x88a8 para 802.1ad. Outer tag mapeado a VNI.


### Tecnología: OSPF Troubleshooting
Total de pasos diagnósticos: **8**

#### Paso `ospf_start`: 1. Ámbito del problema OSPF (Tier 1)
**Descripción**: **Dónde:** Problemas en vecindades OSPF, base de datos, áreas, redistribución, autenticación, o rendimiento.

**Cómo:** Vecinos caídos, rutas ausentes, alta CPU por SPF recalculaciones, o autenticación fallando.

**Cuándo:** Tras cambios de área, upgrades, o aplicación de nuevas políticas de redistribución.

**Por qué:** Requisitos de adjacency no cumplidos, LSA partitioning, redistribución con loops, o timers/MTU/auth mismatch.

**Para qué:** Clasificar el síntoma para enfocar el troubleshooting en vecindades, database, áreas, policies, o rendimiento.

**Resultado Esperado**: Neighbors FULL/DR/BDR. Interfaces en correcta area. Sin contadores de LSA retransmite creciendo. CPU estable.

🔬 **Hipótesis Científica**: La falla de enrutamiento OSPF es causada por una adyacencia que no alcanza el estado Full debido a mismatch de parámetros de área, MTU de interfaz, ID de router duplicado, o interfaces configuradas como pasivas.
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar que las interfaces estén en el área OSPF correcta y no marcadas como passive.
2. Asegurar que la MTU coincida en ambos extremos del enlace (mismatch congela en ExStart/Exchange).
3. Sincronizar timers Hello/Dead (10/40 broadcast, 30/120 NBMA).
4. Verificar que el Router-ID sea único en todo el dominio; corregir si está duplicado.
5. Comparar LSDB entre routers para confirmar sincronización; reparar particiones de área si aplica.

#### Paso `ospf_neighbor`: 2. Vecindades OSPF caídas (Tier 1)
**Descripción**: **Dónde:** Interfaces OSPF y sesiones de vecindad entre routers.

**Cómo:** Vecino stuck en ExStart, 2-Way, o Init. No pasa a Full.

**Cuándo:** Tras cambios de configuración, fallas de enlace, o aplicación de autenticación.

**Por qué:** ExStart suele indicar MTU mismatch. 2-Way puede ser normal en broadcast si no hay DR/BDR. Init indica que no recibe Hellos (unidireccional).

**Para qué:** Diagnosticar por qué la adjacency OSPF no se establece o se mantiene estable.

**Resultado Esperado**: Timers coinciden. MTU igual en ambos lados. Router-ID único. Auth coincide. Network type compatible.

🔬 **Hipótesis Científica**: Las adyacencias OSPF no se establecen o caen porque existe un mismatch de área, MTU de interfaz, timers Hello/Dead, Router-ID duplicado, o la interfaz está marcada como pasiva, impidiendo el intercambio de Hellos y la sincronización de LSDB.
🛠️ **Solución Rápida (Quick Fix)**: 1. Asignar interfaces al área OSPF correcta y quitar passive-interface.
2. Igualar MTU en ambos extremos del enlace.
3. Sincronizar timers Hello/Dead.
4. Corregir Router-ID duplicado.
5. Resolver particiones de área para sincronizar LSDB.
6. Confirmar adyacencias en estado Full.


#### Paso `ospf_auth`: 2.A Autenticación, MTU, Timers y Hello/Dead (Tier 2)
**Descripción**: **Dónde:** Configuración de autenticación, MTU, Hello/Dead timers, y network type en interfaces OSPF.

**Cómo:** Vecinos caídos con mensajes de auth error. Vecinos no se descubren. MTU mismatch detectado en logs.

**Cuándo:** Tras aplicar nuevas claves de autenticación, cambiar timers, o migrar de una interface a otra.

**Por qué:** OSPF requiere exactamente los mismos parámetros en ambos extremos: auth type, key, Hello/Dead, MTU, area, stub flag, y network type.

**Para qué:** Verificar que todos los parámetros de interfaz sean simétricos para permitir la formación de adjacencies.

**Resultado Esperado**: Auth type y key coinciden. MTU idéntica. Hello/Dead timers iguales. Network type compatible (broadcast vs p2p).

🔬 **Hipótesis Científica**: La adyacencia OSPF se congela o cae debido a un mismatch de autenticación (tipo/key), MTU de interfaz desajustada, o timers Hello/Dead que no coinciden en ambos extremos, impidiendo la transición de vecindad a estado Full.
🛠️ **Solución Rápida (Quick Fix)**: 1. Alinear tipo y clave de autenticación en ambos vecinos.
2. Igualar MTU en ambos extremos.
3. Sincronizar timers Hello/Dead.
4. Coincidir tipo de red (broadcast/P2P/NBMA).
5. Revisar logs de 'Auth mismatch'/'MTU mismatch'/'Timer mismatch'.
6. Confirmar transición a estado Full.


#### Paso `ospf_database`: 3. Base de datos OSPF y RIB (Tier 2)
**Descripción**: **Dónde:** LSA database, SPF tree, y RIB.

**Cómo:** Rutas ausentes aunque las LSAs existen. "show ip ospf database" incompleta. Rutas en database pero no en forwarding.

**Cuándo:** Tras particionamiento de área, cambios de ABR/ASBR, o redistribución.

**Por qué:** LSA Type-3/4/5/7 pueden faltar si el ABR/ASBR falla. Next-hop inalcanzable impide instalar en RIB. Administrative distance mayor de otro protocolo.

**Para qué:** Asegurar que la base de datos OSPF esté completa y que las rutas se instalen correctamente en la RIB.

**Resultado Esperado**: LSAs presentes para todas las áreas. Rutas OSPF en RIB con next-hop válido. Sin partitioning de área.

🔬 **Hipótesis Científica**: La LSDB está desincronizada o contiene LSAs corruptos/faltantes, lo que resulta en rutas OSPF no instaladas en la RIB o en rutas subóptimas debido a una partición de área o un Area Border Router mal configurado.
🛠️ **Solución Rápida (Quick Fix)**: 1. Comparar LSDB entre routers y resolver inconsistencias.
2. Asegurar presencia de LSAs Tipo 1/2/3 según corresponda.
3. Investigar LSA sequence 0x80000001 recurrente (estabilizar originador).
4. Verificar que ABRs generen resúmenes inter-área sin filtros incorrectos.
5. Confirmar instalación de rutas OSPF en RIB.
6. Validar sincronización completa de LSDB.


#### Paso `ospf_area`: 4. Problemas de Área (Stub / NSSA / Virtual-Link) (Tier 2)
**Descripción**: **Dónde:** Áreas OSPF, ABRs, NSSA/Stub translation, y virtual-links.

**Cómo:** Rutas externas no llegan a áreas stub. NSSA no traduce Type-7 a Type-5. Virtual-link down.

**Cuándo:** Tras reconfigurar áreas, agregar NSSA, o romper conectividad al área 0.

**Por qué:** Stub no permite Type-5. NSSA requiere translator election (ABR con mayor RID). Virtual-link depende de reachability a área 0.

**Para qué:** Garantizar que el diseño de áreas funcione correctamente y que las rutas externas se propagen según lo previsto.

**Resultado Esperado**: ABR conectado a area 0. NSSA translator election correcto. Virtual-link UP si aplica. Stub flag consistente.

🔬 **Hipótesis Científica**: La conectividad entre áreas OSPF falla o la LSDB muestra rutas inesperadas porque un área está mal declarada (Stub/NSSA/Transit), un virtual-link está roto, o un ABR no genera resúmenes correctos entre áreas backbone y no-backbone.
🛠️ **Solución Rápida (Quick Fix)**: 1. Asignar cada interfaz al área correcta.
2. Asegurar que ABRs tengan interfaz en área 0.
3. Consistir tipo de área (Stub/NSSA/Total Stub) en todos los routers del área.
4. Restaurar virtual-links y conectividad del área de tránsito.
5. Revisar resúmenes inter-área y filtrado de Tipo 5/7.
6. Confirmar rutas entre áreas según diseño.


#### Paso `ospf_redist`: 5. Redistribución en OSPF (Tier 2)
**Descripción**: **Dónde:** Redistribución de BGP/estático/IS-IS en OSPF, y generación de LSAs Type-5/7.

**Cómo:** Rutas externas no aparecen. Métricas incorrectas (E1 vs E2). Loops de routing.

**Cuándo:** Tras agregar nueva redistribución, o cambiar route-maps/tagging.

**Por qué:** Redistribución requiere explícito "redistribute" y cuidado con loops. E1 suma costo interno; E2 no. Tag puede usarse para prevenir loops.

**Para qué:** Asegurar que las rutas externas se inyecten correctamente sin crear loops ni blackholes.

**Resultado Esperado**: Rutas externas (O E1/E2) presentes. Sin loops. Metric-type correcta. Forwarding-address válido. Tag aplicado si aplica.

🔬 **Hipótesis Científica**: Los prefijos externos no se propagan correctamente porque la redistribución está mal configurada (falta de métrica o tipo E1/E2), o porque los LSA Type 5/7 son filtrados por un ABR o por una área NSSA mal convertida, impidiendo que las rutas externas lleguen a todos los routers del dominio OSPF.
🛠️ **Solución Rápida (Quick Fix)**: 1. Configurar métrica y tipo E1/E2 explícitos en redistribución.
2. Verificar prefijos redistribuidos como LSAs Tipo 5 en área 0.
3. Eliminar filtros de ABR que bloqueen LSAs Tipo 5.
4. En NSSA, asegurar traducción Tipo 7 a Tipo 5 en ABR NSSA.
5. Confirmar instalación de rutas externas en RIB.
6. Validar propagación end-to-end de prefijos externos.


#### Paso `ospf_spf`: 6. SPF Tree, CPU alta y Database Overflow (Tier 3)
**Descripción**: **Dónde:** SPF process, CPU del router, y LSA database size.

**Cómo:** CPU alta repetidamente. "show ip ospf statistics" muestra SPF runs frecuentes. Database overflow warnings.

**Cuándo:** Durante eventos de red (flapping de links), o en redes muy grandes sin summarization.

**Por qué:** Cada cambio de estado de interfaz o LSA nueva trigger SPF. En redes grandes, esto consume CPU. Database overflow puede deshabilitar OSPF.

**Para qué:** Identificar si la red necesita summarization, stub areas, o tuning de SPF throttle timers para estabilidad.

**Resultado Esperado**: SPF ejecutado pocas veces. CPU estable. Database size dentro de límites. Sin LSA flapping.

🔬 **Hipótesis Científica**: El router experimenta alta CPU o inestabilidad porque el área tiene demasiados routers/prefijos causando SPF frecuentes, o porque la LSDB ha alcanzado el límite de overflow configurado, descartando nuevos LSAs y provocando agujeros en la topología.
🛠️ **Solución Rápida (Quick Fix)**: 1. Identificar y estabilizar enlaces flappeantes o Router-ID duplicado.
2. Reducir tamaño del área (<100 routers) mediante diseño jerárquico.
3. Aumentar límite de overflow de LSDB si es necesario.
4. Ajustar timers SPF/LSA para reducir carga CPU.
5. Investigar TCNs recurrentes y reparar causa raíz.
6. Confirmar CPU estable y SPF no frecuente.


#### Paso `ospf_bfd_gr`: 7. BFD, GR/NSF y OSPF Flapping (Tier 3)
**Descripción**: **Dónde:** Sesiones BFD asociadas a OSPF, y Graceful Restart/NSF.

**Cómo:** BFD flapping causa vecinos OSPF caídos. OSPF no reacciona a BFD DOWN. GR/NSF no negociado.

**Cuándo:** Tras configurar BFD con timers agresivos, o durante mantenimiento de control plane.

**Por qué:** BFD detecta fallas sub-segundo; timers muy agresivos pueden causar falsos positivos. GR/NSF requiere soporte en ambos extremos.

**Para qué:** Asegurar que BFD acelere la detección de fallas sin causar inestabilidad, y que GR/NSF funcione durante upgrades.

**Resultado Esperado**: BFD sesiones UP, timers negociados. GR/NSF capaz en ambos extremos. OSPF reacciona a BFD DOWN. Sin flapping.

🔬 **Hipótesis Científica**: Las adyacencias OSPF flappean debido a una inestabilidad de BFD que tira la sesión OSPF prematuramente, o a un conflicto entre Graceful Restart/NSF helper y la convergencia de un vecino lento, causando loops transitorios o blackholing.
🛠️ **Solución Rápida (Quick Fix)**: 1. Ajustar timers BFD a valores estables y soportados.
2. Correlacionar flaps OSPF con caídas BFD y resolver causa física.
3. Habilitar Graceful Restart/NSF helper bilateralmente.
4. Verificar que vecino salga de estado HELPER en tiempo esperado.
5. Asegurar compatibilidad de capabilities GR en ambos extremos.
6. Confirmar adyacencia OSPF estable tras reconvergencia.


### Tecnología: IS-IS Troubleshooting
Total de pasos diagnósticos: **4**

#### Paso `isis_start`: 1. Ámbito del problema IS-IS (Tier 1)
**Descripción**: **Dónde:** Adyacencias IS-IS, LSP database, métricas, multi-topology, y overload bit.

**Cómo:** Adyacencias en Init/Down. Rutas IS-IS ausentes. Métricas inconsistentes entre L1 y L2.

**Cuándo:** Tras cambios de área/level, aplicación de auth, o migración de hardware.

**Por qué:** Mismatch de MTU/auth/level, LSP partitioning, narrow vs wide metrics, o overload bit set impeden tránsito.

**Para qué:** Clasificar la falla para enfocar troubleshooting en adjacencies, database, o métricas/policies.

**Resultado Esperado**: Adjacencies UP. Interfaces activas en IS-IS. NET/Area consistente. Sin CSNP/PSNP errors.

🔬 **Hipótesis Científica**: La falla de enrutamiento IS-IS es causada por una adyacencia que no alcanza el estado Up debido a mismatch de tipo de red (P2P vs Broadcast), MTU de interfaz, nivel de área desajustado (L1/L2), o NET/área inconsistente.
🛠️ **Solución Rápida (Quick Fix)**: 1. Asegurar que ambos extremos de la interfaz usen el mismo tipo de red (P2P o Broadcast).
2. Ajustar MTU para que coincida en ambos extremos (IS-IS rellena IIH a MTU completa).
3. Verificar que ambos routers compartan el mismo nivel (L1/L2/L1-L2) y nombre de área para L1.
4. Confirmar que el NET/System-ID sea único en el dominio; corregir duplicados.
5. Revisar LSDB para sincronización; resolver particiones de área o flooding bloqueado.

#### Paso `isis_adj`: 2. Adyacencias IS-IS (Tier 1)
**Descripción**: **Dónde:** Interfaces IS-IS y exchange de IIHs (IS-IS Hello) entre routers.

**Cómo:** Adyacencia en Init (recibe IIH pero no matching) o Down. No pasa a Up.

**Cuándo:** Tras cambios de área, autenticación, o MTU.

**Por qué:** IS-IS requiere: mismo área (L1) o área contigua (L2), misma MTU, mismos auth params, y System-ID único.

**Para qué:** Diagnosticar por qué las adyacencias IS-IS no se establecen o se mantienen estables.

**Resultado Esperado**: State Up. Holdtime decrece. System-ID único. Subnets y levels coinciden. Auth y MTU iguales.

🔬 **Hipótesis Científica**: Las adyacencias IS-IS no se forman porque existe un mismatch de tipo de red (P2P vs Broadcast), MTU desajustada, nivel de área (L1/L2) inconsistente, o NET/System-ID duplicado, impidiendo el intercambio de IIH y la sincronización de LSPs.
🛠️ **Solución Rápida (Quick Fix)**: 1. Coincidir tipo de red (P2P/Broadcast) en ambos extremos.
2. Igualar MTU en ambos extremos.
3. Alinear nivel (L1/L2/L1-L2) y nombre de área para L1.
4. Corregir NET/System-ID duplicado.
5. Habilitar IS-IS en interfaces de tránsito.
6. Confirmar adyacencias Up y LSDB sincronizada.


#### Paso `isis_database`: 3. LSP Database y RIB (Tier 2)
**Descripción**: **Dónde:** LSP database (IS-IS Link State PDUs) y RIB.

**Cómo:** LSPs faltantes. Rutas IS-IS no en RIB. CSNP/PSNP exchange incompleto.

**Cuándo:** Tras particionamiento de red, o cuando un router no refresca sus LSPs.

**Por qué:** Cada router genera un LSP. Si falta uno, la topología está incompleta. Max-age sin refresh causa purge.

**Para qué:** Asegurar que todos los LSPs estén presentes y que las rutas IS-IS se instalen correctamente.

**Resultado Esperado**: Todos los LSPs presentes. Sin * (self) faltante. Rutas IS-IS en RIB. CSNP/PSNP exchange completo.

🔬 **Hipótesis Científica**: La LSDB de IS-IS contiene LSPs faltantes, con secuencia desactualizada, o con información de alcance inconsistente, resultando en rutas no instaladas en la RIB o forwarding subóptimo en el dominio IS-IS.
🛠️ **Solución Rápida (Quick Fix)**: 1. Comparar LSDB entre routers y resolver inconsistencias.
2. Asegurar presencia de LSPs de todos los routers/pseudonodos.
3. Investigar LSPs con lifetime expirado o secuencia reiniciada.
4. Verificar generación correcta de LSPs inter-nivel en L1/L2.
5. Confirmar instalación de rutas IS-IS en RIB.
6. Validar flooding completo sin particiones.


#### Paso `isis_metric`: 4. Métricas Wide / Overload / Attached (Tier 3)
**Descripción**: **Dónde:** Métricas de interfaces IS-IS, wide-metrics, overload bit, y attached bit.

**Cómo:** Rutas con métricas inesperadas. Overload bit impide tránsito. Attached-bit indica reachability a L2.

**Cuándo:** Tras cambios de métricas, o durante mantenimiento (overload bit set temporalmente).

**Por qué:** Wide-metrics (24-bit) vs narrow (6-bit) deben coincidir en toda el área. Overload bit evita tránsito. Attached-bit indica que el router tiene reachability a otras áreas.

**Para qué:** Validar que las métricas sean consistentes y que los bits de control no causen blackholing inesperado.

**Resultado Esperado**: Wide-metrics activas uniformemente. Overload bit solo en mantenimiento. Attached-bit correcto en L1/L2 routers.

🔬 **Hipótesis Científica**: El forwarding IS-IS es subóptimo o los routers no utilizan las métricas esperadas porque wide-metrics no está habilitado, el bit de overload está seteado inadvertidamente, o el attached-bit está generando rutas por defecto no deseadas en L1.
🛠️ **Solución Rápida (Quick Fix)**: 1. Habilitar wide-metrics globalmente y en interfaces.
2. Limpiar overload-bit en routers de tránsito.
3. Verificar attached-bit seteado solo con conectividad inter-área real.
4. Ajustar métricas de interfaces según diseño.
5. Confirmar path de forwarding de menor costo SPF.
6. Validar que métricas no se truncuen.


### Tecnología: BGP Troubleshooting
Total de pasos diagnósticos: **6**

#### Paso `bgp_start`: 1. Ámbito del problema BGP (Tier 1)
**Descripción**: **Dónde:** Sesiones BGP, path selection, route reflectors, confederations, policies, y next-hop.

**Cómo:** Peers en Idle/Active. Peers UP pero sin rutas. Bestpath inesperado. RR no refleja.

**Cuándo:** Tras cambios de peerings, aplicación de route-maps, o problemas de reachability.

**Por qué:** TCP 179 bloqueado, AS/TTL mismatch, policies descartan rutas, AFI/SAFI no activo, o path selection elige ruta alternativa.

**Para qué:** Clasificar si la falla es de peering, de propagación de rutas, o de path selection/policies.

**Resultado Esperado**: Peers Established. Sin prefix-limit exceeded. Capacidades AFI/SAFI negociadas. Bestpath lógico según atributos.

🔬 **Hipótesis Científica**: La falla de conectividad o enrutamiento es causada por una sesión BGP no establecida (estado diferente a Established), o por políticas de enrutamiento (prefix-lists, route-maps) que bloquean el intercambio de prefijos una vez que la sesión está activa.
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar conectividad IP y TCP 179 entre peers; eliminar ACLs/firewall que bloqueen.
2. Validar AS local/remoto, MD5 password, update-source y eBGP multihop si aplica.
3. Verificar que los prefijos esperados estén en Adj-RIB-In/Out; revisar policies de entrada/salida.
4. Revisar prefix-lists, route-maps, y community-filters que puedan descartar rutas.
5. Confirmar que el BGP Next-Hop sea alcanzable y resoluble vía IGP.

#### Paso `bgp_neighbor`: 2. Peers BGP caídos (Tier 1)
**Descripción**: **Dónde:** Sesión TCP/179 entre peers BGP, update-source, y reachability.

**Cómo:** Peer en Active/Idle/Connect. "show bgp neighbor" indica state down o TCP timeout.

**Cuándo:** Tras cambios de loopback, ACLs, o configuración de multihop/TTL.

**Por qué:** BGP requiere reachability al update-source. TCP 179 no debe estar filtrado. AS number debe coincidir. eBGP multihop requiere TTL suficiente.

**Para qué:** Establecer la sesión BGP antes de diagnosticar problemas de rutas o políticas.

**Resultado Esperado**: TCP 179 establecido. Open confirmado. Capacidades coincidentes. TTL OK. AS numbers correctos.

🔬 **Hipótesis Científica**: La sesión BGP no alcanza el estado Established porque existe una falla de conectividad TCP de Capa 3/4 (firewall bloqueando TCP 179, ACLs), un mismatch de parámetros de sesión (AS local/remoto, MD5 password, timers, update-source, eBGP multihop), o una interfaz de origen inestable/cambiando de estado.
🛠️ **Solución Rápida (Quick Fix)**: 1. Restaurar conectividad IP y apertura de TCP 179 entre peers.
2. Corregir AS local/remoto, update-source, eBGP multihop y MD5 password.
3. Sincronizar timers BGP Hold/Keepalive.
4. Revisar NOTIFICATION messages para identificar rechazo de sesión.
5. Asegurar que interfaz update-source esté Up/Up con IP correcta.
6. Confirmar sesión BGP Established y uptime estable.


#### Paso `bgp_routes`: 3. Peer UP pero sin intercambio de rutas (Tier 2)
**Descripción**: **Dónde:** NLRI recibidos, policies inbound/outbound, soft-reconfiguration, y maximum-prefix.

**Cómo:** Peer Established pero "show bgp neighbor <peer> routes" muestra 0 rutas. Prefix-limit alcanzado.

**Cuándo:** Tras cambios de policies, agregar nuevas redes, o cuando el peer envía más rutas de lo esperado.

**Por qué:** Route-map/prefix-list descarta rutas. Soft-reconfig faltante para ver rutas descartadas. Maximum-prefix shutdown. AFI/SAFI no activo. Next-hop inalcanzable.

**Para qué:** Identificar por qué no hay intercambio de rutas a pesar de que la sesión BGP está establecida.

**Resultado Esperado**: Rutas recibidas/advertisadas > 0. Sin prefix-limit exceeded. Policies permiten prefijos esperados. Next-hop resoluble.

🔬 **Hipótesis Científica**: La sesión BGP está Established pero no se intercambian prefijos debido a políticas de filtrado restrictivas (route-maps, prefix-lists, community-filters) aplicadas en el sentido incorrecto, un mismatch de address-family capabilities, o un Next-Hop inalcanzable que impide la instalación de las rutas recibidas en la RIB local.
🛠️ **Solución Rápida (Quick Fix)**: 1. Activar address family deseada bajo el neighbor y verificar capabilities.
2. Revisar Adj-RIB-In/Out para detectar prefijos recibidos pero filtrados.
3. Ajustar route-maps/prefix-lists de entrada/salida para permitir prefijos de interés.
4. Asegurar que Next-Hop de rutas recibidas sea alcanzable vía IGP.
5. Verificar que prefijos locales existan en tabla de rutas y redistribución hacia BGP.
6. Confirmar instalación de rutas en RIB local.


#### Paso `bgp_path`: 4. Path Selection / Bestpath (Tier 2)
**Descripción**: **Dónde:** Decision process de BGP: Weight, LocalPref, AS-Path, Origin, MED, eBGP>iBGP.

**Cómo:** Ruta esperada no es bestpath. Tráfico fluye por camino no óptimo.

**Cuándo:** Tras cambios de policies que modifican LocalPref/MED, o cuando se reciben múltiples rutas al mismo destino.

**Por qué:** BGP selecciona un único bestpath por prefijo. Si el atributo decisivo favorece otra ruta, la esperada no se usa.

**Para qué:** Entender por qué BGP eligió un path específico y si se requiere ajuste de políticas para influir en la selección.

**Resultado Esperado**: Bestpath tiene el atributo ganador según el algoritmo. MED comparado solo si mismo AS-path first. Origin IGP > EGP > Incomplete.

🔬 **Hipótesis Científica**: El router no selecciona el bestpath esperado porque los atributos BGP determinantes (LOCAL_PREF, AS_PATH, MED, ORIGIN, IGP metric to next-hop) no tienen los valores óptimos según el diseño, o porque la ruta más específica no está siendo anunciada/recibida correctamente.
🛠️ **Solución Rápida (Quick Fix)**: 1. Comparar atributos de rutas candidatas con 'show ip bgp <prefix>'.
2. Ajustar LOCAL_PREF según diseño de tráfico entrante.
3. Habilitar 'bgp always-compare-med' si MED proviene de AS diferentes y debe compararse.
4. Optimizar métrica IGP hacia Next-Hop para romper empates.
5. Asegurar que la ruta más específica esté presente y no resumida/suprimida.
6. Verificar que bestpath seleccionado coincida con política de diseño.


#### Paso `bgp_rr`: 5. Route Reflectors y Confederations (Tier 3)
**Descripción**: **Dónde:** Route Reflectors, cluster-id, originator-id, y propagación entre clientes y non-clients.

**Cómo:** Cliente no recibe rutas de otro cliente. RR no refleja rutas. Cluster-list muy largo.

**Cuándo:** Tras agregar nuevos clientes RR, o cambiar cluster-id.

**Por qué:** RR no refleja rutas cuyo originator-id es local (loop prevention). Cluster-list con el cluster-id local causa descarte. Split-horizon entre non-clients.

**Para qué:** Asegurar que el RR distribuya rutas correctamente entre clientes sin crear loops ni silenciar prefijos.

**Resultado Esperado**: Reflector envía rutas a clientes y non-clients. Originator-ID evita loops. Cluster-list no contiene cluster local.

🔬 **Hipótesis Científica**: La topología de Route Reflector o Confederations causa bucles de routing, reflexión inconsistente de rutas, o split-horizon en iBGP que impide que los clientes RR reciban prefijos desde otros clusters o sub-AS, debido a un mal diseño de cluster-ID, originator-ID, o falta de next-hop-self en los reflectores.
🛠️ **Solución Rápida (Quick Fix)**: 1. Asignar cluster-ID único a cada Route Reflector.
2. Verificar ORIGINATOR_ID no genere loop de origen.
3. Permitir rutas reflejadas desde otros clusters (no filtrar cluster-list).
4. Configurar next-hop-self en RRs o anunciar next-hops vía IGP.
5. En confederations, asegurar sub-AS path coherente y sin bucles.
6. Confirmar que clientes RR reciban rutas y next-hops sean alcanzables.


#### Paso `bgp_policies`: 6. Políticas / Communities / AS-Path filters (Tier 3)
**Descripción**: **Dónde:** Route-maps, prefix-lists, community-lists, AS-path filters, y secuencia de aplicación.

**Cómo:** Rutas esperadas no aparecen. Communities no aplicadas. AS-path filter bloquea prefijos legítimos.

**Cuándo:** Tras modificar policies, agregar prefijos, o cambiar communities.

**Por qué:** Las policies controlan import/export. Un deny implícito al final descarta todo lo no permitido. Communities mal formadas pueden ser ignoradas.

**Para qué:** Validar que las políticas BGP no descarten rutas o communities necesarios para el routing.

**Resultado Esperado**: Policies permiten prefijos esperados. Communities aplicadas correctamente. AS-path regex no bloquea rutas legítimas.

🔬 **Hipótesis Científica**: Las políticas de enrutamiento BGP (route-maps, community-filters, AS-Path filters) están configuradas en el sentido incorrecto o con criterios demasiado restrictivos, descartando silenciosamente prefijos legítimos o aplicando atributos no deseados que desvían el tráfico de su path óptimo.
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar dirección (in/out) de cada route-map/prefix-list.
2. Ajustar criterios de match (community, AS-Path, prefix-list) para no excluir prefijos legítimos.
3. Revisar set actions para LOCAL_PREF/MED/community según diseño.
4. Reordenar secuencias: denegaciones específicas primero, permisos generales después.
5. Revisar contadores de matches para identificar secuencias bloqueando tráfico.
6. Confirmar que los prefijos esperados pasen las políticas y se instalen.


### Tecnología: Spanning Tree Troubleshooting
Total de pasos diagnósticos: **5**

#### Paso `st_start`: 1. Ámbito del problema Spanning Tree (Tier 1)
**Descripción**: **Dónde:** STP/RSTP/MSTP en switches L2. Root election, port states, BPDUs, loops, y MST regions.

**Cómo:** Convergencia lenta, root inesperado, puertos en Blocking cuando deberían Forwarding, broadcast storms.

**Cuándo:** Tras cambios de topología, fallas de enlace, o configuración de portfast/BPDU guard.

**Por qué:** Root election depende de Bridge-ID. Port roles dependen de path cost. Loops ocurren cuando BPDUs no llegan o portfast en troncal.

**Para qué:** Clasificar el síntoma para enfocar en root election, port states, loop detection, o MST regions.

**Resultado Esperado**: Root ID consistente. Port roles/states lógicos. Sin TCNs excesivos. Sin loops detectados.

🔬 **Hipótesis Científica**: La falla de conectividad L2 o los loops de broadcast son causados por una topología Spanning Tree inestable: Root Bridge incorrecto, puertos bloqueados inesperadamente, TCNs recurrentes, o falta de protección BPDU en puertos de acceso.
🛠️ **Solución Rápida (Quick Fix)**: 1. Asegurar que el Root Bridge sea el switch de Core con prioridad manual baja (ej. 4096).
2. Verificar roles de puerto (Root/Designated/Blocking) en enlaces troncales; corregir si hay Alternate inesperados.
3. Investigar y eliminar la causa de TCNs recurrentes (enlaces inestables, BPDU filter).
4. Habilitar BPDU Guard en todos los puertos de acceso (edge) para prevenir loops.
5. Validar que MSTP region name, revision y VLAN-to-instance mapping sean idénticos en todos los switches.

#### Paso `st_root`: 2. Root Election y Prioridades (Tier 1)
**Descripción**: **Dónde:** Root bridge election, Bridge-ID (prioridad + MAC), y path cost hacia root.

**Cómo:** Root inesperado. Root flapping. Path cost no óptimo.

**Cuándo:** Tras agregar un nuevo switch, cambiar prioridades, o falla del root actual.

**Por qué:** El switch con menor Bridge-ID gana root. Si un switch no deseado tiene prioridad 0 o menor MAC, se convierte en root.

**Para qué:** Asegurar que el root designado esté en la posición topológica deseada y que la convergencia sea predecible.

**Resultado Esperado**: Root ID estable. Path cost mínimo hacia root. Sin root flapping. Root en ubicación deseada de la topología.


#### Paso `st_ports`: 3. Port States y BPDUs (Tier 2)
**Descripción**: **Dónde:** Estados de puertos STP: Blocking, Listening, Learning, Forwarding, Disabled. BPDU guard/loop guard.

**Cómo:** Puerto en Blocking cuando debería Forwarding. BPDU guard pone puerto en err-disabled. Loop guard en inconsistent.

**Cuándo:** Tras conectar un nuevo dispositivo, o aplicar port security/BPDU guard.

**Por qué:** Un puerto puede bloquearse si recibe BPDU superior. BPDU guard deshabilita puertos que reciben BPDUs (portfast). Loop guard bloquea si BPDUs dejan de llegar.

**Para qué:** Verificar que los puertos estén en los estados correctos y que las características de seguridad no bloqueen tráfico legítimo.

**Resultado Esperado**: Root/Designated/Alternate roles correctos. BPDUs recibidos en puertos non-edge. Forwarding donde se espera.


#### Paso `st_loops`: 4. Detección de Loops / Broadcast Storm (Tier 3)
**Descripción**: **Dónde:** Red L2 física o lógica donde existe más de un path activo sin STP bloqueando.

**Cómo:** CPU alta, tráfico broadcast creciendo, MAC flapping continuo, degradación rápida del rendimiento.

**Cuándo:** Tras conectar un cable no autorizado, falla de STP, o deshabilitar portfast incorrectamente.

**Por qué:** STP debe bloquear redundant links. Si un BPDU no llega (por ejemplo, por un hub no administrable), STP no detecta el loop.

**Para qué:** Detectar y eliminar loops L2 para restaurar la estabilidad de la red.

**Resultado Esperado**: Storm-control dentro de límites. Sin MAC flapping continuo. Loop eliminado. Un solo path activo por segmento.


#### Paso `st_mst`: 5. MST Regiones e Instances (Tier 3)
**Descripción**: **Dónde:** MST regions, donde todos los switches deben compartir mismo name, revision, y VLAN-to-instance mapping.

**Cómo:** MST region mismatch. CIST root inestable. VLANs no mapeadas al instance esperado.

**Cuándo:** Tras agregar un nuevo switch, o reconfigurar VLAN-to-instance mapping.

**Por qué:** MST opera con regions. Switches en diferentes regions ven al otro como boundary y usan CST. Esto puede causar bloqueo inesperado.

**Para qué:** Asegurar que todos los switches del dominio MST compartan la misma configuración de región.

**Resultado Esperado**: MST config consistente en toda la región (name, revision, mapping). CIST root estable. Boundary ports lógicos.


### Tecnología: QoS & Traffic Engineering Troubleshooting
Total de pasos diagnósticos: **5**

#### Paso `qos_start`: 1. Ámbito del problema QoS / TE (Tier 1)
**Descripción**: **Dónde:** Problemas de clasificación, marking, policing, shaping, queuing, o MPLS-TE/RSVP.

**Cómo:** Tráfico no marcado, descartes por policer, delay por shaping, colas saturadas, o LSP sin bandwidth.

**Cuándo:** Tras cambios de políticas QoS, contratos de servicio, o reconfiguración de túneles TE.

**Por qué:** Clasificación incorrecta, rates/burst mal calculados, scheduling no prioriza, o TE constraints no cumplidos.

**Para qué:** Clasificar si la falla está en clasificación, rate limiting, congestion management, o ingeniería de tráfico.

**Resultado Esperado**: Políticas QoS aplicadas en interfaces correctas. Colas con drops esperados. LSPs con bandwidth reservado.

🔬 **Hipótesis Científica**: La degradación de calidad de servicio o el comportamiento inesperado del tráfico es causado por una clasificación incorrecta (DSCP/CoS), policing/shaping mal dimensionado, colas de baja prioridad saturadas, o un LSP TE con RSVP que no reserva el ancho de banda solicitado.
🛠️ **Solución Rápida (Quick Fix)**: 1. Revisar y corregir la clasificación de tráfico en el borde (DSCP/CoS) y asegurar que se preserva en el core.
2. Ajustar policing/shaping para que rate y burst coincidan con el CIR/PIR del SLA.
3. Inspeccionar colas de salida y ajustar WRED/LLQ para evitar descartes en clases de voz/video.
4. Para TE: sincronizar la TED y verificar que el LSP RSVP-TE reserve el ancho de banda esperado.
5. Verificar que FRR bypass esté precalculado y que el tiempo de conmutación sea <50ms.

#### Paso `qos_classification`: 2. Clasificación y Marking (Tier 2)
**Descripción**: **Dónde:** Clasificadores de paquetes: DSCP, IP-Precedence, MPLS EXP, 802.1p CoS.

**Cómo:** Tráfico llega sin marking esperado. Rewrite rules sobrescriben DSCP incorrectamente.

**Cuándo:** Tras cambios de trust boundary, o migración de red IP a MPLS (EXP vs DSCP).

**Por qué:** La clasificación inicial determina en qué cola/tratamiento entra el paquete. Si se marca mal, el tráfico crítico puede compartir cola con best-effort.

**Para qué:** Garantizar que el marking end-to-end sea consistente con el diseño de QoS y los SLAs.

**Resultado Esperado**: Marking coincide con diseño (DSCP/EXP/CoS). Rewrite no sobrescribe inesperadamente. Trust boundary en interfaces correctas.


#### Paso `qos_policing`: 3. Policing y Shaping (Tier 2)
**Descripción**: **Dónde:** Policers y shapers en interfaces de borde o core.

**Cómo:** Tráfico legítimo descartado por policer. Latencia alta por shaper con buffer excesivo.

**Cuándo:** Tras cambios de CIR/PIR, o al activar QoS en un nuevo enlace.

**Por qué:** Policing descarta o remarca tráfico que excede rate+burst. Shaping retrasa. Burst size mal calculado descarta ráfagas legítimas.

**Para qué:** Asegurar que los parámetros de rate y burst sean consistentes con el contrato de servicio del cliente.

**Resultado Esperado**: Policer/shaper rate y burst acordes al contrato. Sin drops inesperados de tráfico conforme. Latencia dentro de SLA.


#### Paso `qos_queuing`: 4. Queuing y Congestion (Tier 2)
**Descripción**: **Dónde:** Colas de salida, schedulers (PQ/CQ/WFQ), WRED, y buffer management.

**Cómo:** Colas con drops excesivos. Tráfico de alta prioridad sufriendo delay. Bufferbloat.

**Cuándo:** Durante congestión sostenida, o tras cambios de scheduling.

**Por qué:** Tail drop descarta todo cuando la cola está llena. WRED descarta preventivamente. PQ puede starvear colas bajas.

**Para qué:** Verificar que el scheduling entrega la prioridad esperada y que los drops sean predecibles según el perfil.

**Resultado Esperado**: Colas con drops acordes a perfil. Scheduling entrega prioridad esperada. Sin starvation de colas críticas.


#### Paso `qos_te`: 5. RSVP-TE / MPLS Traffic Engineering (Tier 3)
**Descripción**: **Dónde:** RSVP-TE LSPs, MPLS Traffic Engineering, constraints de bandwidth y admin-groups.

**Cómo:** LSP no establece por falta de bandwidth. Path no respeta constraints. Preemption no deseado.

**Cuándo:** Tras agregar LSPs, cambiar reservas, o congestión de enlaces.

**Por qué:** RSVP-TE reserva bandwidth hop-by-hop. Si un enlace no tiene bandwidth reservable, el LSP falla. Admin-groups/affinity pueden excluir enlaces válidos.

**Para qué:** Asegurar que los LSPs críticos tengan bandwidth garantizado y que los constraints sean alcanzables.

**Resultado Esperado**: LSPs UP. Bandwidth reservable disponible en enlaces del path. Constraints (affinity, bandwidth) cumplidos.


### Tecnología: BFD Troubleshooting
Total de pasos diagnósticos: **4**

#### Paso `bfd_start`: 1. Ámbito del problema BFD (Tier 1)
**Descripción**: **Dónde:** Sesiones BFD para BGP, OSPF, IS-IS, LDP, o static routes.

**Cómo:** Sesión no establece (Down/Init). Flapping frecuente. BFD Up pero protocolo cliente no reacciona.

**Cuándo:** Tras habilitar BFD, cambiar timers, o durante congestión/micro-bursts.

**Por qué:** BFD requiere reachability IP, mismo UDP port, timers compatibles, y registro del protocolo cliente.

**Para qué:** Clasificar si la falla es de establecimiento, estabilidad, o integración con el protocolo cliente.

**Resultado Esperado**: Sesiones Up. Timers negociados consistentes. Clientes registrados (BGP/OSPF/IS-IS). Sin flapping.

🔬 **Hipótesis Científica**: La falla de convergencia rápida es causada por una sesión BFD que no alcanza el estado Up debido a timers desajustados, tráfico UDP 3784/3785 bloqueado por ACLs/firewall, o una interfaz física con micro-flaps que genera oscilación de la sesión.
🛠️ **Solución Rápida (Quick Fix)**: 1. Ajustar timers BFD (Tx/Rx/Detection Multiplier) al mínimo soportado por ambos extremos según datasheet.
2. Eliminar o relajar ACLs/firewall filters que descarten UDP 3784 (single-hop) o UDP 3785 (multi-hop).
3. Resolver inestabilidad física del enlace (cambiar cable/SFP, corregir dúplex/velocidad) para eliminar micro-flaps.
4. Asociar explícitamente BFD al protocolo cliente (OSPF/BGP/IS-IS/EIGRP) en ambos extremos.
5. Verificar contadores de paquetes BFD transmitidos/recibidos sean simétricos y sin pérdidas.
6. Confirmar que la sesión BFD alcance estado Up y que el cliente la registre ('show bfd neighbors client').


#### Paso `bfd_down`: 2. Sesión BFD caída (Tier 1)
**Descripción**: **Dónde:** Reachability IP al peer BFD, puerto UDP 3784/4784, y configuración BFD.

**Cómo:** Sesión en Down. No se reciben BFD control packets.

**Cuándo:** Tras cambios de routing, ACLs, o configuración de interfaces.

**Por qué:** BFD requiere alcanzabilidad IP al peer. UDP 3784/4784 no debe estar filtrado. Ambos extremos deben tener BFD habilitado.

**Para qué:** Restaurar la sesión BFD para que el protocolo cliente pueda usar detección rápida de fallas.

**Resultado Esperado**: Reachability al peer. BFD enabled en ambos lados. Timers negociados. UDP port libre.


#### Paso `bfd_flap`: 3. BFD Flapping (Tier 2)
**Descripción**: **Dónde:** Estabilidad de la sesión BFD, CPU, y estado de interfaces.

**Cómo:** Sesión Up/Down repetidamente. Contadores de flap altos.

**Cuándo:** Durante micro-bursts de congestión, CPU spikes, o problemas físicos intermitentes.

**Por qué:** Timers demasiado agresivos (ej. 3x50ms) pueden causar falsos positivos con mínima congestión. CPU alta retrasa procesamiento de BFD packets.

**Para qué:** Ajustar timers para balancear detección rápida vs estabilidad, y descartar problemas físicos/CPU.

**Resultado Esperado**: Flap count bajo. Sin errores de interfaz. CPU estable. Timers razonables (ej. 3x300ms o más en links congestionados).


#### Paso `bfd_client`: 4. Protocolo cliente no reacciona a BFD (Tier 2)
**Descripción**: **Dónde:** Registro del protocolo cliente (BGP/OSPF/IS-IS/LDP) en la sesión BFD.

**Cómo:** BFD Up pero "show ospf neighbor" no indica BFD. Protocolo no reacciona a caída de BFD.

**Cuándo:** Tras habilitar BFD en el protocolo, o migrar de una versión de software a otra.

**Por qué:** BFD y el protocolo deben estar vinculados. Si el protocolo no se registra como cliente, BFD opera aislado.

**Para qué:** Garantizar que el protocolo de routing use BFD para detección de fallas sub-segundo.

**Resultado Esperado**: Protocolo registrado como cliente BFD. BFD habilitado bajo el protocolo. Clientes listados en "show bfd clients".


### Tecnología: Multicast Troubleshooting
Total de pasos diagnósticos: **6**

#### Paso `mcast_start`: 1. Ámbito del problema Multicast (Tier 1)
**Descripción**: **Dónde:** IGMP en hosts, PIM en routers, RP, MSDP, MBGP, y forwarding multicast.

**Cómo:** Hosts no reciben multicast. PIM neighbors caídos. RP inalcanzable. MSDP SA no propagadas.

**Cuándo:** Tras cambios de RP, aplicación de IGMP snooping, o reconfiguración de PIM.

**Por qué:** IGMP requiere querier. PIM requiere neighbors en todos los links. RP debe ser conocido por todos. MSDP requiere MBGP.

**Para qué:** Clasificar el dominio del problema: host (IGMP), router (PIM), core (RP/MSDP), o forwarding (RPF/SPT).

**Resultado Esperado**: PIM neighbors UP. IGMP querier activo. Join tree poblado. MSDP peers Established si aplica.

🔬 **Hipótesis Científica**: La falla de entrega multicast es causada por una falla en el plano de control IGMP/PIM (RP inalcanzable, RPF check fallido, o PIM neighbor down) o por una insuficiencia en el plano de datos (tabla MFIB sin entradas activas o OIL vacía).
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar que el IGP subyacente sea funcional y estable antes de diagnosticar multicast.
2. Confirmar que el RP sea alcanzable y consistente en todos los routers; corregir si hay RP inconsistency.
3. Validar el RPF check: 'show ip rpf <source>' debe devolver la interfaz correcta.
4. Verificar que PIM esté habilitado en todas las interfaces de tránsito y que los vecinos estén Up.
5. Revisar la tabla MFIB/MRIB para confirmar que haya estados (S,G) y (*,G) con OIL poblada.

#### Paso `mcast_igmp`: 2. IGMP: Hosts no reciben multicast (Tier 1)
**Descripción**: **Dónde:** Segmento L2 entre hosts y primer router multicast (querier).

**Cómo:** Hosts no reciben tráfico multicast aunque el source está activo. "show igmp groups" vacío.

**Cuándo:** Tras agregar/quitar hosts, cambiar versión IGMP, o aplicar IGMP snooping.

**Por qué:** Hosts deben enviar IGMP Membership Reports. El querier debe estar activo. IGMP snooping puede bloquear puertos incorrectamente.

**Para qué:** Asegurar que los hosts se unan correctamente al grupo multicast y que el router reciba los joins.

**Resultado Esperado**: Grupos IGMP presentes. Querier activo. Versiones coincidentes (v1/v2/v3). Snooping no bloquea puertos de miembros.

🔬 **Hipótesis Científica**: Los hosts no reciben tráfico multicast porque IGMP no está habilitado en la interfaz de acceso, el host no envía IGMP Joins, o el switch/router de última milla no tiene el grupo en su tabla IGMP snooping/mroute, impidiendo la construcción de la OIL.
🛠️ **Solución Rápida (Quick Fix)**: 1. Habilitar IGMP en interfaz de acceso hacia receptores.
2. Verificar que hosts envíen IGMP Joins para el grupo.
3. Activar/configurar IGMP snooping en switch L2 y asociar puerto del host al grupo.
4. Completar entrada (*,G) en router L3 con interfaz de acceso en OIL.
5. Eliminar ACLs/storm-control que descarten IGMP Reports.
6. Confirmar que los hosts reciban tráfico multicast.


#### Paso `mcast_pim`: 3. PIM: Vecinos y Topology (Tier 2)
**Descripción**: **Dónde:** Links entre routers PIM, PIM neighbor table, y PIM topology.

**Cómo:** PIM neighbors ausentes. Join/Prune no fluyen. (*,G) o (S,G) entries incompletas.

**Cuándo:** Tras cambios de interfaces, aplicación de ACLs, o fallas de enlace.

**Por qué:** PIM requiere neighbors en todas las interfaces del path multicast. Si un link no tiene PIM habilitado, el árbol se rompe.

**Para qué:** Verificar que la topología PIM esté completa para construir el shared tree (RPT) y el shortest path tree (SPT).

**Resultado Esperado**: PIM neighbors en todos los links. Join/prune messages fluyendo. (*,G) y (S,G) entries presentes.

🔬 **Hipótesis Científica**: El árbol multicast no se construye porque las adyacencias PIM no se forman (Hellos bloqueados, DR election conflictivo), o porque el RPF check falla por una ruta unicast incorrecta hacia la fuente del tráfico multicast.
🛠️ **Solución Rápida (Quick Fix)**: 1. Habilitar PIM Sparse-Mode en interfaces de tránsito y acceso.
2. Establecer adyacencias PIM Up entre vecinos.
3. Resolver DR election con un único DR por segmento multiacceso.
4. Corregir RPF check para que coincida con ruta unicast hacia fuente.
5. Eliminar ACLs que bloqueen PIM (IP 103) o IGMP Joins/Prunes.
6. Confirmar construcción del árbol multicast.


#### Paso `mcast_rp`: 4. Rendezvous Point (RP) (Tier 2)
**Descripción**: **Dónde:** Rendezvous Point en PIM-SM, estático o dinámico (BSR/Auto-RP).

**Cómo:** RP inalcanzable. Routers no conocen el RP para un grupo. BSR/Auto-RP no convergen.

**Cuándo:** Tras cambios de RP, agregar nuevos grupos, o falla del RP actual.

**Por qué:** Todos los routers PIM-SM deben conocer el mismo RP. BSR requiere que el candidato-RP y el BSR se alcancen.

**Para qué:** Garantizar que el RP esté disponible y correctamente anunciado para todos los routers del dominio.

**Resultado Esperado**: RP alcanzable. BSR/Auto-RP consistente. (*,G) entries apuntando al RP correcto. Sin RP conflict.

🔬 **Hipótesis Científica**: El RP no es alcanzable o está inconsistentemente configurado (RP estático vs Auto-RP/BSR), causando que los routers PIM no puedan establecer el (*,G) shared tree ni el source tree (S,G), resultando en ausencia de tráfico multicast en los receptores.
🛠️ **Solución Rápida (Quick Fix)**: 1. Restaurar alcanzabilidad unicast del RP desde todos los routers.
2. Configurar RP consistente (estático, Auto-RP o BSR) en todos los routers.
3. Asegurar que RP tenga rutas hacia fuentes multicast.
4. Habilitar PIM en interfaces del RP y procesar Registers.
5. Verificar estados (*,G) y (S,G) activos en RP.
6. Confirmar que receptores reciban tráfico del shared tree.


#### Paso `mcast_msdp`: 5. MSDP: Inter-domain Multicast (Tier 3)
**Descripción**: **Dónde:** Peers MSDP entre RPs de diferentes dominios PIM-SM.

**Cómo:** SA messages no llegan. Grupos remotos no visibles. MSDP peer en Down.

**Cuándo:** Tras configurar MSDP, o cuando cambia la reachability entre RPs.

**Por qué:** MSDP requiere reachability IP entre RPs (usualmente vía MBGP). SA messages anuncian (S,G) activos.

**Para qué:** Asegurar que el multicast inter-dominio se propague correctamente vía MSDP.

**Resultado Esperado**: MSDP peers Established. SA-cache poblado con (S,G) de dominios remotos. Reachability IP entre RPs OK.

🔬 **Hipótesis Científica**: La interconexión multicast entre dominios PIM falla porque las sesiones MSDP entre RPs no están establecidas, o los SA (Source-Active) messages son filtrados por políticas de peer, impidiendo que los RPs remotos conozcan las fuentes activas.
🛠️ **Solución Rápida (Quick Fix)**: 1. Establecer sesiones TCP MSDP (puerto 639) Established entre RPs.
2. Asegurar generación y reenvío de SA messages desde RP origen.
3. Revisar sa-filters/peer-filters para permitir grupos/fuentes.
4. Corregir RPF check MSDP hacia originador del SA.
5. Verificar caché de SA en RPs remotos.
6. Confirmar interconexión multicast entre dominios.


#### Paso `mcast_fwd`: 6. Forwarding / SPT (Shortest Path Tree) (Tier 3)
**Descripción**: **Dónde:** Multicast forwarding table, RPF check, y Shortest Path Tree.

**Cómo:** Tráfico multicast no llega a receivers. (S,G) entry existe pero no fluye.

**Cuándo:** Tras cambios de routing unicast (afecta RPF), o cuando el SPT no se construye.

**Por qué:** RPF check falla si la ruta al source no pasa por la interfaz incoming. SPT requiere que el receiver envíe S,G Join.

**Para qué:** Verificar que el data plane multicast pueda entregar tráfico desde source hasta receivers.

**Resultado Esperado**: (S,G) entries con incoming/outgoing interfaces. RPF check passing. Tráfico fluyendo. Sin RPF failures.

🔬 **Hipótesis Científica**: El tráfico multicast no se reenvía correctamente porque la SPT no se ha establecido (RPF failure, PIM Joins bloqueados), o porque el rendimiento del data plane es insuficiente (MFIB sin recursos, OIL vacía, o descartes por congestión en el core).
🛠️ **Solución Rápida (Quick Fix)**: 1. Construir/completar árbol SPT con entradas (S,G) en todos los routers.
2. Corregir RPF check en cada salto del SPT.
3. Poblar OIL con interfaces hacia receptores activos.
4. Verificar entradas activas en MFIB/FIB multicast con contadores incrementando.
5. Eliminar descartes por falta de recursos, buffer o rate-limit.
6. Confirmar reenvío de tráfico multicast a receptores.


### Tecnología: MP-BGP Troubleshooting
Total de pasos diagnósticos: **5**

#### Paso `mpbgp_start`: 1. Ámbito del problema MP-BGP (Tier 1)
**Descripción**: **Dónde:** Address-families MP-BGP: IPv4/IPv6 unicast/multicast, VPNv4/VPNv6, labeled-unicast, EVPN.

**Cómo:** AFI/SAFI no negociado. Labeled-unicast sin labels. VPNv4 sin rutas. IPv6 BGP caído.

**Cuándo:** Tras habilitar una nueva AF, migrar a BGP EVPN, o interconectar AS con labeled-unicast.

**Por qué:** Cada AF requiere activación explícita en ambos peers. Algunas plataformas requieren "address-family" por separado.

**Para qué:** Clasificar qué address-family falla para enfocar el troubleshooting en AFI/SAFI, labeled routes, VPN, o IPv6.

**Resultado Esperado**: Peers Established. AFI/SAFI negociados. Address-families activas según diseño. Capacidades visibles.

🔬 **Hipótesis Científica**: La falla de distribución de rutas multiprotocolo es causada por una sesión MP-BGP no establecida (capability mismatch), una address family no activada, o un error en la resolución de next-hop para las NLRI VPN/EVPN.
🛠️ **Solución Rápida (Quick Fix)**: 1. Establecer sesión BGP base IPv4/IPv6 en Established y abrir TCP 179.
2. Activar explícitamente la address family deseada (VPNv4, VPNv6, EVPN, LU) bajo el neighbor.
3. Verificar que el capability exchange incluya la AFI/SAFI correcta.
4. Asegurar que el Next-Hop de las NLRI sea alcanzable vía IGP y resuelto a label MPLS si aplica.
5. Revisar policies de entrada/salida para permitir las NLRI multiprotocolo.
6. Confirmar que las rutas MP-BGP se instalen en la RIB/LFIB según corresponda.


#### Paso `mpbgp_afi`: 2. AFI/SAFI no negociado (Tier 2)
**Descripción**: **Dónde:** Negociación de capacidades BGP, AFI/SAFI en OPEN message.

**Cómo:** "show bgp neighbor" muestra "not negotiated" para la AF esperada. No hay NLRI de esa familia.

**Cuándo:** Tras agregar un peer MP-BGP, o reconfigurar families.

**Por qué:** Ambos extremos deben activar la misma AF. Si un lado no la tiene, la sesión puede estar UP pero no intercambiar rutas de esa familia.

**Para qué:** Asegurar que ambos peers negocien correctamente la address-family requerida para el servicio.

**Resultado Esperado**: Capabilities negociadas incluyen la AF esperada. Sin not negotiated warnings. NLRI visible para la AF activa.


#### Paso `mpbgp_lu`: 3. BGP Labeled-Unicast (Tier 2)
**Descripción**: **Dónde:** BGP Labeled-Unicast (SAFI 4), inet.3 / labeled-unicast table.

**Cómo:** Rutas BGP presentes pero sin labels. "show mpls forwarding-table" no tiene entrada para el next-hop BGP.

**Cuándo:** En inter-AS Option B, o cuando se usa BGP para distribuir labels (Segment Routing, LU).

**Por qué:** Labeled-unicast requiere que el peer anuncie label junto con el prefijo. Sin label, el next-hop no es resoluble en MPLS.

**Para qué:** Garantizar que el plano de datos MPLS pueda forwardar tráfico usando labels distribuidos por BGP.

**Resultado Esperado**: Rutas con labels en inet.3 / labeled-unicast table. Next-hop label válido. MPLS stack resoluble.


#### Paso `mpbgp_vpn`: 4. VPNv4/VPNv6 entre PEs (Tier 3)
**Descripción**: **Dónde:** VPNv4/VPNv6 (SAFI 128) entre PEs, RD/RT, y next-hop reachability.

**Cómo:** Peers UP pero rutas VPN no se instalan. "show bgp vpnv4 unicast" muestra rutas pero no en RIB VRF.

**Cuándo:** Tras configurar una nueva VPN, o migrar PEs.

**Por qué:** Requiere RD único, RT coincidentes, y next-hop alcanzable vía MPLS (LDP o labeled-unicast).

**Para qué:** Asegurar que las rutas VPN se transporten correctamente entre PEs y se instalen en las VRFs.

**Resultado Esperado**: Rutas VPNv4/VPNv6 presentes. RD correcto. RT communities consistentes. Next-hop resoluble con label stack.


#### Paso `mpbgp_ipv6`: 5. IPv6 over BGP (Tier 2)
**Descripción**: **Dónde:** BGP IPv6 unicast/multicast, reachability IPv6 al peer, y next-hop IPv6.

**Cómo:** Peer IPv6 caído. Rutas IPv6 no recibidas. Next-hop IPv6 inalcanzable.

**Cuándo:** Tras habilitar IPv6 en BGP, o migrar de IPv4-only a dual-stack.

**Por qué:** BGP IPv6 requiere AF IPv6 activa. El next-hop puede ser IPv6 o IPv4 (next-hop-self). Reachability IPv6 debe existir.

**Para qué:** Garantizar que el routing IPv6 funcione sobre BGP, ya sea nativo o sobre transport IPv4.

**Resultado Esperado**: Peer IPv6 Established. Rutas IPv6 en BGP table. Next-hop IPv6 alcanzable. AF IPv6 negociada.


### Tecnología: DHCP / DHCPv6 Troubleshooting
Total de pasos diagnósticos: **5**

#### Paso `dhcp_start`: 1. Ámbito del problema DHCP (Tier 1)
**Descripción**: **Dónde:** Cliente, relay, server, o pool de leases. DHCPv4 y DHCPv6.

**Cómo:** Cliente no obtiene IP. Relay no forwarda. Option 82 incorrecto. Pool agotado.

**Cuándo:** Tras agregar clientes, cambiar configuración de relay, o agotarse el rango de direcciones.

**Por qué:** DHCP requiere broadcast reachability (o relay), pool disponible, y opciones correctas. DHCPv6 requiere RA/PD.

**Para qué:** Clasificar si la falla está en el cliente, relay, server, o agotamiento de recursos.

**Resultado Esperado**: Leases asignados. Relay counters incrementando. Pool con IPs disponibles. Sin errores de auth/option.

🔬 **Hipótesis Científica**: La falla de asignación de direcciones IP es causada por una ruptura en el flujo DORA (Discover/Offer/Request/Ack): el servidor no recibe la solicitud, el relay no reenvía correctamente, o el pool de direcciones está agotado.
🛠️ **Solución Rápida (Quick Fix)**: 1. Asegurar que la interfaz del cliente/SVI tenga IP correcta y esté Up/Up.
2. Configurar o corregir el DHCP Relay ('ip helper-address') en la interfaz L3 del segmento de cliente.
3. Verificar que el campo giaddr en los paquetes relayed coincida con la IP de la interfaz del relay.
4. Liberar/agregar direcciones en el pool del servidor para la subnet indicada por giaddr.
5. Eliminar ACLs/firewall que bloqueen UDP 67/68 entre cliente, relay y servidor.
6. Validar que el cliente reciba Offer/Ack tras un Discover; de lo contrario, revisar logs del servidor.


#### Paso `dhcp_noffer`: 2. Cliente no recibe OFFER (Tier 1)
**Descripción**: **Dónde:** Entre cliente y server (o relay). Mensajes DISCOVER, OFFER, REQUEST, ACK.

**Cómo:** Cliente envía DISCOVER pero no recibe OFFER. Capturas muestran solo DISCOVERs.

**Cuándo:** Tras cambios de VLAN, aplicación de ACLs, o falla del server.

**Por qué:** El relay no está configurado en la interfaz del cliente. Server caído. ACLs bloquean UDP 67/68. Pool vacío.

**Para qué:** Identificar dónde se interrumpe el flujo DORA para restaurar la asignación de direcciones.

**Resultado Esperado**: Relay forwarda DISCOVER al server. Server responde con OFFER. Sin ACLs bloqueando UDP 67/68. Pool con IPs libres.


#### Paso `dhcp_relay`: 3. DHCP Relay (Tier 2)
**Descripción**: **Dónde:** Configuración de DHCP relay en el router/switch de borde.

**Cómo:** Relay agent IP incorrecto. Giaddr no coincide con subnet. Server no responde.

**Cuándo:** Tras reconfigurar relay, migrar interfaces, o cambiar server.

**Por qué:** El relay debe insertar su IP facing el cliente como giaddr. El server responde al giaddr. Si el giaddr está mal, el server no sabe qué pool usar.

**Para qué:** Asegurar que el relay forwarda correctamente los mensajes DHCP y que el server pueda identificar la subnet.

**Resultado Esperado**: Relay activo en interfaz correcta. Server IP alcanzable. Giaddr coincide con subnet del cliente. Counters incrementando.


#### Paso `dhcp_opt82`: 4. Option 82 / Circuit-ID (Tier 3)
**Descripción**: **Dónde:** DHCP relay Option 82 (Agent Information) en entornos ISP/broadband.

**Cómo:** Server rechaza leases. Option 82 no insertado. Circuit-ID no coincide con configuración del server.

**Cuándo:** Tras migrar a DHCP con Option 82, o cambiar circuit-IDs.

**Por qué:** Option 82 identifica el origen del subscriber. Si el server no confía en la opción o no la encuentra, puede no asignar IP.

**Para qué:** Garantizar que el relay inserte correctamente Option 82 y que el server la use para asignar pools/leases.

**Resultado Esperado**: Option 82 insertado. Circuit-ID y remote-ID correctos. Server acepta Option 82. Leases asignados por subscriber.


#### Paso `dhcp_pool`: 5. DHCP Pool Agotado (Tier 2)
**Descripción**: **Dónde:** Pool de direcciones DHCP en el server.

**Cómo:** Clientes nuevos no obtienen IP. "show ip dhcp pool" indica utilización 100%.

**Cuándo:** Al crecer la base de clientes, o cuando lease duration es muy largo y los clientes desconectados mantienen leases.

**Por qué:** Pool finito. Leases no liberados (cliente desconectado sin RELEASE). DHCPv6 IA_PD consume prefijos grandes.

**Para qué:** Verificar que haya capacidad suficiente y que los leases expirados se limpien correctamente.

**Resultado Esperado**: Pool con IPs disponibles. Leases expirados limpiados. Lease duration apropiado. Utilización < 90%.


### Tecnología: NetFlow / IPFIX / sFlow Troubleshooting
Total de pasos diagnósticos: **5**

#### Paso `nf_start`: 1. Ámbito del problema NetFlow/IPFIX (Tier 1)
**Descripción**: **Dónde:** Exportación de flujos desde routers/switches hacia collectors.

**Cómo:** No se reciben flujos. Flujos incompletos. CPU alta. Sampling incorrecto.

**Cuándo:** Tras configurar NetFlow/IPFIX/sFlow, o durante eventos de alto tráfico.

**Por qué:** Reachability al collector, UDP port bloqueado, template no exportado, sampling rate mal configurado, o cache overflow.

**Para qué:** Clasificar si la falla es de exportación, de datos, de rendimiento, o de sampling.

**Resultado Esperado**: Exporter activo. Flujos enviados al collector. Sampling rate consistente. CPU estable.

🔬 **Hipótesis Científica**: La ausencia de datos de telemetría o la inconsistencia en el análisis de tráfico es causada por una configuración incorrecta del exportador (IP/puerto del colector), una sampling rate inadecuada, o una falta de recursos en el router (CPU/memoria para procesar flujos).
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar conectividad IP y ruta hacia el colector NetFlow/sFlow desde el router.
2. Abrir puertos UDP 2055/9995/6343 en firewalls/ACLs intermedios.
3. Ajustar la sampling rate a un valor adecuado para la velocidad del enlace (ej. 1:1000 en 10G/100G).
4. Aplicar el monitor de NetFlow a las interfaces de interés en ingress/egress según diseño.
5. Verificar que la cache de flujos muestre entradas activas y contadores de exportación incrementando.
6. Confirmar que CPU/memoria del router se mantengan estables tras la activación del exportador.


#### Paso `nf_export`: 2. Exporter no envía flujos (Tier 1)
**Descripción**: **Dónde:** Exporter: interfaces configuradas, reachability al collector, y puerto UDP.

**Cómo:** "show flow exporter statistics" muestra 0 packets sent. Collector no recibe datagramas.

**Cuándo:** Tras cambiar IP del collector, aplicar ACLs, o reconfigurar exporter.

**Por qué:** Reachability IP al collector es necesaria. Puerto UDP (2055/4739/6343) debe estar libre. El exporter debe estar habilitado en interfaces.

**Para qué:** Restaurar la exportación de flujos para monitoreo, billing, y detección de anomalías.

**Resultado Esperado**: Exporter status Up. Packets sent incrementando. Collector reachable vía IP underlay. Sin firewall block.


#### Paso `nf_data`: 3. Flujos incompletos o incorrectos (Tier 2)
**Descripción**: **Dónde:** Campos de los flujos exportados y templates NetFlow v9/IPFIX.

**Cómo:** Flujos recibidos con campos vacíos. Template ID no reconocido. Datos inconsistentes.

**Cuándo:** Tras cambiar record format, o cuando el collector no soporta el template.

**Por qué:** NetFlow v9/IPFIX requiere templates periódicos. Sin template, el collector no puede decodificar. Cache overflow descarta flujos.

**Para qué:** Asegurar que los flujos exportados sean completos y decodificables por el collector.

**Resultado Esperado**: Campos completos. Template exportado periódicamente. Cache size adecuado. Sin template mismatch.


#### Paso `nf_perf`: 4. Performance / CPU por NetFlow (Tier 3)
**Descripción**: **Dónde:** CPU del router, cache de NetFlow, y sampling rate.

**Cómo:** CPU alta sostenida. Cache drops. Export delay.

**Cuándo:** Durante picos de tráfico, o con sampling rate muy bajo (1:1 en links de 10G+).

**Por qué:** NetFlow sin sampling en links de alta velocidad consume CPU significativa. Cache pequeño causa drops.

**Para qué:** Ajustar sampling y cache para balancear precisión y rendimiento.

**Resultado Esperado**: CPU estable. Sampling rate apropiado para el throughput. Sin cache drops. Export oportuno.


#### Paso `nf_sflow`: 5. sFlow: Sampling Rate (Tier 3)
**Descripción**: **Dónde:** Sampling estadístico sFlow en interfaces.

**Cómo:** Samples no llegan al collector. Sampling rate inadecuado. Counter samples ausentes.

**Cuándo:** Tras habilitar sFlow, o al cambiar la plataforma de collector.

**Por qué:** sFlow usa sampling aleatorio. Si el rate es muy alto (ej. 1:10000 en link de 1G), se pierde granularidad. Si es muy bajo, consume CPU.

**Para qué:** Calibrar el sampling rate para que sea representativo del tráfico sin sobrecargar el switch ni el collector.

**Resultado Esperado**: Sampling rate consistente. Samples enviados al collector. Counter samples presentes. Sin drops de export.


### Tecnología: ADTRAN Total Access 5000 Troubleshooting
Total de pasos diagnósticos: **18**

#### Paso `adtran_start`: 1. Ámbito del problema TA5000 (Tier 1)
**Descripción**: **Dónde:** El problema puede estar en el módulo de línea (GE, DS3, T1), 
en la redundancia de slot, en el timing del sistema, o en el anillo RPR/ERPS.

**Cómo:** Alarmas de sistema, slots en OOS, interfaces sin tráfico, 
pérdida de sincronización, o fallas en loopbacks.

**Cuándo:** Tras reemplazo de tarjeta, migración de fibra, cambios de 
provisioning, o fallas de alimentación DC.

**Por qué:** Slots no provisionados, interfaces en shutdown, mismatch de 
timing, o anillo RPR/ERPS con switch forzado.

**Para qué:** Determinar si la falla es de hardware (slot/interfaz), 
provisioning, timing, o topología de anillo.

**Resultado Esperado**: Todos los slots usados en IS (In Service) o OOS-MA si se desea. 
Sin alarmas críticas. Timing locked o source válido.

🔬 **Hipótesis Científica**: La falla en el chasis ADTRAN TA5000 es causada por una tarjeta de línea no detectada, un enlace uplink GE/T1/DS3 caído, una inconsistencia en la redundancia RPR/ERPS, o un problema de sincronización de timing (COT/RT).
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar estado de tarjetas, ventiladores y fuentes; reemplazar hardware fault si es necesario.
2. Restaurar enlaces uplink GE/XE activos y sin CRC errors (cable/SFP).
3. Resolver breaks en anillo RPR/ERPS para restablecer redundancia en <50ms.
4. Sincronizar timing locked a referencia primaria (COT) o secundaria (RT); verificar wander/jitter dentro de G.823.
5. Limpiar alarmas de hardware (optical LOS, BERT errors en T1/DS3).
6. Confirmar estabilidad del chasis y servicios TDM/GPON tras la corrección.


#### Paso `adtran_ge`: 2. GE 4-Port Line Module (Tier 1)
**Descripción**: **Dónde:** Administración de slot, estado de puertos de red, downlink 
(Ethernet Star) y redundancia de tarjeta.

**Cómo:** Puerto en shutdown, sin tráfico, o redundancia no activa.

**Por qué:** Slot shutdown, puerto en OOS, falta comando downlink, o 
redundancia no habilitada en ambos slots adyacentes.

**Para qué:** Restaurar el servicio Ethernet de acceso/backhaul.

**Resultado Esperado**: Slot IS. Puerto no shutdown (In Service). Redundancia activa si aplica.


#### Paso `adtran_ge_down`: 2.1 Puerto GE Down / OOS (Tier 1)
**Descripción**: **Dónde:** Interfaz física y estado administrativo del puerto GE.

**Cómo:** Verificar si el puerto está en shutdown, maintenance, o unassigned.

**Para qué:** Levantar el puerto a In Service.

**Resultado Esperado**: Puerto en estado In Service (no shutdown). Sin errores de capa física.


#### Paso `adtran_ge_redundancy`: 2.2 Redundancia de GE 4-Port (Tier 2)
**Descripción**: **Dónde:** Slots adyacentes (odd/even) configurados como par redundante.

**Cómo:** El slot odd debe provisionarse primero y estar activo. 
El even debe estar IS para que la redundancia sea completa.

**Para qué:** Garantizar failover de tarjeta sin pérdida de servicio.

**Resultado Esperado**: Odd slot activo (Master), even slot IS (Standby). No shutdown en ambos.


#### Paso `adtran_ds3`: 3. DS3 Unchannelized EFM 4-Port (Tier 1)
**Descripción**: **Dónde:** Administración de slot DS3, estado de puertos T3, uplink 
identifier, timing source, y loopbacks.

**Cómo:** Puerto T3 en shutdown, falta uplink identifier, timing no locked, 
o fallas en BERT/loopbacks.

**Para qué:** Restaurar el servicio DS3/EFM de backhaul.

**Resultado Esperado**: Slot IS. Puerto T3 In Service. Uplink identifier configurado. Timing source locked.


#### Paso `adtran_ds3_loopback`: 3.1 Loopbacks y BERT DS3 (Tier 2)
**Descripción**: **Dónde:** DS3 Facility loopbacks: Line, Payload y Remote.

**Cómo:** Ejecutar loopback local o remoto para aislar fallas de circuito.

**Para qué:** Verificar integridad del circuito DS3 end-to-end.

**Resultado Esperado**: Line loopback: datos recibidos retransmitidos sin reframing. 
Payload loopback: datos reframed y regenerados. Remote loopback: 
NetVanta 873 responde con line loopback via FEAC (solo C-Bit).


#### Paso `adtran_ds3_bert`: 3.2 BERT DS3 con errores (Tier 3)
**Descripción**: **Dónde:** Bit Error Rate Test en DS3 facility con loopback remoto.

**Cómo:** Errores creciendo en BERT indican problemas de cableado, 
óptica, o interferencia.

**Para qué:** Cuantificar la tasa de error y decidir si escalar a campo.

**Resultado Esperado**: BERT sin errores (0 bit errors). Contadores de interface sin incrementos.


#### Paso `adtran_t1`: 4. T1 8-Port Line Module (Tier 1)
**Descripción**: **Dónde:** Estado de servicio de tarjeta, puertos DS1, Line Buildout (LBO), 
EFM bonding, uplink identifier y timing.

**Cómo:** Tarjeta en OOS, DS1 en shutdown, LBO incorrecto, o bonding no activo.

**Para qué:** Restaurar servicio T1/EFM de acceso.

**Resultado Esperado**: Tarjeta IS. DS1s usados en IS. LBO acorde a longitud de cable. 
EFM bonding activo si aplica. Uplink identifier coincidente.


#### Paso `adtran_t1_ds1`: 4.1 DS1 Interface / LBO (Tier 1)
**Descripción**: **Dónde:** Puerto DS1 y configuración de Line Buildout.

**Cómo:** Puerto en shutdown o LBO no acorde a la distancia del cable.

**Para qué:** Asegurar señalización T1 limpia y sin errores de línea.

**Resultado Esperado**: DS1 In Service. LBO coincide con longitud de cable. Sin errores de línea.


#### Paso `adtran_t1_bonding`: 4.2 EFM Bonding en T1 (Tier 2)
**Descripción**: **Dónde:** Configuración de grupos EFM sobre múltiples DS1s.

**Cómo:** Bonding no establece, fragmentos perdidos, o throughput bajo.

**Para qué:** Maximizar ancho de banda agregado y tolerancia a falla de DS1.

**Resultado Esperado**: EFM group UP. Todos los DS1s miembros activos. Sin fragmentos perdidos.


#### Paso `adtran_rpr`: 5. RPR Line Module (Tier 1)
**Descripción**: **Dónde:** Estado de servicio de tarjeta RPR, modo Hub/Spoke, timing, 
Multicast VLAN y protección de anillo.

**Cómo:** Tarjeta en OOS, anillo abierto, multicast no inunda, o switch forzado.

**Para qué:** Restaurar la topología RPR y el tráfico de anillo.

**Resultado Esperado**: Tarjeta IS (Master) o IS Standby-Hot (Slave). Hub/Spoke correcto. 
Timing propagado. Multicast VLAN habilitada si aplica IGMP.


#### Paso `adtran_rpr_nodes`: 5.1 Añadir o Quitar nodo RPR (Tier 2)
**Descripción**: **Dónde:** Procedimiento de inserción o extracción de nodos en anillo RPR cerrado.

**Cómo:** Usar Manual Switch (MS) y Forced Switch (FS) en interfaces East/West.

**Para qué:** Evitar pérdida de tráfico al modificar la topología.

**Resultado Esperado**: Manual Switch solo aceptado si anillo cerrado y sin errores. 
Forced Switch fuerza tráfico fuera del span. Topología actualizada.


#### Paso `adtran_rpr_igmp`: 5.2 IGMP Multicast VLAN en RPR (Tier 2)
**Descripción**: **Dónde:** Multicast VLAN en el RPR Line Module del nodo Hub.

**Cómo:** Tráfico multicast downstream no llega. RPR no inunda por defecto.

**Para qué:** Habilitar la Multicast VLAN para permitir flooding de tráfico IGMP.

**Resultado Esperado**: Multicast VLAN Enabled en Hub Node. IGMP VLAN configurada en GigE SM.


#### Paso `adtran_erps`: 6. ERPS (Ethernet Ring Protection) (Tier 1)
**Descripción**: **Dónde:** Anillo ERPS sobre puertos 10 GigE del Switch Module.

**Cómo:** Interfaz ERPS no establece, nodo nuevo no visible, o pérdida de tráfico.

**Para qué:** Restaurar protección de anillo Ethernet carrier-class.

**Resultado Esperado**: Interfaz ERPS Up (no shut). West/East interfaces definidos. Hop-count habilitado en RT.


#### Paso `adtran_erps_addnode`: 6.1 Añadir nodo RT a ERPS (Tier 2)
**Descripción**: **Dónde:** Inserción de un nuevo Remote Terminal en anillo ERPS existente.

**Cómo:** Forced Switch en un extremo, conexión física del nuevo nodo, 
luego quitar FS.

**Para qué:** Expandir el anillo sin interrumpir tráfico existente.

**Resultado Esperado**: Nuevo nodo visible en topología. FS removido. Tráfico restablecido.


#### Paso `adtran_timing`: 7. System Timing (Tier 1)
**Descripción**: **Dónde:** Fuentes de timing primaria/secundaria: BITS, DS3, DS1, RPR loops, 
o interfaces 10 GigE fijas.

**Cómo:** Timing no locked, holdover, o switchover no deseado.

**Para qué:** Garantizar sincronización de red y evitar deslizamientos de trama.

**Resultado Esperado**: Primary y Secondary sources definidos y alcanzables. Locked o holdover estable.


#### Paso `adtran_timing_cot`: 7.1 Timing COT (Central Office) (Tier 2)
**Descripción**: **Dónde:** Central Office Node con fuente externa BITS o DS3.

**Cómo:** Configurar primary/secondary external con hop-count y stratum.

**Para qué:** Proveer timing de referencia al resto de la red.

**Resultado Esperado**: External primary/secondary configurados. Hop-count 0 en COT. Stratum 1.


#### Paso `adtran_timing_rt`: 7.2 Timing RT (Remote Terminal) (Tier 2)
**Descripción**: **Dónde:** Remote Terminal con timing derivado de interfaces de anillo (RPR/ERPS) 
o DS1s.

**Cómo:** LoopA/LoopB o interfaces 10 GigE como primary/secondary fixed.

**Para qué:** Sincronizar RT desde el anillo sin fuente BITS local.

**Resultado Esperado**: Primary desde LoopA/West, Secondary desde LoopB/East. Revertive hop-count habilitado.


### Tecnología: CCC / Interface Switching Troubleshooting
Total de pasos diagnósticos: **6**

#### Paso `ccc_start`: 1. Ámbito del problema CCC (Tier 1)
**Descripción**: **Dónde:** El problema puede estar en la conexión CCC local (interface-switch), en el circuito remoto (remote-interface-switch), o en el switching LSP.
**Cómo:** Conexión CCC en estado Down, Uninitialized, Wrong Encapsulation, o Disabled. Tráfico L2 no pasa aunque las interfaces estén Up.
**Cuándo:** Tras reconfiguración de CCC, migración de interfaces, o cambios de encapsulación en el AC.
**Por qué:** AC down, encapsulación mismatch, interfaces no configuradas, o LSP subyacente roto para LSP-switch.
**Para qué:** Determinar si la falla es local (AC), de configuración CCC, o de dataplane (MPLS/LSP).

**Resultado Esperado**: Conexión CCC en estado Up. Interfaces locales/remotas en Up. Encapsulación coincidente. Contadores de tráfico incrementando.

🔬 **Hipótesis Científica**: La falla del circuito CCC es causada por una sesión Targeted LDP caída entre los PEs, un mismatch en el VC-ID o tipo de encapsulación, o una interfaz de Attachment Circuit (AC) no operativa.
🛠️ **Solución Rápida (Quick Fix)**: 1. Establecer sesión Targeted LDP Established entre loopbacks de PE.
2. Corregir VC-ID y tipo de encapsulación (VLAN/Ethernet) para que coincidan exactamente en ambos extremos.
3. Asegurar que la interfaz AC esté Up/Up y en la VLAN/puerto correcto.
4. Aumentar MTU de AC y core MPLS para soportar overhead de labels (>=1504 bytes).
5. Verificar que el pseudowire esté Up con labels de VC locales y remotos en LFIB.
6. Validar conectividad L2 del cliente a través del circuito CCC.


#### Paso `ccc_down`: 2. CCC Down o No Inicializado (Tier 1)
**Descripción**: **Dónde:** Conexión CCC configurada pero no establecida.
**Cómo:** Estado UN (uninitialized), NP (not present), o Dn (down).
**Verificar:**
- `show connections interface-switch <name>` — estado exacto.
- `show configuration protocols connections` — configuración presente.
- `show interfaces <ac-interface>` — estado del AC.

**Resultado Esperado**: Conexión en estado Up. Si UN: falta configuración. Si Dn: verificar AC y encapsulación.


#### Paso `ccc_ac`: 3. Attachment Circuit (AC) Local (Tier 2)
**Descripción**: **Dónde:** Interfaz física o lógica hacia el CE en el PE local.
**Cómo:** Interface en Down/Down o errores de input/output. CE no detecta carrier.
**Verificar:**
- `show interfaces <ac-interface>` — estado físico/lógico.
- `show interfaces <ac-interface> extensive` — contadores y encapsulación.
- `show configuration interfaces <ac-interface>` — encapsulación CCC.

**Resultado Esperado**: Interface Up/Up. Encapsulación ethernet-ccc o vlan-ccc según diseño. Sin errores de CRC o input drops creciendo.


#### Paso `ccc_encap`: 4. Encapsulación Errónea (WE) (Tier 2)
**Descripción**: **Dónde:** Mismatch de encapsulación entre AC local y configuración CCC.
**Cómo:** Estado WE (wrong encapsulation) en `show connections`. El CE envía tramas que no coinciden con la encapsulación esperada.
**Verificar:**
- Encapsulación en interfaz: `ethernet-ccc`, `vlan-ccc`, `extended-vlan-ccc`.
- Coincidencia con configuración del CE (dot1q, QinQ, untagged).

**Resultado Esperado**: Encapsulación coincidente entre interfaz y CCC. Si CE usa dot1q → vlan-ccc. Si CE sin tag → ethernet-ccc.


#### Paso `ccc_lsp`: 5. LSP-Switch / MPLS Subyacente (Tier 3)
**Descripción**: **Dónde:** Conexión CCC tipo LSP-switch que depende de LSP MPLS operativo.
**Cómo:** Estado Dn o RmtDn en LSP-switch. LSP MPLS caído o no reservable.
**Verificar:**
- `show mpls lsp` — estado del LSP.
- `show rsvp session` — sesiones RSVP.
- `show connections lsp-switch` — estado del switch.

**Resultado Esperado**: LSP en estado Up. Labels MPLS instalados en mpls.0. RSVP session establecida. Path activo sin errores.


#### Paso `ccc_config`: 6. Verificar/Crear Configuración CCC (Tier 1)
**Descripción**: **Configuración mínima para interface-switch:**
```
set protocols connections interface-switch <name> 
    interface <ac-interface>.0 
    interface <remote-interface>.0 
```

**Para remote-interface-switch:**
```
set protocols connections remote-interface-switch <name> 
    interface <ac-interface>.0 
    transmit-lsp <lsp-to-remote> 
    receive-lsp <lsp-from-remote> 
```

**Resultado Esperado**: Configuración presente y sintácticamente válida. Interfaces referenciadas existen y tienen encapsulación CCC.


### Tecnología: Troubleshooting NAT
Total de pasos diagnósticos: **3**

#### Paso `nat_tshoot_start`: 1. Verificar tabla de traducciones y flujos activos (Tier 1)
**Descripción**: **Objetivo:** Confirmar si el tráfico de interés genera una sesión/traducción activa en la tabla de NAT del dispositivo.

**Detalles clave:**
- Comprobar si se instalan las tuplas de traducción: IP origen/puerto privado -> IP origen/puerto traducido -> IP destino/puerto destino.
- Si no hay sesión en la tabla, el tráfico no está llegando al dispositivo, no coincide con las reglas de NAT, o es descartado antes por políticas de seguridad o routing.

**Resultado Esperado**: Se debe visualizar la traducción activa con la correspondencia correcta de IPs origen/destino y puertos. Los contadores de paquetes/bytes de la sesión deben ir en incremento.

🔬 **Hipótesis Científica**: La falla de traducción de direcciones NAT es causada por una ACL de inside/outside mal definida, un pool de direcciones agotado, un conflicto de puertos (PAT exhaustion), o una ruta de retorno que no pasa por el mismo dispositivo NAT.
🛠️ **Solución Rápida (Quick Fix)**: 1. Clasificar correctamente interfaces como inside/outside según dirección del tráfico.
2. Ajustar ACL de inside source para que incluya las subnets privadas de interés.
3. Ampliar pool NAT o habilitar PAT (overload) si se agotan direcciones/puertos.
4. Asegurar que el tráfico de retorno sea simétrico y pase por el mismo dispositivo NAT.
5. Verificar tabla de traducciones activas y envejecimiento correcto.
6. Probar conexiones desde hosts internos y confirmar traducción exitosa.


#### Paso `nat_tshoot_exhaustion`: 2. Diagnóstico de agotamiento de puertos (Port Exhaustion / PAT Limits) (Tier 2)
**Descripción**: **Objetivo:** Detectar si el pool de NAT o la IP pública de sobrecarga se ha quedado sin puertos efímeros disponibles (normalmente 65535 puertos por IP pública, descontando los reservados/bajos, reduciendo el rango útil a unos 60000 por IP).

**Síntomas:**
- Los usuarios experimentan desconexiones intermitentes o fallas al cargar páginas web (HTTP/HTTPS requiere múltiples conexiones concurrentes).
- En los logs del sistema aparecen advertencias de "NAT port exhaustion", "allocation failure" o descartes silenciosos de paquetes con causa de error de NAT.

**Resultado Esperado**: El uso del pool de NAT o puertos debe ser inferior al 80%. No deben existir registros de descartes de puertos ni errores de "Port Exhaustion" en el buffer de logs.


#### Paso `nat_tshoot_debug`: 3. Depuración y captura de flujos en tiempo real (Flow Trace / Packet Capture) (Tier 3)
**Descripción**: **Objetivo:** Capturar o rastrear el paso del paquete de interés a través del motor del dispositivo para determinar si NAT lo modifica, lo descarta, o si el paquete de retorno no es reconocido por la sesión.

**Detalles clave:**
- Permite ver la lógica interna del motor de enrutamiento y seguridad (ej. "route lookup", "policy check", "nat translation").
- Ayuda a identificar problemas donde el firewall descarta el paquete debido a que la política de seguridad no coincide con la IP pre-NAT o post-NAT según las reglas del vendor.

**Resultado Esperado**: El log/debug de flujo debe revelar la línea donde ocurre la traducción: "NAT translation applied" o "source NAT to IP:port". Si hay descarte, indicará el motivo específico (ej. "firewall policy deny", "route lookup failed").


### Tecnología: Troubleshooting Enrutamiento Estático
Total de pasos diagnósticos: **4**

#### Paso `static_start`: 1. Definir ámbito del problema de Enrutamiento Estático (Tier 1)
**Descripción**: **Dónde:** Rutas estáticas locales no presentes en la tabla de enrutamiento (RIB) o inoperativas en el plano de forwarding (FIB).

**Cómo:** Pérdida de conectividad (ping/traceroute fallido), tráfico dirigido por la ruta por defecto en lugar de la estática, o siguiente salto reportando como inalcanzable.

**Por qué:** Interfaz de salida en shutdown, IP del siguiente salto inalcanzable, distancia administrativa más alta que otro protocolo IGP, o configuración incorrecta de la distancia administrativa.

**Para qué:** Verificar la presencia de la ruta en la RIB/FIB y determinar si el siguiente salto es físicamente alcanzable.

**Resultado Esperado**: La ruta debe figurar como activa (* en Juniper, A en Cisco, A S en MikroTik) con el siguiente salto e interfaz correcta. El ping al siguiente salto directo debe tener 100% de éxito.

🔬 **Hipótesis Científica**: La falla de enrutamiento estático es causada por una ruta configurada pero no instalada en la RIB debido a un next-hop inalcanzable, una distancia administrativa peor que una ruta dinámica, o un loop de resolución recursiva.
🛠️ **Solución Rápida (Quick Fix)**: 1. Corregir sintaxis de la ruta estática (red, máscara, next-hop o interfaz de salida).
2. Asegurar que el next-hop sea alcanzable directamente o resoluble vía IGP.
3. Ajustar distancia administrativa para que la ruta gane frente a rutas dinámicas según diseño.
4. Confirmar que la interfaz de salida esté Up/Up si se usa sintaxis de salida por interfaz.
5. Configurar track IP SLA o BFD para retiro automático si el path falla.
6. Verificar que la ruta esté instalada en RIB/FIB ('show ip route'/'show ip cef').


#### Paso `static_recursive`: 2. Diagnóstico de Siguiente Salto e Inalcanzabilidad (Tier 2)
**Descripción**: **Objetivo:** Diagnosticar fallas donde el siguiente salto de la ruta estática no está directamente conectado y no puede resolverse (recursive lookup failed).

**Detalles clave:**
- Si el router no puede resolver recursivamente el siguiente salto hacia una interfaz física de salida activa, la ruta estática se oculta de la tabla de forwarding.
- Comprobar que exista una ruta (IGP, BGP o directa) para la subred del siguiente salto.

**Resultado Esperado**: El siguiente salto debe ser resuelto recursivamente hacia una IP de tránsito directamente conectada y una interfaz física en estado UP.


#### Paso `static_floating`: 3. Rutas Estáticas Flotantes y Distancia Administrativa (Tier 2)
**Descripción**: **Objetivo:** Comprobar la precedencia de enrutamiento y el comportamiento de respaldo (flotante).

**Detalles clave:**
- Las rutas flotantes se configuran con una distancia administrativa mayor (ej: AD=200) para actuar como respaldo si el enlace principal (ej: OSPF con AD=110) cae.
- Si la ruta principal no se retira de la RIB, la flotante nunca se activa. Esto suele requerir configurar trackeo de SLA/IP SLA para verificar reachability y no solo el estado de la interfaz física.

**Resultado Esperado**: La ruta estática flotante debe permanecer inactiva (o en standby) mientras el enlace principal y su respectivo trackeo (BFD, SLA, Link Monitor) reporten estado OK. Al fallar el principal, la ruta flotante debe instalarse en la FIB en menos de 1 segundo.


#### Paso `static_ecmp`: 4. Balanceo de Carga Estático (ECMP) (Tier 3)
**Descripción**: **Objetivo:** Verificar el comportamiento de balanceo estático multipath.

**Detalles clave:**
- ECMP (Equal-Cost Multi-Path) se activa cuando se configuran múltiples rutas estáticas para el mismo destino con idéntica distancia administrativa y métrica.
- Si los caminos tienen capacidades diferentes (ancho de banda inconsistente) o si el algoritmo de hashing causa asimetría, se presentarán problemas de performance.

**Resultado Esperado**: La tabla de reenvío (FIB) debe reflejar múltiples entradas de salida activas para el prefijo de destino. El tráfico debe repartirse consistentemente según la tupla de 5 campos (IPs y puertos).


### Tecnología: RIPv2 Troubleshooting
Total de pasos diagnósticos: **4**

#### Paso `rip_start`: 1. Definir ámbito del problema RIP (Tier 1)
**Descripción**: **Dónde:** Plano de control (procesamiento de actualizaciones UDP 520, timers) y plano de datos (envío de actualizaciones multicast).

**Cómo:** Vecinos que no intercambian rutas, métricas incorrectas (hop count excedido), o caída de adyacencias tras cambios de red.

**Cuándo:** Tras cambios de direccionamiento, filtros de ACL, habilitación de autenticación, o cambio de routers de tránsito.

**Por qué:** Mismatch de autenticación, timers desincronizados, hop count mayor a 15 (métrica 16 inalcanzable), o split horizon ocultando rutas.

**Para qué:** Clasificar la falla para saber si se deben revisar adyacencias físicas, configuraciones de timers, o métricas de prefijo.

**Resultado Esperado**: Servicio RIP activo, interfaces en Up/Up y procesando paquetes en puerto UDP 520.


#### Paso `rip_neighbor`: 2. Diagnóstico de Vecinos y Autenticación RIP (Tier 1)
**Descripción**: **Objetivo:** Resolver problemas de autenticación o bloqueo de actualizaciones RIP entre vecinos.

RIPv2 no forma adyacencias de estado formal (como OSPF o BGP), sino que depende del intercambio periódico de mensajes Request/Response por el puerto UDP 520. Un desajuste de autenticación MD5 o el uso de interfaces pasivas evitará que las rutas se instalen.

**Resultado Esperado**: Actualizaciones recibidas exitosamente desde el vecino y autenticadas correctamente.


#### Paso `rip_routes`: 3. Diagnóstico de Prefijos y Métrica 16 (Poisoned) (Tier 2)
**Descripción**: **Objetivo:** Identificar la causa de rutas faltantes o rutas en estado inaccesible (hop count = 16).

En RIP, cualquier prefijo con métrica 16 es considerado inaccesible (infinito). El split horizon evita bucles de enrutamiento pero puede ocultar rutas legítimas en redes no-completamente conexas (hub-and-spoke).

**Resultado Esperado**: Rutas RIP instaladas activamente en la tabla de enrutamiento con métrica <= 15.


#### Paso `rip_timers`: 4. Sincronización y Ajuste de Timers (Tier 2)
**Descripción**: **Objetivo:** Diagnosticar la inestabilidad de rutas debido a desajustes en los timers de RIP.

RIPv2 utiliza cuatro timers principales: Update (30s), Invalid (180s), Holddown (180s) y Flush (240s). Si los timers no coinciden en todos los routers de la red, se producirá un borrado intermitente de rutas (route flapping).

**Resultado Esperado**: Timers de RIP alineados y estables, evitando borrado temporal de rutas.


### Tecnología: Troubleshooting AAA / TACACS+ / RADIUS
Total de pasos diagnósticos: **4**

#### Paso `aaa_ts_acct`: 3. Troubleshooting de Accounting y Autorización (Tier 2)
**Descripción**: **Objetivo:** Verificar que los comandos y sesiones se registran y autorizan correctamente.

**Problemas comunes:**
- Accounting records no enviados: puerto 1813 UDP bloqueado.
- Autorización fallida: usuario autenticado pero comando denegado.
- Logs AAA incompletos: buffer pequeño o nivel de log insuficiente.

**Verificar:**
- Contadores de accounting start/stop/update.
- Reglas de autorización (command sets) en servidor.

**Resultado Esperado**: Accounting records enviados. Autorización permite comandos según rol. Logs completos.


#### Paso `aaa_ts_auth`: 2. Troubleshooting de Autenticación y Fallback (Tier 2)
**Descripción**: **Objetivo:** Diagnosticar por qué un usuario no puede autenticarse.

**Problemas comunes:**
- Usuario no existe en servidor AAA.
- Fallback a local no configurado: si el servidor cae, nadie puede ingresar.
- Privilegio incorrecto: usuario autentica pero no tiene permisos.

**Verificar:**
- Method list: orden de métodos (tacacs+ local none).
- Estado de fallback cuando AAA server no responde.
- Logs de login success/failure.

**Resultado Esperado**: Autenticación exitosa con TACACS+/RADIUS. Fallback local operativo. Permisos correctos.


#### Paso `aaa_ts_doc`: 4. Documentar y Escalar (Tier 3)
**Descripción**: **Objetivo:** Registrar hallazgos y definir siguiente paso si el problema persiste.

**Acciones:**
- Recopilar capturas de TACACS+ y RADIUS.
- Documentar method lists, keys y timeouts.
- Verificar licencias de servidor AAA si aplica.

**Resultado Esperado**: Ticket documentado con evidencia técnica. Escalamiento justificado.


#### Paso `aaa_ts_start`: 1. Verificar conectividad y estado de servidores AAA (Tier 1)
**Descripción**: **Objetivo:** Confirmar que los servidores TACACS+/RADIUS son alcanzables y responden.

**Problemas comunes:**
- Servidor no alcanzable: firewall bloqueando puertos 49 (TACACS+) o 1812/1813 (RADIUS).
- Key/secret mismatch: paquetes descartados por firma incorrecta.
- Timeouts: servidor sobrecargado o ruta asimétrica.

**Verificar:**
- Ping y traceroute al servidor AAA.
- Estado de la sesión TCP/UDP en el router.
- Logs de authentication failure.

**Resultado Esperado**: Servidores AAA alcanzables. Sesiones activas. Sin timeouts.

🔬 **Hipótesis Científica**: La falla de autenticación, autorización o accounting es causada por una falta de conectividad al servidor AAA (RADIUS/TACACS+), un shared secret mismatch, o una method list mal ordenada que no permite fallback local.
🛠️ **Solución Rápida (Quick Fix)**: 1. Restaurar conectividad IP al servidor RADIUS/TACACS+ y abrir puertos 1812/1813 o 49.
2. Corregir el shared secret para que coincida exactamente (case-sensitive, sin espacios extra).
3. Configurar method list con fallback local (ej. group tacacs+ local) y aplicarla a line vty/console.
4. Verificar que el usuario/grupo exista en el servidor con privilegios correctos.
5. Habilitar accounting para exec/commands/network según requisitos de auditoría.
6. Confirmar autenticación exitosa con un usuario de prueba y revisar logs de accounting.


### Tecnología: Troubleshooting DMVPN / GETVPN
Total de pasos diagnósticos: **4**

#### Paso `dmvpn_ts_doc`: 4. Documentar y Escalar (Tier 3)
**Descripción**: **Objetivo:** Registrar hallazgos y definir siguiente paso si el problema persiste.

**Acciones:**
- Recopilar show tech-support.
- Documentar topología hub-spoke y spokes directos.
- Verificar compatibilidad de firmware para DMVPN/GETVPN.

**Resultado Esperado**: Ticket documentado con evidencia técnica. Escalamiento justificado.


#### Paso `dmvpn_ts_ipsec`: 2. Troubleshooting IPSec y GDOI (GETVPN) (Tier 2)
**Descripción**: **Objetivo:** Diagnosticar fallas de cifrado IPSec o distribución de claves GDOI.

**Problemas comunes:**
- IPSec SA no establecida: IKEv2 failure, PSK mismatch, certificado expirado.
- GDOI rekey failure: KS no alcanzable, GMs sin claves actualizadas.
- NAT-T no negociado: puerto 4500 UDP bloqueado.

**Verificar:**
- Fase 1 (IKE) y Fase 2 (IPSec) establecidas.
- SAs instaladas en dataplane.
- GDOI rekey messages recibidos.

**Resultado Esperado**: IKEv2 SA establecida. IPSec SA installed. GDOI keys sincronizadas.


#### Paso `dmvpn_ts_routing`: 3. Verificar Routing sobre DMVPN (Tier 2)
**Descripción**: **Objetivo:** Confirmar que el protocolo de routing (EIGRP/OSPF/BGP) funciona sobre el túnel.

**Problemas comunes:**
- Neighbor no establecido: multicast/broadcast no permitido en mGRE.
- Split-horizon: EIGRP no readvertise rutas por misma interfaz.
- NHRP redirect/cache miss: tráfico hub-spoke subóptimo.

**Verificar:**
- Vecinos de routing en interfaz Tunnel.
- Tabla de rutas con next-hop correcto.
- NHRP shortcut switching.

**Resultado Esperado**: Vecinos EIGRP/OSPF/BGP establecidos sobre túnel. Rutas DMVPN en RIB. Spoke-to-spoke funcional.


#### Paso `dmvpn_ts_start`: 1. Verificar estado de túnel mGRE y NHRP (Tier 1)
**Descripción**: **Objetivo:** Confirmar que el túnel mGRE está UP y NHRP está registrando peers.

**Problemas comunes:**
- Túnel DOWN: interface source no alcanzable o NHRP mapping incomplete.
- NHRP registration failed: NBMA address no responde.
- MTU issues: mGRE + IPSec overhead supera 1500 bytes.

**Verificar:**
- Estado de interfaz Tunnel.
- Registros NHRP (NHS, NHC).
- Reachability NBMA (underlay IP).

**Resultado Esperado**: Túnel UP. NHRP registration successful. Peers DMVPN visibles.

🔬 **Hipótesis Científica**: La falla de conectividad en DMVPN es causada por un registro NHRP fallido en el Hub, una asociación de seguridad IPsec no establecida (IKEv1/v2 failure), o una falla en el enrutamiento dinámico sobre el túnel mGRE (OSPF/EIGRP/BGP no forma adyacencias).
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar registro NHRP en el Hub ('show ip nhrp') y corregir tunnel source/destination si es necesario.
2. Restablecer asociaciones ISAKMP/IPsec verificando políticas criptográficas, PSK y NAT-T (UDP 4500).
3. Habilitar routing dinámico (OSPF/EIGRP/BGP) sobre la interfaz de túnel mGRE en Hub y Spokes.
4. Confirmar que el túnel mGRE esté Up/Up con modo multipoint y tunnel key coincidente.
5. Excluir tráfico GRE/IPsec de la traducción NAT en los Spokes.
6. Validar conectividad Spoke-to-Spoke y Hub-to-Spoke tras los cambios.


### Tecnología: Troubleshooting EIGRP
Total de pasos diagnósticos: **4**

#### Paso `eigrp_ts_doc`: 4. Documentar y Escalar (Tier 3)
**Descripción**: **Objetivo:** Registrar hallazgos y definir siguiente paso si el problema persiste.

**Acciones:**
- Recopilar show tech-support.
- Documentar topología EIGRP y métricas.
- Verificar estabilidad de enlaces físicos.

**Resultado Esperado**: Ticket documentado con evidencia técnica. Escalamiento justificado.


#### Paso `eigrp_ts_sia`: 3. Stuck-In-Active (SIA) y Convergencia (Tier 3)
**Descripción**: **Objetivo:** Diagnosticar SIA y mejorar tiempos de convergencia.

**Problemas comunes:**
- SIA: router no recibe reply de successor dentro del tiempo activo.
- Causas: enlace inestable, vecino congestionado, o timer SIA muy bajo.

**Verificar:**
- Logs de SIA.
- Timers active-time y hello-interval.
- Calidad de enlaces (packet loss, delay).

**Resultado Esperado**: Sin SIA activo. Convergencia rápida. Timers ajustados a red.


#### Paso `eigrp_ts_start`: 1. Verificar vecinos EIGRP y formación de adyacencias (Tier 1)
**Descripción**: **Objetivo:** Confirmar que los vecinos EIGRP están en estado estable.

**Problemas comunes:**
- AS number mismatch.
- K-values mismatch.
- Authentication key mismatch.
- Hello/ Hold timers mismatch.
- Passive interface.

**Verificar:**
- Interfaces en EIGRP process.
- Configuración de AS y K-values.

**Resultado Esperado**: Vecinos EIGRP en estado estable. AS y K-values coincidentes. Interfaces activas.

🔬 **Hipótesis Científica**: La falla de enrutamiento EIGRP es causada por un mismatch de AS o K-Values, bloqueo del tráfico multicast EIGRP (224.0.0.10), una interfaz pasiva configurada por error, o un estado Stuck-In-Active (SIA) que indica inestabilidad en la topología.
🛠️ **Solución Rápida (Quick Fix)**: 1. Corregir el número de AS para que coincida exactamente en todos los routers EIGRP del dominio.
2. Sincronizar K-Values (métrica) en todos los vecinos.
3. Verificar que las network statements usen wildcard mask correcta y capturen interfaces de tránsito.
4. Eliminar 'passive-interface' de enlaces troncales que deben formar adyacencias.
5. Asegurar que la autenticación MD5/key-chain sea idéntica en ambos extremos.
6. Investigar y resolver eventos Stuck-In-Active (SIA) estabilizando links o aumentando active-time.


#### Paso `eigrp_ts_topo`: 2. Verificar Topología y Métricas (Tier 2)
**Descripción**: **Objetivo:** Diagnosticar rutas faltantes o métricas inesperadas.

**Problemas comunes:**
- Ruta no en topology table: filtro de distribución o offset-list.
- Métrica infinita: ancho de banda mal configurado en interfaz.
- Router ID duplicado.

**Verificar:**
- EIGRP topology para prefijo problemático.
- Factores de métrica (bandwidth, delay, load, reliability).
- Distribución de rutas (distribute-list, route-map).

**Resultado Esperado**: Rutas EIGRP en topology y RIB. Métricas coherentes. Sin distribute-lists bloqueando.


### Tecnología: Troubleshooting GPON OLT (Core) - ONT / FTTH
Total de pasos diagnósticos: **9**

#### Paso `fiber_ont_ts_doc`: 6. OLT: Documentar y Escalar (Tier 1)
**Descripción**: **Dónde:** En la OLT, recolectando toda la evidencia técnica antes de escalar.

**Cómo:** Exportar running-config relevante, capturar alarmas, guardar outputs de comandos de verificación.

**Cuándo:** Cuando el problema persiste después de todas las verificaciones de Tier 1-3, o requiere cambio físico (fibra, ONT, splitter).

**Por qué:** Un ticket bien documentado acelera la resolución. Evita que Tier 2/3 repitan los mismos pasos.

**Para qué:** Justificar escalamiento con evidencia técnica sólida. Facilitar auditoría posterior.

**Información mínima a documentar desde OLT:**
- SN/LOID de ONT y ID de posición.
- Niveles ópticos (RX/TX) en ambos sentidos.
- Estado de ONT (Active/Offline/Uncfg).
- Service-ports/bridges configurados con VLANs.
- MAC addresses aprendidas por VLAN.
- Alarmas activas en puerto PON.
- Capturas de running-config relevante.

**Resultado Esperado**: Ticket documentado con evidencia técnica completa desde OLT. Escalamiento justificado a Tier 3 o campo.


#### Paso `fiber_ont_ts_pppoe`: 3. OLT: Troubleshooting PPPoE (Tier 2)
**Descripción**: **Dónde:** En la OLT, verificando service-ports/bridges de datos y MAC learning en VLAN.

**Cómo:** Desde la OLT se verifica si la ONT envía tráfico PPPoE (MAC origen aprendida en VLAN).
La OLT no termina PPPoE, pero puede confirmar que el L2 path entre ONT y BNG está activo.

**Cuándo:** Abonado reporta "no hay Internet", router ONT no obtiene IP, o sesión PPPoE cae constantemente.

**Por qué:** PPPoE falla si: VLAN incorrecta, service-port caído, MAC no aprendida, BNG no responde,
o credenciales incorrectas (esto último solo visible desde logs de BNG, no desde OLT).

**Para qué:** Aislar si el problema es en la red GPON (OLT/ONT) o en la red agregación/BNG.

**Verificación desde OLT:**
- Service-port/bridge activo en OLT.
- MAC address de ONT aprendida en VLAN de datos.
- Contadores de tráfico incrementando en service-port.
- Sin drops por ACL o QoS.

**Resultado Esperado**: Service-port/bridge de datos activo. MAC de ONT aprendida. Tráfico PPPoE fluyendo entre ONT y BNG.


#### Paso `fiber_ont_ts_ranging`: 2. OLT: Ranging y Estado de la ONT (Tier 1)
**Descripción**: **Dónde:** En la OLT, verificando proceso de ranging y estado de registro de la ONT.

**Cómo:** Comandos que muestran estado de ONT (Uncfg/Logging/Ranging/Active/Offline) y detalles de EqD.

**Cuándo:** ONT aparece en estado Logging, Ranging, o Uncfg. ONT se registra pero cae inmediatamente.

**Por qué:** Ranging falla si: SN incorrecto, LOID/password erróneo, niveles ópticos malos,
o perfil de línea incompatible con modelo de ONT.

**Para qué:** Identificar si la ONT logra sincronizar físicamente pero falla en el registro lógico.

**Estados típicos ONT desde OLT:**
- Uncfg: ONT no registrada. Solución: registrar SN/LOID.
- Logging: ONT envía SN pero no está autorizada.
- Ranging: Sincronizando EqD. Si se queda aquí: problema óptico o timing.
- Active: ONT registrada y sincronizada. Debe pasar a Working.
- Offline: ONT se desregistró. Revisar fibra o reboot.

**Resultado Esperado**: ONT en estado Active/Working. Ranging completado. SN/LOID correctos. Sin duplicados de SN en el PON.


#### Paso `fiber_ont_ts_start`: 1. OLT: Diagnóstico Layer 1 - ODN y Niveles Ópticos (Tier 1)
**Descripción**: **Dónde:** En la OLT, verificando puerto PON y estado óptico de la ONT.

**Cómo:** Comandos de OLT que muestran estado de ONT, potencia recibida (RX), y alarmas ópticas.

**Cuándo:** ONT en estado Offline, LOS (Loss of Signal), o cuando el abonado reporta "no hay Internet".

**Por qué:** GPON requiere presupuesto óptico estricto. Si RX OLT < -28 dBm, la ONT no puede sincronizar.
Causas comunes: fibra rota, conector sucio, splitter incorrecto, macrobending.

**Para qué:** Determinar si el problema es físico (Layer 1) antes de investigar configuración (Layer 2/3).

**Alarmas comunes desde OLT:**
- LOS (Loss of Signal): ONT apagada o fibra rota.
- LOFi (Loss of Frame): ONT encendida pero no sincroniza.
- DGi (Drift of GEM): Problema de timing/EqD.
- SDi (Signal Degraded): Nivel óptico bajo pero presente.

**Resultado Esperado**: ONT en estado Active/Online. Niveles ópticos dentro de rango (-8 a -28 dBm en OLT). Sin alarmas LOS/LOFi.

🔬 **Hipótesis Científica**: La falla de servicio GPON/ONT es causada por un nivel de potencia óptica fuera de rango, una ONT en estado distinto a O5 (Operativo), un error en la provisión OMCI, o un problema de autenticación PPPoE/SIP en la capa de servicio.
🛠️ **Solución Rápida (Quick Fix)**: 1. Ajustar potencia óptica dentro del rango GPON (-8 a -27 dBm) limpiando conectores o cambiando splitter/atenuación.
2. Verificar que la ONT alcance estado O5 (Online/Operativo) en la OLT; si no, revisar ranging y serial/LOID.
3. Registrar correctamente el número de serie / LOID de la ONT en la base de datos de la OLT.
4. Completar provisión OMCI: GEM ports, T-CONTs, VLANs y perfiles de servicio asignados.
5. Validar capa de servicio (PPPoE activo, VLAN correcta, SIP registered) con el softswitch.
6. Confirmar que el cliente reciba servicio de datos/voz con pruebas end-to-end.


#### Paso `fiber_ont_ts_voip`: 4. OLT: Troubleshooting VoIP (SIP / RTP) (Tier 2)
**Descripción**: **Dónde:** En la OLT, verificando service-ports/bridges de voz y estado SIP desde OLT (si OMCI disponible).

**Cómo:** La OLT verifica L2 path de VLAN de voz. Si OMCI soportado, también consulta estado SIP de ONT.
Si no, se delega troubleshooting a softswitch/IMS (verificar registro SIP desde allá).

**Cuándo:** Abonado reporta "no hay tono", "no puedo llamar", o teléfono conectado pero mudo.

**Por qué:** VoIP falla si: VLAN de voz incorrecta, service-port bloqueado, softswitch no responde,
credenciales SIP erróneas, o RTP bloqueado por firewall. Desde OLT se puede verificar L2 y QoS.

**Para qué:** Aislar si el problema es transporte (GPON/OLT) o aplicación (SIP server/IMS).

**Verificación desde OLT:**
- Service-port/bridge de voz activo (VLAN 300 típicamente).
- CoS/Queue correcto (voz en prioridad máxima).
- MAC de ONT en VLAN de voz.
- Si OMCI: estado SIP mostrando Registered/Online.

**Resultado Esperado**: Service-port/bridge de voz activo. ONT registrada en softswitch (SIP 200 OK). Tono de marcado presente. Llamada de prueba exitosa.


#### Paso `fiber_ont_ts_wifi`: 5. OLT: Troubleshooting WiFi (Tier 2)
**Descripción**: **Dónde:** En la OLT, verificando service-port de datos que transporta tráfico WiFi.

**Cómo:** La OLT no gestiona WiFi directamente (es función de la ONT/CPE).
Pero verifica que el L2 path de datos esté activo para que el tráfico WiFi llegue al router.
Si OMCI soportado, la OLT puede consultar estado WiFi de la ONT.

**Cuándo:** Abonado reporta "WiFi no aparece", "no puedo conectarme", o "Internet lento solo en WiFi".

**Por qué:** WiFi es un problema de capa física RF (frecuencia, interferencia, distancia).
Desde OLT solo se puede confirmar que la conectividad Ethernet subyacente funciona.
Causas típicas: canal saturado, interferencia de vecinos, paredes gruesas, ONT en closet mal ubicada.

**Para qué:** Descartar que el problema sea de la red GPON/OLT antes de enviar técnico a revisar WiFi localmente.

**Verificación desde OLT:**
- Service-port de datos activo y con tráfico.
- MAC del router/ONT aprendida.
- Si OMCI: SSID visible, clientes asociados.
- Contadores de error bajos en service-port.

**Resultado Esperado**: Service-port de datos activo. Tráfico fluyendo. Si problema persiste: causas RF locales (canal, distancia, interferencia).


#### Paso `fiber_ont_ts_zhone_bridge`: Zhone MXK: Bridges y VLANs (Tier 1)
**Descripción**: **Dónde:** En OLT Zhone MXK, verificando bridges, VLANs y SLANs asignados a la ONU.

**Cómo:** Use "bridge show" para ver todos los bridges. Use "bridge show slan <slan>" para filtrar por SLAN. Use "bridge show onu tls slan <slan>" para verificar TLS específico.

**Para qué:** Confirmar que los service-ports/bridges están configurados correctamente y que la MAC del CPE está aprendida.

**Resultado Esperado**: Bridges UP con SLAN/VLAN correctos. MAC del CPE aprendida en la VLAN de servicio. Sin contadores de error creciendo.


#### Paso `fiber_ont_ts_zhone_delete`: Zhone MXK: Borrar y Migrar ONU (Tier 2)
**Descripción**: **Dónde:** En OLT Zhone MXK, eliminando o migrando una ONU.

**Cómo:** Use "onu delete <slot/pom/ont>" para eliminar la ONU completamente (requiere que no tenga bridges activos). Use "onu clear <slot/pom/ont>" para desvincular el SN actual y poder re-registrar con otro. Use "onu set <slot/pom/ont> meprof <perfil> <ont-id>" para registrar nueva ONU.

**Para qué:** Reemplazar una ONU defectuosa o reutilizar una posición para otro abonado.

**Resultado Esperado**: ONU eliminada o migrada exitosamente. Nueva ONU registrada con SN correcto y estado Active/Online.


#### Paso `fiber_ont_ts_zhone_onu_status`: Zhone MXK: Estado y Potencia de ONU (Tier 1)
**Descripción**: **Dónde:** En OLT Zhone/DASAN MXK, verificando estado de ONT/ONU y potencias ópticas.

**Cómo:** Use "onu show" para listar todas las ONUs del PON. Use "onu show <slot/pom/ont>" para detalles específicos. Use "onu power show" para niveles ópticos RX/TX.

**Para qué:** Determinar si la ONT está registrada, su estado operativo, y si los niveles ópticos están dentro de rango.

**Resultado Esperado**: ONU registrada con serial number válido. Estado operativo. RX OLT entre -8 y -28 dBm. Sin alarmas LOS/LOFi.


### Tecnología: Troubleshooting IPv6
Total de pasos diagnósticos: **4**

#### Paso `ipv6_ts_auto`: 3. Troubleshooting SLAAC / DHCPv6 / RA (Tier 2)
**Descripción**: **Objetivo:** Diagnosticar problemas de asignación de direcciones IPv6 en hosts.

**Problemas comunes:**
- Host no recibe RA: RA suppress habilitado o firewall bloqueando ICMPv6.
- DHCPv6 no asigna prefijo: pool agotado o relay mal configurado.
- DAD falla: dirección duplicada detectada.

**Verificar:**
- RA transmitidos en interfaz LAN.
- DHCPv6 relay/solicitudes.
- Estado de autoconfiguración en host.

**Resultado Esperado**: RA enviados/recibidos. DHCPv6 leases asignados. SLAAC funcional. Sin DAD conflicts.


#### Paso `ipv6_ts_doc`: 4. Documentar y Escalar (Tier 3)
**Descripción**: **Objetivo:** Registrar hallazgos y definir siguiente paso si el problema persiste.

**Acciones:**
- Recopilar captures ICMPv6 y DHCPv6.
- Documentar asignación de prefijos y pools.
- Verificar compatibilidad de firmware IPv6.

**Resultado Esperado**: Ticket documentado con evidencia técnica. Escalamiento justificado.


#### Paso `ipv6_ts_routing`: 2. Troubleshooting Routing IPv6 (Tier 2)
**Descripción**: **Objetivo:** Diagnosticar rutas IPv6 faltantes o incorrectas.

**Problemas comunes:**
- Ruta IPv6 no en RIB: mejor AD desde IPv4 o política de routing.
- Next-hop no alcanzable en IPv6 pero sí en IPv4.
- MP-BGP no negocia address-family IPv6.

**Verificar:**
- Tabla de rutas IPv6.
- Protocolo de routing IPv6 activo (OSPFv3, ISIS, BGP).
- Reachability de next-hop IPv6.

**Resultado Esperado**: Rutas IPv6 en RIB. OSPFv3/IS-IS/BGP vecinos establecidos. Next-hop alcanzable.


#### Paso `ipv6_ts_start`: 1. Verificar conectividad IPv6 básica y Neighbor Discovery (Tier 1)
**Descripción**: **Objetivo:** Confirmar que IPv6 está habilitado y hay conectividad de capa 2/3.

**Problemas comunes:**
- IPv6 no habilitado en interfaz.
- Neighbor Discovery (ND) falla: RA no recibidos o NS/NA bloqueados.
- Duplicate Address Detection (DAD) falla: dirección ya en uso.

**Verificar:**
- Dirección IPv6 en interfaz.
- Vecinos IPv6 en ND cache.
- Ping a gateway link-local y global.

**Resultado Esperado**: Interfaz con IPv6 global/link-local. Vecinos en ND cache. Ping exitoso.

🔬 **Hipótesis Científica**: La falla de conectividad IPv6 es causada por una falla en el Neighbor Discovery Protocol (NDP), una ruta faltante en la tabla de enrutamiento IPv6, o una configuración incorrecta de autoconfiguración (SLAAC/DHCPv6) en el borde de red.
🛠️ **Solución Rápida (Quick Fix)**: 1. Habilitar IPv6 globalmente y en las interfaces de interés.
2. Resolver fallas de NDP verificando que ICMPv6 no esté bloqueado por ACLs/firewall host.
3. Completar el Neighbor Cache eliminando entradas FAILED o verificando segmento L2/VLAN correcto.
4. Agregar ruta estática o dinámica (OSPFv3/IS-IS/MP-BGP) hacia el destino, incluyendo ::/0 si aplica.
5. Corregir prefijo anunciado por SLAAC (Router Advertisement) para que coincida con la subnet del segmento.
6. Validar conectividad end-to-end con ping6 y verificar que el cliente tenga GUA operativa.


### Tecnología: Troubleshooting PBR (Policy-Based Routing)
Total de pasos diagnósticos: **3**

#### Paso `pbr_ts_doc`: 3. Documentar y Escalar (Tier 3)
**Descripción**: **Objetivo:** Registrar hallazgos y definir siguiente paso si el problema persiste.

**Acciones:**
- Recopilar captures y CEF entries.
- Documentar route-maps y ACLs.
- Verificar escalabilidad de PBR (número de rutas).

**Resultado Esperado**: Ticket documentado con evidencia técnica. Escalamiento justificado.


#### Paso `pbr_ts_forward`: 2. Verificar Forwarding PBR (Tier 2)
**Descripción**: **Objetivo:** Confirmar que el tráfico matched se forwarda por el next-hop de PBR y no por la ruta normal.

**Problemas comunes:**
- PBR no installado en CEF/FIB.
- Next-hop down pero ruta normal sigue funcionando (fail-open).
- Recursión: next-hop resuelto por ruta default.

**Verificar:**
- CEF entry para prefijo matched.
- Contadores de PBR.

**Resultado Esperado**: CEF/FIB con next-hop PBR. Contadores incrementando. Tráfico matched steerado correctamente.


#### Paso `pbr_ts_start`: 1. Verificar Route-Map y Matching (Tier 1)
**Descripción**: **Objetivo:** Confirmar que el route-map está configurado y aplicado a la interfaz correcta.

**Problemas comunes:**
- Route-map no aplicado en interfaz (ip policy route-map).
- ACL/match no coincide con tráfico real.
- Set next-hop no alcanzable.

**Verificar:**
- Route-map sequence y condiciones.
- Aplicación en interfaz inbound.

**Resultado Esperado**: Route-map aplicado en interfaz. Matches correctos. Next-hop alcanzable.

🔬 **Hipótesis Científica**: La falla de desvío de tráfico por Policy-Based Routing es causada por una ACL de match que no captura el tráfico esperado, un next-hop inalcanzable o caído en la política, o la aplicación del route-map en la interfaz de entrada incorrecta.
🛠️ **Solución Rápida (Quick Fix)**: 1. Verificar que el route-map esté aplicado en ingress de la interfaz de entrada ('show ip policy interface').
2. Corregir la ACL de match para que capture el tráfico de origen/destino esperado.
3. Asegurar que el next-hop o interface de salida de PBR estén Up y alcanzables.
4. Usar 'set ip next-hop' para forzar el path obligatorio, o 'set ip default next-hop' solo como fallback según diseño.
5. Evitar que rutas por defecto o BGP sobreescriban PBR para el destino.
6. Probar con tráfico de prueba y traceroute para confirmar que sigue el path PBR deseado.


### Tecnología: Troubleshooting SD-WAN
Total de pasos diagnósticos: **3**

#### Paso `sdwan_ts_commit`: 3. Documentar findings SDWAN (Tier 1)
**Descripción**: Documentar y aplicar fixes.

**Resultado Esperado**: Persistido.


#### Paso `sdwan_ts_lsdb`: 2. Verificar LSDB y RIB de SDWAN (Tier 2)
**Descripción**: **Objetivo:** Verificar que la base de datos y la tabla de routing están correctas.

**Resultado Esperado**: LSDB y RIB consistentes. Rutas instaladas.


#### Paso `sdwan_ts_start`: 1. Verificar estado básico de SDWAN (Tier 1)
**Descripción**: **Objetivo:** Diagnosticar problemas comunes de sdwan.

**Problemas comunes:**
- Control connection down: TLOC no registrado.
- OMP peer down: certificados o IP pública bloqueada.
- SLA steering no funciona: thresholds mal configurados.
- Traffic misclassified: app-list o DPI no identifica app.

**Resultado Esperado**: Estado verificado. Problema identificado.

🔬 **Hipótesis Científica**: La falla de conectividad overlay o el rendimiento degradado en SD-WAN es causado por una pérdida de conexiones de control hacia los orquestadores (vManage/vSmart/vBond), fallas en los túneles IPsec de datos (BFD flaps), o políticas de App-Aware Routing que desvían el tráfico por enlaces degradados.
🛠️ **Solución Rápida (Quick Fix)**: 1. Restaurar conectividad de control DTL/TLS del Edge hacia vBond/vManage/vSmart (rutas, certificados, puertos 12346/12366).
2. Estabilizar túneles IPsec de datos (BFD) verificando calidad de enlaces WAN y NAT/firewall intermedios.
3. Ajustar thresholds de App-Aware Routing (latencia/jitter/pérdida) a valores realistas según SLA.
4. Verificar que los colores/transportes estén asignados correctamente a cada TLOC.
5. Revisar tabla OMP para asegurar que los prefijos de servicio se anuncian y reciben con next-hop TLOC válido.
6. Confirmar que el Edge muestra conexiones de control Up y métricas BFD dentro de SLA.


### Tecnología: Troubleshooting Switch L2
Total de pasos diagnósticos: **3**

#### Paso `switch_l2_ts_commit`: 3. Documentar findings SWITCH_L2 (Tier 1)
**Descripción**: Documentar y aplicar fixes.

**Resultado Esperado**: Persistido.


#### Paso `switch_l2_ts_lsdb`: 2. Verificar LSDB y RIB de SWITCH_L2 (Tier 2)
**Descripción**: **Objetivo:** Verificar que la base de datos y la tabla de routing están correctas.

**Resultado Esperado**: LSDB y RIB consistentes. Rutas instaladas.


#### Paso `switch_l2_ts_start`: 1. Verificar estado básico de SWITCH_L2 (Tier 1)
**Descripción**: **Objetivo:** Diagnosticar problemas comunes de switch_l2.

**Problemas comunes:**
- VLAN mismatch: access port en VLAN equivocada.
- Trunk no pasa VLANs: allowed VLAN list o native VLAN mismatch.
- LAG no forma: LACP mode mismatch o port speed diferente.
- MAC flapping: loop o BPDU issue.

**Resultado Esperado**: Estado verificado. Problema identificado.

🔬 **Hipótesis Científica**: La falla de conmutación L2 es causada por una tabla CAM llena (MAC flapping), un mismatch de VLAN nativa o tagged en un enlace trunk, una negociación LACP fallida, o un loop de Capa 2 no detectado por Spanning Tree.
🛠️ **Solución Rápida (Quick Fix)**: 1. Eliminar loops físicos o configurar STP/RSTP/MSTP correctamente para resolver MAC flapping.
2. Alinear VLAN nativa y VLANs permitidas en ambos extremos de los trunks.
3. Corregir negociación LACP asegurando modos compatibles y parámetros idénticos en miembros del EtherChannel.
4. Resolver errores físicos (CRC, runts, giants) cambiando cables/SFPs o ajustando dúplex/velocidad.
5. Verificar que Spanning Tree no bloquee enlaces activos inesperadamente.
6. Validar conectividad L2 entre hosts de la misma VLAN tras los cambios.


### Tecnología: Troubleshooting con Wireshark / tcpdump
Total de pasos diagnósticos: **8**

#### Paso `pcap_bpf`: 2. Filtros BPF (Berkeley Packet Filter) — tcpdump (Tier 1)
**Descripción**: **Dónde:** Filtros de captura en tcpdump / sniffer del router. Aplican en el kernel
antes de escribir al archivo (eficiente).

**Granularidad:**
- Host / red: host 10.1.1.1, net 10.1.1.0/24, src host, dst host.
- Puerto: port 179, src port 53, dst port 443, portrange 10000-20000.
- Protocolo: icmp, tcp, udp, proto 89 (OSPF), proto 112 (VRRP).
- MPLS: mpls (cualquier paquete MPLS).
- VLAN: vlan 100, vlan 100 && icmp.
- VXLAN: udp port 4789.
- PPPoE: pppoes (session), pppoe (discovery).
- EVPN: tcp port 179 && bgp (requiere decodificación post-captura).
- Combinados: "host <ip> and port 179", "net 10.0.0.0/8 and not port 22".

**Errores comunes:**
- Filtro mal escrito (syntax error) → tcpdump no inicia.
- Filtro demasiado restrictivo → se pierde tráfico contextual (ACKs, keepalives).
- Filtro por aplicación (bgp.type == 2) como BPF → inválido; eso es display filter de Wireshark.

**Para qué:** Aislar tráfico relevante sin perder contexto, reduciendo tamaño de archivo y CPU.

**Resultado Esperado**: Filtros BPF sintácticamente válidos. tcpdump inicia sin errores.
Tráfico capturado coincide con el filtro aplicado. Sin dropped by kernel.
Archivo de captura con tamaño razonable (no incluye tráfico no deseado).


#### Paso `pcap_display`: 3. Display Filters y Análisis Post-Captura (Wireshark / tshark) (Tier 2)
**Descripción**: **Dónde:** Filtros de visualización en Wireshark GUI o tshark CLI. Se aplican DESPUÉS de la captura.

**Granularidad de Display Filters:**
- IP/MAC: ip.addr == 10.1.1.1, eth.src == 00:11:22:33:44:55.
- Puerto: tcp.port == 179, udp.port == 53.
- Protocolo: bgp, ospf, mpls, bfd, dhcp, pppoe, vxlan, evpn.
- BGP: bgp.type == 1 (OPEN), bgp.type == 2 (UPDATE), bgp.type == 3 (NOTIFICATION), bgp.type == 4 (KEEPALIVE).
- MPLS: mpls.label == 16001, mpls.exp == 5.
- OSPF: ospf.msg.hello, ospf.msg.dbd, ospf.msg.lsr, ospf.msg.lsu, ospf.msg.lsack.
- EVPN: bgp.nlri.evpn.route_type == 2 (MAC/IP).

**tshark campos útiles:**
- tshark -r capture.pcap -Y "bgp.type == 2" -T fields -e bgp.update.path_attributes.as_path.
- tshark -r capture.pcap -q -z conv,tcp (conversaciones TCP).
- tshark -r capture.pcap -q -z io,stat,1 (estadísticas por segundo).

**Para qué:** Aislar mensajes específicos de protocolo sin re-capturar, y extraer campos
programáticamente para correlación con logs del router.

**Resultado Esperado**: Display filters aplicados correctamente. Wireshark decodifica protocolos sin errores.
tshark extrae campos esperados. Conversaciones y estadísticas coherentes con el tráfico observado.
Archivo de captura completo (no truncado).


#### Paso `pcap_export`: 8. Exportación, Almacenamiento y Correlación con Logs (Tier 1)
**Descripción**: **Dónde:** Transferencia de archivos .pcap desde el router/switch hacia estación de análisis.

**Métodos:**
- TFTP/FTP/SCP desde router hacia servidor.
- Exportación a USB / flash local.
- Streaming en tiempo real (MikroTik streaming-server, ERSPAN).

**Correlación:**
- Comparar timestamps de captura con logs del router (syslog / show log messages).
- Identificar el primer paquete BGP UPDATE descartado por policy (ruta no aparece en RIB).
- Verificar que los keepalives BFD en captura coinciden con los timers de la configuración.

**Para qué:** Preservar evidencia del troubleshooting y correlacionar eventos de data plane
con eventos de control plane.

**Resultado Esperado**: Capturas exportadas y accesibles en estación de análisis. Timestamps coherentes con logs del router.
Sin pérdida de paquetes durante exportación. Archivos con checksums verificados (md5/sha256).
Evidencia almacenada de forma segura para auditoría post-mortem.


#### Paso `pcap_hw`: 7. Captura en Hardware / Port-Mirror / ERSPAN (Tier 3)
**Descripción**: **Dónde:** Switches (SPAN/RSPAN), routers con ASIC/NP (Juniper monitor traffic en PFE,
Cisco EPC en ASIC, Fortinet NP sniffer, MikroTik sniffer en hardware).

**Técnicas:**
- SPAN / RSPAN: Puerto del switch duplica tráfico hacia puerto de captura.
- ERSPAN: Encapsulación GRE de tráfico SPAN sobre IP para transporte remoto.
- Port-mirror en Juniper MX: set forwarding-options port-mirror.
- Fortinet NP sniffer: diagnose sniffer packet con filtro en NP (aceleración por hardware).
- Cisco EPC: monitor capture con match en hardware (no CPU).

**Precauciones:**
- SPAN en switch puede descartar tráfico si la interfaz de destino es más lenta que la fuente.
- ERSPAN añade headers GRE; Wireshark lo decodifica automáticamente.
- Captura en hardware ASIC puede no ver tráfico de control plane (CPU-generated).

**Para qué:** Capturar tráfico a línea rate sin impactar CPU del router/switch.

**Resultado Esperado**: Tráfico reflejado correctamente en puerto de captura / ERSPAN tunnel.
Sin drops en SPAN destino. Headers GRE decodificados en Wireshark.
ASIC/NP sniffer no impacta CPU de control plane (< 10% incremento).


#### Paso `pcap_integrity`: 6. Verificación de Integridad de Paquetes (Tier 3)
**Descripción**: **Dónde:** Análisis de checksums IP/TCP/UDP, tamaños de frame, fragmentación, TTL,
y retransmisiones TCP.

**Verificaciones granulares:**
- IP checksum: Wireshark marca [Checksum: Bad] si el offload de NIC lo invalida.
- TCP checksum: Similar; offload en NIC/SmartNIC puede causar "bad checksum" en captura.
- UDP checksum: Verificar en DHCP, BFD, VXLAN.
- MTU / Fragmentación: Flags DF/MF, Fragment Offset. Ping con DF-bit + size grande.
- TTL: ip.ttl == 1 en OSPF/BFD; si es < 2 en paquetes de control, hay loop.
- TCP retransmisiones: tcp.analysis.retransmission indica pérdida en la red.
- TCP zero-window: tcp.window_size_value == 0 indica receptor saturado.
- Out-of-order: tcp.analysis.out_of_order indica paths asimétricos o micro-cortes.

**Para qué:** Descartar corrupción L2/L3 como causa de problemas de protocolo.
Distinguir entre errores reales y artefactos de hardware offload.

**Resultado Esperado**: Sin checksums inválidos (salvo por hardware offload, que es normal en capturas locales).
Sin fragmentación inesperada (DF bit set y sin fragmentation). TTL consistente.
Sin retransmisiones masivas ni zero-windows. Tamaños de frame dentro del MTU esperado.


#### Paso `pcap_perf`: 5. Troubleshooting de Performance de Captura (Tier 2)
**Descripción**: **Dónde:** Buffer de captura (kernel), CPU del dispositivo, disco/flash donde se escribe,
y colas de control plane del router.

**Síntomas:**
- tcpdump reporta "dropped by kernel" → buffer insuficiente (-B).
- CPU > 80% durante captura → sniffer en interface de alta velocidad sin filtro.
- Archivo de captura truncado → flash llena o snaplen insuficiente.
- Paquetes con timestamps erráticos → buffer de NIC con jitter.

**Verificaciones granulares:**
- Buffer: tcpdump -B 4096 (aumentar kernel buffer).
- Sampling: usar sampleo 1:N en interfaces de 10G+ si solo se necesitan estadísticas.
- Escritura: escribir en RAM (/tmp, /var/tmp) en routers, no en flash lenta.
- CPU: monitorear RE/RP/CP durante captura.

**Para qué:** Asegurar que la captura no pierda paquetes clave por limitaciones de recursos.

**Resultado Esperado**: Sin drops de paquetes durante la captura. CPU/memoria estables (< 80%).
Archivo de captura con tamaño razonable (< 90% de disco/flash).
Contadores de paquetes capturados coinciden con tráfico esperado.


#### Paso `pcap_proto`: 4. Análisis de Protocolos Específicos en la Captura (Tier 2)
**Descripción**: **Dónde:** Decodificación de protocolos en Wireshark / tcpdump para validar comportamiento real.

**MPLS:** Verificar label stack (transport + service), TTL, EXP, S-bit. Filtro: mpls.
**BGP:** OPEN (Type=1), UPDATE (Type=2), NOTIFICATION (Type=3), KEEPALIVE (Type=4).
         Verificar AS_PATH, NEXT_HOP, LOCAL_PREF, COMMUNITIES, NLRI.
**OSPF:** Hello (Type=1), DBD (Type=2), LSR (Type=3), LSU (Type=4), LSAck (Type=5).
         Verificar Router ID, Area ID, Neighbor list, MTU.
**DHCP:** Discover (Option 53=1), Offer (2), Request (3), ACK (5). Verificar giaddr, chaddr.
**BFD:** UDP 3784. Estado Down→Init→Up. Verificar discriminadores, timers.
**PPPoE:** Discovery (0x8863) PADI/PADO/PADR/PADS. Session (0x8864) LCP/IPCP.
**VXLAN:** UDP 4789. Verificar VNI, inner Ethernet/IP.
**EVPN:** BGP UPDATE con NLRI Type 2 (MAC/IP). Verificar RD, ESI, VNI.

**Para qué:** Confirmar que los mensajes de control tienen los valores esperados y que no hay
anomalías (checksums erróneos, sequence numbers desfasados, keepalives perdidos).

**Resultado Esperado**: Protocolos decodificados correctamente en Wireshark / tshark. Sin anomalías en flags,
checksums, o secuencias de estado. Keepalives periódicos presentes.
NLRI/Labels/MACs/VNI coinciden con la configuración del router.


#### Paso `pcap_start`: 1. Preparación y captura inicial (Tier 1)
**Descripción**: **Dónde:** Interfaz de red donde circula el tráfico sospechoso. Puede ser física,
subinterfaz (VLAN), túnel GRE/VXLAN, o interfaz de loopback para tráfico de control.

**Cómo:** Verificar que la interfaz esté en Up/Up. En switches, configurar port-mirror (SPAN).
En routers, usar monitor traffic / embedded packet capture / sniffer. En Linux, tcpdump.

**Verificación previa:**
- Sin hardware offload que descarte paquetes antes de la captura (NIC offload, TSO, GRO).
- Buffer de kernel suficiente (-B en tcpdump).
- Snaplen ilimitado (-s0) para ver payloads completos.
- Privilegios adecuados (root / CAP_NET_RAW).

**Para qué:** Asegurar que la captura sea representativa y no pierda tráfico crítico por
buffer insuficiente, filtrado prematuro, o truncamiento de frames.

**Resultado Esperado**: Captura iniciada sin errores. Interfaz en Up/Up. Buffer de kernel suficiente.
Sin dropped packets reportados por tcpdump. Snaplen ilimitado (-s0).
Archivo de captura crece según tráfico esperado.

🔬 **Hipótesis Científica**: La falla de diagnóstico por captura de paquetes es causada por una captura en la interfaz incorrecta, un filtro BPF demasiado restrictivo, la falta de modo promiscuo/SPAN, o un buffer de captura insuficiente que provoca pérdida de paquetes.
🛠️ **Solución Rápida (Quick Fix)**: 1. Capturar en la interfaz física/lógica correcta donde fluye el tráfico de interés.
2. Relajar o corregir el filtro BPF/display filter para no descartar paquetes relevantes.
3. Habilitar modo promiscuo en la NIC o configurar SPAN/RSPAN en el switch.
4. Aumentar el buffer de captura ('-B' en tcpdump) para interfaces de alta velocidad.
5. Deshabilitar resolución de nombres (-n) durante capturas en alta velocidad.
6. Confirmar que no haya 'packets dropped by kernel' y que la captura sea representativa.


### Tecnología: Diagnóstico de Redes en Linux (iproute2 / tcpdump / tshark)
Total de pasos diagnósticos: **4**

#### Paso `linux_l1_l2_link`: 1. Verificar Interfaces y Estado del Enlace (L1-L2) (Tier 1)
**Descripción**: **Objetivo:** Confirmar que la interfaz física/lógica está activa y tiene los parámetros de velocidad/dúplex correctos.

**Herramientas:** `ip link`, `ip addr`, `ethtool`

**Detalles clave:**
- **Estado UP/DOWN:** El campo `state UP` indica que el enlace físico está activo. `state UNKNOWN` en loopback es normal.
- **Flags:** La presencia de `LOWER_UP` en los flags indica que hay señal eléctrica/óptica en el cable (carrier detect).
- **ethtool:** Muestra la velocidad negociada, dúplex y si el auto-negociación fue exitosa.
- **Errores de capa física:** Los contadores `RX errors`, `TX dropped` o `overruns` indican problemas físicos o de driver.

**Resultado Esperado**: La interfaz debe mostrar estado `UP` con flag `LOWER_UP`. ethtool debe reportar `Link detected: yes` con la velocidad y dúplex esperados (ej. Speed: 1000Mb/s, Duplex: Full). Los contadores de errores RX/TX deben estar en cero o sin incremento en el tiempo.


#### Paso `linux_l3_l4_routing`: 2. Verificar Enrutamiento, ARP y Sockets (L3-L4) (Tier 2)
**Descripción**: **Objetivo:** Validar que la tabla de rutas tiene el camino correcto hacia el destino y que el vecino ARP/NDP está resuelto.

**Herramientas:** `ip route`, `ip neigh`, `ss`, `traceroute`

**Detalles clave:**
- `ip route get <ip>` muestra **exactamente** qué interfaz y siguiente salto usará el kernel para ese destino.
- `ip rule show` lista las tablas de routing policy (PBR). Si hay reglas, los paquetes pueden seguir tablas distintas a la principal.
- `ip neigh show` muestra la caché ARP/NDP. Una entrada en estado `FAILED` o `INCOMPLETE` indica que el vecino no responde.
- `ss -tlnp` lista los servicios escuchando en puertos TCP. Confirma si el proceso de destino está corriendo.
- `sysctl net.ipv4.ip_forward` debe ser `1` si el host actúa como router/gateway.

**Resultado Esperado**: `ip route get <ip>` debe mostrar la interfaz y gateway correctos. `ip neigh show` debe tener el gateway en estado `REACHABLE` o `STALE` con MAC resuelto. `ping` debe tener 0% de pérdida. Si el host es un router, `ip_forward` debe ser `1`.


#### Paso `linux_firewall_nat`: 3. Diagnóstico de Firewall, NAT y Connection Tracking (L3-L4) (Tier 3)
**Descripción**: **Objetivo:** Detectar si iptables/nftables está bloqueando o modificando el tráfico, y verificar el estado de la tabla de seguimiento de conexiones (conntrack).

**Herramientas:** `iptables`, `nft`, `conntrack`, `ss`

**Detalles clave:**
- `iptables -L -n -v` muestra las reglas de filtrado con contadores de paquetes/bytes.
- `iptables -t nat -L -n -v` muestra las reglas PREROUTING/POSTROUTING de NAT.
- `conntrack -L` lista todas las conexiones rastreadas en tiempo real. Buscar la IP/puerto de interés.
- `conntrack -C` muestra el número total de conexiones en la tabla. Si se acerca a `nf_conntrack_max`, habrá descarte silencioso de nuevas conexiones.
- `conntrack -S` muestra estadísticas de error como `drop`, `insert_failed`, que indican agotamiento de la tabla.
- **nftables:** Si el sistema usa nftables moderno, usar `nft list ruleset` en su lugar.

**Resultado Esperado**: Las reglas de iptables/nft deben permitir el tráfico de interés (contador de paquetes en las reglas ACCEPT va aumentando). La tabla conntrack debe mostrar la sesión en estado `ESTABLISHED`. El ratio conntrack_count / conntrack_max debe ser menor al 80% para evitar descarte de nuevas conexiones.


#### Paso `linux_packet_capture`: 4. Captura de Paquetes en Tiempo Real (tcpdump / tshark) — OSI L1 a L7 (Tier 3)
**Descripción**: **Objetivo:** Capturar el tráfico crudo en la interfaz del kernel para confirmar si los paquetes llegan, salen y se modifican correctamente en cada capa del modelo OSI.

**Herramientas:** `tcpdump`, `tshark`

**Detalles clave (OSI L1-L7):**
- **L1-L2 (Físico/Enlace):** tcpdump en modo `-e` muestra direcciones MAC origen/destino y tipo Ethernet.
- **L3 (Red):** Los campos `ip.src` / `ip.dst` revelan si el NAT está modificando las IPs correctamente antes/después del firewall.
- **L4 (Transporte):** Los flags TCP (SYN, ACK, RST, FIN) en tcpdump/tshark indican la fase del handshake y posibles resets.
- **L5-L7 (Sesión/Aplicación):** tshark con filtros de capa 7 (`http`, `dns`, `tls`) permite ver si la aplicación responde correctamente.
- **Guardar a archivo:** Siempre guardar a `.pcap` con `-w` para análisis posterior en Wireshark.
- **Filtros BPF:** Los filtros de captura (`host`, `port`, `tcp`, `udp`) reducen el volumen y evitan pérdida de paquetes en interfaces de alta velocidad.

**Resultado Esperado**: tcpdump/tshark deben mostrar el intercambio completo de 3-way handshake TCP (SYN → SYN-ACK → ACK). Los campos IP src/dst deben reflejar las IPs correctas en cada punto de la cadena (antes y después de NAT). No deben aparecer TCP RST inesperados ni retransmisiones excesivas (> 1%) que indiquen descarte o pérdida en el camino.


### Tecnología: Rastreo IP Extremo a Extremo
Total de pasos diagnósticos: **5**

#### Paso `ip_trace_start`: 1. Origen y Capa 2 (Local Link / Gateway) (Tier 1)
**Descripción**: **Objetivo:** Verificar la configuración IP en el host origen (Capa 3), su alcanzabilidad física de red local y la resolución de direcciones MAC del Default Gateway (Capa 2).

**Acción:** Comprobar dirección IP local, máscara de red, default gateway, y resolver la dirección MAC del gateway usando la tabla ARP/Neighbor.

**Variables:** `<ip-origen>`, `<gateway>`, `<interface>`

**Resultado Esperado**: Interfaz en estado UP/UP, dirección IP y máscara correctas. La tabla ARP debe mostrar la MAC resuelta del gateway.


#### Paso `ip_trace_l3_igp`: 2. Capa 3 - Enrutamiento Interno (IGP / MPLS) (Tier 2)
**Descripción**: **Objetivo:** Validar el camino del paquete a través de la red interna (Core) buscando en la tabla de rutas el prefijo coincidente más largo (Longest Prefix Match - LPM), resolución recursiva, y adyacencias OSPF/IS-IS/EIGRP/MPLS.

**Acción:** Verificar que exista una ruta hacia el destino (o una ruta por defecto), identificar el siguiente salto y validar la sesión del protocolo IGP / MPLS (LDP/Segment Routing) para ese enlace.

**Variables:** `<ip-destino>`, `<neighbor-ip>`

**Resultado Esperado**: Existe una ruta instalada en la tabla FIB/RIB hacia el destino, apuntando a un siguiente salto válido y activo. Las adyacencias IGP deben estar en estado operacional (Full/Established).


#### Paso `ip_trace_l3_egp`: 3. Capa 3 - Enrutamiento Externo (BGP / PBR) (Tier 2)
**Descripción**: **Objetivo:** Comprobar el tránsito inter-Sistemas Autónomos (EGP/BGP) y la aplicación de políticas de enrutamiento estático/dinámico o desvíos por PBR (Policy-Based Routing) hacia la salida WAN/Internet.

**Acción:** Validar la sesión BGP contra el ISP/peer, verificar el anuncio del prefijo, y comprobar si existe alguna política PBR en la interfaz de entrada.

**Variables:** `<ip-destino>`, `<peer-ip>`

**Resultado Esperado**: Sesión BGP activa (Established), Next-Hop del peer BGP alcanzable. PBR activo y con contadores de paquetes incrementándose.


#### Paso `ip_trace_security_nat`: 4. Capa 4 - Firewall, Políticas de Seguridad y NAT (Tier 3)
**Descripción**: **Objetivo:** Verificar si el firewall o gateway perimetral está traduciendo la dirección IP (NAT) y si las políticas de seguridad (Firewall/ACL) permiten el paso del tráfico y su retorno.

**Acción:** Comprobar la tabla de traducción de puertos/direcciones (NAT Session), comprobar las ACLs de entrada/salida, y validar la tabla de estados de conexión (conntrack/sesiones).

**Variables:** `<ip-destino>`, `<ip-origen>`, `<puerto-destino>`

**Resultado Esperado**: Sesión NAT creada activamente. Políticas de firewall en estado permit (accept) con los contadores de paquetes subiendo.


#### Paso `ip_trace_captures`: 5. Capa 4-7 - Capturas de Red, MTU y Aplicación (Tier 3)
**Descripción**: **Objetivo:** Validar mediante análisis de trazas que los paquetes llegan físicamente a través de la interfaz y que no existen descartes silenciosos debidos a fragmentación por MTU/MSS en el camino.

**Acción:** Ejecutar una captura en tiempo real filtrando por la dirección IP y puerto especificado, verificar el handshake TCP y descartar problemas de capa de transporte.

**Variables:** `<ip-destino>`, `<ip-origen>`, `<puerto-destino>`, `<interface>`

**Resultado Esperado**: Captura exitosa mostrando paquetes TCP/UDP fluyendo bidireccionalmente. Comprobar que el tamaño de los paquetes no exceda la MTU configurada (normalmente 1500 bytes en Ethernet).


### Tecnología: Diagnóstico de Bucles (Capas 1-4)
Total de pasos diagnósticos: **4**

#### Paso `loop_l1`: 1. Bucle de Capa 1 (Físico / Optomecánico / Reflectométrico) (Tier 1)
**Descripción**: **Cómo:** Sucede cuando una señal física transmitida (eléctrica u óptica) es devuelta directamente al receptor del mismo puerto o puenteada físicamente a nivel físico sin pasar por una conmutación lógica inteligente.

**Cuándo:** Ocurre durante instalaciones de cableado o empalmes incorrectos, transceptores defectuosos que reflejan el láser de retorno, patching de fibra cruzada errónea, o cuando se habilita intencionalmente el modo de prueba de bucle físico (loopback) sin medidas de control.

**Dónde:** En las interfaces físicas del router/switch (puertos Ethernet, SFP/SFP+, DWDM transponders, cableado estructurado, o patches de fibra en paneles de distribución ODF).

**Por qué:** Errores humanos de conexionado, transceptores dañados (corto óptico interno), o comandos administrativos residuales (`loopback local` o `loopback diagnostic`) dejados tras pruebas de transporte WAN.

**Para qué:** Resolver bucles de Capa 1 es crítico para evitar el bloqueo físico del puerto, impedir lecturas ópticas de Rx anómalas (sobrecarga de luz) y garantizar que la modulación de línea sea bidireccional y limpia.

**Resultado Esperado**: Puertos físicos sin modo loopback habilitado. Potencia de recepción (Rx) estable dentro de umbrales (-3 a -15 dBm para SFP común) y diferente de la potencia de Tx. Sin alarmas de "Loopback detected" o "Physical Loop".

🔬 **Hipótesis Científica**: La interfaz física tiene un puente de hardware o transceptor en modo loopback, reflejando toda la señal de Tx de regreso a su propio Rx.
🛠️ **Solución Rápida (Quick Fix)**: Retirar el loopback plug físico, corregir el cableado/splicing en la bandeja de fibra, o remover el comando "loopback local/diagnostic" del puerto.

#### Paso `loop_l2`: 2. Bucle de Capa 2 (Conmutación / STP / Flapping MAC / Tormenta de Broadcast) (Tier 1)
**Descripción**: **Cómo:** Se genera al interconectar switches en un anillo físico redundante sin un protocolo de prevención de bucles activo (o mal configurado). Las tramas broadcast se copian infinitamente, saturando el ancho de banda y provocando el desbordamiento de la tabla de direcciones MAC (MAC Flapping).

**Cuándo:** Al realizar nuevas conexiones de redundancia física sin habilitar STP/RSTP/MSTP, cuando un switch descarta BPDUs bajo alta carga de CPU, ante inconsistencias de VLANs en troncales, o cuando un usuario conecta un switch casero no administrado a dos tomas de red locales.

**Dónde:** En redes de área local (LAN), switches de agregación/distribución, VLANs, bridge domains, y en entornos Carrier como VPLS, VXLAN o EVPN sin split-horizon.

**Por qué:** STP deshabilitado, comandos `bpdufilter` bloqueando tramas de control, retrasos de Proposal-Agreement en RSTP por puertos no-edge configurados incorrectamente, o tormentas de broadcasts (ARP/DHCP) que invalidan las tablas CAM constantemente.

**Para qué:** Resolver bucles de Capa 2 es crítico para evitar el colapso absoluto de la red (broadcast storm), restaurar la CPU de los switches a niveles normales, detener el flapping de MACs y restablecer la conmutación de datos de usuario.

**Resultado Esperado**: STP/RSTP activo globalmente. Interfaces redundantes en estado "Blocking" / "Discarding". Dirección del Root Bridge apuntando al switch core correcto. Tabla MAC (CAM) estable sin logs de flapping.

🔬 **Hipótesis Científica**: Hay una ruta física redundante en la red LAN que no está siendo bloqueada por STP, provocando una replicación infinita de tramas broadcast.
🛠️ **Solución Rápida (Quick Fix)**: Habilitar STP/RSTP, configurar el switch core principal con prioridad 4096 para ser el Root Bridge, activar "bpduguard" en puertos de acceso (Edge) y habilitar "storm-control broadcast level 1.0" para mitigar tormentas.

#### Paso `loop_l3`: 3. Bucle de Capa 3 (Red / Routing Loop / TTL Expiry) (Tier 1)
**Descripción**: **Cómo:** Ocurre cuando las tablas de enrutamiento (RIB/FIB) de dos o más routers apuntan cíclicamente entre sí para llegar a un prefijo destino común, haciendo que los paquetes IP reboten de ida y vuelta hasta agotar su tiempo de vida (TTL).

**Cuándo:** Durante procesos de convergencia de protocolos dinámicos (OSPF/IS-IS/BGP), cuando se definen rutas estáticas manuales erróneas, o al realizar redistribuciones bidireccionales de rutas entre diferentes protocolos sin aplicar filtros/tags de prevención.

**Dónde:** En enrutadores de core, routers de borde de AS (ASBRs), L3 switches, y firewalls de tránsito IP.

**Por qué:** Desajuste de distancias administrativas, falta de filtrado en redistribuciones, problemas de recursividad en rutas hacia el next-hop en BGP, o enrutamiento estático estático que apunta a una red sumarizada sin ruta de descarte (`null0`).

**Para qué:** Solucionar bucles de Capa 3 es fundamental para restablecer la alcanzabilidad IP end-to-end, evitar que los routers gasten procesamiento descartando paquetes IP por expiración de TTL y liberar el ancho de banda del enlace core saturado.

**Resultado Esperado**: Rutas estables en la tabla RIB/FIB. Traceroute lineal sin repeticiones de saltos IP. Políticas de redistribución con filtros de tags estrictos instalados.

🔬 **Hipótesis Científica**: Existe una inconsistencia en el enrutamiento salto a salto (next-hop circular) que provoca que el paquete rebote cíclicamente entre enrutadores.
🛠️ **Solución Rápida (Quick Fix)**: Ajustar la distancia administrativa para preferir el protocolo correcto, implementar filtrado de etiquetas (route tag filters) en route-maps de redistribución, o configurar una ruta estática de descarte (Null0) para rangos sumarizados.

#### Paso `loop_l4`: 4. Bucle de Capa 4 (Transporte / Sockets TCP-UDP / Hairpin NAT / Redirección Circular) (Tier 1)
**Descripción**: **Cómo:** Sucede cuando una regla de traducción de direcciones (NAT) o redirección de puertos desvía el tráfico entrante de un socket (IP:puerto) de vuelta a la dirección origen original del emisor, o cuando dos servicios UDP/TCP se reenvían datos mutuamente de forma indefinida sin control de estado.

**Cuándo:** Al configurar NAT de bucle (Hairpin NAT o NAT Loopback) sin definir el pool de traducción origen para hosts internos, en delegaciones circulares de servidores DNS (DNS A reenvía a B, y B reenvía a A), o cuando se habilitan servicios de eco (UDP port 7 o 19) expuestos al exterior.

**Dónde:** En los firewalls de frontera (Edge Firewalls), balanceadores de carga, servidores DNS locales, y pilas de red de los hosts de aplicación.

**Por qué:** Errores de lógica en políticas DNAT/Virtual IP, puertos cruzados en proxies reversos, o datagramas UDP huérfanos que rebotan entre servicios de echo (lo que provoca el consumo completo de buffers y agotamiento de puertos efímeros en PAT).

**Para qué:** Detener loops de Capa 4 es indispensable para evitar el desborde de tablas de sesión de firewalls (Connection Table Full), impedir el agotamiento de puertos efímeros del router (Port Exhaustion), y prevenir la caída del servicio de red en las aplicaciones.

**Resultado Esperado**: Reglas Hairpin NAT con traducción de origen (SNAT) activa. Tabla de sesiones NAT libre de conexiones circulares con el mismo socket origen/destino. Servicios obsoletos UDP (puerto 7, 19) deshabilitados.

🔬 **Hipótesis Científica**: Una regla de Destination NAT (Port Forwarding) está redirigiendo el tráfico interno hacia la propia IP del router, o un reenvío circular de puertos está consumiendo sockets TCP/UDP indefinidamente.
🛠️ **Solución Rápida (Quick Fix)**: Modificar la regla de Hairpin NAT para inyectar una traducción SNAT (Masquerade) cuando el origen y destino estén en la misma subred interna. Deshabilitar los puertos legacy UDP 7 (echo) y 19 (chargen) en el servidor y configurar rate-limiting de conexiones TCP en el firewall.

### Tecnología: Diagnóstico de Máscara /31 (RFC 3021)
Total de pasos diagnósticos: **5**

#### Paso `subnet_31_start`: 1. Direccionamiento e Interfaces con /31 (Tier 1)
**Descripción**: **Cómo:** Se configura asignando una máscara de subred de 31 bits (`255.255.255.254`). El rango tiene solo 2 direcciones IP (ej. `.0` y `.1`), y ambas se asignan como IPs de host en cada extremo, eliminando las direcciones tradicionales de red y broadcast.

**Cuándo:** Se implementa en enlaces punto a punto (PtP) WAN o enlaces inter-router de core para duplicar la eficiencia de direccionamiento IPv4 disponible, evitando el desperdicio de un /30 (que usa 4 IPs pero solo 2 útiles).

**Dónde:** En enlaces físicos Ethernet directos, subinterfaces 802.1Q o circuitos virtuales lógicos que interconectan dos routers.

**Por qué:** Errores de sintaxis al ingresar la máscara, descarte preventivo de firewalls que consideran la IP `.0` como dirección de red inválida, o advertencias del sistema operativo que alertan de IP no recomendada en medios de difusión.

**Para qué:** Verificar la asignación de IPs es el primer paso para garantizar la conectividad de Capa 3 y la validez de la máscara RFC 3021 en ambos extremos.

⚠️ **Error de Conexión Común (/24 o /30 como salida fácil):** Cuando un enlace /31 no tiene conectividad (comportamiento muy común en MikroTik RouterOS heredado, Linux antiguos, o firewalls estrictos), muchos administradores caen en el error de configurar una máscara `/24` o `/30` para forzar que funcione. Esto es una mala práctica que desperdicia el direccionamiento IP. El problema real no es físico, sino que el sistema operativo no asocia correctamente el gateway al no calcular la ruta de host conectada automática. La solución correcta es aplicar la alternativa adecuada al vendor sin desperdiciar IPs.

**Resultado Esperado**: Interfaces en estado UP/UP con la máscara /31 (255.255.255.254) aplicada correctamente en ambos extremos del enlace.

🔬 **Hipótesis Científica**: La interfaz no tiene la máscara /31 configurada correctamente, o el vendor reporta un error de sintaxis/validación al rechazar la dirección.
🛠️ **Solución Rápida (Quick Fix)**: Corregir la IP/máscara a 255.255.255.254 (/31) en ambos extremos y levantar la interfaz (no shutdown).

#### Paso `subnet_31_workaround`: 2. Alternativas a /31 (IP Unnumbered y /32 PtP) (Tier 2)
**Descripción**: **Cómo:** Si un vendor no admite /31 o da problemas (como la falta de conectividad típica en RouterOS antiguo), se aplican dos alternativas estándar profesionales en lugar de la mala práctica de ensanchar la máscara a `/24` o `/30`:
1. **IP Unnumbered (Cisco, Juniper, Huawei):** Se asocia el puerto físico a una Loopback (/32) sin asignarle IP al enlace. El tráfico viaja directo y OSPF/BGP se levantan sobre la IP de la Loopback.
2. **Direccionamiento /32 PtP (MikroTik, Linux, Fortinet):** Se asigna una IP local `/32` y se define la IP del peer en el campo `network` (MikroTik), `peer` (Linux) o `remote-ip` (Fortinet), instalando una ruta de host y activando ARP sin desperdiciar subredes.

**Cuándo:** Cuando la interfaz física o el sistema operativo del peer rechaza la máscara 255.255.255.254, o cuando las políticas de seguridad de firewall bloquean direccionamiento que termine en .0 o .1.

**Dónde:** En los puertos de interconexión Ethernet WAN o LAN de tránsito.

**Por qué:** Para eludir limitaciones de hardware/software heredados o evitar que se descarte tráfico multicast/broadcast en el segmento.

**Para qué:** Habilitar interfaces sin numerar o enlaces directos /32 restaura la alcanzabilidad de Capa 3 manteniendo la conservación total de direccionamiento IPv4.

**Resultado Esperado**: Puertos de tránsito activos con IP Unnumbered vinculada a Loopback0, o interfaces configuradas con IP local /32 y red/peer apuntando a la IP remota del vecino.

🔬 **Hipótesis Científica**: El uso de /31 genera problemas de compatibilidad o descarte en el enlace, requiriendo reconfigurar los puertos a modo IP Unnumbered o direccionamiento /32 PtP.
🛠️ **Solución Rápida (Quick Fix)**: En Cisco/Juniper/Huawei: Configurar "ip unnumbered Loopback0" en la interfaz. En MikroTik: Definir address=IP/32 y network=IP_Peer. En Linux: Definir IP peer IP_Peer. En Fortinet: Definir IP/32 y remote-ip IP_Peer.

#### Paso `subnet_31_arp`: 3. Resolución ARP y Conectividad (Ping) (Tier 2)
**Descripción**: **Cómo:** Dado que Ethernet es un medio broadcast, los routers deben resolver la dirección MAC del peer mediante ARP, transmitiendo un ARP Request dirigido a la IP del peer.

**Cuándo:** Al enviar tráfico (pings o paquetes de datos) al peer de la conexión /31 por primera vez o después de que expire la entrada ARP.

**Dónde:** En la tabla caché ARP/Neighbor del enrutador y en la interfaz física.

**Por qué:** Algunos firewalls o políticas de seguridad descartan paquetes ARP para IPs que terminen en `.0` por considerarlas de red. O la tabla ARP local tiene una entrada incompleta/incorrecta debido a la falta de respuesta del peer.

**Para qué:** Resolver ARP exitosamente garantiza la adyacencia de Capa 2 necesaria para encapsular y enviar las tramas IP.

**Resultado Esperado**: Ping exitoso de extremo a extremo. Entrada ARP resuelta con la dirección MAC correcta del peer en estado REACHABLE o Dynamic.

🔬 **Hipótesis Científica**: El peer no responde a las solicitudes ARP, o el firewall del peer bloquea la IP por ser la .0 o .1 del segmento.
🛠️ **Solución Rápida (Quick Fix)**: Verificar si hay un firewall bloqueando la IP .0/.1 o descartando tramas ARP. Confirmar que el peer tenga la interfaz arriba y la IP bien configurada. Limpiar la caché ARP en ambos lados (`clear arp-cache` o equivalente).

#### Paso `subnet_31_ospf`: 4. Enrutamiento Dinámico (OSPF) sobre Enlaces /31 (Tier 3)
**Descripción**: **Cómo:** Al configurar OSPF en una interfaz Ethernet, el tipo de red por defecto es `Broadcast`. OSPF intenta realizar una elección de DR/BDR y enviar paquetes Hello a la dirección multicast `224.0.0.5` usando la máscara del segmento.

**Cuándo:** Al habilitar OSPF en enlaces de interconexión `/31` sobre interfaces físicas tipo Ethernet.

**Dónde:** En los procesos de enrutamiento OSPF y la configuración de las interfaces del enlace.

**Por qué:** El tipo de red `Broadcast` asume que hay múltiples routers. En un /31, esto causa fallos si un lado se configura como P2P o si la falta de IPs de broadcast tradicionales del segmento provoca que las pilas IP rechacen ciertas tramas. Además, realizar la elección DR/BDR en un enlace estrictamente punto a punto agrega latencia innecesaria y complejidad.

**Para qué:** Ajustar el tipo de red OSPF a `Point-to-Point` en ambos extremos fuerza la adyacencia de OSPF a establecerse directamente sin elección de DR/BDR, asegurando una convergencia inmediata.

**Resultado Esperado**: Adyacencia OSPF en estado FULL sin DR/BDR elegidos. Tipo de red configurado como POINT_TO_POINT en ambos extremos.

🔬 **Hipótesis Científica**: La adyacencia OSPF falla o queda stuck en 2-WAY debido a que el tipo de red OSPF está configurado como Broadcast o hay un mismatch entre los extremos.
🛠️ **Solución Rápida (Quick Fix)**: Configurar el comando "ospf network point-to-point" (o equivalente del vendor) bajo la configuración de la interfaz en ambos routers.

#### Paso `subnet_31_architect`: 5. Directivas de Arquitectura y Diseño (RFC 3021) (Tier 4)
**Descripción**: **Cómo:** Desde la perspectiva de diseño, planificar redes usando subredes `/31` conserva un volumen masivo de direccionamiento en redes grandes. Por ejemplo, en 1000 enlaces de interconexión, un diseño con `/30` consume 4000 IPs (2000 desperdiciadas), mientras que con `/31` solo consume 2000 IPs.

**Cuándo:** En la fase de planificación de direccionamiento IP para nuevos backbones, ISPs o despliegues de data centers masivos (Spine-Leaf) donde los enlaces punto a punto abundan.

**Dónde:** En los esquemas globales de direccionamiento y políticas de aprovisionamiento automatizado.

**Por qué:** Para optimizar el uso de direccionamiento IPv4 público o privado limitado (como bloques RFC 1918) y simplificar el cálculo de subredes.

**Para qué:** Entender las implicaciones de arquitectura y diseñar políticas claras asegura que todo el hardware adquirido en el ciclo tecnológico soporte de forma nativa el RFC 3021, evitando incompatibilidades de sistemas legados.

**Resultado Esperado**: Esquema de direccionamiento corporativo estandarizado con máscaras /31 para interconexiones. Políticas de control de compatibilidad de vendors activas.

🔬 **Hipótesis Científica**: Existen dispositivos legados en el path que no entienden RFC 3021 y causan descartes silenciosos de paquetes o errores de parsing de enrutamiento.
🛠️ **Solución Rápida (Quick Fix)**: Definir el uso de /31 como estándar obligatorio de ingeniería de red para enlaces PtP y retirar/aislar plataformas de hardware que no admitan RFC 3021.

### Tecnología: Diagnóstico de 802.1q y 802.1ad (QinQ)
Total de pasos diagnósticos: **5**

#### Paso `vlan_qinq_l2_discovery`: 1. Descubrimiento de Capa 2 y Vecinos (LLDP, CDP, LACP, STP) (Tier 1)
**Descripción**: **Cómo:** Se inspeccionan los protocolos de descubrimiento e interactivos que el vecino remoto emite periódicamente. CDP y LLDP revelan el nombre del equipo, puerto, IP de gestión, VLAN nativa y capacidades. STP (BPDUs) y LACP indican el estado del Spanning Tree y la agregación de enlaces.

**Cuándo:** Cuando no tenemos acceso de gestión al equipo del otro extremo y necesitamos determinar si hay link, qué puerto del peer nos conecta, qué VLAN nativa espera, o si existe una agregación LACP activa.

**Dónde:** En puertos físicos troncales, enlaces troncales agregados (EtherChannel/LACP) y puertos frontera inter-operador.

**Por qué:** Errores de negociación de canal, VLAN nativa diferente en cada extremo que causa mezclas de tráfico o warnings de CDP, o fallas en el intercambio de BPDUs que provocan bloqueos no deseados.

**Para qué:** Identificar al vecino a nivel físico y de Capa 2 es crucial para mapear la topología y asegurar la coherencia del enlace antes de configurar direccionamiento.

**Resultado Esperado**: Vecinos CDP/LLDP detectados con VLAN nativa coherente. Interfaces agregadas LACP negociadas en modo "Active/Forwarding". Spanning Tree en estado estable (Forwarding o Blocking según diseño).

🔬 **Hipótesis Científica**: El equipo remoto está activo pero hay una discrepancia en el direccionamiento de control (LACP/STP) o la VLAN nativa configurada en el peer no coincide con el extremo local.
🛠️ **Solución Rápida (Quick Fix)**: Corregir la VLAN nativa en el extremo local para que coincida con la del peer reportada por CDP/LLDP, habilitar LLDP/CDP de forma global y por interfaz, y configurar la agregación LACP en modo activo si el peer lo requiere.

#### Paso `vlan_qinq_tag_verification`: 2. Verificación de Etiquetas y Encapsulación (802.1q y 802.1ad) (Tier 2)
**Descripción**: **Cómo:** Se configura el etiquetado 802.1q (Dot1q) o 802.1ad (QinQ) en las subinterfaces físicas. Para QinQ, se apila una etiqueta externa de transporte (S-VLAN) y una interna de cliente (C-VLAN). El EtherType define el tipo de trama: `0x8100` para 802.1q y `0x88a8` para 802.1ad.

**Cuándo:** Cuando se requiere segregar el tráfico en múltiples VLANs lógicas sobre un mismo medio físico, o cuando un proveedor de servicios de red (SP) encapsula el tráfico VLAN de múltiples clientes dentro de una sola VLAN de transporte.

**Dónde:** En puertos troncales inter-switch, subinterfaces de routers, firewalls y dispositivos de acceso de transporte de datos.

**Por qué:** Discordancias de EtherType (ej. un extremo configurado con 802.1ad `0x88a8` y el otro con QinQ legacy `0x8100` o `0x9100`), puertos en modo de acceso que descartan tramas etiquetadas, o subinterfaces asociadas a IDs de VLAN erróneos.

**Para qué:** Validar los IDs de VLAN y el protocolo de encapsulación en las subinterfaces asegura que las tramas etiquetadas sean parseadas y procesadas por la VLAN correcta en ambos lados del enlace.

**Resultado Esperado**: IDs de VLAN asignados correctamente en las subinterfaces de ambos extremos. Protocolo de encapsulación (802.1q o 802.1ad) y EtherTypes (TPID) alineados uniformemente en el enlace.

🔬 **Hipótesis Científica**: El enlace físico está UP, pero el tráfico no fluye debido a que uno de los extremos utiliza un tag de VLAN diferente o un EtherType incompatible.
🛠️ **Solución Rápida (Quick Fix)**: Igualar las configuraciones de VLAN IDs y encapsulación en las subinterfaces de ambos lados. Asegurar que los EtherTypes de QinQ (TPID) coincidan a lo largo de todo el trayecto de red (usar 0x88a8 para 802.1ad estándar).

#### Paso `vlan_qinq_packet_sniffing`: 3. Captura de Tráfico y Sniffing (Decodificación de VLAN/QinQ) (Tier 3)
**Descripción**: **Cómo:** Se realiza una captura de tráfico en la interfaz física para capturar las tramas sin procesar. Al analizar la estructura de la cabecera Ethernet (usando la opción `-e` en tcpdump o sniffers nativos), se puede identificar de forma exacta si el tráfico entrante viene etiquetado, los IDs de las etiquetas (VLANs externa e interna) y sus EtherTypes.

**Cuándo:** Cuando el puerto físico está UP pero no hay comunicación lógica, y queremos saber sin lugar a dudas qué etiquetas de VLAN nos está enviando el equipo remoto (al que no tenemos acceso) o si las tramas vienen untagged.

**Dónde:** Directamente en la interfaz física de interconexión orientada al peer remoto.

**Por qué:** Para resolver de manera definitiva disputas de configuración ("yo te entrego VLAN 100", "pues yo no veo nada"), verificar si un equipo intermedio está removiendo (popping) o alterando etiquetas, y confirmar si los EtherTypes son interpretados correctamente.

**Para qué:** Obtener evidencia del tráfico binario real que ingresa al equipo es la prueba definitiva para resolver inconsistencias de Capa 2 en enlaces oscuros.

**Resultado Esperado**: Captura de tramas revelando cabeceras Ethernet con las etiquetas 802.1Q o 802.1ad exactas especificadas en el diseño. Ningún descarte de etiquetas por traducción/manipulación en tránsito.

🔬 **Hipótesis Científica**: Las tramas están llegando etiquetadas con una VLAN diferente a la configurada localmente, o están llegando sin etiquetar (untagged) debido a una omisión del peer.
🛠️ **Solución Rápida (Quick Fix)**: Ajustar la configuración de la subinterfaz local para coincidir con la VLAN identificada en la captura, o solicitar al administrador del equipo remoto que aplique el etiquetado correcto en su puerto de salida.

#### Paso `vlan_qinq_l3_discovery`: 4. Descubrimiento Pasivo de Capa 3 (ARP, NDP, Multicast) (Tier 3)
**Descripción**: **Cómo:** Se monitorean de forma pasiva los paquetes que llegan por la subinterfaz lógica. Las solicitudes ARP broadcast ("Who has X? Tell Y") revelan la dirección IP remota (`Y`) y el direccionamiento de la subred del peer. Los paquetes de protocolos de enrutamiento (ej: OSPF Hello a `224.0.0.5`, HSRP a `224.0.0.102`, VRRP a `224.0.0.18`) revelan subredes y roles.

**Cuándo:** Cuando el enlace físico y VLAN están alineados, pero no sabemos qué direccionamiento IP (/24, /30, etc.) o protocolo de enrutamiento tiene configurado el peer remoto y necesitamos acoplarnos a él.

**Dónde:** En las subinterfaces lógicas configuradas con la VLAN correspondiente (802.1q o QinQ).

**Por qué:** Falta de documentación del direccionamiento IP asignado al enlace, o necesidad de validar si el peer está intentando establecer adyacencias dinámicas antes de configurar el router local.

**Para qué:** Obtener las IPs y subredes mediante sniffing pasivo de Capa 3 evita el escaneo activo intrusivo y permite configurar la IP local correcta del mismo segmento de forma inmediata.

**Resultado Esperado**: ARP requests y anuncios multicast del vecino capturados en la subinterfaz. IP del peer y máscara de subred identificadas y consistentes con el diseño de red.

🔬 **Hipótesis Científica**: El peer remoto está transmitiendo tráfico de Capa 3, lo que permite deducir su direccionamiento IP analizando las direcciones de origen de sus solicitudes ARP y anuncios multicast.
🛠️ **Solución Rápida (Quick Fix)**: Configurar una dirección IP del mismo segmento del peer en nuestra subinterfaz local (ej: 10.200.1.1/30 si el peer es 10.200.1.2/30) y levantar la adyacencia de enrutamiento necesaria.

#### Paso `vlan_qinq_architect`: 5. Directivas de Arquitectura, MTU y Estándares (QinQ/802.1ad) (Tier 4)
**Descripción**: **Cómo:** El apilamiento de etiquetas (QinQ / 802.1ad) incrementa el tamaño total de la trama Ethernet. Cada etiqueta (tag) añade un overhead de 4 bytes. Para una trama estándar con MTU de 1500 bytes, el tamaño de trama L2 pasa de 1518 bytes (con 802.1q) a 1522 bytes (con 802.1ad / QinQ). Es obligatorio configurar el MTU L2 de transporte en un mínimo de `1504` o `1508` (o superior, ej: MTU jumbo `9000`) para evitar descartes por tramas "Giants".

**Cuándo:** Al diseñar e interconectar redes Carrier Ethernet, Metro Ethernet o tránsitos entre ISPs que transportan VLANs de cliente empaquetadas (QinQ).

**Dónde:** En todos los puertos físicos de tránsito intermedio (switches de agregación, enlaces de fibra, routers MPLS).

**Por qué:** Tramas descartadas silenciosamente debido a MTU demasiado bajo en switches intermedios (que descartan tramas mayores a 1500 bytes sin avisar), o incompatibilidad de hardware al no soportar EtherType `0x88a8` (802.1ad) nativo.

**Para qué:** Configurar correctamente los MTUs y EtherTypes de punta a punta asegura la transmisión de paquetes grandes de datos (ej. pings grandes, tráfico de base de datos) sin fragmentación ni descarte.

**Resultado Esperado**: MTU de interfaces físicas de tránsito configuradas a nivel L2 con suficiente margen (mínimo 1508 o superior como 9000/9216). EtherType 802.1ad configurado como 0x88a8 en puertos de transporte.

🔬 **Hipótesis Científica**: Las tramas de tamaño normal fallan al cruzar el enlace debido a un MTU de transporte demasiado bajo que causa el descarte silencioso de tramas QinQ de 1522 bytes.
🛠️ **Solución Rápida (Quick Fix)**: Incrementar el MTU de la interfaz física a 1508 o preferiblemente a 9000 (Jumbo MTU) en todos los switches y routers en el trayecto para alojar el overhead de las etiquetas.
