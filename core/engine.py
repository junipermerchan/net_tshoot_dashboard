"""Motor de navegación interactiva del dashboard de troubleshooting."""

from typing import Optional, Dict, Any, List
from pathlib import Path
from data.knowledge_base import KB, VendorMap, TECH_CONCEPTS
from data.packet_walkthroughs import PACKET_WALKTHROUGHS, WALKTHROUGH_ALIASES
from utils import display


TIER_LABELS = {
    1: "Tier 1 — Operador NOC",
    2: "Tier 2 — Ingeniero de Soporte",
    3: "Tier 3 — Ingeniero de Escalación",
    4: "Arquitecto de Red",
}


class Engine:
    def __init__(self):
        self.tech: Optional[str] = None
        self.vendor: Optional[str] = None
        self.tier: int = 1
        self.current_step: Optional[str] = None
        self.history: List[str] = []
        self.session_variables: Dict[str, str] = {}
        self.notes_log: List[Dict[str, Any]] = []
        self.scientific_mode: str = "normal"  # normal | semi_strict | strict
        self.evidence_registered: set = set()  # (tech, step) tuples
        self.session_confidence: int = 50  # 0-100 score
        self.invalidated_streak: int = 0

    def start(self):
        while True:
            display.clear()
            display.print_banner(confidence=self.session_confidence)
            choice = self._main_menu()
            if choice == "exit":
                self._export_report()
                display.print_alert("Saliendo. Buena suerte en el troubleshooting.")
                break
            elif choice == "search":
                self._run_global_search()
                continue
            elif choice == "sci_mode":
                self._configure_scientific_mode()
                continue
            elif choice == "diagnostico_magico":
                self._run_magic_diagnostic()
                continue
            self.tech = choice
            concepts_result = self._concepts_menu()
            if concepts_result == "back":
                self.tech = None
                continue
            elif concepts_result == "walkthrough":
                self._run_packet_walkthrough()
                self.tech = None
                self.vendor = None
                self.tier = 1
                self.current_step = None
                self.history.clear()
                continue
            # else "continue"
            self._vendor_select()
            if self.vendor:
                self._tier_select()
                if self.tier:
                    self._run_technology_flow()
            self.tech = None
            self.vendor = None
            self.tier = 1
            self.current_step = None
            self.history.clear()

    def _main_menu(self) -> str:
        troubleshooting: List[Dict[str, Any]] = []
        configuration: List[Dict[str, Any]] = []
        for key, meta in KB.items():
            item = {"key": key, "label": meta["name"]}
            if key.endswith("_config"):
                configuration.append(item)
            else:
                troubleshooting.append(item)

        filter_query = ""
        while True:
            # Filtrar tecnologías si hay un filtro de búsqueda activo
            filtered_ts = []
            filtered_config = []
            for opt in troubleshooting:
                if not filter_query or filter_query.lower() in opt["label"].lower() or filter_query.lower() in opt["key"].lower():
                    filtered_ts.append(opt)
            for opt in configuration:
                if not filter_query or filter_query.lower() in opt["label"].lower() or filter_query.lower() in opt["key"].lower():
                    filtered_config.append(opt)

            options: List[Dict[str, Any]] = []
            options.append({"category": True, "label": "━━ Herramientas ━━"})
            mode_label = f"Modo Científico ({self.scientific_mode})"
            options.append({"key": "sci_mode", "label": f"⚙️ Configurar {mode_label}"})
            options.append({"key": "search", "label": "Búsqueda Global (Comandos y Conceptos)"})
            options.append({"key": "diagnostico_magico", "label": "🤖 Diagnóstico Mágico de Configuración y Logs (Analizador)"})

            if filtered_ts:
                options.append({"category": True, "label": "━━ Troubleshooting ━━"})
                options.extend(filtered_ts)
            if filtered_config:
                options.append({"category": True, "label": "━━ Configuración ━━"})
                options.extend(filtered_config)

            options.append({"category": True, "label": "━━ Sistema ━━"})
            options.append({"key": "exit", "label": "Salir"})
            if filter_query:
                options.append({"key": "clear_filter", "label": "Limpiar filtro de búsqueda"})

            print("\nTecnologías disponibles:")
            if filter_query:
                print(f"  [Filtro activo: '{filter_query}']")

            idx_map: Dict[int, str] = {}
            num = 1
            for opt in options:
                if opt.get("category"):
                    print(f"\n  {opt['label']}")
                else:
                    print(f"  [{num}] {opt['label']}")
                    idx_map[num] = opt["key"]
                    num += 1

            val = display.prompt_choice("\nSeleccione opción (o escriba texto para buscar/filtrar): ")
            if not val:
                continue

            try:
                choice_num = int(val)
                if choice_num in idx_map:
                    sel_key = idx_map[choice_num]
                    if sel_key == "clear_filter":
                        filter_query = ""
                        display.clear()
                        display.print_banner(confidence=self.session_confidence)
                        continue
                    return sel_key
            except ValueError:
                # Si el usuario escribe texto, se aplica como filtro de tecnologías
                filter_query = val
                display.clear()
                display.print_banner(confidence=self.session_confidence)
                continue

            display.print_alert("Opción inválida.")

    def _configure_scientific_mode(self):
        while True:
            display.clear()
            display.print_banner(confidence=self.session_confidence)
            print("\n=== Configurar Modo Científico de Troubleshooting ===\n")
            print("  [1] Normal — Campos científicos como guía opcional (por defecto)")
            print("  [2] Semi-Estricto — Advertencia si avanza sin registrar evidencia en pasos Tier ≥ 3")
            print("  [3] Estricto — Bloquea avance hasta registrar evidencia en pasos con hipótesis")
            print("  [4] Volver al menú principal")
            print(f"\n  Modo actual: {self.scientific_mode.upper()}")
            val = display.prompt_choice("\nSeleccione opción: ").strip()
            if val == "1":
                self.scientific_mode = "normal"
                display.print_alert("Modo Científico: NORMAL. La navegación es libre.")
                display.pause()
                return
            elif val == "2":
                self.scientific_mode = "semi_strict"
                display.print_alert("Modo Científico: SEMI-ESTRICTO. Se mostrarán advertencias en pasos complejos.")
                display.pause()
                return
            elif val == "3":
                self.scientific_mode = "strict"
                display.print_alert("Modo Científico: ESTRICTO. Debe registrar evidencia antes de avanzar en pasos con hipótesis.")
                display.pause()
                return
            elif val == "4":
                return
            else:
                display.print_alert("Opción inválida.")

    def _concepts_menu(self) -> str:
        tech_meta = KB.get(self.tech, {})
        concepts = TECH_CONCEPTS.get(self.tech, {})
        if not concepts and self.tech.endswith("_config"):
            concepts = TECH_CONCEPTS.get(self.tech.replace("_config", ""), {})
        walkthrough_key = WALKTHROUGH_ALIASES.get(self.tech, self.tech)
        has_walkthrough = walkthrough_key in PACKET_WALKTHROUGHS
        if not concepts and not has_walkthrough:
            return "continue"
        while True:
            display.clear()
            display.print_banner(confidence=self.session_confidence)
            print(f"\nTecnología: {tech_meta.get('name', self.tech)}\n")
            print("  [1] Ver Conceptos y Definiciones")
            print("  [2] Continuar a Troubleshooting / Configuración")
            if has_walkthrough:
                print("  [3] Simulación de Paquete por Capas OSI")
                print("  [4] Volver al menú principal")
            else:
                print("  [3] Volver al menú principal")
            val = display.prompt_choice("\nSeleccione opción: ")
            if val == "1":
                if concepts:
                    display.print_concepts(tech_meta.get("name", self.tech), concepts)
                else:
                    display.print_alert("No hay conceptos definidos para esta tecnología.")
                display.pause()
            elif val == "2":
                return "continue"
            elif val == "3":
                if has_walkthrough:
                    return "walkthrough"
                return "back"
            elif val == "4":
                if has_walkthrough:
                    return "back"
                display.print_alert("Opción inválida.")
            else:
                display.print_alert("Opción inválida.")

    def _vendor_select(self):
        tech_meta = KB.get(self.tech, {})
        vendors = tech_meta.get("vendors", [])
        opts = []
        for v in vendors:
            opts.append({"key": v, "label": VendorMap.get(v, v)})
        opts.append({"key": "back", "label": "Volver al menú principal"})

        while True:
            display.clear()
            display.print_banner(confidence=self.session_confidence)
            print(f"\nVendor para: {tech_meta.get('name', self.tech)}\n")
            for i, opt in enumerate(opts, start=1):
                print(f"  [{i}] {opt['label']}")
            val = display.prompt_choice("Seleccione vendor: ")
            try:
                idx = int(val) - 1
                if 0 <= idx < len(opts):
                    sel = opts[idx]["key"]
                    if sel == "back":
                        self.vendor = None
                        return
                    self.vendor = sel
                    return
            except ValueError:
                pass
            display.print_alert("Opción inválida.")

    def _tier_select(self):
        opts = [
            {"key": 1, "label": TIER_LABELS[1]},
            {"key": 2, "label": TIER_LABELS[2]},
            {"key": 3, "label": TIER_LABELS[3]},
            {"key": 4, "label": TIER_LABELS[4]},
        ]
        while True:
            display.clear()
            display.print_banner(confidence=self.session_confidence)
            print(f"\nIntensidad de troubleshooting para: {KB[self.tech].get('name', self.tech)}\n")
            for i, opt in enumerate(opts, start=1):
                print(f"  [{i}] {opt['label']}")
            val = display.prompt_choice("Seleccione nivel: ")
            try:
                idx = int(val) - 1
                if 0 <= idx < len(opts):
                    self.tier = opts[idx]["key"]
                    return
            except ValueError:
                pass
            display.print_alert("Opción inválida.")

    def _step_tier(self, step_key: str) -> int:
        steps = KB.get(self.tech, {}).get("steps", {})
        step = steps.get(step_key, {})
        return step.get("tier", 1)

    def _flatten_commands(self, raw: Any) -> List[str]:
        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict):
            result: List[str] = []
            # Acumular según tier seleccionado
            for lvl in ("tier1", "tier2", "tier3", "arch"):
                if lvl in raw:
                    # mapear arch->tier4
                    tier_num = {"tier1": 1, "tier2": 2, "tier3": 3, "arch": 4}.get(lvl, 99)
                    if tier_num <= self.tier:
                        result.extend(raw[lvl])
            return result
        return []

    def _run_technology_flow(self, start_step: Optional[str] = None):
        steps = KB[self.tech].get("steps", {})
        if not steps:
            display.print_alert("No hay pasos definidos para esta tecnología.")
            return

        if start_step:
            self.current_step = start_step
        else:
            self.current_step = "start"
            for key in steps:
                if key.endswith("_start"):
                    self.current_step = key
                    break

        while self.current_step:
            # Si el step actual supera el tier, tratar de saltar a una choice válida
            if self._step_tier(self.current_step) > self.tier:
                step = steps.get(self.current_step, {})
                # Buscar primera choice cuyo destino sea visible
                found = False
                for ch in step.get("choices", []):
                    nxt = ch.get("next")
                    if nxt is None or nxt == "back_menu":
                        continue
                    if self._step_tier(nxt) <= self.tier:
                        self.current_step = nxt
                        found = True
                        break
                if not found:
                    display.print_alert(
                        f"Paso '{self.current_step}' requiere nivel {self._step_tier(self.current_step)}. "
                        "No hay ruta alternativa en su tier seleccionado. Volviendo..."
                    )
                    if self.history:
                        self.current_step = self.history.pop()
                    else:
                        self.current_step = None
                    display.pause()
                continue

            step = steps.get(self.current_step)
            if not step:
                # Buscar en otras tecnologías si el paso existe allí
                found_tech = None
                for t_key, t_data in KB.items():
                    if self.current_step in t_data.get("steps", {}):
                        found_tech = t_key
                        break
                if found_tech:
                    self.tech = found_tech
                    steps = KB[self.tech].get("steps", {})
                    step = steps.get(self.current_step)
                else:
                    display.print_alert(f"Paso '{self.current_step}' no encontrado.")
                    break

            next_step = self._render_step(step)

            if next_step in ("__vars__", "__add_note__", "__view_notes__", "__run_sim__", "__reg_evidence__", "__run_rca__", "__compare_golden__", "__view_rfcs__"):
                if next_step == "__vars__":
                    self._configure_step_variables(step)
                elif next_step == "__add_note__":
                    self._add_step_note(step)
                elif next_step == "__view_notes__":
                    self._view_session_notes()
                elif next_step == "__run_sim__":
                    self._run_command_simulation(step)
                elif next_step == "__reg_evidence__":
                    self._register_evidence(step)
                elif next_step == "__run_rca__":
                    self._run_rca_wizard(step)
                elif next_step == "__compare_golden__":
                    self._run_golden_comparison(step)
                elif next_step == "__view_rfcs__":
                    self._run_view_rfcs()
                continue

            if next_step is None:
                # Volver uno atrás usando la pila limpia de historial
                if self.history:
                    self.current_step = self.history.pop()
                else:
                    self.current_step = None
            elif next_step == "back_menu":
                self.current_step = None
            else:
                # Avanzar guardando el paso actual en el historial
                self.history.append(self.current_step)
                self.current_step = next_step

    def _render_step(self, step: Dict[str, Any]) -> Optional[str]:
        display.clear()
        display.print_banner(self.tier, confidence=self.session_confidence)
        
        # Breadcrumbs
        self._print_breadcrumbs()
        
        applied_body = self._apply_variables(step.get("body", ""))
        display.print_section(step["title"], applied_body, step.get("tier", 1))
        
        # Mostrar Jerarquías de red y metodologías
        display.print_hierarchies(step)

        raw_cmds = step.get("commands", {}).get(self.vendor, [])
        cmds = self._flatten_commands(raw_cmds)
        applied_cmds = [self._apply_variables(c) for c in cmds]
        display.print_commands(self.vendor, applied_cmds)
        
        applied_expected = self._apply_variables(step.get("expected", "N/A"))
        display.print_expected(applied_expected)

        # Mostrar campos científicos mejorados si el paso los tiene
        display.print_scientific_fields(step)

        # Mostrar Quick Fix (solución concreta) si existe
        fix_text = step.get("fix")
        if fix_text:
            display.print_quick_fix(fix_text)

        # Mostrar variables activas si hay placeholders
        step_placeholders = self._get_placeholders(cmds)
        if step_placeholders:
            vars_dict = {ph: self.session_variables.get(ph, f"<{ph}>") for ph in step_placeholders}
            display.print_active_variables(vars_dict)

        # Mostrar notas registradas para este paso
        existing_note = None
        for n in self.notes_log:
            if n["tech"] == self.tech and n["step"] == self.current_step:
                existing_note = n["note"]
                break
        if existing_note:
            display.print_step_notes(existing_note)

        choices = step.get("choices", [])
        if not choices:
            display.pause()
            return None

        # Filtrar choices que apuntan a steps de tier superior al seleccionado
        visible_choices = []
        for ch in choices:
            nxt = ch.get("next")
            if nxt is None or nxt == "back_menu":
                visible_choices.append(ch)
                continue
            if self._step_tier(nxt) <= self.tier:
                visible_choices.append(ch)

        # Añadir opciones de navegación y herramientas
        nav_choices = visible_choices.copy()
        if cmds:
            nav_choices.append({"label": "💻 Ejecutar Simulación de Comandos (Sandbox)", "next": "__run_sim__"})
            nav_choices.append({"label": "⚖️  Comparar con Configuración de Referencia (Golden Config)", "next": "__compare_golden__"})
        nav_choices.append({"label": "🎫  Ver Historial de Cambios Recientes (RFC Log)", "next": "__view_rfcs__"})
        if step_placeholders:
            nav_choices.append({"label": "🔧 Configurar variables para este paso", "next": "__vars__"})
        if step.get("hypothesis"):
            already_ev = (self.tech, self.current_step) in self.evidence_registered
            ev_label = "🔬 Registrar Evidencia (Confirmar/Invalidar Hipótesis)"
            if already_ev:
                ev_label += " [✅ YA REGISTRADA]"
            nav_choices.append({"label": ev_label, "next": "__reg_evidence__"})
        nav_choices.append({"label": "🕵️  Realizar Análisis de Causa Raíz (RCA - 5 Porqués)", "next": "__run_rca__"})
        nav_choices.append({"label": "📝 Añadir nota a este paso", "next": "__add_note__"})
        nav_choices.append({"label": "📋 Ver bitácora de esta sesión", "next": "__view_notes__"})
        nav_choices.append({"label": "Volver atrás", "next": None})
        nav_choices.append({"label": "Volver al menú principal", "next": "back_menu"})

        # Indicador de modo científico activo
        if self.scientific_mode != "normal" and step.get("hypothesis"):
            print(f"\n  [Modo Científico: {self.scientific_mode.upper()}]")
            if self.scientific_mode == "strict" and (self.tech, self.current_step) not in self.evidence_registered:
                print("  ⚠️ Debe registrar evidencia antes de avanzar a otro paso.")

        print("\nOpciones:")
        display.print_choices(nav_choices)
        print("\n  [Atajos: 0=Volver atrás, 99=Menú principal, 88=Simulación, 77=Notas, 66=Variables, 55=RCA, 44=RFC Log, 33=Golden Config]")

        while True:
            val = display.prompt_choice("Seleccione opción: ")
            # Atajos rápidos
            if val == "0":
                val = str(len(nav_choices) - 1)  # Volver atrás (penúltima opción)
            elif val == "99":
                val = str(len(nav_choices))  # Menú principal (última opción)
            elif val == "88":
                # Buscar índice de simulación
                for i, ch in enumerate(nav_choices):
                    if ch.get("next") == "__run_sim__":
                        val = str(i + 1)
                        break
            elif val == "77":
                for i, ch in enumerate(nav_choices):
                    if ch.get("next") == "__add_note__":
                        val = str(i + 1)
                        break
            elif val == "66":
                for i, ch in enumerate(nav_choices):
                    if ch.get("next") == "__vars__":
                        val = str(i + 1)
                        break
            elif val == "55":
                for i, ch in enumerate(nav_choices):
                    if ch.get("next") == "__run_rca__":
                        val = str(i + 1)
                        break
            elif val == "44":
                for i, ch in enumerate(nav_choices):
                    if ch.get("next") == "__view_rfcs__":
                        val = str(i + 1)
                        break
            elif val == "33":
                for i, ch in enumerate(nav_choices):
                    if ch.get("next") == "__compare_golden__":
                        val = str(i + 1)
                        break
            try:
                idx = int(val) - 1
                if 0 <= idx < len(nav_choices):
                    sel = nav_choices[idx]
                    nxt = sel.get("next")
                    # Modo estricto: bloquear avance si no hay evidencia registrada
                    if self.scientific_mode == "strict" and step.get("hypothesis"):
                        if nxt not in ("__reg_evidence__", "__vars__", "__run_sim__", None, "back_menu", "__add_note__", "__view_notes__", "__run_rca__", "__compare_golden__", "__view_rfcs__"):
                            if (self.tech, self.current_step) not in self.evidence_registered:
                                display.print_alert("MODO ESTRICTO: Debe registrar evidencia para este paso antes de avanzar. Seleccione '🔬 Registrar Evidencia'.")
                                continue
                    # Modo semi-estricto: advertencia amarilla si no hay evidencia
                    if self.scientific_mode == "semi_strict" and step.get("hypothesis"):
                        if nxt not in ("__reg_evidence__", "__vars__", "__run_sim__", None, "back_menu", "__add_note__", "__view_notes__", "__run_rca__", "__compare_golden__", "__view_rfcs__"):
                            if (self.tech, self.current_step) not in self.evidence_registered:
                                display.print_alert("ADVERTENCIA: No ha registrado evidencia para esta hipótesis. Se recomienda documentar antes de continuar.")
                                # No bloquea, solo advierte
                    return nxt
            except ValueError:
                pass
            display.print_alert("Opción inválida.")

    def _run_packet_walkthrough(self):
        walkthrough_key = WALKTHROUGH_ALIASES.get(self.tech, self.tech)
        tech_walkthroughs = PACKET_WALKTHROUGHS.get(walkthrough_key)
        if not tech_walkthroughs:
            display.print_alert("No hay simulación de paquete disponible para esta tecnología.")
            display.pause()
            return

        scenarios = tech_walkthroughs.get("scenarios", [])
        if not scenarios:
            display.print_alert("No hay escenarios definidos para esta tecnología.")
            display.pause()
            return

        while True:
            display.clear()
            display.print_banner(confidence=self.session_confidence)
            print(f"\nSimulación de Paquete — {KB[self.tech].get('name', self.tech)}\n")
            for i, sc in enumerate(scenarios, 1):
                print(f"  [{i}] {sc['name']}")
                print(f"      {sc.get('description', '')}")
            print(f"  [{len(scenarios) + 1}] Volver")
            val = display.prompt_choice("\nSeleccione escenario: ")
            try:
                idx = int(val) - 1
                if idx == len(scenarios):
                    return
                if 0 <= idx < len(scenarios):
                    self._run_walkthrough_scenario(scenarios[idx])
            except ValueError:
                pass
            display.print_alert("Opción inválida.")

    def _run_walkthrough_scenario(self, scenario: Dict[str, Any]):
        steps = scenario.get("steps", [])
        if not steps:
            display.print_alert("El escenario seleccionado no tiene pasos.")
            display.pause()
            return

        current = 0
        while True:
            step = steps[current]
            display.clear()
            display.print_banner(confidence=self.session_confidence)
            display.print_packet_step(step)
            print(f"\nPaso {current + 1} de {len(steps)}")
            print("\n  [1] Siguiente paso")
            print("  [2] Paso anterior")
            print("  [3] Volver a escenarios")
            val = display.prompt_choice("\nSeleccione opción: ")
            if val == "1":
                if current + 1 < len(steps):
                    current += 1
                else:
                    display.print_alert("Último paso alcanzado.")
            elif val == "2":
                if current > 0:
                    current -= 1
                else:
                    display.print_alert("Primer paso alcanzado.")
            elif val == "3":
                return
            else:
                display.print_alert("Opción inválida.")

    def _print_breadcrumbs(self):
        """Imprime la ruta de navegación actual (breadcrumbs) basada en el historial."""
        if not self.history:
            return
        crumbs = []
        steps = KB.get(self.tech, {}).get("steps", {})
        for h in self.history:
            s = steps.get(h, {})
            title = s.get("title", h)
            crumbs.append(title)
        # Añadir el paso actual
        current_step = steps.get(self.current_step, {})
        crumbs.append(current_step.get("title", self.current_step))
        if len(crumbs) > 1:
            display.print_breadcrumbs(crumbs)

    def _get_placeholders(self, cmds: List[str]) -> List[str]:
        import re
        found = []
        for cmd in cmds:
            for match in re.findall(r'<([A-Za-z0-9_-]+)>', cmd):
                if match not in found:
                    found.append(match)
        return found

    def _apply_variables(self, text: str) -> str:
        if not text:
            return text
        for var_name, var_val in self.session_variables.items():
            text = text.replace(f"<{var_name}>", var_val)
        return text

    def _configure_step_variables(self, step: Dict[str, Any]):
        raw_cmds = step.get("commands", {}).get(self.vendor, [])
        cmds = self._flatten_commands(raw_cmds)
        step_placeholders = self._get_placeholders(cmds)
        if not step_placeholders:
            display.print_alert("No hay variables identificadas en los comandos de este paso.")
            display.pause()
            return

        print("\n=== Configurar Variables ===")
        print("Esta opción le permite definir valores reales para los marcadores en los comandos")
        print("(como <peer>, <interface>) para que pueda copiarlos y pegarlos directamente.")
        confirm = display.prompt_choice("¿Desea configurar las variables ahora? (s/n) [s]: ").strip().lower()
        if confirm not in ("", "s", "si", "sí", "y", "yes"):
            return

        for ph in step_placeholders:
            current_val = self.session_variables.get(ph, "")
            prompt_str = f"Ingrese valor para <{ph}> (actual: '{current_val}'): " if current_val else f"Ingrese valor para <{ph}>: "
            val = display.prompt_choice(prompt_str).strip()
            if val:
                self.session_variables[ph] = val
        display.print_alert("Variables actualizadas.")
        display.pause()

    def _get_terminal_prompt_host(self) -> str:
        if not self.vendor:
            return "Router#"
        vendor_prompts = {
            "juniper": "user@MX-Edge>",
            "cisco_iosxr": "RP/0/RSP0/CPU0:IOS-XR-PE#",
            "cisco_iosxe": "Cisco-PE-1#",
            "mikrotik": "[admin@MikroTik] >",
            "fortinet": "FGT-GW #",
            "linux": "root@linux-tshoot:~#",
            "zone": "<Huawei>",
            "adtran": "ADTRAN#",
            "ta5k": "TA5000>"
        }
        return vendor_prompts.get(self.vendor, "Router#")

    def _get_simulated_command_output(self, raw_cmd: str, simulated_outputs: Dict[str, Any]) -> str:
        clean_cmd = raw_cmd.lower().strip()
        tech_match = self.tech
        
        if simulated_outputs.get(tech_match) and simulated_outputs[tech_match].get(self.current_step) and simulated_outputs[tech_match][self.current_step].get(self.vendor):
            step_outputs = simulated_outputs[tech_match][self.current_step][self.vendor]
            for key_cmd, val_output in step_outputs.items():
                if clean_cmd in key_cmd.lower().strip() or key_cmd.lower().strip() in clean_cmd:
                    return val_output
                    

        # GPON OLT/ONT-specific fallback configurations and diagnostics
        is_gpon = (tech_match in ('fiber_ont', 'fiber_ont_config'))
        if is_gpon:
            if any(x in clean_cmd for x in ('show run', 'show config', 'current-configuration', 'saved-configuration', '/print')):
                if self.vendor == 'huawei':
                    if 'ont wan-config' in clean_cmd or 'wan-info' in clean_cmd:
                        return "ont wan-config 0/1/1 1 1 ip-index 1 profile-id 10"
                    if 'ont-sipprofile' in clean_cmd:
                        return "ont-sipprofile add 10 server 10.1.1.1"
                    if 'ont wlan-config' in clean_cmd:
                        return "ont wlan-config 0/1/1 1 1 wlan 1 enable ssid HOME-WIFI"
                    if 'service-port' in clean_cmd:
                        return (
                            "service-port 0 gpon 0/1/1 ont 1 gemport 1 multi-service user-vlan 10 tag-transform translate-and-add inner-vlan 100 inbound traffic-table name FTTH-100M outbound traffic-table name FTTH-100M\n"
                            "service-port 1 gpon 0/1/1 ont 1 gemport 2 multi-service user-vlan 20 tag-transform translate-and-add inner-vlan 200 inbound traffic-table name FTTH-IPTV outbound traffic-table name FTTH-IPTV"
                        )
                    if 'section gpon' in clean_cmd:
                        return (
                            "gpon port 0/1\n"
                            "  ont add 1 1 sn-auth \"ZTEGC1A2B3D4\" omci ont-lineprofile-id 10 ont-srvprofile-id 10 desc \"RESIDENTIAL-01\""
                        )
                    if 'ont-lineprofile' in clean_cmd:
                        return (
                            "ont-lineprofile gpon profile-id 10 profile-name \"FTTH-LINE\"\n"
                            "  tcont 1 dba-profile-id 10\n"
                            "  gem add 1 eth tcont 1\n"
                            "  gem add 2 eth tcont 1\n"
                            "  gem mapping 1 1 vlan 10\n"
                            "  gem mapping 2 2 vlan 20\n"
                            "  commit"
                        )
                    return (
                        "[Huawei MA5800 OLT GPON Configuration]\n"
                        "#\n"
                        "sysname MA5800-OLT\n"
                        "#\n"
                        "gpon port 0/1\n"
                        "  ont add 1 1 sn-auth \"ZTEGC1A2B3D4\" omci ont-lineprofile-id 10 ont-srvprofile-id 10 desc \"RESIDENTIAL-01\"\n"
                        "#\n"
                        "ont-lineprofile gpon profile-id 10 profile-name \"FTTH-LINE\"\n"
                        "  tcont 1 dba-profile-id 10\n"
                        "  gem add 1 eth tcont 1\n"
                        "  gem add 2 eth tcont 1\n"
                        "  gem mapping 1 1 vlan 10\n"
                        "  gem mapping 2 2 vlan 20\n"
                        "  commit\n"
                        "#\n"
                        "ont-srvprofile gpon profile-id 10 profile-name \"FTTH-SRV\"\n"
                        "  ont-port pots 1 eth 4 wlan 1\n"
                        "  port vlan eth 1 translation 10 user-vlan 10\n"
                        "  commit\n"
                        "#\n"
                        "service-port 0 gpon 0/1/1 ont 1 gemport 1 multi-service user-vlan 10 tag-transform translate-and-add inner-vlan 100 inbound traffic-table name FTTH-100M outbound traffic-table name FTTH-100M\n"
                        "service-port 1 gpon 0/1/1 ont 1 gemport 2 multi-service user-vlan 20 tag-transform translate-and-add inner-vlan 200 inbound traffic-table name FTTH-IPTV outbound traffic-table name FTTH-IPTV\n"
                        "#"
                    )
                elif self.vendor == 'zte':
                    if 'voice-profile' in clean_cmd or 'sip' in clean_cmd:
                        return "voice-profile SIP-PROF vlan 300"
                    if 'service-port' in clean_cmd:
                        return (
                            "service-port 1 vport 1 user-vlan 10 svlan 100\n"
                            "service-port 2 vport 2 user-vlan 20 svlan 200"
                        )
                    if 'interface gpon-onu' in clean_cmd:
                        return (
                            "interface gpon-onu_1/2/1:1\n"
                            "  name RESIDENTIAL-01\n"
                            "  tcont 1 name T-DATA dba-profile DBA-RESIDENTIAL\n"
                            "  gemport 1 name GEM-DATA tcont 1\n"
                            "  gemport 1 traffic-limit upstream 100M downstream 100M\n"
                            "  service-port 1 vport 1 user-vlan 10 svlan 100\n"
                            "  service-port 2 vport 2 user-vlan 20 svlan 200"
                        )
                    if 'interface gpon-olt' in clean_cmd:
                        return (
                            "interface gpon-olt_1/2/1\n"
                            "  onu 1 type ZTEG-F660 sn ZTEGC1A2B3D4"
                        )
                    return (
                        "[ZTE ZXAN OLT GPON Configuration]\n"
                        "!\n"
                        "hostname ZXAN-OLT\n"
                        "!\n"
                        "interface gpon-olt_1/2/1\n"
                        "  onu 1 type ZTEG-F660 sn ZTEGC1A2B3D4\n"
                        "!\n"
                        "interface gpon-onu_1/2/1:1\n"
                        "  name RESIDENTIAL-01\n"
                        "  tcont 1 name T-DATA dba-profile DBA-RESIDENTIAL\n"
                        "  gemport 1 name GEM-DATA tcont 1\n"
                        "  gemport 1 traffic-limit upstream 100M downstream 100M\n"
                        "  service-port 1 vport 1 user-vlan 10 svlan 100\n"
                        "  service-port 2 vport 2 user-vlan 20 svlan 200\n"
                        "!\n"
                        "pon-onu-mng gpon-onu_1/2/1:1\n"
                        "  service-port 1 gw-port eth_0/1 vlan 10\n"
                        "  wifi 1 mode bgn ssid HOME-WIFI security wpa2-psk password SecretPass123 channel 6\n"
                        "  voice-profile SIP-PROF vlan 300\n"
                        "  pots 1 sip-user 1001 password SecretPass123\n"
                        "!"
                    )
                elif self.vendor in ('zhone', 'zone'):
                    return (
                        "[Zhone/DASAN MXK OLT GPON Configuration]\n"
                        "!\n"
                        "gpononu set 1/4/1 1 profile Default sn ZTEGC1A2B3D4\n"
                        "port description add 1-1-4-1/gpononu \"RESIDENTIAL-01\"\n"
                        "new gpon-traffic-profile 1\n"
                        "!\n"
                        "bridge add 1-1-4-1/gpononu gem 301 gtp 1 downlink vlan 100 tagged eth 1\n"
                        "bridge add 1-1-4-1/gpononu gem 401 gtp 1 0/4 downlink vlan 999 tagged video eth 2\n"
                        "bridge add 1-1-4-1/gpononu gem 702 gtp 1 downlink vlan 300 tagged sip\n"
                        "!"
                    )
                elif self.vendor == 'adtran':
                    return (
                        "[ADTRAN OLT GPON Configuration]\n"
                        "!\n"
                        "gpon-olt 1\n"
                        "  remote-device 1 name \"RESIDENTIAL-01\" serial-number ZTEGC1A2B3D4\n"
                        "  remote-device 1 ont-profile \"default\"\n"
                        "!\n"
                        "bridge-group 100\n"
                        "  description \"Internet Data\"\n"
                        "  member vlan 100\n"
                        "  member remote-device 1 eth 1\n"
                        "!"
                    )

            if self.vendor == 'huawei':
                if 'autofind' in clean_cmd:
                    return (
                        "   ----------------------------------------------------------------------\n"
                        "   Number of newly found ONUs: 1\n"
                        "   ----------------------------------------------------------------------\n"
                        "   Interface ID      : GPON 0/1/1\n"
                        "   ONU ID            : 0\n"
                        "   Serial number     : ZTEGC1A2B3D4\n"
                        "   Discover time     : 2026-06-12 09:42:10\n"
                        "   ----------------------------------------------------------------------"
                    )
                if 'optical-info' in clean_cmd:
                    return (
                        "   -----------------------------------------------------------------------------\n"
                        "   ONU ID                         : 1\n"
                        "   Rx optical power(dBm)          : -19.45\n"
                        "   Tx optical power(dBm)          : 2.12\n"
                        "   OLT Rx ONT optical power(dBm)  : -20.15\n"
                        "   Laser behavior                 : normal\n"
                        "   Bias current(mA)               : 15.42\n"
                        "   Temperature(C)                 : 42.5\n"
                        "   Voltage(V)                     : 3.32\n"
                        "   -----------------------------------------------------------------------------"
                    )
                if any(x in clean_cmd for x in ('detail-info', 'detail', 'lastdowncause', 'version')):
                    return (
                        "   -----------------------------------------------------------------------------\n"
                        "   ONU ID                         : 1\n"
                        "   Distance(m)                    : 1420\n"
                        "   EqD(us)                        : 290150\n"
                        "   SN                             : ZTEGC1A2B3D4\n"
                        "   Hardware Version               : F660v8.0\n"
                        "   Software Version               : V8.0.10P1T1\n"
                        "   Last offline cause             : power-off\n"
                        "   Last offline time              : 2026-06-12 08:30:15\n"
                        "   -----------------------------------------------------------------------------"
                    )
                if 'wan-info' in clean_cmd or 'ipconfig' in clean_cmd:
                    return (
                        "   -----------------------------------------------------------------------------\n"
                        "   ONU ID                         : 1\n"
                        "   WAN Index                      : 1\n"
                        "   Service Type                   : Internet\n"
                        "   Connection Type                : Route\n"
                        "   Connection Status              : Connected\n"
                        "   IPv4 Address                   : 192.168.253.123\n"
                        "   Subnet Mask                    : 255.255.255.0\n"
                        "   Default Gateway                : 192.168.253.1"
                    )
                if 'pppoe' in clean_cmd:
                    return (
                        "   -----------------------------------------------------------------------------\n"
                        "   ONU ID                         : 1\n"
                        "   PPPoE Session State            : Established\n"
                        "   Local IP                       : 192.168.253.123\n"
                        "   Peer IP                        : 192.168.253.1\n"
                        "   Session ID                     : 1403\n"
                        "   -----------------------------------------------------------------------------"
                    )
                if 'sip' in clean_cmd or 'voice' in clean_cmd:
                    return (
                        "   -----------------------------------------------------------------------------\n"
                        "   ONU ID                         : 1\n"
                        "   POTS Port                      : 1\n"
                        "   SIP User                       : 1001\n"
                        "   SIP Server                     : 10.1.1.1\n"
                        "   Register Status                : Registered\n"
                        "   -----------------------------------------------------------------------------"
                    )
                if 'pots' in clean_cmd:
                    return (
                        "   -----------------------------------------------------------------------------\n"
                        "   ONU ID                         : 1\n"
                        "   POTS Port ID                   : 1\n"
                        "   Admin State                    : up\n"
                        "   Physical State                 : idle\n"
                        "   Service State                  : normal\n"
                        "   -----------------------------------------------------------------------------"
                    )
                if 'associated-station' in clean_cmd:
                    return (
                        "   -----------------------------------------------------------------------------\n"
                        "   Index  MAC Address        IP Address        RSSI(dBm)  Tx Rate(Mbps)\n"
                        "   -----------------------------------------------------------------------------\n"
                        "   1      98:ee:cb:dd:c7:63  192.168.1.15      -65        144\n"
                        "   2      fe:53:7a:cd:eb:8d  192.168.1.20      -72        72\n"
                        "   -----------------------------------------------------------------------------"
                    )
                if 'wlan' in clean_cmd:
                    return (
                        "   -----------------------------------------------------------------------------\n"
                        "   ONU ID                         : 1\n"
                        "   WLAN Index                     : 1\n"
                        "   SSID                           : HOME-WIFI\n"
                        "   State                          : Enabled\n"
                        "   Channel                        : 6\n"
                        "   -----------------------------------------------------------------------------"
                    )
                if 'alarm' in clean_cmd:
                    return (
                        "   -----------------------------------------------------------------------------\n"
                        "   Alarm ID  Alarm Name        Alarm Severity  Raise Time\n"
                        "   -----------------------------------------------------------------------------\n"
                        "   0x231001  Dying Gasp        Critical        2026-06-12 09:30:15\n"
                        "   0x231002  Loss of Signal    Critical        2026-06-12 09:30:16\n"
                        "   -----------------------------------------------------------------------------"
                    )
                if 'info' in clean_cmd:
                    return (
                        "   -----------------------------------------------------------------------------\n"
                        "   ONU ID                         : 1\n"
                        "   Name                           : RESIDENTIAL-01\n"
                        "   Admin State                    : up\n"
                        "   Run State                      : online\n"
                        "   Config State                   : active\n"
                        "   Match State                    : match\n"
                        "   Control State                  : active\n"
                        "   Serial number                  : ZTEGC1A2B3D4\n"
                        "   Description                    : RESIDENTIAL-01\n"
                        "   Last offline cause             : power-off\n"
                        "   Last offline time              : 2026-06-12 08:30:15\n"
                        "   -----------------------------------------------------------------------------"
                    )
                if 'vlan' in clean_cmd:
                    return (
                        "   VLAN ID: 100\n"
                        "   VLAN Type: Smart\n"
                        "   VLAN Attribute: Common\n"
                        "   VLAN Description: GPON-DATA-VLAN\n"
                        "   VLAN State: Active"
                    )
                if 'mac-address' in clean_cmd or 'macaddress' in clean_cmd:
                    return (
                        "   -----------------------------------------------------------------------------\n"
                        "   VLAN ID  MAC Address     Type      Source Port\n"
                        "   -----------------------------------------------------------------------------\n"
                        "   100      98ee-cbdd-c763  Dynamic   gpon 0/1/1\n"
                        "   -----------------------------------------------------------------------------"
                    )
            elif self.vendor == 'zte':
                if 'uncfg' in clean_cmd:
                    return (
                        "   OnuIndex                 Sn                  State\n"
                        "   -------------------------------------------------------\n"
                        "   gpon-onu_1/2/1:1         ZTEGC1A2B3D4        unconfigured"
                    )
                if 'optical-info' in clean_cmd:
                    return (
                        "   ONU Optical Information:\n"
                        "   ONU Index: gpon-onu_1/2/1:1\n"
                        "   Tx Power: 2.12 (dBm)\n"
                        "   Rx Power (Received by OLT): -20.15 (dBm)\n"
                        "   Rx Power (Received by ONU): -19.45 (dBm)\n"
                        "   OLT Rx Power Threshold: -28.00 / -8.00 (dBm)\n"
                        "   Work State: Normal"
                    )
                if any(x in clean_cmd for x in ('detail-info', 'base-info', 'detail', 'lastdowncause')):
                    return (
                        "   ONU Index: gpon-onu_1/2/1:1\n"
                        "   Type: ZTEG-F660\n"
                        "   Serial Number: ZTEGC1A2B3D4\n"
                        "   Ranging Distance: 1420 (m)\n"
                        "   Equalization Delay: 290150 (us)\n"
                        "   Last Offline Cause: dying-gasp\n"
                        "   Last Offline Time: 2026-06-12 08:30:15"
                    )
                if 'service-port' in clean_cmd:
                    return (
                        "   ServicePortID  OnuIndex          VportID  UserVlan  Svlan  Cvlan\n"
                        "   ------------------------------------------------------------------\n"
                        "   1              gpon-onu_1/2/1:1  1        10        100    10\n"
                        "   2              gpon-onu_1/2/1:1  2        20        200    20"
                    )
                if 'macaddress' in clean_cmd or 'mac-address' in clean_cmd:
                    return (
                        "   Mac Address      VlanId   Type     Port\n"
                        "   ------------------------------------------------------------------\n"
                        "   98ee.cbdd.c763   100      Dynamic  gpon-onu_1/2/1:1"
                    )
                if 'sip status' in clean_cmd or 'sip register-status' in clean_cmd or 'sip' in clean_cmd:
                    return (
                        "   SIP Register Status:\n"
                        "   User Name: 1001\n"
                        "   Registrar Server IP: 10.1.1.1\n"
                        "   Register Port: 5060\n"
                        "   Register State: Register Success"
                    )
                if 'voice port summary' in clean_cmd:
                    return (
                        "   Port Index  Port Type  State     Hook State  Register State\n"
                        "   ------------------------------------------------------------------\n"
                        "   POTS 1      SIP        Idle      On Hook     Registered"
                    )
                if 'voice call active' in clean_cmd:
                    return "   No active VoIP calls in progress."
                if 'remote-onu wifi' in clean_cmd or ('remote-onu' in clean_cmd and 'wifi' in clean_cmd):
                    return (
                        "   Wifi Configuration:\n"
                        "   Wifi Mode: 802.11b/g/n\n"
                        "   SSID: HOME-WIFI\n"
                        "   SSID Index: 1\n"
                        "   Authentication: WPA2-PSK\n"
                        "   Encryption: AES\n"
                        "   Channel: 6\n"
                        "   State: Enabled"
                    )
                if 'associated-station' in clean_cmd:
                    return (
                        "   Associated Stations:\n"
                        "   SSID 1:\n"
                        "     MAC: 98:ee:cb:dd:c7:63  IP: 192.168.1.15  RSSI: -65 dBm\n"
                        "     MAC: fe:53:7a:cd:eb:8d  IP: 192.168.1.20  RSSI: -72 dBm"
                    )
                if 'wlan-statistics' in clean_cmd:
                    return (
                        "   SSID 1 Statistics:\n"
                        "   Packets Rx: 145920    Packets Tx: 298104\n"
                        "   Bytes Rx: 1294801     Bytes Tx: 4920148\n"
                        "   Errors Rx: 0          Errors Tx: 0"
                    )
                if 'state' in clean_cmd:
                    return (
                        "   OnuIndex                 AdminState   RegState     PhaseState\n"
                        "   ---------------------------------------------------------------------\n"
                        "   gpon-onu_1/2/1:1         enable       active       O5(operation)"
                    )
                if 'vlan' in clean_cmd:
                    return (
                        "   ONU Index: gpon-onu_1/2/1:1\n"
                        "   Port Type: Ethernet\n"
                        "   Port ID: 1\n"
                        "   User VLAN: 10\n"
                        "   Service VLAN: 100"
                    )
                if 'logging' in clean_cmd or 'log' in clean_cmd:
                    return (
                        "   2026-06-12 09:00:10 GPON-ONU-UP: ONU 1/2/RegID:1 registered\n"
                        "   2026-06-12 09:00:15 GPON-ONU-O5: ONU 1/2/RegID:1 phase operation completed successfully"
                    )
            elif self.vendor in ('zhone', 'zone'):
                if 'bridge show onu' in clean_cmd or 'bridge show' in clean_cmd:
                    return (
                        "   Bridge Interface Info for ONU 1/4/1:\n"
                        "   BridgeName                        GTP   VLAN  SLAN  Status\n"
                        "   --------------------------------------------------------------\n"
                        "   1-1-4-301-gponport-100/bridge     1     100   301   Active\n"
                        "   1-1-4-702-gponport-300/bridge     1     300   702   Active"
                    )
                if 'bridge-interface-record' in clean_cmd:
                    return (
                        "   Bridge Interface Record 1-1-4-301-gponport-100/bridge:\n"
                        "     State: enabled\n"
                        "     Uplink Port: eth 1\n"
                        "     Learned MACs: 1 (98:ee:cb:dd:c7:63)"
                    )
                if 'gponolt show bw' in clean_cmd:
                    return (
                        "   GPON OLT Bandwidth Info for Port 1/4:\n"
                        "   Total Allocated Upstream: 120 Mbps\n"
                        "   Dynamic DBA Range: 10 Mbps - 1000 Mbps\n"
                        "   Active GEM Ports: 3"
                    )
                if 'onu show' in clean_cmd:
                    return (
                        "   ONU Index  Status      SN            Profile  AdminState\n"
                        "   ----------------------------------------------------------\n"
                        "   1/4/1      Registered  ZTEGC1A2B3D4  Default  Up"
                    )
                if 'gpon-olt-config' in clean_cmd:
                    return (
                        "   gpon-olt-config for 1-1-4-0/gponolt:\n"
                        "     Status: up\n"
                        "     Laser: enabled\n"
                        "     ONT Count: 1"
                    )
                if 'gpon-olt-onu-config' in clean_cmd:
                    return (
                        "   gpon-onu-config for 1-1-4-1/gpononu:\n"
                        "     ONU-ID: 1\n"
                        "     Serial: ZTEGC1A2B3D4\n"
                        "     Profile: Default\n"
                        "     Status: operational"
                    )
                if 'cpe rg show' in clean_cmd:
                    return (
                        "   CPE Residential Gateway 1/4/1:\n"
                        "     WAN: PPPoE (Connected, IP: 192.168.253.123)\n"
                        "     LAN: 192.168.1.1"
                    )
                if 'cpe voip show' in clean_cmd:
                    return (
                        "   CPE VoIP status for 1/4/1:\n"
                        "     State: Registered\n"
                        "     Line 1: Idle (+541123456)"
                    )
                if 'port show alarm' in clean_cmd or 'alarm' in clean_cmd:
                    return (
                        "   Alarms active on interface 1-1-4-0/gponolt:\n"
                        "   No active critical alarms on port 1/4."
                    )
                if 'port show' in clean_cmd:
                    return (
                        "   Port 1-1-4-1/gpononu details:\n"
                        "     State: enabled\n"
                        "     Description: \"RESIDENTIAL-01\""
                    )
            elif self.vendor == 'adtran':
                if 'remote-devices' in clean_cmd:
                    return (
                        "   OntId   Name             State    SN            Distance  RxPower\n"
                        "   --------------------------------------------------------------------\n"
                        "   1       RESIDENTIAL-01   Active   ZTEGC1A2B3D4  1420m     -19.45 dBm"
                    )
                if 'alarm log' in clean_cmd:
                    return (
                        "   Active alarms:\n"
                        "   No alarm events registered in the past 24 hours."
                    )
                if 'bridge-group' in clean_cmd:
                    return (
                        "   Bridge-group details:\n"
                        "     VLAN: 100\n"
                        "     Status: Up\n"
                        "     Learned MACs: 98:ee:cb:dd:c7:63"
                    )

            if clean_cmd.startswith("show ") or clean_cmd.startswith("display ") or clean_cmd.startswith("get "):
                return (
                    f"GPON OLT Diagnostic Output for command: {raw_cmd}\n"
                    f"-----------------------------------------------------------------------------\n"
                    f"Target Device   : GPON 0/1/1 (or equivalent OLT port)\n"
                    f"ONU ID          : 1\n"
                    f"Serial Number   : ZTEGC1A2B3D4\n"
                    f"Administrative  : up (enabled)\n"
                    f"Operational     : online (Phase O5 - operational)\n"
                    f"Optical Power   : RX (OLT) -20.15 dBm, RX (ONU) -19.45 dBm (within safe limits)\n"
                    f"Active Alarms   : none detected\n"
                    f"-----------------------------------------------------------------------------"
                )
        
        # Fallbacks
        if clean_cmd.startswith("ping") or "ping " in clean_cmd:
            target_ip = self.session_variables.get("ip-privada") or self.session_variables.get("peer-ip") or "8.8.8.8"
            return (
                f"PING {target_ip} (8.8.8.8) 56(84) bytes of data.\n"
                f"64 bytes from 8.8.8.8: icmp_seq=1 ttl=56 time=12.4 ms\n"
                f"64 bytes from 8.8.8.8: icmp_seq=2 ttl=56 time=11.8 ms\n"
                f"64 bytes from 8.8.8.8: icmp_seq=3 ttl=56 time=14.1 ms\n"
                f"64 bytes from 8.8.8.8: icmp_seq=4 ttl=56 time=12.2 ms\n"
                f"64 bytes from 8.8.8.8: icmp_seq=5 ttl=56 time=11.9 ms\n\n"
                f"--- 8.8.8.8 ping statistics ---\n"
                f"5 packets transmitted, 5 received, 0% packet loss, time 4006ms\n"
                f"rtt min/avg/max/mdev = 11.821/12.484/14.112/0.812 ms"
            )
        if "traceroute" in clean_cmd or "trace " in clean_cmd:
            target_ip = self.session_variables.get("peer-ip") or "8.8.8.8"
            return (
                f"traceroute to {target_ip} (8.8.8.8), 30 hops max, 60 byte packets\n"
                f" 1  192.168.1.1 (192.168.1.1)  0.841 ms  0.712 ms  0.688 ms\n"
                f" 2  10.0.12.2 (10.0.12.2)  4.112 ms  4.022 ms  3.988 ms\n"
                f" 3  203.0.113.1 (203.0.113.1)  8.214 ms  8.115 ms  8.092 ms\n"
                f" 4  8.8.8.8 (8.8.8.8)  12.412 ms  12.115 ms  12.022 ms"
            )
        if "debug " in clean_cmd or "diagnose debug" in clean_cmd:
            return (
                "Debugging activado. Monitoreando eventos de red...\n"
                "[16:40:02.102] EVT: Matching criteria ok.\n"
                "[16:40:04.214] EVT: Process queue scheduling.\n"
                "[16:40:07.412] EVT: Diagnostic frame trace finished."
            )
        if "show run" in clean_cmd or "show config" in clean_cmd or "/print" in clean_cmd:
            peer_ip = self.session_variables.get("peer") or "10.0.0.2"
            return (
                f"! Configuration block extracted from active context\n"
                f"!\n"
                f"protocols {{\n"
                f"    bgp {{\n"
                f"        local-as 65001;\n"
                f"        group external-peers {{\n"
                f"            peer-as 65002;\n"
                f"            neighbor {peer_ip};\n"
                f"        }}\n"
                f"    }}\n"
                f"}}"
            )
            
        # Config fallbacks
        if clean_cmd == "configure terminal" or clean_cmd == "configure" or clean_cmd == "system-view" or clean_cmd.startswith("config "):
            confs = {
                "juniper": "Entering configuration mode\n[edit]",
                "cisco_iosxr": "Entering configuration mode\nRP/0/RSP0/CPU0:IOS-XR-PE(config)#",
                "cisco_iosxe": "Entering configuration mode\nCisco-PE-1(config)#",
                "mikrotik": "Entering configuration mode...",
                "fortinet": "Entering configuration mode...",
                "zone": "Entering configuration mode\n[Huawei]",
                "adtran": "Entering configuration mode\nADTRAN(config)#",
                "ta5k": "Entering configuration mode\nTA5000(config)#"
            }
            return confs.get(self.vendor, "Entering configuration mode...")
            
        if clean_cmd == "commit" or clean_cmd == "write memory" or clean_cmd == "save" or clean_cmd == "end":
            commits = {
                "juniper": "commit complete.",
                "cisco_iosxr": "Building configuration...\n[OK]",
                "cisco_iosxe": "Building configuration...\n[OK]",
                "mikrotik": "(Config autosaved)",
                "fortinet": "(Changes applied)",
                "zone": "Information: Save configuration successfully.",
                "adtran": "Copying running-config to startup-config... [OK]",
                "ta5k": "Copying running-config to startup-config... [OK]"
            }
            return commits.get(self.vendor, "[OK]")
            
        if clean_cmd.startswith("set ") or clean_cmd.startswith("no ") or clean_cmd.startswith("ip nat ") or clean_cmd.startswith("router ") or clean_cmd.startswith("edit ") or clean_cmd.startswith("/ip firewall "):
            prompts = {
                "juniper": "[edit]",
                "cisco_iosxr": "RP/0/RSP0/CPU0:IOS-XR-PE(config-router)#",
                "cisco_iosxe": "Cisco-PE-1(config-router)#",
                "mikrotik": "(applied)",
                "fortinet": "(applied)",
                "zone": "[Huawei]",
                "adtran": "(config-router)#",
                "ta5k": "(config-router)#"
            }
            return prompts.get(self.vendor, "(applied)")

        return "Diagnostic executed successfully.\nStatus: Active/Operational\nNo active anomalies detected for this scope."

    def _run_command_simulation(self, step: Dict[str, Any]):
        raw_cmds = step.get("commands", {}).get(self.vendor, [])
        cmds = self._flatten_commands(raw_cmds)
        if not cmds:
            display.print_alert("No hay comandos para simular en este paso.")
            display.pause()
            return

        import time
        from data.simulated_outputs import SIMULATED_OUTPUTS

        prompt_host = self._get_terminal_prompt_host()
        applied_cmds = [self._apply_variables(c) for c in cmds]

        display.clear()
        display.print_banner(confidence=self.session_confidence)
        print(f"\n=== 💻 Modo Consola Interactiva ({VendorMap.get(self.vendor, self.vendor)}) ===")
        print("Escriba un comando sugerido para ejecutarlo, o use los comandos especiales:")
        print("  - 'help': Lista de comandos sugeridos en este paso.")
        print("  - 'run-all': Ejecuta automáticamente todos los comandos sugeridos en secuencia.")
        print("  - 'exit': Regresa al flujo de diagnóstico.")
        print("  - 'clear': Limpia la pantalla de la consola.\n")

        while True:
            # Pedir comando al usuario
            try:
                user_cmd = input(f"{prompt_host} ").strip()
            except (KeyboardInterrupt, EOFError):
                break
                
            if not user_cmd:
                continue

            if user_cmd.lower() == 'exit':
                break
            elif user_cmd.lower() == 'clear':
                display.clear()
                display.print_banner(confidence=self.session_confidence)
                print(f"\n=== 💻 Modo Consola Interactiva ({VendorMap.get(self.vendor, self.vendor)}) ===")
                continue
            elif user_cmd.lower() == 'help':
                print("\nComandos sugeridos para el diagnóstico en este paso:")
                for c in applied_cmds:
                    print(f"  • {c}")
                print("Otros comandos especiales:")
                print("  • run-all  (Ejecuta la secuencia sugerida)")
                print("  • clear    (Limpia pantalla)")
                print("  • exit     (Salir)\n")
                continue
            elif user_cmd.lower() == 'run-all':
                print("Ejecutando secuencia automatizada...")
                for raw_cmd in cmds:
                    cmd = self._apply_variables(raw_cmd)
                    print(f"\n{prompt_host} {cmd}")
                    print("  [Ejecutando diagnóstico...]")
                    time.sleep(0.3)
                    output_text = self._get_simulated_command_output(raw_cmd, SIMULATED_OUTPUTS)
                    applied_output = self._apply_variables(output_text)
                    if display.RICH_AVAILABLE:
                        from rich.panel import Panel
                        display._console.print(Panel(applied_output, style="green", border_style="dim"))
                    else:
                        print(applied_output)
                    time.sleep(0.1)
                continue

            # Buscar si el comando ingresado coincide con alguno sugerido
            matched_raw_cmd = None
            for raw_cmd in cmds:
                applied = self._apply_variables(raw_cmd)
                if user_cmd.lower() == applied.lower() or user_cmd.lower() in applied.lower() or applied.lower() in user_cmd.lower():
                    matched_raw_cmd = raw_cmd
                    break

            if matched_raw_cmd:
                print("  [Ejecutando diagnóstico...]")
                time.sleep(0.3)
                output_text = self._get_simulated_command_output(matched_raw_cmd, SIMULATED_OUTPUTS)
                applied_output = self._apply_variables(output_text)
                if display.RICH_AVAILABLE:
                    from rich.panel import Panel
                    display._console.print(Panel(applied_output, style="green", border_style="dim"))
                else:
                    print(applied_output)
            else:
                # Comandos de red comunes
                cmd_low = user_cmd.lower()
                time.sleep(0.1)
                if 'ping' in cmd_low:
                    print("Sending 5, 100-byte ICMP Echos, timeout is 2 seconds:")
                    print("!!!!!\nSuccess rate is 100 percent (5/5), round-trip min/avg/max = 1/3/8 ms")
                elif 'traceroute' in cmd_low or 'trace' in cmd_low:
                    print("Type escape sequence to abort. Tracing the route...")
                    print(" 1  10.0.0.1  2 msec  1 msec  1 msec")
                    print(" 2  10.0.0.2  4 msec  3 msec  3 msec")
                    print(" 3  10.100.1.1  12 msec  10 msec  11 msec")
                elif 'show version' in cmd_low or 'show ver' in cmd_low or 'version' in cmd_low:
                    print(f"Software Version: Simulated CLI OS v1.0\nUptime: 23 weeks, 4 days\nPlatform: {self.vendor.upper()} virtual image.")
                elif 'show ip interface brief' in cmd_low or 'show ip int brief' in cmd_low or 'show interfaces brief' in cmd_low:
                    print("Interface              IP-Address      OK? Method Status                Protocol")
                    print("GigabitEthernet0/0     10.1.1.1        YES manual up                    up")
                    print("GigabitEthernet0/1     10.2.1.1        YES manual up                    up")
                    print("Loopback0              10.100.1.1      YES manual up                    up")
                else:
                    print(f"% Invalid input detected at '^' marker.")
                    print(f"Comando desconocido o no disponible para simulación en este paso.")
                    print(f"Escriba 'help' para ver los comandos de diagnóstico sugeridos.")

    def _add_step_note(self, step: Dict[str, Any]):
        print("\n=== Añadir Nota/Hallazgo ===")
        print("Esta opción le permite registrar anotaciones y hallazgos sobre este paso")
        print("para guardarlos en la bitácora y exportar un reporte final en Markdown.")
        confirm = display.prompt_choice("¿Desea añadir una nota ahora? (s/n) [s]: ").strip().lower()
        if confirm not in ("", "s", "si", "sí", "y", "yes"):
            return

        note_content = display.prompt_choice("Escriba su anotación para este paso: ").strip()
        if note_content:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Buscar si ya hay nota en este paso para anexar
            existing = None
            for n in self.notes_log:
                if n["tech"] == self.tech and n["step"] == self.current_step:
                    existing = n
                    break
            if existing:
                existing["note"] += f"\n[{timestamp}] {note_content}"
            else:
                step_title = step.get("title", self.current_step)
                self.notes_log.append({
                    "tech": self.tech,
                    "tech_name": KB[self.tech].get("name", self.tech),
                    "step": self.current_step,
                    "title": step_title,
                    "note": note_content,
                    "timestamp": timestamp
                })
            display.print_alert("Nota guardada con éxito.")
            display.pause()

    def _register_evidence(self, step: Dict[str, Any]):
        print("\n=== Registro de Evidencia Científica ===")
        print(f"Hipótesis actual: {step.get('hypothesis', 'N/A')}")
        print("\nSeleccione el resultado de su verificación:")
        print("  [1] La evidencia CONFIRMA la hipótesis (la falla se explica por esta causa)")
        print("  [2] La evidencia INVALIDA la hipótesis (descartar y reformular)")
        print("  [3] La evidencia es INCONCLUSA (se necesitan más datos)")
        print("  [4] Cancelar")
        val = display.prompt_choice("\nSeleccione opción: ").strip()
        if val not in ("1", "2", "3"):
            return

        outcome_map = {"1": "CONFIRMA", "2": "INVALIDA", "3": "INCONCLUSA"}
        outcome = outcome_map[val]

        detail = display.prompt_choice("Describa la evidencia observada (comando/output/clave): ").strip()

        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        step_title = step.get("title", self.current_step)
        note_text = f"[EVIDENCIA {outcome}] {detail}"

        existing = None
        for n in self.notes_log:
            if n["tech"] == self.tech and n["step"] == self.current_step:
                existing = n
                break
        if existing:
            existing["note"] += f"\n[{timestamp}] {note_text}"
        else:
            self.notes_log.append({
                "tech": self.tech,
                "tech_name": KB[self.tech].get("name", self.tech),
                "step": self.current_step,
                "title": step_title,
                "note": note_text,
                "timestamp": timestamp
            })
        # Actualizar score de confianza de sesión
        if outcome == "CONFIRMA":
            self.session_confidence = min(100, self.session_confidence + 15)
            self.invalidated_streak = 0
        elif outcome == "INVALIDA":
            self.session_confidence = max(0, self.session_confidence - 10)
            self.invalidated_streak += 1
        elif outcome == "INCONCLUSA":
            self.session_confidence = max(0, self.session_confidence - 5)

        display.print_alert(f"Evidencia registrada: {outcome}. Continúe con el siguiente paso o reformule la hipótesis.")
        print(f"  [Score de Confianza de Sesión: {self.session_confidence}%]")

        # Alerta contextual si hay patrón de múltiples invalidaciones
        if self.invalidated_streak >= 3 and self.session_confidence < 40:
            display.print_alert(
                "⚠️ PATRÓN DETECTADO: Ha invalidado múltiples hipótesis consecutivas sin encontrar la causa raíz. "
                "Sugerencias: (1) El síntoma podría ser efecto de otra causa no explorada, "
                "(2) Verificar supuestos de diseño de red (MTU global, consistent addressing), "
                "(3) Considerar escalar a revisión de arquitectura."
            )

        # Marcar este paso como con evidencia registrada (para modos estricto/semi-estricto)
        if self.tech and self.current_step:
            self.evidence_registered.add((self.tech, self.current_step))
        display.pause()

    def _run_rca_wizard(self, step: Dict[str, Any]):
        display.clear()
        display.print_banner(confidence=self.session_confidence)
        print("\n=== 🕵️  Asistente de Análisis de Causa Raíz (RCA - 5 Porqués) ===")
        print("Esta metodología estructurada le permite aislar la causa raíz de una falla")
        print("y definir una solución definitiva, evitando acciones temporales recurrentes.\n")
        
        confirm = display.prompt_choice("¿Desea iniciar el análisis de los 5 Porqués para este caso? (s/n) [s]: ").strip().lower()
        if confirm not in ("", "s", "si", "sí", "y", "yes"):
            return

        sintoma = display.prompt_choice("\n1. Síntoma o problema inicial observados (ej: Pérdida de paquetes en L3VPN): ").strip()
        if not sintoma:
            sintoma = step.get("title", "Falla detectada en " + self.tech)

        print("\nAhora responderemos consecutivamente a la pregunta '¿Por qué?' para profundizar:")
        porques = []
        for i in range(1, 6):
            if i == 1:
                prompt = f"   ¿Por qué ocurrió '{sintoma}'?: "
            else:
                prompt = f"   ¿Por qué ocurrió '{porques[-1]}'? (ENTER para finalizar antes): "
            ans = display.prompt_choice(prompt).strip()
            if not ans:
                if i == 1:
                    print("   Debe ingresar al menos el primer porqué.")
                    ans = display.prompt_choice(prompt).strip()
                    if not ans:
                        break
                else:
                    break
            porques.append(ans)

        causa_raiz = display.prompt_choice("\n2. Causa Raíz lógica identificada: ").strip()
        if not causa_raiz and porques:
            causa_raiz = porques[-1]

        solucion = display.prompt_choice("3. Solución Definitiva / Plan de Acción (para evitar recurrencia): ").strip()

        # Construir contenido estructurado en la bitácora
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        rca_block = []
        rca_block.append("=== ANÁLISIS DE CAUSA RAÍZ (RCA - 5 PORQUÉS) ===")
        rca_block.append(f"• Síntoma Inicial: {sintoma}")
        for idx, pq in enumerate(porques, 1):
            rca_block.append(f"  └─ ¿Por qué {idx}?: {pq}")
        rca_block.append(f"• Causa Raíz lógica: {causa_raiz}")
        rca_block.append(f"• Solución Definitiva: {solucion}")
        
        rca_note_text = "\n".join(rca_block)
        
        # Buscar si ya hay un bloque de RCA registrado en este paso para anexar/reemplazar
        existing = None
        for n in self.notes_log:
            if n["tech"] == self.tech and n["step"] == self.current_step and "5 PORQUÉS" in n["note"]:
                existing = n
                break
        if existing:
            existing["note"] += f"\n\n[{timestamp}]\n{rca_note_text}"
        else:
            self.notes_log.append({
                "tech": self.tech,
                "tech_name": KB[self.tech].get("name", self.tech),
                "step": self.current_step,
                "title": f"RCA — {step.get('title', self.current_step)}",
                "note": rca_note_text,
                "timestamp": timestamp
            })
            
        display.print_alert("Análisis de Causa Raíz (RCA) guardado con éxito en la bitácora.")
        display.pause()

    def _view_session_notes(self):
        display.clear()
        display.print_banner(confidence=self.session_confidence)
        print("\n=== Bitácora de la Sesión de Troubleshooting ===\n")
        if not self.notes_log:
            print("  No hay notas registradas en esta sesión.")
        else:
            for i, n in enumerate(self.notes_log, 1):
                print(f"  [{i}] {n['tech_name']} -> {n['title']}")
                print(f"      Nota: {n['note']}")
                print(f"      (Guardado: {n['timestamp']})\n")
        display.pause()

    def _run_golden_comparison(self, step: Dict[str, Any]):
        raw_cmds = step.get("commands", {}).get(self.vendor, [])
        cmds = self._flatten_commands(raw_cmds)
        if not cmds:
            display.print_alert("No hay comandos sugeridos en este paso para comparar.")
            display.pause()
            return

        display.clear()
        display.print_banner(confidence=self.session_confidence)
        print("\n=== ⚖️  Comparación con Golden Config (Línea Base) ===")
        print("A continuación se muestra la comparación entre la salida con falla (Actual)")
        print("y la configuración de referencia esperada (Línea Base) para los comandos del paso:\n")

        from data.simulated_outputs import SIMULATED_OUTPUTS
        from data.golden_baseline import generate_golden_output

        for raw_cmd in cmds:
            cmd = self._apply_variables(raw_cmd)
            current_output = self._get_simulated_command_output(raw_cmd, SIMULATED_OUTPUTS)
            applied_current = self._apply_variables(current_output)
            applied_golden = generate_golden_output(raw_cmd, applied_current)
            
            display.print_golden_comparison(cmd, applied_current, applied_golden)
            
        display.pause()

    def _run_view_rfcs(self):
        from data.change_tickets import get_tickets_for_tech
        tickets = get_tickets_for_tech(self.tech)
        
        display.clear()
        display.print_banner(confidence=self.session_confidence)
        print("\n=== 🎫  Historial de Cambios Recientes (RFC Log) ===")
        print("De acuerdo con la 'Regla del Cambio Reciente', el 80% de las fallas se deben a")
        print("un cambio en las últimas 24 horas. Revise las siguientes órdenes de cambio:\n")
        
        display.print_change_tickets(tickets)
        display.pause()

    def _run_global_search(self):
        while True:
            display.clear()
            display.print_banner(confidence=self.session_confidence)
            print("\n=== Búsqueda Global ===")
            query = display.prompt_choice("Ingrese término a buscar (o ENTER para volver): ").strip()
            if not query:
                break

            results = []
            query_lower = query.lower()

            for tech_key, tech_data in KB.items():
                tech_name = tech_data.get("name", tech_key)

                # Buscar en el nombre y descripción de la tecnología
                if query_lower in tech_name.lower() or query_lower in tech_data.get("description", "").lower():
                    results.append({
                        "type": "tech",
                        "tech_key": tech_key,
                        "tech_name": tech_name,
                        "label": f"Tecnología: {tech_name}"
                    })

                steps = tech_data.get("steps", {})
                for step_key, step_data in steps.items():
                    step_title = step_data.get("title", "")
                    step_body = step_data.get("body", "")

                    match_found = False
                    match_reason = []

                    if query_lower in step_title.lower():
                        match_found = True
                        match_reason.append("título")
                    if query_lower in step_body.lower():
                        match_found = True
                        match_reason.append("explicación")

                    cmds_match = []
                    for vendor, cmd_block in step_data.get("commands", {}).items():
                        cmds = self._flatten_commands(cmd_block)
                        for cmd in cmds:
                            if query_lower in cmd.lower():
                                cmds_match.append(vendor)
                                break
                    if cmds_match:
                        match_found = True
                        match_reason.append(f"comandos ({', '.join(cmds_match)})")

                    if query_lower in step_data.get("expected", "").lower():
                        match_found = True
                        match_reason.append("resultado esperado")

                    if match_found:
                        reason_str = ", ".join(match_reason)
                        results.append({
                            "type": "step",
                            "tech_key": tech_key,
                            "tech_name": tech_name,
                            "step_key": step_key,
                            "step_title": step_title,
                            "label": f"Paso: {tech_name} -> {step_title} (coincidencia en {reason_str})"
                        })

            if not results:
                display.print_alert("No se encontraron coincidencias.")
                display.pause()
                continue

            while True:
                display.clear()
                display.print_banner(confidence=self.session_confidence)
                print(f"\nResultados para: '{query}' ({len(results)} coincidencias):\n")
                for i, res in enumerate(results, 1):
                    print(f"  [{i}] {res['label']}")
                print(f"  [{len(results) + 1}] Nueva búsqueda")
                print(f"  [{len(results) + 2}] Volver al menú principal")

                val = display.prompt_choice("\nSeleccione una opción para ir directamente: ")
                try:
                    idx = int(val) - 1
                    if idx == len(results):
                        break
                    if idx == len(results) + 1:
                        return
                    if 0 <= idx < len(results):
                        res = results[idx]
                        self.tech = res["tech_key"]
                        self._vendor_select()
                        if self.vendor:
                            self._tier_select()
                            if self.tier:
                                if res["type"] == "tech":
                                    self._run_technology_flow()
                                else:
                                    self._run_technology_flow(start_step=res["step_key"])
                        self.tech = None
                        self.vendor = None
                        self.tier = 1
                        self.current_step = None
                        self.history.clear()
                        return
                except ValueError:
                    pass
                display.print_alert("Opción inválida.")

    def _export_report(self):
        if not self.notes_log:
            return

        display.clear()
        display.print_banner(confidence=self.session_confidence)
        print("\n=== Exportación de Reporte ===")
        val = display.prompt_choice("¿Desea exportar la bitácora de esta sesión a un archivo Markdown? (s/n) [s]: ").strip().lower()
        if val in ("", "s", "si", "yes", "y"):
            default_filename = "reporte_tshoot.md"
            filename = display.prompt_choice(f"Nombre del archivo [{default_filename}]: ").strip()
            if not filename:
                filename = default_filename

            try:
                filepath = Path(filename).resolve()
                md_content = []
                md_content.append("# Reporte de Diagnóstico y Troubleshooting de Redes")
                import datetime
                md_content.append(f"**Fecha y Hora:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                md_content.append(f"**Nivel de Diagnóstico:** Tier {self.tier}")
                if self.vendor:
                    md_content.append(f"**Vendor Principal:** {VendorMap.get(self.vendor, self.vendor)}")

                if self.session_variables:
                    md_content.append("\n## Variables de Comandos Utilizadas")
                    for k, v in self.session_variables.items():
                        md_content.append(f"- **`<{k}>`**: `{v}`")

                md_content.append("\n## Bitácora de Hallazgos y Notas")
                for n in self.notes_log:
                    md_content.append(f"\n### {n['tech_name']} — {n['title']}")
                    md_content.append(f"- **Fecha/Hora:** {n['timestamp']}")
                    if "5 PORQUÉS" in n['note']:
                        md_content.append(f"- **Tipo:** Análisis de Causa Raíz (RCA)")
                        md_content.append(f"- **Contenido:**")
                        for line in n['note'].split("\n"):
                            md_content.append(f"  > {line}")
                    else:
                        md_content.append(f"- **Notas registradas:**")
                        for line in n['note'].split("\n"):
                            md_content.append(f"  {line}")

                filepath.write_text("\n".join(md_content), encoding="utf-8")
                display.print_alert(f"Reporte exportado con éxito a: {filepath}")

                # Generar adicionalmente el Runbook de Remediación consolidado
                fix_lines = []
                for n in self.notes_log:
                    note = n.get('note', '')
                    if 'Comandos de reparación sugeridos:' in note or '$ ' in note:
                        fix_lines.append(f"# === {n['title']} ===")
                        for line in note.split('\n'):
                            if line.strip().startswith('$ '):
                                fix_lines.append(line.strip().replace('$ ', ''))
                            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                                fix_lines.append(f"\n# {line.strip()}")

                if fix_lines:
                    runbook_path = filepath.parent / f"{filepath.stem}_runbook.txt"
                    runbook_path.write_text("# RUNBOOK DE REMEDIACIÓN Y COMANDOS FIX\n# Generado por Net Troubleshoot Dashboard\n\n" + "\n".join(fix_lines), encoding="utf-8")
                    display.print_alert(f"Runbook de solución generado en: {runbook_path}")

                display.pause()
            except Exception as e:
                display.print_alert(f"Error al escribir el archivo: {e}")
                display.pause()

    def _run_magic_diagnostic(self):
        """Módulo interactivo de Diagnóstico Mágico e Interpretación de Errores."""
        from core.diagnostic_engine import diagnose_config_or_log, VENDORS
        
        display.clear()
        display.print_banner(confidence=self.session_confidence)
        
        if display.RICH_AVAILABLE:
            from rich.panel import Panel
            from rich.table import Table
            from rich.text import Text
            
            display._console.print(Panel(
                "[bold pink1]🤖 ANALIZADOR DE DIAGNÓSTICO MÁGICO[/bold pink1]\n\n"
                "Pegue la salida de un comando de consola, logs del sistema (Syslog) o fragmentos "
                "de configuración de cualquier vendor. El motor identificará la anomalía, el RFC "
                "asociado y generará los comandos de reparación específicos.",
                border_style="pink1"
            ))
        else:
            print("=============================================================")
            print("🤖 ANALIZADOR DE DIAGNÓSTICO MÁGICO")
            print("=============================================================")
            print("Pegue comandos, logs o configuración. Se detectará el error automáticamente.")
            
        print("\nSeleccione el vendor de origen (o presione ENTER para auto-detectar):")
        vendor_keys = list(VENDORS.keys())
        for idx, vk in enumerate(vendor_keys, 1):
            print(f"  [{idx}] {VENDORS[vk]}")
        print("  [0] Auto-detectar (Recomendado)")
        
        selected_vk = None
        v_choice = display.prompt_choice("\nSeleccione opción [0]: ").strip()
        if v_choice and v_choice != "0":
            try:
                v_idx = int(v_choice) - 1
                if 0 <= v_idx < len(vendor_keys):
                    selected_vk = vendor_keys[v_idx]
            except ValueError:
                pass
                
        print("\n--- Pegue el contenido a analizar ---")
        print("(Pegue el texto y escriba 'EOF' en una línea nueva o deje una línea en blanco y presione ENTER para finalizar):")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "EOF" or (not line.strip() and lines):
                    break
                lines.append(line)
            except (KeyboardInterrupt, EOFError):
                break
                
        input_text = "\n".join(lines)
        if not input_text.strip():
            display.print_alert("No se ingresó ningún texto para analizar.")
            display.pause()
            return
            
        print("\n  [Analizando datos del plano de control y datos...]")
        import time
        time.sleep(0.5)
        
        report = diagnose_config_or_log(input_text, selected_vk)
        
        display.clear()
        display.print_banner(confidence=self.session_confidence)
        
        if display.RICH_AVAILABLE:
            severity_color = "red" if report["severity"] == "Crítica" else "yellow" if report["severity"] == "Alta" else "cyan"
            
            # Encabezado del reporte
            header_text = Text()
            header_text.append("PROBLEMA: ", style="bold")
            header_text.append(report["problem_title"] + "\n", style="bold red" if report["severity"] in ("Alta", "Crítica") else "bold yellow")
            header_text.append(f"Tecnología: {report['technology']} | Severidad: {report['severity']} | RFC: {report['rfc_reference']}", style="dim")
            
            display._console.print(Panel(header_text, title="Diagnóstico Inteligente", border_style="red"))
            
            # Causa raíz
            display._console.print(Panel(
                f"[bold cyan]Explicación Arquitectónica (Causa Raíz):[/bold cyan]\n{report['architectural_cause']}\n\n"
                f"[bold green]Criterio de Aceptación Sano:[/bold green]\n{report['acceptance_criteria']}",
                title="Análisis Científico",
                border_style="cyan"
            ))
            
            # Líneas del error
            if report.get("anomalous_lines"):
                anom_text = "\n".join([f"-> {l}" for l in report["anomalous_lines"]])
                display._console.print(Panel(
                    anom_text,
                    title="Líneas Anómalas Detectadas",
                    border_style="yellow",
                    style="bold red"
                ))
                
            # Soluciones
            if report.get("solutions"):
                table = Table(title="Plan de Acción y Comandos de Solución (Fix)", border_style="green", show_lines=True)
                table.add_column("Vendor / Plataforma", style="bold yellow", width=25)
                table.add_column("Comandos sugeridos de reparación", style="green")
                
                for v_key, cmds_list in report["solutions"].items():
                    vendor_name = VENDORS.get(v_key, v_key.upper())
                    cmds_text = "\n".join([f"$ {c}" for c in cmds_list])
                    table.add_row(vendor_name, cmds_text)
                    
                display._console.print(table)
        else:
            print("=============================================================")
            print(f"DIAGNÓSTICO: {report['problem_title']}")
            print(f"Tecnología: {report['technology']} | Severidad: {report['severity']}")
            print(f"RFC Referencia: {report['rfc_reference']}")
            print("=============================================================")
            print(f"\n[Causa Raíz]:\n{report['architectural_cause']}")
            print(f"\n[Criterio Sano]:\n{report['acceptance_criteria']}")
            
            if report.get("anomalous_lines"):
                print("\n[Líneas Anómalas]:")
                for l in report["anomalous_lines"]:
                    print(f"  ! {l}")
                    
            if report.get("solutions"):
                print("\n[Plan de Acción y Comandos de Solución]:")
                for v_key, cmds_list in report["solutions"].items():
                    print(f"\n  * {VENDORS.get(v_key, v_key.upper())}:")
                    for c in cmds_list:
                        print(f"    $ {c}")
                        
        print("\nOpciones de Registro:")
        print("  [1] Guardar reporte de diagnóstico en la bitácora activa")
        print("  [2] Descartar y volver")
        
        save_choice = display.prompt_choice("\nSeleccione opción [1]: ").strip()
        if not save_choice or save_choice == "1":
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Construir reporte
            note_lines = [
                f"PROBLEMA DETECTADO: {report['problem_title']}",
                f"Tecnología: {report['technology']} | Severidad: {report['severity']}",
                f"RFC: {report['rfc_reference']}",
                f"Causa Raíz: {report['architectural_cause']}",
                f"Criterio de Aceptación: {report['acceptance_criteria']}"
            ]
            if report.get("solutions"):
                note_lines.append("Comandos de reparación sugeridos:")
                for vk, clst in report["solutions"].items():
                    note_lines.append(f"  - {VENDORS.get(vk, vk.upper())}:")
                    for c in clst:
                        note_lines.append(f"    $ {c}")
                        
            self.notes_log.append({
                "tech": "diagnostico_magico",
                "tech_name": "Analizador Inteligente",
                "step": "diagnostico_magico",
                "title": f"Diagnóstico: {report['problem_title']}",
                "note": "\n".join(note_lines),
                "timestamp": timestamp
            })
            display.print_alert("Reporte de diagnóstico registrado en la bitácora de sesión.")
            
        display.pause()
