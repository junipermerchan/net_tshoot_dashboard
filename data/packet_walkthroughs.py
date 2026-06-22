"""
Simulaciones de recorrido de paquetes por capas OSI.

Cada escenario representa un flujo completo (encapsulación / desencapsulación)
mostrando, en cada hop/dispositivo, qué capas están presentes, qué headers
deben contener, qué verificar, qué anomalías indican problemas en esa capa,
y qué filtros de captura usar en Wireshark/tcpdump.

Inspirado en la vista de simulación de Packet Tracer, adaptado para
troubleshooting profesional de redes carrier (MPLS, VPNs, VXLAN, GPON, RSVP, PIM, BFD).
"""

from typing import Dict, Any, List

PACKET_WALKTHROUGHS: Dict[str, Any] = {'adtran_ta5000': {'scenarios': [{'description': 'Recorrido completo de un descubrimiento PPPoE (PADI/PADO/PADR/PADS) '
                                                 'y negociación PPP LCP/IPCP desde un ONT conectado a una OLT ADTRAN '
                                                 'TA5000, a través de splitters GPON, hasta el chasis TA5000 y la red '
                                                 'de agregación hacia un BNG/BRAS. Se muestra la encapsulación GEM, '
                                                 'T-CONT y el forwarding L2/L3 en cada salto.',
                                  'id': 'adtran_ta5000_pppoe_gpon',
                                  'name': 'ADTRAN TA5000 - Sesión PPPoE desde ONT hasta BNG',
                                  'steps': [{'action': 'El ONT recibe o genera la trama PPPoE Discovery PADI y la '
                                                       'envía por la interfaz LAN',
                                             'device': 'ONT / Puerto LAN del suscriptor',
                                             'layers': [{'anomalies': 'ONT no bridgea tramas de broadcast (filtrado '
                                                                      'MAC), CPE no inicia PPPoE (firmware/driver), '
                                                                      'VLAN tag en LAN no esperada por el ONT.',
                                                         'checks': 'Puerto LAN del ONT Up/Up; CPE envía tramas PPPoE '
                                                                   'correctamente formadas; sin VLAN tag inesperado '
                                                                   'que aisle el tráfico.',
                                                         'detail': 'DstMAC=FF:FF:FF:FF:FF:FF (broadcast), '
                                                                   'SrcMAC=MAC_CPE_cliente, EtherType=0x8863 (PPPoE '
                                                                   'Discovery). PPPoE Header: Ver=1, Type=1, Code=0x09 '
                                                                   '(PADI), Session_ID=0x0000. Tags: Service-Name, '
                                                                   'Host-Uniq.',
                                                         'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                         'packet_capture': {'notes': 'Filtrar por EtherType 0x8863 '
                                                                                     '(Discovery) o 0x8864 (Session).',
                                                                            'tcpdump_filter': 'pppoes || pppoe',
                                                                            'wireshark_display_filter': 'pppoes || '
                                                                                                        'pppoe'}}],
                                             'note': 'Desde la perspectiva del suscriptor, el ONT es un bridge L2 '
                                                     'transparente. La trama Ethernet broadcast debe alcanzar la OLT '
                                                     'para que el BNG responda.',
                                             'step_title': 'Paso 1: ONT envía PADI broadcast en LAN'},
                                            {'action': 'El ONT encapsula la trama Ethernet en un frame GEM GPON y '
                                                       'transmite en la ventana TDMA asignada',
                                             'device': 'ONT óptico / Splitter GPON',
                                             'layers': [{'anomalies': 'ONT en estado O1-O4 (no sincronizado), GEM port '
                                                                      'no mapeado a la interfaz LAN (OMCI misconfig), '
                                                                      'T-CONT sin asignación de ancho de banda (DBRu '
                                                                      'no reportado), pérdida de señal óptica (LOS).',
                                                         'checks': 'ONT está en estado O5 (Operation) en la OLT. PLOAM '
                                                                   'messages Up/Down funcionando. GEM port de datos '
                                                                   'está activo y mapeado al puerto LAN del ONT en la '
                                                                   'configuración OMCI.',
                                                         'detail': 'GEM Header (5 bytes): PLI=Payload Length '
                                                                   'Indicator, Port ID=GEM_port_dato (ej: 1024), '
                                                                   'PTI=Payload Type Indicator (0=user data), '
                                                                   'HEC=Header Error Control.\n'
                                                                   'T-CONT ID (Alloc-ID): Asignado por la OLT vía '
                                                                   'PLOAM (ej: Alloc-ID=256). El ONT usa este T-CONT '
                                                                   'para solicitar ancho de banda upstream en los '
                                                                   'reportes DBRu.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM)',
                                                         'packet_capture': {'notes': 'Capturar en interfaz PON del '
                                                                                     'TA5000 si soporta port mirror, o '
                                                                                     'usar CLI OMCI debug.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No aplicable '
                                                                                                        '(GPON es '
                                                                                                        'óptico L1, '
                                                                                                        'usar OMCI/GEM '
                                                                                                        'del OLT)'}},
                                                        {'anomalies': 'MTU de GEM menor que la trama Ethernet (drop '
                                                                      'silencioso), GEM frame corrupto (HEC error).',
                                                         'checks': 'La trama Ethernet no se fragmenta dentro del GEM '
                                                                   'frame; tamaño ≤ MTU GEM (ej: 1518 bytes).',
                                                         'detail': 'Trama Ethernet completa encapsulada en el payload '
                                                                   'GEM: DstMAC=broadcast, SrcMAC=MAC_CPE, '
                                                                   'EtherType=0x8863 (PPPoE Discovery).',
                                                         'name': 'Capa 2 - Enlace de Datos (Ethernet sobre GEM)',
                                                         'packet_capture': {'notes': 'Si hay port-mirror en OLT, '
                                                                                     'filtrar por PPPoE.',
                                                                            'tcpdump_filter': 'pppoes || pppoe',
                                                                            'wireshark_display_filter': 'pppoes || '
                                                                                                        'pppoe'}}],
                                             'note': 'En GPON, el tráfico upstream usa TDMA. El ONT espera asignación '
                                                     'de BWmap desde la OLT para transmitir en su T-CONT. La trama '
                                                     'Ethernet se mapea a un GEM port específico.',
                                             'step_title': 'Paso 2: ONT → OLT GPON encapsulación'},
                                            {'action': 'La OLT recibe el frame GEM, desencapsula la trama Ethernet y '
                                                       'la reenvía por el puerto de uplink/agregación',
                                             'device': 'OLT ADTRAN TA5000',
                                             'layers': [{'anomalies': 'GEM Port ID desconocido (provisioning '
                                                                      'incompleto), errores de HEC (interferencia '
                                                                      'óptica), ONT-ID no asignado (PLOAM fallido), '
                                                                      'descarte por policing en el T-CONT.',
                                                         'checks': 'GEM Port ID está registrado en la OLT para el '
                                                                   'ONT-ID correspondiente. OMCI provisioning creó el '
                                                                   'GEM connection correctamente. Sin errores de HEC '
                                                                   'en la interfaz PON.',
                                                         'detail': 'OLT verifica el GEM Header (Port ID, HEC). El GEM '
                                                                   'Port ID identifica el flujo de datos del ONT. El '
                                                                   'frame GEM se desencapsula y se extrae la trama '
                                                                   'Ethernet original.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM) - Recepción',
                                                         'packet_capture': {'notes': 'Verificar contadores GEM/HEC en '
                                                                                     'CLI del TA5000.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No aplicable '
                                                                                                        '(GPON L1)'}},
                                                        {'anomalies': 'VLAN mismatch entre la configuración del TA5000 '
                                                                      'y el agregador, bridge-domain incompleto, '
                                                                      'spanning-tree bloqueando el puerto de uplink, '
                                                                      'MTU insuficiente en uplink.',
                                                         'checks': 'Interfaz PON del TA5000 Up/Up. Bridge-domain o '
                                                                   'VLAN de servicio correctamente configurada. Uplink '
                                                                   'hacia la red de agregación en estado forwarding.',
                                                         'detail': 'Trama Ethernet: DstMAC=broadcast, SrcMAC=MAC_CPE, '
                                                                   'EtherType=0x8863. El TA5000 puede añadir una VLAN '
                                                                   'tag de servicio (S-VLAN) o mantener la tag del '
                                                                   'cliente (C-VLAN) según el modelo de negocio.',
                                                         'name': 'Capa 2 - Enlace de Datos (Ethernet/Bridge)',
                                                         'packet_capture': {'notes': 'Mirror en puerto uplink del '
                                                                                     'TA5000. Filtrar por VLAN de '
                                                                                     'servicio.',
                                                                            'tcpdump_filter': 'pppoes || pppoe || vlan',
                                                                            'wireshark_display_filter': 'pppoes || '
                                                                                                        'pppoe || '
                                                                                                        'vlan.id == '
                                                                                                        'X'}}],
                                             'note': 'El TA5000 actúa como OLT. Recibe el GEM frame upstream, usa el '
                                                     'GEM Port ID para identificar el ONT/T-CONT, extrae la trama '
                                                     'Ethernet y la entrega al dominio de bridge o VLAN configurado.',
                                             'step_title': 'Paso 3: TA5000 procesa frame GPON y bridgea hacia uplink'},
                                            {'action': 'Forwarding L2/L3 a través de la red de agregación hacia el '
                                                       'BNG/BRAS',
                                             'device': 'Switch/Router de agregación',
                                             'layers': [{'anomalies': 'VLAN pruning en trunk (broadcast filtrada), MAC '
                                                                      'learning límite alcanzado, loop protection '
                                                                      'bloqueando broadcast, BNG en VLAN diferente.',
                                                         'checks': 'Trunk de agregación permite la VLAN de servicio. '
                                                                   'MAC learning del CPE presente en switches '
                                                                   'intermedios. Broadcast domain llega hasta la '
                                                                   'interfaz del BNG.',
                                                         'detail': 'DstMAC=FF:FF:FF:FF:FF:FF, SrcMAC=MAC_CPE, '
                                                                   'EtherType=0x8863. Posible 802.1Q tag: VLAN=100 '
                                                                   '(S-VLAN de servicio) o QinQ (C-VLAN + S-VLAN).',
                                                         'name': 'Capa 2 - Enlace de Datos (Ethernet/VLAN)',
                                                         'packet_capture': {'notes': 'Capturar en trunk de agregación '
                                                                                     'o en puerto hacia BNG.',
                                                                            'tcpdump_filter': 'pppoes || pppoe || vlan '
                                                                                              '100',
                                                                            'wireshark_display_filter': 'pppoes || '
                                                                                                        'pppoe || '
                                                                                                        'vlan.id == '
                                                                                                        '100'}},
                                                        {'anomalies': 'Filtrado de EtherType 0x8863 en algún '
                                                                      'dispositivo intermedio (ACL o policy).',
                                                         'checks': 'N/A para esta etapa.',
                                                         'detail': 'No hay IP aún. PPPoE Discovery opera puramente a '
                                                                   'L2 antes de establecer la sesión.',
                                                         'name': 'Capa 3 - Red (IP)',
                                                         'packet_capture': {'notes': 'Confirmar que no hay IP aún; '
                                                                                     'solo PPPoE Discovery.',
                                                                            'tcpdump_filter': 'not ip and pppoes',
                                                                            'wireshark_display_filter': '!ip && '
                                                                                                        'pppoes'}}],
                                             'note': 'El tráfico PPPoE Discovery (broadcast) debe llegar al BNG para '
                                                     'que este responda. Los switches de agregación reenvían la '
                                                     'broadcast dentro de la VLAN de servicio.',
                                             'step_title': 'Paso 4: Agregación → BNG (L2/L3 forwarding)'},
                                            {'action': 'El BNG recibe el PADI broadcast y responde con PADO unicast (o '
                                                       'broadcast en algunos casos)',
                                             'device': 'BNG/BRAS',
                                             'layers': [{'anomalies': 'BNG no responde (PPPoE service disabled), '
                                                                      'filtro de MAC en agregación bloquea retorno, '
                                                                      'Service-Name mismatch (PADO no enviado), límite '
                                                                      'de sesiones PPPoE alcanzado.',
                                                         'checks': 'BNG tiene la interfaz de acceso configurada para '
                                                                   'PPPoE. Servicio AAA/RADIUS disponible. MAC del CPE '
                                                                   'alcanzable vía L2 (la respuesta PADO es unicast).',
                                                         'detail': 'Rx: EtherType=0x8863, Code=0x09 (PADI). Tx: '
                                                                   'DstMAC=MAC_CPE, SrcMAC=MAC_BNG, EtherType=0x8863, '
                                                                   'Code=0x07 (PADO). Session_ID=0x0000. Tags: '
                                                                   'AC-Name, Service-Name.',
                                                         'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                         'packet_capture': {'notes': 'Filtrar PADI (0x09) y PADO '
                                                                                     '(0x07) en Wireshark.',
                                                                            'tcpdump_filter': 'pppoes and (pppoe[0:1] '
                                                                                              '== 0x07 or pppoe[0:1] '
                                                                                              '== 0x09)',
                                                                            'wireshark_display_filter': 'pppoe.code == '
                                                                                                        '0x07 || '
                                                                                                        'pppoe.code == '
                                                                                                        '0x09'}}],
                                             'note': 'El BNG escucha PPPoE Discovery en la interfaz de acceso. Al '
                                                     'recibir PADI, valida el Service-Name tag y responde con PADO '
                                                     'ofreciendo la sesión.',
                                             'step_title': 'Paso 5: BNG recibe PPPoE y envía PADO'},
                                            {'action': 'Intercambio PADR/PADS y negociación PPP LCP/IPCP',
                                             'device': 'ONT → TA5000 → Agregación → BNG',
                                             'layers': [{'anomalies': 'Session_ID duplicado, GEM port cambia durante '
                                                                      'la sesión (drop), MAC del BNG no resuelta en el '
                                                                      'CPE.',
                                                         'checks': 'Session_ID único asignado. Las tramas de sesión '
                                                                   'atraviesan el mismo GEM port, T-CONT y VLAN de '
                                                                   'servicio. Sin broadcast en esta etapa.',
                                                         'detail': 'EtherType=0x8864 (PPPoE Session). PPPoE Header: '
                                                                   'Session_ID=0x00XX (asignado por BNG). La trama es '
                                                                   'unicast L2 entre CPE y BNG (DstMAC=MAC_BNG, '
                                                                   'SrcMAC=MAC_CPE) y viceversa.',
                                                         'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                         'packet_capture': {'notes': 'EtherType 0x8864 (PPPoE '
                                                                                     'Session). Seguir Session_ID '
                                                                                     'específico.',
                                                                            'tcpdump_filter': 'pppoes',
                                                                            'wireshark_display_filter': 'pppoes && '
                                                                                                        'pppoe.code == '
                                                                                                        '0x00'}},
                                                        {'anomalies': 'LCP Configure-NACK/REJ (MRU mismatch), '
                                                                      'autenticación fallida (RADIUS reject), IPCP '
                                                                      'Configure-NACK (pool de IPs agotado), looped '
                                                                      'PPP keepalives.',
                                                         'checks': 'LCP negocia MRU compatible (típicamente 1492 para '
                                                                   'PPPoE). Autenticación RADIUS/AAA exitosa. IPCP '
                                                                   'asigna IP, máscara, gateway y DNS al suscriptor.',
                                                         'detail': 'PPP Header: Protocol=0xC021 (LCP) o 0x8021 (IPCP). '
                                                                   'LCP: Configure-Request/ACK con MRU, Authentication '
                                                                   '(PAP/CHAP). IPCP: Configure-Request/ACK con '
                                                                   'IP-Address (asignada por BNG), Primary/Secondary '
                                                                   'DNS.',
                                                         'name': 'Capa 3 - PPP (LCP/IPCP)',
                                                         'packet_capture': {'notes': 'En Wireshark expandir PPP → '
                                                                                     'Protocol. Filtrar LCP (0xC021) e '
                                                                                     'IPCP (0x8021).',
                                                                            'tcpdump_filter': 'pppoes',
                                                                            'wireshark_display_filter': 'pppoes && '
                                                                                                        '(ppp.protocol '
                                                                                                        '== 0xc021 || '
                                                                                                        'ppp.protocol '
                                                                                                        '== 0x8021)'}}],
                                             'note': 'El CPE envía PADR (unicast) y el BNG responde PADS asignando '
                                                     'Session_ID. Luego inicia LCP (MRU, auth) e IPCP (IP address, '
                                                     'DNS).',
                                             'step_title': 'Paso 6: Sesión establecida - PPP LCP/IPCP'},
                                            {'action': 'El CPE envía el primer paquete IP a través del túnel PPPoE '
                                                       'hacia Internet',
                                             'device': 'CPE / BNG',
                                             'layers': [{'anomalies': 'Ruta faltante en CPE, BNG sin ruta de retorno '
                                                                      '(IP no en tabla), NAT overflow, MTU path issue '
                                                                      '(1492 vs 1500, requiere TCP MSS clamping).',
                                                         'checks': 'Ruta por defecto del CPE apunta a la interfaz '
                                                                   'PPPoE. BNG tiene ruta hacia Internet. NAT o '
                                                                   'routing público configurado correctamente en el '
                                                                   'BNG.',
                                                         'detail': 'SrcIP=IP_asignada_BNG (ej: 100.64.1.10), '
                                                                   'DstIP=IP_destino_internet, TTL=64, '
                                                                   'Protocol=TCP(6). PPP Protocol=0x0021 (IPv4).',
                                                         'name': 'Capa 3 - Red (IPv4)',
                                                         'packet_capture': {'notes': 'Filtrar IP sobre PPPoE Session. '
                                                                                     'Verificar MSS/MTU.',
                                                                            'tcpdump_filter': 'pppoes and ip',
                                                                            'wireshark_display_filter': 'pppoes && '
                                                                                                        'ip'}},
                                                        {'anomalies': 'Session_ID desconocido en BNG (sesión caída), '
                                                                      'GEM port congestionado (T-CONT sin BW '
                                                                      'suficiente), drops de QoS en el TA5000 o BNG.',
                                                         'checks': 'GEM port de datos activo, T-CONT con ancho de '
                                                                   'banda asignado según SLA. Sin drops en la cola '
                                                                   'GEM/T-CONT.',
                                                         'detail': 'EtherType=0x8864 (PPPoE Session), Session_ID '
                                                                   'activo. DstMAC=MAC_BNG, SrcMAC=MAC_CPE. '
                                                                   'Encapsulación GEM con mismo GEM Port ID y T-CONT.',
                                                         'name': 'Capa 2 - Enlace de Datos (PPPoE Session)',
                                                         'packet_capture': {'notes': 'Mirror en uplink del TA5000 o en '
                                                                                     'BNG.',
                                                                            'tcpdump_filter': 'pppoes and ip',
                                                                            'wireshark_display_filter': 'pppoes && '
                                                                                                        'ip'}}],
                                             'note': 'Con la sesión PPPoE activa y la IP asignada, el tráfico de datos '
                                                     'fluye encapsulado en PPPoE Session (0x8864) a través de toda la '
                                                     'cadena GPON.',
                                             'step_title': 'Paso 7: IP asignada - Primer paquete de datos'}]},
                                 {'description': 'Simulación del flujo de mensajes OMCI (ONT Management and Control '
                                                 'Interface) entre la OLT (TA5000 o Huawei/ZTE) y un ONT durante el '
                                                 'proceso de provisioning. Se muestra el uso de PLOAM, GEM port 4095 '
                                                 '(o dedicado), y la transferencia de MIBs.',
                                  'id': 'gpon_omci_provisioning',
                                  'name': 'GPON OLT→ONT - Flujo de aprovisionamiento OMCI',
                                  'steps': [{'action': 'El ONT realiza el procedimiento de ranging y envía su Serial '
                                                       'Number o LOID a la OLT',
                                             'device': 'ONT (GPON)',
                                             'layers': [{'anomalies': 'ONT no responde al Serial_Number_Request (laser '
                                                                      'apagado, fibra cortada), Serial Number '
                                                                      'duplicado en la red, LOID no coincide '
                                                                      '(autenticación fallida), nivel óptico fuera de '
                                                                      'rango (laser degradado).',
                                                         'checks': 'Nivel óptico dentro de rango (TX ONT ~+1.5 dBm, RX '
                                                                   'ONT ~-8 a -28 dBm). ONT sincronizado en O5. Serial '
                                                                   'Number o LOID coincide con la base de datos de la '
                                                                   'OLT.',
                                                         'detail': 'PLOAM Downstream (OLT→ONT): MsgType=0x01 '
                                                                   '(Serial_Number_Request), ONU-ID=0xFF (broadcast '
                                                                   'para ONTs no registrados). PLOAM Upstream '
                                                                   '(ONT→OLT): MsgType=0x02 (Serial_Number_Response), '
                                                                   'incluye Vendor ID, Serial Number (8 bytes) o LOID.',
                                                         'name': 'Capa 2/1 - GPON Frame (PLOAM)',
                                                         'packet_capture': {'notes': 'Usar CLI del OLT: show gpon onu '
                                                                                     'state, show gpon onu detail.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No aplicable '
                                                                                                        '(PLOAM es '
                                                                                                        'L1/L2 GPON)'}},
                                                        {'anomalies': 'OMCI prematuro antes de tener ONT-ID asignado '
                                                                      '(descartado por OLT).',
                                                         'checks': 'N/A - OMCI se establece después de asignar ONT-ID.',
                                                         'detail': 'Aún no hay OMCI. Solo PLOAM para el descubrimiento '
                                                                   'inicial.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM - OMCI)',
                                                         'packet_capture': {'notes': 'N/A',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'Al encenderse, el ONT espera la sincronización de frame '
                                                     'downstream. Una vez sincronizado, responde al Serial Number '
                                                     'Request de la OLT con su SN/LOID en el campo de PLOAM upstream.',
                                             'step_title': 'Paso 1: ONT se enciende y envía SN/LOID upstream'},
                                            {'action': 'La OLT valida el SN/LOID y asigna un ONT-ID único al ONT '
                                                       'mediante PLOAM',
                                             'device': 'OLT (TA5000 / Huawei / ZTE)',
                                             'layers': [{'anomalies': 'ONT-ID ya en uso (conflicto de provisioning), '
                                                                      'SN/LOID no encontrado en OLT (ONT rechazado), '
                                                                      'Ranging fallido (delay excesivo, distancia '
                                                                      'fuera de rango 0-20 km), PLOAM descartado por '
                                                                      'errores de HEC.',
                                                         'checks': 'OLT tiene el ONT pre-provisionado con su SN/LOID '
                                                                   'correcto. ONT-ID asignado no está en uso por otro '
                                                                   'ONT. Ranging completado exitosamente (equalization '
                                                                   'delay calculada).',
                                                         'detail': 'PLOAM Downstream: MsgType=0x03 (Assign_ONU-ID), '
                                                                   'ONU-ID=0xFF→asignado (ej: 0x01), Payload contiene '
                                                                   'el Serial Number del ONT destino para confirmar la '
                                                                   'asignación. Seguido de MsgType=0x04 (Ranging_Time) '
                                                                   'para ajustar el equalization delay.',
                                                         'name': 'Capa 2/1 - GPON Frame (PLOAM)',
                                                         'packet_capture': {'notes': 'CLI OLT: show gpon onu state, '
                                                                                     'show gpon onu detail.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}},
                                                        {'anomalies': 'N/A',
                                                         'checks': 'N/A',
                                                         'detail': 'Aún no se establecen GEM connections de datos. '
                                                                   'Solo PLOAM para control.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM)',
                                                         'packet_capture': {'notes': 'N/A',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'La OLT verifica el SN/LOID contra su base de datos de '
                                                     'suscriptores. Si coincide, envía un mensaje PLOAM Assign ONU-ID '
                                                     'y luego configura los parámetros iniciales del T-CONT y '
                                                     'Alloc-ID.',
                                             'step_title': 'Paso 2: OLT asigna ONT-ID vía PLOAM'},
                                            {'action': 'Se crea el GEM connection para OMCI y comienza el intercambio '
                                                       'de mensajes OMCI',
                                             'device': 'OLT ↔ ONT',
                                             'layers': [{'anomalies': 'GEM Port 4095 en conflicto con datos '
                                                                      '(provisioning incorrecto), OMCI Create fallido '
                                                                      '(ONT no responde), T-CONT de gestión sin BW '
                                                                      'asignado (timeout OMCI).',
                                                         'checks': 'GEM Port para OMCI creado correctamente en OLT y '
                                                                   'ONT vía OMCI Create. T-CONT de gestión tiene ancho '
                                                                   'de banda mínimo garantizado. OMCI MIB sync lista.',
                                                         'detail': 'GEM Header: Port ID=4095 (u otro GEM port dedicado '
                                                                   'para OMCI), PTI=0 (user data), HEC válido. '
                                                                   'Alloc-ID/T-CONT para OMCI separado del tráfico de '
                                                                   'datos (ej: T-CONT 0 o T-CONT gestión).',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM)',
                                                         'packet_capture': {'notes': 'Capturar OMCI solo vía '
                                                                                     'port-mirror especializado del '
                                                                                     'OLT o debug OMCI CLI.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No aplicable '
                                                                                                        '(OMCI sobre '
                                                                                                        'GEM, no '
                                                                                                        'TCP/IP)'}},
                                                        {'anomalies': 'OMCI CRC error (corrupto en tránsito), Message '
                                                                      'Type desconocido (versión OMCI incompatible), '
                                                                      'Entity Instance duplicado, secuencia OMCI '
                                                                      'desalineada (OLT/ONT out of sync).',
                                                         'checks': 'Formato OMCI correcto. CRC-32 del payload OMCI '
                                                                   'válido. Sequence number alineado entre OLT y ONT. '
                                                                   "MIB sync state 'complete' en la OLT.",
                                                         'detail': 'OMCI Message (53 bytes): Transaction Correlation '
                                                                   'Identifier, Message Type (ej: Create=0x04), Device '
                                                                   'Identifier=0x0A (OMCI), Entity Class (ej: GEM '
                                                                   'Interworking TP=0x0101), Entity Instance, '
                                                                   'Attribute Mask, Attribute contents.',
                                                         'name': 'Capa 2 - OMCI sobre GEM',
                                                         'packet_capture': {'notes': 'OMCI no es capturable con '
                                                                                     'Wireshark estándar. Usar '
                                                                                     'herramientas del vendor.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'La OLT envía un mensaje OMCI Create (GEM Interworking TP) para '
                                                     'establecer el canal de gestión. OMCI típicamente usa GEM '
                                                     'Port=4095 en muchas implementaciones, o un GEM port dedicado '
                                                     'configurado en la OLT.',
                                             'step_title': 'Paso 3: Canal OMCI establecido (GEM port 4095 o dedicado)'},
                                            {'action': 'La OLT solicita la MIB del ONT y envía configuraciones de '
                                                       'creación/modificación',
                                             'device': 'OLT (Gestor OMCI)',
                                             'layers': [{'anomalies': 'Errores de HEC en OMCI GEM port '
                                                                      '(interferencia), buffer overflow en ONT '
                                                                      '(demasiados creates seguidos), OMCI timeout por '
                                                                      'T-CONT de gestión compartido con datos (sin '
                                                                      'prioridad).',
                                                         'checks': 'GEM Port de OMCI sin errores de HEC. Buffer de '
                                                                   'OMCI en ONT no desbordado. T-CONT de gestión con '
                                                                   'ancho de banda suficiente para la ráfaga de '
                                                                   'configuración.',
                                                         'detail': 'GEM Header: Port ID=4095 (OMCI). Alloc-ID/T-CONT '
                                                                   'de gestión activo. Frame GEM con prioridad alta en '
                                                                   'el BWmap.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM)',
                                                         'packet_capture': {'notes': 'Verificar contadores GEM/OMCI en '
                                                                                     'CLI del OLT.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}},
                                                        {'anomalies': 'ONT responde con Result=0x01 (Processing error) '
                                                                      'o 0x02 (Busy). ME Instance ya existe (Create '
                                                                      'duplicado), Attribute no soportado por el ONT, '
                                                                      'MIB Upload incompleto (faltan MEs en el ONT).',
                                                         'checks': 'Cada OMCI Create/Set recibe respuesta ACK/MKC (ej: '
                                                                   'Create Response=0x14). Los Entity Instance son '
                                                                   'únicos y consistentes. La OLT espera respuesta '
                                                                   'antes del siguiente request.',
                                                         'detail': 'OMCI Messages: MIB Upload (0x0A), Create (0x04), '
                                                                   'Set (0x08). MEs involucrados: T-CONT (0x0100), GEM '
                                                                   'Port Network CTP (0x0101), GEM Interworking TP '
                                                                   '(0x0102), MAC Bridge Service Profile (0x0105), MAC '
                                                                   'Bridge Port Config Data (0x0106), VLAN Tagging '
                                                                   'Filter Data (0x010B), etc.',
                                                         'name': 'Capa 2 - OMCI sobre GEM',
                                                         'packet_capture': {'notes': 'Usar OMCI debug/trace en CLI del '
                                                                                     'OLT.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'La OLT inicia con MIB Upload para leer la configuración actual '
                                                     'del ONT, luego envía una serie de OMCI Create/Set para '
                                                     'configurar bridges, VLANs, GEM ports de datos, y otros Managed '
                                                     'Entities (ME).',
                                             'step_title': 'Paso 4: OLT envía MIB uploads / create requests'},
                                            {'action': 'El ONT responde a las solicitudes OMCI con sus datos MIB y '
                                                       'confirma las configuraciones',
                                             'device': 'ONT (Agente OMCI)',
                                             'layers': [{'anomalies': 'Result Code=0x03 (Parameter error) - atributo '
                                                                      'fuera de rango. Result Code=0x04 (Unknown '
                                                                      'managed entity) - OLT intenta configurar una '
                                                                      'feature no soportada. OMCI response perdida '
                                                                      '(drop en GEM port), timeout repetido.',
                                                         'checks': 'Las respuestas OMCI llegan dentro del timeout '
                                                                   '(typ: 1s). CRC-32 válido. Result Code=0x00 '
                                                                   '(Command processed successfully) en todas las '
                                                                   'responses.',
                                                         'detail': 'OMCI Response Messages: MIB Upload Next Response '
                                                                   '(0x0C), Get Response (0x0C), Create Response '
                                                                   '(0x14). Contiene los atributos actuales del ONT: '
                                                                   'Serial Number, Hardware Version, Firmware Version, '
                                                                   'capacidades de bridge, VLANs soportadas, puertos '
                                                                   'ETH/FXS/POTS disponibles.',
                                                         'name': 'Capa 2 - OMCI sobre GEM',
                                                         'packet_capture': {'notes': 'Verificar OMCI response timeouts '
                                                                                     'y result codes en CLI OLT.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}},
                                                        {'anomalies': 'ONT no reporta DBRu para el T-CONT de gestión '
                                                                      '(la OLT no asigna ventanas upstream).',
                                                         'checks': 'ONT tiene T-CONT de gestión activo y reportado en '
                                                                   'DBRu. BWmap asigna ventanas para OMCI.',
                                                         'detail': 'GEM Header: Port ID=4095. Payload=OMCI response. '
                                                                   'T-CONT de gestión.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM)',
                                                         'packet_capture': {'notes': 'N/A',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'El ONT actúa como agente OMCI. Responde a los Get/MIB Upload '
                                                     'Next con los valores actuales de sus MEs y confirma los '
                                                     'Create/Set con responses.',
                                             'step_title': 'Paso 5: ONT responde con datos MIB'},
                                            {'action': 'La OLT envía las configuraciones finales de servicio al ONT '
                                                       'vía OMCI',
                                             'device': 'OLT ↔ ONT',
                                             'layers': [{'anomalies': 'VLAN mismatch (OMCI configura VLAN 100 pero el '
                                                                      'servicio usa 200), GEM Port de datos en '
                                                                      'conflicto con otro ONT (Provisioning error), '
                                                                      'T-CONT sin PIR suficiente (servicio degradado '
                                                                      'desde el inicio), Puertos POTS no configurados '
                                                                      '(VoIP no registra).',
                                                         'checks': 'Cada puerto ETH del ONT mapeado al GEM port de '
                                                                   'datos correcto. VLANs de servicio (Internet, IPTV, '
                                                                   'VoIP) configuradas en el tagging filter. T-CONT de '
                                                                   'datos con ancho de banda mínimo/garantizado '
                                                                   '(CIR/PIR) correcto.',
                                                         'detail': 'OMCI Set/Create final para: VLAN Tagging Filter '
                                                                   'Data (0x010B) - VLANs permitidas, MAC Bridge Port '
                                                                   'Config Data (0x0106) - asociación puerto-VLAN, '
                                                                   'PPTP Ethernet UNI (0x0104) - estado de puertos '
                                                                   'LAN, PPTP POTS UNI (0x0103) - configuración de '
                                                                   'puertos de voz, SIP User Data (0x00D5) / SIP '
                                                                   'Config Data (0x00D6) - parámetros VoIP si aplica.',
                                                         'name': 'Capa 2 - OMCI sobre GEM',
                                                         'packet_capture': {'notes': 'Usar CLI del OLT para verificar '
                                                                                     'configuración OMCI final.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}},
                                                        {'anomalies': 'GEM Port de datos creado pero no mapeado a la '
                                                                      'interfaz física (OMCI incomplete), conflicto de '
                                                                      'Alloc-ID entre ONTs (raro, indica provisioning '
                                                                      'duplicado).',
                                                         'checks': 'GEM connection de datos activo en ambos sentidos. '
                                                                   'OMCI MIB sync completo. ONT pasa a estado '
                                                                   'operativo (O5) con todos los servicios '
                                                                   'habilitados.',
                                                         'detail': 'GEM Port de datos (ej: 1024) creado y mapeado al '
                                                                   'T-CONT de datos (ej: 257). GEM Port de OMCI (4095) '
                                                                   'permanece activo para gestión continua.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM)',
                                                         'packet_capture': {'notes': 'N/A',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'Con la MIB sincronizada, la OLT configura los servicios '
                                                     'específicos: mapeo de GEM ports a puertos ETH, configuración de '
                                                     'VLAN tagging, activación de puertos POTS/FXS para VoIP, y QoS.',
                                             'step_title': 'Paso 6: Configuración de servicios aplicada (bridges, '
                                                           'VLANs, VoIP)'},
                                            {'action': 'El ONT completa el provisioning y entra en estado operativo '
                                                       'completo',
                                             'device': 'ONT / OLT',
                                             'layers': [{'anomalies': 'ONT vuelve a O1-O4 (pérdida de sincronización), '
                                                                      'errores BIP crónicos (fibra sucia o mala '
                                                                      'conexión), OMCI timeouts recurrentes (ONT '
                                                                      'colgado, necesita reboot remoto), derrame de '
                                                                      'tráfico entre GEM ports (security issue).',
                                                         'checks': 'ONT estado O5 (Operation) estable. Sin errores de '
                                                                   'HEC crónicos. Contadores de tráfico GEM '
                                                                   'incrementando. OMCI heartbeat/responses activos.',
                                                         'detail': 'PLOAM: Mensajes de mantenimiento periódicos (ej: '
                                                                   'Encryption Key Request/Response si AES está '
                                                                   'habilitado). GEM: Tráfico de datos en GEM port '
                                                                   'asignado + OMCI continuo en GEM port 4095.',
                                                         'name': 'Capa 2/1 - GPON Frame (PLOAM + GEM)',
                                                         'packet_capture': {'notes': 'Monitorear vía CLI: show gpon '
                                                                                     'onu state, show gpon onu '
                                                                                     'counters.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}},
                                                        {'anomalies': 'OMCI channel caído (ONT no responde a pings de '
                                                                      'gestión), AVC notifications perdidas, firmware '
                                                                      'upgrade fallido (imagen corrupta, ONT en estado '
                                                                      'de recuperación).',
                                                         'checks': 'OMCI channel healthy: respuestas dentro de '
                                                                   'timeout, sin CRC errors. Alarm notifications '
                                                                   'llegan a la OLT cuando el ONT detecta eventos '
                                                                   '(LOS, LOF, etc.).',
                                                         'detail': 'OMCI continúa disponible para: Alarm reporting, '
                                                                   'Attribute value change (AVC) notifications, '
                                                                   'Software download (imagen firmware), Remote reset, '
                                                                   'Performance monitoring (PM) data collection.',
                                                         'name': 'Capa 2 - OMCI sobre GEM (Mantenimiento)',
                                                         'packet_capture': {'notes': 'N/A',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'El ONT está listo para pasar tráfico de datos. La OLT muestra el '
                                                     "ONT en estado 'Online' o 'O5'. Los contadores OMCI se "
                                                     'estabilizan y el canal de gestión permanece abierto para futuros '
                                                     'cambios de configuración (SW upgrade, remote reset, etc.).',
                                             'step_title': 'Paso 7: ONT operativo'}]}]},
 'bfd': {'scenarios': [{'description': 'Recorrido del establecimiento de una sesión BFD entre dos routers en modo '
                                       'asíncrono. Se muestra el intercambio de paquetes de control con transición de '
                                       'estados Down→Init→Up, el mantenimiento periódico y la detección de fallo por '
                                       'timeout.',
                        'id': 'bfd_session_up_failure',
                        'name': 'BFD: Establecimiento de sesión y detección rápida de falla',
                        'steps': [{'action': 'Inicia sesión BFD enviando paquete de control con estado Down y Your '
                                             'Discriminator=0',
                                   'device': 'Router A',
                                   'layers': [{'anomalies': 'BFD no habilitado en interfaz (paquete no generado), Your '
                                                            'Disc≠0 en primer paquete (violación RFC), versión '
                                                            'incorrecta.',
                                               'checks': 'BFD habilitado en interfaz de A; timers configurados '
                                                         'consistentemente; UDP 3784 permitido en control plane.',
                                               'detail': 'BFD Control Packet: Version=1, Diagnostic=0 (No Diagnostic), '
                                                         'State=Down (1), Flags=0, Detect Mult=3 (o valor configurado, '
                                                         'ej: 3 para subsecond), Length=24 bytes, My '
                                                         'Discriminator=valor aleatorio único de A (ej: 0xA1B2C3D4), '
                                                         'Your Discriminator=0x00000000 (desconocido), Desired Min TX '
                                                         'Interval=1000000 µs, Required Min RX Interval=1000000 µs, '
                                                         'Min Echo RX Interval=0 (modo async sin echo). UDP '
                                                         'SrcPort=49152+ (efímero), DstPort=3784 (BFD Control).',
                                               'name': 'Capa 4 - UDP/BFD Control',
                                               'packet_capture': {'notes': 'Filtrar BFD Control UDP 3784. State=Down '
                                                                           '(1).',
                                                                  'tcpdump_filter': 'udp port 3784',
                                                                  'wireshark_display_filter': 'udp.port == 3784 && '
                                                                                              'bfd.state == 1'}},
                                              {'anomalies': 'TTL≠255 descartado por B (configuración estricta), IP '
                                                            'checksum corrupto, ACL bloqueando UDP 3784.',
                                               'checks': 'Interfaz A tiene IP configurada; vecino B alcanzable '
                                                         'directamente L3; TTL=255 verificado en recepción.',
                                               'detail': 'SrcIP=interfaz_A, DstIP=interfaz_B, Protocol=UDP (17), '
                                                         'TTL=255 (requerido por BFD para evitar forwarding multi-hop '
                                                         'accidental), IP Checksum válido, TOS/DSCP posiblemente '
                                                         'marcado para prioridad de control plane.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'Verificar TTL=255 obligatorio en BFD.',
                                                                  'tcpdump_filter': 'ip[8:1] == 255 and udp port 3784',
                                                                  'wireshark_display_filter': 'ip.ttl == 255 && '
                                                                                              'udp.port == 3784'}},
                                              {'anomalies': 'ARP incomplete (B no responde), interface down, CRC '
                                                            'errors, duplex mismatch.',
                                               'checks': 'Interfaz Up/Up; ARP/ND resuelto para vecino B; sin '
                                                         'input/output drops.',
                                               'detail': 'DstMAC=interfaz_B_MAC, SrcMAC=interfaz_A_MAC, '
                                                         'EtherType=0x0800 (IPv4).',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'ether proto ip and udp port 3784',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && '
                                                                                              'udp.port == 3784'}}],
                                   'note': 'Router A desea establecer una sesión BFD con su vecino directo. Como aún '
                                           'no conoce el discriminador del vecino, envía Your Disc=0. El paquete usa '
                                           'UDP destino 3784 (control).',
                                   'step_title': 'Paso 1: Router A envía BFD Control (Your Disc=0, State=Down)'},
                                  {'action': 'Recibe paquete BFD de A y responde con estado Init, incluyendo el '
                                             'discriminador de A',
                                   'device': 'Router B',
                                   'layers': [{'anomalies': 'Your Disc no coincide (paquete de A no llegó '
                                                            'correctamente o fue corrompido), B responde State=Down '
                                                            '(no aceptó parámetros), puerto UDP incorrecto.',
                                               'checks': 'B procesó correctamente el paquete de A; Your Disc coincide '
                                                         'con My Disc de A; timers negociables compatibles.',
                                               'detail': 'BFD Control Packet: Version=1, Diagnostic=0, State=Init (2), '
                                                         'Flags=0 (o Poll P=1 si inicia negociación de parámetros), '
                                                         'Detect Mult=3, Length=24, My Discriminator=valor único de B '
                                                         '(ej: 0xB2C3D4E5), Your Discriminator=0xA1B2C3D4 (aprendido '
                                                         'de A), Desired Min TX Interval=1000000 µs, Required Min RX '
                                                         'Interval=1000000 µs, Min Echo RX Interval=0. UDP '
                                                         'DstPort=3784.',
                                               'name': 'Capa 4 - UDP/BFD Control',
                                               'packet_capture': {'notes': 'Filtrar BFD Init (State=2). Verificar Your '
                                                                           'Discriminator.',
                                                                  'tcpdump_filter': 'udp port 3784',
                                                                  'wireshark_display_filter': 'udp.port == 3784 && '
                                                                                              'bfd.state == 2'}},
                                              {'anomalies': 'TTL≠255 descartado por A, routing asimétrico que impide '
                                                            'llegada directa, ACL unidireccional.',
                                               'checks': 'Ruta directa B→A operativa; TTL=255 en respuesta; sin ACL '
                                                         'bloqueando.',
                                               'detail': 'SrcIP=interfaz_B, DstIP=interfaz_A, Protocol=UDP, TTL=255, '
                                                         'IP Checksum válido. TOS/DSCP igual que A.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'ip[8:1] == 255 and udp port 3784',
                                                                  'wireshark_display_filter': 'ip.ttl == 255 && '
                                                                                              'udp.port == 3784'}},
                                              {'anomalies': 'Link unidireccional (A puede enviar pero B no recibe, o '
                                                            'viceversa), MAC de A no aprendida por B.',
                                               'checks': 'L2 bidireccional operativo; MAC de A resuelta.',
                                               'detail': 'DstMAC=interfaz_A_MAC, SrcMAC=interfaz_B_MAC, '
                                                         'EtherType=0x0800.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'ether proto ip and udp port 3784',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && '
                                                                                              'udp.port == 3784'}}],
                                   'note': 'Router B recibe el primer BFD Control de A, aprende My Disc de A y lo usa '
                                           'como Your Disc en su respuesta. B cambia su estado local a Init y lo '
                                           'anuncia.',
                                   'step_title': "Paso 2: Router B responde (Your Disc=A's, State=Init)"},
                                  {'action': 'Intercambio final de paquetes BFD con State=Up, confirmando sesión '
                                             'establecida',
                                   'device': 'Router A y Router B',
                                   'layers': [{'anomalies': 'State flapping (Up/Down por jitter excesivo), timers '
                                                            'incompatibles (TX local mucho menor que RX remoto), '
                                                            'discriminador duplicado.',
                                               'checks': "Ambos routers muestran estado Up en 'show bfd session'; My "
                                                         'Disc y Your Disc cruzados correctamente; timers negociados '
                                                         'dentro de rangos aceptables.',
                                               'detail': 'Router A envía: State=Up (3), Your Disc=0xB2C3D4E5. Router B '
                                                         'responde: State=Up (3), Your Disc=0xA1B2C3D4. Ambos han '
                                                         'recibido al menos un paquete Init/Up del vecino. Flags=0. '
                                                         'Timers negociados: TX = max(Desired Min TX local, Required '
                                                         'Min RX remoto); RX = max(Required Min RX local, Desired Min '
                                                         'TX remoto).',
                                               'name': 'Capa 4 - UDP/BFD Control',
                                               'packet_capture': {'notes': 'Filtrar BFD Up (State=3). Verificar '
                                                                           'consistencia de discriminadores.',
                                                                  'tcpdump_filter': 'udp port 3784',
                                                                  'wireshark_display_filter': 'udp.port == 3784 && '
                                                                                              'bfd.state == 3'}},
                                              {'anomalies': 'Pérdida esporádica de paquetes BFD (flapping de sesión), '
                                                            'congestión en cola de control plane.',
                                               'checks': 'Conectividad IP estable en ambas direcciones; sin pérdida de '
                                                         'paquetes de control.',
                                               'detail': 'SrcIP/DstIP fijos de las interfaces BFD. TTL=255. '
                                                         'Protocol=UDP. Checksum IP válido. TOS/DSCP de control plane.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'ip[8:1] == 255 and udp port 3784',
                                                                  'wireshark_display_filter': 'ip.ttl == 255 && '
                                                                                              'udp.port == 3784'}},
                                              {'anomalies': 'MAC flapping, VLAN mismatch en subinterfaces, STP '
                                                            'reconvergiendo.',
                                               'checks': 'Interfaz Up/Up en ambos lados; sin errors L2; MTU ≥ 1500.',
                                               'detail': 'EtherType=0x0800. MACs de las interfaces directamente '
                                                         'conectadas. Posible 802.1Q tag si subinterfaces BFD.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'ether proto ip and udp port 3784',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && '
                                                                                              'udp.port == 3784'}}],
                                   'note': 'Router A recibe el paquete Init de B, cambia su estado a Up y envía un '
                                           'paquete con State=Up. B recibe ese paquete y también cambia a Up. La '
                                           'sesión está establecida.',
                                   'step_title': 'Paso 3: Ambos alcanzan estado Up'},
                                  {'action': 'Envío periódico de keepalives BFD en modo asíncrono para mantener la '
                                             'sesión',
                                   'device': 'Router A y Router B',
                                   'layers': [{'anomalies': 'Pérdida de paquetes periódicos (excede Detection Time), '
                                                            'jitter alto que retrasa paquetes, contadores de RX '
                                                            'estancados.',
                                               'checks': 'Paquetes de control llegan dentro del Detection Time; '
                                                         'contadores de RX/TX incrementan sin pérdidas; jitter bajo.',
                                               'detail': 'BFD Control periódico: State=Up (3), Flags=0 (sin '
                                                         'Poll/Final), My Disc y Your Disc establecidos. Detect '
                                                         'Mult=3. TX interval negociado (ej: 300ms para subsecond '
                                                         'BFD). Detection Time = Detect Mult × max(RX interval '
                                                         'negociado, RX interval negociado del vecino). Ejemplo: 3 × '
                                                         '300ms = 900ms. UDP DstPort=3784.',
                                               'name': 'Capa 4 - UDP/BFD Control',
                                               'packet_capture': {'notes': 'Verificar periodicidad de keepalives. '
                                                                           'Medir inter-packet gap.',
                                                                  'tcpdump_filter': 'udp port 3784',
                                                                  'wireshark_display_filter': 'udp.port == 3784 && '
                                                                                              'bfd.state == 3'}},
                                              {'anomalies': 'Control plane congestion (paquetes BFD descartados en '
                                                            'cola), QoS mal configurado que no prioriza UDP 3784.',
                                               'checks': 'Cola de control plane no saturada; COS/QoS preserva BFD en '
                                                         'congestión.',
                                               'detail': 'SrcIP/DstIP fijos. TTL=255. Protocol=UDP. TOS/DSCP '
                                                         'priorizado. No hay variación en IPs ni TTL.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'ip[8:1] == 255 and udp port 3784',
                                                                  'wireshark_display_filter': 'ip.ttl == 255 && '
                                                                                              'udp.port == 3784'}},
                                              {'anomalies': 'Micro-cortes L2 no detectados por otras capas pero '
                                                            'suficientes para perder múltiples paquetes BFD '
                                                            'consecutivos.',
                                               'checks': 'L2 estable; sin micro-cortes; sin buffer overflows.',
                                               'detail': 'EtherType=0x0800. DstMAC del vecino directo. Posible 802.1Q '
                                                         'tag.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'ether proto ip and udp port 3784',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && '
                                                                                              'udp.port == 3784'}}],
                                   'note': 'En modo asíncrono, ambos routers envían paquetes de control periódicamente '
                                           'según el intervalo TX negociado. No se requiere tráfico de datos para '
                                           'mantener la sesión.',
                                   'step_title': 'Paso 4: Intercambio periódico de paquetes BFD (modo async)'},
                                  {'action': 'El enlace falla y los paquetes BFD dejan de recibirse',
                                   'device': 'Router A (monitoring) / Medio físico',
                                   'layers': [{'anomalies': 'Link unidireccional (A sigue enviando pero no recibe), '
                                                            'interfaz atascada en Up/Up pero sin tráfico (silent '
                                                            'failure), layer 1 degradado con BER alto.',
                                               'checks': 'Interface A muestra Down/Down o errores incrementándose; '
                                                         'carrier detect ausente.',
                                               'detail': 'Link down detectado físicamente (carrier loss, LOS, LACP '
                                                         'down) o frames Ethernet dejan de llegar. DstMAC del vecino '
                                                         'ya no es alcanzable. Posibles CRC errors, runts, o input '
                                                         'errors previos al fallo total.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'Capturar en ambos sentidos. Si A no ve '
                                                                           'paquetes de B durante > Detection Time, '
                                                                           'hay fallo.',
                                                                  'tcpdump_filter': 'udp port 3784',
                                                                  'wireshark_display_filter': 'frame.interface_id == '
                                                                                              'interfaz_A && udp.port '
                                                                                              '== 3784'}},
                                              {'anomalies': 'Solo paquetes BFD descartados (ACL específica), mientras '
                                                            'otros IPs pasan (falso positivo de fallo).',
                                               'checks': 'Contadores de input IP en interfaz de A no incrementan; '
                                                         "'show bfd session' muestra paquetes RX detenidos.",
                                               'detail': 'No llegan paquetes IP de ningún tipo (ni BFD ni datos) desde '
                                                         'B. TTL no es factor porque el paquete nunca es recibido. El '
                                                         'control plane de A no ve actividad UDP 3784.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'Verificar ausencia de paquetes BFD de B.',
                                                                  'tcpdump_filter': 'udp port 3784',
                                                                  'wireshark_display_filter': 'udp.port == 3784'}},
                                              {'anomalies': 'BFD echo packets (puerto 3785) también ausentes si están '
                                                            'habilitados; detección de fallo solo por control plane si '
                                                            'echo no se usa.',
                                               'checks': 'A identifica correctamente la ausencia de paquetes BFD (no '
                                                         'hay paquetes OOB ni falsos positivos).',
                                               'detail': 'Ausencia total de paquetes BFD Control de B. El contador de '
                                                         'RX missed en A incrementa. No se reciben keepalives dentro '
                                                         'del Detection Time configurado.',
                                               'name': 'Capa 4 - UDP/BFD Control',
                                               'packet_capture': {'notes': 'Confirmar ausencia completa de paquetes '
                                                                           'BFD.',
                                                                  'tcpdump_filter': 'udp port 3784',
                                                                  'wireshark_display_filter': 'udp.port == 3784'}}],
                                   'note': 'Se produce una interrupción física o lógica del enlace. Los paquetes BFD '
                                           'enviados por B ya no llegan a A. A deja de recibir keepalives.',
                                   'step_title': 'Paso 5: Fallo de enlace: los paquetes dejan de llegar'},
                                  {'action': 'Detection Time expira y los clientes BFD (IGP/BGP/MPLS) son notificados '
                                             'del fallo',
                                   'device': 'Router A',
                                   'layers': [{'anomalies': 'Cliente no registrado correctamente (no recibe '
                                                            'notificación), reconvergencia masiva en red por timer de '
                                                            'Detection Time muy agresivo en muchas sesiones, flapping '
                                                            'por false positive.',
                                               'checks': 'Clientes BFD reaccionan correctamente (OSPF baja adyacencia, '
                                                         'BGP withdraw routes, IGP recalcula SPF).',
                                               'detail': 'Detection Time expirado. Router A cambia State a Down (1). '
                                                         'Diagnostic=1 (Control Detection Time Expired) o 2 (Echo '
                                                         'Function Failed) si usaba echo. Se invoca callback a '
                                                         'clientes registrados: OSPF, IS-IS, BGP, MPLS-TE, etc. Estos '
                                                         'protocolos inician reconvergencia inmediata sin esperar sus '
                                                         'propios timers.',
                                               'name': 'Capa 4 - UDP/BFD Control',
                                               'packet_capture': {'notes': 'Capturar últimos paquetes BFD antes del '
                                                                           'fallo. State final=Down (1).',
                                                                  'tcpdump_filter': 'udp port 3784',
                                                                  'wireshark_display_filter': 'udp.port == 3784 && '
                                                                                              'bfd.state == 1'}},
                                              {'anomalies': 'IGP no tiene ruta alternativa (tráfico blackholed), BGP '
                                                            'graceful restart evita withdraw pero el next-hop sigue '
                                                            'siendo inalcanzable.',
                                               'checks': 'IGP/BGP convergen rápidamente usando rutas alternativas; no '
                                                         'hay blackholes prolongados.',
                                               'detail': 'BFD ya no envía paquetes de control (o envía final con '
                                                         'State=Down). Los clientes (IGP/BGP) pueden generar sus '
                                                         'propios paquetes de notificación (LSA update, BGP UPDATE '
                                                         'withdraw) usando IPs normales.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'Capturar tráfico de reconvergencia IGP/BGP '
                                                                           'después del fallo BFD.',
                                                                  'tcpdump_filter': 'ospf or bgp or isis',
                                                                  'wireshark_display_filter': 'ospf || bgp || isis'}},
                                              {'anomalies': 'Interfaz permanece Up/Up a pesar del fallo (silent '
                                                            'failure que solo BFD detectó), loop L2 en path '
                                                            'alternativo.',
                                               'checks': 'Interface down confirmado. Si hay path alternativo L2 (LAG, '
                                                         'ECMP), el tráfico de datos ya fue desviado por los clientes.',
                                               'detail': 'La interfaz puede estar Down/Down. EtherType irrelevante '
                                                         'porque la sesión BFD yace sobre un medio inoperativo. Si el '
                                                         'enlace se recupera, el proceso de BFD reinicia desde Down.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'Si el enlace se recupera, capturar '
                                                                           'reinicio de sesión BFD desde Down.',
                                                                  'tcpdump_filter': 'udp port 3784',
                                                                  'wireshark_display_filter': 'udp.port == 3784'}}],
                                   'note': 'Router A espera el Detection Time (ej: 900ms con subsecond BFD). Al no '
                                           'recibir paquetes, declara la sesión Down y notifica a todos los protocolos '
                                           'clientes registrados.',
                                   'step_title': 'Paso 6: Timeout de detección, IGP/BGP notificados'}]}]},
 'evpn': {'scenarios': [{'description': 'Simulación de un paquete unicast entre dos hosts en la misma EVI (EVPN '
                                        'Instance) usando EVPN-MPLS. Se muestra cómo el MAC learning se realiza vía '
                                        'BGP y cómo se usa el label de servicio EVPN.',
                         'id': 'evpn_type2_mpls_unicast',
                         'name': 'EVPN Type 2: Unicast MAC/IP sobre MPLS',
                         'steps': [{'action': 'Genera trama Ethernet unicast',
                                    'device': 'Host A / CE-A',
                                    'layers': [{'anomalies': 'ARP unanswered (Host B no alcanzable L2), proxy-ARP mal '
                                                             'configurado.',
                                                'checks': 'Hosts en misma subred; ARP resuelto (MAC B conocida).',
                                                'detail': 'SrcIP=172.16.10.1, DstIP=172.16.10.2, TTL=64. Dentro de '
                                                          'trama Ethernet.',
                                                'name': 'Capa 3 - Red (IPv4)',
                                                'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                            'fragmentación.',
                                                                   'tcpdump_filter': 'ip',
                                                                   'wireshark_display_filter': 'ip'}},
                                               {'anomalies': 'MAC B desconocida (flooding BUM innecesario), MAC B '
                                                             'apuntando a wrong interface.',
                                                'checks': 'CE-A tiene MAC B aprendida vía EVPN (Type 2) o localmente.',
                                                'detail': 'DstMAC=MAC_HostB, SrcMAC=MAC_HostA, EtherType=0x0800, '
                                                          'VLAN=200.',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}}],
                                    'note': 'Host B está en el mismo segmento Ethernet (misma EVI/VLAN) pero en otro '
                                            'sitio. CE-A ya aprendió que MAC B está detrás de PE-A (por proxy o porque '
                                            'es multihomed).',
                                    'step_title': 'Paso 1: Host A envía trama a MAC de Host B'},
                                   {'action': 'Push EVPN label + Transport label + entrega al core MPLS',
                                    'device': 'Router PE-A (Ingress)',
                                    'layers': [{'anomalies': 'EVI-VLAN binding incorrecto, bridge domain Down.',
                                                'checks': 'EVI 100 mapeada a VLAN 200 correctamente. Bridge domain en '
                                                          'PE-A asocia VLAN 200 con EVI 100.',
                                                'detail': 'Trama Ethernet completa preservada (MACs, VLAN tag, payload '
                                                          'IP).',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet Original)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}},
                                               {'anomalies': 'BGP EVPN session Down, AFI/SAFI EVPN no negociado, RT '
                                                             'mismatch (ruta Type 2 filtrada), label EVPN no asignado, '
                                                             'MTU insuficiente en core.',
                                                'checks': 'BGP EVPN peer UP (PE-A ↔ PE-B o vía Route Reflector). Ruta '
                                                          'Type 2 para MAC B presente en rib evpn. Label EVPN 7001 '
                                                          'asignado y anunciado. MTU ≥ 1516 (1500 + 14 + 8 MPLS).',
                                                'detail': 'Bottom Label (EVPN/Servicio): Label=7001, EXP=0, S=1, '
                                                          'TTL=64\n'
                                                          'Top Label (Transporte/LDP o SR): Label=1024, EXP=0, S=0, '
                                                          'TTL=63\n'
                                                          'Label 7001 identifica la EVI y el destino MAC en PE-B.',
                                                'name': 'Capa 2.5 - MPLS (Label Stack - Doble)',
                                                'packet_capture': {'notes': 'Verificar label stack, EXP bits, S-bit, '
                                                                            'TTL.',
                                                                   'tcpdump_filter': 'mpls',
                                                                   'wireshark_display_filter': 'mpls'}},
                                               {'anomalies': 'LDP/SR no asignó label para PE-B loopback.',
                                                'checks': 'MPLS habilitado en interfaz core.',
                                                'detail': 'DstMAC=P_router, SrcMAC=PE-A, EtherType=0x8847.',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet Core)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}}],
                                    'note': 'PE-A aprendió MAC B vía BGP EVPN Type 2 de PE-B. La ruta Type 2 anunció '
                                            'label EVPN=7001 y next-hop=PE-B loopback.',
                                    'step_title': 'Paso 2: PE-A encapsula en EVPN-MPLS'},
                                   {'action': 'Swap de transport label + PHP',
                                    'device': 'Routers P (Transit)',
                                    'layers': [{'anomalies': 'Transport label no resuelto, LFIB drop, PHP no funciona.',
                                                'checks': 'LFIB con swap/pop correcto. EVPN label no tocado.',
                                                'detail': 'Transport label swappeado en cada P y finalmente popeado '
                                                          'por el penúltimo P (PHP).\n'
                                                          'EVPN label=7001 permanece intacto durante todo el trayecto '
                                                          'del core.',
                                                'name': 'Capa 2.5 - MPLS (Label Stack)',
                                                'packet_capture': {'notes': 'Verificar label stack, EXP bits, S-bit, '
                                                                            'TTL.',
                                                                   'tcpdump_filter': 'mpls',
                                                                   'wireshark_display_filter': 'mpls'}},
                                               {'anomalies': 'Link down en path MPLS.',
                                                'checks': 'Conectividad L2 entre todos los nodos del LSP.',
                                                'detail': 'Ethernet reescrita salto a salto.',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}}],
                                    'note': 'El core MPLS reenvía basado en el top label (transporte). El EVPN label y '
                                            'la trama Ethernet son opacos.',
                                    'step_title': 'Paso 3: Core MPLS reenvía hacia PE-B'},
                                   {'action': 'Pop EVPN label + bridge domain lookup + entrega por AC',
                                    'device': 'Router PE-B (Egress)',
                                    'layers': [{'anomalies': 'EVI no encontrada para label 7001, bridge domain '
                                                             'mismatch, MAC B no aprendida localmente (host B '
                                                             'desconectado).',
                                                'checks': 'PE-B tiene EVI 100 con VLAN 200. Bridge domain asocia '
                                                          'correctamente. MAC B aprendida localmente en AC hacia CE-B.',
                                                'detail': 'Trama Ethernet: DstMAC=MAC_HostB, SrcMAC=MAC_HostA, '
                                                          'EtherType=0x0800, VLAN=200.',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet Original)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}}],
                                    'note': 'PE-B recibe el paquete con EVPN label=7001. Usa ILM para identificar EVI '
                                            '100. Elimina el label EVPN y reenvía la trama Ethernet al bridge domain '
                                            'correspondiente.',
                                    'step_title': 'Paso 4: PE-B recibe y decapsula'},
                                   {'action': 'Forwarding L2 final',
                                    'device': 'CE-B',
                                    'layers': [{'anomalies': 'Host B no responde, spanning-tree bloqueo, MAC flapping.',
                                                'checks': 'Host B recibe frame, responde, conectividad confirmada.',
                                                'detail': 'Trama Ethernet entregada a Host B.',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}}],
                                    'note': 'Entrega la trama Ethernet original al puerto donde está Host B.',
                                    'step_title': 'Paso 5: CE-B entrega a Host B'}]}]},
 'l2vpn': {'scenarios': [{'description': 'Simulación de una trama Ethernet de cliente transportada punto-a-punto sobre '
                                         'un Pseudowire MPLS (VPWS). Se muestra la encapsulación MPLS con PW label + '
                                         'Transport label, y el uso opcional de Control Word.',
                          'id': 'l2vpn_vpws_ethernet',
                          'name': 'Trama Ethernet sobre VPWS (Pseudowire MPLS)',
                          'steps': [{'action': 'Genera trama Ethernet normal (sin conocimiento de MPLS)',
                                     'device': 'Host A / CE-A',
                                     'layers': [{'anomalies': 'ARP timeout (host B no responde), IP en subred '
                                                              'diferente (gateway missing).',
                                                 'checks': 'Hosts en misma subred IP; ARP resuelto localmente.',
                                                 'detail': 'SrcIP=192.168.100.10, DstIP=192.168.100.20, TTL=64. Dentro '
                                                           'de la trama Ethernet.',
                                                 'name': 'Capa 3 - Red (IPv4)',
                                                 'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                             'fragmentación.',
                                                                    'tcpdump_filter': 'ip',
                                                                    'wireshark_display_filter': 'ip'}},
                                                {'anomalies': 'MAC B no aprendida, VLAN 100 no configurada en puerto '
                                                              'de host, STP bloqueando.',
                                                 'checks': 'Hosts en mismo broadcast domain L2; switches CE-A aprenden '
                                                           'MAC B.',
                                                 'detail': 'DstMAC=MAC_HostB, SrcMAC=MAC_HostA, EtherType=0x0800. '
                                                           'Posible 802.1Q VLAN=100 (tag de cliente).',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet Original)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'Desde la perspectiva del host, la red es una simple LAN Ethernet '
                                             'extendida.',
                                     'step_title': 'Paso 1: Host A genera trama Ethernet'},
                                    {'action': 'Forwarding L2 hacia PE-A a través del Attachment Circuit (AC)',
                                     'device': 'CE-A / Switch de borde',
                                     'layers': [{'anomalies': 'AC en Down, MTU del AC menor que la trama (drops en '
                                                              'PE-A), VLAN mismatch entre CE-A y PE-A.',
                                                 'checks': 'Interfaz AC en PE-A está Up/Up; MTU del AC ≥ 1500 (o mayor '
                                                           'si jumbo frames).',
                                                 'detail': 'Misma trama Ethernet. Si el AC es trunk, conserva la tag '
                                                           'VLAN=100.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'El AC puede ser una interfaz física, una subinterface VLAN, o '
                                             'unBundle/Ethernet.',
                                     'step_title': 'Paso 2: CE-A entrega trama a PE-A (AC)'},
                                    {'action': 'Push PW Label + Transport Label + Control Word (opcional)',
                                     'device': 'Router PE-A (Ingress)',
                                     'layers': [{'anomalies': 'PE-A hace rewrite de VLAN inesperado, strip de tag '
                                                              'requerido no realizado.',
                                                 'checks': 'PE-A no debe modificar MAC addresses del cliente ni quitar '
                                                           'VLAN tag (salvo configuración de rewrite).',
                                                 'detail': 'La trama Ethernet completa (incluyendo MAC addresses, VLAN '
                                                           'tag, EtherType, payload IP) se preserva intacta.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet Original del Cliente)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}},
                                                {'anomalies': 'CW mismatch: un lado envía CW y el otro no lo espera → '
                                                              'frame descartado o malinterpretado.',
                                                 'checks': 'Ambos extremos (PE-A y PE-B) tienen control-word '
                                                           'configurado consistentemente (ambos sí o ambos no).',
                                                 'detail': 'Si está habilitado: 4 bytes entre MPLS y Ethernet. Campos: '
                                                           'Flags(4b), Frag(2b), Len(6b), Seq#(16b). Valor '
                                                           'típico=0x00000000.',
                                                 'name': 'Capa 2.5 - Control Word (Opcional)'},
                                                {'anomalies': 'PW label no asignado (LDP FEC 128 Down), VC ID mismatch '
                                                              '(100 vs 200), MTU insuficiente en core (drops '
                                                              'silenciosos), label TTL=1.',
                                                 'checks': 'LDP FEC 128 session UP entre PE-A y PE-B para VC ID 100. '
                                                           "Labels locales/remotos visibles en 'show l2vpn pw' o "
                                                           'equivalente. MTU ≥ 1516 (1500 + 14 Ethernet + 4 CW + 8 '
                                                           'MPLS).',
                                                 'detail': 'Bottom Label (PW):  Label=5001, EXP=0, S=1, TTL=64\n'
                                                           'Top Label (Transporte/LDP): Label=1024, EXP=0, S=0, '
                                                           'TTL=63\n'
                                                           'S=1 en PW indica fondo de pila.',
                                                 'name': 'Capa 2.5 - MPLS (Label Stack - Doble)',
                                                 'packet_capture': {'notes': 'Verificar label stack, EXP bits, S-bit, '
                                                                             'TTL.',
                                                                    'tcpdump_filter': 'mpls',
                                                                    'wireshark_display_filter': 'mpls'}},
                                                {'anomalies': 'Interfaz MPLS down, LDP adjacency flapping, MTU core '
                                                              'menor que 1516.',
                                                 'checks': 'Interfaz core MPLS Up; LDP descubrió vecino; sin output '
                                                           'drops.',
                                                 'detail': 'DstMAC=P_router_if, SrcMAC=PE-A_if, EtherType=0x8847 (MPLS '
                                                           'Unicast).',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet del Core)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'PE-A mapea el AC a la instancia VPWS con VC ID=100. Mediante LDP FEC '
                                             '128, se acordó PW label=5001 con PE-B.',
                                     'step_title': 'Paso 3: PE-A encapsula en Pseudowire MPLS'},
                                    {'action': 'Intercambia label de transporte. PW label y trama Ethernet intactos.',
                                     'device': 'Router P (Transit)',
                                     'layers': [{'anomalies': 'LFIB incompleta para transport label.',
                                                 'checks': 'LFIB con swap correcto. Label 5001 no inspeccionado.',
                                                 'detail': 'Top label transporte: 1024 → 2048 (TTL=62). Bottom label '
                                                           'PW=5001 sin cambios.',
                                                 'name': 'Capa 2.5 - MPLS (Label Stack)',
                                                 'packet_capture': {'notes': 'Verificar label stack, EXP bits, S-bit, '
                                                                             'TTL.',
                                                                    'tcpdump_filter': 'mpls',
                                                                    'wireshark_display_filter': 'mpls'}},
                                                {'anomalies': 'Link down en path.',
                                                 'checks': 'Forwarding L2 correcto hacia PE-B.',
                                                 'detail': 'Ethernet reescrita con MACs del next hop.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'El P-router no mira más allá del top label. La trama del cliente es '
                                             'completamente opaca.',
                                     'step_title': 'Paso 4: P Router swap del Transport Label'},
                                    {'action': 'Pop del transport label. Paquete llega a PE-B con PW label únicamente.',
                                     'device': 'Router P (Penúltimo)',
                                     'layers': [{'anomalies': 'Transport label no removido; PE-B recibe doble stack '
                                                              'inesperado.',
                                                 'checks': "PHP habilitado; LFIB muestra 'Pop' para la FEC de PE-B "
                                                           'loopback.',
                                                 'detail': 'Stack restante: únicamente PW Label=5001 (S=1, TTL=64).',
                                                 'name': 'Capa 2.5 - MPLS (Label Stack)',
                                                 'packet_capture': {'notes': 'Verificar label stack, EXP bits, S-bit, '
                                                                             'TTL.',
                                                                    'tcpdump_filter': 'mpls',
                                                                    'wireshark_display_filter': 'mpls'}},
                                                {'anomalies': 'Interfaz esperando IP (0x0800) y rechaza MPLS.',
                                                 'checks': 'Interfaz soporta MPLS.',
                                                 'detail': 'DstMAC=PE-B_if, SrcMAC=P_if, EtherType=0x8847.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'PE-B anunció implicit-null para su loopback. El penúltimo P elimina el '
                                             'top label.',
                                     'step_title': 'Paso 5: P Penúltimo hace PHP'},
                                    {'action': 'Pop PW label + entrega trama Ethernet original por AC',
                                     'device': 'Router PE-B (Egress)',
                                     'layers': [{'anomalies': 'CW presente cuando PE-B no lo espera → frame '
                                                              'malformado.',
                                                 'checks': 'Secuencia CW consistente (sin saltos anómalos que indiquen '
                                                           'reordenamiento).',
                                                 'detail': 'Si estaba presente, PE-B lo remueve antes de entregar la '
                                                           'trama Ethernet.',
                                                 'name': 'Capa 2.5 - Control Word (Opcional)'},
                                                {'anomalies': 'PE-B hizo rewrite de MAC (mal configurado), strip de '
                                                              'VLAN no deseado, MTU AC menor que trama.',
                                                 'checks': 'PE-B no modificó MAC addresses. VLAN tag preservada. MTU '
                                                           'del AC soporta la trama.',
                                                 'detail': 'Trama Ethernet idéntica a la enviada por Host A: '
                                                           'DstMAC=MAC_HostB, SrcMAC=MAC_HostA, EtherType=0x0800, '
                                                           'VLAN=100.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet Original)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'PE-B ve PW label=5001. Consulta la tabla de incoming labels para VPWS. '
                                             'Saca el PW label y el Control Word (si existe). Reenvía la trama '
                                             'Ethernet original por el AC hacia CE-B.',
                                     'step_title': 'Paso 6: PE-B decapsula y entrega por AC'},
                                    {'action': 'Forwarding L2 final',
                                     'device': 'CE-B / Switch',
                                     'layers': [{'anomalies': 'Host B apagado, MAC B no aprendida, spanning-tree '
                                                              'bloqueando puerto de Host B.',
                                                 'checks': 'Host B responde; MAC B aprendida en tabla CAM del switch '
                                                           'CE-B.',
                                                 'detail': 'DstMAC=MAC_HostB, SrcMAC=MAC_HostA, EtherType=0x0800, '
                                                           'VLAN=100.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'CE-B recibe la trama Ethernet y la entrega al puerto donde está '
                                             'conectado Host B.',
                                     'step_title': 'Paso 7: CE-B entrega a Host B'}]}]},
 'l3vpn': {'scenarios': [{'description': 'Recorrido de un paquete entre dos sitios de cliente (CE-CE) a través de una '
                                         'L3VPN MPLS. Se muestra el doble label stack (Transporte + VPN) y cómo los '
                                         'PEs usan VRFs para aislar tráfico.',
                          'id': 'l3vpn_ipv4_double_stack',
                          'name': 'Paquete IPv4 en L3VPN (doble stack MPLS)',
                          'steps': [{'action': 'Genera paquete IP dentro del espacio de direcciones del cliente',
                                     'device': 'Host / CE-A',
                                     'layers': [{'anomalies': 'Timeout local, proxy mal configurado, firewall en CE '
                                                              'descartando.',
                                                 'checks': 'Aplicación funcionando localmente; no hay cortafuegos en '
                                                           'CE bloqueando salida.',
                                                 'detail': 'Payload de aplicación del cliente (HTTP, SMB, SSH, etc.)',
                                                 'name': 'Capa 7/6/5 - Aplicación/Presentación/Sesión'},
                                                {'anomalies': 'Traceroute se detiene en PE (ACL), MTU path descubierto '
                                                              'menor a 1500.',
                                                 'checks': 'Conectividad L3 básica desde CE-A hacia CE-B verificada '
                                                           'con ping/traceroute.',
                                                 'detail': 'TCP/UDP Header con puertos origen/destino del servicio.',
                                                 'name': 'Capa 4 - Transporte'},
                                                {'anomalies': 'Ruta faltante en CE-A; CE-A no anuncia/redistribuye '
                                                              'prefijos correctamente hacia PE-A.',
                                                 'checks': 'CE-A tiene ruta hacia 10.2.2.0/24 vía PE-A '
                                                           '(BGP/OSPF/estático dentro de la VRF o global si CE '
                                                           'simple).',
                                                 'detail': 'SrcIP=10.1.1.10, DstIP=10.2.2.20, TTL=64, Protocol=TCP(6), '
                                                           'Len=1500. Usa prefijo privado del cliente.',
                                                 'name': 'Capa 3 - Red (IPv4 del Cliente)',
                                                 'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                             'fragmentación.',
                                                                    'tcpdump_filter': 'ip',
                                                                    'wireshark_display_filter': 'ip'}},
                                                {'anomalies': 'VLAN mismatch, MTU bajo, interface errors.',
                                                 'checks': 'Interfaz Up, MTU ≥ 1500, VLAN de servicio correcta.',
                                                 'detail': 'Ethernet frame entre Host y CE-A (o CE-A y PE-A). '
                                                           'EtherType=0x0800.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'El cliente usa RFC1918. El paquete es IPv4 normal; desconoce la '
                                             'existencia de la VPN.',
                                     'step_title': 'Paso 1: Host Origen en sitio A'},
                                    {'action': 'VRF lookup + Push double label stack (VPN + Transport)',
                                     'device': 'Router PE-A (Ingress)',
                                     'layers': [{'anomalies': 'Ruta no presente en VRF (RT import/export incorrecto), '
                                                              'MP-BGP peer down, next-hop inalcanzable en global.',
                                                 'checks': "VRF 'CLIENTE_A' tiene ruta para 10.2.2.0/24 con "
                                                           'next-hop=PE-B_loopback (resuelto por IGP global).',
                                                 'detail': 'IP header intacto. PE-A no modifica IPs del cliente (salvo '
                                                           'TTL decrement si hace routing).',
                                                 'name': 'Capa 3 - Red (IPv4 del Cliente)',
                                                 'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                             'fragmentación.',
                                                                    'tcpdump_filter': 'ip',
                                                                    'wireshark_display_filter': 'ip'}},
                                                {'anomalies': 'VPN label ausente (MP-BGP no anunció label), Transport '
                                                              'label ausente (LDP down para loopback de PE-B), MTU '
                                                              'insuficiente causando drops silenciosos, TTL=1 en '
                                                              'labels.',
                                                 'checks': 'MP-BGP anunció label VPN=8001 para el prefijo 10.2.2.0/24. '
                                                           'LDP anunció label transporte=1024 para alcanzar PE-B '
                                                           'loopback. MTU ≥ 1512 (1500 IP + 8 MPLS + 14 Ethernet).',
                                                 'detail': 'Top Label (Transporte/LDP): Label=1024, EXP=0, S=0, '
                                                           'TTL=63\n'
                                                           'Bottom Label (VPN/BGP):   Label=8001, EXP=0, S=1, TTL=63\n'
                                                           'S-bit=1 indica el fondo de la pila. El label VPN '
                                                           'identifica la VRF en PE-B.',
                                                 'name': 'Capa 2.5 - MPLS (Label Stack - Doble)',
                                                 'packet_capture': {'notes': 'Verificar label stack, EXP bits, S-bit, '
                                                                             'TTL.',
                                                                    'tcpdump_filter': 'mpls',
                                                                    'wireshark_display_filter': 'mpls'}},
                                                {'anomalies': 'Interface MPLS down, LDP adjacency Down, MTU mismatch '
                                                              'entre PE y P.',
                                                 'checks': "'family mpls' activo; MTU ajustada; LDP descubrió vecino "
                                                           'en interfaz de salida.',
                                                 'detail': 'DstMAC=P_router_if, SrcMAC=PE-A_if, EtherType=0x8847. '
                                                           'Interfaz core MPLS.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': "PE-A recibe el paquete en una interfaz asignada a la VRF 'CLIENTE_A'. "
                                             'Consulta la VRF FIB. El destino 10.2.2.0/24 fue aprendido vía MP-BGP '
                                             'desde PE-B.',
                                     'step_title': 'Paso 2: PE-A recibe y clasifica en VRF'},
                                    {'action': 'Swap del top label únicamente. El VPN label permanece intacto.',
                                     'device': 'Router P (Transit)',
                                     'layers': [{'anomalies': 'LFIB sin entrada para 1024 (drop), Swap a interfaz '
                                                              'equivocada, label TTL expired.',
                                                 'checks': 'LFIB tiene entrada para 1024 con acción Swap a 2048. El '
                                                           'label 8001 no es consultado.',
                                                 'detail': 'Top Label: 1024 → 2048 (S=0, TTL=62)\n'
                                                           'Bottom Label: 8001 (S=1, TTL=63 sin cambios)\n'
                                                           'El VPN label es opaco para el P-router.',
                                                 'name': 'Capa 2.5 - MPLS (Label Stack)',
                                                 'packet_capture': {'notes': 'Verificar label stack, EXP bits, S-bit, '
                                                                             'TTL.',
                                                                    'tcpdump_filter': 'mpls',
                                                                    'wireshark_display_filter': 'mpls'}},
                                                {'anomalies': 'L2 loop, MAC unicast flooding, link down.',
                                                 'checks': 'MAC forwarding correcto hacia next-hop MPLS.',
                                                 'detail': 'Ethernet reescrita: DstMAC=next_hop, SrcMAC=P_if, '
                                                           'EtherType=0x8847.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'El P-router solo mira el label superior (transporte). No tiene '
                                             'visibilidad del VPN label ni del IP del cliente.',
                                     'step_title': 'Paso 3: P Router intercambia Label de Transporte'},
                                    {'action': 'Pop del label de transporte (PHP). El paquete llega a PE-B con solo el '
                                               'VPN label.',
                                     'device': 'Router P (Penúltimo Hop)',
                                     'layers': [{'anomalies': 'PHP no habilitado → PE-B recibe doble stack (aumenta '
                                                              'carga), Pop incorrecto dejando stack vacío '
                                                              'prematuramente.',
                                                 'checks': "PE-B muestra 'Implicit-null' como label local para su "
                                                           "loopback. P-router LFIB indica 'Pop'.",
                                                 'detail': 'Top label transporte eliminado. Stack restante: únicamente '
                                                           'VPN Label=8001 (S=1, TTL=63).',
                                                 'name': 'Capa 2.5 - MPLS (Label Stack)',
                                                 'packet_capture': {'notes': 'Verificar label stack, EXP bits, S-bit, '
                                                                             'TTL.',
                                                                    'tcpdump_filter': 'mpls',
                                                                    'wireshark_display_filter': 'mpls'}},
                                                {'anomalies': 'PE-B no reconoce label VPN 8001 (ILM missing): paquete '
                                                              'droppeado o forwarded erroneamente.',
                                                 'checks': 'Label 8001 es válido en PE-B (ILM/incoming label map '
                                                           'existe).',
                                                 'detail': 'IP Header oculto bajo el VPN label. SrcIP=10.1.1.10, '
                                                           'DstIP=10.2.2.20, TTL=61.',
                                                 'name': 'Capa 3 - Red (IPv4 del Cliente)',
                                                 'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                             'fragmentación.',
                                                                    'tcpdump_filter': 'ip',
                                                                    'wireshark_display_filter': 'ip'}},
                                                {'anomalies': 'Interfaz configurada solo para IP nativo (0x0800) y '
                                                              'rechaza MPLS.',
                                                 'checks': 'Interfaz entre P y PE-B soporta MPLS.',
                                                 'detail': 'DstMAC=PE-B_if, SrcMAC=P_if, EtherType=0x8847 (aún MPLS '
                                                           'porque queda VPN label).',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'PE-B anunció implicit-null para su loopback. El P-router elimina el top '
                                             'label antes de entregar a PE-B.',
                                     'step_title': 'Paso 4: P Penúltimo hace PHP del Transporte'},
                                    {'action': 'Pop VPN label + VRF lookup + forwarding hacia CE-B',
                                     'device': 'Router PE-B (Egress)',
                                     'layers': [{'anomalies': 'VRF no tiene ruta (RT import bloqueó la ruta), next-hop '
                                                              'CE-B inalcanzable, BGP route distinguisher mismatch.',
                                                 'checks': "VRF 'CLIENTE_A' en PE-B tiene ruta hacia 10.2.2.0/24 "
                                                           'directamente conectada o vía CE-B. RD/RT correctos (no '
                                                           'hubo filtrado de rutas).',
                                                 'detail': 'IP Header visible tras POP del VPN label: SrcIP=10.1.1.10, '
                                                           'DstIP=10.2.2.20, TTL=60.',
                                                 'name': 'Capa 3 - Red (IPv4 del Cliente)',
                                                 'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                             'fragmentación.',
                                                                    'tcpdump_filter': 'ip',
                                                                    'wireshark_display_filter': 'ip'}},
                                                {'anomalies': 'Interface down hacia CE-B, output drops, policing '
                                                              'descartando.',
                                                 'checks': 'Interfaz PE-B hacia CE-B Up/Up; ARP/ND resuelto; QoS '
                                                           'policy aplicada.',
                                                 'detail': 'DstMAC=CE-B_if, SrcMAC=PE-B_if, EtherType=0x0800. Posible '
                                                           'subinterface con VLAN de servicio.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'PE-B recibe el paquete con label 8001. Usa la ILM para identificar la '
                                             "VRF 'CLIENTE_A', hace POP del VPN label, y luego consulta la VRF FIB "
                                             'para reenviar el IP nativo.',
                                     'step_title': 'Paso 5: PE-B decapsula VPN y entrega a CE-B'},
                                    {'action': 'Forwarding final L2/L3 en sitio remoto',
                                     'device': 'Router CE-B / Switch',
                                     'layers': [{'anomalies': 'Host destino apagado, firewall en CE-B bloqueando '
                                                              'retorno, NAT inverso mal configurado.',
                                                 'checks': 'CE-B tiene ruta directa a 10.2.2.20.',
                                                 'detail': 'TTL=59. Checksum IP válido.',
                                                 'name': 'Capa 3 - Red (IPv4)',
                                                 'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                             'fragmentación.',
                                                                    'tcpdump_filter': 'ip',
                                                                    'wireshark_display_filter': 'ip'}},
                                                {'anomalies': 'Host no responde, MAC flapping, spanning-tree blocking.',
                                                 'checks': 'Host destino responde ARP; MAC aprendida.',
                                                 'detail': 'DstMAC=Host_destino, SrcMAC=CE-B_if, EtherType=0x0800.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'CE-B conecta directamente a la LAN del host destino. Entrega el frame '
                                             'Ethernet.',
                                     'step_title': 'Paso 6: CE-B entrega al Host destino'}]}]},
 'mpls': {'scenarios': [{'description': 'Recorrido completo de un paquete IP a través de una red MPLS con LDP y '
                                        'Penultimate Hop Popping (PHP). Se muestra la evolución de las cabeceras en '
                                        'cada salto hasta la entrega final.',
                         'id': 'mpls_ldp_ipv4_php',
                         'name': 'Paquete IPv4 sobre MPLS-LDP con PHP',
                         'steps': [{'action': 'Encapsulación inicial (sin MPLS)',
                                    'device': 'Host / CE local',
                                    'layers': [{'anomalies': 'Connection refused, timeout de aplicación, DNS NXDOMAIN.',
                                                'checks': 'La aplicación responde; no hay timeouts de socket.',
                                                'detail': 'Payload de aplicación (ej: HTTP GET, DNS query, ICMP '
                                                          'echo-request)',
                                                'name': 'Capa 7/6/5 - Aplicación/Presentación/Sesión'},
                                               {'anomalies': 'SYN retransmits (puerto cerrado), RST inesperado, '
                                                             'checksum incorrecto, MSS mismatch por MTU.',
                                                'checks': 'Puerto destino abierto en el servidor; firewall stateful '
                                                          'permite el flujo bidireccional.',
                                                'detail': 'TCP/UDP Header: SrcPort, DstPort, Seq, Ack, Window, '
                                                          'Checksum. Flags (SYN, ACK, PSH, etc.)',
                                                'name': 'Capa 4 - Transporte'},
                                               {'anomalies': 'TTL expired (loop), Destination Unreachable (ruta '
                                                             'faltante), Fragmentation Needed (DF-bit set y MTU bajo).',
                                                'checks': 'Ruta en CE hacia PE ingress correcta; next-hop alcanzable; '
                                                          'no hay filtros ACL bloqueando.',
                                                'detail': 'SrcIP=192.168.1.10, DstIP=10.20.30.40, TTL=64, '
                                                          'Protocol=TCP(6), TotalLen=1500, HeaderLen=20, Checksum IP',
                                                'name': 'Capa 3 - Red (IPv4)',
                                                'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                            'fragmentación.',
                                                                   'tcpdump_filter': 'ip',
                                                                   'wireshark_display_filter': 'ip'}},
                                               {'anomalies': 'Input errors, CRC errors, MAC flapping, duplex mismatch, '
                                                             'VLAN missing.',
                                                'checks': 'Interfaz Up/Up, duplex correcto, MAC address aprendida en '
                                                          'switch/CE, MTU ≥ 1500.',
                                                'detail': 'DstMAC=CE_local, SrcMAC=Host, EtherType=0x0800 (IPv4). '
                                                          'Posible VLAN tag (802.1Q) si trunk.',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}}],
                                    'note': 'El host desconoce MPLS. Genera un paquete IPv4 estándar dirigido al '
                                            'destino remoto.',
                                    'step_title': 'Paso 1: Host Origen genera el paquete'},
                                   {'action': 'Routing IP hacia PE de borde',
                                    'device': 'Router CE local',
                                    'layers': [{'anomalies': 'Ruta faltante en CE; next-hop inalcanzable; blackhole '
                                                             'por summarización incorrecta.',
                                                'checks': 'Tabla de routing del CE tiene ruta estática o BGP/OSPF '
                                                          'hacia 10.20.30.0/24 vía PE ingress.',
                                                'detail': 'Mismo paquete IP. TTL puede decrementar si el CE es un '
                                                          'router L3 (TTL=63).',
                                                'name': 'Capa 3 - Red (IPv4)',
                                                'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                            'fragmentación.',
                                                                   'tcpdump_filter': 'ip',
                                                                   'wireshark_display_filter': 'ip'}},
                                               {'anomalies': 'ARP incomplete (no hay L2 reachability), interface down, '
                                                             'output drops (congestión).',
                                                'checks': 'ARP resuelto (CE conoce MAC del PE); interfaz CE Up/Up; sin '
                                                          'input drops.',
                                                'detail': 'DstMAC=PE_ingress_if, SrcMAC=CE_if, EtherType=0x0800. '
                                                          'Posible 802.1Q tag de servicio.',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}}],
                                    'note': 'El CE realiza forwarding IP normal. No participa en MPLS. El paquete '
                                            'sigue siendo IPv4 nativo.',
                                    'step_title': 'Paso 2: CE local → PE Ingress'},
                                   {'action': 'Push label de transporte (LDP) y reenvío al core MPLS',
                                    'device': 'Router PE Ingress',
                                    'layers': [{'anomalies': 'Ruta no presente en PE; LDP no distribuyó label para la '
                                                             'FEC; LIB/LFIB incompleta.',
                                                'checks': 'PE tiene ruta para el destino (BGP, estático o IGP). La FEC '
                                                          'está mapeada a un label en la LIB.',
                                                'detail': 'IP header intacto. TTL puede ser copiado al label MPLS '
                                                          'según configuración (ttl-propagate).',
                                                'name': 'Capa 3 - Red (IPv4)',
                                                'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                            'fragmentación.',
                                                                   'tcpdump_filter': 'ip',
                                                                   'wireshark_display_filter': 'ip'}},
                                               {'anomalies': 'Label no asignado (LIB vacía), LDP session Down, label '
                                                             'mismatch, loop en LDP (TTL=1 en label).',
                                                'checks': 'LDP vecino UP; label binding presente para la FEC destino; '
                                                          'LIB muestra label local y remoto.',
                                                'detail': 'Label=1024, EXP=0, S=1 (Bottom of Stack), TTL=63. Solo un '
                                                          'label porque es forwarding MPLS puro (no VPN).',
                                                'name': 'Capa 2.5 - MPLS (Label Stack)',
                                                'packet_capture': {'notes': 'Verificar label stack, EXP bits, S-bit, '
                                                                            'TTL.',
                                                                   'tcpdump_filter': 'mpls',
                                                                   'wireshark_display_filter': 'mpls'}},
                                               {'anomalies': 'EtherType incorrecto, MTU insuficiente (drops '
                                                             'silenciosos), interface MPLS disabled.',
                                                'checks': "Interfaz P-P o PE-P con 'family mpls' / 'mpls ip'. MTU ≥ "
                                                          '1508 bytes (1500 IP + 4 MPLS + 14 Ethernet).',
                                                'detail': 'DstMAC=P_router_if, SrcMAC=PE_ingress_if, EtherType=0x8847 '
                                                          '(MPLS Unicast).',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}}],
                                    'note': 'El PE consulta la FIB/LFIB. Para el destino 10.20.30.0/24, el next-hop es '
                                            'un P-router alcanzable vía MPLS. Empuja el label de transporte asignado '
                                            'por LDP.',
                                    'step_title': 'Paso 3: PE Ingress empuja Label MPLS'},
                                   {'action': 'Swap label de entrada por label de salida según LFIB',
                                    'device': 'Router P (Transit)',
                                    'layers': [{'anomalies': 'LFIB sin entrada (label desconocido → drop), label '
                                                             'pointing to wrong interface, TTL=0 en label.',
                                                'checks': "LFIB muestra entrada para label 1024 con acción 'Swap' a "
                                                          '2048 y interfaz de salida correcta.',
                                                'detail': 'Label cambia de 1024 → 2048. EXP=0, S=1, TTL decrementado a '
                                                          '62. El contenido debajo del label es opaco para P.',
                                                'name': 'Capa 2.5 - MPLS (Label Stack)',
                                                'packet_capture': {'notes': 'Verificar label stack, EXP bits, S-bit, '
                                                                            'TTL.',
                                                                   'tcpdump_filter': 'mpls',
                                                                   'wireshark_display_filter': 'mpls'}},
                                               {'anomalies': 'LDP discovery falla en interfaz, MAC unicast flooding, '
                                                             'link down en path MPLS.',
                                                'checks': 'ARP/ND resuelto para next-hop; LDP descubrió vecino en '
                                                          'interfaz de salida; sin output drops.',
                                                'detail': 'DstMAC=Siguiente_P_o_PE, SrcMAC=P_if_out, EtherType=0x8847. '
                                                          'MAC reescrita en cada salto L2.',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}}],
                                    'note': 'El P-router nunca mira la cabecera IP. Solo consulta la LFIB usando el '
                                            'label superior como índice.',
                                    'step_title': 'Paso 4: P Router intercambia Label (Swap)'},
                                   {'action': 'Penultimate Hop Popping: elimina label MPLS antes de entregar al PE '
                                              'Egress',
                                    'device': 'Router P (Penúltimo Hop)',
                                    'layers': [{'anomalies': 'PHP deshabilitado y PE recibe label explícito (aumenta '
                                                             'carga de CPU), label Pop mal configurado (paquete IP sin '
                                                             'label llega a interfaz que espera MPLS).',
                                                'checks': "En PE Egress: 'show mpls ldp bindings' muestra label "
                                                          "local=Implicit-null para la FEC. En P: LFIB indica 'Pop'.",
                                                'detail': '¡AUSENTE! El label fue removido (POP). Ya no hay cabecera '
                                                          'MPLS entre P y PE Egress.',
                                                'name': 'Capa 2.5 - MPLS (Label Stack)',
                                                'packet_capture': {'notes': 'Verificar label stack, EXP bits, S-bit, '
                                                                            'TTL.',
                                                                   'tcpdump_filter': 'mpls',
                                                                   'wireshark_display_filter': 'mpls'}},
                                               {'anomalies': 'TTL=0 (demasiados hops), IP checksum incorrecto '
                                                             '(corrupto en tránsito), IP header modificado '
                                                             'inesperadamente.',
                                                'checks': 'El paquete IP no fue alterado. Checksum IP sigue válido '
                                                          '(MPLS no modifica IP salvo copy-TTL decrement).',
                                                'detail': 'IP Header visible nuevamente: SrcIP=192.168.1.10, '
                                                          'DstIP=10.20.30.40, TTL=61 (decrementado en cada hop '
                                                          'L3/MPLS).',
                                                'name': 'Capa 3 - Red (IPv4)',
                                                'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                            'fragmentación.',
                                                                   'tcpdump_filter': 'ip',
                                                                   'wireshark_display_filter': 'ip'}},
                                               {'anomalies': 'Interfaz configurada solo para MPLS y rechaza IP nativo '
                                                             '(EtherType 0x0800), MTU mismatch.',
                                                'checks': 'La interfaz entre P y PE Egreso soporta frames IPv4 nativos '
                                                          '(no solo MPLS). MTU ≥ 1500.',
                                                'detail': 'DstMAC=PE_egress_if, SrcMAC=P_penultimate_if, '
                                                          'EtherType=0x0800 (IPv4).',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}}],
                                    'note': 'El PE Egress anunció implícitamente label=3 (Implicit Null) para esta '
                                            'FEC. El penúltimo P hace POP, ahorrando una lookup LFIB al PE.',
                                    'step_title': 'Paso 5: P Penúltimo realiza PHP (Pop label)'},
                                   {'action': 'Routing IP hacia CE remoto (después de PHP)',
                                    'device': 'Router PE Egress',
                                    'layers': [{'anomalies': 'Ruta faltante en PE Egress (blackhole), next-hop '
                                                             'inalcanzable, forwarding table out of sync con RIB (CEF '
                                                             'issue).',
                                                'checks': 'PE tiene ruta para DstIP vía CE remoto (BGP, IGP o '
                                                          'estático). Next-hop resuelto vía ARP.',
                                                'detail': 'IP Header: TTL=60 (decrementado en PE Egress). PE hace '
                                                          'lookup en FIB global.',
                                                'name': 'Capa 3 - Red (IPv4)',
                                                'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                            'fragmentación.',
                                                                   'tcpdump_filter': 'ip',
                                                                   'wireshark_display_filter': 'ip'}},
                                               {'anomalies': 'Interface down, output drops, policing/shaping '
                                                             'descartando paquetes, VLAN mismatch.',
                                                'checks': 'Interfaz hacia CE remoto Up/Up; ARP resuelto; QoS/policy '
                                                          'aplicada correctamente.',
                                                'detail': 'DstMAC=CE_remote_if, SrcMAC=PE_egress_if, EtherType=0x0800. '
                                                          'Posible subinterface/VLAN.',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}}],
                                    'note': 'PE Egress recibe IP nativo. Realiza lookup en FIB global y reenvía hacia '
                                            'el CE del destino.',
                                    'step_title': 'Paso 6: PE Egress entrega a CE remoto'},
                                   {'action': 'Forwarding final L2/L3 hacia el host destino',
                                    'device': 'Router CE remoto / Switch',
                                    'layers': [{'anomalies': 'Ruta por default incorrecta, NAT mal aplicado, ACL en CE '
                                                             'bloqueando tráfico de retorno.',
                                                'checks': 'CE tiene ruta directamente conectada o static hacia la red '
                                                          'del host destino.',
                                                'detail': 'TTL=59 (si el CE es L3) o TTL=60 (si es L2 switch). '
                                                          'Checksum IP válido.',
                                                'name': 'Capa 3 - Red (IPv4)',
                                                'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                            'fragmentación.',
                                                                   'tcpdump_filter': 'ip',
                                                                   'wireshark_display_filter': 'ip'}},
                                               {'anomalies': 'MAC not learned (host apagado), broadcast storm, '
                                                             'Spanning Tree bloqueando puerto.',
                                                'checks': 'MAC del host aprendida en tabla CAM del switch/CE; sin '
                                                          'storm/broadcast excesivo.',
                                                'detail': 'DstMAC=Host_destino, SrcMAC=CE_if, EtherType=0x0800. '
                                                          'Posible 802.1Q tag.',
                                                'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                            'tag.',
                                                                   'tcpdump_filter': 'ether',
                                                                   'wireshark_display_filter': 'eth'}}],
                                    'note': 'Último salto antes del host. El CE entrega el frame Ethernet a la LAN del '
                                            'destino.',
                                    'step_title': 'Paso 7: CE remoto → Host destino'}]}]},
 'multicast': {'scenarios': [{'description': 'Recorrido del establecimiento de un flujo multicast IPTV usando PIM-SM. '
                                             'Se muestra el IGMP Join del receptor, el envío de PIM Join hacia el RP, '
                                             'el registro del source, el switchover al SPT y el forwarding nativo '
                                             'multicast.',
                              'id': 'multicast_pim_sm_iptv',
                              'name': 'PIM-SM: Registro/Join para stream IPTV multicast',
                              'steps': [{'action': 'El host solicita unirse al grupo multicast 224.1.1.1 enviando IGMP '
                                                   'Join',
                                         'device': 'Host Receptor / STB',
                                         'layers': [{'anomalies': 'Host envía IGMP Leave en lugar de Join (aplicación '
                                                                  'cerrada), IGMPv2/v3 mismatch, Report enviado a '
                                                                  'grupo equivocado.',
                                                     'checks': 'Host tiene aplicación/cliente IPTV activo; interfaz de '
                                                               'red del host en VLAN correcta; IGMP snooping '
                                                               'habilitado en switch si aplica.',
                                                     'detail': 'IGMPv2 Membership Report (Type=0x16) con grupo '
                                                               '224.1.1.1. O IGMPv3 Report (Type=0x22) con grupo '
                                                               '224.1.1.1 y modo INCLUDE/EXCLUDE de fuentes.',
                                                     'name': 'Capa 3 - IGMP',
                                                     'packet_capture': {'notes': 'Filtrar IGMP. Membership Report tipo '
                                                                                 '0x16 (v2) o 0x22 (v3).',
                                                                        'tcpdump_filter': 'igmp',
                                                                        'wireshark_display_filter': 'igmp'}},
                                                    {'anomalies': 'TTL=0 (host mal configurado), firewall bloqueando '
                                                                  'IGMP, ACL descartando tráfico multicast local.',
                                                     'checks': 'Host tiene IP válida en subred; TTL no bloqueado por '
                                                               'firewall local; no hay ACL en switch descartando IGMP.',
                                                     'detail': 'SrcIP=IP_receptor, DstIP=224.1.1.1 (IGMPv2) o '
                                                               '224.0.0.22 (IGMPv3), Protocol=2 (IGMP), TTL=1 '
                                                               '(obligatorio para tráfico local de multicast).',
                                                     'name': 'Capa 3 - Red (IPv4)',
                                                     'packet_capture': {'notes': 'Verificar TTL=1 en IGMP local.',
                                                                        'tcpdump_filter': 'igmp',
                                                                        'wireshark_display_filter': 'igmp'}},
                                                    {'anomalies': 'IGMP snooping no habilitado (flooding innecesario), '
                                                                  'VLAN incorrecta, MAC multicast no procesada.',
                                                     'checks': 'Switch/CE aprende MAC multicast o procesa IGMP '
                                                               'snooping correctamente; VLAN del host permite '
                                                               'multicast.',
                                                     'detail': 'DstMAC=01:00:5e:01:01:01 (mapeo de 224.1.1.1) para '
                                                               'IGMPv2. O 01:00:5e:00:00:16 (mapeo de 224.0.0.22) para '
                                                               'IGMPv3. SrcMAC=host, EtherType=0x0800.',
                                                     'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                     'packet_capture': {'notes': 'Verificar MAC multicast mapeada '
                                                                                 'correctamente.',
                                                                        'tcpdump_filter': 'ether host '
                                                                                          '01:00:5e:01:01:01 or ether '
                                                                                          'host 01:00:5e:00:00:16',
                                                                        'wireshark_display_filter': 'eth.addr == '
                                                                                                    '01:00:5e:01:01:01 '
                                                                                                    '|| eth.addr == '
                                                                                                    '01:00:5e:00:00:16'}}],
                                         'note': 'El receptor (ej. set-top-box) quiere recibir el stream IPTV. Envia '
                                                 'IGMP Membership Report al grupo deseado o al grupo de control '
                                                 'IGMPv3.',
                                         'step_title': 'Paso 1: Receptor envía IGMP Join (224.1.1.1)'},
                                        {'action': 'Envía mensaje PIM Join/Prune (*,G) en dirección al RP',
                                         'device': 'Router Last-Hop (LHR)',
                                         'layers': [{'anomalies': 'RPF check falla (ruta al RP no coincide con '
                                                                  'interfaz de recepción), RP desconocido (sin '
                                                                  'BSR/auto-RP), PIM no habilitado en interfaz (Join '
                                                                  'no enviado).',
                                                     'checks': 'LHR tiene ruta al RP (estático o auto-RP/BSR); '
                                                               'interfaz RPF determinada correctamente; PIM habilitado '
                                                               'en todas las interfaces del path hacia el RP.',
                                                     'detail': 'PIM Message Type=Join/Prune (3). Encodificación (*,G): '
                                                               'grupo multicast=224.1.1.1, dirección RP=IP_RP. Lista '
                                                               'de joins contiene (*,G). Se envía hacia el upstream '
                                                               'neighbor (RPF).',
                                                     'name': 'Capa 3 - PIM',
                                                     'packet_capture': {'notes': 'Filtrar PIM Join/Prune. Verificar '
                                                                                 'upstream neighbor.',
                                                                        'tcpdump_filter': 'ip proto 103',
                                                                        'wireshark_display_filter': 'pim'}},
                                                    {'anomalies': 'RP inalcanzable (Join descartado), ACL bloqueando '
                                                                  'PIM, TTL expirado en path hacia RP.',
                                                     'checks': 'RP alcanzable vía IGP; no hay ACL bloqueando protocolo '
                                                               '103; TTL suficiente.',
                                                     'detail': 'SrcIP=interfaz_salida_LHR, DstIP=IP_RP (unicast) o '
                                                               '224.0.0.13 (PIM multicast en segmento L2), '
                                                               'Protocol=103 (PIM), TTL=1 en enlace directo o mayor si '
                                                               'tunelado.',
                                                     'name': 'Capa 3 - Red (IPv4)',
                                                     'packet_capture': {'notes': 'N/A',
                                                                        'tcpdump_filter': 'ip proto 103',
                                                                        'wireshark_display_filter': 'ip.proto == 103'}},
                                                    {'anomalies': 'Next-hop MAC no resuelta, segmento L2 sin otros '
                                                                  'routers PIM (Join perdido).',
                                                     'checks': 'L2 reachability al next-hop hacia RP (si unicast); si '
                                                               'PIM multicast en LAN, todos los routers PIM reciben el '
                                                               'frame.',
                                                     'detail': 'DstMAC=MAC_next-hop_hacia_RP (unicast) o '
                                                               '01:00:5e:00:00:0d (224.0.0.13), SrcMAC=LHR_if, '
                                                               'EtherType=0x0800.',
                                                     'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                     'packet_capture': {'notes': 'N/A',
                                                                        'tcpdump_filter': 'ether proto ip and ip proto '
                                                                                          '103',
                                                                        'wireshark_display_filter': 'eth.type == '
                                                                                                    '0x0800 && '
                                                                                                    'ip.proto == '
                                                                                                    '103'}}],
                                         'note': 'El LHR recibe el IGMP Join del host. Como no tiene estado para el '
                                                 'grupo, envía un PIM Join (*,G) unicast o multicast hacia el RP a '
                                                 'través de la interfaz RPF.',
                                         'step_title': 'Paso 2: Last-hop router envía PIM (*,G) Join hacia el RP'},
                                        {'action': 'Encapsula el primer paquete multicast en un mensaje PIM Register '
                                                   'unicast hacia el RP',
                                         'device': 'Router First-Hop (FHR)',
                                         'layers': [{'anomalies': 'FHR no detecta source (DR no elegido, interfaz sin '
                                                                  'PIM), RP desconocido (Register no enviado), inner '
                                                                  'packet malformado.',
                                                     'checks': 'FHR detecta tráfico multicast en interfaz source; FHR '
                                                               'conoce dirección del RP; registro PIM generado '
                                                               'correctamente.',
                                                     'detail': 'PIM Message Type=Register (1). El payload del mensaje '
                                                               'PIM Register contiene el paquete IP multicast original '
                                                               'completo (inner packet): SrcIP=source_unicast, '
                                                               'DstIP=224.1.1.1, Protocol=UDP(17) o RTP.',
                                                     'name': 'Capa 3 - PIM',
                                                     'packet_capture': {'notes': 'Verificar PIM Register (Type=1). '
                                                                                 'Contiene paquete multicast '
                                                                                 'encapsulado.',
                                                                        'tcpdump_filter': 'ip proto 103',
                                                                        'wireshark_display_filter': 'pim'}},
                                                    {'anomalies': 'RP inalcanzable (Register descartado), NAT '
                                                                  'modificando direcciones PIM, TTL expirado.',
                                                     'checks': 'RP alcanzable desde FHR; no hay NAT entre FHR y RP que '
                                                               'rompa la encapsulación PIM; TTL suficiente.',
                                                     'detail': 'SrcIP=interfaz_FHR, DstIP=IP_RP, Protocol=103 (PIM), '
                                                               'TTL=255. El paquete multicast original viaja '
                                                               'encapsulado como payload de PIM.',
                                                     'name': 'Capa 3 - Red (IPv4 Outer)',
                                                     'packet_capture': {'notes': 'Filtrar tráfico PIM hacia el RP.',
                                                                        'tcpdump_filter': 'host IP_RP and ip proto 103',
                                                                        'wireshark_display_filter': 'ip.dst == IP_RP '
                                                                                                    '&& ip.proto == '
                                                                                                    '103'}},
                                                    {'anomalies': 'Link down, output drops en FHR.',
                                                     'checks': 'L2 reachability estable hacia RP.',
                                                     'detail': 'DstMAC=next-hop hacia RP, SrcMAC=FHR_if, '
                                                               'EtherType=0x0800.',
                                                     'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                     'packet_capture': {'notes': 'N/A',
                                                                        'tcpdump_filter': 'ether proto ip and ip proto '
                                                                                          '103',
                                                                        'wireshark_display_filter': 'eth.type == '
                                                                                                    '0x0800 && '
                                                                                                    'ip.proto == '
                                                                                                    '103'}}],
                                         'note': 'Cuando el source empieza a transmitir (UDP/RTP), el FHR detecta '
                                                 'tráfico en la interfaz conectada al source. Como no hay SPT aún, '
                                                 'encapsula el paquete multicast completo dentro de un PIM Register y '
                                                 'lo envía unicast al RP.',
                                         'step_title': 'Paso 3: Source inicia stream, first-hop router encapsula en '
                                                       'PIM Register'},
                                        {'action': 'Decapsula PIM Register y envía PIM Join (S,G) hacia el source para '
                                                   'construir el SPT',
                                         'device': 'Router RP (Rendezvous Point)',
                                         'layers': [{'anomalies': 'RPF check falla hacia source (ruta inexistente), RP '
                                                                  'sin estado (*,G) (tráfico descartado aunque haya '
                                                                  'receptores), interfaz hacia source sin PIM.',
                                                     'checks': 'RP tiene ruta IGP hacia la fuente; interfaz RPF hacia '
                                                               'source correcta; estado (*,G) presente para reenviar a '
                                                               'receptores.',
                                                     'detail': 'PIM Join/Prune (Type=3) con encodificación (S,G): '
                                                               'fuente=IP_source, grupo=224.1.1.1. El RP se une al '
                                                               'árbol source-specific para recibir tráfico nativamente '
                                                               'sin depender del Register.',
                                                     'name': 'Capa 3 - PIM',
                                                     'packet_capture': {'notes': 'Verificar PIM Join (S,G) desde RP '
                                                                                 'hacia source.',
                                                                        'tcpdump_filter': 'ip proto 103',
                                                                        'wireshark_display_filter': 'pim'}},
                                                    {'anomalies': 'IGP reconvergiendo (ruta a source inestable), ACL '
                                                                  'bloqueando PIM entre RP y source.',
                                                     'checks': 'Conectividad IP bidireccional entre RP y source; IGP '
                                                               'convergido.',
                                                     'detail': 'SrcIP=interfaz_RP, DstIP=next-hop RPF hacia source '
                                                               '(unicast) o 224.0.0.13, Protocol=103 (PIM), TTL según '
                                                               'saltos necesarios.',
                                                     'name': 'Capa 3 - Red (IPv4)',
                                                     'packet_capture': {'notes': 'N/A',
                                                                        'tcpdump_filter': 'ip proto 103',
                                                                        'wireshark_display_filter': 'ip.proto == 103'}},
                                                    {'anomalies': 'Link down en segmento crítico.',
                                                     'checks': 'L2 estable en path RP-source.',
                                                     'detail': 'DstMAC=next-hop RPF, SrcMAC=RP_if, EtherType=0x0800.',
                                                     'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                     'packet_capture': {'notes': 'N/A',
                                                                        'tcpdump_filter': 'ether proto ip and ip proto '
                                                                                          '103',
                                                                        'wireshark_display_filter': 'eth.type == '
                                                                                                    '0x0800 && '
                                                                                                    'ip.proto == '
                                                                                                    '103'}}],
                                         'note': 'El RP recibe el Register, extrae el paquete multicast original y lo '
                                                 'reenvía por la interfaz hacia los receptores (si hay estado (*,G)). '
                                                 'Simultáneamente, envía un PIM Join (S,G) hacia el source para '
                                                 'construir el Shortest Path Tree.',
                                         'step_title': 'Paso 4: RP decapsula y envía SPT Join hacia el source'},
                                        {'action': 'El LHR cambia del RPT al SPT y el RP envía Register-Stop al FHR',
                                         'device': 'Router Last-Hop (LHR) / RP',
                                         'layers': [{'anomalies': 'RPF failure (paquete descartado en router '
                                                                  'intermedio), TTL=0 (source muy lejos o loop), (S,G) '
                                                                  'state no creado (tráfico droppeado).',
                                                     'checks': 'Cada router del SPT tiene entrada (S,G) con interfaz '
                                                               'de entrada RPF correcta; no hay RPF failures; TTL>0 en '
                                                               'todos los hops.',
                                                     'detail': 'Paquete multicast nativo: SrcIP=IP_source_unicast, '
                                                               'DstIP=224.1.1.1, TTL decrementado en cada hop (inicia '
                                                               'alto, ej: 64), Protocol=UDP(17) o RTP. RPF check '
                                                               'exitoso en cada router del SPT.',
                                                     'name': 'Capa 3 - IP Multicast',
                                                     'packet_capture': {'notes': 'Verificar flujo multicast nativo '
                                                                                 '(S,G).',
                                                                        'tcpdump_filter': 'host 224.1.1.1',
                                                                        'wireshark_display_filter': 'ip.dst == '
                                                                                                    '224.1.1.1'}},
                                                    {'anomalies': 'Register-Stop perdido (FHR sigue enviando Registers '
                                                                  'innecesariamente), LHR no inicia SPT switchover '
                                                                  '(sigue usando RPT con subóptima ruta).',
                                                     'checks': 'RP conoce FHR (dirección source del Register); LHR '
                                                               'tiene ruta al source para SPT; Register-Stop llega '
                                                               'correctamente.',
                                                     'detail': 'PIM Register-Stop (Type=2) unicast de RP a FHR. '
                                                               'Confirma que el SPT está establecido y que el FHR debe '
                                                               'dejar de enviar Registers. El LHR envía PIM Join (S,G) '
                                                               'directo al source para recibir tráfico por el SPT.',
                                                     'name': 'Capa 3 - PIM',
                                                     'packet_capture': {'notes': 'Verificar Register-Stop (Type=2) y '
                                                                                 'Join (S,G).',
                                                                        'tcpdump_filter': 'ip proto 103',
                                                                        'wireshark_display_filter': 'pim'}},
                                                    {'anomalies': 'Switch sin IGMP snooping hace flooding; switch con '
                                                                  'snooping pero sin querier bloquea multicast; MAC '
                                                                  'multicast no aprendida.',
                                                     'checks': 'L2 forwarding multicast correcto en segmentos '
                                                               'compartidos; switches con IGMP snooping/PIM snooping '
                                                               'no bloquean.',
                                                     'detail': 'Para tráfico nativo multicast: '
                                                               'DstMAC=01:00:5e:01:01:01 (mapeo de 224.1.1.1), '
                                                               'SrcMAC=router_if, EtherType=0x0800. Para PIM '
                                                               'Register-Stop: unicast L2.',
                                                     'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                     'packet_capture': {'notes': 'Verificar MAC multicast mapeada de '
                                                                                 '224.1.1.1.',
                                                                        'tcpdump_filter': 'ether host '
                                                                                          '01:00:5e:01:01:01',
                                                                        'wireshark_display_filter': 'eth.addr == '
                                                                                                    '01:00:5e:01:01:01'}}],
                                         'note': 'Una vez que el tráfico nativo (S,G) llega al LHR a través del SPT (o '
                                                 'al RP y luego al LHR), el LHR puede realizar SPT switchover. El RP '
                                                 'envía PIM Register-Stop al FHR para dejar de recibir registros '
                                                 'encapsulados.',
                                         'step_title': 'Paso 5: SPT switchover'},
                                        {'action': 'Reenvío nativo multicast hop-by-hop desde el source hasta los '
                                                   'receptores a través del SPT',
                                         'device': 'Routers del SPT / LHR',
                                         'layers': [{'anomalies': 'RPF failure (paquete descartado), TTL expirado, '
                                                                  '(S,G) state timeout (no hay receptores activos, '
                                                                  'árbol podado), routing asimétrico que rompe RPF.',
                                                     'checks': 'Estado (S,G) presente en todos los routers del path; '
                                                               'interfaz RPF correcta; TTL>0; sin RPF failures.',
                                                     'detail': 'SrcIP=IP_source, DstIP=224.1.1.1, '
                                                               'Protocol=UDP(17)/RTP, TTL decrementado en cada hop. '
                                                               'Los routers verifican RPF: la interfaz de entrada debe '
                                                               'coincidir con la ruta IGP más corta hacia la fuente.',
                                                     'name': 'Capa 3 - IP Multicast',
                                                     'packet_capture': {'notes': 'Verificar TTL y RPF en cada hop.',
                                                                        'tcpdump_filter': 'host 224.1.1.1',
                                                                        'wireshark_display_filter': 'ip.dst == '
                                                                                                    '224.1.1.1'}},
                                                    {'anomalies': 'Switch descarta trama multicast (VLAN pruning, IGMP '
                                                                  'snooping sin membership), STP bloqueando puerto '
                                                                  'hacia receptor, MAC flapping.',
                                                     'checks': 'Switches L2 reenvían la trama multicast al puerto del '
                                                               'receptor (o flooding si no hay snooping); no hay STP '
                                                               'bloqueando puertos de salida.',
                                                     'detail': 'DstMAC=01:00:5e:01:01:01, SrcMAC=router_if_salida, '
                                                               'EtherType=0x0800. En segmentos L2 se usa la MAC '
                                                               'multicast mapeada.',
                                                     'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                     'packet_capture': {'notes': 'Verificar forwarding L2 multicast.',
                                                                        'tcpdump_filter': 'ether host '
                                                                                          '01:00:5e:01:01:01',
                                                                        'wireshark_display_filter': 'eth.addr == '
                                                                                                    '01:00:5e:01:01:01'}},
                                                    {'anomalies': 'mLDP session Down, label P2MP no asignado, MTU '
                                                                  'insuficiente en core MPLS, replicación P2MP '
                                                                  'fallida.',
                                                     'checks': 'mLDP/RSVP P2MP session UP; labels P2MP distribuidos '
                                                               'correctamente; MTU ajustada para MPLS overhead.',
                                                     'detail': 'Si el core usa mLDP o RSVP P2MP para transporte '
                                                               'multicast: Top Label=transporte P2MP (ej: RSVP-TE P2MP '
                                                               'label o mLDP label), Bottom Label=multicast service '
                                                               'label (S=1). EtherType=0x8847. Los P-routers replican '
                                                               'el paquete basándose en el label P2MP sin mirar el IP '
                                                               'multicast.',
                                                     'name': 'Capa 2 - MPLS (opcional)',
                                                     'packet_capture': {'notes': 'Si usa MPLS multicast (mLDP/RSVP '
                                                                                 'P2MP), filtrar por labels MPLS.',
                                                                        'tcpdump_filter': 'mpls',
                                                                        'wireshark_display_filter': 'mpls'}}],
                                         'note': 'El árbol SPT está completamente establecido. Cada router replica el '
                                                 'paquete multicast hacia todas las interfaces de salida listadas en '
                                                 'el estado (S,G), excepto la interfaz RPF de entrada.',
                                         'step_title': 'Paso 6: Forwarding nativo multicast a lo largo del SPT'}]}]},
 'qos_traffic_eng': {'scenarios': [{'description': 'Recorrido completo del establecimiento de un túnel RSVP-TE en una '
                                                   'red MPLS. Se muestra el intercambio de mensajes PATH y RESV, la '
                                                   'asignación de labels, el forwarding de datos a través del LSP de '
                                                   'ingeniería de tráfico y la conmutación FRR ante fallo de enlace.',
                                    'id': 'qos_te_rsvp_te_tunnel',
                                    'name': 'Establecimiento de túnel RSVP-TE con PATH/RESV',
                                    'steps': [{'action': 'Envía mensaje RSVP PATH para iniciar el establecimiento del '
                                                         'LSP-TE',
                                               'device': 'Router Headend (A)',
                                               'layers': [{'anomalies': 'RSVP PATH no generado (configuración de túnel '
                                                                        'incompleta), objeto LABEL_REQUEST ausente (no '
                                                                        'se solicita label), ERO con salto '
                                                                        'inalcanzable (ruta explícita rota).',
                                                           'checks': 'Headend tiene configuración de túnel TE válida; '
                                                                     'RSVP está habilitado en interfaz de salida; ERO '
                                                                     'construido correctamente (sin saltos '
                                                                     'inalcanzables).',
                                                           'detail': 'RSVP Message Type=PATH (1), Protocolo IP=46. '
                                                                     'Objetos presentes: LABEL_REQUEST (solicita label '
                                                                     'explícito), SESSION (dirección destino del '
                                                                     'túnel, túnel ID, extended ID), SENDER_TEMPLATE, '
                                                                     'SENDER_TSPEC, ERO (Explicit Route Object).',
                                                           'name': 'Capa 4 - RSVP sobre IP',
                                                           'packet_capture': {'notes': 'Filtrar RSVP en toda la red. '
                                                                                       'PATH usa Router Alert.',
                                                                              'tcpdump_filter': 'ip proto 46',
                                                                              'wireshark_display_filter': 'rsvp'}},
                                                          {'anomalies': 'Ruta IP hacia tailend inalcanzable (PATH '
                                                                        'nunca llega), TTL expirado, Router Alert no '
                                                                        'soportado/descartado por ACL en P-router.',
                                                           'checks': 'Conectividad IP al tailend verificada; IGP tiene '
                                                                     'ruta hacia loopback destino; Router Alert '
                                                                     'procesado en cada nodo intermedio sin descarte.',
                                                           'detail': 'SrcIP=Loopback_Headend, DstIP=Loopback_Tailend, '
                                                                     'Protocol=46 (RSVP), IP Option=Router Alert '
                                                                     '(0x94) en todos los hops para forzar '
                                                                     'procesamiento por el control plane. TTL=255 '
                                                                     'inicialmente.',
                                                           'name': 'Capa 3 - Red (IPv4)',
                                                           'packet_capture': {'notes': 'Capturar PATH en cada hop. '
                                                                                       'Verificar Router Alert.',
                                                                              'tcpdump_filter': 'ip proto 46',
                                                                              'wireshark_display_filter': 'ip.proto == '
                                                                                                          '46'}},
                                                          {'anomalies': 'Interface down, ARP incomplete, MTU '
                                                                        'insuficiente descartando PATH.',
                                                           'checks': 'Interfaz Up/Up; ARP/ND resuelto para next-hop; '
                                                                     'MTU ≥ 1500.',
                                                           'detail': 'DstMAC=next-hop P-router, SrcMAC=Headend_if, '
                                                                     'EtherType=0x0800 (IPv4).',
                                                           'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                           'packet_capture': {'notes': 'N/A',
                                                                              'tcpdump_filter': 'ether proto ip and ip '
                                                                                                'proto 46',
                                                                              'wireshark_display_filter': 'eth.type == '
                                                                                                          '0x0800 && '
                                                                                                          'ip.proto == '
                                                                                                          '46'}}],
                                               'note': 'El headend conoce la dirección del tailend y construye el '
                                                       'mensaje PATH incluyendo ERO, Label Request y Session Object. '
                                                       'El mensaje se envía unicast hop-by-hop siguiendo el ERO.',
                                               'step_title': 'Paso 1: Headend envía mensaje RSVP PATH'},
                                              {'action': 'Procesa y reenvía RSVP PATH hacia el siguiente hop del ERO',
                                               'device': 'Router P (Transit)',
                                               'layers': [{'anomalies': 'RSVP no habilitado en interfaz (PATH '
                                                                        'ignorado), ERO apunta a salto incorrecto '
                                                                        '(PATH rechazado con PathErr), loop en ERO '
                                                                        '(TTL expira).',
                                                           'checks': 'RSVP habilitado en interfaz de entrada y salida; '
                                                                     'el P-router se reconoce como next-hop válido en '
                                                                     'el ERO; RRO actualizado correctamente.',
                                                           'detail': 'RSVP PATH reenviado. El P-router no modifica '
                                                                     'LABEL_REQUEST ni SESSION. Puede añadir su '
                                                                     'dirección de salida al RRO si el objeto RRO está '
                                                                     'presente en el mensaje original.',
                                                           'name': 'Capa 4 - RSVP sobre IP',
                                                           'packet_capture': {'notes': 'Capturar en interfaz de '
                                                                                       'entrada y salida del P-router.',
                                                                              'tcpdump_filter': 'ip proto 46',
                                                                              'wireshark_display_filter': 'rsvp'}},
                                                          {'anomalies': 'TTL=0 antes de llegar al tailend, ACL '
                                                                        'descartando RSVP en P-router, IP checksum '
                                                                        'corrupto.',
                                                           'checks': 'TTL suficiente para alcanzar tailend; IP '
                                                                     'forwarding RSVP funciona; no hay ACL bloqueando '
                                                                     'protocolo 46.',
                                                           'detail': 'Protocol=46, Router Alert presente. TTL '
                                                                     'decrementado en cada hop. ERO intacto. RRO puede '
                                                                     'crecer con direcciones de interfaz de salida de '
                                                                     'cada P-router.',
                                                           'name': 'Capa 3 - Red (IPv4)',
                                                           'packet_capture': {'notes': 'N/A',
                                                                              'tcpdump_filter': 'ip proto 46',
                                                                              'wireshark_display_filter': 'ip.proto == '
                                                                                                          '46'}},
                                                          {'anomalies': 'Link down en path, MAC unicast flooding, '
                                                                        'duplex mismatch.',
                                                           'checks': 'L2 reachability al siguiente hop del ERO; sin '
                                                                     'output drops.',
                                                           'detail': 'DstMAC=next-hop (otro P-router o Tailend), '
                                                                     'SrcMAC=P-router_if, EtherType=0x0800.',
                                                           'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                           'packet_capture': {'notes': 'N/A',
                                                                              'tcpdump_filter': 'ether proto ip and ip '
                                                                                                'proto 46',
                                                                              'wireshark_display_filter': 'eth.type == '
                                                                                                          '0x0800 && '
                                                                                                          'ip.proto == '
                                                                                                          '46'}}],
                                               'note': 'El P-router recibe el PATH gracias a Router Alert. Valida que '
                                                       'es el siguiente hop en el ERO, actualiza el RRO (Record Route '
                                                       'Object) si está presente, y reenvía el mensaje sin modificar '
                                                       'los objetos principales.',
                                               'step_title': 'Paso 2: P-router reenvía mensaje RSVP PATH'},
                                              {'action': 'Recibe RSVP PATH, asigna label local y genera RSVP RESV de '
                                                         'respuesta',
                                               'device': 'Router Tailend (Z)',
                                               'layers': [{'anomalies': 'Tailend rechaza reserva (PathErr/ResvErr por '
                                                                        'ancho de banda insuficiente), label no '
                                                                        'asignado (configuración MPLS ausente), '
                                                                        'SESSION mismatch.',
                                                           'checks': 'Tailend tiene recursos disponibles para la '
                                                                     'reserva (ancho de banda); label local asignado '
                                                                     'correctamente; RSVP habilitado en interfaz.',
                                                           'detail': 'RSVP Message Type=RESV (2). Objeto LABEL '
                                                                     'presente con el label asignado localmente (ej: '
                                                                     'Label=3001). Objetos FILTER_SPEC y FLOWSPEC '
                                                                     'definen la reserva de recursos. SESSION coincide '
                                                                     'con la recibida en PATH.',
                                                           'name': 'Capa 4 - RSVP sobre IP',
                                                           'packet_capture': {'notes': 'Capturar RESV en tailend. '
                                                                                       'Verificar objeto LABEL.',
                                                                              'tcpdump_filter': 'ip proto 46',
                                                                              'wireshark_display_filter': 'rsvp'}},
                                                          {'anomalies': 'Ruta hacia headend inalcanzable (RESV no '
                                                                        'llega), routing asimétrico que rompe RSVP '
                                                                        'state.',
                                                           'checks': 'Tailend tiene ruta IGP hacia el headend; '
                                                                     'interfaz de salida correcta para el RESV.',
                                                           'detail': 'SrcIP=Loopback_Tailend, DstIP=Loopback_Headend, '
                                                                     'Protocol=46. TTL=255. Router Alert no es '
                                                                     'obligatorio en RESV. El RPF se basa en la ruta '
                                                                     'IGP hacia el headend.',
                                                           'name': 'Capa 3 - Red (IPv4)',
                                                           'packet_capture': {'notes': 'N/A',
                                                                              'tcpdump_filter': 'ip proto 46',
                                                                              'wireshark_display_filter': 'ip.proto == '
                                                                                                          '46'}},
                                                          {'anomalies': 'Interface down hacia upstream.',
                                                           'checks': 'L2 reachability al upstream neighbor.',
                                                           'detail': 'DstMAC=next-hop hacia headend, '
                                                                     'SrcMAC=Tailend_if, EtherType=0x0800.',
                                                           'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                           'packet_capture': {'notes': 'N/A',
                                                                              'tcpdump_filter': 'ether proto ip and ip '
                                                                                                'proto 46',
                                                                              'wireshark_display_filter': 'eth.type == '
                                                                                                          '0x0800 && '
                                                                                                          'ip.proto == '
                                                                                                          '46'}}],
                                               'note': 'El tailend es el destino final del ERO. Procesa LABEL_REQUEST '
                                                       'asignando un label local para la FEC del túnel. Construye el '
                                                       'mensaje RESV con el label asignado y lo envía por el camino '
                                                       'inverso (upstream) hacia el headend.',
                                               'step_title': 'Paso 3: Tailend recibe PATH y envía RESV'},
                                              {'action': 'Reenvía RSVP RESV hop-by-hop hacia el headend, propagando el '
                                                         'label binding upstream',
                                               'device': 'Router P (Transit) / Headend',
                                               'layers': [{'anomalies': 'ResvErr por recursos insuficientes en nodo '
                                                                        'intermedio, label mismatch entre hops, RSVP '
                                                                        'state timeout en P-router.',
                                                           'checks': 'Estado RSVP reservable en cada nodo; ancho de '
                                                                     'banda disponible en interfaces; label binding '
                                                                     'coherente en toda la ruta.',
                                                           'detail': 'RSVP RESV reenviado. El objeto LABEL con el '
                                                                     'label del tailend (o del downstream neighbor) se '
                                                                     'propaga upstream. Cada nodo puede realizar '
                                                                     "'label recording' si está configurado.",
                                                           'name': 'Capa 4 - RSVP sobre IP',
                                                           'packet_capture': {'notes': 'Capturar RESV en cada hop '
                                                                                       'upstream.',
                                                                              'tcpdump_filter': 'ip proto 46',
                                                                              'wireshark_display_filter': 'rsvp'}},
                                                          {'anomalies': 'Path asimétrico que causa que RESV tome ruta '
                                                                        'diferente y RSVP state no se establezca '
                                                                        'correctamente.',
                                                           'checks': 'Conectividad bidireccional IP estable entre '
                                                                     'headend y tailend.',
                                                           'detail': 'SrcIP/DstIP invertidos respecto a PATH. TTL '
                                                                     'decrementado. Protocol=46.',
                                                           'name': 'Capa 3 - Red (IPv4)',
                                                           'packet_capture': {'notes': 'N/A',
                                                                              'tcpdump_filter': 'ip proto 46',
                                                                              'wireshark_display_filter': 'ip.proto == '
                                                                                                          '46'}},
                                                          {'anomalies': 'Link unidireccional (falla L2 en sentido '
                                                                        'upstream).',
                                                           'checks': 'L2 estable en dirección upstream.',
                                                           'detail': 'DstMAC=upstream neighbor, SrcMAC=P-router_if, '
                                                                     'EtherType=0x0800.',
                                                           'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                           'packet_capture': {'notes': 'N/A',
                                                                              'tcpdump_filter': 'ether proto ip and ip '
                                                                                                'proto 46',
                                                                              'wireshark_display_filter': 'eth.type == '
                                                                                                          '0x0800 && '
                                                                                                          'ip.proto == '
                                                                                                          '46'}}],
                                               'note': 'Cada nodo intermedio recibe RESV, actualiza su estado RSVP '
                                                       'local, reserva recursos según FLOWSPEC y reenvía el RESV al '
                                                       'upstream neighbor. El label binding viaja desde el tailend '
                                                       'hasta el headend.',
                                               'step_title': 'Paso 4: RESV viaja de regreso con label binding'},
                                              {'action': 'Túnel RSVP-TE establecido. Los paquetes de datos se '
                                                         'encapsulan con label TE y se reenvían por el LSP.',
                                               'device': 'Router Headend (A) / Core MPLS',
                                               'layers': [{'anomalies': 'Ruta no apunta al túnel TE (tráfico no '
                                                                        'ingresa al LSP), FIB/LFIB out of sync.',
                                                           'checks': 'El headend tiene ruta que apunta al túnel TE '
                                                                     'como next-hop; la FIB/LFIB refleja el label TE.',
                                                           'detail': 'Paquete de datos del cliente o del router: '
                                                                     'SrcIP/DstIP según tráfico real, TTL=64, '
                                                                     'Protocolo=TCP/UDP/ICMP/etc.',
                                                           'name': 'Capa 3 - Red (IPv4 Payload)',
                                                           'packet_capture': {'notes': 'Verificar doble stack si '
                                                                                       'aplica (TE + VPN label).',
                                                                              'tcpdump_filter': 'mpls and ip',
                                                                              'wireshark_display_filter': 'mpls && '
                                                                                                          'ip'}},
                                                          {'anomalies': 'TE label no instalado en LFIB, label no '
                                                                        'asignado por RSVP (sesión Down), EXP bits no '
                                                                        'copiados (QoS no preservada).',
                                                           'checks': 'RSVP instaló label en LFIB del headend; '
                                                                     'P-routers tienen swap entries para el TE label; '
                                                                     'penúltimo hop hace PHP del TE label o lo swapea '
                                                                     'según configuración.',
                                                           'detail': 'Top Label (TE/RSVP): Label=asignado por RSVP-TE '
                                                                     '(ej: 4001), EXP=bits QoS copiados de IP '
                                                                     'Prec/DSCP, S=0, TTL=63.\n'
                                                                     'Si el túnel transporta L3VPN: Bottom Label '
                                                                     '(VPN/BGP): Label=8001, EXP=0, S=1, TTL=63.\n'
                                                                     'Si es tráfico nativo IPv4 sobre TE: solo TE '
                                                                     'label con S=1.',
                                                           'name': 'Capa 2.5 - MPLS (Label Stack)',
                                                           'packet_capture': {'notes': 'Filtrar por TE label '
                                                                                       'específico. Verificar EXP '
                                                                                       'bits.',
                                                                              'tcpdump_filter': 'mpls 4001',
                                                                              'wireshark_display_filter': 'mpls.label '
                                                                                                          '== 4001'}},
                                                          {'anomalies': 'EtherType incorrecto, MTU insuficiente '
                                                                        'causando drops silenciosos.',
                                                           'checks': 'Interfaz core MPLS Up; MTU ≥ 1508 (1500 IP + 4 '
                                                                     'TE label + 14 Ethernet) o ≥ 1512 si doble stack.',
                                                           'detail': 'DstMAC=next-hop P-router, SrcMAC=Headend_if, '
                                                                     'EtherType=0x8847 (MPLS Unicast).',
                                                           'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                           'packet_capture': {'notes': 'Verificar EtherType MPLS.',
                                                                              'tcpdump_filter': 'ether proto 0x8847',
                                                                              'wireshark_display_filter': 'eth.type == '
                                                                                                          '0x8847'}}],
                                               'note': 'El headend instala la ruta del túnel en la FIB/LFIB. Cuando '
                                                       'llega tráfico destinado al tailend (o VPN que usa el túnel '
                                                       'como transporte), empuja el label TE asignado por RSVP y lo '
                                                       'reenvía.',
                                               'step_title': 'Paso 5: Túnel UP y forwarding de datos por TE LSP'},
                                              {'action': 'Conmutación rápida al túnel de bypass (FRR) cuando el enlace '
                                                         'primario falla',
                                               'device': 'Router Headend / PLR (Point of Local Repair)',
                                               'layers': [{'anomalies': 'Bypass tunnel no configurado (sin protección '
                                                                        'FRR), bypass label no asignado (LFIB vacía), '
                                                                        'merge node no reconoce TE label tras pop del '
                                                                        'bypass (paquete droppeado).',
                                                           'checks': 'Bypass tunnel preestablecido y operativo; PLR '
                                                                     'tiene label de bypass en LFIB; el nodo de merge '
                                                                     '(MP) recibe paquete con TE label válido.',
                                                           'detail': 'Facility Backup: Top Label=Bypass Label (ej: '
                                                                     '9001), EXP=0, S=0, TTL=64.\n'
                                                                     'Next label=TE Label original (ej: 4001), S=0 o '
                                                                     'S=1 según stack original.\n'
                                                                     'El PLR no quita el TE label original; lo '
                                                                     'encapsula bajo el bypass label.\n'
                                                                     'Detour: Top Label=Detour Label asignado '
                                                                     'localmente para el bypass node.',
                                                           'name': 'Capa 2.5 - MPLS (Label Stack FRR)',
                                                           'packet_capture': {'notes': 'Verificar stack de labels '
                                                                                       'durante FRR: bypass label + TE '
                                                                                       'label.',
                                                                              'tcpdump_filter': 'mpls 9001 or mpls '
                                                                                                '4001',
                                                                              'wireshark_display_filter': 'mpls.label '
                                                                                                          '== 9001 || '
                                                                                                          'mpls.label '
                                                                                                          '== 4001'}},
                                                          {'anomalies': 'Bypass loop (paquete nunca llega al merge '
                                                                        'point), MTU insuficiente en bypass path '
                                                                        '(drops por overhead extra de label).',
                                                           'checks': 'El paquete sigue llegando al tailend o al '
                                                                     'next-hop protegido a través del bypass.',
                                                           'detail': 'IP payload del cliente intacto bajo la pila '
                                                                     'MPLS. No hay modificación de IPs ni TTL del '
                                                                     'payload durante el bypass.',
                                                           'name': 'Capa 3 - Red (IPv4 Payload)',
                                                           'packet_capture': {'notes': 'Verificar que IP payload no '
                                                                                       'cambia durante FRR.',
                                                                              'tcpdump_filter': 'mpls and ip',
                                                                              'wireshark_display_filter': 'mpls && '
                                                                                                          'ip'}},
                                                          {'anomalies': 'Link bypass también caído (doble falla), MAC '
                                                                        'no resuelta en bypass path.',
                                                           'checks': 'Interfaz de bypass Up/Up; L2 reachability al '
                                                                     'next-hop del bypass path.',
                                                           'detail': 'DstMAC=next-hop del bypass tunnel, '
                                                                     'SrcMAC=PLR_if, EtherType=0x8847. MAC reescrita '
                                                                     'para el enlace de respaldo.',
                                                           'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                           'packet_capture': {'notes': 'Verificar en interfaz de '
                                                                                       'bypass.',
                                                                              'tcpdump_filter': 'ether proto 0x8847',
                                                                              'wireshark_display_filter': 'eth.type == '
                                                                                                          '0x8847'}}],
                                               'note': 'El PLR tiene preconfigurado un bypass tunnel (o facility '
                                                       'backup). Al detectar fallo del next-hop o enlace protegido, '
                                                       'realiza el push del label de bypass en menos de 50ms y desvía '
                                                       'el tráfico.',
                                               'step_title': 'Paso 6: FRR detour ante fallo de enlace'}]}]},
 'vxlan': {'scenarios': [{'description': 'Simulación de comunicación entre dos VMs en el mismo VNI a través de VXLAN '
                                         'sobre underlay IP. Se muestra la encapsulación MAC-in-UDP y el rol de EVPN '
                                         'Type 2 como control plane.',
                          'id': 'vxlan_evpn_unicast_same_vni',
                          'name': 'VXLAN-EVPN: VM a VM mismo VNI (Unicast)',
                          'steps': [{'action': 'Genera trama Ethernet interna (inner frame)',
                                     'device': 'VM1 / Host Hypervisor A',
                                     'layers': [{'anomalies': 'ARP timeout (VM2 no responde), subnet mismatch.',
                                                 'checks': 'VM1 y VM2 en misma subnet; ARP resuelto.',
                                                 'detail': 'SrcIP=10.0.1.10, DstIP=10.0.1.20, TTL=64. Dentro de inner '
                                                           'frame.',
                                                 'name': 'Capa 3 - Red (IPv4)',
                                                 'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                             'fragmentación.',
                                                                    'tcpdump_filter': 'ip',
                                                                    'wireshark_display_filter': 'ip'}},
                                                {'anomalies': 'MAC VM2 desconocida → BUM flooding (broadcast) '
                                                              'innecesario.',
                                                 'checks': 'MAC VM2 conocida en hypervisor A (vía EVPN Type 2 o local '
                                                           'learning).',
                                                 'detail': 'DstMAC=MAC_VM2, SrcMAC=MAC_VM1, EtherType=0x0800. Esta es '
                                                           "la trama 'original' que será encapsulada.",
                                                 'name': 'Capa 2 - Enlace de Datos (Inner Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'VM1 y VM2 están en la misma red L2 lógica (mismo VNI). VM1 ya conoce la '
                                             'MAC de VM2 (aprendida localmente o vía EVPN).',
                                     'step_title': 'Paso 1: VM Origen genera trama'},
                                    {'action': 'Encapsulación VXLAN: Inner Ethernet → VXLAN → UDP → IP → Ethernet',
                                     'device': 'VTEP-A (Leaf/TOR)',
                                     'layers': [{'anomalies': 'VNI-VLAN binding incorrecto, bridge domain no asociado.',
                                                 'checks': 'VNI 5010 mapeado a VLAN/Bridge-Domain correcto en VTEP-A.',
                                                 'detail': 'Trama original intacta: DstMAC=MAC_VM2, SrcMAC=MAC_VM1, '
                                                           'EtherType=0x0800, payload IP.',
                                                 'name': 'Capa 2 - Enlace de Datos (Inner Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}},
                                                {'anomalies': 'VNI incorrecto (tráfico entregado a wrong segment), '
                                                              'flags malformados.',
                                                 'checks': 'VNI correcto para el segmento L2. Flags indican VNI '
                                                           'válido.',
                                                 'detail': 'Flags=0x08 (I=1, VNI presente), Reserved=0x000000, '
                                                           'VNI=0x00501A (VNI 5010), Reserved=0x0000.',
                                                 'name': 'Capa 2.5 - VXLAN Header',
                                                 'packet_capture': {'notes': 'Verificar VNI, flags, inner Ethernet.',
                                                                    'tcpdump_filter': 'udp port 4789',
                                                                    'wireshark_display_filter': 'vxlan'}},
                                                {'anomalies': 'Firewall bloqueando UDP 4789, SrcPort fijo causando '
                                                              'polarización ECMP.',
                                                 'checks': 'UDP 4789 permitido en firewalls del underlay. SrcPort '
                                                           'variado para balanceo ECMP.',
                                                 'detail': 'SrcPort=49152 (hash de flujo para ECMP), DstPort=4789 '
                                                           '(VXLAN well-known). Length incluye VXLAN + inner frame. '
                                                           'Checksum UDP (puede ser 0x0000 en some impl).',
                                                 'name': 'Capa 4 - Transporte (Outer UDP)'},
                                                {'anomalies': 'Loopback VTEP no alcanzable (IGP/BGP missing), next-hop '
                                                              'inalcanzable, asymmetric routing entre VTEPs.',
                                                 'checks': 'Underlay IP alcanzable entre VTEPs (loopbacks anunciados '
                                                           'por IGP/BGP). Rutas /32 o /128 para loopbacks de VTEP en '
                                                           'underlay.',
                                                 'detail': 'SrcIP=Loopback_VTEP-A=192.168.50.1, '
                                                           'DstIP=Loopback_VTEP-B=192.168.50.2, Protocol=17 (UDP), '
                                                           'TTL=64, Len=total packet.',
                                                 'name': 'Capa 3 - Red (Outer IPv4)',
                                                 'packet_capture': {'notes': 'Outer IP. Verificar TTL, checksum, '
                                                                             'fragmentación.',
                                                                    'tcpdump_filter': 'ip',
                                                                    'wireshark_display_filter': 'ip'}},
                                                {'anomalies': 'MTU insuficiente en underlay (drops silenciosos), '
                                                              'interface down.',
                                                 'checks': 'Interfaz de salida de VTEP-A Up/Up. MTU ≥ 1550 (1500 inner '
                                                           '+ 50 VXLAN overhead + 14 outer Ethernet).',
                                                 'detail': 'DstMAC=Router_Underlay_if, SrcMAC=VTEP-A_if, '
                                                           'EtherType=0x0800 (IPv4).',
                                                 'name': 'Capa 2 - Enlace de Datos (Outer Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'VTEP-A aprendió vía EVPN-BGP que MAC VM2 está detrás de VTEP-B '
                                             '(next-hop=192.168.50.2). Empaqueta la trama en VXLAN.',
                                     'step_title': 'Paso 2: VTEP-A encapsula en VXLAN'},
                                    {'action': 'Routing IP basado en Outer IP dst=192.168.50.2',
                                     'device': 'Routers Underlay (Spine/Core)',
                                     'layers': [{'anomalies': 'Ruta a 192.168.50.2 faltante, IGP reconvergiendo, TTL=0 '
                                                              'en underlay.',
                                                 'checks': 'IGP/OSPF/IS-IS/BGP underlay tiene rutas para todos los '
                                                           'loopbacks de VTEP. ECMP balanceando flujos.',
                                                 'detail': 'IP Header outer: Src=192.168.50.1, Dst=192.168.50.2, TTL '
                                                           'decrementado en cada hop L3 (63, 62, ...).',
                                                 'name': 'Capa 3 - Red (Outer IPv4)',
                                                 'packet_capture': {'notes': 'Outer IP. Verificar TTL, checksum, '
                                                                             'fragmentación.',
                                                                    'tcpdump_filter': 'ip',
                                                                    'wireshark_display_filter': 'ip'}},
                                                {'anomalies': 'Link down, MAC unicast flooding, spanning-tree en '
                                                              'underlay (si hay L2).',
                                                 'checks': 'Conectividad L2 estable en todos los enlaces del path.',
                                                 'detail': 'Ethernet reescrita en cada salto del underlay.',
                                                 'name': 'Capa 2 - Enlace de Datos (Outer Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'Los routers del underlay ven únicamente la cabecera Outer IP. No tienen '
                                             'conocimiento del VNI ni de las VMs.',
                                     'step_title': 'Paso 3: Underlay IP reenvía hacia VTEP-B'},
                                    {'action': 'Decapsulación: Outer headers removidos, inner frame entregado a VM2',
                                     'device': 'VTEP-B (Leaf/TOR)',
                                     'layers': [{'anomalies': 'VNI desconocido en VTEP-B (paquete descartado), VNI '
                                                              'mapeado a VLAN equivocada.',
                                                 'checks': 'VNI 5010 existe en VTEP-B y está mapeado al bridge '
                                                           'domain/VLAN correcto.',
                                                 'detail': 'VNI=0x00501A (5010). Flags validados. VTEP-B confirma que '
                                                           'este VNI está localmente configurado.',
                                                 'name': 'Capa 2.5 - VXLAN Header',
                                                 'packet_capture': {'notes': 'Verificar VNI, flags, inner Ethernet.',
                                                                    'tcpdump_filter': 'udp port 4789',
                                                                    'wireshark_display_filter': 'vxlan'}},
                                                {'anomalies': 'MAC VM2 no aprendida localmente (VM2 apagada o movida).',
                                                 'checks': 'MAC VM2 aprendida localmente en el puerto hacia VM2 (o vía '
                                                           'hipervisor).',
                                                 'detail': 'Trama original: DstMAC=MAC_VM2, SrcMAC=MAC_VM1, '
                                                           'EtherType=0x0800, payload IP.',
                                                 'name': 'Capa 2 - Enlace de Datos (Inner Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'VTEP-B recibe UDP 4789. Valida VNI 5010. Extrae inner Ethernet y la '
                                             'entrega al bridge domain/VLAN correspondiente.',
                                     'step_title': 'Paso 4: VTEP-B decapsula VXLAN'},
                                    {'action': 'Recepción de trama Ethernet nativa',
                                     'device': 'VM2 / Host Hypervisor B',
                                     'layers': [{'anomalies': 'VM2 no responde (firewall de VM, aplicación down), MTU '
                                                              'issues en VM.',
                                                 'checks': 'VM2 responde (ping reply, TCP SYN-ACK, etc.).',
                                                 'detail': 'SrcIP=10.0.1.10, DstIP=10.0.1.20, TTL=64 (no decrementado '
                                                           'por VXLAN).',
                                                 'name': 'Capa 3 - Red (IPv4)',
                                                 'packet_capture': {'notes': 'Verificar TTL, checksum, flags, '
                                                                             'fragmentación.',
                                                                    'tcpdump_filter': 'ip',
                                                                    'wireshark_display_filter': 'ip'}},
                                                {'anomalies': 'VM2 no recibe trama (vSwitch misconfiguration).',
                                                 'checks': 'Conectividad L2 confirmada.',
                                                 'detail': 'Trama Ethernet entregada a interfaz virtual de VM2.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar MAC addresses, EtherType, VLAN '
                                                                             'tag.',
                                                                    'tcpdump_filter': 'ether',
                                                                    'wireshark_display_filter': 'eth'}}],
                                     'note': 'VM2 recibe exactamente la misma trama que VM1 generó, como si estuvieran '
                                             'en el mismo switch L2.',
                                     'step_title': 'Paso 5: VM2 recibe el paquete'}]}]},
 'evc': {'scenarios': [{'id': 'evc_nni_e_line_dot1q',
                        'name': 'EVC E-Line: Trama Ethernet dot1q sobre NNI (ASR-903)',
                        'description': 'Simulación de una trama Ethernet VLAN-tagged (dot1q) que atraviesa un puerto '
                                       'NNI del Cisco ASR-903 con EVC. Se muestra la clasificación por Service '
                                       'Instance (EFP), el rewrite de VLAN, y la entrega a un Bridge-Domain o Xconnect '
                                       '(Pseudowire).',
                        'steps': [{'step_title': 'Paso 1: Cliente genera trama Ethernet tagged',
                                   'device': 'CE / Switch del cliente',
                                   'action': 'Genera trama Ethernet con VLAN tag 100 dirigida a otro sitio',
                                   'note': 'El cliente envía tráfico tagged con VLAN 100 hacia el ASR-903 a través del '
                                           'puerto NNI.',
                                   'layers': [{'name': 'Capa 3 - Red (IPv4)',
                                               'detail': 'SrcIP=10.10.10.1, DstIP=10.20.20.2, TTL=64, Protocol=TCP(6). '
                                                         'Dentro de trama Ethernet.',
                                               'checks': 'Host origen tiene ruta hacia destino. ARP resuelto '
                                                         'localmente.',
                                               'anomalies': 'ARP timeout, subnet mismatch.',
                                               'packet_capture': {'wireshark_display_filter': 'vlan.id == 100 && ip',
                                                                  'tcpdump_filter': 'vlan 100 and ip',
                                                                  'notes': 'Verificar trama tagged con VLAN 100 e IP '
                                                                           'payload.'}},
                                              {'name': 'Capa 2 - Enlace de Datos (Ethernet dot1q)',
                                               'detail': 'DstMAC=MAC_ASR903_NNI, SrcMAC=MAC_CE, EtherType=0x8100 '
                                                         '(802.1Q), VLAN ID=100, PCF=0. Payload=IPv4.',
                                               'checks': 'Interfaz CE Up/Up. Duplex correcto. MTU ≥ 1504 (1500 IP + 4 '
                                                         'dot1q).',
                                               'anomalies': 'CRC errors, duplex mismatch, VLAN 100 no configurada en '
                                                            'CE.',
                                               'packet_capture': {'wireshark_display_filter': 'eth.addr == '
                                                                                              'MAC_ASR903_NNI && '
                                                                                              'vlan.id == 100',
                                                                  'tcpdump_filter': 'ether host MAC_ASR903_NNI and '
                                                                                    'vlan 100',
                                                                  'notes': 'Confirmar presencia de tag dot1q.'}}]},
                                  {'step_title': 'Paso 2: ASR-903 NNI recibe y clasifica por EFP',
                                   'device': 'Cisco ASR-903 (RSP3_400)',
                                   'action': 'Service Instance (EFP) 100 clasifica trama por dot1q 100',
                                   'note': "La EFP 100 en Gig0/0/0 está configurada con 'encapsulation dot1q 100'. La "
                                           'trama coincide y se procesa.',
                                   'layers': [{'name': 'Capa 2 - Enlace de Datos (Ethernet dot1q)',
                                               'detail': 'Trama recibida: DstMAC=MAC_ASR903, SrcMAC=MAC_CE, '
                                                         'EtherType=0x8100, VLAN=100. ASR-903 verifica FCS y VLAN.',
                                               'checks': 'Interfaz NNI Up/Up. Contadores input incrementan. Sin input '
                                                         'errors.',
                                               'anomalies': 'Input errors, CRC, runts, giants. VLAN mismatch si trama '
                                                            'llega untagged o con VLAN diferente.',
                                               'packet_capture': {'wireshark_display_filter': 'vlan.id == 100',
                                                                  'tcpdump_filter': 'vlan 100',
                                                                  'notes': 'Mirror en puerto NNI del ASR-903.'}},
                                              {'name': 'Capa 2 - Service Instance (EFP) / EVC',
                                               'detail': 'EFP 100: encapsulation dot1q 100. Match realizado. '
                                                         'Contadores de match incrementan. Action: rewrite ingress tag '
                                                         'pop 1 symmetric.',
                                               'checks': "'show ethernet service instance id 100 interface Gig0/0/0' "
                                                         'muestra Up. Contadores de match > 0.',
                                               'anomalies': 'EFP Down, encapsulation mismatch (ej: dot1ad vs dot1q), '
                                                            'match counters en 0 (trama no clasificada).',
                                               'packet_capture': {'wireshark_display_filter': 'vlan.id == 100',
                                                                  'tcpdump_filter': 'vlan 100',
                                                                  'notes': 'Si EFP hace pop, la trama interna ya no '
                                                                           'tendrá tag en BD.'}}]},
                                  {'step_title': 'Paso 3: ASR-903 aplica rewrite y entrega a Bridge-Domain',
                                   'device': 'Cisco ASR-903 (RSP3_400)',
                                   'action': 'Pop VLAN tag + forwarding dentro de Bridge-Domain 100',
                                   'note': "La EFP 100 tiene 'rewrite ingress tag pop 1 symmetric'. El tag dot1q 100 "
                                           'se remueve y la trama se entrega al Bridge-Domain 100.',
                                   'layers': [{'name': 'Capa 2 - Enlace de Datos (Ethernet sin tag)',
                                               'detail': 'Trama interna en BD: DstMAC=MAC_destino, SrcMAC=MAC_CE, '
                                                         'EtherType=0x0800 (IPv4). Sin VLAN tag (pop aplicado).',
                                               'checks': 'Bridge-Domain 100 activo. MAC learning habilitado. EFP 100 '
                                                         'asociada a BD 100.',
                                               'anomalies': 'BD no existe, EFP no asociada a BD, MAC learning '
                                                            'deshabilitado, split-horizon bloqueando reenvío.',
                                               'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800 && '
                                                                                              'not vlan',
                                                                  'tcpdump_filter': 'ether proto ip and not vlan',
                                                                  'notes': 'Verificar trama untagged dentro del '
                                                                           'Bridge-Domain.'}},
                                              {'name': 'Capa 2 - Bridge-Domain (MAC Learning)',
                                               'detail': 'ASR-903 aprende MAC fuente en BD 100. Consulta MAC destino '
                                                         'en tabla CAM del BD. Si conocida, reenvía por EFP de salida.',
                                               'checks': "'show mac address-table bridge-domain 100' muestra MACs "
                                                         'aprendidas. Sin unknown unicast flooding excesivo.',
                                               'anomalies': 'MAC destino unknown (flooding), MAC flapping entre EFPs, '
                                                            'tabla CAM llena.',
                                               'packet_capture': {'wireshark_display_filter': 'eth.addr == MAC_destino',
                                                                  'tcpdump_filter': 'ether host MAC_destino',
                                                                  'notes': 'Verificar forwarding unicast específico en '
                                                                           'BD.'}}]},
                                  {'step_title': 'Paso 4: ASR-903 entrega por EFP de salida',
                                   'device': 'Cisco ASR-903 (RSP3_400)',
                                   'action': 'Push VLAN tag + entrega por interfaz NNI de salida',
                                   'note': "La EFP de salida tiene 'rewrite ingress tag pop 1 symmetric', por lo que "
                                           'en sentido inverso hace push del tag 100. La trama sale tagged hacia el '
                                           'siguiente salto.',
                                   'layers': [{'name': 'Capa 2 - Enlace de Datos (Ethernet dot1q)',
                                               'detail': 'Trama de salida: DstMAC=MAC_next_hop, SrcMAC=MAC_ASR903_out, '
                                                         'EtherType=0x8100, VLAN=100, Payload IPv4.',
                                               'checks': 'EFP de salida Up. MAC next-hop resuelta. MTU de salida ≥ '
                                                         '1504.',
                                               'anomalies': 'EFP de salida Down, MAC next-hop no resuelta, output '
                                                            'drops por congestión o policing.',
                                               'packet_capture': {'wireshark_display_filter': 'vlan.id == 100',
                                                                  'tcpdump_filter': 'vlan 100',
                                                                  'notes': 'Mirror en puerto de salida del '
                                                                           'ASR-903.'}}]},
                                  {'step_title': 'Paso 5: CFM / OAM verifica conectividad',
                                   'device': 'ASR-903 ↔ PE remoto',
                                   'action': 'CCM (Continuity Check Messages) entre MEPs en EFP 100',
                                   'note': 'Los MEPs configurados en EFP 100 intercambian CCMs cada 1s. Si hay break '
                                           'en el path, CFM detecta LOC (Loss of Continuity) o RDI.',
                                   'layers': [{'name': 'Capa 2 - CFM / OAM (802.1ag)',
                                               'detail': 'CCM Frame: EtherType=0x8902 (CFM), MD Level=4, MA '
                                                         'Name=CLIENTE_A, MEP ID=1. Periódico cada 1s.',
                                               'checks': "'show ethernet cfm domain PROVIDER service CLIENTE_A' "
                                                         'muestra CCMs RX/TX incrementando. Sin defectos.',
                                               'anomalies': 'LOC detectado (MEP remoto no responde), RDI (Remote '
                                                            'Defect Indication), AIS (Alarm Indication Signal).',
                                               'packet_capture': {'wireshark_display_filter': 'cfm',
                                                                  'tcpdump_filter': 'ether proto 0x8902',
                                                                  'notes': 'Filtrar CFM (EtherType 0x8902). Verificar '
                                                                           'MD Level y MA Name.'}}]},
                                  {'step_title': 'Paso 6: Destino final recibe trama',
                                   'device': 'CE remoto / Host destino',
                                   'action': 'Recepción de trama Ethernet tagged VLAN 100',
                                   'note': 'El CE remoto recibe la trama con VLAN 100 intacta. El host destino procesa '
                                           'el paquete IP.',
                                   'layers': [{'name': 'Capa 3 - Red (IPv4)',
                                               'detail': 'SrcIP=10.10.10.1, DstIP=10.20.20.2, TTL=63. Paquete IP '
                                                         'intacto.',
                                               'checks': 'Host destino responde. Conectividad end-to-end confirmada.',
                                               'anomalies': 'Host no responde, firewall bloqueando, MTU path issue.',
                                               'packet_capture': {'wireshark_display_filter': 'ip.dst == 10.20.20.2',
                                                                  'tcpdump_filter': 'host 10.20.20.2',
                                                                  'notes': 'Verificar recepción en host destino.'}},
                                              {'name': 'Capa 2 - Enlace de Datos (Ethernet dot1q)',
                                               'detail': 'DstMAC=MAC_CE_remoto, SrcMAC=MAC_ASR903_out, '
                                                         'EtherType=0x8100, VLAN=100.',
                                               'checks': 'CE remoto recibe trama tagged correctamente. VLAN 100 '
                                                         'mapeada a interfaz/switch local.',
                                               'anomalies': 'VLAN mismatch en CE remoto, STP bloqueando puerto.',
                                               'packet_capture': {'wireshark_display_filter': 'vlan.id == 100 && '
                                                                                              'ip.dst == 10.20.20.2',
                                                                  'tcpdump_filter': 'vlan 100 and host 10.20.20.2',
                                                                  'notes': 'Confirmar entrega final con VLAN 100 '
                                                                           'preservada.'}}]}]}]},
 'sdwan': {'scenarios': [{'id': 'sdwan_control_tunnel_sla',
                          'name': 'SD-WAN: Control plane DTLS/TLS, túnel de datos y steering por SLA',
                          'description': 'Recorrido del establecimiento del control plane DTLS/TLS entre edge y '
                                         'orquestador, intercambio de rutas TLOC/OMP o BGP, creación del túnel de '
                                         'datos IPSec/GRE, BFD sobre overlay y steering de aplicaciones basado en '
                                         'métricas SLA.',
                          'steps': [{'step_title': 'Paso 1: Edge envía conexión de control al orquestador',
                                     'device': 'Edge SD-WAN (Viptela / FortiGate)',
                                     'action': 'El edge inicia la conexión de control segura hacia '
                                               'vManage/FortiManager o controlador SD-WAN',
                                     'note': 'Cisco Viptela utiliza DTLS (UDP 12346) o TLS (TCP 23456). Fortinet '
                                             'utiliza TCP 443/514 o UDP 4500.',
                                     'layers': [{'name': 'Capa 4 - Transporte (UDP/TCP)',
                                                 'detail': 'Cisco Viptela: UDP SrcPort=efímero, DstPort=12346 (DTLS) o '
                                                           'TCP DstPort=23456 (TLS). Fortinet: TCP DstPort=443/514 o '
                                                           'UDP 4500. Flags SYN (TLS) o DTLS Client Hello.',
                                                 'checks': 'Puertos de control permitidos en firewalls intermedios. '
                                                           'NAT no altera puertos requeridos.',
                                                 'anomalies': 'Firewall bloqueando puertos de control, NAT sin '
                                                              'pinhole, SYN retransmits (TLS) o timeout en DTLS '
                                                              'handshake.',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 12346 || '
                                                                                                'tcp.port == 23456 || '
                                                                                                'tcp.port == 443',
                                                                    'tcpdump_filter': 'udp port 12346 or tcp port '
                                                                                      '23456 or tcp port 443',
                                                                    'notes': 'Filtrar por puertos de control SD-WAN '
                                                                             'según vendor.'}},
                                                {'name': 'Capa 3 - Red (IPv4/IPv6)',
                                                 'detail': 'SrcIP=IP_WAN_edge, DstIP=IP_orquestador. Protocol=17 (UDP) '
                                                           'o 6 (TCP). TTL≥64. Checksum IP válido.',
                                                 'checks': 'Edge tiene IP válida en interfaz WAN. Ruta por defecto o '
                                                           'estática hacia el orquestador.',
                                                 'anomalies': 'Ruta faltante, NAT outbound fallando, IP privada sin '
                                                              'NAT hacia Internet, TTL expirado.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.dst == '
                                                                                                'IP_orquestador && '
                                                                                                '(udp.port == 12346 || '
                                                                                                'tcp.port == 23456 || '
                                                                                                'tcp.port == 443)',
                                                                    'tcpdump_filter': 'host IP_orquestador and (udp '
                                                                                      'port 12346 or tcp port 23456 or '
                                                                                      'tcp port 443)',
                                                                    'notes': 'Verificar direccionamiento IP '
                                                                             'origen/destino.'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'DstMAC=MAC_default_gateway, SrcMAC=MAC_edge_WAN, '
                                                           'EtherType=0x0800.',
                                                 'checks': 'Interfaz WAN Up/Up. ARP/ND resuelto para default gateway. '
                                                           'Sin input errors.',
                                                 'anomalies': 'Interface down, ARP incomplete, MTU bajo, duplex '
                                                              'mismatch.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'Capturar en interfaz WAN del edge.'}}]},
                                    {'step_title': 'Paso 2: Handshake DTLS/TLS para seguridad del control plane',
                                     'device': 'Edge ↔ Orquestador/Controlador',
                                     'action': 'Negociación criptográfica del canal de control (cipher suite, '
                                               'certificados, claves de sesión)',
                                     'note': 'DTLS usa UDP sin conexión pero con retransmisión propia. TLS requiere '
                                             'TCP three-way handshake previo.',
                                     'layers': [{'name': 'Capa 5/6/7 - Handshake DTLS/TLS',
                                                 'detail': 'DTLS/TLS Client Hello (Version=1.2/1.3, Random, Session '
                                                           'ID, Cipher Suites, Extensions: SNI, Supported Groups, '
                                                           'Signature Algorithms). Server Hello + Certificate + Server '
                                                           'Key Exchange + Server Hello Done. Client Key Exchange + '
                                                           'Change Cipher Spec + Finished.',
                                                 'checks': 'Certificado del servidor válido y no expirado. Cipher '
                                                           'suite soportada por ambos lados. Tiempo sincronizado (NTP) '
                                                           'para validar certificados.',
                                                 'anomalies': 'Certificado expirado o no confiado, cipher suite '
                                                              'mismatch (handshake failure), retransmisión de Client '
                                                              'Hello por pérdida de UDP, reloj desincronizado.',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 12346 || '
                                                                                                'tcp.port == 23456 || '
                                                                                                'tcp.port == 443',
                                                                    'tcpdump_filter': 'udp port 12346 or tcp port '
                                                                                      '23456 or tcp port 443',
                                                                    'notes': 'En Wireshark expandir DTLS/TLS '
                                                                             'handshake. Verificar certificados y '
                                                                             'alertas.'}},
                                                {'name': 'Capa 4 - Transporte (UDP/TCP)',
                                                 'detail': 'DTLS: UDP mantene los mismos puertos (12346). TLS: TCP '
                                                           'sequence numbers avanzan, ACKs confirman recepción de '
                                                           'segmentos handshake.',
                                                 'checks': 'Sin retransmisiones excesivas de TCP/UDP. Ventana TCP '
                                                           'suficiente. Sin fragmentación de paquetes DTLS/TLS.',
                                                 'anomalies': 'TCP retransmits (congestión o pérdida), UDP packets '
                                                              'DTLS descartados sin retransmisión (timeout handshake), '
                                                              'MTU insuficiente causando fragmentación IP.',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 12346 || '
                                                                                                'tcp.port == 23456 || '
                                                                                                'tcp.port == 443',
                                                                    'tcpdump_filter': 'udp port 12346 or tcp port '
                                                                                      '23456 or tcp port 443',
                                                                    'notes': 'Verificar flags TCP y retransmisiones.'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'SrcIP/DstIP fijos del edge y orquestador. Protocol=17 '
                                                           '(UDP) o 6 (TCP). TTL decrementado en cada hop. TOS/DSCP '
                                                           'marcado para control plane (ej: CS6).',
                                                 'checks': 'Conectividad IP estable bidireccional. TOS/DSCP no '
                                                           'descartado por QoS intermedio.',
                                                 'anomalies': 'Asymmetric routing que rompe TCP, ACL intermedia '
                                                              'bloqueando ACKs, QoS descartando paquetes de control.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.src == IP_edge && '
                                                                                                'ip.dst == '
                                                                                                'IP_orquestador',
                                                                    'tcpdump_filter': 'host IP_edge and host '
                                                                                      'IP_orquestador',
                                                                    'notes': 'Capturar ambos sentidos.'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'DstMAC=next-hop, SrcMAC=edge/orquestador_if, '
                                                           'EtherType=0x0800. Posible 802.1Q tag en WAN.',
                                                 'checks': 'L2 estable en todo el path. Sin micro-cortes.',
                                                 'anomalies': 'MAC flapping, interface errors, STP reconvergiendo.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 3: Intercambio de rutas TLOC (OMP/BGP)',
                                     'device': 'Edge ↔ Controlador SD-WAN',
                                     'action': 'El edge anuncia sus TLOCs/prefijos locales y recibe rutas de overlay '
                                               'del controlador (vSmart/FortiManager)',
                                     'note': 'Cisco Viptela usa OMP (Overlay Management Protocol) sobre DTLS. Fortinet '
                                             'usa iBGP/ADVPN sobre TLS/IPSec.',
                                     'layers': [{'name': 'Capa 7 - OMP/BGP Update',
                                                 'detail': 'OMP: Opcode=Update, Flags=0, Path IDs, TLOC routes (color, '
                                                           'encap, preference). BGP UPDATE: Path Attributes (ORIGIN, '
                                                           'AS_PATH, NEXT_HOP, Extended Communities para SD-WAN).',
                                                 'checks': 'Rutas locales correctamente anunciadas. Políticas de '
                                                           'control permiten intercambio. Sin loop en AS_PATH.',
                                                 'anomalies': 'OMP session flapping, BGP holdtime expirado, rutas '
                                                              'filtradas por policy, TLOC color mismatch.',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 12346 || '
                                                                                                'tcp.port == 179 || '
                                                                                                'tcp.port == 443',
                                                                    'tcpdump_filter': 'udp port 12346 or tcp port 179 '
                                                                                      'or tcp port 443',
                                                                    'notes': 'OMP viaja encapsulado en DTLS. BGP via '
                                                                             'TLS/IPSec o TCP directo.'}},
                                                {'name': 'Capa 5/6 - DTLS/TLS Record',
                                                 'detail': 'Content Type=Application Data (23). Version=1.2/1.3. '
                                                           'Encrypted payload contiene mensajes OMP o BGP.',
                                                 'checks': 'Sesión DTLS/TLS estable (no renegotiation excesiva). MAC '
                                                           'de TLS válido.',
                                                 'anomalies': 'DTLS renegotiation loop, TLS bad record MAC (corrupto '
                                                              'en tránsito), session timeout.',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 12346 || '
                                                                                                'tcp.port == 23456 || '
                                                                                                'tcp.port == 443',
                                                                    'tcpdump_filter': 'udp port 12346 or tcp port '
                                                                                      '23456 or tcp port 443',
                                                                    'notes': 'Datos encriptados; usar decrypt si se '
                                                                             'dispone de claves.'}},
                                                {'name': 'Capa 4 - Transporte (UDP/TCP)',
                                                 'detail': 'Puertos consistentes con sesión de control. TCP ACKs '
                                                           'avanzan sin retransmisión.',
                                                 'checks': 'Puerto de sesión no cambia. Sin RST inesperado.',
                                                 'anomalies': 'TCP RST (firewall matando sesión), NAT timeout en '
                                                              'sesión UDP DTLS, cambio de puerto por NAT.',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 12346 || '
                                                                                                'tcp.port == 23456 || '
                                                                                                'tcp.port == 443',
                                                                    'tcpdump_filter': 'udp port 12346 or tcp port '
                                                                                      '23456 or tcp port 443',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'SrcIP/DstIP del edge y controlador. Protocol=17 o 6. TTL y '
                                                           'checksum válidos.',
                                                 'checks': 'Rutas estables. Sin blackholes.',
                                                 'anomalies': 'IGP reconvergiendo (ruta flapping), ACL bloqueando '
                                                              'tráfico de control.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip',
                                                                    'tcpdump_filter': 'ip',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'Ethernet estándar con EtherType=0x0800.',
                                                 'checks': 'Sin errores L2.',
                                                 'anomalies': 'Errores de capa física.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 4: Establecimiento de túnel de datos IPSec/GRE hacia '
                                                   'hub/spoke',
                                     'device': 'Edge SD-WAN (Spoke) ↔ Hub / Otro Spoke',
                                     'action': 'Negociación IKEv2/IKEv1 y establecimiento de SA IPSec para túnel de '
                                               'datos; opcionalmente GRE dentro de IPSec',
                                     'note': 'El túnel de datos se establece usando las credenciales/PKI del control '
                                             'plane. Puede ser IPSec directo o GRE over IPSec.',
                                     'layers': [{'name': 'Capa 3.5/4 - IKEv2 / IPSec',
                                                 'detail': 'IKEv2: INIT (SA, KE, Ni) y AUTH (IDr, CERT, AUTH, CP, SA, '
                                                           'TSi, TSr). IPSec ESP: SPI=0x00AABBCC, Seq#, Encrypted '
                                                           'payload. GRE: Flags=0x0000, Protocol Type=0x0800, Key, '
                                                           'Sequence.',
                                                 'checks': 'IKEv2 policy y proposal coinciden en ambos lados. '
                                                           'Certificados o PSK válidos. SA IPSec instalada en ambos '
                                                           'sentidos (SPIs visibles).',
                                                 'anomalies': 'IKE policy mismatch, certificado rechazado, PSK '
                                                              'incorrecta, NAT-T no negociado cuando hay NAT '
                                                              'intermedio, SA unidireccional (solo un lado instala '
                                                              'SPI).',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 500 || '
                                                                                                'udp.port == 4500 || '
                                                                                                'esp || gre',
                                                                    'tcpdump_filter': 'udp port 500 or udp port 4500 '
                                                                                      'or esp or ip proto 47',
                                                                    'notes': 'IKEv2 usa UDP 500 (sin NAT) o 4500 '
                                                                             '(NAT-T). ESP es IP proto 50. GRE es IP '
                                                                             'proto 47.'}},
                                                {'name': 'Capa 3 - Red (Outer IPv4)',
                                                 'detail': 'SrcIP=IP_WAN_edge, DstIP=IP_WAN_peer. Protocol=50 (ESP) o '
                                                           '47 (GRE). TTL=64.',
                                                 'checks': 'Peer alcanzable directamente por IP pública o a través de '
                                                           'NAT con NAT-T.',
                                                 'anomalies': 'Peer inalcanzable, ACL bloqueando ESP o GRE, NAT no '
                                                              'traduce correctamente SPIs (para IKE sin NAT-T).',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.proto == 50 || '
                                                                                                'ip.proto == 47',
                                                                    'tcpdump_filter': 'ip proto 50 or ip proto 47',
                                                                    'notes': 'Verificar IPs origen/destino outer.'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'DstMAC=next-hop, SrcMAC=edge_WAN_if, EtherType=0x0800.',
                                                 'checks': 'Interfaz Up. MTU ≥ 1500 + overhead IPSec/GRE (ej: 1540 '
                                                           'para GRE+IPSec).',
                                                 'anomalies': 'MTU insuficiente causando drops silenciosos, interface '
                                                              'errors.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 5: BFD sobre el túnel para calidad de path',
                                     'device': 'Edge SD-WAN ↔ Peer (Hub/Spoke)',
                                     'action': 'Intercambio periódico de paquetes BFD sobre el túnel GRE/IPSec para '
                                               'medir latencia, jitter y pérdida',
                                     'note': 'En SD-WAN, BFD puede correr nativamente sobre el túnel o ser emulado por '
                                             'el propio edge. Los timers suelen ser agresivos (subsecond).',
                                     'layers': [{'name': 'Capa 4/5 - BFD sobre túnel',
                                                 'detail': 'BFD Control: Version=1, State=Up (3), Flags=0, My '
                                                           'Disc/Your Disc configurados. Encapsulado dentro de GRE o '
                                                           'directamente sobre IPSec.',
                                                 'checks': 'Sesión BFD Up en ambos extremos. Timers negociados '
                                                           'consistentemente (Desired Min TX, Required Min RX).',
                                                 'anomalies': 'BFD flapping (Up/Down), timers incompatibles (un lado '
                                                              'requiere 100ms y otro solo puede 1s), paquetes BFD '
                                                              'descartados por QoS en el underlay.',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 3784 || '
                                                                                                'gre || ip.proto == 50',
                                                                    'tcpdump_filter': 'udp port 3784 or ip proto 47 or '
                                                                                      'ip proto 50',
                                                                    'notes': 'BFD puede usar UDP 3784 o estar '
                                                                             'encapsulado en GRE/IPSec.'}},
                                                {'name': 'Capa 3 - Red (IPv4 inner/outer)',
                                                 'detail': 'Inner IP: SrcIP=IP_túnel_local, DstIP=IP_túnel_remoto. '
                                                           'Outer IP: SrcIP=IP_WAN_local, DstIP=IP_WAN_remoto.',
                                                 'checks': 'Direcciones de túnel alcanzables. Routing de underlay '
                                                           'estable.',
                                                 'anomalies': 'Ruta del túnel inalcanzable, peer túnel caído aunque '
                                                              'underlay esté Up.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip',
                                                                    'tcpdump_filter': 'ip',
                                                                    'notes': 'Verificar ambas capas IP si hay '
                                                                             'encapsulación.'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'Ethernet outer con EtherType=0x0800.',
                                                 'checks': 'Sin errores L2 en el underlay.',
                                                 'anomalies': 'Micro-cortes L2 no detectados por capa 3 pero '
                                                              'suficientes para perder BFD.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 6: Flujo de aplicación dirigido basado en SLA',
                                     'device': 'Edge SD-WAN (origen) → Peer (destino)',
                                     'action': 'El edge selecciona el túnel óptimo basado en SLA (latencia, jitter, '
                                               'pérdida) y reenvía el tráfico de aplicación',
                                     'note': 'El steering puede ser por aplicación (App-Aware Routing) o por prefijo. '
                                             'El edge monitoriza SLA vía BFD o probes.',
                                     'layers': [{'name': 'Capa 7 - Aplicación',
                                                 'detail': 'Payload de aplicación: HTTP(S), VoIP (RTP/SIP), SMB, etc.',
                                                 'checks': 'Aplicación funciona correctamente sobre el túnel '
                                                           'seleccionado. No hay timeouts.',
                                                 'anomalies': 'Aplicación lenta (túnel subóptimo seleccionado), VoIP '
                                                              'con mala calidad (alta latencia/jitter en túnel '
                                                              'activo), fallo de failover SLA.',
                                                 'packet_capture': {'wireshark_display_filter': 'http || tls || sip || '
                                                                                                'rtp',
                                                                    'tcpdump_filter': 'tcp port 80 or tcp port 443 or '
                                                                                      'udp port 5060 or udp portrange '
                                                                                      '10000-20000',
                                                                    'notes': 'Filtrar por protocolo de aplicación '
                                                                             'específico.'}},
                                                {'name': 'Capa 4 - Transporte (TCP/UDP)',
                                                 'detail': 'TCP/UDP inner: SrcPort/DstPort de la aplicación. Flags, '
                                                           'Sequence Numbers, Window size normal.',
                                                 'checks': 'Conexiones TCP establecidas. Sin retransmisiones '
                                                           'excesivas. Sin fragmentación.',
                                                 'anomalies': 'TCP retransmits (túnel con pérdida), UDP jitter alto, '
                                                              'NAT dentro del túnel conflicto con applicación.',
                                                 'packet_capture': {'wireshark_display_filter': 'tcp || udp',
                                                                    'tcpdump_filter': 'tcp or udp',
                                                                    'notes': 'Verificar flujo inner.'}},
                                                {'name': 'Capa 3 - Red (Inner IPv4)',
                                                 'detail': 'SrcIP=IP_app_origen, DstIP=IP_app_destino. Protocol=6 '
                                                           '(TCP) o 17 (UDP). TTL decrementado por edge si hace '
                                                           'routing.',
                                                 'checks': 'Subredes de aplicación conocidas y alcanzables por el '
                                                           'túnel.',
                                                 'anomalies': 'Ruta de aplicación no aprendida por SD-WAN, blackhole '
                                                              'en VRF de túnel.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip',
                                                                    'tcpdump_filter': 'ip',
                                                                    'notes': 'Verificar IPs inner.'}},
                                                {'name': 'Capa 3.5/4 - Encapsulación túnel (ESP/GRE)',
                                                 'detail': 'ESP: SPI, Seq#, Encrypted payload. GRE: Flags=0x0000, '
                                                           'Protocol=0x0800, Key opcional.',
                                                 'checks': 'SA IPSec activa. GRE tunnel Up.',
                                                 'anomalies': 'SA IPSec expirada (no rekey), GRE tunnel Down, MTU path '
                                                              'issue (requiere TCP MSS clamping).',
                                                 'packet_capture': {'wireshark_display_filter': 'esp || gre',
                                                                    'tcpdump_filter': 'ip proto 50 or ip proto 47',
                                                                    'notes': 'Verificar encapsulación outer.'}},
                                                {'name': 'Capa 3 - Red (Outer IPv4)',
                                                 'detail': 'SrcIP=IP_WAN_edge, DstIP=IP_WAN_peer. Protocol=50 (ESP) o '
                                                           '47 (GRE). TTL=64.',
                                                 'checks': 'Underlay estable.',
                                                 'anomalies': 'Underlay congestionado, ruta asimétrica.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip',
                                                                    'tcpdump_filter': 'ip',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'DstMAC=next-hop, SrcMAC=edge_WAN_if, EtherType=0x0800.',
                                                 'checks': 'L2 estable.',
                                                 'anomalies': 'Link down, congestion L2.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]}]}]},
 'sr_mpls': {'scenarios': [{'id': 'sr_mpls_sid_stack_php',
                            'name': 'SR-MPLS: Pila de labels con Prefix-SID y Adjacency-SID',
                            'description': 'Recorrido de un paquete IPv4 a través de una red SR-MPLS usando IGP '
                                           '(IS-IS/OSPF) para distribuir SIDs, push de stack en ingress, swap en '
                                           'transit, PHP de Adjacency-SID y pop de Prefix-SID en egress.',
                            'steps': [{'step_title': 'Paso 1: IGP (IS-IS/OSPF) anuncia SIDs como prefijos',
                                       'device': 'Todos los routers SR (IS-IS/OSPF)',
                                       'action': 'Cada router anuncia sus Prefix-SIDs y Adjacency-SIDs mediante '
                                                 'extensiones de IGP',
                                       'note': 'IS-IS usa sub-TLVs en Extended IP Reachability (Type=135). OSPF usa '
                                               'Opaque LSAs (Type 9/10).',
                                       'layers': [{'name': 'Capa 4/7 - IS-IS LSP / OSPF LSA',
                                                   'detail': 'IS-IS: LSP PDU con sub-TLV Prefix-SID (Type=3) y Adj-SID '
                                                             '(Type=31). Flags: R=1, N=1. Algorithm=0 (SPF). SRGB '
                                                             'base=16000, range=8000. Prefix-SID=index+SRGB. OSPF: '
                                                             'Opaque LSA Type-9 intra-area con SID/Label sub-TLV.',
                                                   'checks': 'Todos los routers tienen el mismo SRGB (si se usa '
                                                             'explícito). Prefix-SIDs únicos dentro del dominio. '
                                                             'Adjacency-SIDs locales por interfaz visibles.',
                                                   'anomalies': 'SRGB mismatch (Prefix-SID duplicado), LSP checksum '
                                                                'error, OSPF neighbor Down, sub-TLV desconocido '
                                                                '(router sin soporte SR), algoritmo inconsistente.',
                                                   'packet_capture': {'wireshark_display_filter': 'isis || ospf',
                                                                      'tcpdump_filter': 'isis or ospf',
                                                                      'notes': 'IS-IS usa CLNS (Protocol 0x83FE). OSPF '
                                                                               'usa IP proto 89. Filtrar en interfaces '
                                                                               'de core.'}},
                                                  {'name': 'Capa 3/4 - IS-IS sobre CLNS / OSPF sobre IP',
                                                   'detail': 'IS-IS: CLNS PDU (NLPID=0x81). OSPF: IP Protocol=89, '
                                                             'SrcIP=Router-ID, DstIP=224.0.0.5/6 o unicast.',
                                                   'checks': 'IS-IS adjacencies Up (L1/L2 según diseño). OSPF '
                                                             'neighbors Full. LSDB sincronizada.',
                                                   'anomalies': 'IS-IS MTU mismatch (adjacency flapping), OSPF area '
                                                                'mismatch, CLNS NLPID no procesado, IP multicast '
                                                                'descartado.',
                                                   'packet_capture': {'wireshark_display_filter': 'isis || ospf',
                                                                      'tcpdump_filter': 'isis or ip proto 89',
                                                                      'notes': 'Capturar IS-IS en interfaces de core '
                                                                               '(L2 directo). Capturar OSPF en '
                                                                               'interfaces IP.'}},
                                                  {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                   'detail': 'IS-IS: DstMAC=01:80:C2:00:00:14 (L1), 01:80:C2:00:00:15 '
                                                             '(L2) o 09:00:2B:00:00:05 (All IS). OSPF: '
                                                             'DstMAC=01:00:5E:00:00:05/06. EtherType=0x8847 (MPLS) '
                                                             'para interfaces SR, o 0x0800/0x8864 según encapsulación.',
                                                   'checks': 'Interfaces Up/Up. MAC multicast permitida en switches '
                                                             'intermedios. MTU ≥ 1500 (o jumbo si L2 core).',
                                                   'anomalies': 'MAC multicast filtrada por switch, interface down, '
                                                                'MTU mismatch en L2.',
                                                   'packet_capture': {'wireshark_display_filter': 'eth.addr == '
                                                                                                  '01:80:c2:00:00:14 '
                                                                                                  '|| eth.addr == '
                                                                                                  '01:80:c2:00:00:15 '
                                                                                                  '|| eth.addr == '
                                                                                                  '01:00:5e:00:00:05 '
                                                                                                  '|| eth.addr == '
                                                                                                  '01:00:5e:00:00:06',
                                                                      'tcpdump_filter': 'ether host 01:80:c2:00:00:14 '
                                                                                        'or ether host '
                                                                                        '01:80:c2:00:00:15 or ether '
                                                                                        'host 01:00:5e:00:00:05 or '
                                                                                        'ether host 01:00:5e:00:00:06',
                                                                      'notes': 'Verificar MAC multicast de IGP según '
                                                                               'protocolo.'}}]},
                                      {'step_title': 'Paso 2: Nodo ingress recibe paquete y empuja stack de SIDs',
                                       'device': 'Router Ingress (SR Headend)',
                                       'action': 'El router ingress recibe el paquete IP nativo, consulta la SRDB y '
                                                 'empuja una pila MPLS con Prefix-SID (destino) + Adjacency-SID '
                                                 '(primer salto)',
                                       'note': 'El stack puede tener más labels si la política requiere un path '
                                               'explícito (strict/loose).',
                                       'layers': [{'name': 'Capa 3 - Red (IPv4 Payload)',
                                                   'detail': 'SrcIP=192.168.1.10, DstIP=10.20.30.40, TTL=64, '
                                                             'Protocol=TCP(6). Paquete original del cliente.',
                                                   'checks': 'Ruta existe en FIB global y apunta a SR tunnel o '
                                                             'prefix-sid. Next-hop resuelto vía IGP.',
                                                   'anomalies': 'Ruta faltante en ingress, FIB no sincronizada con RIB '
                                                                '(CEF issue), next-hop no tiene Adj-SID asignado.',
                                                   'packet_capture': {'wireshark_display_filter': 'ip',
                                                                      'tcpdump_filter': 'ip',
                                                                      'notes': 'Verificar paquete IP original.'}},
                                                  {'name': 'Capa 2.5 - MPLS (Label Stack - SR SIDs)',
                                                   'detail': 'Top Label (Adjacency-SID): Label=9001, EXP=0, S=0, '
                                                             'TTL=63. Asignado localmente por el next-hop directo para '
                                                             'identificar el enlace/adjacencia específica.\n'
                                                             'Bottom Label (Prefix-SID): Label=16010, EXP=0, S=1, '
                                                             'TTL=63. Corresponde al destino 10.20.30.0/24 (index=10 + '
                                                             'SRGB base=16000).\n'
                                                             'S=1 indica fondo de pila.',
                                                   'checks': 'SRDB tiene Adj-SID para next-hop. Prefix-SID del destino '
                                                             'aprendido vía IGP. Label stack compatible con MTU.',
                                                   'anomalies': 'Prefix-SID no aprendido (IGP no convergido), Adj-SID '
                                                                'no asignado (interface no habilitada para SR), stack '
                                                                'depth excede capacidad del hardware, MTU insuficiente '
                                                                '(drop silencioso).',
                                                   'packet_capture': {'wireshark_display_filter': 'mpls',
                                                                      'tcpdump_filter': 'mpls',
                                                                      'notes': 'Verificar label stack, S-bits y TTL.'}},
                                                  {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                   'detail': 'DstMAC=MAC_next-hop_P, SrcMAC=MAC_ingress_if, '
                                                             'EtherType=0x8847 (MPLS Unicast).',
                                                   'checks': 'Interfaz core MPLS Up. MAC next-hop resuelta vía ARP/ND. '
                                                             'MTU ≥ 1514 + stack MPLS.',
                                                   'anomalies': 'Interface down, ARP incomplete, EtherType incorrecto, '
                                                                'MTU bajo.',
                                                   'packet_capture': {'wireshark_display_filter': 'eth.type == 0x8847',
                                                                      'tcpdump_filter': 'ether proto 0x8847',
                                                                      'notes': 'Verificar EtherType MPLS en interfaz '
                                                                               'de salida.'}}]},
                                      {'step_title': 'Paso 3: P-router intercambia top label basado en SID',
                                       'device': 'Router P (Transit SR)',
                                       'action': 'El P-router recibe el paquete MPLS, consulta LFIB usando el top '
                                                 'label (Adj-SID) y realiza swap por el siguiente label '
                                                 'correspondiente al SID',
                                       'note': 'En SR-MPLS, el P-router no necesita conocer el Prefix-SID del destino; '
                                               'solo manipula el top label según la LFIB.',
                                       'layers': [{'name': 'Capa 2.5 - MPLS (Label Stack)',
                                                   'detail': 'Top label ingress: Adj-SID=9001. LFIB indica Swap a 9002 '
                                                             '(siguiente Adj-SID) o Pop si es penúltimo hop. EXP=0, '
                                                             'TTL decrementado a 62. Prefix-SID=16010 permanece '
                                                             'intacto (S=1, TTL=63).',
                                                   'checks': 'LFIB tiene entrada para el Adj-SID recibido con acción '
                                                             'Swap o Pop correcta. El Prefix-SID inferior no se '
                                                             'inspecciona.',
                                                   'anomalies': 'LFIB missing (drop), swap a interfaz equivocada, '
                                                                'TTL=0 en label (descartado), label stack corrupto.',
                                                   'packet_capture': {'wireshark_display_filter': 'mpls',
                                                                      'tcpdump_filter': 'mpls',
                                                                      'notes': 'Verificar cambio de top label y TTL.'}},
                                                  {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                   'detail': 'DstMAC=MAC_siguiente_salto, SrcMAC=MAC_P_if_out, '
                                                             'EtherType=0x8847. MAC reescrita en cada salto L2.',
                                                   'checks': 'L2 reachability al siguiente hop. Sin output drops.',
                                                   'anomalies': 'Link down, MAC unicast flooding, STP bloqueando.',
                                                   'packet_capture': {'wireshark_display_filter': 'eth.type == 0x8847',
                                                                      'tcpdump_filter': 'ether proto 0x8847',
                                                                      'notes': 'N/A'}}]},
                                      {'step_title': 'Paso 4: Penúltimo P hace pop de Adjacency-SID (PHP)',
                                       'device': 'Router P (Penúltimo Hop)',
                                       'action': 'El penúltimo P-router elimina el top label (Adj-SID) antes de '
                                                 'entregar al egress, ya que el egress anunció implicit-null para su '
                                                 'Adj-SID',
                                       'note': 'En SR-MPLS con PHP, el egress anuncia label explícito 3 (Implicit '
                                               'Null) para su Adjacency-SID, permitiendo al penúltimo P hacer Pop.',
                                       'layers': [{'name': 'Capa 2.5 - MPLS (Label Stack)',
                                                   'detail': 'Top label Adj-SID eliminado (Pop). Stack restante: '
                                                             'únicamente Prefix-SID=16010 (S=1, TTL=63). Si '
                                                             'explicit-null configurado: top label=0 (IPv4 Explicit '
                                                             'Null) o 2 (IPv6 Explicit Null) en lugar de Pop.',
                                                   'checks': 'Egress anunció implicit-null (label local=3) para su '
                                                             'Adj-SID. LFIB del penúltimo P indica Pop.',
                                                   'anomalies': 'PHP deshabilitado (egress recibe doble stack, aumenta '
                                                                'carga), Pop incorrecto dejando stack vacío, '
                                                                'explicit-null no procesado por egress.',
                                                   'packet_capture': {'wireshark_display_filter': 'mpls',
                                                                      'tcpdump_filter': 'mpls',
                                                                      'notes': 'Verificar que solo queda Prefix-SID al '
                                                                               'llegar al egress.'}},
                                                  {'name': 'Capa 3 - Red (IPv4)',
                                                   'detail': 'IP Header visible tras Pop del Adj-SID: '
                                                             'SrcIP=192.168.1.10, DstIP=10.20.30.40, TTL=61 '
                                                             '(decrementado en cada hop L3/MPLS).',
                                                   'checks': 'IP header intacto. Checksum válido. TTL>0.',
                                                   'anomalies': 'TTL=0 (demasiados hops), IP checksum corrupto.',
                                                   'packet_capture': {'wireshark_display_filter': 'ip',
                                                                      'tcpdump_filter': 'ip',
                                                                      'notes': 'Verificar TTL y checksum tras PHP.'}},
                                                  {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                   'detail': 'DstMAC=MAC_egress_if, SrcMAC=MAC_P_penultimate_if, '
                                                             'EtherType=0x8847 (aún MPLS porque queda Prefix-SID).',
                                                   'checks': 'Interfaz entre P y egress soporta MPLS.',
                                                   'anomalies': 'Interfaz esperando IP nativo (0x0800) y rechaza MPLS.',
                                                   'packet_capture': {'wireshark_display_filter': 'eth.type == 0x8847',
                                                                      'tcpdump_filter': 'ether proto 0x8847',
                                                                      'notes': 'N/A'}}]},
                                      {'step_title': 'Paso 5: Nodo egress hace pop de Prefix-SID y entrega IP nativo',
                                       'device': 'Router Egress (SR Tailend)',
                                       'action': 'El egress recibe el paquete con Prefix-SID, consulta ILM, elimina el '
                                                 'label y reenvía el paquete IPv4 nativo hacia el destino final',
                                       'note': 'El Prefix-SID identifica la función de forwarding del egress hacia el '
                                               'prefijo destino.',
                                       'layers': [{'name': 'Capa 2.5 - MPLS (Label Stack)',
                                                   'detail': 'Prefix-SID=16010. Egress consulta ILM: acción Pop. El '
                                                             'label se elimina y se expone el paquete IP.',
                                                   'checks': 'ILM tiene entrada para Prefix-SID=16010 con acción Pop y '
                                                             'forwarding hacia interfaz de destino correcta.',
                                                   'anomalies': 'Prefix-SID no encontrado en ILM (paquete droppeado), '
                                                                'ILM apunta a interfaz incorrecta (blackhole o '
                                                                'forwarding erróneo).',
                                                   'packet_capture': {'wireshark_display_filter': 'mpls.label == 16010',
                                                                      'tcpdump_filter': 'mpls 16010',
                                                                      'notes': 'Capturar paquetes con Prefix-SID '
                                                                               'específico.'}},
                                                  {'name': 'Capa 3 - Red (IPv4)',
                                                   'detail': 'SrcIP=192.168.1.10, DstIP=10.20.30.40, TTL=60. '
                                                             'Protocol=TCP(6). Checksum IP válido.',
                                                   'checks': 'Ruta en FIB global del egress para DstIP existe. '
                                                             'Next-hop alcanzable vía ARP/ND.',
                                                   'anomalies': 'Ruta faltante en egress, next-hop inalcanzable, TTL '
                                                                'expirado.',
                                                   'packet_capture': {'wireshark_display_filter': 'ip',
                                                                      'tcpdump_filter': 'ip',
                                                                      'notes': 'Verificar paquete IP nativo tras '
                                                                               'decapsulación.'}},
                                                  {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                   'detail': 'DstMAC=MAC_CE_destino o MAC_next-hop, '
                                                             'SrcMAC=MAC_egress_if, EtherType=0x0800. Posible 802.1Q '
                                                             'tag.',
                                                   'checks': 'Interfaz de salida Up/Up. MTU soporta paquete.',
                                                   'anomalies': 'Interface down, output drops, VLAN mismatch.',
                                                   'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                      'tcpdump_filter': 'ether proto ip',
                                                                      'notes': 'N/A'}}]}]}]},
 'dmvpn': {'scenarios': [{'id': 'dmpvpn_phase3_nhrp_spoke_to_spoke',
                          'name': 'DMVPN Fase 3: Registro NHRP y túnel dinámico spoke-to-spoke',
                          'description': 'Recorrido del registro NHRP del spoke en el hub, resolución dinámica '
                                         'spoke-to-spoke mediante NHRP Redirect/Resolution, y establecimiento de túnel '
                                         'IPSec directo entre spokes para forwarding de datos.',
                          'steps': [{'step_title': 'Paso 1: Spoke envía NHRP Registration Request al Hub',
                                     'device': 'Spoke A (DMVPN)',
                                     'action': 'El spoke se registra en el hub anunciando su NBMA (IP pública) y sus '
                                               'redes protegidas',
                                     'note': 'El registro NHRP permite al hub conocer la IP NBMA actual del spoke '
                                             '(útil detrás de NAT).',
                                     'layers': [{'name': 'Capa 5/7 - NHRP Registration Request',
                                                 'detail': 'NHRP Packet Type=1 (Registration Request). Flags: '
                                                           'Unique=1. AFI=0x0001 (IPv4). Protocol Type=0x0800. NBMA '
                                                           'Address=IP_pública_SpokeA. Client Protocol '
                                                           'Address=IP_túnel_SpokeA. Client NBMA '
                                                           'Address=IP_NBMA_SpokeA. Extension: NAT Traversal (NAT-T) '
                                                           'si aplica.',
                                                 'checks': 'NHRP procesado correctamente. Spoke tiene IP NBMA válida. '
                                                           'NAT traversal habilitado si hay NAT.',
                                                 'anomalies': 'Registration Request descartado (NHRP no habilitado en '
                                                              'interfaz), NAT no permite respuesta (sin pinhole), '
                                                              'duplicado de NHRP ID, timeout de registro.',
                                                 'packet_capture': {'wireshark_display_filter': 'nhrp',
                                                                    'tcpdump_filter': 'udp port 487',
                                                                    'notes': 'NHRP usa UDP 487. Filtrar por tipo 1 '
                                                                             '(Registration Request).'}},
                                                {'name': 'Capa 4 - Transporte (UDP)',
                                                 'detail': 'SrcPort=efímero, DstPort=487 (NHRP). Length=variable. '
                                                           'Checksum UDP válido.',
                                                 'checks': 'UDP 487 permitido en firewalls intermedios.',
                                                 'anomalies': 'Firewall bloqueando UDP 487, NAT modificando puertos '
                                                              'fuente de forma incompatible.',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 487',
                                                                    'tcpdump_filter': 'udp port 487',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'SrcIP=IP_NBMA_SpokeA, DstIP=IP_NBMA_Hub. Protocol=17 '
                                                           '(UDP). TTL=64.',
                                                 'checks': 'Spoke tiene conectividad IP al hub. Ruta por defecto o '
                                                           'estática funcional.',
                                                 'anomalies': 'Ruta faltante, ACL bloqueando tráfico al hub, TTL '
                                                              'expirado.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.proto == 17 && '
                                                                                                'udp.port == 487',
                                                                    'tcpdump_filter': 'ip proto 17 and udp port 487',
                                                                    'notes': 'Verificar IPs NBMA.'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'DstMAC=MAC_default_gateway, SrcMAC=MAC_SpokeA_WAN, '
                                                           'EtherType=0x0800.',
                                                 'checks': 'Interfaz WAN Up/Up. ARP resuelto.',
                                                 'anomalies': 'Interface down, ARP incomplete.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 2: Hub responde NHRP Registration Reply',
                                     'device': 'Hub DMVPN',
                                     'action': 'El hub confirma el registro del spoke y actualiza su caché NHRP con la '
                                               'asociación NBMA-protocolo',
                                     'note': 'El Registration Reply indica éxito (Code=0) o error.',
                                     'layers': [{'name': 'Capa 5/7 - NHRP Registration Reply',
                                                 'detail': 'NHRP Packet Type=2 (Registration Reply). Code=0 (Success). '
                                                           'Client NBMA Address=IP_NBMA_SpokeA. Client Protocol '
                                                           'Address=IP_túnel_SpokeA. Server NBMA Address=IP_NBMA_Hub. '
                                                           'Server Protocol Address=IP_túnel_Hub. Hold Time=segundos.',
                                                 'checks': 'Caché NHRP del hub muestra entrada para SpokeA. Hold Time '
                                                           'no expirado.',
                                                 'anomalies': 'Code≠0 (error de autenticación, rango duplicado), caché '
                                                              'no actualizada (memory overflow), reply perdido '
                                                              '(timeout en spoke).',
                                                 'packet_capture': {'wireshark_display_filter': 'nhrp',
                                                                    'tcpdump_filter': 'udp port 487',
                                                                    'notes': 'Filtrar por tipo 2 (Registration '
                                                                             'Reply).'}},
                                                {'name': 'Capa 4 - Transporte (UDP)',
                                                 'detail': 'SrcPort=487, DstPort=efímero (origen del request).',
                                                 'checks': 'Respuesta llega al puerto origen correcto.',
                                                 'anomalies': 'NAT timeout (respuesta llega a puerto cerrado), '
                                                              'firewall stateful bloqueando reply.',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 487',
                                                                    'tcpdump_filter': 'udp port 487',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'SrcIP=IP_NBMA_Hub, DstIP=IP_NBMA_SpokeA. Protocol=17. '
                                                           'TTL=64.',
                                                 'checks': 'Hub puede alcanzar IP NBMA del spoke (importante si spoke '
                                                           'está detrás de NAT con NAT-T).',
                                                 'anomalies': 'Spoke detrás de NAT simétrico (reply no llega), ACL '
                                                              'inbound bloqueando UDP 487 en spoke.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.proto == 17 && '
                                                                                                'udp.port == 487',
                                                                    'tcpdump_filter': 'ip proto 17 and udp port 487',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'Ethernet estándar con EtherType=0x0800.',
                                                 'checks': 'L2 estable.',
                                                 'anomalies': 'Link down.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 3: Spoke A quiere alcanzar red detrás de Spoke B',
                                     'device': 'Spoke A',
                                     'action': 'Spoke A recibe tráfico destinado a una red protegida por Spoke B. Como '
                                               'no tiene entrada NHRP para esa red, enruta el tráfico al hub (default '
                                               'route en tunnel)',
                                     'note': 'En DMVPN Phase 3, los spokes usan default route (0.0.0.0/0) apuntando al '
                                             'túnel NHRP.',
                                     'layers': [{'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'SrcIP=Host_origen, DstIP=Red_destino_SpokeB. TTL=64. '
                                                           'Protocol=TCP/UDP.',
                                                 'checks': 'Spoke A tiene ruta default por el túnel GRE/NHRP hacia el '
                                                           'hub.',
                                                 'anomalies': 'Ruta más específica existente que no apunta al túnel '
                                                              '(tráfico no encapsulado), default route faltante.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip',
                                                                    'tcpdump_filter': 'ip',
                                                                    'notes': 'Verificar forwarding inicial hacia '
                                                                             'hub.'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet inner)',
                                                 'detail': 'Trama Ethernet LAN del spoke hacia el host origen.',
                                                 'checks': 'LAN Up.',
                                                 'anomalies': 'Interface LAN down.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 4: Spoke A envía NHRP Resolution Request al Hub',
                                     'device': 'Spoke A',
                                     'action': 'Spoke A consulta al hub para resolver la IP NBMA de Spoke B (next-hop '
                                               'para la red destino)',
                                     'note': 'El Resolution Request contiene la IP destino que Spoke A quiere '
                                             'alcanzar.',
                                     'layers': [{'name': 'Capa 5/7 - NHRP Resolution Request',
                                                 'detail': 'NHRP Packet Type=6 (Resolution Request). Flags: Q=1. '
                                                           'Client Protocol Address=IP_túnel_SpokeA. Client NBMA '
                                                           'Address=IP_NBMA_SpokeA. Dest Protocol '
                                                           'Address=IP_destino_SpokeB_network.',
                                                 'checks': 'NHRP cache del hub contiene Spoke B. Spoke A tiene '
                                                           'conectividad NHRP al hub.',
                                                 'anomalies': 'Resolution Request descartado, hub sin entrada para red '
                                                              'destino (Spoke B no registrado), timeout de resolución.',
                                                 'packet_capture': {'wireshark_display_filter': 'nhrp',
                                                                    'tcpdump_filter': 'udp port 487',
                                                                    'notes': 'Filtrar por tipo 6 (Resolution '
                                                                             'Request).'}},
                                                {'name': 'Capa 4 - Transporte (UDP)',
                                                 'detail': 'SrcPort=efímero, DstPort=487.',
                                                 'checks': 'Puerto 487 abierto.',
                                                 'anomalies': 'Firewall bloqueando.',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 487',
                                                                    'tcpdump_filter': 'udp port 487',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'SrcIP=IP_túnel_SpokeA, DstIP=IP_túnel_Hub. Protocol=17. '
                                                           'TTL=255 (dentro del túnel GRE) o 64 (nativo).',
                                                 'checks': 'Túnel GRE/IPSec estable entre Spoke A y Hub.',
                                                 'anomalies': 'Túnel caído (IPSec SA expirada, GRE keepalive fallido).',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 487 || '
                                                                                                'gre || esp',
                                                                    'tcpdump_filter': 'udp port 487 or ip proto 47 or '
                                                                                      'ip proto 50',
                                                                    'notes': 'Capturar dentro del túnel GRE o nativo '
                                                                             'según configuración.'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'Ethernet inner (túnel) o outer (underlay) según '
                                                           'encapsulación.',
                                                 'checks': 'L2 estable.',
                                                 'anomalies': 'Link down.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800 || '
                                                                                                'eth.type == 0x8847',
                                                                    'tcpdump_filter': 'ether proto ip or ether proto '
                                                                                      '0x8847',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 5: Hub redirige, Spoke B responde directamente',
                                     'device': 'Hub → Spoke A / Spoke B → Spoke A',
                                     'action': 'El hub envía NHRP Redirect a Spoke A indicándole que solicite '
                                               'resolución directamente a Spoke B. Spoke B responde con NHRP '
                                               'Resolution Reply directamente a Spoke A.',
                                     'note': 'En DMVPN Phase 3, el hub actúa como redirector, no reenvía datos '
                                             'spoke-to-spoke.',
                                     'layers': [{'name': 'Capa 5/7 - NHRP Redirect / Resolution Reply',
                                                 'detail': 'Hub→SpokeA: NHRP Redirect (mensaje de redirección '
                                                           'indicando que Spoke B tiene la ruta). SpokeB→SpokeA: NHRP '
                                                           'Resolution Reply (Type=7) con NBMA Address de Spoke B y '
                                                           'Protocol Address de la red destino.',
                                                 'checks': 'Spoke A recibe Redirect y genera nuevo Resolution Request '
                                                           'directo a Spoke B. Spoke B responde con su NBMA actual.',
                                                 'anomalies': 'Redirect perdido, Spoke B no responde (firewall '
                                                              'bloqueando UDP 487 desde Spoke A), NAT impide '
                                                              'comunicación directa NBMA.',
                                                 'packet_capture': {'wireshark_display_filter': 'nhrp',
                                                                    'tcpdump_filter': 'udp port 487',
                                                                    'notes': 'Filtrar NHRP en ambos sentidos. '
                                                                             'Verificar Redirect y Resolution Reply.'}},
                                                {'name': 'Capa 4 - Transporte (UDP)',
                                                 'detail': 'UDP 487 en ambos mensajes.',
                                                 'checks': 'Sin bloqueo de UDP 487 entre spokes.',
                                                 'anomalies': 'Firewall entre spokes bloqueando NHRP (común en '
                                                              'Internet).',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 487',
                                                                    'tcpdump_filter': 'udp port 487',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'Mensajes viajan entre NBMA addresses de los spokes (o a '
                                                           'través del túnel GRE si aún no se conoce NBMA directo).',
                                                 'checks': 'Spokes pueden alcanzar NBMA mutuamente (o a través de '
                                                           'NAT-T).',
                                                 'anomalies': 'NAT simétrico impide comunicación directa NBMA. Spoke B '
                                                              'detrás de doble NAT.',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 487',
                                                                    'tcpdump_filter': 'udp port 487',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'Ethernet estándar.',
                                                 'checks': 'L2 estable.',
                                                 'anomalies': 'Link down.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 6: Spoke A construye túnel IPSec dinámico a Spoke B',
                                     'device': 'Spoke A ↔ Spoke B',
                                     'action': 'Spoke A conoce la NBMA de Spoke B. Inicia negociación IKEv2/IKEv1 y '
                                               'establece SA IPSec para túnel GRE spoke-to-spoke.',
                                     'note': 'El túnel dinámico usa el mismo perfil de transformación que el hub, pero '
                                             'las SPIs se negocian directamente entre spokes.',
                                     'layers': [{'name': 'Capa 3.5/4 - IKEv2 / IPSec',
                                                 'detail': 'IKEv2: INIT y AUTH entre SpokeA y SpokeB. IPSec ESP: SPIs '
                                                           'negociadas dinámicamente. GRE: Protocol Type=0x0800, Key '
                                                           'opcional.',
                                                 'checks': 'Políticas IKE/IPSec idénticas en ambos spokes. '
                                                           'Certificados o PSK válidos. NAT-T negociado si hay NAT.',
                                                 'anomalies': 'IKE policy mismatch, PSK incorrecta, certificado no '
                                                              'confiado, NAT-T no negociado (comunicación ESP falla a '
                                                              'través de NAT), SA unidireccional.',
                                                 'packet_capture': {'wireshark_display_filter': 'udp.port == 500 || '
                                                                                                'udp.port == 4500 || '
                                                                                                'esp || gre',
                                                                    'tcpdump_filter': 'udp port 500 or udp port 4500 '
                                                                                      'or esp or ip proto 47',
                                                                    'notes': 'IKEv2 usa UDP 500/4500. ESP=proto 50. '
                                                                             'GRE=proto 47.'}},
                                                {'name': 'Capa 3 - Red (Outer IPv4)',
                                                 'detail': 'SrcIP=IP_NBMA_SpokeA, DstIP=IP_NBMA_SpokeB. Protocol=50 '
                                                           '(ESP) o 47 (GRE). TTL=64.',
                                                 'checks': 'NBMAs mutuamente alcanzables directamente o vía NAT-T.',
                                                 'anomalies': 'Peer inalcanzable (NBMA no responde), ACL bloqueando '
                                                              'ESP/GRE entre spokes.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.proto == 50 || '
                                                                                                'ip.proto == 47',
                                                                    'tcpdump_filter': 'ip proto 50 or ip proto 47',
                                                                    'notes': 'Verificar encapsulación outer.'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'DstMAC=next-hop, SrcMAC=SpokeA_WAN_if, EtherType=0x0800.',
                                                 'checks': 'WAN Up. MTU suficiente para GRE+IPSec overhead.',
                                                 'anomalies': 'MTU insuficiente (drops silenciosos).',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 7: Datos fluyen directamente spoke-to-spoke',
                                     'device': 'Spoke A ↔ Spoke B',
                                     'action': 'Tráfico de datos entre redes protegidas fluye directamente a través '
                                               'del túnel GRE/IPSec establecido dinámicamente',
                                     'note': 'El tráfico ya no pasa por el hub, optimizando el path y reduciendo carga '
                                             'en el hub.',
                                     'layers': [{'name': 'Capa 7 - Aplicación',
                                                 'detail': 'Payload de aplicación: HTTP, SMB, VoIP, etc.',
                                                 'checks': 'Aplicación funciona end-to-end. Latencia baja (path '
                                                           'directo).',
                                                 'anomalies': 'Aplicación lenta (aunque túnel esté Up, path puede no '
                                                              'ser óptimo), asimetría de routing.',
                                                 'packet_capture': {'wireshark_display_filter': 'http || tls || sip || '
                                                                                                'smb',
                                                                    'tcpdump_filter': 'tcp port 80 or tcp port 443 or '
                                                                                      'udp port 5060',
                                                                    'notes': 'Filtrar por aplicación.'}},
                                                {'name': 'Capa 4 - Transporte (TCP/UDP)',
                                                 'detail': 'TCP/UDP inner: SrcPort/DstPort de aplicación.',
                                                 'checks': 'Conexiones establecidas.',
                                                 'anomalies': 'Retransmisiones por pérdida en túnel.',
                                                 'packet_capture': {'wireshark_display_filter': 'tcp || udp',
                                                                    'tcpdump_filter': 'tcp or udp',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 3 - Red (Inner IPv4)',
                                                 'detail': 'SrcIP=Host_SpokeA, DstIP=Host_SpokeB. TTL decrementado por '
                                                           'spoke si hace routing.',
                                                 'checks': 'Rutas de redes protegidas aprendidas vía NHRP o routing '
                                                           'overlay.',
                                                 'anomalies': 'Ruta no instalada en caché NHRP (tráfico sigue yendo al '
                                                              'hub), route flapping.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip',
                                                                    'tcpdump_filter': 'ip',
                                                                    'notes': 'Verificar IPs inner.'}},
                                                {'name': 'Capa 3.5/4 - Encapsulación GRE/IPSec',
                                                 'detail': 'GRE: Protocol=0x0800, Flags=0x0000. ESP: SPI=0x00AABBCC, '
                                                           'Seq#. Encrypted payload.',
                                                 'checks': 'SA IPSec activa y no expirada. GRE tunnel Up.',
                                                 'anomalies': 'SA expirada (no rekey automático), GRE keepalive '
                                                              'fallido, MTU path issue.',
                                                 'packet_capture': {'wireshark_display_filter': 'esp || gre',
                                                                    'tcpdump_filter': 'ip proto 50 or ip proto 47',
                                                                    'notes': 'Verificar encapsulación.'}},
                                                {'name': 'Capa 3 - Red (Outer IPv4)',
                                                 'detail': 'SrcIP=IP_NBMA_SpokeA, DstIP=IP_NBMA_SpokeB. Protocol=50 o '
                                                           '47. TTL=64.',
                                                 'checks': 'Underlay estable entre NBMAs.',
                                                 'anomalies': 'Peer NBMA no responde, NAT cambió mapping.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip',
                                                                    'tcpdump_filter': 'ip',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'Ethernet estándar.',
                                                 'checks': 'L2 estable.',
                                                 'anomalies': 'Link down.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]}]}]},
 'eigrp': {'scenarios': [{'id': 'eigrp_hello_update_dual',
                          'name': 'EIGRP: Intercambio Hello, Update/Query/Reply y DUAL',
                          'description': 'Recorrido del establecimiento de adyacencia EIGRP mediante Hellos multicast, '
                                         'intercambio de Updates iniciales con ACKs, y proceso DUAL ante pérdida de '
                                         'ruta con Query/Reply.',
                          'steps': [{'step_title': 'Paso 1: Router A envía EIGRP Hello (224.0.0.10)',
                                     'device': 'Router A',
                                     'action': 'Router A envía paquete EIGRP Hello multicast para descubrir vecinos en '
                                               'la misma subred',
                                     'note': 'EIGRP Hello usa multicast 224.0.0.10 (IPv4) o FF02::A (IPv6). No '
                                             'requiere confirmación.',
                                     'layers': [{'name': 'Capa 5/4 - EIGRP Hello',
                                                 'detail': 'EIGRP Packet: Version=2, Opcode=5 (Hello), Flags=0x0000, '
                                                           'Sequence=0, Ack=0. TLVs: Parameter Type=0x0001 (K-values: '
                                                           'K1=1, K2=0, K3=1, K4=0, K5=0; Hold Time=15s). Autonomous '
                                                           'System=100.',
                                                 'checks': 'AS number correcto. K-values idénticos en todos los '
                                                           'vecinos. Hold Time adecuado. Interfaz habilitada para '
                                                           'EIGRP.',
                                                 'anomalies': 'AS mismatch (adyacencia rechazada), K-values mismatch '
                                                              '(no forman adyacencia), Hello descartado por ACL, '
                                                              'passive interface.',
                                                 'packet_capture': {'wireshark_display_filter': 'eigrp',
                                                                    'tcpdump_filter': 'ip multicast and ip[9] == 88',
                                                                    'notes': 'EIGRP usa IP protocol 88. Filtrar '
                                                                             'multicast 224.0.0.10.'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'SrcIP=IP_interfaz_A, DstIP=224.0.0.10. Protocol=88 '
                                                           '(EIGRP). TTL=2. IP Checksum válido.',
                                                 'checks': 'Interfaz tiene IP en subred correcta. Multicast permitido '
                                                           'en switches. No hay ACL bloqueando IP proto 88.',
                                                 'anomalies': 'TTL=0 o 1 (algunos routers descartan), ACL bloqueando '
                                                              'EIGRP multicast, subred diferente (vecino no recibe).',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.dst == 224.0.0.10 '
                                                                                                '&& ip.proto == 88',
                                                                    'tcpdump_filter': 'host 224.0.0.10 and ip proto 88',
                                                                    'notes': 'Verificar TTL=2 obligatorio para EIGRP '
                                                                             'multicast.'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'DstMAC=01:00:5E:00:00:0A (mapeo de 224.0.0.10). '
                                                           'SrcMAC=MAC_interfaz_A. EtherType=0x0800.',
                                                 'checks': 'Switch permite MAC multicast 01:00:5E:00:00:0A. IGMP '
                                                           'snooping no bloquea EIGRP multicast (EIGRP no usa IGMP). '
                                                           'Spanning-tree no bloquea puerto.',
                                                 'anomalies': 'Switch filtrando MAC multicast, spanning-tree blocking, '
                                                              'interface down.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.addr == '
                                                                                                '01:00:5e:00:00:0a',
                                                                    'tcpdump_filter': 'ether host 01:00:5e:00:00:0a',
                                                                    'notes': 'Verificar MAC multicast de EIGRP.'}}]},
                                    {'step_title': 'Paso 2: Router B recibe, verifica AS number y K-values',
                                     'device': 'Router B',
                                     'action': 'Router B recibe el Hello, valida AS number y K-values. Si coinciden, '
                                               'procesa el paquete y prepara respuesta.',
                                     'note': 'EIGRP no forma adyacencia si AS o K-values difieren. El Hold Time debe '
                                             'ser mayor que el Hello Interval.',
                                     'layers': [{'name': 'Capa 5/4 - EIGRP Hello (procesado)',
                                                 'detail': 'Mismo contenido que el Hello de A: Opcode=5, Flags=0, '
                                                           'Seq=0, Ack=0. TLV Parameter con AS=100, K1=1, K2=0, K3=1, '
                                                           'K4=0, K5=0.',
                                                 'checks': 'Router B verifica AS=100 (match). K-values idénticos. Hold '
                                                           'Time aceptable.',
                                                 'anomalies': 'AS mismatch → log %DUAL-5-NBRCHANGE. K-values mismatch '
                                                              '→ adyacencia no formada. Hello con opciones '
                                                              'incompatibles (ej: stub mismatch).',
                                                 'packet_capture': {'wireshark_display_filter': 'eigrp',
                                                                    'tcpdump_filter': 'ip proto 88',
                                                                    'notes': 'Verificar TLV Parameter en Wireshark.'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'DstIP=224.0.0.10 llega a interfaz de B. Protocol=88. TTL≥1 '
                                                           'al recibir.',
                                                 'checks': 'Interfaz B en misma subred.',
                                                 'anomalies': 'TTL expirado en tránsito (raro en L2 directo), IP '
                                                              'checksum error (frame corrupto).',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.dst == 224.0.0.10 '
                                                                                                '&& ip.proto == 88',
                                                                    'tcpdump_filter': 'host 224.0.0.10 and ip proto 88',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'DstMAC=01:00:5E:00:00:0A recibida en interfaz B.',
                                                 'checks': 'Interfaz B recibe frames multicast correctamente.',
                                                 'anomalies': 'NIC en modo promiscuo no requerido (multicast se '
                                                              'procesa por MAC), frame corrupto (FCS error).',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.addr == '
                                                                                                '01:00:5e:00:00:0a',
                                                                    'tcpdump_filter': 'ether host 01:00:5e:00:00:0a',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 3: Router B envía Hello de respuesta',
                                     'device': 'Router B',
                                     'action': 'Router B envía EIGRP Hello multicast (o unicast tras formar adyacencia '
                                               'inicial) confirmando presencia y parámetros',
                                     'note': 'Tras la adyacencia inicial, los Hellos continúan periódicamente '
                                             '(típicamente cada 5s en redes multipunto, 1s en punto-a-punto).',
                                     'layers': [{'name': 'Capa 5/4 - EIGRP Hello',
                                                 'detail': 'Version=2, Opcode=5, Flags=0x0000, Sequence=0, Ack=0. TLV '
                                                           'Parameter Type=0x0001 (AS=100, K1=1, K2=0, K3=1, K4=0, '
                                                           'K5=0, Hold Time=15s).',
                                                 'checks': 'Parámetros consistentes con Router A.',
                                                 'anomalies': 'Parámetros cambiados durante operación (flapping de '
                                                              'adyacencia).',
                                                 'packet_capture': {'wireshark_display_filter': 'eigrp',
                                                                    'tcpdump_filter': 'ip proto 88',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'SrcIP=IP_interfaz_B, DstIP=224.0.0.10. Protocol=88. TTL=2.',
                                                 'checks': 'IP origen en misma subred.',
                                                 'anomalies': 'Secondary IP mismatch (EIGRP usa primary IP).',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.dst == 224.0.0.10 '
                                                                                                '&& ip.proto == 88',
                                                                    'tcpdump_filter': 'host 224.0.0.10 and ip proto 88',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'DstMAC=01:00:5E:00:00:0A, SrcMAC=MAC_interfaz_B, '
                                                           'EtherType=0x0800.',
                                                 'checks': 'L2 estable.',
                                                 'anomalies': 'Link down.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.addr == '
                                                                                                '01:00:5e:00:00:0a',
                                                                    'tcpdump_filter': 'ether host 01:00:5e:00:00:0a',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 4: Router A envía Update con rutas iniciales',
                                     'device': 'Router A',
                                     'action': 'Una vez formada la adyacencia, Router A envía un Update unicast (o '
                                               'multicast) con sus rutas conocidas al vecino B',
                                     'note': 'El Update inicial tiene Flag Init=1 (0x0001) indicando inicio de '
                                             'intercambio de rutas.',
                                     'layers': [{'name': 'Capa 5/4 - EIGRP Update',
                                                 'detail': 'Version=2, Opcode=1 (Update), Flags=0x0001 (Init), '
                                                           'Sequence=1, Ack=0. TLVs: IP Internal Routes (Type=0x0102) '
                                                           'con prefijos, métricas (Bandwidth, Delay, Load, '
                                                           'Reliability, MTU, Hop Count), Next-Hop.',
                                                 'checks': 'Rutas locales correctamente incluidas en Update. Métricas '
                                                           'calculadas correctamente. Next-hop alcanzable.',
                                                 'anomalies': 'Update descartado (ACL), split horizon bloqueando '
                                                              'readvertisement, métrica infinita (route stuck in '
                                                              'active).',
                                                 'packet_capture': {'wireshark_display_filter': 'eigrp.opcode == 1',
                                                                    'tcpdump_filter': 'ip proto 88',
                                                                    'notes': 'Filtrar por Opcode=1 (Update). Verificar '
                                                                             'TLV Internal Routes.'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'SrcIP=IP_interfaz_A, DstIP=IP_interfaz_B (unicast) o '
                                                           '224.0.0.10 (multicast). Protocol=88. TTL=2 (multicast) o '
                                                           '64 (unicast).',
                                                 'checks': 'Vecino B alcanzable por IP.',
                                                 'anomalies': 'Ruta al vecino inestable, TTL expirado.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.proto == 88 && '
                                                                                                'eigrp.opcode == 1',
                                                                    'tcpdump_filter': 'ip proto 88',
                                                                    'notes': 'Updates iniciales pueden ser multicast o '
                                                                             'unicast según configuración.'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'Unicast: DstMAC=MAC_interfaz_B. Multicast: '
                                                           'DstMAC=01:00:5E:00:00:0A. SrcMAC=MAC_interfaz_A. '
                                                           'EtherType=0x0800.',
                                                 'checks': 'MAC destino resuelta (unicast) o multicast permitida.',
                                                 'anomalies': 'MAC destino unknown (flooding), multicast filtrado.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 5: Router B envía Ack',
                                     'device': 'Router B',
                                     'action': 'Router B confirma recepción del Update de A enviando un ACK (EIGRP '
                                               'Hello con número de Ack correspondiente)',
                                     'note': 'En EIGRP, el ACK es un paquete Hello (Opcode=5) sin datos TLV, con el '
                                             'campo Ack establecido al Sequence Number del Update recibido.',
                                     'layers': [{'name': 'Capa 5/4 - EIGRP Ack',
                                                 'detail': 'Version=2, Opcode=5 (Hello/Ack), Flags=0x0000, Sequence=0, '
                                                           'Ack=1 (Sequence de A). Sin TLVs de datos.',
                                                 'checks': 'Ack corresponde al Sequence Number del Update. Sin '
                                                           'retransmisión de Update por parte de A.',
                                                 'anomalies': 'Ack perdido (A retransmite Update), Ack con número '
                                                              'incorrecto (A ignora y retransmite).',
                                                 'packet_capture': {'wireshark_display_filter': 'eigrp.opcode == 5 && '
                                                                                                'eigrp.ack != 0',
                                                                    'tcpdump_filter': 'ip proto 88',
                                                                    'notes': 'Ack tiene Opcode=5 pero Ack≠0. Filtrar '
                                                                             'en Wireshark por eigrp.ack.'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'SrcIP=IP_interfaz_B, DstIP=IP_interfaz_A (unicast). '
                                                           'Protocol=88. TTL=64.',
                                                 'checks': 'Unicast a A funcional.',
                                                 'anomalies': 'Ruta unicast fallando (asimetría).',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.src == IP_B && '
                                                                                                'ip.dst == IP_A && '
                                                                                                'ip.proto == 88',
                                                                    'tcpdump_filter': 'host IP_B and host IP_A and ip '
                                                                                      'proto 88',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'DstMAC=MAC_interfaz_A, SrcMAC=MAC_interfaz_B, '
                                                           'EtherType=0x0800.',
                                                 'checks': 'MAC de A aprendida.',
                                                 'anomalies': 'MAC not learned.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 6: Si ruta perdida, Query enviado, Reply recibido',
                                     'device': 'Router A / Router B / Vecinos EIGRP',
                                     'action': 'Cuando una ruta se pierde y no hay sucesor factible, el router envía '
                                               'Query multicast/unicast a todos los vecinos y espera Reply antes de '
                                               'reconverger',
                                     'note': 'El Query lleva la métrica actual (posiblemente infinita) para el prefijo '
                                             'afectado. Los vecinos deben responder con Reply.',
                                     'layers': [{'name': 'Capa 5/4 - EIGRP Query / Reply',
                                                 'detail': 'Query: Opcode=3, Flags=0x0000, Sequence=X, Ack=0. TLV IP '
                                                           'Internal Routes con prefijo afectado y métrica=4294967295 '
                                                           '(infinite/inaccessible) o métrica actual. Reply: Opcode=4, '
                                                           'Flags=0x0000, Sequence=Y, Ack=X. TLV con métrica del '
                                                           'vecino.',
                                                 'checks': 'Todos los vecinos responden Reply antes del Active Time (3 '
                                                           'minutos por defecto). Sin SIA (Stuck-In-Active). '
                                                           'Query/Reply loop-free.',
                                                 'anomalies': 'SIA (Stuck-In-Active) por Reply no recibido, Query '
                                                              'storm (muchas rutas activas simultáneamente), vecino no '
                                                              'responde (CPU alta, interface congestionada).',
                                                 'packet_capture': {'wireshark_display_filter': 'eigrp.opcode == 3 || '
                                                                                                'eigrp.opcode == 4',
                                                                    'tcpdump_filter': 'ip proto 88',
                                                                    'notes': 'Opcode 3=Query, 4=Reply. Verificar '
                                                                             'métricas en TLV Internal Routes.'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'Query: multicast 224.0.0.10 (TTL=2) o unicast por vecino. '
                                                           'Reply: unicast al originador del Query. Protocol=88.',
                                                 'checks': 'Multicasts llegan a todos los vecinos. Unicasts no '
                                                           'descartados.',
                                                 'anomalies': 'Multicast Query perdido (L2 issue), Reply unicast '
                                                              'descartado por ACL, TTL expirado.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.proto == 88 && '
                                                                                                '(eigrp.opcode == 3 || '
                                                                                                'eigrp.opcode == 4)',
                                                                    'tcpdump_filter': 'ip proto 88',
                                                                    'notes': 'Capturar ambos sentidos.'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'Multicast: DstMAC=01:00:5E:00:00:0A. Unicast: DstMAC del '
                                                           'vecino específico.',
                                                 'checks': 'L2 permite multicast Query y unicast Reply.',
                                                 'anomalies': 'L2 congestion descartando EIGRP packets, STP blocking.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.addr == '
                                                                                                '01:00:5e:00:00:0a || '
                                                                                                'eth.dst == MAC_vecino',
                                                                    'tcpdump_filter': 'ether host 01:00:5e:00:00:0a or '
                                                                                      'ether host MAC_vecino',
                                                                    'notes': 'N/A'}}]},
                                    {'step_title': 'Paso 7: Algoritmo DUAL computa sucesor factible',
                                     'device': 'Router A / Router B',
                                     'action': 'Tras recibir todos los Replies, DUAL evalúa las métricas reportadas '
                                               'por vecinos, verifica la condición de factibilidad (RD < FD) y '
                                               'selecciona nuevo sucesor',
                                     'note': 'Si no hay sucesor factible, la ruta queda en Active hasta recibir Reply. '
                                             'Si hay sucesor factible, la transición es local sin Query.',
                                     'layers': [{'name': 'Capa 5/4 - EIGRP Update (nueva ruta)',
                                                 'detail': 'Opcode=1 (Update), Flags=0x0000, Sequence=Z, Ack=0. TLV IP '
                                                           'Internal Routes con prefijo actualizado, nueva métrica '
                                                           'composite (Bandwidth + Delay), nuevo Next-Hop (sucesor '
                                                           'factible).',
                                                 'checks': 'Nueva métrica calculada correctamente. Next-hop '
                                                           'alcanzable. Ruta instalada en RIB/FIB.',
                                                 'anomalies': 'Métrica incorrecta (K-values inconsistentes), loop de '
                                                              'routing (condición de factibilidad violada), ruta no '
                                                              'instalada (admin distance conflict).',
                                                 'packet_capture': {'wireshark_display_filter': 'eigrp.opcode == 1',
                                                                    'tcpdump_filter': 'ip proto 88',
                                                                    'notes': 'Verificar Update anunciando nueva '
                                                                             'métrica post-DUAL.'}},
                                                {'name': 'Capa 3 - Red (IPv4)',
                                                 'detail': 'SrcIP=IP_router, DstIP=vecino o multicast. Protocol=88.',
                                                 'checks': 'Conectividad IP estable.',
                                                 'anomalies': 'Asymmetric routing.',
                                                 'packet_capture': {'wireshark_display_filter': 'ip.proto == 88',
                                                                    'tcpdump_filter': 'ip proto 88',
                                                                    'notes': 'N/A'}},
                                                {'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'detail': 'Ethernet estándar.',
                                                 'checks': 'L2 estable.',
                                                 'anomalies': 'Link down.',
                                                 'packet_capture': {'wireshark_display_filter': 'eth.type == 0x0800',
                                                                    'tcpdump_filter': 'ether proto ip',
                                                                     'notes': 'N/A'}}]}]}]},
     'pbr': {
        'scenarios': [
{
    "id": "pbr_route_map_forwarding",
    "name": "PBR - Policy-Based Routing con route-map",
    "description": "Recorrido de un paquete IP que es procesado por Policy-Based Routing en un router. Se evalúan criterios de match en route-map (ACL, prefix-list) y se redirige el tráfico fuera de la tabla de routing por defecto hacia un next-hop o interfaz específica.",
    "steps": [
        {
            "step_title": "Paso 1: Paquete ingresa por interfaz de entrada",
            "device": "Router - Interfaz ingress",
            "action": "La trama Ethernet llega al puerto de entrada del router que tiene aplicada la política PBR.",
            "note": "PBR solo actúa sobre paquetes que ingresan por interfaces configuradas con 'ip policy route-map'.",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (Ethernet)",
                    "detail": "DstMAC=MAC_router_ingress, SrcMAC=MAC_host_origen, EtherType=0x0800 (IPv4). FCS válido.",
                    "checks": "Interfaz ingress Up/Up. MAC de destino resuelta correctamente. Sin errores de CRC.",
                    "anomalies": "Interfaz en estado down, MAC destino incorrecta (paquete descartado en L2), CRC errors indican problema físico.",
                    "packet_capture": {
                        "wireshark_display_filter": "eth.dst == MAC_router && eth.type == 0x0800",
                        "tcpdump_filter": "ether host MAC_router and ip",
                        "notes": "Capturar en interfaz ingress del router. Verificar que la trama llega intacta."
                    }
                },
                {
                    "name": "Capa 3 - Red (IPv4)",
                    "detail": "SrcIP=IP_origen, DstIP=IP_destino, Protocol=TCP(6)/UDP(17), TTL=X, Header Checksum válido.",
                    "checks": "Paquete IP no tiene errores de checksum. TTL > 0. Tamaño dentro de MTU de interfaz.",
                    "anomalies": "IP checksum incorrecto (descarte ASIC), TTL=0 (loop o path largo), IP options que complejicen el parsing.",
                    "packet_capture": {
                        "wireshark_display_filter": "ip.src == IP_origen && ip.dst == IP_destino",
                        "tcpdump_filter": "host IP_origen and host IP_destino",
                        "notes": "Filtrar por IPs de origen y destino para aislar el flujo de interés."
                    }
                },
                {
                    "name": "Capa 4 - Transporte (TCP/UDP)",
                    "detail": "SrcPort=X, DstPort=Y (ej: 80, 443, 22). TCP flags: SYN, ACK, etc. Sequence numbers presentes.",
                    "checks": "Puertos bien formados. Flags TCP válidos para el estado de la conexión. Checksum L4 correcto.",
                    "anomalies": "Puertos malformados, checksum L4 incorrecto, TCP flags inválidos (ej: todos en 1).",
                    "packet_capture": {
                        "wireshark_display_filter": "tcp or udp",
                        "tcpdump_filter": "tcp or udp",
                        "notes": "Expandir capa TCP/UDP en Wireshark para verificar puertos y flags."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 3: Evaluación de route-map y criterios de match",
            "device": "Router - PBR Engine",
            "action": "Se evalúan secuencialmente las sentencias del route-map: match ip address (ACL), match length, match interface, etc.",
            "note": "El route-map se procesa en orden secuencial. La primera coincidencia determina la acción.",
            "layers": [
                {
                    "name": "Capa 3 - Red (IP/ACL)",
                    "detail": "ACL evalúa SrcIP, DstIP, Protocol. Prefix-list evalúa prefijos y longitudes de máscara.",
                    "checks": "La ACL o prefix-list referenciada existe y tiene entradas correctas. La secuencia del route-map no tiene lógica contradictoria.",
                    "anomalies": "ACL inexistente (route-map no hace match nunca), ACL mal ordenada (deny implícito bloquea tráfico esperado), prefix-list con máscaras incorrectas.",
                    "packet_capture": {
                        "wireshark_display_filter": "ip",
                        "tcpdump_filter": "ip",
                        "notes": "Usar 'show route-map' y 'show access-lists' para verificar configuración, no solo captura."
                    }
                },
                {
                    "name": "Capa 4 - Transporte (TCP/UDP/Ports)",
                    "detail": "Si la ACL incluye puertos (extended ACL), se evalúan SrcPort y DstPort junto con el protocolo.",
                    "checks": "Extended ACL coincide con los puertos y protocolo del paquete. Orden de entradas permit/deny correcto.",
                    "anomalies": "Extended ACL con puertos invertidos (src vs dst), protocolo no coincide (TCP vs UDP), wildcard mask incorrecta.",
                    "packet_capture": {
                        "wireshark_display_filter": "tcp.port == X || udp.port == Y",
                        "tcpdump_filter": "tcp port X or udp port Y",
                        "notes": "Verificar en captura que los puertos capturados coincidan con la ACL configurada."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 4: Aplicación de acciones set (next-hop, interfaz, precedencia)",
            "device": "Router - PBR Engine",
            "action": "Si hay coincidencia, se aplican las acciones set: set ip next-hop, set interface, set ip precedence/dscp.",
            "note": "El next-hop debe ser resoluble en la tabla ARP/ND del router; de lo contrario, el paquete puede ser droppeado.",
            "layers": [
                {
                    "name": "Capa 3 - Red (IP/Decision PBR)",
                    "detail": "Se sobrescribe la decisión de forwarding del FIB. set ip next-hop=A.B.C.D, set ip precedence=5, set dscp=EF.",
                    "checks": "El next-hop indicado es alcanzable (entrada ARP/ND presente). La interfaz de salida está Up/Up.",
                    "anomalies": "Next-hop no resoluble (paquete droppeado), next-hop inactivo (sin detección de next-hop verify-availability), interfaz de salida en down.",
                    "packet_capture": {
                        "wireshark_display_filter": "ip",
                        "tcpdump_filter": "ip",
                        "notes": "Capturar en interfaz de salida PBR para confirmar que el paquete sale por el path correcto."
                    }
                },
                {
                    "name": "Capa 2 - Enlace de Datos (Salida)",
                    "detail": "Se reescribe la trama Ethernet: nuevo DstMAC=MAC_next_hop o MAC_destino si es directamente conectado.",
                    "checks": "Resolución ARP/ND exitosa para el next-hop. MAC de siguiente salto presente en tabla ARP.",
                    "anomalies": "ARP incomplete (no hay MAC para el next-hop), MAC del vecino no responde a ARP request.",
                    "packet_capture": {
                        "wireshark_display_filter": "arp || ip",
                        "tcpdump_filter": "arp or ip",
                        "notes": "Verificar tráfico ARP previo si el next-hop no tiene entrada L2 resuelta."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 5: Forwarding vía path PBR (no FIB default)",
            "device": "Router - Interfaz de salida PBR",
            "action": "El paquete se reenvía según la decisión PBR, ignorando completamente la entrada por defecto de la tabla de routing.",
            "note": "El contador de la política PBR debe incrementarse ('show route-map' o 'show policy-map interface').",
            "layers": [
                {
                    "name": "Capa 3 - Red (IPv4)",
                    "detail": "SrcIP=IP_origen, DstIP=IP_destino. TTL decrementado en 1. IP Checksum recalculado.",
                    "checks": "TTL decrementado correctamente. IP checksum recalculado. TOS/Precedence modificado si fue configurado.",
                    "anomalies": "TTL no decrementado (bug o bypass), checksum incorrecto, paquete enrutado por FIB en lugar de PBR (falla de configuración).",
                    "packet_capture": {
                        "wireshark_display_filter": "ip.src == IP_origen && ip.dst == IP_destino",
                        "tcpdump_filter": "host IP_origen and host IP_destino",
                        "notes": "Capturar en interfaz de salida para confirmar que el paquete sigue el path PBR."
                    }
                },
                {
                    "name": "Capa 2 - Enlace de Datos (Ethernet de salida)",
                    "detail": "DstMAC=MAC_next_hop, SrcMAC=MAC_router_egress, EtherType=0x0800. Posible VLAN tag si es subinterfaz.",
                    "checks": "MAC de destino correcta para el next-hop. VLAN tag correcto si aplica. MTU no excedido.",
                    "anomalies": "MAC destino incorrecta (envío a gateway equivocado), VLAN missing o incorrecta, giant frame por encapsulación adicional.",
                    "packet_capture": {
                        "wireshark_display_filter": "eth.src == MAC_router_egress && ip",
                        "tcpdump_filter": "ether host MAC_router_egress and ip",
                        "notes": "Verificar en salida que la trama Ethernet está correctamente reescrita para el path PBR."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 6: Sin coincidencia - fallback a routing normal",
            "device": "Router - FIB lookup",
            "action": "Si ninguna secuencia del route-map hace match, el paquete sigue el proceso de forwarding estándar mediante lookup en la FIB.",
            "note": "El comportamiento por defecto es caer al proceso de routing normal. Algunas plataformas permiten 'set default next-hop'.",
            "layers": [
                {
                    "name": "Capa 3 - Red (IPv4)",
                    "detail": "DstIP consultada en FIB/RIB. Longest prefix match determina next-hop y interfaz de salida por defecto.",
                    "checks": "Ruta hacia DstIP presente en RIB/FIB. Next-hop resoluble. Métrica/administrative distance correcta.",
                    "anomalies": "Ruta faltante en RIB (drop/null0), next-hop no resoluble (drop), FIB desincronizada con RIB.",
                    "packet_capture": {
                        "wireshark_display_filter": "ip.dst == IP_destino",
                        "tcpdump_filter": "host IP_destino",
                        "notes": "Si no hay match PBR, el paquete debe aparecer en la interfaz de salida determinada por la FIB."
                    }
                },
                {
                    "name": "Capa 2 - Enlace de Datos (Salida normal)",
                    "detail": "Encapsulación Ethernet estándar según la interfaz de salida determinada por la FIB.",
                    "checks": "ARP/ND resuelto para el next-hop por defecto. Interfaz de salida en forwarding state.",
                    "anomalies": "Interfaz de salida en down, ARP incomplete para el next-hop por defecto, loop de routing.",
                    "packet_capture": {
                        "wireshark_display_filter": "ip.dst == IP_destino",
                        "tcpdump_filter": "host IP_destino",
                        "notes": "Comparar path de salida normal vs path PBR para validar la política."
                    }
                }
            ]
        }
    ]
}
        ]
    },
    'security': {
        'scenarios': [
{
    "id": "stateful_firewall_acl_filtering",
    "name": "Seguridad - Stateful Firewall y ACL con connection tracking",
    "description": "Simulación del flujo de un paquete a través de un firewall stateful. Se evalúan ACLs o zone-pairs, se inspecciona la tabla de conexiones para tráfico existente, se crean nuevos estados para conexiones permitidas, y se gestiona el tráfico de retorno o los descartes con log.",
    "steps": [
        {
            "step_title": "Paso 1: Paquete llega a interfaz outside",
            "device": "Firewall - Interfaz outside/untrust",
            "action": "La trama Ethernet con el paquete IP llega a la interfaz perimetral del firewall.",
            "note": "La dirección del tráfico (outside→inside vs inside→outside) determina qué políticas de zona aplican.",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (Ethernet)",
                    "detail": "DstMAC=MAC_firewall_outside, SrcMAC=MAC_upstream, EtherType=0x0800.",
                    "checks": "Interfaz outside Up/Up. MAC destino coincide con la interfaz. Sin errores físicos.",
                    "anomalies": "Link down, MAC flapping, errores de CRC indican problema de capa física.",
                    "packet_capture": {
                        "wireshark_display_filter": "eth.dst == MAC_firewall && ip",
                        "tcpdump_filter": "ether host MAC_firewall and ip",
                        "notes": "Capturar en puerto outside para confirmar recepción del paquete."
                    }
                },
                {
                    "name": "Capa 3 - Red (IPv4)",
                    "detail": "SrcIP=IP_origen_externa, DstIP=IP_interna, Protocol=TCP/UDP, TTL decrementado.",
                    "checks": "IP header válido, checksum correcto, TTL > 0.",
                    "anomalies": "IP spoofing (src IP de rango interno desde outside), IP malformed, fragmentación excesiva.",
                    "packet_capture": {
                        "wireshark_display_filter": "ip.dst == IP_interna",
                        "tcpdump_filter": "host IP_interna",
                        "notes": "Verificar source IP para detectar posible spoofing."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 2: Evaluación de ACL o zone-pair",
            "device": "Firewall - Motor de políticas",
            "action": "El firewall evalúa las reglas ACL o la configuración de zone-pair/security policy aplicable a la interfaz/zona de entrada.",
            "note": "Las ACL se evalúan secuencialmente. La primera coincidencia determina permit o deny.",
            "layers": [
                {
                    "name": "Capa 3 - Red (IP/ACL)",
                    "detail": "Reglas ACL: permit/deny basado en SrcIP, DstIP, Protocol. Zone-pair: source zone → destination zone.",
                    "checks": "Existe una regla explícita que cubre el flujo. La ACL no termina en deny implícito no deseado.",
                    "anomalies": "ACL mal ordenada, falta regla permit (deny implícito), zone-pair no configurado para la combinación de zonas.",
                    "packet_capture": {
                        "wireshark_display_filter": "ip.src == IP_origen && ip.dst == IP_interna",
                        "tcpdump_filter": "host IP_origen and host IP_interna",
                        "notes": "Usar 'show access-list' / 'show zone-pair security' para correlacionar con la captura."
                    }
                },
                {
                    "name": "Capa 4 - Transporte (TCP/UDP)",
                    "detail": "Puertos SrcPort/DstPort evaluados en ACL extendida. Protocolo TCP/UDP/ICMP verificado.",
                    "checks": "Puertos del flujo coinciden con la regla ACL. Protocolo correcto.",
                    "anomalies": "Regla ACL con puertos invertidos, protocolo no coincide, ACL basada en puertos pero tráfico ICMP.",
                    "packet_capture": {
                        "wireshark_display_filter": "tcp.port == X || udp.port == Y",
                        "tcpdump_filter": "tcp port X or udp port Y",
                        "notes": "Verificar que puertos y protocolo de la captura coinciden con la ACL."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 3: Inspección stateful - verificación de tabla de conexiones",
            "device": "Firewall - Connection Tracker",
            "action": "El motor stateful verifica si el paquete pertenece a una conexión existente en la connection/state table.",
            "note": "El stateful inspection rastrea el estado de la conexión TCP (SYN, SYN-ACK, ACK) y secuencias para prevenir ataques.",
            "layers": [
                {
                    "name": "Capa 4 - Transporte (TCP State)",
                    "detail": "TCP flags: SYN, ACK, FIN, RST. Sequence number (SEQ), Acknowledgment number (ACK). Window size.",
                    "checks": "Si es tráfico de retorno: ACK válido respecto al SEQ esperado. Flags consistentes con estado de conexión. Sin anomalías de secuencia.",
                    "anomalies": "Out-of-state packet (ej: ACK sin SYN previo), secuencia TCP inválida (spoofing/ataque), window size anómalo.",
                    "packet_capture": {
                        "wireshark_display_filter": "tcp",
                        "tcpdump_filter": "tcp",
                        "notes": "Usar 'show conn' / 'show session all' para verificar estado esperado vs flags capturados."
                    }
                },
                {
                    "name": "Capa 3 - Red (IP/State Table)",
                    "detail": "Clave de state table: SrcIP, DstIP, SrcPort, DstPort, Protocol. Timeout de conexión configurado.",
                    "checks": "Entrada de estado existe para el flujo inverso (DstIP→SrcIP, DstPort→SrcPort).",
                    "anomalies": "Estado expirado (idle timeout), tabla de conexiones llena (connection limit alcanzado), NAT mismatch en state table.",
                    "packet_capture": {
                        "wireshark_display_filter": "ip.src == IP_origen && ip.dst == IP_interna && tcp.port == X",
                        "tcpdump_filter": "host IP_origen and host IP_interna and tcp port X",
                        "notes": "Correlacionar timestamps de captura con tiempos de expiración de la state table."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 4: Nueva conexión permitida - creación de estado",
            "device": "Firewall - Connection Tracker",
            "action": "Si el paquete inicia una nueva conexión (ej: TCP SYN) y la ACL lo permite, se crea una entrada en la state table.",
            "note": "La entrada de estado permite el tráfico de retorno sin re-evaluar la ACL contra el flujo inverso.",
            "layers": [
                {
                    "name": "Capa 4 - Transporte (TCP SYN)",
                    "detail": "TCP flag SYN=1, ACK=0. Initial sequence number (ISN) aleatorio. MSS opcional en options.",
                    "checks": "Paquete es realmente un SYN inicial (no SYN-ACK). La política de seguridad permite nuevas conexiones.",
                    "anomalies": "SYN flood (muchos SYN sin ACK), SYN con datos (no estándar), flags TCP inválidos.",
                    "packet_capture": {
                        "wireshark_display_filter": "tcp.flags.syn == 1 && tcp.flags.ack == 0",
                        "tcpdump_filter": "tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack == 0",
                        "notes": "Confirmar que el primer paquete de la nueva conexión es un SYN limpio."
                    }
                },
                {
                    "name": "Capa 3 - Red (IP/NAT/State)",
                    "detail": "Se crea entrada bidireccional en state table: original flow y expected reply flow. Posible PAT/NAT translation.",
                    "checks": "Entrada creada en 'show conn' / 'show session all'. Timeout de conexión configurado adecuadamente.",
                    "anomalies": "Fallo en creación de estado (memory exhausted), translation slot no disponible (NAT/PAT overflow), política de aplicación (inspección L7) bloquea el SYN.",
                    "packet_capture": {
                        "wireshark_display_filter": "ip.src == IP_origen && ip.dst == IP_interna",
                        "tcpdump_filter": "host IP_origen and host IP_interna",
                        "notes": "Verificar que el SYN es permitido y el firewall responde (o deja pasar) correctamente."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 5: Tráfico de retorno - match contra state table",
            "device": "Firewall - Interfaz inside→outside",
            "action": "El tráfico de respuesta desde inside hacia outside es permitido automáticamente porque hace match con la entrada de estado creada.",
            "note": "El tráfico de retorno no necesita una regla ACL explícita si la state table tiene una entrada válida.",
            "layers": [
                {
                    "name": "Capa 3 - Red (IPv4)",
                    "detail": "SrcIP=IP_interna, DstIP=IP_origen_externa. El firewall realiza reverse NAT si aplica.",
                    "checks": "El paquete de retorno hace match con la clave de estado esperada. NAT reverse translation exitoso.",
                    "anomalies": "No hay entrada de estado (tráfico de retorno bloqueado), NAT reverse fallido (IP/port mismatch), asimetría de routing (bypass de state table).",
                    "packet_capture": {
                        "wireshark_display_filter": "ip.src == IP_interna && ip.dst == IP_origen",
                        "tcpdump_filter": "host IP_interna and host IP_origen",
                        "notes": "Capturar en interfaz inside para verificar que el firewall permite el retorno."
                    }
                },
                {
                    "name": "Capa 4 - Transporte (TCP Return)",
                    "detail": "TCP flags SYN-ACK o ACK. SEQ/ACK numbers consistentes con el estado creado durante el SYN.",
                    "checks": "ACK number del paquete de retorno coincide con el SEQ esperado. Flags válidos para el estado.",
                    "anomalies": "Out-of-window packet, RST inesperado (conexión abortada), retransmisión excesiva (pérdida de paquetes).",
                    "packet_capture": {
                        "wireshark_display_filter": "tcp",
                        "tcpdump_filter": "tcp",
                        "notes": "Seguir el stream TCP en Wireshark para verificar consistencia de SEQ/ACK."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 6: Paquete denegado - drop y log",
            "device": "Firewall - Motor de políticas",
            "action": "Si la ACL deniega el paquete o no hay match en state table para tráfico de retorno, el firewall descarta el paquete y opcionalmente genera un log.",
            "note": "Los paquetes descartados por deny ACL no generan estado. El logging puede ser rate-limited.",
            "layers": [
                {
                    "name": "Capa 3 - Red (IPv4)",
                    "detail": "Paquete IP coincidente con regla deny de ACL o sin entrada en state table.",
                    "checks": "Contadores de ACL incrementándose ('show access-list'). Logs de firewall mostrando drop. Syslog con evento de denegación.",
                    "anomalies": "Drop silencioso sin log (dificulta troubleshooting), contadores ACL no incrementan (descarte por otro motivo), flood de logs.",
                    "packet_capture": {
                        "wireshark_display_filter": "ip.src == IP_origen && ip.dst == IP_interna",
                        "tcpdump_filter": "host IP_origen and host IP_interna",
                        "notes": "Capturar en inside y outside para confirmar que el paquete no atraviesa el firewall."
                    }
                },
                {
                    "name": "Capa 2 - Enlace de Datos (Silencio)",
                    "detail": "No hay trama Ethernet de salida. El paquete se descarta internamente.",
                    "checks": "No se observa tráfico en interfaz opuesta. Contadores de input errors/drops incrementan.",
                    "anomalies": "Paquete reenviado a pesar de deny (bug o ACL mal aplicada), loop interno.",
                    "packet_capture": {
                        "wireshark_display_filter": "ip.src == IP_origen && ip.dst == IP_interna",
                        "tcpdump_filter": "host IP_origen and host IP_interna",
                        "notes": "Capturar simultáneamente en ambas interfaces del firewall para confirmar el drop."
                    }
                }
            ]
        }
    ]
}
        ]
    },
    'switch_l2': {
        'scenarios': [
{
    "id": "switch_l2_access_trunk_forwarding",
    "name": "Switch L2 - Forwarding Access/Trunk/VTP y CAM table",
    "description": "Recorrido de una trama Ethernet en una red conmutada L2. Desde que un host envía una trama untagged por un puerto access, pasando por el aprendizaje MAC, el lookup en la CAM table, el tagging 802.1Q en trunk, hasta la entrega untagged en el puerto access destino.",
    "steps": [
        {
            "step_title": "Paso 1: Host envía trama untagged a puerto access",
            "device": "Host - NIC Ethernet",
            "action": "El host origen genera una trama Ethernet estándar sin tag VLAN y la transmite por su interfaz de red.",
            "note": "Los hosts finales típicamente no son VLAN-aware (excepto en configuraciones especiales) y envían tramas untagged.",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (Ethernet untagged)",
                    "detail": "DstMAC=MAC_destino, SrcMAC=MAC_host_origen, EtherType=0x0800 (IPv4), sin 802.1Q tag. FCS válido.",
                    "checks": "Trama bien formada. MAC origen válida. Tamaño entre 64 y 1518 bytes.",
                    "anomalies": "Runt frame (<64 bytes), giant frame (>MTU), MAC origen aleatoria/inválida, FCS incorrecto.",
                    "packet_capture": {
                        "wireshark_display_filter": "eth.src == MAC_host && not vlan",
                        "tcpdump_filter": "ether host MAC_host and not vlan",
                        "notes": "Capturar en el puerto del host para confirmar trama untagged."
                    }
                },
                {
                    "name": "Capa 1 - Física (Cableado)",
                    "detail": "Señal eléctrica/óptica sobre par trenzado o fibra. Codificación Ethernet (ej: 1000BASE-T, 10GBASE-SR).",
                    "checks": "LED de enlace encendido. Negociación auto speed/duplex correcta. Sin errores físicos.",
                    "anomalies": "Cable dañado, par trenzado no cruzado donde se necesita, velocidad/duplex mismatch (auto-negociación fallida).",
                    "packet_capture": {
                        "wireshark_display_filter": "No aplicable",
                        "tcpdump_filter": "No aplicable",
                        "notes": "Verificar LEDs, 'show interface status', contadores de errores físicos."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 2: Switch añade VLAN tag (access VLAN)",
            "device": "Switch - Puerto access",
            "action": "El switch recibe la trama untagged en un puerto access y le asigna internamente el VLAN ID configurado en ese puerto.",
            "note": "Internamente el switch trabaja siempre con tramas tagged (excepto en VLAN nativa de trunk).",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (Ethernet 802.1Q tagged)",
                    "detail": "Se añade tag 802.1Q: TPID=0x8100, PCP=0, DEI=0, VLAN ID=access_vlan (ej: 10). EtherType original se mueve después del tag.",
                    "checks": "Puerto access configurado en la VLAN correcta. VLAN existe en la base de datos del switch.",
                    "anomalies": "Puerto access en VLAN incorrecta (aislamiento), VLAN no creada en el switch (descarte), dot1q-tunnel (QinQ) agrega tag adicional no deseado.",
                    "packet_capture": {
                        "wireshark_display_filter": "vlan.id == 10",
                        "tcpdump_filter": "vlan 10",
                        "notes": "En switch manageable, usar SPAN/RSPAN en puerto trunk para ver la trama tagged."
                    }
                },
                {
                    "name": "Capa 2 - Control (Spanning Tree)",
                    "detail": "El puerto access debe estar en estado forwarding para pasar tráfico de usuario.",
                    "checks": "STP/RSTP estado forwarding en el puerto. Sin bloqueo por loop protection o BPDU guard.",
                    "anomalies": "Puerto en blocking/listening/learning (no forwarding), BPDU Guard err-disabled, Root Guard bloqueando.",
                    "packet_capture": {
                        "wireshark_display_filter": "stp",
                        "tcpdump_filter": "stp",
                        "notes": "Verificar estado STP con 'show spanning-tree' más que captura de usuario."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 3: MAC learning - registro de source MAC en CAM",
            "device": "Switch - Motor de bridging",
            "action": "El switch lee la MAC origen de la trama y la registra en la CAM/MAC address table asociada a la VLAN y puerto de ingreso.",
            "note": "El learning es fundamental para el forwarding unicast posterior. Sin learning, todo el tráfico unicast sería flood.",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (MAC Learning)",
                    "detail": "Entrada CAM: MAC_src=VLAN:Puerto. Timeout de aging típico 300 segundos.",
                    "checks": "CAM table tiene entrada para MAC_origen en VLAN correcta y puerto de ingreso. Tabla CAM no llena.",
                    "anomalies": "MAC flapping (entrada cambia de puerto repetidamente), CAM table llena (flood de todo el tráfico), MAC aging muy corto (relearning constante).",
                    "packet_capture": {
                        "wireshark_display_filter": "eth.src == MAC_host",
                        "tcpdump_filter": "ether host MAC_host",
                        "notes": "Verificar con 'show mac address-table' que la MAC fue aprendida correctamente."
                    }
                },
                {
                    "name": "Capa 2 - Seguridad (Port Security)",
                    "detail": "Opcional: port security puede limitar MACs permitidas por puerto.",
                    "checks": "Port security no en violación. Número de MACs aprendidas dentro del límite. Sticky MAC configurado si aplica.",
                    "anomalies": "Port security violation (shutdown/restrict/protect), MAC de host no permitida (descarte).",
                    "packet_capture": {
                        "wireshark_display_filter": "eth.src == MAC_host",
                        "tcpdump_filter": "ether host MAC_host",
                        "notes": "Si port security está en shutdown, la interfaz pasará a err-disabled."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 4: Lookup de destino MAC en CAM o flooding",
            "device": "Switch - Motor de bridging",
            "action": "El switch busca la MAC destino en la CAM table. Si la encuentra, reenvía unicast por el puerto asociado. Si no, hace flooding en todos los puertos de la VLAN.",
            "note": "El flooding se limita a los puertos que pertenecen a la misma VLAN (o trunks que la permiten).",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (CAM Lookup)",
                    "detail": "Consulta CAM table por (MAC_dst, VLAN_ID). Si hit: forwarding por puerto específico. Si miss: broadcast/flood.",
                    "checks": "CAM table tiene entrada para MAC destino. Si no, el flooding debe llegar al puerto destino.",
                    "anomalies": "MAC destino aprendida en puerto equivocado (loop o asimetría), CAM miss persistente (host destino no responde), asymmetric routing en L3 switch.",
                    "packet_capture": {
                        "wireshark_display_filter": "eth.dst == MAC_destino",
                        "tcpdump_filter": "ether host MAC_destino",
                        "notes": "Verificar 'show mac address-table' para confirmar puerto de salida esperado."
                    }
                },
                {
                    "name": "Capa 2 - Control (VTP/VLAN Database)",
                    "detail": "La VLAN debe existir en la base de datos del switch (VTP domain consistente si se usa VTP).",
                    "checks": "VLAN presente en 'show vlan'. Si VTP: modo correcto (server/client/transparent), dominio coincidente, revision number coherente.",
                    "anomalies": "VLAN pruning en trunk (VLAN no propagada), VTP domain mismatch (no aprende VLANs), VTP transparent con VLAN faltante localmente.",
                    "packet_capture": {
                        "wireshark_display_filter": "vtp",
                        "tcpdump_filter": "vlan",
                        "notes": "VTP es tráfico de control; capturar en trunk si se sospecha problema de propagación de VLAN."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 5: Forwarding por trunk con tag 802.1Q",
            "device": "Switch - Puerto trunk",
            "action": "La trama tagged se reenvía por el puerto trunk hacia el siguiente switch, preservando el VLAN ID en el tag 802.1Q.",
            "note": "Solo las VLANs permitidas en el trunk ('switchport trunk allowed vlan') serán reenviadas.",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (Trunk 802.1Q)",
                    "detail": "Trama Ethernet con tag 802.1Q: TPID=0x8100, VLAN=10. DstMAC=MAC_destino, SrcMAC=MAC_switch_local. FCS recalculado.",
                    "checks": "Trunk permite VLAN 10 en allowed list. Native VLAN correctamente manejada (sin tag para native si no se usa dot1q native tagging).",
                    "anomalies": "VLAN not allowed en trunk (descarte silencioso), native VLAN mismatch (VLAN leaking), DTP negotiation fallida (trunk no formado).",
                    "packet_capture": {
                        "wireshark_display_filter": "vlan.id == 10",
                        "tcpdump_filter": "vlan 10",
                        "notes": "Capturar en el trunk para confirmar que la trama sale con tag correcto."
                    }
                },
                {
                    "name": "Capa 1 - Física (Enlace trunk)",
                    "detail": "Señal física sobre el enlace trunk. Velocidad/duplex negociado.",
                    "checks": "Enlace trunk Up/Up. Velocidad suficiente para la suma de tráfico de todas las VLANs.",
                    "anomalies": "Enlace trunk saturado (congestión), errores físicos en trunk (CRC, runts, giants).",
                    "packet_capture": {
                        "wireshark_display_filter": "No aplicable",
                        "tcpdump_filter": "No aplicable",
                        "notes": "Revisar contadores de interfaz y utilización de bandwidth."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 6: Switch receptor quita tag en puerto access de salida",
            "device": "Switch destino - Puerto access",
            "action": "El switch destino recibe la trama tagged por el trunk, consulta CAM, y la entrega untagged por el puerto access del host destino.",
            "note": "El host destino recibe una trama Ethernet estándar sin tag, como si estuviera conectado a una red flat.",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (Ethernet untagged egress)",
                    "detail": "El tag 802.1Q se elimina antes de la transmisión por el puerto access. Trama resultante: DstMAC=MAC_destino, SrcMAC=MAC_switch_egress, EtherType=0x0800, sin tag.",
                    "checks": "Puerto de salida es access en VLAN 10. CAM table indica MAC destino en ese puerto.",
                    "anomalies": "Puerto configurado como trunk en lugar de access (envía tag al host), VLAN ID incorrecto en puerto de salida, output drops por buffer exhaustion.",
                    "packet_capture": {
                        "wireshark_display_filter": "eth.dst == MAC_destino && not vlan",
                        "tcpdump_filter": "ether host MAC_destino and not vlan",
                        "notes": "Capturar en puerto del host destino para confirmar trama untagged."
                    }
                },
                {
                    "name": "Capa 2 - Control (QoS/CoS)",
                    "detail": "El campo PCP (3 bits) del tag 802.1Q puede ser usado para QoS si el switch mapea CoS a colas de salida.",
                    "checks": "Mapeo CoS→queue correcto. Sin descartes por policing/shaping en puerto de salida.",
                    "anomalies": "CoS no mapeado (tráfico crítico en cola best-effort), buffer overflow en egress, microbursts.",
                    "packet_capture": {
                        "wireshark_display_filter": "vlan.id == 10",
                        "tcpdump_filter": "vlan 10",
                        "notes": "Verificar campo PCP en el tag 802.1Q antes de que se strippee en el puerto access."
                    }
                }
            ]
        }
    ]
}
        ]
    },
    'vrrp_hsrp': {
        'scenarios': [
{
    "id": "vrrp_hsrp_gateway_redundancy",
    "name": "VRRP / HSRP - Gateway redundancy y failover",
    "description": "Simulación del protocolo de redundancia de gateway VRRP/HSRP entre dos routers, incluyendo la elección de Master/Backup, la respuesta ARP a hosts, el forwarding de tráfico, el failover por falla del Master y el envío de Gratuitous ARP para actualizar las tablas MAC de los switches.",
    "steps": [
        {
            "step_title": "Paso 1: Routers A y B envían anuncios VRRP/HSRP",
            "device": "Router A / Router B - Interfaz LAN",
            "action": "Ambos routers envían periódicamente mensajes de advertisement para anunciar su prioridad y estado.",
            "note": "VRRP usa IP multicast 224.0.0.18 (protocolo 112). HSRP usa multicast 224.0.0.2 (UDP puerto 1985 v1) o 224.0.0.102 (v2).",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (Ethernet)",
                    "detail": "VRRP: DstMAC=01-00-5E-00-00-12 (multicast 224.0.0.18), SrcMAC=MAC_router. HSRP: DstMAC=01-00-5E-00-00-02 (v1) o 01-00-5E-00-00-66 (v2).",
                    "checks": "Tramas multicast enviadas periódicamente (VRRP: 1 seg por defecto, HSRP: 3 seg). Switches permiten flooding de multicast de control.",
                    "anomalies": "Tramas no enviadas (proceso detenido), multicast bloqueado en switches (IGMP snooping agresivo), MAC conflict.",
                    "packet_capture": {
                        "wireshark_display_filter": "vrrp || hsrp",
                        "tcpdump_filter": "ip multicast and (proto 112 or udp port 1985)",
                        "notes": "Filtrar por VRRP o HSRP según el protocolo configurado."
                    }
                },
                {
                    "name": "Capa 3 - Red (VRRP/HSRP)",
                    "detail": "VRRP: SrcIP=IP_real_router, DstIP=224.0.0.18, Protocol=112, Advertisement con Priority, Virtual Router ID, Auth. HSRP: Grupo, Priority, Virtual IP, State.",
                    "checks": "Prioridad anunciada coincide con configuración. Virtual Router ID / Grupo consistente. Autenticación coincide (si está configurada).",
                    "anomalies": "Virtual Router ID mismatch (grupos diferentes no ven anuncios), auth mismatch (descarte de anuncios), versión HSRP incompatible (v1 vs v2).",
                    "packet_capture": {
                        "wireshark_display_filter": "vrrp || hsrp",
                        "tcpdump_filter": "ip multicast and (proto 112 or udp port 1985)",
                        "notes": "Expandir el protocolo en Wireshark para verificar priority, VIP y group number."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 2: Router A gana la elección (prioridad o IP owner)",
            "device": "Router A / Router B - Control Plane",
            "action": "Se comparan las prioridades anunciadas. Si son iguales, gana el router con la IP real más alta (VRRP) o la MAC más alta (HSRP). Si un router es IP owner (IP real = VIP), su prioridad es 255 en VRRP.",
            "note": "En VRRP, 'ip address x.x.x.x/24' donde x.x.x.x es la VIP hace que ese router sea owner con priority 255 automáticamente.",
            "layers": [
                {
                    "name": "Capa 3 - Red (VRRP/HSRP Priority)",
                    "detail": "VRRP Priority: 1-255. HSRP Priority: 0-255. Comparación: mayor prioridad gana. Empate → desempate por IP/MAC.",
                    "checks": "Router A tiene prioridad más alta o es IP owner. Ambos routers están en el mismo grupo/VLAN.",
                    "anomalies": "Priority mal configurada (router esperado pierde), preempt no habilitado (router de mayor priority no toma control), version mismatch.",
                    "packet_capture": {
                        "wireshark_display_filter": "vrrp || hsrp",
                        "tcpdump_filter": "ip multicast and (proto 112 or udp port 1985)",
                        "notes": "Comparar los campos de priority en las capturas de ambos routers."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 3: Router A asume rol Master, Router B Backup",
            "device": "Router A (Master) / Router B (Backup)",
            "action": "Router A pasa a estado Master, asume la Virtual MAC y responde ARP/ND para la Virtual IP. Router B pasa a Backup y deja de responder.",
            "note": "VRRP Virtual MAC: 00-00-5E-00-01-VRID. HSRP v1 Virtual MAC: 00-00-0C-07-AC-Grupo. HSRP v2: 00-00-0C-9F-FX-XX.",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (Virtual MAC)",
                    "detail": "Master responde ARP con Virtual MAC. Switches aprenden la Virtual MAC en el puerto del Master.",
                    "checks": "Virtual MAC correcta para el grupo. Solo el Master responde ARP/ND para la VIP. Backup no responde.",
                    "anomalies": "Split brain (ambos creen ser Master por aislamiento de anuncios), virtual MAC conflict, ambos responden ARP (flapping).",
                    "packet_capture": {
                        "wireshark_display_filter": "arp || vrrp || hsrp",
                        "tcpdump_filter": "arp or ip multicast and (proto 112 or udp port 1985)",
                        "notes": "Verificar que solo el Master envía ARP replies con la Virtual MAC."
                    }
                },
                {
                    "name": "Capa 3 - Red (IP/Virtual IP)",
                    "detail": "Master responde pings/ARPs dirigidos a la Virtual IP. Backup monitorea anuncios del Master.",
                    "checks": "Master responde a tráfico destinado a VIP. Backup recibe anuncios del Master (hold time no expira).",
                    "anomalies": "Master no responde ARP (VIP no configurada), Backup no recibe anuncios (aislamiento L2/L3), gratuitous ARP no enviado.",
                    "packet_capture": {
                        "wireshark_display_filter": "arp || vrrp || hsrp",
                        "tcpdump_filter": "arp or ip multicast and (proto 112 or udp port 1985)",
                        "notes": "Monitorear ARP replies y anuncios periódicos del Master."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 4: Host solicita ARP para gateway IP y aprende MAC virtual",
            "device": "Host - Stack IP",
            "action": "El host envía un ARP request broadcast para resolver la IP del gateway (VIP). El Master responde con la Virtual MAC.",
            "note": "Todos los hosts de la VLAN deben apuntar su default gateway a la Virtual IP, no a las IPs reales de los routers.",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (ARP)",
                    "detail": "ARP Request: DstMAC=FF:FF:FF:FF:FF:FF, SrcMAC=MAC_host, ARP opcode=1 (request), Target IP=VIP. ARP Reply: DstMAC=MAC_host, SrcMAC=Virtual_MAC, opcode=2.",
                    "checks": "Host recibe ARP reply con la Virtual MAC. La entrada ARP del host apunta a Virtual MAC.",
                    "anomalies": "ARP reply con MAC real del router (configuración incorrecta), ARP poisoning/spoofing, no reply (Master caído).",
                    "packet_capture": {
                        "wireshark_display_filter": "arp",
                        "tcpdump_filter": "arp",
                        "notes": "Filtrar ARP para ver el request del host y el reply del Master con Virtual MAC."
                    }
                },
                {
                    "name": "Capa 3 - Red (IP/Gateway)",
                    "detail": "Host configura default gateway = VIP. Todo el tráfico off-net se envía a la Virtual MAC.",
                    "checks": "Configuración IP del host correcta. Default gateway = VIP. Máscara de red correcta.",
                    "anomalies": "Host con gateway estático apuntando a IP real (falla ante failover), VIP en subnet diferente (routing issue).",
                    "packet_capture": {
                        "wireshark_display_filter": "arp",
                        "tcpdump_filter": "arp",
                        "notes": "Verificar configuración de red del host además de la captura ARP."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 5: Tráfico reenviado vía Master",
            "device": "Router A (Master)",
            "action": "El Master recibe las tramas destinadas a la Virtual MAC, las desencapsula y las rutea/reenvía hacia el destino final.",
            "note": "El Master funciona como gateway activo. El Backup no procesa tráfico de datos (solo escucha anuncios).",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (Ethernet)",
                    "detail": "Tramas entrantes con DstMAC=Virtual_MAC. El switch de acceso las entrega al puerto del Master.",
                    "checks": "CAM table del switch apunta Virtual MAC al puerto del Master. Tráfico fluye solo por Master.",
                    "anomalies": "Virtual MAC aprendida en puerto del Backup (ambos activos), flapping de Virtual MAC entre puertos.",
                    "packet_capture": {
                        "wireshark_display_filter": "eth.dst == Virtual_MAC",
                        "tcpdump_filter": "ether host Virtual_MAC",
                        "notes": "Capturar en interfaz LAN del Master para verificar que recibe tráfico destinado a Virtual MAC."
                    }
                },
                {
                    "name": "Capa 3 - Red (IPv4)",
                    "detail": "Master realiza routing lookup en RIB/FIB y reenvía el paquete hacia la red destino (WAN/Internet).",
                    "checks": "Master tiene ruta hacia destino. NAT/PAT configurado si aplica. Interfaz WAN Up/Up.",
                    "anomalies": "Ruta faltante en Master, NAT pool agotado, interfaz WAN caída (aunque LAN está up).",
                    "packet_capture": {
                        "wireshark_display_filter": "ip.src == IP_host && ip.dst == IP_destino",
                        "tcpdump_filter": "host IP_host and host IP_destino",
                        "notes": "Capturar en WAN del Master para confirmar forwarding exitoso."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 6: Falla del Master - Backup toma el control",
            "device": "Router B (Backup → Master)",
            "action": "El Backup deja de recibir anuncios del Master (hold time expira). Asume el rol de Master y comienza a responder ARP/ND para la VIP.",
            "note": "VRRP hold time = 3x advertisement interval (default 3.6 seg con track). HSRP hold time = 3x hello (default 10 seg).",
            "layers": [
                {
                    "name": "Capa 3 - Red (VRRP/HSRP Timeout)",
                    "detail": "Backup espera hold time. Si no recibe anuncios, transiciona a Master y envía sus propios anuncios.",
                    "checks": "Backup tiene hold time configurado correctamente. No hay aislamiento que impida ver anuncios pero sí forwarding.",
                    "anomalies": "Hold time muy largo (failover lento), preempt no configurado (Backup no retoma cuando Master vuelve), track interface no funciona (Master sigue enviando anuncios aunque WAN caída).",
                    "packet_capture": {
                        "wireshark_display_filter": "vrrp || hsrp",
                        "tcpdump_filter": "ip multicast and (proto 112 or udp port 1985)",
                        "notes": "Verificar ausencia de anuncios del Master durante el hold time, seguido de anuncios del nuevo Master."
                    }
                },
                {
                    "name": "Capa 2 - Enlace de Datos (Failover L2)",
                    "detail": "El nuevo Master comienza a usar la Virtual MAC en su interfaz. Los switches deben actualizar la ubicación de la Virtual MAC.",
                    "checks": "Virtual MAC ahora responde desde puerto del Backup. Tráfico redirigido al nuevo Master.",
                    "anomalies": "Virtual MAC aún apuntando a puerto del Master caído (CAM aging no expiró), loop temporal durante failover.",
                    "packet_capture": {
                        "wireshark_display_filter": "vrrp || hsrp || arp",
                        "tcpdump_filter": "ip multicast and (proto 112 or udp port 1985) or arp",
                        "notes": "Capturar en LAN para observar la transición de anuncios y ARP."
                    }
                }
            ]
        },
        {
            "step_title": "Paso 7: Gratuitous ARP enviado para actualizar switches",
            "device": "Router B (nuevo Master)",
            "action": "El nuevo Master envía un Gratuitous ARP broadcast para forzar a los switches a actualizar la CAM table y apuntar la Virtual MAC a su puerto.",
            "note": "El GARP acelera la convergencia L2 evitando esperar al CAM aging (300 seg por defecto).",
            "layers": [
                {
                    "name": "Capa 2 - Enlace de Datos (ARP Gratuito)",
                    "detail": "GARP: DstMAC=FF:FF:FF:FF:FF:FF, SrcMAC=Virtual_MAC, ARP opcode=1 o 2, Sender IP=VIP, Target IP=VIP, Sender MAC=Virtual_MAC.",
                    "checks": "GARP enviado inmediatamente tras transición a Master. Todos los switches de la LAN reciben el broadcast.",
                    "anomalies": "GARP no enviado (convergencia lenta o blackhole), GARP bloqueado por switch (DHCP snooping/DAI), broadcast storm.",
                    "packet_capture": {
                        "wireshark_display_filter": "arp.isgratuitous",
                        "tcpdump_filter": "arp",
                        "notes": "En Wireshark usar display filter 'arp.isgratuitous'. Verificar Sender IP = Target IP = VIP."
                    }
                },
                {
                    "name": "Capa 3 - Red (IP/Convergencia)",
                    "detail": "Hosts no necesitan cambiar su ARP table porque la VIP→Virtual MAC sigue siendo válida. Solo la ubicación física (puerto) cambia.",
                    "checks": "Host mantiene ARP entry para VIP→Virtual_MAC. No se requiere re-ARP en hosts.",
                    "anomalies": "Host con ARP estática a MAC real (fallará), Virtual MAC diferente entre Master/Backup (HSRP mal configurado), proxy ARP interferente.",
                    "packet_capture": {
                        "wireshark_display_filter": "arp.isgratuitous",
                        "tcpdump_filter": "arp",
                        "notes": "Verificar en host que su caché ARP no cambia (solo debe actualizarse el puerto del switch)."
                    }
                }
            ]
        }
    ]
}
        ]
    },
    'rstp': {
        'scenarios': [
            {
                "id": "rstp_bpdu_election",
                "name": "Spanning Tree (RSTP) - Elección de root bridge y BPDU",
                "description": "Recorrido del intercambio de BPDUs RSTP entre dos switches, comparación de Bridge ID, elección de root bridge, designación de puertos root/designated, notificación de cambio de topología (TCN) y transición rápida mediante proposal/agreement.",
                "steps": [
                    {
                        "step_title": "Paso 1: Switch A envía BPDU claim de root (prioridad 4096)",
                        "device": "Switch A",
                        "action": "Switch A inicia el envío periódico de BPDUs RSTP anunciándose como root bridge con prioridad 4096.",
                        "note": "Al iniciar, cada switch se considera root. Switch A tiene prioridad 4096 (0x1000), muy inferior al default 32768, por lo que tiene alta probabilidad de ganar la elección.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "DstMAC=01:80:C2:00:00:00 (STP Multicast), SrcMAC=MAC_SwitchA, EtherType=0x8100 (si hay VLAN) o LLC/SNAP. En RSTP, los BPDUs se envían a la dirección de grupo IEEE 802.1D.",
                                "checks": "Verificar que la interfaz está en estado forwarding y no filtra BPDUs. Comprobar que la dirección MAC destino es 01:80:C2:00:00:00.",
                                "anomalies": "BPDU Filter habilitado (no envía BPDU), BPDU Guard bloqueando el puerto, dirección MAC destino incorrecta, VLAN tag faltante en entorno 802.1Q.",
                                "packet_capture": {
                                    "wireshark_display_filter": "stp",
                                    "tcpdump_filter": "stp",
                                    "notes": "Capturar en la interfaz del switch conectada al enlace trunk. En Wireshark filtrar 'stp' para ver BPDUs."
                                }
                            },
                            {
                                "name": "Capa 2 - Spanning Tree (RSTP BPDU)",
                                "detail": "Protocol Identifier=0x0000, Protocol Version Identifier=2 (RSTP), BPDU Type=0x02 (RST/MST). Flags: Topology Change=0, Proposal=1, Port Role=01 (Designated), Learning=0, Forwarding=0, Agreement=0. Root Identifier: Priority=4096, MAC=MAC_SwitchA. Bridge Identifier: Priority=4096, MAC=MAC_SwitchA. Port Identifier: Priority=128, Port=1. Message Age=0, Max Age=20, Hello Time=2, Forward Delay=15.",
                                "checks": "Verificar Protocol Version ID=2 (RSTP). Root ID == Bridge ID (indica que se considera root). Flags Proposal=1 indica que inicia el handshake rápido. Message Age=0 (es el originador).",
                                "anomalies": "Protocol Version=0 (STP legacy), Root ID != Bridge ID (ya recibió un BPDU mejor), Flags incorrectos, Proposal=0 (no usará transición rápida).",
                                "packet_capture": {
                                    "wireshark_display_filter": "stp.flags.proposal == 1 && stp.root.id == stp.bridge.id",
                                    "tcpdump_filter": "stp",
                                    "notes": "En Wireshark expandir 'Spanning Tree Protocol' para ver flags, root ID y bridge ID. Confirmar Proposal=1."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 2: Switch B recibe BPDU y compara Bridge ID",
                        "device": "Switch B",
                        "action": "Switch B recibe el BPDU de Switch A, extrae Root Identifier y compara con su propio Bridge ID (default 32768).",
                        "note": "La comparación de Bridge ID usa primero la prioridad (menor es mejor) y luego la MAC. Switch A con 4096 gana sobre 32768.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "DstMAC=01:80:C2:00:00:00, SrcMAC=MAC_SwitchA, EtherType=0x8100 (opcional VLAN 1). La trama llega por el puerto conectado a Switch A.",
                                "checks": "Interfaz Up/Up. STP habilitado en la VLAN. No hay ACL ni storm-control bloqueando BPDUs multicast.",
                                "anomalies": "Interfaz en err-disabled (BPDU Guard), port-security bloqueando tráfico, storm-control descartando multicast, VLAN no permitida en trunk.",
                                "packet_capture": {
                                    "wireshark_display_filter": "stp && eth.src == MAC_SwitchA",
                                    "tcpdump_filter": "ether host 01:80:c2:00:00:00 and stp",
                                    "notes": "Capturar en el puerto de recepción de Switch B. Verificar que la MAC origen es Switch A."
                                }
                            },
                            {
                                "name": "Capa 2 - Spanning Tree (RSTP BPDU)",
                                "detail": "Switch B extrae: Root Priority=4096, Root MAC=MAC_SwitchA. Compara con su propio Bridge ID: Priority=32768, MAC=MAC_SwitchB. Como 4096 < 32768, Switch B acepta a Switch A como root. Calcula Root Path Cost: costo del enlace (ej: Gigabit=20000 en RSTP/802.1t, o 4 en 802.1D-1998) + 0 (Message Age=0).",
                                "checks": "Root ID recibido es mejor (menor) que el propio Bridge ID. El puerto por donde llega se marca como Root Port candidato.",
                                "anomalies": "Root ID recibido es peor (no acepta), BPDU corrupto (CRC invalidado ya en capa Ethernet), version mismatch que ignora el BPDU, path cost desactualizado por configuración manual.",
                                "packet_capture": {
                                    "wireshark_display_filter": "stp.root.prio < 32768",
                                    "tcpdump_filter": "stp",
                                    "notes": "En Wireshark verificar stp.root.prio menor a la prioridad default. Verificar consistencia de root MAC."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 3: Switch B reconoce a Switch A como root bridge",
                        "device": "Switch B",
                        "action": "Switch B actualiza su tabla STP: registra a Switch A como root, marca el puerto de recepción como Root Port, y comienza a reenviar BPDUs con Root ID de Switch A.",
                        "note": "Una vez elegido el root, todos los demás switches deben tener un único Root Port (el de menor costo hacia el root) y Designated Ports en cada segmento.",
                        "layers": [
                            {
                                "name": "Capa 2 - Spanning Tree (RSTP BPDU generado)",
                                "detail": "Protocol Version=2, BPDU Type=0x02. Flags: Topology Change=0, Proposal=0, Port Role=01 (Designated), Learning=0, Forwarding=0, Agreement=0. Root Identifier: Priority=4096, MAC=MAC_SwitchA. Bridge Identifier: Priority=32768, MAC=MAC_SwitchB. Port Identifier: según puerto de salida. Root Path Cost: costo acumulado desde Switch B hacia A (ej: 20000).",
                                "checks": "Root ID en BPDUs salientes es MAC_SwitchA (no el propio). Root Path Cost > 0. El puerto de salida se anuncia como Designated Port Role.",
                                "anomalies": "Root ID sigue siendo el propio (no aceptó el root ajeno), Root Path Cost=0 (loop potencial), Port Role=00 (Unknown) o 11 (Alternate/Backup) en lugar de Designated.",
                                "packet_capture": {
                                    "wireshark_display_filter": "stp && stp.root.id == MAC_SwitchA && stp.bridge.id == MAC_SwitchB",
                                    "tcpdump_filter": "stp",
                                    "notes": "Capturar BPDUs salientes de Switch B. Verificar que anuncia a Switch A como root y su propio Bridge ID."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 4: Elección de puertos Root y Designated",
                        "device": "Switch A y Switch B",
                        "action": "En el enlace punto a punto entre A y B, Switch A es Designated (mejor Bridge ID) y Switch B es Root Port. No hay Alternate/Backup en un enlace directo con solo dos switches.",
                        "note": "En cada segmento LAN, el puerto con menor Root Path Cost es Designated. Si hay empate, gana el menor Bridge ID, luego menor Port ID.",
                        "layers": [
                            {
                                "name": "Capa 2 - Spanning Tree (RSTP Estado de Puertos)",
                                "detail": "Switch A puerto hacia B: Designated Port, Role=Designated, State=Forwarding (rápido en RSTP). Switch B puerto hacia A: Root Port, Role=Root, State=Forwarding. BPDU enviado por A: Root Path Cost=0, Designated. BPDU enviado por B: Root Path Cost=20000, Designated en otros enlaces (si los tuviera).",
                                "checks": "En CLI: show spanning-tree vlan X. Verificar Root ID=Switch A. Root Port en Switch B es el puerto hacia A. Ambos puertos en estado forwarding.",
                                "anomalies": "Puerto en estado Blocking/Discarding (loop protection), Root Port en puerto incorrecto (costo mal configurado), Designated Port no establecido por empate en Bridge ID.",
                                "packet_capture": {
                                    "wireshark_display_filter": "stp.port.role == 0x01 && stp.root.id == MAC_SwitchA",
                                    "tcpdump_filter": "stp",
                                    "notes": "Verificar en Wireshark el campo Port Role (01=Designated). Ambos switches envían BPDUs, pero A tiene prioridad."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 5: Topology Change Notification (TCN)",
                        "device": "Switch B",
                        "action": "Si un puerto no-root de Switch B cambia a forwarding (ej: conexión de un host), Switch B activa la flag Topology Change (TC) en sus BPDUs salientes por el Root Port hacia el root.",
                        "note": "En RSTP, no hay TCN BPDU separado como en STP. Se usa la flag TC en los BPDUs normales. El root propaga esto con TC durante Hello+Forward Delay.",
                        "layers": [
                            {
                                "name": "Capa 2 - Spanning Tree (RSTP TCN)",
                                "detail": "BPDU enviado por Switch B hacia A: Flags: Topology Change=1, Proposal=0, Port Role=01 (Designated/Root según puerto), Agreement=0. Root ID sigue siendo Switch A. Bridge ID=Switch B. Este BPDU con TC=1 indica cambio de topología.",
                                "checks": "Flag TC=1 en BPDU saliente del switch que detectó el cambio. El root recibe esto y comienza a enviar BPDUs con TC=1 a todos los demás switches.",
                                "anomalies": "TC=1 persistiendo por mucho tiempo (flapping de puertos), TCN no propagado (puerto bloqueado), switches no reduciendo aging time de MAC table a 15 segundos.",
                                "packet_capture": {
                                    "wireshark_display_filter": "stp.flags.tc == 1",
                                    "tcpdump_filter": "stp",
                                    "notes": "Filtrar BPDUs con Topology Change flag activa. En Wireshark: stp.flags.tc == 1."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 6: Transición rápida RSTP (Proposal/Agreement)",
                        "device": "Switch A y Switch B",
                        "action": "Cuando un puerto punto a punto pasa a designado, Switch A envía BPDU con Proposal=1. Switch B bloquea todos sus puertos designados (sync), pone el puerto hacia A en forwarding, y responde con Agreement=1.",
                        "note": "El mecanismo Proposal/Agreement permite transicionar a forwarding en milisegundos en enlaces punto a punto, sin esperar Forward Delay (15s).",
                        "layers": [
                            {
                                "name": "Capa 2 - Spanning Tree (RSTP Proposal)",
                                "detail": "Switch A → B: BPDU Flags: Proposal=1, Port Role=01 (Designated), Learning=0, Forwarding=0, Agreement=0. Root ID=Switch A, Root Path Cost=0. Switch B recibe Proposal, verifica que es el mejor BPDU para ese puerto, inicia sync.",
                                "checks": "Proposal=1 en BPDU entrante. El puerto está en modo punto a punto (point-to-point) según duplex full. PortFast no debe estar en puertos conectados a switches.",
                                "anomalies": "Proposal ignorado porque el puerto no está en modo punto a punto (half-duplex), BPDU Guard err-disabled, Proposal/Agreement loop si hay un hub o puerto compartido.",
                                "packet_capture": {
                                    "wireshark_display_filter": "stp.flags.proposal == 1",
                                    "tcpdump_filter": "stp",
                                    "notes": "Capturar BPDUs con Proposal=1. Verificar que el puerto está en full-duplex para que RSTP use proposal/agreement."
                                }
                            },
                            {
                                "name": "Capa 2 - Spanning Tree (RSTP Agreement)",
                                "detail": "Switch B → A: BPDU Flags: Agreement=1, Port Role=10 (Root), Learning=0, Forwarding=1 (o transiciona inmediatamente). Root ID=Switch A, Bridge ID=Switch B. Al recibir Agreement, Switch A pone su puerto en forwarding inmediatamente.",
                                "checks": "Agreement=1 en BPDU de respuesta. Ambos puertos pasan a forwarding sin pasar por Listening/Learning de 30s. Verificar estado 'forwarding' en ambos extremos.",
                                "anomalies": "Agreement no recibido (timeout, BPDU drop), puerto queda en Learning/Listening, switch con version STP legacy que no entiende Agreement (ignora y usa timers legacy).",
                                "packet_capture": {
                                    "wireshark_display_filter": "stp.flags.agreement == 1",
                                    "tcpdump_filter": "stp",
                                    "notes": "Verificar BPDU de respuesta con Agreement=1. El tiempo entre Proposal y Agreement debe ser muy corto (<1s en redes estables)."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 7: Topología estable final",
                        "device": "Switch A (Root) y Switch B",
                        "action": "Ambos switches envían BPDUs periódicamente (Hello Time=2s) para mantener la topología. Switch A envía con Root Path Cost=0; Switch B reenvía con Root Path Cost actualizado.",
                        "note": "La topología permanece estable hasta que expire Max Age sin recibir BPDUs del root, o se detecte un cambio de puerto.",
                        "layers": [
                            {
                                "name": "Capa 2 - Spanning Tree (RSTP Estable)",
                                "detail": "BPDU periódico: Protocol Version=2, Type=0x02, Flags=0x3C (o similar según rol), Root ID=Switch A (4096+MAC), Bridge ID=origen, Hello Time=2s, Max Age=20s, Forward Delay=15s.",
                                "checks": "BPDUs recibidos cada 2 segundos en Root Port. Message Age no excede Max Age. Root ID consistente en todos los BPDUs.",
                                "anomalies": "BPDUs faltantes (cable desconectado, unidireccional), Message Age >= Max Age (root caído), Root ID cambia inesperadamente (rogue switch con menor prioridad), inconsistencia de VLAN (PVST+ mismatch).",
                                "packet_capture": {
                                    "wireshark_display_filter": "stp && frame.time_delta < 3",
                                    "tcpdump_filter": "stp",
                                    "notes": "Capturar BPDUs periódicos. Verificar intervalo de ~2 segundos. Usar Wireshark IO Graph para confirmar periodicidad estable."
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    'dhcp': {
        'scenarios': [
            {
                "id": "dhcp_dora_ipv4",
                "name": "DHCP - Proceso DORA IPv4 (Discover, Offer, Request, ACK)",
                "description": "Recorrido completo del proceso DORA DHCPv4 desde que un cliente solicita una dirección IP hasta que la configura y envía Gratuitous ARP. Incluye opciones DHCP, retransmisiones relay y validación de parámetros.",
                "steps": [
                    {
                        "step_title": "Paso 1: Cliente envía DHCP Discover (broadcast)",
                        "device": "Cliente DHCP",
                        "action": "El cliente sin IP envía un mensaje DHCP Discover como broadcast Ethernet y broadcast IP (255.255.255.255) al puerto UDP 67 del servidor.",
                        "note": "El cliente usa 0.0.0.0 como origen porque aún no tiene IP. El puerto origen UDP es 68 (cliente). Se incluye la opción 53 (Message Type=1 Discover) y opción 61 (Client Identifier) o  chaddr.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "DstMAC=FF:FF:FF:FF:FF:FF (broadcast), SrcMAC=MAC_Cliente, EtherType=0x0800 (IPv4). Si hay VLAN, puede llevar 802.1Q tag (ej: VLAN 100).",
                                "checks": "Interfaz del cliente Up/Up. Cable conectado. El switch permite broadcast en la VLAN de acceso. No hay port-security bloqueando la MAC del cliente.",
                                "anomalies": "Interfaz down, VLAN incorrecta en el puerto de acceso, storm-control descartando broadcasts, MAC filtering, cliente en VLAN diferente al servidor sin relay agent.",
                                "packet_capture": {
                                    "wireshark_display_filter": "dhcp.option.dhcp == 1",
                                    "tcpdump_filter": "udp port 67 and udp port 68",
                                    "notes": "Capturar en el puerto de acceso del cliente. En Wireshark filtrar por dhcp.option.dhcp == 1 (Discover)."
                                }
                            },
                            {
                                "name": "Capa 3 - Red (IPv4)",
                                "detail": "SrcIP=0.0.0.0, DstIP=255.255.255.255 (limited broadcast), TTL=128 (o 64 según OS), Protocol=UDP(17), IP Header Length=20 bytes, Total Length variable. Identification y Flags pueden variar.",
                                "checks": "SrcIP=0.0.0.0 válido para Discover. DstIP broadcast. No hay IP options que alteren el procesamiento. Checksum IP válido.",
                                "anomalies": "SrcIP != 0.0.0.0 (cliente ya tiene IP, no debería hacer Discover), DstIP unicast (incorrecto), TTL=0 o TTL=1 que sea descartado en primer router, IP checksum incorrecto.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.src == 0.0.0.0 and dhcp.option.dhcp == 1",
                                    "tcpdump_filter": "src host 0.0.0.0 and udp port 67",
                                    "notes": "Filtrar por origen 0.0.0.0 y puerto UDP 67. Verificar que es broadcast IP."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte (UDP)",
                                "detail": "SrcPort=68 (BOOTP Client), DstPort=67 (BOOTP Server). UDP Length incluye payload DHCP. UDP Checksum puede ser 0x0000 (optional IPv4) o calculado.",
                                "checks": "Puertos correctos (68→67). UDP checksum válido o 0x0000. Payload mínimo de 300 bytes (BOOTP fixed field=236 + options).",
                                "anomalies": "SrcPort/DstPort invertidos (67→68), firewall bloqueando UDP 67/68, UDP checksum incorrecto que algunos stacks descartan, payload menor a 236 bytes (malformado).",
                                "packet_capture": {
                                    "wireshark_display_filter": "udp.srcport == 68 and udp.dstport == 67 and dhcp.option.dhcp == 1",
                                    "tcpdump_filter": "udp src port 68 and udp dst port 67",
                                    "notes": "Verificar puertos UDP. El Discover debe ser 68→67."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (DHCP Discover)",
                                "detail": "BOOTP Fixed Fields: op=0x01 (request), htype=0x01 (Ethernet), hlen=0x06, hops=0, xid=0x12345678 (transaction ID), secs=0, flags=0x8000 (broadcast flag, opcional), ciaddr=0.0.0.0, yiaddr=0.0.0.0, siaddr=0.0.0.0, giaddr=0.0.0.0, chaddr=MAC_Cliente, sname y file vacíos. DHCP Options: 53=1 (Discover), 55 (Parameter Request List: 1,3,6,15,31,33,43,119), 61 (Client Identifier), 12 (Hostname), 60 (Vendor Class Identifier), 50 (Requested IP, si renueva). Magic Cookie=0x63825363.",
                                "checks": "xid consistente durante todo el flujo DORA. op=1 (request). chaddr coincide con MAC del cliente. Opción 53=1. Magic Cookie correcto.",
                                "anomalies": "xid cambia entre mensajes (no correlaciona Offer/ACK), op=2 (reply en lugar de request), Magic Cookie incorrecto (servidor ignora), opción 53 faltante, broadcast flag=0 cuando el cliente no puede recibir unicast pre-configuración.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bootp.option.dhcp == 1",
                                    "tcpdump_filter": "udp port 67 or udp port 68",
                                    "notes": "En Wireshark usar bootp.option.dhcp == 1. Expandir opciones para ver Parameter Request List (opt 55) y Client Identifier (opt 61)."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 2: Servidor recibe Discover y verifica pool",
                        "device": "Servidor DHCP",
                        "action": "El servidor recibe el Discover, verifica el xid, busca una IP disponible en el pool según la subnet del giaddr (o interfaz local), y valida reglas estáticas/reservas.",
                        "note": "Si el mensaje llega vía relay agent (giaddr != 0.0.0.0), el servidor usa giaddr para identificar el scope. Si giaddr=0, usa la subnet de la interfaz por donde llegó.",
                        "layers": [
                            {
                                "name": "Capa 3 - Red (IPv4)",
                                "detail": "SrcIP=0.0.0.0, DstIP=255.255.255.255. Si hay relay: giaddr=IP_Relay_Agent. El servidor procesa según giaddr o interfaz de recepción.",
                                "checks": "Servidor tiene scope configurado para la subnet identificada. Pool tiene IPs libres. No hay exclusión de la MAC del cliente en deny list.",
                                "anomalies": "Scope no configurado para la subnet, pool agotado (exhausted), IP reservada para otra MAC, regla de exclusion que bloquea al cliente, giaddr no coincide con ningún scope (relay mal configurado).",
                                "packet_capture": {
                                    "wireshark_display_filter": "dhcp.option.dhcp == 1",
                                    "tcpdump_filter": "udp port 67",
                                    "notes": "Verificar en el servidor que recibe Discover. Si hay relay, verificar giaddr en el paquete."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (DHCP Discover procesado)",
                                "detail": "Servidor extrae chaddr, Client Identifier (opt 61), hostname (opt 12). Busca reserva estática. Si no, selecciona IP libre del pool. Valida que no esté en uso (ping check opcional). Prepara Offer.",
                                "checks": "Log del servidor muestra Discover recibido. IP propuesta está dentro del rango. Lease time configurado. Opciones solicitadas en opt 55 están disponibles.",
                                "anomalies": "Log muestra 'no free leases', 'unknown client', 'DHCPDECLINE' previo que marcó la IP como conflictiva, ping check falla (IP ya en uso en red).",
                                "packet_capture": {
                                    "wireshark_display_filter": "dhcp.option.dhcp == 1",
                                    "tcpdump_filter": "udp port 67",
                                    "notes": "Analizar opciones del Discover. Verificar que el servidor tenga configuradas las opciones que el cliente solicita en opt 55."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 3: Servidor envía DHCP Offer con IP propuesta",
                        "device": "Servidor DHCP",
                        "action": "El servidor responde con DHCP Offer (broadcast si flags=0x8000, o unicast a chaddr/yiaddr si flags=0). Incluye la IP propuesta, máscara, gateway, DNS y lease time.",
                        "note": "Si el cliente envió Discover con broadcast flag=1, el servidor debe responder con broadcast. Si no, puede intentar unicast ARP-free al cliente (aunque muchos servidores siempre broadcast por simplicidad).",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "Si broadcast: DstMAC=FF:FF:FF:FF:FF:FF, SrcMAC=MAC_Servidor. Si unicast: DstMAC=MAC_Cliente (requiere que el servidor conozca la MAC del cliente, que sí la tiene por chaddr). EtherType=0x0800.",
                                "checks": "En broadcast: trama llega a todos los hosts de la VLAN. En unicast: switch tiene MAC del cliente en su tabla (o se envía por el mismo puerto de entrada si aún no expiró).",
                                "anomalies": "Servidor envía unicast pero el switch no tiene la MAC del cliente (drop por unknown unicast flooding o bloqueo), broadcast storm descarta Offer, VLAN del servidor diferente al cliente sin relay.",
                                "packet_capture": {
                                    "wireshark_display_filter": "dhcp.option.dhcp == 2",
                                    "tcpdump_filter": "udp port 68",
                                    "notes": "Capturar Offer. Si es broadcast, DstMAC es FF:FF:FF:FF:FF:FF. Si es unicast, DstMAC es la del cliente."
                                }
                            },
                            {
                                "name": "Capa 3 - Red (IPv4)",
                                "detail": "SrcIP=IP_Servidor_DHCP, DstIP=255.255.255.255 (broadcast) o DstIP=IP_Propuesta (unicast). TTL=128. Protocol=UDP.",
                                "checks": "SrcIP es la del servidor DHCP. DstIP coincide con el modo broadcast/unicast. Si hay relay, el servidor envía al giaddr, no al cliente directamente.",
                                "anomalies": "SrcIP incorrecto (servidor con múltiples interfaces), DstIP unicast pero el cliente no acepta unicast antes de configurar IP, firewall bloqueando respuesta del servidor.",
                                "packet_capture": {
                                    "wireshark_display_filter": "dhcp.option.dhcp == 2",
                                    "tcpdump_filter": "udp port 68",
                                    "notes": "Verificar SrcIP del servidor. En entornos relay, el servidor envía al giaddr y el relay reenvía al cliente."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte (UDP)",
                                "detail": "SrcPort=67, DstPort=68. UDP checksum calculado. Length según payload.",
                                "checks": "Puertos 67→68 correctos. UDP checksum válido.",
                                "anomalies": "Puertos invertidos, NAT modificando puertos (raro en broadcast), checksum incorrecto descartado por stack del cliente.",
                                "packet_capture": {
                                    "wireshark_display_filter": "udp.srcport == 67 and udp.dstport == 68 and dhcp.option.dhcp == 2",
                                    "tcpdump_filter": "udp src port 67 and udp dst port 68",
                                    "notes": "Verificar dirección UDP 67→68."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (DHCP Offer)",
                                "detail": "BOOTP: op=0x02 (reply), xid=mismo que Discover, yiaddr=IP_Propuesta (ej: 192.168.1.50), siaddr=IP_Servidor (opcional, para TFTP/boot), chaddr=MAC_Cliente. Options: 53=2 (Offer), 54=IP_Servidor (Server Identifier), 51=Lease Time (ej: 86400s), 1=Subnet Mask (ej: 255.255.255.0), 3=Router (Gateway), 6=DNS Servers, 15=Domain Name, 58=T1 (Renewal Time, 50%), 59=T2 (Rebinding Time, 87.5%).",
                                "checks": "xid coincide con Discover. yiaddr es una IP válida del scope. Opción 54 identifica al servidor. Opciones 1, 3, 6 presentes según solicitud del cliente.",
                                "anomalies": "xid diferente (cliente ignora Offer), yiaddr fuera del scope, opción 54 faltante (cliente no sabe a quién responder), lease time=0 (inválido), T1/T2 ausentes o incorrectos.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bootp.option.dhcp == 2",
                                    "tcpdump_filter": "udp port 68",
                                    "notes": "Expandir opciones DHCP en Wireshark. Verificar yiaddr, opción 54 (Server ID) y opción 51 (Lease Time)."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 4: Cliente envía DHCP Request",
                        "device": "Cliente DHCP",
                        "action": "El cliente recibe una o más Offers. Selecciona una (generalmente la primera) y envía DHCP Request como broadcast para informar a todos los servidores cuál aceptó.",
                        "note": "El Request es broadcast para que otros servidores cuyas Offers no fueron aceptadas liberen la IP reservada. Incluye opción 54 (Server Identifier del elegido) y opción 50 (Requested IP).",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "DstMAC=FF:FF:FF:FF:FF:FF, SrcMAC=MAC_Cliente. EtherType=0x0800. Broadcast en la VLAN de acceso.",
                                "checks": "Broadcast L2. El switch reenvía la trama por todos los puertos de la VLAN (excepto el de entrada).",
                                "anomalies": "Unicast L2 (incorrecto, aunque algunos clientes lo hacen post-configuración), puerto del cliente en VLAN diferente, storm-control descartando.",
                                "packet_capture": {
                                    "wireshark_display_filter": "dhcp.option.dhcp == 3",
                                    "tcpdump_filter": "udp port 67 and udp port 68",
                                    "notes": "Capturar Request. DstMAC debe ser broadcast."
                                }
                            },
                            {
                                "name": "Capa 3 - Red (IPv4)",
                                "detail": "SrcIP=0.0.0.0, DstIP=255.255.255.255. TTL=128. Protocol=UDP.",
                                "checks": "Origen 0.0.0.0 (aún no configura IP). Destino broadcast.",
                                "anomalies": "SrcIP ya configurado (renovación/rebinding, no inicial), DstIP unicast (solo en RENEWING cuando T1 expira y el cliente conoce al servidor).",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.src == 0.0.0.0 and dhcp.option.dhcp == 3",
                                    "tcpdump_filter": "src host 0.0.0.0 and udp port 67",
                                    "notes": "Filtrar Request con src 0.0.0.0."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (DHCP Request)",
                                "detail": "BOOTP: op=1, xid=mismo que Discover/Offer, ciaddr=0.0.0.0, chaddr=MAC_Cliente. Options: 53=3 (Request), 54=IP_Servidor_Elegido, 50=IP_Propuesta (Requested IP), 55=Parameter Request List (misma que Discover), 61=Client Identifier, 12=Hostname.",
                                "checks": "xid consistente. Opción 54 coincide con el servidor cuya Offer se aceptó. Opción 50 es la yiaddr recibida. Opción 53=3.",
                                "anomalies": "xid diferente, opción 54 faltante (servidor no sabe si fue elegido), opción 50 faltante (servidor no sabe qué IP asignar), múltiples Requests con diferentes xid (cliente confuso).",
                                "packet_capture": {
                                    "wireshark_display_filter": "bootp.option.dhcp == 3",
                                    "tcpdump_filter": "udp port 67 or udp port 68",
                                    "notes": "Verificar opciones 54 y 50. El Request debe identificar claramente al servidor y a la IP solicitada."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 5: Servidor envía DHCP ACK",
                        "device": "Servidor DHCP",
                        "action": "El servidor elegido recibe el Request, confirma que la IP sigue disponible, crea el binding (lease) y responde con DHCP ACK.",
                        "note": "El ACK contiene la misma información que la Offer pero con opción 53=5. Si la IP ya no está disponible, respondería con DHCP NAK (opción 53=6).",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "DstMAC=FF:FF:FF:FF:FF:FF (broadcast) o MAC_Cliente (unicast), SrcMAC=MAC_Servidor.",
                                "checks": "Broadcast si el cliente aún no configura IP. Unicast solo si el cliente ya tiene IP previa y está en renewing.",
                                "anomalies": "Servidor envía ACK a MAC incorrecta (confusión de binding), broadcast descartado por storm-control en algún switch intermedio.",
                                "packet_capture": {
                                    "wireshark_display_filter": "dhcp.option.dhcp == 5",
                                    "tcpdump_filter": "udp port 68",
                                    "notes": "Capturar ACK. Verificar que llega al cliente."
                                }
                            },
                            {
                                "name": "Capa 3 - Red (IPv4)",
                                "detail": "SrcIP=IP_Servidor, DstIP=255.255.255.255 o IP_Propuesta. TTL=128. Protocol=UDP.",
                                "checks": "SrcIP correcto del servidor. DstIP según modo broadcast/unicast.",
                                "anomalies": "DstIP=255.255.255.255 pero hay NAT entre servidor y cliente (raro en DHCP local), firewall bloqueando broadcast de retorno.",
                                "packet_capture": {
                                    "wireshark_display_filter": "dhcp.option.dhcp == 5",
                                    "tcpdump_filter": "udp port 68",
                                    "notes": "Verificar SrcIP del servidor. Confirmar que no es NAK (opt 53=6)."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (DHCP ACK)",
                                "detail": "BOOTP: op=2, xid=mismo, yiaddr=IP_Asignada, siaddr=IP_Servidor, chaddr=MAC_Cliente. Options: 53=5 (ACK), 54=IP_Servidor, 51=Lease Time, 1=Subnet Mask, 3=Router, 6=DNS, 15=Domain Name, 58=T1, 59=T2.",
                                "checks": "xid coincide. yiaddr = IP solicitada en Request. Opción 53=5 (no 6=NAK). Lease time > 0. Binding creado en servidor.",
                                "anomalies": "NAK (opt 53=6): IP ya no disponible, cliente en subnet incorrecta, lease time=0, opciones faltantes que el cliente necesita.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bootp.option.dhcp == 5",
                                    "tcpdump_filter": "udp port 68",
                                    "notes": "Confirmar ACK. Verificar yiaddr y lease time. Si aparece NAK, investigar logs del servidor."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 6: Cliente configura IP y envía Gratuitous ARP",
                        "device": "Cliente DHCP",
                        "action": "Tras recibir ACK, el cliente configura su interfaz con IP, máscara, gateway y DNS. Antes de usar la IP, envía un Gratuitous ARP Request para detectar conflictos (Duplicate Address Detection).",
                        "note": "Gratuitous ARP: ARP Request con SPA (Sender Protocol Address) = nueva IP, TPA (Target Protocol Address) = nueva IP. Tha=00:00:00:00:00:00. Es un broadcast L2 pero unicast-like L3.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "DstMAC=FF:FF:FF:FF:FF:FF, SrcMAC=MAC_Cliente, EtherType=0x0806 (ARP).",
                                "checks": "Broadcast L2. SrcMAC es la del cliente. EtherType 0x0806.",
                                "anomalies": "Interfaz del cliente no sube tras ACK (driver issue), ARP no enviado (DAD deshabilitado en el SO).",
                                "packet_capture": {
                                    "wireshark_display_filter": "arp.opcode == 1 and arp.src.proto_ipv4 == arp.dst.proto_ipv4",
                                    "tcpdump_filter": "arp",
                                    "notes": "Filtrar ARP Requests donde origen y destino IP son iguales (Gratuitous ARP)."
                                }
                            },
                            {
                                "name": "Capa 3 - Red (ARP)",
                                "detail": "Hardware Type=1 (Ethernet), Protocol Type=0x0800 (IPv4), HLEN=6, PLEN=4, Operation=1 (Request). Sender HA=MAC_Cliente, Sender PA=IP_Asignada. Target HA=00:00:00:00:00:00, Target PA=IP_Asignada.",
                                "checks": "Operation=1 (Request). SPA=TPA (misma IP). Tha=00:00:00:00:00:00. No debe haber respuesta (si la hay, indica IP duplicada).",
                                "anomalies": "Respuesta ARP recibida (IP conflict, cliente debería descartar la IP y enviar DHCPDECLINE), ARP Reply en lugar de Request (algunos sistemas usan Reply para GARP), SPA != TPA (no es gratuitous).",
                                "packet_capture": {
                                    "wireshark_display_filter": "arp.opcode == 1 and arp.src.proto_ipv4 == arp.dst.proto_ipv4",
                                    "tcpdump_filter": "arp",
                                    "notes": "Verificar que no haya respuesta a este ARP. Si hay respuesta, existe conflicto de IP."
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    'netflow_ipfix': {
        'scenarios': [
            {
                "id": "netflow_ipfix_export",
                "name": "NetFlow v9/IPFIX - Creación de flujo y exportación al colector",
                "description": "Recorrido del proceso de creación de un registro de flujo en un router, su mantenimiento en caché, el alcance de timeout activo, la exportación usando plantilla v9/IPFIX, recepción en el colector UDP 2055 y análisis.",
                "steps": [
                    {
                        "step_title": "Paso 1: Paquete llega al router y se clasifica",
                        "device": "Router (NetFlow Exporter)",
                        "action": "Un paquete IP llega a una interfaz del router donde NetFlow/IPFIX está habilitado. El motor de forwarding extrae la 5-tupla y busca en la caché de flujos.",
                        "note": "La 5-tupla clásica es: SrcIP, DstIP, SrcPort, DstPort, Protocol. En IPFIX puede ser n-tupla con campos adicionales (VLAN, TOS, etc.).",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "Trama Ethernet con EtherType=0x0800 (IPv4) o 0x86DD (IPv6). DstMAC=MAC_router, SrcMAC=MAC_dispositivo_previo. Posible 802.1Q tag.",
                                "checks": "Interfaz del router Up/Up. NetFlow/IPFIX habilitado en la interfaz de ingreso (input) o salida (output) según configuración.",
                                "anomalies": "Interfaz down, NetFlow no habilitado en la interfaz (no se muestrea), trama con FCS error descartada antes de NetFlow.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip",
                                    "tcpdump_filter": "ip or ip6",
                                    "notes": "Capturar en la interfaz del router. NetFlow no altera el paquete original; solo lo muestrea."
                                }
                            },
                            {
                                "name": "Capa 3 - Red (IPv4/IPv6)",
                                "detail": "IPv4: SrcIP, DstIP, Protocol, TOS, TTL. IPv6: SrcIP, DstIP, Next Header, Traffic Class, Hop Limit. El router extrae estos campos para formar la clave del flujo.",
                                "checks": "Header IP válido (checksum IPv4 correcto, IPv6 sin checksum L3). No es un paquete de control del propio router (BGP, OSPF) a menos que también se muestree.",
                                "anomalies": "IP checksum incorrecto (paquete descartado antes de contabilizar), header IP truncado, fragmentación que genera múltiples flujos (solo el primero tiene L4 info).",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip",
                                    "tcpdump_filter": "ip or ip6",
                                    "notes": "Verificar que el paquete es válido antes de la clasificación NetFlow."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte (L4 Header)",
                                "detail": "TCP/UDP/ICMP: SrcPort, DstPort (TCP/UDP), o Type/Code (ICMP). Flags TCP (SYN, ACK, FIN, RST, PSH, URG, ECE, CWR) también se registran para análisis de estado de flujo.",
                                "checks": "Puertos L4 válidos (no 0 en TCP/UDP a menos que sea ICMP). Flags TCP coherentes.",
                                "anomalies": "Paquete fragmentado (offset>0, no hay puertos L4), protocolo no soportado por NetFlow (ej: ESP sin desencapsulación), puertos dinámicos que cambian dentro del mismo flujo (NAT).",
                                "packet_capture": {
                                    "wireshark_display_filter": "tcp or udp or icmp",
                                    "tcpdump_filter": "tcp or udp or icmp",
                                    "notes": "NetFlow clasifica según L4. Los fragmentos posteriores pueden ir a un flujo separado o al mismo según implementación."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 2: Creación de entrada en caché de flujos (5-tupla)",
                        "device": "Router (NetFlow Cache)",
                        "action": "Si la 5-tupla no existe en la caché, se crea una nueva entrada de flujo. Se inicializan contadores de bytes y paquetes, timestamps, y flags de estado.",
                        "note": "NetFlow v9 usa un enfoque de 'flow' basado en la conexión. Un flujo termina por inactividad (inactive timeout), timeout activo (active timeout), FIN/RST (TCP), o caché llena.",
                        "layers": [
                            {
                                "name": "Capa 7 - Aplicación (NetFlow Cache Entry)",
                                "detail": "Clave del flujo: {SrcIP, DstIP, Protocol, SrcPort, DstPort, Input SNMP Index, Output SNMP Index}. Valores: packet count=1, byte count=IP total length, first_switched=timestamp sysuptime, last_switched=timestamp sysuptime, TCP flags acumulados (OR de flags), TOS, src/dst mask, next-hop IP, AS src/dst.",
                                "checks": "Caché tiene espacio disponible (no llena). No hay flujo duplicado (misma 5-tupla ya existente, en cuyo caso solo se actualiza). Timestamps del router son correctos (NTP sincronizado).",
                                "anomalies": "Caché llena (eviction prematuro de flujos antiguos), clock skew (timestamps incorrectos), flujo duplicado por NAT (misma 5-tupla pública pero privadas diferentes), agregación configurada que oculta detalles.",
                                "packet_capture": {
                                    "wireshark_display_filter": "cflow",
                                    "tcpdump_filter": "udp port 2055 or udp port 4739",
                                    "notes": "Verificar caché en CLI: show ip cache flow / show flow monitor. No se captura aquí, se inspecciona la tabla del router."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 3: Timeout activo alcanzado (Active Timeout)",
                        "device": "Router (NetFlow Exporter)",
                        "action": "Cuando un flujo supera el tiempo activo configurado (ej: 60 segundos), se marca para exportación y se reinician los contadores (o se crea un nuevo registro continuo).",
                        "note": "El active timeout evita que flujos de larga duración (ej: streaming, backup) nunca sean exportados. Típicamente 1-5 minutos.",
                        "layers": [
                            {
                                "name": "Capa 7 - Aplicación (NetFlow Active Timeout)",
                                "detail": "last_switched - first_switched >= active_timeout (ej: 1800 segundos / 30 min en Cisco default, configurable). El router cierra el flujo actual, lo encola para exportación, y si llegan más paquetes, crea un nuevo flujo con el mismo key.",
                                "checks": "Active timeout configurado según requerimiento. El flujo se exporta con first_switched y last_synchronized correctos. No hay gap en contadores entre flujo antiguo y nuevo.",
                                "anomalies": "Active timeout muy largo (datos atrasados en colector), muy corto (sobrecarga de exportación y crecimiento de base de datos), clock del router desfasado (timestamps erróneos), flujo no exportado por política (sampler).",
                                "packet_capture": {
                                    "wireshark_display_filter": "cflow",
                                    "tcpdump_filter": "udp port 2055 or udp port 4739",
                                    "notes": "Verificar configuración: active timeout en CLI. Los flujos exportados por timeout activo tienen last_switched - first_switched aproximadamente igual al timeout."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 4: Exportación de plantilla y registro de datos NetFlow v9/IPFIX",
                        "device": "Router → Colector",
                        "action": "El router envía primero la plantilla (Template FlowSet) que define la estructura de los campos, seguida del Data FlowSet con los valores reales. En IPFIX el concepto es similar pero con Template Record y Data Record.",
                        "note": "NetFlow v9 usa UDP 2055 (Cisco default). IPFIX usa UDP 4739 (IANA standard). La plantilla debe enviarse periódicamente para que el colector sepa cómo interpretar los Data Records.",
                        "layers": [
                            {
                                "name": "Capa 3 - Red (IPv4/IPv6)",
                                "detail": "SrcIP=IP_Loopback o IP_interfaz_salida del router. DstIP=IP_Colector. TTL=255 (o default). Protocol=UDP. IP Total Length según payload.",
                                "checks": "Ruta hacia el colector disponible. SrcIP alcanzable por el colector. No hay NAT entre router y colector que cambie los puertos. MTU suficiente para el datagrama UDP.",
                                "anomalies": "Ruta faltante hacia colector (descarte silencioso), ACL bloqueando UDP 2055/4739, NAT modificando SrcIP/ports, MTU insuficiente causando fragmentación UDP (raro pero posible).",
                                "packet_capture": {
                                    "wireshark_display_filter": "udp.dstport == 2055 or udp.dstport == 4739",
                                    "tcpdump_filter": "udp dst port 2055 or udp dst port 4739",
                                    "notes": "Capturar en la interfaz de salida del router hacia el colector. Verificar que los paquetes salen."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte (UDP)",
                                "detail": "SrcPort=variable (ephemeral, o configurable). DstPort=2055 (NetFlow v9) o 4739 (IPFIX). UDP Length incluye payload NetFlow/IPFIX. UDP Checksum puede ser 0x0000 o calculado.",
                                "checks": "DstPort correcto según protocolo. UDP checksum válido. No hay firewall intermedio bloqueando estos puertos.",
                                "anomalies": "DstPort incorrecto (colector escucha en otro puerto), firewall bloqueando UDP, UDP checksum incorrecto descartado por algún middlebox.",
                                "packet_capture": {
                                    "wireshark_display_filter": "udp.dstport == 2055 or udp.dstport == 4739",
                                    "tcpdump_filter": "udp dst port 2055 or udp dst port 4739",
                                    "notes": "Verificar DstPort. El colector debe estar escuchando en el mismo puerto."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (NetFlow v9 Template + Data Record)",
                                "detail": "NetFlow v9 Header: Version=9, Count=número de FlowSets, SysUptime, UNIX Seconds, Sequence Number, Source ID. Template FlowSet: FlowSet ID=0, Length, Template ID=256 (ej), Field Count=m, [Field Type, Field Length] x m. Data FlowSet: FlowSet ID=256 (coincide con Template), Length, [Data Record] x k. Campos típicos: IN_BYTES(1), IN_PKTS(2), PROTOCOL(4), SRC_TOS(5), TCP_FLAGS(6), L4_SRC_PORT(7), IPV4_SRC_ADDR(8), L4_DST_PORT(11), IPV4_DST_ADDR(12), INPUT_SNMP(10), OUTPUT_SNMP(14), LAST_SWITCHED(21), FIRST_SWITCHED(22).",
                                "checks": "Version=9. Template ID consistente entre Template y Data FlowSets. Field Types y Lengths coinciden con lo esperado por el colector. Sequence number incrementa monotónicamente (sin gap indica pérdida).",
                                "anomalies": "Template ID no reconocido por colector (datos descartados), mismatch en Field Length (offset corruption), Sequence number gap (pérdida de paquetes UDP), Source ID cambiado (colector no agrupa correctamente), Template no reenviada tras reinicio del colector.",
                                "packet_capture": {
                                    "wireshark_display_filter": "cflow",
                                    "tcpdump_filter": "udp port 2055 or udp port 4739",
                                    "notes": "En Wireshark expandir 'Cisco NetFlow' o 'IPFIX'. Verificar que el colector reciba primero Template (FlowSet ID=0 o 2 para IPFIX) y luego Data Records."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (IPFIX Template + Data Record)",
                                "detail": "IPFIX Header: Version=10, Length=total message length, Export Time, Sequence Number, Observation Domain ID. Template Set: Set ID=2, Length, Template Record con Template ID y Field Specifiers. Data Set: Set ID=Template ID, Length, Data Records. IPFIX usa Information Elements (IE) estandarizados por IANA.",
                                "checks": "Version=10. Set ID=2 para Template, >255 para Data. IE IDs válidos según IANA registry. Enterprise bit (bit 15) solo para IEs privados. Observation Domain ID consistente.",
                                "anomalies": "Enterprise IE no reconocido por colector (sin definición), Set Length incorrecto (padding mal calculado), Export Time desfasado (NTP no sincronizado), Observation Domain ID diferente por interfaz (requiere configuración en colector).",
                                "packet_capture": {
                                    "wireshark_display_filter": "ipfix",
                                    "tcpdump_filter": "udp port 4739",
                                    "notes": "Wireshark soporta IPFIX nativamente. Verificar Set ID=2 para templates y que los Data Sets usen IDs de template válidos."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 5: Colector recibe en UDP 2055/4739",
                        "device": "Colector NetFlow/IPFIX",
                        "action": "El colector recibe los datagramas UDP, parsea el header, almacena templates en memoria, decodifica Data Records y persiste en base de datos o envía a analítica.",
                        "note": "El colector debe mantener un diccionario de templates por Source ID / Observation Domain. Si recibe Data sin conocer el Template, descarta el record hasta recibir el Template.",
                        "layers": [
                            {
                                "name": "Capa 4 - Transporte (UDP Recepción)",
                                "detail": "DstPort=2055 (NetFlow v9) o 4739 (IPFIX). SrcPort=ephemeral del router. UDP payload entregado a la aplicación colectora.",
                                "checks": "Socket UDP escuchando en el puerto correcto. Firewall del SO permite tráfico entrante en ese puerto. No hay otro proceso usando el puerto.",
                                "anomalies": "Puerto ocupado por otro servicio, firewall OS bloqueando (iptables/Windows Defender), socket buffer overflow (drop de datagramas bajo alta carga), SO descartando UDP por checksum incorrecto.",
                                "packet_capture": {
                                    "wireshark_display_filter": "udp.dstport == 2055 or udp.dstport == 4739",
                                    "tcpdump_filter": "udp dst port 2055 or udp dst port 4739",
                                    "notes": "Capturar en la interfaz del colector. Verificar que llegan datagramas."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (Colector - Parsing)",
                                "detail": "El colector lee Version. Si es 9: busca Template FlowSets (ID=0) para actualizar su diccionario, luego parsea Data FlowSets usando el diccionario. Si es 10 (IPFIX): similar con Set ID=2 para Templates. Extrae campos y los inserta en base de datos (InfluxDB, Elastic, ClickHouse, etc.).",
                                "checks": "Colector reconoce el Source ID / Observation Domain. Templates actualizadas recientemente. No hay errores de parsing en logs. Base de datos accesible.",
                                "anomalies": "Template desconocido (Data descartado), mismatch de endianness ( algunos campos malinterpretados), IE privado sin definición (parsing fallido), base de datos llena o lenta (backlog de exportación), Sequence number gap detectado (pérdida de paquetes).",
                                "packet_capture": {
                                    "wireshark_display_filter": "cflow or ipfix",
                                    "tcpdump_filter": "udp port 2055 or udp port 4739",
                                    "notes": "En Wireshark: Statistics → Protocol Hierarchy → buscar CFLOW/IPFIX. Verificar que no haya errores de 'Malformed Packet'."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 6: Flujo analizado en el colector",
                        "device": "Colector / Dashboard",
                        "action": "Los datos almacenados se consultan para análisis: top talkers, protocolos, aplicaciones (L7 con DPI adicional), anomalías de tráfico, seguridad (DDoS, exfiltración).",
                        "note": "NetFlow v5/v9/IPFIX por sí solo no da L7 (aplicación). Para L7 se necesita NBAR, DPI, o campos enterprise específicos. Pero con puertos L4 se puede inferir servicios.",
                        "layers": [
                            {
                                "name": "Capa 7 - Aplicación (Análisis)",
                                "detail": "Consultas SQL/NoSQL: SELECT src_ip, dst_ip, sum(bytes), sum(packets) FROM flows WHERE timestamp BETWEEN x AND y GROUP BY src_ip, dst_ip. Detección de anomalías: flujos con bytes/packet ratio anómalo, conexiones a puertos raros, scan de puertos (muchas conexiones cortas), DDoS (mucho tráfico hacia una IP).",
                                "checks": "Dashboard muestra datos actualizados. Timestamps correctos. Agregaciones matemáticas consistentes. Alertas configuradas y funcionando.",
                                "anomalies": "Datos faltantes (gaps en time series), timestamps duplicados (problema de NTP), agregaciones incorrectas (sumas desbordadas en 32-bit), falso positivo en alertas por NAT compartido, flujo asimétrico (solo se ve en un sentido si NetFlow está en una sola interfaz).",
                                "packet_capture": {
                                    "wireshark_display_filter": "cflow or ipfix",
                                    "tcpdump_filter": "udp port 2055 or udp port 4739",
                                    "notes": "El análisis es post-recepción. Si hay dudas, comparar los datos del dashboard con capturas directas (tcpdump) en el router."
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    'ipv6_ndp': {
        'scenarios': [
            {
                "id": "ipv6_ndp_icmpv6",
                "name": "IPv6 / NDP - Neighbor Discovery y ICMPv6 Echo",
                "description": "Recorrido del descubrimiento de vecinos IPv6 (NS/NA), resolución de gateway, envío de ICMPv6 Echo Request, forwarding por router, respuesta Echo Reply, y Path MTU Discovery si el enlace intermedio tiene menor MTU.",
                "steps": [
                    {
                        "step_title": "Paso 1: Host envía Neighbor Solicitation para gateway por defecto",
                        "device": "Host IPv6",
                        "action": "El host necesita enviar un paquete IPv6 fuera de su subnet. Primero debe resolver la MAC del gateway por defecto mediante NDP (equivalente a ARP en IPv4). Envía Neighbor Solicitation (NS) al solicited-node multicast del gateway.",
                        "note": "Solicited-node multicast se forma con prefix FF02::1:FF00:0/104 + últimos 24 bits de la dirección IPv6 objetivo. Ej: gateway=2001:db8::1 → solicited-node=ff02::1:ff00:1.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "DstMAC=33:33:FF:00:00:01 (solicited-node multicast Ethernet, últimos 32 bits del IPv6 multicast), SrcMAC=MAC_Host, EtherType=0x86DD (IPv6).",
                                "checks": "Interfaz del host Up/Up. IPv6 habilitado. La dirección link-local del host está configurada (requerida para NDP). El switch permite multicast IPv6 (MLD snooping o flooding controlado).",
                                "anomalies": "IPv6 deshabilitado en interfaz, dirección link-local faltante (autoconfig fallida), MLD snooping bloqueando el grupo solicitado (raro en LAN simple), port-security descartando tramas multicast.",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 135",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 135",
                                    "notes": "Capturar NS. DstMAC empieza con 33:33:FF. En Wireshark filtrar icmpv6.type == 135."
                                }
                            },
                            {
                                "name": "Capa 3 - Red (IPv6)",
                                "detail": "SrcIP=Link-Local del host (ej: fe80::a00:27ff:fe01:1). DstIP=Solicited-node multicast del gateway (ej: ff02::1:ff00:1). Hop Limit=255 (obligatorio para NDP, descarta si <255). Next Header=58 (ICMPv6).",
                                "checks": "SrcIP es link-local del host. DstIP es solicited-node del gateway. Hop Limit=255 (NDP requiere esto para asegurar que el paquete no fue enrutado). Next Header=58.",
                                "anomalies": "Hop Limit != 255 (paquete posiblemente spoofeado o enrutado, debe descartarse según RFC 4861), SrcIP no es link-local (incorrecto para NDP en LAN), DstIP unicast en lugar de multicast (algunas optimizaciones, pero no es el comportamiento inicial).",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 135 and ipv6.hlim == 255",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 135 and ip6[7] == 255",
                                    "notes": "Verificar Hop Limit=255. Si no es 255, el NS es inválido según RFC 4861."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte (ICMPv6)",
                                "detail": "Type=135 (Neighbor Solicitation), Code=0. Checksum ICMPv6 calculado sobre pseudo-header IPv6 + payload. Reserved=0. Target Address=IPv6 del gateway (ej: 2001:db8::1). Options: Source Link-Layer Address=MAC_Host.",
                                "checks": "Type=135. Target Address es la dirección del gateway que se quiere resolver. Option Type=1 (Source Link-Layer Address) presente con MAC correcta.",
                                "anomalies": "Checksum ICMPv6 incorrecto (descartado por stack), Target Address no es la del gateway (solicitud errónea), Option Source LLA faltante (el router no sabrá a qué MAC responder unicast), Type != 135.",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 135",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 135",
                                    "notes": "Expandir ICMPv6 en Wireshark. Verificar Target Address y opción Source Link-Layer Address."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 2: Router responde con Neighbor Advertisement",
                        "device": "Router (Gateway IPv6)",
                        "action": "El router recibe el NS en el grupo solicited-node. Reconoce que Target Address es una de sus direcciones. Responde con Neighbor Advertisement (NA) unicast al host.",
                        "note": "Si el router tiene la dirección objetivo, responde. Si no, ignora. El NA puede ser unicast o multicast dependiendo de la flag Solicited y de si hay un proxy ND.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "DstMAC=MAC_Host (unicast), SrcMAC=MAC_Router, EtherType=0x86DD. El switch reenvía por el puerto donde aprendió MAC_Host.",
                                "checks": "El switch tiene MAC_Host en su tabla (aprendida del NS anterior). Puerto del router Up/Up. No hay MAC filtering.",
                                "anomalies": "MAC del host no aprendida (flooding o descarte), puerto del router bloqueado por spanning-tree, router con ND proxy habilitado respondiendo por otra interfaz.",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 136",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 136",
                                    "notes": "Capturar NA. DstMAC debe ser la del host (unicast), no broadcast/multicast."
                                }
                            },
                            {
                                "name": "Capa 3 - Red (IPv6)",
                                "detail": "SrcIP=Link-Local del router (ej: fe80::a00:27ff:fe01:2) o la propia Target Address. DstIP=Link-Local del host (fe80::a00:27ff:fe01:1). Hop Limit=255. Next Header=58.",
                                "checks": "Hop Limit=255. DstIP es la link-local del host (aprendida del SrcIP del NS). SrcIP es válida del router.",
                                "anomalies": "Hop Limit != 255 (inválido según RFC), DstIP multicast (solo si Router Advertisement o unsolicited NA), SrcIP no pertenece al router (spoofing).",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 136 and ipv6.hlim == 255",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 136 and ip6[7] == 255",
                                    "notes": "Verificar Hop Limit=255 en NA. Filtrar por type 136."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte (ICMPv6)",
                                "detail": "Type=136 (Neighbor Advertisement), Code=0. Checksum ICMPv6. Flags: Router=1 (es un router), Solicited=1 (respuesta a NS), Override=1 (actualizar caché del vecino). Target Address=2001:db8::1 (la dirección solicitada). Options: Target Link-Layer Address=MAC_Router.",
                                "checks": "Type=136. Router flag=1 (confirma que es gateway). Solicited=1. Target Address coincide con la solicitada en NS. Option Type=2 (Target Link-Layer Address) con MAC del router.",
                                "anomalies": "Router flag=0 (el host no lo usará como gateway por defecto), Solicited=0 (NA no solicitado, puede ser anuncio periódico), Target Address diferente (respuesta errónea), Option Target LLA faltante (host no puede actualizar caché).",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 136",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 136",
                                    "notes": "Expandir NA en Wireshark. Verificar flags R=1, S=1. Confirmar Target Address y MAC del router."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 3: Host envía ICMPv6 Echo Request",
                        "device": "Host IPv6",
                        "action": "Con la MAC del gateway resuelta, el host encapsula un paquete IPv6 con destino al host remoto y lo envía al router.",
                        "note": "El host usa su dirección global (GUA) como origen si está disponible, o link-local si no. El destino es la dirección global del host remoto.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "DstMAC=MAC_Router (gateway), SrcMAC=MAC_Host, EtherType=0x86DD. El host usa la entrada de caché NDP creada en el paso anterior.",
                                "checks": "Caché NDP del host tiene la MAC del router (show ipv6 neighbors / ip -6 neigh). DstMAC es la del gateway, no la del destino final (que está en otra subnet).",
                                "anomalies": "Caché NDP vacía o incompleta (host reenvía NS nuevamente), DstMAC del host remoto en lugar del gateway (host cree que está en la misma subnet), MAC del router cambiada (caché stale).",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 128",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 128",
                                    "notes": "Capturar Echo Request. DstMAC debe ser la del router."
                                }
                            },
                            {
                                "name": "Capa 3 - Red (IPv6)",
                                "detail": "SrcIP=GUA del host (ej: 2001:db8::100). DstIP=GUA del host remoto (ej: 2001:db8:1::50). Traffic Class=0, Flow Label=0 (o aleatorio). Payload Length=40 (ICMPv6 header + data). Next Header=58 (ICMPv6). Hop Limit=64 (o valor del SO).",
                                "checks": "SrcIP y DstIP son direcciones globales válidas (no link-local para tráfico entre subnets). Hop Limit > 0. Next Header=58.",
                                "anomalies": "SrcIP=:: (unspecified, inválido para Echo Request), SrcIP link-local (puede fallar enrutamiento si el router no acepta LLA como origen enrutado), Hop Limit=1 (descartado en primer salto), Next Header != 58.",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 128 and ipv6.src != fe80::/10",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 128",
                                    "notes": "Verificar que SrcIP no sea link-local (fe80::/10) para tráfico inter-subnet."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte (ICMPv6)",
                                "detail": "Type=128 (Echo Request), Code=0. Checksum ICMPv6 calculado con pseudo-header. Identifier=0x1234 (ej), Sequence Number=1. Data=payload variable (timestamp o pattern).",
                                "checks": "Type=128. Identifier y Sequence Number consistentes con la respuesta esperada. Checksum válido.",
                                "anomalies": "Type=129 (Echo Reply en lugar de Request, indica loop), Checksum incorrecto (descartado), Identifier no coincide con la Reply recibida (múltiples procesos de ping).",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 128",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 128",
                                    "notes": "En Wireshark: icmpv6.type == 128. Verificar Identifier y Sequence Number."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 4: Router reenvía hacia el destino",
                        "device": "Router IPv6",
                        "action": "El router recibe el paquete IPv6, decrementa Hop Limit en 1, busca en su tabla de rutas el next-hop hacia 2001:db8:1::/64, resuelve la MAC del next-hop (o del destino si es directamente conectado) y reenvía.",
                        "note": "Si el destino está directamente conectado, el router envía NS al solicited-node del destino. Si es next-hop remoto, resuelve la MAC del next-hop según la subnet del enlace saliente.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "Si destino directo: DstMAC=MAC_Destino (resuelto por NDP). Si next-hop remoto: DstMAC=MAC_NextHop. SrcMAC=MAC_Router_interfaz_salida. EtherType=0x86DD.",
                                "checks": "Router tiene ruta hacia el destino (show ipv6 route). Interfaz de salida Up/Up. MAC del next-hop resuelta (NDP completo en interfaz saliente).",
                                "anomalies": "Ruta faltante hacia destino (ICMPv6 Type 1 Code 0: No Route to Destination), interfaz de salida down, NDP incompleto en next-hop (paquete encolado o descartado), ACL IPv6 bloqueando.",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 128 or icmpv6.type == 1",
                                    "tcpdump_filter": "icmp6 and (ip6[40] == 128 or ip6[40] == 1)",
                                    "notes": "Capturar en interfaz de salida del router. Si aparece ICMPv6 Type 1 (Destination Unreachable) Code 0, es ruta faltante."
                                }
                            },
                            {
                                "name": "Capa 3 - Red (IPv6)",
                                "detail": "SrcIP=GUA del host origen (sin cambiar). DstIP=GUA del destino (sin cambiar). Hop Limit=63 (decrementado de 64). Next Header=58. Si el router genera error: Type=1 (Destination Unreachable) o Type=3 (Time Exceeded).",
                                "checks": "Hop Limit decrementado en 1. SrcIP/DstIP no modificados (a diferencia de NAT, IPv6 no usa NAT en routing estándar). Routing extension header presente solo si source routing.",
                                "anomalies": "Hop Limit=0 tras decremento (router descarta y envía Time Exceeded, Type 3 Code 0). SrcIP modificado (NAT66 o NPTv6, no estándar carrier). Extension header Hop-by-Hop con Router Alert que requiere procesamiento especial.",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 128 and ipv6.hlim < 64",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 128 and ip6[7] < 64",
                                    "notes": "Verificar que Hop Limit es menor al original (normalmente 63 si origen envió 64)."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 5: Destino responde con ICMPv6 Echo Reply",
                        "device": "Host Destino IPv6",
                        "action": "El host destino recibe el Echo Request, verifica que la dirección destino es suya, y responde con ICMPv6 Echo Reply al host origen.",
                        "note": "La Reply usa como SrcIP la dirección que recibió en DstIP del Request. El DstIP es el SrcIP del Request. El path de retorno puede ser diferente al de ida (asymmetric routing).",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet)",
                                "detail": "DstMAC=MAC_Router_saliente (o MAC del host origen si están en misma subnet). SrcMAC=MAC_Host_Destino. EtherType=0x86DD.",
                                "checks": "Host destino resuelve MAC del next-hop (gateway) vía NDP si está en subnet diferente. Si misma subnet, usa NDP directo al host origen.",
                                "anomalies": "Gateway del destino mal configurado (no sabe a dónde enviar), NDP incompleto en destino (no resuelve MAC del gateway), firewall en destino bloqueando ICMPv6 entrante o saliente.",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 129",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 129",
                                    "notes": "Capturar Echo Reply en destino. Verificar que responde."
                                }
                            },
                            {
                                "name": "Capa 3 - Red (IPv6)",
                                "detail": "SrcIP=GUA del destino (2001:db8:1::50). DstIP=GUA del origen (2001:db8::100). Hop Limit=64 (o valor del SO). Next Header=58.",
                                "checks": "SrcIP y DstIP invertidos respecto al Request. Hop Limit >= 1. Direcciones globales válidas.",
                                "anomalies": "SrcIP diferente (múltiples direcciones en interfaz, elige una no esperada), DstIP link-local (si el origen usó link-local, la reply irá a link-local), Hop Limit=0 (descartado en primer salto de retorno).",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 129",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 129",
                                    "notes": "Verificar SrcIP/DstIP invertidos. El Identifier y Sequence Number deben coincidir con el Request."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte (ICMPv6)",
                                "detail": "Type=129 (Echo Reply), Code=0. Checksum ICMPv6. Identifier y Sequence Number = mismos valores del Request. Data = mismo payload recibido (echo).",
                                "checks": "Type=129. Identifier y Sequence Number coinciden con el Request enviado. Data idéntica.",
                                "anomalies": "Identifier/Sequence mismatch (reply de otro ping), Data modificada (middlebox interferencia, aunque raro en ICMPv6), Type=1 (error en lugar de reply).",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 129",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 129",
                                    "notes": "En Wireshark: icmpv6.type == 129. Comparar Identifier/Sequence con el Request correspondiente."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 6: Path MTU Discovery si es necesario",
                        "device": "Router intermedio / Host origen",
                        "action": "Si un enlace intermedio tiene MTU menor al tamaño del paquete IPv6 (ej: túnel con MTU 1480 vs paquete de 1500 bytes), el router intermedio descarta el paquete y envía ICMPv6 Packet Too Big (Type 2) al origen.",
                        "note": "IPv6 no permite fragmentación en routers intermedios. Solo el host origen puede fragmentar. Por eso PMTUD es esencial. Si PMTUD falla (firewall bloquea ICMPv6 Type 2), aparecen problemas de 'MTU black hole'.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos (Ethernet/Túnel)",
                                "detail": "Paquete IPv6 de 1500 bytes llega a router con interfaz de salida MTU=1480 (ej: túnel GRE, PPPoE, o VPN). La capa L2 no puede encapsular 1500+overhead. El router no fragmenta.",
                                "checks": "MTU de todas las interfaces en el path >= 1280 (mínimo IPv6). MTU del enlace más restrictivo conocido. Túneles tienen overhead adicional (GRE=24 bytes, IPsec ESP=~36-56 bytes).",
                                "anomalies": "MTU < 1280 (inválido para IPv6), túnel sin ajuste de MTU (paquetes > path MTU descartados silenciosamente si ICMP bloqueado), enlace con jumbo frames en un extremo pero no en otro.",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 2",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 2",
                                    "notes": "Capturar ICMPv6 Type 2 (Packet Too Big). Aparece en el router con MTU restrictivo y en el host origen."
                                }
                            },
                            {
                                "name": "Capa 3 - Red (IPv6)",
                                "detail": "Router intermedio genera ICMPv6 Type 2 (Packet Too Big) con MTU del enlace problemático en el campo MTU (ej: 1480). SrcIP=Link-Local o GUA del router. DstIP=SrcIP del paquete original.",
                                "checks": "ICMPv6 Type 2 llega al host origen. Campo MTU indica el tamaño máximo permitido. El host origen reduce el tamaño de paquete subsecuente.",
                                "anomalies": "Firewall bloqueando ICMPv6 Type 2 (PMTUD black hole, conexiones TCP se cuelgan, UDP pierde paquetes grandes), router envía MTU=0 (inválido, host debe usar 1280), Type 2 no generado (algunos routers mal configurados descartan sin avisar).",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 2",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 2",
                                    "notes": "Verificar que ICMPv6 Type 2 llega al origen. El campo MTU debe ser > 0. Si no aparece y los paquetes grandes fallan, sospechar firewall bloqueando ICMPv6."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte (ICMPv6)",
                                "detail": "Type=2 (Packet Too Big), Code=0. Checksum ICMPv6. MTU=1480 (o valor real del enlace). El payload incluye los primeros bytes del paquete original descartado (hasta 1280 bytes como máximo según RFC, típicamente el header IPv6 + algo de L4).",
                                "checks": "Type=2, Code=0. MTU > 0 y >= 1280. Payload incluye header IPv6 original para identificar el flujo afectado.",
                                "anomalies": "MTU < 1280 (inválido), payload no incluye header original (host no sabe qué flujo ajustar), Checksum incorrecto (descartado por stack).",
                                "packet_capture": {
                                    "wireshark_display_filter": "icmpv6.type == 2",
                                    "tcpdump_filter": "icmp6 and ip6[40] == 2",
                                    "notes": "Expandir ICMPv6 en Wireshark. Verificar campo MTU y el payload incluido (original packet)."
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "ospf": {
        "scenarios": [
            {
                "id": "ospf_hello_sync",
                "name": "OSPF - Intercambio de Hello y Sincronización LSDB",
                "description": "Escenario de troubleshooting del intercambio de paquetes OSPF Hello entre dos routers en Area 0, seguido de la sincronización de la base de datos de estado de enlace mediante DBD, LSU y LSAck.",
                "steps": [
                    {
                        "step_title": "Paso 1: Router A envía OSPF Hello",
                        "device": "Router A",
                        "action": "Transmite paquete OSPF Hello a la dirección multicast 224.0.0.5 para descubrir vecinos en el segmento.",
                        "note": "El intervalo de Hello por defecto en broadcast es 10 segundos. Verificar que ambos routers compartan el mismo intervalo y área.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet: MAC origen = MAC de interfaz de Router A; MAC destino = 01:00:5E:00:00:05 (multicast OSPF); EtherType = 0x0800 (IPv4).",
                                "checks": "Verificar que la interfaz esté en UP/UP, sin errores de capa 2, y que el switch no filtre multicast 01:00:5E:00:00:05.",
                                "anomalies": "MAC destino incorrecta, tramas con FCS error, o interfaces en estado down indican problema físico o de switch.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 1",
                                    "tcpdump_filter": "ip multicast and ip proto ospf",
                                    "notes": "Capturar en la interfaz física. El filtro tcpdump debe usar 'ip[9] == 89' para OSPF exacto."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "Encabezado IP: Protocolo = 89 (OSPF); IP origen = IP de interfaz de Router A; IP destino = 224.0.0.5 (AllSPFRouters); TTL = 1.",
                                "checks": "Confirmar que la interfaz pertenece al área correcta, que la red está en modo broadcast o point-to-point, y que el TTL es 1.",
                                "anomalies": "TTL distinto de 1, IP origen no perteneciente a la subred del vecino, o filtrado ACL de protocolo IP 89.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.proto == 89 and ip.dst == 224.0.0.5",
                                    "tcpdump_filter": "ip proto 89 and dst 224.0.0.5",
                                    "notes": "En tcpdump usar 'ip[9] == 89' si el nombre del protocolo no está resuelto."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (OSPF)",
                                "detail": "Paquete OSPF Hello: Tipo = 1; Router ID de A; Area ID = 0.0.0.0; Máscara de red; Intervalo Hello = 10s; Intervalo Dead = 40s; Opciones = E; Prioridad DR/BDR.",
                                "checks": "Verificar Router ID único, Area ID coincidente, mismos parámetros de red (máscara en modo non-broadcast), y timers idénticos.",
                                "anomalies": "Máscara diferente, Area ID distinta, Hello/Dead interval desajustado, o MTU mismatch (en algunas implementaciones) impiden la adyacencia.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 1",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "En Wireshark, expandir el paquete OSPF para ver los campos Hello específicos como Network Mask y Hello Interval."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 2: Router B recibe Hello y verifica parámetros",
                        "device": "Router B",
                        "action": "Procesa el paquete Hello recibido, validando parámetros de capa 3 y OSPF antes de considerar a Router A como vecino.",
                        "note": "Router B debe encontrar el Router ID de A en su lista de vecinos. Si los parámetros no coinciden, ignora el paquete.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Interfaz de Router B recibe trama con MAC destino multicast 01:00:5E:00:00:05. La NIC debe estar en modo promiscuo para aceptar multicast.",
                                "checks": "Verificar estado de la interfaz, duplex/speed, y que el driver de red acepte multicast OSPF.",
                                "anomalies": "Interface en modo err-disabled, VLAN incorrecta, o IGMP snooping bloqueando multicast de control.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf and eth.dst == 01:00:5e:00:00:05",
                                    "tcpdump_filter": "ether dst 01:00:5e:00:00:05",
                                    "notes": "Asegurar que la captura se realice en ambos sentidos del enlace."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP destino 224.0.0.5 es entregada al proceso OSPF. Se verifica que la IP origen pertenezca a la misma subred.",
                                "checks": "Validar subred IP, máscara, y ausencia de ACLs que descarten IP multicast o protocolo 89.",
                                "anomalies": "IP origen en subred diferente causa rechazo silencioso. Filtrado de ACL en entrada o salida.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.proto == 89 and ip.src == <IP_Router_A>",
                                    "tcpdump_filter": "src host <IP_Router_A> and ip[9] == 89",
                                    "notes": "Sustituir <IP_Router_A> con la dirección real."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (OSPF)",
                                "detail": "Motor OSPF compara: Area ID, máscara (si aplica), Hello/Dead intervals, autenticación (si está configurada), y opciones.",
                                "checks": "Mostrar vecinos OSPF: estado debe pasar de DOWN a INIT. Verificar 'show ip ospf neighbor'.",
                                "anomalies": "Si autenticación falla, paquetes se descartan. Si MTU difiere, estado puede quedarse en EXSTART.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 1",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "Si se usa autenticación MD5, el paquete Hello incluirá el campo Auth Type = 2."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 3: Router B responde con Hello",
                        "device": "Router B",
                        "action": "Envía paquete OSPF Hello a 224.0.0.5 incluyendo el Router ID de A en su lista de vecinos visibles.",
                        "note": "Router A al recibir este Hello con su propio Router ID en la lista, transiciona el vecino a estado 2-WAY.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet: MAC origen = MAC de Router B; MAC destino = 01:00:5E:00:00:05; EtherType = 0x0800.",
                                "checks": "Confirmar que la interfaz de B transmite multicast correctamente sin errores de colisión.",
                                "anomalies": "Ausencia de tramas salientes indica problema de capa 2 o proceso OSPF detenido en B.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf and eth.src == <MAC_Router_B>",
                                    "tcpdump_filter": "ether src <MAC_Router_B> and ether dst 01:00:5e:00:00:05",
                                    "notes": "Verificar dirección MAC origen en la captura."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP: Protocolo = 89; origen = IP de B; destino = 224.0.0.5; TTL = 1.",
                                "checks": "Verificar que la IP origen de B es alcanzable y que no existe NAT o policy-routing alterando el paquete.",
                                "anomalies": "TTL decrementado incorrectamente, IP origen modificada, o rutas asimétricas.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.src == <IP_B> and ip.dst == 224.0.0.5 and ip.proto == 89",
                                    "tcpdump_filter": "src host <IP_B> and dst 224.0.0.5 and ip[9] == 89",
                                    "notes": "Capturar en ambos extremos para confirmar llegada."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (OSPF)",
                                "detail": "Hello: Tipo 1; Router ID de B; Area ID = 0; Neighbor field contiene Router ID de A.",
                                "checks": "Verificar que el campo Neighbor list incluye el Router ID de A. Estado en A debe ser 2-WAY.",
                                "anomalies": "Si el campo Neighbor está vacío, B no ha procesado el Hello de A. Revisar configuración de área y timers.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 1",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "En Wireshark filtrar por ospf.hello.neighbor para ver la lista de vecinos."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 4: Inicio del intercambio de DBD",
                        "device": "Router A y Router B",
                        "action": "Los routers intercambian paquetes Database Description (DBD) para negociar el master/slave y describir sus LSAs.",
                        "note": "En broadcast, el DR/BDR coordina la sincronización. En modo point-to-point, ambos routers negocian directamente.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Tramas Ethernet unicast entre MACs de A y B (o multicast si se anuncian al DR).",
                                "checks": "Verificar que el DR/BDR esté correctamente electo. Las DBD son unicast después de la elección.",
                                "anomalies": "Sin tramas unicast entre vecinos indica fallo en la elección DR o problema de capa 2.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 2",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "Los DBD pueden ir dirigidos a la dirección multicast (en algunas fases) o unicast."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP Protocol 89. En broadcast, DBD se envían a 224.0.0.5 o unicast al vecino según la fase de la adyacencia.",
                                "checks": "Confirmar que las IPs de A y B se resuelven mutuamente y que no hay fragmentación IP.",
                                "anomalies": "Fragmentación de paquetes OSPF puede causar problemas. MTU mismatch previene la sincronización.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 2 and ip.flags.df == 1",
                                    "tcpdump_filter": "ip[9] == 89 and ip[6] & 0x40 != 0",
                                    "notes": "Verificar que el flag Don't Fragment esté activo en DBD."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (OSPF)",
                                "detail": "DBD: Tipo 2; Flags (I/M/MS); DD Sequence Number; Lista resumida de LSAs (Tipo, ID, Advertising Router, Sequence Number).",
                                "checks": "Verificar flags: Initial (I), More (M), Master (MS). Confirmar que el DD sequence number coincida.",
                                "anomalies": "Flags inconsistentes, DD sequence number desincronizado, o ausencia de LSA headers indica fallo en el intercambio.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 2",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "Wireshark muestra los flags DBD y el resumen de LSAs incluidos."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 5: Envío de LSU con LSA tipo 1, 2 y 3",
                        "device": "Router A (o DR)",
                        "action": "Transmite Link-State Update (LSU) conteniendo LSAs de tipo 1 (Router), tipo 2 (Network) y tipo 3 (Summary).",
                        "note": "El DR es responsable de originar LSA tipo 2. Las LSA tipo 3 son generadas por ABRs para inter-área.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet unicast o multicast 224.0.0.5/224.0.0.6 dependiendo del rol (routers envían LSU al DR vía 224.0.0.6; DR inunda vía 224.0.0.5).",
                                "checks": "Verificar que la interfaz del DR tenga la prioridad correcta y que el switch no bloquee multicast 224.0.0.6.",
                                "anomalies": "Ausencia de tramas LSU del DR indica que el DR no está sincronizado o no tiene rutas para anunciar.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 4",
                                    "tcpdump_filter": "ip[9] == 89 and (dst 224.0.0.5 or dst 224.0.0.6)",
                                    "notes": "Los LSU van dirigidos a 224.0.0.6 (AllDRouters) en segmentos broadcast."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP Protocol 89. Dirección destino puede ser multicast (224.0.0.6 para DR) o unicast al vecino específico.",
                                "checks": "Confirmar que las direcciones IP de los vecinos son alcanzables y que el routing intra-área funciona.",
                                "anomalies": "Ruteo incorrecto o filtros de multicast impiden la recepción de LSU.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 4",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "Wireshark filtra LSU con ospf.msg == 4."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (OSPF)",
                                "detail": "LSU: Tipo 4; contiene múltiples LSAs. LSA tipo 1 (Router Links), tipo 2 (Network Links para segmentos transit), tipo 3 (Summary LSAs).",
                                "checks": "Verificar que las LSAs tengan sequence numbers válidos, checksum correcto, y age no expirado.",
                                "anomalies": "LSA con sequence number inconsistente, checksum error, o LSA tipo 3 sin ABR indican corrupción o configuración errónea.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 4",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "En Wireshark expandir 'OSPF Link-State Update' para ver el tipo y contenido de cada LSA."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 6: Recepción de LSAck y LSDB sincronizada",
                        "device": "Router B",
                        "action": "Envía Link-State Ack (LSAck) confirmando la recepción de las LSAs. Ambas LSDB están sincronizadas.",
                        "note": "LSAck puede ser enviado como respuesta múltiple (un solo paquete reconoce varias LSAs).",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet unicast o multicast. LSAck suele ser unicast al emisor del LSU.",
                                "checks": "Verificar que las tramas de LSAck lleguen al emisor original sin errores de capa 2.",
                                "anomalies": "Pérdida de LSAck causa retransmisión de LSU. Verificar colas de salida y buffer de interfaces.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 5",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "LSAck es el tipo 5 de mensaje OSPF."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP Protocol 89. Unicast desde B hacia A (o hacia DR). TTL = 1.",
                                "checks": "Verificar conectividad IP directa. En multi-acceso, confirmar que el DR recibe los acks.",
                                "anomalies": "Retrasos o pérdida de paquetes IP indican congestión o errores de capa 3.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 5",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "Capturar en ambos extremos para verificar la bidireccionalidad."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (OSPF)",
                                "detail": "LSAck: Tipo 5; contiene headers de las LSAs recibidas (sólo tipo, ID, Advertising Router, Sequence Number).",
                                "checks": "Verificar que los LSA headers en el ack coincidan con los enviados en el LSU. Estado FULL en vecinos.",
                                "anomalies": "LSAck con headers diferentes indica desincronización. Estado atorado en EXCHANGE o LOADING.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg == 5",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "Wireshark muestra los LSA headers reconocidos en el LSAck."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 7: Cálculo SPF e instalación de ruta",
                        "device": "Router A y Router B",
                        "action": "Cada router ejecuta el algoritmo Dijkstra (SPF) sobre la LSDB sincronizada e instala las rutas en la RIB.",
                        "note": "El cálculo SPF se ejecuta cuando hay cambios en la topología. Verificar que las rutas OSPF aparezcan en la tabla de enrutamiento.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "No hay tráfico de datos específico para SPF. La convergencia es un proceso interno del CPU.",
                                "checks": "Monitorear utilización de CPU durante el cálculo SPF. Verificar que las interfaces de salida estén operativas.",
                                "anomalies": "Alto CPU por SPF indica inestabilidad de red (flapping) o LSDB muy grande.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "Durante la convergencia pueden observarse múltiples LSU. Un SPF throttle indica inestabilidad."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "Proceso interno: construcción del SPT (Shortest Path Tree) desde el router hacia todos los destinos conocidos.",
                                "checks": "Ejecutar 'show ip route ospf' y verificar que las rutas intra-área (O) e inter-área (O IA) estén presentes.",
                                "anomalies": "Rutas faltantes indican que el área no está correctamente configurada o que los ABRs no generan LSA tipo 3.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "La ausencia de rutas no se detecta en pcap, pero se correlaciona con la falta de LSA tipo 3 en captures previos."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (OSPF)",
                                "detail": "OSPF marca las rutas como válidas si el next-hop es alcanzable. Las métricas (cost) se calculan por ancho de banda.",
                                "checks": "Verificar costos OSPF en interfaces. El costo acumulado debe ser coherente con la topología.",
                                "anomalies": "Costos OSPF mal configurados (auto-reference bandwidth) causan rutas subóptimas o inalcanzables.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ospf.msg.lsa",
                                    "tcpdump_filter": "ip[9] == 89",
                                    "notes": "Revisar las métricas (Metric) dentro de las LSA tipo 3 en captures de LSU."
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "isis": {
        "scenarios": [
            {
                "id": "isis_l2_sync",
                "name": "IS-IS - Adjacencia Level-2 y Flooding de LSP",
                "description": "Escenario de troubleshooting del establecimiento de adyacencia IS-IS nivel 2 mediante IIH en LAN, seguido del flooding de LSP y sincronización mediante PSNP/CSNP.",
                "steps": [
                    {
                        "step_title": "Paso 1: Router A envía LAN IIH con TLVs",
                        "device": "Router A",
                        "action": "Transmite IS-IS Hello (IIH) de tipo LAN Level-2 a la dirección multicast de capa 2 01:80:C2:00:00:15.",
                        "note": "IS-IS utiliza CLNS y no depende de IP. Los IIH se encapsulan directamente en tramas IEEE 802.3/802.2 LLC.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama IEEE 802.3/802.2 LLC: MAC destino = 01:80:C2:00:00:15 (AllL2ISs); MAC origen = Router A; DSAP = 0xFE (ISO CLNP); SSAP = 0xFE; Control = 0x03.",
                                "checks": "Verificar que la interfaz esté en UP y que el switch no filtre la MAC 01:80:C2:00:00:15 (especialmente en STP implementations).",
                                "anomalies": "MAC destino incorrecta, tramas con SNAP en lugar de LLC, o Spanning Tree bloqueando el puerto.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.iih",
                                    "tcpdump_filter": "isis",
                                    "notes": "En Wireshark filtrar por isis.l2.iih. En tcpdump, IS-IS suele ser reconocido automáticamente."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IS-IS opera directamente sobre la subred de capa 2 (CLNS). No hay encabezado IP. El NSEL (NSAP selector) es 00.",
                                "checks": "Verificar que la NET/NSAP esté correctamente configurada y que ambos routers estén en el mismo área (para L1) o que L2 esté habilitado.",
                                "anomalies": "NET duplicado, NSAP mal formada, o área mismatch (para L1) impiden la adyacencia.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.iih",
                                    "tcpdump_filter": "isis",
                                    "notes": "Wireshark muestra los campos NSAP y los TLVs del IIH."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (IS-IS)",
                                "detail": "IIH L2: PDU Type = 16; Holding Time; System-ID de A; LAN ID (Designated IS); TLVs: Area Addresses (1), Protocols Supported (129), IP Interface Address (132), Authentication (10).",
                                "checks": "Verificar que el System-ID sea único, los TLVs de área coincidan, y que el protocolo soportado incluya IP (0xCC para IPv4).",
                                "anomalies": "System-ID duplicado causa inestabilidad. TLV 129 ausente indica que no se anuncia soporte IP. Autenticación fallida descarta el IIH.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.iih",
                                    "tcpdump_filter": "isis",
                                    "notes": "Expandir los TLVs en Wireshark para verificar Area Addresses y Protocols Supported."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 2: Router B recibe IIH y verifica System-ID",
                        "device": "Router B",
                        "action": "Procesa el IIH recibido, valida el System-ID de A, los TLVs de área, y los timers antes de aceptar la adyacencia.",
                        "note": "Router B compara su propia NET y parámetros con los recibidos. IS-IS es menos estricto que OSPF en algunos parámetros.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Interfaz de B recibe trama con MAC destino 01:80:C2:00:00:15. Verificar estado de la interfaz y ausencia de errores.",
                                "checks": "Confirmar que la interfaz de B está en UP/UP y que no existen ACLs de capa 2 filtrando IS-IS.",
                                "anomalies": "Interface err-disabled, trunk con VLAN nativa incorrecta, o storm-control descartando multicast.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.iih and eth.dst == 01:80:c2:00:00:15",
                                    "tcpdump_filter": "isis",
                                    "notes": "Verificar que las tramas llegan con la MAC multicast correcta."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IS-IS CLNS: Se verifica la NSAP origen y se compara con la propia. No hay IP involucrado en el intercambio de control IS-IS.",
                                "checks": "Validar que la NET de B está correctamente configurada y que el área (para L2 no es estricto, pero L1 requiere match).",
                                "anomalies": "NET no configurada, o formato NSAP incorrecto (debe terminar en .00).",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.iih",
                                    "tcpdump_filter": "isis",
                                    "notes": "Wireshark decodifica el campo Source ID (System-ID) en el IIH."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (IS-IS)",
                                "detail": "Motor IS-IS extrae System-ID, Holding Time, Priority, y verifica autenticación si está configurada.",
                                "checks": "Mostrar vecinos IS-IS: estado debe ser Init o Up. Verificar 'show isis neighbors'.",
                                "anomalies": "Autenticación mismatch (clave o tipo diferente) causa descarte silencioso. MTU mismatch (1497 vs 1500) puede impedir LSP exchange.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.iih",
                                    "tcpdump_filter": "isis",
                                    "notes": "El campo Authentication TLV debe coincidir en ambos routers."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 3: Adyacencia UP",
                        "device": "Router B",
                        "action": "Transiciona la adyacencia con A a estado UP. Ambos routers ahora son vecinos Level-2.",
                        "note": "En broadcast, se elige un DIS (Designated IS). El DIS genera pseudonode LSP (tipo 2).",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Router B comienza a enviar sus propios IIH periódicamente. El DIS envía IIH con mayor frecuencia (3.3s vs 10s).",
                                "checks": "Verificar que ambos routers envíen IIH. El DIS debe tener la prioridad más alta (default 64).",
                                "anomalies": "Adyacencia atorada en Init indica que B ve a A pero A no ve a B (problema unidireccional).",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.iih",
                                    "tcpdump_filter": "isis",
                                    "notes": "Observar el campo IS Neighbors TLV (6) que lista los System-ID vistos."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IS-IS CLNS: Los IIH contienen los System-ID de los vecinos visibles en el TLV 6 (IS Neighbors).",
                                "checks": "Verificar que el TLV 6 del IIH de B contiene el System-ID de A.",
                                "anomalies": "TLV 6 vacío o con System-ID incorrecto indica problema de recepción en B o transmisión en A.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.iih",
                                    "tcpdump_filter": "isis",
                                    "notes": "Wireshark decodifica IS Neighbors TLV mostrando los SNPA (MAC) de los vecinos."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (IS-IS)",
                                "detail": "Estado de adyacencia = UP. Se inicia el intercambio de CSNP para sincronizar la LSDB.",
                                "checks": "Comando 'show isis neighbors' debe mostrar estado UP y tipo L2. Verificar el DIS election.",
                                "anomalies": "Adyacencia UP pero sin rutas indica problema en el flooding de LSP posterior.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.iih",
                                    "tcpdump_filter": "isis",
                                    "notes": "Confirmar que el campo Priority y LAN ID corresponden al DIS electo."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 4: Router A origina LSP",
                        "device": "Router A",
                        "action": "Genera un Link-State Protocol Data Unit (LSP) con los prefijos directamente conectados y los métricos.",
                        "note": "Cada LSP tiene un LSP-ID compuesto por System-ID + Pseudonode-ID + Fragment Number. Sequence number incrementa con cada nueva versión.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet multicast 01:80:C2:00:00:15 (L2) o unicast dependiendo de la topología (broadcast vs p2p).",
                                "checks": "Verificar que la interfaz permita la transmisión de multicast IS-IS y que no haya rate-limiting.",
                                "anomalies": "Ausencia de tramas LSP indica que el router no tiene información para anunciar o el proceso IS-IS está atorado.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.lsp",
                                    "tcpdump_filter": "isis",
                                    "notes": "En Wireshark usar isis.l2.lsp para filtrar solo LSPs de nivel 2."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IS-IS CLNS: PDU Type = 20 (L2 LSP). LSP-ID = System-ID.00-00. Remaining Lifetime, Sequence Number, Checksum.",
                                "checks": "Verificar que el LSP-ID sea válido y que el Remaining Lifetime no esté expirado.",
                                "anomalies": "Remaining Lifetime = 0 indica LSP purgado. Sequence Number wrap-around puede causar rechazo temporal.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.lsp",
                                    "tcpdump_filter": "isis",
                                    "notes": "Wireshark muestra LSP-ID, Sequence Number y Remaining Lifetime."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (IS-IS)",
                                "detail": "LSP contiene TLVs: IP Reachability (128/130 para narrow, 135 para wide), Extended IS Reachability (22), Authentication (10).",
                                "checks": "Verificar que los prefijos IP estén presentes en los TLVs de reachability. Métricas coherentes.",
                                "anomalies": "Prefijos faltantes indican que no están incluidos en el proceso IS-IS. Métrica wide vs narrow mismatch causa rutas incorrectas.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.lsp",
                                    "tcpdump_filter": "isis",
                                    "notes": "Expandir TLV 135 (Extended IP Reachability) para ver prefijos y métricas."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 5: Sincronización PSNP/CSNP",
                        "device": "Router B (y DIS si aplica)",
                        "action": "En broadcast, el DIS envía CSNP periódicamente. Los routers solicitan LSPs faltantes con PSNP.",
                        "note": "CSNP = Complete Sequence Number PDU (resumen de todos los LSPs). PSNP = Partial Sequence Number PDU (solicitud o ack).",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "CSNP se envía en multicast 01:80:C2:00:00:15. PSNP puede ser multicast o unicast.",
                                "checks": "Verificar que el DIS esté transmitiendo CSNP periódicamente (cada 10 segundos en broadcast).",
                                "anomalies": "DIS no envía CSNP indica fallo del DIS o proceso IS-IS detenido. CSNP con entries faltantes indica desincronización.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.csnp or isis.l2.psnp",
                                    "tcpdump_filter": "isis",
                                    "notes": "Wireshark diferencia CSNP y PSNP por el PDU Type."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IS-IS CLNS: CSNP (PDU Type 25), PSNP (PDU Type 26). Contienen lista de LSP summaries (LSP-ID, Sequence Number, Checksum, Remaining Lifetime).",
                                "checks": "Comparar el CSNP recibido con la LSDB local. Identificar LSP-ID faltantes o con Sequence Number diferente.",
                                "anomalies": "CSNP incompleto o PSNP sin respuesta indica pérdida de paquetes o congestión.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.csnp or isis.l2.psnp",
                                    "tcpdump_filter": "isis",
                                    "notes": "En Wireshark expandir LSP Entries para ver el resumen."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (IS-IS)",
                                "detail": "Sincronización: B recibe CSNP, compara con su LSDB, envía PSNP solicitando LSPs específicos. A responde con el LSP completo.",
                                "checks": "Verificar que la LSDB esté sincronizada ('show isis database'). Todos los LSP deben tener el mismo Sequence Number.",
                                "anomalies": "LSDB no sincronizada causa rutas inconsistentes. LSP con Sequence Number menor indica información obsoleta.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.psnp",
                                    "tcpdump_filter": "isis",
                                    "notes": "Wireshark muestra las entradas LSP solicitadas en el PSNP."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 6: Cálculo SPF",
                        "device": "Router A y Router B",
                        "action": "Ejecutan el algoritmo SPF (Dijkstra) sobre la LSDB sincronizada para calcular el shortest path tree.",
                        "note": "IS-IS mantiene una LSDB por nivel (L1 y L2). SPF se ejecuta independientemente para cada nivel.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Proceso interno de CPU. No hay tráfico de red durante el cálculo SPF propiamente dicho.",
                                "checks": "Monitorear CPU durante el cálculo. Verificar que no haya flapping de interfaces causando SPF frecuentes.",
                                "anomalies": "CPU al 100% por SPF indica inestabilidad de red o LSDB excesivamente grande.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis",
                                    "tcpdump_filter": "isis",
                                    "notes": "Capturar durante la convergencia para identificar la causa del recálculo (ej. LSP flooding masivo)."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "Construcción del SPT usando los nodos (System-ID) y enlaces (IS Reachability TLV 22) de la LSDB.",
                                "checks": "Verificar que el SPT incluya todos los routers alcanzables y que las métricas sean coherentes.",
                                "anomalies": "Nodos faltantes en el SPT indican LSP no recibidos o rechazados por checksum error.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.lsp",
                                    "tcpdump_filter": "isis",
                                    "notes": "Revisar métricas en TLV 22 (Extended IS Reachability) de los LSP capturados."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (IS-IS)",
                                "detail": "SPF calcula las rutas óptimas. Los prefijos IP se extraen de los LSP y se instalan en la RIB con la métrica acumulada.",
                                "checks": "Verificar que el resultado del SPF genere rutas IS-IS en la tabla de enrutamiento.",
                                "anomalies": "Rutas faltantes pueden deberse a prefijos no incluidos en IS-IS, filtrado de políticas, o next-hop inalcanzable.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.lsp",
                                    "tcpdump_filter": "isis",
                                    "notes": "Correlacionar los prefijos en TLV 135 con las rutas instaladas."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 7: Instalación de ruta",
                        "device": "Router A y Router B",
                        "action": "Instalan las rutas IS-IS en la tabla de enrutamiento global (RIB) y opcionalmente en el FIB para forwarding.",
                        "note": "IS-IS utiliza el System-ID como identificador del next-hop a nivel CLNS, pero el forwarding IP usa la dirección MAC del next-hop.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Para forwarding IP, se resuelve la MAC del next-hop vía ARP (IPv4) o ND (IPv6) sobre la interfaz de salida.",
                                "checks": "Verificar tabla ARP/ND del next-hop. Confirmar que la MAC del next-hop es alcanzable físicamente.",
                                "anomalies": "Entrada ARP faltante indica que el next-hop IP no responde o no existe en el segmento.",
                                "packet_capture": {
                                    "wireshark_display_filter": "arp",
                                    "tcpdump_filter": "arp",
                                    "notes": "Verificar que ARP resuelve la MAC del next-hop IS-IS."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "La ruta IS-IS se instala con código 'i' (L1) o 'I' (L2) en la RIB. El next-hop es la IP del vecino directo.",
                                "checks": "Ejecutar 'show ip route' y verificar rutas IS-IS con métrica y next-hop correctos.",
                                "anomalies": "Ruta con next-hop inalcanzable no se instala. Ruta con mejor distancia administrativa (ej. OSPF) puede preferirse.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis.l2.lsp",
                                    "tcpdump_filter": "isis",
                                    "notes": "Revisar el campo Default Metric en los LSP para validar la métrica de la ruta."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (IS-IS)",
                                "detail": "El proceso IS-IS interactúa con el RIB Manager. Si se usa MPLS, se pueden generar entradas en el LIB/LFIB.",
                                "checks": "Verificar que el prefijo destino y la métrica coincidan con el LSP originado. Revisar políticas de route leaking L1-L2.",
                                "anomalies": "Route leaking mal configurado impide que prefijos L1 sean visibles en L2 o viceversa. Falta de rutas indica problema de redistribución.",
                                "packet_capture": {
                                    "wireshark_display_filter": "isis",
                                    "tcpdump_filter": "isis",
                                    "notes": "Para troubleshooting avanzado, verificar TLV 128/130 vs TLV 135 (narrow vs wide metrics)."
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "bgp": {
        "scenarios": [
            {
                "id": "bgp_ebgp_open_update",
                "name": "BGP - Intercambio OPEN y UPDATE eBGP",
                "description": "Escenario de troubleshooting del establecimiento de sesión BGP externa entre dos peers de sistemas autónomos distintos, incluyendo el intercambio de mensajes OPEN, KEEPALIVE y UPDATE con NLRI.",
                "steps": [
                    {
                        "step_title": "Paso 1: Router A envía OPEN (AS 100)",
                        "device": "Router A",
                        "action": "Inicia la sesión BGP enviando un mensaje OPEN a través de la conexión TCP hacia el puerto 179 de Router B.",
                        "note": "El mensaje OPEN debe contener el AS number, BGP Identifier (Router ID), Hold Time, y parámetros opcionales (capabilities).",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet: MAC origen = Router A; MAC destino = Router B (o gateway); EtherType = 0x0800.",
                                "checks": "Verificar que la interfaz de A tenga conectividad directa o a través del gateway de siguiente salto.",
                                "anomalies": "MAC destino desconocida (incomplete ARP) impide el envío del segmento TCP SYN inicial.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 1",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Esperar a que el three-way handshake TCP se complete antes de ver el OPEN."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "Encabezado IP: Protocolo = 6 (TCP); IP origen = A; IP destino = B; TTL depende de si es directo o multihop.",
                                "checks": "Verificar que las IPs de origen y destino sean alcanzables. En eBGP multihop, verificar TTL y rutas.",
                                "anomalies": "TTL expirado en eBGP directo indica más de un salto. Filtrado de IP o NAT altera la sesión.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.proto == 6 and tcp.dstport == 179 and bgp.type == 1",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "El OPEN llega después de que TCP esté establecido."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "TCP: Puerto origen = efímero (>1024); Puerto destino = 179; Flags = PSH, ACK; Seq/Ack numbers válidos.",
                                "checks": "Confirmar que el three-way handshake se completó. No debe haber retransmisiones antes del OPEN.",
                                "anomalies": "RST enviado por B indica que no hay proceso BGP escuchando en 179. SYN retransmitido indica filtrado de TCP 179.",
                                "packet_capture": {
                                    "wireshark_display_filter": "tcp.port == 179 and bgp.type == 1",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Verificar que no haya TCP RST inmediatamente después del SYN."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "BGP OPEN: Marker = 16 bytes 0xFF; Length; Type = 1; Version = 4; My AS = 100; Hold Time; BGP Identifier; Optional Parameters (capabilities: MP-BGP, Route Refresh, 4-octet AS).",
                                "checks": "Verificar AS 100, Hold Time (típicamente 180s), BGP Identifier único, y capabilities deseadas.",
                                "anomalies": "Versión BGP distinta (ej. 3), AS number incorrecto, o BGP Identifier duplicado causan NOTIFICATION y cierre.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 1",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Wireshark decodifica los Optional Parameters mostrando capabilities como MP-BGP AFI/SAFI."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 2: Router B responde con OPEN (AS 200)",
                        "device": "Router B",
                        "action": "Responde con su propio mensaje BGP OPEN confirmando AS 200, hold time, y capabilities soportadas.",
                        "note": "Router B debe coincidir en número de AS esperado para el peer. Si A envió AS 100 pero B espera otro, envía NOTIFICATION.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet desde B hacia A (o su gateway). MAC origen = B; MAC destino = A.",
                                "checks": "Verificar bidireccionalidad de capa 2. Asegurar que no haya asimetría en el camino de retorno.",
                                "anomalies": "Tramas de retorno perdidas indican problema de switch o spanning tree unidireccional.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 1 and ip.src == <IP_B>",
                                    "tcpdump_filter": "src host <IP_B> and tcp port 179",
                                    "notes": "Capturar en ambos extremos para confirmar llegada del OPEN de B."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP: Protocolo = 6 (TCP); origen = B; destino = A; TTL apropiado.",
                                "checks": "Verificar que la IP de B sea la esperada por A. En eBGP multihop, verificar source-interface.",
                                "anomalies": "IP origen inesperada causa rechazo. Políticas de ruteo asimétrico o load-balancing pueden afectar.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.src == <IP_B> and tcp.dstport == 179 and bgp.type == 1",
                                    "tcpdump_filter": "src host <IP_B> and tcp port 179",
                                    "notes": "El OPEN de B debe llegar por la misma sesión TCP establecida."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "TCP: Puerto origen = 179 (si B es pasivo) o efímero; Puerto destino = efímero de A; Flags = PSH, ACK.",
                                "checks": "Confirmar que la sesión TCP permanece establecida. No debe haber retransmisiones excesivas.",
                                "anomalies": "TCP window zero indica congestión. Retransmisiones indican pérdida de paquetes en el camino.",
                                "packet_capture": {
                                    "wireshark_display_filter": "tcp.port == 179 and bgp.type == 1",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Verificar que el OPEN viaje sobre la conexión TCP ya establecida."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "BGP OPEN: My AS = 200; Hold Time; BGP Identifier de B; Capabilities. Debe coincidir con lo esperado por A.",
                                "checks": "Verificar AS 200, hold time negociado (mínimo de ambos), y que las capabilities sean compatibles.",
                                "anomalies": "AS mismatch (A espera 200, B envía 200 OK, pero si B envía otro valor falla). Capability negotiation failure.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 1",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Wireshark muestra AS number y capabilities en el OPEN."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 3: Router A envía KEEPALIVE",
                        "device": "Router A",
                        "action": "Envía mensaje BGP KEEPALIVE para mantener la sesión activa y confirmar la recepción del OPEN de B.",
                        "note": "El intervalo de KEEPALIVE es típicamente 1/3 del hold time negociado. Si hold time es 180s, keepalive cada 60s.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet desde A hacia B. MACs resueltas previamente por ARP.",
                                "checks": "Verificar que ARP siga resuelto. Si ARP expira, puede haber interrupción temporal.",
                                "anomalies": "ARP timeout causa pérdida de conectividad capa 2. Interfaces flapping causan caída de sesión.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 4",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "KEEPALIVE es un mensaje BGP pequeño (19 bytes)."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP: Protocolo = 6; origen = A; destino = B; TTL apropiado.",
                                "checks": "Confirmar que la sesión IP permanece estable. Verificar contadores de errores en interfaces.",
                                "anomalies": "IP TTL expirado en tránsito indica loop o problema de ruteo intermedio.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.proto == 6 and bgp.type == 4",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "KEEPALIVE viaja sobre la misma sesión TCP 179."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "TCP: Flags = ACK (o PSH+ACK). No hay payload de aplicación excepto el header BGP de 19 bytes.",
                                "checks": "Verificar que el ACK number avance correctamente. Confirmar ausencia de retransmisiones.",
                                "anomalies": "TCP retransmission de keepalive indica posible congestión o descarte en el camino.",
                                "packet_capture": {
                                    "wireshark_display_filter": "tcp.port == 179 and bgp.type == 4",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "En Wireshark, bgp.type == 4 filtra KEEPALIVEs."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "BGP KEEPALIVE: Marker = 0xFF; Length = 19; Type = 4. No contiene datos adicionales.",
                                "checks": "Verificar que los keepalives se envíen periódicamente (intervalo = hold_time/3).",
                                "anomalies": "Ausencia de KEEPALIVE por más del hold time causa cierre de sesión (Hold Timer Expired).",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 4",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Wireshark muestra KEEPALIVE con longitud 19 bytes exactos."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 4: Router B envía KEEPALIVE",
                        "device": "Router B",
                        "action": "Responde con KEEPALIVE confirmando que la sesión BGP está establecida y activa en ambos sentidos.",
                        "note": "La sesión BGP está ahora en estado ESTABLISHED. Pueden comenzar a intercambiarse UPDATEs.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet desde B hacia A. ARP bidireccional debe estar resuelto.",
                                "checks": "Verificar que no haya spanning-tree bloqueando el puerto en el sentido de retorno.",
                                "anomalies": "Unidirectional link failure causa que B envíe keepalive pero A no los reciba, llevando a hold timer expired.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 4 and ip.src == <IP_B>",
                                    "tcpdump_filter": "src host <IP_B> and tcp port 179",
                                    "notes": "Verificar que el keepalive de B llega a A."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP: Protocolo = 6; origen = B; destino = A.",
                                "checks": "Confirmar que no hay filtros de IP o rate-limiting que descarten paquetes de retorno.",
                                "anomalies": "Filtrado asimétrico o firewall stateful que droppea paquetes de retorno.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.src == <IP_B> and bgp.type == 4",
                                    "tcpdump_filter": "src host <IP_B> and tcp port 179",
                                    "notes": "Capturar en A para confirmar recepción."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "TCP: Flags = ACK. Sesión TCP estable y sin errores.",
                                "checks": "Verificar que los números de secuencia TCP avancen sin saltos ni retransmisiones.",
                                "anomalies": "TCP ZeroWindow o retransmisiones indican problema de buffer o congestión en algún extremo.",
                                "packet_capture": {
                                    "wireshark_display_filter": "tcp.port == 179 and bgp.type == 4",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Verificar que el keepalive sea respondido con ACK TCP."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "BGP KEEPALIVE: Length 19; Type 4. Sesión de sesión = ESTABLISHED.",
                                "checks": "Comando 'show ip bgp summary' debe mostrar estado Established y uptime creciente.",
                                "anomalies": "Sesión flapping (establecida y caída repetidamente) indica hold time expirado o políticas route-map con error.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 4",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Una vez establecida, los keepalives deben ser periódicos y regulares."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 5: Router A envía UPDATE con NLRI",
                        "device": "Router A",
                        "action": "Envía mensaje BGP UPDATE anunciando uno o más prefijos (NLRI) con sus atributos path.",
                        "note": "En eBGP, los atributos por defecto incluyen AS_PATH con el AS local, NEXT_HOP = IP de A, ORIGIN = IGP, LOCAL_PREF no se envía (iBGP only).",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet desde A hacia B. Posible fragmentación si la ruta tiene muchos atributos o es muy larga.",
                                "checks": "Verificar MTU de la interfaz. BGP UPDATE puede ser grande si hay muchos prefijos o AS_PATH largo.",
                                "anomalies": "Fragmentación de UPDATEs grandes puede causar descarte si algún enlace intermedio tiene MTU menor.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Si hay TCP MSS adecuado, la fragmentación IP debe evitarse."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP: Protocolo = 6; origen = A; destino = B; Don't Fragment (DF) puede estar activo según configuración TCP MSS.",
                                "checks": "Verificar DF bit y tamaño del paquete. Confirmar que no exceda MTU del path.",
                                "anomalies": "ICMP Fragmentation Needed pero con DF activo indica PMTUD issue. Firewall bloqueando ICMP causa black hole.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.proto == 6 and tcp.dstport == 179 and bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Verificar tamaño del paquete en Wireshark (Len IP)."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "TCP: Puerto destino = 179; Flags = PSH, ACK; Payload = mensaje BGP UPDATE completo.",
                                "checks": "Verificar que el payload TCP coincida con el mensaje BGP. Confirmar checksum TCP válido.",
                                "anomalies": "Checksum TCP erróneo o payload truncado indica corrupción de capa 2 o descarte de buffer.",
                                "packet_capture": {
                                    "wireshark_display_filter": "tcp.port == 179 and bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Wireshark reensambla el mensaje BGP sobre el stream TCP."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "BGP UPDATE: Withdrawn Routes (vacío); Path Attributes (AS_PATH=[100], NEXT_HOP=<IP_A>, ORIGIN=igp); NLRI = [prefijos anunciados].",
                                "checks": "Verificar AS_PATH correcto, NEXT_HOP alcanzable, ORIGIN = IGP, y que los prefijos sean los esperados.",
                                "anomalies": "AS_PATH loop (si hay prepending erróneo), NEXT_HOP inalcanzable, o ORIGIN incomplete indican configuración errónea.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Wireshark decodifica NLRI, AS_PATH, NEXT_HOP, y demás atributos."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 6: Router B procesa e instala ruta",
                        "device": "Router B",
                        "action": "Recibe el UPDATE, valida los atributos BGP, ejecuta políticas (route-map/prefix-list), e instala la ruta en la RIB.",
                        "note": "B debe verificar que el AS_PATH no contenga su propio AS (loop prevention). El NEXT_HOP debe ser alcanzable.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet desde A llega a interfaz de B. Verificar estado de interfaz y contadores de errores.",
                                "checks": "Confirmar que la interfaz no tenga CRC errors, runts, o giants.",
                                "anomalies": "Errores de entrada en la interfaz indican problema de cable o transcoding.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2 and ip.src == <IP_A>",
                                    "tcpdump_filter": "src host <IP_A> and tcp port 179",
                                    "notes": "Capturar en B para verificar recepción del UPDATE."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP entrega el segmento TCP al puerto 179. Verificar que no haya filtrado de IP o NAT.",
                                "checks": "Verificar que la IP de A no está siendo traducida (NAT) de forma que invalide la sesión BGP.",
                                "anomalies": "Cambio de IP origen por NAT rompe la sesión BGP o causa que B rechace el UPDATE.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.src == <IP_A> and bgp.type == 2",
                                    "tcpdump_filter": "src host <IP_A> and tcp port 179",
                                    "notes": "Confirmar IP origen consistente durante toda la sesión."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "TCP entrega el payload BGP al proceso BGP de B. Verificar que el ACK correspondiente sea enviado.",
                                "checks": "Verificar que B envíe ACK TCP por el UPDATE recibido.",
                                "anomalies": "Retraso en ACK o TCP window zero indica que el proceso BGP de B está saturado.",
                                "packet_capture": {
                                    "wireshark_display_filter": "tcp.port == 179 and ip.src == <IP_B> and tcp.flags.ack == 1",
                                    "tcpdump_filter": "src host <IP_B> and tcp port 179 and tcp[13] & 16 != 0",
                                    "notes": "El ACK debe seguir al UPDATE sin retraso excesivo."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "Proceso BGP valida: AS_PATH loop check, NEXT_HOP reachability, valid origin AS. Aplica inbound policies. Instala en BGP table luego en RIB si es la mejor ruta.",
                                "checks": "Ejecutar 'show ip bgp' para ver el prefijo recibido. Verificar 'show ip route' para confirmar instalación.",
                                "anomalies": "Ruta en 'show ip bgp' pero no en RIB = next-hop inalcanzable. Ruta filtrada por route-map. Ruta con AS_PATH loop descartada.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Correlacionar los atributos capturados con 'show ip bgp <prefijo>'."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 7: Intercambio continuo de KEEPALIVE",
                        "device": "Router A y Router B",
                        "action": "Ambos peers continúan enviando KEEPALIVE periódicamente para mantener la sesión BGP establecida.",
                        "note": "Si no hay cambios en NLRI, solo se intercambian KEEPALIVEs. Cualquier cambio genera un UPDATE.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Tramas Ethernet periódicas entre A y B con los KEEPALIVEs.",
                                "checks": "Verificar estabilidad de capa 2 durante minutos/horas. Sin flapping de interfaz.",
                                "anomalies": "Pérdida periódica de tramas KEEPALIVE causa hold timer expired y sesión caída.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 4",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Observar la regularidad del intervalo entre keepalives."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP entrega los segmentos TCP sin errores. Verificar contadores de drop en colas.",
                                "checks": "Verificar que no haya policers o QoS descartando paquetes BGP como best-effort.",
                                "anomalies": "Descarte de paquetes pequeños por policer agresivo puede eliminar keepalives.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.proto == 6 and bgp.type == 4",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Si hay QoS, asegurar que la clase de BGP tenga garantía de ancho de banda."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "TCP: Sesión estable sin RST ni retransmisiones. Window size estable.",
                                "checks": "Verificar que no haya TCP retransmissions ni out-of-order segments.",
                                "anomalies": "TCP retransmission indica congestión o pérdida. TCP RST indica cierre forzoso por algún extremo.",
                                "packet_capture": {
                                    "wireshark_display_filter": "tcp.analysis.retransmission or tcp.flags.reset == 1",
                                    "tcpdump_filter": "tcp port 179 and (tcp[13] & 4 != 0)",
                                    "notes": "Filtrar retransmisiones y RST para detectar inestabilidad."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "BGP KEEPALIVE periódicos. Estado = ESTABLISHED. Uptime incrementa.",
                                "checks": "'show ip bgp summary' debe mostrar uptime estable y sin incremento de counters de mensajes de NOTIFICATION.",
                                "anomalies": "Hold timer expired es la causa más común de caída silenciosa. Verificar CPU y memoria en ambos routers.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 4 or bgp.type == 3",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Un NOTIFICATION (type 3) seguido de TCP FIN/RST indica error de BGP."
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "mpbgp": {
        "scenarios": [
            {
                "id": "mp_bgp_vpnv4_exchange",
                "name": "MP-BGP - Negociación AFI/SAFI e Intercambio VPNv4",
                "description": "Escenario de troubleshooting de la negociación de capacidades MP-BGP (AFI/SAFI) y el intercambio de rutas VPNv4 con Route Distinguisher, labels MPLS y Extended Communities.",
                "steps": [
                    {
                        "step_title": "Paso 1: OPEN con capacidad MP-BGP (AFI=1, SAFI=128)",
                        "device": "Router A",
                        "action": "Envía mensaje BGP OPEN incluyendo el Optional Parameter Capability Code 1 (MP-BGP) con AFI=1 (IPv4) y SAFI=128 (Labeled VPN).",
                        "note": "La negociación MP-BGP debe ser exitosa para que ambos peers acepten rutas VPNv4. Si B no soporta MP-BGP, la sesión puede cerrarse o ignorar el capability.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet entre A y B (o a través de IBGP next-hop). MAC origen/destino resueltas.",
                                "checks": "Verificar conectividad capa 2 estable. En PE-PE, puede haber múltiples saltos L2 si hay switches intermedios.",
                                "anomalies": "ARP flapping o MAC move en switch indica inestabilidad de capa 2.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 1",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Capturar el OPEN completo. El capability MP-BGP aparece en los Optional Parameters."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP: Protocolo = 6 (TCP); origen = loopback de A (típico iBGP); destino = loopback de B; TTL = 255 o ajustado por multihop.",
                                "checks": "Verificar que las loopbacks sean alcanzables vía IGP. El next-hop para el peer debe ser la loopback.",
                                "anomalies": "IGP inestable o rutas a loopback perdidas causan fallo TCP subyacente. Filtrado de TCP 179 entre loopbacks.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.proto == 6 and tcp.dstport == 179 and bgp.type == 1",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Verificar que las IPs origen/destino sean las loopbacks configuradas para el peer."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "TCP: Puerto destino = 179; Three-way handshake completado sobre conexión iBGP entre loopbacks.",
                                "checks": "Confirmar que la sesión TCP se estableció sin errores. Verificar que no haya intermedios con MTU bajo.",
                                "anomalies": "TCP SYN retransmitido indica bloqueo de firewall o ruta inexistente a la loopback del peer.",
                                "packet_capture": {
                                    "wireshark_display_filter": "tcp.port == 179 and bgp.type == 1",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "El OPEN debe ser el primer payload BGP después del handshake."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "BGP OPEN: Version=4; My AS; Hold Time; BGP Identifier; Optional Parameters: Capability Code 1, Length 4, Value: AFI=1, Res=0, SAFI=128. También puede incluir Route Refresh (64) y Extended Next-Hop (5).",
                                "checks": "Verificar que AFI=1 (IPv4) y SAFI=128 (MPLS-labeled VPN). Confirmar que B también anuncie el mismo capability.",
                                "anomalies": "SAFI mismatch (ej. 128 vs 1) impide el intercambio VPNv4. Ausencia de capability MP-BGP indica peer no configurado para address-family vpnv4.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 1",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "En Wireshark expander BGP Optional Parameters → Capability → Multiprotocol Extensions."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 2: KEEPALIVE",
                        "device": "Router B",
                        "action": "Responde con KEEPALIVE confirmando que aceptó el OPEN y la sesión MP-BGP está activa.",
                        "note": "Si B no soporta SAFI 128, podría enviar NOTIFICATION con Unsupported Capability o simplemente no intercambiar rutas VPNv4.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet de retorno desde B hacia A. Verificar bidireccionalidad.",
                                "checks": "Asegurar que las tramas de retorno lleguen sin pérdida.",
                                "anomalies": "Spanning-tree bloqueando el puerto de retorno o unidirectional link failure.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 4 and ip.src == <IP_B>",
                                    "tcpdump_filter": "src host <IP_B> and tcp port 179",
                                    "notes": "El keepalive de B confirma que procesó el OPEN de A."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP: Protocolo = 6; origen = loopback de B; destino = loopback de A.",
                                "checks": "Verificar que la loopback de B sea alcanzable desde A vía IGP.",
                                "anomalies": "Rutas IGP asimétricas o filtrado de tráfico de retorno.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.src == <IP_B> and bgp.type == 4",
                                    "tcpdump_filter": "src host <IP_B> and tcp port 179",
                                    "notes": "Verificar que la IP origen coincida con la configuración del peer en A."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "TCP: Flags = ACK. Sesión TCP estable y confirmada bidireccionalmente.",
                                "checks": "Confirmar que no haya retransmisiones ni TCP RST.",
                                "anomalies": "TCP RST por B indica que el proceso BGP de B cerró la sesión (posiblemente por NOTIFICATION previa).",
                                "packet_capture": {
                                    "wireshark_display_filter": "tcp.port == 179 and bgp.type == 4",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Verificar que el keepalive sea respondido con ACK."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "BGP KEEPALIVE: Length 19; Type 4. Sesión en estado ESTABLISHED con capacidad MP-BGP negociada.",
                                "checks": "'show bgp vpnv4 unicast summary' debe mostrar estado Established y AFI/SAFI vpnv4 activo.",
                                "anomalies": "Sesión Established pero sin prefixes received indica que no hay rutas para anunciar o que el peer no tiene VRF configurado.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 4",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Wireshark no diferencia keepalives de VPNv4 vs IPv4 unicast; la diferencia está en el contexto AFI/SAFI."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 3: UPDATE con MP_REACH_NLRI (VPNv4 + RD + Label)",
                        "device": "Router A",
                        "action": "Envía mensaje BGP UPDATE con el atributo MP_REACH_NLRI conteniendo prefijo VPNv4, Route Distinguisher (RD) y label MPLS.",
                        "note": "El prefijo VPNv4 se forma como RD:IPv4 (ej. 65000:1:10.0.0.0/24). El label es asignado localmente por A.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Trama Ethernet desde A hacia B. El tamaño del UPDATE puede ser mayor que un keepalive por la cantidad de información.",
                                "checks": "Verificar MTU en todo el path. El TCP MSS debe prevenir fragmentación IP.",
                                "anomalies": "Paquetes grandes fragmentados o descartados por MTU en algún enlace intermedio.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Verificar que el paquete no exceda la MTU del path."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP: Protocolo = 6; origen = loopback A; destino = loopback B. No debe haber NAT entre loopbacks.",
                                "checks": "Confirmar que las loopbacks sean enrutables y que no haya firewall descartando paquetes TCP grandes.",
                                "anomalies": "IP TTL expirado indica loop. PMTUD failure si hay tunelización y DF bit activo.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.proto == 6 and bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Verificar DF bit y longitud IP en la captura."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "TCP: Puerto destino = 179; Payload = BGP UPDATE con múltiples atributos path y NLRI codificado.",
                                "checks": "Verificar que el segmento TCP se entregue completo y sin retransmisiones.",
                                "anomalies": "TCP retransmission indica pérdida de paquetes en la red subyacente (posible congestión MPLS core).",
                                "packet_capture": {
                                    "wireshark_display_filter": "tcp.port == 179 and bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Wireshark reensambla el UPDATE sobre el stream TCP."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "BGP UPDATE: Path Attributes incluyen MP_REACH_NLRI (14) con AFI=1, SAFI=128, Next-Hop=<IP_A>, NLRI=[Label(3 bytes), RD(8 bytes), Prefix(length+IPv4)]. También ORIGIN, AS_PATH, LOCAL_PREF (si iBGP).",
                                "checks": "Verificar que el RD coincida con la configuración VRF de A. El label debe estar en el rango asignado por MPLS.",
                                "anomalies": "RD incorrecto o no configurado en B causa que la ruta no se asocie al VRF correcto. Label fuera de rango indica error de asignación MPLS.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2 and bgp.path_attribute.type == 14",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Wireshark decodifica MP_REACH_NLRI mostrando Label, RD, y Prefix por separado."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 4: Extended Communities (RT)",
                        "device": "Router A",
                        "action": "El UPDATE incluye el atributo Extended Communities (16) con Route Targets (RT) para controlar la importación/exportación del VRF.",
                        "note": "RT format: Type=0x00x2 (transitive), Global Administrator=ASN, Local Administrator=valor. Define a qué VRFs se importa la ruta en B.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Misma trama Ethernet que transporta el UPDATE. El atributo RT viaja dentro del mismo mensaje BGP.",
                                "checks": "Verificar que no haya filtrado de paquetes grandes que pudiera truncar el UPDATE.",
                                "anomalies": "Paquete truncado pierde los atributos extendidos al final del UPDATE.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "El RT es un path attribute dentro del UPDATE; no es tráfico separado."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP/TCP entrega el UPDATE completo. Verificar que no haya segmentación que cause reordenamiento.",
                                "checks": "Confirmar que todos los fragments (si los hay) lleguen y se reensamblen correctamente.",
                                "anomalies": "Fragments perdidos causan descarte del UPDATE completo por reensamblaje fallido.",
                                "packet_capture": {
                                    "wireshark_display_filter": "ip.frag or bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Preferir evitar fragmentación con TCP MSS adecuado (ej. 1460 bytes en Ethernet)."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "TCP entrega el payload BGP completo al proceso BGP de B. Verificar ACK por parte de B.",
                                "checks": "Verificar que B envíe ACK TCP por el UPDATE recibido.",
                                "anomalies": "Retraso excesivo en ACK o TCP ZeroWindow indica sobrecarga del proceso BGP en B.",
                                "packet_capture": {
                                    "wireshark_display_filter": "tcp.port == 179 and ip.src == <IP_B> and tcp.flags.ack == 1",
                                    "tcpdump_filter": "src host <IP_B> and tcp port 179 and tcp[13] & 16 != 0",
                                    "notes": "Verificar ACKs periódicos y sin retraso anormal."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "Extended Communities (Type 16): contiene Route Target(s). Ej. RT:100:1 (import), RT:100:2 (export). Puede incluir también SOO (Site of Origin).",
                                "checks": "Verificar que el RT en el UPDATE coincida con el import RT configurado en el VRF de B.",
                                "anomalies": "RT mismatch: si B no tiene configurado el mismo RT en su VRF import, descarta la ruta silenciosamente (aparece en BGP table pero no en VRF).",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2 and bgp.path_attribute.type == 16",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Wireshark decodifica Extended Communities mostrando RT en formato ASN:NN."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 5: Resolución de Next-Hop vía IGP",
                        "device": "Router B",
                        "action": "Router B debe resolver la dirección next-hop del MP_REACH_NLRI (IP de A) a través de la tabla de enrutamiento global (IGP).",
                        "note": "Si el next-hop no es alcanzable en la tabla global, la ruta VPNv4 se recibe pero no se instala en el VRF (hidden/inaccessible).",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "No hay tráfico de control nuevo. La resolución de next-hop es un proceso interno de B consultando su RIB global.",
                                "checks": "Verificar que la interfaz de salida hacia el next-hop esté operativa.",
                                "anomalies": "Interfaz de salida hacia el next-hop en DOWN impide la resolución.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "La resolución de next-hop no genera nuevos paquetes de control."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "B consulta su RIB global: ¿existe una ruta IGP (OSPF/IS-IS/EIGRP/Static) hacia la loopback de A?",
                                "checks": "Ejecutar 'show ip route <next-hop>' en B. Debe existir una ruta IGP o BGP (con next-hop recursivo alcanzable).",
                                "anomalies": "Next-hop no alcanzable = ruta VPNv4 recibida pero no instalada. Ruta al next-hop vía BGP requiere next-hop-self o redistribución.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "La causa raíz se diagnostica con 'show ip route', no directamente en el pcap del UPDATE."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "Proceso interno. No hay intercambio TCP por la resolución de next-hop.",
                                "checks": "N/A - proceso local.",
                                "anomalies": "N/A",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "No aplica captura de transporte para este paso."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "BGP marca la ruta como válida solo si el next-hop es recursivamente resuelto. El next-hop puede ser modificado con 'next-hop-self' en route-reflector o iBGP.",
                                "checks": "Verificar 'show bgp vpnv4 unicast <prefix>': debe indicar valid, best, y el next-hop resuelto.",
                                "anomalies": "Ruta con 'not usable' o 'inaccessible next-hop' indica fallo de IGP o next-hop-self no configurado.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2 and bgp.path_attribute.type == 14",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "El next-hop original está en el UPDATE. Si se usa next-hop-self, la IP será la del peer local."
                                }
                            }
                        ]
                    },
                    {
                        "step_title": "Paso 6: Instalación de ruta en VRF",
                        "device": "Router B",
                        "action": "Instala el prefijo VPNv4 en la tabla de enrutamiento del VRF correspondiente, usando el label MPLS recibido para forwarding.",
                        "note": "El prefijo se instala en la VRF routing table con next-hop = loopback de A y outgoing label = label recibido en MP_REACH_NLRI.",
                        "layers": [
                            {
                                "name": "Capa 2 - Enlace de Datos",
                                "detail": "Para forwarding de tráfico de datos: se encapsula en MPLS con el label recibido y se envía por la interfaz de salida hacia A.",
                                "checks": "Verificar que la interfaz de salida soporte MPLS (LDP/RSVP habilitado) y que el LFIB tenga entrada para el label.",
                                "anomalies": "Interfaz sin MPLS habilitado causa imposibilidad de forwardar tráfico VPN aunque la ruta esté instalada.",
                                "packet_capture": {
                                    "wireshark_display_filter": "mpls",
                                    "tcpdump_filter": "mpls",
                                    "notes": "Capturar tráfico de datos con etiqueta MPLS para verificar el label stack."
                                }
                            },
                            {
                                "name": "Capa 3 - Red",
                                "detail": "IP del paquete de datos se encapsula con label MPLS. El next-hop IGP resuelve la MAC del siguiente salto LSR.",
                                "checks": "Verificar que la tabla LFIB tenga una entrada para el label VPN con next-hop correcto y operación SWAP/PUSH.",
                                "anomalies": "Label no encontrado en LFIB genera drop. Next-hop IGP inalcanzable genera uninstall de la ruta VRF.",
                                "packet_capture": {
                                    "wireshark_display_filter": "mpls.label",
                                    "tcpdump_filter": "mpls",
                                    "notes": "En Wireshark filtrar por mpls.label == <label_value> para ver el tráfico encapsulado."
                                }
                            },
                            {
                                "name": "Capa 4 - Transporte",
                                "detail": "No aplica capa 4 para la instalación propiamente dicha. El forwarding MPLS opera entre capa 2 y 3.",
                                "checks": "N/A",
                                "anomalies": "N/A",
                                "packet_capture": {
                                    "wireshark_display_filter": "mpls",
                                    "tcpdump_filter": "mpls",
                                    "notes": "El tráfico MPLS no tiene cabecera TCP/UDP visible hasta que se hace pop del label VPN."
                                }
                            },
                            {
                                "name": "Capa 7 - Aplicación (BGP)",
                                "detail": "VRF routing table: 'show ip route vrf <name>' muestra el prefijo con código 'B' (BGP) y el next-hop/label. El prefijo es accesible para el CE conectado.",
                                "checks": "Verificar que el prefijo aparezca en la VRF de B. Revisar que el label asignado por A coincida con el recibido.",
                                "anomalies": "Prefijo no en VRF indica RT mismatch o import policy. Prefijo en VRF pero sin label indica que no se negoció MPLS correctamente.",
                                "packet_capture": {
                                    "wireshark_display_filter": "bgp.type == 2",
                                    "tcpdump_filter": "tcp port 179",
                                    "notes": "Correlacionar el label mostrado en 'show bgp vpnv4 unicast labels' con el valor capturado en MP_REACH_NLRI."
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },

  'aaa': {'scenarios': [{'description': 'Recorrido del proceso AAA mediante RADIUS: Access-Request, Access-Challenge, '
                                        'Access-Accept, y Accounting Start/Stop/Interim-Update entre NAS y servidor '
                                        'RADIUS.',
                          'id': 'radius_auth_accounting',
                          'name': 'AAA - Autenticación RADIUS y Contabilidad',
                          'steps': [{'action': 'El usuario establece una sesión Telnet, SSH o 802.1X con el NAS, que '
                                               'detecta que requiere autenticación AAA.',
                                     'device': 'NAS (Router/Switch)',
                                     'layers': [{'anomalies': 'Interfaz down, cable desconectado, errores de física (FCS, '
                                                              'runts, giants), negociación fallida.',
                                                 'checks': 'Verificar estado de interfaz (up/up), cableado correcto, '
                                                           'negociación de velocidad/dúplex, led de enlace activo.',
                                                 'detail': 'Señal eléctrica/óptica en cable Ethernet o consola. Interfaces '
                                                           'activas: Ethernet (autenticación de red) o puerto de consola '
                                                           '(acceso local).',
                                                 'name': 'Capa 1 - Física',
                                                 'packet_capture': {'notes': 'Verificar negociación de velocidad/dúplex '
                                                                             'y ausencia de errores de capa física.',
                                                                    'tcpdump_filter': 'ether proto 0x888e',
                                                                    'wireshark_display_filter': 'eapol'}},
                                                {'anomalies': 'MAC no aprendida, VLAN incorrecta, broadcast storm, '
                                                              'spanning-tree bloqueando puerto.',
                                                 'checks': 'Interfaz Up/Up. MAC de destino del NAS aprendida. VLAN de '
                                                           'autenticación correcta (si aplica).',
                                                 'detail': 'DstMAC=NAS, SrcMAC=host. EtherType=0x0800 (IPv4). Posible '
                                                           'tag 802.1Q para VLAN de management/autenticación.',
                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                 'packet_capture': {'notes': 'Verificar que el host envía tramas EAPOL '
                                                                             'o IP correctamente formadas.',
                                                                    'tcpdump_filter': 'ether host <MAC_host>',
                                                                    'wireshark_display_filter': 'eth.src == '
                                                                                                '<MAC_host>'}}],
                                     'note': 'Verificar que el método de acceso (VTY, console, dot1x) está configurado '
                                             'para usar RADIUS como método de autenticación primario.',
                                     'step_title': 'Paso 1: Usuario inicia sesión en el NAS'},
                                    {'action': 'El NAS recibe la solicitud de autenticación y genera un Access-Request '
                                               'UDP hacia el servidor RADIUS.',
                                     'device': 'NAS (Router/Switch)',
                                     'layers': [{'anomalies': 'IP del servidor RADIUS inalcanzable, puerto 1812 bloqueado '
                                                              '(firewall/ACL), shared-secret incorrecto (paquete '
                                                              'descartado por servidor).',
                                                 'checks': 'Servidor RADIUS configurado y alcanzable. UDP 1812 permitido '
                                                           'en ambas direcciones. Shared-secret coincide.',
                                                 'detail': 'SrcIP=interfaz NAS, DstIP=servidor RADIUS. Protocol=UDP '
                                                           '(17). TTL=X. IP Checksum válido.',
                                                 'name': 'Capa 3 - Red (IPv4)',
                                                 'packet_capture': {'notes': 'Verificar IP origen/destino y que el '
                                                                             'paquete sale por la interfaz correcta.',
                                                                    'tcpdump_filter': 'host <IP_RADIUS> and udp port 1812',
                                                                    'wireshark_display_filter': 'ip.dst == '
                                                                                                '<IP_RADIUS> and '
                                                                                                'udp.port == 1812'}},
                                                {'anomalies': 'Puerto origen no efímero, NAT alterando puerto origen, '
                                                              'fragmentación UDP (evitar).',
                                                 'checks': 'Puerto origen efímero (>1024). DstPort=1812. Sin '
                                                           'fragmentación. Checksum UDP válido.',
                                                 'detail': 'SrcPort=efímero (NAS), DstPort=1812 (Authentication). '
                                                           'RADIUS Access-Request: Code=1, Identifier=secuencia, '
                                                           'Length=variable, Authenticator=16 bytes aleatorios, '
                                                           'Attribute-Value Pairs (AVPs): User-Name, User-Password '
                                                           '(encriptado con MD5/shared-secret), NAS-IP-Address, '
                                                           'NAS-Port, Service-Type, etc.',
                                                 'name': 'Capa 4 - Transporte (UDP/RADIUS)',
                                                 'packet_capture': {'notes': 'Filtrar RADIUS Access-Request (Code=1). '
                                                                             'Verificar que AVPs están presentes.',
                                                                    'tcpdump_filter': 'udp port 1812',
                                                                    'wireshark_display_filter': 'radius.code == 1'}}],
                                     'note': 'Si el NAS no tiene conectividad IP con el servidor RADIUS, cae al método '
                                             'de autenticación de backup (local/tacacs).',
                                     'step_title': 'Paso 2: NAS envía Access-Request al servidor RADIUS'},
                                    {'action': 'El servidor RADIUS evalúa las credenciales y responde Access-Accept '
                                               '(autenticación exitosa) o Access-Reject.',
                                     'device': 'Servidor RADIUS',
                                     'layers': [{'anomalies': 'Servidor caído, proceso radiusd detenido, base de datos '
                                                              'de usuarios inaccesible, shared-secret mismatch.',
                                                 'checks': 'Servidor RADIUS operativo. Base de datos de usuarios '
                                                           'accesible. Shared-secret coincide con NAS.',
                                                 'detail': 'Servidor RADIUS recibe Access-Request, verifica '
                                                           'Authenticator (recomputa MD5(shared-secret + '
                                                           'Authenticator_request)), descifra User-Password, consulta '
                                                           'base de datos.',
                                                 'name': 'Capa 7 - Aplicación (RADIUS Server)',
                                                 'packet_capture': {'notes': 'Verificar en servidor que llega '
                                                                             'Access-Request y se genera respuesta.',
                                                                    'tcpdump_filter': 'udp port 1812',
                                                                    'wireshark_display_filter': 'radius.code == 1'}},
                                                {'anomalies': 'Access-Reject por contraseña incorrecta, usuario '
                                                              'deshabilitado, caducidad de cuenta, política de acceso '
                                                              'no cumplida.',
                                                 'checks': 'Usuario existe y está habilitado. Contraseña correcta. '
                                                           'Políticas de acceso (horario, origen) cumplidas.',
                                                 'detail': 'Access-Accept: Code=2, Identifier=mismo que request, '
                                                           'Authenticator=MD5(Code+ID+Length+Auth_req+attributes+secret), '
                                                           'AVPs: Service-Type, Session-Timeout, Filter-Id, etc. '
                                                           'Access-Reject: Code=3.',
                                                 'name': 'Capa 7 - Aplicación (Respuesta RADIUS)',
                                                 'packet_capture': {'notes': 'Filtrar Access-Accept (Code=2) y '
                                                                             'Access-Reject (Code=3). Verificar '
                                                                             'consistencia de Identifier.',
                                                                    'tcpdump_filter': 'udp port 1812',
                                                                    'wireshark_display_filter': 'radius.code == 2 or '
                                                                                                'radius.code == 3'}}],
                                     'note': 'En algunos casos el servidor responde Access-Challenge (Code=11) para '
                                             'autenticación multi-factor (EAP/MS-CHAPv2).',
                                     'step_title': 'Paso 3: Servidor responde Access-Accept o Access-Reject'},
                                    {'action': 'Tras autenticación exitosa, el NAS envía Accounting-Request Start al '
                                               'servidor de contabilidad.',
                                     'device': 'NAS (Router/Switch)',
                                     'layers': [{'anomalies': 'Puerto 1813 bloqueado, servidor contable diferente al de '
                                                              'autenticación inalcanzable, shared-secret diferente '
                                                              'incorrecto.',
                                                 'checks': 'Servidor de accounting configurado y alcanzable. UDP 1813 '
                                                           'permitido. Shared-secret coincide.',
                                                 'detail': 'SrcIP=interfaz NAS, DstIP=servidor contable. Protocol=UDP. '
                                                           'Misma ruta IP que autenticación o diferente según '
                                                           'configuración.',
                                                 'name': 'Capa 3 - Red (IPv4)',
                                                 'packet_capture': {'notes': 'Verificar que paquetes de accounting usan '
                                                                             'el puerto 1813 y llegan al servidor '
                                                                             'correcto.',
                                                                    'tcpdump_filter': 'udp port 1813',
                                                                    'wireshark_display_filter': 'udp.port == 1813'}},
                                                {'anomalies': 'Acct-Session-Id duplicado, atributos de accounting '
                                                              'incompletos, NAS no recibe Accounting-Response.',
                                                 'checks': 'Acct-Session-Id único. Atributos: Acct-Status-Type=1 (Start), '
                                                           'User-Name, NAS-IP-Address, NAS-Port, Service-Type, '
                                                           'Framed-IP-Address (si asignado).',
                                                 'detail': 'Accounting-Request Start: Code=4, Acct-Status-Type=1 '
                                                           '(Start). Indica inicio de sesión. Si es asignación de IP, '
                                                           'incluye Framed-IP-Address.',
                                                 'name': 'Capa 4 - Transporte (UDP/RADIUS Accounting)',
                                                 'packet_capture': {'notes': 'Filtrar Accounting-Request (Code=4). '
                                                                             'Verificar Acct-Status-Type=1.',
                                                                    'tcpdump_filter': 'udp port 1813',
                                                                    'wireshark_display_filter': 'radius.code == 4'}}],
                                     'note': 'El NAS debe recibir Accounting-Response (Code=5) del servidor. Si no la '
                                             'recibe, retransmite el Accounting-Request.',
                                     'step_title': 'Paso 4: NAS envía Accounting-Request Start'},
                                    {'action': 'Durante la sesión activa, el NAS envía periódicamente Accounting-Request '
                                               'Interim-Update.',
                                     'device': 'NAS (Router/Switch) / Servidor RADIUS',
                                     'layers': [{'anomalies': 'Interim-Update no enviados (intervalo desconfigurado), '
                                                              'contadores no incrementan, Acct-Session-Id cambia '
                                                              '(sesión rota).',
                                                 'checks': 'Intervalo de interim configurado (ej: cada 10 min). '
                                                           'Contadores Acct-Input-Octets/Output-Octets crecen. '
                                                           'Acct-Session-Id consistente.',
                                                 'detail': 'Accounting-Request Interim-Update: Code=4, '
                                                           'Acct-Status-Type=3 (Interim-Update). Incluye contadores '
                                                           'acumulados: Acct-Input-Octets, Acct-Output-Octets, '
                                                           'Acct-Input-Packets, Acct-Output-Packets, Acct-Session-Time.',
                                                 'name': 'Capa 4 - Transporte (UDP/RADIUS Interim)',
                                                 'packet_capture': {'notes': 'Verificar periodicidad de Interim-Update. '
                                                                             'Cada request debe tener Acct-Session-Id '
                                                                             'igual al Start.',
                                                                    'tcpdump_filter': 'udp port 1813',
                                                                    'wireshark_display_filter': 'radius.code == 4 and '
                                                                                                'radius.avp.acct_status '
                                                                                                '== 3'}}],
                                     'note': 'El servidor debe responder con Accounting-Response (Code=5) para cada '
                                             'Interim-Update. La ausencia de respuesta indica pérdida de paquetes o '
                                             'servidor contable saturado.',
                                     'step_title': 'Paso 5: Interim-Update periódicos durante la sesión'},
                                    {'action': 'Al cerrar la sesión (logout, desconexión, timeout), el NAS envía '
                                               'Accounting-Request Stop.',
                                     'device': 'NAS (Router/Switch)',
                                     'layers': [{'anomalies': 'Accounting-Request Stop no enviado (NAS reiniciado, '
                                                              'interfaz caída bruscamente), contadores finales en cero '
                                                              '(no se midió tráfico).',
                                                 'checks': 'NAS envía Stop al cerrar sesión. Contadores finales reflejan '
                                                           'tráfico total. Acct-Session-Time > 0. Acct-Terminate-Cause '
                                                           'presente.',
                                                 'detail': 'Accounting-Request Stop: Code=4, Acct-Status-Type=2 (Stop). '
                                                           'Incluye contadores finales y Acct-Terminate-Cause '
                                                           '(User-Request, Idle-Timeout, Session-Timeout, '
                                                           'NAS-Request, etc.).',
                                                 'name': 'Capa 4 - Transporte (UDP/RADIUS Stop)',
                                                 'packet_capture': {'notes': 'Filtrar Accounting-Request Stop '
                                                                             '(Acct-Status-Type=2). Verificar que '
                                                                             'contadores finales son consistentes con '
                                                                             'Interim-Updates previos.',
                                                                    'tcpdump_filter': 'udp port 1813',
                                                                    'wireshark_display_filter': 'radius.code == 4 and '
                                                                                                'radius.avp.acct_status '
                                                                                                '== 2'}}],
                                     'note': 'Es crítico que el servidor reciba el Stop para cerrar la sesión '
                                             'contable. Si se pierde, la sesión queda huérfana hasta timeout del '
                                             'servidor.',
                                     'step_title': 'Paso 6: Accounting-Request Stop al finalizar sesión'}]},
                            {'description': 'Recorrido del proceso AAA con TACACS+ en lugar de RADIUS. TACACS+ usa TCP '
                                            'puerto 49 y separa autenticación, autorización y accounting en diferentes '
                                            'tipos de paquetes.',
                             'id': 'tacacs_authz_acct',
                             'name': 'AAA - Autenticación/Autorización TACACS+',
                             'steps': [{'action': 'El NAS inicia conexión TCP hacia el servidor TACACS+ para autenticar '
                                                  'al usuario.',
                                        'device': 'NAS (Router/Switch)',
                                        'layers': [{'anomalies': 'Servidor TACACS+ inalcanzable, puerto TCP 49 bloqueado, '
                                                                 'SYN no respondido (servidor caído).',
                                                    'checks': 'Conectividad IP con servidor TACACS+. TCP 49 permitido. '
                                                              'Proceso tacacs+ operativo en servidor.',
                                                    'detail': 'SrcIP=interfaz NAS, DstIP=servidor TACACS+. Protocol=TCP. '
                                                              'SYN→SYN-ACK→ACK. TCP SrcPort=efímero, DstPort=49.',
                                                    'name': 'Capa 4 - Transporte (TCP/TACACS+)',
                                                    'packet_capture': {'notes': 'Filtrar TCP puerto 49. Verificar '
                                                                                'handshake SYN/SYN-ACK.',
                                                                       'tcpdump_filter': 'tcp port 49',
                                                                       'wireshark_display_filter': 'tcp.port == 49'}}],
                                        'note': 'TACACS+ usa TCP en lugar de UDP, lo que garantiza entrega confiable.',
                                        'step_title': 'Paso 1: NAS establece conexión TCP con servidor TACACS+'},
                                       {'action': 'El NAS envía TACACS+ Authentication START packet con credenciales del '
                                                  'usuario.',
                                        'device': 'NAS (Router/Switch)',
                                        'layers': [{'anomalies': 'Shared-secret incorrecto (paquete descartado), versión '
                                                                 'de TACACS+ incompatible, tipo de autenticación no '
                                                                 'soportado.',
                                                    'checks': 'Versión TACACS+ compatible (0xc0). Shared-secret '
                                                              'configurado correctamente.',
                                                    'detail': 'TACACS+ Header: Version=0xc0 (major=0xc0), Type=1 '
                                                              '(Authentication), Seq=1, Flags=0. Payload encriptado con '
                                                              'shared-secret.',
                                                    'name': 'Capa 7 - Aplicación (TACACS+ Auth)',
                                                    'packet_capture': {'notes': 'Verificar handshake TCP exitoso antes '
                                                                                'de TACACS+. Filtrar paquetes TACACS+ '
                                                                                'post-SYN.',
                                                                       'tcpdump_filter': 'tcp port 49',
                                                                       'wireshark_display_filter': 'tcp.port == 49'}}],
                                        'note': 'TACACS+ encripta todo el payload, no solo la contraseña como en '
                                                'RADIUS.',
                                        'step_title': 'Paso 2: NAS envía Authentication START'},
                                       {'action': 'El servidor responde con Authentication PASS o FAIL.',
                                        'device': 'Servidor TACACS+',
                                        'layers': [{'anomalies': 'Usuario no encontrado, contraseña incorrecta, '
                                                                 'autorización denegada por política.',
                                                    'checks': 'Usuario existe en base de datos. Permisos correctos. '
                                                              'Políticas de acceso cumplidas.',
                                                    'detail': 'Authentication REPLY: Status=PASS (0x01) o FAIL (0x02). '
                                                              'Puede incluir mensaje al usuario.',
                                                    'name': 'Capa 7 - Aplicación (Respuesta TACACS+)',
                                                    'packet_capture': {'notes': 'Verificar respuesta del servidor tras '
                                                                                'Authentication START.',
                                                                       'tcpdump_filter': 'tcp port 49',
                                                                       'wireshark_display_filter': 'tcp.port == 49'}}],
                                        'note': 'Si es PASS, el NAS procede a enviar Authorization REQUEST para '
                                                'verificar qué comandos puede ejecutar el usuario.',
                                        'step_title': 'Paso 3: Servidor responde PASS/FAIL'},
                                       {'action': 'Tras autenticación exitosa, el NAS consulta autorización para '
                                                  'comandos específicos.',
                                        'device': 'NAS (Router/Switch)',
                                        'layers': [{'anomalies': 'Servidor no responde a Authorization REQUEST, políticas '
                                                                 'mal configuradas (usuario sin permisos).',
                                                    'checks': 'Authorization REQUEST enviado correctamente. Servidor '
                                                              'responde con AV pairs de autorización.',
                                                    'detail': 'Authorization REQUEST: Type=2 (Authorization), Seq=1, '
                                                              'incluye user, port, rem_addr, service, cmd.',
                                                    'name': 'Capa 7 - Aplicación (TACACS+ Authorization)',
                                                    'packet_capture': {'notes': 'Verificar que después de PASS viene '
                                                                                'Authorization REQUEST y REPLY.',
                                                                       'tcpdump_filter': 'tcp port 49',
                                                                       'wireshark_display_filter': 'tcp.port == 49'}}],
                                        'note': 'La separación de auth y authz es la ventaja principal de TACACS+ '
                                                'sobre RADIUS.',
                                        'step_title': 'Paso 4: Autorización de comandos'}]}]},

  'fiber_ont': {'scenarios': [{'description': 'Recorrido completo del establecimiento de una sesión GPON desde la ONT '
                                                'del suscriptor, pasando por el splitter óptico pasivo, hasta la OLT '
                                                '(ADTRAN TA5000 o similar), incluyendo ranging, registro OMCI, '
                                                'asignación de T-CONT, GEM ports, VLAN, y tráfico Ethernet/PPPoE.',
                                'id': 'gpon_ont_to_olt_session',
                                'name': 'GPON/FTTH - Establecimiento de sesión desde ONT hasta OLT',
                                'steps': [{'action': 'La ONT se enciende y comienza el proceso de ranging para sincronizar '
                                                     'su distancia óptica con la OLT.',
                                           'device': 'ONT del suscriptor',
                                           'layers': [{'anomalies': 'Fibra cortada, conector sucio/dañado, atenuación '
                                                                'excesiva (>28 dBm), splitter mal conectado.',
                                                       'checks': 'Nivel óptico RX en ONT dentro de rango (-8 a -27 dBm). '
                                                                 'Láser ONT TX operativo. Conector LC/APC limpio.',
                                                       'detail': 'Señal óptica 1490 nm (downstream) desde OLT. La ONT '
                                                                 'mide potencia RX y ajusta su TX (1310 nm) para que la '
                                                                 'OLT reciba niveles aceptables.',
                                                       'name': 'Capa 1 - Física (Óptica GPON)',
                                                       'packet_capture': {'notes': 'No capturable electrónicamente. '
                                                                                   'Usar OTDR o power meter óptico. '
                                                                                   'Verificar conectorizado en splitter '
                                                                                   'y ODF.',
                                                                          'tcpdump_filter': 'N/A',
                                                                          'wireshark_display_filter': 'N/A'}},
                                                      {'anomalies': 'Ranging falla (equidistante no alcanzable), ONT '
                                                                'no responde a Serial Number request, LOID incorrecto.',
                                                       'checks': 'ONT en estado O1 (initial ranging) → O2 (ranging '
                                                                 'complete) → O3 (ranging succcess) → O4 (operation '
                                                                 'state).',
                                                       'detail': 'La OLT envía downstream frames con broadcast GEM '
                                                                 'Port-ID. La ONT responde con upstream burst usando '
                                                                 'el timeslot asignado. Serial Number o LOID '
                                                                 'configurado correctamente en ONT para que la OLT lo '
                                                                 'identifique.',
                                                       'name': 'Capa 2 - Enlace de Datos (GPON TC Layer)',
                                                       'packet_capture': {'notes': 'No es Ethernet estándar. '
                                                                                   'Requiere analizador de tráfico GPON '
                                                                                   'especializado (exparo) o mirroring '
                                                                                   'en OLT.',
                                                                          'tcpdump_filter': 'N/A',
                                                                          'wireshark_display_filter': 'N/A'}}],
                                           'note': 'La ONT debe estar configurada con el mismo Serial Number/LOID que '
                                                   'la OLT tiene provisionado.',
                                           'step_title': 'Paso 1: Ranging y registro de ONT en la OLT'},
                                          {'action': 'Tras el ranging exitoso, la OLT establece el canal de management '
                                                     'OMCI (ONT Management and Control Interface).',
                                           'device': 'OLT / ONT',
                                           'layers': [{'anomalies': 'OMCI no establece (GEM port de management no '
                                                                'configurado), mensajes OMCI perdidos, MIB sync falla.',
                                                       'checks': 'GEM Port de OMCI activo en OLT. ONT responde a '
                                                                 'Get/Set requests. MIB de ONT sincronizada con OLT.',
                                                       'detail': 'OMCI corre sobre GEM Port-ID 4095 (o similar, '
                                                                 'vendor-specific). La OLT configura la ONT '
                                                                 'remotamente: servicios, VLANs, GEM ports, '
                                                                 'bridging, QoS. Protocolo GPON OMCI (ITU-T G.988).',
                                                       'name': 'Capa 2 - Enlace de Datos (OMCI/GEM)',
                                                       'packet_capture': {'notes': 'OMCI no es capturable con '
                                                                                   'Wireshark/tcpdump estándar. Usar OMCI '
                                                                                   'debug/trace en CLI de OLT.',
                                                                          'tcpdump_filter': 'N/A',
                                                                          'wireshark_display_filter': 'N/A'}}],
                                           'note': 'OMCI es crítico para el provisioning. Si OMCI falla, la ONT no '
                                                   'puede recibir configuración de servicios.',
                                           'step_title': 'Paso 2: Establecimiento de canal OMCI'},
                                          {'action': 'La OLT configura GEM Ports para datos y los mapea a service-ports '
                                                     'o bridges con VLANs específicas.',
                                           'device': 'OLT (ADTRAN TA5000 / Huawei / ZTE / Zhone)',
                                           'layers': [{'anomalies': 'GEM Port no creado, VLAN mismatch, service-port no '
                                                                'vinculado al puerto PON, VLAN stacking (QinQ) mal '
                                                                'configurado.',
                                                       'checks': 'GEM Port creado y activo. Service-port/bridge '
                                                                 'configurado con VLAN correcta. ONT en estado Active.',
                                                       'detail': 'Cada servicio (Internet, VoIP, IPTV) tiene su propio '
                                                                 'GEM Port. La OLT mapea GEM Port-ID a una VLAN '
                                                                 '(untagged, tagged, o QinQ) en el puerto PON. Ej: '
                                                                 'GEM Port 1 → VLAN 100 (Internet), GEM Port 2 → VLAN '
                                                                 '200 (VoIP).',
                                                       'name': 'Capa 2 - Enlace de Datos (GEM/VLAN Mapping)',
                                                       'packet_capture': {'notes': 'Verificar configuración de GEM ports '
                                                                                   'y VLANs en OLT. No hay captura de '
                                                                                   'paquetes en este nivel.',
                                                                          'tcpdump_filter': 'N/A',
                                                                          'wireshark_display_filter': 'N/A'}}],
                                           'note': 'La VLAN del servicio debe coincidir entre la configuración de la '
                                                   'ONT (via OMCI) y el service-port de la OLT.',
                                           'step_title': 'Paso 3: Configuración de GEM Ports y VLANs'},
                                          {'action': 'El CPE/ Router del suscriptor conectado a la ONT inicia una sesión '
                                                     'PPPoE o solicita DHCP.',
                                           'device': 'CPE / Router del suscriptor',
                                           'layers': [{'anomalies': 'ONT no bridgea tramas (modo router), VLAN tag no '
                                                                'configurado en CPE, MAC del CPE no aprendida por ONT.',
                                                       'checks': 'ONT en modo bridge (si aplica). CPE envía tramas '
                                                                 'Ethernet correctamente. MAC aprendida en ONT.',
                                                       'detail': 'DstMAC=Broadcast (PPPoE Discovery) o MAC del router '
                                                                 'BNG (PPPoE Session). SrcMAC=CPE. EtherType=0x8863 '
                                                                 '(Discovery) o 0x8864 (Session). Posible 802.1Q tag '
                                                                 '(VLAN de servicio).',
                                                       'name': 'Capa 2 - Enlace de Datos (Ethernet/ONT-CPE)',
                                                       'packet_capture': {'notes': 'Capturar en puerto LAN del CPE. '
                                                                                   'Verificar tramas PPPoE o DHCP.',
                                                                          'tcpdump_filter': 'pppoes or pppoe-disc or '
                                                                                            'udp port 67 or udp port 68',
                                                                          'wireshark_display_filter': 'pppoe or dhcp'}},
                                                      {'anomalies': 'PPPoE Discovery falla (no PADO), DHCP Discover no '
                                                                'responde (no DHCPOFFER), credenciales PPP incorrectas.',
                                                       'checks': 'CPE envía PADI (PPPoE) o DHCP Discover. Servidor '
                                                                 'responde. Credenciales correctas. IP asignada.',
                                                       'detail': 'PPPoE: PADI→PADO→PADR→PADS. LCP negotiation '
                                                                 '(MRU, auth method: PAP/CHAP). IPCP (IP address, DNS). '
                                                                 'DHCP: Discover→Offer→Request→ACK.',
                                                       'name': 'Capa 3 - Red (PPPoE/IP)',
                                                       'packet_capture': {'notes': 'Filtrar PPPoE Discovery (0x8863) y '
                                                                                   'Session (0x8864). Para DHCP filtrar '
                                                                                   'puertos 67/68.',
                                                                          'tcpdump_filter': 'pppoes or pppoe-disc or '
                                                                                            'udp port 67 or udp port 68',
                                                                          'wireshark_display_filter': 'pppoe or dhcp'}}],
                                           'note': 'La ONT actúa como bridge transparente para tráfico Ethernet. El '
                                                   'proceso PPPoE/DHCP es transparente a la capa GPON.',
                                           'step_title': 'Paso 4: CPE inicia PPPoE o DHCP a través de ONT'},
                                          {'action': 'El tráfico PPPoE/DHCP encapsulado en Ethernet atraviesa la ONT y '
                                                     'es mapeado a GEM frames hacia la OLT.',
                                           'device': 'ONT / Splitter / OLT',
                                           'layers': [{'anomalies': 'GEM frame descartado (buffer ONT lleno), T-CONT '
                                                                'sin ancho de banda asignado (DBA falla), upstream '
                                                                'burst no alineado.',
                                                       'checks': 'Contadores GEM de ONT sin errores. T-CONT asignado '
                                                                 'con BW suficiente. Sin descartes de upstream.',
                                                       'detail': 'La ONT encapsula frames Ethernet en GEM frames. '
                                                                 'Cada GEM frame tiene GEM Port-ID y payload. '
                                                                 'Upstream: la ONT transmite en el timeslot asignado '
                                                                 'por la OLT (DBA - Dynamic Bandwidth Assignment).',
                                                       'name': 'Capa 2 - Enlace de Datos (GEM Encapsulation)',
                                                       'packet_capture': {'notes': 'No capturable con herramientas '
                                                                                   'estándar. Verificar contadores GEM en '
                                                                                   'OLT/ONT.',
                                                                          'tcpdump_filter': 'N/A',
                                                                          'wireshark_display_filter': 'N/A'}},
                                                      {'anomalies': 'Atentuación excesiva en sentido upstream, splitter '
                                                                'desbalanceado, conector sucio en lado ONT.',
                                                       'checks': 'Nivel óptico TX de ONT dentro de rango. OLT recibe '
                                                                 'con niveles aceptables. Splitter balanceado.',
                                                       'detail': 'Upstream: 1310 nm (ONT→OLT). La OLT mide la potencia '
                                                                 'RX de cada ONT y ajusta el laser de la ONT vía OMCI '
                                                                 '(si soporta).',
                                                       'name': 'Capa 1 - Física (Óptica Upstream)',
                                                       'packet_capture': {'notes': 'Usar power meter en splitter para '
                                                                                   'verificar niveles. OTDR si hay '
                                                                                   'sospecha de fibra cortada.',
                                                                          'tcpdump_filter': 'N/A',
                                                                          'wireshark_display_filter': 'N/A'}}],
                                           'note': 'El ancho de banda upstream es compartido entre todas las ONT del '
                                                   'mismo puerto PON mediante TDMA.',
                                           'step_title': 'Paso 5: Tráfico upstream desde ONT hacia OLT'},
                                          {'action': 'La OLT recibe GEM frames, los desencapsula a Ethernet, y envía el '
                                                     'tráfico hacia la red de agregación (BNG/BRAS).',
                                           'device': 'OLT / Red de agregación',
                                           'layers': [{'anomalies': 'GEM Port-ID desconocido, VLAN no mapeada a '
                                                                'interface de uplink, service-port no activo, MAC '
                                                                'flooding por tabla CAM llena.',
                                                       'checks': 'OLT desencapsula GEM correctamente. VLAN mapeada a '
                                                                 'puerto de uplink. MAC aprendida en CAM. Service-port '
                                                                 'activo.',
                                                       'detail': 'La OLT mantiene una tabla de mapeo GEM Port-ID → '
                                                                 'VLAN → interfaz de salida. Los frames Ethernet se '
                                                                 'envían por el puerto de agregación (10GE, 25GE, 100GE) '
                                                                 'hacia el BNG/BRAS.',
                                                       'name': 'Capa 2 - Enlace de Datos (OLT Uplink)',
                                                       'packet_capture': {'notes': 'Capturar en puerto de uplink de la '
                                                                                   'OLT. Verificar tramas Ethernet con '
                                                                                   'VLAN correcta.',
                                                                          'tcpdump_filter': 'vlan <vlan_id>',
                                                                          'wireshark_display_filter': 'vlan.id == '
                                                                                                      '<vlan_id>'}},
                                                      {'anomalies': 'BNG no responde a PPPoE, IP pool agotada, RADIUS '
                                                                'servidor inalcanzable, política de QoS descarta tráfico.',
                                                       'checks': 'BNG/BRAS operativo. Sesión PPPoE establecida. IP '
                                                                 'asignada. RADIUS responde. QoS no descarta.',
                                                       'detail': 'El BNG termina la sesión PPPoE, autentica contra '
                                                                 'RADIUS, asigna IP desde pool, aplica políticas de '
                                                                 'QoS (rate limit, shaping).',
                                                       'name': 'Capa 3 - Red (IP/BNG)',
                                                       'packet_capture': {'notes': 'Capturar en interfaz de uplink de '
                                                                                   'OLT o en BNG. Verificar tráfico PPPoE '
                                                                                   'Session o IP encapsulado.',
                                                                          'tcpdump_filter': 'pppoes or ip',
                                                                          'wireshark_display_filter': 'pppoes or ip'}}],
                                           'note': 'La OLT actúa como switch L2 transparente entre la ONT y la red '
                                                   'de agregación. No realiza routing.',
                                             'step_title': 'Paso 6: OLT desencapsula y envía tráfico a red de agregación'}]}]},

  'ccc_interface_switch': {'scenarios': [{'description': 'Recorrido de una trama Ethernet a través de una conexión CCC '
                                                         '(Circuit Cross Connect) tipo interface-switch en un Juniper MX. '
                                                         'La trama ingresa por el AC local, es procesada por el CCC, '
                                                         'y sale por el AC remoto hacia el CE destino. '
                                                         'Se muestra el encapsulado/decapsulado en cada hop.',
                                          'id': 'ccc_interface_switch_unicast',
                                          'name': 'CCC Interface Switching — Trama Ethernet entre CEs locales',
                                          'steps': [{'action': 'El CE origen genera una trama Ethernet unicast hacia el CE destino',
                                                     'device': 'CE Origen (Customer Edge)',
                                                     'layers': [{'anomalies': 'CE origen no tiene ARP resuelto para destino, '
                                                                              'interfaz CE hacia PE en down, VLAN tag '
                                                                              'mismatch con AC del PE.',
                                                                 'checks': 'Interfaz CE Up/Up. MAC destino conocida. '
                                                                           'VLAN tag coincide con AC configurado en PE. '
                                                                           'Sin errores FCS/CRC.',
                                                                 'detail': 'DstMAC=MAC_CE_destino, SrcMAC=MAC_CE_origen, '
                                                                           'EtherType=0x0800 (IPv4). Si CE usa dot1q: '
                                                                           'tag VLAN de servicio (ej: 100). Si CE sin tag: '
                                                                           'frame untagged (encapsulación ethernet-ccc en PE).',
                                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet CE→PE)',
                                                                 'packet_capture': {'notes': 'Capturar en interfaz CE hacia PE. '
                                                                                             'Verificar MAC origen/destino y VLAN tag.',
                                                                                    'tcpdump_filter': 'ether host <MAC_CE_destino>',
                                                                                    'wireshark_display_filter': 'eth.dst == '
                                                                                                                '<MAC_CE_destino>'}}],
                                                     'note': 'Desde la perspectiva del CE, el PE es el siguiente hop L2. '
                                                             'La trama Ethernet debe llegar intacta al AC del PE.',
                                                     'step_title': 'Paso 1: CE origen envía trama Ethernet hacia PE local'},
                                                    {'action': 'La trama ingresa por el Attachment Circuit (AC) local del PE '
                                                               'y es procesada por el CCC engine',
                                                     'device': 'PE local (Juniper MX) — Attachment Circuit',
                                                     'layers': [{'anomalies': 'AC en down (interface ge/xe down), encapsulación '
                                                                              'mismatch (ej: CE envía tagged pero AC espera '
                                                                              'untagged), CCC state UN/NP/WE.',
                                                                 'checks': 'AC Up/Up. Encapsulación coincide: ethernet-ccc, '
                                                                           'vlan-ccc, o extended-vlan-ccc según diseño. '
                                                                           'CCC connection en estado Up.',
                                                                 'detail': 'La interfaz AC recibe la trama Ethernet. El CCC '
                                                                           'engine la encapsula según tipo: si es '
                                                                           'interface-switch, la trama se reenvía directamente '
                                                                           'al AC remoto sin modificaciones L2. '
                                                                           'Si es remote-interface-switch, se encapsula en MPLS '
                                                                           'con label CCC (0x0001) y se envía por LSP.',
                                                                 'name': 'Capa 2 - Enlace de Datos (AC local / CCC Engine)',
                                                                 'packet_capture': {'notes': 'Mirror en AC local. Verificar que '
                                                                                             'la trama llega al PE y que el CCC '
                                                                                             'engine la procesa.',
                                                                                    'tcpdump_filter': 'ether host <MAC_CE_destino>',
                                                                                    'wireshark_display_filter': 'eth.dst == '
                                                                                                                '<MAC_CE_destino>'}},
                                                                {'anomalies': 'CCC engine descarta trama (AC no pertenece a '
                                                                             'ninguna conexión CCC), MPLS label no asignado '
                                                                             '(para remote-interface-switch), MTU excedido '
                                                                             '(trama + MPLS headers > interface MTU).',
                                                                 'checks': 'CCC connection asociada al AC. Labels MPLS '
                                                                           'instalados (para LSP-switch). MTU del AC '
                                                                           '≥ 1514 + overhead CCC/MPLS.',
                                                                 'detail': 'En el PE local, el CCC engine consulta la tabla de '
                                                                           'conexiones CCC. Para interface-switch: reenvía la '
                                                                           'trama al AC remoto. Para remote-interface-switch: '
                                                                           'empuja label MPLS CCC (0x0001) + label transporte, '
                                                                           'y reenvía por LSP hacia PE remoto.',
                                                                 'name': 'Capa 2.5 - CCC Forwarding (Juniper MX)',
                                                                 'packet_capture': {'notes': 'Si es remote-interface-switch, '
                                                                                             'capturar en interfaz MPLS. Verificar '
                                                                                             'labels MPLS (CCC label = 0x0001).',
                                                                                    'tcpdump_filter': 'mpls',
                                                                                    'wireshark_display_filter': 'mpls.label == 1'}}],
                                                     'note': 'El CCC engine opera a nivel L2. No inspecciona IPs. '
                                                             'El forwarding es determinístico basado en la conexión CCC.',
                                                     'step_title': 'Paso 2: PE local recibe trama y la procesa via CCC'},
                                                    {'action': 'La trama atraviesa el CCC hacia el AC remoto '
                                                               '(interface-switch) o hacia el PE remoto (remote-interface-switch)',
                                                     'device': 'CCC Path / MPLS Core',
                                                     'layers': [{'anomalies': 'CCC connection Dn/DS (down/disabled), LSP caído '
                                                                              '(para remote-interface-switch), MPLS label '
                                                                              'expirado (TTL=0), label mismatch en P routers.',
                                                                 'checks': 'CCC connection Up. Si remote-interface-switch: '
                                                                           'LSP MPLS Up. Labels instalados en mpls.0. '
                                                                           'TTL > 0 en label stack.',
                                                                 'detail': 'Para interface-switch: la trama se reenvía directamente '
                                                                           'por el AC remoto del mismo PE (back-to-back interfaces). '
                                                                           'Para remote-interface-switch: la trama encapsulada MPLS '
                                                                           'atraviesa los P routers del core MPLS. '
                                                                           'Los P routers switchean basados en el label de transporte.',
                                                                 'name': 'Capa 2.5 - CCC Dataplane (Path/Switching)',
                                                                 'packet_capture': {'notes': 'Para remote-interface-switch, '
                                                                                             'capturar en interfaces MPLS de P routers. '
                                                                                             'Verificar label stack y TTL.',
                                                                                    'tcpdump_filter': 'mpls',
                                                                                    'wireshark_display_filter': 'mpls.label == 1 || '
                                                                                                                'mpls'}},
                                                                {'anomalies': 'Penultimate Hop Popping (PHP) remueve label '
                                                                             'transporte antes del PE remoto, dejando solo '
                                                                             'CCC label (0x0001). Si PHP no funciona, el PE '
                                                                             'remoto ve label incorrecto.',
                                                                 'checks': 'PHP configurado correctamente (default en JunOS). '
                                                                           'PE remoto recibe trama con CCC label (0x0001) visible.',
                                                                 'detail': 'En el último P router (penultimate hop), el label de '
                                                                           'transporte es removido (PHP). El PE remoto recibe la '
                                                                           'trama con el CCC label (0x0001) como top label. '
                                                                           'El PE remoto popea el CCC label y reenvía la trama '
                                                                           'Ethernet original al AC remoto.',
                                                                 'name': 'Capa 2.5 - MPLS Label Stack (P→PE remoto)',
                                                                 'packet_capture': {'notes': 'Capturar en interfaz MPLS del '
                                                                                             'PE remoto (antes del pop). Verificar '
                                                                                             'que solo queda CCC label.',
                                                                                    'tcpdump_filter': 'mpls',
                                                                                    'wireshark_display_filter': 'mpls.label == 1 && '
                                                                                                                'mpls.bottom == 1'}}],
                                                     'note': 'Para interface-switch local, no hay MPLS involucrado. '
                                                             'Para remote-interface-switch, el dataplane MPLS debe estar operativo.',
                                                     'step_title': 'Paso 3: Trama atraviesa CCC path hacia destino'},
                                                    {'action': 'El PE remoto recibe la trama (con o sin MPLS label CCC) '
                                                               'y la reenvía por el AC remoto hacia el CE destino',
                                                     'device': 'PE remoto (Juniper MX) — AC remoto',
                                                     'layers': [{'anomalies': 'CCC label no reconocido (0x0001 no instalado '
                                                                              'en mpls.0), AC remoto en down, encapsulación '
                                                                              'mismatch con CE destino.',
                                                                 'checks': 'CCC label 0x0001 instalado en mpls.0. '
                                                                           'AC remoto Up/Up. Encapsulación coincide con CE destino.',
                                                                 'detail': 'El PE remoto popea el CCC label (si es '
                                                                           'remote-interface-switch) o recibe la trama directamente '
                                                                           '(si es interface-switch). El CCC engine reenvía la '
                                                                           'trama Ethernet original (sin labels) por el AC remoto.',
                                                                 'name': 'Capa 2 - Enlace de Datos (AC remoto / CCC Engine)',
                                                                 'packet_capture': {'notes': 'Mirror en AC remoto. Verificar que '
                                                                                             'la trama sale sin labels MPLS y con '
                                                                                             'MACs originales intactas.',
                                                                                    'tcpdump_filter': 'ether host <MAC_CE_destino>',
                                                                                    'wireshark_display_filter': 'eth.dst == '
                                                                                                                '<MAC_CE_destino>'}}],
                                                     'note': 'El PE remoto debe tener la misma conexión CCC configurada '
                                                             'con el mismo nombre y AC remoto correspondiente.',
                                                     'step_title': 'Paso 4: PE remoto reenvía trama por AC remoto'},
                                                    {'action': 'El CE destino recibe la trama Ethernet y la procesa',
                                                     'device': 'CE Destino (Customer Edge)',
                                                     'layers': [{'anomalies': 'CE destino descarta trama (MAC destino no coincide, '
                                                                              'VLAN tag incorrecto, frame con etiqueta MPLS '
                                                                              'residual), CE destino no responde (interfaz down).',
                                                                 'checks': 'CE destino recibe trama con MAC destino propia. '
                                                                           'VLAN tag coincide (si aplica). Sin residuos MPLS. '
                                                                           'FCS válido.',
                                                                 'detail': 'DstMAC=MAC_CE_destino (propia), SrcMAC=MAC_CE_origen. '
                                                                           'EtherType original preservado. Si CE usa dot1q: '
                                                                           'VLAN tag intacto. Payload Ethernet entregado a capa 3.',
                                                                 'name': 'Capa 2 - Enlace de Datos (Ethernet PE→CE)',
                                                                 'packet_capture': {'notes': 'Capturar en interfaz CE del destino. '
                                                                                             'Verificar integridad de trama original.',
                                                                                    'tcpdump_filter': 'ether host <MAC_CE_origen>',
                                                                                    'wireshark_display_filter': 'eth.src == '
                                                                                                                '<MAC_CE_origen>'}}],
                                                     'note': 'La trama recibida por el CE destino debe ser idéntica '
                                                             'a la enviada por el CE origen (salvo posibles cambios de QoS/CoS).',
                                                                                                           'step_title': 'Paso 5: CE destino recibe trama Ethernet'}]}]},
  'ospf': {'scenarios': [{'description': 'Recorrido del establecimiento de una adyacencia OSPF entre dos routers directamente conectados. Se muestra el intercambio de Hello, DBD, LSR, LSU, LSAck y el mantenimiento de la vecindad.',
                         'id': 'ospf_adjacency_full',
                         'name': 'OSPF: Establecimiento de adyacencia y mantenimiento Full',
                         'steps': [{'action': 'Router A envía paquete OSPF Hello multicast en la interfaz',
                                    'device': 'Router A',
                                    'layers': [{'anomalies': 'OSPF no habilitado en interfaz, ACL bloqueando IP 89, área mismatch, timer mismatch, MTU mismatch, subnet mismatch.',
                                               'checks': 'Interfaz Up/Up; OSPF habilitado; timers coincidentes; MTU igual en ambos lados; misma área y subnet.',
                                               'detail': 'OSPF Hello: Version=2 (IPv4) o 3 (IPv6), Type=1 (Hello), Area ID=X, Router ID=A, Network Mask=255.255.255.0, Hello Interval=10s, Dead Interval=40s, Options=E/L/N/P/DC, Neighbors=empty (primero) o lista de vecinos conocidos.',
                                               'name': 'Capa 4/3 - OSPF Hello',
                                               'packet_capture': {'notes': 'Filtrar OSPF Hello (Type=1). Verificar Router ID, Area ID, Network Mask.',
                                                                  'tcpdump_filter': 'ip[9] == 89',
                                                                  'wireshark_display_filter': 'ospf.msg.lsa.type == 1 or ospf.msg.hello'}},
                                              {'anomalies': 'TTL≠1 (OSPF requiere TTL=1 en broadcast/point-to-point), IP checksum corrupto, dirección multicast incorrecta (224.0.0.5 para IPv4, ff02::5 para IPv6).',
                                               'checks': 'TTL=1 en paquete OSPF (asegura L2 adjacency). IP destino=224.0.0.5 (AllSPFRouters) o 224.0.0.6 (AllDRouters).',
                                               'detail': 'IPv4 Header: SrcIP=interfaz_A, DstIP=224.0.0.5, Protocol=89 (OSPF), TTL=1, TOS=0xC0 (Internetwork Control).',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'Verificar TTL=1 obligatorio para OSPF en segmento broadcast.',
                                                                  'tcpdump_filter': 'ip[9] == 89 and ip[8] == 1',
                                                                  'wireshark_display_filter': 'ospf and ip.ttl == 1'}},
                                              {'anomalies': 'MAC desconocida del vecino (B no recibe), VLAN mismatch en subinterfaces, interface errors (CRC, giants).',
                                               'checks': 'Interfaz Up/Up; ARP resuelto (si unicast en NBMA); sin input/output drops.',
                                               'detail': 'DstMAC=01:00:5E:00:00:05 (multicast 224.0.0.5), SrcMAC=interfaz_A_MAC, EtherType=0x0800.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'Verificar MAC multicast OSPF correcto.',
                                                                  'tcpdump_filter': 'ether multicast and ip[9] == 89',
                                                                  'wireshark_display_filter': 'eth.dst == 01:00:5e:00:00:05'}}],
                                    'note': 'En segmentos broadcast, OSPF envía Hellos a AllSPFRouters (224.0.0.5) cada Hello Interval. Si los parámetros coinciden, el vecino aparece en 2-Way.',
                                    'step_title': 'Paso 1: Router A envía OSPF Hello ( multicast 224.0.0.5 )'},
                                   {'action': 'Router B recibe Hello, valida parámetros y responde con Hello propio incluyendo Router ID de A en su lista de vecinos',
                                    'device': 'Router B',
                                    'layers': [{'anomalies': 'B no responde (OSPF down en interfaz), parámetros mismatch (área, timer, auth, MTU), ACL bloqueando IP 89 entrante.',
                                               'checks': 'B tiene OSPF habilitado en interfaz; mismos parámetros de Hello/Dead/MTU/Area/Auth.',
                                               'detail': 'OSPF Hello: Version=2, Type=1, Area ID=X, Router ID=B, Neighbors list incluye Router ID=A.',
                                               'name': 'Capa 4/3 - OSPF Hello',
                                               'packet_capture': {'notes': 'Verificar que B incluye a A en su lista de vecinos.',
                                                                  'tcpdump_filter': 'ip[9] == 89',
                                                                  'wireshark_display_filter': 'ospf.msg.hello and ospf.neighbor.router_id == <A>'}},
                                              {'anomalies': 'TTL≠1, IP checksum corrupto, multicast no reenviado por switch (IGMP snooping o VLAN pruning bloqueando 224.0.0.5).',
                                               'checks': 'Switch permite multicast 224.0.0.5 en VLAN. TTL=1.',
                                               'detail': 'IPv4 Header: SrcIP=interfaz_B, DstIP=224.0.0.5, Protocol=89, TTL=1.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'ip[9] == 89 and ip[8] == 1',
                                                                  'wireshark_display_filter': 'ospf and ip.ttl == 1'}},
                                              {'anomalies': 'MAC flapping, B no recibe Hello de A (unidireccional), VLAN mismatch.',
                                               'checks': 'L2 bidireccional operativo.',
                                               'detail': 'DstMAC=01:00:5E:00:00:05, SrcMAC=interfaz_B_MAC.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'ether multicast and ip[9] == 89',
                                                                  'wireshark_display_filter': 'eth.dst == 01:00:5e:00:00:05'}}],
                                    'note': 'B recibe el Hello de A, valida que coincidan área, timer, MTU, subnet. Si todo OK, B pasa a estado 2-Way y anuncia a A como vecino en sus Hellos.',
                                    'step_title': 'Paso 2: Router B responde Hello (2-Way)'},
                                   {'action': 'Elección de DR/BDR (en segmentos broadcast/NBMA) e inicio del intercambio de Database Description (DBD)',
                                    'device': 'Router A y Router B',
                                    'layers': [{'anomalies': 'DR election no concluye (prioridad 0 en ambos, o Router ID igual), DR no establece adyacencia con BDR (stuck en 2-Way).',
                                               'checks': 'DR/BDR elegidos correctamente. Router con mayor prioridad (o Router ID si empate) es DR.',
                                               'detail': 'OSPF Hello contiene campos DR=0.0.0.0 y BDR=0.0.0.0 inicialmente. Tras 2-Way, cada router calcula DR/BDR basado en Prioridad y Router ID.',
                                               'name': 'Capa 4/3 - OSPF Hello (DR/BDR)',
                                               'packet_capture': {'notes': 'Verificar campos DR y BDR en Hello.',
                                                                  'tcpdump_filter': 'ip[9] == 89',
                                                                  'wireshark_display_filter': 'ospf.msg.hello'}}],
                                    'note': 'En enlaces point-to-point no hay DR/BDR. En broadcast, solo DR y BDR establecen adyacencia Full con todos los demás. Los DROthers se quedan en 2-Way entre sí.',
                                    'step_title': 'Paso 3: Elección DR/BDR y transición a ExStart'},
                                   {'action': 'Intercambio de Database Description (DBD) para sincronizar LSDB',
                                    'device': 'Router A (DR) y Router B',
                                    'layers': [{'anomalies': 'DBD sequence number desincronizado, MTU mismatch en DBD (drop silencioso), Master/Slave negotiation fallida.',
                                               'checks': 'DBD packets con I-bit, M-bit, MS-bit correctos. Sequence number incrementado consistentemente.',
                                               'detail': 'OSPF DBD: Type=2, Interface MTU=X (debe coincidir en ambos lados), Options, I-bit=1 (init), M-bit=1 (more), MS-bit=1 (master), DD Sequence Number=N.',
                                               'name': 'Capa 4/3 - OSPF DBD',
                                               'packet_capture': {'notes': 'Verificar I/M/MS bits y sequence numbers.',
                                                                  'tcpdump_filter': 'ip[9] == 89',
                                                                  'wireshark_display_filter': 'ospf.msg.dbd'}}],
                                    'note': 'El router con mayor Router ID se convierte en Master. El Slave responde con DBD usando el sequence number del Master. Si hay MTU mismatch, los DBD se descartan silenciosamente.',
                                    'step_title': 'Paso 4: Intercambio DBD (ExStart → Exchange)'},
                                   {'action': 'Solicitud de LSAs faltantes mediante Link-State Request (LSR)',
                                    'device': 'Router A o Router B',
                                    'layers': [{'anomalies': 'LSR no recibido (stuck en Exchange), LSA checksum erróneo, LSA tipo no soportado.',
                                               'checks': 'LSR contiene Type, Link State ID, Advertising Router correctos.',
                                               'detail': 'OSPF LSR: Type=3, lista de LSAs solicitados (Type, LS ID, Adv Router).',
                                               'name': 'Capa 4/3 - OSPF LSR',
                                               'packet_capture': {'notes': 'Verificar que LSR solicita LSAs presentes en DBD del vecino.',
                                                                  'tcpdump_filter': 'ip[9] == 89',
                                                                  'wireshark_display_filter': 'ospf.msg.lsr'}}],
                                    'note': 'Tras comparar DBDs, cada router detecta LSAs que el vecino tiene y él no. Envía LSR para solicitarlos.',
                                    'step_title': 'Paso 5: LSR — Solicitud de LSAs faltantes'},
                                   {'action': 'Envío de Link-State Update (LSU) con LSAs completos',
                                    'device': 'Router A o Router B',
                                    'layers': [{'anomalies': 'LSU fragmentado y no reensamblado (MTU bajo en path), LSA Age=MaxAge (3600s) indicando flushing, LSA checksum inválido.',
                                               'checks': 'LSU contiene LSAs válidos con checksum correcto. Sin duplicados innecesarios.',
                                               'detail': 'OSPF LSU: Type=4, Number of LSAs=N, seguido de cada LSA completo (Header + Body).',
                                               'name': 'Capa 4/3 - OSPF LSU',
                                               'packet_capture': {'notes': 'Verificar LSA Type, Link State ID, Age, Sequence Number, Checksum.',
                                                                  'tcpdump_filter': 'ip[9] == 89',
                                                                  'wireshark_display_filter': 'ospf.msg.lsu'}}],
                                    'note': 'El LSU es un multicast (224.0.0.5 o 224.0.0.6) o unicast si se usa retransmission. Contiene los LSAs completos solicitados.',
                                    'step_title': 'Paso 6: LSU — Actualización de LSAs'},
                                   {'action': 'Reconocimiento de LSU mediante Link-State Ack (LSAck)',
                                    'device': 'Router A y Router B',
                                    'layers': [{'anomalies': 'LSAck perdido (retransmisión innecesaria de LSU), LSAck con checksum erróneo, LSAck no reconocido por transmisor.',
                                               'checks': 'LSAck contiene headers de LSAs reconocidos. Sin pérdida de paquetes.',
                                               'detail': 'OSPF LSAck: Type=5, lista de LSA Headers reconocidos.',
                                               'name': 'Capa 4/3 - OSPF LSAck',
                                               'packet_capture': {'notes': 'Verificar que cada LSU recibe su LSAck correspondiente.',
                                                                  'tcpdump_filter': 'ip[9] == 89',
                                                                  'wireshark_display_filter': 'ospf.msg.lsack'}}],
                                    'note': 'Tras recibir LSU, el receptor responde con LSAck. Si el transmisor no recibe LSAck dentro de RxmtInterval, retransmite el LSU.',
                                    'step_title': 'Paso 7: LSAck — Reconocimiento de LSU'},
                                   {'action': 'Mantenimiento de la adyacencia Full con Hellos periódicos',
                                    'device': 'Router A y Router B',
                                    'layers': [{'anomalies': 'Hellos perdidos (Dead Timer expira, adyacencia cae a Down), timer mismatch tras cambio de configuración, interface flapping.',
                                               'checks': 'Hellos periódicos cada Hello Interval. Dead Timer no expira. Vecindad Full estable.',
                                               'detail': 'OSPF Hello periódico: Type=1, Area ID, Router ID, Neighbors list incluye Router ID del vecino. Dead Interval=40s (default), Hello Interval=10s.',
                                               'name': 'Capa 4/3 - OSPF Hello (Mantenimiento)',
                                               'packet_capture': {'notes': 'Medir inter-packet gap de Hellos. Verificar que no hay gap > Dead Interval.',
                                                                  'tcpdump_filter': 'ip[9] == 89',
                                                                  'wireshark_display_filter': 'ospf.msg.hello'}}],
                                    'note': 'Una vez en Full, los routers intercambian Hellos periódicamente. Si un router deja de recibir Hellos por más de Dead Interval, baja la adyacencia a Down y recalcula SPF.',
                                    'step_title': 'Paso 8: Mantenimiento Full — Hellos periódicos'}]}]},
  'isis': {'scenarios': [{'description': 'Recorrido del establecimiento de una adyacencia IS-IS entre dos routers en un segmento broadcast (LAN) o point-to-point. Se muestra el intercambio de IIH (IS-IS Hello), CSNP, PSNP, LSP, y el mantenimiento de la base de datos de link-state.',
                         'id': 'isis_adjacency_up',
                         'name': 'IS-IS: Establecimiento de adyacencia y sincronización LSDB',
                         'steps': [{'action': 'Router A envía IS-IS Hello (IIH) en la interfaz',
                                    'device': 'Router A',
                                    'layers': [{'anomalies': 'IS-IS no habilitado en interfaz, encapsulación mismatch (ISO 802.2 vs Ethernet II), area mismatch (L1 vs L2 vs L1/L2), timer mismatch, MTU mismatch, auth mismatch (MD5 o cleartext), System ID duplicado.',
                                               'checks': 'Interfaz Up/Up; IS-IS habilitado; mismo nivel (L1/L2); mismos timers; MTU ≥ 1492 (para LSP); auth coincide.',
                                               'detail': 'IS-IS Hello (IIH): Protocol Discriminator=0x83, Length Indicator=var, Version/Version2=1, Type=17 (LAN-IIH) o 18 (P2P-IIH), Holding Time=X, Circuit Type=L1/L2, Source ID=System ID de A, LAN ID=Designated IS (si broadcast).',
                                               'name': 'Capa 3/2 - IS-IS Hello (IIH)',
                                               'packet_capture': {'notes': 'Filtrar IS-IS (Protocol 0x83). Verificar Type, Holding Time, Circuit Type, Source ID.',
                                                                  'tcpdump_filter': "ether proto 0x83",
                                                                  'wireshark_display_filter': 'isis'}},
                                              {'anomalies': 'ISO 802.2 LLC no soportado por switch (algunos switches no bridgean LLC), VLAN mismatch en subinterfaces, MAC multicast no reenviada.',
                                               'checks': 'Switch permite tramas LLC/SNAP (0xFEFE). MAC destino correcta (AllIS: 01:80:C2:00:00:14 L1, 01:80:C2:00:00:15 L2, 09:00:2B:00:00:05 AllIntermediateSystems).',
                                               'detail': 'Ethernet: DstMAC=01:80:C2:00:00:14 (L1) o 01:80:C2:00:00:15 (L2) o 09:00:2B:00:00:05 (AllIS), SrcMAC=interfaz_A_MAC, DSAP=0xFE, SSAP=0xFE, Control=0x03 (UI).',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet/LLC)',
                                               'packet_capture': {'notes': 'Verificar MAC destino IS-IS correcta.',
                                                                  'tcpdump_filter': 'ether proto 0x83',
                                                                  'wireshark_display_filter': 'isis'}}],
                                    'note': 'En LAN, IS-IS usa MAC multicast 01:80:C2:00:00:14 (L1) o 01:80:C2:00:00:15 (L2). En P2P se usa 09:00:2B:00:00:05. No usa IP.',
                                    'step_title': 'Paso 1: Router A envía IS-IS Hello (IIH)'},
                                   {'action': 'Router B recibe IIH, valida parámetros y responde con IIH propio',
                                    'device': 'Router B',
                                    'layers': [{'anomalies': 'B no responde (IS-IS down, encapsulación mismatch, auth failed, area mismatch, timer mismatch).',
                                               'checks': 'B tiene IS-IS habilitado; mismos parámetros que A.',
                                               'detail': 'IS-IS IIH: Type=17 (LAN) o 18 (P2P), Holding Time, Circuit Type, Source ID=System ID de B.',
                                               'name': 'Capa 3/2 - IS-IS Hello (IIH)',
                                               'packet_capture': {'notes': 'Verificar que B responde con IIH.',
                                                                  'tcpdump_filter': 'ether proto 0x83',
                                                                  'wireshark_display_filter': 'isis'}},
                                              {'anomalies': 'MAC no reenviada, LLC filtrado, VLAN mismatch.',
                                               'checks': 'L2 bidireccional operativo.',
                                               'detail': 'Ethernet: DstMAC multicast IS-IS, SrcMAC=interfaz_B_MAC.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet/LLC)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'ether proto 0x83',
                                                                  'wireshark_display_filter': 'isis'}}],
                                    'note': 'B recibe IIH de A, valida encapsulación, auth, área, timers. Si todo OK, B transiciona a Initializing y responde con IIH incluyendo a A.',
                                    'step_title': 'Paso 2: Router B responde IIH (Initializing)'},
                                   {'action': 'Elección de DIS (Designated Intermediate System) en segmento broadcast',
                                    'device': 'Routers en LAN',
                                    'layers': [{'anomalies': 'DIS election no concluye (prioridad 0 en todos), DIS flapping (prioridades iguales, System ID cambia), no hay DIS en segmento multi-access.',
                                               'checks': 'DIS elegido correctamente (mayor prioridad, o mayor System ID si empate). DIS envía IIH con mayor frecuencia (1/3 del Holding Time).',
                                               'detail': 'DIS election basada en Priority (campo en IIH) y System ID. El DIS envía IIH cada 1/3 del Holding Time para mantener caché de vecinos.',
                                               'name': 'Capa 3/2 - IS-IS DIS Election',
                                               'packet_capture': {'notes': 'Verificar Priority y DIS flag en IIH.',
                                                                  'tcpdump_filter': 'ether proto 0x83',
                                                                  'wireshark_display_filter': 'isis'}}],
                                    'note': 'En P2P no hay DIS. En broadcast, el DIS actúa como pseudonodo y genera un LSP separado para representar la LAN.',
                                    'step_title': 'Paso 3: Elección DIS (broadcast only)'},
                                   {'action': 'Intercambio de Complete Sequence Number PDU (CSNP) para sincronizar LSDB',
                                    'device': 'DIS (o ambos routers en P2P)',
                                    'layers': [{'anomalies': 'CSNP perdido (LSDB desincronizada), CSNP con checksum erróneo, CSNP enviado por non-DIS en broadcast.',
                                               'checks': 'CSNP contiene lista de todos los LSPs conocidos en el área (L1) o dominio (L2).',
                                               'detail': 'IS-IS CSNP: Type=24 (L1 CSNP) o 25 (L2 CSNP), Source ID=DIS System ID, Start LSP ID, End LSP ID, lista de LSP Entries (LSP ID, Sequence Number, Checksum, Remaining Lifetime).',
                                               'name': 'Capa 3/2 - IS-IS CSNP',
                                               'packet_capture': {'notes': 'Verificar que CSNP cubre todo el rango de LSP IDs.',
                                                                  'tcpdump_filter': 'ether proto 0x83',
                                                                  'wireshark_display_filter': 'isis.pdu_type == 24 or isis.pdu_type == 25'}}],
                                    'note': 'En broadcast, el DIS envía CSNP periódicamente (cada 10s por defecto). En P2P, ambos routers envían CSNP al establecer la adyacencia.',
                                    'step_title': 'Paso 4: Intercambio CSNP (sincronización LSDB)'},
                                   {'action': 'Solicitud de LSPs faltantes mediante Partial Sequence Number PDU (PSNP)',
                                    'device': 'Router A o Router B',
                                    'layers': [{'anomalies': 'PSNP no recibido (stuck en sincronización), PSNP con LSP ID incorrecto, PSNP checksum erróneo.',
                                               'checks': 'PSNP contiene LSP IDs que faltan o que tienen sequence number más bajo.',
                                               'detail': 'IS-IS PSNP: Type=26 (L1 PSNP) o 27 (L2 PSNP), Source ID, lista de LSP Entries solicitados.',
                                               'name': 'Capa 3/2 - IS-IS PSNP',
                                               'packet_capture': {'notes': 'Verificar LSP IDs en PSNP.',
                                                                  'tcpdump_filter': 'ether proto 0x83',
                                                                  'wireshark_display_filter': 'isis.pdu_type == 26 or isis.pdu_type == 27'}}],
                                    'note': 'Tras comparar CSNP con su LSDB local, un router detecta LSPs faltantes o desactualizados. Envía PSNP para solicitarlos.',
                                    'step_title': 'Paso 5: PSNP — Solicitud de LSPs faltantes'},
                                   {'action': 'Envío de Link-State PDU (LSP) con información de topología',
                                    'device': 'Router A o Router B (o DIS)',
                                    'layers': [{'anomalies': 'LSP fragmentado (MTU insuficiente en interfaz), LSP con Remaining Lifetime=0 (flushing), LSP checksum erróneo, LSP duplicado (sequence number no incrementado).',
                                               'checks': 'LSP contiene información de topología válida. Sequence number incrementado correctamente.',
                                               'detail': 'IS-IS LSP: Type=18 (L1 LSP) o 20 (L2 LSP), LSP ID, Sequence Number, Remaining Lifetime, Checksum, TLVs (Area Addresses, IP Internal Reachability, IP External Reachability, IS Neighbors, etc.).',
                                               'name': 'Capa 3/2 - IS-IS LSP',
                                               'packet_capture': {'notes': 'Verificar LSP ID, Sequence Number, Remaining Lifetime, Checksum.',
                                                                  'tcpdump_filter': 'ether proto 0x83',
                                                                  'wireshark_display_filter': 'isis.pdu_type == 18 or isis.pdu_type == 20'}}],
                                    'note': 'El LSP es el análogo al LSA de OSPF. Contiene la topología del router (IS Neighbors) y los prefijos IP alcanzables.',
                                    'step_title': 'Paso 6: LSP — Propagación de topología'},
                                   {'action': 'Reconocimiento de LSP mediante PSNP (en P2P) o CSNP (en broadcast)',
                                    'device': 'Router receptor',
                                    'layers': [{'anomalies': 'PSNP/CSNP perdido (retransmisión de LSP), reconocimiento con LSP ID incorrecto.',
                                               'checks': 'En P2P: PSNP reconoce LSP recibido. En broadcast: CSNP periódico confirma sincronización.',
                                               'detail': 'En P2P, el receptor envía PSNP como ACK. En broadcast, el DIS no envía ACK explícito; la ausencia del LSP en el próximo CSNP indica que fue aceptado.',
                                               'name': 'Capa 3/2 - IS-IS ACK (PSNP/CSNP)',
                                               'packet_capture': {'notes': 'Verificar PSNP como ACK en P2P. Verificar CSNP periódico en broadcast.',
                                                                  'tcpdump_filter': 'ether proto 0x83',
                                                                  'wireshark_display_filter': 'isis.pdu_type == 26 or isis.pdu_type == 27'}}],
                                    'note': 'En P2P, PSNP actúa como ACK. En broadcast, la confiabilidad se logra mediante CSNP periódicos del DIS. Si un router no ve su LSP en el CSNP, lo retransmite.',
                                    'step_title': 'Paso 7: ACK — PSNP (P2P) o CSNP (broadcast)'},
                                   {'action': 'Mantenimiento de la adyacencia Up con IIH periódicos',
                                    'device': 'Router A y Router B',
                                    'layers': [{'anomalies': 'IIH perdidos (Holding Time expira, adyacencia cae a Down), encapsulación cambiada, auth key rotada sin sincronización.',
                                               'checks': 'IIH periódicos cada Hello Interval (3.3s default broadcast, 10s default P2P). Holding Time no expira.',
                                               'detail': 'IS-IS IIH periódico: Type=17/18, Holding Time, Circuit Type, Source ID.',
                                               'name': 'Capa 3/2 - IS-IS Hello (Mantenimiento)',
                                               'packet_capture': {'notes': 'Medir inter-packet gap de IIH. Verificar que no hay gap > Holding Time.',
                                                                  'tcpdump_filter': 'ether proto 0x83',
                                                                  'wireshark_display_filter': 'isis'}}],
                                    'note': 'Una vez en Up, los routers intercambian IIH periódicamente. Si un router deja de recibir IIH por más de Holding Time, baja la adyacencia a Down y recalcula SPF.',
                                    'step_title': 'Paso 8: Mantenimiento Up — IIH periódicos'}]}]},
  'bgp': {'scenarios': [{'description': 'Recorrido del establecimiento de una sesión BGP IPv4 unicast entre dos routers. Se muestra el intercambio de OPEN, KEEPALIVE, UPDATE, NOTIFICATION, y el mantenimiento de la sesión.',
                        'id': 'bgp_ipv4_unicast_session',
                        'name': 'BGP IPv4 Unicast: Establecimiento de sesión y mantenimiento',
                        'steps': [{'action': 'Router A inicia conexión TCP hacia Router B (port 179) y envía mensaje OPEN',
                                   'device': 'Router A',
                                   'layers': [{'anomalies': 'BGP no habilitado, neighbor IP no alcanzable, ACL bloqueando TCP 179, AS number mismatch, Router ID conflictivo, BGP version mismatch.',
                                               'checks': 'A tiene neighbor <B> remote-as <X>; B alcanzable vía L3; TCP 179 permitido; AS numbers coincidentes.',
                                               'detail': 'BGP OPEN: Marker=16 bytes 0xFF, Length=29+, Type=1 (OPEN), Version=4, My AS=64512, Hold Time=180s, BGP Identifier=Router ID de A, Optional Parameters Length=var (Capabilities: MP-BGP, Route Refresh, Graceful Restart, 4-octet AS, etc.).',
                                               'name': 'Capa 7/5 - BGP OPEN',
                                               'packet_capture': {'notes': 'Verificar Type=1, AS number, Hold Time, BGP ID, Capabilities.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'bgp.type == 1'}},
                                             {'anomalies': 'TCP SYN no recibido (ruta asimétrica, ACL unidireccional), TCP SYN/ACK no retorna (firewall en B), TCP RST (BGP no habilitado en B o peer-group mismatch).',
                                              'checks': 'Three-way handshake completo (SYN, SYN-ACK, ACK). Sin RST.',
                                              'detail': 'TCP Header: SrcPort=efímero (>1024), DstPort=179, SYN=1, Seq=N, Ack=0, Window=X, Options (MSS, SACK, Timestamps, Window Scale).',
                                              'name': 'Capa 4 - Transporte (TCP)',
                                              'packet_capture': {'notes': 'Verificar three-way handshake completo.',
                                                                 'tcpdump_filter': 'tcp port 179',
                                                                 'wireshark_display_filter': 'tcp.port == 179 && tcp.flags.syn == 1'}},
                                             {'anomalies': 'IP no alcanzable, TTL expirado, MTU path menor que 1500, fragmentación no permitida.',
                                              'checks': 'Ping/TCP SYN llega a B. TTL suficiente. MTU ≥ 1500 en path.',
                                              'detail': 'IPv4 Header: SrcIP=interfaz_A, DstIP=interfaz_B, Protocol=TCP(6), TTL=64 (o más), TOS=0xC0 (Internetwork Control).',
                                              'name': 'Capa 3 - Red (IPv4)',
                                              'packet_capture': {'notes': 'Verificar TTL y TOS en SYN.',
                                                                 'tcpdump_filter': 'tcp port 179',
                                                                 'wireshark_display_filter': 'tcp.port == 179'}},
                                             {'anomalies': 'MAC no resuelto (ARP incomplete), VLAN mismatch, interface errors.',
                                              'checks': 'Interfaz Up/Up; ARP/ND resuelto; sin drops L2.',
                                              'detail': 'Ethernet: DstMAC=next_hop_MAC, SrcMAC=interfaz_A_MAC, EtherType=0x0800.',
                                              'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                              'packet_capture': {'notes': 'Verificar MACs y EtherType.',
                                                                 'tcpdump_filter': 'tcp port 179',
                                                                 'wireshark_display_filter': 'eth.type == 0x0800 && tcp.port == 179'}}],
                                   'note': 'BGP usa TCP 179. El router con IP mayor inicia la conexión (si no hay connect-mode passive en ambos). Primero se establece TCP, luego BGP OPEN.',
                                   'step_title': 'Paso 1: TCP SYN + BGP OPEN desde Router A'},
                                  {'action': 'Router B responde con OPEN propio y KEEPALIVE',
                                   'device': 'Router B',
                                   'layers': [{'anomalies': 'B envía OPEN con AS mismatch (notification Type=Cease/Subcode=bad peer AS), Hold Time menor al mínimo aceptable, Router ID duplicado, capacidades incompatibles (ej: 4-octet AS no soportado).',
                                               'checks': 'B acepta AS number, Router ID único, Hold Time ≥ 3s, capacidades compatibles.',
                                               'detail': 'BGP OPEN: Type=1, My AS=64512, Hold Time=180s, BGP Identifier=Router ID de B.',
                                               'name': 'Capa 7/5 - BGP OPEN',
                                               'packet_capture': {'notes': 'Verificar OPEN de B.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'bgp.type == 1'}},
                                             {'anomalies': 'TCP SYN-ACK no llega a A (ruta asimétrica, ACL), TCP window scale mismatch.',
                                              'checks': 'Three-way handshake completo.',
                                              'detail': 'TCP SYN-ACK: SrcPort=179, DstPort=efímero, SYN=1, ACK=1.',
                                              'name': 'Capa 4 - Transporte (TCP)',
                                              'packet_capture': {'notes': 'Verificar SYN-ACK.',
                                                                 'tcpdump_filter': 'tcp port 179',
                                                                 'wireshark_display_filter': 'tcp.port == 179 && tcp.flags.syn == 1 && tcp.flags.ack == 1'}},
                                             {'anomalies': 'IP no alcanzable hacia A.',
                                              'checks': 'Ruta B→A operativa.',
                                              'detail': 'IPv4: SrcIP=interfaz_B, DstIP=interfaz_A, Protocol=TCP, TTL=64.',
                                              'name': 'Capa 3 - Red (IPv4)',
                                              'packet_capture': {'notes': 'N/A',
                                                                 'tcpdump_filter': 'tcp port 179',
                                                                 'wireshark_display_filter': 'tcp.port == 179'}},
                                             {'anomalies': 'L2 unidireccional.',
                                              'checks': 'L2 bidireccional.',
                                              'detail': 'Ethernet: DstMAC=interfaz_A_MAC, SrcMAC=interfaz_B_MAC.',
                                              'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                              'packet_capture': {'notes': 'N/A',
                                                                 'tcpdump_filter': 'tcp port 179',
                                                                 'wireshark_display_filter': 'eth.type == 0x0800 && tcp.port == 179'}}],
                                   'note': 'B recibe OPEN de A, valida AS, Router ID, Hold Time, capacidades. Si todo OK, responde con OPEN propio y un KEEPALIVE.',
                                   'step_title': 'Paso 2: Router B responde OPEN + KEEPALIVE'},
                                  {'action': 'Intercambio de KEEPALIVE periódicos para mantener la sesión',
                                   'device': 'Router A y Router B',
                                   'layers': [{'anomalies': 'KEEPALIVE perdidos (Hold Timer expira, sesión cae a Idle), TCP window cerrada, TCP retransmisiones masivas.',
                                               'checks': 'KEEPALIVE cada 1/3 del Hold Time (default 60s si Hold=180s). Contadores de RX/TX incrementan.',
                                               'detail': 'BGP KEEPALIVE: Marker=0xFF..., Length=19, Type=4 (KEEPALIVE). Sin payload.',
                                               'name': 'Capa 7/5 - BGP KEEPALIVE',
                                               'packet_capture': {'notes': 'Verificar periodicidad de KEEPALIVE. Medir inter-packet gap.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'bgp.type == 4'}}],
                                   'note': 'Tras recibir OPEN, ambos routers envían KEEPALIVE. La sesión pasa a Established. KEEPALIVEs mantienen la sesión sin consumir ancho de banda.',
                                   'step_title': 'Paso 3: KEEPALIVE — Sesión Established'},
                                  {'action': 'Router A anuncia una ruta con UPDATE',
                                   'device': 'Router A',
                                   'layers': [{'anomalies': 'UPDATE mal formado (malformed attribute, missing well-known attribute), AS path loop, next-hop inalcanzable, prefix-length > 24 no aceptada por policy.',
                                               'checks': 'UPDATE contiene atributos well-known obligatorios (ORIGIN, AS_PATH, NEXT_HOP). Sin loops de AS.',
                                               'detail': 'BGP UPDATE: Type=2, Withdrawn Routes Length, Total Path Attribute Length, Path Attributes (ORIGIN, AS_PATH, NEXT_HOP, MED, LOCAL_PREF, COMMUNITY, EXTENDED COMMUNITY), NLRI (Network Layer Reachability Information: prefix/length).',
                                               'name': 'Capa 7/5 - BGP UPDATE',
                                               'packet_capture': {'notes': 'Verificar atributos en UPDATE.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'bgp.type == 2'}},
                                             {'anomalies': 'TCP PSH/ACK perdido, TCP zero-window, segmento retransmitido.',
                                              'checks': 'TCP ACK recibido por cada UPDATE. Sin retransmisiones.',
                                              'detail': 'TCP: SrcPort=efímero/179, DstPort=179/efímero, PSH=1, ACK=1, Seq/Ack correctos.',
                                              'name': 'Capa 4 - Transporte (TCP)',
                                              'packet_capture': {'notes': 'Verificar que cada UPDATE recibe ACK.',
                                                                 'tcpdump_filter': 'tcp port 179',
                                                                 'wireshark_display_filter': 'tcp.port == 179 && tcp.flags.psh == 1'}},
                                             {'anomalies': 'IP checksum erróneo, TTL expirado, MTU insuficiente causando fragmentación TCP.',
                                              'checks': 'IP válido. MTU ≥ 1500. Sin fragmentación de UPDATEs grandes.',
                                              'detail': 'IPv4: SrcIP=interfaz_A, DstIP=interfaz_B, Protocol=TCP, TTL=64.',
                                              'name': 'Capa 3 - Red (IPv4)',
                                              'packet_capture': {'notes': 'N/A',
                                                                 'tcpdump_filter': 'tcp port 179',
                                                                 'wireshark_display_filter': 'tcp.port == 179'}},
                                             {'anomalies': 'L2 errors, MAC flapping.',
                                              'checks': 'L2 estable.',
                                              'detail': 'Ethernet: DstMAC=interfaz_B_MAC, SrcMAC=interfaz_A_MAC.',
                                              'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                              'packet_capture': {'notes': 'N/A',
                                                                 'tcpdump_filter': 'tcp port 179',
                                                                 'wireshark_display_filter': 'eth.type == 0x0800 && tcp.port == 179'}}],
                                   'note': 'A anuncia un prefijo (ej: 192.0.2.0/24) con sus atributos BGP. B recibe el UPDATE y lo procesa según sus policies de entrada.',
                                   'step_title': 'Paso 4: UPDATE — Anuncio de ruta'},
                                  {'action': 'Router B envía UPDATE de retorno o withdraw',
                                   'device': 'Router B',
                                   'layers': [{'anomalies': 'UPDATE con AS path loop, next-hop inalcanzable, prefix no aceptada por policy de B (silently discarded).',
                                               'checks': 'B anuncia prefijos válidos o envía withdraw si la ruta ya no existe.',
                                               'detail': 'BGP UPDATE: Type=2, Path Attributes, NLRI o Withdrawn Routes.',
                                               'name': 'Capa 7/5 - BGP UPDATE',
                                               'packet_capture': {'notes': 'Verificar UPDATEs bidireccionales.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'bgp.type == 2'}}],
                                   'note': 'En eBGP, B puede no anunciar nada de retorno (solo default o rutas específicas). En iBGP, ambos peers intercambian rutas según split-horizon (route-reflector rules).',
                                   'step_title': 'Paso 5: UPDATE bidireccional / Withdraw'},
                                  {'action': 'Mantenimiento de la sesión con KEEPALIVE y posible NOTIFICATION en falla',
                                   'device': 'Router A y Router B',
                                   'layers': [{'anomalies': 'NOTIFICATION enviada (Type=3) por error de sintaxis, hold timer expirado, cease administrativo, finite state machine error.',
                                               'checks': 'Sin NOTIFICATIONs. Solo KEEPALIVEs periódicos y UPDATEs según cambios de routing.',
                                               'detail': 'BGP NOTIFICATION: Type=3, Error Code (Message Header, OPEN, UPDATE, Hold Timer Expired, Finite State Machine, Cease), Error Subcode, Data (contexto del error).',
                                               'name': 'Capa 7/5 - BGP NOTIFICATION',
                                               'packet_capture': {'notes': 'Capturar NOTIFICATION para diagnosticar la causa exacta del teardown.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'bgp.type == 3'}},
                                             {'anomalies': 'TCP FIN/RST (sesión cerrada por peer), TCP retransmisiones masivas (path congestionado).',
                                              'checks': 'Sin FIN/RST inesperados. TCP estable.',
                                              'detail': 'TCP FIN: src/dst port 179, FIN=1. TCP RST: RST=1.',
                                              'name': 'Capa 4 - Transporte (TCP)',
                                              'packet_capture': {'notes': 'Verificar FIN/RST.',
                                                                 'tcpdump_filter': 'tcp port 179',
                                                                 'wireshark_display_filter': 'tcp.port == 179 && (tcp.flags.fin == 1 || tcp.flags.reset == 1)'}}],
                                   'note': 'Si hay un error crítico, cualquier peer puede enviar NOTIFICATION y cerrar la sesión. En caso de cierre administrativo (Cease), se envía NOTIFICATION con Error Code=6.',
                                   'step_title': 'Paso 6: NOTIFICATION / Teardown de sesión'}]}]},
'spanning_tree': {'scenarios': [{'description': 'Recorrido de la convergencia RSTP en una topología de switches. Se muestra la elección de Root Bridge, port roles (Root, Designated, Alternate, Backup), BPDU exchange, y transición de estados (Discarding → Learning → Forwarding).',
                                   'id': 'rstp_convergence_topology',
                                   'name': 'RSTP: Convergencia y roles de puerto',
                                   'steps': [{'action': 'Todos los switches envían BPDUs con su Bridge ID al inicio',
                                             'device': 'Switch A, B, C',
                                             'layers': [{'anomalies': 'BPDUs no enviadas (spanning-tree deshabilitado en VLAN), BPDU filter activo (silently discarding), BPDU guard bloqueando puertos edge.',
                                                         'checks': 'Spanning-tree habilitado en VLAN. Sin BPDU filter indiscriminado. Edge ports con BPDU guard solo donde aplica.',
                                                         'detail': 'RSTP BPDU: Protocol Identifier=0x0000, Protocol Version=2 (RSTP), BPDU Type=2 (RST/MST), Flags (Topology Change, Agreement, Forwarding, Learning, Port Role), Root ID=Bridge ID del switch, Root Path Cost=0 (inicialmente), Bridge ID=MAC+Priority del switch, Port ID=Port+Priority.',
                                                         'name': 'Capa 2 - STP/RSTP BPDU',
                                                         'packet_capture': {'notes': 'Filtrar BPDUs (DST MAC 01:80:C2:00:00:00). Verificar Root ID, Bridge ID, Port Role.',
                                                                            'tcpdump_filter': 'ether dst 01:80:c2:00:00:00',
                                                                            'wireshark_display_filter': 'stp'}},
                                                       {'anomalies': 'BPDUs descartadas por switch (port-blocking no-STP), VLAN pruning en trunk (BPDU de VLAN nativa no pasa), PVST+ mismatch (BPDUs con VLAN tag no reconocidas por RSTP estándar).',
                                                        'checks': 'Trunk permite VLAN nativa donde viajan BPDUs (o PVST+ simulación correcta). Port no bloqueado por seguridad.',
                                                        'detail': 'Ethernet: DstMAC=01:80:C2:00:00:00 (Spanning Tree), SrcMAC=switch_port_MAC, EtherType=0x8100 (802.1Q opcional para PVST+) o sin tag para RSTP estándar. LLC/SNAP no aplica; BPDU va directo en Ethernet II.',
                                                        'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                        'packet_capture': {'notes': 'Verificar MAC destino 01:80:C2:00:00:00.',
                                                                           'tcpdump_filter': 'ether dst 01:80:c2:00:00:00',
                                                                           'wireshark_display_filter': 'stp'}}],
                                             'note': 'Al inicio, cada switch se considera Root. Envía BPDUs periódicamente. En RSTP, los BPDUs se envían incluso si el puerto no recibe BPDUs del root (proactive).',
                                             'step_title': 'Paso 1: Todos envían BPDUs (considerándose Root)'},
                                            {'action': 'Elección de Root Bridge basada en menor Bridge ID (Priority + MAC)',
                                             'device': 'Switches en topología',
                                             'layers': [{'anomalies': 'Root Bridge no deseado (prioridad 32768 en switch incorrecto), Root Bridge flapping ( Bridge ID cambia por MAC address-table instability), dos switches con igual Bridge ID (imposible en RSTP estándar, pero puede ocurrir en virtual switches).',
                                                         'checks': 'Root Bridge tiene la menor Priority (default 32768). Si hay empate, menor MAC.',
                                                         'detail': 'Bridge ID = Priority (2 bytes) + MAC (6 bytes). Ej: 32768.00:11:22:33:44:55. Root Bridge = menor Bridge ID en la red.',
                                                         'name': 'Capa 2 - STP/RSTP Root Election',
                                                         'packet_capture': {'notes': 'Verificar Root ID en BPDUs recibidos. Todos deben converger al mismo Root ID.',
                                                                            'tcpdump_filter': 'ether dst 01:80:c2:00:00:00',
                                                                            'wireshark_display_filter': 'stp'}}],
                                             'note': 'El switch con menor Bridge ID gana y se convierte en Root Bridge. Todos los demás switches recalculan su Root Path Cost.',
                                             'step_title': 'Paso 2: Elección de Root Bridge'},
                                            {'action': 'Cálculo de Root Path Cost y asignación de port roles',
                                             'device': 'Switch B (non-root)',
                                             'layers': [{'anomalies': 'Root Path Cost incorrecto (costo de enlace mal configurado, ej: 10G configurado como costo de 1G), port role incorrecto (Alternate designado como Root por spanning-tree vlan X root primary mal aplicado).',
                                                         'checks': 'Root Path Cost acumulado correctamente desde cada switch hasta el Root. Root port = puerto con menor costo hacia el Root.',
                                                         'detail': 'Root Path Cost = suma de costos de enlaces hacia el Root. RSTP usa costos IEEE 802.1t (auto-negotiated por bandwidth): 10G=2, 1G=4, 100M=19, 10M=100. Port Role: Root (mejor path), Designated (mejor path para segmento), Alternate (backup path), Backup (backup en mismo segmento).',
                                                         'name': 'Capa 2 - STP/RSTP Port Roles',
                                                         'packet_capture': {'notes': 'Verificar Root Path Cost y Port Role en BPDUs.',
                                                                            'tcpdump_filter': 'ether dst 01:80:c2:00:00:00',
                                                                            'wireshark_display_filter': 'stp'}}],
                                             'note': 'Cada switch selecciona un Root Port (mejor camino al Root) y Designated Ports (mejor camino para cada segmento). Los demás puertos no-root/no-designated se bloquean (Alternate/Backup).',
                                             'step_title': 'Paso 3: Cálculo de Root Path Cost y Port Roles'},
                                            {'action': 'Transición de estados en puertos Designated/Root (Discarding → Learning → Forwarding)',
                                             'device': 'Switch B',
                                             'layers': [{'anomalies': 'Port stuck en Discarding (BPDU guard erróneo, loop guard detection, inconsistent port type), port flapping entre Learning y Forwarding (topology change recurrente).',
                                                         'checks': 'Root/Designated ports alcanzan Forwarding en ~2×Hello Time (RSTP) o 30s (STP 802.1D). Sin errores de consistencia.',
                                                         'detail': 'RSTP: Discarding (no forwarding, learning MACs) → Learning (learning MACs, no forwarding) → Forwarding (full operation). Transición rápida (~2×Hello=4s) en punto-a-punto con proposal/agreement.',
                                                         'name': 'Capa 2 - STP/RSTP Port States',
                                                         'packet_capture': {'notes': 'Verificar flags Agreement y Forwarding en BPDUs durante transición.',
                                                                            'tcpdump_filter': 'ether dst 01:80:c2:00:00:00',
                                                                            'wireshark_display_filter': 'stp'}}],
                                             'note': 'RSTP acelera la convergencia usando proposal/agreement en enlaces punto-a-punto. En shared media (hub) usa timers tradicionales.',
                                             'step_title': 'Paso 4: Transición de estados (RSTP sync)'},
                                            {'action': 'Detección de cambio de topología (TC) y flooding de BPDUs con TC flag',
                                             'device': 'Switch B',
                                             'layers': [{'anomalies': 'TC flooding masivo (topology change storm), MAC table flapping, broadcast storm temporal, TC bit no propagado (VLAN pruning bloqueando BPDU de TC).',
                                                         'checks': 'TCN/BPDU con TC flag propagado correctamente. MAC tables flushed en switches afectados.',
                                                         'detail': 'Topology Change BPDU: Flags con TC bit=1. RSTP: el switch que detecta el cambio envía BPDU con TC flag por todos sus Designated/Root ports durante 2×Forward Delay + Hello Time.',
                                                         'name': 'Capa 2 - STP/RSTP Topology Change',
                                                         'packet_capture': {'notes': 'Verificar TC bit en BPDUs.',
                                                                            'tcpdump_filter': 'ether dst 01:80:c2:00:00:00',
                                                                            'wireshark_display_filter': 'stp.flags.tc == 1'}}],
                                             'note': 'Un topology change hace que los switches reduzcan el aging time de la MAC table a Forward Delay (15s) para evitar blackholing de tráfico unicast.',
                                             'step_title': 'Paso 5: Topology Change — Flooding de TC BPDUs'},
                                            {'action': 'Mantenimiento de la topología estable con BPDUs periódicas del Root Bridge',
                                             'device': 'Root Bridge',
                                             'layers': [{'anomalies': 'BPDUs del Root no llegan (link unidireccional, VLAN mismatch), BPDUs con Root ID incorrecto (Root Bridge flapping), BPDUs con Max Age expirado (Root Bridge caído).',
                                                         'checks': 'Root envía BPDUs cada Hello Time (2s default). Non-root switches retransmiten BPDUs por Designated ports.',
                                                         'detail': 'Configuration BPDU periódica: Root ID, Root Path Cost, Bridge ID, Port ID, Max Age (20s), Hello Time (2s), Forward Delay (15s).',
                                                         'name': 'Capa 2 - STP/RSTP BPDU periódica',
                                                         'packet_capture': {'notes': 'Verificar periodicidad de BPDUs (cada 2s en RSTP).',
                                                                            'tcpdump_filter': 'ether dst 01:80:c2:00:00:00',
                                                                            'wireshark_display_filter': 'stp'}}],
                                             'note': 'En topología estable, solo el Root Bridge genera BPDUs originales. Los demás switches las retransmiten. Si un switch no recibe BPDUs por Max Age, asume que el Root ha caído e inicia nueva elección.',
                                             'step_title': 'Paso 6: Mantenimiento — BPDUs periódicas del Root'}]}]},
  'mpbgp': {'scenarios': [{'description': 'Recorrido del establecimiento de una sesión MP-BGP con address family EVPN. Se muestra el intercambio de OPEN con Capability MP-BGP, UPDATE con NLRI EVPN Type 2 (MAC/IP advertisement), y mantenimiento de la sesión.',
                          'id': 'mpbgp_evpnnlri_type2',
                          'name': 'MP-BGP EVPN: Establecimiento y anuncio de MAC/IP (Type 2)',
                          'steps': [{'action': 'Router A inicia TCP 179 y envía OPEN con Capability MP-BGP (AFI/SAFI)',
                                    'device': 'Router A',
                                    'layers': [{'anomalies': 'Capability MP-BGP no presente (router no soporta EVPN), AFI=25 (L2VPN) o SAFI=70 (EVPN) no negociado, peer sin route-target policy (rechaza UPDATE).',
                                                'checks': 'OPEN incluye Optional Parameter Type=2 (Capability), Capability Code=1 (MP-BGP), AFI=25 (L2VPN), SAFI=70 (EVPN).',
                                                'detail': 'BGP OPEN: Marker=0xFF..., Length=29+, Type=1, Version=4, My AS=64512, Hold Time=180s, BGP Identifier=Router ID. Optional Parameters: Capability Code=1 (MP_EXT), AFI=25, SAFI=70.',
                                                'name': 'Capa 7/5 - BGP OPEN (MP-BGP)',
                                                'packet_capture': {'notes': 'Verificar Capability Code=1, AFI=25, SAFI=70 en OPEN.',
                                                                   'tcpdump_filter': 'tcp port 179',
                                                                   'wireshark_display_filter': 'bgp.type == 1'}},
                                              {'anomalies': 'TCP SYN no recibido, ACL bloqueando 179, AS mismatch.',
                                               'checks': 'Three-way handshake completo.',
                                               'detail': 'TCP SYN: SrcPort=efímero, DstPort=179, SYN=1.',
                                               'name': 'Capa 4 - Transporte (TCP)',
                                               'packet_capture': {'notes': 'Verificar SYN.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'tcp.port == 179 && tcp.flags.syn == 1'}},
                                              {'anomalies': 'IP no alcanzable, TTL expirado.',
                                               'checks': 'Ping OK.',
                                               'detail': 'IPv4: SrcIP=loopback_A, DstIP=loopback_B, Protocol=TCP, TTL=64.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'tcp.port == 179'}},
                                              {'anomalies': 'L2 errors.',
                                               'checks': 'L2 OK.',
                                               'detail': 'Ethernet: DstMAC=next_hop, SrcMAC=A_if, EtherType=0x0800.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && tcp.port == 179'}}],
                                    'note': 'MP-BGP requiere que ambos peers anuncien la capacidad MP_EXT con el AFI/SAFI correspondiente. Si no, el address family no se activa.',
                                    'step_title': 'Paso 1: OPEN con Capability MP-BGP (AFI=25, SAFI=70)'},
                                   {'action': 'Router B responde OPEN con MP-BGP capability y KEEPALIVE',
                                    'device': 'Router B',
                                    'layers': [{'anomalies': 'B no soporta EVPN (SAFI 70 no en capabilities), AS mismatch, Hold Time mismatch.',
                                                'checks': 'B responde OPEN con MP_EXT AFI=25 SAFI=70.',
                                                'detail': 'BGP OPEN: Type=1, My AS=64512, Hold Time=180s, BGP Identifier=Router ID de B. Optional Parameters: MP_EXT AFI=25 SAFI=70.',
                                                'name': 'Capa 7/5 - BGP OPEN (MP-BGP)',
                                                'packet_capture': {'notes': 'Verificar OPEN de B.',
                                                                   'tcpdump_filter': 'tcp port 179',
                                                                   'wireshark_display_filter': 'bgp.type == 1'}},
                                              {'anomalies': 'SYN-ACK no llega, TCP RST.',
                                               'checks': 'Three-way handshake completo.',
                                               'detail': 'TCP SYN-ACK: SrcPort=179, DstPort=efímero, SYN=1, ACK=1.',
                                               'name': 'Capa 4 - Transporte (TCP)',
                                               'packet_capture': {'notes': 'Verificar SYN-ACK.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'tcp.port == 179 && tcp.flags.syn == 1 && tcp.flags.ack == 1'}},
                                              {'anomalies': 'IP no alcanzable.',
                                               'checks': 'Ruta OK.',
                                               'detail': 'IPv4: SrcIP=loopback_B, DstIP=loopback_A, Protocol=TCP, TTL=64.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'tcp.port == 179'}},
                                              {'anomalies': 'L2 unidireccional.',
                                               'checks': 'L2 OK.',
                                               'detail': 'Ethernet: DstMAC=A_if_MAC, SrcMAC=B_if_MAC.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && tcp.port == 179'}}],
                                    'note': 'B recibe OPEN de A, valida AS, Router ID, y capabilities. Si todo OK, responde con OPEN propio + KEEPALIVE. La sesión pasa a Established.',
                                    'step_title': 'Paso 2: Router B responde OPEN + KEEPALIVE'},
                                   {'action': 'Router A anuncia EVPN Type 2 (MAC/IP Advertisement) con UPDATE',
                                    'device': 'Router A',
                                    'layers': [{'anomalies': 'UPDATE mal formado (Route Distinguisher missing, Ethernet Segment Identifier incorrecto, VNI no presente), RT import/export mismatch (ruta filtrada por policy), next-hop inalcanzable.',
                                                'checks': 'UPDATE contiene Path Attributes bien formados. NLRI EVPN Type 2 con RD, ESI, Ethernet Tag ID, MAC Address, IP Address, MPLS Label/VNI.',
                                                'detail': 'BGP UPDATE: Type=2, Path Attributes (ORIGIN, AS_PATH, NEXT_HOP, EXTENDED COMMUNITIES incluyendo Route Target y Encapsulation Type=VXLAN/MPLS), NLRI: Route Type=2 (MAC/IP Advertisement), Length, Route Distinguisher, ESI, Ethernet Tag ID, MAC Address Length, MAC Address, IP Address Length, IP Address, MPLS Label1 (VNI), MPLS Label2.',
                                                'name': 'Capa 7/5 - BGP UPDATE (EVPN Type 2)',
                                                'packet_capture': {'notes': 'Verificar Route Type=2, RD, ESI, MAC, IP, VNI/Label.',
                                                                   'tcpdump_filter': 'tcp port 179',
                                                                   'wireshark_display_filter': 'bgp.type == 2 && bgp.nlri.evpn.route_type == 2'}},
                                              {'anomalies': 'TCP PSH/ACK perdido, TCP window cerrada.',
                                               'checks': 'TCP ACK recibido.',
                                               'detail': 'TCP: PSH=1, ACK=1.',
                                               'name': 'Capa 4 - Transporte (TCP)',
                                               'packet_capture': {'notes': 'Verificar ACK.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'tcp.port == 179 && tcp.flags.psh == 1'}},
                                              {'anomalies': 'IP checksum erróneo, TTL expirado.',
                                               'checks': 'IP válido.',
                                               'detail': 'IPv4: SrcIP=loopback_A, DstIP=loopback_B, Protocol=TCP, TTL=64.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'tcp.port == 179'}},
                                              {'anomalies': 'L2 errors.',
                                               'checks': 'L2 OK.',
                                               'detail': 'Ethernet: DstMAC=next_hop, SrcMAC=A_if.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && tcp.port == 179'}}],
                                    'note': 'El UPDATE EVPN Type 2 anuncia un MAC address (y opcionalmente IP) asociado a un VNI/Label. B recibe el UPDATE y lo instala en su MAC-VRF si el RT import coincide.',
                                    'step_title': 'Paso 3: UPDATE EVPN Type 2 (MAC/IP Advertisement)'},
                                   {'action': 'Mantenimiento de la sesión MP-BGP con KEEPALIVE y NOTIFICATION si falla',
                                    'device': 'Router A y Router B',
                                    'layers': [{'anomalies': 'NOTIFICATION por malformación de UPDATE (Error Code=3, Subcode=attribute flags/length/flags), Hold Timer expirado, Cease administrativo.',
                                                'checks': 'Sin NOTIFICATIONs. KEEPALIVEs periódicos.',
                                                'detail': 'BGP NOTIFICATION: Type=3, Error Code (UPDATE Message Error=3), Error Subcode (Attribute Flags Error=1, Attribute Length Error=2, Malformed Attribute List=3, etc.).',
                                                'name': 'Capa 7/5 - BGP NOTIFICATION',
                                                'packet_capture': {'notes': 'Capturar NOTIFICATION para diagnosticar.',
                                                                   'tcpdump_filter': 'tcp port 179',
                                                                   'wireshark_display_filter': 'bgp.type == 3'}},
                                              {'anomalies': 'TCP FIN/RST.',
                                               'checks': 'Sin FIN/RST.',
                                               'detail': 'TCP FIN/RST.',
                                               'name': 'Capa 4 - Transporte (TCP)',
                                               'packet_capture': {'notes': 'Verificar FIN/RST.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'tcp.port == 179 && (tcp.flags.fin == 1 || tcp.flags.reset == 1)'}}],
                                    'note': 'Si hay un error en el UPDATE EVPN (ej: VNI mal formado, ESI inconsistente), B puede enviar NOTIFICATION y bajar la sesión.',
                                    'step_title': 'Paso 4: NOTIFICATION / Mantenimiento de sesión'}]}]},
  'dhcp': {'scenarios': [{'description': 'Recorrido del proceso DORA (Discover, Offer, Request, Acknowledge) de DHCPv4 entre un cliente, un relay agent (router) y un servidor DHCP.',
                          'id': 'dhcp_dora_relay',
                          'name': 'DHCPv4: Proceso DORA con Relay Agent',
                          'steps': [{'action': 'Cliente envía DHCP Discover broadcast en la red local',
                                    'device': 'Cliente DHCP',
                                    'layers': [{'anomalies': 'Cliente no envía Discover (NIC deshabilitada, DHCP client service parado), VLAN mismatch (cliente en VLAN sin DHCP relay), storm control bloqueando broadcast.',
                                                'checks': 'Cliente tiene NIC habilitada y configurada para DHCP. Red local permite broadcast UDP 67/68.',
                                                'detail': 'DHCP Discover: Operation=1 (Request), Hardware Type=1 (Ethernet), Hardware Address Length=6, Hops=0, Transaction ID=X, Seconds=0, Flags=0x8000 (broadcast), Client IP=0.0.0.0, Your IP=0.0.0.0, Server IP=0.0.0.0, Gateway IP=0.0.0.0, Client Hardware Address=MAC_cliente, Server Host Name=empty, Boot File Name=empty, Magic Cookie=0x63825363, Options: Message Type=53 (Discover), Parameter Request List, Client Identifier, Host Name.',
                                                'name': 'Capa 7/5 - DHCP Discover',
                                                'packet_capture': {'notes': 'Filtrar DHCP Discover (UDP src=68, dst=67, Option 53=1).',
                                                                   'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                   'wireshark_display_filter': 'bootp.option.dhcp == 1'}},
                                              {'anomalies': 'IP checksum erróneo, TTL no aplicable (broadcast L2).',
                                               'checks': 'IP broadcast correcto.',
                                               'detail': 'IPv4: SrcIP=0.0.0.0, DstIP=255.255.255.255, Protocol=UDP(17), TTL=128 (varía por OS).',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'Verificar SrcIP=0.0.0.0 y DstIP=255.255.255.255.',
                                                                  'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                  'wireshark_display_filter': 'bootp'}},
                                              {'anomalies': 'MAC broadcast no reenviada (switch con broadcast suppression), VLAN pruning, port-security bloqueando MAC del cliente.',
                                               'checks': 'Switch reenvía broadcast dentro de la VLAN. Cliente no bloqueado por port-security.',
                                               'detail': 'Ethernet: DstMAC=FF:FF:FF:FF:FF:FF, SrcMAC=MAC_cliente, EtherType=0x0800. Posible 802.1Q tag si cliente en VLAN diferente.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'Verificar MAC broadcast.',
                                                                  'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                  'wireshark_display_filter': 'eth.dst == ff:ff:ff:ff:ff:ff && bootp'}}],
                                    'note': 'El cliente no tiene IP aún. Envía Discover como broadcast L2 y L3. Si hay relay agent en la red, este recibe el broadcast y lo reenvía como unicast al servidor DHCP.',
                                    'step_title': 'Paso 1: Cliente envía DHCP Discover (broadcast)'},
                                   {'action': 'Relay Agent recibe Discover y reenvía como unicast al servidor DHCP (giaddr=IP_relay)',
                                    'device': 'Router / Relay Agent',
                                    'layers': [{'anomalies': 'Relay agent no configurado (ip helper-address / dhcp relay missing), relay agent en interfaz equivocada, servidor DHCP no alcanzable desde relay.',
                                                'checks': 'Relay agent tiene ip helper-address <server> en interfaz del cliente. Servidor alcanzable vía routing.',
                                                'detail': 'DHCP Relay: Operation=1 (Request), Hops=1, giaddr=IP_interfaz_relay (ej: 10.0.0.1), chaddr=MAC_cliente. Options: Message Type=53 (Discover), Relay Agent Information Option (Option 82) si está habilitado.',
                                                'name': 'Capa 7/5 - DHCP Relay Discover',
                                                'packet_capture': {'notes': 'Verificar giaddr ≠ 0.0.0.0. Verificar Option 82 si aplica.',
                                                                   'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                   'wireshark_display_filter': 'bootp.option.dhcp == 1 && bootp.ip.relay != 0.0.0.0'}},
                                              {'anomalies': 'Servidor DHCP no responde (servidor caído, pool agotado, ACL bloqueando UDP 67 desde relay).',
                                               'checks': 'Servidor DHCP UP. Pool disponible. Sin ACL bloqueando UDP 67/68 entre relay y servidor.',
                                               'detail': 'IPv4: SrcIP=IP_relay, DstIP=IP_servidor_DHCP, Protocol=UDP(17), TTL=decrementado por routing.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'Verificar routing relay→servidor.',
                                                                  'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                  'wireshark_display_filter': 'bootp'}},
                                              {'anomalies': 'MAC no resuelto hacia servidor (ARP incomplete en relay), VLAN mismatch en trunk hacia servidor.',
                                               'checks': 'ARP/ND resuelto hacia servidor. Trunk permite VLAN de servidor.',
                                               'detail': 'Ethernet: DstMAC=next_hop_MAC, SrcMAC=interfaz_relay_MAC, EtherType=0x0800.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && bootp'}}],
                                    'note': 'El relay agent añade su IP en el campo giaddr. Esto permite al servidor DHCP identificar el pool de direcciones a asignar (según la subnet del giaddr).',
                                    'step_title': 'Paso 2: Relay Agent reenvía Discover (unicast al servidor)'},
                                   {'action': 'Servidor DHCP responde con DHCP Offer unicast al relay (giaddr)',
                                    'device': 'Servidor DHCP',
                                    'layers': [{'anomalies': 'Servidor no tiene pool para la subnet del giaddr (misconfig), pool agotado, IP ofrecida duplicada, Option 82 mismatch (servidor rechaza relay).',
                                                'checks': 'Servidor tiene pool para subnet del giaddr. IP ofrecida disponible. Sin conflictos.',
                                                'detail': 'DHCP Offer: Operation=2 (Reply), Hops=1, giaddr=IP_relay, yiaddr=IP_ofrecida (ej: 10.0.0.50), siaddr=IP_servidor, chaddr=MAC_cliente, Options: Message Type=53 (Offer), Subnet Mask, Router (Gateway), DNS, Lease Time, Server Identifier.',
                                                'name': 'Capa 7/5 - DHCP Offer',
                                                'packet_capture': {'notes': 'Verificar yiaddr, siaddr, y Options.',
                                                                   'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                   'wireshark_display_filter': 'bootp.option.dhcp == 2'}},
                                              {'anomalies': 'Servidor no alcanza relay (ruta inversa falla), TTL expirado.',
                                               'checks': 'Ruta servidor→relay operativa.',
                                               'detail': 'IPv4: SrcIP=IP_servidor, DstIP=IP_relay (giaddr), Protocol=UDP(17), TTL=64.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'Verificar DstIP=giaddr.',
                                                                  'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                  'wireshark_display_filter': 'bootp'}},
                                              {'anomalies': 'L2 errors hacia relay.',
                                               'checks': 'L2 OK.',
                                               'detail': 'Ethernet: DstMAC=relay_next_hop_MAC, SrcMAC=servidor_MAC.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && bootp'}}],
                                    'note': 'El servidor ofrece una IP basada en la subnet del giaddr. Si el cliente acepta, solicitará esa IP en el siguiente paso (Request).',
                                    'step_title': 'Paso 3: Servidor responde DHCP Offer'},
                                   {'action': 'Relay Agent reenvía Offer al cliente como broadcast (o unicast si soportado)',
                                    'device': 'Router / Relay Agent',
                                    'layers': [{'anomalies': 'Relay no reenvía Offer (DHCP relay service caído, interfaz down hacia cliente), broadcast suppression en switch.',
                                                'checks': 'Relay reenvía Offer por interfaz del cliente. Switch permite broadcast.',
                                                'detail': 'DHCP Offer relayed: Operation=2, giaddr=IP_relay, yiaddr=IP_ofrecida, chaddr=MAC_cliente. Relay puede enviar como broadcast (DstIP=255.255.255.255) o unicast al cliente si conoce su MAC y la red lo soporta.',
                                                'name': 'Capa 7/5 - DHCP Relay Offer',
                                                'packet_capture': {'notes': 'Verificar que Offer llega al cliente.',
                                                                   'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                   'wireshark_display_filter': 'bootp.option.dhcp == 2'}},
                                              {'anomalies': 'IP broadcast no reenviada, VLAN mismatch.',
                                               'checks': 'Broadcast llega a cliente.',
                                               'detail': 'IPv4: SrcIP=IP_servidor o IP_relay, DstIP=255.255.255.255 (broadcast) o yiaddr.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                  'wireshark_display_filter': 'bootp'}},
                                              {'anomalies': 'MAC broadcast no reenviada, port-security.',
                                               'checks': 'Cliente recibe broadcast.',
                                               'detail': 'Ethernet: DstMAC=FF:FF:FF:FF:FF:FF, SrcMAC=relay_if_MAC.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                  'wireshark_display_filter': 'eth.dst == ff:ff:ff:ff:ff:ff && bootp'}}],
                                    'note': 'El cliente recibe uno o más Offers (si hay múltiples servidores). Elige una y responde con DHCP Request.',
                                    'step_title': 'Paso 4: Relay reenvía Offer al cliente'},
                                   {'action': 'Cliente envía DHCP Request broadcast para aceptar la oferta',
                                    'device': 'Cliente DHCP',
                                    'layers': [{'anomalies': 'Cliente no envía Request (firewall local, DHCP client parado), Request con Server Identifier incorrecto (elige servidor equivocado).',
                                                'checks': 'Cliente envía Request con Option 54 (Server Identifier) correcto.',
                                                'detail': 'DHCP Request: Operation=1, chaddr=MAC_cliente, Options: Message Type=53 (Request), Requested IP Address=yiaddr_ofrecida, Server Identifier=IP_servidor_elegido, Parameter Request List.',
                                                'name': 'Capa 7/5 - DHCP Request',
                                                'packet_capture': {'notes': 'Verificar Option 53=3 (Request) y Option 54 (Server Identifier).',
                                                                   'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                   'wireshark_display_filter': 'bootp.option.dhcp == 3'}},
                                              {'anomalies': 'Broadcast no reenviado.',
                                               'checks': 'Broadcast OK.',
                                               'detail': 'IPv4: SrcIP=0.0.0.0, DstIP=255.255.255.255, Protocol=UDP(17).',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                  'wireshark_display_filter': 'bootp'}},
                                              {'anomalies': 'MAC broadcast bloqueada.',
                                               'checks': 'MAC broadcast OK.',
                                               'detail': 'Ethernet: DstMAC=FF:FF:FF:FF:FF:FF, SrcMAC=MAC_cliente.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                  'wireshark_display_filter': 'eth.dst == ff:ff:ff:ff:ff:ff && bootp'}}],
                                    'note': 'El Request es broadcast para informar a todos los servidores cuál fue la oferta aceptada. Los servidores no elegidos liberan la IP reservada.',
                                    'step_title': 'Paso 5: Cliente envía DHCP Request (broadcast)'},
                                   {'action': 'Servidor responde con DHCP Acknowledge (ACK) unicast al relay, que lo reenvía al cliente',
                                    'device': 'Servidor DHCP → Relay Agent → Cliente',
                                    'layers': [{'anomalies': 'Servidor envía NAK (IP ya asignada a otro cliente, pool incorrecto), ACK no llega al cliente (relay falla, broadcast suppression).',
                                                'checks': 'Servidor confirma asignación con ACK.',
                                                'detail': 'DHCP ACK: Operation=2, yiaddr=IP_asignada, siaddr=IP_servidor, chaddr=MAC_cliente, Options: Message Type=53 (ACK), Subnet Mask, Router, DNS, Lease Time, Server Identifier.',
                                                'name': 'Capa 7/5 - DHCP ACK',
                                                'packet_capture': {'notes': 'Verificar Option 53=5 (ACK).',
                                                                   'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                   'wireshark_display_filter': 'bootp.option.dhcp == 5'}},
                                              {'anomalies': 'IP no alcanzable, TTL expirado.',
                                               'checks': 'Routing OK.',
                                               'detail': 'IPv4: SrcIP=IP_servidor, DstIP=IP_relay (giaddr) o 255.255.255.255.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                  'wireshark_display_filter': 'bootp'}},
                                              {'anomalies': 'L2 errors.',
                                               'checks': 'L2 OK.',
                                               'detail': 'Ethernet: DstMAC=next_hop, SrcMAC=servidor/relay.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'udp port 67 or udp port 68',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && bootp'}}],
                                    'note': 'Tras recibir ACK, el cliente configura su IP, máscara, gateway y DNS. Comienza el lease timer y envía DHCP Inform o renueva al 50% del lease.',
                                    'step_title': 'Paso 6: Servidor envía DHCP ACK (asignación confirmada)'}]}]},
  'netflow': {'scenarios': [{'description': 'Recorrido de un registro NetFlow v5/v9/IPFIX desde un router exportador hasta un colector. Se muestra la creación del flow en el router, el empaquetado en UDP, y la recepción en el colector.',
                             'id': 'netflow_v9_export',
                             'name': 'NetFlow v9/IPFIX: Exportación de flow al colector',
                             'steps': [{'action': 'Paquete IP atraviesa el router y el motor de NetFlow crea un registro de flow',
                                       'device': 'Router Exportador',
                                       'layers': [{'anomalies': 'NetFlow no habilitado en interfaz de ingreso (no se crea flow), sampling rate muy alta (solo 1 de cada N paquetes crea flow, estadísticas incompletas), ACL bloqueando el tráfico antes de que NetFlow lo vea.',
                                                   'checks': 'NetFlow habilitado en interfaz de ingreso (ip flow ingress / flow monitor). Sampling rate adecuado (1:1 para debug, 1:1000 para producción).',
                                                   'detail': 'NetFlow crea un flow record con: src IP, dst IP, src port, dst port, protocol, TOS, ingress interface, bytes, packets, start time, end time. En v9/IPFIX usa template-based records.',
                                                   'name': 'Capa 3/4 - NetFlow Flow Record',
                                                   'packet_capture': {'notes': 'NetFlow opera en el data plane del router. No genera paquetes de red en este paso.',
                                                                      'tcpdump_filter': 'No aplicable',
                                                                      'wireshark_display_filter': 'No aplicable'}},
                                                 {'anomalies': 'Paquete droppeado por ACL o QoS antes de contabilización.',
                                                  'checks': 'Paquete atraviesa el router y es contabilizado.',
                                                  'detail': 'IPv4/TCP/UDP/ICMP header del paquete original analizado por el motor de NetFlow.',
                                                  'name': 'Capa 3/4 - Paquete original',
                                                  'packet_capture': {'notes': 'Capturar el paquete original en ingreso/egreso para comparar con el flow record.',
                                                                     'tcpdump_filter': 'host <src_ip> and host <dst_ip>',
                                                                     'wireshark_display_filter': 'ip.addr == <src_ip> && ip.addr == <dst_ip>'}}],
                                       'note': 'NetFlow crea flows basado en tuplas de 5 o 7 campos. Un flow es unidirectional (A→B). El tráfico de retorno (B→A) genera un flow separado.',
                                       'step_title': 'Paso 1: Router crea flow record del paquete'},
                                      {'action': 'El router agrupa múltiples flows en un NetFlow Export Packet y lo envía al colector',
                                       'device': 'Router Exportador',
                                       'layers': [{'anomalies': 'Template no enviado (colector no puede decodificar v9/IPFIX), export packet excede MTU (fragmentación no deseada), timeout de active/inactive flow mal configurado (flows no exportados oportunamente).',
                                                   'checks': 'Template enviado periódicamente (v9/IPFIX). Export packet ≤ MTU. Active timeout ≤ 60s. Inactive timeout ≤ 15s.',
                                                   'detail': 'NetFlow Export Packet: UDP Header: SrcPort=efímero, DstPort=2055 (NetFlow) o 4739 (IPFIX) o 6343 (sFlow). NetFlow v9 Header: Version=9, Count=N, System Uptime, UNIX Seconds, Sequence Number, Source ID. FlowSet ID=template ID, Length=var, Records (campos definidos en template).',
                                                   'name': 'Capa 7 - NetFlow Export (v9/IPFIX)',
                                                   'packet_capture': {'notes': 'Verificar Version, Count, Sequence Number, Source ID. En v9/IPFIX verificar Template FlowSet primero.',
                                                                      'tcpdump_filter': 'udp port 2055 or udp port 4739 or udp port 6343',
                                                                      'wireshark_display_filter': 'cflow'}},
                                                 {'anomalies': 'UDP checksum erróneo, datagrama truncado.',
                                                  'checks': 'UDP checksum válido.',
                                                  'detail': 'UDP Header: SrcPort=efímero, DstPort=2055/4739/6343, Length=var, Checksum=var.',
                                                  'name': 'Capa 4 - Transporte (UDP)',
                                                  'packet_capture': {'notes': 'Verificar puertos y checksum UDP.',
                                                                     'tcpdump_filter': 'udp port 2055 or udp port 4739 or udp port 6343',
                                                                     'wireshark_display_filter': 'udp.port == 2055 || udp.port == 4739 || udp.port == 6343'}},
                                                 {'anomalies': 'IP no alcanzable hacia colector, TTL expirado, MTU path issue.',
                                                  'checks': 'Colector alcanzable vía L3. MTU ≥ 1500. Sin ACL bloqueando UDP 2055/4739/6343.',
                                                  'detail': 'IPv4: SrcIP=interfaz_exportador, DstIP=IP_colector, Protocol=UDP(17), TTL=64.',
                                                  'name': 'Capa 3 - Red (IPv4)',
                                                  'packet_capture': {'notes': 'Verificar DstIP=colector.',
                                                                     'tcpdump_filter': 'udp port 2055 or udp port 4739 or udp port 6343',
                                                                     'wireshark_display_filter': 'udp.port == 2055 || udp.port == 4739 || udp.port == 6343'}},
                                                 {'anomalies': 'MAC no resuelto (ARP incomplete), VLAN mismatch, interface errors.',
                                                  'checks': 'L2 estable hacia colector (o next-hop).',
                                                  'detail': 'Ethernet: DstMAC=next_hop_MAC, SrcMAC=exportador_if_MAC, EtherType=0x0800.',
                                                  'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                  'packet_capture': {'notes': 'N/A',
                                                                     'tcpdump_filter': 'udp port 2055 or udp port 4739 or udp port 6343',
                                                                     'wireshark_display_filter': 'eth.type == 0x0800 && (udp.port == 2055 || udp.port == 4739 || udp.port == 6343)'}}],
                                       'note': 'En NetFlow v9/IPFIX, el template define qué campos se exportan. El colector necesita recibir el template antes de poder decodificar los data records. El template se envía periódicamente.',
                                       'step_title': 'Paso 2: Router exporta NetFlow Packet UDP al colector'},
                                      {'action': 'Colector recibe y decodifica el NetFlow Export Packet',
                                       'device': 'Colector NetFlow (nfdump / ElastiFlow / SolarWinds)',
                                       'layers': [{'anomalies': 'Colector no recibe (firewall, NAT, puerto incorrecto), template desconocido (decodificación fallida), sequence number desalineado (pérdida de paquetes).',
                                                   'checks': 'Colector escucha en UDP 2055/4739/6343. Template recibido y cacheado. Sequence numbers consecutivos (sin gaps).',
                                                   'detail': 'Colector parsea NetFlow Header, FlowSet ID, Length, y Records. Almacena en base de datos / archivo.',
                                                   'name': 'Capa 7 - NetFlow Colector',
                                                   'packet_capture': {'notes': 'Verificar en colector que sequence numbers son consecutivos. Gaps indican pérdida de export packets.',
                                                                      'tcpdump_filter': 'udp port 2055 or udp port 4739 or udp port 6343',
                                                                      'wireshark_display_filter': 'cflow'}},
                                                 {'anomalies': 'UDP datagrama truncado (snaplen insuficiente en captura), checksum erróneo.',
                                                  'checks': 'UDP checksum válido. Datagrama completo.',
                                                  'detail': 'UDP: SrcPort=efímero, DstPort=2055/4739/6343, Length, Checksum.',
                                                  'name': 'Capa 4 - Transporte (UDP)',
                                                  'packet_capture': {'notes': 'N/A',
                                                                     'tcpdump_filter': 'udp port 2055 or udp port 4739 or udp port 6343',
                                                                     'wireshark_display_filter': 'udp.port == 2055 || udp.port == 4739 || udp.port == 6343'}},
                                                 {'anomalies': 'IP checksum erróneo, TTL expirado.',
                                                  'checks': 'IP válido.',
                                                  'detail': 'IPv4: SrcIP=exportador, DstIP=colector, Protocol=UDP, TTL=64.',
                                                  'name': 'Capa 3 - Red (IPv4)',
                                                  'packet_capture': {'notes': 'N/A',
                                                                     'tcpdump_filter': 'udp port 2055 or udp port 4739 or udp port 6343',
                                                                     'wireshark_display_filter': 'udp.port == 2055 || udp.port == 4739 || udp.port == 6343'}},
                                                 {'anomalies': 'L2 errors.',
                                                  'checks': 'L2 OK.',
                                                  'detail': 'Ethernet: DstMAC=colector_MAC, SrcMAC=next_hop_MAC.',
                                                  'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                  'packet_capture': {'notes': 'N/A',
                                                                     'tcpdump_filter': 'udp port 2055 or udp port 4739 or udp port 6343',
                                                                     'wireshark_display_filter': 'eth.type == 0x0800 && (udp.port == 2055 || udp.port == 4739 || udp.port == 6343)'}}],
                                       'note': 'El colector debe mantener un cache de templates por Source ID. Si el router reinicia, el Source ID puede cambiar y el colector necesita esperar el nuevo template.',
                                       'step_title': 'Paso 3: Colector recibe y decodifica NetFlow'},
                                      {'action': 'Mantenimiento: exportación periódica de flows activos/inactivos y templates',
                                       'device': 'Router Exportador',
                                       'layers': [{'anomalies': 'Active timeout muy largo (flows acumulados en router, memoria agotada), inactive timeout muy corto (muchos export packets pequeños, overhead alto), template no reenviado tras reinicio del colector.',
                                                   'checks': 'Active timeout ≤ 60s (recomendado). Inactive timeout ≤ 15s. Template resend cada 1-5 minutos.',
                                                   'detail': 'NetFlow Export periódico: flows activos exportados cada active timeout. flows inactivos exportados tras inactive timeout. Template reenviado periódicamente.',
                                                   'name': 'Capa 7 - NetFlow Maintenance',
                                                   'packet_capture': {'notes': 'Verificar periodicidad de export packets y template resends.',
                                                                      'tcpdump_filter': 'udp port 2055 or udp port 4739 or udp port 6343',
                                                                      'wireshark_display_filter': 'cflow'}}],
                                       'note': 'En producción, los timeouts deben balancear granularidad vs overhead. Un active timeout de 60s e inactive de 15s es un buen punto de partida para la mayoría de las redes.',
                                       'step_title': 'Paso 4: Mantenimiento — Exportación periódica'}]}]},
'adtran_ta5000': {'scenarios': [{'description': 'Recorrido completo de un descubrimiento PPPoE (PADI/PADO/PADR/PADS) '
                                                 'y negociación PPP LCP/IPCP desde un ONT conectado a una OLT ADTRAN '
                                                 'TA5000, a través de splitters GPON, hasta el chasis TA5000 y la red '
                                                 'de agregación hacia un BNG/BRAS. Se muestra la encapsulación GEM, '
                                                 'T-CONT y el forwarding L2/L3 en cada salto.',
                                  'id': 'adtran_ta5000_pppoe_gpon',
                                  'name': 'ADTRAN TA5000 - Sesión PPPoE desde ONT hasta BNG',
                                  'steps': [{'action': 'El ONT recibe o genera la trama PPPoE Discovery PADI y la '
                                                       'envía por la interfaz LAN',
                                             'device': 'ONT / Puerto LAN del suscriptor',
                                             'layers': [{'anomalies': 'ONT no bridgea tramas de broadcast (filtrado '
                                                                      'MAC), CPE no inicia PPPoE (firmware/driver), '
                                                                      'VLAN tag en LAN no esperada por el ONT.',
                                                         'checks': 'Puerto LAN del ONT Up/Up; CPE envía tramas PPPoE '
                                                                   'correctamente formadas; sin VLAN tag inesperado '
                                                                   'que aisle el tráfico.',
                                                         'detail': 'DstMAC=FF:FF:FF:FF:FF:FF (broadcast), '
                                                                   'SrcMAC=MAC_CPE_cliente, EtherType=0x8863 (PPPoE '
                                                                   'Discovery). PPPoE Header: Ver=1, Type=1, Code=0x09 '
                                                                   '(PADI), Session_ID=0x0000. Tags: Service-Name, '
                                                                   'Host-Uniq.',
                                                         'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                         'packet_capture': {'notes': 'Filtrar por EtherType 0x8863 '
                                                                                     '(Discovery) o 0x8864 (Session).',
                                                                            'tcpdump_filter': 'pppoes || pppoe',
                                                                            'wireshark_display_filter': 'pppoes || '
                                                                                                        'pppoe'}}],
                                             'note': 'Desde la perspectiva del suscriptor, el ONT es un bridge L2 '
                                                     'transparente. La trama Ethernet broadcast debe alcanzar la OLT '
                                                     'para que el BNG responda.',
                                             'step_title': 'Paso 1: ONT envía PADI broadcast en LAN'},
                                            {'action': 'El ONT encapsula la trama Ethernet en un frame GEM GPON y '
                                                       'transmite en la ventana TDMA asignada',
                                             'device': 'ONT óptico / Splitter GPON',
                                             'layers': [{'anomalies': 'ONT en estado O1-O4 (no sincronizado), GEM port '
                                                                      'no mapeado a la interfaz LAN (OMCI misconfig), '
                                                                      'T-CONT sin asignación de ancho de banda (DBRu '
                                                                      'no reportado), pérdida de señal óptica (LOS).',
                                                         'checks': 'ONT está en estado O5 (Operation) en la OLT. PLOAM '
                                                                   'messages Up/Down funcionando. GEM port de datos '
                                                                   'está activo y mapeado al puerto LAN del ONT en la '
                                                                   'configuración OMCI.',
                                                         'detail': 'GEM Header (5 bytes): PLI=Payload Length '
                                                                   'Indicator, Port ID=GEM_port_dato (ej: 1024), '
                                                                   'PTI=Payload Type Indicator (0=user data), '
                                                                   'HEC=Header Error Control.\n'
                                                                   'T-CONT ID (Alloc-ID): Asignado por la OLT vía '
                                                                   'PLOAM (ej: Alloc-ID=256). El ONT usa este T-CONT '
                                                                   'para solicitar ancho de banda upstream en los '
                                                                   'reportes DBRu.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM)',
                                                         'packet_capture': {'notes': 'Capturar en interfaz PON del '
                                                                                     'TA5000 si soporta port mirror, o '
                                                                                     'usar CLI OMCI debug.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No aplicable '
                                                                                                        '(GPON es '
                                                                                                        'óptico L1, '
                                                                                                        'usar OMCI/GEM '
                                                                                                        'del OLT)'}},
                                                        {'anomalies': 'MTU de GEM menor que la trama Ethernet (drop '
                                                                      'silencioso), GEM frame corrupto (HEC error).',
                                                         'checks': 'La trama Ethernet no se fragmenta dentro del GEM '
                                                                   'frame; tamaño ≤ MTU GEM (ej: 1518 bytes).',
                                                         'detail': 'Trama Ethernet completa encapsulada en el payload '
                                                                   'GEM: DstMAC=broadcast, SrcMAC=MAC_CPE, '
                                                                   'EtherType=0x8863 (PPPoE Discovery).',
                                                         'name': 'Capa 2 - Enlace de Datos (Ethernet sobre GEM)',
                                                         'packet_capture': {'notes': 'Si hay port-mirror en OLT, '
                                                                                     'filtrar por PPPoE.',
                                                                            'tcpdump_filter': 'pppoes || pppoe',
                                                                            'wireshark_display_filter': 'pppoes || '
                                                                                                        'pppoe'}}],
                                             'note': 'En GPON, el tráfico upstream usa TDMA. El ONT espera asignación '
                                                     'de BWmap desde la OLT para transmitir en su T-CONT. La trama '
                                                     'Ethernet se mapea a un GEM port específico.',
                                             'step_title': 'Paso 2: ONT → OLT GPON encapsulación'},
                                            {'action': 'La OLT recibe el frame GEM, desencapsula la trama Ethernet y '
                                                       'la reenvía por el puerto de uplink/agregación',
                                             'device': 'OLT ADTRAN TA5000',
                                             'layers': [{'anomalies': 'GEM Port ID desconocido (provisioning '
                                                                      'incompleto), errores de HEC (interferencia '
                                                                      'óptica), ONT-ID no asignado (PLOAM fallido), '
                                                                      'descarte por policing en el T-CONT.',
                                                         'checks': 'GEM Port ID está registrado en la OLT para el '
                                                                   'ONT-ID correspondiente. OMCI provisioning creó el '
                                                                   'GEM connection correctamente. Sin errores de HEC '
                                                                   'en la interfaz PON.',
                                                         'detail': 'OLT verifica el GEM Header (Port ID, HEC). El GEM '
                                                                   'Port ID identifica el flujo de datos del ONT. El '
                                                                   'frame GEM se desencapsula y se extrae la trama '
                                                                   'Ethernet original.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM) - Recepción',
                                                         'packet_capture': {'notes': 'Verificar contadores GEM/HEC en '
                                                                                     'CLI del TA5000.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No aplicable '
                                                                                                        '(GPON L1)'}},
                                                        {'anomalies': 'VLAN mismatch entre la configuración del TA5000 '
                                                                      'y el agregador, bridge-domain incompleto, '
                                                                      'spanning-tree bloqueando el puerto de uplink, '
                                                                      'MTU insuficiente en uplink.',
                                                         'checks': 'Interfaz PON del TA5000 Up/Up. Bridge-domain o '
                                                                   'VLAN de servicio correctamente configurada. Uplink '
                                                                   'hacia la red de agregación en estado forwarding.',
                                                         'detail': 'Trama Ethernet: DstMAC=broadcast, SrcMAC=MAC_CPE, '
                                                                   'EtherType=0x8863. El TA5000 puede añadir una VLAN '
                                                                   'tag de servicio (S-VLAN) o mantener la tag del '
                                                                   'cliente (C-VLAN) según el modelo de negocio.',
                                                         'name': 'Capa 2 - Enlace de Datos (Ethernet/Bridge)',
                                                         'packet_capture': {'notes': 'Mirror en puerto uplink del '
                                                                                     'TA5000. Filtrar por VLAN de '
                                                                                     'servicio.',
                                                                            'tcpdump_filter': 'pppoes || pppoe || vlan',
                                                                            'wireshark_display_filter': 'pppoes || '
                                                                                                        'pppoe || '
                                                                                                        'vlan.id == '
                                                                                                        'X'}}],
                                             'note': 'El TA5000 actúa como OLT. Recibe el GEM frame upstream, usa el '
                                                     'GEM Port ID para identificar el ONT/T-CONT, extrae la trama '
                                                     'Ethernet y la entrega al dominio de bridge o VLAN configurado.',
                                             'step_title': 'Paso 3: TA5000 procesa frame GPON y bridgea hacia uplink'},
                                            {'action': 'Forwarding L2/L3 a través de la red de agregación hacia el '
                                                       'BNG/BRAS',
                                             'device': 'Switch/Router de agregación',
                                             'layers': [{'anomalies': 'VLAN pruning en trunk (broadcast filtrada), MAC '
                                                                      'learning límite alcanzado, loop protection '
                                                                      'bloqueando broadcast, BNG en VLAN diferente.',
                                                         'checks': 'Trunk de agregación permite la VLAN de servicio. '
                                                                   'MAC learning del CPE presente en switches '
                                                                   'intermedios. Broadcast domain llega hasta la '
                                                                   'interfaz del BNG.',
                                                         'detail': 'DstMAC=FF:FF:FF:FF:FF:FF, SrcMAC=MAC_CPE, '
                                                                   'EtherType=0x8863. Posible 802.1Q tag: VLAN=100 '
                                                                   '(S-VLAN de servicio) o QinQ (C-VLAN + S-VLAN).',
                                                         'name': 'Capa 2 - Enlace de Datos (Ethernet/VLAN)',
                                                         'packet_capture': {'notes': 'Capturar en trunk de agregación '
                                                                                     'o en puerto hacia BNG.',
                                                                            'tcpdump_filter': 'pppoes || pppoe || vlan '
                                                                                              '100',
                                                                            'wireshark_display_filter': 'pppoes || '
                                                                                                        'pppoe || '
                                                                                                        'vlan.id == '
                                                                                                        '100'}},
                                                        {'anomalies': 'Filtrado de EtherType 0x8863 en algún '
                                                                      'dispositivo intermedio (ACL o policy).',
                                                         'checks': 'N/A para esta etapa.',
                                                         'detail': 'No hay IP aún. PPPoE Discovery opera puramente a '
                                                                   'L2 antes de establecer la sesión.',
                                                         'name': 'Capa 3 - Red (IP)',
                                                         'packet_capture': {'notes': 'Confirmar que no hay IP aún; '
                                                                                     'solo PPPoE Discovery.',
                                                                            'tcpdump_filter': 'not ip and pppoes',
                                                                            'wireshark_display_filter': '!ip && '
                                                                                                        'pppoes'}}],
                                             'note': 'El tráfico PPPoE Discovery (broadcast) debe llegar al BNG para '
                                                     'que este responda. Los switches de agregación reenvían la '
                                                     'broadcast dentro de la VLAN de servicio.',
                                             'step_title': 'Paso 4: Agregación → BNG (L2/L3 forwarding)'},
                                            {'action': 'El BNG recibe el PADI broadcast y responde con PADO unicast (o '
                                                       'broadcast en algunos casos)',
                                             'device': 'BNG/BRAS',
                                             'layers': [{'anomalies': 'BNG no responde (PPPoE service disabled), '
                                                                      'filtro de MAC en agregación bloquea retorno, '
                                                                      'Service-Name mismatch (PADO no enviado), límite '
                                                                      'de sesiones PPPoE alcanzado.',
                                                         'checks': 'BNG tiene la interfaz de acceso configurada para '
                                                                   'PPPoE. Servicio AAA/RADIUS disponible. MAC del CPE '
                                                                   'alcanzable vía L2 (la respuesta PADO es unicast).',
                                                         'detail': 'Rx: EtherType=0x8863, Code=0x09 (PADI). Tx: '
                                                                   'DstMAC=MAC_CPE, SrcMAC=MAC_BNG, EtherType=0x8863, '
                                                                   'Code=0x07 (PADO). Session_ID=0x0000. Tags: '
                                                                   'AC-Name, Service-Name.',
                                                         'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                         'packet_capture': {'notes': 'Filtrar PADI (0x09) y PADO '
                                                                                     '(0x07) en Wireshark.',
                                                                            'tcpdump_filter': 'pppoes and (pppoe[0:1] '
                                                                                              '== 0x07 or pppoe[0:1] '
                                                                                              '== 0x09)',
                                                                            'wireshark_display_filter': 'pppoe.code == '
                                                                                                        '0x07 || '
                                                                                                        'pppoe.code == '
                                                                                                        '0x09'}}],
                                             'note': 'El BNG escucha PPPoE Discovery en la interfaz de acceso. Al '
                                                     'recibir PADI, valida el Service-Name tag y responde con PADO '
                                                     'ofreciendo la sesión.',
                                             'step_title': 'Paso 5: BNG recibe PPPoE y envía PADO'},
                                            {'action': 'Intercambio PADR/PADS y negociación PPP LCP/IPCP',
                                             'device': 'ONT → TA5000 → Agregación → BNG',
                                             'layers': [{'anomalies': 'Session_ID duplicado, GEM port cambia durante '
                                                                      'la sesión (drop), MAC del BNG no resuelta en el '
                                                                      'CPE.',
                                                         'checks': 'Session_ID único asignado. Las tramas de sesión '
                                                                   'atraviesan el mismo GEM port, T-CONT y VLAN de '
                                                                   'servicio. Sin broadcast en esta etapa.',
                                                         'detail': 'EtherType=0x8864 (PPPoE Session). PPPoE Header: '
                                                                   'Session_ID=0x00XX (asignado por BNG). La trama es '
                                                                   'unicast L2 entre CPE y BNG (DstMAC=MAC_BNG, '
                                                                   'SrcMAC=MAC_CPE) y viceversa.',
                                                         'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                                         'packet_capture': {'notes': 'EtherType 0x8864 (PPPoE '
                                                                                     'Session). Seguir Session_ID '
                                                                                     'específico.',
                                                                            'tcpdump_filter': 'pppoes',
                                                                            'wireshark_display_filter': 'pppoes && '
                                                                                                        'pppoe.code == '
                                                                                                        '0x00'}},
                                                        {'anomalies': 'LCP Configure-NACK/REJ (MRU mismatch), '
                                                                      'autenticación fallida (RADIUS reject), IPCP '
                                                                      'Configure-NACK (pool de IPs agotado), looped '
                                                                      'PPP keepalives.',
                                                         'checks': 'LCP negocia MRU compatible (típicamente 1492 para '
                                                                   'PPPoE). Autenticación RADIUS/AAA exitosa. IPCP '
                                                                   'asigna IP, máscara, gateway y DNS al suscriptor.',
                                                         'detail': 'PPP Header: Protocol=0xC021 (LCP) o 0x8021 (IPCP). '
                                                                   'LCP: Configure-Request/ACK con MRU, Authentication '
                                                                   '(PAP/CHAP). IPCP: Configure-Request/ACK con '
                                                                   'IP-Address (asignada por BNG), Primary/Secondary '
                                                                   'DNS.',
                                                         'name': 'Capa 3 - PPP (LCP/IPCP)',
                                                         'packet_capture': {'notes': 'En Wireshark expandir PPP → '
                                                                                     'Protocol. Filtrar LCP (0xC021) e '
                                                                                     'IPCP (0x8021).',
                                                                            'tcpdump_filter': 'pppoes',
                                                                            'wireshark_display_filter': 'pppoes && '
                                                                                                        '(ppp.protocol '
                                                                                                        '== 0xc021 || '
                                                                                                        'ppp.protocol '
                                                                                                        '== 0x8021)'}}],
                                             'note': 'El CPE envía PADR (unicast) y el BNG responde PADS asignando '
                                                     'Session_ID. Luego inicia LCP (MRU, auth) e IPCP (IP address, '
                                                     'DNS).',
                                             'step_title': 'Paso 6: Sesión establecida - PPP LCP/IPCP'},
                                            {'action': 'El CPE envía el primer paquete IP a través del túnel PPPoE '
                                                       'hacia Internet',
                                             'device': 'CPE / BNG',
                                             'layers': [{'anomalies': 'Ruta faltante en CPE, BNG sin ruta de retorno '
                                                                      '(IP no en tabla), NAT overflow, MTU path issue '
                                                                      '(1492 vs 1500, requiere TCP MSS clamping).',
                                                         'checks': 'Ruta por defecto del CPE apunta a la interfaz '
                                                                   'PPPoE. BNG tiene ruta hacia Internet. NAT o '
                                                                   'routing público configurado correctamente en el '
                                                                   'BNG.',
                                                         'detail': 'SrcIP=IP_asignada_BNG (ej: 100.64.1.10), '
                                                                   'DstIP=IP_destino_internet, TTL=64, '
                                                                   'Protocol=TCP(6). PPP Protocol=0x0021 (IPv4).',
                                                         'name': 'Capa 3 - Red (IPv4)',
                                                         'packet_capture': {'notes': 'Filtrar IP sobre PPPoE Session. '
                                                                                     'Verificar MSS/MTU.',
                                                                            'tcpdump_filter': 'pppoes and ip',
                                                                            'wireshark_display_filter': 'pppoes && '
                                                                                                        'ip'}},
                                                        {'anomalies': 'Session_ID desconocido en BNG (sesión caída), '
                                                                      'GEM port congestionado (T-CONT sin BW '
                                                                      'suficiente), drops de QoS en el TA5000 o BNG.',
                                                         'checks': 'GEM port de datos activo, T-CONT con ancho de '
                                                                   'banda asignado según SLA. Sin drops en la cola '
                                                                   'GEM/T-CONT.',
                                                         'detail': 'EtherType=0x8864 (PPPoE Session), Session_ID '
                                                                   'activo. DstMAC=MAC_BNG, SrcMAC=MAC_CPE. '
                                                                   'Encapsulación GEM con mismo GEM Port ID y T-CONT.',
                                                         'name': 'Capa 2 - Enlace de Datos (PPPoE Session)',
                                                         'packet_capture': {'notes': 'Mirror en uplink del TA5000 o en '
                                                                                     'BNG.',
                                                                            'tcpdump_filter': 'pppoes and ip',
                                                                            'wireshark_display_filter': 'pppoes && '
                                                                                                        'ip'}}],
                                             'note': 'Con la sesión PPPoE activa y la IP asignada, el tráfico de datos '
                                                     'fluye encapsulado en PPPoE Session (0x8864) a través de toda la '
                                                     'cadena GPON.',
                                             'step_title': 'Paso 7: IP asignada - Primer paquete de datos'}]},
                                 {'description': 'Simulación del flujo de mensajes OMCI (ONT Management and Control '
                                                 'Interface) entre la OLT (TA5000 o Huawei/ZTE) y un ONT durante el '
                                                 'proceso de provisioning. Se muestra el uso de PLOAM, GEM port 4095 '
                                                 '(o dedicado), y la transferencia de MIBs.',
                                  'id': 'gpon_omci_provisioning',
                                  'name': 'GPON OLT→ONT - Flujo de aprovisionamiento OMCI',
                                  'steps': [{'action': 'El ONT realiza el procedimiento de ranging y envía su Serial '
                                                       'Number o LOID a la OLT',
                                             'device': 'ONT (GPON)',
                                             'layers': [{'anomalies': 'ONT no responde al Serial_Number_Request (laser '
                                                                      'apagado, fibra cortada), Serial Number '
                                                                      'duplicado en la red, LOID no coincide '
                                                                      '(autenticación fallida), nivel óptico fuera de '
                                                                      'rango (laser degradado).',
                                                         'checks': 'Nivel óptico dentro de rango (TX ONT ~+1.5 dBm, RX '
                                                                   'ONT ~-8 a -28 dBm). ONT sincronizado en O5. Serial '
                                                                   'Number o LOID coincide con la base de datos de la '
                                                                   'OLT.',
                                                         'detail': 'PLOAM Downstream (OLT→ONT): MsgType=0x01 '
                                                                   '(Serial_Number_Request), ONU-ID=0xFF (broadcast '
                                                                   'para ONTs no registrados). PLOAM Upstream '
                                                                   '(ONT→OLT): MsgType=0x02 (Serial_Number_Response), '
                                                                   'incluye Vendor ID, Serial Number (8 bytes) o LOID.',
                                                         'name': 'Capa 2/1 - GPON Frame (PLOAM)',
                                                         'packet_capture': {'notes': 'Usar CLI del OLT: show gpon onu '
                                                                                     'state, show gpon onu detail.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No aplicable '
                                                                                                        '(PLOAM es '
                                                                                                        'L1/L2 GPON)'}},
                                                        {'anomalies': 'OMCI prematuro antes de tener ONT-ID asignado '
                                                                      '(descartado por OLT).',
                                                         'checks': 'N/A - OMCI se establece después de asignar ONT-ID.',
                                                         'detail': 'Aún no hay OMCI. Solo PLOAM para el descubrimiento '
                                                                   'inicial.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM - OMCI)',
                                                         'packet_capture': {'notes': 'N/A',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'Al encenderse, el ONT espera la sincronización de frame '
                                                     'downstream. Una vez sincronizado, responde al Serial Number '
                                                     'Request de la OLT con su SN/LOID en el campo de PLOAM upstream.',
                                             'step_title': 'Paso 1: ONT se enciende y envía SN/LOID upstream'},
                                            {'action': 'La OLT valida el SN/LOID y asigna un ONT-ID único al ONT '
                                                       'mediante PLOAM',
                                             'device': 'OLT (TA5000 / Huawei / ZTE)',
                                             'layers': [{'anomalies': 'ONT-ID ya en uso (conflicto de provisioning), '
                                                                      'SN/LOID no encontrado en OLT (ONT rechazado), '
                                                                      'Ranging fallido (delay excesivo, distancia '
                                                                      'fuera de rango 0-20 km), PLOAM descartado por '
                                                                      'errores de HEC.',
                                                         'checks': 'OLT tiene el ONT pre-provisionado con su SN/LOID '
                                                                   'correcto. ONT-ID asignado no está en uso por otro '
                                                                   'ONT. Ranging completado exitosamente (equalization '
                                                                   'delay calculada).',
                                                         'detail': 'PLOAM Downstream: MsgType=0x03 (Assign_ONU-ID), '
                                                                   'ONU-ID=0xFF→asignado (ej: 0x01), Payload contiene '
                                                                   'el Serial Number del ONT destino para confirmar la '
                                                                   'asignación. Seguido de MsgType=0x04 (Ranging_Time) '
                                                                   'para ajustar el equalization delay.',
                                                         'name': 'Capa 2/1 - GPON Frame (PLOAM)',
                                                         'packet_capture': {'notes': 'CLI OLT: show gpon onu state, '
                                                                                     'show gpon onu detail.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}},
                                                        {'anomalies': 'N/A',
                                                         'checks': 'N/A',
                                                         'detail': 'Aún no se establecen GEM connections de datos. '
                                                                   'Solo PLOAM para control.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM)',
                                                         'packet_capture': {'notes': 'N/A',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'La OLT verifica el SN/LOID contra su base de datos de '
                                                     'suscriptores. Si coincide, envía un mensaje PLOAM Assign ONU-ID '
                                                     'y luego configura los parámetros iniciales del T-CONT y '
                                                     'Alloc-ID.',
                                             'step_title': 'Paso 2: OLT asigna ONT-ID vía PLOAM'},
                                            {'action': 'Se crea el GEM connection para OMCI y comienza el intercambio '
                                                       'de mensajes OMCI',
                                             'device': 'OLT ↔ ONT',
                                             'layers': [{'anomalies': 'GEM Port 4095 en conflicto con datos '
                                                                      '(provisioning incorrecto), OMCI Create fallido '
                                                                      '(ONT no responde), T-CONT de gestión sin BW '
                                                                      'asignado (timeout OMCI).',
                                                         'checks': 'GEM Port para OMCI creado correctamente en OLT y '
                                                                   'ONT vía OMCI Create. T-CONT de gestión tiene ancho '
                                                                   'de banda mínimo garantizado. OMCI MIB sync lista.',
                                                         'detail': 'GEM Header: Port ID=4095 (u otro GEM port dedicado '
                                                                   'para OMCI), PTI=0 (user data), HEC válido. '
                                                                   'Alloc-ID/T-CONT para OMCI separado del tráfico de '
                                                                   'datos (ej: T-CONT 0 o T-CONT gestión).',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM)',
                                                         'packet_capture': {'notes': 'Capturar OMCI solo vía '
                                                                                     'port-mirror especializado del '
                                                                                     'OLT o debug OMCI CLI.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No aplicable '
                                                                                                        '(OMCI sobre '
                                                                                                        'GEM, no '
                                                                                                        'TCP/IP)'}},
                                                        {'anomalies': 'OMCI CRC error (corrupto en tránsito), Message '
                                                                      'Type desconocido (versión OMCI incompatible), '
                                                                      'Entity Instance duplicado, secuencia OMCI '
                                                                      'desalineada (OLT/ONT out of sync).',
                                                         'checks': 'Formato OMCI correcto. CRC-32 del payload OMCI '
                                                                   'válido. Sequence number alineado entre OLT y ONT. '
                                                                   "MIB sync state 'complete' en la OLT.",
                                                         'detail': 'OMCI Message (53 bytes): Transaction Correlation '
                                                                   'Identifier, Message Type (ej: Create=0x04), Device '
                                                                   'Identifier=0x0A (OMCI), Entity Class (ej: GEM '
                                                                   'Interworking TP=0x0101), Entity Instance, '
                                                                   'Attribute Mask, Attribute contents.',
                                                         'name': 'Capa 2 - OMCI sobre GEM',
                                                         'packet_capture': {'notes': 'OMCI no es capturable con '
                                                                                     'Wireshark estándar. Usar '
                                                                                     'herramientas del vendor.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'La OLT envía un mensaje OMCI Create (GEM Interworking TP) para '
                                                     'establecer el canal de gestión. OMCI típicamente usa GEM '
                                                     'Port=4095 en muchas implementaciones, o un GEM port dedicado '
                                                     'configurado en la OLT.',
                                             'step_title': 'Paso 3: Canal OMCI establecido (GEM port 4095 o dedicado)'},
                                            {'action': 'La OLT solicita la MIB del ONT y envía configuraciones de '
                                                       'creación/modificación',
                                             'device': 'OLT (Gestor OMCI)',
                                             'layers': [{'anomalies': 'Errores de HEC en OMCI GEM port '
                                                                      '(interferencia), buffer overflow en ONT '
                                                                      '(demasiados creates seguidos), OMCI timeout por '
                                                                      'T-CONT de gestión compartido con datos (sin '
                                                                      'prioridad).',
                                                         'checks': 'GEM Port de OMCI sin errores de HEC. Buffer de '
                                                                   'OMCI en ONT no desbordado. T-CONT de gestión con '
                                                                   'ancho de banda suficiente para la ráfaga de '
                                                                   'configuración.',
                                                         'detail': 'GEM Header: Port ID=4095 (OMCI). Alloc-ID/T-CONT '
                                                                   'de gestión activo. Frame GEM con prioridad alta en '
                                                                   'el BWmap.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM)',
                                                         'packet_capture': {'notes': 'Verificar contadores GEM/OMCI en '
                                                                                     'CLI del OLT.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}},
                                                        {'anomalies': 'ONT responde con Result=0x01 (Processing error) '
                                                                      'o 0x02 (Busy). ME Instance ya existe (Create '
                                                                      'duplicado), Attribute no soportado por el ONT, '
                                                                      'MIB Upload incompleto (faltan MEs en el ONT).',
                                                         'checks': 'Cada OMCI Create/Set recibe respuesta ACK/MKC (ej: '
                                                                   'Create Response=0x14). Los Entity Instance son '
                                                                   'únicos y consistentes. La OLT espera respuesta '
                                                                   'antes del siguiente request.',
                                                         'detail': 'OMCI Messages: MIB Upload (0x0A), Create (0x04), '
                                                                   'Set (0x08). MEs involucrados: T-CONT (0x0100), GEM '
                                                                   'Port Network CTP (0x0101), GEM Interworking TP '
                                                                   '(0x0102), MAC Bridge Service Profile (0x0105), MAC '
                                                                   'Bridge Port Config Data (0x0106), VLAN Tagging '
                                                                   'Filter Data (0x010B), etc.',
                                                         'name': 'Capa 2 - OMCI sobre GEM',
                                                         'packet_capture': {'notes': 'Usar OMCI debug/trace en CLI del '
                                                                                     'OLT.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'La OLT inicia con MIB Upload para leer la configuración actual '
                                                     'del ONT, luego envía una serie de OMCI Create/Set para '
                                                     'configurar bridges, VLANs, GEM ports de datos, y otros Managed '
                                                     'Entities (ME).',
                                             'step_title': 'Paso 4: OLT envía MIB uploads / create requests'},
                                            {'action': 'El ONT responde a las solicitudes OMCI con sus datos MIB y '
                                                       'confirma las configuraciones',
                                             'device': 'ONT (Agente OMCI)',
                                             'layers': [{'anomalies': 'Result Code=0x03 (Parameter error) - atributo '
                                                                      'fuera de rango. Result Code=0x04 (Unknown '
                                                                      'managed entity) - OLT intenta configurar una '
                                                                      'feature no soportada. OMCI response perdida '
                                                                      '(drop en GEM port), timeout repetido.',
                                                         'checks': 'Las respuestas OMCI llegan dentro del timeout '
                                                                   '(typ: 1s). CRC-32 válido. Result Code=0x00 '
                                                                   '(Command processed successfully) en todas las '
                                                                   'responses.',
                                                         'detail': 'OMCI Response Messages: MIB Upload Next Response '
                                                                   '(0x0C), Get Response (0x0C), Create Response '
                                                                   '(0x14). Contiene los atributos actuales del ONT: '
                                                                   'Serial Number, Hardware Version, Firmware Version, '
                                                                   'capacidades de bridge, VLANs soportadas, puertos '
                                                                   'ETH/FXS/POTS disponibles.',
                                                         'name': 'Capa 2 - OMCI sobre GEM',
                                                         'packet_capture': {'notes': 'Verificar OMCI response timeouts '
                                                                                     'y result codes en CLI OLT.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}},
                                                        {'anomalies': 'ONT no reporta DBRu para el T-CONT de gestión '
                                                                      '(la OLT no asigna ventanas upstream).',
                                                         'checks': 'ONT tiene T-CONT de gestión activo y reportado en '
                                                                   'DBRu. BWmap asigna ventanas para OMCI.',
                                                         'detail': 'GEM Header: Port ID=4095. Payload=OMCI response. '
                                                                   'T-CONT de gestión.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM)',
                                                         'packet_capture': {'notes': 'N/A',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'El ONT actúa como agente OMCI. Responde a los Get/MIB Upload '
                                                     'Next con los valores actuales de sus MEs y confirma los '
                                                     'Create/Set con responses.',
                                             'step_title': 'Paso 5: ONT responde con datos MIB'},
                                            {'action': 'La OLT envía las configuraciones finales de servicio al ONT '
                                                       'vía OMCI',
                                             'device': 'OLT ↔ ONT',
                                             'layers': [{'anomalies': 'VLAN mismatch (OMCI configura VLAN 100 pero el '
                                                                      'servicio usa 200), GEM Port de datos en '
                                                                      'conflicto con otro ONT (Provisioning error), '
                                                                      'T-CONT sin PIR suficiente (servicio degradado '
                                                                      'desde el inicio), Puertos POTS no configurados '
                                                                      '(VoIP no registra).',
                                                         'checks': 'Cada puerto ETH del ONT mapeado al GEM port de '
                                                                   'datos correcto. VLANs de servicio (Internet, IPTV, '
                                                                   'VoIP) configuradas en el tagging filter. T-CONT de '
                                                                   'datos con ancho de banda mínimo/garantizado '
                                                                   '(CIR/PIR) correcto.',
                                                         'detail': 'OMCI Set/Create final para: VLAN Tagging Filter '
                                                                   'Data (0x010B) - VLANs permitidas, MAC Bridge Port '
                                                                   'Config Data (0x0106) - asociación puerto-VLAN, '
                                                                   'PPTP Ethernet UNI (0x0104) - estado de puertos '
                                                                   'LAN, PPTP POTS UNI (0x0103) - configuración de '
                                                                   'puertos de voz, SIP User Data (0x00D5) / SIP '
                                                                   'Config Data (0x00D6) - parámetros VoIP si aplica.',
                                                         'name': 'Capa 2 - OMCI sobre GEM',
                                                         'packet_capture': {'notes': 'Usar CLI del OLT para verificar '
                                                                                     'configuración OMCI final.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}},
                                                        {'anomalies': 'GEM Port de datos creado pero no mapeado a la '
                                                                      'interfaz física (OMCI incomplete), conflicto de '
                                                                      'Alloc-ID entre ONTs (raro, indica provisioning '
                                                                      'duplicado).',
                                                         'checks': 'GEM connection de datos activo en ambos sentidos. '
                                                                   'OMCI MIB sync completo. ONT pasa a estado '
                                                                   'operativo (O5) con todos los servicios '
                                                                   'habilitados.',
                                                         'detail': 'GEM Port de datos (ej: 1024) creado y mapeado al '
                                                                   'T-CONT de datos (ej: 257). GEM Port de OMCI (4095) '
                                                                   'permanece activo para gestión continua.',
                                                         'name': 'Capa 2/1 - GPON Frame (GEM)',
                                                         'packet_capture': {'notes': 'N/A',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'Con la MIB sincronizada, la OLT configura los servicios '
                                                     'específicos: mapeo de GEM ports a puertos ETH, configuración de '
                                                     'VLAN tagging, activación de puertos POTS/FXS para VoIP, y QoS.',
                                             'step_title': 'Paso 6: Configuración de servicios aplicada (bridges, '
                                                           'VLANs, VoIP)'},
                                            {'action': 'El ONT completa el provisioning y entra en estado operativo '
                                                       'completo',
                                             'device': 'ONT / OLT',
                                             'layers': [{'anomalies': 'ONT vuelve a O1-O4 (pérdida de sincronización), '
                                                                      'errores BIP crónicos (fibra sucia o mala '
                                                                      'conexión), OMCI timeouts recurrentes (ONT '
                                                                      'colgado, necesita reboot remoto), derrame de '
                                                                      'tráfico entre GEM ports (security issue).',
                                                         'checks': 'ONT estado O5 (Operation) estable. Sin errores de '
                                                                   'HEC crónicos. Contadores de tráfico GEM '
                                                                   'incrementando. OMCI heartbeat/responses activos.',
                                                         'detail': 'PLOAM: Mensajes de mantenimiento periódicos (ej: '
                                                                   'Encryption Key Request/Response si AES está '
                                                                   'habilitado). GEM: Tráfico de datos en GEM port '
                                                                   'asignado + OMCI continuo en GEM port 4095.',
                                                         'name': 'Capa 2/1 - GPON Frame (PLOAM + GEM)',
                                                         'packet_capture': {'notes': 'Monitorear vía CLI: show gpon '
                                                                                     'onu state, show gpon onu '
                                                                                     'counters.',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}},
                                                        {'anomalies': 'OMCI channel caído (ONT no responde a pings de '
                                                                      'gestión), AVC notifications perdidas, firmware '
                                                                      'upgrade fallido (imagen corrupta, ONT en estado '
                                                                      'de recuperación).',
                                                         'checks': 'OMCI channel healthy: respuestas dentro de '
                                                                   'timeout, sin CRC errors. Alarm notifications '
                                                                   'llegan a la OLT cuando el ONT detecta eventos '
                                                                   '(LOS, LOF, etc.).',
                                                         'detail': 'OMCI continúa disponible para: Alarm reporting, '
                                                                   'Attribute value change (AVC) notifications, '
                                                                   'Software download (imagen firmware), Remote reset, '
                                                                   'Performance monitoring (PM) data collection.',
                                                         'name': 'Capa 2 - OMCI sobre GEM (Mantenimiento)',
                                                         'packet_capture': {'notes': 'N/A',
                                                                            'tcpdump_filter': 'No aplicable',
                                                                            'wireshark_display_filter': 'No '
                                                                                                        'aplicable'}}],
                                             'note': 'El ONT está listo para pasar tráfico de datos. La OLT muestra el '
                                                     "ONT en estado 'Online' o 'O5'. Los contadores OMCI se "
                                                     'estabilizan y el canal de gestión permanece abierto para futuros '
                                                     'cambios de configuración (SW upgrade, remote reset, etc.).',
                                             'step_title': 'Paso 7: ONT operativo'}]}]},
  'wireshark_tcpdump': {'scenarios': [{'description': 'Simulación de la captura de un paquete BGP UPDATE mediante tcpdump y análisis en Wireshark. Se muestra el three-way handshake TCP, el OPEN, KEEPALIVE, UPDATE, y los filtros BPF y display filters aplicables.',
                         'id': 'wireshark_tcpdump_bgp_capture',
                         'name': 'Wireshark/tcpdump: Captura y análisis de sesión BGP',
                         'steps': [{'action': 'Iniciar captura tcpdump en interfaz de red con filtro BPF para BGP (TCP port 179)',
                                    'device': 'Linux / Workstation de análisis',
                                    'layers': [{'anomalies': 'tcpdump no tiene permisos (sudo requerido), interfaz incorrecta (-i), filtro BPF mal escrito (syntax error), buffer de kernel insuficiente (-B), snaplen demasiado pequeño (-s).',
                                                'checks': 'tcpdump ejecutándose con privilegios root o capabilities CAP_NET_RAW. Interfaz correcta (-i). Filtro BPF sintácticamente válido.',
                                                'detail': 'tcpdump command: tcpdump -i <if> -nn -s0 -w bgp_capture.pcap "tcp port 179". Flags: -nn (no resolver DNS ni port names), -s0 (snaplen ilimitado, capturar todo el frame), -w (escribir a archivo), "tcp port 179" (filtro BPF).',
                                                'name': 'Capa 7 - Aplicación (tcpdump CLI)',
                                                'packet_capture': {'notes': 'Verificar que tcpdump no reporta dropped packets.',
                                                                   'tcpdump_filter': 'tcp port 179',
                                                                   'wireshark_display_filter': 'tcp.port == 179'}},
                                              {'anomalies': 'Promiscuous mode no soportado (virtual interface sin permisos), NIC filtra VLAN tags en hardware (strip).',
                                               'checks': 'Interfaz en promiscuo mode. Sin VLAN stripping por NIC.',
                                               'detail': 'Interfaz de red configurada en promiscuous mode para capturar todo el tráfico, no solo el dirigido a la MAC local.',
                                               'name': 'Capa 2 - Interfaz de red (NIC)',
                                               'packet_capture': {'notes': 'Verificar en tcpdump que se ven paquetes con MACs ajenas.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'eth'}}],
                                    'note': 'La captura debe iniciarse antes de que el router establezca la sesión BGP, para no perder el three-way handshake ni el OPEN.',
                                    'step_title': 'Paso 1: Iniciar tcpdump con filtro BPF "tcp port 179"'},
                                   {'action': 'Router inicia three-way handshake TCP hacia peer BGP (port 179)',
                                    'device': 'Router A / Peer BGP',
                                    'layers': [{'anomalies': 'TCP SYN no capturado (filtro BPF erróneo, snaplen insuficiente descartando payload), SYN/ACK perdido (asymmetric routing).',
                                                'checks': 'Captura muestra SYN, SYN-ACK, ACK consecutivos. Sequence numbers coherentes.',
                                                'detail': 'TCP SYN: SrcPort=efímero (>1024), DstPort=179, Seq=N, Ack=0, Flags=SYN. Window Scale, SACK permitted, MSS options presentes.',
                                                'name': 'Capa 4 - Transporte (TCP)',
                                                'packet_capture': {'notes': 'En Wireshark: Analyze → Follow → TCP Stream. Verificar handshake completo.',
                                                                   'tcpdump_filter': 'tcp port 179',
                                                                   'wireshark_display_filter': 'tcp.port == 179 && tcp.flags.syn == 1'}},
                                              {'anomalies': 'IP checksum erróneo (offloading de NIC), TTL insuficiente, fragmentación por MTU.',
                                               'checks': 'IP header válido. TTL > 1. Sin fragmentación.',
                                               'detail': 'IPv4: SrcIP=interfaz_A, DstIP=interfaz_B, Protocol=TCP(6), TTL=64, TOS=0xC0 (Internetwork Control). IP checksum validado por hardware.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'Verificar TOS/DSCP en Wireshark.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'tcp.port == 179'}},
                                              {'anomalies': 'MAC broadcast/multicast inesperada, VLAN tag stripping en captura.',
                                               'checks': 'MAC destino = MAC del next-hop o peer directo. EtherType=0x0800.',
                                               'detail': 'Ethernet II: DstMAC=next_hop_MAC, SrcMAC=router_A_MAC, EtherType=0x0800 (IPv4). Posible 802.1Q tag si subinterfaces.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'Verificar MACs y posible VLAN tag.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && tcp.port == 179'}}],
                                    'note': 'El three-way handshake debe aparecer completo en la captura. Si falta algún paquete, verificar filtros BPF y snaplen.',
                                    'step_title': 'Paso 2: Three-way handshake TCP (SYN, SYN-ACK, ACK)'},
                                   {'action': 'Router envía BGP OPEN inmediatamente tras el handshake',
                                    'device': 'Router A',
                                    'layers': [{'anomalies': 'OPEN no capturado (filtro BPF activo después del handshake), OPEN mal formado (Marker no 0xFF, Length < 29).',
                                                'checks': 'OPEN presente tras ACK final del handshake. Type=1. Version=4. AS correcto. Hold Time ≥ 3s.',
                                                'detail': 'BGP OPEN: Marker=16 bytes 0xFF, Length=29+, Type=1 (OPEN), Version=4, My AS=64512, Hold Time=180s, BGP Identifier=Router ID, Optional Parameters (Capabilities: MP-BGP, Route Refresh, 4-octet AS).',
                                                'name': 'Capa 7/5 - BGP OPEN',
                                                'packet_capture': {'notes': 'En Wireshark expandir BGP → OPEN. Verificar AS, Hold Time, Capabilities.',
                                                                   'tcpdump_filter': 'tcp port 179',
                                                                   'wireshark_display_filter': 'bgp.type == 1'}},
                                              {'anomalies': 'TCP PSH/ACK no presente (segmento retransmitido), zero-window.',
                                               'checks': 'TCP PSH=1, ACK=1. Window no cero.',
                                               'detail': 'TCP: SrcPort=efímero/179, DstPort=179/efímero, PSH=1, ACK=1, Seq/Ack correctos.',
                                               'name': 'Capa 4 - Transporte (TCP)',
                                               'packet_capture': {'notes': 'Verificar que OPEN viaja en un segmento TCP PSH.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'tcp.port == 179 && tcp.flags.psh == 1'}},
                                              {'anomalies': 'IP checksum erróneo, TTL expirado.',
                                               'checks': 'IP válido. TTL consistente.',
                                               'detail': 'IPv4: SrcIP/DstIP fijos, Protocol=TCP, TTL=64.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'tcp.port == 179'}},
                                              {'anomalies': 'L2 errors.',
                                               'checks': 'L2 estable.',
                                               'detail': 'Ethernet: DstMAC/SrcMAC correspondientes.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && tcp.port == 179'}}],
                                    'note': 'El OPEN es el primer mensaje BGP. Si no aparece, verificar que el filtro BPF no descarta tráfico posterior al handshake (ej: filtro por host IP en lugar de port).',
                                    'step_title': 'Paso 3: BGP OPEN (Type=1)'},
                                   {'action': 'KEEPALIVE periódicos y UPDATE de ruta capturados',
                                    'device': 'Router A y Router B',
                                    'layers': [{'anomalies': 'KEEPALIVE ausente (Hold Timer expira, sesión cae), UPDATE mal formado (malformed attribute), NOTIFICATION de teardown.',
                                                'checks': 'KEEPALIVE cada 1/3 del Hold Time (default 60s si Hold=180s). UPDATE con atributos well-known. Sin NOTIFICATIONs.',
                                                'detail': 'BGP KEEPALIVE: Type=4, Length=19. BGP UPDATE: Type=2, Path Attributes (ORIGIN, AS_PATH, NEXT_HOP, MED, COMMUNITY), NLRI (prefix/length).',
                                                'name': 'Capa 7/5 - BGP KEEPALIVE / UPDATE',
                                                'packet_capture': {'notes': 'Wireshark: Statistics → BGP → Messages. Verificar contadores de UPDATE/KEEPALIVE.',
                                                                   'tcpdump_filter': 'tcp port 179',
                                                                   'wireshark_display_filter': 'bgp.type == 4 || bgp.type == 2'}},
                                              {'anomalies': 'TCP retransmisiones masivas (path congestionado), window scale no negociado (throughput bajo).',
                                               'checks': 'Sin retransmisiones innecesarias. TCP window suficiente para UPDATEs grandes.',
                                               'detail': 'TCP ACKs periódicos. Sin duplicados de SEQ.',
                                               'name': 'Capa 4 - Transporte (TCP)',
                                               'packet_capture': {'notes': 'Wireshark: Analyze → Expert Info. Buscar retransmisiones.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'tcp.port == 179 && tcp.analysis.retransmission'}},
                                              {'anomalies': 'IP checksum erróneo, fragmentación de UPDATE grande (MTU path insuficiente).',
                                               'checks': 'IP válido. Sin fragmentación (DF bit set en BGP peers modernos).',
                                               'detail': 'IPv4: DF bit puede estar set. MTU ≥ 1500.',
                                               'name': 'Capa 3 - Red (IPv4)',
                                               'packet_capture': {'notes': 'Verificar flags DF y MF.',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'tcp.port == 179 && ip.flags.df == 1'}},
                                              {'anomalies': 'L2 errors, MAC flapping.',
                                               'checks': 'L2 estable.',
                                               'detail': 'Ethernet consistente.',
                                               'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                               'packet_capture': {'notes': 'N/A',
                                                                  'tcpdump_filter': 'tcp port 179',
                                                                  'wireshark_display_filter': 'eth.type == 0x0800 && tcp.port == 179'}}],
                                    'note': 'En Wireshark, usar el display filter `bgp` para ver todos los mensajes BGP. Usar `bgp.type == 2` para aislar UPDATEs.',
                                    'step_title': 'Paso 4: KEEPALIVE y UPDATE en sesión Established'},
                                   {'action': 'Análisis post-captura con Wireshark: display filters y estadísticas',
                                    'device': 'Workstation de análisis',
                                    'layers': [{'anomalies': 'Wireshark no decodifica BGP (dissector deshabilitado), template de MPLS no cargado, NLRI EVPN no reconocido.',
                                                'checks': 'Dissectors habilitados: BGP, MPLS, OSPF, L2VPN/EVPN. Preferencias → Protocols → BGP.',
                                                'detail': 'Wireshark display filters: `bgp`, `bgp.type == 1` (OPEN), `bgp.type == 2` (UPDATE), `bgp.type == 3` (NOTIFICATION), `bgp.type == 4` (KEEPALIVE), `tcp.port == 179`, `ip.addr == <peer>`. Statistics → Protocol Hierarchy para ver distribución de protocolos.',
                                                'name': 'Capa 7 - Aplicación (Wireshark GUI)',
                                                'packet_capture': {'notes': 'Verificar que Wireshark decodifique correctamente los Path Attributes y NLRI.',
                                                                   'tcpdump_filter': 'tcp port 179',
                                                                   'wireshark_display_filter': 'bgp'}},
                                              {'anomalies': 'tshark no genera reporte (plantilla de campo incorrecto), archivo corrupto (truncado por tcpdump -c).',
                                               'checks': 'tshark -r bgp_capture.pcap -q -z conv,tcp muestra conversación completa.',
                                               'detail': 'tshark CLI: tshark -r bgp_capture.pcap -Y "bgp.type == 2" -T fields -e bgp.update.path_attributes.as_path. Exportar a JSON/CSV si es necesario.',
                                               'name': 'Capa 7 - Aplicación (tshark CLI)',
                                               'packet_capture': {'notes': 'Usar tshark para extraer campos específicos sin abrir GUI.',
                                                                  'tcpdump_filter': 'tshark -r bgp_capture.pcap',
                                                                  'wireshark_display_filter': 'tshark -r bgp_capture.pcap -Y bgp'}}],
                                    'note': 'El análisis post-captura permite correlacionar los mensajes BGP con los eventos de routing observados en los logs del router.',
                                    'step_title': 'Paso 5: Análisis post-captura con Wireshark / tshark'}]},
                     {
                         'id': 'wireshark_tcpdump_linux_nat_trace',
                         'name': 'Wireshark/tcpdump: Diagnóstico y Trazado de NAT en Linux',
                         'name_en': 'Wireshark/tcpdump: Linux NAT Diagnosis and Tracing',
                         'description': 'Simulación paso a paso del trazado de un paquete HTTP (L1-L7) cruzando un gateway Linux que realiza MASQUERADE (NAT de origen). Se detalla el uso de tcpdump para capturar en LAN/WAN, iptables TRACE para auditar las reglas de netfilter en el kernel, y filtros de Wireshark para analizar el flujo.',
                         'description_en': 'Step-by-step simulation of tracing an HTTP packet (L1-L7) crossing a Linux gateway performing MASQUERADE (source NAT). Details the use of tcpdump to capture on LAN/WAN, iptables TRACE to audit netfilter rules in the kernel, and Wireshark filters to analyze the flow.',
                         'steps': [
                             {
                                 'step_title': 'Paso 1: Verificación de capa física (L1) e inicio de captura tcpdump en LAN',
                                 'step_title_en': 'Step 1: Physical layer (L1) verification and start of tcpdump capture on LAN',
                                 'device': 'Router Linux (Interfaz LAN: eth1)',
                                 'device_en': 'Linux Router (LAN Interface: eth1)',
                                 'action': 'El administrador de red verifica que la interfaz física eth1 está activa y arranca tcpdump para escuchar el tráfico proveniente de la red interna.',
                                 'action_en': 'The network administrator verifies that physical interface eth1 is active and runs tcpdump to listen for traffic coming from the internal network.',
                                 'note': 'Se utiliza ethtool para validar el enlace L1. Se inicia tcpdump en background capturando hacia un archivo pcap.',
                                 'note_en': 'ethtool is used to validate the L1 link. tcpdump is started in the background capturing to a pcap file.',
                                 'layers': [
                                     {
                                         'name': 'Capa 1 - Física',
                                         'name_en': 'Layer 1 - Physical',
                                         'detail': 'Interfaz eth1, Link detected: yes, Speed: 1000Mb/s, Duplex: Full. Verificación con: ethtool eth1.',
                                         'detail_en': 'Interface eth1, Link detected: yes, Speed: 1000Mb/s, Duplex: Full. Verification command: ethtool eth1.',
                                         'checks': 'Validar estado físico del cable, potencia óptica o ethernet auto-negotiation.',
                                         'checks_en': 'Validate physical cable status, optical power or ethernet auto-negotiation.',
                                         'anomalies': 'Link detected: no (cable desconectado o puerto apagado), speed/duplex mismatch.',
                                         'anomalies_en': 'Link detected: no (disconnected cable or port down), speed/duplex mismatch.',
                                         'packet_capture': {
                                             'notes': 'La capa 1 no es capturable directamente por tcpdump. Usar ethtool o dmesg.',
                                             'notes_en': 'Layer 1 is not directly capturable by tcpdump. Use ethtool or dmesg.',
                                             'tcpdump_filter': 'No aplicable',
                                             'wireshark_display_filter': 'No aplicable'
                                         }
                                     },
                                     {
                                         'name': 'Capa 2 - Enlace de Datos (Ethernet/ARP)',
                                         'name_en': 'Layer 2 - Data Link (Ethernet/ARP)',
                                         'detail': 'Trama Ethernet ingresando por eth1. MAC origen = MAC del cliente (52:54:00:11:22:33), MAC destino = MAC de eth1 del Router (52:54:00:aa:bb:cc), EtherType = 0x0800 (IPv4).',
                                         'detail_en': 'Ethernet frame entering via eth1. Source MAC = client MAC (52:54:00:11:22:33), Destination MAC = Router eth1 MAC (52:54:00:aa:bb:cc), EtherType = 0x0800 (IPv4).',
                                         'checks': 'Verificar tabla ARP en el cliente y router con ip neigh show.',
                                         'checks_en': 'Verify ARP table on client and router with ip neigh show.',
                                         'anomalies': 'ARP Request sin respuesta (IP del router duplicada o no configurada), MAC flapping.',
                                         'anomalies_en': 'ARP Request with no response (router IP duplicate or not configured), MAC flapping.',
                                         'packet_capture': {
                                             'notes': 'Comando de captura: tcpdump -i eth1 -nn -s0 -w /tmp/lan_nat.pcap arp or tcp port 80',
                                             'notes_en': 'Capture command: tcpdump -i eth1 -nn -s0 -w /tmp/lan_nat.pcap arp or tcp port 80',
                                             'tcpdump_filter': 'arp or port 80',
                                             'wireshark_display_filter': 'arp || tcp.port == 80'
                                         }
                                     }
                                 ]
                             },
                             {
                                 'step_title': 'Paso 2: Inspección de Capas L3-L4 del paquete entrante (LAN)',
                                 'step_title_en': 'Step 2: L3-L4 inspection of the incoming packet (LAN)',
                                 'device': 'Router Linux (eth1)',
                                 'device_en': 'Linux Router (eth1)',
                                 'action': 'El router recibe el paquete IP y tcpdump captura las cabeceras de red (L3) y transporte (L4) antes de cualquier procesamiento de NAT.',
                                 'action_en': 'The router receives the IP packet and tcpdump captures the network (L3) and transport (L4) headers before any NAT processing.',
                                 'note': 'El paquete tiene IP origen privada (192.168.1.10) e IP destino pública (8.8.8.8). El puerto de destino es TCP 80 (HTTP).',
                                 'note_en': 'The packet has a private source IP (192.168.1.10) and a public destination IP (8.8.8.8). The destination port is TCP 80 (HTTP).',
                                 'layers': [
                                     {
                                         'name': 'Capa 3 - Red (IPv4)',
                                         'name_en': 'Layer 3 - Network (IPv4)',
                                         'detail': 'IP Origen = 192.168.1.10, IP Destino = 8.8.8.8, Protocolo = TCP (6), TTL = 64. Verificación en tabla de rutas con: ip route get 8.8.8.8.',
                                         'detail_en': 'Source IP = 192.168.1.10, Destination IP = 8.8.8.8, Protocol = TCP (6), TTL = 64. Route verification: ip route get 8.8.8.8.',
                                         'checks': 'Validar que el router tiene ruta para 8.8.8.8 y que el reenvío de paquetes está habilitado (sysctl net.ipv4.ip_forward).',
                                         'checks_en': 'Validate that the router has a route for 8.8.8.8 and that packet forwarding is enabled (sysctl net.ipv4.ip_forward).',
                                         'anomalies': 'IP forward deshabilitado (sysctl net.ipv4.ip_forward=0), descarte por falta de ruta por defecto.',
                                         'anomalies_en': 'IP forward disabled (sysctl net.ipv4.ip_forward=0), discard due to lack of default route.',
                                         'packet_capture': {
                                             'notes': 'Filtrar por IP origen privada en la captura.',
                                             'notes_en': 'Filter by private source IP in the capture.',
                                             'tcpdump_filter': 'ip src 192.168.1.10',
                                             'wireshark_display_filter': 'ip.src == 192.168.1.10'
                                         }
                                     },
                                     {
                                         'name': 'Capa 4 - Transporte (TCP)',
                                         'name_en': 'Layer 4 - Transport (TCP)',
                                         'detail': 'Puerto Origen = 45231 (efímero), Puerto Destino = 80, Seq = 0, Flags = [SYN], Window = 64240.',
                                         'detail_en': 'Source Port = 45231 (ephemeral), Destination Port = 80, Seq = 0, Flags = [SYN], Window = 64240.',
                                         'checks': 'Verificar que los flags TCP sean los correctos para el inicio de conexión (SYN).',
                                         'checks_en': 'Verify that TCP flags are correct for connection initiation (SYN).',
                                         'anomalies': 'Retransmisiones constantes de SYN en LAN sin respuesta (problema de routing de retorno o firewall en el router).',
                                         'anomalies_en': 'Constant SYN retransmissions on LAN with no response (return routing problem or firewall on the router).',
                                         'packet_capture': {
                                             'notes': 'Filtrar por puerto de destino HTTP.',
                                             'notes_en': 'Filter by HTTP destination port.',
                                             'tcpdump_filter': 'tcp port 80',
                                             'wireshark_display_filter': 'tcp.port == 80'
                                         }
                                     }
                                 ]
                             },
                             {
                                 'step_title': 'Paso 3: Trazado de Netfilter/iptables en el kernel de Linux',
                                 'step_title_en': 'Step 3: Netfilter/iptables tracing in the Linux kernel',
                                 'device': 'Kernel Linux (Subsistema Netfilter)',
                                 'device_en': 'Linux Kernel (Netfilter Subsystem)',
                                 'action': 'El paquete IP entra al subsistema de enrutamiento y NAT de Netfilter. El administrador audita el recorrido de la regla usando iptables TRACE.',
                                 'action_en': 'The IP packet enters Netfilter\'s routing and NAT subsystem. The administrator audits the rule path using iptables TRACE.',
                                 'note': 'La traza de iptables muestra cómo el paquete pasa por raw:PREROUTING, nat:PREROUTING (sin cambios de DNAT), filter:FORWARD (permitido), y finalmente nat:POSTROUTING donde se aplica MASQUERADE cambiando la IP origen por la IP pública del router.',
                                 'note_en': 'The iptables trace shows how the packet goes through raw:PREROUTING, nat:PREROUTING (no DNAT changes), filter:FORWARD (allowed), and finally nat:POSTROUTING where MASQUERADE is applied changing the source IP to the router\'s public IP.',
                                 'layers': [
                                     {
                                         'name': 'Capa 3 - Netfilter / Connection Tracking (conntrack)',
                                         'name_en': 'Layer 3 - Netfilter / Connection Tracking (conntrack)',
                                         'detail': 'Se crea una nueva sesión conntrack en estado [NEW]. iptables TRACE loggea en dmesg: "TRACE: nat:POSTROUTING:rule:1 IN= OUT=eth0 SRC=203.0.113.1 DST=8.8.8.8". La IP de origen se traduce de 192.168.1.10 a 203.0.113.1.',
                                         'detail_en': 'A new conntrack session is created in [NEW] state. iptables TRACE logs in dmesg: "TRACE: nat:POSTROUTING:rule:1 IN= OUT=eth0 SRC=203.0.113.1 DST=8.8.8.8". The source IP is translated from 192.168.1.10 to 203.0.113.1.',
                                         'checks': 'Consultar la tabla conntrack activa usando conntrack -L | grep 192.168.1.10. Comprobar logs en dmesg | grep TRACE.',
                                         'checks_en': 'Query the active conntrack table using conntrack -L | grep 192.168.1.10. Check logs in dmesg | grep TRACE.',
                                         'anomalies': 'Paquete dropeado por política de firewall en filter:FORWARD, fallo de MASQUERADE (regla inexistente en tabla nat, POSTROUTING).',
                                         'anomalies_en': 'Packet dropped by firewall policy in filter:FORWARD, MASQUERADE failure (non-existent rule in nat table, POSTROUTING).',
                                         'packet_capture': {
                                             'notes': 'Este paso ocurre internamente en el kernel. Los logs en dmesg confirman la traslación.',
                                             'notes_en': 'This step occurs internally in the kernel. Logs in dmesg confirm the translation.',
                                             'tcpdump_filter': 'No aplicable',
                                             'wireshark_display_filter': 'No aplicable'
                                         }
                                     }
                                 ]
                             },
                             {
                                 'step_title': 'Paso 4: Captura tcpdump en WAN (eth0) después de NAT',
                                 'step_title_en': 'Step 4: tcpdump capture on WAN (eth0) after NAT',
                                 'device': 'Router Linux (Interfaz WAN: eth0)',
                                 'device_en': 'Linux Router (WAN Interface: eth0)',
                                 'action': 'El paquete traducido se envía por la interfaz WAN eth0 hacia Internet. tcpdump captura la trama de salida.',
                                 'action_en': 'The translated packet is sent via WAN interface eth0 towards the Internet. tcpdump captures the outbound frame.',
                                 'note': 'El paquete muestra ahora la IP origen modificada (203.0.113.1), mientras que el puerto de destino y la IP de destino se mantienen intactos.',
                                 'note_en': 'The packet now shows the modified source IP (203.0.113.1), while the destination port and destination IP remain intact.',
                                 'layers': [
                                     {
                                         'name': 'Capa 3 - Red (IPv4)',
                                         'name_en': 'Layer 3 - Network (IPv4)',
                                         'detail': 'IP Origen = 203.0.113.1 (IP pública del router), IP Destino = 8.8.8.8, Protocolo = TCP, TTL = 63 (decrementado en 1 por ruteo).',
                                         'detail_en': 'Source IP = 203.0.113.1 (router\'s public IP), Destination IP = 8.8.8.8, Protocol = TCP, TTL = 63 (decremented by 1 due to routing).',
                                         'checks': 'Confirmar que la IP origen corresponde a la asignada en eth0 (ip addr show eth0).',
                                         'checks_en': 'Confirm that the source IP corresponds to the one assigned on eth0 (ip addr show eth0).',
                                         'anomalies': 'IP origen sigue siendo privada en la WAN (fallo crítico de NAT), MTU path issue requiriendo MSS Clamping.',
                                         'anomalies_en': 'Source IP is still private on the WAN (critical NAT failure), MTU path issue requiring MSS Clamping.',
                                         'packet_capture': {
                                             'notes': 'Comando de captura: tcpdump -i eth0 -nn -s0 -w /tmp/wan_nat.pcap host 8.8.8.8',
                                             'notes_en': 'Capture command: tcpdump -i eth0 -nn -s0 -w /tmp/wan_nat.pcap host 8.8.8.8',
                                             'tcpdump_filter': 'ip src 203.0.113.1 and ip dst 8.8.8.8',
                                             'wireshark_display_filter': 'ip.src == 203.0.113.1 && ip.dst == 8.8.8.8'
                                         }
                                     },
                                     {
                                         'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                         'name_en': 'Layer 2 - Data Link (Ethernet)',
                                         'detail': 'SrcMAC = MAC de eth0 del Router (52:54:00:cc:dd:ee), DstMAC = MAC del gateway de la WAN (52:54:00:ff:11:22).',
                                         'detail_en': 'SrcMAC = Router eth0 MAC (52:54:00:cc:dd:ee), DstMAC = WAN gateway MAC (52:54:00:ff:11:22).',
                                         'checks': 'Validar ARP del gateway WAN con ip neigh show dev eth0.',
                                         'checks_en': 'Validate WAN gateway ARP with ip neigh show dev eth0.',
                                         'anomalies': 'Gateway WAN inalcanzable por ARP.',
                                         'anomalies_en': 'WAN gateway unreachable by ARP.',
                                         'packet_capture': {
                                             'notes': 'Verificar cambio de direccionamiento MAC de salida.',
                                             'notes_en': 'Verify outbound MAC address change.',
                                             'tcpdump_filter': 'ether src 52:54:00:cc:dd:ee',
                                             'wireshark_display_filter': 'eth.src == 52:54:00:cc:dd:ee'
                                         }
                                     }
                                 ]
                             },
                             {
                                 'step_title': 'Paso 5: Análisis en Wireshark/tshark del flujo completo L7',
                                 'step_title_en': 'Step 5: Wireshark/tshark analysis of the complete L7 flow',
                                 'device': 'Estación de Trabajo / Wireshark',
                                 'device_en': 'Workstation / Wireshark',
                                 'action': 'El administrador de red abre las capturas en Wireshark o utiliza tshark en la consola para analizar el flujo HTTP capa 7.',
                                 'action_en': 'The network administrator opens the captures in Wireshark or uses tshark in the console to analyze the Layer 7 HTTP flow.',
                                 'note': 'Se utiliza follow tcp stream para decodificar las peticiones HTTP GET y respuestas 200 OK correspondientes, validando que el NAT no corrompió los datos.',
                                 'note_en': 'follow tcp stream is used to decode the HTTP GET requests and corresponding 200 OK responses, validating that NAT did not corrupt the data.',
                                 'layers': [
                                     {
                                         'name': 'Capa 7 - Aplicación (HTTP)',
                                         'name_en': 'Layer 7 - Application (HTTP)',
                                         'detail': 'Petición: GET /api/status HTTP/1.1\\r\\nHost: api.example.com. Respuesta: HTTP/1.1 200 OK\\r\\nContent-Type: application/json.',
                                         'detail_en': 'Request: GET /api/status HTTP/1.1\\r\\nHost: api.example.com. Response: HTTP/1.1 200 OK\\r\\nContent-Type: application/json.',
                                         'checks': 'Usar display filter http en Wireshark. Seguir stream TCP con tshark -r /tmp/lan_nat.pcap -q -z follow,tcp,ascii,0.',
                                         'checks_en': 'Use display filter http in Wireshark. Follow TCP stream with tshark -r /tmp/lan_nat.pcap -q -z follow,tcp,ascii,0.',
                                         'anomalies': 'Pérdida de paquetes en L7, respuestas HTTP 504 Gateway Timeout (servidor destino apagado pero NAT funcionando).',
                                         'anomalies_en': 'Packet loss at L7, HTTP 504 Gateway Timeout responses (destination server down but NAT working).',
                                         'packet_capture': {
                                             'notes': 'Análisis final del payload L7 decodificado.',
                                             'notes_en': 'Final analysis of the decoded L7 payload.',
                                             'tcpdump_filter': 'tcp port 80',
                                             'wireshark_display_filter': 'http'
                                         }
                                     }
                                 ]
                             }
                         ]
                     }
                     ]},
    'nat': {
        'scenarios': [
            {
                'id': 'source_nat_pat_outbound',
                'name': 'Source NAT (PAT): Navegación Cliente a Internet',
                'name_en': 'Source NAT (PAT): Client Internet Browsing',
                'description': 'Simulación de flujo de paquete cruzando un gateway con Source NAT (PAT) hacia un servidor público en Internet.',
                'description_en': 'Simulation of a packet flow crossing a gateway with Source NAT (PAT) to a public server on the Internet.',
                'steps': [
                    {
                        'step_title': 'Paso 1: PC-Cliente genera petición TCP SYN',
                        'step_title_en': 'Step 1: PC-Client generates TCP SYN request',
                        'device': 'PC-Cliente (IP: 192.168.1.50)',
                        'device_en': 'PC-Client (IP: 192.168.1.50)',
                        'action': 'El host interno inicia la conexión HTTP enviando un paquete TCP SYN al gateway.',
                        'action_en': 'The internal host initiates the HTTP connection by sending a TCP SYN packet to the gateway.',
                        'note': 'El cliente usa su IP privada y un puerto efímero. La trama Ethernet se dirige a la MAC del default gateway.',
                        'note_en': 'The client uses its private IP and an ephemeral port. The Ethernet frame is directed to the default gateway MAC.',
                        'layers': [
                            {
                                'name': 'Capa 3 - Red (IPv4)',
                                'name_en': 'Layer 3 - Network (IPv4)',
                                'detail': 'SrcIP=192.168.1.50, DstIP=8.8.8.8, TTL=128, Protocol=TCP',
                                'detail_en': 'SrcIP=192.168.1.50, DstIP=8.8.8.8, TTL=128, Protocol=TCP',
                                'anomalies': 'IP destino inalcanzable, falta de ruta local en PC.',
                                'anomalies_en': 'Destination IP unreachable, lack of local route on PC.',
                                'checks': 'Gateway IP configurado en PC, tabla de rutas local.',
                                'checks_en': 'Gateway IP configured on PC, local routing table.',
                                'packet_capture': {
                                    'notes': 'Verificar cabecera IP origen y destino.',
                                    'notes_en': 'Verify source and destination IP headers.',
                                    'tcpdump_filter': 'ip src 192.168.1.50 and ip dst 8.8.8.8',
                                    'wireshark_display_filter': 'ip.src == 192.168.1.50 && ip.dst == 8.8.8.8'
                                }
                            },
                            {
                                'name': 'Capa 4 - Transporte (TCP)',
                                'name_en': 'Layer 4 - Transport (TCP)',
                                'detail': 'SrcPort=52130, DstPort=80, Flags=SYN, Seq=0',
                                'detail_en': 'SrcPort=52130, DstPort=80, Flags=SYN, Seq=0',
                                'anomalies': 'Puerto bloqueado por firewall local o puerto origen ya en uso.',
                                'anomalies_en': 'Port blocked by local firewall or source port already in use.',
                                'checks': 'Sockets activos en el sistema operativo.',
                                'checks_en': 'Active sockets in the operating system.',
                                'packet_capture': {
                                    'notes': 'Verificar puerto origen TCP y flag SYN.',
                                    'notes_en': 'Verify TCP source port and SYN flag.',
                                    'tcpdump_filter': 'tcp port 80',
                                    'wireshark_display_filter': 'tcp.port == 80'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 2: Gateway realiza lookup de ruta y política de seguridad',
                        'step_title_en': 'Step 2: Gateway performs route lookup and security policy check',
                        'device': 'Gateway / Firewall (puerto interno: port2)',
                        'device_en': 'Gateway / Firewall (internal port: port2)',
                        'action': 'El gateway recibe el paquete, consulta su tabla de rutas y evalúa la política de seguridad.',
                        'action_en': 'The gateway receives the packet, queries its routing table, and evaluates the security policy.',
                        'note': 'El gateway confirma que la ruta de destino es por la WAN (port1) y que la política LAN->WAN permite el tráfico.',
                        'note_en': 'The gateway confirms that the destination route is via WAN (port1) and that the LAN to WAN policy allows the traffic.',
                        'layers': [
                            {
                                'name': 'Capa 3 - Red (Routing/FIB)',
                                'name_en': 'Layer 3 - Network (Routing/FIB)',
                                'detail': 'Búsqueda en FIB de 8.8.8.8. Ruta: 0.0.0.0/0 vía 203.0.113.1 (ISP) en interfaz port1.',
                                'detail_en': 'FIB lookup for 8.8.8.8. Route: 0.0.0.0/0 via 203.0.113.1 (ISP) on interface port1.',
                                'anomalies': 'Falta de ruta por defecto en el gateway (paquete descartado).',
                                'anomalies_en': 'Missing default route on the gateway (packet discarded).',
                                'checks': 'Comprobar tabla de enrutamiento estático/dinámico en el gateway.',
                                'checks_en': 'Check static/dynamic routing table on the gateway.',
                                'packet_capture': {
                                    'notes': 'Verificar llegada del paquete a la interfaz port2.',
                                    'notes_en': 'Verify packet arrival on interface port2.',
                                    'tcpdump_filter': 'i port2 tcp port 80',
                                    'wireshark_display_filter': 'tcp.port == 80'
                                }
                            },
                            {
                                'name': 'Capa 4 - Inspección de Sesión',
                                'name_en': 'Layer 4 - Session Inspection',
                                'detail': 'Match con política LAN_to_WAN (ID: 5) con acción ACCEPT. Se crea una sesión NAT incompleta.',
                                'detail_en': 'Match with policy LAN_to_WAN (ID: 5) with ACCEPT action. An incomplete NAT session is created.',
                                'anomalies': 'Denegado por ACL/Política (implicit deny o drop en política).',
                                'anomalies_en': 'Denied by ACL/Policy (implicit deny or drop in policy).',
                                'checks': 'Revisar logs de tráfico y hit count de las políticas.',
                                'checks_en': 'Review traffic logs and policy hit counts.',
                                'packet_capture': {
                                    'notes': 'Logs de depuración del firewall para políticas de seguridad.',
                                    'notes_en': 'Firewall debug logs for security policies.',
                                    'tcpdump_filter': 'No aplicable',
                                    'wireshark_display_filter': 'No aplicable'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 3: Gateway traduce IP/Puerto Origen (PAT) y reenvía por WAN',
                        'step_title_en': 'Step 3: Gateway translates Source IP/Port (PAT) and forwards via WAN',
                        'device': 'Gateway / Firewall (puerto externo: port1)',
                        'device_en': 'Gateway / Firewall (external port: port1)',
                        'action': 'El gateway aplica la traducción Source NAT / PAT y transmite por la WAN.',
                        'action_en': 'The gateway applies Source NAT / PAT translation and transmits over the WAN.',
                        'note': 'El origen 192.168.1.50 se traduce a 203.0.113.10. El puerto 52130 se traduce a 10245 para evitar colisiones. Se crea la entrada final de sesión.',
                        'note_en': 'Source 192.168.1.50 translates to 203.0.113.10. Port 52130 translates to 10245 to avoid collisions. The final session entry is created.',
                        'layers': [
                            {
                                'name': 'Capa 3 - Traducción IP (Source NAT)',
                                'name_en': 'Layer 3 - IP Translation (Source NAT)',
                                'detail': 'IP Origen original: 192.168.1.50 -> Traducida: 203.0.113.10. Checksum IP recalculado.',
                                'detail_en': 'Original Source IP: 192.168.1.50 -> Translated: 203.0.113.10. IP checksum recalculated.',
                                'anomalies': 'Agotamiento del pool de IPs de NAT o IP de interfaz WAN incorrecta.',
                                'anomalies_en': 'NAT IP pool exhaustion or incorrect WAN interface IP.',
                                'checks': 'Verificar tamaño del pool de NAT y estadísticas de uso del pool.',
                                'checks_en': 'Verify NAT pool size and usage statistics.',
                                'packet_capture': {
                                    'notes': 'Verificar el paquete saliente en la interfaz WAN con la IP traducida.',
                                    'notes_en': 'Verify the outbound packet on the WAN interface with the translated IP.',
                                    'tcpdump_filter': 'i port1 host 203.0.113.10 and tcp port 80',
                                    'wireshark_display_filter': 'ip.addr == 203.0.113.10 && tcp.port == 80'
                                }
                            },
                            {
                                'name': 'Capa 4 - Traducción de Puerto (PAT)',
                                'name_en': 'Layer 4 - Port Translation (PAT)',
                                'detail': 'Puerto Origen original: 52130 -> Traducido: 10245 (o retenido si no hay colisión). Checksum TCP recalculado.',
                                'detail_en': 'Original Source Port: 52130 -> Translated: 10245 (or kept if no collision). TCP checksum recalculated.',
                                'anomalies': 'Agotamiento de puertos efímeros en la IP pública (port exhaustion).',
                                'anomalies_en': 'Ephemeral port exhaustion on the public IP (port exhaustion).',
                                'checks': 'Verificar tabla de traducción NAT activa (`show system session` / `diagnose sys session list`).',
                                'checks_en': 'Verify active NAT translation table (`show system session` / `diagnose sys session list`).',
                                'packet_capture': {
                                    'notes': 'Verificar el puerto de origen traducido.',
                                    'notes_en': 'Verify the translated source port.',
                                    'tcpdump_filter': 'i port1 tcp port 80',
                                    'wireshark_display_filter': 'tcp.srcport == 10245'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 4: Servidor recibe petición y responde con TCP SYN-ACK',
                        'step_title_en': 'Step 4: Server receives request and responds with TCP SYN-ACK',
                        'device': 'Servidor Web Público (IP: 8.8.8.8)',
                        'device_en': 'Public Web Server (IP: 8.8.8.8)',
                        'action': 'El servidor procesa la petición y responde enviando un paquete SYN-ACK hacia la IP pública del gateway.',
                        'action_en': 'The server processes the request and responds by sending a SYN-ACK packet to the public IP of the gateway.',
                        'note': 'El servidor web ve la IP pública 203.0.113.10 y el puerto 10245 como origen del tráfico.',
                        'note_en': 'The web server sees public IP 203.0.113.10 and port 10245 as the source of traffic.',
                        'layers': [
                            {
                                'name': 'Capa 3 - Red (IPv4)',
                                'name_en': 'Layer 3 - Network (IPv4)',
                                'detail': 'SrcIP=8.8.8.8, DstIP=203.0.113.10, TTL=64',
                                'detail_en': 'SrcIP=8.8.8.8, DstIP=203.0.113.10, TTL=64',
                                'anomalies': 'Ruta de retorno rota en Internet o descarte en tránsito por ISP.',
                                'anomalies_en': 'Broken return route on the Internet or drop in transit by ISP.',
                                'checks': 'Ping bidireccional, traceroute de retorno.',
                                'checks_en': 'Bidirectional ping, return traceroute.',
                                'packet_capture': {
                                    'notes': 'Verificar la llegada del paquete de retorno a la interfaz WAN.',
                                    'notes_en': 'Verify arrival of return packet on the WAN interface.',
                                    'tcpdump_filter': 'i port1 src 8.8.8.8 and dst 203.0.113.10',
                                    'wireshark_display_filter': 'ip.src == 8.8.8.8 && ip.dst == 203.0.113.10'
                                }
                            },
                            {
                                'name': 'Capa 4 - Transporte (TCP)',
                                'name_en': 'Layer 4 - Transport (TCP)',
                                'detail': 'SrcPort=80, DstPort=10245, Flags=SYN-ACK, Seq=0, Ack=1',
                                'detail_en': 'SrcPort=80, DstPort=10245, Flags=SYN-ACK, Seq=0, Ack=1',
                                'anomalies': 'Servidor no responde en puerto 80 o envía TCP RST (reinicio).',
                                'anomalies_en': 'Server not responding on port 80 or sends TCP RST (reset).',
                                'checks': 'Verificar servicio HTTP activo en servidor.',
                                'checks_en': 'Verify active HTTP service on server.',
                                'packet_capture': {
                                    'notes': 'Verificar flags SYN-ACK de retorno.',
                                    'notes_en': 'Verify return SYN-ACK flags.',
                                    'tcpdump_filter': 'tcp port 80',
                                    'wireshark_display_filter': 'tcp.flags.syn == 1 && tcp.flags.ack == 1'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 5: Gateway revierte la traducción (De-NAT) y reenvía a la LAN',
                        'step_title_en': 'Step 5: Gateway reverts translation (De-NAT) and forwards to LAN',
                        'device': 'Gateway / Firewall (WAN -> LAN)',
                        'device_en': 'Gateway / Firewall (WAN -> LAN)',
                        'action': 'El gateway recibe el paquete de respuesta por port1, busca en su tabla de estados NAT, traduce las cabeceras de destino y lo envía a la LAN.',
                        'action_en': 'The gateway receives the response packet on port1, looks up its NAT state table, translates destination headers, and sends it to the LAN.',
                        'note': 'La IP destino se traduce de 203.0.113.10 a 192.168.1.50 y el puerto se des-traduce de 10245 a 52130.',
                        'note_en': 'The destination IP is translated from 203.0.113.10 to 192.168.1.50, and the port is de-translated from 10245 to 52130.',
                        'layers': [
                            {
                                'name': 'Capa 3 - De-NAT IP de Destino',
                                'name_en': 'Layer 3 - Destination IP De-NAT',
                                'detail': 'DstIP original: 203.0.113.10 -> Traducida: 192.168.1.50. Búsqueda de routing LAN: 192.168.1.0/24 vía port2.',
                                'detail_en': 'Original DstIP: 203.0.113.10 -> Translated: 192.168.1.50. LAN routing lookup: 192.168.1.0/24 via port2.',
                                'anomalies': 'Expiración del timeout de sesión NAT (paquete de respuesta descartado por no haber coincidencia).',
                                'anomalies_en': 'NAT session timeout expiration (response packet discarded due to no match).',
                                'checks': 'Configuración de timeouts de sesión TCP en firewall (ej. TCP half-close timeout).',
                                'checks_en': 'TCP session timeout configuration on firewall (e.g. TCP half-close timeout).',
                                'packet_capture': {
                                    'notes': 'Verificar que la trama salga traducida por la interfaz LAN.',
                                    'notes_en': 'Verify the frame exits translated on the LAN interface.',
                                    'tcpdump_filter': 'i port2 dst 192.168.1.50 and tcp port 80',
                                    'wireshark_display_filter': 'ip.dst == 192.168.1.50 && tcp.port == 80'
                                }
                            },
                            {
                                'name': 'Capa 4 - De-NAT Puerto de Destino',
                                'name_en': 'Layer 4 - Destination Port De-NAT',
                                'detail': 'DstPort original: 10245 -> Traducido de vuelta a: 52130. Recalcular checksums.',
                                'detail_en': 'Original DstPort: 10245 -> Translated back to: 52130. Recalculate checksums.',
                                'anomalies': 'Falla de traducción de puertos por colisión interna.',
                                'anomalies_en': 'Port translation failure due to internal collision.',
                                'checks': 'Estadísticas de colisiones en la tabla de traducción del firewall.',
                                'checks_en': 'Collision statistics in the firewall translation table.',
                                'packet_capture': {
                                    'notes': 'Verificar puerto de destino final TCP en la LAN.',
                                    'notes_en': 'Verify final TCP destination port on the LAN.',
                                    'tcpdump_filter': 'i port2 tcp port 52130',
                                    'wireshark_display_filter': 'tcp.dstport == 52130'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 6: PC-Cliente recibe el paquete de respuesta',
                        'step_title_en': 'Step 6: PC-Client receives the response packet',
                        'device': 'PC-Cliente (IP: 192.168.1.50)',
                        'device_en': 'PC-Client (IP: 192.168.1.50)',
                        'action': 'El PC cliente recibe el paquete TCP SYN-ACK en el socket abierto y envía el ACK final, completando el saludo de 3 vías (3-way handshake).',
                        'action_en': 'The client PC receives the TCP SYN-ACK packet on the open socket and sends the final ACK, completing the 3-way handshake.',
                        'note': 'La conexión TCP queda establecida de forma transparente para el cliente final.',
                        'note_en': 'The TCP connection is established transparently for the end client.',
                        'layers': [
                            {
                                'name': 'Capa 4 - Establecimiento TCP',
                                'name_en': 'Layer 4 - TCP Establishment',
                                'detail': 'Recibe SYN-ACK de 8.8.8.8:80. Estado de socket: ESTABLISHED.',
                                'detail_en': 'Receives SYN-ACK from 8.8.8.8:80. Socket state: ESTABLISHED.',
                                'anomalies': 'El host local cierra la conexión (TCP RST) si el puerto de destino no coincide con ningún socket abierto.',
                                'anomalies_en': 'The local host closes the connection (TCP RST) if the destination port does not match any open socket.',
                                'checks': 'Comprobar estado del socket con `netstat -an` o `ss -t`.',
                                'checks_en': 'Check socket state with `netstat -an` or `ss -t`.',
                                'packet_capture': {
                                    'notes': 'Verificar el flujo de tres vías completo en el cliente.',
                                    'notes_en': 'Verify the full 3-way handshake on the client.',
                                    'tcpdump_filter': 'tcp port 80',
                                    'wireshark_display_filter': 'tcp.port == 80'
                                }
                            }
                        ]
                    }
                ]
            },
            {
                'id': 'destination_nat_vip_inbound',
                'name': 'Destination NAT (VIP): Acceso Externo a Servidor Web Interno',
                'name_en': 'Destination NAT (VIP): External Access to Internal Web Server',
                'description': 'Simulación de una petición desde Internet dirigida a la IP pública del Gateway, la cual se traduce mediante DNAT (Virtual IP) hacia un servidor interno en la DMZ en un puerto específico.',
                'description_en': 'Simulation of a request from the Internet directed to the Gateways public IP, translated via DNAT (Virtual IP) to an internal server on the DMZ on a specific port.',
                'steps': [
                    {
                        'step_title': 'Paso 1: Host externo en Internet inicia conexión HTTPS',
                        'step_title_en': 'Step 1: External host on Internet initiates HTTPS connection',
                        'device': 'Host Externo (IP: 198.51.100.22)',
                        'device_en': 'External Host (IP: 198.51.100.22)',
                        'action': 'Un cliente en Internet inicia una conexión TCP SYN hacia la IP pública de la empresa en el puerto HTTPS 443.',
                        'action_en': 'A client on the Internet initiates a TCP SYN connection to the public IP of the company on HTTPS port 443.',
                        'note': 'El paquete viaja a través de Internet hasta la interfaz WAN del Gateway corporativo.',
                        'note_en': 'The packet travels through the Internet to the WAN interface of the corporate Gateway.',
                        'layers': [
                            {
                                'name': 'Capa 3 - Red (IPv4)',
                                'name_en': 'Layer 3 - Network (IPv4)',
                                'detail': 'SrcIP=198.51.100.22, DstIP=203.0.113.10 (Gateway Public IP), TTL=56',
                                'detail_en': 'SrcIP=198.51.100.22, DstIP=203.0.113.10 (Gateway Public IP), TTL=56',
                                'anomalies': 'Ruta de Internet rota, paquete descartado en el ISP.',
                                'anomalies_en': 'Internet route broken, packet discarded at the ISP.',
                                'checks': 'Verificar alcance de la IP pública desde fuentes externas.',
                                'checks_en': 'Verify reachability of the public IP from external sources.',
                                'packet_capture': {
                                    'notes': 'Verificar la llegada del paquete SYN en la interfaz WAN.',
                                    'notes_en': 'Verify the arrival of the SYN packet on the WAN interface.',
                                    'tcpdump_filter': 'tcp port 443',
                                    'wireshark_display_filter': 'tcp.port == 443'
                                }
                            },
                            {
                                'name': 'Capa 4 - Transporte (TCP)',
                                'name_en': 'Layer 4 - Transport (TCP)',
                                'detail': 'SrcPort=48120, DstPort=443, Flags=SYN, Seq=0',
                                'detail_en': 'SrcPort=48120, DstPort=443, Flags=SYN, Seq=0',
                                'anomalies': 'TCP SYN corrupto o puerto bloqueado en tránsito.',
                                'anomalies_en': 'TCP SYN corrupted or port blocked in transit.',
                                'checks': 'Estadísticas de drop de TCP en el firewall de tránsito.',
                                'checks_en': 'TCP drop statistics on the transit firewall.',
                                'packet_capture': {
                                    'notes': 'Verificar flags TCP.',
                                    'notes_en': 'Verify TCP flags.',
                                    'tcpdump_filter': 'tcp',
                                    'wireshark_display_filter': 'tcp.flags.syn == 1'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 2: Gateway aplica Destination NAT (VIP) y evalúa políticas',
                        'step_title_en': 'Step 2: Gateway applies Destination NAT (VIP) and evaluates policies',
                        'device': 'Gateway / Firewall (Interfaz de ingreso: port1 - WAN)',
                        'device_en': 'Gateway / Firewall (Ingress interface: port1 - WAN)',
                        'action': 'El gateway intercepta el paquete en port1, busca reglas de DNAT activas, traduce el destino y evalúa las políticas de seguridad.',
                        'action_en': 'The gateway intercepts the packet on port1, looks up active DNAT rules, translates the destination, and evaluates security policies.',
                        'note': 'La IP destino 203.0.113.10:443 coincide con una regla Virtual IP (VIP) que la traduce a 10.0.10.10:8443 en la DMZ. Se permite por la política de seguridad.',
                        'note_en': 'Destination IP 203.0.113.10:443 matches a Virtual IP (VIP) rule that translates it to 10.0.10.10:8443 in the DMZ. Security policy allows it.',
                        'layers': [
                            {
                                'name': 'Capa 3 - Traducción IP (Destination NAT)',
                                'name_en': 'Layer 3 - IP Translation (Destination NAT)',
                                'detail': 'DstIP original: 203.0.113.10 -> Traducida: 10.0.10.10 (Servidor DMZ). Búsqueda de ruta: 10.0.10.0/24 vía port3 (DMZ).',
                                'detail_en': 'Original DstIP: 203.0.113.10 -> Translated: 10.0.10.10 (DMZ Server). Route lookup: 10.0.10.0/24 via port3 (DMZ).',
                                'anomalies': 'Configuración de IP virtual (VIP) incorrecta o inactiva en el firewall.',
                                'anomalies_en': 'Incorrect or inactive Virtual IP (VIP) configuration on the firewall.',
                                'checks': 'Revisar la configuración de VIP (`show firewall vip` o equivalente).',
                                'checks_en': 'Review VIP configuration (`show firewall vip` or equivalent).',
                                'packet_capture': {
                                    'notes': 'Verificar traducción del IP destino en logs del firewall.',
                                    'notes_en': 'Verify destination IP translation in firewall logs.',
                                    'tcpdump_filter': 'No aplicable',
                                    'wireshark_display_filter': 'No aplicable'
                                }
                            },
                            {
                                'name': 'Capa 4 - Traducción de Puerto y Políticas',
                                'name_en': 'Layer 4 - Port Translation & Policies',
                                'detail': 'DstPort original: 443 -> Traducido: 8443. Política de seguridad evaluada contra IP real (10.0.10.10) y puerto (8443): MATCH en ID 12 (Permitir). Se crea sesión NAT.',
                                'detail_en': 'Original DstPort: 443 -> Translated: 8443. Security policy evaluated against real IP (10.0.10.10) and port (8443): MATCH on ID 12 (Allow). NAT session is created.',
                                'anomalies': 'Política de seguridad bloquea el puerto traducido 8443 (drop) o error al evaluar la política pre-NAT/post-NAT.',
                                'anomalies_en': 'Security policy blocks translated port 8443 (drop) or pre-NAT/post-NAT policy evaluation error.',
                                'checks': 'Confirmar que la política de seguridad use la IP/puerto interno real (post-translation) en firewalls modernos.',
                                'checks_en': 'Confirm that the security policy uses the real internal IP/port (post-translation) in modern firewalls.',
                                'packet_capture': {
                                    'notes': 'Inspeccionar hits de políticas de seguridad en el firewall.',
                                    'notes_en': 'Inspect security policy hits on the firewall.',
                                    'tcpdump_filter': 'No aplicable',
                                    'wireshark_display_filter': 'No aplicable'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 3: Gateway reenvía el paquete traducido hacia la DMZ',
                        'step_title_en': 'Step 3: Gateway forwards the translated packet to the DMZ',
                        'device': 'Gateway / Firewall (Interfaz de salida: port3 - DMZ)',
                        'device_en': 'Gateway / Firewall (Egress interface: port3 - DMZ)',
                        'action': 'El gateway encapsula el paquete con las IPs traducidas en una trama Ethernet y lo envía por el puerto de la DMZ hacia el Servidor.',
                        'action_en': 'The gateway encapsulates the packet with translated IPs into an Ethernet frame and sends it through the DMZ port to the Server.',
                        'note': 'El paquete viaja a través del switch DMZ hasta la interfaz física del servidor web.',
                        'note_en': 'The packet travels through the DMZ switch to the web servers physical interface.',
                        'layers': [
                            {
                                'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                'name_en': 'Layer 2 - Data Link (Ethernet)',
                                'detail': 'SrcMAC=MAC_Gateway_DMZ, DstMAC=MAC_Servidor (resuelto por ARP), EtherType=0x0800',
                                'detail_en': 'SrcMAC=MAC_Gateway_DMZ, DstMAC=MAC_Servidor (resolved via ARP), EtherType=0x0800',
                                'anomalies': 'Falla de resolución ARP para la IP del servidor (10.0.10.10).',
                                'anomalies_en': 'ARP resolution failure for server IP (10.0.10.10).',
                                'checks': 'Revisar la tabla ARP del firewall (`get sys arp` / `show arp`).',
                                'checks_en': 'Check firewall ARP table (`get sys arp` / `show arp`).',
                                'packet_capture': {
                                    'notes': 'Verificar el paquete traducido saliendo por port3.',
                                    'notes_en': 'Verify the translated packet exiting port3.',
                                    'tcpdump_filter': 'i port3 host 10.0.10.10 and tcp port 8443',
                                    'wireshark_display_filter': 'ip.dst == 10.0.10.10 && tcp.dstport == 8443'
                                }
                            },
                            {
                                'name': 'Capa 3 - Red (IPv4)',
                                'name_en': 'Layer 3 - Network (IPv4)',
                                'detail': 'SrcIP=198.51.100.22, DstIP=10.0.10.10, TTL=55',
                                'detail_en': 'SrcIP=198.51.100.22, DstIP=10.0.10.10, TTL=55',
                                'anomalies': 'Checksum IP incorrecto recalculado por el firewall.',
                                'anomalies_en': 'Incorrect IP checksum recalculated by the firewall.',
                                'checks': 'Estadísticas de descartes por checksum en el host de destino.',
                                'checks_en': 'Checksum drop statistics on the destination host.',
                                'packet_capture': {
                                    'notes': 'Inspeccionar cabeceras IP.',
                                    'notes_en': 'Inspect IP headers.',
                                    'tcpdump_filter': 'i port3 ip',
                                    'wireshark_display_filter': 'ip.dst == 10.0.10.10'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 4: Servidor procesa la petición y responde con TCP SYN-ACK',
                        'step_title_en': 'Step 4: Server processes request and responds with TCP SYN-ACK',
                        'device': 'Servidor Web Interno (IP: 10.0.10.10)',
                        'device_en': 'Internal Web Server (IP: 10.0.10.10)',
                        'action': 'El servidor web recibe el paquete en el puerto 8443, lo procesa y genera la respuesta SYN-ACK dirigida a la IP externa original.',
                        'action_en': 'The web server receives the packet on port 8443, processes it, and generates the SYN-ACK response directed to the original external IP.',
                        'note': 'El servidor web no sabe que hubo DNAT; responde de manera nativa usando su propia IP como origen y puerto 8443.',
                        'note_en': 'The web server does not know DNAT occurred; it responds natively using its own IP as source and port 8443.',
                        'layers': [
                            {
                                'name': 'Capa 3 - Red (IPv4)',
                                'name_en': 'Layer 3 - Network (IPv4)',
                                'detail': 'SrcIP=10.0.10.10, DstIP=198.51.100.22, TTL=64. Enrutamiento: hacia Default Gateway (IP del firewall DMZ).',
                                'detail_en': 'SrcIP=10.0.10.10, DstIP=198.51.100.22, TTL=64. Routing: to Default Gateway (DMZ firewall IP).',
                                'anomalies': 'Ruta por defecto faltante o incorrecta en el servidor (tráfico de respuesta se envía por otra interfaz o se descarta).',
                                'anomalies_en': 'Missing or incorrect default route on the server (response traffic sent through another interface or discarded).',
                                'checks': 'Verificar tabla de rutas en el servidor web (`ip route` / `route print`).',
                                'checks_en': 'Verify routing table on the web server (`ip route` / `route print`).',
                                'packet_capture': {
                                    'notes': 'Verificar el paquete de respuesta saliendo de la interfaz del servidor.',
                                    'notes_en': 'Verify the response packet exiting the server interface.',
                                    'tcpdump_filter': 'tcp port 8443',
                                    'wireshark_display_filter': 'tcp.srcport == 8443'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 5: Gateway revierte la traducción (De-NAT) y reenvía a Internet',
                        'step_title_en': 'Step 5: Gateway reverts translation (De-NAT) and forwards to Internet',
                        'device': 'Gateway / Firewall (DMZ -> WAN)',
                        'device_en': 'Gateway / Firewall (DMZ -> WAN)',
                        'action': 'El gateway recibe el paquete de respuesta en port3, busca en su tabla de estados NAT, revierte el DNAT en las cabeceras de origen y lo envía a la WAN.',
                        'action_en': 'The gateway receives the response packet on port3, looks up its NAT state table, reverts DNAT in source headers, and sends it to the WAN.',
                        'note': 'El origen se traduce de 10.0.10.10 a la IP pública corporativa 203.0.113.10, y el puerto se des-traduce de 8443 a 443.',
                        'note_en': 'Source translates from 10.0.10.10 to corporate public IP 203.0.113.10, and port de-translates from 8443 to 443.',
                        'layers': [
                            {
                                'name': 'Capa 3 - De-NAT IP de Origen',
                                'name_en': 'Layer 3 - Source IP De-NAT',
                                'detail': 'SrcIP original: 10.0.10.10 -> Traducida: 203.0.113.10. Enrutamiento WAN: hacia ISP en port1.',
                                'detail_en': 'Original SrcIP: 10.0.10.10 -> Translated: 203.0.113.10. WAN routing: to ISP on port1.',
                                'anomalies': 'Expiración de la sesión NAT en el firewall (paquete de respuesta descartado).',
                                'anomalies_en': 'NAT session expiration on the firewall (response packet discarded).',
                                'checks': 'Verificar tabla de sesiones en firewall.',
                                'checks_en': 'Verify session table on firewall.',
                                'packet_capture': {
                                    'notes': 'Verificar paquete de respuesta en WAN con IP origen pública.',
                                    'notes_en': 'Verify response packet on WAN with public source IP.',
                                    'tcpdump_filter': 'i port1 src 203.0.113.10 and tcp port 443',
                                    'wireshark_display_filter': 'ip.src == 203.0.113.10 && tcp.srcport == 443'
                                }
                            },
                            {
                                'name': 'Capa 4 - De-NAT Puerto de Origen',
                                'name_en': 'Layer 4 - Source Port De-NAT',
                                'detail': 'SrcPort original: 8443 -> Traducido a: 443. Checksums TCP e IP recalculados.',
                                'detail_en': 'Original SrcPort: 8443 -> Translated to: 443. TCP and IP checksums recalculated.',
                                'anomalies': 'Falla de traducción de puertos.',
                                'anomalies_en': 'Port translation failure.',
                                'checks': 'Revisar logs de NAT del firewall.',
                                'checks_en': 'Review firewall NAT logs.',
                                'packet_capture': {
                                    'notes': 'Verificar que el puerto origen sea 443.',
                                    'notes_en': 'Verify that the source port is 443.',
                                    'tcpdump_filter': 'i port1 tcp port 443',
                                    'wireshark_display_filter': 'tcp.srcport == 443'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 6: Host en Internet recibe el paquete SYN-ACK',
                        'step_title_en': 'Step 6: Host on Internet receives the SYN-ACK packet',
                        'device': 'Host Externo (IP: 198.51.100.22)',
                        'device_en': 'External Host (IP: 198.51.100.22)',
                        'action': 'El host externo recibe el SYN-ACK desde la IP pública en el puerto 443, completando el saludo de 3 vías de manera transparente.',
                        'action_en': 'The external host receives the SYN-ACK from the public IP on port 443, completing the 3-way handshake transparently.',
                        'note': 'El cliente externo nunca se entera de la existencia del puerto 8443 ni de la IP privada del servidor.',
                        'note_en': 'The external client never knows of the existence of port 8443 or the private IP of the server.',
                        'layers': [
                            {
                                'name': 'Capa 4 - Establecimiento TCP',
                                'name_en': 'Layer 4 - TCP Establishment',
                                'detail': 'Recibe SYN-ACK de 203.0.113.10:443. Estado: ESTABLISHED.',
                                'detail_en': 'Receives SYN-ACK from 203.0.113.10:443. State: ESTABLISHED.',
                                'anomalies': 'Conexión rechazada por el cliente si el TTL expiró o si hubo demoras excesivas.',
                                'anomalies_en': 'Connection rejected by client if TTL expired or if there were excessive delays.',
                                'checks': 'Inspección de tiempos de respuesta en el navegador del cliente.',
                                'checks_en': 'Inspection of response times in the client browser.',
                                'packet_capture': {
                                    'notes': 'Verificar handshake final TCP en el extremo del cliente.',
                                    'notes_en': 'Verify final TCP handshake on the client side.',
                                    'tcpdump_filter': 'tcp port 443',
                                    'wireshark_display_filter': 'tcp.port == 443'
                                }
                            }
                        ]
                    }
                ]
            },
            {
                'id': 'static_nat_1to1_mapping',
                'name': 'NAT Estático (1:1): Mapeo Bidireccional de Servidor',
                'name_en': 'Static NAT (1:1): Bidirectional Server Mapping',
                'description': 'Simulación de traducción estática 1 a 1 entre una dirección IP privada y una dirección IP pública. El tráfico saliente desde el servidor siempre se traduce a su IP pública correspondiente, y las peticiones entrantes a esa IP pública se redirigen a su IP privada.',
                'description_en': 'Simulation of static 1-to-1 translation between a private IP address and a public IP address. Outbound traffic from the server always translates to its corresponding public IP, and inbound requests to that public IP redirect to its private IP.',
                'steps': [
                    {
                        'step_title': 'Paso 1: Servidor interno inicia tráfico hacia Internet (Outbound)',
                        'step_title_en': 'Step 1: Internal server initiates traffic to the Internet (Outbound)',
                        'device': 'Servidor Interno (IP: 10.0.10.20)',
                        'device_en': 'Internal Server (IP: 10.0.10.20)',
                        'action': 'El servidor interno inicia una consulta DNS o servicio externo enviando un paquete hacia un host en Internet.',
                        'action_en': 'The internal server initiates a DNS query or external service, sending a packet to a host on the Internet.',
                        'note': 'El servidor utiliza su IP privada como origen.',
                        'note_en': 'The server uses its private IP as source.',
                        'layers': [
                            {
                                'name': 'Capa 3 - Red (IPv4)',
                                'name_en': 'Layer 3 - Network (IPv4)',
                                'detail': 'SrcIP=10.0.10.20, DstIP=198.51.100.22, TTL=64, Protocol=UDP',
                                'detail_en': 'SrcIP=10.0.10.20, DstIP=198.51.100.22, TTL=64, Protocol=UDP',
                                'anomalies': 'Servidor sin IP estática configurada o sin default gateway.',
                                'anomalies_en': 'Server without configured static IP or default gateway.',
                                'checks': 'Verificar configuración IP local en el servidor.',
                                'checks_en': 'Verify local IP configuration on the server.',
                                'packet_capture': {
                                    'notes': 'Verificar la salida del paquete UDP original.',
                                    'notes_en': 'Verify the original UDP outbound packet.',
                                    'tcpdump_filter': 'udp port 53',
                                    'wireshark_display_filter': 'udp.port == 53'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 2: Gateway traduce IP origen 1:1 y envía por WAN',
                        'step_title_en': 'Step 2: Gateway translates Source IP 1:1 and forwards via WAN',
                        'device': 'Gateway / Firewall (Interfaz de salida: port1 - WAN)',
                        'device_en': 'Gateway / Firewall (Egress interface: port1 - WAN)',
                        'action': 'El gateway evalúa la regla de NAT Estático 1:1, traduce el IP origen del servidor a su IP pública reservada y reenvía el paquete.',
                        'action_en': 'The gateway evaluates the Static 1:1 NAT rule, translates the servers source IP to its reserved public IP, and forwards the packet.',
                        'note': 'Mapeo estático activo: 10.0.10.20 <-> 203.0.113.20. El IP de origen se traduce de 10.0.10.20 a 203.0.113.20. Los puertos no sufren cambios ya que es un mapeo 1:1 dedicado.',
                        'note_en': 'Active static mapping: 10.0.10.20 <-> 203.0.113.20. Source IP translates from 10.0.10.20 to 203.0.113.20. Ports are unchanged since this is a dedicated 1:1 mapping.',
                        'layers': [
                            {
                                'name': 'Capa 3 - Traducción IP (Static NAT)',
                                'name_en': 'Layer 3 - IP Translation (Static NAT)',
                                'detail': 'SrcIP original: 10.0.10.20 -> Traducida: 203.0.113.20. DstIP original=198.51.100.22 (sin cambios).',
                                'detail_en': 'Original SrcIP: 10.0.10.20 -> Translated: 203.0.113.20. Original DstIP=198.51.100.22 (unchanged).',
                                'anomalies': 'Mapeo de NAT estático mal configurado o IP pública no asignada al gateway.',
                                'anomalies_en': 'Misconfigured static NAT mapping or public IP not assigned to the gateway.',
                                'checks': 'Verificar políticas de NAT estático (`show firewall central-nat-rule` o equivalente).',
                                'checks_en': 'Verify static NAT policies (`show firewall central-nat-rule` or equivalent).',
                                'packet_capture': {
                                    'notes': 'Verificar paquete traducido en la interfaz WAN.',
                                    'notes_en': 'Verify translated packet on the WAN interface.',
                                    'tcpdump_filter': 'i port1 host 203.0.113.20',
                                    'wireshark_display_filter': 'ip.src == 203.0.113.20'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 3: Host externo recibe y responde a la IP pública dedicada',
                        'step_title_en': 'Step 3: External host receives and responds to the dedicated public IP',
                        'device': 'Host Externo (IP: 198.51.100.22)',
                        'device_en': 'External Host (IP: 198.51.100.22)',
                        'action': 'El host externo procesa la petición y responde enviando el tráfico hacia la IP pública dedicada del servidor.',
                        'action_en': 'The external host processes the request and responds, sending traffic to the servers dedicated public IP.',
                        'note': 'El host de destino ve la IP 203.0.113.20 como origen y le responde directamente.',
                        'note_en': 'The destination host sees IP 203.0.113.20 as source and responds to it directly.',
                        'layers': [
                            {
                                'name': 'Capa 3 - Red (IPv4)',
                                'name_en': 'Layer 3 - Network (IPv4)',
                                'detail': 'SrcIP=198.51.100.22, DstIP=203.0.113.20, TTL=64',
                                'detail_en': 'SrcIP=198.51.100.22, DstIP=203.0.113.20, TTL=64',
                                'anomalies': 'Ruta de retorno fallida hacia la subred pública de NAT.',
                                'anomalies_en': 'Failed return route to the public NAT subnet.',
                                'checks': 'Asegurar que el ISP enrute la IP de NAT pública dedicada (203.0.113.20) hacia la interfaz WAN del gateway (ARP proxy o ruta estática).',
                                'checks_en': 'Ensure the ISP routes the dedicated public NAT IP (203.0.113.20) to the gateways WAN interface (proxy ARP or static route).',
                                'packet_capture': {
                                    'notes': 'Verificar la llegada del paquete en WAN.',
                                    'notes_en': 'Verify arrival of packet on WAN.',
                                    'tcpdump_filter': 'i port1 dst 203.0.113.20',
                                    'wireshark_display_filter': 'ip.dst == 203.0.113.20'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 4: Gateway recibe en WAN, traduce Destino 1:1 y entrega al servidor',
                        'step_title_en': 'Step 4: Gateway receives on WAN, translates Destination 1:1 and delivers to server',
                        'device': 'Gateway / Firewall (WAN -> DMZ)',
                        'device_en': 'Gateway / Firewall (WAN -> DMZ)',
                        'action': 'El gateway intercepta el paquete de respuesta dirigido a la IP pública 203.0.113.20, traduce el destino a la IP privada del servidor y lo entrega por port3.',
                        'action_en': 'The gateway intercepts the response packet addressed to public IP 203.0.113.20, translates the destination to the servers private IP, and delivers it through port3.',
                        'note': 'Al ser un mapeo bidireccional estático, no se requiere coincidencia estricta de sesión dinámica para tráfico entrante; se traduce usando la regla 1:1 estática.',
                        'note_en': 'As this is a bidirectional static mapping, strict dynamic session match is not required for inbound traffic; it translates using the static 1:1 rule.',
                        'layers': [
                            {
                                'name': 'Capa 3 - De-NAT IP de Destino',
                                'name_en': 'Layer 3 - Destination IP De-NAT',
                                'detail': 'DstIP original: 203.0.113.20 -> Traducida: 10.0.10.20. Búsqueda de routing DMZ: 10.0.10.0/24 vía port3.',
                                'detail_en': 'Original DstIP: 203.0.113.20 -> Translated: 10.0.10.20. DMZ routing lookup: 10.0.10.0/24 via port3.',
                                'anomalies': 'Descarte en el gateway por política de seguridad entrante (ACL bloqueando el tráfico hacia la IP privada).',
                                'anomalies_en': 'Discard at the gateway due to inbound security policy (ACL blocking traffic to the private IP).',
                                'checks': 'Verificar política de seguridad WAN -> DMZ para la IP privada 10.0.10.20.',
                                'checks_en': 'Verify WAN -> DMZ security policy for private IP 10.0.10.20.',
                                'packet_capture': {
                                    'notes': 'Verificar el paquete traducido saliendo por la DMZ hacia el servidor.',
                                    'notes_en': 'Verify the translated packet exiting the DMZ to the server.',
                                    'tcpdump_filter': 'i port3 dst 10.0.10.20',
                                    'wireshark_display_filter': 'ip.dst == 10.0.10.20'
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    },
    'static_routing': {
        'scenarios': [
            {
                'id': 'static_routing_transit_http',
                'name': 'Búsqueda de Ruta y Tránsito de Paquete HTTP (L1-L7)',
                'name_en': 'Route Lookup and HTTP Packet Transit (L1-L7)',
                'description': 'Simulación de la búsqueda de ruta estática, coincidencia del prefijo más específico (LPM), resolución de siguiente salto recursivo y paso de capas OSI de 1 a 7 para un paquete HTTP GET de tránsito.',
                'description_en': 'Simulation of static route lookup, longest prefix match (LPM), recursive next-hop resolution, and OSI layers 1 to 7 processing for a transit HTTP GET packet.',
                'steps': [
                    {
                        'step_title': 'Paso 1: Recepción del paquete físico y decapsulación L2',
                        'step_title_en': 'Step 1: Physical packet reception and L2 decapsulation',
                        'device': 'Router de Agregación (Interfaz de Ingreso: ge-0/0/0)',
                        'device_en': 'Aggregation Router (Ingress Interface: ge-0/0/0)',
                        'action': 'El puerto óptico ge-0/0/0 recibe fotones, convierte la señal a pulsos eléctricos y decodifica la trama Ethernet.',
                        'action_en': 'Optical port ge-0/0/0 receives photons, converts the signal to electrical pulses, and decodes the Ethernet frame.',
                        'note': 'El router verifica que la dirección MAC destino de la trama coincida con su propia dirección MAC de interfaz para aceptar el paquete.',
                        'note_en': 'The router verifies that the destination MAC address of the frame matches its own interface MAC address to accept the packet.',
                        'layers': [
                            {
                                'name': 'Capa 1 - Física (Óptica)',
                                'name_en': 'Layer 1 - Physical (Optical)',
                                'detail': 'Interfaz ge-0/0/0, potencia óptica de entrada: -8.2 dBm (dentro del rango aceptable), modulación 1000BASE-LX, bitrate 1.25 Gbps.',
                                'detail_en': 'Interface ge-0/0/0, optical input power: -8.2 dBm (within acceptable range), 1000BASE-LX modulation, 1.25 Gbps bitrate.',
                                'checks': 'Verificar potencia del transceptor (show interfaces diagnostics optics ge-0/0/0) y estado del link (Up).',
                                'checks_en': 'Verify transceiver power (show interfaces diagnostics optics ge-0/0/0) and link status (Up).',
                                'anomalies': 'RX loss-of-signal (LOS), potencia óptica fuera de rango (ej. -22 dBm), link flapping por fibra defectuosa o suciedad.',
                                'anomalies_en': 'RX loss-of-signal (LOS), optical power out of range (e.g. -22 dBm), link flapping due to bad fiber or dirt.',
                                'packet_capture': {
                                    'notes': 'No es posible capturar a nivel físico de fotones; usar analizador de espectro óptico si se sospecha atenuación.',
                                    'notes_en': 'Physical photons capture not possible; use optical spectrum analyzer if attenuation is suspected.',
                                    'tcpdump_filter': 'No aplicable a nivel óptico',
                                    'wireshark_display_filter': 'No aplicable a nivel óptico'
                                }
                            },
                            {
                                'name': 'Capa 2 - Enlace de Datos (Ethernet)',
                                'name_en': 'Layer 2 - Data Link (Ethernet)',
                                'detail': 'SrcMAC=MAC_Cliente (00:50:56:a1:b2:c3), DstMAC=MAC_Router_Ingreso (00:50:56:88:99:aa), EtherType=0x0800 (IPv4).',
                                'detail_en': 'SrcMAC=MAC_Cliente (00:50:56:a1:b2:c3), DstMAC=MAC_Router_Ingreso (00:50:56:88:99:aa), EtherType=0x0800 (IPv4).',
                                'checks': 'Validar que el router reciba tramas con su MAC origen en la tabla de interfaces. Comprobar que no haya errores de CRC.',
                                'checks_en': 'Validate that the router receives frames with its MAC source in the interface table. Check that there are no CRC errors.',
                                'anomalies': 'Errores CRC/FCS (trama corrupta en el cable), descartes por destino MAC incorrecto (si el cliente envía a otra MAC), MTU mismatch.',
                                'anomalies_en': 'CRC/FCS errors (frame corrupted on cable), discards due to wrong destination MAC (if client sends to another MAC), MTU mismatch.',
                                'packet_capture': {
                                    'notes': 'Capturar en interfaz ge-0/0/0.',
                                    'notes_en': 'Capture on interface ge-0/0/0.',
                                    'tcpdump_filter': 'ether proto 0x0800',
                                    'wireshark_display_filter': 'eth.type == 0x0800'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 2: Análisis de cabeceras IP y búsqueda de la ruta más específica (LPM)',
                        'step_title_en': 'Step 2: IP header analysis and Longest Prefix Match (LPM) route lookup',
                        'device': 'Router de Agregación (Plano de Control / Motor de Ruta)',
                        'device_en': 'Aggregation Router (Control Plane / Route Engine)',
                        'action': 'El router extrae el paquete IPv4 de la trama, valida el checksum IP, e inspecciona la IP destino 192.168.100.45 de la petición HTTP GET de tránsito.',
                        'action_en': 'The router extracts the IPv4 packet from the frame, validates the IP checksum, and inspects the destination IP 192.168.100.45 of the transit HTTP GET request.',
                        'note': 'Se realiza una búsqueda en la tabla de enrutamiento (RIB) usando Longest Prefix Match (LPM). Coincide con la ruta estática 192.168.100.0/24 en lugar de la ruta por defecto 0.0.0.0/0.',
                        'note_en': 'A search is performed in the routing table (RIB) using Longest Prefix Match (LPM). It matches the static route 192.168.100.0/24 instead of the default route 0.0.0.0/0.',
                        'layers': [
                            {
                                'name': 'Capa 3 - Red (IPv4)',
                                'name_en': 'Layer 3 - Network (IPv4)',
                                'detail': 'SrcIP=10.10.10.50 (Cliente), DstIP=192.168.100.45 (Servidor Web Externo), TTL=64, Protocol=6 (TCP). Ruta coincidente: 192.168.100.0/24 vía Next-Hop 10.200.200.1 (no conectado directamente).',
                                'detail_en': 'SrcIP=10.10.10.50 (Client), DstIP=192.168.100.45 (External Web Server), TTL=64, Protocol=6 (TCP). Matching route: 192.168.100.0/24 via Next-Hop 10.200.200.1 (not directly connected).',
                                'checks': 'Verificar la tabla de rutas con show route 192.168.100.45 y comprobar que la ruta estática esté instalada en la RIB.',
                                'checks_en': 'Verify the routing table with show route 192.168.100.45 and check that the static route is installed in the RIB.',
                                'anomalies': 'IP dest inalcanzable (sin ruta por defecto ni estática), descartes de TTL (TTL=0), checksum IP inválido.',
                                'anomalies_en': 'Destination IP unreachable (no default or static route), TTL discards (TTL=0), invalid IP checksum.',
                                'packet_capture': {
                                    'notes': 'Inspeccionar cabeceras IP y ver TTL.',
                                    'notes_en': 'Inspect IP headers and check TTL.',
                                    'tcpdump_filter': 'ip dst 192.168.100.45',
                                    'wireshark_display_filter': 'ip.dst == 192.168.100.45'
                                }
                            },
                            {
                                'name': 'Capa 4 - Transporte (TCP)',
                                'name_en': 'Layer 4 - Transport (TCP)',
                                'detail': 'SrcPort=49200, DstPort=80, Seq=1, Ack=1, Flags=[ACK, PSH], Window=65535.',
                                'detail_en': 'SrcPort=49200, DstPort=80, Seq=1, Ack=1, Flags=[ACK, PSH], Window=65535.',
                                'checks': 'Confirmar que el puerto destino sea 80 (HTTP estándar).',
                                'checks_en': 'Confirm that the destination port is 80 (standard HTTP).',
                                'anomalies': 'Puerto cerrado en destino que cause TCP RST, descartes de firewall intermedios por reglas ACL.',
                                'anomalies_en': 'Closed port at destination causing TCP RST, intermediate firewall discards due to ACL rules.',
                                'packet_capture': {
                                    'notes': 'Revisar el handshake TCP y la carga útil.',
                                    'notes_en': 'Check the TCP handshake and payload.',
                                    'tcpdump_filter': 'tcp port 80',
                                    'wireshark_display_filter': 'tcp.port == 80'
                                }
                            },
                            {
                                'name': 'Capa 7 - Aplicación (HTTP)',
                                'name_en': 'Layer 7 - Application (HTTP)',
                                'detail': 'HTTP GET /index.html HTTP/1.1, Host: www.servidorexterno.com, User-Agent: Mozilla/5.0.',
                                'detail_en': 'HTTP GET /index.html HTTP/1.1, Host: www.servidorexterno.com, User-Agent: Mozilla/5.0.',
                                'checks': 'Validar que el request HTTP esté completo y bien formado.',
                                'checks_en': 'Validate that the HTTP request is complete and well-formed.',
                                'anomalies': 'Payload HTTP malformado, descarte por filtros de capa 7 (WAF/DPI) en el router o firewall de tránsito.',
                                'anomalies_en': 'Malformed HTTP payload, discard by Layer 7 filters (WAF/DPI) on transit router or firewall.',
                                'packet_capture': {
                                    'notes': 'Analizar flujo HTTP.',
                                    'notes_en': 'Analyze HTTP stream.',
                                    'tcpdump_filter': 'tcp port 80 and (tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420)',
                                    'wireshark_display_filter': 'http.request.method == "GET"'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 3: Resolución recursiva del siguiente salto',
                        'step_title_en': 'Step 3: Recursive next-hop resolution',
                        'device': 'Router de Agregación (Tabla de Rutas / RIB)',
                        'device_en': 'Aggregation Router (Routing Table / RIB)',
                        'action': 'El siguiente salto de nuestra ruta estática es 10.200.200.1 (no conectado directamente). El router busca cómo llegar a 10.200.200.1.',
                        'action_en': 'The next-hop of our static route is 10.200.200.1 (not directly connected). The router looks up how to reach 10.200.200.1.',
                        'note': 'El router realiza una búsqueda recursiva y encuentra una ruta OSPF para 10.200.200.0/30 con siguiente salto directo 10.10.12.2 a través de la interfaz ge-0/0/1.',
                        'note_en': 'The router performs a recursive lookup and finds an OSPF route for 10.200.200.0/30 with a direct next-hop 10.10.12.2 via interface ge-0/0/1.',
                        'layers': [
                            {
                                'name': 'Capa 3 - Resolución de Ruta (Recursive Lookup)',
                                'name_en': 'Layer 3 - Route Resolution (Recursive Lookup)',
                                'detail': 'Destino original: 192.168.100.45 -> Ruta: 192.168.100.0/24 -> Siguiente Salto: 10.200.200.1. Resolución recursiva: 10.200.200.1 -> Ruta: 10.200.200.0/30 (OSPF) -> Siguiente Salto Físico: 10.10.12.2 -> Interfaz de salida: ge-0/0/1 (directamente conectada).',
                                'detail_en': 'Original destination: 192.168.100.45 -> Route: 192.168.100.0/24 -> Next-hop: 10.200.200.1. Recursive resolution: 10.200.200.1 -> Route: 10.200.200.0/30 (OSPF) -> Physical Next-hop: 10.10.12.2 -> Egress interface: ge-0/0/1 (directly connected).',
                                'checks': 'Verificar la ruta del siguiente salto con show route 10.200.200.1 en la CLI. Confirmar que la ruta de tránsito esté activa en la RIB.',
                                'checks_en': 'Verify the route of the next-hop with show route 10.200.200.1 in the CLI. Confirm that the transit route is active in the RIB.',
                                'anomalies': 'Fallo de resolución recursiva (FIB drop) si no existe ninguna ruta para la subred 10.200.200.0/30. Bucle recursivo (cuando una ruta estática apunta a sí misma o a través de otra que depende de ella).',
                                'anomalies_en': 'Recursive resolution failure (FIB drop) if no route exists for subnet 10.200.200.0/30. Recursive loop (when a static route points to itself or via another that depends on it).',
                                'packet_capture': {
                                    'notes': 'La resolución recursiva es interna del plano de control del router; no se refleja en paquetes de tránsito.',
                                    'notes_en': 'Recursive resolution is internal to the routers control plane; it is not reflected in transit packets.',
                                    'tcpdump_filter': 'No aplicable',
                                    'wireshark_display_filter': 'No aplicable'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 4: Encapsulación Ethernet de salida y resolución ARP',
                        'step_title_en': 'Step 4: Outbound Ethernet encapsulation and ARP resolution',
                        'device': 'Router de Agregación (Interfaz de Egreso: ge-0/0/1)',
                        'device_en': 'Aggregation Router (Egress Interface: ge-0/0/1)',
                        'action': 'El router prepara el paquete para ser enviado por la interfaz física ge-0/0/1 hacia el siguiente salto físico 10.10.12.2.',
                        'action_en': 'The router prepares the packet to be sent via the physical interface ge-0/0/1 towards the physical next-hop 10.10.12.2.',
                        'note': 'El router consulta su tabla ARP para obtener la dirección MAC correspondiente a 10.10.12.2. Reescribe las cabeceras MAC de la trama Ethernet.',
                        'note_en': 'The router queries its ARP table to obtain the MAC address corresponding to 10.10.12.2. It rewrites the MAC headers of the Ethernet frame.',
                        'layers': [
                            {
                                'name': 'Capa 2 - Enlace de Datos (Ethernet / ARP)',
                                'name_en': 'Layer 2 - Data Link (Ethernet / ARP)',
                                'detail': 'SrcMAC=MAC_Router_Egreso (00:50:56:88:99:bb), DstMAC=MAC_Siguiente_Salto (00:50:56:11:22:33, resuelto mediante ARP para IP 10.10.12.2), EtherType=0x0800.',
                                'detail_en': 'SrcMAC=MAC_Router_Egreso (00:50:56:88:99:bb), DstMAC=MAC_Siguiente_Salto (00:50:56:11:22:33, resolved via ARP for IP 10.10.12.2), EtherType=0x0800.',
                                'checks': 'Verificar la tabla ARP con show arp | match 10.10.12.2 o arp -a. Confirmar que la MAC esté en estado Resolved/Dynamic.',
                                'checks_en': 'Verify the ARP table with show arp | match 10.10.12.2 or arp -a. Confirm that the MAC is in Resolved/Dynamic state.',
                                'anomalies': 'Entrada ARP incompleta o inexistente (ARP timeout/no response), ARP spoofing (MAC incorrecta asociada al gateway), descarte por interfaz de salida inoperativa.',
                                'anomalies_en': 'Incomplete or non-existent ARP entry (ARP timeout/no response), ARP spoofing (wrong MAC associated with the gateway), discard due to down egress interface.',
                                'packet_capture': {
                                    'notes': 'Si falta el ARP, se observarán tramas ARP Request saliendo pero ningún Reply.',
                                    'notes_en': 'If ARP is missing, ARP Requests will be seen exiting but no Reply.',
                                    'tcpdump_filter': 'arp or (ip host 10.10.12.2)',
                                    'wireshark_display_filter': 'arp || ip.addr == 10.10.12.2'
                                }
                            }
                        ]
                    },
                    {
                        'step_title': 'Paso 5: Serialización de bits y transmisión por la interfaz de egreso ge-0/0/1',
                        'step_title_en': 'Step 5: Bit serialization and transmission on egress interface ge-0/0/1',
                        'device': 'Router de Agregación (Interfaz de Egreso: ge-0/0/1)',
                        'device_en': 'Aggregation Router (Egress Interface: ge-0/0/1)',
                        'action': 'La interfaz ge-0/0/1 serializa la trama Ethernet en una corriente de bits, la convierte a señales ópticas y la transmite a través de la fibra física.',
                        'action_en': 'Interface ge-0/0/1 serializes the Ethernet frame into a bitstream, converts it to optical signals, and transmits it through the physical fiber.',
                        'note': 'El paquete de tránsito ha cruzado con éxito el router usando enrutamiento estático y recursivo.',
                        'note_en': 'The transit packet has successfully crossed the router using static and recursive routing.',
                        'layers': [
                            {
                                'name': 'Capa 1 - Física (Óptica)',
                                'name_en': 'Layer 1 - Physical (Optical)',
                                'detail': 'Interfaz ge-0/0/1, puerto en estado Up/Up, velocidad 1000 Mbps Full-Duplex, potencia de salida óptica: -5.4 dBm.',
                                'detail_en': 'Interface ge-0/0/1, port status Up/Up, speed 1000 Mbps Full-Duplex, optical output power: -5.4 dBm.',
                                'checks': 'Monitorear contadores de la interfaz con show interfaces ge-0/0/1 para descartar incremento de error counters (input/output errors).',
                                'checks_en': 'Monitor interface counters with show interfaces ge-0/0/1 to rule out increasing error counters (input/output errors).',
                                'anomalies': 'Interfaz de egreso en shutdown o en error-disabled, atenuación excesiva de fibra, incremento de colisiones o errores físicos.',
                                'anomalies_en': 'Egress interface down or in error-disabled state, excessive fiber attenuation, increasing collisions or physical errors.',
                                'packet_capture': {
                                    'notes': 'Utilizar un tap óptico físico pasivo para capturar el tráfico en el hilo de fibra de egreso.',
                                    'notes_en': 'Use a physical passive optical tap to capture traffic on the egress fiber strand.',
                                    'tcpdump_filter': 'No aplicable a nivel óptico',
                                    'wireshark_display_filter': 'No aplicable a nivel óptico'
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

PACKET_WALKTHROUGHS['ip_trace'] = {
    'scenarios': [
        {
            'id': 'ip_trace_end_to_end',
            'name': 'Rastreo Completo de Paquete IP: Cliente LAN (A) -> Servidor DMZ (B) vía Core MPLS/BGP y Firewall NAT',
            'name_en': 'End-to-End IP Packet Tracing: LAN Client (A) -> DMZ Server (B) via Core MPLS/BGP and NAT Firewall',
            'description': 'Simulación interactiva del paso de un paquete IP desde un host cliente en una subred privada local hasta un servidor web público en una DMZ externa, evaluando cada capa del modelo OSI/TCP-IP en cada salto.',
            'description_en': 'Interactive simulation of an IP packet traversing from a client host in a local private subnet to a public web server in an external DMZ, evaluating each layer of the OSI/TCP-IP model at every hop.',
            'steps': [
                {
                    'step_title': '1. Host A de Origen (LAN) - Capas 1 a 4',
                    'step_title_en': '1. Source Host A (LAN) - Layers 1 to 4',
                    'device': 'Cliente LAN (A)',
                    'device_en': 'LAN Client (A)',
                    'action': 'Cliente genera solicitud HTTP GET hacia la IP del servidor 198.51.100.80',
                    'action_en': 'Client generates HTTP GET request towards server IP 198.51.100.80',
                    'note': 'El host origen determina que la IP destino está fuera de su subred (192.168.1.0/24) y decide enviar el paquete a su Default Gateway (192.168.1.1). Hace consulta en su tabla ARP para obtener la MAC del gateway.',
                    'note_en': "The source host determines that the destination IP lies outside its subnet (192.168.1.0/24) and decides to forward the packet to its Default Gateway (192.168.1.1). It performs an ARP table lookup to obtain the gateway's MAC address.",
                    'layers': [
                        {
                            'name': 'Capa 4 - Transporte (TCP)',
                            'name_en': 'Layer 4 - Transport (TCP)',
                            'detail': 'Puerto Origen: 51234, Puerto Destino: 80 (HTTP). Flags: [SYN]. Sequence Number: 0.',
                            'detail_en': 'Source Port: 51234, Destination Port: 80 (HTTP). Flags: [SYN]. Sequence Number: 0.',
                            'checks': 'TCP local socket en estado SYN_SENT.',
                            'checks_en': 'TCP local socket in SYN_SENT state.',
                            'anomalies': 'Socket local bloqueado, puertos efímeros agotados.',
                            'anomalies_en': "Local socket blocked, ephemeral ports exhausted."
                        },
                        {
                            'name': 'Capa 3 - Red (IP)',
                            'name_en': 'Layer 3 - Network (IP)',
                            'detail': 'IP Origen: 192.168.1.10, IP Destino: 198.51.100.80. TTL: 64. Protocolo: 6 (TCP).',
                            'detail_en': 'Source IP: 192.168.1.10, Destination IP: 198.51.100.80. TTL: 64. Protocolo: 6 (TCP).',
                            'checks': 'La IP destino no pertenece al prefijo local 192.168.1.0/24; se selecciona la ruta por defecto (0.0.0.0/0) apuntando al Gateway 192.168.1.1.',
                            'checks_en': "Destination IP does not match local prefix 192.168.1.0/24; default route (0.0.0.0/0) pointing to Gateway 192.168.1.1 is selected.",
                            'anomalies': 'Ruta por defecto ausente en la tabla de enrutamiento local del host origen.',
                            'anomalies_en': "Default route missing in the source host's local routing table."
                        },
                        {
                            'name': 'Capa 2 - Enlace de Datos (Ethernet II)',
                            'name_en': 'Layer 2 - Data Link (Ethernet II)',
                            'detail': 'MAC Origen: 00:50:56:c0:00:01 (Host A), MAC Destino: 00:50:56:c0:00:ff (Default Gateway). EtherType: 0x0800 (IPv4).',
                            'detail_en': 'Source MAC: 00:50:56:c0:00:01 (Host A), Destination MAC: 00:50:56:c0:00:ff (Default Gateway). EtherType: 0x0800 (IPv4).',
                            'checks': 'Búsqueda en la tabla ARP local. Si no existe, se envía una trama ARP Request broadcast y se recibe un ARP Reply unicast del Gateway.',
                            'checks_en': 'Local ARP table lookup. If missing, a broadcast ARP Request is sent and a unicast ARP Reply is received from the Gateway.',
                            'anomalies': 'Falla de resolución ARP por gateway apagado o IP duplicada. Inconsistencia de VLAN en el switch de acceso.',
                            'anomalies_en': 'ARP resolution failure due to gateway offline or IP conflict. VLAN mismatch on the access switch.'
                        },
                        {
                            'name': 'Capa 1 - Física',
                            'name_en': 'Layer 1 - Physical',
                            'detail': 'Interfaz: eth0 (1 Gbps Full-Duplex). Cable UTP Cat 6 conectado a puerto de switch Access.',
                            'detail_en': 'Interface: eth0 (1 Gbps Full-Duplex). UTP Cat 6 cable connected to Access switch port.',
                            'checks': 'Link status: UP. Sin errores de alineación ni colisiones en el puerto.',
                            'checks_en': 'Link status: UP. No alignment errors or collisions on the port.',
                            'anomalies': 'Cable defectuoso (Link flaps), mismatch de dúplex/velocidad, o puerto administrativo abajo.',
                            'anomalies_en': 'Faulty cable (Link flaps), duplex/speed mismatch, or port administratively down.'
                        }
                    ],
                    'packet_capture': {
                        'wireshark_display_filter': 'ip.src == 192.168.1.10 and ip.dst == 198.51.100.80 and tcp.flags.syn == 1',
                        'tcpdump_filter': 'tcp[tcpflags] & (tcp-syn) != 0 and src 192.168.1.10',
                        'notes': 'Captura en la tarjeta de red eth0 del host origen.',
                        'notes_en': "Capture on the source host's network interface card eth0."
                    }
                },
                {
                    'step_title': '2. Router de Acceso (Core Routing IGP) - Capas 1 a 3',
                    'step_title_en': '2. Access Router (Core Routing IGP) - Layers 1 to 3',
                    'device': 'Router de Acceso (PE1)',
                    'device_en': 'Access Router (PE1)',
                    'action': 'Router de acceso recibe la trama en GigabitEthernet0/0 y busca en la tabla de rutas',
                    'action_en': 'Access router receives the frame on GigabitEthernet0/0 and looks up the routing table',
                    'note': 'El router lee la MAC destino, verifica que es suya y remueve la cabecera Ethernet. Luego evalúa la IP destino en la tabla FIB buscando el prefijo coincidente más largo (Longest Prefix Match).',
                    'note_en': 'The router reads the destination MAC, verifies it matches its own, and strips the Ethernet header. It then evaluates the destination IP in the FIB table searching for the longest matching prefix (LPM).',
                    'layers': [
                        {
                            'name': 'Capa 3 - Red (FIB Lookup & LPM)',
                            'name_en': 'Layer 3 - Network (FIB Lookup & LPM)',
                            'detail': 'IP Origen: 192.168.1.10, IP Destino: 198.51.100.80. TTL decrementado a 63. Búsqueda en la FIB: match con el prefijo BGP aprendido 198.51.100.0/24 vía Next-Hop 10.10.12.2.',
                            'detail_en': 'Source IP: 192.168.1.10, Destination IP: 198.51.100.80. TTL decremented to 63. FIB lookup: matches BGP-learned prefix 198.51.100.0/24 via Next-Hop 10.10.12.2.',
                            'checks': 'Verificar que la ruta hacia el Next-Hop esté activa en la RIB y resuelva a una interfaz física saliente.',
                            'checks_en': 'Verify that the route to Next-Hop is active in the RIB and resolves to an active physical egress interface.',
                            'anomalies': 'Ruta ausente hacia el destino (caída en el IGP/BGP), next-hop inalcanzable, o loop de enrutamiento recursivo.',
                            'anomalies_en': "Route to destination missing (IGP/BGP flap), unreachable next-hop, or recursive routing loop."
                        },
                        {
                            'name': 'Capa 2 - Encapsulación de Tránsito',
                            'name_en': 'Layer 2 - Transit Encapsulation',
                            'detail': 'MAC Origen: MAC del router saliente, MAC Destino: MAC del router del siguiente salto. Se prepara para inyectar en el core de transporte MPLS.',
                            'detail_en': 'Source MAC: Egress router MAC, Destination MAC: Next-hop router MAC. Preparing to inject into the MPLS transport core.',
                            'checks': 'Resolución ARP/Neighbor para el siguiente salto 10.10.12.2.',
                            'checks_en': 'ARP/Neighbor resolution for the next-hop 10.10.12.2.',
                            'anomalies': 'Falla de ARP con el router vecino de tránsito.',
                            'anomalies_en': 'ARP failure with the transit neighbor router.'
                        }
                    ],
                    'packet_capture': {
                        'wireshark_display_filter': 'ip.addr == 198.51.100.80 and tcp.port == 80',
                        'tcpdump_filter': 'tcp port 80 and host 198.51.100.80',
                        'notes': 'Captura en la interfaz de tránsito Gi0/1 del Router.',
                        'notes_en': "Capture on the Router's Gi0/1 transit interface."
                    }
                },
                {
                    'step_title': '3. Core MPLS / MP-BGP PE - Capas 1 a 3 (MPLS VPN)',
                    'step_title_en': '3. Core MPLS / MP-BGP PE - Layers 1 to 3 (MPLS VPN)',
                    'device': 'Router de Core / Provider Edge',
                    'device_en': 'Transit / Provider Edge Router',
                    'action': 'Conmutación de etiquetas MPLS a través del Core de red',
                    'action_en': 'MPLS label switching through the network Core',
                    'note': 'El PE de origen encapsula el paquete IP con dos etiquetas MPLS: una etiqueta externa de transporte (LDP o SR) para guiar el paquete al PE remoto, y una etiqueta interna de servicio VPNv4 para identificar la VRF del cliente en el PE destino.',
                    'note_en': "The ingress PE encapsulats the IP packet with two MPLS labels: an outer transport label (LDP or SR) to guide the packet to the remote PE, and an inner VPNv4 service label to identify the customer's VRF on the egress PE.",
                    'layers': [
                        {
                            'name': 'Capa 3 - MPLS VPN Label Swap/Push',
                            'name_en': 'Layer 3 - MPLS VPN Label Swap/Push',
                            'detail': 'Etiqueta Externa (Transporte): 24005 (distribuida por LDP hacia el PE destino). Etiqueta Interna (Servicio/VPN): 16012 (distribuida por MP-BGP para identificar la VRF de destino). TTL IP original decrementado a 62 (o propagado al MPLS TTL).',
                            'detail_en': 'Outer Label (Transport): 24005 (distributed by LDP to the egress PE). Inner Label (Service/VPN): 16012 (distributed by MP-BGP to identify the destination VRF). Original IP TTL decremented to 62 (or propagated to MPLS TTL).',
                            'checks': 'Verificar la base de datos LFIB (Label Forwarding Information Base) del core MPLS.',
                            'checks_en': 'Verify the LFIB (Label Forwarding Information Base) database on the MPLS core.',
                            'anomalies': 'Inconsistencia de etiquetas MPLS (Label Mismatch), desincronización de base de datos LDP, o caída de la sesión MP-BGP entre los PEs.',
                            'anomalies_en': 'MPLS Label Mismatch, LDP database desynchronization, or MP-BGP session down between PEs.'
                        },
                        {
                            'name': 'Capa 2 - Enlace (Core Transport)',
                            'name_en': 'Layer 2 - Link (Core Transport)',
                            'detail': 'MAC Origen: MAC de interfaz Core del PE local, MAC Destino: MAC del Router P de tránsito. EtherType: 0x8847 (MPLS Unicast).',
                            'detail_en': 'Source MAC: Core egress interface MAC, Destination MAC: Transit P Router MAC. EtherType: 0x8847 (MPLS Unicast).',
                            'checks': 'Validación de la MTU en el Core (debe soportar al menos 1508 bytes para las cabeceras MPLS adicionales).',
                            'checks_en': 'Verify Core MTU (must support at least 1508 bytes to account for additional MPLS labels).',
                            'anomalies': 'Descarte silencioso debido a MTU baja en los enlaces core (paquetes con DF=1 caen si no cabe la pila de etiquetas).',
                            'anomalies_en': 'Silent drop due to low MTU on core links (DF=1 packets are dropped if they do not fit the label stack).'
                        }
                    ],
                    'packet_capture': {
                        'wireshark_display_filter': 'mpls.label == 24005 or mpls.label == 16012',
                        'tcpdump_filter': 'mpls',
                        'notes': 'Captura en los enlaces de core MPLS.',
                        'notes_en': 'Capture on the MPLS core transit links.'
                    }
                },
                {
                    'step_title': '4. Firewall Perimetral (NAT & Seguridad) - Capas 1 a 4',
                    'step_title_en': '4. Perimeter Firewall (NAT & Security) - Layers 1 to 4',
                    'device': 'Firewall de Borde',
                    'device_en': 'Edge Firewall',
                    'action': 'Firewall recibe el paquete de un PE del Core, aplica Source NAT e inspecciona la política de seguridad',
                    'action_en': 'Firewall receives the decapsulated packet from the Core, applies Source NAT and inspects security policies',
                    'note': 'El firewall remueve la encapsulación del Core. Evalúa la política de seguridad IP origen -> IP destino. Si se permite, busca reglas de NAT de salida. Traduce la IP origen privada a una IP pública del pool, y crea una sesión en su tabla de conntrack.',
                    'note_en': 'The firewall strips the Core encapsulation. It evaluates the security policy from source IP -> destination IP. If allowed, it checks outbound NAT rules, translates the private source IP to a public pool IP, and creates a session in its conntrack table.',
                    'layers': [
                        {
                            'name': 'Capa 4 - Inspección de Estado de Conexión (Conntrack)',
                            'name_en': 'Layer 4 - Stateful Connection Inspection (Conntrack)',
                            'detail': 'Inspección del TCP [SYN]. Se crea sesión en la tabla con estado SYN_SENT. Dirección original: 192.168.1.10:51234 -> 198.51.100.80:80. Dirección traducida: 203.0.113.15:10432 -> 198.51.100.80:80.',
                            'detail_en': 'Inspection of TCP [SYN]. A session is created in the conntrack table in SYN_SENT state. Original direction: 192.168.1.10:51234 -> 198.51.100.80:80. Translated direction: 203.0.113.15:10432 -> 198.51.100.80:80.',
                            'checks': 'Monitorear la tabla de sesiones activa del firewall y verificar que la política de seguridad permita la zona de confianza a zona de no confianza.',
                            'checks_en': 'Monitor active session table on the firewall and verify security policy permits trust-to-untrust zone traffic.',
                            'anomalies': 'Sesión descartada por política de firewall restrictiva (Deny/Drop), agotamiento de puertos en el pool de NAT (Port Exhaustion), o descarte por anomalía TCP (mismatch de número de secuencia).',
                            'anomalies_en': 'Session dropped by restrictive firewall policy (Deny/Drop), NAT pool port exhaustion, or TCP anomaly drop (sequence number mismatch).'
                        },
                        {
                            'name': 'Capa 3 - Traducción de Red (Source NAT / PAT)',
                            'name_en': 'Layer 3 - Network Address Translation (Source NAT / PAT)',
                            'detail': 'Cabecera IP reescrita. Nueva IP Origen: 203.0.113.15 (IP pública), IP Destino permanece: 198.51.100.80. TTL decrementado a 61. Recalculación del Checksum IP/TCP.',
                            'detail_en': 'IP header rewritten. New Source IP: 203.0.113.15 (public IP), Destination IP remains: 198.51.100.80. TTL decremented to 61. IP/TCP Checksum recalculated.',
                            'checks': 'Validar que las rutas de retorno existan para el bloque de NAT público (203.0.113.15) en el firewall y en los proveedores de tránsito.',
                            'checks_en': 'Validate that return routes exist for the public NAT block (203.0.113.15) on the firewall and transit providers.',
                            'anomalies': 'Falla de enrutamiento de retorno: el ISP no sabe cómo llegar a la IP pública traducida del NAT.',
                            'anomalies_en': 'Return routing failure: ISP does not know how to route to the translated public NAT IP.'
                        }
                    ],
                    'packet_capture': {
                        'wireshark_display_filter': 'ip.src == 203.0.113.15 and ip.dst == 198.51.100.80',
                        'tcpdump_filter': 'src host 203.0.113.15 and dst host 198.51.100.80',
                        'notes': 'Captura en la interfaz externa (WAN/DMZ) del Firewall.',
                        'notes_en': 'Capture on the external WAN/DMZ interface of the Firewall.'
                    }
                },
                {
                    'step_title': '5. Servidor Destino B (DMZ) - Capas 1 a 7',
                    'step_title_en': '5. Destination Server B (DMZ) - Layers 1 to 7',
                    'device': 'Servidor Destino (B)',
                    'device_en': 'Destination Server (B)',
                    'action': 'Servidor recibe el paquete IP traducido, procesa en el socket TCP y genera respuesta',
                    'action_en': 'Server receives the NATed IP packet, processes it in the TCP socket, and generates a response',
                    'note': 'El servidor procesa el paquete hasta la Capa de aplicación. Al ver que es un SYN en el puerto 80, y el puerto está en escucha, genera una respuesta SYN-ACK. Esta respuesta recorrerá el camino inverso de forma simétrica.',
                    'note_en': 'The server decapsulates the packet up to the Application Layer. Seeing a TCP SYN on port 80, and because the port is listening, it generates a SYN-ACK reply. This reply will traverse the path back symmetrically.',
                    'layers': [
                        {
                            'name': 'Capa 7/4 - Aplicación y Socket TCP',
                            'name_en': 'Layer 7/4 - Application & TCP Socket',
                            'detail': 'El servidor lee la cabecera TCP en el puerto 80. Servicio HTTP (nginx/apache) procesa la solicitud. Estado del socket local: LISTEN -> SYN_RCVD.',
                            'detail_en': 'Server reads the TCP header on port 80. HTTP service (nginx/apache) processes the request. Local socket state: LISTEN -> SYN_RCVD.',
                            'checks': 'Verificar sockets locales en escucha usando comandos ss o netstat en el servidor.',
                            'checks_en': 'Verify local listening sockets using ss or netstat commands on the destination server.',
                            'anomalies': 'El servicio web en el puerto 80 está caído, o el servidor está en su capacidad máxima de conexiones (TCP SYN Flood o backlog de sockets lleno).',
                            'anomalies_en': 'Web service on port 80 is down, or server socket backlog is full (TCP SYN Flood or high load).'
                        },
                        {
                            'name': 'Capa 3 - Generación de Respuesta (IP/Retorno)',
                            'name_en': 'Layer 3 - Response Generation (IP/Return Path)',
                            'detail': 'Se genera el paquete de retorno. IP Origen: 198.51.100.80, IP Destino: 203.0.113.15 (la IP del NAT del firewall). TTL: 64. Protocolo: TCP. Flags: [SYN, ACK].',
                            'detail_en': 'Return packet generated. Source IP: 198.51.100.80, Destination IP: 203.0.113.15 (the translated NAT IP). TTL: 64. Protocolo: TCP. Flags: [SYN, ACK].',
                            'checks': 'El servidor rutea el paquete de respuesta a través de su gateway por defecto en la DMZ.',
                            'checks_en': 'The server routes the response packet through its default gateway in the DMZ segment.',
                            'anomalies': 'Gateway de la DMZ inalcanzable, o ruta de retorno mal configurada en el servidor destino.',
                            'anomalies_en': 'DMZ Gateway unreachable, or misconfigured return route on the destination server.'
                        }
                    ],
                    'packet_capture': {
                        'wireshark_display_filter': 'ip.src == 198.51.100.80 and ip.dst == 203.0.113.15 and tcp.flags == 0x012',
                        'tcpdump_filter': 'src host 198.51.100.80 and dst host 203.0.113.15 and tcp[tcpflags] & (tcp-syn|tcp-ack) == 0x12',
                        'notes': 'Captura en la interfaz de red del servidor destino.',
                        'notes_en': 'Capture on the network interface card of the destination server.'
                    }
                }
            ]
        }
    ]
}

WALKTHROUGH_ALIASES = {
    'ip_trace': 'ip_trace_end_to_end',
    'spanning_tree': 'spanning_tree',
    'ipv6': 'ipv6_ndp',
    'netflow': 'netflow',
    'nat': 'nat',
    'nat_config': 'nat',
    'static': 'static_routing',
    'static_config': 'static_routing',
}
