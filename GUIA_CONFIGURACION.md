# Guía de Configuración — Network Tshoot Dashboard

Este documento explica **cómo configurar cada item** del dashboard de troubleshooting: tecnologías, vendors, pasos (steps), comandos por nivel (tier), navegación entre pasos, y personalización de la interfaz.

> **Ubicación del código fuente de verdad:** `data/knowledge_base.py`  
> **No ejecuta comandos en equipos reales:** es una herramienta de guía diagnóstica interactiva.

---

## Tabla de Contenidos

1. [Arquitectura y archivos clave](#1-arquitectura-y-archivos-clave)
2. [Cómo agregar una nueva tecnología](#2-cómo-agregar-una-nueva-tecnología)
3. [Cómo configurar vendors](#3-cómo-configurar-vendors)
4. [Cómo configurar steps (pasos)](#4-cómo-configurar-steps-pasos)
5. [Cómo configurar comandos por tier](#5-cómo-configurar-comandos-por-tier)
6. [Cómo configurar choices (navegación)](#6-cómo-configurar-choices-navegación)
7. [Cómo personalizar la UI (display)](#7-cómo-personalizar-la-ui-display)
8. [Configuración de VS Code](#8-configuración-de-vs-code)
9. [Ejemplo completo: agregar una nueva tecnología](#9-ejemplo-completo-agregar-una-nueva-tecnología)
10. [Validación y pruebas](#10-validación-y-pruebas)

---

## 1. Arquitectura y archivos clave

```
net_tshoot_dashboard/
├── main.py              # Punto de entrada; inicia el Engine
├── requirements.txt     # Dependencias (rich>=13.0.0 opcional)
├── AGENTS.md            # Contexto para agentes de IA
├── core/
│   └── engine.py        # Máquina de estados: menús, navegación, tiers
├── data/
│   └── knowledge_base.py # FUENTE DE VERDAD: KB dict con toda la config
└── utils/
    └── display.py       # Capa de UI terminal (rich o fallback)
```

**Regla de oro:** casi toda la configuración del contenido se hace en `data/knowledge_base.py`. No es necesario tocar `engine.py` salvo que quieras cambiar la lógica de navegación.

---

## 2. Cómo agregar una nueva tecnología

En `data/knowledge_base.py`, el diccionario `_kb()` retorna un dict donde **cada clave de nivel superior es una tecnología**.

### Estructura mínima de una tecnología

```python
'mi_tecnologia': {
    'name': 'Nombre visible en el menú',
    'description': 'Breve descripción para el usuario.',
    'vendors': ['juniper', 'cisco_iosxr', 'cisco_iosxe'],
    'steps': {
        'mi_tecnologia_start': {
            'title': '1. Título del paso inicial',
            'tier': 1,
            'body': 'Texto explicativo. Puede usar markdown básico (**negrita**, saltos de línea).',
            'commands': {
                'juniper': ['show version'],
                'cisco_iosxr': ['show version'],
            },
            'expected': 'Qué debería mostrar el comando.',
            'choices': [
                {'label': 'Ir a detalle A', 'next': 'mi_tecnologia_a'},
                {'label': 'Ir a detalle B', 'next': 'mi_tecnologia_b'},
            ]
        },
        'mi_tecnologia_a': {
            'title': '2. Detalle A',
            'tier': 2,
            'body': '...',
            'commands': {...},
            'expected': '...',
            'choices': [
                {'label': 'Volver al inicio', 'next': 'mi_tecnologia_start'},
            ]
        },
    }
}
```

### Reglas importantes

- La clave de la tecnología (ej. `'mpls'`) debe coincidir con el prefijo de los steps (ej. `'mpls_start'`).
- Debe existir **al menos un step cuya clave termine en `_start`**. El motor busca automáticamente una clave que termine en `_start` para comenzar el flujo.
- Las claves de los steps deben ser **únicas dentro de la tecnología**.
- El campo `vendors` controla qué vendors aparecerán en el submenú de selección de vendor para esa tecnología.

---

## 3. Cómo configurar vendors

Los vendors se definen en el diccionario `VendorMap` al inicio de `knowledge_base.py`:

```python
VendorMap = {
    "juniper": "Juniper JunOS",
    "cisco_iosxr": "Cisco IOS-XR",
    "cisco_iosxe": "Cisco IOS-XE / NX-OS",
    "mikrotik": "MikroTik RouterOS v7",
    "fortinet": "Fortinet FortiOS",
}
```

### Agregar un nuevo vendor

1. **Agregar la entrada en `VendorMap`**:
   ```python
   "arista": "Arista EOS",
   ```

2. **Incluirlo en la lista `vendors` de las tecnologías** que lo soporten:
   ```python
   'vendors': ['juniper', 'arista'],
   ```

3. **Agregar sus comandos en cada step** dentro del bloque `'commands'`:
   ```python
   'commands': {
       'juniper': ['show version'],
       'arista': ['show version'],
   }
   ```

> **Nota:** Si un vendor no tiene comandos definidos en un step, el dashboard mostrará *(Sin comandos específicos para este vendor)*.

---

## 4. Cómo configurar steps (pasos)

Cada step es un diccionario con los siguientes campos:

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `title` | `str` | Sí | Título visible del paso. |
| `tier` | `int` (1–4) | Sí | Nivel mínimo requerido para ver este paso. |
| `body` | `str` | Sí | Texto explicativo. Usa `\n` para saltos de línea y `**texto**` para negrita. |
| `commands` | `dict` | No | Diccionario por vendor. Ver sección 5. |
| `expected` | `str` | No | Resultado esperado o qué buscar en la salida. |
| `choices` | `list` | No | Opciones de navegación. Ver sección 6. |

### Jerarquía de tiers

```
tier=1  →  Tier 1 — Operador NOC
tier=2  →  Tier 2 — Ingeniero de Soporte
tier=3  →  Tier 3 — Ingeniero de Escalación
tier=4  →  Arquitecto de Red
```

**Comportamiento del motor:** si el usuario selecciona un tier menor al requerido por un step, el motor intentará **saltar automáticamente** a la primera choice cuyo destino sea visible para ese tier. Si no encuentra ruta, muestra una alerta y vuelve atrás.

---

## 5. Cómo configurar comandos por tier

Dentro de cada step, el campo `commands` es un diccionario cuyas claves son los **vendor keys** definidos en `VendorMap`.

### Formato 1: Lista simple (retrocompatible, siempre visible)

```python
'commands': {
    'juniper': ['show mpls interface', 'show ldp neighbor'],
}
```

Los comandos de lista se muestran **sin importar el tier seleccionado**.

### Formato 2: Diccionario por tier (acumulativo)

```python
'commands': {
    'juniper': {
        'tier1': ['show mpls interface', 'show ldp neighbor'],
        'tier2': ['show rsvp neighbor', 'show mpls lsp'],
        'tier3': ['show ldp database', 'show mpls label usage'],
        'arch': ['show configuration protocols mpls | display set'],
    },
}
```

**Reglas de acumulación:**

| Tier seleccionado | Comandos mostrados |
|-------------------|-------------------|
| Tier 1 | `tier1` |
| Tier 2 | `tier1` + `tier2` |
| Tier 3 | `tier1` + `tier2` + `tier3` |
| Arquitecto (Tier 4) | `tier1` + `tier2` + `tier3` + `arch` |

> **Puedes mezclar formatos:** un vendor puede usar lista y otro dict en el mismo step.

---

## 6. Cómo configurar choices (navegación)

Las choices definen los **botones de navegación** al final de cada paso.

```python
'choices': [
    {'label': 'Vecinos DOWN', 'next': 'mpls_ctrl_down'},
    {'label': 'Vecinos UP pero sin labels', 'next': 'mpls_ctrl_nolabel'},
    {'label': 'Sospecha de IGP', 'next': 'mpls_igp_sync'},
]
```

### Valores especiales de `next`

| Valor | Efecto |
|-------|--------|
| `'back_menu'` | Volver al menú principal de tecnologías. |
| `None` (o sin campo `next`) | Volver al paso anterior (pop del historial). |
| Cualquier otra clave | Ir al step con esa clave dentro de la **misma tecnología**. |

### Filtrado automático por tier

El motor **oculta automáticamente** las choices cuyo destino (`next`) tenga un `tier` mayor al seleccionado por el usuario. Esto evita que un Operador NOC (Tier 1) vea opciones que lo lleven a pasos de Arquitecto (Tier 4).

### Navegación implícita

El motor siempre añade dos opciones al final de cada menú de choices:
- **Volver atrás** → equivale a `next: None`
- **Volver al menú principal** → equivale a `next: 'back_menu'`

No es necesario (ni recomendado) incluirlas manualmente en `choices`.

---

## 7. Cómo personalizar la UI (display)

El archivo `utils/display.py` controla la apariencia en terminal.

### Dependencia opcional: `rich`

Instala `rich` para una experiencia visual profesional:

```bash
pip install rich>=13.0.0
```

Si `rich` no está instalado, el dashboard funciona igual con salida de texto plano.

### Cambiar el banner

Edita `print_banner()` en `utils/display.py`:

```python
def print_banner(tier: int = 1):
    tier_str = TIER_NAME.get(tier, "Tier 1")
    banner = (
        "╔══════════════════════════════════════════════════════════════════╗\n"
        "║      MI DASHBOARD DE RED  —  Tier 3 / Arquitecto                ║\n"
        f"║      Nivel activo: {tier_str:<46}║\n"
        "╚══════════════════════════════════════════════════════════════════╝"
    )
    ...
```

### Cambiar colores o estilos de Rich

Busca las líneas que usan `style="bold cyan"`, `border_style="green"`, etc., y modifícalas a tu gusto. Algunos estilos útiles de Rich: `bold red`, `yellow`, `magenta`, `dim`, `bright_white`.

### Cambiar etiquetas de tier

Edita el diccionario `TIER_NAME` en `utils/display.py`:

```python
TIER_NAME = {
    1: "Nivel 1 — Básico",
    2: "Nivel 2 — Intermedio",
    3: "Nivel 3 — Avanzado",
    4: "Nivel 4 — Experto",
}
```

O el diccionario `TIER_LABELS` en `core/engine.py` para los textos del menú de selección de nivel.

---

## 8. Configuración de VS Code

El archivo `.vscode/tasks.json` permite ejecutar el dashboard sin salir del editor:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "🌐 Network Tshoot Dashboard",
      "type": "shell",
      "command": "python main.py",
      "presentation": {
        "panel": "new"
      }
    }
  ]
}
```

### Cómo usarlo

1. Abre el proyecto en VS Code.
2. Presiona `Ctrl+Shift+P` (o `Cmd+Shift+P` en macOS).
3. Escribe **"Tasks: Run Task"**.
4. Selecciona **"🌐 Network Tshoot Dashboard"**.

### Personalizar el task

Puedes cambiar el icono, el nombre, o añadir argumentos:

```json
{
  "label": "🚀 Mi Dashboard Personalizado",
  "type": "shell",
  "command": "python main.py --modo-experto",
  "presentation": { "panel": "dedicated" }
}
```

---

## 9. Ejemplo completo: agregar una nueva tecnología

Vamos a agregar **"BGP Troubleshooting"** como ejemplo paso a paso.

### Paso 1: Abrir `data/knowledge_base.py`

### Paso 2: Agregar la tecnología al dict `_kb()`

```python
'bgp': {
    'name': 'BGP Troubleshooting',
    'description': 'Diagnóstico de sesiones BGP, path selection, communities, y route reflection.',
    'vendors': ['juniper', 'cisco_iosxr', 'cisco_iosxe'],
    'steps': {
        'bgp_start': {
            'title': '1. Ámbito del problema BGP',
            'tier': 1,
            'body': (
                '**Dónde:** El problema puede estar en la sesión BGP (no levanta), '
                'en la política (no se intercambian rutas), o en el path selection.'
                '\n\n'
                '**Cómo:** Peers en Idle/Active, rutas recibidas pero no instaladas, '
                'o next-hop inalcanzable.'
            ),
            'commands': {
                'juniper': {
                    'tier1': ['show bgp summary', 'show bgp neighbor'],
                    'tier2': ['show route table inet.0', 'show bgp neighbor detail'],
                },
                'cisco_iosxr': {
                    'tier1': ['show bgp all summary', 'show bgp neighbors'],
                    'tier2': ['show route ipv4', 'show cef <prefix>'],
                },
                'cisco_iosxe': {
                    'tier1': ['show ip bgp summary', 'show ip bgp neighbors'],
                    'tier2': ['show ip route', 'show ip cef <prefix>'],
                },
            },
            'expected': 'Peers Established. Rutas presentes en la tabla BGP.',
            'choices': [
                {'label': 'Peers caídos / no levantan', 'next': 'bgp_peers_down'},
                {'label': 'Peers UP pero no intercambian rutas', 'next': 'bgp_no_routes'},
            ]
        },
        'bgp_peers_down': {
            'title': '2.1 Peers BGP caídos',
            'tier': 1,
            'body': (
                '**Dónde:** Capa de transporte (TCP 179), reachability al neighbor, '
                'autenticación MD5/TTL.'
                '\n\n'
                '**Por qué:** ACL bloqueando 179, mismatch de AS, o update-source no alcanzable.'
            ),
            'commands': {
                'juniper': ['show bgp neighbor <peer> | match state', 'show route <peer>'],
                'cisco_iosxr': ['show bgp neighbors <peer> | include state', 'show ip route <peer>'],
                'cisco_iosxe': ['show ip bgp neighbors <peer> | include state', 'show ip route <peer>'],
            },
            'expected': 'Estado Established. Ruta válida al neighbor. TCP 179 abierto.',
            'choices': [
                {'label': 'Reachability falla', 'next': 'bgp_start'},
                {'label': 'Autenticación / TTL sospechoso', 'next': 'bgp_no_routes'},
            ]
        },
        'bgp_no_routes': {
            'title': '2.2 Peers UP sin intercambio de rutas',
            'tier': 2,
            'body': (
                '**Dónde:** Policies de import/export, prefix-lists, o communities.'
                '\n\n'
                '**Por qué:** Route-map descarta prefijos. Maximum-prefix alcanzado. '
                'AFI/SAFI no negociada.'
            ),
            'commands': {
                'juniper': ['show policy <name>', 'show route receive-protocol bgp <peer>'],
                'cisco_iosxr': ['show route-policy <name>', 'show bgp neighbors <peer> routes'],
                'cisco_iosxe': ['show route-map', 'show ip bgp neighbors <peer> routes'],
            },
            'expected': 'Rutas recibidas/advertisadas > 0. Sin prefix-limit exceeded.',
            'choices': [
                {'label': 'Volver al inicio BGP', 'next': 'bgp_start'},
            ]
        },
    }
}
```

### Paso 3: Guardar y probar

```bash
python main.py
```

En el menú principal ahora aparecerá:

```
[4] BGP Troubleshooting
```

---

## 10. Validación y pruebas

### Checklist antes de guardar cambios

- [ ] La clave de la tecnología tiene al menos un step terminado en `_start`.
- [ ] Los `next` de las choices apuntan a steps que **existen** dentro de la misma tecnología.
- [ ] Los vendor keys en `commands` coinciden con los definidos en `VendorMap`.
- [ ] Los valores de `tier` en los steps están entre 1 y 4.
- [ ] No hay claves de step duplicadas dentro de la misma tecnología.

### Ejecutar el dashboard

```bash
# Sin rich (modo texto plano)
python main.py

# Con rich (modo UI enriquecida)
pip install rich>=13.0.0
python main.py
```

### Depurar la base de conocimiento

Si el dashboard no inicia o falla al navegar:

1. Verifica que `_kb()` retorne un diccionario válido de Python.
2. Revisa que no haya comillas o comas faltantes en `knowledge_base.py`.
3. Asegúrate de que los steps `_start` existan para cada tecnología.

---

## Resumen rápido de edición

| Quiero hacer... | Archivo a editar | Sección relevante |
|-----------------|------------------|-------------------|
| Agregar una tecnología | `data/knowledge_base.py` | Clave de nivel superior en `_kb()` |
| Agregar un vendor | `data/knowledge_base.py` | `VendorMap` + `vendors` list + `commands` |
| Agregar/modificar un paso | `data/knowledge_base.py` | Dentro de `'steps'` de la tecnología |
| Cambiar comandos de un vendor | `data/knowledge_base.py` | Dentro de `'commands'` del step |
| Cambiar navegación entre pasos | `data/knowledge_base.py` | Campo `'choices'` del step |
| Cambiar apariencia terminal | `utils/display.py` | `print_banner`, `print_section`, colores Rich |
| Cambiar etiquetas de nivel | `core/engine.py` | `TIER_LABELS` |
| Agregar shortcut en VS Code | `.vscode/tasks.json` | Nuevo objeto en `"tasks"` |

---

*¿Necesitas ayuda para configurar una tecnología específica? Edita `data/knowledge_base.py` siguiendo esta guía y ejecuta `python main.py` para ver los cambios en tiempo real.*
