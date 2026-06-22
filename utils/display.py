"""Utilidades de display para la CLI de troubleshooting."""

import os
import sys
from typing import Dict, List, Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.rule import Rule
    from rich import box
    RICH_AVAILABLE = True
except Exception:
    RICH_AVAILABLE = False

_console = Console() if RICH_AVAILABLE else None

TIER_NAME = {
    1: "Tier 1 — Frontline / NOC L1",
    2: "Tier 2 — Network Specialist / NOC L2",
    3: "Tier 3 — Core Engineering / NOC L3",
    4: "Tier 4 — Vendor Support / TAC",
}


def _fallback_print(text: str):
    print(text)


def clear():
    if _console:
        _console.clear()
    else:
        os.system("clear" if os.name != "nt" else "cls")


def print_banner(tier: int = 1, confidence: int = -1):
    tier_str = TIER_NAME.get(tier, "Tier 1")
    conf_line = ""
    if 0 <= confidence <= 100:
        conf_bar = "█" * (confidence // 10) + "░" * (10 - confidence // 10)
        conf_color = "green" if confidence >= 70 else "yellow" if confidence >= 40 else "red"
        conf_line = f"\n║      Confianza Sesión: [{conf_bar}] {confidence}%{'':<30}║"
    banner = (
        "╔══════════════════════════════════════════════════════════════════╗\n"
        f"║      NET-TSHOOT DASHBOARD  —  {tier_str:<31} ║\n"
        f"║      Nivel activo: {tier_str:<46}║{conf_line}\n"
        "║      MPLS · L3VPN · L2VPN · EVPN · VXLAN · BGP · OSPF · IS-IS   ║\n"
        "║      STP · QoS/TE · BFD · Multicast · MP-BGP · DHCP · NetFlow   ║\n"
        "║      Juniper · Cisco · MikroTik · Fortinet · ADTRAN             ║\n"
        "╚══════════════════════════════════════════════════════════════════╝"
    )
    if _console:
        _console.print(Panel(banner, style="bold cyan", border_style="cyan"))
    else:
        print(banner)


def print_section(title: str, body: str, tier: int = 1):
    tier_str = TIER_NAME.get(tier, "Tier 1")
    header = f"[{tier_str}] {title}"
    if _console:
        _console.print(Rule(header, style="bold yellow"))
        _console.print(Panel(body, style="white", border_style="dim"))
    else:
        print(f"\n{'=' * 60}")
        print(f"  {header}")
        print(f"{'=' * 60}")
        print(body)


def print_commands(vendor_key: str, cmds: List[str]):
    if not cmds:
        print("  (Sin comandos específicos para este vendor)")
        return
    if _console:
        content = "\n".join(cmds)
        syntax = Syntax(content, "bash", theme="monokai", line_numbers=False)
        _console.print(Panel(syntax, title=f"Comandos — {vendor_key}", border_style="green"))
    else:
        print(f"\n  Comandos [{vendor_key}]:")
        for c in cmds:
            print(f"    $ {c}")


def print_expected(text: str):
    if _console:
        _console.print(Panel(text, title="Resultado Esperado / Qué buscar", border_style="magenta"))
    else:
        print(f"\n  [Resultado Esperado]\n    {text}\n")


def print_active_variables(vars_dict: Dict[str, str]):
    if not vars_dict:
        return
    
    lines = []
    for k, v in vars_dict.items():
        if v == f"<{k}>":
            lines.append(f"  • [bold yellow]{k}[/bold yellow]: [dim](No definido)[/dim]")
        else:
            lines.append(f"  • [bold yellow]{k}[/bold yellow]: [bold green]{v}[/bold green]")
    
    content = "\n".join(lines)
    if _console:
        _console.print(Panel(content, title="Variables de Comandos", border_style="yellow"))
    else:
        print("\n  [Variables de Comandos]")
        for k, v in vars_dict.items():
            val_str = "(No definido)" if v == f"<{k}>" else v
            print(f"  • {k}: {val_str}")
        print()


def print_step_notes(note_text: str):
    if _console:
        _console.print(Panel(note_text, title="Mis anotaciones en este paso", border_style="yellow", style="italic"))
    else:
        print(f"\n  [Mis anotaciones en este paso]\n    {note_text}\n")


def print_choices(choices: List[Dict[str, Any]]):
    if _console:
        table = Table(show_header=False, box=box.SIMPLE)
        table.add_column("#", style="bold cyan", justify="right")
        table.add_column("Opción", style="white")
        for i, ch in enumerate(choices, start=1):
            table.add_row(str(i), ch["label"])
        _console.print(table)
    else:
        for i, ch in enumerate(choices, start=1):
            print(f"  [{i}] {ch['label']}")


def prompt_choice(prompt_text: str = "Seleccione opción: ") -> str:
    try:
        return input(prompt_text).strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)


