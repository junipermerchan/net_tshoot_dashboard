"""
Parches científicos y mejoras granulares para la base de conocimiento.

Este módulo implementa el Método Científico en el troubleshooting de red:
- Hipótesis falsificables
- Verificación sistemática con evidencia esperada e invalidante
- Advertencias de sesgo cognitivo (para evitar confirmation bias)
- Bases científicas documentadas (RFCs, papers, mejores prácticas)
- Nivel de confianza y referencias bibliográficas

Aplicación:
    engine.py fusiona estos campos con los pasos existentes de knowledge_base.py.
"""

from typing import Dict, Any

ScientificOverride = Dict[str, Any]

SCIENTIFIC_OVERRIDES: Dict[str, ScientificOverride] = {
    # ── MPLS ──────────────────────────────────────────────────────────
    "mpls.mpls_start": {
        "hypothesis": (
            "La falla observada es causada por una discontinuidad en el plano de control MPLS "
            "(IGP no sincronizado, sesión LDP/RSVP caída, o transport-address inalcanzable) "
            "que impide la correcta programación de la LFIB, resultando en blackholing o "
            "descartes silenciosos en el data plane."
        ),
        "verification_steps": [
            "1. Verificar salud general del router (CPU, memoria, logs recientes) para descartar causas externas.",
            "2. Listar interfaces MPLS y confirmar estado administrativo y operacional Up/Up.",
            "3. Verificar adyacencias LDP (UDP 646) y RSVP (IP 46) en estado Operational/Established.",
            "4. Confirmar alcanzabilidad IP (preferiblemente /32 loopback) a la transport-address de los peers.",
            "5. Revisar contadores de error y descartes en interfaces físicas para detectar MTU insuficiente.",
        ],
        "expected_evidence": {
            "confirming": [
                "CPU < 80% y memoria disponible > 20%. Sin logs de errores de hardware o kernel.",
                "Todas las interfaces MPLS en Up/Up con family mpls / mpls ip activo.",
                "LDP neighbors en Operational; RSVP neighbors en Hello/Keepalive OK.",
                "Ruta IGP activa (/32) hacia la transport-address del peer.",
                "Sin incremento de contadores de input/output errors o MTU exceeded.",
            ],
            "invalidating": [
                "CPU o memoria críticos (>95%) que indiquen proceso de control plane saturado.",
                "Interfaces MPLS en Down/Down o sin 'family mpls' / 'mpls ip'.",
                "LDP sessions en NonExistent, Initialized, o OpenSent (falla de transport-address o ACL).",
                "Ruta hacia transport-address ausente, estática solitaria, o apuntando a interfaz incorrecta.",
                "Contadores de giant frames o MTU errors creciendo (indica overhead de labels no soportado).",
            ],
        },
        "scientific_basis": (
            "Según RFC 5036 (LDP Specification), una sesión LDP requiere alcanzabilidad IP a la transport-address. "
            "RFC 3209 (RSVP-TE) especifica que los mensajes Path/Resv dependen de la reachability IGP y de la "
            "capacidad de reserva de recursos. La desincronización IGP-MPLS es identificada en estudios de campo "
            "como la causa raíz del ~40% de los casos de blackholing MPLS (Juniper Networks, 'Troubleshooting MPLS "
            "Networks', 2022; Cisco Live BRKRST-3041). El overhead de labels MPLS (4 bytes por etiqueta) puede "
            "provocar descartes silenciosos si la MTU física no se incrementa adecuadamente (RFC 3032)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que un ping exitoso entre PEs implica forwarding MPLS correcto. El ping usa la tabla IP global, no la LFIB.",
            "NO descarte la hipótesis de MTU solo porque los vecinos LDP están Up. Los paquetes pequeños (Hellos) pasan, pero los grandes (tráfico de usuario) pueden droppear.",
            "Verifique la dirección del tráfico: un LSP es unidireccional. Un fallo puede ser asimétrico (Ingress OK, Egress falla).",
        ],
        "references": [
            "RFC 5036: LDP Specification",
            "RFC 3209: RSVP-TE: Extensions to RSVP for LSP Tunnels",
            "RFC 3032: MPLS Label Stack Encoding",
            "Juniper Networks: Troubleshooting MPLS Networks (2022)",
            "Cisco Live BRKRST-3041: Advanced MPLS Troubleshooting",
        ],
        "fix": (
            "1. Habilitar 'family mpls' (JunOS) o 'mpls ip' (Cisco) en todas las interfaces troncales.\n"
            "2. Verificar y corregir la ruta IGP (/32 loopback) hacia la transport-address del peer LDP.\n"
            "3. Si hay MTU issues: aumentar MTU a 9000 en interfaces troncales o configurar 'mpls mtu' adecuada.\n"
            "4. Revisar ACLs/firewall filters que bloqueen UDP 646 (LDP) o IP 46 (RSVP).\n"
            "5. Si RSVP-TE: verificar que la TED tenga ancho de banda suficiente y ajustar reservas."
        ),
    },
    "mpls.mpls_ctrl_sig": {
        "hypothesis": (
            "El protocolo de señalización (LDP o RSVP-TE) no establece o mantiene la sesión debido a "
            "fallas en la transport-address, desajuste de timers, ACLs/firewall filters, o falta de "
            "recursos (ancho de banda en RSVP-TE)."
        ),
        "verification_steps": [
            "1. Verificar que la transport-address (LSR-id/router-id) esté anunciada en IGP y sea alcanzable.",
            "2. Comparar timers Hello/Keepalive y parámetros de sesión entre peers.",
            "3. Inspeccionar ACLs, firewall filters, o security policies que bloqueen UDP 646 (LDP) o IP 46 (RSVP).",
            "4. Para RSVP-TE: verificar que el ancho de banda solicitado no exceda la capacidad del enlace (TED).",
            "5. Capturar tráfico de control en la interfaz física para confirmar intercambio de mensajes.",
        ],
        "expected_evidence": {
            "confirming": [
                "'show route <transport-address>' devuelve ruta activa vía IGP (OSPF/IS-IS).",
                "Timers Hello/Keepalive coinciden en ambos extremos de la sesión.",
                "Sin entradas de ACL/firewall descartando paquetes LDP/RSVP en logs o contadores.",
                "RSVP session en Up con bandwidth reservado correctamente.",
                "Captura de paquetes muestra intercambio de LDP Hellos (UDP 646) o RSVP Path/Resv.",
            ],
            "invalidating": [
                "Ruta hacia transport-address ausente, inactiva, o con Next-Hop incorrecto.",
                "Mismatch de timers: un peer envía Hellos cada 5s y el otro espera cada 15s (Hold time expira).",
                "Logs de firewall/ACL indican descartes explícitos de UDP 646 o IP 46.",
                "RSVP muestra 'Reservation Error' o 'Bad Tunnel' por insuficiencia de bandwidth.",
                "Captura de paquetes NO muestra tráfico LDP/RSVP saliente o entrante (indica configuración faltante en interfaz).",
            ],
        },
        "scientific_basis": (
            "RFC 5036 define el mecanismo de descubrimiento de vecinos LDP vía UDP 646 y el establecimiento de "
            "sesiones vía TCP 646. Cualquier interrupción en la conectividad IP a la transport-address rompe la máquina "
            "de estados. RSVP-TE (RFC 3209) depende de la base de datos TED (Traffic Engineering Database) para el "
            "cálculo de CSPF; si el ancho de banda disponible es menor al solicitado, la señalización falla con "
            "'Reservation Error'."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el peer es alcanzable por IP, la sesión LDP debe estar Up. Verifique explícitamente la sesión TCP 646.",
            "Un 'show logging | include LDP' vacío NO significa que todo está bien; puede significar que el logging está deshabilitado o filtrado.",
            "En RSVP-TE, descarte la hipótesis de ancho de banda solo si ha verificado la TED con 'show mpls traffic-eng topology'.",
        ],
        "references": [
            "RFC 5036: LDP Specification",
            "RFC 3209: RSVP-TE: Extensions to RSVP for LSP Tunnels",
            "RFC 4202: Routing Extensions for Traffic Engineering",
        ],
        "fix": (
            "1. Corregir la ruta IGP hacia la transport-address (asegurar /32 loopback en OSPF/IS-IS).\n"
            "2. Sincronizar timers Hello/Keepalive en ambos peers (ej. 5s/15s).\n"
            "3. Eliminar o ajustar ACLs/firewall que bloqueen UDP 646 o IP 46.\n"
            "4. Para RSVP-TE: aumentar ancho de banda en la TED o reducir la reserva solicitada.\n"
            "5. Capturar tráfico en la interfaz para confirmar que los paquetes de control llegan y salen."
        ),
    },
    "mpls.mpls_ctrl_down": {
        "hypothesis": (
            "Los vecinos LDP/RSVP están DOWN porque la transport-address no es alcanzable vía IGP, "
            "la interfaz física no tiene MPLS habilitado, o existe un filtro de seguridad/ACL bloqueando "
            "el tráfico de señalización."
        ),
        "verification_steps": [
            "1. Ejecutar 'show route <transport-address>' y confirmar Next-Hop activo y correcto.",
            "2. Verificar configuración de interfaz: 'family mpls' (JunOS) o 'mpls ip' (Cisco) activo.",
            "3. Revisar ACLs, prefix-lists, o firewall filters aplicados a la interfaz o al control-plane host.",
            "4. Validar MTU de la interfaz: los Hellos de IS-IS y LDP pueden requerir MTU > 1492 bytes.",
            "5. Verificar que no haya duplicado de Router-ID o LSR-ID en la red (causa loop o rechazo de sesión).",
        ],
        "expected_evidence": {
            "confirming": [
                "Ruta IGP activa y preferida hacia la transport-address del peer.",
                "Configuración de interfaz confirma MPLS habilitado en la subinterfaz lógica y física.",
                "Sin reglas de ACL/firewall que matcheen puerto 646 (LDP) o protocolo 46 (RSVP).",
                "MTU de interfaz >= 1504 bytes (para soportar al menos 1 label + overhead Ethernet).",
                "Router-ID único en el dominio MPLS; sin mensajes de conflicto en logs.",
            ],
            "invalidating": [
                "Ruta hacia transport-address inexistente o con Next-Hop por interfaz down/administratively down.",
                "Interfaz configurada sin 'family mpls' / 'mpls ip'; o en estado passive.",
                "ACLs explícitamente bloqueando tráfico de control MPLS (ej. 'deny udp any any eq 646').",
                "MTU <= 1500 en enlaces con stacks de múltiples labels (VPN + Transport + Entropy), causando fragmentación o descarte.",
                "Logs indicando duplicado de Router-ID o LSR-ID, causando rechazo de adyacencia.",
            ],
        },
        "scientific_basis": (
            "La alcanzabilidad IP es un requisito necesario pero no suficiente para MPLS. Según RFC 5036, la transport-address "
            "debe ser anunciada por IGP. La habilitación de MPLS en la interfaz es un requisito local. Los filtros de seguridad "
            "son una causa frecuente de fallas 'silenciosas' porque los protocolos de señalización no generan mensajes de error "
            "visibles en el plano de datos (a diferencia de ICMP). La MTU insuficiente es particularmente insidiosa porque "
            "los paquetes de control (Hellos) son pequeños y pasan, mientras que los paquetes de datos se descartan (RFC 3032)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO confíe ciegamente en el output de 'show ip route'; verifique que la ruta sea IGP y no una estática con Next-Hop inalcanzable.",
            "Una interfaz en 'Up/Up' a nivel físico NO garantiza que MPLS esté habilitado en la subinterfaz lógica.",
            "Descarte la hipótesis de duplicado de Router-ID solo si ha verificado todos los equipos del área; use 'show ldp neighbor extensive' para ver el ID del peer.",
        ],
        "references": [
            "RFC 5036: LDP Specification",
            "RFC 3032: MPLS Label Stack Encoding",
            "RFC 4202: Routing Extensions for Traffic Engineering",
        ],
        "fix": (
            "1. Asegurar que la interfaz tenga 'family mpls' (JunOS) o 'mpls ip' (Cisco) activo.\n"
            "2. Corregir la ruta IGP hacia la transport-address (asegurar /32 loopback).\n"
            "3. Eliminar ACLs/firewall que bloqueen UDP 646 (LDP) o IP 46 (RSVP).\n"
            "4. Aumentar MTU de la interfaz a al menos 9000 bytes para soportar stacks de labels múltiples.\n"
            "5. Verificar que no haya duplicado de Router-ID/LSR-ID en la red."
        ),
    },
    "mpls.mpls_ctrl_nolabel": {
        "hypothesis": (
            "Los vecinos LDP/RSVP están UP pero no intercambian labels (bindings) porque la FEC no existe en la tabla IGP, "
            "existe una policy de import/export filtrando la FEC, o el rango de labels locales se ha agotado."
        ),
        "verification_steps": [
            "1. Verificar que la FEC (prefijo destino) exista en la tabla de rutas IGP activa.",
            "2. Revisar 'show ldp database' / 'show mpls ldp bindings' para confirmar presencia/ausencia de binding.",
            "3. Inspeccionar policies, route-maps, o prefix-lists que filtren el anuncio o recepción de labels.",
            "4. Verificar el rango de labels locales ('show mpls label range') para descartar agotamiento.",
            "5. Confirmar que la FEC no esté en una VRF sin redistribución hacia MP-BGP o LDP."
        ],
        "expected_evidence": {
            "confirming": [
                "La FEC aparece activa en la tabla de rutas IGP (OSPF/IS-IS) con métrica válida.",
                "LDP database / MPLS bindings muestra entradas locales y remotas para la FEC.",
                "Policies de LDP permiten explícitamente el prefijo o usan 'accept all' por defecto.",
                "Rango de labels local no agotado; capacidad de asignación disponible.",
                "En escenarios VRF, la redistribución entre el protocolo PE-CE y MP-BGP/LDP está configurada.",
            ],
            "invalidating": [
                "La FEC no aparece en la tabla IGP (posible filtro de IGP o ruta no inyectada).",
                "LDP database vacío o con 'No remote label' para la FEC de interés.",
                "Policy de LDP con regla explícita de 'reject' o 'deny' para el prefijo.",
                "Rango de labels local agotado ('Label space exhausted' en logs).",
                "VRF configurada pero sin redistribución hacia el proceso de señalización MPLS.",
            ],
        },
        "scientific_basis": (
            "LDP solo genera bindings para rutas activas en la RIB (RFC 5036, Sección 2.4). Si una FEC es filtrada por una "
            "policy de exportación, el router local no anuncia el binding; si es filtrada por importación, no acepta el binding "
            "remoto. El agotamiento del rango de labels (Label Space) es un evento de escala documentado en redes grandes "
            "(Cisco DocWiki: 'MPLS Label Space Exhaustion')."
        ),
        "confidence_level": "Media",
        "bias_warnings": [
            "NO asuma que porque la ruta existe en la RIB global, LDP la está anunciando. Verifique 'show ldp database extensive'.",
            "Un binding local existente NO garantiza un binding remoto. Verifique ambos lados del pseudowire/LSP.",
            "Descarte la hipótesis de agotamiento de labels solo si ha verificado el rango y el conteo de entradas activas.",
        ],
        "references": [
            "RFC 5036: LDP Specification",
            "Cisco DocWiki: MPLS Label Space Exhaustion",
            "Juniper Networks: LDP Policy and Filtering Best Practices",
        ],
        "fix": (
            "1. Verificar que la FEC destino esté activa en la RIB/VRF y no sea filtrada por IGP.\n"
            "2. Revisar 'show ldp database'/'show mpls ldp bindings' para confirmar binding local/remoto; si falta, forzar re-anuncio o reiniciar LDP.\n"
            "3. Ajustar policies de import/export de LDP para permitir explícitamente la FEC (aceptar prefijo o eliminar regla de reject).\n"
            "4. Ampliar el rango de labels locales si está agotado ('mpls label range') y verificar capacidad de hardware.\n"
            "5. En escenarios VRF, confirmar redistribución del protocolo PE-CE hacia MP-BGP/LDP.\n"
            "6. Validar que la FEC tenga binding remoto en ambos PEs antes de probar tráfico.\n"
        ),
    },
    # ── L3VPN ─────────────────────────────────────────────────────────
    "l3vpn.l3vpn_start": {
        "hypothesis": (
            "La falla de conectividad del cliente en L3VPN es causada por una ruptura en la cadena de señalización end-to-end: "
            "falla en el core MPLS (LSP no funcional), sesión MP-BGP VPNv4 caída, o desajuste de Route Targets (RT) "
            "entre PEs de origen y destino."
        ),
        "verification_steps": [
            "1. Validar que el LSP MPLS entre loopbacks de PE esté funcional (ping MPLS o traceroute MPLS).",
            "2. Verificar que la sesión MP-BGP VPNv4 (AFI/SAFI 1/128) esté en estado Established.",
            "3. Comprobar que el Route Distinguisher (RD) y los Route Targets (RT import/export) coincidan exactamente.",
            "4. Verificar que el prefijo del cliente esté presente en la VRF local (tabla de rutas PE-CE) y en la VPNv4 RIB.",
            "5. Revisar que el Next-Hop de las rutas VPNv4 sea alcanzable y resoluble vía IGP/MPLS.",
        ],
        "expected_evidence": {
            "confirming": [
                "Ping MPLS exitoso entre loopbacks de PE (valida LSP end-to-end).",
                "Sesión MP-BGP VPNv4 en Established; sin mensajes de NOTIFICATION recientes.",
                "Export-RT en PE origen == Import-RT en PE destino (y viceversa para tráfico bidireccional).",
                "Prefijo del cliente aparece en 'show route table <vrf>' local y en 'show route table bgp.l3vpn.0' (JunOS) / 'show bgp vpnv4 unicast' (Cisco).",
                "Next-Hop de rutas VPNv4 alcanzable vía IGP y resuelto a label MPLS en la LFIB.",
            ],
            "invalidating": [
                "Ping MPLS falla o traceroute MPLS se detiene en un salto intermedio (LSP roto).",
                "Sesión MP-BGP en Idle/Active o con NOTIFICATION por AS mismatch, capability mismatch, o policy reject.",
                "Mismatch de RT: export-RT de origen no coincide con import-RT de destino (rutas descartadas silenciosamente).",
                "Prefijo del cliente ausente en VRF local (falla PE-CE) o en VPNv4 RIB (falla redistribución a BGP).",
                "Next-Hop de rutas VPNv4 no resoluble o apuntando a una interfaz sin MPLS (causa 'unreachable next-hop').",
            ],
        },
        "scientific_basis": (
            "RFC 4364 (BGP/MPLS IP VPNs) define que el plano de control VPNv4 requiere MP-BGP con comunidades extendidas (RT). "
            "Un mismatch de RT es un error de configuración silencioso: las rutas se reciben pero se descartan antes de ser importadas a la VRF. "
            "El Next-Hop de una ruta VPNv4 debe ser alcanzable vía IGP y resuelto a un label MPLS; si no, el paquete no puede ser encapsulado "
            "en el core (RFC 3032, RFC 4271)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el ping entre PEs funciona, el LSP MPLS está OK. Use ping MPLS explícito.",
            "Una sesión MP-BGP Established NO garantiza que las rutas estén siendo importadas. Verifique la VRF con 'show route table <vrf>'.",
            "Descarte la hipótesis de RT mismatch solo si ha verificado TODOS los RTs (incluyendo los de VPNs de-mgmt si aplica).",
        ],
        "references": [
            "RFC 4364: BGP/MPLS IP Virtual Private Networks (VPNs)",
            "RFC 4271: A Border Gateway Protocol 4 (BGP-4)",
            "Cisco Live BRKRST-3340: Advanced L3VPN Troubleshooting",
        ],
        "fix": (
            "1. Validar LSP MPLS entre PEs con ping MPLS o traceroute MPLS. Corregir LDP/RSVP si está caído.\n"
            "2. Verificar que MP-BGP VPNv4 esté en Established; corregir AS mismatch o MD5/TCP 179 si aplica.\n"
            "3. Asegurar que export-RT en origen == import-RT en destino (y viceversa).\n"
            "4. Verificar que el prefijo del cliente esté en la VRF local y en VPNv4 RIB.\n"
            "5. Confirmar que el Next-Hop de VPNv4 sea resoluble vía IGP y tenga label MPLS en LFIB."
        ),
    },
    # ── EVPN ──────────────────────────────────────────────────────────
    "evpn.evpn_start": {
        "hypothesis": (
            "La falla en EVPN (MAC/IP no aprendidas o tráfico BUM no replicado) es causada por una falla en el underlay IP/MPLS, "
            "una adyacencia BGP EVPN no establecida, o un error en la configuración de la MAC-VRF/bridge domain."
        ),
        "verification_steps": [
            "1. Validar underlay IP/MPLS: confirmar conectividad entre loopbacks de VTEPs/PEs.",
            "2. Verificar sesión BGP EVPN (AFI/SAFI 25/70) en estado Established.",
            "3. Confirmar recepción de rutas EVPN Tipo 2 (MAC/IP) en el PE/VTEP remoto.",
            "4. Verificar que la MAC-VRF/bridge domain esté configurada con el RD/RT correctos y asociada a las VLANs locales.",
            "5. En escenarios multihomed (MH): verificar el estado de DF Election y ESI consistency.",
        ],
        "expected_evidence": {
            "confirming": [
                "Underlay IP/MPLS funcional: ping entre loopbacks de VTEPs con MTU ajustado OK.",
                "BGP EVPN session Established; comunidades extendidas permitidas en ambos sentidos.",
                "Rutas EVPN Tipo 2 presentes en 'show bgp evpn' / 'show route table evpn.evpn.0'.",
                "MAC-VRF configurada con RD/RT correctos; bridge domain asociado a VLANs locales.",
                "En MH: DF election concluido con un DF activo; ESI consistente en ambos PEs.",
            ],
            "invalidating": [
                "Underlay falla: ping entre loopbacks descarta o traceroute se interrumpe.",
                "BGP EVPN en Idle/Active o filtrado por policy de comunidades extendidas.",
                "Sin rutas Tipo 2 recibidas (falla de anuncio o importación de RT).",
                "MAC-VRF con RD duplicado o RT mismatch (rutas descartadas silenciosamente).",
                "En MH: conflictos de ESI o DF election no concluido (loop o split-brain).",
            ],
        },
        "scientific_basis": (
            "EVPN (RFC 7432) utiliza BGP como plano de control para distribuir MACs e IPs. La familia de direcciones EVPN (AFI 25, SAFI 70) "
            "depende de un underlay funcional (IP o MPLS) y de la correcta propagación de comunidades extendidas (RT). Las rutas Tipo 2 (MAC/IP) "
            "son fundamentales para el aprendizaje de MACs remotas. En escenarios multihomed, el Designated Forwarder (DF) election "
            "(RFC 7432, Sección 8.5) previene loops; un DF conflictivo causa duplicación o descarte de tráfico BUM."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque BGP IPv4 está Up, BGP EVPN también lo está. Verifique explícitamente la familia EVPN.",
            "Un 'show mac-table' vacío puede deberse a falla de aprendizaje local, no a falla EVPN remota. Verifique ambos lados.",
            "Descarte la hipótesis de underlay solo si ha verificado con pings de tamaño MTU completo (>1600 bytes para VXLAN).",
        ],
        "references": [
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "RFC 8365: A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)",
            "Cisco Live BRKDCT-3378: EVPN Deep Dive and Troubleshooting",
        ],
        "fix": (
            "1. Verificar underlay IP/MPLS entre VTEPs/PEs; corregir rutas IGP si hay falla.\n"
            "2. Asegurar que BGP EVPN (AFI 25/SAFI 70) esté en Established y que las policies permitan comunidades extendidas.\n"
            "3. Verificar recepción de rutas EVPN Tipo 2 (MAC/IP) en ambos PEs.\n"
            "4. Confirmar que MAC-VRF/bridge domain tengan RD/RT correctos y VLANs asociadas.\n"
            "5. En multihoming: verificar ESI consistency y DF election; resolver conflictos de ESI."
        ),
    },
    # ── VXLAN ─────────────────────────────────────────────────────────
    "vxlan.vxlan_start": {
        "hypothesis": (
            "La falla de conectividad L2 sobre VXLAN es causada por una falla en el underlay IP (no hay reachability entre VTEPs), "
            "una configuración incorrecta de la interfaz NVE (VNI, VLAN mapping, o source IP), o un mecanismo de replicación BUM "
            "(multicast/HER) no operativo."
        ),
        "verification_steps": [
            "1. Validar conectividad IP básica entre loopbacks de VTEPs con pings de tamaño > 1550 bytes (para validar MTU).",
            "2. Verificar que la interfaz NVE esté administrativamente Up y que el source IP sea la loopback correcta.",
            "3. Confirmar el mapeo de VLAN a VNI en el VTEP local y remoto (deben coincidir).",
            "4. Verificar el mecanismo de replicación BUM: grupo multicast configurado y funcional, o tabla HER poblada.",
            "5. Inspeccionar la tabla de túneles remotos (remote VTEPs) y confirmar que las MACs apunten al VTEP correcto.",
        ],
        "expected_evidence": {
            "confirming": [
                "Ping entre loopbacks de VTEPs exitoso con DF y tamaño >= 1550 bytes (valida MTU underlay).",
                "Interfaz NVE en Up; source IP coincide con loopback anunciada en IGP.",
                "VLAN-to-VNI mapping idéntico en ambos VTEPs para el segmento de interés.",
                "Grupo multicast funcional (para multicast-based BUM) o tabla HER poblada con VTEPs remotos.",
                "Tabla de MACs muestra Next-Hop al VTEP remoto correcto para las MACs del cliente.",
            ],
            "invalidating": [
                "Ping entre loopbacks falla o requiere fragmentación (MTU insuficiente en underlay).",
                "Interfaz NVE en Down, source IP incorrecta, o no asociada a la loopback principal.",
                "VLAN-to-VNI mismatch: una VLAN mapea a VNI 10000 en un VTEP y a VNI 10001 en el otro.",
                "Sin receptores multicast registrados para el grupo BUM (IGMP/MLD falla) o tabla HER vacía.",
                "Tabla de MACs muestra MACs aprendidas localmente pero no remotas (falla de plane EVPN/control).",
            ],
        },
        "scientific_basis": (
            "VXLAN (RFC 7348) encapsula tramas Ethernet en UDP/4789. El underlay IP debe soportar una MTU de al menos 1550 bytes "
            "(1500 + 50 bytes de overhead VXLAN) para evitar fragmentación. El plano de control puede ser flood-and-learn (multicast/HER) "
            "o EVPN. En cualquier caso, el mapeo VLAN-to-VNI debe ser consistente en todos los VTEPs del mismo segmento. "
            "La inconsistencia de VNI es un error de configuración común que causa aislamiento de segmento."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que un ping entre VTEPs con tamaño 56 bytes valida VXLAN. Debe usar tamaño >= 1550 bytes con DF.",
            "Una NVE en 'Up' NO garantiza que el VNI esté correctamente mapeado. Verifique 'show vxlan vlan-to-vni'.",
            "Descarte la hipótesis de underlay solo si ha verificado el path completo incluyendo firewalls intermedios que puedan bloquear UDP 4789.",
        ],
        "references": [
            "RFC 7348: Virtual eXtensible Local Area Network (VXLAN)",
            "RFC 8365: A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)",
            "Cisco Live BRKDCT-3080: VXLAN/EVPN Troubleshooting",
        ],
        "fix": (
            "1. Verificar conectividad IP entre loopbacks de VTEPs con ping >= 1550 bytes + DF. Corregir MTU en underlay.\n"
            "2. Asegurar que la interfaz NVE esté Up y que la source IP sea la loopback correcta.\n"
            "3. Confirmar que el mapeo VLAN-to-VNI sea idéntico en todos los VTEPs del segmento.\n"
            "4. Verificar que el grupo multicast para BUM esté funcional o que la tabla HER esté poblada.\n"
            "5. Inspeccionar la tabla de MACs para confirmar que las MACs remotas apuntan al VTEP correcto."
        ),
    },
    # ── OSPF ──────────────────────────────────────────────────────────
    "ospf.ospf_start": {
        "hypothesis": (
            "La falla de enrutamiento OSPF es causada por una adyacencia que no alcanza el estado Full debido a "
            "mismatch de parámetros de área, MTU de interfaz, ID de router duplicado, o interfaces configuradas como pasivas."
        ),
        "verification_steps": [
            "1. Verificar que las interfaces estén asignadas al área OSPF correcta y no estén en 'passive-interface'.",
            "2. Comparar MTU de interfaz en ambos extremos del enlace (OSPF requiere MTU match para pasar de ExStart a Exchange).",
            "3. Confirmar que los timers Hello/Dead sean idénticos en ambos vecinos (mismatch = no adyacencia).",
            "4. Verificar que el Router-ID sea único en el área (duplicado causa inestabilidad y flaps).",
            "5. Inspeccionar LSDB para confirmar sincronización completa (todos los routers del área deben tener la misma LSDB).",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaces activas en el área correcta; 'passive-interface' solo en interfaces de loopback o sin vecinos.",
                "MTU idéntica en ambos extremos del enlace (ej. 1500 bytes).",
                "Timers Hello/Dead coincidentes (ej. 10/40 en broadcast, 30/120 en NBMA).",
                "Router-ID único en todo el dominio OSPF; sin mensajes de conflicto en logs.",
                "LSDB con el mismo número de entradas en todos los routers del área (sincronización completa).",
            ],
            "invalidating": [
                "Interfaces en área incorrecta o marcadas como passive en enlaces troncal.",
                "MTU mismatch: un extremo tiene 1500 y el otro 9000 (OSPF se congela en ExStart/Exchange).",
                "Timers mismatch: Hello 10s vs Hello 30s (vecino declarado Down por Dead timer expirado).",
                "Router-ID duplicado detectado en logs (causa reconvergencia continua).",
                "LSDB desincronizada: faltan LSAs Tipo 1/Tipo 2 en algunos routers (indica falla de flooding o partición de área).",
            ],
        },
        "scientific_basis": (
            "OSPF (RFC 2328) requiere que dos vecinos acuerden parámetros clave (Hello/Dead intervals, MTU, área, tipo de red) "
            "antes de alcanzar el estado Full. El MTU mismatch es una causa clásica de congelación en ExStart/Exchange porque los DBD packets "
            "son fragmentados o rechazados. Un Router-ID duplicado rompe la unicidad del LSA Tipo 1 (Router LSA), causando reconvergencias "
            "cíclicas (RFC 2328, Sección 13.3)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show ip ospf neighbor' muestra un vecino, la LSDB está sincronizada. Verifique el estado 'Full'.",
            "Una interfaz en 'Up/Up' a nivel físico NO garantiza que OSPF esté habilitada en ella. Verifique 'show ip ospf interface'.",
            "Descarte la hipótesis de MTU solo si ha verificado ambos extremos del enlace (incluyendo subinterfaces lógicas).",
        ],
        "references": [
            "RFC 2328: OSPF Version 2",
            "RFC 5340: OSPF for IPv6 (OSPFv3)",
            "Cisco Live BRKRST-3036: Advanced OSPF Troubleshooting",
        ],
        "fix": (
            "1. Verificar que las interfaces estén en el área OSPF correcta y no marcadas como passive.\n"
            "2. Asegurar que la MTU coincida en ambos extremos del enlace (mismatch congela en ExStart/Exchange).\n"
            "3. Sincronizar timers Hello/Dead (10/40 broadcast, 30/120 NBMA).\n"
            "4. Verificar que el Router-ID sea único en todo el dominio; corregir si está duplicado.\n"
            "5. Comparar LSDB entre routers para confirmar sincronización; reparar particiones de área si aplica."
        ),
    },
    # ── BGP ───────────────────────────────────────────────────────────
    "bgp.bgp_start": {
        "hypothesis": (
            "La falla de conectividad o enrutamiento es causada por una sesión BGP no establecida (estado diferente a Established), "
            "o por políticas de enrutamiento (prefix-lists, route-maps) que bloquean el intercambio de prefijos una vez que la sesión "
            "está activa."
        ),
        "verification_steps": [
            "1. Verificar conectividad IP de Capa 3 y Capa 4 (TCP 179) entre los peers BGP.",
            "2. Inspeccionar el estado de la sesión BGP (Idle, Active, Connect, OpenSent, OpenConfirm, Established).",
            "3. Validar parámetros de sesión: AS local/remoto, timers, MD5 password, update-source, multihop (eBGP).",
            "4. Verificar que los prefijos esperados estén siendo anunciados/recibidos (Adj-RIB-In/Out).",
            "5. Revisar políticas de entrada y salida (prefix-lists, route-maps, community-filters) que puedan filtrar rutas.",
        ],
        "expected_evidence": {
            "confirming": [
                "Ping/traceroute exitoso entre las IPs de los peers BGP.",
                "TCP 179 accesible y no bloqueado por firewall/ACL (ej. 'telnet <peer> 179' o SYN recibido).",
                "Sesión BGP en estado Established con Uptime estable (sin flaps recientes).",
                "Prefijos esperados presentes en Adj-RIB-In (recibidos) y/o Adj-RIB-Out (anunciados).",
                "Políticas de enrutamiento permiten explícitamente los prefijos de interés (o 'permit any' por defecto en iBGP).",
            ],
            "invalidating": [
                "Sin conectividad IP entre peers o TTL excedido (en eBGP sin multihop).",
                "TCP 179 rechazado o filtrado por ACL/firewall (connection refused / timeout).",
                "Sesión BGP en Active/Idle recurrente (posible AS mismatch, MD5 error, o timer mismatch).",
                "Adj-RIB-In vacío o con prefijos filtrados por policy de entrada.",
                "Adj-RIB-Out vacío o con prefijos filtrados por policy de salida.",
            ],
        },
        "scientific_basis": (
            "BGP opera sobre TCP 179 (RFC 4271). El establecimiento de sesión requiere alcanzabilidad IP y apertura de puerto. "
            "El algoritmo de Best Path Selection (RFC 4271, Sección 9.1) es determinista pero depende de que los prefijos lleguen "
            "a la Adj-RIB-In. Las políticas de enrutamiento son la causa más común de 'prefijos faltantes' en redes de producción, "
            "superando incluso a fallas de sesión (Cisco Live BRKRST-3320)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que un peer en estado 'Active' está funcionando. 'Active' significa que está intentando conectar, no que está activo.",
            "Un 'show ip bgp summary' con '0 received' puede deberse a políticas, no a falla de sesión. Verifique 'show ip bgp neighbors <peer> received-routes' y 'policy'.",
            "Descarte la hipótesis de políticas solo si ha verificado tanto la configuración como los contadores de matches en las route-maps/prefix-lists.",
        ],
        "references": [
            "RFC 4271: A Border Gateway Protocol 4 (BGP-4)",
            "RFC 2385: Protection of BGP Sessions via the TCP MD5 Signature Option",
            "Cisco Live BRKRST-3320: BGP Troubleshooting Deep Dive",
        ],
        "fix": (
            "1. Verificar conectividad IP y TCP 179 entre peers; eliminar ACLs/firewall que bloqueen.\n"
            "2. Validar AS local/remoto, MD5 password, update-source y eBGP multihop si aplica.\n"
            "3. Verificar que los prefijos esperados estén en Adj-RIB-In/Out; revisar policies de entrada/salida.\n"
            "4. Revisar prefix-lists, route-maps, y community-filters que puedan descartar rutas.\n"
            "5. Confirmar que el BGP Next-Hop sea alcanzable y resoluble vía IGP."
        ),
    },
    "isis.isis_start": {
        "hypothesis": "La falla de enrutamiento IS-IS es causada por una adyacencia que no alcanza el estado Up debido a mismatch de tipo de red (P2P vs Broadcast), MTU de interfaz, nivel de área desajustado (L1/L2), o NET/área inconsistente.",
        "verification_steps": [
            "1. Verificar que las interfaces estén configuradas con el mismo tipo de red (P2P o Broadcast) en ambos extremos.",
            "2. Comparar MTU de interfaz: IS-IS llena los IIH a la MTU completa; un mismatch impide la adyacencia.",
            "3. Confirmar que ambos routers compartan el mismo nivel (L1, L2 o L1-L2) y nombre de área para L1.",
            "4. Validar que el NET sea único en el dominio y que el System-ID no esté duplicado.",
            "5. Revisar la LSDB para confirmar sincronización completa y ausencia de LSPs faltantes.",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaces con el mismo tipo de red (P2P o Broadcast) en ambos extremos.",
                "MTU idéntica en ambos extremos del enlace (ej. 1497 bytes para IS-IS sobre Ethernet).",
                "Nivel de área coincidente (L1/L2) y System-ID único en el dominio.",
                "Adyacencias IS-IS en estado Up con CSNP/PSNP intercambiados correctamente.",
                "LSDB con el mismo número de entradas en todos los routers del área.",
            ],
            "invalidating": [
                "Interfaces con tipo de red desajustado (P2P vs Broadcast) causando rechazo de Hellos.",
                "MTU mismatch: un extremo acepta IIH de 1492 bytes y el otro espera 4462 (wide metrics/TLVs).",
                "Nivel desajustado: un router L1-only intenta formar adyacencia con un L2-only.",
                "System-ID duplicado detectado en logs (causa inestabilidad y flaps de adyacencia).",
                "LSPs faltantes en la LSDB de algunos routers (indica partición de área o flooding bloqueado).",
            ],
        },
        "scientific_basis": "IS-IS opera directamente sobre Capa 2 (CLNS) sin depender de IP para sus Hellos (RFC 1195, ISO 10589). El MTU es crítico porque los IIH se rellenan a la MTU completa para detectar incompatibilidades. Un System-ID duplicado rompe la unicidad de los LSPs y causa reconvergencias cíclicas (ISO 10589, Sección 7.2).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque los vecinos aparecen en 'show isis adjacency', la LSDB está sincronizada. Verifique el estado 'Up'.",
            "Una interfaz en 'Up/Up' a nivel físico NO garantiza que IS-IS esté habilitada en ella. Verifique 'show isis interface'.",
            "Descarte la hipótesis de MTU solo si ha verificado ambos extremos del enlace (incluyendo subinterfaces lógicas y MTU L2).",
        ],
        "references": [
            "RFC 1195: Use of OSI IS-IS for Routing in TCP/IP and Dual Environments",
            "ISO 10589: Intermediate System to Intermediate System Intra-Domain Routing Exchange Protocol",
            "Cisco Live BRKRST-3037: Advanced IS-IS Troubleshooting",
        ],
        "fix": (
            "1. Asegurar que ambos extremos de la interfaz usen el mismo tipo de red (P2P o Broadcast).\n"
            "2. Ajustar MTU para que coincida en ambos extremos (IS-IS rellena IIH a MTU completa).\n"
            "3. Verificar que ambos routers compartan el mismo nivel (L1/L2/L1-L2) y nombre de área para L1.\n"
            "4. Confirmar que el NET/System-ID sea único en el dominio; corregir duplicados.\n"
            "5. Revisar LSDB para sincronización; resolver particiones de área o flooding bloqueado."
        ),
    },
    "spanning_tree.st_start": {
        "hypothesis": "La falla de conectividad L2 o los loops de broadcast son causados por una topología Spanning Tree inestable: Root Bridge incorrecto, puertos bloqueados inesperadamente, TCNs recurrentes, o falta de protección BPDU en puertos de acceso.",
        "verification_steps": [
            "1. Identificar el Root Bridge actual y comparar con el diseño planificado (debe ser el Core principal).",
            "2. Verificar los roles de puerto en los enlaces clave (Root, Designated, Blocking/Alternate).",
            "3. Buscar eventos de Topology Change Notification (TCN) recurrentes en logs.",
            "4. Confirmar que los puertos de acceso (edge) tengan BPDU Guard habilitado para evitar loops accidentales.",
            "5. Validar la consistencia de configuración de MSTP (region name, revision, VLAN-to-instance mapping).",
        ],
        "expected_evidence": {
            "confirming": [
                "Root Bridge coincide con el switch de Core designado (prioridad baja configurada manualmente).",
                "Puertos troncales en estado Forwarding con roles correctos (RP/DP) y sin Alternate inesperados.",
                "Sin TCNs recurrentes en los últimos 15 minutos (tabla CAM estable).",
                "BPDU Guard activo en todos los puertos de acceso; sin logs de BPDU recibidos en puertos edge.",
                "MSTP region name, revision y VLAN-to-instance mapping idénticos en todos los switches del dominio.",
            ],
            "invalidating": [
                "Root Bridge inesperado en switch de acceso con prioridad por defecto (32768) y MAC más baja.",
                "Puertos designados en Blocking o Alternate en enlaces que deberían ser troncales activos.",
                "TCNs recurrentes (>1 por minuto) que vacían la CAM e inducen flooding masivo.",
                "Puertos edge recibiendo BPDUs (posible loop por conexión accidental o equipos no autorizados).",
                "MSTP region mismatch: switches en regiones diferentes calculan CST separadas y bloquean puertos.",
            ],
        },
        "scientific_basis": "STP/RSTP/MSTP (IEEE 802.1D/802.1w/802.1s) calculan una topología activa sin bucles mediante el intercambio de BPDUs. Un TCN recurrente indica inestabilidad física o lógica que limpia la tabla CAM cada vez, degradando el rendimiento (IEEE 802.1w, Sección 17). La ausencia de BPDU Guard en puertos edge es una causa frecuente de loops en entornos de campus.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un puerto está en 'forwarding', no hay loop. Un loop físico con BPDU filter puede silenciar STP.",
            "Un Root Bridge 'correcto' en el Core NO garantiza que todos los switches estén en la misma MSTP region. Verifique 'show spanning-tree mst configuration'.",
            "Descarte la hipótesis de TCN recurrente solo si ha verificado la estabilidad física de TODOS los enlaces del path.",
        ],
        "references": [
            "IEEE 802.1D: Media Access Control (MAC) Bridges",
            "IEEE 802.1w: Rapid Reconfiguration of Spanning Tree",
            "IEEE 802.1s: Multiple Spanning Trees",
            "Cisco Live BRKCRS-2501: Campus LAN Troubleshooting",
        ],
        "fix": (
            "1. Asegurar que el Root Bridge sea el switch de Core con prioridad manual baja (ej. 4096).\n"
            "2. Verificar roles de puerto (Root/Designated/Blocking) en enlaces troncales; corregir si hay Alternate inesperados.\n"
            "3. Investigar y eliminar la causa de TCNs recurrentes (enlaces inestables, BPDU filter).\n"
            "4. Habilitar BPDU Guard en todos los puertos de acceso (edge) para prevenir loops.\n"
            "5. Validar que MSTP region name, revision y VLAN-to-instance mapping sean idénticos en todos los switches."
        ),
    },
    "qos_traffic_eng.qos_start": {
        "hypothesis": "La degradación de calidad de servicio o el comportamiento inesperado del tráfico es causado por una clasificación incorrecta (DSCP/CoS), policing/shaping mal dimensionado, colas de baja prioridad saturadas, o un LSP TE con RSVP que no reserva el ancho de banda solicitado.",
        "verification_steps": [
            "1. Verificar la clasificación de tráfico en el borde: DSCP/CoS marcados correctamente y preservados en el core.",
            "2. Revisar las políticas de policing/shaping para confirmar que los límites de velocidad coinciden con el SLA.",
            "3. Inspeccionar las colas de salida (output queues) y contadores de descarte por congestión (tail-drop/WRED).",
            "4. Para TE: validar que la TED esté sincronizada y que el LSP RSVP-TE esté reservando el ancho de banda esperado.",
            "5. Confirmar que el mecanismo de Fast Reroute (FRR) esté operativo y que el bypass LSP esté precalculado.",
        ],
        "expected_evidence": {
            "confirming": [
                "Clasificación de bordes marca DSCP/CoS según política y los valores se preservan end-to-end.",
                "Policing/shaping configura rate y burst acordes al CIR/PIR del cliente sin descartes prematuros.",
                "Colas de salida sin descartes por tail-drop o WRED en las clases de prioridad de voz/video.",
                "TED sincronizada con ancho de banda disponible real; RSVP session Up con bandwidth reservado correctamente.",
                "FRR bypass LSP precalculado y listo; tiempo de conmutación <50ms ante falla de enlace/nodo.",
            ],
            "invalidating": [
                "DSCP/CoS remarcados o reseteados a 0 en un salto intermedio (trust boundary mal configurado).",
                "Policing con burst demasiado bajo que descarta ráfagas legítimas de tráfico agresivo (TCP slow-start afectado).",
                "Colas de voz/video con descartes crecientes por falta de bandwidth garantizado o mal configuración de LLQ.",
                "RSVP session Down o con 'Reservation Error' por insuficiencia de bandwidth en la TED.",
                "FRR no configurado o bypass LSP no precalculado, causando reconvergencia lenta (>1s) ante fallas.",
            ],
        },
        "scientific_basis": "DiffServ (RFC 2475) define la arquitectura de servicios diferenciados basada en clasificación y condicionamiento en el borde. RSVP-TE (RFC 3209) depende de la TED para CSPF; si el ancho de banda disponible es menor al solicitado, la señalización falla. El burst size en policing/shaping debe ser suficiente para absorber las ráfagas TCP (RFC 2697, RFC 2698).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el DSCP está marcado en el origen, se preserva en el core. Verifique 'show policy-map interface' en cada salto.",
            "Un 'show interface' sin errores NO excluye descartes por WRED en colas específicas. Verifique contadores de clase.",
            "Descarte la hipótesis de bandwidth insuficiente solo si ha verificado la TED y la política de RSVP en todos los nodos del path.",
        ],
        "references": [
            "RFC 2475: An Architecture for Differentiated Services",
            "RFC 3209: RSVP-TE: Extensions to RSVP for LSP Tunnels",
            "RFC 2697: A Single Rate Three Color Marker",
            "Cisco Live BRKRST-2042: QoS Troubleshooting and Design",
        ],
        "fix": (
            "1. Revisar y corregir la clasificación de tráfico en el borde (DSCP/CoS) y asegurar que se preserva en el core.\n"
            "2. Ajustar policing/shaping para que rate y burst coincidan con el CIR/PIR del SLA.\n"
            "3. Inspeccionar colas de salida y ajustar WRED/LLQ para evitar descartes en clases de voz/video.\n"
            "4. Para TE: sincronizar la TED y verificar que el LSP RSVP-TE reserve el ancho de banda esperado.\n"
            "5. Verificar que FRR bypass esté precalculado y que el tiempo de conmutación sea <50ms."
        ),
    },
    "multicast.mcast_start": {
        "hypothesis": "La falla de entrega multicast es causada por una falla en el plano de control IGMP/PIM (RP inalcanzable, RPF check fallido, o PIM neighbor down) o por una insuficiencia en el plano de datos (tabla MFIB sin entradas activas o OIL vacía).",
        "verification_steps": [
            "1. Verificar que el enrutamiento unicast subyacente (IGP) sea funcional y estable antes de diagnosticar multicast.",
            "2. Confirmar que el RP esté alcanzable por todos los routers del dominio PIM-SM y que la elección de RP sea consistente.",
            "3. Validar el RPF check: 'show ip rpf <source>' debe devolver la interfaz correcta hacia la fuente del tráfico.",
            "4. Verificar adyacencias PIM (Hello messages) y que las interfaces de tránsito tengan PIM habilitado.",
            "5. Revisar la tabla MFIB/MRIB para confirmar presencia de estados (S,G) y (*,G) con lista OIL no vacía.",
        ],
        "expected_evidence": {
            "confirming": [
                "IGP funcional con rutas estables hacia todas las fuentes y receptores multicast.",
                "RP alcanzable y consistente en todos los routers (estático o dinámico vía BSR/Auto-RP).",
                "RPF check exitoso: interfaz de ingreso del tráfico multicast coincide con la ruta IGP hacia la fuente.",
                "PIM neighbors en estado Up en todas las interfaces de tránsito del árbol multicast.",
                "MFIB/MRIB muestra entradas (S,G) y (*,G) activas con OIL poblada y contadores de reenvío incrementando.",
            ],
            "invalidating": [
                "IGP inestable o rutas faltantes hacia la fuente, causando fallas de RPF intermitentes.",
                "RP inconsistente: algunos routers usan un RP distinto, causando árboles fragmentados.",
                "RPF check fallido: tráfico multicast ingresa por interfaz distinta a la ruta IGP hacia la fuente (descarte silencioso).",
                "PIM neighbors Down por interfaces sin 'ip pim sparse-mode' o ACLs bloqueando IP 103/IGMP.",
                "MFIB con OIL vacía o sin estado (S,G): indica que no hay receptores interesados o IGMP Joins no llegan.",
            ],
        },
        "scientific_basis": "PIM-SM (RFC 4601) requiere un RP funcional y un RPF check estricto basado en la ruta unicast hacia la fuente. Un fallo de RPF es la causa más común de descarte silencioso de tráfico multicast (Cisco Live BRKRST-3325). IGMP (RFC 3376) gestiona la membresía de grupos en la última milla; sin IGMP Joins, la OIL permanece vacía.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un ping unicast funciona, el RPF multicast está OK. Verifique explícitamente 'show ip rpf <source>'.",
            "Un 'show ip pim neighbor' vacío NO significa ausencia de vecinos; puede significar que PIM no está habilitado en la interfaz.",
            "Descarte la hipótesis de RP solo si ha verificado la consistencia del RP en TODOS los routers del dominio multicast.",
        ],
        "references": [
            "RFC 4601: Protocol Independent Multicast - Sparse Mode (PIM-SM)",
            "RFC 3376: Internet Group Management Protocol, Version 3",
            "Cisco Live BRKRST-3325: Advanced Multicast Troubleshooting",
        ],
        "fix": (
            "1. Verificar que el IGP subyacente sea funcional y estable antes de diagnosticar multicast.\n"
            "2. Confirmar que el RP sea alcanzable y consistente en todos los routers; corregir si hay RP inconsistency.\n"
            "3. Validar el RPF check: 'show ip rpf <source>' debe devolver la interfaz correcta.\n"
            "4. Verificar que PIM esté habilitado en todas las interfaces de tránsito y que los vecinos estén Up.\n"
            "5. Revisar la tabla MFIB/MRIB para confirmar que haya estados (S,G) y (*,G) con OIL poblada."
        ),
    },
    "segment_routing_config.sr_config_start": {
        "hypothesis": "La configuración de Segment Routing no produce el comportamiento esperado debido a un desajuste en el bloque SRGB entre routers, un Prefix-SID duplicado, dependencias IGP sin habilitar extensiones SR, o un error de sintaxis en la asignación de SIDs.",
        "verification_steps": [
            "1. Verificar que el bloque SRGB (Segment Routing Global Block) sea idéntico en todos los routers del dominio.",
            "2. Confirmar que cada router tenga un Prefix-SID único asignado a su loopback principal.",
            "3. Validar que OSPF o IS-IS tengan las extensiones de Segment Routing habilitadas y operativas.",
            "4. Revisar la LFIB para confirmar que los Prefix-SIDs locales y remotos estén instalados correctamente.",
            "5. Verificar que el hardware/Plataforma soporte el forwarding de Segment Routing (algunas linecards no lo soportan).",
        ],
        "expected_evidence": {
            "confirming": [
                "SRGB idéntico en todos los routers del dominio (ej. 16000-23999).",
                "Prefix-SID único por loopback; sin duplicados detectados en logs ni en la base de datos IGP.",
                "Extensiones SR habilitadas en OSPF/IS-IS con TLVs propagándose correctamente (verificar en LSDB/LSP).",
                "LFIB muestra entradas para Prefix-SIDs locales y remotos con operación 'swap' o 'pop' correcta.",
                "Plataforma/linecard confirma soporte de SR-MPLS o SRv6 en la documentación del vendor y en la configuración.",
            ],
            "invalidating": [
                "SRGB desajustado entre routers: un router usa 16000-23999 y otro 900000-965535 (SRv6), causando descarte de labels.",
                "Prefix-SID duplicado en dos routers distintos (conflicto de forwarding en el core).",
                "IGP sin extensiones SR habilitadas: los TLVs de SIDs no se anuncian y la LSDB no contiene información de labels.",
                "LFIB vacía o con Prefix-SIDs en estado 'unresolved' (falta de ruta IGP hacia la loopback del origen).",
                "Linecard o software version no soporta SR: los labels se programan en la RIB pero no en el hardware de forwarding.",
            ],
        },
        "scientific_basis": "Segment Routing (RFC 8402) requiere un SRGB consistente en todo el dominio para que los Prefix-SIDs sean interpretados correctamente. Un Prefix-SID duplicado rompe la unicidad de la ruta y causa blackholing o loops. Las extensiones IGP (OSPF/IS-IS) son obligatorias para distribuir los SIDs sin depender de LDP/RSVP (RFC 8665, RFC 8667).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el IGP está funcional, SR está operativo. Verifique explícitamente los TLVs de SR en la LSDB.",
            "Un 'show segment-routing mpls lb' con labels NO garantiza que el data plane los esté usando. Verifique la LFIB.",
            "Descarte la hipótesis de SRGB solo si ha verificado el rango configurado en TODOS los routers del área/AS.",
        ],
        "references": [
            "RFC 8402: Segment Routing Architecture",
            "RFC 8665: OSPF Extensions for Segment Routing",
            "RFC 8667: IS-IS Extensions for Segment Routing",
            "Cisco Live BRKRST-2335: Segment Routing Deep Dive",
        ],
        "fix": (
            "1. Verificar que el SRGB sea idéntico en todos los routers del dominio (ej. 16000-23999).\n"
            "2. Confirmar que cada router tenga un Prefix-SID único asignado a su loopback principal.\n"
            "3. Validar que OSPF o IS-IS tengan las extensiones SR habilitadas y que los TLVs se propaguen.\n"
            "4. Revisar la LFIB para confirmar que los Prefix-SIDs estén instalados correctamente.\n"
            "5. Verificar que el hardware/linecard soporte forwarding de Segment Routing."
        ),
    },
    "bfd.bfd_start": {
        "hypothesis": "La falla de convergencia rápida es causada por una sesión BFD que no alcanza el estado Up debido a timers desajustados, tráfico UDP 3784/3785 bloqueado por ACLs/firewall, o una interfaz física con micro-flaps que genera oscilación de la sesión.",
        "verification_steps": [
            "1. Verificar que los timers BFD (Tx, Rx, Detection Multiplier) sean compatibles y soportados por el hardware en ambos extremos.",
            "2. Confirmar que no existan ACLs, firewall filters o security policies bloqueando UDP 3784 (single-hop) o 3785 (multi-hop).",
            "3. Validar el estado de la interfaz física: micro-flaps, errores CRC o descartes que indiquen inestabilidad L1-L2.",
            "4. Revisar si BFD está asociado correctamente al protocolo cliente (OSPF, BGP, IS-IS) y que el client registre la sesión.",
            "5. Verificar que los contadores de paquetes BFD reflejen intercambio bidireccional de control packets sin pérdida significativa.",
        ],
        "expected_evidence": {
            "confirming": [
                "Timers BFD soportados por ASIC/CPU en ambos extremos y negociados correctamente.",
                "Sin entradas de ACL/firewall descartando paquetes BFD en logs o contadores de interfaz.",
                "Interfaz física estable (sin flaps, CRC errors ni input/output errors creciendo).",
                "Protocolo cliente (OSPF/BGP/IS-IS) registrado con BFD; sesión BFD en estado Up con clientes activos.",
                "Contadores de paquetes BFD transmitidos/recibidos simétricos y sin incremento de drops en intervalos de 30s.",
            ],
            "invalidating": [
                "Timers BFD desajustados: un extremo pide 3.3ms pero el hardware del otro solo soporta 100ms mínimo.",
                "ACLs o firewall filters explícitamente bloqueando UDP 3784/3785 en alguna dirección.",
                "Micro-flaps de interfaz física que causan caídas breves de BFD inferiores al timer de detección.",
                "BFD sesión Up pero el protocolo cliente no registrado (falla de integración; no se produce convergencia rápida).",
                "Pérdida asimétrica de paquetes BFD (>50% en una dirección) por congestión o QoS descartando control packets.",
            ],
        },
        "scientific_basis": "BFD (RFC 5880) opera sobre UDP y proporciona detección de fallas sub-segundo independiente del protocolo de enrutamiento. Los timers deben ser soportados por el hardware (algunos ASICs no procesan <50ms). Una sesión BFD Up sin cliente registrado es inútil: el protocolo de enrutamiento no recibe la notificación de caída (RFC 5882).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque BFD está configurado, el protocolo cliente lo usa. Verifique 'show bfd neighbors client'.",
            "Una sesión BFD en 'Admin Down' NO significa falla de vecino; verifique si fue deshabilitada manualmente.",
            "Descarte la hipótesis de micro-flaps solo si ha monitorizado la interfaz durante al menos 5 minutos con 'monitor interface'.",
        ],
        "references": [
            "RFC 5880: Bidirectional Forwarding Detection (BFD)",
            "RFC 5882: Generic Application of BFD",
            "Cisco Live BRKRST-2331: BFD Design and Troubleshooting",
        ],
        "fix": (
            "1. Ajustar timers BFD (Tx/Rx/Detection Multiplier) al mínimo soportado por ambos extremos según datasheet.\n"
            "2. Eliminar o relajar ACLs/firewall filters que descarten UDP 3784 (single-hop) o UDP 3785 (multi-hop).\n"
            "3. Resolver inestabilidad física del enlace (cambiar cable/SFP, corregir dúplex/velocidad) para eliminar micro-flaps.\n"
            "4. Asociar explícitamente BFD al protocolo cliente (OSPF/BGP/IS-IS/EIGRP) en ambos extremos.\n"
            "5. Verificar contadores de paquetes BFD transmitidos/recibidos sean simétricos y sin pérdidas.\n"
            "6. Confirmar que la sesión BFD alcance estado Up y que el cliente la registre ('show bfd neighbors client').\n"
        ),
    },
    "dhcp.dhcp_start": {
        "hypothesis": "La falla de asignación de direcciones IP es causada por una ruptura en el flujo DORA (Discover/Offer/Request/Ack): el servidor no recibe la solicitud, el relay no reenvía correctamente, o el pool de direcciones está agotado.",
        "verification_steps": [
            "1. Verificar que el cliente envíe DHCP Discover (broadcast) y que la interfaz L3 local tenga IP configurada correctamente.",
            "2. Confirmar que el DHCP Relay (ip helper-address / relay agent) esté configurado y reenvíe los paquetes al servidor.",
            "3. Validar que el campo giaddr en los paquetes relayed coincida con la IP de la interfaz del relay agent (determina el pool).",
            "4. Revisar disponibilidad de direcciones en el pool del servidor DHCP para la subnet indicada por giaddr.",
            "5. Inspeccionar reglas de firewall/ACL que puedan bloquear UDP 67/68 entre relay y servidor, o entre cliente y relay.",
        ],
        "expected_evidence": {
            "confirming": [
                "Cliente genera DHCP Discover broadcast en la VLAN de acceso (captura tcpdump lo confirma).",
                "Relay agent reenvía el Discover como unicast al servidor DHCP configurado (IP helper correcta).",
                "Campo giaddr coincide con la IP de la interfaz SVI/subinterfaz del relay (servidor selecciona el pool correcto).",
                "Pool de direcciones del servidor con leases disponibles (>0% libre) para la subnet del giaddr.",
                "Sin ACLs ni firewalls bloqueando UDP 67/68 en el path cliente-relay-servidor.",
            ],
            "invalidating": [
                "Cliente no envía Discover: cable desconectado, VLAN incorrecta, o NIC deshabilitada.",
                "Relay agent no configurado o apuntando a IP de servidor inexistente (Discover broadcast no sale del segmento).",
                "giaddr incorrecto o ausente: el servidor no sabe qué pool asignar y descarta la solicitud.",
                "Pool agotado (exhausted): sin direcciones disponibles para nuevos clientes en la subnet.",
                "Firewall/ACL bloqueando UDP 67/68 entre relay y servidor (Discover llega al relay pero no al servidor).",
            ],
        },
        "scientific_basis": "DHCP (RFC 2131) utiliza el flujo DORA sobre UDP 67/68. El relay agent inserta giaddr para que el servidor identifique la subnet correcta. Sin giaddr válido, el servidor no puede seleccionar un pool. La exhaustión de pools es una causa común en entornos de alta rotación de clientes (RFC 2131, Sección 4.1).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el servidor DHCP está Up, los clientes reciben ofertas. Verifique el relay y el giaddr.",
            "Un 'show ip dhcp pool' con leases libres NO garantiza que la VLAN del cliente esté asociada a ese pool.",
            "Descarte la hipótesis de pool agotado solo si ha verificado la asignación de subnets a pools en el servidor.",
        ],
        "references": [
            "RFC 2131: Dynamic Host Configuration Protocol",
            "RFC 3046: DHCP Relay Agent Information Option (Option 82)",
            "Cisco Live BRKCRS-2502: Campus Network Troubleshooting",
        ],
        "fix": (
            "1. Asegurar que la interfaz del cliente/SVI tenga IP correcta y esté Up/Up.\n"
            "2. Configurar o corregir el DHCP Relay ('ip helper-address') en la interfaz L3 del segmento de cliente.\n"
            "3. Verificar que el campo giaddr en los paquetes relayed coincida con la IP de la interfaz del relay.\n"
            "4. Liberar/agregar direcciones en el pool del servidor para la subnet indicada por giaddr.\n"
            "5. Eliminar ACLs/firewall que bloqueen UDP 67/68 entre cliente, relay y servidor.\n"
            "6. Validar que el cliente reciba Offer/Ack tras un Discover; de lo contrario, revisar logs del servidor.\n"
        ),
    },
    "netflow.nf_start": {
        "hypothesis": "La ausencia de datos de telemetría o la inconsistencia en el análisis de tráfico es causada por una configuración incorrecta del exportador (IP/puerto del colector), una sampling rate inadecuada, o una falta de recursos en el router (CPU/memoria para procesar flujos).",
        "verification_steps": [
            "1. Verificar la conectividad IP y accesibilidad al colector NetFlow/sFlow desde el router (ping al IP del colector).",
            "2. Confirmar que el puerto UDP del colector (2055, 9995, 6343 para sFlow) no esté bloqueado por ACLs o firewalls intermedios.",
            "3. Validar la sampling rate: en enlaces de alta velocidad, una rate de 1:1 puede saturar la CPU o el enlace de management.",
            "4. Revisar la cache de NetFlow en el router: verificar que flujos activos se estén creando y exportando.",
            "5. Inspeccionar recursos del router (CPU, memoria) para confirmar que el procesamiento de flujos no está causando degradación.",
        ],
        "expected_evidence": {
            "confirming": [
                "Ping exitoso desde el router hacia el IP del colector NetFlow/sFlow.",
                "Puerto UDP del colector accesible y sin descartes en ACLs/firewalls del path.",
                "Sampling rate configurada acorde a la capacidad del router y al volumen de tráfico (ej. 1:1000 en 10G).",
                "NetFlow cache muestra flujos activos creciendo y exportador con 'flows exported' incrementando.",
                "CPU y memoria del router estables (<80% CPU) durante el procesamiento de NetFlow.",
            ],
            "invalidating": [
                "Sin conectividad IP hacia el colector (ruta inexistente o interfaz de management down).",
                "ACL/firewall bloqueando el tráfico de exportación UDP hacia el colector (descarte silencioso).",
                "Sampling rate 1:1 en enlace 100G que satura la CPU del router o el enlace out-of-band.",
                "NetFlow cache vacía o con '0 flows exported' (monitor no aplicado a interfaces o dirección incorrecta).",
                "CPU del router >95% con el proceso de NetFlow como top consumer (sobrecarga por sampling excesivo).",
            ],
        },
        "scientific_basis": "NetFlow v5/v9/IPFIX (RFC 3954, RFC 7011) requiere conectividad IP al colector y recursos suficientes para el muestreo. Un sampling rate inadecuado es una causa frecuente de pérdida de paquetes de exportación o degradación de CPU. La configuración debe aplicarse en la dirección correcta (ingress/egress) de las interfaces de interés.",
        "confidence_level": "Media",
        "bias_warnings": [
            "NO asuma que porque el colector recibe algunos paquetes, la sampling rate es correcta. Verifique la representatividad estadística.",
            "Una cache de NetFlow vacía puede deberse a que el monitor no está aplicado a la interfaz, no a una falla del colector.",
            "Descarte la hipótesis de recursos solo si ha correlacionado el uso de CPU con el proceso de NetFlow en los logs.",
        ],
        "references": [
            "RFC 3954: Cisco Systems NetFlow Services Export Version 9",
            "RFC 7011: Specification of the IPFIX Protocol for the Exchange of Flow Information",
            "Cisco Live BRKCRS-2502: Network Telemetry Troubleshooting",
        ],
        "fix": (
            "1. Verificar conectividad IP y ruta hacia el colector NetFlow/sFlow desde el router.\n"
            "2. Abrir puertos UDP 2055/9995/6343 en firewalls/ACLs intermedios.\n"
            "3. Ajustar la sampling rate a un valor adecuado para la velocidad del enlace (ej. 1:1000 en 10G/100G).\n"
            "4. Aplicar el monitor de NetFlow a las interfaces de interés en ingress/egress según diseño.\n"
            "5. Verificar que la cache de flujos muestre entradas activas y contadores de exportación incrementando.\n"
            "6. Confirmar que CPU/memoria del router se mantengan estables tras la activación del exportador.\n"
        ),
    },
    "sdwan.sdwan_ts_start": {
        "hypothesis": "La falla de conectividad overlay o el rendimiento degradado en SD-WAN es causado por una pérdida de conexiones de control hacia los orquestadores (vManage/vSmart/vBond), fallas en los túneles IPsec de datos (BFD flaps), o políticas de App-Aware Routing que desvían el tráfico por enlaces degradados.",
        "verification_steps": [
            "1. Verificar que el Edge tenga sesiones de control activas (DTL/TLS) hacia vManage, vSmart y vBond.",
            "2. Revisar el estado de los túneles IPsec de datos (BFD sessions) y su estabilidad (uptime sin flaps).",
            "3. Validar la calidad de los enlaces físicos WAN: latencia, jitter y pérdida de paquetes medidos por BFD.",
            "4. Inspeccionar las políticas de App-Aware Routing para confirmar que los SLA thresholds coincidan con el diseño.",
            "5. Revisar la tabla de rutas OMP para confirmar que los prefijos de servicio estén siendo anunciados y recibidos correctamente.",
        ],
        "expected_evidence": {
            "confirming": [
                "Edge con conexiones de control Up/Active hacia vManage, vSmart y vBond (estado 'connected').",
                "Túneles IPsec de datos estables (BFD sessions Up sin flaps en los últimos 15 minutos).",
                "Enlaces WAN con métricas de BFD dentro de los SLA thresholds configurados (latencia <150ms, jitter <30ms, loss <1%).",
                "Políticas de App-Aware Routing configuradas con color/transporte correcto y SLA class match.",
                "Tabla OMP muestra prefijos de servicio con next-hop TLOC válido y reachability 'ok'.",
            ],
            "invalidating": [
                "Edge sin conexiones de control (estado 'unreachable' o 'disabled') por falta de ruta o certificados inválidos.",
                "BFD sessions con flaps recurrentes por inestabilidad del enlace físico WAN o NAT timeout en firewalls intermedios.",
                "Enlaces WAN con latencia/jitter fuera de SLA, causando desvío continuo de tráfico y posible blackholing.",
                "Políticas de App-Aware Routing con SLA class vacío (sin enlaces que cumplan el umbral, tráfico descartado).",
                "OMP no anuncia/recibe rutas de servicio (política de control bloqueando la distribución de prefijos).",
            ],
        },
        "scientific_basis": "SD-WAN (Cisco SD-WAN / Viptela) depende de conexiones de control DTLS/TLS hacia los orquestadores para recibir políticas. BFD monitorea la calidad de cada túnel IPsec overlay y alimenta el App-Aware Routing. Sin conexión de control, el Edge opera en modo 'stale' con las últimas políticas conocidas, pero no puede recibir actualizaciones.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el Edge tiene IP en el WAN, la conexión de control funciona. Verifique certificados y firewall (port 12346, 12366).",
            "Un BFD session Up NO garantiza que el SLA esté dentro del umbral. Verifique las métricas de calidad, no solo el estado.",
            "Descarte la hipótesis de política solo si ha verificado el SLA class y los colors en vManage para el Edge afectado.",
        ],
        "references": [
            "Cisco SD-WAN Design and Deployment Guide",
            "Cisco SD-WAN Troubleshooting and Operations Guide",
            "Cisco Live BRKSDW-2820: SD-WAN Deep Dive Troubleshooting",
        ],
        "fix": (
            "1. Restaurar conectividad de control DTL/TLS del Edge hacia vBond/vManage/vSmart (rutas, certificados, puertos 12346/12366).\n"
            "2. Estabilizar túneles IPsec de datos (BFD) verificando calidad de enlaces WAN y NAT/firewall intermedios.\n"
            "3. Ajustar thresholds de App-Aware Routing (latencia/jitter/pérdida) a valores realistas según SLA.\n"
            "4. Verificar que los colores/transportes estén asignados correctamente a cada TLOC.\n"
            "5. Revisar tabla OMP para asegurar que los prefijos de servicio se anuncian y reciben con next-hop TLOC válido.\n"
            "6. Confirmar que el Edge muestra conexiones de control Up y métricas BFD dentro de SLA.\n"
        ),
    },
    "dmvpn.dmvpn_ts_start": {
        "hypothesis": "La falla de conectividad en DMVPN es causada por un registro NHRP fallido en el Hub, una asociación de seguridad IPsec no establecida (IKEv1/v2 failure), o una falla en el enrutamiento dinámico sobre el túnel mGRE (OSPF/EIGRP/BGP no forma adyacencias).",
        "verification_steps": [
            "1. Verificar en el Hub que los Spokes estén registrados en la base de datos NHRP con sus IPs NBMA y túnel correctas.",
            "2. Confirmar que las asociaciones de seguridad ISAKMP/IPsec estén activas entre Hub-Spoke y Spoke-Spoke.",
            "3. Validar que el protocolo de enrutamiento (OSPF, EIGRP, BGP) forme adyacencias sobre las IPs del túnel mGRE.",
            "4. Revisar que el túnel mGRE esté operativo en ambos extremos (source interface correcta, tunnel key/mode match).",
            "5. Inspeccionar NAT en los Spokes: el tráfico GRE/IPsec debe estar excluido de la traducción NAT para evitar conflicto.",
        ],
        "expected_evidence": {
            "confirming": [
                "Hub muestra Spokes registrados en NHRP con estado 'dynamic' y IP NBMA resoluble.",
                "Sesiones ISAKMP en estado 'QM_IDLE' e IPsec SA activas con contadores de encapsulación incrementando.",
                "Protocolo de enrutamiento forma adyacencias sobre IPs de túnel mGRE (vecinos visibles en estado Full/Up).",
                "Túnel mGRE en estado Up/Up con source interface apuntando a la interfaz WAN pública correcta.",
                "NAT excluye explícitamente el tráfico GRE (IP 47) e IPsec (ESP, UDP 500/4500) de la traducción.",
            ],
            "invalidating": [
                "Spoke no registrado en NHRP Hub (tunnel source incorrecto, firewall bloqueando NHRP, o NAT traversal no habilitado).",
                "ISAKMP/IPsec en estado 'MM_NO_STATE' o 'ACTIVE(INIT)' indicando mismatch de políticas criptográficas o pre-shared key.",
                "Protocolo de enrutamiento sin vecinos sobre mGRE por split-horizon mal configurado o timers incompatibles.",
                "Túnel mGRE en estado Down/Down por source interface caída o tunnel destination inalcanzable.",
                "NAT traduce el tráfico GRE/IPsec antes del cifrado, rompiendo la negociación IKE y el registro NHRP.",
            ],
        },
        "scientific_basis": "DMVPN (RFC draft/Cisco) combina mGRE, NHRP e IPsec para crear VPNs dinámicas. NHRP actúa como resolución de next-hop entre Spokes; sin registro en el Hub, no hay resolución directa Spoke-to-Spoke. NAT-T (UDP 4500) es esencial cuando los Spokes están detrás de NAT (RFC 3947).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el túnel mGRE está Up, IPsec está funcionando. Verifique 'show crypto ipsec sa'.",
            "Un 'show dmvpn' con entradas NO garantiza que el Spoke pueda resolver al otro Spoke. Pruebe 'show ip nhrp' y ping Spoke-to-Spoke.",
            "Descarte la hipótesis de NAT solo si ha verificado la ACL de exclusión de NAT y el estado de NAT-T en IKE.",
        ],
        "references": [
            "RFC 3947: Negotiation of NAT-Traversal in the IKE",
            "Cisco DMVPN Design Guide",
            "Cisco Live BRKSEC-4054: DMVPN Troubleshooting",
        ],
        "fix": (
            "1. Verificar registro NHRP en el Hub ('show ip nhrp') y corregir tunnel source/destination si es necesario.\n"
            "2. Restablecer asociaciones ISAKMP/IPsec verificando políticas criptográficas, PSK y NAT-T (UDP 4500).\n"
            "3. Habilitar routing dinámico (OSPF/EIGRP/BGP) sobre la interfaz de túnel mGRE en Hub y Spokes.\n"
            "4. Confirmar que el túnel mGRE esté Up/Up con modo multipoint y tunnel key coincidente.\n"
            "5. Excluir tráfico GRE/IPsec de la traducción NAT en los Spokes.\n"
            "6. Validar conectividad Spoke-to-Spoke y Hub-to-Spoke tras los cambios.\n"
        ),
    },
    "eigrp.eigrp_ts_start": {
        "hypothesis": "La falla de enrutamiento EIGRP es causada por un mismatch de AS o K-Values, bloqueo del tráfico multicast EIGRP (224.0.0.10), una interfaz pasiva configurada por error, o un estado Stuck-In-Active (SIA) que indica inestabilidad en la topología.",
        "verification_steps": [
            "1. Verificar que el número de Sistema Autónomo (AS) y los K-Values coincidan exactamente en todos los vecinos.",
            "2. Confirmar que el tráfico multicast IP 224.0.0.10 no esté bloqueado por ACLs, firewalls o configuración de interfaz.",
            "3. Revisar que las interfaces relevantes no estén configuradas como passive-interface en el proceso EIGRP.",
            "4. Validar que los vecinos alcancen el estado Up y que la tabla de topología muestre rutas con Successor y Feasible Successor.",
            "5. Buscar eventos Stuck-In-Active (SIA) en logs, que indican que un router no recibió respuesta a un Query de reenvío.",
        ],
        "expected_evidence": {
            "confirming": [
                "AS number y K-Values idénticos en ambos extremos de cada adyacencia EIGRP.",
                "Multicast 224.0.0.10 alcanzable en el segmento L2 (sin ACLs o storm control bloqueando EIGRP Hellos).",
                "Interfaces activas en EIGRP no marcadas como passive-interface.",
                "Vecinos EIGRP en estado Up con tiempo de hold estable; tabla de topología muestra Successor con métrica finita.",
                "Sin logs de Stuck-In-Active (SIA) en los últimos 15 minutos; Queries y Replies se intercambian correctamente.",
            ],
            "invalidating": [
                "AS mismatch o K-Values desajustados (vecinos no forman adyacencia aunque estén en el mismo segmento).",
                "ACL o storm control descartando paquetes EIGRP multicast (Hellos no llegan; vecino declarado Down).",
                "Interfaces clave configuradas como passive-interface (no envían ni reciben Hellos/Updates).",
                "Vecino en estado 'Init' o sin aparecer (falla de Capa 2 o dirección IP incorrecta en subred).",
                "SIA recurrente en logs: un router envía Query pero no recibe Reply en 3 minutos (topología inestable o vecino lento).",
            ],
        },
        "scientific_basis": "EIGRP (RFC 7868) requiere AS y K-Values idénticos para formar adyacencias. Los paquetes Hello se envían a 224.0.0.10 (IP 88). Un estado SIA indica que un router no puede resolver un Query, lo que detiene el cálculo DUAL para ese prefijo (RFC 7868, Sección 3.3). La inestabilidad de topología o links lentos son causas frecuentes de SIA.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show ip eigrp neighbors' muestra un vecino, la topología está convergida. Verifique 'show ip eigrp topology'.",
            "Un 'passive-interface default' olvidado puede silenciar EIGRP en interfaces críticas sin generar logs evidentes.",
            "Descarte la hipótesis de SIA solo si ha verificado la estabilidad de todos los links y la carga de CPU de los routers del path.",
        ],
        "references": [
            "RFC 7868: The EIGRP Protocol",
            "Cisco EIGRP Configuration Guide",
            "Cisco Live BRKRST-3038: Advanced EIGRP Troubleshooting",
        ],
        "fix": (
            "1. Corregir el número de AS para que coincida exactamente en todos los routers EIGRP del dominio.\n"
            "2. Sincronizar K-Values (métrica) en todos los vecinos.\n"
            "3. Verificar que las network statements usen wildcard mask correcta y capturen interfaces de tránsito.\n"
            "4. Eliminar 'passive-interface' de enlaces troncales que deben formar adyacencias.\n"
            "5. Asegurar que la autenticación MD5/key-chain sea idéntica en ambos extremos.\n"
            "6. Investigar y resolver eventos Stuck-In-Active (SIA) estabilizando links o aumentando active-time.\n"
        ),
    },
    "pbr.pbr_ts_start": {
        "hypothesis": "La falla de desvío de tráfico por Policy-Based Routing es causada por una ACL de match que no captura el tráfico esperado, un next-hop inalcanzable o caído en la política, o la aplicación del route-map en la interfaz de entrada incorrecta.",
        "verification_steps": [
            "1. Verificar que la ACL referenciada en el route-map tenga contadores activos (matches) para el tráfico de interés.",
            "2. Confirmar que el next-hop o interface de salida especificados en la política estén activos y alcanzables.",
            "3. Validar que el route-map esté aplicado en la dirección correcta (ingress) de la interfaz de entrada del tráfico.",
            "4. Revisar si existe un 'default next-hop' o 'default interface' que deba actuar como fallback cuando el primario falla.",
            "5. Inspeccionar la tabla de rutas local para confirmar que la ruta por defecto no esté interfiriendo con PBR.",
        ],
        "expected_evidence": {
            "confirming": [
                "ACL de match muestra contadores incrementando al pasar tráfico de prueba del origen esperado.",
                "Next-hop de la política alcanzable y en estado Up (ping exitoso desde el router al next-hop PBR).",
                "Route-map aplicado en la interfaz de entrada correcta y en dirección 'ip policy route-map' (ingress).",
                "'set ip next-hop' tiene prioridad sobre 'set ip default next-hop' y el primario está activo.",
                "Tráfico de prueba sigue el path PBR esperado según traceroute o captura en la interfaz de salida designada.",
            ],
            "invalidating": [
                "ACL de match con contadores en cero (tráfico no coincide con la ACL por subnet o puerto mal definido).",
                "Next-hop PBR caído o inalcanzable; sin 'default next-hop' configurado, el tráfico se enruta por la RIB normal.",
                "Route-map aplicado en la interfaz de salida en lugar de la de entrada (PBR no se evalúa).",
                "Confusión entre 'set ip next-hop' (obligatorio) y 'set ip default next-hop' (solo si la RIB no tiene ruta).",
                "Ruta por defecto más específica o BGP route overriding el comportamiento de PBR para el destino.",
            ],
        },
        "scientific_basis": "PBR evalúa paquetes en la interfaz de entrada mediante route-maps con ACLs. Si el next-hop no es alcanzable, PBR falla silenciosamente y el paquete sigue la RIB (dependiendo de la implementación del vendor). La dirección de aplicación del route-map es crítica: debe ser ingress (Cisco IOS IP Routing Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el route-map existe, está siendo evaluado. Verifique 'show ip policy' en la interfaz correcta.",
            "Un next-hop 'alcanzable' en la RIB global NO garantiza que PBR lo use; verifique que el next-hop sea directamente alcanzable o resoluble.",
            "Descarte la hipótesis de ACL solo si ha enviado tráfico de prueba que cumpla EXACTAMENTE con las condiciones de la ACL.",
        ],
        "references": [
            "Cisco IOS IP Routing: Policy-Based Routing Configuration Guide",
            "RFC 1102: Policy Routing in Internet Protocols",
            "Cisco Live BRKRST-3035: Advanced IP Routing Troubleshooting",
        ],
        "fix": (
            "1. Verificar que el route-map esté aplicado en ingress de la interfaz de entrada ('show ip policy interface').\n"
            "2. Corregir la ACL de match para que capture el tráfico de origen/destino esperado.\n"
            "3. Asegurar que el next-hop o interface de salida de PBR estén Up y alcanzables.\n"
            "4. Usar 'set ip next-hop' para forzar el path obligatorio, o 'set ip default next-hop' solo como fallback según diseño.\n"
            "5. Evitar que rutas por defecto o BGP sobreescriban PBR para el destino.\n"
            "6. Probar con tráfico de prueba y traceroute para confirmar que sigue el path PBR deseado.\n"
        ),
    },
    "ipv6.ipv6_ts_start": {
        "hypothesis": "La falla de conectividad IPv6 es causada por una falla en el Neighbor Discovery Protocol (NDP), una ruta faltante en la tabla de enrutamiento IPv6, o una configuración incorrecta de autoconfiguración (SLAAC/DHCPv6) en el borde de red.",
        "verification_steps": [
            "1. Verificar que la interfaz tenga una Link-Local Address válida (fe80::/10) y que esté en estado UP.",
            "2. Confirmar que el Neighbor Cache (equivalente a ARP) resuelve correctamente las direcciones MAC de los vecinos IPv6.",
            "3. Validar la tabla de rutas IPv6 para confirmar que existe una ruta activa hacia el destino (incluyendo ruta por defecto ::/0).",
            "4. Revisar que ICMPv6 no esté bloqueado por firewall/ACLs (Neighbor Solicitation/Advertisement y Router Advertisement dependen de ICMPv6).",
            "5. Inspeccionar la configuración de SLAAC/DHCPv6: el router debe anunciar el prefijo correcto (RA) y el cliente debe generar una IP válida.",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaz IPv6 con Link-Local Address generada automáticamente y estado 'UP/UP'.",
                "Neighbor Cache muestra las MACs resueltas en estado 'REACHABLE' o 'STALE' para los gateways.",
                "Tabla de rutas IPv6 contiene ruta activa hacia el destino o ruta por defecto ::/0 con next-hop resoluble.",
                "Sin reglas de firewall/ACL descartando ICMPv6 tipo 135/136 (NDP) o tipo 134 (RA).",
                "Cliente IPv6 recibe Router Advertisement (RA) con prefijo válido y genera una Global Unicast Address operativa.",
            ],
            "invalidating": [
                "Interfaz IPv6 en Down/Down o sin Link-Local Address (IPv6 deshabilitado globalmente o en la interfaz).",
                "Neighbor Cache con entradas en estado 'FAILED' o 'INCOMPLETE' (NDP bloqueado o vecino no responde).",
                "Ruta IPv6 hacia el destino ausente o con next-hop inalcanzable (IGPv6 no configurado o redistribución fallida).",
                "Firewall/ACL bloqueando ICMPv6 (NDP y RA descartados silenciosamente, causando falla de autodescubrimiento).",
                "Cliente no recibe RA o el prefijo anunciado no coincide con la subnet esperada (DHCPv6/SLAAC mal configurado).",
            ],
        },
        "scientific_basis": "IPv6 NDP (RFC 4861) reemplaza ARP usando ICMPv6. Sin NDP funcional, no hay resolución de Capa 2. SLAAC (RFC 4862) depende de Router Advertisements (RA) para anunciar prefijos; si ICMPv6 está bloqueado, la autoconfiguración falla. La ruta por defecto ::/0 debe ser aprendida vía RA o configurada estáticamente.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un ping IPv6 funciona en un sentido, NDP está resuelto en ambos sentidos. Verifique el Neighbor Cache en ambos extremos.",
            "Una interfaz con Global Unicast Address NO garantiza que el default gateway sea alcanzable. Verifique 'ip -6 route'.",
            "Descarte la hipótesis de firewall solo si ha verificado TODAS las ACLs en el path, incluyendo las del host local (ip6tables).",
        ],
        "references": [
            "RFC 4861: Neighbor Discovery for IP Version 6 (IPv6)",
            "RFC 4862: IPv6 Stateless Address Autoconfiguration",
            "Cisco Live BRKIPV6-3000: IPv6 Troubleshooting",
        ],
        "fix": (
            "1. Habilitar IPv6 globalmente y en las interfaces de interés.\n"
            "2. Resolver fallas de NDP verificando que ICMPv6 no esté bloqueado por ACLs/firewall host.\n"
            "3. Completar el Neighbor Cache eliminando entradas FAILED o verificando segmento L2/VLAN correcto.\n"
            "4. Agregar ruta estática o dinámica (OSPFv3/IS-IS/MP-BGP) hacia el destino, incluyendo ::/0 si aplica.\n"
            "5. Corregir prefijo anunciado por SLAAC (Router Advertisement) para que coincida con la subnet del segmento.\n"
            "6. Validar conectividad end-to-end con ping6 y verificar que el cliente tenga GUA operativa.\n"
        ),
    },
    "aaa.aaa_ts_start": {
        "hypothesis": "La falla de autenticación, autorización o accounting es causada por una falta de conectividad al servidor AAA (RADIUS/TACACS+), un shared secret mismatch, o una method list mal ordenada que no permite fallback local.",
        "verification_steps": [
            "1. Verificar conectividad IP y accesibilidad al servidor AAA (ping y telnet/nc a puertos 1812/1813 o 49).",
            "2. Confirmar que el shared secret coincida exactamente (distingue mayúsculas/minúsculas y espacios) en el NAS y el servidor.",
            "3. Revisar la method list de autenticación para confirmar que incluya un método local como fallback si el servidor remoto falla.",
            "4. Validar que el servidor AAA tenga el usuario/grupo configurado con los privilegios y permisos correctos.",
            "5. Inspeccionar logs de accounting para confirmar que las sesiones y comandos se registran sin errores de buffer o timeout.",
        ],
        "expected_evidence": {
            "confirming": [
                "Ping y conectividad de puerto exitosos hacia el servidor AAA desde el NAS.",
                "Shared secret idéntico en ambos extremos (verificado mediante debug o captura de paquetes).",
                "Method list configurada con fallback local (ej. 'aaa authentication login default group tacacs+ local').",
                "Usuario existe en el servidor AAA con el nivel de privilegio asignado correctamente.",
                "Logs de accounting muestran registros de inicio/fin de sesión y comandos ejecutados sin errores.",
            ],
            "invalidating": [
                "Sin conectividad IP al servidor AAA (interfaz de management down, ACL bloqueando puertos AAA).",
                "Shared secret mismatch: el servidor rechaza la autenticación con 'Authentication Failed' o 'Invalid Signature'.",
                "Method list sin fallback local: si el servidor AAA cae, no hay acceso administrativo al dispositivo.",
                "Usuario no existe en el servidor AAA o tiene privilegios insuficientes (rechazo de autorización).",
                "Accounting logs con errores de buffer lleno o timeout de transmisión (pérdida de registros de auditoría).",
            ],
        },
        "scientific_basis": "RADIUS (RFC 2865) y TACACS+ (RFC draft/Cisco) requieren conectividad IP y shared secret para cifrar las credenciales. Una method list sin fallback local es un riesgo operacional crítico: si el servidor AAA no responde, el dispositivo queda inaccesible. El accounting depende de la disponibilidad del buffer local y del enlace hacia el servidor (Cisco AAA Implementation Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el ping al servidor AAA funciona, el puerto está abierto. Verifique con 'telnet <server> 49' o 'nc -u <server> 1812'.",
            "Un 'Authentication Failed' puede deberse al usuario, al shared secret o a la autorización. Verifique los debugs por separado.",
            "Descarte la hipótesis de servidor solo si ha probado la autenticación con un usuario local conocido y funciona.",
        ],
        "references": [
            "RFC 2865: Remote Authentication Dial-In User Service (RADIUS)",
            "RFC 2866: RADIUS Accounting",
            "Cisco AAA Implementation Guide",
            "Cisco Live BRKSEC-4032: AAA Troubleshooting",
        ],
        "fix": (
            "1. Restaurar conectividad IP al servidor RADIUS/TACACS+ y abrir puertos 1812/1813 o 49.\n"
            "2. Corregir el shared secret para que coincida exactamente (case-sensitive, sin espacios extra).\n"
            "3. Configurar method list con fallback local (ej. group tacacs+ local) y aplicarla a line vty/console.\n"
            "4. Verificar que el usuario/grupo exista en el servidor con privilegios correctos.\n"
            "5. Habilitar accounting para exec/commands/network según requisitos de auditoría.\n"
            "6. Confirmar autenticación exitosa con un usuario de prueba y revisar logs de accounting.\n"
        ),
    },
    "switch_l2.switch_l2_ts_start": {
        "hypothesis": "La falla de conmutación L2 es causada por una tabla CAM llena (MAC flapping), un mismatch de VLAN nativa o tagged en un enlace trunk, una negociación LACP fallida, o un loop de Capa 2 no detectado por Spanning Tree.",
        "verification_steps": [
            "1. Verificar la tabla CAM/MAC para detectar flapping de direcciones MAC entre puertos (indica loop o topología dual).",
            "2. Confirmar que los puertos trunk permitan las mismas VLANs en ambos extremos y que la VLAN nativa coincida.",
            "3. Validar el estado del EtherChannel/LACP: interfaces agrupadas, modo activo/pasivo compatible y sin errores de negociación.",
            "4. Revisar Spanning Tree para confirmar que no haya puertos bloqueados inesperadamente en enlaces activos.",
            "5. Inspeccionar contadores de errores de Capa 1 (CRC, runts, giants) que puedan indicar problemas físicos o duplex mismatch.",
        ],
        "expected_evidence": {
            "confirming": [
                "Tabla CAM estable sin flapping de MACs en los últimos 5 minutos.",
                "Puertos trunk con mismas VLANs permitidas y VLAN nativa idéntica en ambos extremos.",
                "EtherChannel/LACP en estado 'bundled' con todas las interfaces en 'I' (in_use) o 'P' (bundled-in-port-channel).",
                "Spanning Tree muestra puertos en estado Forwarding en enlaces activos y Alternate/Backup solo donde es esperado.",
                "Contadores de errores L1 estables (CRC, runts, giants) sin incremento continuo.",
            ],
            "invalidating": [
                "MAC flapping recurrente entre puertos (loop físico o conexión a dos switches sin STP habilitado).",
                "VLAN nativa mismatch en trunk: tráfico untagged procesado en VLAN incorrecta (causa aislamiento de management).",
                "LACP negotiation failed: modos incompatibles (active/passive vs on/off) o velocidades/dúplex desajustadas en miembros.",
                "Spanning Tree bloqueando puertos en enlaces troncales activos por loop detectado o BPDU inconsistency.",
                "Contadores de CRC creciendo (indica problema físico: cable dañado, conector flojo, o duplex mismatch).",
            ],
        },
        "scientific_basis": "La tabla CAM se aprende dinámicamente; el flapping indica inestabilidad de topología o loop. El mismatch de VLAN nativa en trunks es una causa clásica de aislamiento de VLAN management (Cisco Troubleshooting LAN Switching). LACP (802.3ad) requiere coincidencia de velocidad, dúplex y modo de canal en ambos extremos.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque los LEDs del switch están verdes, el enlace está libre de errores. Verifique 'show interface counters errors'.",
            "Un puerto trunk en 'Up/Up' NO garantiza que las VLANs permitidas coincidan. Verifique 'show interfaces trunk allowed'.",
            "Descarte la hipótesis de loop solo si ha verificado la topología física y la consistencia de STP en TODOS los switches del dominio.",
        ],
        "references": [
            "IEEE 802.3ad: Link Aggregation Control Protocol (LACP)",
            "Cisco LAN Switching Configuration Guide",
            "Cisco Live BRKCRS-2501: Campus LAN Troubleshooting",
        ],
        "fix": (
            "1. Eliminar loops físicos o configurar STP/RSTP/MSTP correctamente para resolver MAC flapping.\n"
            "2. Alinear VLAN nativa y VLANs permitidas en ambos extremos de los trunks.\n"
            "3. Corregir negociación LACP asegurando modos compatibles y parámetros idénticos en miembros del EtherChannel.\n"
            "4. Resolver errores físicos (CRC, runts, giants) cambiando cables/SFPs o ajustando dúplex/velocidad.\n"
            "5. Verificar que Spanning Tree no bloquee enlaces activos inesperadamente.\n"
            "6. Validar conectividad L2 entre hosts de la misma VLAN tras los cambios.\n"
        ),
    },
    "fiber_ont.fiber_ont_ts_start": {
        "hypothesis": "La falla de servicio GPON/ONT es causada por un nivel de potencia óptica fuera de rango, una ONT en estado distinto a O5 (Operativo), un error en la provisión OMCI, o un problema de autenticación PPPoE/SIP en la capa de servicio.",
        "verification_steps": [
            "1. Medir la potencia óptica de Tx/Rx en la ONT y la OLT para confirmar que está dentro del rango GPON (-8 a -27 dBm).",
            "2. Verificar el estado de la ONT en la OLT (debe estar en O5 u Online; estados O1-O4 indican falla de sincronización).",
            "3. Confirmar que el número de serie / LOID de la ONT esté correctamente registrado en la OLT y coincida con el equipo físico.",
            "4. Revisar la provisión OMCI: GEM ports, T-CONTs, VLANs y perfiles de servicio asignados a la ONT.",
            "5. Validar la capa de servicio L2/L3: sesión PPPoE establecida, VLAN correcta, o registro SIP VoIP exitoso.",
        ],
        "expected_evidence": {
            "confirming": [
                "Potencia óptica dentro del rango GPON en Tx y Rx (sin alarmas de 'low optical signal').",
                "ONT en estado O5 (Operativo) o 'Online' en la OLT, con OMCI negotiation completado.",
                "Número de serie / LOID registrado y coincidente entre ONT física y base de datos de la OLT.",
                "GEM ports, T-CONTs y VLANs provisionados correctamente en la ONT vía OMCI.",
                "Sesión PPPoE en estado 'Active' o registro SIP en estado 'Registered' con el softswitch.",
            ],
            "invalidating": [
                "Potencia óptica fuera de rango (<-27 dBm o >-8 dBm) causando descarte de tramas o desconexión.",
                "ONT en estado O1 (Inicial) o O2 ( standby) indicando falla de ranging o sincronización óptica.",
                "Número de serie / LOID no registrado o duplicado en la OLT (la ONT no se aprovisiona).",
                "OMCI incompleto: faltan GEM ports o T-CONTs, causando que el tráfico de usuario no tenga canal de datos.",
                "Fallo de autenticación PPPoE (usuario/contraseña incorrectos) o registro SIP rechazado (credenciales o servidor SIP inalcanzable).",
            ],
        },
        "scientific_basis": "GPON (ITU-T G.984) define los umbrales de potencia óptica para operación estable. El estado O5 indica que la ONT completó el ranging, la autenticación de serie y la negociación OMCI. OMCI (ITU-T G.988) configura los servicios L2/L3 de la ONT de forma remota; sin OMCI, la ONT no sabe qué VLANs o GEM ports usar.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la ONT muestra luz verde, la potencia está OK. Use 'show optic' o medidor óptico para confirmar.",
            "Un estado O5 en la OLT NO garantiza que el servicio de datos funcione. Verifique la provisión OMCI y la capa PPPoE/SIP.",
            "Descarte la hipótesis de potencia solo si ha medido en ambos sentidos (Tx OLT -> Rx ONT y Tx ONT -> Rx OLT).",
        ],
        "references": [
            "ITU-T G.984: Gigabit-capable Passive Optical Networks (GPON)",
            "ITU-T G.988: ONU Management and Control Interface (OMCI)",
            "Cisco GPON Troubleshooting Guide",
        ],
        "fix": (
            "1. Ajustar potencia óptica dentro del rango GPON (-8 a -27 dBm) limpiando conectores o cambiando splitter/atenuación.\n"
            "2. Verificar que la ONT alcance estado O5 (Online/Operativo) en la OLT; si no, revisar ranging y serial/LOID.\n"
            "3. Registrar correctamente el número de serie / LOID de la ONT en la base de datos de la OLT.\n"
            "4. Completar provisión OMCI: GEM ports, T-CONTs, VLANs y perfiles de servicio asignados.\n"
            "5. Validar capa de servicio (PPPoE activo, VLAN correcta, SIP registered) con el softswitch.\n"
            "6. Confirmar que el cliente reciba servicio de datos/voz con pruebas end-to-end.\n"
        ),
    },
    "adtran_ta5000.adtran_start": {
        "hypothesis": "La falla en el chasis ADTRAN TA5000 es causada por una tarjeta de línea no detectada, un enlace uplink GE/T1/DS3 caído, una inconsistencia en la redundancia RPR/ERPS, o un problema de sincronización de timing (COT/RT).",
        "verification_steps": [
            "1. Verificar el estado general del chasis: temperatura, ventiladores, fuentes de alimentación y tarjetas de línea (show shelf/slot).",
            "2. Confirmar que los enlaces uplink GE/XE estén activos y sin errores de CRC o descartes en las interfaces de backplane.",
            "3. Revisar el estado de la protección RPR o ERPS para confirmar que no haya nodos aislados o breaks en el anillo.",
            "4. Validar la sincronización de timing: la tarjeta de timing debe estar locked a la referencia primaria (COT) o secundaria (RT).",
            "5. Inspeccionar logs del sistema para detectar alarmas de hardware (tarjeta fault, optical LOS, BERT errors en T1/DS3).",
        ],
        "expected_evidence": {
            "confirming": [
                "Chasis con temperatura normal, ventiladores operativos y fuentes de alimentación redundantes activas.",
                "Enlaces uplink GE/XE en estado Up/Up sin incremento de CRC errors ni output drops.",
                "RPR/ERPS en estado operativo con todos los nodos visibles y sin breaks o steering protection activa.",
                "Timing locked a la referencia primaria (BITS/T1) con wander y jitter dentro de especificación (G.823).",
                "Sin alarmas de hardware críticas en logs (tarjeta fault, optical LOS, BERT clean en interfaces seriales).",
            ],
            "invalidating": [
                "Temperatura crítica o ventilador fallando (posible shutdown automático de tarjetas).",
                "Enlaces uplink con flaps o CRC errors creciendo (cable dañado, SFP defectuoso, o dúplex mismatch).",
                "RPR/ERPS con break en el anillo (cable cortado) causando reconvergencia y posible aislamiento de nodos.",
                "Timing en estado 'freerun' o 'holdover' (falla de referencia primaria y secundaria; deriva de reloj afecta servicios TDM).",
                "Alarmas de tarjeta 'fault', optical LOS en puertos PON, o BERT errors en T1/DS3 (indica problema físico o configuración de línea).",
            ],
        },
        "scientific_basis": "El TA5000 es un chasis multiservicio donde la sincronización de timing es crítica para servicios TDM y GPON. RPR (Resilient Packet Ring) y ERPS (Ethernet Ring Protection Switching) proveen redundancia; un break en el anillo debe converger en <50ms (ITU-T G.8032). La integridad física de las tarjetas y los enlaces uplink es fundamental para la estabilidad del chasis.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el chasis enciende, todas las tarjetas están operativas. Verifique 'show card' o 'show shelf'.",
            "Un enlace GE en 'Up/Up' NO garantiza que el RPR/ERPS esté convergido. Verifique el estado del anillo separadamente.",
            "Descarte la hipótesis de timing solo si ha verificado ambas referencias (primaria y secundaria) y el estado del PLL.",
        ],
        "references": [
            "ADTRAN TA5000 System Manual",
            "ITU-T G.8032: Ethernet Ring Protection Switching",
            "ITU-T G.823: The Control of Jitter and Wander in Digital Networks",
        ],
        "fix": (
            "1. Verificar estado de tarjetas, ventiladores y fuentes; reemplazar hardware fault si es necesario.\n"
            "2. Restaurar enlaces uplink GE/XE activos y sin CRC errors (cable/SFP).\n"
            "3. Resolver breaks en anillo RPR/ERPS para restablecer redundancia en <50ms.\n"
            "4. Sincronizar timing locked a referencia primaria (COT) o secundaria (RT); verificar wander/jitter dentro de G.823.\n"
            "5. Limpiar alarmas de hardware (optical LOS, BERT errors en T1/DS3).\n"
            "6. Confirmar estabilidad del chasis y servicios TDM/GPON tras la corrección.\n"
        ),
    },
    "evc_config.evc_config_start": {
        "hypothesis": "La configuración de Ethernet Virtual Connection (EVC) no produce el comportamiento esperado debido a un error de sintaxis en la definición del EFP (Ethernet Flow Point), un mismatch en la clasificación de VLANs, o una dependencia faltante del bridge-domain.",
        "verification_steps": [
            "1. Verificar que el EFP (service instance) esté configurado con la VLAN correcta y que la sintaxis de clasificación sea válida.",
            "2. Confirmar que el bridge-domain o cross-connect asociado al EFP exista y esté activo.",
            "3. Validar que la encapsulación del EFP (dot1q, qinq, untagged) coincida con el servicio esperado en el puerto de cliente.",
            "4. Revisar que el EVC esté vinculado a la interfaz física correcta y que la interfaz esté en estado Up.",
            "5. Inspeccionar la tabla de forwarding L2 para confirmar que las MACs se aprenden en el EFP y el bridge-domain correctos.",
        ],
        "expected_evidence": {
            "confirming": [
                "EFP configurado con VLAN ID correcto y sintaxis de clasificación válida (verificado con 'show run interface').",
                "Bridge-domain existe, está activo y asociado al EFP (sin errores de vinculación).",
                "Encapsulación del EFP coincide con el C-tag/S-tag del tráfico del cliente (dot1q, qinq pop/push correcto).",
                "EVC aplicado a la interfaz física esperada y la interfaz reporta estado Up/Up.",
                "Tabla de forwarding L2 muestra MACs aprendidas en el EFP y bridge-domain correspondientes.",
            ],
            "invalidating": [
                "Sintaxis de EFP inválida (VLAN fuera de rango, palabra clave mal escrita) causando error de commit.",
                "Bridge-domain no existe o no está asociado al EFP (el servicio no tiene dominio de bridging).",
                "Encapsulación mismatch: EFP espera dot1q 100 pero el cliente envía untagged o double-tagged.",
                "EFP aplicado a interfaz incorrecta o interfaz en Down/Administratively Down.",
                "Tabla de forwarding L2 vacía para el bridge-domain (indica falla de clasificación o tráfico no llega al puerto).",
            ],
        },
        "scientific_basis": "EVC (MEF) define servicios punto a punto (E-Line) y multipunto (E-LAN/E-Tree) mediante EFPs y bridge-domains. Un error de sintaxis en el EFP impide la creación del servicio. La clasificación de VLANs debe coincidir exactamente con la oferta comercial (Cisco EVC Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el bridge-domain existe, el EFP está correctamente vinculado. Verifique 'show bridge-domain'.",
            "Una interfaz en 'Up/Up' NO garantiza que el EFP esté clasificando tráfico. Verifique los contadores del service instance.",
            "Descarte la hipótesis de encapsulación solo si ha capturado tráfico real del cliente y confirmado los tags Ethernet.",
        ],
        "references": [
            "MEF 6.3: Ethernet Services Definitions",
            "Cisco EVC Configuration Guide (IOS-XE)",
            "Cisco Live BRKARC-3445: EVC and L2VPN Design",
        ],
        "fix": (
            "1. Corregir la sintaxis del EFP (service instance) asegurando VLAN ID válido y encapsulación correcta.\n"
            "2. Crear/asociar el bridge-domain o cross-connect al EFP.\n"
            "3. Alinear encapsulación del EFP (dot1q/qinq/untagged) con el tráfico del cliente.\n"
            "4. Aplicar el EVC a la interfaz física correcta y confirmar estado Up/Up.\n"
            "5. Verificar que las MACs se aprendan en el EFP y bridge-domain esperados.\n"
            "6. Confirmar commit exitoso y servicio E-Line/E-LAN operativo.\n"
        ),
    },
    "mpbgp.mpbgp_start": {
        "hypothesis": "La falla de distribución de rutas multiprotocolo es causada por una sesión MP-BGP no establecida (capability mismatch), una address family no activada, o un error en la resolución de next-hop para las NLRI VPN/EVPN.",
        "verification_steps": [
            "1. Verificar que la sesión BGP base (IPv4/IPv6 unicast) esté en estado Established.",
            "2. Confirmar que la address family específica (VPNv4, VPNv6, EVPN, LU) esté activada bajo el neighbor.",
            "3. Validar que el intercambio de capabilities en el OPEN message incluya la AFI/SAFI deseada.",
            "4. Revisar que el Next-Hop de las rutas MP-BGP sea alcanzable vía IGP y resoluble a un label MPLS (si aplica).",
            "5. Inspeccionar políticas de entrada/salida (prefix-lists, route-maps) que puedan filtrar las NLRI multiprotocolo.",
        ],
        "expected_evidence": {
            "confirming": [
                "Sesión BGP base en Established sin NOTIFICATIONs recientes.",
                "Address family VPNv4/VPNv6/EVPN activada bajo el peer (estado 'advertised and received').",
                "Capabilities exchange confirma AFI/SAFI negociada en ambos sentidos (verificar con 'show bgp neighbors').",
                "Next-Hop de rutas MP-BGP alcanzable vía IGP y resuelto a label MPLS en la LFIB.",
                "Políticas de enrutamiento permiten explícitamente las NLRI de interés (sin descarte por community o prefix-list).",
            ],
            "invalidating": [
                "Sesión BGP base en Idle/Active (falla de conectividad TCP 179 o AS mismatch).",
                "Address family no activada bajo el peer (BGP no anuncia ni recibe rutas de esa familia).",
                "Capability mismatch en OPEN: un peer no soporta la AFI/SAFI solicitada (sesión cae a Idle).",
                "Next-Hop de rutas MP-BGP inalcanzable (rutas recibidas pero no instaladas en RIB).",
                "Policy de entrada/salida filtrando NLRI multiprotocolo (rutas recibidas pero descartadas silenciosamente).",
            ],
        },
        "scientific_basis": "MP-BGP (RFC 4760) extiende BGP para soportar múltiples AFI/SAFI mediante atributos MP_REACH_NLRI y MP_UNREACH_NLRI. La address family debe estar explícitamente activada bajo cada neighbor. El Next-Hop debe ser alcanzable para instalar las rutas (RFC 4364, RFC 7432).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque BGP IPv4 está Up, MP-BGP VPNv4 también lo está. Verifique la familia específica.",
            "Un 'show bgp vpnv4 unicast summary' con prefijos recibidos NO garantiza que estén en la VRF. Verifique la RIB.",
            "Descarte la hipótesis de política solo si ha verificado tanto la configuración como los contadores de matches.",
        ],
        "references": [
            "RFC 4760: Multiprotocol Extensions for BGP-4",
            "RFC 4364: BGP/MPLS IP Virtual Private Networks (VPNs)",
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "Cisco Live BRKRST-3320: BGP Troubleshooting Deep Dive",
        ],
        "fix": (
            "1. Establecer sesión BGP base IPv4/IPv6 en Established y abrir TCP 179.\n"
            "2. Activar explícitamente la address family deseada (VPNv4, VPNv6, EVPN, LU) bajo el neighbor.\n"
            "3. Verificar que el capability exchange incluya la AFI/SAFI correcta.\n"
            "4. Asegurar que el Next-Hop de las NLRI sea alcanzable vía IGP y resuelto a label MPLS si aplica.\n"
            "5. Revisar policies de entrada/salida para permitir las NLRI multiprotocolo.\n"
            "6. Confirmar que las rutas MP-BGP se instalen en la RIB/LFIB según corresponda.\n"
        ),
    },
    "linux_tshoot.linux_l1_l2_link": {
        "hypothesis": "La falla de conectividad en Linux es causada por una interfaz física caída, un duplex/speed mismatch, una ruta incorrecta en la tabla de enrutamiento del kernel, o reglas de firewall/nat descartando el tráfico antes de que alcance la interfaz de salida.",
        "verification_steps": [
            "1. Verificar el estado del enlace físico con 'ip link show' y 'ethtool' (flags UP, LOWER_UP, Link detected: yes).",
            "2. Confirmar que la velocidad y el dúplex negociados coincidan con el equipo remoto (evitar half-duplex en Gigabit).",
            "3. Validar la tabla de rutas y reglas de policy routing ('ip route', 'ip rule') para confirmar el path de salida correcto.",
            "4. Revisar la tabla ARP/NDP ('ip neigh') para confirmar que el gateway vecino está resuelto a nivel L2.",
            "5. Inspeccionar iptables/nftables y conntrack para descartar bloqueos de firewall o tabla de conexiones agotada.",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaz en estado UP con flag LOWER_UP y 'ethtool' reporta Link detected: yes.",
                "Velocidad y dúplex coinciden en ambos extremos (ej. 1000Mb/s Full en ambos lados).",
                "'ip route get <dest>' muestra la interfaz y gateway correctos sin conflictos de policy routing.",
                "Neighbor Cache muestra gateway en estado REACHABLE con MAC resuelta.",
                "iptables/nftables permite el tráfico de interés y conntrack_count < 80% de conntrack_max.",
            ],
            "invalidating": [
                "Interfaz en estado DOWN o sin LOWER_UP (cable desconectado, módulo SFP no detectado).",
                "Duplex mismatch: un extremo en Full y el otro en Half (colisiones excesivas y throughput degradado).",
                "'ip route get <dest>' apunta a interfaz incorrecta o gateway inalcanzable (policy routing desviando tráfico).",
                "Neighbor Cache con gateway en FAILED (ARP/NDP no responde; posible VLAN o segmento L2 incorrecto).",
                "iptables DROP/REJECT en cadena FORWARD o conntrack_max alcanzado (nuevas conexiones descartadas silenciosamente).",
            ],
        },
        "scientific_basis": "El kernel Linux utiliza el stack iproute2 para L3 y netfilter para firewall. Un enlace físico caído es la causa raíz más común. El conntrack agotado (nf_conntrack_max) provoca descarte silencioso de nuevas conexiones sin logs visibles (Linux Netfilter documentation). Policy routing (ip rule) puede desviar paquetes a tablas de rutas no esperadas.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'ping localhost' funciona, la interfaz física está OK. Verifique el estado de carrier.",
            "Una tabla de rutas 'correcta' en la tabla principal NO excluye reglas de policy routing que desvíen el tráfico. Verifique 'ip rule show'.",
            "Descarte la hipótesis de firewall solo si ha probado con 'iptables -F' o 'nft flush ruleset' en un entorno controlado.",
        ],
        "references": [
            "Linux iproute2 Documentation",
            "Linux Netfilter Documentation",
            "RFC 792: Internet Control Message Protocol (ICMP)",
        ],
        "fix": (
            "1. Levantar la interfaz física ('ip link set up') y resolver problemas de cable/SFP/módulo.\n"
            "2. Alinear velocidad y dúplex con el equipo remoto (evitar half-duplex en Gigabit).\n"
            "3. Corregir tabla de rutas y reglas de policy routing ('ip route'/'ip rule') para el path de salida.\n"
            "4. Resolver ARP/NDP FAILED verificando VLAN/segmento L2 y reachability del gateway.\n"
            "5. Ajustar iptables/nftables para permitir el tráfico de interés y liberar conntrack si está saturado.\n"
            "6. Validar conectividad con ping/traceroute y verificar throughput esperado.\n"
        ),
    },
    "nat.nat_tshoot_start": {
        "hypothesis": "La falla de traducción de direcciones NAT es causada por una ACL de inside/outside mal definida, un pool de direcciones agotado, un conflicto de puertos (PAT exhaustion), o una ruta de retorno que no pasa por el mismo dispositivo NAT.",
        "verification_steps": [
            "1. Verificar que las interfaces estén correctamente clasificadas como inside o outside (dirección del tráfico relativa a NAT).",
            "2. Confirmar que la ACL de inside source coincida con el tráfico de origen que debe ser traducido.",
            "3. Validar que el pool de direcciones NAT o la IP de overload (PAT) tengan capacidad suficiente (sin agotamiento de puertos).",
            "4. Revisar la tabla de traducciones activas ('show ip nat translations') para confirmar que las entradas se crean y envejecen correctamente.",
            "5. Asegurar que el tráfico de retorno llegue al mismo dispositivo NAT para que la traducción inversa pueda aplicarse (asymmetric routing).",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaces correctamente clasificadas como inside/outside en la configuración NAT.",
                "ACL de inside source tiene contadores de match para el tráfico de los hosts privados de interés.",
                "Pool NAT con direcciones disponibles; PAT con puertos TCP/UDP disponibles (>10% libres).",
                "Tabla de traducciones NAT muestra entradas dinámicas activas incrementándose con el tráfico de prueba.",
                "Tráfico de retorno simétrico: el mismo dispositivo NAT ve el flujo en ambas direcciones.",
            ],
            "invalidating": [
                "Interfaces mal clasificadas (inside en interfaz WAN o outside en LAN) causando falla de traducción.",
                "ACL de inside source demasiado restrictiva (no incluye la subnet del cliente; contadores en cero).",
                "Pool NAT agotado o PAT con todos los puertos de la IP pública en uso (nuevas conexiones rechazadas).",
                "Tabla NAT vacía a pesar del tráfico de prueba (indica falla de clasificación o ACL no haciendo match).",
                "Asymmetric routing: el tráfico de retorno llega por otro path y no pasa por el NAT device (conexión half-open).",
            ],
        },
        "scientific_basis": "NAT (RFC 3022) requiere que el tráfico atraviese las interfaces correctamente clasificadas. La ACL define qué flujos se traducen. PAT (NAPT, RFC 3022) puede agotar los ~64,000 puertos por IP pública. El asymmetric routing rompe las traducciones stateful porque el dispositivo no ve el flujo de retorno (Cisco NAT Troubleshooting Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la ACL tiene 'permit ip any any', está haciendo match. Verifique la dirección del tráfico (inside vs outside).",
            "Un 'show ip nat translations' vacío puede deberse a interfaces no clasificadas, no solo a falta de tráfico.",
            "Descarte la hipótesis de agotamiento de pool solo si ha verificado el conteo de entradas dinámicas vs el tamaño del pool.",
        ],
        "references": [
            "RFC 3022: Traditional IP Network Address Translator (Traditional NAT)",
            "Cisco NAT Troubleshooting and Design Guide",
            "Cisco Live BRKRST-3320: NAT Deep Dive",
        ],
        "fix": (
            "1. Clasificar correctamente interfaces como inside/outside según dirección del tráfico.\n"
            "2. Ajustar ACL de inside source para que incluya las subnets privadas de interés.\n"
            "3. Ampliar pool NAT o habilitar PAT (overload) si se agotan direcciones/puertos.\n"
            "4. Asegurar que el tráfico de retorno sea simétrico y pase por el mismo dispositivo NAT.\n"
            "5. Verificar tabla de traducciones activas y envejecimiento correcto.\n"
            "6. Probar conexiones desde hosts internos y confirmar traducción exitosa.\n"
        ),
    },
    "static.static_start": {
        "hypothesis": "La falla de enrutamiento estático es causada por una ruta configurada pero no instalada en la RIB debido a un next-hop inalcanzable, una distancia administrativa peor que una ruta dinámica, o un loop de resolución recursiva.",
        "verification_steps": [
            "1. Verificar que la ruta estática esté presente en la configuración y en la tabla de rutas (RIB) con estado activo.",
            "2. Confirmar que el next-hop configurado sea alcanzable directamente o resoluble vía una ruta IGP/BGP válida.",
            "3. Revisar la distancia administrativa/preferencia de la ruta estática frente a otras rutas hacia el mismo destino.",
            "4. Validar que la interfaz de salida especificada esté en estado Up/Up (si se usó sintaxis de interfaz de salida).",
            "5. Buscar bucles recursivos donde el next-hop de la ruta estática dependa indirectamente de la propia ruta estática.",
        ],
        "expected_evidence": {
            "confirming": [
                "Ruta estática visible en 'show ip route' con código 'S' y estado activo (no 'inactive').",
                "Next-hop alcanzable directamente o resuelto a través de una ruta IGP válida en la RIB.",
                "Distancia administrativa de la ruta estática menor que la de la ruta dinámica competidora (ej. 1 < 110 de OSPF).",
                "Interfaz de salida en estado Up/Up (si la ruta usa sintaxis de salida por interfaz).",
                "Sin mensajes de 'recursive routing failure' o loop en logs al instalar la ruta estática.",
            ],
            "invalidating": [
                "Ruta estática configurada pero ausente en la RIB (next-hop inalcanzable o interfaz de salida Down).",
                "Next-hop no resoluble: no existe ruta IGP hacia la IP del next-hop (ruta estática permanece 'inactive').",
                "Distancia administrativa mayor que OSPF/IS-IS/BGP: la ruta dinámica gana y la estática nunca se instala.",
                "Interfaz de salida Down/Administratively Down (ruta estática removida automáticamente de la FIB).",
                "Loop recursivo: el next-hop de la ruta estática se resuelve usando la misma ruta estática (causa CPU spike y descarte).",
            ],
        },
        "scientific_basis": "El enrutamiento estático se instala en la RIB solo si el next-hop es alcanzable. Si el next-hop cae, la ruta se retira (excepto si se usa 'permanent'). Una distancia administrativa más alta que un IGP hace que la ruta estática sea invisible para forwarding (Cisco IP Routing Reference). La resolución recursiva infinita consume CPU y puede causar inestabilidad.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la ruta aparece en 'show running-config', está en la FIB. Verifique 'show ip route' y 'show ip cef'.",
            "Un next-hop alcanzable por ping NO garantiza que la interfaz de salida esté en la FIB. Verifique la resolución recursiva.",
            "Descarte la hipótesis de distancia administrativa solo si ha comparado explícitamente los valores de AD de todas las rutas al destino.",
        ],
        "references": [
            "Cisco IP Routing Configuration Guide",
            "Juniper Routing Protocols Configuration Guide",
            "Cisco Live BRKRST-3035: Advanced IP Routing Troubleshooting",
        ],
        "fix": (
            "1. Corregir sintaxis de la ruta estática (red, máscara, next-hop o interfaz de salida).\n"
            "2. Asegurar que el next-hop sea alcanzable directamente o resoluble vía IGP.\n"
            "3. Ajustar distancia administrativa para que la ruta gane frente a rutas dinámicas según diseño.\n"
            "4. Confirmar que la interfaz de salida esté Up/Up si se usa sintaxis de salida por interfaz.\n"
            "5. Configurar track IP SLA o BFD para retiro automático si el path falla.\n"
            "6. Verificar que la ruta esté instalada en RIB/FIB ('show ip route'/'show ip cef').\n"
        ),
    },
    "ccc_interface_switch.ccc_start": {
        "hypothesis": "La falla del circuito CCC es causada por una sesión Targeted LDP caída entre los PEs, un mismatch en el VC-ID o tipo de encapsulación, o una interfaz de Attachment Circuit (AC) no operativa.",
        "verification_steps": [
            "1. Verificar que la sesión Targeted LDP entre los loopbacks de los PEs esté en estado Established.",
            "2. Confirmar que el VC-ID y el tipo de encapsulación (VLAN vs Ethernet) coincidan exactamente en ambos extremos del pseudowire.",
            "3. Validar que la interfaz de Attachment Circuit (AC) esté en estado Up/Up y configurada en la VLAN/puerto correcto.",
            "4. Revisar la MTU de la interfaz AC y del core MPLS para asegurar que soporte el overhead de etiquetas MPLS.",
            "5. Inspeccionar la tabla de forwarding MPLS y el estado del pseudowire para confirmar que el label de VC esté programado.",
        ],
        "expected_evidence": {
            "confirming": [
                "Targeted LDP session Established entre loopbacks de PE origen y destino.",
                "VC-ID idéntico y encapsulación coincidente (VLAN o Ethernet) en ambos extremos del pseudowire.",
                "Interfaz AC en Up/Up con family bridge/ethernet-switching o encapsulación VLAN según el servicio.",
                "MTU de AC y core MPLS >= 1504 bytes (para soportar al menos 1 label de VC + overhead MPLS).",
                "Pseudowire en estado Up con label de VC local y remoto instalados en la LFIB.",
            ],
            "invalidating": [
                "Targeted LDP session Down (transport-address inalcanzable o firewall bloqueando TCP 646).",
                "VC-ID mismatch: un PE usa VC-ID 100 y el otro 101 (pseudowire no se establece).",
                "Interfaz AC en Down/Down o sin VLAN configurada (tráfico del cliente no ingresa al pseudowire).",
                "MTU insuficiente en AC o core MPLS (paquetes de datos descartados silenciosamente).",
                "Pseudowire en estado Down o 'no remote label' (falta de binding LDP para la FEC del VC-ID).",
            ],
        },
        "scientific_basis": "CCC (Circuit Cross-Connect) en Juniper utiliza Targeted LDP para señalizar el pseudowire (RFC 4447, FEC 128). El VC-ID y el tipo de encapsulación deben coincidir exactamente. La MTU insuficiente es una causa insidiosa de descarte silencioso (RFC 4623).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el LDP de tránsito está Up, el Targeted LDP también lo está. Verifique la sesión explícitamente.",
            "Un pseudowire 'Up' en un solo extremo NO garantiza que el otro extremo esté Up. Verifique ambos PEs.",
            "Descarte la hipótesis de MTU solo si ha verificado el path completo incluyendo las interfaces de AC y los P routers intermedios.",
        ],
        "references": [
            "RFC 4447: Pseudowire Setup and Maintenance Using the Label Distribution Protocol",
            "RFC 4623: Pseudowire Emulation Edge-to-Edge (PWE3) Fragmentation and Reassembly",
            "Juniper CCC and L2Circuit Troubleshooting Guide",
        ],
        "fix": (
            "1. Establecer sesión Targeted LDP Established entre loopbacks de PE.\n"
            "2. Corregir VC-ID y tipo de encapsulación (VLAN/Ethernet) para que coincidan exactamente en ambos extremos.\n"
            "3. Asegurar que la interfaz AC esté Up/Up y en la VLAN/puerto correcto.\n"
            "4. Aumentar MTU de AC y core MPLS para soportar overhead de labels (>=1504 bytes).\n"
            "5. Verificar que el pseudowire esté Up con labels de VC locales y remotos en LFIB.\n"
            "6. Validar conectividad L2 del cliente a través del circuito CCC.\n"
        ),
    },
    "wireshark_tcpdump.pcap_start": {
        "hypothesis": "La falla de diagnóstico por captura de paquetes es causada por una captura en la interfaz incorrecta, un filtro BPF demasiado restrictivo, la falta de modo promiscuo/SPAN, o un buffer de captura insuficiente que provoca pérdida de paquetes.",
        "verification_steps": [
            "1. Verificar que la captura se realice en la interfaz física/lógica correcta (incluyendo VLANs, túneles o subinterfaces).",
            "2. Confirmar que el filtro BPF (tcpdump) o display filter (Wireshark) no esté descartando paquetes relevantes.",
            "3. Validar que la NIC esté en modo promiscuo o que el puerto del switch tenga SPAN/RSPAN configurado para reenviar el tráfico.",
            "4. Revisar los contadores de paquetes capturados vs paquetes recibidos por la interfaz para detectar pérdida por buffer insuficiente.",
            "5. Asegurar que la resolución de nombres no esté habilitada durante la captura (puede ralentizar y causar pérdida de paquetes en alta velocidad).",
        ],
        "expected_evidence": {
            "confirming": [
                "Captura en la interfaz correcta donde fluye el tráfico de interés (confirmado con 'tcpdump -D' o Wireshark GUI).",
                "Filtro BPF permite explícitamente el tráfico relevante (host, port, proto) sin restricciones ocultas.",
                "NIC en modo promiscuo o SPAN/RSPAN configurado en el switch para redirigir tráfico al puerto de captura.",
                "Sin pérdida de paquetes por buffer ('packets dropped by kernel' en cero durante la captura).",
                "Resolución de nombres deshabilitada (-n en tcpdump) para evitar latencia en interfaces de alta velocidad.",
            ],
            "invalidating": [
                "Captura en interfaz incorrecta (ej. loopback en lugar de eth0) que no ve el tráfico de red.",
                "Filtro BPF demasiado restrictivo (ej. 'tcp port 80' cuando el tráfico usa HTTPS 443).",
                "NIC sin modo promiscuo o SPAN no configurado (solo se ven paquetes unicast dirigidos a la MAC de la capturadora).",
                "Buffer de kernel insuficiente causando 'packets dropped by kernel' (pérdida de paquetes críticos).",
                "Resolución de nombres habilitada causando delay y pérdida de paquetes en tráfico de >1 Gbps.",
            ],
        },
        "scientific_basis": "tcpdump y Wireshark utilizan libpcap para capturar tramas crudas del kernel. Un filtro BPF mal diseñado descarta paquetes en el kernel antes de entregarlos a userspace. La ausencia de modo promiscuo o SPAN hace que solo se capturen frames dirigidos a la MAC local, ocultando broadcast y tráfico de terceros. El buffer de captura debe dimensionarse con '-B' en tcpdump para interfaces de alta velocidad (libpcap documentation).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque Wireshark muestra paquetes, la captura es representativa. Verifique 'packets dropped'.",
            "Una captura vacía NO significa que no haya tráfico; puede deberse a un filtro BPF que descarta todo antes de entregarlo.",
            "Descarte la hipótesis de interfaz incorrecta solo si ha verificado la topología física y los puntos de SPAN.",
        ],
        "references": [
            "tcpdump Manual (libpcap)",
            "Wireshark User Guide",
            "RFC 793: Transmission Control Protocol (para interpretación de flags TCP)",
        ],
        "fix": (
            "1. Capturar en la interfaz física/lógica correcta donde fluye el tráfico de interés.\n"
            "2. Relajar o corregir el filtro BPF/display filter para no descartar paquetes relevantes.\n"
            "3. Habilitar modo promiscuo en la NIC o configurar SPAN/RSPAN en el switch.\n"
            "4. Aumentar el buffer de captura ('-B' en tcpdump) para interfaces de alta velocidad.\n"
            "5. Deshabilitar resolución de nombres (-n) durante capturas en alta velocidad.\n"
            "6. Confirmar que no haya 'packets dropped by kernel' y que la captura sea representativa.\n"
        ),
    },
    "ip_trace.ip_trace_start": {
        "hypothesis": "La falla de rastreo de paquetes end-to-end es causada por un error en la resolución ARP/NDP en el origen, una ruta faltante en un salto intermedio, un firewall/ACL bloqueando ICMP Time Exceeded, o NAT asimétrico que cambia el path de retorno.",
        "verification_steps": [
            "1. Verificar la resolución ARP/NDP en el host de origen para confirmar que el gateway L2 está accesible.",
            "2. Ejecutar traceroute/traceroute6 para identificar el último salto alcanzable y el primero que no responde.",
            "3. Validar la tabla de rutas en cada salto intermedio para confirmar que existe una ruta de retorno hacia el origen.",
            "4. Revisar ACLs y firewalls en los saltos intermedios que puedan bloquear ICMP Time Exceeded o el puerto de destino.",
            "5. Confirmar que el path de ida y el de vuelta sean simétricos (mismos dispositivos NAT en ambas direcciones).",
        ],
        "expected_evidence": {
            "confirming": [
                "ARP/NDP resuelto en el origen; gateway L2 alcanzable con ping al primer salto.",
                "Traceroute alcanza el destino final en <=30 saltos con respuestas ICMP/UDP/TCP consistentes.",
                "Cada salto intermedio tiene ruta de retorno hacia la IP de origen (sin blackholing por ruta faltante).",
                "Sin ACLs descartando ICMP Time Exceeded o mensajes de puerto inalcanzable en los routers del path.",
                "Path simétrico: NAT de ida y vuelta aplicado por los mismos dispositivos (mismas IPs traducidas en ambos sentidos).",
            ],
            "invalidating": [
                "ARP/NDP no resuelto en el origen (host no puede enviar el primer paquete al gateway).",
                "Traceroute se detiene en un salto intermedio (router sin ruta hacia el destino o hacia la IP de origen).",
                "Ruta de retorno faltante en un salto intermedio (asymmetric routing causa descarte silencioso).",
                "ACL/firewall bloqueando ICMP Time Exceeded (traceroute no recibe respuesta pero el paquete sí avanza).",
                "NAT asimétrico: el path de ida usa un NAT y el de vuelta otro, causando que el flujo no se reconozca.",
            ],
        },
        "scientific_basis": "Traceroute funciona enviando paquetes con TTL incrementado y esperando respuestas ICMP Time Exceeded (RFC 792). Un firewall que bloquea ICMP Time Exceeded hace que un salto aparezca como '*' aunque el paquete sí avanza. La asimetría de rutas (asymmetric routing) es una causa frecuente de fallas intermitentes que traceroute no puede detectar completamente.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un salto aparece como '*' en traceroute, el router está caído. Puede estar bloqueando ICMP.",
            "Un ping exitoso al destino NO garantiza un path simétrico. Use traceroute desde ambos extremos para comparar.",
            "Descarte la hipótesis de ruta faltante solo si ha verificado la RIB en el salto intermedio donde traceroute se detiene.",
        ],
        "references": [
            "RFC 792: Internet Control Message Protocol",
            "RFC 1393: Traceroute Using an IP Option",
            "Cisco IP Routing Troubleshooting Guide",
        ],
        "fix": (
            "1. Resolver ARP/NDP en el host origen para alcanzar el gateway L2.\n"
            "2. Corregir rutas faltantes en cada salto intermedio para llegar al destino y retornar.\n"
            "3. Abrir ICMP Time Exceeded y puerto inalcanzable en firewalls/ACLs intermedios.\n"
            "4. Asegurar path simétrico de ida y vuelta (mismos dispositivos NAT en ambas direcciones).\n"
            "5. Usar traceroute/traceroute6 con protocolo adecuado (ICMP/UDP/TCP) según el firewall.\n"
            "6. Confirmar que se alcanza el destino final sin saltos perdidos por ACL.\n"
        ),
    },
    "l2vpn.l2vpn_start": {
        "hypothesis": "La falla de conectividad L2VPN es causada por una sesión de señalización LDP/BGP caída, un VC-ID o FEC mismatch, una interfaz AC no operativa, o una MTU insuficiente en el Attachment Circuit o en el core MPLS.",
        "verification_steps": [
            "1. Verificar que la sesión de señalización (Targeted LDP o BGP L2VPN) esté establecida entre los PEs.",
            "2. Confirmar que el VC-ID (para LDP FEC 128) o los parámetros BGP (para FEC 129) coincidan en ambos extremos.",
            "3. Validar que la interfaz AC (Attachment Circuit) esté en estado Up/Up y configurada con la VLAN correcta.",
            "4. Revisar la MTU del AC y del core para asegurar que soporten el overhead de etiquetas MPLS y del Control Word.",
            "5. Inspeccionar el estado del pseudowire y la tabla LFIB para confirmar que los labels de VC estén programados.",
        ],
        "expected_evidence": {
            "confirming": [
                "Sesión Targeted LDP o BGP L2VPN en estado Established/Operational.",
                "VC-ID idéntico y encapsulación coincidente (Ethernet o VLAN) en ambos PEs.",
                "Interfaz AC en estado Up/Up con la VLAN de servicio correcta.",
                "MTU de AC >= 1504 bytes y MTU de core MPLS >= AC + overhead de labels (ej. 1508 para dos labels).",
                "Pseudowire en estado Up con labels de VC local y remoto instalados en la LFIB.",
            ],
            "invalidating": [
                "Sesión LDP/BGP caída (transport-address inalcanzable o firewall bloqueando señalización).",
                "VC-ID mismatch (un PE usa 200, el otro 201) causando rechazo del pseudowire.",
                "Interfaz AC en Down/Down o VLAN incorrecta (tráfico del cliente no ingresa al pseudowire).",
                "MTU insuficiente en AC o core (paquetes grandes descartados silenciosamente sin fragmentación).",
                "Pseudowire Down o sin label remoto (falta de binding en la base de datos de señalización).",
            ],
        },
        "scientific_basis": "L2VPN VPWS (RFC 4447) utiliza LDP FEC 128 para señalizar pseudowires. El VC-ID debe coincidir exactamente. La encapsulación Ethernet vs VLAN define si se transporta el tag del cliente (RFC 4448). La MTU del AC debe considerar el overhead de etiquetas MPLS para evitar descarte silencioso.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el LDP de tránsito está Up, el Targeted LDP para el pseudowire también lo está.",
            "Un pseudowire 'Up' en un solo PE NO garantiza conectividad end-to-end. Verifique ambos lados y el AC.",
            "Descarte la hipótesis de MTU solo si ha verificado con pings de tamaño máximo con DF en el AC y el core.",
        ],
        "references": [
            "RFC 4447: Pseudowire Setup and Maintenance Using LDP",
            "RFC 4448: Encapsulation Methods for Transport of Ethernet over MPLS Networks",
            "Cisco L2VPN Troubleshooting Guide",
        ],
        "fix": (
            "1. Restablecer sesión de señalización Targeted LDP o BGP L2VPN Established entre PEs.\n"
            "2. Corregir VC-ID/FEC y encapsulación (Ethernet/VLAN) para que coincidan en ambos PEs.\n"
            "3. Asegurar que la interfaz AC esté Up/Up con VLAN de servicio correcta.\n"
            "4. Aumentar MTU del AC y core MPLS para soportar labels y Control Word.\n"
            "5. Verificar pseudowire Up con labels de VC local/remoto instalados en LFIB.\n"
            "6. Validar conectividad L2 end-to-end entre sites del cliente.\n"
        ),
    },
    "mpls_config.mpls_config_start": {
        "hypothesis": "La configuración MPLS no produce el comportamiento esperado debido a un error de sintaxis en la habilitación de 'family mpls', un orden incorrecto en la configuración de LDP (global vs interfaz), o una dependencia faltante de IGP para anunciar la loopback /32.",
        "verification_steps": [
            "1. Verificar que MPLS esté habilitado globalmente y en las interfaces físicas (family mpls / mpls ip).",
            "2. Confirmar que LDP o RSVP esté configurado en el nivel correcto (global, área, o interfaz) según el vendor.",
            "3. Validar que la interfaz loopback tenga una /32 configurada y esté incluida en el proceso IGP (OSPF/IS-IS).",
            "4. Revisar que no existan errores de commit o sintaxis en la configuración (comandos rechazados por el parser).",
            "5. Inspeccionar que la transport-address (LSR-ID) apunte a la loopback principal y no a una interfaz física inestable.",
        ],
        "expected_evidence": {
            "confirming": [
                "MPLS habilitado globalmente y en interfaces físicas sin errores de sintaxis.",
                "LDP/RSVP configurado en el nivel adecuado (global + interfaces) con commit exitoso.",
                "Loopback principal con /32 configurada y anunciada activamente en IGP.",
                "Sin errores de parser ni advertencias de dependencias faltantes en el commit de configuración.",
                "Transport-address/LSR-ID configurada explícitamente como la IP de loopback principal.",
            ],
            "invalidating": [
                "MPLS habilitado globalmente pero no en la interfaz física (comando faltante en subinterfaz lógica).",
                "LDP configurado en interfaz antes de habilitarlo globalmente (orden de comandos incorrecto; sesión no inicia).",
                "Loopback /32 no incluida en IGP (transport-address inalcanzable para los peers LDP).",
                "Errores de sintaxis en el commit (ej. 'family mpls' en interfaz que no lo soporta).",
                "Transport-address apuntando a interfaz física (cambio de IP al flapear causa caída de sesiones LDP).",
            ],
        },
        "scientific_basis": "La habilitación de MPLS requiere coordinación entre configuración global e interfaces. Según RFC 5036, la transport-address debe ser una interfaz estable (preferentemente loopback). Un error de orden en la configuración puede dejar el protocolo en estado incompleto (Juniper/Cisco commit model).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el commit fue exitoso, MPLS está operativo. Verifique 'show mpls interface'.",
            "Una interfaz con 'mpls ip' en la configuración NO garantiza que la subinterfaz lógica también lo tenga.",
            "Descarte la hipótesis de IGP solo si ha verificado que la loopback aparece en 'show route' de los peers.",
        ],
        "references": [
            "RFC 5036: LDP Specification",
            "Cisco MPLS Configuration Guide",
            "Juniper MPLS Configuration Guide",
        ],
        "fix": (
            "1. Habilitar MPLS globalmente y en interfaces físicas/subinterfaces ('family mpls'/'mpls ip').\n"
            "2. Configurar LDP/RSVP en el orden correcto (global antes de interfaz) según vendor.\n"
            "3. Anunciar la loopback /32 en el proceso IGP (OSPF/IS-IS).\n"
            "4. Apuntar transport-address/LSR-ID a la loopback principal y no a interfaz física.\n"
            "5. Resolver errores de sintaxis o dependencias faltantes en el commit.\n"
            "6. Confirmar que las interfaces MPLS aparecen operativas ('show mpls interface').\n"
        ),
    },
    "bgp_config.bgp_config_start": {
        "hypothesis": "La configuración BGP no produce el comportamiento esperado debido a un error de sintaxis en el neighbor statement, una address family no activada, un update-source incorrecto, o una política de enrutamiento aplicada en el sentido equivocado.",
        "verification_steps": [
            "1. Verificar que el neighbor esté definido con la IP correcta y el AS remoto coincida con el diseño.",
            "2. Confirmar que la address family deseada (IPv4 unicast, VPNv4, EVPN) esté activada bajo el neighbor.",
            "3. Validar el update-source para iBGP (debe ser la loopback, no la interfaz física).",
            "4. Revisar que las políticas de entrada/salida (route-maps, prefix-lists) estén aplicadas en la dirección correcta.",
            "5. Inspeccionar posibles errores de commit por comandos no soportados en la versión de software actual.",
        ],
        "expected_evidence": {
            "confirming": [
                "Neighbor configurado con IP y AS correctos, sin errores de sintaxis en el commit.",
                "Address family activada explícitamente bajo el peer (estado 'advertised and received').",
                "Update-source apunta a loopback principal para iBGP; eBGP multihop configurado si aplica.",
                "Políticas de entrada/salida aplicadas en la dirección correcta (route-map in vs out).",
                "Commit exitoso sin advertencias de comandos obsoletos o no soportados.",
            ],
            "invalidating": [
                "Sintaxis de neighbor incorrecta (IP mal escrita o AS remoto equivocado).",
                "Address family no activada (BGP no anuncia rutas de esa familia a pesar de que la sesión base está Up).",
                "Update-source por defecto a interfaz física en iBGP (causa inestabilidad por flaps de sesión).",
                "Política de entrada aplicada como salida (prefijos filtrados en el sentido equivocado).",
                "Comando no soportado en la versión actual (advertencia de parser o rollback parcial).",
            ],
        },
        "scientific_basis": "BGP (RFC 4271) requiere que cada address family se active explícitamente bajo el peer para intercambiar NLRI. El update-source incorrecto en iBGP es una causa común de flaps de sesión. Las políticas deben aplicarse en la dirección correcta para evitar filtrado accidental (Cisco BGP Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show ip bgp summary' muestra el peer, la VPNv4/EVPN está activa. Verifique la familia.",
            "Un commit exitoso NO garantiza que todas las líneas de la política sean válidas. Verifique 'show route-map'.",
            "Descarte la hipótesis de update-source solo si ha verificado la estabilidad de la sesión durante al menos 5 minutos.",
        ],
        "references": [
            "RFC 4271: A Border Gateway Protocol 4 (BGP-4)",
            "Cisco BGP Configuration Guide",
            "Juniper BGP Configuration Guide",
        ],
        "fix": (
            "1. Corregir IP y AS remoto en el neighbor statement.\n"
            "2. Activar explícitamente la address family deseada bajo el neighbor.\n"
            "3. Configurar update-source a loopback para iBGP; aplicar eBGP multihop si aplica.\n"
            "4. Aplicar route-maps/prefix-lists en la dirección correcta (in/out).\n"
            "5. Verificar compatibilidad de comandos con la versión de software.\n"
            "6. Confirmar sesión BGP Established y recepción/anuncio de prefijos.\n"
        ),
    },
    "l3vpn_config.l3vpn_config_start": {
        "hypothesis": "La configuración L3VPN no produce el comportamiento esperado debido a un RD/RT mal formado, una VRF no asociada a la interfaz del cliente, o una redistribución incorrecta del protocolo PE-CE hacia MP-BGP.",
        "verification_steps": [
            "1. Verificar que la VRF esté definida con un RD único y los RTs de import/export correctos.",
            "2. Confirmar que la interfaz física/subinterfaz del cliente esté asociada a la VRF (binding correcto).",
            "3. Validar que el protocolo PE-CE (OSPF, BGP, estático) esté configurado dentro del contexto de la VRF.",
            "4. Revisar que la redistribución desde el protocolo PE-CE hacia MP-BGP VPNv4 esté habilitada y sin filtros.",
            "5. Inspeccionar que la sesión MP-BGP esté activa y que la address family VPNv4/VPNv6 esté negociada.",
        ],
        "expected_evidence": {
            "confirming": [
                "VRF definida con RD único y RTs de import/export correctos y consistentes entre PEs.",
                "Interfaz de cliente vinculada a la VRF (aparece en 'show vrf interfaces' o equivalente).",
                "Protocolo PE-CE configurado dentro del contexto de la VRF (no en la tabla global).",
                "Redistribución habilitada desde PE-CE hacia MP-BGP sin route-map de deny explícito.",
                "Sesión MP-BGP VPNv4 activa con capabilities negociadas y rutas presentes en la VPNv4 RIB.",
            ],
            "invalidating": [
                "RD duplicado o mal formado (rutas VPNv4 no únicas en el core).",
                "Interfaz de cliente no asociada a la VRF (tráfico ingresa a la tabla global, no a la VRF).",
                "Protocolo PE-CE configurado en la tabla global en lugar del contexto VRF (rutas no redistribuidas a MP-BGP).",
                "Redistribución omitida o con route-map deny que filtra todos los prefijos del cliente.",
                "Sesión MP-BGP sin address family VPNv4 activada (rutas locales no se anuncian al PE remoto).",
            ],
        },
        "scientific_basis": "L3VPN (RFC 4364) requiere RD para unicidad de prefijos y RT para control de importación/exportación. La interfaz debe estar explícitamente en la VRF. La redistribución debe ocurrir dentro del contexto de la VRF para que las rutas lleguen a MP-BGP (Cisco L3VPN Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la VRF existe, la interfaz está en ella. Verifique el binding de interfaz explícitamente.",
            "Una sesión MP-BGP Up NO garantiza que las rutas del cliente estén siendo anunciadas. Verifique la redistribución.",
            "Descarte la hipótesis de RT solo si ha verificado los RTs en ambos PEs (origen y destino) y en todas las VRFs involucradas.",
        ],
        "references": [
            "RFC 4364: BGP/MPLS IP Virtual Private Networks (VPNs)",
            "Cisco L3VPN Configuration Guide",
            "Juniper Layer 3 VPNs Configuration Guide",
        ],
        "fix": (
            "1. Definir VRF con RD único y RTs de import/export correctos.\n"
            "2. Asociar explícitamente la interfaz PE-CE a la VRF.\n"
            "3. Configurar el protocolo PE-CE dentro del contexto de la VRF (no global).\n"
            "4. Habilitar redistribución del protocolo PE-CE hacia MP-BGP VPNv4/VPNv6.\n"
            "5. Activar sesión MP-BGP y address family VPNv4/VPNv6.\n"
            "6. Verificar que los prefijos del cliente aparezcan en VPNv4 RIB y VRF remota.\n"
        ),
    },
    "evpn_config.evpn_config_start": {
        "hypothesis": "La configuración EVPN no produce el comportamiento esperado debido a un RD/RT duplicado, una MAC-VRF no asociada al bridge domain local, una VLAN-to-EVI mapping incorrecta, o la falta de activación de la familia EVPN en BGP.",
        "verification_steps": [
            "1. Verificar que la familia EVPN (AFI/SAFI 25/70) esté activada bajo la sesión BGP en ambos PEs/VTEPs.",
            "2. Confirmar que el RD y los RTs de la MAC-VRF coincidan con el diseño y no estén duplicados en el dominio.",
            "3. Validar que el bridge domain o VLAN local esté mapeado correctamente a la EVI (EVPN Instance).",
            "4. Revisar que las interfaces de acceso (AC) estén en estado Up y asociadas al bridge domain/VLAN correcto.",
            "5. Inspeccionar que el encapsulado (VXLAN o MPLS) y el VNI/label estén configurados consistentemente.",
        ],
        "expected_evidence": {
            "confirming": [
                "Familia EVPN activada bajo BGP con capabilities negociadas en ambos extremos.",
                "RD único y RTs correctos en la MAC-VRF; sin duplicados detectados en logs.",
                "Bridge domain/VLAN local mapeado correctamente a la EVI con VLAN-to-EVI sin mismatch.",
                "Interfaces AC en Up/Up y asociadas al bridge domain/VLAN esperado.",
                "Encapsulado VXLAN/MPLS con VNI/label coincidente en todos los VTEPs/PEs del segmento.",
            ],
            "invalidating": [
                "Familia EVPN no activada en BGP (rutas tipo 2/5 no se anuncian ni se reciben).",
                "RD duplicado o RT mismatch (rutas EVPN descartadas silenciosamente al importar a la MAC-VRF).",
                "VLAN-to-EVI mapping incorrecto (tráfico de VLAN 100 mapeado a EVI 10 en lugar de EVI 20).",
                "Interfaces AC en Down o asociadas a bridge domain distinto (tráfico no ingresa a la MAC-VRF).",
                "VNI mismatch entre VTEPs (aislamiento de segmento; tramas BUM no replicadas correctamente).",
            ],
        },
        "scientific_basis": "EVPN (RFC 7432) depende de BGP para distribuir MACs e IPs. El RD debe ser único por MAC-VRF. El mapeo VLAN-to-EVI debe ser consistente en todos los PEs. Un VNI mismatch en VXLAN rompe el segmento overlay (RFC 8365).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque BGP está Up, EVPN está activo. Verifique 'show bgp evpn' explícitamente.",
            "Una MAC-VRF configurada NO garantiza que el bridge domain esté poblado. Verifique 'show bridge-domain'.",
            "Descarte la hipótesis de VNI solo si ha verificado el mapeo en TODOS los VTEPs del mismo segmento.",
        ],
        "references": [
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "RFC 8365: A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)",
            "Cisco EVPN Configuration Guide",
        ],
        "fix": (
            "1. Activar familia EVPN (AFI/SAFI 25/70) bajo BGP en ambos PEs/VTEPs.\n"
            "2. Usar RD único y RTs correctos en la MAC-VRF.\n"
            "3. Mapear correctamente bridge-domain/VLAN local a la EVI.\n"
            "4. Asegurar que interfaces AC estén Up y asociadas al bridge-domain/VLAN.\n"
            "5. Configurar encapsulado (VXLAN/MPLS) y VNI/label consistentemente.\n"
            "6. Validar recepción de rutas EVPN y aprendizaje de MACs remotas.\n"
        ),
    },
    "vxlan_config.vxlan_config_start": {
        "hypothesis": "La configuración VXLAN no produce el comportamiento esperado debido a un source IP incorrecto en la interfaz NVE, un VLAN-to-VNI mismatch entre VTEPs, o una dependencia faltante del underlay IGP para anunciar la loopback de origen.",
        "verification_steps": [
            "1. Verificar que la interfaz NVE/VTEP esté configurada con la source IP correcta (loopback principal).",
            "2. Confirmar que el mapeo de VLAN a VNI sea idéntico en todos los VTEPs del mismo segmento.",
            "3. Validar que la loopback de origen esté anunciada en el underlay IGP (OSPF/IS-IS/BGP) y sea alcanzable.",
            "4. Revisar que el mecanismo de replicación BUM (multicast o HER) esté configurado y funcional.",
            "5. Inspeccionar que el hardware soporte el encapsulado VXLAN en la plataforma utilizada (algunas linecards no soportan NVE).",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaz NVE activa con source IP igual a la loopback principal anunciada en IGP.",
                "VLAN-to-VNI mapping idéntico en todos los VTEPs para cada segmento de interés.",
                "Loopback de origen alcanzable desde todos los VTEPs vía underlay IGP.",
                "Mecanismo BUM configurado (grupo multicast funcional o tabla HER poblada).",
                "Plataforma confirma soporte de VXLAN/NVE en la documentación del vendor.",
            ],
            "invalidating": [
                "Source IP de NVE apuntando a interfaz física o a loopback no anunciada en IGP (VTEPs no se ven entre sí).",
                "VLAN-to-VNI mismatch (aislamiento de segmento; tramas descartadas por VNI desconocido).",
                "Loopback de origen no incluida en el underlay IGP (ruta inalcanzable, túneles NVE no establecidos).",
                "BUM no configurado (falta grupo multicast o tabla HER vacía; tráfico broadcast desconocido no replicado).",
                "Plataforma o linecard sin soporte de VXLAN (NVE en estado administratively down por falta de capacidad de hardware).",
            ],
        },
        "scientific_basis": "VXLAN (RFC 7348) encapsula tramas Ethernet en UDP/4789. El underlay IP debe anunciar la loopback de origen de cada VTEP. La consistencia del VLAN-to-VNI mapping es crítica; un mismatch causa aislamiento completo del segmento (Cisco VXLAN Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el IGP underlay está funcional, la loopback del VTEP es alcanzable. Verifique la ruta específica.",
            "Una NVE en estado 'Up' NO garantiza que el VNI esté mapeado correctamente. Verifique 'show vxlan vlan-to-vni'.",
            "Descarte la hipótesis de hardware solo si ha verificado en la datasheet que la plataforma/linecard soporta NVE.",
        ],
        "references": [
            "RFC 7348: Virtual eXtensible Local Area Network (VXLAN)",
            "Cisco VXLAN Configuration Guide",
            "Juniper EVPN-VXLAN Configuration Guide",
        ],
        "fix": (
            "1. Configurar source IP de NVE/VTEP como la loopback principal anunciada en IGP.\n"
            "2. Alinear mapeo VLAN-to-VNI idéntico en todos los VTEPs del segmento.\n"
            "3. Anunciar la loopback de origen en el underlay IGP (OSPF/IS-IS/BGP).\n"
            "4. Configurar replicación BUM (grupo multicast funcional o HER poblada).\n"
            "5. Verificar soporte de hardware/linecard para VXLAN/NVE.\n"
            "6. Confirmar que los VTEPs se vean entre sí y que las MACs remotas apunten al VTEP correcto.\n"
        ),
    },
    "ospf_config.ospf_config_start": {
        "hypothesis": "La configuración OSPF no produce el comportamiento esperado debido a un error de área en la interfaz, un Router-ID duplicado, una red inversa mal definida (wildcard mask incorrecta), o una interfaz pasiva aplicada por error a un enlace troncal.",
        "verification_steps": [
            "1. Verificar que las interfaces estén asignadas al área OSPF correcta (mismatch de área impide adyacencia).",
            "2. Confirmar que el Router-ID sea único en todo el dominio OSPF y esté explícitamente configurado.",
            "3. Validar que las sentencias de red (network statements) usen la wildcard mask correcta para capturar las interfaces deseadas.",
            "4. Revisar que las interfaces de tránsito no estén configuradas como passive-interface.",
            "5. Inspeccionar que los timers Hello/Dead coincidan y que la autenticación (si se usa) tenga la misma clave en ambos extremos.",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaces en el área OSPF designada con network statement y wildcard mask correctas.",
                "Router-ID único y explícitamente configurado (preferentemente loopback /32).",
                "Sin interfaces de tránsito marcadas como passive-interface.",
                "Timers Hello/Dead idénticos en ambos extremos del enlace.",
                "Autenticación configurada con el mismo tipo y clave en ambos vecinos (si aplica).",
            ],
            "invalidating": [
                "Interfaz en área incorrecta (vecinos no forman adyacencia aunque estén en el mismo segmento).",
                "Router-ID duplicado (inestabilidad y flaps continuos en el área).",
                "Wildcard mask incorrecta (network statement no incluye la interfaz deseada o incluye interfaces no deseadas).",
                "Passive-interface aplicado a enlace troncal (Hellos no enviados, adyacencia imposible).",
                "Autenticación mismatch (OSPF cae a Down inmediatamente por MD5/key-id incorrecto).",
            ],
        },
        "scientific_basis": "OSPF (RFC 2328) requiere que las interfaces vecinas compartan área, timers y autenticación. El Router-ID debe ser único; un duplicado causa reconvergencia cíclica. La wildcard mask define qué interfaces participan en el proceso (Cisco IOS OSPF Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show ip ospf interface' lista la interfaz, la network statement es correcta. Verifique la wildcard.",
            "Un 'passive-interface default' olvidado puede silenciar adyacencias sin generar logs evidentes.",
            "Descarte la hipótesis de Router-ID solo si ha verificado el ID en TODOS los routers del dominio.",
        ],
        "references": [
            "RFC 2328: OSPF Version 2",
            "Cisco OSPF Configuration Guide",
            "Juniper OSPF Configuration Guide",
        ],
        "fix": (
            "1. Asignar interfaces al área OSPF correcta.\n"
            "2. Configurar Router-ID único y explícito (preferentemente loopback /32).\n"
            "3. Corregir network statements/wildcard mask para capturar las interfaces deseadas.\n"
            "4. Eliminar passive-interface de enlaces troncales.\n"
            "5. Sincronizar timers Hello/Dead y autenticación en ambos extremos.\n"
            "6. Verificar adyacencias Full y sincronización de LSDB.\n"
        ),
    },
    "isis_config.isis_config_start": {
        "hypothesis": "La configuración IS-IS no produce el comportamiento esperado debido a un NET duplicado, un desajuste de nivel (L1/L2) en la interfaz, un error en el área de L1, o la falta de wide-metrics habilitadas para soportar topologías modernas.",
        "verification_steps": [
            "1. Verificar que el NET (Network Entity Title) sea único en todo el dominio IS-IS.",
            "2. Confirmar que el nivel de la interfaz (L1, L2, L1-L2) coincida con el vecino conectado.",
            "3. Validar que el nombre de área coincida para adyacencias de Level 1 (L1 requiere área idéntica).",
            "4. Revisar que wide-metrics esté habilitado para soportar métricas superiores a 63 y TE extensions.",
            "5. Inspeccionar que el proceso IS-IS esté habilitado en las interfaces deseadas y no solo globalmente.",
        ],
        "expected_evidence": {
            "confirming": [
                "NET único en todo el dominio IS-IS sin duplicados detectados.",
                "Nivel de interfaz coincidente con el vecino (L1, L2 o L1-L2 según diseño).",
                "Nombre de área idéntico para adyacencias Level 1.",
                "Wide-metrics habilitado globalmente y en interfaces para soportar TE y métricas grandes.",
                "IS-IS habilitado explícitamente en cada interfaz de tránsito (no solo a nivel de proceso).",
            ],
            "invalidating": [
                "NET duplicado (causa inestabilidad y flaps de adyacencia en todo el dominio).",
                "Nivel desajustado (L1-only conectado a L2-only; adyacencia imposible).",
                "Área diferente en adyacencia L1 (Hellos rechazados por área no coincidente).",
                "Wide-metrics deshabilitado (métricas truncadas a 6 bits; rutas subóptimas o inalcanzables).",
                "IS-IS habilitado globalmente pero no en la interfaz (Hellos no transmitidos, adyacencia inexistente).",
            ],
        },
        "scientific_basis": "IS-IS (ISO 10589) utiliza el NET para identificar el router. Un NET duplicado rompe la topología. L1 requiere área idéntica. Wide-metrics (RFC 5305) es obligatorio para redes modernas y TE. La habilitación en interfaces es requisito en algunos vendors (Cisco/Juniper IS-IS Configuration Guides).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque IS-IS está configurado globalmente, está habilitado en la interfaz. Verifique 'show isis interface'.",
            "Un NET 'correcto' en un router NO garantiza unicidad en el dominio. Verifique todos los routers.",
            "Descarte la hipótesis de nivel solo si ha verificado el nivel en ambos extremos del enlace.",
        ],
        "references": [
            "ISO 10589: Intermediate System to Intermediate System Intra-Domain Routing Exchange Protocol",
            "RFC 5305: IS-IS Extensions for Traffic Engineering",
            "Cisco IS-IS Configuration Guide",
        ],
        "fix": (
            "1. Asignar NET único en todo el dominio IS-IS.\n"
            "2. Alinear nivel de interfaz (L1/L2/L1-L2) con el vecino conectado.\n"
            "3. Coincidir nombre de área para adyacencias Level 1.\n"
            "4. Habilitar wide-metrics globalmente y en interfaces.\n"
            "5. Habilitar IS-IS explícitamente en interfaces de tránsito.\n"
            "6. Confirmar adyacencias Up y LSDB sincronizada.\n"
        ),
    },
    "spanning_tree_config.spanning_tree_config_start": {
        "hypothesis": "La configuración Spanning Tree no produce el comportamiento esperado debido a una prioridad de bridge mal calculada, un modo RSTP/MSTP inconsistente entre switches, o la falta de BPDU Guard en puertos de acceso.",
        "verification_steps": [
            "1. Verificar que el modo Spanning Tree (RSTP, MSTP, PVST+) sea consistente en todos los switches del dominio.",
            "2. Confirmar que la prioridad del Root Bridge esté manualmente ajustada al switch de Core designado.",
            "3. Validar que los puertos de acceso (edge) tengan BPDU Guard habilitado para prevenir loops accidentales.",
            "4. Revisar el mapping de VLANs a instancias MSTP (debe ser idéntico en todos los switches de la región).",
            "5. Inspeccionar que Root Guard esté aplicado en puertos de distribución donde no se espera recibir BPDUs superiores.",
        ],
        "expected_evidence": {
            "confirming": [
                "Modo STP consistente (RSTP/MSTP) en todos los switches del dominio.",
                "Root Bridge en el Core con prioridad manual baja (ej. 4096) y BID estable.",
                "BPDU Guard habilitado en todos los puertos de acceso (edge).",
                "MSTP region name, revision y VLAN-to-instance mapping idénticos en todos los switches.",
                "Root Guard aplicado en puertos de distribución hacia acceso para evibir Root Bridge inesperado.",
            ],
            "invalidating": [
                "Modo inconsistente (MSTP en un switch, RSTP en otro) causando incompatibilidad de regiones.",
                "Prioridad por defecto (32768) en switch de acceso que gana la elección de Root Bridge.",
                "BPDU Guard omitido en puertos edge (loop accidental por conexión no autorizada).",
                "MSTP region mismatch (VLAN-to-instance mapping diferente; switches aislados en regiones separadas).",
                "Root Guard omitido en enlaces de distribución (switch de acceso se convierte en Root Bridge).",
            ],
        },
        "scientific_basis": "Spanning Tree (IEEE 802.1D/802.1w/802.1s) requiere consistencia de modo y parámetros. El Root Bridge debe ser el switch de Core con prioridad configurada. BPDU Guard y Root Guard son controles de seguridad esenciales para estabilidad (Cisco Campus LAN Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el switch tiene prioridad 4096, será Root Bridge. Verifique si otro switch tiene prioridad más baja.",
            "Una configuración 'correcta' en un switch NO garantiza consistencia de región MSTP. Verifique todos los switches.",
            "Descarte la hipótesis de modo inconsistente solo si ha verificado 'show spanning-tree mode' en TODOS los switches.",
        ],
        "references": [
            "IEEE 802.1w: Rapid Reconfiguration of Spanning Tree",
            "IEEE 802.1s: Multiple Spanning Trees",
            "Cisco Campus LAN Configuration Guide",
        ],
        "fix": (
            "1. Usar modo STP consistente (RSTP/MSTP) en todos los switches.\n"
            "2. Configurar prioridad del Root Bridge en el Core (ej. 4096).\n"
            "3. Habilitar BPDU Guard en puertos de acceso (edge).\n"
            "4. Alinear MSTP region name, revision y VLAN-to-instance mapping.\n"
            "5. Aplicar Root Guard en enlaces de distribución hacia acceso.\n"
            "6. Verificar topología STP estable y sin TCNs recurrentes.\n"
        ),
    },
    "qos_traffic_eng_config.qos_te_config_start": {
        "hypothesis": "La configuración QoS/TE no produce el comportamiento esperado debido a un error en la clasificación (ACL mal definida), un policing con burst insuficiente, una cola LLQ no asignada, o un túnel TE sin RSVP habilitado en las interfaces de tránsito.",
        "verification_steps": [
            "1. Verificar que la clasificación (class-map) use ACLs o condiciones que capturen el tráfico deseado.",
            "2. Confirmar que el policing/shaping tenga un burst size adecuado para absorber ráfagas TCP (mínimo RTT * rate / 8).",
            "3. Validar que la cola de baja latencia (LLQ/Priority Queue) esté configurada y asignada a la clase de voz/video.",
            "4. Revisar que RSVP esté habilitado en todas las interfaces de tránsito del túnel TE.",
            "5. Inspeccionar que el ancho de banda reservado en el túnel TE no exceda la capacidad del enlace físico.",
        ],
        "expected_evidence": {
            "confirming": [
                "Class-map con ACL que muestra contadores de match para el tráfico de interés.",
                "Policing/shaping con burst size >= Bc (committed burst) calculado correctamente para la velocidad de línea.",
                "Cola LLQ/Priority configurada y asignada a la clase de voz con ancho de banda garantizado.",
                "RSVP habilitado en todas las interfaces del path del túnel TE.",
                "Bandwidth reservado del túnel TE <= capacidad física del enlace más débil del path.",
            ],
            "invalidating": [
                "ACL de class-map demasiado restrictiva (no captura el tráfico real; contadores en cero).",
                "Burst size insuficiente (policing descarta ráfagas legítimas, degrada throughput TCP).",
                "LLQ no configurada (tráfico de voz comparte cola con best-effort, causando jitter y pérdida).",
                "RSVP no habilitado en una interfaz de tránsito (túnel TE no puede reservar recursos, señalización falla).",
                "Bandwidth del túnel TE mayor que la capacidad del enlace (reservación imposible, LSP no establecido).",
            ],
        },
        "scientific_basis": "QoS requiere clasificación precisa y burst size proporcional a la velocidad de línea (RFC 2697). LLQ debe asignarse explícitamente para tráfico sensible a latencia. RSVP-TE requiere habilitación en cada interfaz del path para reservar recursos (RFC 3209).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la policy-map existe, está aplicada a la interfaz. Verifique 'service-policy'.",
            "Un burst size 'grande' NO es siempre mejor; un valor excesivo puede violar el CIR acordado.",
            "Descarte la hipótesis de RSVP solo si ha verificado 'show ip rsvp interface' en TODOS los routers del path.",
        ],
        "references": [
            "RFC 2697: A Single Rate Three Color Marker",
            "RFC 3209: RSVP-TE: Extensions to RSVP for LSP Tunnels",
            "Cisco QoS Configuration Guide",
        ],
        "fix": (
            "1. Corregir class-map/ACL para capturar el tráfico deseado.\n"
            "2. Ajustar burst size del policer/shaper (mínimo RTT*rate/8).\n"
            "3. Configurar cola LLQ/Priority Queue para voz/video con ancho de banda garantizado.\n"
            "4. Habilitar RSVP en todas las interfaces de tránsito del túnel TE.\n"
            "5. Asegurar que bandwidth reservado del túnel TE no exceda capacidad física.\n"
            "6. Validar que el LSP TE se establezca y que las clases de tráfico reciban tratamiento esperado.\n"
        ),
    },
    "multicast_config.multicast_config_start": {
        "hypothesis": "La configuración multicast no produce el comportamiento esperado debido a un RP no configurado o inconsistente, una falta de PIM en las interfaces de tránsito, o un bloqueo de IGMP en la última milla.",
        "verification_steps": [
            "1. Verificar que el RP esté configurado de forma consistente (estático, Auto-RP o BSR) en todos los routers.",
            "2. Confirmar que PIM Sparse-Mode esté habilitado en todas las interfaces de tránsito y loopbacks implicadas.",
            "3. Validar que IGMP esté habilitado en las interfaces de acceso hacia los receptores.",
            "4. Revisar que el RPF check tenga una ruta unicast válida hacia la fuente del tráfico multicast.",
            "5. Inspeccionar que no existan ACLs o filtros bloqueando el tráfico de control multicast (PIM, IGMP, MSDP).",
        ],
        "expected_evidence": {
            "confirming": [
                "RP configurado y consistente en todos los routers del dominio PIM-SM.",
                "PIM Sparse-Mode habilitado en todas las interfaces de tránsito y loopbacks.",
                "IGMP habilitado en interfaces de acceso con receptores presentes.",
                "Ruta unicast hacia la fuente multicast presente y estable en la RIB.",
                "Sin ACLs descartando paquetes de control multicast (IGMP, PIM, MSDP).",
            ],
            "invalidating": [
                "RP inconsistente o no alcanzable (algunos routers usan RP distinto, árboles fragmentados).",
                "PIM no habilitado en interfaz de tránsito (vecinos PIM no descubiertos, árbol no construido).",
                "IGMP deshabilitado en interfaz de acceso (receptores no reportan membresía, OIL vacía).",
                "Ruta unicast hacia la fuente faltante (RPF check falla, tráfico multicast descartado silenciosamente).",
                "ACL bloqueando IGMP Reports o PIM Joins (control plane bloqueado, datos no fluyen).",
            ],
        },
        "scientific_basis": "PIM-SM (RFC 4601) requiere un RP funcional y PIM habilitado en todas las interfaces del árbol. IGMP gestiona la membresía en la última milla. El RPF check depende del unicast routing (RFC 4601, Sección 4.6).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un router tiene RP configurado, todos los demás lo usan. Verifique 'show ip pim rp mapping'.",
            "Una interfaz con PIM habilitado NO garantiza que el vecino PIM esté activo. Verifique 'show ip pim neighbor'.",
            "Descarte la hipótesis de RPF solo si ha verificado la ruta unicast hacia la fuente en TODOS los routers del path.",
        ],
        "references": [
            "RFC 4601: Protocol Independent Multicast - Sparse Mode (PIM-SM)",
            "RFC 3376: Internet Group Management Protocol, Version 3",
            "Cisco Multicast Configuration Guide",
        ],
        "fix": (
            "1. Configurar RP consistente en todos los routers (estático, Auto-RP o BSR).\n"
            "2. Habilitar PIM Sparse-Mode en todas las interfaces de tránsito y loopbacks.\n"
            "3. Habilitar IGMP en interfaces de acceso hacia receptores.\n"
            "4. Asegurar RPF check válido con ruta unicast hacia la fuente.\n"
            "5. Eliminar ACLs/filtros que bloqueen PIM, IGMP o MSDP.\n"
            "6. Verificar estados (*,G)/(S,G) y entrega de tráfico a receptores.\n"
        ),
    },
    "bfd_config.bfd_config_start": {
        "hypothesis": "La configuración BFD no produce el comportamiento esperado debido a timers desajustados con el hardware, una asociación incorrecta con el protocolo cliente, o la falta de habilitación en la interfaz física.",
        "verification_steps": [
            "1. Verificar que los timers BFD configurados sean soportados por el hardware/ASIC de la plataforma.",
            "2. Confirmar que BFD esté habilitado en la interfaz física o lógica donde se requiere la sesión.",
            "3. Validar que el protocolo cliente (OSPF, BGP, IS-IS, EIGRP) tenga BFD activado explícitamente bajo sus parámetros.",
            "4. Revisar que no existan ACLs o QoS policies descartando paquetes UDP 3784/3785.",
            "5. Inspeccionar que la sesión BFD esté en estado Up y que el protocolo cliente la tenga registrada.",
        ],
        "expected_evidence": {
            "confirming": [
                "Timers BFD dentro del rango soportado por el hardware (verificado en datasheet o 'show bfd neighbors').",
                "BFD habilitado en la interfaz de interés (comando de interfaz presente y commit exitoso).",
                "Protocolo cliente con BFD explícitamente activado (ej. 'bfd interval' bajo interfaz OSPF o 'fall-over bfd' en BGP).",
                "Sin ACLs ni políticas de QoS descartando paquetes de control BFD.",
                "Sesión BFD en estado Up con clientes registrados y contadores de paquetes simétricos.",
            ],
            "invalidating": [
                "Timers BFD por debajo del mínimo soportado por el hardware (sesión no se establece o cae inmediatamente).",
                "BFD habilitado globalmente pero no en la interfaz (Hellos no transmitidos).",
                "Protocolo cliente sin BFD activado (sesión BFD Up pero el cliente no recibe notificaciones de caída).",
                "ACL bloqueando UDP 3784/3785 (paquetes BFD descartados silenciosamente).",
                "Sesión BFD en Admin Down o con clientes no registrados (falla de integración BFD-cliente).",
            ],
        },
        "scientific_basis": "BFD (RFC 5880) requiere que los timers sean soportados por la plataforma. La sesión debe estar vinculada al protocolo cliente para notificar caídas. La habilitación en la interfaz es un requisito común en implementaciones vendor-specific (Cisco/Juniper BFD Configuration Guides).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque BFD está configurado globalmente, la interfaz lo usa. Verifique 'show bfd neighbors'.",
            "Una sesión BFD 'Up' NO garantiza que el cliente esté registrado. Verifique 'show bfd neighbors client'.",
            "Descarte la hipótesis de timers solo si ha verificado el mínimo soportado en la documentación del hardware.",
        ],
        "references": [
            "RFC 5880: Bidirectional Forwarding Detection (BFD)",
            "RFC 5882: Generic Application of BFD",
            "Cisco BFD Configuration Guide",
        ],
        "fix": (
            "1. Ajustar timers BFD a valores soportados por el hardware/ASIC.\n"
            "2. Habilitar BFD en la interfaz física/lógica requerida.\n"
            "3. Activar BFD explícitamente bajo el protocolo cliente (OSPF/BGP/IS-IS/EIGRP).\n"
            "4. Eliminar ACLs/QoS policies que descarten UDP 3784/3785.\n"
            "5. Verificar sesión BFD en estado Up y protocolo cliente registrado.\n"
            "6. Confirmar convergencia rápida ante falla simulada del enlace.\n"
        ),
    },
    "dhcp_config.dhcp_config_start": {
        "hypothesis": "La configuración DHCP no produce el comportamiento esperado debido a un pool mal definido (subnet/máscara incorrectas), una exclusión de direcciones que incluye la gateway, o la falta de configuración de relay en el router de acceso.",
        "verification_steps": [
            "1. Verificar que el pool DHCP tenga la subnet, máscara y gateway correctos para el segmento de cliente.",
            "2. Confirmar que el rango de direcciones excluidas no incluya la IP del gateway o del servidor DHCP mismo.",
            "3. Validar que el DHCP Relay (ip helper-address) esté configurado en la interfaz L3 del cliente si el servidor está remoto.",
            "4. Revisar que las opciones DHCP (DNS, domain-name, lease time) estén configuradas según el diseño.",
            "5. Inspeccionar que no existan conflictos de direcciones IP ya asignadas estáticamente dentro del pool dinámico.",
        ],
        "expected_evidence": {
            "confirming": [
                "Pool DHCP con subnet, máscara y gateway coincidentes con el segmento de acceso del cliente.",
                "Rango de exclusión correcto (no incluye gateway ni servidor DHCP).",
                "DHCP Relay configurado en la interfaz SVI/subinterfaz del cliente (si el servidor es remoto).",
                "Opciones DHCP (DNS, lease time) configuradas y consistentes con el diseño.",
                "Sin conflictos de direcciones estáticas dentro del rango dinámico del pool.",
            ],
            "invalidating": [
                "Pool con subnet o máscara incorrecta (servidor ofrece IP de subnet distinta a la del cliente).",
                "Exclusión que incluye la IP del gateway (cliente recibe IP de gateway, causando conflicto ARP).",
                "DHCP Relay omitido en router de acceso (Discover broadcast no llega al servidor remoto).",
                "Opciones DHCP faltantes (sin DNS, lease time 0, o domain-name incorrecto).",
                "Dirección estática dentro del pool dinámico (servidor ofrece IP en uso, causa conflicto).",
            ],
        },
        "scientific_basis": "DHCP (RFC 2131) requiere que el pool coincida con la subnet del segmento de acceso. El relay agent es obligatorio cuando el servidor no está en el mismo broadcast domain. La exclusión de direcciones debe evitar la IP del gateway y direcciones estáticas (Cisco IOS DHCP Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el pool tiene direcciones libres, el cliente recibe una oferta. Verifique el relay y la subnet.",
            "Una interfaz con 'ip helper-address' correcto NO garantiza que el firewall no bloquee UDP 67/68.",
            "Descarte la hipótesis de conflicto solo si ha verificado la tabla ARP y las reservas estáticas del segmento.",
        ],
        "references": [
            "RFC 2131: Dynamic Host Configuration Protocol",
            "RFC 3046: DHCP Relay Agent Information Option",
            "Cisco IOS DHCP Configuration Guide",
        ],
        "fix": (
            "1. Corregir subnet, máscara y gateway en el pool DHCP para el segmento.\n"
            "2. Excluir del rango la IP del gateway y direcciones estáticas.\n"
            "3. Configurar DHCP Relay ('ip helper-address') en la interfaz del cliente si el servidor es remoto.\n"
            "4. Ajustar opciones DHCP (DNS, domain-name, lease time) según diseño.\n"
            "5. Eliminar conflictos de direcciones estáticas dentro del pool dinámico.\n"
            "6. Validar que el cliente reciba IP, gateway y DNS correctos.\n"
        ),
    },
    "netflow_config.netflow_config_start": {
        "hypothesis": "La configuración NetFlow/IPFIX no produce el comportamiento esperado debido a un monitor no aplicado a la interfaz, una sampling rate de 1:1 que sature recursos, o una IP/puerto de colector incorrectos.",
        "verification_steps": [
            "1. Verificar que el monitor de NetFlow esté aplicado a las interfaces de interés en la dirección correcta (ingress/egress).",
            "2. Confirmar que la IP y el puerto UDP del colector estén configurados correctamente y sean alcanzables.",
            "3. Validar que la sampling rate sea apropiada para la velocidad del enlace (evitar 1:1 en 10G/100G).",
            "4. Revisar que la plantilla de exportación (template) esté definida y coincida con lo esperado por el colector.",
            "5. Inspeccionar que no existan ACLs descartando el tráfico de exportación UDP hacia el colector.",
        ],
        "expected_evidence": {
            "confirming": [
                "Monitor NetFlow aplicado a interfaces de interés en ingress y/o egress según diseño.",
                "Colector configurado con IP y puerto correctos, alcanzables desde el router.",
                "Sampling rate configurada adecuadamente para la capacidad del enlace y del router.",
                "Plantilla de exportación definida y compatible con el software del colector.",
                "Sin ACLs ni firewalls bloqueando el tráfico UDP de exportación NetFlow/IPFIX.",
            ],
            "invalidating": [
                "Monitor configurado pero no aplicado a ninguna interfaz (sin flujos capturados).",
                "IP o puerto de colector incorrectos (exportador envía flujos a destino inexistente).",
                "Sampling rate 1:1 en enlace de alta velocidad (saturación de CPU o buffer de exportación).",
                "Plantilla no definida o incompatible (colector no puede decodificar los registros exportados).",
                "ACL bloqueando tráfico UDP de exportación (descarte silencioso, colector no recibe nada).",
            ],
        },
        "scientific_basis": "NetFlow v9/IPFIX (RFC 7011) requiere que el monitor esté activo en la interfaz. El sampling rate debe equilibrar precisión y recursos. La plantilla de exportación es crítica para que el colector interprete los campos correctamente (Cisco NetFlow Configuration Guide).",
        "confidence_level": "Media",
        "bias_warnings": [
            "NO asuma que porque 'show flow monitor' existe, está aplicado a la interfaz. Verifique 'show run interface'.",
            "Un colector que no recibe datos NO siempre indica falla de red; puede ser una plantilla incompatible.",
            "Descarte la hipótesis de sampling solo si ha verificado la carga de CPU del router durante el tráfico pico.",
        ],
        "references": [
            "RFC 7011: Specification of the IPFIX Protocol for the Exchange of Flow Information",
            "Cisco NetFlow Configuration Guide",
            "Juniper Flow Monitoring Configuration Guide",
        ],
        "fix": (
            "1. Aplicar el monitor NetFlow a las interfaces de interés en ingress/egress.\n"
            "2. Corregir IP y puerto UDP del colector y verificar alcanzabilidad.\n"
            "3. Configurar sampling rate adecuada para la velocidad del enlace.\n"
            "4. Definir plantilla de exportación compatible con el colector.\n"
            "5. Abrir puertos UDP de exportación en ACLs/firewalls.\n"
            "6. Confirmar que el colector reciba flujos y los decodifique correctamente.\n"
        ),
    },
    "sdwan_config.sdwan_config_start": {
        "hypothesis": "La configuración SD-WAN no produce el comportamiento esperado debido a un error en el template de política, una color/transporte mal asignado al TLOC, o una falta de certificados/whitelist para el registro con los orquestadores.",
        "verification_steps": [
            "1. Verificar que el Edge tenga los certificados válidos y esté en la whitelist de vBond/vManage.",
            "2. Confirmar que los colores/transportes (MPLS, INET, LTE) estén asignados correctamente a los TLOCs de cada interfaz WAN.",
            "3. Validar que las políticas de control (control-policy) permitan el intercambio de rutas OMP entre los sites.",
            "4. Revisar que las políticas de datos (data-policy) y App-Aware Routing estén aplicadas al site correcto.",
            "5. Inspeccionar que los SLA class lists y los thresholds de latencia/jitter/pérdida coincidan con el diseño.",
        ],
        "expected_evidence": {
            "confirming": [
                "Edge con certificados válidos y registrado en la whitelist de vBond/vManage.",
                "Colores/transportes asignados correctamente a cada TLOC según el diseño de transporte.",
                "Control-policy permitiendo el intercambio de rutas OMP entre sites y VPNs.",
                "Data-policy y App-Aware Routing aplicadas al site/vRF correcto.",
                "SLA class lists configuradas con thresholds realistas y coincidentes con los requisitos de aplicación.",
            ],
            "invalidating": [
                "Certificado inválido o Edge fuera de whitelist (registro con vBond rechazado, Edge aislado).",
                "Color/transporte mal asignado (tráfico MPLS enviado por interface INET por error de TLOC).",
                "Control-policy bloqueando la distribución de rutas OMP (sites no ven rutas entre sí).",
                "Data-policy aplicada al site incorrecto (política de break-out local no aplica al Edge afectado).",
                "SLA thresholds demasiado restrictivos (ningún enlace cumple, App-Aware Routing descarta tráfico).",
            ],
        },
        "scientific_basis": "SD-WAN (Cisco Viptela) requiere certificados para el control plane. Los colores definen el transporte y deben coincidir con el diseño. Las políticas de control determinan qué rutas OMP se distribuyen. SLA thresholds muy restrictivos pueden dejar sin path válido al tráfico (Cisco SD-WAN Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el Edge aparece en vManage, los certificados son válidos. Verifique la fecha de expiración y el CA root.",
            "Un color 'correcto' en la interfaz NO garantiza que el TLOC esté anunciado. Verifique 'show omp tlocs'.",
            "Descarte la hipótesis de política solo si ha comparado la configuración del template con la del Edge en 'show policy'.",
        ],
        "references": [
            "Cisco SD-WAN Configuration Guide",
            "Cisco SD-WAN Design and Deployment Guide",
            "Cisco Live BRKSDW-2820: SD-WAN Deep Dive",
        ],
        "fix": (
            "1. Validar/renovar certificados del Edge y asegurar que esté en whitelist de vBond/vManage.\n"
            "2. Asignar colores/transportes correctos a los TLOCs según diseño.\n"
            "3. Ajustar control-policy para permitir intercambio de rutas OMP entre sites.\n"
            "4. Aplicar data-policy y App-Aware Routing al site/vRF correcto.\n"
            "5. Configurar SLA class lists con thresholds realistas.\n"
            "6. Verificar que el Edge se registre y reciba políticas desde vManage.\n"
        ),
    },
    "dmvpn_config.dmvpn_config_start": {
        "hypothesis": "La configuración DMVPN no produce el comportamiento esperado debido a un error en el mGRE (source/destination mismatch), una política IPsec incompatible, o la falta de configuración de routing sobre el túnel.",
        "verification_steps": [
            "1. Verificar que el túnel mGRE tenga source interface correcta y modo multipoint en Hub y Spoke.",
            "2. Confirmar que la política de transform-set/IPsec profile sea compatible entre Hub y Spokes (algoritmos, PFS).",
            "3. Validar que NHRP esté habilitado en el túnel con la IP del Hub correctamente referenciada en los Spokes.",
            "4. Revisar que el protocolo de enrutamiento (OSPF/EIGRP/BGP) esté configurado sobre la interfaz del túnel.",
            "5. Inspeccionar que NAT traversal (NAT-T) esté habilitado si los Spokes están detrás de NAT.",
        ],
        "expected_evidence": {
            "confirming": [
                "Túnel mGRE con source interface correcta y modo 'multipoint' en ambos extremos.",
                "IPsec profile con transform-set compatible y clave pre-compartida coincidente.",
                "NHRP habilitado con IP del Hub correcta en la configuración de los Spokes.",
                "Protocolo de enrutamiento activo sobre la interfaz de túnel mGRE con vecinos visibles.",
                "NAT-T habilitado (UDP 4500) para Spokes detrás de NAT (si aplica).",
            ],
            "invalidating": [
                "Source interface del túnel incorrecta o no en modo multipoint (túnel no levanta o no soporta múltiples peers).",
                "Transform-set incompatible (un extremo usa AES-GCM y el otro AES-CBC; negociación IKE falla).",
                "NHRP mal configurado (Spoke apunta a IP de Hub incorrecta o NHRP no habilitado en túnel).",
                "Protocolo de enrutamiento omitido en interfaz de túnel (sin vecinos, rutas no propagadas).",
                "NAT-T deshabilitado con Spokes detrás de NAT (IKE falla por traducción de puertos).",
            ],
        },
        "scientific_basis": "DMVPN requiere mGRE para múltiples túneles dinámicos, NHRP para resolución de next-hop e IPsec para cifrado. NAT-T es obligatorio cuando los Spokes están detrás de NAT (RFC 3947). El routing sobre el túnel es necesario para distribuir prefijos (Cisco DMVPN Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el túnel está Up, NHRP funciona. Verifique 'show ip nhrp' en el Hub.",
            "Una política IPsec 'similar' NO garantiza compatibilidad. Verifique algoritmos, modos y PFS explícitamente.",
            "Descarte la hipótesis de routing solo si ha verificado la configuración del protocolo en la interfaz de túnel.",
        ],
        "references": [
            "RFC 3947: Negotiation of NAT-Traversal in the IKE",
            "Cisco DMVPN Configuration Guide",
            "Cisco Live BRKSEC-4054: DMVPN Troubleshooting",
        ],
        "fix": (
            "1. Corregir source interface y modo multipoint del túnel mGRE en Hub y Spokes.\n"
            "2. Alinear política IPsec profile/transform-set y PSK entre Hub y Spokes.\n"
            "3. Configurar NHRP en el túnel con IP del Hub correcta en Spokes.\n"
            "4. Habilitar protocolo de routing sobre la interfaz de túnel mGRE.\n"
            "5. Habilitar NAT-T (UDP 4500) si Spokes están detrás de NAT.\n"
            "6. Confirmar registro NHRP y conectividad Hub-Spoke/Spoke-Spoke.\n"
        ),
    },
    "eigrp_config.eigrp_config_start": {
        "hypothesis": "La configuración EIGRP no produce el comportamiento esperado debido a un AS number incorrecto, K-Values desajustados, una red mal definida (wildcard mask), o una interfaz pasiva aplicada a un enlace que debería formar adyacencia.",
        "verification_steps": [
            "1. Verificar que el número de Sistema Autónomo (AS) coincida exactamente en todos los routers del dominio EIGRP.",
            "2. Confirmar que los K-Values (coeficientes de métrica) sean idénticos en todos los vecinos.",
            "3. Validar que las sentencias de red usen la wildcard mask correcta para incluir las interfaces deseadas.",
            "4. Revisar que las interfaces de tránsito no estén configuradas como passive-interface.",
            "5. Inspeccionar que la autenticación (si se usa) tenga el mismo tipo y clave en todos los vecinos.",
        ],
        "expected_evidence": {
            "confirming": [
                "AS number idéntico en todos los routers del dominio EIGRP.",
                "K-Values coincidentes en todos los vecinos (verificado con 'show ip eigrp neighbors').",
                "Network statements con wildcard mask correcta, capturando interfaces de tránsito.",
                "Sin interfaces de tránsito marcadas como passive-interface.",
                "Autenticación configurada con el mismo tipo y clave en todos los vecinos (si aplica).",
            ],
            "invalidating": [
                "AS number desajustado (vecinos no forman adyacencia aunque estén en el mismo segmento).",
                "K-Values mismatch (EIGRP rechaza adyacencia si los coeficientes de métrica difieren).",
                "Wildcard mask incorrecta (network statement no incluye la interfaz deseada o incluye de más).",
                "Passive-interface en enlace troncal (no se envían Hellos, adyacencia imposible).",
                "Autenticación mismatch (EIGRP descarta paquetes del vecino por MD5/key-chain incorrecto).",
            ],
        },
        "scientific_basis": "EIGRP (RFC 7868) requiere AS y K-Values idénticos. La wildcard mask define qué interfaces participan. La autenticación MD5/key-chain debe coincidir exactamente. Un passive-interface en troncal impide adyacencias (Cisco EIGRP Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show ip eigrp interfaces' lista la interfaz, la network statement es correcta. Verifique la wildcard.",
            "Un 'passive-interface default' olvidado puede silenciar adyacencias sin generar logs evidentes.",
            "Descarte la hipótesis de K-Values solo si ha verificado los valores en TODOS los routers del dominio.",
        ],
        "references": [
            "RFC 7868: The EIGRP Protocol",
            "Cisco EIGRP Configuration Guide",
            "Cisco Live BRKRST-3038: Advanced EIGRP Troubleshooting",
        ],
        "fix": (
            "1. Corregir AS number para que coincida en todos los routers.\n"
            "2. Sincronizar K-Values en todos los vecinos.\n"
            "3. Ajustar network statements/wildcard mask para incluir interfaces de tránsito.\n"
            "4. Eliminar passive-interface de enlaces troncales.\n"
            "5. Alinear autenticación MD5/key-chain en todos los vecinos.\n"
            "6. Verificar adyacencias Up y tabla de topología.\n"
        ),
    },
    "pbr_config.pbr_config_start": {
        "hypothesis": "La configuración PBR no produce el comportamiento esperado debido a un route-map aplicado en la dirección incorrecta (egress vs ingress), una ACL de match que no captura el tráfico, o un next-hop no alcanzable que causa fallback no deseado a la RIB.",
        "verification_steps": [
            "1. Verificar que el route-map esté aplicado en la dirección ingress de la interfaz de entrada del tráfico.",
            "2. Confirmar que la ACL de match tenga la sintaxis correcta y capture el tráfico de origen/destino esperado.",
            "3. Validar que el next-hop o interface de salida especificados en la política estén activos y alcanzables.",
            "4. Revisar que el comando 'set ip next-hop' y 'set ip default next-hop' se usen según el diseño (obligatorio vs fallback).",
            "5. Inspeccionar que no existan políticas de routing por defecto (default routes) que estén sobreescribiendo PBR.",
        ],
        "expected_evidence": {
            "confirming": [
                "Route-map aplicado en ingress de la interfaz correcta (verificado con 'show ip policy').",
                "ACL de match con contadores activos para el tráfico de interés.",
                "Next-hop de la política alcanzable y en estado Up.",
                "Uso correcto de 'set ip next-hop' vs 'set ip default next-hop' según diseño.",
                "Sin ruta por defecto o BGP route que cause fallback no deseado antes de evaluar PBR.",
            ],
            "invalidating": [
                "Route-map aplicado en egress en lugar de ingress (PBR no evalúa paquetes entrantes).",
                "ACL de match demasiado restrictiva (contadores en cero, tráfico no capturado).",
                "Next-hop inalcanzable (PBR falla y el paquete sigue la RIB, posiblemente por path no deseado).",
                "Uso de 'default next-hop' cuando el diseño requiere 'next-hop' obligatorio (fallback no deseado).",
                "Ruta por defecto más específica en la RIB que redirige el tráfico antes de que PBR actúe.",
            ],
        },
        "scientific_basis": "PBR evalúa paquetes en la interfaz de entrada (ingress). La ACL debe coincidir con el tráfico real. El next-hop debe ser alcanzable; de lo contrario, el comportamiento fallback depende de la implementación (Cisco Policy-Based Routing Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el route-map existe, está aplicado. Verifique 'show ip policy interface'.",
            "Un next-hop 'alcanzable' por ping NO garantiza que PBR lo use; verifique que sea resoluble en la tabla de rutas.",
            "Descarte la hipótesis de ACL solo si ha enviado tráfico de prueba que cumpla EXACTAMENTE con las condiciones definidas.",
        ],
        "references": [
            "Cisco Policy-Based Routing Configuration Guide",
            "RFC 1102: Policy Routing in Internet Protocols",
            "Cisco Live BRKRST-3035: Advanced IP Routing Troubleshooting",
        ],
        "fix": (
            "1. Aplicar route-map en ingress de la interfaz de entrada correcta.\n"
            "2. Corregir ACL de match para capturar el tráfico esperado.\n"
            "3. Asegurar que next-hop/interface de salida estén Up y alcanzables.\n"
            "4. Usar 'set ip next-hop' obligatorio o 'set ip default next-hop' fallback según diseño.\n"
            "5. Evitar que rutas por defecto o BGP sobreescriban PBR.\n"
            "6. Validar con traceroute que el tráfico sigue el path deseado.\n"
        ),
    },
    "ipv6_config.ipv6_config_start": {
        "hypothesis": "La configuración IPv6 no produce el comportamiento esperado debido a IPv6 deshabilitado globalmente, una ruta estática mal definida, un error en el mapeo de prefijos para SLAAC, o una política de firewall bloqueando ICMPv6.",
        "verification_steps": [
            "1. Verificar que IPv6 esté habilitado globalmente en el router y en las interfaces de interés.",
            "2. Confirmar que las rutas estáticas o dinámicas IPv6 estén correctamente definidas (sin errores de sintaxis de dirección).",
            "3. Validar que el prefijo anunciado por SLAAC (Router Advertisement) coincida con el diseño de subnet.",
            "4. Revisar que OSPFv3, IS-IS para IPv6 o MP-BGP estén configurados con la address family IPv6 activada.",
            "5. Inspeccionar que no existan ACLs o firewall filters bloqueando ICMPv6 esencial (NDP, RA, ping).",
        ],
        "expected_evidence": {
            "confirming": [
                "IPv6 habilitado globalmente y en interfaces de interés (sin errores de sintaxis).",
                "Rutas estáticas/dinámicas IPv6 correctamente definidas y presentes en la RIB.",
                "Prefijo SLAAC anunciado en RA coincide con la subnet designada del segmento.",
                "Protocolo de enrutamiento IPv6 (OSPFv3, IS-IS, MP-BGP) con address family activa.",
                "Sin ACLs descartando ICMPv6 tipos 134 (RA), 135 (NS), 136 (NA) esenciales.",
            ],
            "invalidating": [
                "IPv6 deshabilitado globalmente (interfaces no generan Link-Local Addresses ni procesan IPv6).",
                "Ruta estática IPv6 con sintaxis de dirección incorrecta (caracteres ilegales o máscara mal formada).",
                "Prefijo SLAAC en RA no coincide con la subnet del segmento (cliente autoconfigura IP fuera de rango).",
                "Protocolo de enrutamiento IPv6 sin address family activada (no anuncia ni recibe rutas IPv6).",
                "ACL bloqueando ICMPv6 (NDP y RA fallan, causando inalcanzabilidad completa de vecinos IPv6).",
            ],
        },
        "scientific_basis": "IPv6 requiere habilitación explícita en interfaces en algunos sistemas. NDP y RA dependen de ICMPv6 (RFC 4861). La address family IPv6 debe activarse en los protocolos de enrutamiento (RFC 5340 para OSPFv3). Un prefijo SLAAC incorrecto causa autoconfiguración de direcciones inválidas.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque IPv4 funciona, IPv6 está habilitado. Verifique 'show ipv6 interface'.",
            "Una interfaz con Global Unicast Address NO garantiza que el routing IPv6 esté configurado. Verifique la RIB.",
            "Descarte la hipótesis de NDP solo si ha verificado la reachability ICMPv6 end-to-end con pings explícitos.",
        ],
        "references": [
            "RFC 4861: Neighbor Discovery for IP Version 6 (IPv6)",
            "RFC 5340: OSPF for IPv6 (OSPFv3)",
            "Cisco IPv6 Configuration Guide",
        ],
        "fix": (
            "1. Habilitar IPv6 globalmente y en interfaces de interés.\n"
            "2. Corregir sintaxis de rutas estáticas/dinámicas IPv6.\n"
            "3. Ajustar prefijo anunciado por SLAAC (RA) a la subnet del segmento.\n"
            "4. Activar address family IPv6 en OSPFv3/IS-IS/MP-BGP.\n"
            "5. Permitir ICMPv6 esencial (NS/NA/RA) en ACLs/firewall.\n"
            "6. Validar autoconfiguración y conectividad IPv6 end-to-end.\n"
        ),
    },
    "aaa_config.aaa_config_start": {
        "hypothesis": "La configuración AAA no produce el comportamiento esperado debido a un error en la method list (orden incorrecto o fallback omitido), un shared secret con caracteres especiales mal escapados, o la falta de habilitación de accounting en el modelo deseado.",
        "verification_steps": [
            "1. Verificar que la method list tenga el orden correcto (remoto primero, local como fallback) y esté aplicada al tipo de acceso (login, enable, dot1x).",
            "2. Confirmar que el shared secret no contenga caracteres mal escapados y coincida exactamente con el servidor.",
            "3. Validar que el servidor RADIUS/TACACS+ esté configurado con la IP y puertos correctos (1812/1813 o 49).",
            "4. Revisar que el accounting esté habilitado para los tipos de acceso requeridos (commands, network, exec).",
            "5. Inspeccionar que no existan conflictos entre grupos de servidores y servidores individuales en la configuración.",
        ],
        "expected_evidence": {
            "confirming": [
                "Method list con orden correcto y fallback local configurado para login/enable/dot1x.",
                "Shared secret idéntico en NAS y servidor, sin caracteres mal escapados.",
                "Servidor AAA configurado con IP y puertos correctos, alcanzable desde el NAS.",
                "Accounting habilitado para los tipos de acceso requeridos (commands, exec, network).",
                "Sin conflictos entre server groups y servidores individuales (configuración consistente).",
            ],
            "invalidating": [
                "Method list sin fallback local (si el servidor cae, no hay acceso administrativo).",
                "Shared secret con caracteres especiales mal escapados (comillas, espacios) causando mismatch.",
                "Servidor AAA con IP o puerto incorrecto (paquetes AAA enviados a destino inexistente).",
                "Accounting omitido (sin registro de auditoría para cumplimiento normativo).",
                "Conflictos entre server group y servidor individual (grupo apunta a IP distinta a la configurada directamente).",
            ],
        },
        "scientific_basis": "AAA requiere una method list bien definida con fallback local para evitar bloqueo administrativo. El shared secret debe coincidir exactamente (case-sensitive). El accounting debe habilitarse explícitamente para cada tipo de acceso (Cisco AAA Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la method list existe, está aplicada al line vty o console. Verifique 'aaa new-model' y la asignación.",
            "Un servidor AAA 'alcanzable' por ping NO garantiza que el puerto específico esté abierto. Verifique con netcat.",
            "Descarte la hipótesis de shared secret solo si ha comparado carácter por carácter ambas configuraciones.",
        ],
        "references": [
            "RFC 2865: Remote Authentication Dial-In User Service (RADIUS)",
            "Cisco AAA Configuration Guide",
            "Cisco Live BRKSEC-4032: AAA Troubleshooting",
        ],
        "fix": (
            "1. Ordenar method list con servidor remoto primero y fallback local, aplicar a login/enable/dot1x.\n"
            "2. Corregir/escapar shared secret para coincidir exactamente con el servidor.\n"
            "3. Configurar IP y puertos correctos del servidor RADIUS/TACACS+.\n"
            "4. Habilitar accounting para exec/commands/network.\n"
            "5. Resolver conflictos entre server groups y servidores individuales.\n"
            "6. Probar autenticación con usuario local y remoto; verificar logs.\n"
        ),
    },
    "switch_l2_config.switch_l2_config_start": {
        "hypothesis": "La configuración de switching L2 no produce el comportamiento esperado debido a un mismatch de VLAN nativa en un trunk, una configuración incorrecta de LACP (modos incompatibles), o la falta de spanning-tree portfast en puertos de acceso.",
        "verification_steps": [
            "1. Verificar que los puertos trunk tengan la misma VLAN nativa y las mismas VLANs permitidas en ambos extremos.",
            "2. Confirmar que la negociación LACP (EtherChannel) use modos compatibles (active-active o active-passive).",
            "3. Validar que los puertos de acceso tengan Spanning Tree PortFast habilitado para evitar delay de convergencia.",
            "4. Revisar que las VLANs existan en la base de datos del switch y estén activas antes de asignarlas a puertos.",
            "5. Inspeccionar que no haya BPDU Filter aplicado globalmente o por error en puertos donde se necesita STP.",
        ],
        "expected_evidence": {
            "confirming": [
                "Trunk con VLAN nativa idéntica y VLANs permitidas coincidentes en ambos extremos.",
                "LACP en modo compatible (active/passive) con todas las interfaces del canal en Up/Up.",
                "PortFast habilitado en puertos de acceso (edge) para evitar delay de 30s en STP.",
                "VLANs existentes en la base de datos del switch y en estado activo.",
                "BPDU Guard/Filter aplicado solo donde corresponde (edge vs trunk) sin conflictos.",
            ],
            "invalidating": [
                "VLAN nativa mismatch en trunk (tráfico untagged procesado en VLAN incorrecta, aislamiento de management).",
                "LACP en modos incompatibles (active vs on) o velocidades desajustadas en miembros del canal.",
                "PortFast omitido en puertos de acceso (delay de 30s en STP, usuarios reportan 'red lenta').",
                "VLAN no creada en el switch (puerto asignado a VLAN inexistente, tráfico no conmutado).",
                "BPDU Filter aplicado en puerto troncal (STP no detecta loops, posible tormenta de broadcast).",
            ],
        },
        "scientific_basis": "La consistencia de trunking (VLAN nativa y allowed list) es crítica para la conectividad L2. LACP requiere modos compatibles y parámetros idénticos en miembros. PortFast debe habilitarse en puertos edge para evitar el delay de convergencia STP (Cisco Campus LAN Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un puerto trunk está Up, las VLANs permitidas coinciden. Verifique 'show interfaces trunk'.",
            "Un EtherChannel en 'bundled' NO garantiza que todos los miembros estén activos. Verifique 'show etherchannel summary'.",
            "Descarte la hipótesis de VLAN solo si ha verificado la existencia de la VLAN en 'show vlan brief'.",
        ],
        "references": [
            "IEEE 802.1Q: Virtual Bridged Local Area Networks",
            "IEEE 802.3ad: Link Aggregation Control Protocol (LACP)",
            "Cisco Campus LAN Configuration Guide",
        ],
        "fix": (
            "1. Alinear VLAN nativa y VLANs permitidas en trunks.\n"
            "2. Configurar LACP con modos compatibles y parámetros idénticos en miembros.\n"
            "3. Habilitar PortFast en puertos de acceso.\n"
            "4. Crear/activar VLANs antes de asignarlas a puertos.\n"
            "5. Aplicar BPDU Guard/Filter solo donde corresponde.\n"
            "6. Validar conectividad L2 y estado de EtherChannel.\n"
        ),
    },
    "vrrp_hsrp_config.vrrp_hsrp_config_start": {
        "hypothesis": "La configuración de redundancia de gateway (VRRP/HSRP/GLBP) no produce el comportamiento esperado debido a un mismatch de grupo/VRID, una prioridad mal calculada, una autenticación incompatible, o un preempt no habilitado cuando el diseño lo requiere.",
        "verification_steps": [
            "1. Verificar que el número de grupo (HSRP group / VRRP vrid) sea idéntico en ambos routers del par.",
            "2. Confirmar que la prioridad esté configurada correctamente (router activo con prioridad más alta).",
            "3. Validar que la autenticación (si se usa) tenga el mismo tipo y clave en ambos routers.",
            "4. Revisar que preempt esté habilitado en el router designado como activo (si el diseño requiere recaptura).",
            "5. Inspeccionar que la interfaz virtual (SVI) y la interfaz física subyacente estén en estado Up en ambos routers.",
        ],
        "expected_evidence": {
            "confirming": [
                "Grupo/VRID idéntico en ambos routers del par de redundancia.",
                "Prioridad configurada correctamente (activo > standby) según diseño.",
                "Autenticación coincidente en tipo y clave en ambos routers (si aplica).",
                "Preempt habilitado en el router designado para recapturar el rol activo tras recuperación.",
                "Interfaz virtual y física en estado Up/Up en ambos routers.",
            ],
            "invalidating": [
                "Grupo/VRID desajustado (routers no se ven como pares, dos gateways activos independientes).",
                "Prioridad por defecto igual en ambos routers (elección no determinística por IP más alta).",
                "Autenticación mismatch (paquetes VRRP/HSRP descartados, ambos routers se declaran activos).",
                "Preempt deshabilitado (router de mayor prioridad no recaptura el rol tras recuperación).",
                "Interfaz física o SVI en Down (router no puede enviar/recibir Hellos, declarado inactivo).",
            ],
        },
        "scientific_basis": "VRRP (RFC 3768) y HSRP (Cisco propietario) requieren grupo y autenticación coincidentes. La prioridad define el activo; un preempt deshabilitado impide la recaptura tras fallo. Un mismatch de autenticación causa split-brain (ambos routers activos) con MAC conflictiva.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un router tiene prioridad 110, será siempre activo. Verifique si el otro tiene prioridad mayor o preempt deshabilitado.",
            "Un 'show standby brief' o 'show vrrp' en un solo router NO muestra el estado del par. Verifique ambos.",
            "Descarte la hipótesis de interfaz solo si ha verificado el estado físico y lógico en AMBOS routers.",
        ],
        "references": [
            "RFC 3768: Virtual Router Redundancy Protocol (VRRP)",
            "Cisco HSRP Configuration Guide",
            "Cisco Live BRKCRS-2501: Campus LAN Troubleshooting",
        ],
        "fix": (
            "1. Alinear número de grupo/VRID en ambos routers.\n"
            "2. Configurar prioridad correcta (activo con valor más alto según diseño).\n"
            "3. Coincidir tipo y clave de autenticación si se usa.\n"
            "4. Habilitar preempt en el router designado para recapturar rol activo.\n"
            "5. Asegurar que SVI e interfaz física subyacente estén Up/Up.\n"
            "6. Verificar un único gateway activo y failover funcional.\n"
        ),
    },
    "static_config.static_config_start": {
        "hypothesis": "La configuración de rutas estáticas no produce el comportamiento esperado debido a un error de sintaxis en la máscara, un next-hop inalcanzable, una distancia administrativa mal elegida, o la falta de asociación con IP SLA/BFD para retiro automático.",
        "verification_steps": [
            "1. Verificar que la sintaxis de la ruta estática sea válida (dirección de red, máscara, next-hop o interfaz de salida correctos).",
            "2. Confirmar que el next-hop configurado sea alcanzable directamente o resoluble vía IGP.",
            "3. Validar que la distancia administrativa/preferencia sea la adecuada para el rol de la ruta (principal vs flotante).",
            "4. Revisar que la interfaz de salida especificada esté en estado Up (si se usa sintaxis de salida por interfaz).",
            "5. Inspeccionar que el track IP SLA o BFD esté configurado y activo si la ruta requiere retiro condicional.",
        ],
        "expected_evidence": {
            "confirming": [
                "Sintaxis de ruta estática válida y commit exitoso sin errores de parser.",
                "Next-hop alcanzable directamente o resuelto por IGP en la RIB.",
                "Distancia administrativa correcta (ej. 1 para principal, 10 para flotante).",
                "Interfaz de salida en estado Up/Up (si la ruta usa interfaz de salida).",
                "Track IP SLA o BFD asociado a la ruta estática y en estado activo.",
            ],
            "invalidating": [
                "Sintaxis inválida (máscara mal formada, dirección IP con octetos >255, o next-hop en subnet distinta sin ruta).",
                "Next-hop inalcanzable (ruta estática no se instala en la RIB).",
                "Distancia administrativa mayor que IGP/BGP (ruta nunca se usa aunque esté instalada).",
                "Interfaz de salida Down (ruta retirada automáticamente de la FIB).",
                "Track IP SLA o BFD no configurado o caído (ruta permanece activa aunque el path esté roto).",
            ],
        },
        "scientific_basis": "La ruta estática se instala en la RIB solo si el next-hop es alcanzable. La distancia administrativa determina la preferencia frente a rutas dinámicas. El track IP SLA/BFD permite retiro automático cuando el path falla, pero debe configurarse explícitamente (Cisco IP Routing Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la ruta está en 'show run', está en la FIB. Verifique 'show ip route' y 'show ip cef'.",
            "Una distancia administrativa 'más baja' NO siempre es mejor; verifique el diseño de preferencia de rutas.",
            "Descarte la hipótesis de track solo si ha verificado que el SLA/BFD está activo y la ruta reacciona a su caída.",
        ],
        "references": [
            "Cisco IP Routing Configuration Guide",
            "Juniper Routing Protocols Configuration Guide",
            "Cisco Live BRKRST-3035: Advanced IP Routing Troubleshooting",
        ],
        "fix": (
            "1. Corregir sintaxis de ruta estática (red, máscara, next-hop/interfaz).\n"
            "2. Asegurar next-hop alcanzable directamente o resoluble por IGP.\n"
            "3. Ajustar distancia administrativa para principal/flotante según diseño.\n"
            "4. Confirmar interfaz de salida Up si se usa sintaxis de salida por interfaz.\n"
            "5. Configurar track IP SLA/BFD activo para retiro condicional.\n"
            "6. Verificar instalación en RIB/FIB.\n"
        ),
    },
    "nat_config.nat_config_start": {
        "hypothesis": "La configuración NAT no produce el comportamiento esperado debido a un error en la ACL de inside source, un pool de direcciones mal definido, una falta de overload en PAT, o la omisión de la clasificación inside/outside en interfaces.",
        "verification_steps": [
            "1. Verificar que las interfaces estén correctamente clasificadas como inside o outside.",
            "2. Confirmar que la ACL de inside source capture las direcciones privadas que deben ser traducidas.",
            "3. Validar que el pool de direcciones NAT tenga IPs válidas y suficientes para el número de conexiones esperadas.",
            "4. Revisar que PAT (overload) esté habilitado cuando se usa una única IP pública para múltiples hosts internos.",
            "5. Inspeccionar que no existan rutas de retorno asimétricas que eviten que el tráfico traducido regrese al dispositivo NAT.",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaces correctamente clasificadas como inside y outside.",
                "ACL de inside source con contadores de match para las subnets privadas de interés.",
                "Pool NAT con direcciones válidas y suficientes (o PAT overload habilitado).",
                "PAT overload configurado para escenarios de muchos hosts internos con pocas IPs públicas.",
                "Path de retorno simétrico a través del mismo dispositivo NAT.",
            ],
            "invalidating": [
                "Interfaces sin clasificación inside/outside (NAT no evalúa el tráfico).",
                "ACL demasiado restrictiva (no incluye la subnet del host interno; contadores en cero).",
                "Pool NAT con IPs fuera del rango asignado o duplicadas (errores de sintaxis o commit).",
                "Overload omitido en PAT (solo primera conexión traducida, resto rechazada por agotamiento de puertos).",
                "Ruta de retorno asimétrica (tráfico de vuelta pasa por otro router que no tiene la traducción activa).",
            ],
        },
        "scientific_basis": "NAT requiere la clasificación correcta de interfaces. PAT (overload) es obligatorio cuando múltiples hosts internos comparten una IP pública. El pool debe contener IPs válidas del segmento outside. La asimetría de rutas rompe las traducciones stateful (Cisco NAT Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show ip nat translations' muestra algunas entradas, el pool es suficiente. Verifique la tasa de agotamiento.",
            "Una ACL 'permit ip any any' en inside source NO siempre es correcta; verifique la dirección del tráfico.",
            "Descarte la hipótesis de asimetría solo si ha trazado el path de retorno en TODOS los routers posibles.",
        ],
        "references": [
            "RFC 3022: Traditional IP Network Address Translator (Traditional NAT)",
            "Cisco NAT Configuration Guide",
            "Cisco Live BRKRST-3320: NAT Deep Dive",
        ],
        "fix": (
            "1. Clasificar correctamente interfaces inside/outside.\n"
            "2. Ajustar ACL inside source para las subnets privadas.\n"
            "3. Definir pool NAT con IPs válidas/suficientes o habilitar overload.\n"
            "4. Habilitar PAT (overload) cuando muchos hosts comparten IP pública.\n"
            "5. Asegurar path de retorno simétrico por el mismo NAT device.\n"
            "6. Validar traducciones activas y conectividad saliente.\n"
        ),
    },
    "ripv2_config.ripv2_config_start": {
        "hypothesis": "La configuración RIPv2 no produce el comportamiento esperado debido a un error en las sentencias de red (versión 1 vs 2), una autenticación incompatible, o la falta de deshabilitación del auto-summary en redes discontiguas.",
        "verification_steps": [
            "1. Verificar que RIP esté configurado en modo version 2 en todas las interfaces y routers del dominio.",
            "2. Confirmar que las sentencias de red incluyan las interfaces deseadas con la wildcard mask correcta.",
            "3. Validar que la autenticación (texto o MD5) sea idéntica en tipo y clave en todos los vecinos.",
            "4. Revisar que el auto-summary esté deshabilitado si la red usa subnets discontiguas (no contiguous).",
            "5. Inspeccionar que no existan interfaces pasivas aplicadas por error a enlaces donde se requieren adyacencias.",
        ],
        "expected_evidence": {
            "confirming": [
                "RIPv2 habilitado globalmente y en interfaces (sin interfaces en versión 1 por error).",
                "Network statements con wildcard mask correcta capturando interfaces de tránsito.",
                "Autenticación coincidente en tipo y clave en todos los routers RIP.",
                "Auto-summary deshabilitado (no auto-summary) para redes discontiguas.",
                "Sin interfaces de tránsito configuradas como passive-interface.",
            ],
            "invalidating": [
                "RIPv1 en algunas interfaces (broadcast de version 1 ignorado por routers v2, adyacencias incompletas).",
                "Network statement con wildcard incorrecta (interfaces no incluidas o incluidas de más).",
                "Autenticación mismatch (paquetes RIP descartados, vecinos no visibles).",
                "Auto-summary habilitado en red discontigua (subnets resumidas incorrectamente, rutas faltantes).",
                "Passive-interface en enlace troncal (Hellos no enviados, adyacencia RIP imposible).",
            ],
        },
        "scientific_basis": "RIPv2 (RFC 2453) requiere versión 2 para soportar subnet masks en las actualizaciones. La autenticación debe coincidir. El auto-summary en redes discontiguas causa resumen incorrecto y blackholing (Cisco RIP Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show ip protocols' muestra RIP, todas las interfaces usan versión 2. Verifique 'show ip rip database'.",
            "Un 'network' statement correcto en una interfaz NO garantiza que la versión 2 esté activa en ella.",
            "Descarte la hipótesis de auto-summary solo si ha verificado la contigüidad de la red y la presencia de subnets remotas.",
        ],
        "references": [
            "RFC 2453: RIP Version 2",
            "Cisco RIP Configuration Guide",
            "Cisco Live BRKRST-3035: Advanced IP Routing Troubleshooting",
        ],
        "fix": (
            "1. Habilitar RIPv2 en todas las interfaces/routers del dominio.\n"
            "2. Corregir network statements/wildcard mask.\n"
            "3. Alinear autenticación texto/MD5 en todos los vecinos.\n"
            "4. Deshabilitar auto-summary en redes discontiguas.\n"
            "5. Eliminar passive-interface de enlaces troncales.\n"
            "6. Verificar vecinos y tabla de rutas RIP.\n"
        ),
    },
    "seguridad_config.seguridad_config_start": {
        "hypothesis": "La configuración de seguridad no produce el comportamiento esperado debido a un error de sintaxis en ACLs (orden de reglas), una autenticación 802.1X mal aplicada al puerto, un conflicto entre MACsec y la compatibilidad del hardware, o la falta de asociación de políticas AAA a los puertos de acceso.",
        "verification_steps": [
            "1. Verificar que las ACLs tengan el orden correcto (permit/deny) y que no haya reglas implícitas bloqueando tráfico necesario.",
            "2. Confirmar que 802.1X esté habilitado en el puerto de acceso y que el RADIUS server sea alcanzable.",
            "3. Validar que el hardware soporte MACsec si está configurado (algunos switches requieren licencias o linecards específicas).",
            "4. Revisar que las políticas de port security (sticky MAC, maximum MACs) estén configuradas acorde al diseño.",
            "5. Inspeccionar que las VLANs de voz y datos estén correctamente asignadas y que el trunking no esté habilitado por error en puertos de acceso.",
        ],
        "expected_evidence": {
            "confirming": [
                "ACLs con orden correcto de reglas y sin bloqueo implícito de tráfico de gestión o control.",
                "802.1X habilitado en puertos de acceso con RADIUS server alcanzable y method list aplicada.",
                "Hardware confirma soporte de MACsec (licencia activa, linecard compatible).",
                "Port security configurado con máximo de MACs y sticky MAC según diseño de seguridad.",
                "Puertos de acceso en modo access (no trunk) con VLAN de datos y voz correctas.",
            ],
            "invalidating": [
                "ACL con regla implícita 'deny any any' al final bloqueando tráfico de gestión (SSH, SNMP).",
                "802.1X no habilitado en puerto o RADIUS inalcanzable (autenticación falla, puerto en estado unauthorized).",
                "MACsec configurado en hardware no compatible (comando aceptado pero no aplicado al ASIC).",
                "Port security con máximo de MACs=1 y sticky deshabilitado (usuario legítimo bloqueado al cambiar de puerto).",
                "Puerto de acceso configurado como trunk por error (VLAN hopping, bypass de seguridad L2).",
            ],
        },
        "scientific_basis": "La seguridad de red requiere consistencia entre ACLs, autenticación 802.1X y port security. MACsec depende de hardware compatible. El orden de las ACLs es crítico: una regla prematura puede bloquear tráfico legítimo (Cisco Campus LAN Security Configuration Guide).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque una ACL tiene una regla permit, el tráfico pasa. Verifique el orden y las reglas anteriores.",
            "Un puerto con 802.1X configurado NO garantiza que el switch esté en modo 'multi-auth' si hay múltiples dispositivos.",
            "Descarte la hipótesis de hardware solo si ha verificado la datasheet y las licencias del switch/linecard.",
        ],
        "references": [
            "IEEE 802.1X: Port-Based Network Access Control",
            "Cisco Campus LAN Security Configuration Guide",
            "Cisco Live BRKSEC-4052: Campus LAN Security Troubleshooting",
        ],
        "fix": (
            "1. Reordenar ACLs para no bloquear tráfico de gestión/control legítimo.\n"
            "2. Habilitar 802.1X en puertos de acceso y asegurar RADIUS alcanzable.\n"
            "3. Verificar soporte de hardware/licencias para MACsec.\n"
            "4. Ajustar port security (máximo de MACs, sticky MAC) según diseño.\n"
            "5. Asignar correctamente VLANs de datos/voz y evitar trunk accidental en puertos de acceso.\n"
            "6. Validar acceso/autenticación y políticas de seguridad aplicadas.\n"
        ),
    },
    # ── MPLS ──────────────────────────────────────────────────────────
    "mpls.mpls_policies": {
        "hypothesis": (
            "Los bindings de labels no se generan o no se propagan para ciertas FECs porque una política de filtrado "
            "(accept/reject en LDP, prefix-segment policy en SR, o filtro de RSVP-TE) está descartando silenciosamente "
            "las etiquetas, o porque el rango local de labels (label space) se ha agotado para el prefijo de interés."
        ),
        "verification_steps": [
            "1. Revisar las policies de LDP/RSVP aplicadas a las FECs para detectar reglas explícitas de reject o deny.",
            "2. Verificar el rango de labels locales y el consumo actual con 'show mpls label range' / 'show ldp database summary'.",
            "3. Confirmar que la FEC objetivo exista en la RIB y no esté filtrada por un prefix-list antes de llegar a MPLS.",
            "4. Inspeccionar los logs de señalización en busca de mensajes 'Label space exhausted' o 'Policy rejected binding'.",
            "5. Validar que las policies de import/export de labels no tengan un orden de reglas que descarte prematuramente la FEC.",
        ],
        "expected_evidence": {
            "confirming": [
                "Policies de LDP/RSVP permiten explícitamente la FEC con reglas 'accept' o 'permit' sin restricciones.",
                "Rango de labels local con capacidad disponible (>10% libre) y sin mensajes de agotamiento en logs.",
                "La FEC aparece activa en la RIB global/VRF y no está filtrada por IGP prefix-list.",
                "Logs de señalización sin errores de 'Label space exhausted' ni 'Policy rejected' para la FEC.",
                "Bindings locales y remotos presentes en 'show ldp database' / 'show rsvp session' para la FEC.",
            ],
            "invalidating": [
                "Policy de LDP/RSVP con regla explícita 'reject' o 'deny' para el prefijo o el label de la FEC.",
                "Rango de labels local agotado ('Label space exhausted' o contadores al 100% de capacity).",
                "FEC ausente en la RIB por filtro de IGP o porque la redistribución no la inyectó.",
                "Logs indicando 'Policy rejected binding' o 'No label allocated' para el prefijo de interés.",
                "LDP database vacío o con 'No remote label' para la FEC debido a filtro de exportación del peer.",
            ],
        },
        "scientific_basis": (
            "Según RFC 5036, LDP permite aplicar policies de import/export que controlan qué bindings se aceptan o anuncian. "
            "Una policy restrictiva es una causa silenciosa de ausencia de labels. El agotamiento del label space es un evento "
            "de escala documentado en redes grandes (Cisco DocWiki: 'MPLS Label Space Exhaustion'). Los filtros de RSVP-TE "
            "pueden restringir qué LSPs se establecen basándose en admin-groups o bandwidth."
        ),
        "confidence_level": "Media",
        "bias_warnings": [
            "NO asuma que porque una FEC existe en la RIB, LDP/RSVP debe generar un label. Verifique las policies de señalización.",
            "Un binding local NO garantiza un binding remoto. Verifique ambos lados del LSP.",
            "Descarte la hipótesis de agotamiento solo si ha verificado el rango de labels y el conteo de entradas activas.",
        ],
        "references": [
            "RFC 5036: LDP Specification",
            "Cisco DocWiki: MPLS Label Space Exhaustion",
            "Juniper Networks: LDP Policy and Filtering Best Practices",
        ],
        "fix": (
            "1. Revisar policies LDP/RSVP/SR y cambiar reglas reject/deny a accept/permit para la FEC de interés.\n"
            "2. Ampliar rango de labels locales si está agotado.\n"
            "3. Confirmar que la FEC esté activa en RIB y no filtrada por IGP prefix-list.\n"
            "4. Ajustar orden de reglas en policies para no descartar prematuramente.\n"
            "5. Verificar bindings locales/remotos en 'show ldp database'/'show rsvp session'.\n"
            "6. Validar que la FEC tenga label asignado end-to-end.\n"
        ),
    },
    "mpls.mpls_igp_sync": {
        "hypothesis": (
            "La desincronización entre IGP y MPLS (ausencia de LDP-IGP Synchronization o IGP shortcut sin RSVP funcional) "
            "causa que el tráfico IP se enrute hacia un next-hop cuyo LSP está caído o incompleto, produciendo blackholing "
            "o forwarding IP directo no deseado en el core MPLS."
        ),
        "verification_steps": [
            "1. Verificar si está habilitada la sincronización LDP-IGP en las interfaces de tránsito del core.",
            "2. Confirmar que IGP no instale rutas hacia un next-hop si el LDP/RSVP adjacency no está operativo.",
            "3. Revisar el estado de los protocolos IGP y MPLS en paralelo: timestamps de convergencia y posible race condition.",
            "4. Validar la presencia de 'sync' o 'holddown' timers que retarden la instalación de rutas IGP hasta que LDP esté listo.",
            "5. Inspeccionar si IGP shortcut o Forwarding Adjacency está configurado pero sin LSP funcional.",
        ],
        "expected_evidence": {
            "confirming": [
                "LDP-IGP Synchronization habilitada y reportando estado 'Up' o 'Achieved' en todas las interfaces del área.",
                "IGP no instala rutas hacia next-hops con LDP session Down (ruta marcada como 'not installed' o 'LDP down').",
                "Convergencia simultánea de IGP y LDP: rutas y labels disponibles al mismo tiempo en los logs.",
                "Timers de sync configurados (ej. max-metric o holddown) para evitar forwarding antes de LDP ready.",
                "Sin tráfico IP siendo forwarded por interfaces sin label asignado en la LFIB.",
            ],
            "invalidating": [
                "LDP-IGP Sync no configurada o en estado 'Not Achieved' en enlaces críticos.",
                "IGP instala rutas activas hacia next-hop mientras LDP session está en NonExistent/Initialized.",
                "Race condition visible en logs: IGP convergence completa antes de LDP session Up (tráfico blackholed).",
                "IGP Shortcut habilitado pero RSVP/LDP no establece el LSP al next-hop shortcut.",
                "LFIB sin entrada para el next-hop IGP, pero la RIB sí tiene ruta activa (forwarding IP puro en core MPLS).",
            ],
        },
        "scientific_basis": (
            "RFC 5443 (LDP IGP Synchronization) define los mecanismos para evitar que IGP instale rutas antes de que LDP "
            "esté listo, preveniendo blackholing en redes donde MPLS es obligatorio para forwarding. En implementaciones Cisco, "
            "el timer 'mpls ldp igp sync holddown' retrasa la instalación de rutas OSPF/IS-IS hasta la sincronización de labels."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque IGP y LDP están Up ahora, estuvieron sincronizados durante la última reconvergencia. Verifique los logs.",
            "Un enlace con IGP y LDP Up NO garantiza que el neighbor tenga los labels necesarios para todos los prefijos.",
            "Descarte la hipótesis de sync solo si ha verificado la configuración de LDP-IGP sync en TODOS los routers del área.",
        ],
        "references": [
            "RFC 5443: LDP IGP Synchronization",
            "RFC 4202: Routing Extensions for Traffic Engineering",
            "Cisco MPLS Configuration Guide: LDP-IGP Synchronization",
        ],
        "fix": (
            "1. Habilitar LDP-IGP Synchronization en interfaces de tránsito del core.\n"
            "2. Configurar holddown timers para retrasar instalación de rutas IGP hasta que LDP esté listo.\n"
            "3. Evitar que IGP instale rutas hacia next-hops con LDP session Down.\n"
            "4. Verificar convergencia simultánea de IGP y LDP en logs.\n"
            "5. Revisar configuración de IGP shortcut/Forwarding Adjacency con LSP funcional.\n"
            "6. Confirmar que no haya forwarding IP puro en core MPLS sin label.\n"
        ),
    },
    "mpls.mpls_data_fwd": {
        "hypothesis": (
            "El reenvío de paquetes MPLS falla en el data plane porque la LFIB carece de una entrada válida para el label "
            "recibido, la pila de labels está mal formada (TTL expirado, stack mal balanceado), o la MTU de una interfaz "
            "del path es insuficiente para el paquete etiquetado."
        ),
        "verification_steps": [
            "1. Verificar la LFIB en cada salto del LSP para confirmar la presencia de entradas con acción 'pop', 'swap' o 'push' correcta.",
            "2. Revisar contadores de descarte MPLS ('show mpls forwarding-table drops' / 'show mpls statistics') en routers intermedios.",
            "3. Confirmar que la MTU de cada interfaz del path soporte el tamaño del payload más el overhead de labels MPLS.",
            "4. Validar que el TTL de los paquetes IP originales sea suficiente para sobrevivir al decremento por salto MPLS.",
            "5. Inspeccionar si existe Penultimate Hop Popping (PHP) configurado y si el egress PE espera el label correcto.",
        ],
        "expected_evidence": {
            "confirming": [
                "LFIB muestra entradas activas para todos los labels del LSP con operaciones válidas en cada salto.",
                "Contadores de descarte MPLS en cero o estables sin incremento durante el tráfico de prueba.",
                "MTU de todas las interfaces del path >= payload + 4 bytes por label en la pila (ej. >=1508 para dos labels).",
                "TTL del paquete origen suficiente para llegar al destino final después del decremento MPLS.",
                "PHP operativo: penultimate router envía sin label o con label explícito según diseño; egress PE recibe correctamente.",
            ],
            "invalidating": [
                "LFIB con entrada 'unresolved' o ausente para el label de transporte (causa descarte silencioso).",
                "Contadores de descarte MPLS incrementando en un router intermedio (fallo de LFIB o MTU).",
                "MTU insuficiente en interfaz del core (paquetes grandes descartados sin fragmentación por DF bit).",
                "TTL expired in transit en traceroute MPLS (TTL insuficiente o loop en el LSP).",
                "PHP deshabilitado cuando el egress PE espera un label, o PHP habilitado pero el PE no procesa IP nativo.",
            ],
        },
        "scientific_basis": (
            "La LFIB es la estructura de datos que determina el forwarding de paquetes etiquetados (RFC 3031). Una entrada faltante "
            "produce descarte silencioso. El overhead de labels (4 bytes por etiqueta) requiere MTU ajustada (RFC 3032). PHP "
            "reduce la pila en el penúltimo salto, pero si el egress PE espera un label específico (ej. por VPN), PHP puede "
            "causar descarte si no está coordinado."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show mpls forwarding-table' muestra una entrada, el hardware la ha programado. Verifique 'show platform mpls'.",
            "Un ping pequeño exitoso NO excluye un problema de MTU. Pruebe con paquetes de tamaño máximo con DF.",
            "Descarte la hipótesis de LFIB solo si ha verificado la tabla en TODOS los routers del path LSP.",
        ],
        "references": [
            "RFC 3031: Multiprotocol Label Switching Architecture",
            "RFC 3032: MPLS Label Stack Encoding",
            "Cisco Live BRKRST-3041: Advanced MPLS Troubleshooting",
        ],
        "fix": (
            "1. Completar entradas faltantes en LFIB para labels del LSP (pop/swap/push correctos).\n"
            "2. Corregir stack de labels desbalanceado en ingress/transit/egress.\n"
            "3. Aumentar MTU en interfaces del path para soportar payload + overhead de labels.\n"
            "4. Ajustar TTL de origen para sobrevivir decremento por salto MPLS.\n"
            "5. Verificar configuración de PHP coordinada con egress PE.\n"
            "6. Validar reenvío de paquetes MPLS sin descartes en data plane.\n"
        ),
    },
    "mpls.mpls_data_mtu": {
        "hypothesis": (
            "La MTU insuficiente en una o más interfaces del path MPLS causa fragmentación o descarte silencioso de paquetes "
            "etiquetados, especialmente cuando se usan stacks de múltiples labels (Transport + VPN + Entropy) que añaden 12+ bytes "
            "al frame original, superando la MTU configurada en el enlace físico."
        ),
        "verification_steps": [
            "1. Verificar la MTU configurada en todas las interfaces físicas y lógicas del path MPLS (PE, P routers, interfaces PE-CE).",
            "2. Calcular el overhead máximo de labels esperado (ej. 3 labels x 4 bytes = 12 bytes) y sumarlo al MTU del payload.",
            "3. Ejecutar ping con tamaño máximo y DF bit activado desde el CE hacia el CE remoto a través del L3VPN/L2VPN.",
            "4. Revisar contadores de 'giant frames', 'MTU exceeded' o 'input/output errors' en interfaces del core y del borde.",
            "5. Validar que la MTU de la interfaz PE-CE sea coherente con la MTU del core MPLS menos el overhead de labels.",
        ],
        "expected_evidence": {
            "confirming": [
                "MTU de interfaces del core >= 1504 bytes (para 1 label) o >= 1516 bytes (para 4 labels) según diseño.",
                "Ping con payload 1472 bytes + DF exitoso a través del LSP (valida MTU end-to-end con un label).",
                "Sin contadores de 'MTU exceeded', 'giant frames' ni 'input errors' creciendo en interfaces del path.",
                "PE-CE MTU configurada de forma que payload + labels del core no exceda la MTU de ningún salto.",
                "Fragmentación no observada en captures de tráfico MPLS (paquetes intactos en todos los saltos).",
            ],
            "invalidating": [
                "MTU de interfaz física en core = 1500 bytes con stack de 3 labels (payload > 1488 bytes es descartado).",
                "Ping con payload > 1472 bytes y DF activado falla en algún salto del LSP (indica MTU insuficiente).",
                "Contadores de 'MTU exceeded' o 'giant frames' incrementando en una interfaz del path.",
                "PE-CE MTU = 1500 pero core solo soporta 1500 (los 12 bytes de labels causan descarte de paquetes de 1492+).",
                "Captura de paquetes muestra fragmentación de paquetes MPLS o ICMP 'MTU exceeded' desde un salto intermedio.",
            ],
        },
        "scientific_basis": (
            "MPLS añade 4 bytes por etiqueta al frame (RFC 3032). En escenarios L3VPN con Penultimate Hop Popping, el core puede "
            "transportar 2 labels (Transport + VPN) = 8 bytes adicionales. Con Entropy Label o SR se pueden añadir más. La MTU "
            "del enlace físico debe incrementarse proporcionalmente (Juniper/Cisco recomiendan MTU >= 1504 para un label, >= 1512 "
            "para tres labels) para evitar descartes silenciosos."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO descarte la hipótesis de MTU solo porque los vecinos LDP están Up. Los Hellos son pequeños y pasan, pero el tráfico de usuario puede droppear.",
            "Un 'show interfaces' sin errores NO excluye descartes por MTU. Verifique contadores específicos de MPLS.",
            "Descarte la hipótesis de MTU solo si ha verificado con pings de tamaño máximo en ambos sentidos del LSP.",
        ],
        "references": [
            "RFC 3032: MPLS Label Stack Encoding",
            "Juniper Networks: MPLS MTU Best Practices",
            "Cisco Live BRKRST-3041: Advanced MPLS Troubleshooting",
        ],
        "fix": (
            "1. Aumentar MTU en interfaces físicas/lógicas del path MPLS (>=1504 para 1 label, >=1516 para 4 labels).\n"
            "2. Calcular overhead máximo de labels esperado y sumarlo al payload.\n"
            "3. Ejecutar ping con tamaño máximo y DF entre CEs a través del servicio MPLS.\n"
            "4. Limpiar contadores de 'MTU exceeded'/'giant frames'.\n"
            "5. Alinear MTU PE-CE con MTU core menos overhead de labels.\n"
            "6. Confirmar que no haya fragmentación ni descartes silenciosos.\n"
        ),
    },
    "mpls.mpls_data_blackhole": {
        "hypothesis": (
            "El blackholing de tráfico MPLS ocurre cuando un paquete etiquetado llega a un router que no tiene entrada en la LFIB "
            "para ese label (label swapping incorrecto), cuando el egress PE no puede resolver el payload IP a una VRF/IP global "
            "válida, o cuando el LSP es unidireccional y el return path usa un label no programado."
        ),
        "verification_steps": [
            "1. Verificar la LFIB en cada salto del LSP para confirmar que el label recibido tiene una entrada válida con next-hop correcto.",
            "2. Revisar si el label stack está balanceado correctamente: push en ingress, swap en transit, pop en egress/penultimate.",
            "3. Confirmar que el egress PE tiene una ruta válida hacia el destino final del payload (en la VRF o tabla global según diseño).",
            "4. Validar la simetría del LSP: verificar que el path de ida y vuelta usen labels correctamente programados en ambas direcciones.",
            "5. Inspeccionar contadores de descarte por 'No label' o 'Lookup failed' en los routers del core.",
        ],
        "expected_evidence": {
            "confirming": [
                "LFIB con entradas válidas para todos los labels del LSP en ida y vuelta en cada router.",
                "Label stack balanceado: push/swap/pop en los saltos correctos según el diseño del servicio.",
                "Egress PE con ruta activa hacia el destino del payload en la tabla de rutas apropiada (VRF o global).",
                "Simetría de LSP confirmada: traceroute MPLS bidireccional exitoso entre PEs.",
                "Sin contadores de descarte por 'No label' o 'Lookup failed' en routers del path.",
            ],
            "invalidating": [
                "LFIB con entrada 'unresolved' o ausente para el label transporte en un router intermedio.",
                "Label stack desbalanceado: ingress hace push de un label que ningún transit router tiene en su LFIB.",
                "Egress PE sin ruta hacia el destino del payload (paquete poppeado pero no enrutable tras quitar labels).",
                "Asimetría de LSP: path de ida funcional pero return path usa un LSP caído o no programado.",
                "Contadores de 'No label' o 'Lookup failed' creciendo en un router específico del path.",
            ],
        },
        "scientific_basis": (
            "El blackholing MPLS es un evento de data plane donde el paquete etiquetado es descartado sin generar ICMP hacia el origen "
            "(a menos que el router esté configurado para generar ICMP para TTL expired). Según RFC 3032, un label desconocido "
            "debe descartarse. La asimetría de LSPs es particularmente peligrosa porque un ping puede funcionar en un sentido pero "
            "no en el otro."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un ping funciona en un sentido, el LSP es simétrico. Verifique ambas direcciones.",
            "Un paquete ICMP TTL-expired del core NO implica que el LSP funcione; verifique el forwarding real del tráfico de usuario.",
            "Descarte la hipótesis de blackhole solo si ha verificado la LFIB y las rutas en TODOS los routers del path LSP.",
        ],
        "references": [
            "RFC 3032: MPLS Label Stack Encoding",
            "RFC 3031: Multiprotocol Label Switching Architecture",
            "Cisco Live BRKRST-3041: Advanced MPLS Troubleshooting",
        ],
        "fix": (
            "1. Completar entradas LFIB faltantes para labels de transporte/VPN en cada salto.\n"
            "2. Corregir label stack para que push/swap/pop estén balanceados en ida y vuelta.\n"
            "3. Asegurar que egress PE tenga ruta hacia destino del payload en VRF/tabla global.\n"
            "4. Verificar simetría del LSP bidireccional con traceroute MPLS.\n"
            "5. Limpiar contadores de 'No label'/'Lookup failed'.\n"
            "6. Validar que el tráfico de usuario alcance el destino sin blackholing.\n"
        ),
    },
    "mpls.mpls_te_path": {
        "hypothesis": (
            "El túnel RSVP-TE no establece el LSP deseado porque el path calculado por CSPF no es viable: la TED (Traffic Engineering "
            "Database) está desactualizada, las restricciones de bandwidth o admin-group no se cumplen en todos los saltos, o RSVP "
            "encuentra errores de reserva (Reservation Error) en un nodo intermedio."
        ),
        "verification_steps": [
            "1. Verificar la TED local con 'show mpls traffic-eng topology' para confirmar que los enlaces del path tienen bandwidth disponible.",
            "2. Revisar las restricciones del túnel TE (affinity, admin-group, bandwidth, explicit-path) contra la topología real.",
            "3. Validar el estado de la sesión RSVP para el túnel: Path/Resv messages intercambiados sin errores de reserva.",
            "4. Inspeccionar logs de RSVP en busca de 'Reservation Error', 'Bad Tunnel', o 'No Route To Destination'.",
            "5. Confirmar que OSPF/IS-IS TE extensions estén habilitadas y propagando los TLVs de bandwidth en todas las áreas del path.",
        ],
        "expected_evidence": {
            "confirming": [
                "TED muestra bandwidth disponible suficiente en cada enlace del path calculado por CSPF.",
                "Restricciones del túnel (affinity, admin-group) coinciden con las capacidades de los enlaces del path.",
                "RSVP session en Up con Path y Resv messages intercambiados sin errores en todos los nodos.",
                "Sin logs de 'Reservation Error' ni 'Bad Tunnel' para el tunnel ID de interés.",
                "OSPF/IS-IS TE extensions activas y LSDB/LSP contienen los TLVs de bandwidth en todos los routers del área.",
            ],
            "invalidating": [
                "TED muestra bandwidth disponible = 0 o insuficiente en uno o más enlaces del path.",
                "Restricción de admin-group/affinity excluye todos los posibles enlaces del path (CSPF no encuentra ruta).",
                "RSVP session en Down con 'Reservation Error' por insuficiencia de bandwidth en un salto intermedio.",
                "Logs de RSVP indicando 'No Route To Destination' (ruta explícita no alcanzable o salto inexistente).",
                "OSPF/IS-IS sin TE extensions en algún router del área (LSDB no contiene bandwidth, CSPF usa métrica IGP pura).",
            ],
        },
        "scientific_basis": (
            "RSVP-TE (RFC 3209) utiliza CSPF para calcular un path que cumpla restricciones de bandwidth y admin-groups. La TED "
            "debe estar sincronizada con el IGP. Si un enlace del path no tiene bandwidth suficiente, RSVP devuelve un 'Reservation "
            "Error' y el LSP no se establece. Las extensiones TE de OSPF (RFC 3630) e IS-IS (RFC 5305) son obligatorias para que "
            "la TED refleje recursos reales."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el IGP path funciona, CSPF encontrará un path válido. Las restricciones TE pueden excluir el único path disponible.",
            "Un 'show mpls traffic-eng tunnels' con estado 'Up' NO garantiza que esté usando el path deseado. Verifique el explicit-path actual.",
            "Descarte la hipótesis de bandwidth solo si ha verificado la TED y la reserva RSVP en TODOS los nodos del path.",
        ],
        "references": [
            "RFC 3209: RSVP-TE: Extensions to RSVP for LSP Tunnels",
            "RFC 3630: Traffic Engineering Extensions to OSPF",
            "RFC 5305: IS-IS Extensions for Traffic Engineering",
        ],
        "fix": (
            "1. Verificar TED y asegurar bandwidth disponible en cada enlace del path.\n"
            "2. Ajustar restricciones de admin-group/affinity para que CSPF encuentre ruta.\n"
            "3. Resolver errores de reserva RSVP ('Reservation Error') aumentando bandwidth o reduciendo solicitud.\n"
            "4. Habilitar OSPF/IS-IS TE extensions en todos los routers del área.\n"
            "5. Corregir explicit-path si un salto es inalcanzable.\n"
            "6. Confirmar que el túnel TE establezca LSP con Path/Resv intercambiados.\n"
        ),
    },
    # ── BGP ───────────────────────────────────────────────────────────
    "bgp.bgp_neighbor": {
        "hypothesis": (
            "La sesión BGP no alcanza el estado Established porque existe una falla de conectividad TCP de Capa 3/4 (firewall bloqueando "
            "TCP 179, ACLs), un mismatch de parámetros de sesión (AS local/remoto, MD5 password, timers, update-source, eBGP multihop), "
            "o una interfaz de origen inestable/cambiando de estado."
        ),
        "verification_steps": [
            "1. Verificar conectividad IP y apertura de puerto TCP 179 entre los peers con telnet/nc o captura de paquetes.",
            "2. Comparar el AS local, AS remoto, update-source, eBGP multihop y MD5 password en ambos extremos de la sesión.",
            "3. Revisar los timers BGP (Hold/Keepalive) para descartar mismatch de temporizadores.",
            "4. Inspeccionar logs de BGP en busca de NOTIFICATION messages que indiquen el motivo del rechazo de sesión.",
            "5. Validar que la interfaz de update-source esté en estado Up/Up y que su IP sea la correcta para iBGP/eBGP.",
        ],
        "expected_evidence": {
            "confirming": [
                "Ping/traceroute exitoso entre las IPs de los peers BGP y TCP 179 accesible (SYN-ACK confirmado).",
                "AS local/remoto, update-source, eBGP multihop y MD5 coinciden exactamente en ambos extremos.",
                "Timers BGP idénticos (Hold/Keepalive) en la configuración de ambos peers.",
                "Sin mensajes de NOTIFICATION recientes en logs; sesión en Established con uptime estable.",
                "Interfaz de update-source en Up/Up con IP correcta y sin flaps recientes.",
            ],
            "invalidating": [
                "TCP 179 no accesible (connection refused, timeout, o SYN descartado por firewall/ACL).",
                "AS mismatch: local AS en un extremo no coincide con remote AS del otro (NOTIFICATION con 'OPEN message error').",
                "MD5 password mismatch (TCP MD5 signature verification failure, sesión reinicia cíclicamente).",
                "Timers desajustados (Hold time menor que Keepalive x 3; sesión flappea cada pocos segundos).",
                "Update-source caída o con IP incorrecta (BGP intenta originar sesión desde interfaz inexistente).",
            ],
        },
        "scientific_basis": (
            "BGP (RFC 4271) opera sobre TCP 179. El establecimiento de sesión requiere alcanzabilidad IP y apertura de puerto. El AS "
            "mismatch es detectado en el OPEN message y causa NOTIFICATION. El MD5 password (RFC 2385) debe coincidir exactamente para "
            "que TCP acepte la conexión. La interfaz de update-source inestable es una causa común de flaps en iBGP."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que un ping exitoso implica que TCP 179 está abierto. Verifique explícitamente con 'telnet <peer> 179'.",
            "Un estado 'Active' NO significa que el peer esté activo; significa que está intentando conectar activamente.",
            "Descarte la hipótesis de parámetros solo si ha comparado TODOS los campos del OPEN message en ambos extremos.",
        ],
        "references": [
            "RFC 4271: A Border Gateway Protocol 4 (BGP-4)",
            "RFC 2385: Protection of BGP Sessions via the TCP MD5 Signature Option",
            "Cisco Live BRKRST-3320: BGP Troubleshooting Deep Dive",
        ],
        "fix": (
            "1. Restaurar conectividad IP y apertura de TCP 179 entre peers.\n"
            "2. Corregir AS local/remoto, update-source, eBGP multihop y MD5 password.\n"
            "3. Sincronizar timers BGP Hold/Keepalive.\n"
            "4. Revisar NOTIFICATION messages para identificar rechazo de sesión.\n"
            "5. Asegurar que interfaz update-source esté Up/Up con IP correcta.\n"
            "6. Confirmar sesión BGP Established y uptime estable.\n"
        ),
    },
    "bgp.bgp_routes": {
        "hypothesis": (
            "La sesión BGP está Established pero no se intercambian prefijos debido a políticas de filtrado restrictivas (route-maps, "
            "prefix-lists, community-filters) aplicadas en el sentido incorrecto, un mismatch de address-family capabilities, o un Next-Hop "
            "inalcanzable que impide la instalación de las rutas recibidas en la RIB local."
        ),
        "verification_steps": [
            "1. Verificar que la address family deseada esté activada bajo el neighbor y que las capabilities se hayan negociado correctamente.",
            "2. Revisar Adj-RIB-In y Adj-RIB-Out para confirmar si los prefijos están siendo recibidos pero filtrados, o no anunciados.",
            "3. Inspeccionar las políticas de entrada y salida (route-maps, prefix-lists, distribute-lists) para detectar filtros explícitos.",
            "4. Validar que el Next-Hop de las rutas recibidas sea alcanzable vía IGP y no esté descartado por una política de next-hop.",
            "5. Confirmar que los prefijos locales existan en la tabla de rutas y que la redistribución hacia BGP no esté omitida.",
        ],
        "expected_evidence": {
            "confirming": [
                "Address family activada y capabilities negociadas en el OPEN message ('advertised and received').",
                "Adj-RIB-In muestra prefijos recibidos; Adj-RIB-Out muestra prefijos anunciados hacia el peer.",
                "Políticas de enrutamiento permiten explícitamente los prefijos de interés (sin descarte por community o prefix-list).",
                "Next-Hop de rutas recibidas alcanzable vía IGP y resuelto en la RIB local.",
                "Prefijos locales presentes en la tabla de rutas y redistribuidos correctamente al proceso BGP.",
            ],
            "invalidating": [
                "Address family no activada bajo el peer (BGP no anuncia ni recibe rutas de esa familia).",
                "Adj-RIB-In vacío a pesar de sesión Established (peer no anuncia por policy de salida remota o prefijo no existe).",
                "Route-map o prefix-list de entrada descartando silenciosamente los prefijos recibidos (contadores de match creciendo).",
                "Next-Hop inalcanzable ('unreachable next-hop' en BGP output; rutas recibidas pero no instaladas en RIB).",
                "Prefijos locales ausentes en la tabla de rutas o redistribución hacia BGP omitida/filtrada.",
            ],
        },
        "scientific_basis": (
            "BGP (RFC 4271) aplica políticas en la entrada (Adj-RIB-In -> Loc-RIB) y salida (Loc-RIB -> Adj-RIB-Out). Un prefix "
            "puede ser recibido pero descartado por policy sin afectar la sesión. El Next-Hop debe ser alcanzable para que la ruta sea "
            "instalada (RFC 4271, Sección 9.1.2.1). Las capabilities determinan qué address families se intercambian."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show ip bgp summary' muestra prefijos recibidos, están en la RIB. Verifique 'show ip bgp' y 'show ip route'.",
            "Un '0 received' puede deberse a políticas del peer remoto, no a falla local. Coordinar verificación bilateral.",
            "Descarte la hipótesis de Next-Hop solo si ha verificado la ruta IGP hacia el Next-Hop en TODOS los routers de recepción.",
        ],
        "references": [
            "RFC 4271: A Border Gateway Protocol 4 (BGP-4)",
            "Cisco Live BRKRST-3320: BGP Troubleshooting Deep Dive",
            "Juniper BGP Policy and Route Filtering Guide",
        ],
        "fix": (
            "1. Activar address family deseada bajo el neighbor y verificar capabilities.\n"
            "2. Revisar Adj-RIB-In/Out para detectar prefijos recibidos pero filtrados.\n"
            "3. Ajustar route-maps/prefix-lists de entrada/salida para permitir prefijos de interés.\n"
            "4. Asegurar que Next-Hop de rutas recibidas sea alcanzable vía IGP.\n"
            "5. Verificar que prefijos locales existan en tabla de rutas y redistribución hacia BGP.\n"
            "6. Confirmar instalación de rutas en RIB local.\n"
        ),
    },
    "bgp.bgp_path": {
        "hypothesis": (
            "El router no selecciona el bestpath esperado porque los atributos BGP determinantes (LOCAL_PREF, AS_PATH, MED, "
            "ORIGIN, IGP metric to next-hop) no tienen los valores óptimos según el diseño, o porque la ruta más específica "
            "no está siendo anunciada/recibida correctamente."
        ),
        "verification_steps": [
            "1. Listar todas las rutas candidatas al destino con 'show ip bgp <prefix>' y comparar atributos en el orden de bestpath.",
            "2. Verificar que LOCAL_PREF sea coherente con el diseño de tráfico entrante (preferencia de upstreams).",
            "3. Confirmar que el MED sea comparable (mismo AS de origen) y que no esté siendo ignorado por 'bgp always-compare-med' omitido.",
            "4. Revisar la métrica IGP hacia el Next-Hop en rutas recibidas por iBGP (IGP cost puede decidir bestpath en empate).",
            "5. Validar que la ruta más específica (/32, /24) esté presente y no esté siendo filtrada o resumida inadvertidamente.",
        ],
        "expected_evidence": {
            "confirming": [
                "Bestpath seleccionado coincide con la política de diseño tras evaluar LOCAL_PREF > AS_PATH > MED > IGP metric.",
                "LOCAL_PREF configurado consistentemente para preferir el upstream/camino deseado.",
                "MED comparable entre rutas del mismo AS de origen (o 'always-compare-med' habilitado si aplica).",
                "IGP metric hacia Next-Hop coherente con el camino preferido en empate de atributos superiores.",
                "Ruta más específica presente en BGP y no filtrada por summarization o aggregate.",
            ],
            "invalidating": [
                "Bestpath seleccionado ignora LOCAL_PREF más alto por un atributo con mayor precedencia no documentado.",
                "LOCAL_PREF inconsistente entre routers de borde (tráfico entrante no balanceado según diseño).",
                "MED ignorado porque los candidatos provienen de AS diferentes y 'always-compare-med' no está configurado.",
                "IGP metric hacia Next-Hop subóptima causa selección de bestpath peor aunque MED/AS_PATH sean iguales.",
                "Ruta más específica filtrada por aggregate-address summary-only o por una política de supresión.",
            ],
        },
        "scientific_basis": (
            "El algoritmo de Best Path Selection de BGP (RFC 4271, Sección 9.1) es determinista y jerárquico: WEIGHT > LOCAL_PREF > "
            "AS_PATH > ORIGIN > MED > eBGP/iBGP > IGP metric. Un desconocimiento del orden de evaluación es causa frecuente de "
            "'routing no deseado'. El MED solo es comparable entre rutas del mismo AS a menos que se configure 'always-compare-med'."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un atributo tiene valor 'mejor', esa ruta será bestpath. Verifique el orden completo de decisión.",
            "Una ruta con MED más bajo puede perder contra una con IGP metric más baja si los atributos superiores empatan.",
            "Descarte la hipótesis de atributos solo si ha evaluado TODOS los candidatos con 'show ip bgp <prefix> detail'.",
        ],
        "references": [
            "RFC 4271: A Border Gateway Protocol 4 (BGP-4)",
            "Cisco Live BRKRST-3320: BGP Troubleshooting Deep Dive",
            "Juniper BGP Path Selection Algorithm",
        ],
        "fix": (
            "1. Comparar atributos de rutas candidatas con 'show ip bgp <prefix>'.\n"
            "2. Ajustar LOCAL_PREF según diseño de tráfico entrante.\n"
            "3. Habilitar 'bgp always-compare-med' si MED proviene de AS diferentes y debe compararse.\n"
            "4. Optimizar métrica IGP hacia Next-Hop para romper empates.\n"
            "5. Asegurar que la ruta más específica esté presente y no resumida/suprimida.\n"
            "6. Verificar que bestpath seleccionado coincida con política de diseño.\n"
        ),
    },
    "bgp.bgp_rr": {
        "hypothesis": (
            "La topología de Route Reflector o Confederations causa bucles de routing, reflexión inconsistente de rutas, o "
            "split-horizon en iBGP que impide que los clientes RR reciban prefijos desde otros clusters o sub-AS, debido a "
            "un mal diseño de cluster-ID, originator-ID, o falta de next-hop-self en los reflectores."
        ),
        "verification_steps": [
            "1. Verificar que los Route Reflectores tengan cluster-ID único y que no haya loops de reflexión entre RRs.",
            "2. Revisar el atributo ORIGINATOR_ID en las rutas recibidas para detectar rechazo por loop de origen.",
            "3. Confirmar que los clientes RR reciban rutas reflejadas desde otros clusters (verificar que no se apliquen filters de cluster-list).",
            "4. Validar que next-hop-self esté configurado en los RRs o que el IGP anuncie los next-hops de los peers iBGP.",
            "5. En confederations: verificar que el sub-AS path sea coherente y que no haya bucles intra-confederation.",
        ],
        "expected_evidence": {
            "confirming": [
                "Route Reflectores con cluster-ID único y sin loops en la topología de reflexión (malla de RRs estable).",
                "Atributo ORIGINATOR_ID presente y no igual al Router-ID del receptor (sin loop de origen).",
                "Clientes RR recibiendo rutas reflejadas desde múltiples clusters con cluster-list válido.",
                "Next-hop de rutas iBGP alcanzable vía IGP (o next-hop-self configurado en RRs).",
                "En confederations: sub-AS path coherente y sin bucles; rutas propagadas correctamente entre sub-AS.",
            ],
            "invalidating": [
                "Cluster-ID duplicado causando que las rutas sean descartadas por loop de cluster-list.",
                "ORIGINATOR_ID igual al Router-ID local (ruta generada localmente o loop de origen detectado).",
                "Filtro de cluster-list descartando rutas de otros clusters (cliente RR aislado de prefijos remotos).",
                "Next-hop de rutas reflejadas inalcanzable (sin next-hop-self ni IGP reachability al next-hop del peer iBGP).",
                "Confederation con sub-AS path loop (rutas descartadas por loop detection intra-confederation).",
            ],
        },
        "scientific_basis": (
            "Los Route Reflectores (RFC 4456) rompen la regla de split-horizon iBGP pero introducen riesgos de loop mediante "
            "cluster-list y originator-ID. Un cluster-ID duplicado causa que las rutas sean rechazadas. En confederations (RFC 5065), "
            "el AS_PATH se divide en sub-ASes; un loop de sub-AS path causa descarte de rutas. El next-hop de una ruta reflejada "
            "debe ser alcanzable para los clientes RR."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un RR tiene rutas, sus clientes también las tienen. Verifique la RIB de los clientes RR.",
            "Un cluster-ID 'correcto' en un RR NO garantiza unicidad en el dominio. Verifique TODOS los RRs.",
            "Descarte la hipótesis de loop solo si ha trazado el cluster-list y originator-ID en la ruta completa.",
        ],
        "references": [
            "RFC 4456: BGP Route Reflection",
            "RFC 5065: Autonomous System Confederations for BGP",
            "Cisco Live BRKRST-3320: BGP Troubleshooting Deep Dive",
        ],
        "fix": (
            "1. Asignar cluster-ID único a cada Route Reflector.\n"
            "2. Verificar ORIGINATOR_ID no genere loop de origen.\n"
            "3. Permitir rutas reflejadas desde otros clusters (no filtrar cluster-list).\n"
            "4. Configurar next-hop-self en RRs o anunciar next-hops vía IGP.\n"
            "5. En confederations, asegurar sub-AS path coherente y sin bucles.\n"
            "6. Confirmar que clientes RR reciban rutas y next-hops sean alcanzables.\n"
        ),
    },
    "bgp.bgp_policies": {
        "hypothesis": (
            "Las políticas de enrutamiento BGP (route-maps, community-filters, AS-Path filters) están configuradas en el sentido "
            "incorrecto o con criterios demasiado restrictivos, descartando silenciosamente prefijos legítimos o aplicando atributos "
            "no deseados que desvían el tráfico de su path óptimo."
        ),
        "verification_steps": [
            "1. Verificar la dirección de aplicación de cada route-map/prefix-list (in vs out) para confirmar que filtran en el sentido esperado.",
            "2. Revisar los criterios de match (community, AS-Path, prefix-list, ACL) para detectar reglas demasiado restrictivas.",
            "3. Confirmar que los set actions (LOCAL_PREF, MED, community) apliquen los valores correctos sin sobrescribir atributos críticos.",
            "4. Validar el orden de las secuencias en route-maps (las secuencias de deny al principio pueden bloquear tráfico legítimo).",
            "5. Inspeccionar los contadores de matches en las políticas para identificar qué secuencias están activamente descartando prefijos.",
        ],
        "expected_evidence": {
            "confirming": [
                "Route-maps aplicados en la dirección correcta (in para entrada, out para salida) según diseño.",
                "Criterios de match capturan exactamente los prefijos/comunidades/AS-Path deseados sin exclusiones accidentales.",
                "Set actions aplican LOCAL_PREF, MED y communities según el diseño de política de tráfico.",
                "Orden de secuencias en route-map coherente: permisos generales después de denegaciones específicas.",
                "Contadores de matches muestran que las secuencias de permit están activas y las de deny solo capturan lo esperado.",
            ],
            "invalidating": [
                "Route-map aplicado como 'in' cuando debería ser 'out', filtrando prefijos en el sentido equivocado.",
                "Prefix-list con wildcard o máscara incorrecta que excluye prefijos legítimos del cliente.",
                "Set action sobrescribiendo LOCAL_PREF con valor incorrecto (ej. 50 en lugar de 200) desviando tráfico.",
                "Secuencia 'deny any' al principio del route-map que descarta silenciosamente todos los prefijos.",
                "Contadores de matches muestran que una secuencia de deny está bloqueando prefijos que deberían permitirse.",
            ],
        },
        "scientific_basis": (
            "Las políticas BGP son la causa más común de 'prefijos faltantes' en redes de producción (Cisco Live BRKRST-3320). "
            "Un route-map mal direccionado (in vs out) o con match excesivo puede filtrar rutas sin generar errores visibles. "
            "El orden de las secuencias es crítico: una deny prematura impide la evaluación de permits posteriores."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la política existe, está siendo evaluada. Verifique que esté aplicada al neighbor correcto.",
            "Un 'permit any' al final del route-map NO compensa un 'deny any' al principio. Verifique el orden completo.",
            "Descarte la hipótesis de política solo si ha verificado los contadores de matches para CADA secuencia del route-map.",
        ],
        "references": [
            "RFC 4271: A Border Gateway Protocol 4 (BGP-4)",
            "Cisco Live BRKRST-3320: BGP Troubleshooting Deep Dive",
            "Juniper Routing Policy Framework Guide",
        ],
        "fix": (
            "1. Verificar dirección (in/out) de cada route-map/prefix-list.\n"
            "2. Ajustar criterios de match (community, AS-Path, prefix-list) para no excluir prefijos legítimos.\n"
            "3. Revisar set actions para LOCAL_PREF/MED/community según diseño.\n"
            "4. Reordenar secuencias: denegaciones específicas primero, permisos generales después.\n"
            "5. Revisar contadores de matches para identificar secuencias bloqueando tráfico.\n"
            "6. Confirmar que los prefijos esperados pasen las políticas y se instalen.\n"
        ),
    },
    # ── L3VPN ─────────────────────────────────────────────────────────
    "l3vpn.l3vpn_ce_pe": {
        "hypothesis": (
            "La falla de conectividad entre CE y PE es causada por un error en el protocolo de routing PE-CE (OSPF, BGP, estático), "
            "un mismatch de parámetros de vecindad (AS, timers, área, autenticación), o una falta de asociación de la interfaz PE-CE "
            "a la VRF correcta."
        ),
        "verification_steps": [
            "1. Verificar que la interfaz física/subinterfaz PE-CE esté en estado Up/Up y asociada a la VRF del cliente.",
            "2. Confirmar que el protocolo de routing PE-CE esté configurado dentro del contexto de la VRF (no en la tabla global).",
            "3. Comparar parámetros de vecindad: AS (BGP), área/timers/MTU (OSPF), gateway/next-hop (estático).",
            "4. Revisar que las VLANs/encapsulación en el enlace PE-CE coincidan en ambos extremos (trunk vs access, dot1q tag).",
            "5. Inspeccionar logs del protocolo de routing PE-CE para detectar mensajes de error de autenticación o mismatch.",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaz PE-CE en Up/Up y explícitamente vinculada a la VRF del cliente.",
                "Protocolo PE-CE configurado dentro del contexto VRF (vecinos visibles en 'show vrf <name> protocols').",
                "Parámetros de vecindad coincidentes en ambos extremos (AS, área, timers, MTU, autenticación).",
                "VLAN/encapsulación idéntica en CE y PE (sin mismatch de dot1q tag o modo trunk/access).",
                "Logs del protocolo sin errores de autenticación, MTU mismatch ni parameter mismatch.",
            ],
            "invalidating": [
                "Interfaz PE-CE en Down/Down o no asociada a la VRF (tráfico procesado en tabla global).",
                "Protocolo PE-CE configurado en la tabla global en lugar de la VRF (sin vecinos en el contexto correcto).",
                "AS mismatch (BGP), área/timers/MTU desajustados (OSPF), o next-hop inalcanzable (estático).",
                "VLAN mismatch en PE-CE (ej. CE envía untagged pero PE espera dot1q 100).",
                "Logs indicando errores de autenticación OSPF/BGP o 'Neighbor ignored due to MTU mismatch'.",
            ],
        },
        "scientific_basis": (
            "L3VPN (RFC 4364) requiere que el enlace PE-CE esté explícitamente en la VRF. El protocolo de routing PE-CE debe operar "
            "dentro del contexto de esa VRF para que las rutas del cliente sean redistribuibles a MP-BGP. Un mismatch de VLAN en el "
            "enlace físico es una causa clásica de falla de Capa 2 que impide toda adyacencia de Capa 3."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la interfaz está Up, la VRF binding es correcto. Verifique 'show vrf interfaces' explícitamente.",
            "Un vecino BGP visible en 'show ip bgp summary' NO garantiza que esté en la VRF correcta. Verifique la tabla de rutas.",
            "Descarte la hipótesis de protocolo solo si ha verificado la configuración dentro del contexto VRF en ambos extremos.",
        ],
        "references": [
            "RFC 4364: BGP/MPLS IP Virtual Private Networks (VPNs)",
            "Cisco L3VPN Configuration Guide",
            "Juniper Layer 3 VPNs Configuration Guide",
        ],
        "fix": (
            "1. Asegurar interfaz PE-CE Up/Up y vinculada a la VRF del cliente.\n"
            "2. Configurar protocolo de routing PE-CE dentro del contexto VRF.\n"
            "3. Alinear parámetros de vecindad (AS, área, timers, MTU, autenticación).\n"
            "4. Coincidir VLAN/encapsulación en enlace PE-CE.\n"
            "5. Revisar logs de autenticación o mismatch.\n"
            "6. Validar adyacencia PE-CE y rutas en la VRF.\n"
        ),
    },
    "l3vpn.l3vpn_ce_pe_down": {
        "hypothesis": (
            "La adyacencia CE-PE no se establece o cae porque los parámetros de Capa 2 están fallando (VLAN mismatch, cable desconectado, "
            "duplex/speed), o porque los parámetros del protocolo de routing (OSPF area, BGP AS, timers, autenticación) no coinciden "
            "en ambos extremos del enlace PE-CE."
        ),
        "verification_steps": [
            "1. Verificar estado físico del enlace PE-CE: LEDs, 'show interface status', velocidad/duplex negociados.",
            "2. Confirmar que la VLAN/encapsulación configurada en el PE coincida exactamente con la del CE.",
            "3. Comparar parámetros del protocolo de routing en CE y PE (AS BGP, área OSPF, timers, autenticación).",
            "4. Revisar que la interfaz PE no esté en un estado administrativo que bloquee el protocolo de routing (shutdown, passive).",
            "5. Validar que no existan ACLs o storm-control en el switch/PE que descarten los paquetes de control del protocolo PE-CE.",
        ],
        "expected_evidence": {
            "confirming": [
                "Enlace PE-CE en Up/Up con velocidad/duplex coincidentes y sin errores físicos creciendo.",
                "VLAN/encapsulación idéntica en CE y PE (verificado en configuración y captures de tráfico).",
                "Parámetros de protocolo (AS, área, timers, auth) exactamente iguales en ambos extremos.",
                "Interfaz PE no en shutdown ni passive; estado administrativo permite envío/recepción de Hellos/Updates.",
                "Sin ACLs ni storm-control descartando paquetes de control del protocolo PE-CE en el path L2.",
            ],
            "invalidating": [
                "Enlace PE-CE en Down/Down o con errores físicos crecientes (CRC, runts, input errors).",
                "VLAN mismatch: CE envía tráfico en VLAN 10 pero PE espera VLAN 20 (sin conectividad L2).",
                "AS BGP desajustado, área OSPF diferente, timers mismatch, o autenticación MD5/key-id incorrecta.",
                "Interfaz PE en shutdown o passive-interface (sin Hellos/Updates enviados ni recibidos).",
                "ACL o storm-control en switch/PE descartando paquetes de control (OSPF multicast 224.0.0.5, BGP TCP 179).",
            ],
        },
        "scientific_basis": (
            "La adyacencia PE-CE depende de una base L2 estable (IEEE 802.1Q, autonegociación). Un mismatch de VLAN o duplex impide "
            "cualquier comunicación L3. Los protocolos de routing requieren coincidencia de parámetros básicos: AS en BGP, área/timers/MTU "
            "en OSPF, MD5 en autenticación (RFC 2328, RFC 4271). Un enlace físico caído es la causa raíz más común."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque los LEDs están verdes, el enlace está libre de errores. Verifique contadores de CRC/duplex.",
            "Un 'show ip ospf neighbor' vacío puede deberse a Capa 2, no siempre a OSPF. Verifique la VLAN y la interfaz primero.",
            "Descarte la hipótesis de parámetros solo si ha comparado TODOS los campos de configuración del protocolo en CE y PE.",
        ],
        "references": [
            "RFC 2328: OSPF Version 2",
            "RFC 4271: A Border Gateway Protocol 4 (BGP-4)",
            "Cisco L3VPN Troubleshooting Guide",
        ],
        "fix": (
            "1. Resolver estado físico del enlace PE-CE (cable, SFP, dúplex, velocidad).\n"
            "2. Corregir VLAN/encapsulación en CE y PE.\n"
            "3. Alinear AS BGP, área OSPF, timers, autenticación.\n"
            "4. Levantar interfaz PE si está shutdown y quitar passive-interface si aplica.\n"
            "5. Eliminar ACLs/storm-control que descarten paquetes de control.\n"
            "6. Confirmar adyacencia estable en ambos extremos.\n"
        ),
    },
    "l3vpn.l3vpn_redist": {
        "hypothesis": (
            "Los prefijos del cliente no llegan al core MP-BGP porque la redistribución desde el protocolo PE-CE (OSPF, BGP, estático, "
            "RIP) hacia MP-BGP VPNv4 está omitida, mal configurada, o filtrada por un route-map que bloquea los prefijos de interés."
        ),
        "verification_steps": [
            "1. Verificar que exista una sentencia de redistribución explícita del protocolo PE-CE hacia BGP bajo el address-family VPNv4.",
            "2. Confirmar que el route-map asociado a la redistribución no tenga reglas de deny que capturen los prefijos del cliente.",
            "3. Revisar la tabla de rutas de la VRF local para confirmar que los prefijos del cliente están presentes y activos.",
            "4. Validar que los prefijos redistribuidos aparezcan en la VPNv4 RIB ('show bgp vpnv4 unicast' / 'show route table bgp.l3vpn.0').",
            "5. Inspeccionar los contadores de matches del route-map de redistribución para detectar si los prefijos están siendo filtrados.",
        ],
        "expected_evidence": {
            "confirming": [
                "Redistribución explícita configurada del protocolo PE-CE hacia MP-BGP VPNv4 bajo el VRF.",
                "Route-map de redistribución con reglas de permit para los prefijos/comunidades del cliente.",
                "Prefijos del cliente presentes y activos en la tabla de rutas de la VRF local.",
                "Prefijos del cliente visibles en la VPNv4 RIB con next-hop y labels MPLS asignados.",
                "Contadores de matches del route-map mostrando que los prefijos del cliente pasan la política de redistribución.",
            ],
            "invalidating": [
                "Redistribución hacia MP-BGP omitida o configurada bajo address-family IPv4 global en lugar de VPNv4.",
                "Route-map de redistribución con deny explícito o implícito ('deny any') que bloquea prefijos del cliente.",
                "Prefijos del cliente ausentes en la tabla de rutas de la VRF (falla PE-CE previa a la redistribución).",
                "Prefijos presentes en VRF local pero ausentes en VPNv4 RIB (indica falla de redistribución o filtrado).",
                "Contadores de matches del route-map muestran que los prefijos del cliente coinciden con una secuencia deny.",
            ],
        },
        "scientific_basis": (
            "L3VPN requiere que las rutas del cliente en la VRF local sean redistribuidas explícitamente a MP-BGP VPNv4 (RFC 4364). "
            "Una redistribución omitida o mal direccionada (ej. hacia IPv4 unicast global) hace que las rutas nunca lleguen al core. "
            "Los route-maps de redistribución pueden filtrar rutas basándose en prefix-lists, tags o communities."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el protocolo PE-CE tiene vecinos, la redistribución a MP-BGP está configurada. Verifique 'address-family vpnv4'.",
            "Un 'show ip route vrf' con rutas NO garantiza que estén en MP-BGP. Verifique 'show bgp vpnv4 unicast vrf'.",
            "Descarte la hipótesis de filtrado solo si ha verificado cada secuencia del route-map de redistribución.",
        ],
        "references": [
            "RFC 4364: BGP/MPLS IP Virtual Private Networks (VPNs)",
            "Cisco L3VPN Configuration Guide",
            "Juniper Layer 3 VPNs Configuration Guide",
        ],
        "fix": (
            "1. Configurar redistribución explícita del protocolo PE-CE hacia MP-BGP VPNv4.\n"
            "2. Revisar route-map de redistribución y cambiar denies que afecten prefijos del cliente.\n"
            "3. Confirmar prefijos del cliente en tabla de rutas de VRF local.\n"
            "4. Verificar prefijos en VPNv4 RIB.\n"
            "5. Revisar contadores de matches del route-map.\n"
            "6. Validar que prefijos lleguen al PE destino e instalen en VRF remota.\n"
        ),
    },
    "l3vpn.l3vpn_policies": {
        "hypothesis": (
            "Los prefijos VPNv4 son recibidos pero descartados silenciosamente debido a un mismatch en los Route Targets de importación/exportación, "
            "un RD duplicado que rompe la unicidad del prefijo en el core, o un Site-of-Origin (SOO) que previene loops de redistribución "
            "bloqueando la re-importación de rutas propias."
        ),
        "verification_steps": [
            "1. Verificar que los Route Targets de export en el PE origen coincidan exactamente con los de import en el PE destino (y viceversa).",
            "2. Confirmar que el RD configurado en cada VRF sea único en todo el dominio MPLS (sin duplicados).",
            "3. Revisar si el atributo SOO está aplicado a las rutas recibidas del CE y si impide la re-importación desde MP-BGP.",
            "4. Validar que las políticas de entrada/salida VPNv4 no filtren comunidades extendidas (RT) o prefijos por error.",
            "5. Inspeccionar la VPNv4 RIB en el PE destino para confirmar si las rutas llegan pero se marcan como 'not imported to VRF'.",
        ],
        "expected_evidence": {
            "confirming": [
                "Export-RT en PE origen == Import-RT en PE destino; sin mismatch de comunidades extendidas.",
                "RD único por VRF en todo el dominio; sin duplicados detectados en logs ni en la VPNv4 RIB.",
                "SOO configurado consistentemente y no bloqueando la re-importación de rutas legítimas.",
                "Políticas VPNv4 permiten el paso de comunidades extendidas RT sin filtrado accidental.",
                "Rutas VPNv4 recibidas en PE destino y correctamente importadas a la VRF local ('imported' / 'installed').",
            ],
            "invalidating": [
                "Export-RT de origen no coincide con Import-RT de destino (rutas recibidas pero descartadas silenciosamente).",
                "RD duplicado en dos VRFs distintas (prefijos no distinguibles en el core, causando blackholing o loop).",
                "SOO bloqueando la re-importación (ruta recibida desde MP-BGP pero descartada por loop prevention de SOO).",
                "Policy de entrada VPNv4 filtrando comunidades RT (rutas recibidas pero no procesadas para importación a VRF).",
                "Rutas presentes en VPNv4 RIB pero marcadas como 'not imported' o 'rejected' al intentar instalar en VRF local.",
            ],
        },
        "scientific_basis": (
            "RFC 4364 define que RTs controlan la importación/exportación de rutas VPNv4. Un mismatch de RT es un error de configuración "
            "silencioso: las rutas se reciben pero se descartan antes de ser importadas. Un RD duplicado rompe la unicidad de los NLRI "
            "en MP-BGP. El atributo SOO (RFC 4364, Sección 4.5) evita loops de redistribución pero puede bloquear rutas legítimas si "
            "está mal aplicado."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la sesión MP-BGP está Up, los RTs son correctos. Verifique TODOS los RTs en ambos PEs.",
            "Un RD 'correcto' en un PE NO garantiza unicidad en el dominio. Verifique todos los RDs de la red.",
            "Descarte la hipótesis de SOO solo si ha verificado que el valor SOO no coincide con el origen de la ruta recibida.",
        ],
        "references": [
            "RFC 4364: BGP/MPLS IP Virtual Private Networks (VPNs)",
            "Cisco Live BRKRST-3340: Advanced L3VPN Troubleshooting",
            "Juniper Layer 3 VPNs Configuration Guide",
        ],
        "fix": (
            "1. Alinear export-RT en PE origen con import-RT en PE destino (y viceversa).\n"
            "2. Asignar RD único por VRF en todo el dominio.\n"
            "3. Revisar SOO para no bloquear re-importación legítima.\n"
            "4. Permitir comunidades extendidas RT en policies de entrada/salida VPNv4.\n"
            "5. Verificar en VPNv4 RIB destino si las rutas llegan y se importan a VRF.\n"
            "6. Confirmar conectividad inter-site del cliente.\n"
        ),
    },
    "l3vpn.l3vpn_mpbgp": {
        "hypothesis": (
            "Las sesiones MP-BGP entre PEs no establecen la address family VPNv4/VPNv6, o los prefijos son anunciados pero el Next-Hop "
            "no es alcanzable vía el core MPLS, impidiendo la instalación de rutas VPN en la LFIB y causando blackholing del tráfico "
            "inter-site del cliente."
        ),
        "verification_steps": [
            "1. Verificar que la sesión BGP base esté Established y que la address family VPNv4/VPNv6 esté activada bajo el neighbor.",
            "2. Confirmar que el capability exchange en el OPEN message incluya AFI/SAFI 1/128 (VPNv4) o 2/128 (VPNv6).",
            "3. Validar que el Next-Hop de las rutas VPNv4 sea la loopback del PE origen y que sea alcanzable vía IGP/MPLS.",
            "4. Revisar que los labels de transporte (LDP/SR) estén asignados a la /32 loopback del PE origen en todos los routers del core.",
            "5. Inspeccionar la VPNv4 RIB para confirmar que las rutas tengan next-hop resoluble y label stack completo.",
        ],
        "expected_evidence": {
            "confirming": [
                "Sesión BGP base Established con address family VPNv4/VPNv6 activada y capabilities negociadas.",
                "Capability exchange confirma AFI/SAFI 1/128 o 2/128 en ambos sentidos.",
                "Next-Hop de rutas VPNv4 alcanzable vía IGP y resuelto a un label MPLS en la LFIB de todos los PEs.",
                "Labels de transporte asignados a la loopback /32 del PE origen en la LFIB de todos los routers del core.",
                "VPNv4 RIB muestra rutas con next-hop resoluble, label de transporte y label de VPN correctamente asignados.",
            ],
            "invalidating": [
                "Sesión BGP base en Idle/Active o address family VPNv4 no activada bajo el peer.",
                "Capability mismatch: un peer no soporta AFI/SAFI 1/128 (VPNv4 session cae a Idle o no se activa).",
                "Next-Hop de rutas VPNv4 inalcanzable (ruta faltante en IGP hacia loopback del PE origen).",
                "Falta de label de transporte hacia la loopback del PE origen (LDP/SR no anuncia binding para la /32).",
                "VPNv4 RIB muestra rutas con next-hop 'unresolved' o sin label de transporte (no instalables en LFIB).",
            ],
        },
        "scientific_basis": (
            "MP-BGP (RFC 4760) extiende BGP para soportar múltiples AFI/SAFI. Para L3VPN, la familia VPNv4 (1/128) debe estar activada. "
            "El Next-Hop de las rutas VPNv4 debe ser alcanzable vía IGP y resuelto a un label MPLS; de lo contrario, el paquete no puede "
            "ser encapsulado en el core (RFC 4364, RFC 3032). La ausencia de label de transporte hacia el PE origen es causa común de "
            "blackholing."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque BGP IPv4 está Up, MP-BGP VPNv4 también lo está. Verifique explícitamente la familia VPNv4.",
            "Un 'show bgp vpnv4 unicast summary' con prefijos recibidos NO garantiza que estén resolubles. Verifique el Next-Hop.",
            "Descarte la hipótesis de Next-Hop solo si ha verificado la ruta IGP y el label MPLS hacia la loopback del PE origen.",
        ],
        "references": [
            "RFC 4364: BGP/MPLS IP Virtual Private Networks (VPNs)",
            "RFC 4760: Multiprotocol Extensions for BGP-4",
            "RFC 3032: MPLS Label Stack Encoding",
        ],
        "fix": (
            "1. Establecer sesión BGP base Established y activar address family VPNv4/VPNv6.\n"
            "2. Verificar capability exchange AFI/SAFI 1/128 o 2/128.\n"
            "3. Asegurar Next-Hop (loopback PE origen) alcanzable vía IGP/MPLS.\n"
            "4. Verificar labels de transporte hacia loopback PE origen en LFIB de core.\n"
            "5. Confirmar rutas VPNv4 con next-hop resoluble y label stack completo.\n"
            "6. Validar instalación en LFIB y forwarding de tráfico VPN.\n"
        ),
    },
    "l3vpn.l3vpn_mpbgp_down": {
        "hypothesis": (
            "La sesión MP-BGP cae o no negocia la familia VPNv4/VPNv6 debido a un capability mismatch, una política que rechaza la NLRI, "
            "o una falla del underlay IP/MPLS entre las loopbacks de PE que transporta la sesión TCP 179 de BGP."
        ),
        "verification_steps": [
            "1. Verificar el estado de la sesión BGP base: Idle, Active, Connect, OpenSent, OpenConfirm, Established.",
            "2. Revisar los mensajes de NOTIFICATION para identificar capability mismatch, AS mismatch, o policy reject.",
            "3. Confirmar que la address family VPNv4/VPNv6 esté activada bajo el neighbor en ambos PEs.",
            "4. Validar la conectividad IP y apertura de TCP 179 entre las loopbacks de PE a través del core MPLS/IP.",
            "5. Inspeccionar ACLs, firewall filters o QoS policies que puedan descartar paquetes TCP 179 entre loopbacks de PE.",
        ],
        "expected_evidence": {
            "confirming": [
                "Sesión BGP base en Established con uptime estable y sin NOTIFICATIONs recientes.",
                "Address family VPNv4/VPNv6 activada bajo el neighbor en ambos PEs.",
                "Capabilities exchange exitoso con AFI/SAFI 1/128 o 2/128 negociados en ambos sentidos.",
                "Ping/traceroute y TCP 179 accesibles entre loopbacks de PE vía underlay MPLS/IP.",
                "Sin ACLs, firewall filters ni QoS policies descartando tráfico TCP 179 entre loopbacks de PE.",
            ],
            "invalidating": [
                "Sesión BGP base en Idle/Active recurrente (falla de conectividad TCP o AS mismatch).",
                "NOTIFICATION de capability mismatch: un peer no soporta VPNv4/VPNv6 (OPEN message error).",
                "Address family VPNv4/VPNv6 no activada bajo el peer (BGP no negocia la familia).",
                "Ping o TCP 179 falla entre loopbacks de PE (underlay MPLS/IP roto o ACL bloqueando).",
                "ACL/firewall filter explícitamente descartando TCP 179 entre las IPs de loopback de los PEs.",
            ],
        },
        "scientific_basis": (
            "MP-BGP requiere que la address family esté explícitamente activada bajo cada neighbor (RFC 4760). Un capability mismatch "
            "en el OPEN message causa NOTIFICATION y caída de sesión. La sesión BGP base (TCP 179) depende del underlay IP/MPLS; si "
            "la loopback no es alcanzable, la sesión MP-BGP no puede establecerse (RFC 4271, RFC 4364)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el ping entre PEs funciona, TCP 179 está abierto. Verifique con 'telnet <loopback> 179'.",
            "Un estado 'Active' significa que está intentando conectar, no que la sesión esté activa.",
            "Descarte la hipótesis de underlay solo si ha verificado el path MPLS/IP completo entre loopbacks de PE.",
        ],
        "references": [
            "RFC 4271: A Border Gateway Protocol 4 (BGP-4)",
            "RFC 4760: Multiprotocol Extensions for BGP-4",
            "RFC 4364: BGP/MPLS IP Virtual Private Networks (VPNs)",
        ],
        "fix": (
            "1. Restaurar sesión BGP base o corregir capability mismatch.\n"
            "2. Activar address family VPNv4/VPNv6 bajo el neighbor.\n"
            "3. Verificar conectividad IP y TCP 179 entre loopbacks de PE.\n"
            "4. Eliminar ACLs/firewall filters/QoS descartando TCP 179.\n"
            "5. Corregir AS mismatch u otros NOTIFICATION.\n"
            "6. Confirmar sesión MP-BGP Established y estable.\n"
        ),
    },
    "l3vpn.l3vpn_mpbgp_noroutes": {
        "hypothesis": (
            "La sesión MP-BGP entre PEs está Up pero no se intercambian rutas VPNv4/VPNv6 porque los prefijos locales no son redistribuidos "
            "desde el protocolo PE-CE hacia MP-BGP, o porque las políticas de exportación (route-maps, RT filters) las descartan antes "
            "de ser anunciadas al peer remoto."
        ),
        "verification_steps": [
            "1. Verificar que los prefijos del cliente existan en la tabla de rutas de la VRF local en el PE origen.",
            "2. Confirmar que la redistribución del protocolo PE-CE hacia MP-BGP VPNv4 esté configurada y activa.",
            "3. Revisar las políticas de exportación BGP para detectar route-maps o prefix-lists que filtren los prefijos VPN.",
            "4. Validar que los Route Targets de exportación en la VRF coincidan con los de importación en el PE destino.",
            "5. Inspeccionar Adj-RIB-Out en el PE origen para confirmar si los prefijos VPN están siendo anunciados hacia el peer remoto.",
        ],
        "expected_evidence": {
            "confirming": [
                "Prefijos del cliente presentes y activos en la tabla de rutas de la VRF local en el PE origen.",
                "Redistribución PE-CE hacia MP-BGP configurada correctamente bajo el address-family VPNv4.",
                "Políticas de exportación BGP permiten explícitamente los prefijos/comunidades/RT del cliente.",
                "Export-RT en PE origen coincide con Import-RT en PE destino.",
                "Adj-RIB-Out en PE origen muestra los prefijos VPN siendo anunciados con atributos y labels correctos.",
            ],
            "invalidating": [
                "Prefijos del cliente ausentes en la VRF local (falla PE-CE previa a la redistribución).",
                "Redistribución hacia MP-BGP omitida o configurada bajo IPv4 unicast global en lugar de VPNv4.",
                "Route-map de salida descartando prefijos VPN por prefix-list, community o AS-Path filter.",
                "Export-RT en origen no coincide con Import-RT en destino (prefijos recibidos pero descartados silenciosamente).",
                "Adj-RIB-Out vacío para la familia VPNv4 hacia el peer remoto (prefijos no anunciados por falla local).",
            ],
        },
        "scientific_basis": (
            "MP-BGP solo anuncia prefijos que están presentes en su Loc-RIB y que pasan las políticas de exportación (RFC 4271). Para "
            "L3VPN, los prefijos deben ser redistribuidos explícitamente desde el protocolo PE-CE a la VPNv4 RIB. Un route-map de salida "
            "puede filtrar rutas basándose en prefix-lists, communities o RTs. Un mismatch de RT es una causa silenciosa de ausencia de "
            "prefijos en el PE destino (RFC 4364)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la sesión MP-BGP está Up, las rutas están siendo intercambiadas. Verifique Adj-RIB-In/Out.",
            "Un 'show ip bgp vpnv4 all summary' con prefijos '0 sent' indica falla de anuncio, no necesariamente de recepción.",
            "Descarte la hipótesis de redistribución solo si ha verificado que los prefijos están en la VRF Y en la VPNv4 RIB local.",
        ],
        "references": [
            "RFC 4364: BGP/MPLS IP Virtual Private Networks (VPNs)",
            "RFC 4271: A Border Gateway Protocol 4 (BGP-4)",
            "Cisco Live BRKRST-3340: Advanced L3VPN Troubleshooting",
        ],
        "fix": (
            "1. Verificar prefijos del cliente en VRF local del PE origen.\n"
            "2. Habilitar redistribución PE-CE hacia MP-BGP VPNv4.\n"
            "3. Revisar policies de exportación y permitir prefijos/comunidades/RT del cliente.\n"
            "4. Alinear export-RT origen con import-RT destino.\n"
            "5. Verificar Adj-RIB-Out VPNv4 hacia peer remoto.\n"
            "6. Confirmar recepción e instalación en VRF destino.\n"
        ),
    },
    "l3vpn.l3vpn_vrf_fwd": {
        "hypothesis": (
            "El plano de datos de la VRF falla porque el paquete ingresado desde el CE no es clasificado correctamente en la VRF "
            "(interfaz no vinculada a VRF), o porque el label de transporte/VPN no se resuelve correctamente en la LFIB del PE egress, "
            "provocando que el paquete sea descartado o enrutado por la tabla IP global."
        ),
        "verification_steps": [
            "1. Verificar que la interfaz PE-CE esté explícitamente vinculada a la VRF del cliente en ambos PEs.",
            "2. Revisar la LFIB del PE egress para confirmar que el label VPN recibido se resuelva a una interfaz de salida o next-hop VRF.",
            "3. Confirmar que la ruta de retorno desde el PE egress hacia el CE esté presente en la VRF local.",
            "4. Validar que el label stack recibido (transporte + VPN) sea el esperado según el diseño del servicio L3VPN.",
            "5. Inspeccionar contadores de descarte en la interfaz PE-CE y en la LFIB por 'VRF not found' o 'No route to host'.",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaz PE-CE explícitamente asociada a la VRF en ambos PEs (binding correcto verificado).",
                "LFIB del PE egress resuelve el label VPN a una interfaz CE o next-hop VRF válido.",
                "Ruta de retorno desde PE egress hacia CE presente y activa en la tabla de rutas de la VRF.",
                "Label stack recibido coincide con el diseño: label de transporte (LDP/SR) + label de VPN asignado por PE origen.",
                "Sin contadores de descarte por 'VRF not found', 'No route to host' ni LFIB miss en el PE egress.",
            ],
            "invalidating": [
                "Interfaz PE-CE no asociada a la VRF (paquete clasificado en tabla global, no en la VRF del cliente).",
                "LFIB del PE egress sin entrada para el label VPN (descarte silencioso del paquete etiquetado).",
                "Ruta de retorno hacia CE ausente en la VRF del PE egress (paquete poppeado pero no enrutable).",
                "Label stack incorrecto: label de VPN no coincide con el asignado por el PE origen (causa LFIB miss).",
                "Contadores de descarte creciendo en PE egress por 'VRF not found' o 'No route to host'.",
            ],
        },
        "scientific_basis": (
            "En L3VPN, el PE ingress encapsula el paquete IP con dos labels: transporte (LDP/SR) y VPN (asignado por MP-BGP). El PE egress "
            "hace pop del label de transporte y usa el label VPN para identificar la VRF y enrutar el paquete hacia el CE (RFC 4364). Si "
            "la interfaz PE-CE no está en la VRF, el paquete poppeado se enruta por la tabla global. Si el label VPN no está en la LFIB, "
            "el paquete se descarta."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la interfaz está configurada con 'ip vrf forwarding', el binding es activo. Verifique 'show vrf interfaces'.",
            "Un 'show mpls forwarding-table' con entradas NO garantiza que el label VPN específico esté resuelto. Verifique el label exacto.",
            "Descarte la hipótesis de LFIB solo si ha verificado la entrada del label VPN en el PE egress con tráfico de prueba activo.",
        ],
        "references": [
            "RFC 4364: BGP/MPLS IP Virtual Private Networks (VPNs)",
            "RFC 3031: Multiprotocol Label Switching Architecture",
            "Cisco Live BRKRST-3340: Advanced L3VPN Troubleshooting",
        ],
        "fix": (
            "1. Vincular explícitamente interfaz PE-CE a la VRF en ambos PEs.\n"
            "2. Completar entrada LFIB en PE egress para label VPN.\n"
            "3. Asegurar ruta de retorno hacia CE en VRF local del PE egress.\n"
            "4. Verificar label stack (transporte+VPN) según diseño.\n"
            "5. Limpiar contadores de descarte por 'VRF not found'/'No route to host'.\n"
            "6. Validar forwarding de paquetes del CE hacia el destino remoto.\n"
        ),
    },
    # ── EVPN ──────────────────────────────────────────────────────────
    "evpn.evpn_bgp": {
        "hypothesis": (
            "La sesión BGP EVPN no se establece o no intercambia rutas porque la address-family EVPN (AFI/SAFI 25/70) no está activada "
            "bajo el peer, existe un mismatch de capabilities en el OPEN message, o el underlay IP/MPLS entre PEs/VTEPs está roto, "
            "impidiendo el transporte de la sesión TCP 179."
        ),
        "verification_steps": [
            "1. Verificar que la address family EVPN esté activada explícitamente bajo el neighbor BGP en ambos PEs/VTEPs.",
            "2. Revisar el capability exchange en el OPEN message para confirmar AFI/SAFI 25/70 negociada.",
            "3. Confirmar que la sesión BGP base (TCP 179) esté Established entre las loopbacks/interfaces de origen.",
            "4. Validar la conectividad IP del underlay entre loopbacks de VTEPs/PEs con pings de tamaño MTU completo.",
            "5. Inspeccionar políticas de BGP que puedan filtrar la familia EVPN o bloquear el intercambio de capabilities.",
        ],
        "expected_evidence": {
            "confirming": [
                "Address family EVPN activada bajo el neighbor en ambos extremos.",
                "Capability exchange muestra AFI/SAFI 25/70 'advertised and received' en 'show bgp neighbors'.",
                "Sesión BGP base en Established sin NOTIFICATIONs recientes.",
                "Underlay IP/MPLS funcional: ping entre loopbacks exitoso con DF y tamaño >= 1550 bytes.",
                "Sin políticas de BGP descartando la familia EVPN o bloqueando capabilities.",
            ],
            "invalidating": [
                "Address family EVPN no activada bajo el peer (BGP no negocia EVPN).",
                "Capability mismatch: un peer no soporta AFI/SAFI 25/70 (NOTIFICATION con 'unsupported capability').",
                "Sesión BGP base en Idle/Active (falla de conectividad TCP 179 o AS mismatch).",
                "Ping entre loopbacks falla o requiere fragmentación (MTU insuficiente o underlay roto).",
                "Policy de BGP descartando la capability EVPN o filtrando NLRI de la familia.",
            ],
        },
        "scientific_basis": (
            "EVPN (RFC 7432) utiliza BGP como plano de control con la address family EVPN (AFI 25, SAFI 70). La sesión debe estar "
            "activa y las capabilities deben coincidir. El underlay IP o MPLS debe ser funcional para transportar la sesión BGP y los "
            "paquetes de datos encapsulados. La ausencia de la familia EVPN en la configuración del peer es una causa frecuente de "
            "falla silenciosa."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque BGP IPv4 está Up, BGP EVPN también lo está. Verifique explícitamente la familia EVPN.",
            "Un 'show bgp summary' con prefijos '0' en la familia EVPN NO significa ausencia de vecinos; puede ser falta de redistribución.",
            "Descarte la hipótesis de underlay solo si ha verificado con pings de tamaño MTU y traceroute entre loopbacks de PE/VTEP.",
        ],
        "references": [
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "RFC 8365: A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)",
            "Cisco Live BRKDCT-3378: EVPN Deep Dive and Troubleshooting",
        ],
        "fix": (
            "1. Activar address family EVPN (AFI/SAFI 25/70) bajo el neighbor en ambos PEs/VTEPs.\n"
            "2. Verificar capabilities exchange en OPEN message.\n"
            "3. Establecer sesión BGP base TCP 179 entre loopbacks/interfaces de origen.\n"
            "4. Restaurar underlay IP/MPLS entre loopbacks con MTU adecuado.\n"
            "5. Eliminar policies BGP que filtren familia EVPN o capabilities.\n"
            "6. Confirmar sesión BGP EVPN Established.\n"
        ),
    },
    "evpn.evpn_routes": {
        "hypothesis": (
            "Las rutas EVPN Tipo 1/2/3/5 no se propagan entre PEs/VTEPs porque los Route Targets no coinciden, las políticas de BGP "
            "filtran las NLRI EVPN, o el next-hop de las rutas EVPN no es alcanzable en el underlay IP/MPLS."
        ),
        "verification_steps": [
            "1. Verificar que los Route Targets de export en el PE origen coincidan con los de import en el PE destino para cada EVI.",
            "2. Revisar las políticas de entrada/salida BGP para detectar filtros que descarten NLRI EVPN por community o prefix-list.",
            "3. Confirmar que el next-hop de las rutas EVPN sea alcanzable vía underlay IGP/MPLS en todos los PEs receptores.",
            "4. Validar que las rutas EVPN estén presentes en la EVPN RIB local ('show bgp evpn' / 'show route table evpn.evpn.0').",
            "5. Inspeccionar si el peer remoto está anunciando y recibiendo rutas EVPN con 'show bgp neighbors <peer> advertised-routes'.",
        ],
        "expected_evidence": {
            "confirming": [
                "Export-RT en PE origen == Import-RT en PE destino para cada EVI de interés.",
                "Políticas BGP permiten explícitamente NLRI EVPN y no descartan comunidades extendidas RT.",
                "Next-Hop de rutas EVPN alcanzable vía underlay IGP/MPLS en todos los PEs receptores.",
                "Rutas EVPN Tipo 1/2/3/5 presentes en la EVPN RIB local con atributos válidos.",
                "Peer remoto anunciando y recibiendo rutas EVPN según contadores de 'advertised-routes' y 'received-routes'.",
            ],
            "invalidating": [
                "Export-RT e Import-RT desajustados para una EVI (rutas recibidas pero descartadas silenciosamente).",
                "Policy de BGP descartando NLRI EVPN por community-filter o prefix-list aplicado a la familia EVPN.",
                "Next-Hop de rutas EVPN inalcanzable (rutas recibidas pero no instaladas en forwarding).",
                "EVPN RIB local vacía para la EVI (falla de generación local de rutas Tipo 2/5).",
                "Peer remoto no anunciando rutas EVPN (falla de exportación o policy de salida remota).",
            ],
        },
        "scientific_basis": (
            "EVPN utiliza BGP para distribuir MACs, segmentos y prefijos IP. Las rutas EVPN son NLRI multiprotocolo que requieren "
            "RTs correctos para importación/exportación (RFC 7432). Un mismatch de RT es un error de configuración silencioso. El "
            "next-hop debe ser alcanzable en el underlay para que el data plane funcione (RFC 8365)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque BGP EVPN está Up, las rutas se propagan. Verifique la EVPN RIB en ambos extremos.",
            "Una ruta EVPN presente en la RIB local NO garantiza que esté siendo anunciada. Verifique Adj-RIB-Out.",
            "Descarte la hipótesis de RT solo si ha verificado TODOS los RTs de import/export en todos los PEs del segmento.",
        ],
        "references": [
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "RFC 8365: A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)",
            "Cisco Live BRKDCT-3378: EVPN Deep Dive and Troubleshooting",
        ],
        "fix": (
            "1. Alinear export-RT origen con import-RT destino para cada EVI.\n"
            "2. Revisar policies BGP para no descartar NLRI EVPN ni comunidades RT.\n"
            "3. Asegurar Next-Hop de rutas EVPN alcanzable en underlay.\n"
            "4. Verificar rutas EVPN Tipo 1/2/3/5 en EVPN RIB local.\n"
            "5. Confirmar anuncio/recepción con 'advertised-routes'/'received-routes'.\n"
            "6. Validar forwarding de MACs/prefijos entre PEs.\n"
        ),
    },
    "evpn.evpn_mac": {
        "hypothesis": (
            "Las MACs del cliente no se aprenden localmente o no se anuncian remotamente porque el bridge-domain/EVI local no está "
            "asociado a la VLAN correcta, las rutas EVPN Tipo 2 son filtradas por políticas de exportación/importación, o el mecanismo "
            "de aprendizaje de MACs está deshabilitado o saturado en el PE/VTEP."
        ),
        "verification_steps": [
            "1. Verificar que el bridge-domain o VLAN local esté mapeado correctamente a la EVI y que la interfaz AC esté Up/Up.",
            "2. Revisar la tabla de MACs locales ('show mac-address-table' / 'show bridge mac-table') para confirmar aprendizaje de la MAC.",
            "3. Confirmar que la MAC de interés aparezca en las rutas EVPN Tipo 2 ('show bgp evpn type-2' / 'show route table evpn.evpn.0').",
            "4. Validar que las políticas de BGP no filtren las rutas Tipo 2 por MAC, VLAN o RT antes de anunciarlas.",
            "5. Inspeccionar si el límite de MACs por bridge-domain está alcanzado, causando descarte de nuevas MACs (MAC limit exceeded).",
        ],
        "expected_evidence": {
            "confirming": [
                "Bridge-domain/VLAN local mapeado correctamente a EVI con interfaz AC en Up/Up.",
                "MAC del cliente presente en la tabla de MACs local con interfaz de ingreso correcta.",
                "Ruta EVPN Tipo 2 presente en la EVPN RIB local con la MAC, IP y next-hop VTEP/PE correctos.",
                "Políticas BGP permiten anuncio y recepción de rutas Tipo 2 sin filtrado por MAC/VLAN/RT.",
                "Sin alarmas de 'MAC limit exceeded' ni contadores de descarte por saturación de tabla MAC.",
            ],
            "invalidating": [
                "Bridge-domain/VLAN no mapeado a EVI correcta (tráfico del cliente no ingresa a la instancia EVPN).",
                "MAC del cliente ausente en la tabla local (falla de aprendizaje L2 o interfaz AC caída).",
                "Ruta EVPN Tipo 2 ausente en EVPN RIB (política de exportación descarta el anuncio de la MAC).",
                "Policy BGP descartando rutas Tipo 2 por community, RT o MAC-specific filter.",
                "Alarma 'MAC limit exceeded' activa (tabla MAC llena, nuevas MACs descartadas silenciosamente).",
            ],
        },
        "scientific_basis": (
            "EVPN Tipo 2 (MAC/IP Advertisement) es fundamental para el aprendizaje distribuido de MACs (RFC 7432). El bridge-domain local "
            "debe estar asociado a la EVI correcta para que las MACs locales sean anunciadas. Las políticas BGP pueden filtrar rutas Tipo 2 "
            "basándose en atributos. El límite de MACs es una protección contra flooding pero puede causar aislamiento de clientes si se "
            "alcanza el umbral (Cisco/Juniper EVPN Configuration Guides)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la interfaz AC está Up, la MAC se aprende. Verifique la tabla MAC local y los contadores del service instance.",
            "Una MAC aprendida localmente NO garantiza que se anuncie por EVPN. Verifique la EVPN RIB para la ruta Tipo 2.",
            "Descarte la hipótesis de límite de MACs solo si ha verificado el conteo actual vs el máximo configurado en el bridge-domain.",
        ],
        "references": [
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "RFC 8365: A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)",
            "Cisco EVPN Configuration Guide",
        ],
        "fix": (
            "1. Mapear bridge-domain/VLAN local correctamente a EVI y asegurar AC Up/Up.\n"
            "2. Verificar aprendizaje de MAC local en tabla de MACs.\n"
            "3. Revisar policies BGP para permitir anuncio/recepción de rutas Tipo 2.\n"
            "4. Ajustar límite de MACs por bridge-domain si se alcanzó el máximo.\n"
            "5. Confirmar ruta EVPN Tipo 2 en EVPN RIB con MAC/IP/next-hop correctos.\n"
            "6. Validar reachability L2 del cliente remoto.\n"
        ),
    },
    "evpn.evpn_ac": {
        "hypothesis": (
            "El Attachment Circuit (AC) local no transporta tráfico del cliente al bridge-domain/EVI porque la interfaz física está "
            "caída, la VLAN configurada en el AC no coincide con la del cliente (dot1q mismatch), o el encapsulado no es compatible con "
            "el bridge-domain (untagged vs tagged)."
        ),
        "verification_steps": [
            "1. Verificar el estado físico/lógico de la interfaz AC ('show interface', 'show ethernet-switching interface').",
            "2. Confirmar que la VLAN/encapsulación configurada en el AC coincida con el tráfico enviado por el cliente (dot1q tag).",
            "3. Revisar que el bridge-domain esté asociado correctamente al AC y que la EVI esté configurada con el RD/RT apropiados.",
            "4. Validar que no existan storm-control o ACLs descartando el tráfico del cliente en el puerto de acceso.",
            "5. Inspeccionar contadores de errores en la interfaz AC (CRC, runts, giants, input/output drops).",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaz AC en estado Up/Up sin errores físicos ni administrativos.",
                "VLAN/encapsulación del AC coincidente con el tráfico del cliente (verificado por captura o configuración CE).",
                "Bridge-domain asociado al AC con EVI configurada y RD/RT correctos.",
                "Sin storm-control ni ACLs descartando tráfico de control o datos del cliente en el puerto AC.",
                "Contadores de la interfaz AC sin incremento de CRC, runts, giants ni drops.",
            ],
            "invalidating": [
                "Interfaz AC en Down/Down o Administratively Down (sin conectividad física).",
                "VLAN mismatch: cliente envía untagged pero AC espera dot1q 100, o viceversa.",
                "Bridge-domain no asociado al AC (tráfico no conmutado hacia la EVI).",
                "Storm-control descartando tráfico broadcast/multicast del cliente (BUM bloqueado en el AC).",
                "Contadores de CRC creciendo en la interfaz AC (cable dañado, dúplex mismatch, o SFP defectuoso).",
            ],
        },
        "scientific_basis": (
            "El Attachment Circuit es el punto de conexión física/lógica entre el cliente y el PE/VTEP en EVPN (RFC 7432). Un mismatch "
            "de VLAN o encapsulado impide que las tramas Ethernet del cliente sean clasificadas en el bridge-domain correcto. Los errores "
            "físicos (CRC, runts) indican problemas de Capa 1 que deben resolverse antes de diagnosticar EVPN (IEEE 802.1Q)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la interfaz está Up, la VLAN es correcta. Capture tráfico del cliente para confirmar los tags.",
            "Un bridge-domain configurado NO garantiza que esté asociado al AC. Verifique 'show bridge-domain' o 'show evpn instance'.",
            "Descarte la hipótesis física solo si ha verificado el estado de carrier, negociación y contadores de errores L1.",
        ],
        "references": [
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "IEEE 802.1Q: Virtual Bridged Local Area Networks",
            "Cisco EVPN Troubleshooting Guide",
        ],
        "fix": (
            "1. Levantar interfaz AC y resolver errores físicos.\n"
            "2. Alinear VLAN/encapsulación del AC con tráfico del cliente.\n"
            "3. Asociar bridge-domain/EVI con RD/RT correctos al AC.\n"
            "4. Eliminar storm-control/ACLs que descarten tráfico del cliente.\n"
            "5. Limpiar contadores de errores (CRC, runts, giants).\n"
            "6. Validar que tráfico del cliente ingrese al bridge-domain.\n"
        ),
    },
    "evpn.evpn_df": {
        "hypothesis": (
            "El DF election en un segmento multihomed EVPN falla o produce un DF incorrecto debido a un ESI duplicado en la red, "
            "una prioridad de DF desajustada entre los PEs multihomed, o un número inconsistente de PEs por Ethernet Segment."
        ),
        "verification_steps": [
            "1. Verificar que el ESI configurado en todos los PEs multihomed del mismo segmento sea idéntico y único en toda la red.",
            "2. Comparar la prioridad de DF (DF preference) configurada en cada PE para confirmar coherencia con el diseño.",
            "3. Revisar el estado del DF election en cada PE ('show evpn instance df-election') para identificar múltiples DFs o ningún DF.",
            "4. Validar que todos los PEs del Ethernet Segment estén activos y alcanzables por el underlay EVPN.",
            "5. Inspeccionar logs de EVPN en busca de mensajes de 'DF election conflict' o 'ESI mismatch'.",
        ],
        "expected_evidence": {
            "confirming": [
                "ESI idéntico en todos los PEs multihomed del segmento y único en todo el dominio EVPN.",
                "Prioridad de DF coherente con diseño (PE activo con prioridad más baja o más alta según vendor).",
                "DF election concluido con un único DF activo por EVI/ESI; sin conflictos.",
                "Todos los PEs del Ethernet Segment alcanzables vía underlay EVPN/BGP.",
                "Sin logs de 'DF election conflict', 'ESI mismatch' ni múltiples DFs detectados.",
            ],
            "invalidating": [
                "ESI duplicado o diferente entre PEs multihomed del mismo segmento (DF election no concluye o es errático).",
                "Prioridad de DF inconsistente (dos PEs con la misma prioridad causan elección no determinística).",
                "Múltiples DFs activos para la misma EVI/ESI (split-brain, loops BUM o duplicación de tráfico).",
                "PE del Ethernet Segment inalcanzable (underlay roto, BGP caído) impidiendo DF election completo.",
                "Logs indicando 'ESI mismatch' o 'DF election conflict' entre PEs del mismo segmento.",
            ],
        },
        "scientific_basis": (
            "El Designated Forwarder (DF) election en EVPN multihomed (RFC 7432, Sección 8.5) evita loops de tráfico BUM. Requiere "
            "que todos los PEs del Ethernet Segment compartan el mismo ESI. La prioridad de DF determina qué PE reenvía BUM. Un "
            "conflicto de ESI o prioridad causa split-brain, loops o duplicación de tramas."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un PE se declara DF, los demás están de acuerdo. Verifique el DF election en TODOS los PEs del segmento.",
            "Un ESI 'similar' NO es suficiente; debe ser idéntico carácter por carácter en todos los PEs multihomed.",
            "Descarte la hipótesis de DF solo si ha verificado la consistencia de ESI y prioridad en TODOS los PEs del segmento.",
        ],
        "references": [
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "RFC 8365: A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)",
            "Cisco EVPN Multihoming Design Guide",
        ],
        "fix": (
            "1. Asegurar ESI idéntico y único en todos los PEs multihomed del segmento.\n"
            "2. Alinear prioridad de DF según diseño.\n"
            "3. Resolver conflictos de DF election ('show evpn instance df-election').\n"
            "4. Restaurar underlay EVPN/BGP para todos los PEs del Ethernet Segment.\n"
            "5. Revisar logs de 'DF election conflict'/'ESI mismatch'.\n"
            "6. Confirmar un único DF activo por EVI/ESI.\n"
        ),
    },
    "evpn.evpn_esi": {
        "hypothesis": (
            "La inconsistencia del ESI (Ethernet Segment Identifier) entre PEs multihomed causa loops de tráfico BUM o un DF election "
            "inestable, resultando en aprendizaje de MACs inestable, duplicación de tramas, o descarte de tráfico cuando un PE cambia "
            "de estado forwarding/no-forwarding."
        ),
        "verification_steps": [
            "1. Verificar que el ESI configurado sea idéntico en todos los PEs conectados al mismo Ethernet Segment del cliente.",
            "2. Confirmar que el ESI sea único en todo el dominio EVPN (no reutilizado en otro segmento multihomed).",
            "3. Revisar el estado de sincronización de MACs entre los PEs multihomed para detectar flapping o duplicación.",
            "4. Validar que las rutas EVPN Tipo 1 (Ethernet Auto-Discovery) contengan el ESI correcto y consistente.",
            "5. Inspeccionar logs de EVPN en busca de 'ESI mismatch', 'DF election failure' o 'MAC move' recurrentes.",
        ],
        "expected_evidence": {
            "confirming": [
                "ESI idéntico en todos los PEs del mismo Ethernet Segment y único en el dominio EVPN.",
                "Sin duplicación de ESI en otros segmentos de la red (verificado en la base de datos EVPN).",
                "Sincronización de MACs estable entre PEs multihomed (sin MAC moves ni flapping).",
                "Rutas EVPN Tipo 1 con ESI consistente en todos los PEs del segmento.",
                "Sin logs de 'ESI mismatch', 'DF election failure' ni 'MAC move' recurrentes.",
            ],
            "invalidating": [
                "ESI diferente entre PEs del mismo Ethernet Segment (DF election falla o es inconsistente).",
                "ESI duplicado en otro segmento de la red (conflicto de rutas Tipo 1 y aprendizaje de MACs errático).",
                "MAC moves recurrentes entre PEs multihomed (indica loop o DF election conflictivo).",
                "Rutas EVPN Tipo 1 con ESI distinto según el PE que las origina (inconsistencia de configuración).",
                "Logs de 'ESI mismatch' o 'MAC move limit exceeded' en los PEs del segmento multihomed.",
            ],
        },
        "scientific_basis": (
            "El ESI identifica un Ethernet Segment multihomed en EVPN (RFC 7432). Debe ser único en todo el dominio y consistente entre "
            "todos los PEs del mismo segmento. Un ESI duplicado o inconsistente causa conflicto en el DF election y en la sincronización de "
            "MACs (Cisco/Juniper EVPN Multihoming documentation). Los MAC moves recurrentes son un síntoma clásico de loop o ESI problem."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el ESI fue generado automáticamente, es correcto. Verifique la consistencia manualmente en todos los PEs.",
            "Un 'MAC move' puede ser normal durante convergencia, pero movimientos recurrentes (>5/min) indican problema de ESI o loop.",
            "Descarte la hipótesis de ESI solo si ha verificado el valor exacto del ESI en TODOS los PEs del segmento multihomed.",
        ],
        "references": [
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "RFC 8365: A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)",
            "Juniper EVPN Multihoming Troubleshooting Guide",
        ],
        "fix": (
            "1. Corregir ESI para que sea idéntico en todos los PEs del mismo Ethernet Segment.\n"
            "2. Asegurar unicidad del ESI en todo el dominio EVPN.\n"
            "3. Estabilizar sincronización de MACs eliminando loops o flapping.\n"
            "4. Verificar rutas EVPN Tipo 1 con ESI consistente.\n"
            "5. Investigar y resolver MAC moves recurrentes.\n"
            "6. Validar DF election estable tras corregir ESI.\n"
        ),
    },
    "evpn.evpn_bum": {
        "hypothesis": (
            "El tráfico BUM (Broadcast, Unknown unicast, Multicast) no se replica correctamente porque el mecanismo de flooding "
            "(ingress replication, multicast core subyacente, o EVPN Tipo 3 Inclusive Multicast Ethernet Tag) no está operativo, o porque "
            "el Designated Forwarder no está reenviando BUM hacia el core EVPN."
        ),
        "verification_steps": [
            "1. Verificar que el mecanismo de replicación BUM esté configurado (ingress replication lista de VTEPs/PEs, o multicast core funcional).",
            "2. Revisar que el DF election haya concluido con un único DF activo para el segmento, capaz de reenviar BUM.",
            "3. Confirmar que las rutas EVPN Tipo 3 (Inclusive Multicast) estén presentes y que el next-hop sea alcanzable.",
            "4. Validar que el core underlay (IP/MPLS) soporte el transporte de tráfico multicast/BUM sin filtrado.",
            "5. Inspeccionar contadores de descarte BUM en el PE/VTEP y en el core para detectar drops silenciosos.",
        ],
        "expected_evidence": {
            "confirming": [
                "Mecanismo de replicación BUM configurado y funcional (ingress replication con lista de PEs/VTEPs poblada).",
                "DF election concluido con un único DF activo que reenvía BUM hacia el core.",
                "Rutas EVPN Tipo 3 presentes con next-hop alcanzable vía underlay.",
                "Core underlay permite transporte de BUM sin ACLs o filtros descartando tráfico multicast/flood.",
                "Sin contadores de descarte BUM creciendo en PE/VTEP ni en routers del core.",
            ],
            "invalidating": [
                "Ingress replication con lista vacía o incompleta de VTEPs/PEs remotos (BUM no replicado).",
                "DF election fallido o múltiples DFs activos (BUM duplicado o no reenviado).",
                "Rutas EVPN Tipo 3 ausentes (falla de anuncio o importación de multicast tag).",
                "Core underlay filtrando tráfico multicast/BUM (ACLs, PIM no habilitado, o RPF check fallido).",
                "Contadores de descarte BUM incrementando en PE/VTEP (buffer insuficiente o policy de flood rate limit).",
            ],
        },
        "scientific_basis": (
            "EVPN utiliza rutas Tipo 3 (Inclusive Multicast Ethernet Tag) para indicar el mecanismo de replicación BUM (RFC 7432). "
            "En escenarios multihomed, solo el DF debe reenviar BUM hacia el core para evitar loops. La ausencia de rutas Tipo 3 o un DF "
            "conflictivo causa falla de replicación BUM (Cisco/Juniper EVPN documentation)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque el unicast funciona, BUM también funciona. Verifique explícitamente el mecanismo de flooding.",
            "Un 'show evpn instance' con DF election NO garantiza que el DF esté reenviando BUM. Verifique contadores de flood.",
            "Descarte la hipótesis de replicación solo si ha verificado la lista de ingress replication y las rutas Tipo 3 en todos los PEs.",
        ],
        "references": [
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "RFC 8365: A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)",
            "Cisco EVPN BUM Replication Design Guide",
        ],
        "fix": (
            "1. Configurar mecanismo de replicación BUM (ingress replication lista completa o multicast core funcional).\n"
            "2. Resolver DF election con un único DF activo.\n"
            "3. Asegurar rutas EVPN Tipo 3 presentes y next-hop alcanzable.\n"
            "4. Permitir transporte de BUM en underlay (sin ACLs/filtros).\n"
            "5. Revisar contadores de descarte BUM y buffers.\n"
            "6. Validar replicación de broadcast/desconocido/multicast entre PEs.\n"
        ),
    },
    "evpn.evpn_rt5": {
        "hypothesis": (
            "El routing inter-subnet en EVPN no funciona porque las rutas EVPN Tipo 5 (IP Prefix) no son generadas o no son importadas "
            "debido a un VRF mismatch, un next-hop inalcanzable en el underlay, o políticas de Route-Target que descartan los prefijos IP "
            "antes de instalarlos en la RIB de la VRF."
        ),
        "verification_steps": [
            "1. Verificar que las rutas EVPN Tipo 5 estén generadas localmente para los prefijos IP del cliente ('show bgp evpn type-5').",
            "2. Confirmar que las rutas Tipo 5 sean recibidas por los PEs remotos y que estén presentes en la EVPN RIB.",
            "3. Validar que el next-hop de las rutas Tipo 5 sea alcanzable vía underlay IGP/MPLS en todos los PEs receptores.",
            "4. Revisar que los Route Targets de las rutas Tipo 5 coincidan con los RT de importación de la VRF en el PE destino.",
            "5. Inspeccionar la RIB de la VRF en el PE destino para confirmar que los prefijos IP se instalan correctamente desde EVPN.",
        ],
        "expected_evidence": {
            "confirming": [
                "Rutas EVPN Tipo 5 generadas localmente para los prefijos IP del cliente con next-hop y label correctos.",
                "Rutas Tipo 5 recibidas en PEs remotos y visibles en la EVPN RIB.",
                "Next-hop de rutas Tipo 5 alcanzable vía underlay IGP/MPLS en todos los PEs receptores.",
                "Route Targets de rutas Tipo 5 coincidentes con RT de importación de la VRF destino.",
                "Prefijos IP instalados correctamente en la RIB de la VRF del PE destino con next-hop EVPN resoluble.",
            ],
            "invalidating": [
                "Rutas EVPN Tipo 5 no generadas localmente (falla de redistribución IP->EVPN o policy de generación).",
                "Rutas Tipo 5 generadas pero no recibidas en PE remoto (falla de anuncio BGP o filtrado de RT).",
                "Next-hop de rutas Tipo 5 inalcanzable (rutas recibidas pero no instalables en forwarding).",
                "RT mismatch para rutas Tipo 5 (prefijos descartados silenciosamente al importar a VRF).",
                "Prefijos IP ausentes en la RIB de la VRF destino a pesar de estar en la EVPN RIB (falla de importación o resolución).",
            ],
        },
        "scientific_basis": (
            "EVPN Tipo 5 (IP Prefix Route) permite el routing inter-subnet entre segmentos EVPN (RFC 7432, RFC 8365). Requiere que los "
            "prefijos IP del cliente sean redistribuidos a EVPN y que los RTs permitan la importación en la VRF destino. El next-hop debe "
            "ser alcanzable para que el data plane funcione. La ausencia de rutas Tipo 5 en la RIB de la VRF es un síntoma de falla de "
            "importación o redistribución."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque EVPN L2 funciona, el routing inter-subnet (Tipo 5) también funciona. Verifique explícitamente las rutas Tipo 5.",
            "Un prefijo IP presente en la EVPN RIB NO garantiza que esté en la RIB de la VRF. Verifique 'show ip route vrf'.",
            "Descarte la hipótesis de Tipo 5 solo si ha verificado la generación, recepción e importación en TODOS los PEs del dominio.",
        ],
        "references": [
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "RFC 8365: A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)",
            "Cisco EVPN Inter-Subnet Routing Design Guide",
        ],
        "fix": (
            "1. Generar rutas EVPN Tipo 5 para prefijos IP del cliente (redistribución IP->EVPN).\n"
            "2. Confirmar recepción de rutas Tipo 5 en PEs remotos.\n"
            "3. Asegurar Next-Hop alcanzable vía underlay IGP/MPLS.\n"
            "4. Alinear RTs de rutas Tipo 5 con importación de VRF destino.\n"
            "5. Verificar instalación de prefijos IP en RIB de VRF destino.\n"
            "6. Validar routing inter-subnet entre segmentos EVPN.\n"
        ),
    },
    "evpn.evpn_rt": {
        "hypothesis": (
            "Las políticas de Route-Target en EVPN descartan silenciosamente rutas Tipo 1/2/3/5 porque el RT de exportación en el origen "
            "no coincide con el RT de importación en el destino, o un route-map aplica un RT inesperado que aísla el segmento EVPN."
        ),
        "verification_steps": [
            "1. Verificar los Route Targets de export e import configurados en cada EVI/MAC-VRF en todos los PEs/VTEPs.",
            "2. Confirmar que los RT de export en el PE origen coincidan exactamente con los RT de import en el PE destino.",
            "3. Revisar las políticas de BGP para detectar route-maps que modifiquen o filtren comunidades extendidas RT.",
            "4. Validar que las rutas EVPN en la EVPN RIB local contengan los RT esperados (verificar atributo communities extendidas).",
            "5. Inspeccionar si existe un RT duplicado o mal formado (typo, AS mal escrito) que cause mismatch de importación.",
        ],
        "expected_evidence": {
            "confirming": [
                "Export-RT e Import-RT idénticos en valor y formato para cada EVI en todos los PEs del segmento.",
                "Sin route-maps modificando o descartando comunidades extendidas RT en BGP EVPN.",
                "Rutas EVPN en la RIB local contienen los RT esperados en el atributo de comunidades extendidas.",
                "Rutas importadas correctamente a la MAC-VRF/VRF destino sin mensajes de 'RT mismatch'.",
                "Sin RT duplicados ni mal formados en la configuración de EVIs.",
            ],
            "invalidating": [
                "Export-RT en origen distinto de Import-RT en destino (rutas recibidas pero descartadas silenciosamente).",
                "Route-map de salida sobrescribiendo RT con valor inesperado (aislamiento de segmento).",
                "Rutas EVPN sin comunidades RT o con RT vacío (falla de configuración de RT en la EVI).",
                "Logs de BGP/EVPN indicando 'RT mismatch' o 'route not imported due to RT filter'.",
                "RT mal formado (ej. typo en AS o valor) que no coincide con ninguna configuración de importación.",
            ],
        },
        "scientific_basis": (
            "Route-Target (RT) es una comunidad extendida BGP que controla la importación/exportación de rutas EVPN (RFC 4364, RFC 7432). "
            "Un mismatch de RT es la causa más común de rutas 'no importadas' en L2VPN/EVPN. Las políticas de BGP pueden modificar RTs, "
            "y un typo en la configuración es suficiente para romper la conectividad del segmento."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque una ruta EVPN está en la RIB, tiene el RT correcto. Verifique el atributo communities extendidas explícitamente.",
            "Un 'show bgp evpn' con rutas presentes NO garantiza que estén importadas a la MAC-VRF. Verifique 'show mac-table' o 'show bridge-domain'.",
            "Descarte la hipótesis de RT solo si ha comparado TODOS los RTs carácter por carácter en la configuración de ambos PEs.",
        ],
        "references": [
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "RFC 8365: A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)",
            "Cisco EVPN Route-Target Design Guide",
        ],
        "fix": (
            "1. Verificar export-RT e import-RT carácter por carácter en cada EVI.\n"
            "2. Asegurar que export origen == import destino.\n"
            "3. Revisar route-maps para no modificar ni descartar comunidades RT.\n"
            "4. Validar atributo communities extendidas en rutas EVPN recibidas.\n"
            "5. Corregir RTs duplicados o mal formados.\n"
            "6. Confirmar importación correcta a MAC-VRF/VRF destino.\n"
        ),
    },
    "evpn.evpn_encap": {
        "hypothesis": (
            "El tráfico del cliente no ingresa correctamente al EVPN porque el encapsulado del Attachment Circuit (dot1q, qinq, untagged) "
            "no coincide con la configuración del bridge-domain o del service instance, causando que las tramas sean descartadas o "
            "clasificadas en un segmento incorrecto."
        ),
        "verification_steps": [
            "1. Verificar el encapsulado configurado en el Attachment Circuit (dot1q, qinq pop/push, untagged) en el PE/VTEP.",
            "2. Confirmar que el tráfico enviado por el cliente coincida con el encapsulado esperado (captura de paquetes en el AC).",
            "3. Revisar que el bridge-domain o service instance clasifique correctamente las tramas según el tag recibido.",
            "4. Validar que el encapsulado del core EVPN (MPLS o VXLAN) sea coherente con el AC y que el VNI/label coincida.",
            "5. Inspeccionar contadores de descarte del AC por 'encapsulation mismatch' o 'unknown tag'.",
        ],
        "expected_evidence": {
            "confirming": [
                "Encapsulado del AC configurado como dot1q/qinq/untagged según el servicio contratado por el cliente.",
                "Captura de tráfico del cliente muestra tags Ethernet coincidentes con la configuración del AC.",
                "Bridge-domain/service instance clasifica las tramas en la EVI correcta según el tag.",
                "Encapsulado del core EVPN (VXLAN/MPLS) coherente con AC y VNI/label coincidente en todos los VTEPs/PEs.",
                "Sin contadores de descarte por 'encapsulation mismatch' ni 'unknown tag' en el AC.",
            ],
            "invalidating": [
                "Encapsulado del AC configurado como dot1q 100 pero cliente envía untagged (tramas descartadas en el AC).",
                "Captura muestra double-tagged (qinq) pero AC espera single-tagged dot1q (clasificación fallida).",
                "Bridge-domain asociado a AC con encapsulado diferente al del service instance (tramas no conmutadas).",
                "Encapsulado del core EVPN inconsistente: un PE usa MPLS y otro VXLAN para la misma EVI.",
                "Contadores de descarte creciendo por 'encapsulation mismatch' o 'unknown VLAN tag' en la interfaz AC.",
            ],
        },
        "scientific_basis": (
            "EVPN soporta múltiples encapsulados en el Attachment Circuit (RFC 7432): dot1q, qinq, untagged. El bridge-domain debe "
            "coincidir con el tag recibido para clasificar las tramas en la EVI correcta. Un mismatch de encapsulado es una causa común "
            "de falla de conectividad L2 en el borde (Cisco/Juniper EVPN AC Configuration Guides)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la interfaz AC está Up, el encapsulado es correcto. Capture tráfico real para confirmar los tags.",
            "Un bridge-domain configurado con 'encapsulation dot1q' NO procesará tráfico untagged. Verifique el modo de la interfaz.",
            "Descarte la hipótesis de encapsulado solo si ha capturado y comparado los tags Ethernet con la configuración del AC.",
        ],
        "references": [
            "RFC 7432: BGP MPLS-Based Ethernet VPN",
            "IEEE 802.1Q: Virtual Bridged Local Area Networks",
            "Cisco EVPN Attachment Circuit Configuration Guide",
        ],
        "fix": (
            "1. Alinear encapsulado del AC (dot1q/qinq/untagged) con tráfico del cliente.\n"
            "2. Verificar que bridge-domain/service instance clasifique según tag recibido.\n"
            "3. Asegurar coherencia de encapsulado del core (VXLAN/MPLS) entre PEs.\n"
            "4. Coincidir VNI/label de EVPN en todos los VTEPs/PEs del segmento.\n"
            "5. Limpiar contadores de 'encapsulation mismatch'/'unknown tag'.\n"
            "6. Validar que tramas del cliente se conmuten correctamente.\n"
        ),
    },
    # ── OSPF ──────────────────────────────────────────────────────────
    "ospf.ospf_neighbor": {
        "hypothesis": (
            "Las adyacencias OSPF no se establecen o caen porque existe un mismatch de área, MTU de interfaz, timers Hello/Dead, "
            "Router-ID duplicado, o la interfaz está marcada como pasiva, impidiendo el intercambio de Hellos y la sincronización de LSDB."
        ),
        "verification_steps": [
            "1. Verificar que las interfaces estén asignadas al área OSPF correcta y no estén en 'passive-interface'.",
            "2. Comparar MTU de interfaz en ambos extremos del enlace (OSPF requiere MTU match para pasar de ExStart a Exchange).",
            "3. Confirmar que los timers Hello/Dead sean idénticos en ambos vecinos (mismatch = no adyacencia).",
            "4. Verificar que el Router-ID sea único en el área (duplicado causa inestabilidad y flaps).",
            "5. Inspeccionar LSDB para confirmar sincronización completa (todos los routers del área deben tener la misma LSDB).",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaces activas en el área correcta; 'passive-interface' solo en interfaces de loopback o sin vecinos.",
                "MTU idéntica en ambos extremos del enlace (ej. 1500 bytes).",
                "Timers Hello/Dead coincidentes (ej. 10/40 en broadcast, 30/120 en NBMA).",
                "Router-ID único en todo el dominio OSPF; sin mensajes de conflicto en logs.",
                "LSDB con el mismo número de entradas en todos los routers del área (sincronización completa).",
            ],
            "invalidating": [
                "Interfaces en área incorrecta o marcadas como passive en enlaces troncal.",
                "MTU mismatch: un extremo tiene 1500 y el otro 9000 (OSPF se congela en ExStart/Exchange).",
                "Timers mismatch: Hello 10s vs Hello 30s (vecino declarado Down por Dead timer expirado).",
                "Router-ID duplicado detectado en logs (causa reconvergencia continua).",
                "LSDB desincronizada: faltan LSAs Tipo 1/Tipo 2 en algunos routers (indica falla de flooding o partición de área).",
            ],
        },
        "scientific_basis": (
            "OSPF (RFC 2328) requiere que dos vecinos acuerden parámetros clave (Hello/Dead intervals, MTU, área, tipo de red) "
            "antes de alcanzar el estado Full. El MTU mismatch es una causa clásica de congelación en ExStart/Exchange porque los DBD packets "
            "son fragmentados o rechazados. Un Router-ID duplicado rompe la unicidad del LSA Tipo 1 (Router LSA), causando reconvergencias "
            "cíclicas (RFC 2328, Sección 13.3)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show ip ospf neighbor' muestra un vecino, la LSDB está sincronizada. Verifique el estado 'Full'.",
            "Una interfaz en 'Up/Up' a nivel físico NO garantiza que OSPF esté habilitada en ella. Verifique 'show ip ospf interface'.",
            "Descarte la hipótesis de MTU solo si ha verificado ambos extremos del enlace (incluyendo subinterfaces lógicas).",
        ],
        "references": [
            "RFC 2328: OSPF Version 2",
            "RFC 5340: OSPF for IPv6 (OSPFv3)",
            "Cisco Live BRKRST-3036: Advanced OSPF Troubleshooting",
        ],
        "fix": (
            "1. Asignar interfaces al área OSPF correcta y quitar passive-interface.\n"
            "2. Igualar MTU en ambos extremos del enlace.\n"
            "3. Sincronizar timers Hello/Dead.\n"
            "4. Corregir Router-ID duplicado.\n"
            "5. Resolver particiones de área para sincronizar LSDB.\n"
            "6. Confirmar adyacencias en estado Full.\n"
        ),
    },
    "ospf.ospf_auth": {
        "hypothesis": (
            "La adyacencia OSPF se congela o cae debido a un mismatch de autenticación (tipo/key), MTU de interfaz desajustada, "
            "o timers Hello/Dead que no coinciden en ambos extremos, impidiendo la transición de vecindad a estado Full."
        ),
        "verification_steps": [
            "1. Verificar el tipo y la clave de autenticación OSPF en ambos extremos (plaintext, MD5, o SHA/HMAC según RFC 5709).",
            "2. Confirmar que la MTU de la interfaz sea idéntica en ambos vecinos (OSPF llena DBD packets a la MTU completa).",
            "3. Comparar los timers Hello/Dead: deben ser iguales para que OSPF declare al vecino como activo.",
            "4. Revisar que el tipo de red (broadcast, P2P, NBMA) coincida en ambos extremos del enlace.",
            "5. Inspeccionar logs de OSPF en busca de mensajes 'Auth mismatch', 'MTU mismatch', o 'Timer mismatch'.",
        ],
        "expected_evidence": {
            "confirming": [
                "Autenticación OSPF con el mismo tipo y clave en ambos vecinos (verificado con 'show ip ospf interface').",
                "MTU idéntica en ambos extremos (ej. 1500 bytes o 9000 bytes de forma consistente).",
                "Timers Hello/Dead coincidentes y dentro de los rangos soportados por la plataforma.",
                "Tipo de red idéntico en ambos extremos (broadcast, P2P, NBMA) sin modificación accidental.",
                "Sin logs de error de autenticación, MTU o timers en ambos routers vecinos.",
            ],
            "invalidating": [
                "Autenticación mismatch: un extremo usa MD5 y el otro plaintext, o la clave MD5 no coincide (adyacencia cae inmediatamente).",
                "MTU mismatch: un extremo acepta DBD de 1500 bytes y el otro espera 4462 (OSPF se congela en ExStart).",
                "Timers desajustados: Hello 1s vs Hello 10s (Dead timer expira y el vecino se declara Down).",
                "Tipo de red desajustado: un extremo en broadcast y el otro en P2P (DR/BDR election conflictiva).",
                "Logs indicando 'OSPF authentication mismatch' o 'OSPF timer mismatch' con timestamps coincidentes con los flaps.",
            ],
        },
        "scientific_basis": (
            "OSPF (RFC 2328, RFC 5709) requiere autenticación coincidente para aceptar Hellos y DBD. Un mismatch de autenticación es "
            "la causa más inmediata de caída de adyacencia: el router descarta todos los paquetes del vecino sin generar errores visibles "
            "en el data plane. La MTU es crítica porque los DBD se rellenan a la MTU para detectar incompatibilidades."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la clave 'parece' igual, es idéntica. Verifique carácter por carácter y el tipo de autenticación.",
            "Un 'show ip ospf neighbor' con estado 'Init' puede deberse a autenticación, no siempre a unidireccionalidad de tráfico.",
            "Descarte la hipótesis de MTU solo si ha verificado el valor exacto en ambos extremos, incluyendo subinterfaces lógicas.",
        ],
        "references": [
            "RFC 2328: OSPF Version 2",
            "RFC 5709: OSPF Support for SHA-HMAC",
            "Cisco Live BRKRST-3036: Advanced OSPF Troubleshooting",
        ],
        "fix": (
            "1. Alinear tipo y clave de autenticación en ambos vecinos.\n"
            "2. Igualar MTU en ambos extremos.\n"
            "3. Sincronizar timers Hello/Dead.\n"
            "4. Coincidir tipo de red (broadcast/P2P/NBMA).\n"
            "5. Revisar logs de 'Auth mismatch'/'MTU mismatch'/'Timer mismatch'.\n"
            "6. Confirmar transición a estado Full.\n"
        ),
    },
    "ospf.ospf_database": {
        "hypothesis": (
            "La LSDB está desincronizada o contiene LSAs corruptos/faltantes, lo que resulta en rutas OSPF no instaladas en la RIB "
            "o en rutas subóptimas debido a una partición de área o un Area Border Router mal configurado."
        ),
        "verification_steps": [
            "1. Comparar el número de LSAs y el checksum de la LSDB en todos los routers del área para detectar inconsistencias.",
            "2. Verificar la presencia de LSAs Tipo 1 (Router), Tipo 2 (Network) y Tipo 3 (Summary) en routers de área backbone y no-backbone.",
            "3. Revisar si existen LSAs con secuencia 0x80000001 que indiquen reinicio o flapping reciente del originador.",
            "4. Validar que los ABRs generen correctamente LSAs Tipo 3/4 entre áreas y que no filtren prefijos por error.",
            "5. Inspeccionar la RIB para confirmar que las rutas OSPF se instalan con el next-hop y métrica esperados.",
        ],
        "expected_evidence": {
            "confirming": [
                "LSDB con el mismo número de entradas y checksum consistente en todos los routers del área.",
                "LSAs Tipo 1/2 presentes en todos los routers del área; Tipo 3/4 generados correctamente por ABRs.",
                "Sin LSAs con secuencia de reinicio (0x80000001) excepto tras reconvergencia planificada.",
                "ABRs generando resúmenes entre áreas sin filtros de prefix-list que bloqueen rutas legítimas.",
                "RIB instalando rutas OSPF con next-hop activo y métrica coherente con el cálculo SPF.",
            ],
            "invalidating": [
                "LSDB con número de entradas diferente entre routers del mismo área (indica flooding incompleto o partición).",
                "Faltan LSAs Tipo 3 en un ABR (rutas inter-área no propagadas, causando blackholing).",
                "LSAs con secuencia 0x80000001 recurrentes (originador de LSA flappeando o reiniciando).",
                "ABR con area-range o filter-list bloqueando prefijos legítimos de áreas no-backbone.",
                "Rutas OSPF presentes en la LSDB pero ausentes en la RIB (indica falla de next-hop o política de route filtering).",
            ],
        },
        "scientific_basis": (
            "La LSDB de OSPF debe ser idéntica en todos los routers dentro del mismo área (RFC 2328). Una discrepancia indica un "
            "fallo de flooding o una partición de red. Los ABRs son responsables de generar LSAs Tipo 3/4 entre áreas; un mal "
            "configurado ABR puede causar aislamiento de áreas. La secuencia de LSA refleja la edad del anuncio; valores de reinicio "
            "indican inestabilidad del originador."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show ip ospf database' muestra entradas, la LSDB está completa. Compare el conteo entre routers.",
            "Un LSA Tipo 3 faltante en un ABR NO siempre es un error; verifique si el área de origen está correctamente configurada.",
            "Descarte la hipótesis de partición solo si ha verificado la conectividad L2/L3 entre TODOS los routers del área.",
        ],
        "references": [
            "RFC 2328: OSPF Version 2",
            "RFC 5340: OSPF for IPv6 (OSPFv3)",
            "Cisco Live BRKRST-3036: Advanced OSPF Troubleshooting",
        ],
        "fix": (
            "1. Comparar LSDB entre routers y resolver inconsistencias.\n"
            "2. Asegurar presencia de LSAs Tipo 1/2/3 según corresponda.\n"
            "3. Investigar LSA sequence 0x80000001 recurrente (estabilizar originador).\n"
            "4. Verificar que ABRs generen resúmenes inter-área sin filtros incorrectos.\n"
            "5. Confirmar instalación de rutas OSPF en RIB.\n"
            "6. Validar sincronización completa de LSDB.\n"
        ),
    },
    "ospf.ospf_area": {
        "hypothesis": (
            "La conectividad entre áreas OSPF falla o la LSDB muestra rutas inesperadas porque un área está mal declarada "
            "(Stub/NSSA/Transit), un virtual-link está roto, o un ABR no genera resúmenes correctos entre áreas backbone y no-backbone."
        ),
        "verification_steps": [
            "1. Verificar que cada interfaz esté asignada al área OSPF correcta (mismatch impide adyacencia y generación de resúmenes).",
            "2. Confirmar que los ABRs tengan al menos una interfaz en el área 0 (backbone) para poder generar LSAs Tipo 3/4.",
            "3. Revisar la configuración de Stub/NSSA/Total Stub para detectar inconsistencias en el tipo de área entre routers del mismo área.",
            "4. Validar que los virtual-links estén operativos y que el área de tránsito tenga conectividad estable.",
            "5. Inspeccionar la RIB para confirmar la presencia/ausencia de rutas externas (Tipo 5/7) según el tipo de área configurado.",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaces asignadas al área correcta; ABRs con conectividad al backbone (área 0).",
                "Áreas Stub/NSSA/Total Stub consistentemente configuradas en todos los routers del área.",
                "Virtual-links (si aplica) en estado Up con adyacencia estable y LSDB sincronizada.",
                "ABRs generando LSAs Tipo 3/4 correctamente sin filtros de área que bloqueen prefijos.",
                "RIB mostrando rutas externas (Tipo 5) en áreas normales y rutas NSSA (Tipo 7) traducciéndose a Tipo 5 en ABRs NSSA.",
            ],
            "invalidating": [
                "Interfaz de un ABR en área incorrecta (sin conexión al backbone, no genera resúmenes inter-área).",
                "Área Stub en algunos routers y Normal en otros (LSA Tipo 5 no propagados, rutas externas faltantes).",
                "Virtual-link roto por área de tránsito particionada (ABR remoto aislado del backbone).",
                "ABR con area-range mal configurado resumiendo prefijos que no deberían ser resumidos.",
                "Rutas externas ausentes en área Normal o presentes en área Stub (indica tipo de área inconsistente).",
            ],
        },
        "scientific_basis": (
            "OSPF requiere que todos los ABRs tengan una interfaz en el área 0 (RFC 2328). Los tipos de área (Stub, NSSA, Total Stub) "
            "deben ser consistentes. Un virtual-link es un túnel lógico sobre un área de tránsito para conectar un área remota al backbone; "
            "si el área de tránsito falla, el virtual-link se rompe. Los resúmenes inter-área (LSA Tipo 3) son generados por ABRs y su "
            "ausencia causa blackholing entre áreas."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un router tiene interfaces en el área 0, es un ABR funcional. Verifique que genera LSAs Tipo 3.",
            "Una área Stub mal configurada en un solo router causa descarte silencioso de LSAs Tipo 5 en ese router.",
            "Descarte la hipótesis de área solo si ha verificado el tipo de área en TODOS los routers del dominio.",
        ],
        "references": [
            "RFC 2328: OSPF Version 2",
            "RFC 3101: The OSPF Not-So-Stubby Area (NSSA) Option",
            "Cisco Live BRKRST-3036: Advanced OSPF Troubleshooting",
        ],
        "fix": (
            "1. Asignar cada interfaz al área correcta.\n"
            "2. Asegurar que ABRs tengan interfaz en área 0.\n"
            "3. Consistir tipo de área (Stub/NSSA/Total Stub) en todos los routers del área.\n"
            "4. Restaurar virtual-links y conectividad del área de tránsito.\n"
            "5. Revisar resúmenes inter-área y filtrado de Tipo 5/7.\n"
            "6. Confirmar rutas entre áreas según diseño.\n"
        ),
    },
    "ospf.ospf_redist": {
        "hypothesis": (
            "Los prefijos externos no se propagan correctamente porque la redistribución está mal configurada (falta de métrica o tipo E1/E2), "
            "o porque los LSA Type 5/7 son filtrados por un ABR o por una área NSSA mal convertida, impidiendo que las rutas externas "
            "lleguen a todos los routers del dominio OSPF."
        ),
        "verification_steps": [
            "1. Verificar que la redistribución hacia OSPF tenga una métrica explícita y el tipo E1/E2 correcto según diseño.",
            "2. Confirmar que los prefijos redistribuidos aparezcan como LSAs Tipo 5 (external) en la LSDB de los routers del área 0.",
            "3. Revisar que los ABRs no filtren LSAs Tipo 5 con distribute-list o prefix-list en la dirección inter-área.",
            "4. Validar que en áreas NSSA, los LSA Tipo 7 sean traduccidos correctamente a Tipo 5 en el ABR NSSA.",
            "5. Inspeccionar la RIB para confirmar que las rutas externas se instalan con el next-hop y métrica esperados.",
        ],
        "expected_evidence": {
            "confirming": [
                "Redistribución configurada con métrica y tipo E1/E2 explícitos según diseño.",
                "Prefijos redistribuidos visibles como LSAs Tipo 5 en la LSDB del área 0 con métrica consistente.",
                "ABRs propagando LSAs Tipo 5 entre áreas sin filtros de prefix-list o distribute-list.",
                "En NSSA: LSAs Tipo 7 presentes en el área NSSA y traducidos a Tipo 5 en el ABR NSSA.",
                "Rutas externas instaladas en la RIB con next-hop alcanzable y métrica coherente (E1 incluye costo interno).",
            ],
            "invalidating": [
                "Redistribución sin métrica explícita (OSPF asigna métrica por defecto 20, posiblemente subóptima o inalcanzable).",
                "Prefijos redistribuidos ausentes en LSDB como LSAs Tipo 5 (falla de redistribución o filtrado local).",
                "ABR con distribute-list bloqueando LSAs Tipo 5 (rutas externas no llegan a áreas no-backbone).",
                "NSSA con LSA Tipo 7 no traducidos a Tipo 5 (ABR NSSA sin 'nssa-only' o sin traducción configurada).",
                "Rutas externas en RIB con métrica infinita o next-hop inalcanzable (redistribución parcialmente fallida).",
            ],
        },
        "scientific_basis": (
            "OSPF (RFC 2328) requiere métrica y tipo (E1/E2) explícitos para rutas redistribuidas. Las rutas E1 incluyen el costo "
            "interno al calcular la métrica total; las E2 usan solo la métrica externa. Un ABR puede filtrar LSAs Tipo 5, y en NSSA, "
            "el ABR debe traducir Tipo 7 a Tipo 5 para que las rutas externas lleguen al resto del dominio (RFC 3101)."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show ip route' muestra una ruta estática, OSPF la redistribuye. Verifique 'show ip ospf database external'.",
            "Un ABR que filtra Tipo 5 puede no mostrar logs. Verifique la LSDB en ambos lados del ABR.",
            "Descarte la hipótesis de redistribución solo si ha verificado la presencia del prefijo en la LSDB como LSA Tipo 5 o 7.",
        ],
        "references": [
            "RFC 2328: OSPF Version 2",
            "RFC 3101: The OSPF Not-So-Stubby Area (NSSA) Option",
            "Cisco Live BRKRST-3036: Advanced OSPF Troubleshooting",
        ],
        "fix": (
            "1. Configurar métrica y tipo E1/E2 explícitos en redistribución.\n"
            "2. Verificar prefijos redistribuidos como LSAs Tipo 5 en área 0.\n"
            "3. Eliminar filtros de ABR que bloqueen LSAs Tipo 5.\n"
            "4. En NSSA, asegurar traducción Tipo 7 a Tipo 5 en ABR NSSA.\n"
            "5. Confirmar instalación de rutas externas en RIB.\n"
            "6. Validar propagación end-to-end de prefijos externos.\n"
        ),
    },
    "ospf.ospf_spf": {
        "hypothesis": (
            "El router experimenta alta CPU o inestabilidad porque el área tiene demasiados routers/prefijos causando SPF frecuentes, "
            "o porque la LSDB ha alcanzado el límite de overflow configurado, descartando nuevos LSAs y provocando agujeros en la topología."
        ),
        "verification_steps": [
            "1. Verificar el uso de CPU y memoria del proceso OSPF durante y fuera de horas pico para detectar picos de procesamiento SPF.",
            "2. Revisar el número de LSAs en la LSDB y compararlo con el límite máximo configurado (overflow database limit).",
            "3. Confirmar que los routers del área no estén generando TCNs (Topology Change Notifications) o LSA updates excesivos.",
            "4. Validar que la red esté diseñada con áreas jerárquicas para limitar el tamaño de la LSDB por área.",
            "5. Inspeccionar logs de OSPF en busca de mensajes 'LSA overflow', 'Database overflow', o 'SPF calculation triggered frequently'.",
        ],
        "expected_evidence": {
            "confirming": [
                "CPU del router estable (<50%) sin picos correlacionados con eventos OSPF.",
                "Número de LSAs en la LSDB por debajo del límite de overflow configurado.",
                "Sin TCNs recurrentes ni routers generando LSA updates más frecuentes que el timer de refresh.",
                "Diseño jerárquico con áreas apropiadamente dimensionadas (<100 routers por área según mejores prácticas).",
                "Sin logs de 'LSA overflow' ni 'Database overflow' en los últimos 30 días.",
            ],
            "invalidating": [
                "CPU >80% con el proceso OSPF como top consumer (SPF frecuente por inestabilidad de topología).",
                "LSDB con número de LSAs cercano o superior al límite de overflow (nuevos LSAs descartados).",
                "TCNs recurrentes (>1 por minuto) que disparan SPF continuamente (posible enlace flappeando o Router-ID duplicado).",
                "Área única (flat design) con >200 routers (LSDB enorme, SPF lenta y consumo de memoria elevado).",
                "Logs de 'LSA overflow' o 'Database overflow' indicando que se han descartado LSAs por límite alcanzado.",
            ],
        },
        "scientific_basis": (
            "OSPF utiliza Dijkstra (SPF) para calcular el shortest path tree cada vez que la LSDB cambia (RFC 2328). El tiempo de cálculo "
            "crece con el número de nodos y aristas. Un área excesivamente grande o un enlace flappeante pueden causar SPF frecuentes, "
            "degradando la CPU. El overflow de LSDB (RFC 2328, Apéndice C) es un mecanismo de protección que descarta LSAs cuando se "
            "alcanza un límite configurado."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la CPU es alta, el problema es OSPF. Correlacione los picos de CPU con eventos de SPF en los logs.",
            "Un 'show ip ospf database' con muchas entradas NO es necesariamente un problema. Verifique el límite de overflow configurado.",
            "Descarte la hipótesis de SPF solo si ha verificado que no hay eventos de topología (TCN, LSA updates) en el intervalo de alta CPU.",
        ],
        "references": [
            "RFC 2328: OSPF Version 2",
            "RFC 5340: OSPF for IPv6 (OSPFv3)",
            "Cisco Live BRKRST-3036: Advanced OSPF Troubleshooting",
        ],
        "fix": (
            "1. Identificar y estabilizar enlaces flappeantes o Router-ID duplicado.\n"
            "2. Reducir tamaño del área (<100 routers) mediante diseño jerárquico.\n"
            "3. Aumentar límite de overflow de LSDB si es necesario.\n"
            "4. Ajustar timers SPF/LSA para reducir carga CPU.\n"
            "5. Investigar TCNs recurrentes y reparar causa raíz.\n"
            "6. Confirmar CPU estable y SPF no frecuente.\n"
        ),
    },
    "ospf.ospf_bfd_gr": {
        "hypothesis": (
            "Las adyacencias OSPF flappean debido a una inestabilidad de BFD que tira la sesión OSPF prematuramente, o a un conflicto "
            "entre Graceful Restart/NSF helper y la convergencia de un vecino lento, causando loops transitorios o blackholing."
        ),
        "verification_steps": [
            "1. Verificar el estado de la sesión BFD asociada a OSPF para confirmar si los flaps de OSPF coinciden con caídas de BFD.",
            "2. Revisar los timers BFD para asegurar que sean compatibles con el hardware y que no sean más agresivos que los de OSPF.",
            "3. Confirmar que Graceful Restart (NSF) esté habilitado correctamente en ambos extremos (helper y restarting router).",
            "4. Validar que el vecino OSPF no esté en estado 'HELPER' perpetuo por falta de reconocimiento de GR capability.",
            "5. Inspeccionar logs de OSPF y BFD en busca de eventos simultáneos que indiquen correlación entre caídas de BFD y flaps OSPF.",
        ],
        "expected_evidence": {
            "confirming": [
                "Sesión BFD estable con timers soportados por el hardware y correlación positiva con OSPF.",
                "BFD no genera caídas falsas por jitter de la red o timers desajustados.",
                "Graceful Restart/NSF configurado consistentemente en ambos extremos (helper y restarting).",
                "Vecino OSPF sale del estado HELPER en el tiempo esperado tras reconvergencia del restarting router.",
                "Sin correlación entre eventos BFD Down y flaps de adyacencia OSPF (indica causas independientes).",
            ],
            "invalidating": [
                "Sesión BFD flappeando por timers desajustados (3.3ms en un extremo, 100ms en el otro), arrastrando OSPF a Down.",
                "BFD cae por micro-flaps de Capa 1/2 que OSPF por sí solo toleraría (Hellos más lentos), causando reconvergencia innecesaria.",
                "NSF helper deshabilitado en el vecino (restarting router pierde todas las adyacencias y reconstruye LSDB desde cero).",
                "Vecino en estado HELPER perpetuo (restarting router nunca completa la sincronización, posible loop transitorio).",
                "Logs muestran BFD session Down inmediatamente seguido de OSPF neighbor Down en múltiples ocasiones.",
            ],
        },
        "scientific_basis": (
            "BFD (RFC 5880) proporciona detección de fallas sub-segundo independiente del protocolo de enrutamiento. Una sesión BFD "
            "inestable puede causar flaps prematuros de OSPF. Graceful Restart (RFC 3623) permite que un router reinicie sin perder "
            "adyacencias, pero requiere que el vecino actúe como helper. Un helper mal configurado o un vecino lento pueden causar "
            "inestabilidad durante el proceso de GR."
        ),
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque BFD está configurado, es la causa de los flaps. Verifique la correlación temporal exacta en los logs.",
            "Una sesión BFD 'Up' NO garantiza que los timers sean estables. Verifique los contadores de paquetes perdidos.",
            "Descarte la hipótesis de GR solo si ha verificado que el vecino no está en HELPER y que NSF está configurado bilateralmente.",
        ],
        "references": [
            "RFC 3623: Graceful OSPF Restart",
            "RFC 5880: Bidirectional Forwarding Detection",
            "Cisco Live BRKRST-3036: Advanced OSPF Troubleshooting",
        ],
        "fix": (
            "1. Ajustar timers BFD a valores estables y soportados.\n"
            "2. Correlacionar flaps OSPF con caídas BFD y resolver causa física.\n"
            "3. Habilitar Graceful Restart/NSF helper bilateralmente.\n"
            "4. Verificar que vecino salga de estado HELPER en tiempo esperado.\n"
            "5. Asegurar compatibilidad de capabilities GR en ambos extremos.\n"
            "6. Confirmar adyacencia OSPF estable tras reconvergencia.\n"
        ),
    },
    # ── ISIS ──────────────────────────────────────────────────────────
    "isis.isis_adj": {
        "hypothesis": (
            "Las adyacencias IS-IS no se forman porque existe un mismatch de tipo de red (P2P vs Broadcast), MTU desajustada, "
            "nivel de área (L1/L2) inconsistente, o NET/System-ID duplicado, impidiendo el intercambio de IIH y la sincronización de LSPs."
        ),
        "verification_steps": [
            "1. Verificar que las interfaces estén configuradas con el mismo tipo de red (P2P o Broadcast) en ambos extremos.",
            "2. Comparar MTU de interfaz: IS-IS llena los IIH a la MTU completa; un mismatch impide la adyacencia.",
            "3. Confirmar que ambos routers compartan el mismo nivel (L1, L2 o L1-L2) y nombre de área para L1.",
            "4. Validar que el NET sea único en el dominio y que el System-ID no esté duplicado.",
            "5. Revisar la LSDB para confirmar sincronización completa y ausencia de LSPs faltantes.",
        ],
        "expected_evidence": {
            "confirming": [
                "Interfaces con el mismo tipo de red (P2P o Broadcast) en ambos extremos.",
                "MTU idéntica en ambos extremos del enlace (ej. 1497 bytes para IS-IS sobre Ethernet).",
                "Nivel de área coincidente (L1/L2) y System-ID único en el dominio.",
                "Adyacencias IS-IS en estado Up con CSNP/PSNP intercambiados correctamente.",
                "LSDB con el mismo número de entradas en todos los routers del área.",
            ],
            "invalidating": [
                "Interfaces con tipo de red desajustado (P2P vs Broadcast) causando rechazo de Hellos.",
                "MTU mismatch: un extremo acepta IIH de 1492 bytes y el otro espera 4462 (wide metrics/TLVs).",
                "Nivel desajustado: un router L1-only intenta formar adyacencia con un L2-only.",
                "System-ID duplicado detectado en logs (causa inestabilidad y flaps de adyacencia).",
                "LSPs faltantes en la LSDB de algunos routers (indica partición de área o flooding bloqueado).",
            ],
        },
        "scientific_basis": "IS-IS opera directamente sobre Capa 2 (CLNS) sin depender de IP para sus Hellos (RFC 1195, ISO 10589). El MTU es crítico porque los IIH se rellenan a la MTU completa para detectar incompatibilidades. Un System-ID duplicado rompe la unicidad de los LSPs y causa reconvergencias cíclicas (ISO 10589, Sección 7.2).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque los vecinos aparecen en 'show isis adjacency', la LSDB está sincronizada. Verifique el estado 'Up'.",
            "Una interfaz en 'Up/Up' a nivel físico NO garantiza que IS-IS esté habilitada en ella. Verifique 'show isis interface'.",
            "Descarte la hipótesis de MTU solo si ha verificado ambos extremos del enlace (incluyendo subinterfaces lógicas y MTU L2).",
        ],
        "references": [
            "RFC 1195: Use of OSI IS-IS for Routing in TCP/IP and Dual Environments",
            "ISO 10589: Intermediate System to Intermediate System Intra-Domain Routing Exchange Protocol",
            "Cisco Live BRKRST-3037: Advanced IS-IS Troubleshooting",
        ],
        "fix": (
            "1. Coincidir tipo de red (P2P/Broadcast) en ambos extremos.\n"
            "2. Igualar MTU en ambos extremos.\n"
            "3. Alinear nivel (L1/L2/L1-L2) y nombre de área para L1.\n"
            "4. Corregir NET/System-ID duplicado.\n"
            "5. Habilitar IS-IS en interfaces de tránsito.\n"
            "6. Confirmar adyacencias Up y LSDB sincronizada.\n"
        ),
    },
    "isis.isis_database": {
        "hypothesis": (
            "La LSDB de IS-IS contiene LSPs faltantes, con secuencia desactualizada, o con información de alcance inconsistente, "
            "resultando en rutas no instaladas en la RIB o forwarding subóptimo en el dominio IS-IS."
        ),
        "verification_steps": [
            "1. Comparar el número de LSPs y el checksum de la LSDB en todos los routers del área para detectar inconsistencias.",
            "2. Verificar la presencia de LSPs de todos los routers del área, incluyendo pseudonodos (para broadcast).",
            "3. Revisar si existen LSPs con secuencia baja o lifetime expirado que indiquen flapping o descarte.",
            "4. Validar que los L1/L2 routers generen correctamente los LSPs de alcance inter-nivel sin filtrar prefijos.",
            "5. Inspeccionar la RIB para confirmar que las rutas IS-IS se instalan con el next-hop y métrica esperados.",
        ],
        "expected_evidence": {
            "confirming": [
                "LSDB con el mismo número de LSPs y checksum consistente en todos los routers del dominio.",
                "LSPs de todos los routers y pseudonodos presentes sin lifetime expirado.",
                "Sin LSPs con secuencia de reinicio recurrente (indica inestabilidad del originador).",
                "L1/L2 routers generando LSPs de alcance inter-nivel correctamente (attached-bit set cuando aplica).",
                "RIB instalando rutas IS-IS con next-hop activo y métrica coherente con el cálculo SPF.",
            ],
            "invalidating": [
                "LSDB con número de LSPs diferente entre routers del mismo área (flooding incompleto o partición).",
                "LSPs faltantes de routers específicos (posible descarte por MTU o policy de flooding).",
                "LSPs con lifetime expirado o secuencia reiniciada recurrentemente (originador inestable).",
                "L1/L2 router sin attached-bit o con attached-bit set incorrectamente (rutas por defecto mal generadas).",
                "Rutas IS-IS presentes en LSDB pero ausentes en RIB (falla de next-hop o conflicto de métrica/policy).",
            ],
        },
        "scientific_basis": "IS-IS utiliza LSPs (Link State PDUs) para distribuir la topología. La LSDB debe ser idéntica en todos los routers del área (ISO 10589). Un LSP faltante indica falla de flooding. El attached-bit indica que un L1/L2 router tiene conectividad a otras áreas; su ausencia puede aislar un área L1. La métrica wide (RFC 5305) permite valores superiores a 63, pero su ausencia trunca la métrica.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show isis database' lista entradas, la LSDB está completa. Compare el conteo entre routers.",
            "Un LSP con lifetime expirado NO significa necesariamente que el router esté caído; verifique si es un problema de clock.",
            "Descarte la hipótesis de flooding solo si ha verificado la conectividad L2 y la capacidad de receptación de IIH/LSP en todos los nodos.",
        ],
        "references": [
            "ISO 10589: Intermediate System to Intermediate System Intra-Domain Routing Exchange Protocol",
            "RFC 5305: IS-IS Extensions for Traffic Engineering",
            "Cisco Live BRKRST-3037: Advanced IS-IS Troubleshooting",
        ],
        "fix": (
            "1. Comparar LSDB entre routers y resolver inconsistencias.\n"
            "2. Asegurar presencia de LSPs de todos los routers/pseudonodos.\n"
            "3. Investigar LSPs con lifetime expirado o secuencia reiniciada.\n"
            "4. Verificar generación correcta de LSPs inter-nivel en L1/L2.\n"
            "5. Confirmar instalación de rutas IS-IS en RIB.\n"
            "6. Validar flooding completo sin particiones.\n"
        ),
    },
    "isis.isis_metric": {
        "hypothesis": (
            "El forwarding IS-IS es subóptimo o los routers no utilizan las métricas esperadas porque wide-metrics no está habilitado, "
            "el bit de overload está seteado inadvertidamente, o el attached-bit está generando rutas por defecto no deseadas en L1."
        ),
        "verification_steps": [
            "1. Verificar que wide-metrics esté habilitado globalmente y en interfaces para soportar métricas superiores a 63 y TE extensions.",
            "2. Confirmar que el bit de overload no esté seteado de forma persistente en routers que deberían forwardar tráfico de tránsito.",
            "3. Revisar el attached-bit en L1/L2 routers para validar que genere rutas por defecto solo cuando haya conectividad inter-área.",
            "4. Comparar la métrica de las rutas en la RIB con los valores configurados en las interfaces para detectar truncamiento.",
            "5. Inspeccionar la tabla de forwarding para confirmar que el path seleccionado coincide con la métrica menor esperada.",
        ],
        "expected_evidence": {
            "confirming": [
                "Wide-metrics habilitado globalmente y en interfaces (soporta TE y métricas >63).",
                "Bit de overload limpio en routers de tránsito (solo seteado temporalmente durante mantenimiento).",
                "Attached-bit seteado correctamente en L1/L2 routers con conectividad real a otras áreas.",
                "Métricas de rutas en RIB coinciden con la suma de métricas de interfaces sin truncamiento.",
                "Forwarding path seleccionado es el de menor métrica total según el cálculo SPF.",
            ],
            "invalidating": [
                "Wide-metrics deshabilitado (métricas truncadas a 6 bits; rutas subóptimas o inalcanzables con métrica >63).",
                "Overload bit seteado permanentemente (router anuncia capacidad cero, tráfico de tránsito evitado).",
                "Attached-bit seteado en L1/L2 router sin conectividad inter-área (genera ruta por defecto hacia un blackhole).",
                "Métrica en RIB inconsistente con la suma de interfaces (indica truncamiento o uso de métrica por defecto).",
                "Forwarding path no coincide con el menor costo SPF (posible política de route leaking o filtrado inter-área).",
            ],
        },
        "scientific_basis": "IS-IS utiliza métricas de 6 bits por defecto (valores 0-63), insuficientes para redes modernas. Wide-metrics (RFC 5305) extiende a 32 bits. El overload-bit indica que el router no debe usarse para tránsito (ISO 10589). El attached-bit en L1/L2 routers genera una ruta por defecto en áreas L1, pero si está seteado incorrectamente, causa blackholing.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la métrica está configurada como 100, se usa como 100. Verifique si wide-metrics está habilitado.",
            "Un router con overload-bit seteado puede parecer funcional localmente pero rechazar tráfico de tránsito sin generar logs.",
            "Descarte la hipótesis de attached-bit solo si ha verificado que el L1/L2 router tiene rutas activas hacia otras áreas.",
        ],
        "references": [
            "ISO 10589: Intermediate System to Intermediate System Intra-Domain Routing Exchange Protocol",
            "RFC 5305: IS-IS Extensions for Traffic Engineering",
            "Cisco Live BRKRST-3037: Advanced IS-IS Troubleshooting",
        ],
        "fix": (
            "1. Habilitar wide-metrics globalmente y en interfaces.\n"
            "2. Limpiar overload-bit en routers de tránsito.\n"
            "3. Verificar attached-bit seteado solo con conectividad inter-área real.\n"
            "4. Ajustar métricas de interfaces según diseño.\n"
            "5. Confirmar path de forwarding de menor costo SPF.\n"
            "6. Validar que métricas no se truncuen.\n"
        ),
    },
    # ── MULTICAST ─────────────────────────────────────────────────────
    "multicast.mcast_igmp": {
        "hypothesis": (
            "Los hosts no reciben tráfico multicast porque IGMP no está habilitado en la interfaz de acceso, el host no envía IGMP Joins, "
            "o el switch/router de última milla no tiene el grupo en su tabla IGMP snooping/mroute, impidiendo la construcción de la OIL."
        ),
        "verification_steps": [
            "1. Verificar que IGMP esté habilitado en la interfaz de acceso hacia los hosts receptores.",
            "2. Confirmar que el host envíe IGMP Joins (Membership Reports) para el grupo de interés (captura tcpdump/wireshark).",
            "3. Revisar la tabla IGMP snooping en el switch L2 para confirmar que el puerto del host está asociado al grupo multicast.",
            "4. Validar que el router L3 tenga una entrada (*,G) o (S,G) con la interfaz de acceso en la lista OIL.",
            "5. Inspeccionar si existen ACLs o storm-control descartando IGMP Reports en la interfaz de acceso.",
        ],
        "expected_evidence": {
            "confirming": [
                "IGMP habilitado en interfaz de acceso con receptores presentes.",
                "Host genera IGMP Join (v2/v3) para el grupo de interés confirmado por captura de paquetes.",
                "Tabla IGMP snooping muestra el puerto del host asociado al grupo multicast deseado.",
                "Router L3 con entrada (*,G) activa y OIL incluyendo la interfaz de acceso hacia los hosts.",
                "Sin ACLs ni storm-control descartando IGMP Reports en la interfaz de acceso.",
            ],
            "invalidating": [
                "IGMP deshabilitado en interfaz de acceso (router no procesa Membership Reports).",
                "Host no envía IGMP Join (aplicación multicast no iniciada o firewall host bloqueando IGMP).",
                "IGMP snooping tabla vacía para el grupo (switch no aprende la membresía, BUM no replicado al puerto).",
                "Router L3 sin entrada (*,G) o con OIL vacía (sin receptores reportados, tráfico no reenviado a la interfaz).",
                "ACL o storm-control descartando IGMP Reports en la interfaz de acceso (membresía no registrada).",
            ],
        },
        "scientific_basis": "IGMP (RFC 3376) gestiona la membresía de grupos multicast en la última milla. Sin IGMP Joins, la OIL (Outgoing Interface List) permanece vacía y el tráfico no se reenvía a los hosts. IGMP snooping en switches L2 optimiza la replicación evitando flooding innecesario, pero si no está habilitado o si la tabla snooping está vacía, el host no recibe el tráfico.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque la aplicación multicast está abierta en el host, el Join se envía. Verifique con tcpdump en el host.",
            "Una tabla IGMP snooping vacía puede deberse a que snooping está deshabilitado, no a ausencia de hosts.",
            "Descarte la hipótesis de IGMP solo si ha capturado un IGMP Join explícito y verificado su llegada al router L3.",
        ],
        "references": [
            "RFC 3376: Internet Group Management Protocol, Version 3",
            "Cisco Multicast Configuration Guide",
            "Cisco Live BRKRST-3325: Advanced Multicast Troubleshooting",
        ],
        "fix": (
            "1. Habilitar IGMP en interfaz de acceso hacia receptores.\n"
            "2. Verificar que hosts envíen IGMP Joins para el grupo.\n"
            "3. Activar/configurar IGMP snooping en switch L2 y asociar puerto del host al grupo.\n"
            "4. Completar entrada (*,G) en router L3 con interfaz de acceso en OIL.\n"
            "5. Eliminar ACLs/storm-control que descarten IGMP Reports.\n"
            "6. Confirmar que los hosts reciban tráfico multicast.\n"
        ),
    },
    "multicast.mcast_pim": {
        "hypothesis": (
            "El árbol multicast no se construye porque las adyacencias PIM no se forman (Hellos bloqueados, DR election conflictivo), "
            "o porque el RPF check falla por una ruta unicast incorrecta hacia la fuente del tráfico multicast."
        ),
        "verification_steps": [
            "1. Verificar que PIM Sparse-Mode (o Dense-Mode según diseño) esté habilitado en todas las interfaces de tránsito del dominio.",
            "2. Revisar las adyacencias PIM ('show ip pim neighbor') para confirmar vecinos visibles en estado Up.",
            "3. Validar el DR election en segmentos multiacceso (el DR es responsable de enviar Joins hacia el RP).",
            "4. Confirmar que el RPF check ('show ip rpf <source>') devuelva la interfaz correcta hacia la fuente multicast.",
            "5. Inspeccionar si existen ACLs o filtros descartando paquetes PIM (IP 103) o IGMP Joins/Prunes en el dominio.",
        ],
        "expected_evidence": {
            "confirming": [
                "PIM Sparse-Mode habilitado en todas las interfaces de tránsito y de acceso del dominio multicast.",
                "PIM neighbors en estado Up en todas las interfaces de tránsito del árbol multicast.",
                "DR election concluido con un único DR activo por segmento multiacceso.",
                "RPF check exitoso: interfaz de ingreso del tráfico multicast coincide con la ruta IGP hacia la fuente.",
                "Sin ACLs ni filtros descartando PIM Hellos, Joins o Prunes en el dominio.",
            ],
            "invalidating": [
                "PIM no habilitado en interfaz de tránsito (vecinos PIM no descubiertos, árbol no construido).",
                "PIM neighbors Down por Hellos bloqueados o timers desajustados (Holdtime expira).",
                "DR election conflictivo o ausente (segmento multiacceso sin DR activo, Joins no enviados hacia RP).",
                "RPF check fallido: tráfico multicast ingresa por interfaz distinta a la ruta IGP hacia la fuente (descarte silencioso).",
                "ACL bloqueando PIM (IP 103) o IGMP en interfaces del path multicast.",
            ],
        },
        "scientific_basis": "PIM-SM (RFC 4601) requiere adyacencias PIM funcionales para construir el árbol de distribución multicast. El DR election es crítico en segmentos multiacceso para evitar duplicación de Joins. El RPF check es una verificación estricta: si el tráfico multicast ingresa por una interfaz distinta a la ruta unicast hacia la fuente, se descarta (RFC 4601, Sección 4.6).",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un router tiene PIM habilitado, el vecino PIM está activo. Verifique 'show ip pim neighbor'.",
            "Un RPF check exitoso en un router NO garantiza que todos los routers del árbol tengan RPF correcto. Verifique cada salto.",
            "Descarte la hipótesis de PIM solo si ha verificado las adyacencias y el RPF en TODOS los routers del path multicast.",
        ],
        "references": [
            "RFC 4601: Protocol Independent Multicast - Sparse Mode (PIM-SM)",
            "RFC 3376: Internet Group Management Protocol, Version 3",
            "Cisco Live BRKRST-3325: Advanced Multicast Troubleshooting",
        ],
        "fix": (
            "1. Habilitar PIM Sparse-Mode en interfaces de tránsito y acceso.\n"
            "2. Establecer adyacencias PIM Up entre vecinos.\n"
            "3. Resolver DR election con un único DR por segmento multiacceso.\n"
            "4. Corregir RPF check para que coincida con ruta unicast hacia fuente.\n"
            "5. Eliminar ACLs que bloqueen PIM (IP 103) o IGMP Joins/Prunes.\n"
            "6. Confirmar construcción del árbol multicast.\n"
        ),
    },
    "multicast.mcast_rp": {
        "hypothesis": (
            "El RP no es alcanzable o está inconsistentemente configurado (RP estático vs Auto-RP/BSR), causando que los routers PIM "
            "no puedan establecer el (*,G) shared tree ni el source tree (S,G), resultando en ausencia de tráfico multicast en los receptores."
        ),
        "verification_steps": [
            "1. Verificar que el RP esté alcanzable por todos los routers del dominio PIM-SM (ping/traceroute a la IP del RP).",
            "2. Confirmar que la elección de RP sea consistente en todos los routers (estático, Auto-RP o BSR).",
            "3. Revisar que el RP tenga rutas hacia las fuentes multicast (tráfico de fuentes llega al RP para construir el shared tree).",
            "4. Validar que las interfaces del RP tengan PIM habilitado y que el RP acepte registros PIM de los DRs de fuente.",
            "5. Inspeccionar la tabla de grupos multicast en el RP para confirmar presencia de estados (*,G) y (S,G) activos.",
        ],
        "expected_evidence": {
            "confirming": [
                "RP alcanzable desde todos los routers PIM-SM vía unicast.",
                "RP consistente en todos los routers (misma IP y modo de descubrimiento: estático, Auto-RP o BSR).",
                "RP con rutas activas hacia las fuentes multicast y PIM habilitado en interfaces de tránsito.",
                "RP recibiendo y procesando PIM Register messages de los DRs de fuente.",
                "RP con estados (*,G) y (S,G) activos para los grupos de interés.",
            ],
            "invalidating": [
                "RP inalcanzable desde algunos routers (ruta unicast faltante o ACL bloqueando tráfico hacia RP).",
                "RP inconsistente: algunos routers usan RP distinto (shared tree fragmentado, receptores aislados).",
                "RP sin rutas hacia las fuentes (tráfico de fuentes no llega al RP, shared tree incompleto).",
                "RP con PIM deshabilitado en interfaces (no procesa Registers ni construye el árbol).",
                "RP sin estados (*,G) o (S,G) (no hay registros activos, posible falla de conectividad fuente->RP).",
            ],
        },
        "scientific_basis": "PIM-SM (RFC 4601) requiere un RP funcional para el shared tree (*,G). El RP debe ser alcanzable por todos los routers y tener conectividad a las fuentes. En Auto-RP (RFC 3446) y BSR (RFC 5059), el mecanismo de descubrimiento debe ser consistente. Un RP inconsistente causa árboles fragmentados y falla de entrega multicast.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque un router tiene RP configurado, todos los demás lo usan. Verifique 'show ip pim rp mapping'.",
            "Un RP alcanzable por ping NO garantiza que PIM Register lleguen. Verifique contadores de registers en el RP.",
            "Descarte la hipótesis de RP solo si ha verificado la consistencia del RP y el estado (*,G)/(S,G) en TODOS los routers del dominio.",
        ],
        "references": [
            "RFC 4601: Protocol Independent Multicast - Sparse Mode (PIM-SM)",
            "RFC 3446: Anycast-RP Protocol Independent Multicast",
            "Cisco Live BRKRST-3325: Advanced Multicast Troubleshooting",
        ],
        "fix": (
            "1. Restaurar alcanzabilidad unicast del RP desde todos los routers.\n"
            "2. Configurar RP consistente (estático, Auto-RP o BSR) en todos los routers.\n"
            "3. Asegurar que RP tenga rutas hacia fuentes multicast.\n"
            "4. Habilitar PIM en interfaces del RP y procesar Registers.\n"
            "5. Verificar estados (*,G) y (S,G) activos en RP.\n"
            "6. Confirmar que receptores reciban tráfico del shared tree.\n"
        ),
    },
    "multicast.mcast_msdp": {
        "hypothesis": (
            "La interconexión multicast entre dominios PIM falla porque las sesiones MSDP entre RPs no están establecidas, "
            "o los SA (Source-Active) messages son filtrados por políticas de peer, impidiendo que los RPs remotos conozcan las fuentes activas."
        ),
        "verification_steps": [
            "1. Verificar que las sesiones TCP MSDP entre RPs de diferentes dominios estén en estado Established.",
            "2. Confirmar que los SA messages sean generados por el RP que tiene la fuente activa y reenviados a los peers MSDP.",
            "3. Revisar políticas de MSDP (sa-filters, peer-filters) que puedan descartar SA messages legítimos.",
            "4. Validar que el RPF check de MSDP (hacia el originador del SA) sea exitoso para evitar descarte de SA spoofeados.",
            "5. Inspeccionar la caché de SA en los RPs remotos para confirmar que contienen las fuentes activas del dominio origen.",
        ],
        "expected_evidence": {
            "confirming": [
                "Sesiones MSDP en estado Established entre RPs de dominios diferentes.",
                "SA messages generados localmente y reenviados a todos los peers MSDP sin filtrado.",
                "Políticas MSDP permiten explícitamente los grupos/fuentes de interés (sin sa-filter deny).",
                "RPF check MSDP exitoso hacia el originador del SA (prevención de spoofing).",
                "Caché de SA en RP remoto contiene las fuentes activas del dominio origen con next-hop resoluble.",
            ],
            "invalidating": [
                "Sesiones MSDP en estado Down o Idle (TCP 639 bloqueado o peer inalcanzable).",
                "SA messages no generados (RP origen sin fuente activa o política local descarta el SA).",
                "SA-filter descartando mensajes SA para el grupo o fuente de interés (peer remoto no aprende la fuente).",
                "RPF check MSDP fallido (SA descartado como spoofeado por ruta inalcanzable al originador).",
                "Caché de SA vacía en RP remoto (no hay conocimiento de fuentes externas, shared tree inter-dominio incompleto).",
            ],
        },
        "scientific_basis": "MSDP (RFC 3618) permite la interconexión de dominios PIM-SM mediante el intercambio de SA messages entre RPs. Un SA message anuncia una fuente activa; sin MSDP, los RPs remotos no conocen las fuentes fuera de su dominio. Las políticas de filtrado de SA y el RPF check son mecanismos de seguridad que, si mal configurados, bloquean legítimamente el tráfico inter-dominio.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque MSDP está configurado, los SA messages fluyen. Verifique la caché de SA en ambos extremos.",
            "Un 'show ip msdp summary' con peers Up NO garantiza que SA messages estén siendo intercambiados. Verifique contadores de SA.",
            "Descarte la hipótesis de MSDP solo si ha verificado la sesión TCP, el RPF check y la presencia de fuentes en la caché de SA.",
        ],
        "references": [
            "RFC 3618: Multicast Source Discovery Protocol (MSDP)",
            "RFC 4601: Protocol Independent Multicast - Sparse Mode (PIM-SM)",
            "Cisco Live BRKRST-3325: Advanced Multicast Troubleshooting",
        ],
        "fix": (
            "1. Establecer sesiones TCP MSDP (puerto 639) Established entre RPs.\n"
            "2. Asegurar generación y reenvío de SA messages desde RP origen.\n"
            "3. Revisar sa-filters/peer-filters para permitir grupos/fuentes.\n"
            "4. Corregir RPF check MSDP hacia originador del SA.\n"
            "5. Verificar caché de SA en RPs remotos.\n"
            "6. Confirmar interconexión multicast entre dominios.\n"
        ),
    },
    "multicast.mcast_fwd": {
        "hypothesis": (
            "El tráfico multicast no se reenvía correctamente porque la SPT no se ha establecido (RPF failure, PIM Joins bloqueados), "
            "o porque el rendimiento del data plane es insuficiente (MFIB sin recursos, OIL vacía, o descartes por congestión en el core)."
        ),
        "verification_steps": [
            "1. Verificar que el árbol SPT (Shortest Path Tree) esté construido hacia la fuente con 'show ip mroute' / 'show multicast routing'.",
            "2. Confirmar que el RPF check sea exitoso en cada router del path SPT hacia la fuente.",
            "3. Revisar la OIL (Outgoing Interface List) para confirmar que las interfaces de salida hacia los receptores estén presentes.",
            "4. Validar que la MFIB/FIB multicast tenga entradas activas para (S,G) con contadores de reenvío incrementando.",
            "5. Inspeccionar contadores de descarte multicast por falta de recursos (buffer, CPU) o políticas de rate-limit.",
        ],
        "expected_evidence": {
            "confirming": [
                "Árbol SPT construido con entradas (S,G) activas en todos los routers del path desde la fuente hasta los receptores.",
                "RPF check exitoso en cada salto del SPT (interfaz de ingreso coincide con ruta unicast hacia la fuente).",
                "OIL poblada con las interfaces de salida hacia los segmentos con receptores activos.",
                "MFIB/FIB multicast muestra entradas (S,G) con contadores de paquetes reenviados incrementando.",
                "Sin descartes multicast por falta de recursos, buffer congestion ni rate-limiting en routers del path.",
            ],
            "invalidating": [
                "Árbol SPT incompleto: falta entrada (S,G) en algún router del path (PIM Join no llegó o fue descartado).",
                "RPF check fallido en router intermedio (tráfico multicast descartado silenciosamente en ese salto).",
                "OIL vacía para el grupo (sin receptores registrados o IGMP Joins no procesados).",
                "MFIB/FIB sin entrada (S,G) o con contadores estáticos (no hay reenvío de data plane).",
                "Descartes multicast creciendo por buffer congestion, CPU alta, o rate-limit aplicado a tráfico multicast.",
            ],
        },
        "scientific_basis": "El forwarding multicast depende del SPT (Shortest Path Tree) o del shared tree (*,G) para reenviar tráfico. El RPF check es obligatorio en cada salto (RFC 4601). La OIL determina hacia qué interfaces se replica el tráfico. Sin entradas en la MFIB/FIB, el data plane no puede reenviar los paquetes multicast, aunque el control plane (PIM) esté funcional.",
        "confidence_level": "Alta",
        "bias_warnings": [
            "NO asuma que porque 'show ip mroute' muestra una entrada, el data plane está reenviando. Verifique los contadores de la MFIB.",
            "Un SPT completo en el RP NO garantiza que el SPT hacia los receptores esté construido. Verifique el último salto (LHR).",
            "Descarte la hipótesis de forwarding solo si ha verificado los contadores de paquetes reenviados en TODOS los routers del path.",
        ],
        "references": [
            "RFC 4601: Protocol Independent Multicast - Sparse Mode (PIM-SM)",
            "RFC 3376: Internet Group Management Protocol, Version 3",
            "Cisco Live BRKRST-3325: Advanced Multicast Troubleshooting",
        ],
        "fix": (
            "1. Construir/completar árbol SPT con entradas (S,G) en todos los routers.\n"
            "2. Corregir RPF check en cada salto del SPT.\n"
            "3. Poblar OIL con interfaces hacia receptores activos.\n"
            "4. Verificar entradas activas en MFIB/FIB multicast con contadores incrementando.\n"
            "5. Eliminar descartes por falta de recursos, buffer o rate-limit.\n"
            "6. Confirmar reenvío de tráfico multicast a receptores.\n"
        ),
    },

}