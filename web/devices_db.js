// devices_db.js - Catálogo de Equipos y Procedimientos Multi-Vendor (ES6 Module)
export const hardwareCatalog = [
  {
    "familyId": "cisco-ios-classic",
    "familyName": "Cisco IOS Classic (ISR G1/G2 & 800 Series)",
    "models": [
      "1841",
      "1941",
      "2801",
      "2811",
      "2821",
      "2851",
      "2921",
      "2951",
      "3825",
      "3845",
      "3925",
      "3945",
      "881",
      "HWIC-Cards"
    ],
    "prompts": {
      "user": "Router>",
      "privileged": "Router#",
      "config": "Router(config)#"
    },
    "tshootSteps": [
      {
        "step": 1,
        "title": "Auditoría de Hardware, Inventario y Módulos HWIC/WIC",
        "goal": "Validar estado de la controladora, números de serie, licencias y módulos HWIC instalados en los slots.",
        "command": "show version\nshow inventory\nshow diag\nshow license"
      },
      {
        "step": 2,
        "title": "Diagnóstico de Capa 1 / Capa 2 (Interfaces y HWIC)",
        "goal": "Detectar CRC errors, colisiones, flaps en módulos seriales/Ethernet y estados de negociación.",
        "command": "show interfaces {{interface}}\nshow interfaces summary\nshow controllers {{interface}}"
      },
      {
        "step": 3,
        "title": "Validación de Routing, Control Plane y Consumo de Recursos",
        "goal": "Comprobar carga de CPU, consumo de memoria DRAM/TCAM y tabla de rutas.",
        "command": "show processes cpu sorted | exclude 0.00\nshow memory statistics\nshow ip route\nshow ip arp"
      }
    ],
    "configTemplate": "! =====================================\n! Cisco IOS Classic - Baseline Config\n! =====================================\nhostname {{hostname}}\nservice password-encryption\nno ip domain-lookup\nip routing\n!\ninterface {{interface}}\n description WAN_LINK_{{client_name}}\n ip address {{ip_address}} {{subnet_mask}}\n duplex auto\n speed auto\n no shutdown\n!\nip route 0.0.0.0 0.0.0.0 {{default_gateway}}\n!\nline vty 0 4\n transport input ssh\n login local"
  },
  {
    "familyId": "cisco-ios-xe-asr",
    "familyName": "Cisco IOS-XE / Carrier Ethernet (ASR 920 / ASR 901)",
    "models": [
      "ASR 920",
      "ASR 901"
    ],
    "prompts": {
      "privileged": "ASR#",
      "config": "ASR(config)#"
    },
    "tshootSteps": [
      {
        "step": 1,
        "title": "Diagnóstico de Transceivers SFP / DOM (Digital Optical Monitoring)",
        "goal": "Monitorear niveles de potencia óptica TX/RX (dBm) en puertos SFP/SFP+.",
        "command": "show hw-module subslot 0/0 transceiver {{port_id}} status\nshow controllers optics {{port_id}}\nshow inventory"
      },
      {
        "step": 2,
        "title": "Troubleshooting de Carrier Ethernet (EVC / BD / MPLS)",
        "goal": "Verificar Service Instances, Bridge Domains y conmutación de etiquetas MPLS.",
        "command": "show ethernet service instance\nshow bridge-domain {{vlan_id}}\nshow mpls l2transport vc"
      }
    ],
    "configTemplate": "! =====================================\n! Cisco ASR 920 Carrier Ethernet Config\n! =====================================\ninterface GigabitEthernet0/0/{{port_id}}\n no ip address\n negotiation auto\n service instance {{service_id}} ethernet\n  encapsulation dot1q {{vlan_id}}\n  rewrite ingress tag pop 1 symmetric\n  bridge-domain {{vlan_id}}\n !\n!"
  },
  {
    "familyId": "juniper-junos",
    "familyName": "Juniper JunOS (ACX Series & SRX Gateways)",
    "models": [
      "ACX 2200 AC",
      "SRX300",
      "SRX340",
      "SRX1500"
    ],
    "prompts": {
      "operational": "user@router> ",
      "config": "user@router# "
    },
    "tshootSteps": [
      {
        "step": 1,
        "title": "Auditoría de Alarmas de Chasis y Potencia Óptica SFP",
        "goal": "Comprobar alarmas de hardware y niveles ópticos recibidos en interfaces ge-/xe-.",
        "command": "show system alarms\nshow chassis hardware\nshow chassis environment\nshow interfaces diagnostics optics {{interface}}"
      },
      {
        "step": 2,
        "title": "Inspección de Flujo de Seguridad / Zonas (Modelos SRX)",
        "goal": "Identificar descartes por políticas de seguridad, zonas de tráfico o tabla de sesiones.",
        "command": "show security flow session source-prefix {{ip_address}}\nshow security zones\nshow security policies hit-count"
      },
      {
        "step": 3,
        "title": "Diagnóstico de Enrutamiento y MPLS (Modelos ACX)",
        "goal": "Verificar tablas de enrutamiento inet.0, inet.3 y estado de adyacencias IGP/BGP.",
        "command": "show route table inet.0\nshow ldp session\nshow bgp summary"
      }
    ],
    "configTemplate": "# =====================================\n# Juniper JunOS Baseline Config\n# =====================================\nset system host-name {{hostname}}\nset interfaces {{interface}} unit 0 family inet address {{ip_address}}/{{prefix}}\nset routing-options static route 0.0.0.0/0 next-hop {{default_gateway}}\n# En SRX añadir a zona:\nset security zones security-zone TRUST interfaces {{interface}}.0"
  },
  {
    "familyId": "fortinet-fortios",
    "familyName": "Fortinet FortiOS (FortiGate Series)",
    "models": [
      "40F",
      "60F",
      "80F",
      "100F",
      "200F"
    ],
    "prompts": {
      "admin": "FortiGate # "
    },
    "tshootSteps": [
      {
        "step": 1,
        "title": "Diagnóstico de Recursos y Estado de SPU/NP/CP",
        "goal": "Evaluar uso de CPU/RAM, conservación de memoria (Conserve Mode) y estado de hardware.",
        "command": "get system status\nget system performance status\ndiagnose hardware sysinfo memory\ndiagnose hardware sysinfo conserve"
      },
      {
        "step": 2,
        "title": "Inspección de Transceivers SFP y Enlaces Físicos",
        "goal": "Revisar lecturas DOM de módulos ópticos insertados en slots SFP.",
        "command": "get system interface transceiver\nget system interface physical"
      },
      {
        "step": 3,
        "title": "Debug de Flujo de Paquetes en Tiempo Real (Packet Sniffer & Flow)",
        "goal": "Capturar paquetes y seguir el flujo de decisiones del motor de políticas de FortiOS.",
        "command": "diagnose sniffer packet any 'host {{ip_address}}' 4 0 l\ndiagnose debug flow filter addr {{ip_address}}\ndiagnose debug flow show function-name enable\ndiagnose debug flow trace start 100\ndiagnose debug enable"
      }
    ],
    "configTemplate": "# =====================================\n# FortiOS Interface & Default Route\n# =====================================\nconfig system interface\n    edit \"{{interface}}\"\n        set mode static\n        set ip {{ip_address}} {{subnet_mask}}\n        set allowaccess ping ssh https\n    next\nend\nconfig router static\n    edit 1\n        set dst 0.0.0.0 0.0.0.0\n        set gateway {{default_gateway}}\n        set device \"{{interface}}\"\n    next\nend"
  },
  {
    "familyId": "sophos-sfos",
    "familyName": "Sophos SFOS (XG / XGS Series & Sophos Central)",
    "models": [
      "XG 85",
      "XG 86",
      "XG 115",
      "XG 125",
      "XG 135",
      "XG 210",
      "XG 310",
      "XG 330",
      "XGS 87",
      "XGS 107",
      "XGS 116",
      "XGS 126",
      "XGS 136",
      "Sophos Central"
    ],
    "prompts": {
      "console": "console> "
    },
    "tshootSteps": [
      {
        "step": 1,
        "title": "Diagnóstico de Servicios de Sistema y Estado Sophos Central",
        "goal": "Verificar servicios de firewall, estado del motor IPS/Antivirus y sincronización con Sophos Central.",
        "command": "system diagnostics show version-info\nservice -S\ncentral-management show-status"
      },
      {
        "step": 2,
        "title": "Captura de Paquetes y Conexiones por Consola Avanzada",
        "goal": "Filtrar tráfico en tiempo real mediante tcpdump desde la consola de administración.",
        "command": "tcpdump 'host {{ip_address}}'\ndrppkt | grep {{ip_address}}\nconntrack -L | grep {{ip_address}}"
      }
    ],
    "configTemplate": "# =====================================\n# Sophos SFOS Advanced Shell / CLI\n# =====================================\n# Configurar IP en interfaz Port2 (WAN):\nset network interface Port2 ip {{ip_address}} netmask {{subnet_mask}}\n# Añadir Gateway predeterminado:\nset network default-gateway {{default_gateway}}"
  },
  {
    "familyId": "datacom-dmos",
    "familyName": "Datacom DmOS / Switches de Acceso & Agregación",
    "models": [
      "DM4073",
      "DM4170",
      "DM4370",
      "DM4380"
    ],
    "prompts": {
      "operational": "DM4370# ",
      "config": "DM4370(config)# "
    },
    "tshootSteps": [
      {
        "step": 1,
        "title": "Inspección de Puertos Ópticos SFP/SFP+ y Diagnóstico DDM",
        "goal": "Monitorear valores de potencia óptica de transmisión/recepción y temperatura del módulo.",
        "command": "show interface optical-diagnostics\nshow interface transceiver\nshow interface {{interface}}"
      },
      {
        "step": 2,
        "title": "Validación de VLANs, Spanning Tree y Tablas MAC",
        "goal": "Verificar el reenvío de tramas L2 y el estado de puertos en STP.",
        "command": "show vlan {{vlan_id}}\nshow mac-address-table\nshow spanning-tree"
      }
    ],
    "configTemplate": "! =====================================\n! Datacom DmOS Interface Config\n! =====================================\ninterface {{interface}}\n description ENLACE_{{client_name}}\n switchport mode trunk\n switchport trunk allowed vlan add {{vlan_id}}\n no shutdown\n!"
  },
  {
    "familyId": "teltonika-rutos",
    "familyName": "Teltonika RutOS (Routers Industriales & M2M LTE)",
    "models": [
      "RUT300",
      "RUX08",
      "RUTX10",
      "RUTX11",
      "RUTXR1"
    ],
    "prompts": {
      "root": "root@Teltonika:~# "
    },
    "tshootSteps": [
      {
        "step": 1,
        "title": "Diagnóstico de Módem Celular / Señal LTE (Modelos RUTX11/RUTXR1)",
        "goal": "Validar intensidad de señal (RSSI, RSRP, RSRQ, SINR) y estado de registro en el operador móvil.",
        "command": "gsmctl -q\ngsmctl -K\ngsmctl -A 'AT+QENG=\"servingcell\"'\ngsmctl -t"
      },
      {
        "step": 2,
        "title": "Comprobación de Interfaces WAN / LAN y Rutas Linux",
        "goal": "Verificar configuración de interfaces lógicas OpenWrt (uci) y tabla de rutas.",
        "command": "ip addr show\nip route show\nuci show network\nlogread | grep mwan3"
      }
    ],
    "configTemplate": "# =====================================\n# Teltonika RutOS UCI Config (WAN Static)\n# =====================================\nuci set network.wan.proto='static'\nuci set network.wan.ipaddr='{{ip_address}}'\nuci set network.wan.netmask='{{subnet_mask}}'\nuci set network.wan.gateway='{{default_gateway}}'\nuci commit network\n/etc/init.d/network restart"
  },
  {
    "familyId": "raisecom-ros",
    "familyName": "Raisecom ROS Switches Administrables",
    "models": [
      "ISCOM 2600G",
      "ISCOM 2608G"
    ],
    "prompts": {
      "privileged": "Raisecom# ",
      "config": "Raisecom(config)# "
    },
    "tshootSteps": [
      {
        "step": 1,
        "title": "Diagnóstico de Puertos Ópticos SFP / DDM",
        "goal": "Revisar la potencia óptica del puerto de uplink/acceso.",
        "command": "show ddm interface {{interface}}\nshow port {{interface}}"
      },
      {
        "step": 2,
        "title": "Verificación de Tablas MAC y Configuración VLAN",
        "goal": "Confirmar que la MAC del cliente está aprendida en el puerto correcto.",
        "command": "show mac-address-table interface {{interface}}\nshow vlan {{vlan_id}}"
      }
    ],
    "configTemplate": "! =====================================\n! Raisecom ISCOM Base Config\n! =====================================\ninterface {{interface}}\n switchport mode trunk\n switchport trunk allowed vlan {{vlan_id}}\n no shutdown\n!"
  },
  {
    "familyId": "allied-telesis",
    "familyName": "Allied Telesis AlliedWare Plus & Gateways iMG",
    "models": [
      "AT-x510",
      "iMG606",
      "iMG616W",
      "iMG1405",
      "iMG1425",
      "iMG1505"
    ],
    "prompts": {
      "manager": "awplus# ",
      "config": "awplus(config)# "
    },
    "tshootSteps": [
      {
        "step": 1,
        "title": "Diagnóstico de Hardware y Módulos Ópticos",
        "goal": "Revisar lecturas DDM y estado de puertos Ethernet/Fibra.",
        "command": "show system\nshow interface {{interface}}\nshow interface {{interface}} optical-diagnostics"
      },
      {
        "step": 2,
        "title": "Verificación de Switching L2 y EPSR / STP",
        "goal": "Comprobar reenvío en anillos EPSR y tablas de conmutación.",
        "command": "show mac address-table\nshow epsr"
      }
    ],
    "configTemplate": "! =====================================\n! Allied Telesis AT-x510 Port Config\n! =====================================\ninterface {{interface}}\n switchport mode access\n switchport access vlan {{vlan_id}}\n!"
  },
  {
    "familyId": "huawei-vrp",
    "familyName": "Huawei Enterprise VRP (Routers Serie AR)",
    "models": [
      "AR611W",
      "AR650"
    ],
    "prompts": {
      "user": "<Huawei>",
      "config": "[Huawei]"
    },
    "tshootSteps": [
      {
        "step": 1,
        "title": "Auditoría de Estado de Dispositivo y Diagnóstico Óptico",
        "goal": "Verificar alarmas del sistema y niveles ópticos en interfaces GigabitEthernet.",
        "command": "display version\ndisplay device\ndisplay transceiver interface {{interface}} verbose"
      },
      {
        "step": 2,
        "title": "Diagnóstico de Interfaces y Enrutamiento IP",
        "goal": "Comprobar estadísticas de tráfico, descartes y tabla de rutas de forwarding.",
        "command": "display interface {{interface}}\ndisplay ip routing-table\ndisplay ip interface brief"
      }
    ],
    "configTemplate": "# =====================================\n# Huawei AR Config\n# =====================================\nsysname {{hostname}}\ninterface {{interface}}\n ip address {{ip_address}} {{subnet_mask}}\n undo shutdown\nquit\nip route-static 0.0.0.0 0.0.0.0 {{default_gateway}}"
  },
  {
    "familyId": "bdcom-switch",
    "familyName": "BDCOM Managed Switches",
    "models": [
      "BDCOM 1705"
    ],
    "prompts": {
      "privileged": "BDCOM# ",
      "config": "BDCOM(config)# "
    },
    "tshootSteps": [
      {
        "step": 1,
        "title": "Inspección de Puertos y Tabla de Direcciones MAC",
        "goal": "Comprobar velocidad, dúplex y MACs aprendidas por interfaz.",
        "command": "show interface {{interface}} status\nshow mac address-table"
      }
    ],
    "configTemplate": "! =====================================\n! BDCOM 1705 Interface Config\n! =====================================\ninterface {{interface}}\n switchport mode access\n switchport access vlan {{vlan_id}}"
  },
  {
    "familyId": "l1-passive-media",
    "familyName": "Capa 1: Medios Físicos, Conversores y Transceivers",
    "models": [
      "VKS-100-25 VKOM",
      "VKDG2",
      "VKSF1100-20A",
      "TRS OPT-1202S25",
      "CONVERSOR SFP",
      "FIBRA OPTICA",
      "NO APLICA"
    ],
    "prompts": {
      "note": "Verificación Física / Instrumental"
    },
    "tshootSteps": [
      {
        "step": 1,
        "title": "Verificación de LEDs de Estado en Conversores de Medios",
        "goal": "Comprobar alimentación (PWR), enlace óptico (FX Link/Act) y enlace de cobre (TP Link/Act).",
        "command": "# Inspección visual de LEDs:\n- PWR: Verde fijo\n- FX LINK/ACT: Verde fijo o parpadeante (tráfico)\n- TP LINK/ACT: Verde fijo (negociación 10/100/1000 Mbps)\n- FDX/COL: Modo Full Duplex activo\n- LFP (Link Fault Pass-through): Desactivar para aislar fallas de tramo"
      },
      {
        "step": 2,
        "title": "Medición con Power Meter Óptico y VFL (Localizador Visual de Fallas)",
        "goal": "Verificar que la atenuación óptica esté dentro del presupuesto de potencia (Power Budget).",
        "command": "# Procedimiento Óptico:\n1. Conectar VFL (Láser rojo 650nm) para verificar continuidad y quiebres de fibra.\n2. Medir potencia RX con Power Meter calibrado a 1310nm / 1550nm.\n3. Rangos esperados estándar: Monomodo (SMF) entre -8 dBm y -22 dBm (Evitar saturación > -3 dBm o atenuación excesiva < -27 dBm)."
      }
    ],
    "configTemplate": "# NOTA DE INGENIERÍA:\n# Los conversores de medios no gestionables (VKOM, TRS) operan en Capa 1 pura.\n# Asegurarse de que la velocidad/dúplex en el switch conectado esté forzada (ej. 100/Full) si el conversor no soporta Auto-Negociación."
  }
];

// Función para buscar por modelo individual dentro del catálogo
export function findFamilyByModel(modelQuery) {
  if (!modelQuery) return null;
  const cleanQuery = modelQuery.trim().toLowerCase();
  
  for (const family of hardwareCatalog) {
    const matchedModel = family.models.find(m => 
      cleanQuery.includes(m.toLowerCase()) || m.toLowerCase().includes(cleanQuery)
    );
    if (matchedModel) {
      return { family, matchedModel };
    }
  }
  return null;
}