def print_alert(text: str):
    if _console:
        _console.print(Panel(text, title="ALERTA", border_style="red", style="bold red"))
    else:
        print(f"\n  [ALERTA] {text}\n")


def print_breadcrumbs(crumbs: List[str]):
    if _console:
        breadcrumb_text = "  > ".join(crumbs)
        _console.print(Panel(breadcrumb_text, title="Navegación", border_style="dim", style="dim"))
    else:
        print(f"\n  [{' > '.join(crumbs)}]")


def print_quick_fix(text: str):
    if _console:
        _console.print(Panel(text, title="🛠️ Solución Rápida / Quick Fix", border_style="green", style="bold green"))
    else:
        print(f"\n  [SOLUCIÓN RÁPIDA]\n    {text}\n")


def print_hierarchies(step: Dict[str, Any]):
    """Imprime el panel de jerarquías de red, OSI y metodologías."""
    osi = step.get("osi_layer")
    domain = step.get("network_domain")
    methodology = step.get("methodology")
    
    if not any([osi, domain, methodology]):
        return
        
    lines = []
    if osi:
        lines.append(f"📡 [bold cyan]Jerarquía Técnica (OSI):[/bold cyan] {osi}")
    if domain:
        lines.append(f"🗺️  [bold green]Jerarquía de Red (Topología):[/bold green] {domain}")
    if methodology:
        lines.append(f"⚙️  [bold yellow]Metodología de Diagnóstico:[/bold yellow] {methodology}")
        
    content = "\n".join(lines)
    if _console:
        _console.print(Panel(content, title="Jerarquías de Troubleshooting", border_style="blue"))
    else:
        print("\n  [Jerarquías de Troubleshooting]")
        if osi:
            print(f"    • Técnica (OSI): {osi}")
        if domain:
            print(f"    • Red (Topología): {domain}")
        if methodology:
            print(f"    • Metodología: {methodology}")
        print()


def print_change_tickets(tickets: List[Dict[str, str]]):
    """Muestra de forma elegante los tickets en formato tabular o de paneles."""
    if _console:
        table = Table(title="RFC Log — Últimas 24 Horas", border_style="bold yellow", show_lines=True)
        table.add_column("ID", style="bold cyan", width=10)
        table.add_column("Tiempo / Time", style="magenta", width=15)
        table.add_column("Dispositivo / Device", style="green", width=15)
        table.add_column("Descripción / Description (ES / EN)", style="white")
        table.add_column("Estado / Status", style="bold green", width=20)
        table.add_column("Autor", style="dim white", width=15)
        
        for t in tickets:
            desc = f"{t['description_es']}\n[dim]{t['description_en']}[/dim]"
            table.add_row(t['id'], t['time_es'], t['device'], desc, t['status'], t['author'])
        _console.print(table)
    else:
        print("-" * 80)
        print(f"{'ID':<10} | {'Tiempo':<12} | {'Dispositivo':<15} | {'Estado':<15}")
        print("-" * 80)
        for t in tickets:
            print(f"{t['id']:<10} | {t['time_es']:<12} | {t['device']:<15} | {t['status']:<15}")
            print(f"Descripción: {t['description_es']}")
            print(f"Description: {t['description_en']}")
            print(f"Autor: {t['author']}")
            print("-" * 80)


def print_golden_comparison(command: str, current: str, golden: str):
    """Compara línea a línea las dos salidas y muestra las diferencias."""
    if _console:
        table = Table(title=f"Comando: {command}", show_header=True, header_style="bold magenta", box=None)
        table.add_column("SALIDA ACTUAL (CON FALLA)", style="bold red", ratio=1)
        table.add_column("LÍNEA BASE (GOLDEN CONFIG)", style="bold green", ratio=1)
        
        curr_lines = current.split('\n')
        gold_lines = golden.split('\n')
        max_lines = max(len(curr_lines), len(gold_lines))
        
        for i in range(max_lines):
            c_l = curr_lines[i] if i < len(curr_lines) else ""
            g_l = gold_lines[i] if i < len(gold_lines) else ""
            
            if c_l != g_l:
                table.add_row(f"[bold red]{c_l}[/bold red]", f"[bold green]{g_l}[/bold green]")
            else:
                table.add_row(f"[dim white]{c_l}[/dim white]", f"[dim white]{g_l}[/dim white]")
                
        _console.print(Panel(table, border_style="cyan"))
    else:
        print(f"\n>>> Comando: {command}")
        print(f"{'='*30} SALIDA ACTUAL (CON FALLA) {'='*30}")
        print(current)
        print(f"{'='*30} LÍNEA BASE (GOLDEN CONFIG) {'='*30}")
        print(golden)
        print("-" * 80)


def print_concepts(tech_name: str, concepts: Dict[str, str]):
    title_map = {
        "definition": "Definición",
        "key_concepts": "Conceptos Clave",
        "architecture": "Arquitectura",
        "control_vs_data": "Plano de Control vs. Datos",
        "troubleshooting_strategy": "Estrategia de Troubleshooting",
        "configuration_basics": "Fundamentos de Configuración",
    }
    if _console:
        _console.print(Rule(f"Conceptos y Definiciones — {tech_name}", style="bold green"))
        for key, text in concepts.items():
            title = title_map.get(key, key.replace("_", " ").title())
            _console.print(Panel(text, title=title, border_style="green"))
        _console.print()
    else:
        print(f"\n{'=' * 60}")
        print(f"  Conceptos y Definiciones — {tech_name}")
        print(f"{'=' * 60}")
        for key, text in concepts.items():
            title = title_map.get(key, key.replace("_", " ").title())
            print(f"\n  [{title}]")
            print(f"    {text}")
        print()


def print_scientific_fields(step: Dict[str, Any]):
    """Renderiza los campos científicos (hipótesis, evidencia, sesgos, etc.) de un paso."""
    hypothesis = step.get("hypothesis")
    verification = step.get("verification_steps", [])
    expected_ev = step.get("expected_evidence", {})
    basis = step.get("scientific_basis")
    confidence = step.get("confidence_level")
    biases = step.get("bias_warnings", [])
    references = step.get("references", [])

    if not any([hypothesis, verification, expected_ev, basis, confidence, biases, references]):
        return

    def _build_panel():
        lines = []
        if hypothesis:
            lines.append(f"[bold yellow]🔬 Hipótesis:[/bold yellow] {hypothesis}\n")
        if verification:
            lines.append("[bold cyan]🧪 Pasos de Verificación:[/bold cyan]")
            for v in verification:
                lines.append(f"  • {v}")
            lines.append("")
        if expected_ev:
            confirming = expected_ev.get("confirming", [])
            invalidating = expected_ev.get("invalidating", [])
            if confirming:
                lines.append("[bold green]✅ Evidencia Confirmatoria (esperada si la hipótesis es CIERTA):[/bold green]")
                for item in confirming:
                    lines.append(f"  [green]+[/green] {item}")
                lines.append("")
            if invalidating:
                lines.append("[bold red]❌ Evidencia Invalidante (descarta la hipótesis):[/bold red]")
                for item in invalidating:
                    lines.append(f"  [red]-[/red] {item}")
                lines.append("")
        if basis:
            lines.append(f"[bold blue]📚 Base Científica:[/bold blue] {basis}\n")
        if confidence:
            color = "green" if confidence.lower() == "alta" else "yellow" if confidence.lower() == "media" else "red"
            lines.append(f"[bold {color}]📊 Nivel de Confianza: {confidence}[/bold {color}]\n")
        if biases:
            lines.append("[bold magenta]⚠️ Advertencias de Sesgo (Anti-Confirmation Bias):[/bold magenta]")
            for b in biases:
                lines.append(f"  [magenta]•[/magenta] {b}")
            lines.append("")
        if references:
            lines.append("[bold white]🔗 Referencias:[/bold white]")
            for r in references:
                lines.append(f"  • {r}")
            lines.append("")
        return "\n".join(lines)

    def _build_plain():
        lines = []
        if hypothesis:
            lines.append(f"\n  [HIPOTESIS] {hypothesis}")
        if verification:
            lines.append("\n  [PASOS DE VERIFICACION]")
            for v in verification:
                lines.append(f"    • {v}")
        if expected_ev:
            confirming = expected_ev.get("confirming", [])
            invalidating = expected_ev.get("invalidating", [])
            if confirming:
                lines.append("\n  [EVIDENCIA CONFIRMATORIA]")
                for item in confirming:
                    lines.append(f"    + {item}")
            if invalidating:
                lines.append("\n  [EVIDENCIA INVALIDANTE]")
                for item in invalidating:
                    lines.append(f"    - {item}")
        if basis:
            lines.append(f"\n  [BASE CIENTIFICA] {basis}")
        if confidence:
            lines.append(f"\n  [NIVEL DE CONFIANZA] {confidence}")
        if biases:
            lines.append("\n  [ADVERTENCIAS DE SESGO]")
            for b in biases:
                lines.append(f"    • {b}")
        if references:
            lines.append("\n  [REFERENCIAS]")
            for r in references:
                lines.append(f"    • {r}")
        return "\n".join(lines)

    if _console:
        panel_content = _build_panel()
        _console.print(Panel(panel_content, title="Método Científico de Troubleshooting", border_style="cyan", style="white"))
    else:
        print(_build_plain())


def print_packet_step(step: Dict[str, Any]):
    step_title = step.get("step_title", "Paso")
    device = step.get("device", "")
    action = step.get("action", "")
    note = step.get("note", "")

    if _console:
        _console.print(Rule(f"{step_title} — {device}", style="bold blue"))
        if action:
            _console.print(Panel(action, title="Acción", border_style="yellow"))
        if note:
            _console.print(Panel(note, title="Nota", border_style="dim"))

        for layer in step.get("layers", []):
            name = layer.get("name", "Capa")
            detail = layer.get("detail", "")
            checks = layer.get("checks", "")
            anomalies = layer.get("anomalies", "")

            # Color por tipo de capa
            border = "white"
            if "Capa 7" in name or "Capa 6" in name or "Capa 5" in name:
                border = "cyan"
            elif "Capa 4" in name:
                border = "green"
            elif "Capa 3" in name:
                border = "yellow"
            elif "Capa 2.5" in name or "MPLS" in name or "VXLAN" in name or "PW" in name or "VNI" in name:
                border = "magenta"
            elif "Capa 2" in name:
                border = "blue"
            elif "Capa 1" in name:
                border = "dim"

            table = Table(show_header=False, box=box.ROUNDED, border_style=border)
            table.add_column("Campo", style="bold", no_wrap=True)
            table.add_column("Valor", style="white")
            if detail:
                table.add_row("Contenido", detail)
            if checks:
                table.add_row("Verificar", checks)
            if anomalies:
                table.add_row("Anomalías", anomalies)
            pc = layer.get("packet_capture")
            if pc:
                w = pc.get("wireshark_display_filter", "N/A")
                t = pc.get("tcpdump_filter", "N/A")
                n = pc.get("notes", "")
                cap_text = f"Wireshark: {w}\ntcpdump: {t}"
                if n:
                    cap_text += f"\nNota: {n}"
                table.add_row("Captura", cap_text)
            _console.print(Panel(table, title=name, border_style=border))
    else:
        print(f"\n{'=' * 60}")
        print(f"  {step_title}")
        print(f"  Dispositivo: {device}")
        if action:
            print(f"  Acción: {action}")
        if note:
            print(f"  Nota: {note}")
        print(f"{'=' * 60}")
        for layer in step.get("layers", []):
            name = layer.get("name", "Capa")
            print(f"\n  [{name}]")
            if layer.get("detail"):
                print(f"    Contenido: {layer['detail']}")
            if layer.get("checks"):
                print(f"    Verificar: {layer['checks']}")
            if layer.get("anomalies"):
                print(f"    Anomalías: {layer['anomalies']}")
            pc = layer.get("packet_capture")
            if pc:
                print(f"    [Captura]")
                print(f"      Wireshark: {pc.get('wireshark_display_filter', 'N/A')}")
                print(f"      tcpdump:   {pc.get('tcpdump_filter', 'N/A')}")
                if pc.get("notes"):
                    print(f"      Nota:      {pc['notes']}")


def pause():
    try:
        input("\nPresione ENTER para continuar...")
    except (EOFError, KeyboardInterrupt):
        pass
