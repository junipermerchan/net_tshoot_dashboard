/**
 * NET-TSHOOT — Network Troubleshooting Dashboard Web App Engine
 * Pure Vanilla JS, client-side state management.
 */

class WebApp {
    constructor() {
        this.data = NET_TSHOOT_DATA;
        
        // Inject ID into each KB item for easier lookup
        if (this.data && this.data.KB) {
            for (const key in this.data.KB) {
                this.data.KB[key].id = key;
            }
        }
        
        // App State
        this.activeView = 'home'; // home, flow, simulator, search
        this.activeSidebarTab = 'ts'; // ts, config
        
        this.activeTech = null;
        this.activeVendor = null;
        this.activeTier = 3; // Default Tier 3
        this.currentStepKey = null;
        this.history = [];
        
        this.sessionVariables = {};
        this.notesLog = [];
        this.evidenceRegistered = new Set(); // Set of "tech.step" strings
        
        this.activeTheoryTab = 'definition';
        this.theoryCollapsed = true;
        
        this.activeSimScenario = null;
        this.activeSimStepIdx = 0;
        this.collapsedSimLayers = {};
        
        this.techFilterQuery = '';
        this.globalSearchQuery = '';
        this.theme = 'dark';
        this.currentLang = 'es'; // Default language
        this.scientificMode = 'normal'; // Default scientific mode
        this.terminalMode = 'cmds'; // Default terminal mode
        this.simScenarioState = 'fail'; // Default scenario state
        this.simRunning = false;
        this.noteSavedTimeout = null;
        this.activeIpVersion = 'ipv4'; // Default IP version
    }

    init() {
        console.log("Inicializando aplicación web NET-TSHOOT...");
        
        // Load persistent session from LocalStorage
        this.loadSessionFromStorage();
        this.currentLang = localStorage.getItem('net_tshoot_lang') || 'es';
        
        // Set language buttons state
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.id === `lang-btn-${this.currentLang}`);
        });
        
        // Translate UI
        this.translateUI();
        
        // Set Initial Select values
        document.getElementById('session-tier-select').value = this.activeTier;
        
        // Render menus
        this.renderSidebar();
        
        // Init Lucide icons
        lucide.createIcons();
        
        // Setup initial view
        this.showView(this.activeView);
        
        // Render variables, notes, and hypotheses in the sidebar
        this.renderSidebarVariables();
        this.renderSidebarNotes();
        this.renderSidebarHypotheses();
        this.updateConfidenceIndicator();
    }

    showView(viewName) {
        this.activeView = viewName;
        document.querySelectorAll('.content-view').forEach(view => {
            view.classList.remove('active');
        });
        
        const viewId = viewName === 'search' ? 'view-search-results' : `view-${viewName}`;
        const activeEl = document.getElementById(viewId);
        if (activeEl) {
            activeEl.classList.add('active');
        }
        
        // Update URL/History indicators if needed
        if (viewName === 'home') {
            this.activeTech = null;
            this.currentStepKey = null;
            this.history = [];
            // Remove active classes in sidebar
            document.querySelectorAll('.tech-item').forEach(item => item.classList.remove('active'));
        }
        
        // Rerender Lucide icons for newly shown elements
        lucide.createIcons();
    }

    goHome() {
        this.showView('home');
        document.getElementById('global-search-input').value = '';
        this.clearSearch();
    }

    // ==========================================================================
    // DATA LOADERS & PERSISTENCE
    // ==========================================================================
    loadSessionFromStorage() {
        try {
            const savedVars = localStorage.getItem('net_tshoot_vars');
            if (savedVars) this.sessionVariables = JSON.parse(savedVars);
            
            const savedNotes = localStorage.getItem('net_tshoot_notes');
            if (savedNotes) this.notesLog = JSON.parse(savedNotes);
            
            const savedTier = localStorage.getItem('net_tshoot_tier');
            if (savedTier) this.activeTier = parseInt(savedTier, 10);
            
            const savedTheme = localStorage.getItem('net_tshoot_theme');
            if (savedTheme) {
                this.theme = savedTheme;
                if (savedTheme === 'light') {
                    document.body.classList.remove('dark-theme');
                    document.body.classList.add('light-theme');
                    this.toggleThemeIcon(false);
                }
            }

            const savedMode = localStorage.getItem('net_tshoot_scientific_mode');
            if (savedMode) this.scientificMode = savedMode;
        } catch (e) {
            console.error("Error al cargar localStorage:", e);
        }
    }

    saveSessionToStorage() {
        try {
            localStorage.setItem('net_tshoot_vars', JSON.stringify(this.sessionVariables));
            localStorage.setItem('net_tshoot_notes', JSON.stringify(this.notesLog));
            localStorage.setItem('net_tshoot_tier', this.activeTier.toString());
            localStorage.setItem('net_tshoot_theme', this.theme);
            localStorage.setItem('net_tshoot_scientific_mode', this.scientificMode);
        } catch (e) {
            console.error("Error al guardar localStorage:", e);
        }
    }

    // ==========================================================================
    // SIDEBAR NAVIGATION
    // ==========================================================================
    switchSidebarTab(tab) {
        this.activeSidebarTab = tab;
        document.getElementById('tab-btn-ts').classList.toggle('active', tab === 'ts');
        document.getElementById('tab-btn-config').classList.toggle('active', tab === 'config');
        
        document.getElementById('tech-list-ts').classList.toggle('hidden', tab !== 'ts');
        document.getElementById('tech-list-config').classList.toggle('hidden', tab !== 'config');
    }

    filterTechList(event) {
        this.techFilterQuery = event.target.value.toLowerCase();
        this.renderSidebar();
    }

    renderSidebar() {
        const tsContainer = document.getElementById('tech-list-ts');
        const configContainer = document.getElementById('tech-list-config');
        
        tsContainer.innerHTML = '';
        configContainer.innerHTML = '';
        
        const troubleshooting = [];
        const configuration = [];
        
        // Sort keys to show alphabetically
        const sortedKeys = Object.keys(this.data.KB).sort((a, b) => {
            const nameA = this.getLocalizedText(this.data.KB[a], 'name');
            const nameB = this.getLocalizedText(this.data.KB[b], 'name');
            return nameA.localeCompare(nameB);
        });
        
        for (const key of sortedKeys) {
            const tech = this.data.KB[key];
            const name = this.getLocalizedText(tech, 'name');
            const matchesFilter = !this.techFilterQuery || name.toLowerCase().includes(this.techFilterQuery) || key.toLowerCase().includes(this.techFilterQuery);
            
            if (matchesFilter) {
                const item = { key, label: name };
                if (key.endsWith('_config')) {
                    configuration.push(item);
                } else {
                    troubleshooting.push(item);
                }
            }
        }
        
        if (troubleshooting.length === 0) {
            tsContainer.innerHTML = `<span class="empty-msg">${this.currentLang === 'es' ? 'No se encontraron tecnologías' : 'No technologies found'}</span>`;
        } else {
            troubleshooting.forEach(item => {
                const btn = document.createElement('button');
                btn.className = `tech-item ${this.activeTech === item.key ? 'active' : ''}`;
                btn.onclick = () => this.selectTechnology(item.key);
                btn.innerHTML = `<span>${item.label}</span><span class="item-meta">TS</span>`;
                tsContainer.appendChild(btn);
            });
        }
        
        if (configuration.length === 0) {
            configContainer.innerHTML = `<span class="empty-msg">${this.currentLang === 'es' ? 'No se encontraron guías' : 'No config guides found'}</span>`;
        } else {
            configuration.forEach(item => {
                const btn = document.createElement('button');
                btn.className = `tech-item ${this.activeTech === item.key ? 'active' : ''}`;
                btn.onclick = () => this.selectTechnology(item.key);
                btn.innerHTML = `<span>${item.label}</span><span class="item-meta">CONFIG</span>`;
                configContainer.appendChild(btn);
            });
        }
    }

    // ==========================================================================
    // GUIDED FLOW STATE ENGINE
    // ==========================================================================
    selectTechnology(techKey) {
        console.log(`Seleccionando tecnología: ${techKey}`);
        this.activeTech = techKey;
        this.history = [];
        
        // Mark active item in sidebar
        document.querySelectorAll('.tech-item').forEach(item => item.classList.remove('active'));
        this.renderSidebar(); // Redraws to highlight active
        
        const techData = this.data.KB[techKey];
        if (!techData) return;
        
        // Default vendor selection: select the first available vendor for this tech
        const vendors = techData.vendors || [];
        if (vendors.length > 0) {
            // Prefer keeping current vendor if supported, otherwise choose first
            if (!this.activeVendor || !vendors.includes(this.activeVendor)) {
                this.activeVendor = vendors[0];
            }
        } else {
            this.activeVendor = null;
        }
        
        // Find default start step key (ends with _start)
        const steps = techData.steps || {};
        let startStep = null;
        for (const stepKey in steps) {
            if (stepKey.endsWith('_start')) {
                startStep = stepKey;
                break;
            }
        }
        // Fallback to the first step key if no step ends with _start
        if (!startStep) {
            const stepKeys = Object.keys(steps);
            if (stepKeys.length > 0) {
                startStep = stepKeys[0];
            } else {
                startStep = 'start';
            }
        }
        this.currentStepKey = startStep;
        
        // Reset view panel theory state
        this.theoryCollapsed = true;
        document.getElementById('theory-collapsible').classList.add('collapsed');
        
        // Render Flow
        this.showView('flow');
        this.renderFlowHeader();
        this.renderVendorButtons();
        this.renderCurrentStep();
    }

    handleContextSwitch() {
        let targetTech = null;
        if (this.activeTech.endsWith('_config')) {
            targetTech = this.activeTech.replace('_config', '');
        } else {
            targetTech = this.activeTech + '_config';
        }
        
        if (this.data.KB[targetTech]) {
            // Switch sidebar tab automatically
            this.switchSidebarTab(targetTech.endsWith('_config') ? 'config' : 'ts');
            this.selectTechnology(targetTech);
        }
    }

    renderFlowHeader() {
        const techData = this.data.KB[this.activeTech];
        const isConfig = this.activeTech.endsWith('_config');
        
        // Set Header content
        document.getElementById('flow-tech-name').innerText = this.getLocalizedText(techData, 'name');
        document.getElementById('flow-tech-desc').innerText = this.getLocalizedText(techData, 'description') || (this.currentLang === 'es' ? 'Sin descripción disponible.' : 'No description available.');
        
        const categoryBadge = document.getElementById('flow-tech-category-badge');
        categoryBadge.innerText = isConfig ? (this.currentLang === 'es' ? 'Configuración' : 'Configuration') : 'Troubleshooting';
        categoryBadge.className = `badge ${isConfig ? 'config-badge' : 'ts-badge'}`;
        
        // Enlazar contraparte (TS <-> Config)
        let counterpart = isConfig ? this.activeTech.replace('_config', '') : this.activeTech + '_config';
        const switchBtn = document.getElementById('context-switch-btn');
        if (this.data.KB[counterpart]) {
            switchBtn.classList.remove('hidden');
            document.getElementById('context-switch-label').innerText = isConfig ? (this.currentLang === 'es' ? 'Ver Diagnóstico (TS)' : 'View Diagnostics (TS)') : (this.currentLang === 'es' ? 'Ver Configuración' : 'View Configuration');
        } else {
            switchBtn.classList.add('hidden');
        }
        
        // Load Theory Concepts
        this.renderTheoryConcepts();
    }

    renderVendorButtons() {
        const techData = this.data.KB[this.activeTech];
        const vendors = techData.vendors || [];
        const container = document.getElementById('vendor-btn-container');
        container.innerHTML = '';
        
        vendors.forEach(v => {
            const btn = document.createElement('button');
            btn.className = `vendor-btn ${this.activeVendor === v ? 'active' : ''}`;
            btn.innerText = this.data.VendorMap[v] || v;
            btn.onclick = () => this.changeVendor(v);
            container.appendChild(btn);
        });
    }

    changeVendor(vendorKey) {
        this.activeVendor = vendorKey;
        this.renderVendorButtons();
        this.renderCurrentStep();
    }

    changeSessionTier(event) {
        this.activeTier = parseInt(event.target.value, 10);
        this.saveSessionToStorage();
        if (this.activeView === 'flow') {
            // Update UI buttons indicators
            this.updateTierButtonsState();
            // Check step accessibility
            this.checkCurrentStepTierAccess();
        }
    }

    changeFlowTier(tierNum) {
        this.activeTier = tierNum;
        document.getElementById('session-tier-select').value = tierNum;
        this.saveSessionToStorage();
        this.updateTierButtonsState();
        this.checkCurrentStepTierAccess();
    }

    updateTierButtonsState() {
        document.querySelectorAll('#tier-radio-container .tier-btn').forEach(btn => {
            const btnTier = parseInt(btn.getAttribute('data-tier'), 10);
            btn.classList.toggle('active', btnTier === this.activeTier);
        });
    }

    changeScientificMode(mode) {
        this.scientificMode = mode;
        this.saveSessionToStorage();
        this.updateScientificModeButtonsState();
        if (this.activeView === 'flow') {
            this.renderCurrentStep();
        }
    }

    updateScientificModeButtonsState() {
        document.querySelectorAll('#scientific-mode-radio-container .scientific-btn').forEach(btn => {
            const btnMode = btn.getAttribute('data-mode');
            btn.classList.toggle('active', btnMode === this.scientificMode);
        });
        const descDiv = document.getElementById('scientific-mode-desc');
        if (descDiv) {
            const t = (k) => uiTranslations[this.currentLang][k] || k;
            if (this.scientificMode === 'normal') {
                descDiv.innerHTML = t('descScientificNormal');
            } else if (this.scientificMode === 'semi_strict') {
                descDiv.innerHTML = t('descScientificSemiStrict');
            } else if (this.scientificMode === 'strict') {
                descDiv.innerHTML = t('descScientificStrict');
            }
        }
    }

    checkCurrentStepTierAccess() {
        const steps = this.data.KB[this.activeTech].steps || {};
        let step = steps[this.currentStepKey] || {};
        let stepTier = step.tier || 1;
        
        while (stepTier > this.activeTier) {
            // Find a valid fallback choice in current step that matches current active tier
            let fallbackFound = false;
            for (const ch of (step.choices || [])) {
                const nxt = ch.next;
                if (!nxt || nxt === 'back_menu') continue;
                
                const nextStepData = steps[nxt] || {};
                const nextStepTier = nextStepData.tier || 1;
                if (nextStepTier <= this.activeTier) {
                    this.currentStepKey = nxt;
                    fallbackFound = true;
                    break;
                }
            }
            
            if (fallbackFound) {
                break;
            }
            
            // If no direct path, backtrack or go home
            if (this.history.length > 0) {
                this.currentStepKey = this.history.pop();
                step = steps[this.currentStepKey] || {};
                stepTier = step.tier || 1;
            } else {
                const startStepKey = this.data.KB[this.activeTech].start_step || 'start';
                this.currentStepKey = startStepKey;
                const startStep = steps[startStepKey] || {};
                if ((startStep.tier || 1) > this.activeTier) {
                    this.goHome();
                    return;
                }
                break;
            }
        }
        this.renderCurrentStep();
    }

    getStepTier(stepKey) {
        const steps = this.data.KB[this.activeTech].steps || {};
        const step = steps[stepKey] || {};
        return step.tier || 1;
    }

    nextStep(nextStepKey) {
        if (!nextStepKey) return;
        if (nextStepKey === 'back_menu') {
            this.goHome();
            return;
        }
        const steps = this.data.KB[this.activeTech].steps || {};
        const step = steps[this.currentStepKey] || {};
        const stepKey = `${this.activeTech}.${this.currentStepKey}`;
        // Scientific mode enforcement
        if (this.scientificMode === 'strict' && step.hypothesis) {
            if (!this.evidenceRegistered.has(stepKey)) {
                const alertBox = document.getElementById('scientific-alert-box');
                if (alertBox) {
                    alertBox.classList.remove('hidden');
                    alertBox.innerHTML = `<div class="scientific-alert strict"><i data-lucide="shield-alert"></i> <strong>Modo Estricto:</strong> Debe registrar evidencia para este paso antes de avanzar. Use el botón "Registrar Evidencia".</div>`;
                    if (window.lucide) window.lucide.createIcons();
                }
                return;
            }
        }
        if (this.scientificMode === 'semi_strict' && step.hypothesis) {
            if (!this.evidenceRegistered.has(stepKey)) {
                const alertBox = document.getElementById('scientific-alert-box');
                if (alertBox) {
                    alertBox.classList.remove('hidden');
                    alertBox.innerHTML = `<div class="scientific-alert semi"><i data-lucide="alert-triangle"></i> <strong>Advertencia:</strong> No ha registrado evidencia para esta hipótesis. Se recomienda documentar antes de continuar.</div>`;
                    if (window.lucide) window.lucide.createIcons();
                }
            }
        }
        this.history.push(this.currentStepKey);
        this.currentStepKey = nextStepKey;
        this.checkCurrentStepTierAccess();
    }

    prevStep() {
        if (this.history.length > 0) {
            this.currentStepKey = this.history.pop();
            this.checkCurrentStepTierAccess();
        }
    }

    // ==========================================================================
    // RENDER CURRENT FLOW STEP
    // ==========================================================================
    renderScientificFields(step) {
        const container = document.getElementById('step-scientific-container');
        if (!container) return;

        // Determine localized hypothesis
        const hypothesis = this.getLocalizedText(step, 'hypothesis');
        if (!hypothesis) {
            container.classList.add('hidden');
            container.innerHTML = '';
            return;
        }

        container.classList.remove('hidden');

        const escape = (s) => this.escapeHtml(s || '');
        const md = (s) => this.replaceMarkdown(escape(s));
        const listItems = (arr) => (arr || []).map(i => `<li>${md(i)}</li>`).join('');

        // Localized expected evidence
        let confirming = [];
        let invalidating = [];
        const evidence = step.expected_evidence || {};
        if (this.currentLang === 'en') {
            confirming = evidence.confirming_en || evidence.confirming || [];
            invalidating = evidence.invalidating_en || evidence.invalidating || [];
        } else {
            confirming = evidence.confirming || [];
            invalidating = evidence.invalidating || [];
        }

        // Localized fields
        const verificationSteps = this.currentLang === 'en' ? (step.verification_steps_en || step.verification_steps || []) : (step.verification_steps || []);
        const fix = this.getLocalizedText(step, 'fix');
        const scientificBasis = this.getLocalizedText(step, 'scientific_basis');
        const confidenceLevel = this.getLocalizedText(step, 'confidence_level');
        const biasWarnings = this.currentLang === 'en' ? (step.bias_warnings_en || step.bias_warnings || []) : (step.bias_warnings || []);
        const references = this.currentLang === 'en' ? (step.references_en || step.references || []) : (step.references || []);

        let html = `<div class="scientific-card">`;
        html += `<div class="scientific-header"><i data-lucide="microscope"></i><span>${this.currentLang === 'es' ? 'Método Científico de Troubleshooting' : 'Scientific Troubleshooting Method'}</span></div>`;

        // Hypothesis
        html += `<div class="scientific-section hypothesis-section">`;
        html += `<h4>🔬 ${this.currentLang === 'es' ? 'Hipótesis' : 'Hypothesis'}</h4>`;
        html += `<p>${md(hypothesis)}</p>`;
        html += `</div>`;

        // Verification steps
        if (verificationSteps && verificationSteps.length) {
            html += `<div class="scientific-section">`;
            html += `<h4>🧪 ${this.currentLang === 'es' ? 'Pasos de Verificación' : 'Verification Steps'}</h4>`;
            html += `<ol>${listItems(verificationSteps)}</ol>`;
            html += `</div>`;
        }

        // Evidence
        if (confirming.length || invalidating.length) {
            html += `<div class="scientific-section evidence-section">`;
            html += `<h4>📊 ${this.currentLang === 'es' ? 'Evidencia Esperada' : 'Expected Evidence'}</h4>`;
            if (confirming.length) {
                html += `<div class="evidence-group confirming">`;
                html += `<h5>✅ ${this.currentLang === 'es' ? 'Confirmatoria (si la hipótesis es CIERTA)' : 'Confirming (if hypothesis is TRUE)'}</h5>`;
                html += `<ul>${listItems(confirming)}</ul>`;
                html += `</div>`;
            }
            if (invalidating.length) {
                html += `<div class="evidence-group invalidating">`;
                html += `<h5>❌ ${this.currentLang === 'es' ? 'Invalidante (descarta la hipótesis)' : 'Invalidating (disproves hypothesis)'}</h5>`;
                html += `<ul>${listItems(invalidating)}</ul>`;
                html += `</div>`;
            }
            html += `</div>`;
        }

        // Quick Fix
        if (fix) {
            html += `<div class="scientific-section quickfix-section">`;
            html += `<h4>🛠️ ${this.currentLang === 'es' ? 'Solución Rápida / Quick Fix' : 'Quick Fix'}</h4>`;
            html += `<div class="quickfix-content">${md(fix)}</div>`;
            html += `</div>`;
        }

        // Basis
        if (scientificBasis) {
            html += `<div class="scientific-section basis-section">`;
            html += `<h4>📚 ${this.currentLang === 'es' ? 'Base Científica' : 'Scientific Basis'}</h4>`;
            html += `<p>${md(scientificBasis)}</p>`;
            html += `</div>`;
        }

        // Confidence
        if (confidenceLevel) {
            const isEs = this.currentLang === 'es';
            let normConf = confidenceLevel.toLowerCase();
            let color = 'red';
            if (normConf === 'alta' || normConf === 'high') color = 'green';
            else if (normConf === 'media' || normConf === 'medium') color = 'yellow';
            
            const displayConf = this.currentLang === 'en' && (confidenceLevel === 'Alta' || confidenceLevel === 'alta') ? 'High' : (this.currentLang === 'en' && (confidenceLevel === 'Media' || confidenceLevel === 'media') ? 'Medium' : confidenceLevel);

            html += `<div class="scientific-section confidence-section">`;
            html += `<h4>📊 ${isEs ? 'Nivel de Confianza' : 'Confidence Level'}</h4>`;
            html += `<span class="confidence-badge ${color}">${escape(displayConf)}</span>`;
            html += `</div>`;
        }

        // Bias warnings
        if (biasWarnings && biasWarnings.length) {
            html += `<div class="scientific-section bias-section">`;
            html += `<h4>⚠️ ${this.currentLang === 'es' ? 'Advertencias de Sesgo' : 'Bias Warnings'}</h4>`;
            html += `<ul class="bias-list">${listItems(biasWarnings)}</ul>`;
            html += `</div>`;
        }

        // References
        if (references && references.length) {
            html += `<div class="scientific-section refs-section">`;
            html += `<h4>🔗 ${this.currentLang === 'es' ? 'Referencias' : 'References'}</h4>`;
            html += `<ul class="refs-list">${listItems(references)}</ul>`;
            html += `</div>`;
        }

        html += `</div>`;
        container.innerHTML = html;
        if (window.lucide) window.lucide.createIcons();
    }

    renderBreadcrumbs() {
        const container = document.getElementById('step-breadcrumbs');
        if (!container) return;
        const steps = this.data.KB[this.activeTech].steps || {};
        let html = '';
        for (let i = 0; i < this.history.length; i++) {
            const h = this.history[i];
            const s = steps[h] || {};
            const title = this.getLocalizedText(s, 'title') || h;
            html += `<span class="crumb" data-step="${this.escapeHtml(h)}" onclick="app.jumpToHistoryStep(${i})">${this.escapeHtml(title)}</span>`;
            html += `<span class="crumb-separator">></span>`;
        }
        const currentStep = steps[this.currentStepKey] || {};
        const currentTitle = this.getLocalizedText(currentStep, 'title') || this.currentStepKey;
        html += `<span class="crumb crumb-current">${this.escapeHtml(currentTitle)}</span>`;
        container.innerHTML = html;
    }

    jumpToHistoryStep(index) {
        if (index < 0 || index >= this.history.length) return;
        this.history = this.history.slice(0, index + 1);
        this.currentStepKey = this.history.pop();
        this.renderCurrentStep();
    }

    renderCurrentStep() {
        let steps = this.data.KB[this.activeTech].steps || {};
        let step = steps[this.currentStepKey];
        
        if (!step) {
            // Global lookup if step is defined in another technology
            let foundTech = null;
            for (const tKey in this.data.KB) {
                if (this.data.KB[tKey].steps && this.data.KB[tKey].steps[this.currentStepKey]) {
                    foundTech = tKey;
                    break;
                }
            }
            if (foundTech) {
                console.log(`Paso '${this.currentStepKey}' encontrado en la tecnología: ${foundTech}. Cambiando contexto...`);
                this.activeTech = foundTech;
                this.switchSidebarTab(foundTech.endsWith('_config') ? 'config' : 'ts');
                this.renderFlowHeader();
                this.renderVendorButtons();
                steps = this.data.KB[this.activeTech].steps;
                step = steps[this.currentStepKey];
            } else {
                console.error(`Paso '${this.currentStepKey}' no encontrado en ninguna parte.`);
                this.goHome();
                return;
            }
        }
        
        // Breadcrumbs
        this.renderBreadcrumbs();

        // Title & Tier
        document.getElementById('step-title').innerText = this.getLocalizedText(step, 'title');
        document.getElementById('step-tier-badge').innerText = `Tier ${step.tier || 1}`;
        
        // Render step hierarchies
        const textOsi = document.getElementById('text-hierarchy-osi');
        const textDomain = document.getElementById('text-hierarchy-domain');
        const textMethodology = document.getElementById('text-hierarchy-methodology');
        
        if (textOsi && textDomain && textMethodology) {
            textOsi.innerText = this.getLocalizedText(step, 'osi_layer') || 'N/A';
            textDomain.innerText = this.getLocalizedText(step, 'network_domain') || 'N/A';
            textMethodology.innerText = this.getLocalizedText(step, 'methodology') || 'N/A';
        }
        
        // Progress index indicator
        const stepKeys = Object.keys(steps);
        const idx = stepKeys.indexOf(this.currentStepKey) + 1;
        document.getElementById('step-number-badge').innerText = this.currentLang === 'es' ? `Paso ${idx}` : `Step ${idx}`;
        
        // Description Body (simple Markdown replacement)
        let bodyHtml = this.replaceMarkdown(this.getLocalizedText(step, 'body') || '');
        bodyHtml = this.applyVariablesToText(bodyHtml);
        document.getElementById('step-body-content').innerHTML = bodyHtml;

        // Scientific Method fields
        this.renderScientificFields(step);
        
        // Get Vendor command lines
        const rawCmds = (step.commands && step.commands[this.activeVendor]) || [];
        const cmds = this.flattenCommandsByTier(rawCmds);
        
        // Extract placeholders
        const placeholders = this.getPlaceholdersFromCommands(cmds);
        this.renderVariablesForm(placeholders);
        
        // Render process terminal commands
        const terminalCodeEl = document.getElementById('terminal-commands-code');
        document.getElementById('terminal-vendor-title').innerText = `${this.currentLang === 'es' ? 'Terminal' : 'Terminal'} — ${this.data.VendorMap[this.activeVendor] || this.activeVendor || 'Vendor'}`;
        if (cmds.length === 0) {
            terminalCodeEl.innerHTML = `<span class="comment"># ${this.currentLang === 'es' ? 'No hay comandos de diagnóstico específicos de este paso para este vendor.' : 'No specific diagnostics commands for this step for this vendor.'}</span>`;
        } else {
            const processedCmds = cmds.map(c => this.applyVariablesToText(c));
            // Basic simulation of color highlighting
            const codeHtml = processedCmds.map(cmd => {
                if (cmd.startsWith('#') || cmd.startsWith('!')) {
                    return `<span class="comment">${this.escapeHtml(cmd)}</span>`;
                }
                // Highlight configuration keywords
                let highlighted = this.escapeHtml(cmd);
                const keywords = ['show', 'set', 'get', 'diagnose', 'execute', 'display', 'ping', 'traceroute', 'commit', 'configure', 'exit', 'interface', 'routing', 'policy'];
                keywords.forEach(kw => {
                    const regex = new RegExp(`\\b${kw}\\b`, 'g');
                    highlighted = highlighted.replace(regex, `<span class="keyword">${kw}</span>`);
                });
                return highlighted;
            }).join('\n');
            terminalCodeEl.innerHTML = codeHtml;
        }
        
        // Expected outcome
        const appliedExpected = this.applyVariablesToText(this.getLocalizedText(step, 'expected') || 'N/A');
        document.getElementById('expected-text').innerHTML = this.replaceMarkdown(appliedExpected);
        
        // Load note text from logs
        const currentNote = this.notesLog.find(n => n.tech === this.activeTech && n.step === this.currentStepKey);
        document.getElementById('step-note-textarea').value = currentNote ? currentNote.note : '';
        document.getElementById('note-saved-indicator').classList.add('hidden');
        
        // Render Choices Navigation
        const choicesContainer = document.getElementById('choices-btn-container');
        choicesContainer.innerHTML = '';
        
        // Filter choices by tier compatibility
        const visibleChoices = (step.choices || []).filter(ch => {
            const nxt = ch.next;
            if (!nxt || nxt === 'back_menu') return true;
            
            // Check if step exists locally in activeTech steps
            const nextStepLocal = steps[nxt];
            if (nextStepLocal) {
                return (nextStepLocal.tier || 1) <= this.activeTier;
            }
            
            // Fallback checking in entire KB dictionary
            for (const tKey in this.data.KB) {
                if (this.data.KB[tKey].steps && this.data.KB[tKey].steps[nxt]) {
                    return (this.data.KB[tKey].steps[nxt].tier || 1) <= this.activeTier;
                }
            }
            return true;
        });
        
        // Build buttons
        visibleChoices.forEach(ch => {
            const btn = document.createElement('button');
            btn.className = 'choice-btn';
            btn.innerText = this.getLocalizedText(ch, 'label');
            btn.onclick = () => this.nextStep(ch.next);
            choicesContainer.appendChild(btn);
        });
        
        // Evidence button (if step has hypothesis)
        if (step.hypothesis) {
            const stepKey = `${this.activeTech}.${this.currentStepKey}`;
            const alreadyEv = this.evidenceRegistered.has(stepKey);
            const evBtn = document.createElement('button');
            evBtn.className = 'choice-btn btn-accent';
            evBtn.innerHTML = `<i data-lucide="microscope" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"></i> ${this.currentLang === 'es' ? 'Registrar Evidencia' : 'Register Evidence'}${alreadyEv ? ' ✅' : ''}`;
            evBtn.onclick = () => this.registerEvidence(step);
            choicesContainer.appendChild(evBtn);
        }

        // RCA 5 Porqués button
        const rcaBtn = document.createElement('button');
        rcaBtn.className = 'choice-btn btn-secondary';
        rcaBtn.style.borderColor = 'var(--accent-yellow)';
        rcaBtn.innerHTML = `<i data-lucide="search-code" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px; color: var(--accent-yellow)"></i> ${this.currentLang === 'es' ? 'Realizar RCA (5 Porqués)' : 'Perform RCA (5 Whys)'}`;
        rcaBtn.onclick = () => this.openRcaModal(step);
        choicesContainer.appendChild(rcaBtn);

        // System options
        if (this.history.length > 0) {
            const backBtn = document.createElement('button');
            backBtn.className = 'choice-btn btn-secondary';
            backBtn.innerHTML = `<i data-lucide="arrow-left" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"></i> ${this.currentLang === 'es' ? 'Volver Atrás' : 'Go Back'}`;
            backBtn.onclick = () => this.prevStep();
            choicesContainer.appendChild(backBtn);
        }
        
        // Sync terminal mode selector buttons and wrapper blocks
        this.setTerminalMode(this.terminalMode);
    }

    registerEvidence(step) {
        const stepKey = `${this.activeTech}.${this.currentStepKey}`;
        const alertBox = document.getElementById('scientific-alert-box');
        if (this.evidenceRegistered.has(stepKey)) {
            if (alertBox) {
                alertBox.classList.remove('hidden');
                alertBox.innerHTML = `<div class="scientific-alert success"><i data-lucide="check-circle"></i> Evidencia ya estaba registrada para este paso.</div>`;
                if (window.lucide) window.lucide.createIcons();
            }
            return;
        }
        this.evidenceRegistered.add(stepKey);
        this.saveSessionToStorage();
        if (alertBox) {
            alertBox.classList.remove('hidden');
            alertBox.innerHTML = `<div class="scientific-alert success"><i data-lucide="check-circle"></i> Evidencia registrada correctamente.</div>`;
            if (window.lucide) window.lucide.createIcons();
        }
        this.renderCurrentStep(); // Refresh button state
    }

    // ==========================================================================
    // OSI LAYERS PACKET SIMULATOR
    // ==========================================================================
    openSimulatorView() {
        // Load initial scenarios
        const scenariosList = [];
        for (const [key, val] of Object.entries(this.data.PACKET_WALKTHROUGHS)) {
            const keyScenarios = val.scenarios || [];
            keyScenarios.forEach(sc => {
                scenariosList.push({
                    techKey: key,
                    id: sc.id,
                    name: sc.name,
                    raw: sc
                });
            });
        }
        
        if (!this.activeSimScenario && scenariosList.length > 0) {
            this.activeSimScenario = scenariosList[0].raw;
        }
        
        this.activeSimStepIdx = 0;
        this.collapsedSimLayers = {};
        
        this.showView('simulator');
        
        // Render selector button state
        if (this.activeSimScenario) {
            document.getElementById('selected-scenario-name').innerText = this.getLocalizedText(this.activeSimScenario, 'name');
        }
        
        this.setSimulatorState(this.simScenarioState || 'fail');
    }

    setSimulatorState(state) {
        this.simScenarioState = state;
        
        const btnFail = document.getElementById('sim-state-fail');
        const btnOk = document.getElementById('sim-state-ok');
        
        if (btnFail) btnFail.classList.toggle('active', state === 'fail');
        if (btnOk) btnOk.classList.toggle('active', state === 'ok');
        
        this.renderSimulatorTimeline();
        this.renderSimulatorStep();
    }

    toggleScenarioModal(show) {
        const overlay = document.getElementById('scenario-modal-overlay');
        if (show) {
            overlay.classList.remove('hidden');
            document.getElementById('modal-scenario-search').value = '';
            this.renderModalScenarios();
        } else {
            overlay.classList.add('hidden');
        }
    }
    
    handleOverlayClick(event) {
        if (event.target.id === 'scenario-modal-overlay') {
            this.toggleScenarioModal(false);
        }
    }

    openRcaModal(step) {
        this.activeRcaStep = step;
        this.toggleRcaModal(true);
        
        // Populate default symptom field
        const symptomInput = document.getElementById('rca-input-sintoma');
        if (symptomInput) {
            const currentTitle = this.getLocalizedText(step, 'title') || this.currentStepKey;
            symptomInput.value = this.currentLang === 'es' ? `Falla detectada en: ${currentTitle}` : `Issue detected at: ${currentTitle}`;
        }
        
        // Reset/Clear other fields
        for (let i = 1; i <= 5; i++) {
            const el = document.getElementById(`rca-input-p${i}`);
            if (el) el.value = '';
        }
        const causaInput = document.getElementById('rca-input-causa');
        if (causaInput) causaInput.value = '';
        const solucionInput = document.getElementById('rca-input-solucion');
        if (solucionInput) solucionInput.value = '';
    }

    toggleRcaModal(show) {
        const overlay = document.getElementById('rca-modal-overlay');
        if (overlay) {
            if (show) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
            }
        }
    }

    handleRcaOverlayClick(event) {
        if (event.target.id === 'rca-modal-overlay') {
            this.toggleRcaModal(false);
        }
    }

    saveRcaAnalysis() {
        if (!this.activeRcaStep) return;
        
        const sintoma = document.getElementById('rca-input-sintoma').value.trim();
        const p1 = document.getElementById('rca-input-p1').value.trim();
        const p2 = document.getElementById('rca-input-p2').value.trim();
        const p3 = document.getElementById('rca-input-p3').value.trim();
        const p4 = document.getElementById('rca-input-p4').value.trim();
        const p5 = document.getElementById('rca-input-p5').value.trim();
        const causa = document.getElementById('rca-input-causa').value.trim();
        const solucion = document.getElementById('rca-input-solucion').value.trim();
        
        if (!sintoma) {
            alert(this.currentLang === 'es' ? 'Por favor ingrese el síntoma inicial.' : 'Please enter the initial symptom.');
            return;
        }
        if (!p1) {
            alert(this.currentLang === 'es' ? 'Por favor ingrese al menos el primer porqué.' : 'Please enter at least the first why.');
            return;
        }
        
        // Format RCA string block
        const isEs = this.currentLang === 'es';
        let rcaText = `=== ANÁLISIS DE CAUSA RAÍZ (RCA - 5 PORQUÉS) ===\n`;
        rcaText += `• ${isEs ? 'Síntoma Inicial' : 'Initial Symptom'}: ${sintoma}\n`;
        if (p1) rcaText += `  └─ ¿Por qué 1?: ${p1}\n`;
        if (p2) rcaText += `  └─ ¿Por qué 2?: ${p2}\n`;
        if (p3) rcaText += `  └─ ¿Por qué 3?: ${p3}\n`;
        if (p4) rcaText += `  └─ ¿Por qué 4?: ${p4}\n`;
        if (p5) rcaText += `  └─ ¿Por qué 5?: ${p5}\n`;
        rcaText += `• ${isEs ? 'Causa Raíz lógica' : 'Logical Root Cause'}: ${causa || p1}\n`;
        rcaText += `• ${isEs ? 'Solución Definitiva' : 'Definitive Solution'}: ${solucion || 'N/A'}`;
        
        // Register it as a note for the current step
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        
        let existingNoteIndex = this.notesLog.findIndex(n => n.tech === this.activeTech && n.step === this.currentStepKey);
        if (existingNoteIndex !== -1) {
            this.notesLog[existingNoteIndex].note = rcaText;
            this.notesLog[existingNoteIndex].timestamp = timestamp;
        } else {
            const stepTitle = this.getLocalizedText(this.activeRcaStep, 'title') || this.currentStepKey;
            const techName = this.getLocalizedText(this.data.KB[this.activeTech], 'name') || this.activeTech;
            this.notesLog.push({
                tech: this.activeTech,
                tech_name: techName,
                techName: techName,
                step: this.currentStepKey,
                title: `RCA — ${stepTitle}`,
                note: rcaText,
                timestamp: timestamp
            });
        }
        
        this.saveSessionToStorage();
        this.renderNotesSidebar();
        this.toggleRcaModal(false);
        this.renderCurrentStep();
    }
    
    // ==========================================================================
    // GOLDEN CONFIG DIFF & RFC LOG WINDOWS AND HELPERS
    // ==========================================================================
    toggleGoldenModal(show) {
        const overlay = document.getElementById('golden-modal-overlay');
        if (overlay) {
            if (show) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
            }
        }
    }
    
    handleGoldenOverlayClick(event) {
        if (event.target.id === 'golden-modal-overlay') {
            this.toggleGoldenModal(false);
        }
    }
    
    toggleRfcModal(show) {
        const overlay = document.getElementById('rfc-modal-overlay');
        if (overlay) {
            if (show) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
            }
        }
    }
    
    handleRfcOverlayClick(event) {
        if (event.target.id === 'rfc-modal-overlay') {
            this.toggleRfcModal(false);
        }
    }
    
    openGoldenModal() {
        const steps = this.data.KB[this.activeTech].steps || {};
        const step = steps[this.currentStepKey];
        if (!step) return;
        
        const rawCmds = (step.commands && step.commands[this.activeVendor]) || [];
        const cmds = this.flattenCommandsByTier(rawCmds);
        
        const container = document.getElementById('golden-comparison-container');
        if (!container) return;
        container.innerHTML = '';
        
        if (cmds.length === 0) {
            container.innerHTML = `<div class="sim-system-msg">${this.currentLang === 'es' ? 'No hay comandos de diagnóstico en este paso.' : 'No diagnostic commands in this step.'}</div>`;
            this.toggleGoldenModal(true);
            return;
        }
        
        cmds.forEach(rawCmd => {
            const cmd = this.applyVariablesToText(rawCmd);
            const currentOutput = this.getSimulatedCommandOutput(rawCmd, this.activeVendor, this.currentStepKey);
            const appliedCurrent = this.applyVariablesToText(currentOutput);
            const appliedGolden = this.generateGoldenOutput(rawCmd, appliedCurrent);
            
            const section = document.createElement('div');
            section.className = 'golden-cmd-section';
            section.style.marginBottom = '25px';
            
            const title = document.createElement('h3');
            title.style.fontFamily = 'var(--font-mono)';
            title.style.fontSize = '13px';
            title.style.color = 'var(--accent-cyan)';
            title.style.marginBottom = '10px';
            title.innerText = `$ ${cmd}`;
            section.appendChild(title);
            
            const table = document.createElement('table');
            table.className = 'golden-diff-table';
            
            const header = document.createElement('tr');
            header.innerHTML = `
                <th style="width: 50%;">${this.currentLang === 'es' ? 'SALIDA ACTUAL (CON FALLA)' : 'CURRENT OUTPUT (FAILING)'}</th>
                <th style="width: 50%;">${this.currentLang === 'es' ? 'LÍNEA BASE (GOLDEN CONFIG)' : 'GOLDEN CONFIG (BASELINE)'}</th>
            `;
            table.appendChild(header);
            
            const currLines = appliedCurrent.split('\n');
            const goldLines = appliedGolden.split('\n');
            const maxLines = Math.max(currLines.length, goldLines.length);
            
            for (let i = 0; i < maxLines; i++) {
                const cL = i < currLines.length ? currLines[i] : '';
                const gL = i < goldLines.length ? goldLines[i] : '';
                
                const row = document.createElement('tr');
                if (cL !== gL) {
                    row.className = 'golden-diff-row modified';
                    row.innerHTML = `
                        <td class="diff-actual">${this.escapeHtml(cL)}</td>
                        <td class="diff-golden">${this.escapeHtml(gL)}</td>
                    `;
                } else {
                    row.className = 'golden-diff-row equal';
                    row.innerHTML = `
                        <td>${this.escapeHtml(cL)}</td>
                        <td>${this.escapeHtml(gL)}</td>
                    `;
                }
                table.appendChild(row);
            }
            
            section.appendChild(table);
            container.appendChild(section);
        });
        
        this.toggleGoldenModal(true);
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    generateGoldenOutput(cmd, currentOutput) {
        if (!currentOutput) return '';
        
        const cmdLower = cmd.toLowerCase();
        let golden = currentOutput;
        
        // 1. General Interface/Protocol State rules
        golden = golden.replace(/\bdown\b/g, 'up');
        golden = golden.replace(/\bDown\b/g, 'Up');
        golden = golden.replace(/\bDOWN\b/g, 'UP');
        golden = golden.replace(/\bshutdown\b/g, 'no shutdown');
        golden = golden.replace(/\bShutdown\b/g, 'No Shutdown');
        
        // 2. L2VPN Juniper codes
        golden = golden.replace(/\bDn\b/g, 'Up');
        golden = golden.replace(/\bEI\b/g, 'Up');
        golden = golden.replace(/\bEM\b/g, 'Up');
        golden = golden.replace(/\bVM\b/g, 'Up');
        golden = golden.replace(/\bOL\b/g, 'Up');
        golden = golden.replace(/\bWE\b/g, 'Up');
        golden = golden.replace(/\bNC\b/g, 'Up');
        
        // 3. BGP
        if (cmdLower.includes('bgp')) {
            golden = golden.replace(/\bIdle\b/g, 'Established');
            golden = golden.replace(/\bActive\b/g, 'Established');
            golden = golden.replace(/\bidle\b/g, 'established');
            golden = golden.replace(/\bactive\b/g, 'established');
            golden = golden.replace(/\bIDLE\b/g, 'ESTABLISHED');
            golden = golden.replace(/\bACTIVE\b/g, 'ESTABLISHED');
            
            golden = golden.replace(/\b0\s+routes\b/g, '150 routes');
            golden = golden.replace(/\b0\s+prefixes\b/g, '150 prefixes');
            golden = golden.replace(/\b0\s+received\b/g, '150 received');
        }
        
        // 4. OSPF / ISIS
        if (cmdLower.includes('ospf') || cmdLower.includes('isis')) {
            golden = golden.replace(/\bInit\b/g, 'Full');
            golden = golden.replace(/\bAttempt\b/g, 'Full');
            golden = golden.replace(/\bExchange\b/g, 'Full');
            golden = golden.replace(/\bLoading\b/g, 'Full');
            golden = golden.replace(/\b2-Way\b/g, 'Full');
            golden = golden.replace(/\bPri:\s*0\b/g, 'Pri: 128');
        }
        
        // 5. LACP
        if (cmdLower.includes('lacp') || cmdLower.includes('etherchannel') || cmdLower.includes('port-channel')) {
            golden = golden.replace(/\bIndividual\b/g, 'Bundle');
            golden = golden.replace(/\bSuspended\b/g, 'Bundle');
            golden = golden.replace(/\bindividual\b/g, 'bundle');
            golden = golden.replace(/\bsuspended\b/g, 'bundle');
        }
        
        // 6. Errors
        golden = golden.replace(/\b(errors|Errors|ERRORS)\s*:\s*\d+/g, 'errors: 0');
        golden = golden.replace(/\b(discarded|discards|Discards)\s*:\s*\d+/g, 'discards: 0');
        golden = golden.replace(/\b(input errors|input error)\s*:\s*\d+/g, 'input errors: 0');
        golden = golden.replace(/\b(output errors|output error)\s*:\s*\d+/g, 'output errors: 0');
        golden = golden.replace(/\b(collisions|Collisions)\s*:\s*\d+/g, 'collisions: 0');
        
        // 7. MTU Mismatch
        golden = golden.replace(/\bMTU\s+mismatch\b/gi, 'MTU match');
        golden = golden.replace(/\bmismatch\b/g, 'match');
        golden = golden.replace(/\bMismatch\b/g, 'Match');
        golden = golden.replace(/\bMISMATCH\b/g, 'MATCH');
        
        // 8. Fibra GPON
        if (cmdLower.includes('gpon') || cmdLower.includes('ont') || cmdLower.includes('olt')) {
            golden = golden.replace(/-\d+\.\d+\s*dBm/g, '-19.2 dBm');
            golden = golden.replace(/optical power: low/g, 'optical power: normal');
            golden = golden.replace(/ranging state: \w+/g, 'ranging state: operation');
            golden = golden.replace(/auth state: \w+/g, 'auth state: operational');
            golden = golden.replace(/phase: \w+/g, 'phase: operational');
        }
        
        return golden;
    }
    
    openRfcModal() {
        const container = document.getElementById('rfc-list-container');
        if (!container) return;
        container.innerHTML = '';
        
        const ticketsDb = this.data.CHANGE_TICKETS || {};
        let techTickets = [];
        
        const cleanTech = this.activeTech.toLowerCase().replace('_config', '');
        
        let foundKey = null;
        for (const key in ticketsDb) {
            if (cleanTech.includes(key) || key.includes(cleanTech)) {
                foundKey = key;
                break;
            }
        }
        
        if (foundKey && ticketsDb[foundKey]) {
            techTickets = ticketsDb[foundKey];
        } else {
            techTickets = [
                {
                    "id": "RFC-8800",
                    "time_es": "Hace 12 horas",
                    "time_en": "12 hours ago",
                    "device": "Router-Borde-01",
                    "description_es": "Revisión general de políticas de seguridad y actualización de firmas de firewall.",
                    "description_en": "General security policies review and firewall signatures update.",
                    "status": "Completado / Completed",
                    "author": "Soporte TI"
                },
                {
                    "id": "RFC-8790",
                    "time_es": "Hace 20 horas",
                    "time_en": "20 hours ago",
                    "device": "Switch-Distribucion-02",
                    "description_es": "Mantenimiento correctivo y limpieza de puertos SFP+ fibra óptica.",
                    "description_en": "Corrective maintenance and cleaning of SFP+ fiber ports.",
                    "status": "Completado / Completed",
                    "author": "Fusión S.L. (Contratista)"
                }
            ];
        }
        
        const isEs = this.currentLang === 'es';
        
        techTickets.forEach(t => {
            const card = document.createElement('div');
            card.className = 'rfc-card';
            card.innerHTML = `
                <div class="rfc-card-header">
                    <span class="rfc-id-badge">${t.id}</span>
                    <span class="rfc-time">${isEs ? t.time_es : t.time_en}</span>
                </div>
                <div class="rfc-device-line">${isEs ? 'Dispositivo afectado' : 'Affected device'}: <span>${t.device}</span></div>
                <div class="rfc-desc">${t.description_es}</div>
                <div class="rfc-desc-en">${t.description_en}</div>
                <div class="rfc-meta-footer">
                    <span>${isEs ? 'Autor' : 'Author'}: ${t.author}</span>
                    <span class="rfc-status">${isEs ? 'Completado' : 'Completed'}</span>
                </div>
            `;
            container.appendChild(card);
        });
        
        this.toggleRfcModal(true);
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    renderModalScenarios(query = '') {
        const container = document.getElementById('modal-scenarios-categories-container');
        container.innerHTML = '';
        
        // Group scenarios by category
        const groups = {
            'routing': [],
            'switching': [],
            'security': [],
            'carrier': [],
            'other': []
        };
        
        for (const [key, val] of Object.entries(this.data.PACKET_WALKTHROUGHS)) {
            const cat = techToCategory[key] || 'other';
            const keyScenarios = val.scenarios || [];
            keyScenarios.forEach(sc => {
                const name = this.getLocalizedText(sc, 'name');
                const desc = this.getLocalizedText(sc, 'description');
                
                const matches = !query || 
                    name.toLowerCase().includes(query.toLowerCase()) || 
                    desc.toLowerCase().includes(query.toLowerCase()) ||
                    key.toLowerCase().includes(query.toLowerCase());
                
                if (matches) {
                    groups[cat].push({
                        techKey: key,
                        id: sc.id,
                        name: name,
                        desc: desc,
                        stepsCount: sc.steps ? sc.steps.length : 0,
                        raw: sc
                    });
                }
            });
        }
        
        let totalRendered = 0;
        
        // Render categories
        for (const catKey of ['routing', 'switching', 'security', 'carrier', 'other']) {
            const list = groups[catKey];
            if (list.length === 0) continue;
            
            totalRendered += list.length;
            
            const groupDiv = document.createElement('div');
            groupDiv.className = 'scenario-category-group';
            
            const title = document.createElement('h3');
            title.className = 'scenario-category-title';
            title.innerText = categoryMap[this.currentLang][catKey];
            groupDiv.appendChild(title);
            
            const grid = document.createElement('div');
            grid.className = 'scenarios-grid';
            
            list.forEach(sc => {
                const card = document.createElement('div');
                const isActive = this.activeSimScenario && this.activeSimScenario.id === sc.id;
                card.className = `scenario-card-item ${isActive ? 'active' : ''}`;
                card.onclick = () => this.selectModalScenario(sc.id);
                
                // Choose icon based on category
                let iconName = 'network';
                if (catKey === 'routing') iconName = 'route';
                else if (catKey === 'switching') iconName = 'git-commit';
                else if (catKey === 'security') iconName = 'shield';
                else if (catKey === 'carrier') iconName = 'globe';
                
                card.innerHTML = `
                    <div class="scenario-card-header">
                        <h3>${this.escapeHtml(sc.name)}</h3>
                        <div class="scenario-card-icon">
                            <i data-lucide="${iconName}"></i>
                        </div>
                    </div>
                    <p class="scenario-card-desc">${this.escapeHtml(sc.desc || '')}</p>
                    <div class="scenario-card-meta">
                        <span class="scenario-card-tech">${this.escapeHtml(sc.techKey)}</span>
                        <span class="scenario-card-steps">${sc.stepsCount} ${this.currentLang === 'es' ? 'pasos' : 'steps'}</span>
                    </div>
                `;
                grid.appendChild(card);
            });
            
            groupDiv.appendChild(grid);
            container.appendChild(groupDiv);
        }
        
        if (totalRendered === 0) {
            container.innerHTML = `<span class="empty-msg" style="padding:40px 0;">${uiTranslations[this.currentLang]['noResults']}</span>`;
        }
        
        lucide.createIcons();
    }

    filterModalScenarios(event) {
        const query = event.target.value;
        this.renderModalScenarios(query);
    }

    selectModalScenario(scenarioId) {
        // Find scenario object
        for (const [key, val] of Object.entries(this.data.PACKET_WALKTHROUGHS)) {
            const found = (val.scenarios || []).find(s => s.id === scenarioId);
            if (found) {
                this.activeSimScenario = found;
                break;
            }
        }
        
        this.activeSimStepIdx = 0;
        this.collapsedSimLayers = {};
        
        // Update selector button label
        if (this.activeSimScenario) {
            document.getElementById('selected-scenario-name').innerText = this.getLocalizedText(this.activeSimScenario, 'name');
        }
        
        this.toggleScenarioModal(false);
        this.renderSimulatorTimeline();
        this.renderSimulatorStep();
    }

    renderSimulatorTimeline() {
        const list = document.getElementById('sim-timeline-steps-list');
        list.innerHTML = '';
        
        if (!this.activeSimScenario) return;
        const steps = this.activeSimScenario.steps || [];
        
        steps.forEach((st, idx) => {
            const node = document.createElement('div');
            node.className = `timeline-node ${this.activeSimStepIdx === idx ? 'active' : ''}`;
            if (this.simScenarioState === 'ok') {
                node.classList.add('solved');
            }
            node.onclick = () => this.handleSimulatorStepSelect(idx);
            
            const deviceName = this.getLocalizedText(st, 'device');
            const stepLabel = this.currentLang === 'es' ? `Paso ${idx + 1}` : `Step ${idx + 1}`;
            
            node.innerHTML = `
                <div class="timeline-dot"></div>
                <div class="timeline-info">
                    <h4>${stepLabel}</h4>
                    <span>${this.escapeHtml(deviceName || 'Device')}</span>
                </div>
            `;
            list.appendChild(node);
        });
    }

    handleSimulatorStepSelect(index) {
        this.activeSimStepIdx = index;
        this.renderSimulatorTimeline();
        this.renderSimulatorStep();
    }

    renderSimulatorStep() {
        if (!this.activeSimScenario) return;
        const steps = this.activeSimScenario.steps || [];
        const step = steps[this.activeSimStepIdx];
        if (!step) return;
        
        const stepOfText = this.currentLang === 'es' ? 
            `Paso ${this.activeSimStepIdx + 1} de ${steps.length}` : 
            `Step ${this.activeSimStepIdx + 1} of ${steps.length}`;
            
        // Meta
        document.getElementById('sim-step-badge-num').innerText = stepOfText;
        document.getElementById('sim-step-title-text').innerText = this.getLocalizedText(step, 'step_title');
        document.getElementById('sim-step-device-name').innerText = this.getLocalizedText(step, 'device') || 'N/A';
        
        // Scenario State status badge
        const badgeState = document.getElementById('sim-step-state-badge');
        if (badgeState) {
            if (this.simScenarioState === 'ok') {
                badgeState.innerText = this.currentLang === 'es' ? 'Solucionado' : 'Healthy';
                badgeState.className = 'state-status-badge ok';
            } else {
                badgeState.innerText = this.currentLang === 'es' ? 'Con Falla' : 'Failed';
                badgeState.className = 'state-status-badge fail';
            }
        }
        
        // Actions & Note
        document.getElementById('sim-step-action-desc').innerText = this.getLocalizedText(step, 'action') || '';
        document.getElementById('sim-step-note-desc').innerText = this.getLocalizedText(step, 'note') || (this.currentLang === 'es' ? 'Sin anotación adicional.' : 'No additional note.');
        
        // Encapsulation Layers
        const layersContainer = document.getElementById('sim-layers-list');
        layersContainer.innerHTML = '';
        
        const layers = step.layers || [];
        if (layers.length === 0) {
            layersContainer.innerHTML = `<span class="empty-msg">${this.currentLang === 'es' ? 'No hay capas OSI descritas en este paso.' : 'No OSI layers described in this step.'}</span>`;
            return;
        }
        
        layers.forEach((lyr, index) => {
            const name = this.getLocalizedText(lyr, 'name') || 'Layer';
            const detail = this.getLocalizedText(lyr, 'detail') || '';
            const checks = this.getLocalizedText(lyr, 'checks') || '';
            const anomalies = this.simScenarioState === 'ok' ? '' : (this.getLocalizedText(lyr, 'anomalies') || '');
            const pc = lyr.packet_capture;
            
            // Map CSS Layer styling
            let cssClass = 'layer-l1';
            if (name.includes('Capa 7') || name.includes('Capa 6') || name.includes('Capa 5') || name.includes('Aplicación') || name.includes('Layer 7') || name.includes('Layer 6') || name.includes('Layer 5') || name.includes('Application')) cssClass = 'layer-l7';
            else if (name.includes('Capa 4') || name.includes('Transporte') || name.includes('Layer 4') || name.includes('Transport')) cssClass = 'layer-l4';
            else if (name.includes('Capa 3') || name.includes('Red') || name.includes('Layer 3') || name.includes('Network')) cssClass = 'layer-l3';
            else if (name.includes('Capa 2.5') || name.includes('MPLS') || name.includes('VXLAN') || name.includes('PW') || name.includes('Layer 2.5')) cssClass = 'layer-l25';
            else if (name.includes('Capa 2') || name.includes('Enlace') || name.includes('Layer 2') || name.includes('Link')) cssClass = 'layer-l2';
            
            const panel = document.createElement('div');
            panel.className = `osi-layer-panel ${cssClass}`;
            if (this.simScenarioState === 'fail' && anomalies) {
                panel.classList.add('has-anomaly');
            }
            
            // Accordion toggle status
            const isCollapsed = this.collapsedSimLayers[`${this.activeSimStepIdx}_${index}`] ?? false;
            
            const header = document.createElement('div');
            header.className = 'layer-header-bar';
            header.onclick = () => this.toggleSimulatorLayerCollapse(index);
            header.innerHTML = `
                <div class="layer-left-group">
                    <i data-lucide="${isCollapsed ? 'chevron-right' : 'chevron-down'}" style="width:16px;height:16px;"></i>
                    <h4>${this.escapeHtml(name)}</h4>
                </div>
            `;
            
            const body = document.createElement('div');
            body.className = `layer-content-body ${isCollapsed ? 'hidden' : ''}`;
            
            // Detail grid
            const table = document.createElement('div');
            table.className = 'osi-detail-table';
            
            const lblDetails = this.currentLang === 'es' ? 'Detalles:' : 'Details:';
            const lblVerify = this.currentLang === 'es' ? 'Verificar:' : 'Verify:';
            const lblAnomalies = this.currentLang === 'es' ? 'Anomalías:' : 'Anomalies:';
            
            if (detail) {
                table.innerHTML += `<div class="row-title">${lblDetails}</div><div class="row-value">${this.escapeHtml(detail)}</div>`;
            }
            if (checks) {
                table.innerHTML += `<div class="row-title">${lblVerify}</div><div class="row-value">${this.escapeHtml(checks)}</div>`;
            }
            if (anomalies) {
                table.innerHTML += `<div class="row-title">${lblAnomalies}</div><div class="row-value" style="color:var(--accent-red); font-weight:500;">${this.escapeHtml(anomalies)}</div>`;
            }
            body.appendChild(table);
            
            // Wireshark/tcpdump captures
            if (pc) {
                const capBox = document.createElement('div');
                capBox.className = 'osi-capture-box';
                const capTitle = this.currentLang === 'es' ? 'Comandos de Captura de Paquetes' : 'Packet Capture Commands';
                const noteTitle = this.currentLang === 'es' ? 'Nota' : 'Note';
                const pcNotes = this.getLocalizedText(pc, 'notes');
                
                capBox.innerHTML = `
                    <span class="cap-title">${capTitle}</span>
                    <div class="osi-detail-table" style="margin-top: 4px;">
                        <div class="row-title" style="color: var(--accent-cyan)">Wireshark:</div>
                        <div class="row-value cap-cmd">${this.escapeHtml(pc.wireshark_display_filter || 'N/A')}</div>
                        <div class="row-title" style="color: var(--accent-green)">tcpdump:</div>
                        <div class="row-value cap-cmd">${this.escapeHtml(pc.tcpdump_filter || 'N/A')}</div>
                    </div>
                `;
                if (pcNotes) {
                    capBox.innerHTML += `<span class="empty-msg" style="text-align:left; padding:6px 0 0 0; font-size:0.7rem; border-top: 1px solid rgba(255,255,255,0.03); margin-top:6px;">${noteTitle}: ${this.escapeHtml(pcNotes)}</span>`;
                }
                body.appendChild(capBox);
            }
            
            panel.appendChild(header);
            panel.appendChild(body);
            layersContainer.appendChild(panel);
        });
        lucide.createIcons();
    }

    toggleSimulatorLayerCollapse(layerIdx) {
        const key = `${this.activeSimStepIdx}_${layerIdx}`;
        this.collapsedSimLayers[key] = !(this.collapsedSimLayers[key] ?? false);
        this.renderSimulatorStep();
    }

    // ==========================================================================
    // UTILITIES
    // ==========================================================================
    toggleTheme() {
        if (this.theme === 'dark') {
            this.theme = 'light';
            document.body.classList.remove('dark-theme');
            document.body.classList.add('light-theme');
            this.toggleThemeIcon(false);
        } else {
            this.theme = 'dark';
            document.body.classList.remove('light-theme');
            document.body.classList.add('dark-theme');
            this.toggleThemeIcon(true);
        }
        this.saveSessionToStorage();
    }

    toggleThemeIcon(isDark) {
        document.getElementById('theme-sun-icon').classList.toggle('hidden', isDark);
        document.getElementById('theme-moon-icon').classList.toggle('hidden', !isDark);
    }

    escapeHtml(text) {
        if (!text) return '';
        return text.toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    copyCommandsToClipboard() {
        if (!this.activeTech) return;
        const steps = this.data.KB[this.activeTech].steps || {};
        const step = steps[this.currentStepKey];
        if (!step) return;
        
        const rawCmds = (step.commands && step.commands[this.activeVendor]) || [];
        const cmds = this.flattenCommandsByTier(rawCmds);
        if (cmds.length === 0) return;
        
        const processedText = cmds.map(c => this.applyVariablesToText(c)).join('\n');
        
        navigator.clipboard.writeText(processedText).then(() => {
            const btn = document.getElementById('btn-copy-cmds');
            if (btn) {
                const originalHTML = btn.innerHTML;
                btn.innerHTML = `<i data-lucide="check" style="color:#10b981;"></i>`;
                if (window.lucide) window.lucide.createIcons();
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    if (window.lucide) window.lucide.createIcons();
                }, 2000);
            }
        }).catch(err => {
            console.error('No se pudo copiar el texto al portapapeles: ', err);
        });
    }

    clearSearch() {
        this.globalSearchQuery = '';
        const searchInput = document.getElementById('global-search-input');
        if (searchInput) {
            searchInput.value = '';
        }
        const clearBtn = document.getElementById('clear-search-btn');
        if (clearBtn) {
            clearBtn.classList.add('hidden');
        }
        if (this.activeView === 'search') {
            this.showView('home');
        }
    }

    handleGlobalSearch(event) {
        const query = event.target.value;
        this.globalSearchQuery = query.trim();
        
        const clearBtn = document.getElementById('clear-search-btn');
        
        if (this.globalSearchQuery.length === 0) {
            if (clearBtn) clearBtn.classList.add('hidden');
            if (this.activeView === 'search') {
                this.showView('home');
            }
        } else {
            if (clearBtn) clearBtn.classList.remove('hidden');
            this.showView('search');
            this.renderSearchResults();
        }
    }

    focusSearch() {
        const searchInput = document.getElementById('global-search-input');
        if (searchInput) {
            searchInput.focus();
            searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    renderSearchResults() {
        const wrapper = document.getElementById('search-results-wrapper');
        const queryHighlight = document.getElementById('search-query-highlight');
        const resultsCountEl = document.getElementById('search-results-count');
        
        if (!wrapper) return;
        
        wrapper.innerHTML = '';
        if (queryHighlight) queryHighlight.innerText = `"${this.globalSearchQuery}"`;
        
        const query = this.globalSearchQuery.toLowerCase();
        if (!query) {
            if (resultsCountEl) resultsCountEl.innerText = '0';
            wrapper.innerHTML = `<div class="no-results">${this.currentLang === 'es' ? 'Ingrese un término de búsqueda.' : 'Enter a search term.'}</div>`;
            return;
        }
        
        let results = [];
        
        // Loop through all KB items
        for (const techKey in this.data.KB) {
            const tech = this.data.KB[techKey];
            const techName = this.getLocalizedText(tech, 'name') || '';
            const techDesc = this.getLocalizedText(tech, 'description') || '';
            
            // 1. Check technology match
            if (techName.toLowerCase().includes(query) || techDesc.toLowerCase().includes(query) || techKey.toLowerCase().includes(query)) {
                results.push({
                    type: 'tech',
                    techKey: techKey,
                    title: techName,
                    description: techDesc,
                    badge: this.currentLang === 'es' ? 'Tecnología' : 'Technology'
                });
            }
            
            // 2. Check steps matches
            if (tech.steps) {
                for (const stepKey in tech.steps) {
                    const step = tech.steps[stepKey];
                    const stepTitle = this.getLocalizedText(step, 'title') || '';
                    const stepBody = this.getLocalizedText(step, 'body') || '';
                    const stepHypothesis = this.getLocalizedText(step, 'hypothesis') || '';
                    const stepBasis = this.getLocalizedText(step, 'scientific_basis') || '';
                    
                    let stepMatched = false;
                    let matchDetails = '';
                    
                    if (stepTitle.toLowerCase().includes(query)) {
                        stepMatched = true;
                        matchDetails = this.currentLang === 'es' ? 'Coincidencia en el título del paso.' : 'Match in step title.';
                    } else if (stepBody.toLowerCase().includes(query)) {
                        stepMatched = true;
                        matchDetails = this.currentLang === 'es' ? 'Coincidencia en el cuerpo del diagnóstico.' : 'Match in diagnostics details.';
                    } else if (stepHypothesis.toLowerCase().includes(query)) {
                        stepMatched = true;
                        matchDetails = this.currentLang === 'es' ? 'Coincidencia en la hipótesis.' : 'Match in hypothesis.';
                    } else if (stepBasis.toLowerCase().includes(query)) {
                        stepMatched = true;
                        matchDetails = this.currentLang === 'es' ? 'Coincidencia en la base científica.' : 'Match in scientific basis.';
                    }
                    
                    if (stepMatched) {
                        results.push({
                            type: 'step',
                            techKey: techKey,
                            stepKey: stepKey,
                            title: `${techName} — ${stepTitle}`,
                            description: matchDetails,
                            badge: `Tier ${step.tier || 1} — ${this.currentLang === 'es' ? 'Paso de Diagnóstico' : 'Diagnostic Step'}`
                        });
                    }
                    
                    // 3. Check command matches
                    if (step.commands) {
                        let cmdMatched = false;
                        let matchedCmdText = '';
                        let matchedVendor = '';
                        let matchedTier = '';
                        
                        for (const vendorKey in step.commands) {
                            const vendorCmdsByTier = step.commands[vendorKey] || {};
                            for (const tierKey in vendorCmdsByTier) {
                                const cmdList = vendorCmdsByTier[tierKey] || [];
                                for (const cmd of cmdList) {
                                    if (cmd.toLowerCase().includes(query)) {
                                        cmdMatched = true;
                                        matchedCmdText = cmd;
                                        matchedVendor = this.data.VendorMap[vendorKey] || vendorKey;
                                        matchedTier = tierKey.replace('tier', 'Tier ').replace('arch', 'Tier 4 (Arch)');
                                        break;
                                    }
                                }
                                if (cmdMatched) break;
                            }
                            if (cmdMatched) break;
                        }
                        
                        if (cmdMatched) {
                            results.push({
                                type: 'command',
                                techKey: techKey,
                                stepKey: stepKey,
                                title: `${techName} — ${stepTitle}`,
                                description: `${this.currentLang === 'es' ? 'Comando' : 'Command'}: <code>${this.escapeHtml(matchedCmdText)}</code> (${matchedVendor} / ${matchedTier})`,
                                badge: this.currentLang === 'es' ? 'Comando CLI' : 'CLI Command'
                            });
                        }
                    }
                }
            }
        }
        
        if (resultsCountEl) resultsCountEl.innerText = results.length;
        
        if (results.length === 0) {
            wrapper.innerHTML = `<div class="no-results"><i data-lucide="alert-circle"></i> ${this.currentLang === 'es' ? 'No se encontraron resultados para su búsqueda.' : 'No results found for your search.'}</div>`;
            if (window.lucide) window.lucide.createIcons();
            return;
        }
        
        results.forEach(res => {
            const card = document.createElement('div');
            card.className = 'search-result-card';
            
            if (res.type === 'tech') {
                card.onclick = () => {
                    this.selectTechnology(res.techKey);
                };
            } else {
                card.onclick = () => {
                    this.activeTech = res.techKey;
                    this.currentStepKey = res.stepKey;
                    this.history = [];
                    
                    // Switch tab and load layout
                    const isConfig = res.techKey.endsWith('_config');
                    this.switchSidebarTab(isConfig ? 'config' : 'ts');
                    this.showView('flow');
                    this.renderFlowHeader();
                    this.renderVendorButtons();
                    this.renderCurrentStep();
                };
            }
            
            card.innerHTML = `
                <div class="result-header">
                    <span class="result-badge">${res.badge}</span>
                    <h3>${res.title}</h3>
                </div>
                <p>${res.description}</p>
            `;
            wrapper.appendChild(card);
        });
        
        if (window.lucide) window.lucide.createIcons();
    }

    replaceMarkdown(text) {
        if (!text) return '';
        let html = this.escapeHtml(text);
        
        // Replace bold **text**
        html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        // Replace bulleted points
        html = html.replace(/^[•-]\s*(.+)$/gm, '<li>$1</li>');
        // Replace line breaks
        html = html.replace(/\n/g, '<br>');
        
        // Wrap <li> inside <ul>
        if (html.includes('<li>')) {
            // Basic wrapping logic
            html = html.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');
        }
        
        return html;
    }

    switchLanguage(lang) {
        console.log(`Cambiando idioma a: ${lang}`);
        this.currentLang = lang;
        localStorage.setItem('net_tshoot_lang', lang);
        
        // Update language button state
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.id === `lang-btn-${lang}`);
        });
        
        this.translateUI();
        
        // Re-render active views to reflect translations
        this.renderSidebar();
        this.renderSidebarVariables();
        this.renderSidebarNotes();
        this.renderSidebarHypotheses();
        
        if (this.activeView === 'home') {
            // Static translations are handled by translateUI()
        } else if (this.activeView === 'flow') {
            this.renderFlowHeader();
            this.renderCurrentStep();
        } else if (this.activeView === 'simulator') {
            this.renderSimulatorTimeline();
            this.renderSimulatorStep();
            if (this.activeSimScenario) {
                document.getElementById('selected-scenario-name').innerText = this.getLocalizedText(this.activeSimScenario, 'name');
            }
        } else if (this.activeView === 'search') {
            this.renderSearchResults();
        }
    }

    getLocalizedText(obj, field) {
        if (!obj) return '';
        if (this.currentLang === 'en') {
            if (obj[field + '_en']) {
                return obj[field + '_en'];
            }
            // Dynamic concept translations if they are standard keys
            if (field === 'definition' || field === 'key_concepts' || field === 'architecture' || field === 'control_vs_data' || field === 'troubleshooting_strategy' || field === 'configuration_basics') {
                const conceptTranslations = {
                    'bgp': {
                        'definition': 'Border Gateway Protocol (BGP) is the core routing protocol of the Internet, allowing routing path-vector information exchange between Autonomous Systems (AS).',
                        'key_concepts': '- **AS (Autonomous System)**: Group of IP networks under single control.\n- **iBGP vs eBGP**: Internal peers (same AS) vs External peers (different AS).\n- **Path Attributes**: AS-Path, Local Preference, MED, Origin, Next-Hop, Community.\n- **Split Horizon**: iBGP routes are not advertised to other iBGP peers to prevent routing loops.',
                        'architecture': 'BGP runs over TCP port 179. It is a reliable connection-oriented protocol that starts in IDLE, transitions through CONNECT, ACTIVE, OPENSENT, OPENCONFIRM, and finally ESTABLISHED.',
                        'control_vs_data': '- **Control Plane**: TCP 179 session, exchanged UPDATE messages, Adj-RIB-In, Local-RIB, Adj-RIB-Out.\n- **Data Plane**: FIB routing tables forwarding IP traffic based on selected best paths.',
                        'troubleshooting_strategy': '1. Check TCP Layer connectivity (Ping, Telnet port 179).\n2. Verify peer state: Idle/Active indicates TCP negotiation failure (check routing/ACLs).\n3. Inspect advertised and received routes to verify export/import policies.',
                        'configuration_basics': 'Configure Autonomous System, define neighbor IP and remote-as, configure address-family (IPv4 Unicast), and apply export/import policies.'
                    },
                    'static': {
                        'definition': 'Static routing is the manual configuration of network routes. Unlike dynamic routing, it does not adapt automatically to topology changes, requiring administrative intervention for redundancy. Diagnostics focus on route presence, next-hop reachability, recursive lookup loops, and floating route precedence.',
                        'key_concepts': '- **RIB (Routing Information Base)**: Routing table containing all learned routes.\n- **FIB (Forwarding Information Base)**: Data-plane forwarding table with only the active best paths.\n- **LPM (Longest Prefix Match)**: Metric that prefers the most specific route prefix.\n- **Recursive Lookup**: Resolving a next-hop through another routing table entry.',
                        'architecture': 'Static routes are processed in the control plane (RIB). If the next-hop is reachable, the route is installed in the data plane (FIB).',
                        'control_vs_data': '- **Control Plane**: Interface status evaluation, next-hop resolution, and RIB installation.\n- **Data Plane**: Packet forwarding via LPM in the FIB.',
                        'troubleshooting_strategy': '1. Verify route configuration and presence in the RIB.\n2. Confirm next-hop reachability (ping/physical link status).\n3. Check recursive route resolution.\n4. Verify distance/precedence against other protocols.',
                        'configuration_basics': 'Define destination prefix, subnet mask, next-hop IP or egress interface, and optionally specify administrative distance.'
                    },
                    'static_config': {
                        'definition': 'Configuration of static routes to manually define forwarding paths. Includes standard routes, floating backup routes, ECMP load balancing, and track associations (SLA/BFD) for automatic removal.',
                        'key_concepts': '- **Floating Route**: Backup route with higher administrative distance.\n- **ECMP (Equal-Cost Multi-Path)**: Active-active load balancing over multiple routes.\n- **IP SLA**: Tracking destination reachability to dynamically drop/activate routes.\n- **Static BFD**: Sub-second bidirectional link failure detection.',
                        'architecture': 'Routers apply static route rules to the forwarding plane. When tracking is enabled, the control plane monitors destination health and updates the FIB accordingly.',
                        'control_vs_data': '- **Control Plane**: Provisioning routes, SLA/BFD timers, and RIB updates.\n- **Data Plane**: Forwarding traffic over the interface selected by hashing/active paths.',
                        'troubleshooting_strategy': '1. Verify prefix/mask syntax across vendors.\n2. Check administrative distance order.\n3. Verify SLA tracker status.\n4. Check static BFD session state.',
                        'configuration_basics': 'Add static route with next-hop. For backup, append metric/preference. For SLA/BFD, define tracker and link it to the route.'
                    },
                    'nat': {
                        'definition': 'Network Address Translation (NAT) modifies IP addresses and ports in packet headers in transit. It conserves IPv4 address space by allowing private hosts to share public IPs, and hides internal network topology.',
                        'key_concepts': '- **Source NAT (SNAT)**: Translates source IP (many-to-one / MASQUERADE).\n- **Destination NAT (DNAT)**: Translates destination IP (Port Forwarding / VIP).\n- **PAT (Port Address Translation)**: Translates ports to track multiple connections per IP.',
                        'architecture': 'NAT works in the IP stack using state tables. When a packet passes, the device updates headers and registers mapping in its translation table.',
                        'control_vs_data': '- **Control Plane**: Rulesets, pools, timeouts, and state table updates.\n- **Data Plane**: Rewriting headers and updating checksums at line speed.',
                        'troubleshooting_strategy': '1. Check active translation table and session count.\n2. Verify port/session exhaustion.\n3. Run flow traces or packet captures.',
                        'configuration_basics': 'Configure interface zones, define rules matching traffic, and allocate IP translation pools.'
                    },
                    'nat_config': {
                        'definition': 'Configuration of SNAT, DNAT, and Static NAT. Includes configuring IP pools, overload/PAT rules, port forwarding (Virtual IP), and 1:1 bidirectional mapping.',
                        'key_concepts': '- **Dynamic NAT/PAT Pool**: Range of public IPs for outbound translation.\n- **Virtual IP (VIP)**: External IP/port mapping to internal server.\n- **Static NAT (1:1)**: Bidirectional mapping between private and public IP.',
                        'architecture': 'The system processes rules based on flow hooks (Prerouting for DNAT, Postrouting for SNAT). The translation engine creates state sessions to handle replies.',
                        'control_vs_data': '- **Control Plane**: Rule configuration, pool definition, and binding mappings.\n- **Data Plane**: Hashing, pool allocation, and header rewriting.',
                        'troubleshooting_strategy': '1. Verify NAT rules matching conditions.\n2. Confirm IP pool range and interface assignments.\n3. Check security policies allowing translated IPs.',
                        'configuration_basics': 'Define NAT policy, specify source/destination criteria, map translation action, and bind to interface.'
                    },
                    'linux_tshoot': {
                        'definition': 'Network troubleshooting in Linux using iproute2 tools (ip link, ip addr, ip route, ss, ip neigh), netfilter utilities (iptables, nft, conntrack), and packet capture tools (tcpdump, tshark) to diagnose issues from the physical layer (L1) to the application layer (L7).',
                        'key_concepts': '- **iproute2**: Modern Linux networking tools interacting via netlink.\n- **Netfilter/conntrack**: Kernel framework for filtering, NAT, and connection tracking.\n- **tcpdump/tshark**: Packet capture tools using libpcap.\n- **Routing Policy Database (RPDB)**: Custom routing tables selected via ip rule.',
                        'architecture': 'The Linux kernel processes packets through Netfilter hooks: PREROUTING (DNAT) -> Route Lookup -> INPUT (local processes) / FORWARD (routing) -> OUTPUT -> POSTROUTING (SNAT/MASQUERADE).',
                        'control_vs_data': '- **Control Plane**: Management of routing tables, rules, firewall rulesets, and conntrack entries.\n- **Data Plane**: Kernel-level packet forwarding, filtering, and header modification.',
                        'troubleshooting_strategy': '1. Verify interface state and duplex (ip link, ethtool).\n2. Check route table and ARP cache (ip route get, ip neigh).\n3. Inspect firewall rules and connection table (iptables -L, conntrack -L).\n4. Perform packet captures (tcpdump, tshark).',
                        'configuration_basics': 'Configure routing (ip route add), enable packet forwarding (sysctl net.ipv4.ip_forward=1), add firewall/NAT rules (iptables -t nat -A), and capture packets (tcpdump -i eth0).'
                    },
                    'ip_trace': {
                        'definition': 'End-to-end IP tracing (A -> B) is the systematic methodology used to track the logical and physical path of a packet across multiple hops (routers, switches, firewalls) in the OSI/TCP-IP model. Its main goal is to identify the exact point where a packet or its return traffic is dropped or modified.',
                        'key_concepts': '• **Longest Prefix Match (LPM):** A data-plane forwarding algorithm that prefers the most specific subnet mask (e.g., /28 over /24) to forward a packet.\n• **Recursive Lookup:** A control-plane process where a router recursively resolves the exit interface for a next-hop IP address.\n• **Symmetric vs Asymmetric Routing:** Symmetric routing means traffic flows along the same path in both directions (A -> B and B -> A). Asymmetric routing uses different paths, which frequently triggers packet drops in stateful firewalls.\n• **Path MTU Discovery (PMTUD):** An ICMP-based process to discover the lowest MTU link along the end-to-end path, preventing silent packet fragmentation drops.',
                        'architecture': 'Each transit router performs Layer 2 decapsulation (Ethernet), decrements the IP header TTL by 1, recalculates the IP checksum, and re-encapsulates the packet with a new Layer 2 header (source MAC of the router, destination MAC of the next-hop). The source and destination IPs remain unchanged unless NAT (Network Address Translation) is applied.',
                        'control_vs_data': '• **Control Plane:** Routing protocols (OSPF, BGP, etc.) exchange network prefixes to populate the Routing Information Base (RIB).\n• **Data Plane:** Specialized ASICs search the Forwarding Information Base (FIB) to switch packets at line rate.',
                        'troubleshooting_strategy': '1. **Step 1 (Source and local L2):** Verify physical and Layer 2 connectivity to the local Default Gateway using ping and ARP.\n2. **Step 2 (Traceroute):** Run traceroute/tracert from the source host to pinpoint the last responding hop and narrow down the failure area.\n3. **Step 3 (Hop-by-hop Routing):** Access the last responsive hop router, check routing table entries for the destination prefix using LPM, and repeat this process hop-by-hop.\n4. **Step 4 (Firewall/NAT and Return Path):** Check security policies (ACLs) and state connection tables (conntrack) in firewalls to eliminate firewall blocks and ensure a valid return routing path exists.',
                        'configuration_basics': '• Ensure default gateways are correctly configured on all hosts.\n• Configure routing protocols and interface IPs consistently across all hops.\n• Prevent asymmetric routing across stateful security devices, or configure session synchronization if needed.'
                    }
                };
                
                const techKey = this.activeTech;
                const baseTechKey = techKey ? techKey.replace('_config', '') : '';
                
                if (conceptTranslations[techKey] && conceptTranslations[techKey][field]) {
                    return conceptTranslations[techKey][field];
                } else if (conceptTranslations[baseTechKey] && conceptTranslations[baseTechKey][field]) {
                    return conceptTranslations[baseTechKey][field];
                }
            }
            // Dynamic translation for technology selector names
            if (field === 'name') {
                const enNames = {
                    'static': 'Static Routing - TS',
                    'ip_trace': 'End-to-End IP Tracing - TS',
                    'static_config': 'Static Routing - Config',
                    'linux_tshoot': 'Linux Network Troubleshooting - TS',
                    'nat': 'NAT (Source, Dest, Static) - TS',
                    'nat_config': 'Advanced NAT - Config',
                    'bgp': 'BGP (Border Gateway Protocol) - TS',
                    'bgp_config': 'Advanced BGP Policies - Config',
                    'mpls': 'MPLS & LDP - TS',
                    'evpn': 'EVPN / VXLAN Control Plane - TS',
                    'vxlan': 'VXLAN Overlay - TS',
                    'spanning_tree': 'Spanning Tree (RSTP) - TS',
                    'ipv6': 'IPv6 & NDP - TS',
                    'netflow': 'NetFlow/IPFIX - TS',
                    'sdwan': 'SD-WAN - TS',
                    'sr_mpls': 'Segment Routing MPLS - TS',
                    'dmvpn': 'DMVPN Phase 3 - TS',
                    'eigrp': 'EIGRP Routing - TS',
                    'pbr': 'Policy-Based Routing - TS',
                    'security': 'Stateful Firewall & ACL - TS',
                    'switch_l2': 'Layer 2 Switching - TS',
                    'vrrp_hsrp': 'VRRP / HSRP Redundancy - TS',
                    'rstp': 'RSTP Convergence - TS',
                    'dhcp': 'DHCPv4 & Relay - TS',
                    'netflow_ipfix': 'NetFlow v9 / IPFIX - TS',
                    'ipv6_ndp': 'IPv6 & Neighbor Discovery - TS',
                    'ospf': 'OSPF Routing - TS',
                    'isis': 'IS-IS Routing - TS',
                    'mpbgp': 'MP-BGP EVPN - TS',
                    'aaa': 'AAA (RADIUS/TACACS+) - TS',
                    'fiber_ont': 'GPON/FTTH Broadband - TS',
                    'ccc_interface_switch': 'CCC Interface Switching - TS',
                    'wireshark_tcpdump': 'Wireshark & tcpdump - TS',
                    'subnet_31': 'Subnet Mask /31 - TS'
                };
                
                const id = obj.id || '';
                if (id) {
                    if (enNames[id]) {
                        return enNames[id];
                    }
                    if (id.endsWith('_config')) {
                        const baseId = id.replace('_config', '');
                        if (enNames[baseId]) {
                            return enNames[baseId].replace(' - TS', '') + ' - Config';
                        }
                        const configNames = {
                            'ospf': 'OSPF Routing - Config',
                            'isis': 'IS-IS Routing - Config',
                            'l2vpn': 'L2VPN - Config',
                            'l3vpn': 'L3VPN - Config',
                            'mpbgp': 'MP-BGP EVPN - Config',
                            'mpls': 'MPLS & LDP - Config',
                            'multicast': 'Multicast - Config',
                            'netflow': 'NetFlow/IPFIX - Config',
                            'spanning_tree': 'Spanning Tree (RSTP) - Config',
                            'switch_l2': 'Layer 2 Switching - Config',
                            'vxlan': 'VXLAN Overlay - Config',
                            'vrrp_hsrp': 'VRRP / HSRP Redundancy - Config',
                            'dhcp': 'DHCPv4 & Relay - Config',
                            'ipv6': 'IPv6 & NDP - Config',
                            'dmvpn': 'DMVPN Phase 3 - Config',
                            'eigrp': 'EIGRP Routing - Config',
                            'pbr': 'Policy-Based Routing - Config',
                            'sdwan': 'SD-WAN - Config',
                            'fiber_ont': 'GPON/FTTH Broadband - Config',
                            'aaa': 'AAA (RADIUS/TACACS+) - Config'
                        };
                        if (configNames[baseId]) return configNames[baseId];
                    }
                }
                
                if (enNames[obj.id] || enNames[obj.name]) {
                    return enNames[obj.id] || enNames[obj.name];
                }
                for (const [k, v] of Object.entries(enNames)) {
                    if (obj.name && obj.name.toLowerCase().startsWith(k.replace('_', ' '))) {
                        return v;
                    }
                }
            }
            // Dynamic translation for choice labels
            if (field === 'label') {
                const commonChoices = {
                    'establecido': 'Established',
                    'no establecido': 'Not Established / Active / Idle',
                    'bgp md5': 'BGP MD5 Authentication',
                    'volver al menú': 'Back to Menu',
                    'siguiente paso': 'Next Step',
                    'sí': 'Yes',
                    'no': 'No',
                    'aceptar': 'Accept',
                    'denegar': 'Deny',
                    'continuar': 'Continue',
                    'solución': 'Solution',
                    'verificar de nuevo': 'Verify Again',
                    'reiniciar': 'Restart'
                };
                const textLower = (obj.label || '').toLowerCase();
                for (const [k, v] of Object.entries(commonChoices)) {
                    if (textLower.includes(k)) {
                        return v;
                    }
                }
            }
        }
        return obj[field] || '';
    }

    translateUI() {
        const t = (k) => uiTranslations[this.currentLang][k] || k;
        
        // Logo & header
        const logoSpan = document.querySelector('.logo-text span');
        if (logoSpan) logoSpan.innerText = t('appSubtitle');
        
        const searchInput = document.getElementById('global-search-input');
        if (searchInput) searchInput.placeholder = t('filterPlaceholder');
        
        const sessionTierLabel = document.getElementById('lbl-session-tier');
        if (sessionTierLabel) sessionTierLabel.innerText = t('sessionTierLabel');

        const scientificLabel = document.getElementById('lbl-scientific-mode');
        if (scientificLabel) scientificLabel.innerText = t('lblScientificMode');
        
        const btnNormal = document.querySelector('.scientific-btn[data-mode="normal"]');
        const btnSemiStrict = document.querySelector('.scientific-btn[data-mode="semi_strict"]');
        const btnStrict = document.querySelector('.scientific-btn[data-mode="strict"]');
        if (btnNormal) btnNormal.innerText = t('btnScientificNormal');
        if (btnSemiStrict) btnSemiStrict.innerText = t('btnScientificSemiStrict');
        if (btnStrict) btnStrict.innerText = t('btnScientificStrict');
        
        this.updateScientificModeButtonsState();
        
        // Session Tier Selector Options
        const opt1 = document.getElementById('opt-tier1');
        const opt2 = document.getElementById('opt-tier2');
        const opt3 = document.getElementById('opt-tier3');
        const opt4 = document.getElementById('opt-tier4');
        if (opt1) opt1.innerText = this.currentLang === 'es' ? 'Tier 1 — Operador NOC' : 'Tier 1 — NOC Operator';
        if (opt2) opt2.innerText = this.currentLang === 'es' ? 'Tier 2 — Soporte Técnico' : 'Tier 2 — Tech Support';
        if (opt3) opt3.innerText = this.currentLang === 'es' ? 'Tier 3 — Escalación' : 'Tier 3 — Escalation';
        if (opt4) opt4.innerText = this.currentLang === 'es' ? 'Tier 4 — Arquitecto' : 'Tier 4 — Architect';

        // Left Sidebar
        const sidebarTitle = document.querySelector('#sidebar-left .sidebar-header h2');
        if (sidebarTitle) sidebarTitle.innerText = t('techTitle');
        
        const filterInput = document.getElementById('tech-filter');
        if (filterInput) filterInput.placeholder = t('filterPlaceholder');
        
        const tabTs = document.getElementById('tab-btn-ts');
        if (tabTs) tabTs.innerText = t('tabTroubleshooting');
        
        const tabConfig = document.getElementById('tab-btn-config');
        if (tabConfig) tabConfig.innerText = t('tabConfig');
        
        const simBtnSpan = document.querySelector('.simulator-btn span');
        if (simBtnSpan) simBtnSpan.innerText = t('btnOsiSim');
        
        // Right Sidebar
        const bitacoraHeader = document.querySelector('#sidebar-right .sidebar-header h2');
        if (bitacoraHeader) bitacoraHeader.innerText = t('bitacoraTitle');
        
        const activeVarsHeader = document.querySelector('.active-vars-section h3');
        if (activeVarsHeader) activeVarsHeader.innerText = t('bitacoraActiveVars');
        
        const notesLogHeader = document.querySelector('.notes-log-section h3');
        if (notesLogHeader) notesLogHeader.innerText = t('bitacoraNotesLogged');
        
        const exportBtnSpan = document.querySelector('.btn-export span');
        if (exportBtnSpan) exportBtnSpan.innerText = t('btnExport');
        
        // Home view static translation
        const welcomeBadge = document.querySelector('.welcome-badge');
        if (welcomeBadge) welcomeBadge.innerText = t('welcomeBadge');
        
        const welcomeTitle = document.querySelector('.welcome-card h2');
        if (welcomeTitle) welcomeTitle.innerText = t('welcomeTitle');
        
        const welcomeDesc = document.querySelector('.welcome-card p');
        if (welcomeDesc) welcomeDesc.innerText = t('welcomeDesc');
        
        const welcomeSearchSpan = document.querySelector('.welcome-actions button:nth-child(1) span');
        if (welcomeSearchSpan) welcomeSearchSpan.innerText = t('btnSearchStart');
        
        const welcomeSimSpan = document.querySelector('.welcome-actions button:nth-child(2) span');
        if (welcomeSimSpan) welcomeSimSpan.innerText = t('btnViewSims');
        
        // Home Stats
        const stat1H = document.querySelector('.quick-stats-grid .stat-card:nth-child(1) h3');
        const stat1P = document.querySelector('.quick-stats-grid .stat-card:nth-child(1) p');
        if (stat1H) stat1H.innerText = t('statsVendors');
        if (stat1P) stat1P.innerText = t('statsVendorsDesc');
        
        const stat2H = document.querySelector('.quick-stats-grid .stat-card:nth-child(2) h3');
        const stat2P = document.querySelector('.quick-stats-grid .stat-card:nth-child(2) p');
        if (stat2H) stat2H.innerText = t('statsTechs');
        if (stat2P) stat2P.innerText = t('statsTechsDesc');
        
        const stat3H = document.querySelector('.quick-stats-grid .stat-card:nth-child(3) h3');
        const stat3P = document.querySelector('.quick-stats-grid .stat-card:nth-child(3) p');
        if (stat3H) stat3H.innerText = t('statsCmds');
        if (stat3P) stat3P.innerText = t('statsCmdsDesc');
        
        // Home access quick
        const accessTitle = document.querySelector('.home-tech-section h3');
        if (accessTitle) accessTitle.innerText = t('accessQuickTitle');
        
        // Home Quick tech cards titles & descriptions
        const cardItems = document.querySelectorAll('.tech-cards-grid .tech-card-item');
        if (cardItems.length >= 6) {
            // NAT TS
            cardItems[0].querySelector('h4').innerText = t('quickNat');
            cardItems[0].querySelector('p').innerText = t('quickNatDesc');
            // NAT Config
            cardItems[1].querySelector('h4').innerText = t('quickNatConfig');
            cardItems[1].querySelector('p').innerText = t('quickNatConfigDesc');
            // BGP TS
            cardItems[2].querySelector('h4').innerText = t('quickBgp');
            cardItems[2].querySelector('p').innerText = t('quickBgpDesc');
            // BGP Config
            cardItems[3].querySelector('h4').innerText = t('quickBgpConfig');
            cardItems[3].querySelector('p').innerText = t('quickBgpConfigDesc');
            // MPLS TS
            cardItems[4].querySelector('h4').innerText = 'MPLS & LDP';
            cardItems[4].querySelector('p').innerText = t('quickMplsDesc');
            // EVPN TS
            cardItems[5].querySelector('h4').innerText = t('quickEvpn');
            cardItems[5].querySelector('p').innerText = t('quickEvpnDesc');
        }
        
        // Central Flow view static
        const vendorLabel = document.querySelector('.vendor-selector-group label');
        if (vendorLabel) vendorLabel.innerText = t('lblSelectVendor');
        
        const tierLabel = document.querySelector('.tier-selector-group label');
        if (tierLabel) tierLabel.innerText = t('lblSelectTier');
        
        const theoryTitle = document.querySelector('#theory-collapsible .header-left h3');
        if (theoryTitle) theoryTitle.innerText = t('lblTheoryTitle');
        
        // Theory Tabs
        const theoryTabBtns = document.querySelectorAll('.concepts-tabs .concept-tab-btn');
        if (theoryTabBtns.length >= 6) {
            theoryTabBtns[0].innerText = t('tabDef');
            theoryTabBtns[1].innerText = t('tabKey');
            theoryTabBtns[2].innerText = t('tabArch');
            theoryTabBtns[3].innerText = t('tabCtrl');
            theoryTabBtns[4].innerText = t('tabTshoot');
            theoryTabBtns[5].innerText = t('tabBasics');
        }
        
        // Variables header
        const varHeader = document.querySelector('.vars-box-header h4');
        if (varHeader) varHeader.innerText = t('lblVarsBoxTitle');
        
        // Terminal Copy
        const copyBtnSpan = document.querySelector('.terminal-header .btn-copy span');
        if (copyBtnSpan) copyBtnSpan.innerText = t('lblCopyCmds');
        
        // Expected outcome
        const expectedHeader = document.querySelector('.expected-header h4');
        if (expectedHeader) expectedHeader.innerText = t('lblExpectedOutcome');
        
        // Notes label
        const notesLabel = document.querySelector('.step-note-container label span');
        if (notesLabel) notesLabel.innerText = t('lblNotesLabel');
        
        const notesTextarea = document.getElementById('step-note-textarea');
        if (notesTextarea) notesTextarea.placeholder = t('lblNotesPlaceholder');
        
        const savedIndicator = document.getElementById('note-saved-indicator');
        if (savedIndicator) {
            savedIndicator.innerHTML = `<i data-lucide="check" style="width:12px;height:12px;"></i> ${t('lblNotesSaved')}`;
        }
        
        // Choice box title
        const choiceBoxTitle = document.querySelector('.step-navigation-box h4');
        if (choiceBoxTitle) choiceBoxTitle.innerText = t('lblNextActionTitle');
        
        // Simulator View static
        const simTitle = document.getElementById('lbl-sim-title');
        if (simTitle) simTitle.innerText = t('lblSimTitle');
        
        const simDesc = document.getElementById('lbl-sim-desc');
        if (simDesc) simDesc.innerText = t('lblSimDesc');
        
        const activeScenarioTitle = document.getElementById('lbl-active-scenario-title');
        if (activeScenarioTitle) activeScenarioTitle.innerText = t('lblActiveScenario');
        
        const scenarioStateTitle = document.getElementById('lbl-scenario-state-title');
        if (scenarioStateTitle) scenarioStateTitle.innerText = t('lblScenarioState');
        
        const lblSimStateFail = document.getElementById('lbl-sim-state-fail');
        if (lblSimStateFail) lblSimStateFail.innerText = t('lblSimStateFail');
        
        const lblSimStateOk = document.getElementById('lbl-sim-state-ok');
        if (lblSimStateOk) lblSimStateOk.innerText = t('lblSimStateOk');
        
        const timelineTitle = document.querySelector('#simulator-timeline-card h3');
        if (timelineTitle) timelineTitle.innerText = t('lblSimTimeline');
        
        // Modal static
        const modalTitleEl = document.getElementById('modal-title-text');
        if (modalTitleEl) modalTitleEl.innerText = t('modalTitle');
        
        const modalSearchInput = document.getElementById('modal-scenario-search');
        if (modalSearchInput) modalSearchInput.placeholder = t('modalSearchPlaceholder');
        
        // Search View static
        const searchTitleEl = document.querySelector('.search-header-card h2');
        if (searchTitleEl) searchTitleEl.innerText = t('searchTitle');
        
        // Console Sandbox translations
        const lblTermCmds = document.getElementById('lbl-term-mode-cmds');
        if (lblTermCmds) lblTermCmds.innerText = t('lblTerminalCommands');
        
        const lblTermSim = document.getElementById('lbl-term-mode-sim');
        if (lblTermSim) lblTermSim.innerText = t('lblTerminalSimulate');
        
        const lblRunSim = document.getElementById('lbl-run-sim');
        if (lblRunSim) lblRunSim.innerText = t('lblRunSim');
        
        const lblClearSim = document.getElementById('lbl-clear-sim');
        if (lblClearSim) lblClearSim.innerText = t('lblClearSim');
        
        // Automation Corner translations
        const autoHeaderH2 = document.querySelector('.automation-header-card h2');
        if (autoHeaderH2) autoHeaderH2.innerText = t('autoHeaderTitle');
        
        const autoHeaderP = document.querySelector('.automation-header-card p');
        if (autoHeaderP) autoHeaderP.innerText = t('autoHeaderDesc');
        
        const autoSidebarH3 = document.querySelector('.auto-sidebar h3');
        if (autoSidebarH3) autoSidebarH3.innerText = t('autoSidebarTitle');
        
        const autoSearchInput = document.getElementById('auto-script-search');
        if (autoSearchInput) autoSearchInput.placeholder = t('autoSearchPlaceholder');
        
        const autoEmptyP = document.querySelector('.auto-detail-empty p');
        if (autoEmptyP) autoEmptyP.innerText = t('autoEmptyState');
        
        const autoVarsH4 = document.querySelector('.auto-variables-section h4');
        if (autoVarsH4) autoVarsH4.innerText = t('autoVarsTitle');
        
        const autoNoteTitleSpan = document.querySelector('.auto-architect-note .note-title span');
        if (autoNoteTitleSpan) autoNoteTitleSpan.innerText = t('autoNoteTitle');
        
        const autoTabPythonBtn = document.getElementById('code-tab-python');
        if (autoTabPythonBtn) autoTabPythonBtn.innerText = t('autoTabPython');
        
        const autoTabAnsibleBtn = document.getElementById('code-tab-ansible');
        if (autoTabAnsibleBtn) autoTabAnsibleBtn.innerText = t('autoTabAnsible');
        
        const autoTabApiBtn = document.getElementById('code-tab-api');
        if (autoTabApiBtn) autoTabApiBtn.innerText = t('autoTabApi');
        
        const copyAutoText = document.getElementById('lbl-copy-auto-text');
        if (copyAutoText) {
            copyAutoText.innerText = this.copiedAutoTimeout ? t('autoBtnCopied') : t('autoBtnCopy');
        }
        
        const autoTriggerSpan = document.querySelector('#btn-automation-trigger span');
        if (autoTriggerSpan) autoTriggerSpan.innerText = t('btnAutomation');

        const lblAutoConcepts = document.getElementById('lbl-auto-concepts');
        if (lblAutoConcepts) lblAutoConcepts.innerText = t('lblAutoConcepts');
        
        const lblAutoVendors = document.getElementById('lbl-auto-vendors');
        if (lblAutoVendors) lblAutoVendors.innerText = t('lblAutoVendors');
        
        const lblAutoLibrary = document.getElementById('lbl-auto-library');
        if (lblAutoLibrary) lblAutoLibrary.innerText = t('lblAutoLibrary');

        const lblAutoMatrixTitle = document.getElementById('lbl-auto-matrix-title');
        if (lblAutoMatrixTitle) lblAutoMatrixTitle.innerText = t('lblAutoMatrixTitle');

        const lblAutoMatrixDesc = document.getElementById('lbl-auto-matrix-desc');
        if (lblAutoMatrixDesc) lblAutoMatrixDesc.innerText = t('lblAutoMatrixDesc');

        const lblMatrixTech = document.getElementById('lbl-matrix-tech');
        if (lblMatrixTech) lblMatrixTech.innerText = t('lblMatrixTech');

        const lblMatrixVendor = document.getElementById('lbl-matrix-vendor');
        if (lblMatrixVendor) lblMatrixVendor.innerText = t('lblMatrixVendor');

        // Update vendor matrix details if visible
        this.renderVendorMatrixDetails();
        
        lucide.createIcons();
    }

    // ==========================================================================
    // CLI SANDBOX SIMULATOR & INTERACTIVE EXECUTION
    // ==========================================================================
    setTerminalMode(mode) {
        this.terminalMode = mode;
        
        const btnCmds = document.getElementById('term-mode-cmds');
        const btnSim = document.getElementById('term-mode-sim');
        const wrapCmds = document.getElementById('terminal-commands-wrapper');
        const wrapSim = document.getElementById('terminal-simulation-wrapper');
        const btnCopy = document.getElementById('btn-copy-cmds');
        
        if (btnCmds) btnCmds.classList.toggle('active', mode === 'cmds');
        if (btnSim) btnSim.classList.toggle('active', mode === 'sim');
        
        if (wrapCmds) wrapCmds.classList.toggle('hidden', mode !== 'cmds');
        if (wrapSim) wrapSim.classList.toggle('hidden', mode !== 'sim');
        if (btnCopy) btnCopy.classList.toggle('hidden', mode !== 'cmds');
        
        if (mode === 'sim') {
            const outputEl = document.getElementById('terminal-simulation-output');
            if (outputEl && !outputEl.innerHTML.trim()) {
                this.clearSimulationScreen();
            }
            
            // Toggle visibility of Golden baseline button based on command presence
            const steps = this.data.KB[this.activeTech].steps || {};
            const step = steps[this.currentStepKey];
            const rawCmds = (step && step.commands && step.commands[this.activeVendor]) || [];
            const cmds = this.flattenCommandsByTier(rawCmds);
            
            const btnGolden = document.getElementById('btn-golden-sim');
            if (btnGolden) {
                btnGolden.style.display = cmds.length > 0 ? 'inline-flex' : 'none';
            }
        }
    }

    clearSimulationScreen() {
        const outputEl = document.getElementById('terminal-simulation-output');
        if (!outputEl) return;
        
        const promptHost = this.getTerminalPromptHost();
        outputEl.innerHTML = `
            <div class="sim-prompt-line">
                <span class="sim-prompt-host">${this.escapeHtml(promptHost)}</span>
                <span class="blinking-cursor"></span>
            </div>
        `;
        
        // Clean and focus interactive console input
        const inputEl = document.getElementById('interactive-terminal-input');
        if (inputEl) {
            inputEl.value = '';
            inputEl.disabled = false;
        }
        
        const interactivePromptHost = document.getElementById('interactive-prompt-host');
        if (interactivePromptHost) {
            interactivePromptHost.innerText = promptHost;
        }
    }
    
    handleInteractiveTerminalKey(event) {
        if (event.key === 'Enter') {
            const inputEl = document.getElementById('interactive-terminal-input');
            if (!inputEl) return;
            
            const cmdText = inputEl.value.trim();
            if (!cmdText) return;
            
            inputEl.value = '';
            this.executeInteractiveCommand(cmdText);
        }
    }
    
    executeInteractiveCommand(cmdText) {
        const outputEl = document.getElementById('terminal-simulation-output');
        if (!outputEl) return;
        
        // Remove active cursor line
        const lastPrompt = outputEl.querySelector('.sim-prompt-line:last-child');
        if (lastPrompt) {
            lastPrompt.remove();
        }
        
        // Print the typed prompt line
        const cmdLine = document.createElement('div');
        cmdLine.className = 'sim-prompt-line';
        cmdLine.innerHTML = `
            <span class="sim-prompt-host">${this.escapeHtml(this.getTerminalPromptHost())}</span>
            <span class="sim-prompt-cmd">${this.escapeHtml(cmdText)}</span>
        `;
        outputEl.appendChild(cmdLine);
        
        const cmdLower = cmdText.toLowerCase().trim();
        
        if (cmdLower === 'exit') {
            const exitMsg = this.currentLang === 'es' ? 'Saliendo de la simulación de consola...' : 'Exiting console simulation...';
            outputEl.innerHTML += `<div class="sim-system-msg">${exitMsg}</div>`;
            setTimeout(() => {
                this.setTerminalMode('cmds');
            }, 600);
            return;
        }
        
        if (cmdLower === 'clear') {
            this.clearSimulationScreen();
            return;
        }
        
        const steps = this.data.KB[this.activeTech].steps || {};
        const step = steps[this.currentStepKey];
        const rawCmds = (step && step.commands && step.commands[this.activeVendor]) || [];
        const cmds = this.flattenCommandsByTier(rawCmds);
        const appliedCmds = cmds.map(c => this.applyVariablesToText(c));
        
        if (cmdLower === 'help') {
            let helpHtml = `<div class="sim-system-msg">${this.currentLang === 'es' ? 'Comandos sugeridos para este paso:' : 'Suggested commands for this step:'}</div>`;
            appliedCmds.forEach(c => {
                helpHtml += `<div>  • ${this.escapeHtml(c)}</div>`;
            });
            helpHtml += `<div class="sim-system-msg">${this.currentLang === 'es' ? 'Comandos de consola especiales:' : 'Special console commands:'}</div>`;
            helpHtml += `<div>  • run-all  (${this.currentLang === 'es' ? 'Ejecutar todos los sugeridos' : 'Run all suggested'})</div>`;
            helpHtml += `<div>  • clear    (${this.currentLang === 'es' ? 'Limpiar pantalla' : 'Clear screen'})</div>`;
            helpHtml += `<div>  • exit     (${this.currentLang === 'es' ? 'Regresar' : 'Return'})</div>`;
            
            outputEl.innerHTML += helpHtml;
            this.appendTerminalBlinkingCursor();
            return;
        }
        
        if (cmdLower === 'run-all') {
            this.runCommandSimulation();
            return;
        }
        
        let matchedRawCmd = null;
        for (let i = 0; i < cmds.length; i++) {
            const applied = this.applyVariablesToText(cmds[i]);
            if (cmdLower === applied.toLowerCase() || cmdLower === cmds[i].toLowerCase() ||
                cmdLower.includes(applied.toLowerCase()) || applied.toLowerCase().includes(cmdLower)) {
                matchedRawCmd = cmds[i];
                break;
            }
        }
        
        if (matchedRawCmd) {
            const loadMsg = this.currentLang === 'es' ? '[Ejecutando diagnóstico...]' : '[Executing diagnostic...]';
            const loadingLine = document.createElement('div');
            loadingLine.className = 'sim-system-msg';
            loadingLine.innerText = loadMsg;
            outputEl.appendChild(loadingLine);
            outputEl.scrollTop = outputEl.scrollHeight;
            
            const interactiveInput = document.getElementById('interactive-terminal-input');
            if (interactiveInput) interactiveInput.disabled = true;
            
            setTimeout(() => {
                if (interactiveInput) interactiveInput.disabled = false;
                if (loadingLine) loadingLine.remove();
                
                const outputText = this.getSimulatedCommandOutput(matchedRawCmd, this.activeVendor, this.currentStepKey);
                const appliedOutput = this.applyVariablesToText(outputText);
                
                const outputBlock = document.createElement('pre');
                outputBlock.className = 'sim-output-block';
                outputBlock.innerText = appliedOutput;
                outputEl.appendChild(outputBlock);
                
                this.appendTerminalBlinkingCursor();
                if (interactiveInput) interactiveInput.focus();
            }, 450);
            
        } else {
            let outText = '';
            if (cmdLower.includes('ping')) {
                outText = "Sending 5, 100-byte ICMP Echos, timeout is 2 seconds:\n!!!!!\nSuccess rate is 100 percent (5/5), round-trip min/avg/max = 1/3/8 ms";
            } else if (cmdLower.includes('traceroute') || cmdLower.includes('trace')) {
                outText = "Type escape sequence to abort. Tracing the route...\n 1  10.0.0.1  2 msec  1 msec  1 msec\n 2  10.0.0.2  4 msec  3 msec  3 msec\n 3  10.100.1.1  12 msec  10 msec  11 msec";
            } else if (cmdLower.includes('version') || cmdLower.includes('show ver')) {
                outText = `Software Version: Simulated CLI OS v1.0\nUptime: 23 weeks, 4 days\nPlatform: ${this.activeVendor.toUpperCase()} virtual image.`;
            } else if (cmdLower.includes('show ip interface brief') || cmdLower.includes('show ip int brief') || cmdLower.includes('show interfaces brief')) {
                outText = "Interface              IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0     10.1.1.1        YES manual up                    up\nGigabitEthernet0/1     10.2.1.1        YES manual up                    up\nLoopback0              10.100.1.1      YES manual up                    up";
            } else {
                outText = `% Invalid input detected.\nUnknown command or simulation output not available in this context.\nType 'help' to see the recommended diagnostic commands for this step.`;
            }
            
            const outputBlock = document.createElement('pre');
            outputBlock.className = 'sim-output-block';
            outputBlock.innerText = outText;
            outputEl.appendChild(outputBlock);
            
            this.appendTerminalBlinkingCursor();
        }
    }
    
    appendTerminalBlinkingCursor() {
        const outputEl = document.getElementById('terminal-simulation-output');
        if (!outputEl) return;
        
        const finalPrompt = document.createElement('div');
        finalPrompt.className = 'sim-prompt-line';
        finalPrompt.innerHTML = `
            <span class="sim-prompt-host">${this.escapeHtml(this.getTerminalPromptHost())}</span>
            <span class="blinking-cursor"></span>
        `;
        outputEl.appendChild(finalPrompt);
        outputEl.scrollTop = outputEl.scrollHeight;
    }

    getTerminalPromptHost() {
        if (!this.activeVendor) return 'Router#';
        switch (this.activeVendor) {
            case 'juniper':
                return 'user@MX-Edge>';
            case 'cisco_iosxr':
                return 'RP/0/RSP0/CPU0:IOS-XR-PE#';
            case 'cisco_iosxe':
                return 'Cisco-PE-1#';
            case 'mikrotik':
                return '[admin@MikroTik] >';
            case 'fortinet':
                return 'FGT-GW #';
            case 'linux':
                return 'root@linux-tshoot:~#';
            case 'zone':
                return '<Huawei>';
            case 'huawei':
                return 'MA5800-OLT(config)#';
            case 'zte':
                return 'ZXAN(config)#';
            case 'zhone':
                return 'MXK>';
            case 'adtran':
                return 'ADTRAN#';
            case 'ta5k':
                return 'TA5000>';
            default:
                return 'Router#';
        }
    }

    runCommandSimulation() {
        if (this.simRunning) return;
        
        const steps = this.data.KB[this.activeTech].steps || {};
        const step = steps[this.currentStepKey];
        if (!step) return;
        
        const rawCmds = (step.commands && step.commands[this.activeVendor]) || [];
        const cmds = this.flattenCommandsByTier(rawCmds);
        
        const outputEl = document.getElementById('terminal-simulation-output');
        if (!outputEl) return;
        
        if (cmds.length === 0) {
            const noCmdsMsg = this.currentLang === 'es' ? 
                '# No hay comandos de diagnóstico específicos en este paso.' : 
                '# No specific diagnostics commands in this step.';
            outputEl.innerHTML = `<div class="sim-system-msg">${this.escapeHtml(noCmdsMsg)}</div>`;
            return;
        }
        
        this.simRunning = true;
        
        const btnRun = document.getElementById('btn-run-sim');
        const btnClear = document.getElementById('btn-clear-sim');
        if (btnRun) btnRun.disabled = true;
        if (btnClear) btnClear.disabled = true;
        
        outputEl.innerHTML = ''; // Clear
        
        let cmdIdx = 0;
        
        const executeNext = () => {
            if (cmdIdx >= cmds.length) {
                this.simRunning = false;
                if (btnRun) btnRun.disabled = false;
                if (btnClear) btnClear.disabled = false;
                
                const finalPrompt = document.createElement('div');
                finalPrompt.className = 'sim-prompt-line';
                finalPrompt.innerHTML = `
                    <span class="sim-prompt-host">${this.escapeHtml(this.getTerminalPromptHost())}</span>
                    <span class="blinking-cursor"></span>
                `;
                outputEl.appendChild(finalPrompt);
                outputEl.scrollTop = outputEl.scrollHeight;
                return;
            }
            
            const rawCmd = cmds[cmdIdx];
            const cmd = this.applyVariablesToText(rawCmd);
            const promptHost = this.getTerminalPromptHost();
            
            const promptLine = document.createElement('div');
            promptLine.className = 'sim-prompt-line';
            promptLine.innerHTML = `
                <span class="sim-prompt-host">${this.escapeHtml(promptHost)}</span>
                <span class="sim-prompt-cmd"></span>
            `;
            outputEl.appendChild(promptLine);
            outputEl.scrollTop = outputEl.scrollHeight;
            
            const cmdSpan = promptLine.querySelector('.sim-prompt-cmd');
            
            let charIdx = 0;
            const typeChar = () => {
                if (charIdx < cmd.length) {
                    cmdSpan.textContent += cmd[charIdx];
                    charIdx++;
                    setTimeout(typeChar, 10);
                } else {
                    const loader = document.createElement('div');
                    loader.className = 'sim-system-msg';
                    loader.innerText = this.currentLang === 'es' ? 'Ejecutando diagnóstico...' : 'Running diagnostics...';
                    outputEl.appendChild(loader);
                    outputEl.scrollTop = outputEl.scrollHeight;
                    
                    setTimeout(() => {
                        outputEl.removeChild(loader);
                        
                        const outputBlock = document.createElement('pre');
                        outputBlock.className = 'sim-output-block';
                        
                        const outputText = this.getSimulatedCommandOutput(rawCmd, this.activeVendor, this.currentStepKey);
                        outputBlock.innerText = this.applyVariablesToText(outputText);
                        
                        outputEl.appendChild(outputBlock);
                        outputEl.scrollTop = outputEl.scrollHeight;
                        
                        cmdIdx++;
                        setTimeout(executeNext, 300);
                    }, 450);
                }
            };
            
            setTimeout(typeChar, 150);
        };
        
        executeNext();
    }

    getSimulatedCommandOutput(cmd, vendor, stepKey) {
        const cleanCmd = cmd.toLowerCase().trim();
        const techMatch = this.activeTech;
        const simOuts = this.data.simulatedOutputs || {};
        
        if (simOuts[techMatch] && simOuts[techMatch][stepKey] && simOuts[techMatch][stepKey][vendor]) {
            const stepOutputs = simOuts[techMatch][stepKey][vendor];
            for (const [keyCmd, valOutput] of Object.entries(stepOutputs)) {
                if (cleanCmd.includes(keyCmd.toLowerCase().trim()) || keyCmd.toLowerCase().trim().includes(cleanCmd)) {
                    return valOutput;
                }
            }
        }
        
        // GPON OLT/ONT-specific fallback configurations and diagnostics
        const isGpon = (techMatch === 'fiber_ont' || techMatch === 'fiber_ont_config');
        if (isGpon) {
            if (cleanCmd.includes('show run') || 
                cleanCmd.includes('show config') || 
                cleanCmd.includes('current-configuration') || 
                cleanCmd.includes('saved-configuration') ||
                cleanCmd.startsWith('get ') ||
                cleanCmd.startsWith('port show') ||
                cleanCmd.startsWith('onu show') ||
                cleanCmd.startsWith('bridge show')
            ) {
                if (vendor === 'huawei') {
                    return `[Huawei MA5800 OLT GPON Configuration]
#
sysname MA5800-OLT
#
gpon port 0/1
  ont add 1 1 sn-auth "ZTEGC1A2B3D4" omci ont-lineprofile-id 10 ont-srvprofile-id 10 desc "RESIDENTIAL-01"
#
ont-lineprofile gpon profile-id 10 profile-name "FTTH-LINE"
  tcont 1 dba-profile-id 10
  gem add 1 eth tcont 1
  gem add 2 eth tcont 1
  gem mapping 1 1 vlan 10
  gem mapping 2 2 vlan 20
  commit
#
ont-srvprofile gpon profile-id 10 profile-name "FTTH-SRV"
  ont-port pots 1 eth 4 wlan 1
  port vlan eth 1 translation 10 user-vlan 10
  commit
#
service-port 0 gpon 0/1/1 ont 1 gemport 1 multi-service user-vlan 10 tag-transform translate-and-add inner-vlan 100 inbound traffic-table name FTTH-100M outbound traffic-table name FTTH-100M
service-port 1 gpon 0/1/1 ont 1 gemport 2 multi-service user-vlan 20 tag-transform translate-and-add inner-vlan 200 inbound traffic-table name FTTH-IPTV outbound traffic-table name FTTH-IPTV
#`;
                } else if (vendor === 'zte') {
                    return `[ZTE ZXAN OLT GPON Configuration]
!
hostname ZXAN-OLT
!
interface gpon-olt_1/2/1
  onu 1 type ZTEG-F660 sn ZTEGC1A2B3D4
!
interface gpon-onu_1/2/1:1
  name RESIDENTIAL-01
  tcont 1 name T-DATA dba-profile DBA-RESIDENTIAL
  gemport 1 name GEM-DATA tcont 1
  gemport 1 traffic-limit upstream 100M downstream 100M
  service-port 1 vport 1 user-vlan 10 svlan 100
  service-port 2 vport 2 user-vlan 20 svlan 200
!
pon-onu-mng gpon-onu_1/2/1:1
  service-port 1 gw-port eth_0/1 vlan 10
  wifi 1 mode bgn ssid HOME-WIFI security wpa2-psk password SecretPass123 channel 6
  voice-profile SIP-PROF vlan 300
  pots 1 sip-user 1001 password SecretPass123
!`;
                } else if (vendor === 'zhone' || vendor === 'zone') {
                    return `[Zhone/DASAN MXK OLT GPON Configuration]
!
gpononu set 1/4/1 1 profile Default sn ZTEGC1A2B3D4
port description add 1-1-4-1/gpononu "RESIDENTIAL-01"
new gpon-traffic-profile 1
!
bridge add 1-1-4-1/gpononu gem 301 gtp 1 downlink vlan 100 tagged eth 1
bridge add 1-1-4-1/gpononu gem 401 gtp 1 0/4 downlink vlan 999 tagged video eth 2
bridge add 1-1-4-1/gpononu gem 702 gtp 1 downlink vlan 300 tagged sip
!`;
                } else if (vendor === 'adtran') {
                    return `[ADTRAN OLT GPON Configuration]
!
gpon-olt 1
  remote-device 1 name "RESIDENTIAL-01" serial-number ZTEGC1A2B3D4
  remote-device 1 ont-profile "default"
!
bridge-group 100
  description "Internet Data"
  member vlan 100
  member remote-device 1 eth 1
!`;
                }
            }
            
            // Dynamic Diagnostic Queries
            if (vendor === 'huawei') {
                if (cleanCmd.includes('autofind')) {
                    return `   ----------------------------------------------------------------------
   Number of newly found ONUs: 1
   ----------------------------------------------------------------------
   Interface ID      : GPON 0/1/1
   ONU ID            : 0
   Serial number     : ZTEGC1A2B3D4
   Discover time     : 2026-06-12 09:42:10
   ----------------------------------------------------------------------`;
                }
                if (cleanCmd.includes('optical-info')) {
                    return `   -----------------------------------------------------------------------------
   ONU ID                         : 1
   Rx optical power(dBm)          : -19.45
   Tx optical power(dBm)          : 2.12
   OLT Rx ONT optical power(dBm)  : -20.15
   Laser behavior                 : normal
   Bias current(mA)               : 15.42
   Temperature(C)                 : 42.5
   Voltage(V)                     : 3.32
   -----------------------------------------------------------------------------`;
                }
                if (cleanCmd.includes('detail-info') || cleanCmd.includes('detail') || cleanCmd.includes('lastdowncause') || cleanCmd.includes('version')) {
                    return `   -----------------------------------------------------------------------------
   ONU ID                         : 1
   Distance(m)                    : 1420
   EqD(us)                        : 290150
   SN                             : ZTEGC1A2B3D4
   Hardware Version               : F660v8.0
   Software Version               : V8.0.10P1T1
   Last offline cause             : power-off
   Last offline time              : 2026-06-12 08:30:15
   -----------------------------------------------------------------------------`;
                }
                if (cleanCmd.includes('wan-info') || cleanCmd.includes('ipconfig')) {
                    return `   -----------------------------------------------------------------------------
   ONU ID                         : 1
   WAN Index                      : 1
   Service Type                   : Internet
   Connection Type                : Route
   Connection Status              : Connected
   IPv4 Address                   : 192.168.253.123
   Subnet Mask                    : 255.255.255.0
   Default Gateway                : 192.168.253.1`;
                }
                if (cleanCmd.includes('pppoe')) {
                    return `   -----------------------------------------------------------------------------
   ONU ID                         : 1
   PPPoE Session State            : Established
   Local IP                       : 192.168.253.123
   Peer IP                        : 192.168.253.1
   Session ID                     : 1403
   -----------------------------------------------------------------------------`;
                }
                if (cleanCmd.includes('sip') || cleanCmd.includes('voice')) {
                    return `   -----------------------------------------------------------------------------
   ONU ID                         : 1
   POTS Port                      : 1
   SIP User                       : 1001
   SIP Server                     : 10.1.1.1
   Register Status                : Registered
   -----------------------------------------------------------------------------`;
                }
                if (cleanCmd.includes('pots')) {
                    return `   -----------------------------------------------------------------------------
   ONU ID                         : 1
   POTS Port ID                   : 1
   Admin State                    : up
   Physical State                 : idle
   Service State                  : normal
   -----------------------------------------------------------------------------`;
                }
                if (cleanCmd.includes('associated-station')) {
                    return `   -----------------------------------------------------------------------------
   Index  MAC Address        IP Address        RSSI(dBm)  Tx Rate(Mbps)
   -----------------------------------------------------------------------------
   1      98:ee:cb:dd:c7:63  192.168.1.15      -65        144
   2      fe:53:7a:cd:eb:8d  192.168.1.20      -72        72
   -----------------------------------------------------------------------------`;
                }
                if (cleanCmd.includes('wlan')) {
                    return `   -----------------------------------------------------------------------------
   ONU ID                         : 1
   WLAN Index                     : 1
   SSID                           : HOME-WIFI
   State                          : Enabled
   Channel                        : 6
   -----------------------------------------------------------------------------`;
                }
                if (cleanCmd.includes('alarm')) {
                    return `   -----------------------------------------------------------------------------
   Alarm ID  Alarm Name        Alarm Severity  Raise Time
   -----------------------------------------------------------------------------
   0x231001  Dying Gasp        Critical        2026-06-12 09:30:15
   0x231002  Loss of Signal    Critical        2026-06-12 09:30:16
   -----------------------------------------------------------------------------`;
                }
                if (cleanCmd.includes('info')) {
                    return `   -----------------------------------------------------------------------------
   ONU ID                         : 1
   Name                           : RESIDENTIAL-01
   Admin State                    : up
   Run State                      : online
   Config State                   : active
   Match State                    : match
   Control State                  : active
   Serial number                  : ZTEGC1A2B3D4
   Description                    : RESIDENTIAL-01
   Last offline cause             : power-off
   Last offline time              : 2026-06-12 08:30:15
   -----------------------------------------------------------------------------`;
                }
                if (cleanCmd.includes('vlan')) {
                    return `   VLAN ID: 100
   VLAN Type: Smart
   VLAN Attribute: Common
   VLAN Description: GPON-DATA-VLAN
   VLAN State: Active`;
                }
                if (cleanCmd.includes('mac-address') || cleanCmd.includes('macaddress')) {
                    return `   -----------------------------------------------------------------------------
   VLAN ID  MAC Address     Type      Source Port
   -----------------------------------------------------------------------------
   100      98ee-cbdd-c763  Dynamic   gpon 0/1/1
   -----------------------------------------------------------------------------`;
                }
            } else if (vendor === 'zte') {
                if (cleanCmd.includes('uncfg')) {
                    return `   OnuIndex                 Sn                  State
   -------------------------------------------------------
   gpon-onu_1/2/1:1         ZTEGC1A2B3D4        unconfigured`;
                }
                if (cleanCmd.includes('optical-info')) {
                    return `   ONU Optical Information:
   ONU Index: gpon-onu_1/2/1:1
   Tx Power: 2.12 (dBm)
   Rx Power (Received by OLT): -20.15 (dBm)
   Rx Power (Received by ONU): -19.45 (dBm)
   OLT Rx Power Threshold: -28.00 / -8.00 (dBm)
   Work State: Normal`;
                }
                if (cleanCmd.includes('detail-info') || cleanCmd.includes('base-info') || cleanCmd.includes('detail') || cleanCmd.includes('lastdowncause')) {
                    return `   ONU Index: gpon-onu_1/2/1:1
   Type: ZTEG-F660
   Serial Number: ZTEGC1A2B3D4
   Ranging Distance: 1420 (m)
   Equalization Delay: 290150 (us)
   Last Offline Cause: dying-gasp
   Last Offline Time: 2026-06-12 08:30:15`;
                }
                if (cleanCmd.includes('service-port')) {
                    return `   ServicePortID  OnuIndex          VportID  UserVlan  Svlan  Cvlan
   ------------------------------------------------------------------
   1              gpon-onu_1/2/1:1  1        10        100    10
   2              gpon-onu_1/2/1:1  2        20        200    20`;
                }
                if (cleanCmd.includes('macaddress') || cleanCmd.includes('mac-address')) {
                    return `   Mac Address      VlanId   Type     Port
   ------------------------------------------------------------------
   98ee.cbdd.c763   100      Dynamic  gpon-onu_1/2/1:1`;
                }
                if (cleanCmd.includes('sip status') || cleanCmd.includes('sip register-status') || cleanCmd.includes('sip')) {
                    return `   SIP Register Status:
   User Name: 1001
   Registrar Server IP: 10.1.1.1
   Register Port: 5060
   Register State: Register Success`;
                }
                if (cleanCmd.includes('voice port summary')) {
                    return `   Port Index  Port Type  State     Hook State  Register State
   ------------------------------------------------------------------
   POTS 1      SIP        Idle      On Hook     Registered`;
                }
                if (cleanCmd.includes('voice call active')) {
                    return `   No active VoIP calls in progress.`;
                }
                if (cleanCmd.includes('remote-onu wifi') || (cleanCmd.includes('remote-onu') && cleanCmd.includes('wifi'))) {
                    return `   Wifi Configuration:
   Wifi Mode: 802.11b/g/n
   SSID: HOME-WIFI
   SSID Index: 1
   Authentication: WPA2-PSK
   Encryption: AES
   Channel: 6
   State: Enabled`;
                }
                if (cleanCmd.includes('associated-station')) {
                    return `   Associated Stations:
   SSID 1:
     MAC: 98:ee:cb:dd:c7:63  IP: 192.168.1.15  RSSI: -65 dBm
     MAC: fe:53:7a:cd:eb:8d  IP: 192.168.1.20  RSSI: -72 dBm`;
                }
                if (cleanCmd.includes('wlan-statistics')) {
                    return `   SSID 1 Statistics:
   Packets Rx: 145920    Packets Tx: 298104
   Bytes Rx: 1294801     Bytes Tx: 4920148
   Errors Rx: 0          Errors Tx: 0`;
                }
                if (cleanCmd.includes('state')) {
                    return `   OnuIndex                 AdminState   RegState     PhaseState
   ---------------------------------------------------------------------
   gpon-onu_1/2/1:1         enable       active       O5(operation)`;
                }
                if (cleanCmd.includes('vlan')) {
                    return `   ONU Index: gpon-onu_1/2/1:1
   Port Type: Ethernet
   Port ID: 1
   User VLAN: 10
   Service VLAN: 100`;
                }
                if (cleanCmd.includes('logging') || cleanCmd.includes('log')) {
                    return `   2026-06-12 09:00:10 GPON-ONU-UP: ONU 1/2/RegID:1 registered
   2026-06-12 09:00:15 GPON-ONU-O5: ONU 1/2/RegID:1 phase operation completed successfully`;
                }
            } else if (vendor === 'zhone' || vendor === 'zone') {
                if (cleanCmd.includes('bridge show onu') || cleanCmd.includes('bridge show')) {
                    return `   Bridge Interface Info for ONU 1/4/1:
   BridgeName                        GTP   VLAN  SLAN  Status
   --------------------------------------------------------------
   1-1-4-301-gponport-100/bridge     1     100   301   Active
   1-1-4-702-gponport-300/bridge     1     300   702   Active`;
                }
                if (cleanCmd.includes('bridge-interface-record')) {
                    return `   Bridge Interface Record 1-1-4-301-gponport-100/bridge:
     State: enabled
     Uplink Port: eth 1
     Learned MACs: 1 (98:ee:cb:dd:c7:63)`;
                }
                if (cleanCmd.includes('gponolt show bw')) {
                    return `   GPON OLT Bandwidth Info for Port 1/4:
   Total Allocated Upstream: 120 Mbps
   Dynamic DBA Range: 10 Mbps - 1000 Mbps
   Active GEM Ports: 3`;
                }
                if (cleanCmd.includes('onu show')) {
                    return `   ONU Index  Status      SN            Profile  AdminState
   ----------------------------------------------------------
   1/4/1      Registered  ZTEGC1A2B3D4  Default  Up`;
                }
                if (cleanCmd.includes('gpon-olt-config')) {
                    return `   gpon-olt-config for 1-1-4-0/gponolt:
     Status: up
     Laser: enabled
     ONT Count: 1`;
                }
                if (cleanCmd.includes('gpon-olt-onu-config')) {
                    return `   gpon-onu-config for 1-1-4-1/gpononu:
     ONU-ID: 1
     Serial: ZTEGC1A2B3D4
     Profile: Default
     Status: operational`;
                }
                if (cleanCmd.includes('cpe rg show')) {
                    return `   CPE Residential Gateway 1/4/1:
     WAN: PPPoE (Connected, IP: 192.168.253.123)
     LAN: 192.168.1.1`;
                }
                if (cleanCmd.includes('cpe voip show')) {
                    return `   CPE VoIP status for 1/4/1:
     State: Registered
     Line 1: Idle (+541123456)`;
                }
                if (cleanCmd.includes('port show alarm') || cleanCmd.includes('alarm')) {
                    return `   Alarms active on interface 1-1-4-0/gponolt:
   No active critical alarms on port 1/4.`;
                }
                if (cleanCmd.includes('port show')) {
                    return `   Port 1-1-4-1/gpononu details:
     State: enabled
     Description: "RESIDENTIAL-01"`;
                }
            } else if (vendor === 'adtran') {
                if (cleanCmd.includes('remote-devices')) {
                    return `   OntId   Name             State    SN            Distance  RxPower
   --------------------------------------------------------------------
   1       RESIDENTIAL-01   Active   ZTEGC1A2B3D4  1420m     -19.45 dBm`;
                }
                if (cleanCmd.includes('alarm log')) {
                    return `   Active alarms:
   No alarm events registered in the past 24 hours.`;
                }
                if (cleanCmd.includes('bridge-group')) {
                    return `   Bridge-group details:
     VLAN: 100
     Status: Up
     Learned MACs: 98:ee:cb:dd:c7:63`;
                }
            }
            
            if (cleanCmd.startsWith('show ') || cleanCmd.startsWith('display ') || cleanCmd.startsWith('get ')) {
                return `GPON OLT Diagnostic Output for command: ${cmd}
-----------------------------------------------------------------------------
Target Device   : GPON 0/1/1 (or equivalent OLT port)
ONU ID          : 1
Serial Number   : ZTEGC1A2B3D4
Administrative  : up (enabled)
Operational     : online (Phase O5 - operational)
Optical Power   : RX (OLT) -20.15 dBm, RX (ONU) -19.45 dBm (within safe limits)
Active Alarms   : none detected
-----------------------------------------------------------------------------`;
            }
            
            // Action command fallbacks
            if (cleanCmd.startsWith('interface ')) {
                return `Entering interface configuration mode.`;
            }
            if (cleanCmd.startsWith('ont add') || cleanCmd.startsWith('onu ') || cleanCmd.includes('gpononu set')) {
                return `ONU configuration registered successfully. Assigning ONU-ID. Registering MIBs via OMCI...`;
            }
            if (cleanCmd.includes('reboot') || cleanCmd.includes('reset') || cleanCmd.includes('clear') || cleanCmd.includes('delete')) {
                return `Resetting ONT/ONU remote state... Connection terminated. Status: Offline (Discovering)`;
            }
            if (cleanCmd.includes('rule ') || cleanCmd.startsWith('acl ')) {
                return `Access control rule parsed and applied successfully to current traffic-filter profile.`;
            }
            if (cleanCmd.startsWith('service-port') || cleanCmd.startsWith('bridge add') || cleanCmd.startsWith('new gpon-traffic-profile') || cleanCmd.startsWith('bridge insertpppoevendortag')) {
                return `Service-port mapping and Tag-transform rules successfully provisioned. Data path active.`;
            }
            if (cleanCmd.startsWith('dba-profile ') || cleanCmd.startsWith('gpon profile ') || cleanCmd.startsWith('tcont ')) {
                return `Traffic profile and dynamic bandwidth assignment (DBA) parameters applied successfully.`;
            }
            if (cleanCmd.startsWith('ont wlan-config') || cleanCmd.startsWith('wifi ')) {
                return `SSID and wireless security parameters pushed successfully to ONT.`;
            }
            if (cleanCmd.startsWith('ont-sipprofile') || cleanCmd.startsWith('voice-profile') || cleanCmd.startsWith('pots ') || cleanCmd.startsWith('cpe voip ')) {
                return `SIP client parameters configured. Remote POTS port mapping updated.`;
            }
            if (cleanCmd.startsWith('debug ') || cleanCmd.startsWith('undebug ')) {
                return `Debugging trace activated for GPON target scope. Monitoring events...`;
            }
            
            // GPON OLT / ONT Specific commands
            if (cleanCmd.startsWith('gponolt ')) {
                if (cleanCmd.includes('show bw')) {
                    return `GPON OLT Bandwidth Info for Port 1/4:
  Total Allocated Upstream: 120 Mbps
  Dynamic DBA Range: 10 Mbps - 1000 Mbps
  Active GEM Ports: 3`;
                }
                return `GPON OLT command executed successfully.`;
            }
            if (cleanCmd.startsWith('gpononu ')) {
                if (cleanCmd.includes('show')) {
                    return `ONU Index  Status      SN            Profile  AdminState
----------------------------------------------------------
1/4/1      Registered  ZTEGC1A2B3D4  Default  Up`;
                }
                if (cleanCmd.includes('resync')) {
                    return `MIB resync requested for ONU. MIB sync success.`;
                }
                if (cleanCmd.includes('profile export') || cleanCmd.includes('profile import')) {
                    return `OMCI MIB profile processed successfully.`;
                }
                return `GPON ONU command executed successfully.`;
            }
            if (cleanCmd.startsWith('ont ') || cleanCmd.startsWith('ont-')) {
                if (cleanCmd.includes('internet-config') || cleanCmd.includes('wan-config')) {
                    return `Internet WAN interface configured on ONT (mode Route/Bridge, DHCP client enabled).`;
                }
                if (cleanCmd.includes('pots-config') || cleanCmd.includes('voice-config')) {
                    return `POTS voice line configured and associated with SIP profile.`;
                }
                if (cleanCmd.includes('lineprofile') || cleanCmd.includes('srvprofile')) {
                    return `ONT profile configuration created and committed successfully.`;
                }
                return `ONT command executed successfully.`;
            }
            if (cleanCmd.startsWith('gem ') || cleanCmd.startsWith('gemport ')) {
                return `GEM port configured and mapped to T-CONT/VLAN.`;
            }
            if (cleanCmd.startsWith('ip-host ')) {
                return `IP host profile configuration completed.`;
            }
            if (cleanCmd.startsWith('nat outbound') || cleanCmd.includes('nat outbound')) {
                return `NAT outbound rules successfully applied to WAN interface/VLAN.`;
            }
            if (cleanCmd.startsWith('vlan ') || cleanCmd.startsWith('port vlan ')) {
                return `VLAN tag-transform and smart-qinq configurations applied to OLT port.`;
            }
        }
        
        // Fallbacks
        if (cleanCmd === 'configure terminal' || cleanCmd === 'configure' || cleanCmd === 'system-view' || cleanCmd.startsWith('config ')) {
            return vendor === 'juniper' ? 'Entering configuration mode\n[edit]' :
                   vendor === 'cisco_iosxr' ? 'Entering configuration mode\nRP/0/RSP0/CPU0:IOS-XR-PE(config)#' :
                   vendor === 'cisco_iosxe' ? 'Entering configuration mode\nCisco-PE-1(config)#' :
                   vendor === 'mikrotik' ? 'Entering configuration mode...' :
                   vendor === 'fortinet' ? 'Entering configuration mode...' :
                   vendor === 'zone' ? 'Entering configuration mode\n[Huawei]' :
                   vendor === 'adtran' ? 'Entering configuration mode\nADTRAN(config)#' :
                   vendor === 'ta5k' ? 'Entering configuration mode\nTA5000(config)#' :
                   'Entering configuration mode...';
        }
        if (cleanCmd === 'commit' || cleanCmd === 'write memory' || cleanCmd === 'save' || cleanCmd === 'end') {
            return vendor === 'juniper' ? 'commit complete.' :
                   vendor === 'cisco_iosxr' ? 'Building configuration...\n[OK]' :
                   vendor === 'cisco_iosxe' ? 'Building configuration...\n[OK]' :
                   vendor === 'mikrotik' ? '(Config autosaved)' :
                   vendor === 'fortinet' ? '(Changes applied)' :
                   vendor === 'zone' ? 'Information: Save configuration successfully.' :
                   vendor === 'adtran' || vendor === 'ta5k' ? 'Copying running-config to startup-config... [OK]' :
                   '[OK]';
        }
        if (cleanCmd.startsWith('set ') || cleanCmd.startsWith('no ') || cleanCmd.startsWith('ip nat ') || cleanCmd.startsWith('router ') || cleanCmd.startsWith('edit ') || cleanCmd.startsWith('/ip firewall ')) {
            return vendor === 'juniper' ? '[edit]' :
                   vendor === 'cisco_iosxr' ? 'RP/0/RSP0/CPU0:IOS-XR-PE(config-router)#' :
                   vendor === 'cisco_iosxe' ? 'Cisco-PE-1(config-router)#' :
                   vendor === 'mikrotik' ? '(applied)' :
                   vendor === 'fortinet' ? '(applied)' :
                   vendor === 'zone' ? '[Huawei]' :
                   vendor === 'adtran' || vendor === 'ta5k' ? '(config-router)#' :
                   '(applied)';
        }

        // Fallbacks
        if (cleanCmd.startsWith('ping') || cleanCmd.includes('ping ')) {
            return `PING ${this.sessionVariables['ip-privada'] || this.sessionVariables['peer-ip'] || '8.8.8.8'} (8.8.8.8) 56(84) bytes of data.\n64 bytes from 8.8.8.8: icmp_seq=1 ttl=56 time=12.4 ms\n64 bytes from 8.8.8.8: icmp_seq=2 ttl=56 time=11.8 ms\n64 bytes from 8.8.8.8: icmp_seq=3 ttl=56 time=14.1 ms\n64 bytes from 8.8.8.8: icmp_seq=4 ttl=56 time=12.2 ms\n64 bytes from 8.8.8.8: icmp_seq=5 ttl=56 time=11.9 ms\n\n--- 8.8.8.8 ping statistics ---\n5 packets transmitted, 5 received, 0% packet loss, time 4006ms\nrtt min/avg/max/mdev = 11.821/12.484/14.112/0.812 ms`;
        }
        if (cleanCmd.includes('traceroute') || cleanCmd.includes('trace ')) {
            return `traceroute to ${this.sessionVariables['peer-ip'] || '8.8.8.8'} (8.8.8.8), 30 hops max, 60 byte packets\n 1  192.168.1.1 (192.168.1.1)  0.841 ms  0.712 ms  0.688 ms\n 2  10.0.12.2 (10.0.12.2)  4.112 ms  4.022 ms  3.988 ms\n 3  203.0.113.1 (203.0.113.1)  8.214 ms  8.115 ms  8.092 ms\n 4  8.8.8.8 (8.8.8.8)  12.412 ms  12.115 ms  12.022 ms`;
        }
        if (cleanCmd.includes('debug ') || cleanCmd.includes('diagnose debug')) {
            return `${this.currentLang === 'es' ? 'Debugging activado. Monitoreando eventos de red...' : 'Debugging activated. Monitoring network events...'}\n[16:40:02.102] EVT: Matching criteria ok.\n[16:40:04.214] EVT: Process queue scheduling.\n[16:40:07.412] EVT: Diagnostic frame trace finished.`;
        }
        if (cleanCmd.includes('show run') || cleanCmd.includes('show config') || cleanCmd.includes('/print')) {
            return `! Configuration block extracted from active context\n!\nprotocols {\n    bgp {\n        local-as 65001;\n        group external-peers {\n            peer-as 65002;\n            neighbor ${this.sessionVariables['peer'] || '10.0.0.2'};\n        }\n    }\n}`;
        }
        
        return `Diagnostic executed successfully.\nStatus: Active/Operational\nNo active anomalies detected for this scope.`;
    }

    // ==========================================================================
    // VARIABLE INPUTS & NOTES CONTROLLERS
    // ==========================================================================
    getPlaceholdersFromCommands(cmds) {
        if (!cmds || !Array.isArray(cmds)) return [];
        const found = [];
        const regex = /<([A-Za-z0-9_-]+)>/g;
        cmds.forEach(cmd => {
            let match;
            regex.lastIndex = 0;
            while ((match = regex.exec(cmd)) !== null) {
                if (!found.includes(match[1])) {
                    found.push(match[1]);
                }
            }
        });
        return found;
    }

    renderVariablesForm(placeholders) {
        const container = document.getElementById('step-variables-container');
        const grid = document.getElementById('variables-inputs-grid');
        
        if (!grid) return;
        grid.innerHTML = '';
        
        if (!placeholders || placeholders.length === 0) {
            if (container) container.classList.add('hidden');
            return;
        }
        
        if (container) container.classList.remove('hidden');
        
        placeholders.forEach(ph => {
            const group = document.createElement('div');
            group.className = 'var-input-group';
            
            const label = document.createElement('label');
            label.innerText = ph;
            
            const input = document.createElement('input');
            input.type = 'text';
            input.value = this.sessionVariables[ph] || '';
            input.placeholder = `<${ph}>`;
            
            input.oninput = (e) => {
                this.sessionVariables[ph] = e.target.value;
                this.saveSessionToStorage();
                
                this.renderSidebarVariables();
                this.updateTerminalCommandsOnly();
            };
            
            group.appendChild(label);
            group.appendChild(input);
            grid.appendChild(group);
        });
        
        lucide.createIcons();
    }

    updateTerminalCommandsOnly() {
        const steps = this.data.KB[this.activeTech].steps || {};
        const step = steps[this.currentStepKey];
        if (!step) return;
        
        const rawCmds = (step.commands && step.commands[this.activeVendor]) || [];
        const cmds = this.flattenCommandsByTier(rawCmds);
        
        const terminalCodeEl = document.getElementById('terminal-commands-code');
        if (terminalCodeEl) {
            if (cmds.length === 0) {
                terminalCodeEl.innerHTML = `<span class="comment"># ${this.currentLang === 'es' ? 'No hay comandos de diagnóstico específicos de este paso para este vendor.' : 'No specific diagnostics commands for this step for this vendor.'}</span>`;
            } else {
                const processedCmds = cmds.map(c => this.applyVariablesToText(c));
                const codeHtml = processedCmds.map(cmd => {
                    if (cmd.startsWith('#') || cmd.startsWith('!')) {
                        return `<span class="comment">${this.escapeHtml(cmd)}</span>`;
                    }
                    let highlighted = this.escapeHtml(cmd);
                    const keywords = ['show', 'set', 'get', 'diagnose', 'execute', 'display', 'ping', 'traceroute', 'commit', 'configure', 'exit', 'interface', 'routing', 'policy'];
                    keywords.forEach(kw => {
                        const regex = new RegExp(`\\b${kw}\\b`, 'g');
                        highlighted = highlighted.replace(regex, `<span class="keyword">${kw}</span>`);
                    });
                    return highlighted;
                }).join('\n');
                terminalCodeEl.innerHTML = codeHtml;
            }
        }
        
        if (this.terminalMode === 'sim' && !this.simRunning) {
            this.clearSimulationScreen();
        }
    }

    flattenCommandsByTier(raw) {
        if (!raw) return [];
        let cmds = [];
        if (Array.isArray(raw)) {
            cmds = raw;
        } else if (typeof raw === 'object') {
            const result = [];
            const tiers = ["tier1", "tier2", "tier3", "arch"];
            for (const lvl of tiers) {
                if (raw[lvl]) {
                    const tier_num = {"tier1": 1, "tier2": 2, "tier3": 3, "arch": 1}[lvl];
                    if (tier_num <= this.activeTier) {
                        result.push(...raw[lvl]);
                    }
                }
            }
            cmds = result;
        }
        return this.filterCommandsByIpVersion(cmds, this.activeIpVersion);
    }

    setIpVersion(version) {
        if (version !== 'ipv4' && version !== 'ipv6') return;
        this.activeIpVersion = version;
        
        // Update active class on buttons
        const btnV4 = document.getElementById('ip-btn-v4');
        const btnV6 = document.getElementById('ip-btn-v6');
        if (btnV4 && btnV6) {
            if (version === 'ipv4') {
                btnV4.classList.add('active');
                btnV6.classList.remove('active');
            } else {
                btnV6.classList.add('active');
                btnV4.classList.remove('active');
            }
        }
        
        // Re-render current step to apply filtering
        this.renderCurrentStep();
    }

    filterCommandsByIpVersion(cmds, version) {
        if (!cmds) return [];
        return cmds.filter(cmd => {
            const clean = cmd.toLowerCase();
            
            // Determine if it is specifically an IPv6 command
            const isIpv6Cmd = clean.includes('ipv6') || 
                               clean.includes('ospf3') || 
                               clean.includes('ospfv3') || 
                               clean.includes('mld') || 
                               clean.includes('static6') || 
                               clean.includes('inet6') || 
                               clean.includes('raguard') || 
                               clean.includes('/ipv6') ||
                               clean.includes('ndp') ||
                               (clean.includes(' nd ') || clean.startsWith('nd ')) ||
                               clean.includes('dhcp6') ||
                               clean.includes('dhcpv6') ||
                               clean.includes('vpnv6') ||
                               clean.includes('2001:db8') ||
                               clean.includes('fe80::');
                               
            if (version === 'ipv6') {
                // For IPv6, filter out explicit IPv4 commands. Keep generic or IPv6-specific commands.
                const isIpv4Cmd = clean.includes('ip route') || 
                                   clean.includes('ip ospf') || 
                                   clean.includes('show ip bgp') || 
                                   clean.includes('show ip interface') || 
                                   clean.includes('show ip neighbor') || 
                                   clean.includes(' arp ') || clean.startsWith('arp ') ||
                                   clean.includes('igmp') ||
                                   clean.includes('/ip route') ||
                                   clean.includes('192.168.') ||
                                   clean.includes('10.10.');
                                   
                if (isIpv4Cmd) return false;
                return true;
            } else {
                // For IPv4, filter out IPv6 commands
                return !isIpv6Cmd;
            }
        });
    }

    applyVariablesToText(text) {
        if (!text) return '';
        let result = text;
        for (const [varName, varVal] of Object.entries(this.sessionVariables)) {
            if (varVal !== undefined && varVal !== null) {
                result = result.replaceAll(`<${varName}>`, varVal);
            }
        }
        return result;
    }

    renderSidebarVariables() {
        const list = document.getElementById('sidebar-vars-list');
        if (!list) return;
        list.innerHTML = '';
        
        const keys = Object.keys(this.sessionVariables).filter(k => this.sessionVariables[k]);
        if (keys.length === 0) {
            list.innerHTML = `<span class="empty-msg">${this.currentLang === 'es' ? 'No hay variables configuradas en esta sesión.' : 'No variables configured in this session.'}</span>`;
            return;
        }
        
        keys.forEach(k => {
            const item = document.createElement('div');
            item.className = 'sidebar-var-item';
            item.innerHTML = `<span class="var-key">&lt;${this.escapeHtml(k)}&gt;</span><span class="var-val">${this.escapeHtml(this.sessionVariables[k])}</span>`;
            list.appendChild(item);
        });
    }

    renderSidebarNotes() {
        const list = document.getElementById('sidebar-notes-list');
        if (!list) return;
        list.innerHTML = '';
        
        if (!this.notesLog || this.notesLog.length === 0) {
            list.innerHTML = `<span class="empty-msg">${this.currentLang === 'es' ? 'No has tomado notas en ningún paso aún. Escribe en la caja de anotaciones de un paso para guardar un registro.' : 'You have not taken notes on any step yet. Write in the notes box of any step to log comments.'}</span>`;
            return;
        }
        
        this.notesLog.forEach(n => {
            const card = document.createElement('div');
            card.className = 'sidebar-note-card';
            
            const header = document.createElement('div');
            header.style.display = 'flex';
            header.style.justifyContent = 'space-between';
            header.style.fontSize = '0.65rem';
            header.style.color = 'var(--text-muted)';
            header.style.marginBottom = '4px';
            
            const techSpan = document.createElement('span');
            techSpan.innerText = n.tech_name || n.tech;
            
            const timeSpan = document.createElement('span');
            timeSpan.innerText = n.timestamp.split(', ')[1] || n.timestamp;
            
            header.appendChild(techSpan);
            header.appendChild(timeSpan);
            
            const title = document.createElement('h4');
            title.style.fontSize = '0.72rem';
            title.style.margin = '2px 0 4px 0';
            title.style.color = 'var(--accent-cyan)';
            title.innerText = n.title;
            
            const text = document.createElement('p');
            text.style.fontSize = '0.7rem';
            text.style.margin = '0';
            text.style.color = 'var(--text-secondary)';
            text.style.whiteSpace = 'pre-wrap';
            text.innerText = n.note;
            
            card.appendChild(header);
            card.appendChild(title);
            card.appendChild(text);
            list.appendChild(card);
        });
    }

    saveCurrentStepNote(event) {
        const val = event.target.value.trim();
        const timestamp = new Date().toLocaleString();
        
        let existingNoteIdx = this.notesLog.findIndex(n => n.tech === this.activeTech && n.step === this.currentStepKey);
        
        if (val) {
            const stepTitle = document.getElementById('step-title').innerText;
            const techName = this.getLocalizedText(this.data.KB[this.activeTech], 'name');
            const noteObj = {
                tech: this.activeTech,
                tech_name: techName,
                step: this.currentStepKey,
                title: stepTitle,
                note: val,
                timestamp: timestamp
            };
            
            if (existingNoteIdx !== -1) {
                this.notesLog[existingNoteIdx] = noteObj;
            } else {
                this.notesLog.push(noteObj);
            }
        } else {
            if (existingNoteIdx !== -1) {
                this.notesLog.splice(existingNoteIdx, 1);
            }
        }
        
        this.saveSessionToStorage();
        this.renderSidebarNotes();
        this.renderSidebarHypotheses();
        
        const indicator = document.getElementById('note-saved-indicator');
        if (indicator) {
            indicator.classList.remove('hidden');
            if (this.noteSavedTimeout) clearTimeout(this.noteSavedTimeout);
            this.noteSavedTimeout = setTimeout(() => {
                indicator.classList.add('hidden');
            }, 1500);
        }
    }

    clearAllNotes() {
        const confirmMsg = this.currentLang === 'es' ? 
            '¿Está seguro de que desea limpiar todas las anotaciones y variables de la bitácora de la sesión?' : 
            'Are you sure you want to clear all session notes and variables?';
        if (confirm(confirmMsg)) {
            this.notesLog = [];
            this.sessionVariables = {};
            this.saveSessionToStorage();
            this.renderSidebarVariables();
            this.renderSidebarNotes();
            this.renderSidebarHypotheses();
            
            const textarea = document.getElementById('step-note-textarea');
            if (textarea) textarea.value = '';
            
            if (this.activeView === 'flow') {
                this.renderCurrentStep();
            }
        }
    }

    calculateConfidence() {
        let score = 50;
        let invalidatedStreak = 0;
        if (this.notesLog) {
            this.notesLog.forEach(n => {
                if (n.note.includes('[EVIDENCIA CONFIRMA]')) {
                    score = Math.min(100, score + 15);
                    invalidatedStreak = 0;
                } else if (n.note.includes('[EVIDENCIA INVALIDA]')) {
                    score = Math.max(0, score - 10);
                    invalidatedStreak += 1;
                } else if (n.note.includes('[EVIDENCIA INCONCLUSA]')) {
                    score = Math.max(0, score - 5);
                }
            });
        }
        return { score, invalidatedStreak };
    }

    updateConfidenceIndicator() {
        const { score, invalidatedStreak } = this.calculateConfidence();
        const bar = document.getElementById('confidence-bar-fill');
        const text = document.getElementById('confidence-value-text');
        if (bar && text) {
            bar.style.width = `${score}%`;
            text.innerText = `${score}%`;
            if (score >= 70) {
                bar.style.background = '#22c55e';
                text.style.color = '#4ade80';
            } else if (score >= 40) {
                bar.style.background = '#facc15';
                text.style.color = '#facc15';
            } else {
                bar.style.background = '#ef4444';
                text.style.color = '#f87171';
            }
        }
        // Alerta contextual en web
        if (invalidatedStreak >= 3 && score < 40) {
            const alertBox = document.getElementById('scientific-alert-box');
            if (alertBox) {
                alertBox.innerHTML = `<div class="scientific-alert">
                    <strong>⚠️ Patrón detectado:</strong> Ha invalidado múltiples hipótesis consecutivas sin encontrar la causa raíz.
                    Sugerencias: (1) El síntoma podría ser efecto de otra causa no explorada,
                    (2) Verificar supuestos de diseño de red,
                    (3) Considerar escalar a revisión de arquitectura.
                </div>`;
                alertBox.classList.remove('hidden');
            }
        }
    }

    renderSidebarHypotheses() {
        const list = document.getElementById('sidebar-hypotheses-list');
        if (!list) return;
        list.innerHTML = '';
        
        // Build list of visited steps that have hypotheses
        const hypothesisEntries = [];
        for (const [techKey, techData] of Object.entries(this.data.KB)) {
            const steps = techData.steps || {};
            for (const [stepKey, step] of Object.entries(steps)) {
                if (step.hypothesis) {
                    // Check if this step was visited (has a note or is in history)
                    const wasVisited = this.notesLog.some(n => n.tech === techKey && n.step === stepKey) ||
                                      (this.activeTech === techKey && this.currentStepKey === stepKey) ||
                                      this.history.includes(stepKey);
                    if (wasVisited) {
                        const noteEntry = this.notesLog.find(n => n.tech === techKey && n.step === stepKey);
                        let status = 'inconclusive';
                        let statusLabel = 'Sin evidencia';
                        if (noteEntry && noteEntry.note) {
                            if (noteEntry.note.includes('[EVIDENCIA CONFIRMA]')) {
                                status = 'confirmed';
                                statusLabel = 'Confirmada';
                            } else if (noteEntry.note.includes('[EVIDENCIA INVALIDA]')) {
                                status = 'invalidated';
                                statusLabel = 'Invalidada';
                            } else if (noteEntry.note.includes('[EVIDENCIA INCONCLUSA]')) {
                                status = 'inconclusive';
                                statusLabel = 'Inconclusa';
                            }
                        }
                        hypothesisEntries.push({
                            techName: this.getLocalizedText(techData, 'name') || techKey,
                            stepKey,
                            title: step.title || stepKey,
                            hypothesis: step.hypothesis.substring(0, 120) + (step.hypothesis.length > 120 ? '...' : ''),
                            status,
                            statusLabel
                        });
                    }
                }
            }
        }
        
        if (hypothesisEntries.length === 0) {
            list.innerHTML = `<span class="empty-msg">${this.currentLang === 'es' ? 'Navega pasos con hipótesis científicas para ver el árbol de verificación.' : 'Navigate steps with scientific hypotheses to see the verification tree.'}</span>`;
            return;
        }
        
        hypothesisEntries.forEach(entry => {
            const node = document.createElement('div');
            node.className = `hypothesis-node ${entry.status}`;
            
            const title = document.createElement('div');
            title.className = 'hyp-title';
            title.innerText = entry.title;
            
            const meta = document.createElement('div');
            meta.className = 'hyp-meta';
            meta.innerText = `${entry.techName} — ${entry.hypothesis}`;
            
            const badge = document.createElement('span');
            badge.className = `hyp-status ${entry.status}`;
            badge.innerText = entry.statusLabel;
            
            node.appendChild(title);
            node.appendChild(meta);
            node.appendChild(badge);
            list.appendChild(node);
        });
    }

    exportSessionJSON() {
        const stepsWithEvidence = [];
        for (const [techKey, techData] of Object.entries(this.data.KB)) {
            const steps = techData.steps || {};
            for (const [stepKey, step] of Object.entries(steps)) {
                if (step.hypothesis) {
                    const noteEntry = this.notesLog.find(n => n.tech === techKey && n.step === stepKey);
                    let outcome = null;
                    let evidenceDetail = null;
                    if (noteEntry && noteEntry.note) {
                        if (noteEntry.note.includes('[EVIDENCIA CONFIRMA]')) outcome = 'CONFIRMA';
                        else if (noteEntry.note.includes('[EVIDENCIA INVALIDA]')) outcome = 'INVALIDA';
                        else if (noteEntry.note.includes('[EVIDENCIA INCONCLUSA]')) outcome = 'INCONCLUSA';
                        const match = noteEntry.note.match(/\[EVIDENCIA [^\]]+\] (.+)/);
                        if (match) evidenceDetail = match[1];
                    }
                    stepsWithEvidence.push({
                        technology: techKey,
                        technology_name: this.getLocalizedText(techData, 'name') || techKey,
                        step_key: stepKey,
                        step_title: step.title || stepKey,
                        hypothesis: step.hypothesis,
                        verification_steps: step.verification_steps || [],
                        scientific_basis: step.scientific_basis || null,
                        confidence_level: step.confidence_level || null,
                        outcome,
                        evidence_detail: evidenceDetail,
                        notes: noteEntry ? noteEntry.note : null,
                        timestamp: noteEntry ? noteEntry.timestamp : null
                    });
                }
            }
        }
        
        const sessionObj = {
            session_id: `tshoot-${Date.now()}`,
            export_date: new Date().toISOString(),
            language: this.currentLang,
            tier: this.activeTier,
            vendor: this.activeVendor ? (this.data.VendorMap[this.activeVendor] || this.activeVendor) : null,
            variables: this.sessionVariables,
            hypotheses_tested: stepsWithEvidence,
            raw_notes: this.notesLog
        };
        
        const blob = new Blob([JSON.stringify(sessionObj, null, 2)], { type: 'application/json;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tshoot_session_${new Date().toISOString().slice(0,10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    exportSessionReport() {
        if (!this.notesLog || this.notesLog.length === 0) {
            const alertMsg = this.currentLang === 'es' ? 
                'No hay notas registradas para exportar.' : 
                'No notes logged to export.';
            alert(alertMsg);
            return;
        }
        
        let md = `# ${this.currentLang === 'es' ? 'Reporte de Diagnóstico y Troubleshooting de Redes' : 'Network Diagnostics & Troubleshooting Report'}\n\n`;
        md += `**${this.currentLang === 'es' ? 'Fecha y Hora:' : 'Date & Time:'}** ${new Date().toLocaleString()}\n`;
        md += `**${this.currentLang === 'es' ? 'Nivel de Diagnóstico:' : 'Diagnostics Level:'}** Tier ${this.activeTier}\n`;
        if (this.activeVendor) {
            md += `**${this.currentLang === 'es' ? 'Vendor Principal:' : 'Primary Vendor:'}** ${this.data.VendorMap[this.activeVendor] || this.activeVendor}\n`;
        }
        
        const varKeys = Object.keys(this.sessionVariables).filter(k => this.sessionVariables[k]);
        if (varKeys.length > 0) {
            md += `\n## ${this.currentLang === 'es' ? 'Variables de Comandos Utilizadas' : 'Command Variables Used'}\n`;
            varKeys.forEach(k => {
                md += `- **\`<${k}>\`**: \`${this.sessionVariables[k]}\`\n`;
            });
        }
        
        md += `\n## ${this.currentLang === 'es' ? 'Bitácora de Hallazgos y Notas' : 'Logged Findings & Notes'}\n`;
        this.notesLog.forEach(n => {
            md += `\n### ${(n.tech_name || n.techName || '')} — ${n.title}\n`;
            md += `- **${this.currentLang === 'es' ? 'Fecha/Hora:' : 'Date/Time:'}** ${n.timestamp}\n`;
            if (n.note.includes('5 PORQUÉS') || n.note.includes('5 WHYS')) {
                md += `- **${this.currentLang === 'es' ? 'Tipo:' : 'Type:'}** ${this.currentLang === 'es' ? 'Análisis de Causa Raíz (RCA)' : 'Root Cause Analysis (RCA)'}\n`;
                md += `- **${this.currentLang === 'es' ? 'Contenido:' : 'Content:'}**\n\n`;
                n.note.split('\n').forEach(line => {
                    md += `  > ${line}\n`;
                });
            } else {
                md += `- **${this.currentLang === 'es' ? 'Notas registradas:' : 'Logged notes:'}**\n\n`;
                n.note.split('\n').forEach(line => {
                    md += `  ${line}\n`;
                });
            }
        });

        // Quick Fixes applied
        const fixes = [];
        for (const n of this.notesLog) {
            const steps = this.data.KB[n.tech] && this.data.KB[n.tech].steps ? this.data.KB[n.tech].steps : {};
            const s = steps[n.step] || {};
            if (s.fix) {
                fixes.push({ tech: n.tech_name, title: n.title, fix: s.fix });
            }
        }
        if (fixes.length > 0) {
            md += `\n## ${this.currentLang === 'es' ? 'Soluciones Aplicadas (Quick Fixes)' : 'Applied Quick Fixes'}\n`;
            fixes.forEach(f => {
                md += `\n### ${f.tech} — ${f.title}\n`;
                md += f.fix.split('\n').map(l => `  ${l}`).join('\n') + '\n';
            });
        }

        // Evidence registered
        if (this.evidenceRegistered.size > 0) {
            md += `\n## ${this.currentLang === 'es' ? 'Evidencia Registrada' : 'Registered Evidence'}\n`;
            for (const evKey of this.evidenceRegistered) {
                md += `- ✅ ${evKey}\n`;
            }
        }
        
        const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reporte_tshoot_${new Date().toISOString().slice(0,10)}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    renderTheoryConcepts() {
        let techKey = this.activeTech;
        let concepts = this.data.TECH_CONCEPTS[techKey];
        if (!concepts && techKey && techKey.endsWith('_config')) {
            const baseKey = techKey.replace('_config', '');
            concepts = this.data.TECH_CONCEPTS[baseKey];
        }
        concepts = concepts || {};
        this.renderTheoryTabContent(concepts);
    }

    switchConceptTab(tab, event) {
        this.activeTheoryTab = tab;
        
        const tabContainer = event.target.parentElement;
        tabContainer.querySelectorAll('.concept-tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
        this.renderTheoryConcepts();
    }

    toggleTheoryCollapse() {
        this.theoryCollapsed = !this.theoryCollapsed;
        document.getElementById('theory-collapsible').classList.toggle('collapsed', this.theoryCollapsed);
    }

    renderTheoryTabContent(conceptsObj) {
        const panel = document.getElementById('concept-panel-content');
        if (!panel) return;
        const activeTabKey = this.activeTheoryTab;
        const text = this.getLocalizedText(conceptsObj, activeTabKey) || (this.currentLang === 'es' ? 'No definido para esta categoría.' : 'Not defined for this category.');
        panel.innerHTML = this.replaceMarkdown(text);
    }

    // ==========================================================================
    // NETWORK AUTOMATION CORNER
    // ==========================================================================
    initVendorMatrixData() {
        this.vendorMatrixData = {
            bgp: {
                cisco_xe: {
                    protocol: "RESTCONF (JSON / HTTPS) - YANG Model: Cisco-IOS-XE-bgp-oper",
                    path: "GET /restconf/data/Cisco-IOS-XE-bgp-oper:bgp-state-data/neighbors/neighbor=<peer_ip>",
                    strategy: "1. Autenticar mediante HTTPS Basic Auth.\n2. Consultar el endpoint de estado operacional de BGP.\n3. Extraer el objeto JSON nativo devuelto por el IOS-XE.",
                    strategy_en: "1. Authenticate using HTTPS Basic Auth.\n2. Query the OID/YANG operational BGP neighbor endpoint.\n3. Extract the native JSON payload returned by IOS-XE.",
                    assertion: "Validar que el campo 'connection-state' sea igual a 'ESTABLISHED' y que 'prefixes-received' sea mayor que 0.",
                    assertion_en: "Verify 'connection-state' is equal to 'ESTABLISHED' and 'prefixes-received' is greater than 0.",
                    example: "response = requests.get(url, headers={'Accept': 'application/yang-data+json'}, auth=(user, password))\nstate = response.json()['Cisco-IOS-XE-bgp-oper:neighbor']['connection-state']\nassert state == 'established'"
                },
                cisco_xr: {
                    protocol: "gNMI / gRPC Telemetry - YANG Model: openconfig-bgp",
                    path: "gNMI Subscribe PATH: /bgp/neighbors/neighbor[neighbor-address=<peer_ip>]/state",
                    strategy: "1. Establecer canal gRPC seguro/inseguro en puerto 57400.\n2. Suscribirse a la ruta de estado del peer BGP.\n3. Escuchar actualizaciones asíncronas disparadas por cambios de estado (on-change).",
                    strategy_en: "1. Open a secure or insecure gRPC channel on port 57400.\n2. Subscribe to the BGP neighbor state YANG path.\n3. Listen for asynchronous on-change stream notifications.",
                    assertion: "Si el evento 'session-state' cambia de 'ESTABLISHED', gatillar script de alerta y recolectar logs locales.",
                    assertion_en: "If 'session-state' events transition from 'ESTABLISHED', trigger alert webhooks and dump local logs.",
                    example: "# pygnmi client\nfor msg in client.subscribe(subscribe=sub_options):\n    state = msg['update']['values']['session-state']\n    if state != 'ESTABLISHED': alert_remediation()"
                },
                juniper: {
                    protocol: "NETCONF XML-RPC (Junos PyEZ)",
                    path: "RPC XML: <get-bgp-neighbor-information><neighbor-address><peer_ip></neighbor-address></get-bgp-neighbor-information>",
                    strategy: "1. Iniciar conexión NETCONF vía SSH (puerto 830).\n2. Enviar RPC estructurado para consultar neighbors.\n3. Parsear el árbol XML utilizando PyEZ para extraer el estado del peer.",
                    strategy_en: "1. Start a NETCONF session over SSH (port 830).\n2. Send a structured XML-RPC query for BGP peers.\n3. Parse the XML tree using PyEZ to extract operational values.",
                    assertion: "Comprobar que el tag XML <bgp-state> contenga el valor 'Established'.",
                    assertion_en: "Verify that the XML element <bgp-state> matches the value 'Established'.",
                    example: "from jnpr.junos.op.bgp import BgpTable\nbgp = BgpTable(dev).get()\nassert bgp[peer_ip]['state'] == 'Established'"
                },
                fortinet: {
                    protocol: "FortiOS REST API (JSON / HTTPS)",
                    path: "GET /api/v2/monitor/router/bgp",
                    strategy: "1. Autenticar mediante API token HTTP en cabecera.\n2. Realizar petición GET para obtener el estado del protocolo de ruteo.\n3. Filtrar el neighbor requerido en la lista JSON.",
                    strategy_en: "1. Authenticate using a custom HTTP API Token header.\n2. Perform a GET request to query the router BGP monitor database.\n3. Filter for the target neighbor in the JSON array.",
                    assertion: "Validar que 'state' sea 'Established' y que 'up' sea true.",
                    assertion_en: "Verify that the peer status is 'Established' and 'up' flag is true.",
                    example: "headers = {'Authorization': 'Bearer ' + api_token}\nres = requests.get(url, headers=headers)\npeers = res.json()['results']['neighbors']"
                },
                mikrotik: {
                    protocol: "RouterOS API (Python Package)",
                    path: "API Path: /routing/bgp/session/print where remote.address=<peer_ip>",
                    strategy: "1. Conectar al socket API (puerto 8728 o 8729 TLS).\n2. Enviar comando estructurado '/routing/bgp/session/print' con filtro de IP.\n3. Leer respuesta en formato clave-valor nativo de RouterOS.",
                    strategy_en: "1. Open a socket connection to RouterOS API port 8728 (or 8729 TLS).\n2. Send command string word-lists to query BGP session status.\n3. Parse the key-value dictionary list returned by RouterOS.",
                    assertion: "Validar que la propiedad 'established' sea 'yes' o que el 'state' sea 'established'.",
                    assertion_en: "Ensure 'established' equals 'yes' or 'state' equals 'established'.",
                    example: "api = routeros_api.RouterOSApiPool(host, username=user, password=pw)\napi.get_api().get_resource('/routing/bgp/session').get(remote_address=peer_ip)"
                },
                huawei: {
                    protocol: "NETCONF XML over SSH - VRP YANG",
                    path: "RPC Filter: <bgp oper-state=''><neighbors><neighbor><peer-ip><peer_ip></peer-ip></neighbor></neighbors></bgp>",
                    strategy: "1. Conectar vía NETCONF sobre SSH en puerto 830.\n2. Enviar filtro XML para recuperar estado de BGP oper.\n3. Analizar respuesta XML con ElementTree.",
                    strategy_en: "1. Connect over SSH on NETCONF port 830.\n2. Send XML query filter requesting bgp oper-state.\n3. Parse XML response trees using standard ElementTree namespaces.",
                    assertion: "Validar que '<connection-state>' sea 'Established'.",
                    assertion_en: "Ensure '<connection-state>' equals 'Established'.",
                    example: "netconf_conn.get(filter=('subtree', xml_filter))\nstate = root.find('.//connection-state').text\nassert state == 'Established'"
                },
                linux: {
                    protocol: "FRRouting (FRR) CLI + JSON output",
                    path: "CLI Command: vtysh -c \"show ip bgp summary json\"",
                    strategy: "1. Conectar vía SSH al host o ejecutar script localmente.\n2. Ejecutar la CLI de FRR (vtysh) solicitando salida estructurada JSON.\n3. Cargar el string de salida utilizando json.loads() en Python.",
                    strategy_en: "1. Connect over SSH or execute the python script locally on the server.\n2. Run the FRR command utility (vtysh) requesting json output.\n3. Load the output string using standard Python json.loads().",
                    assertion: "Inspeccionar que el peer tenga 'state' en 'Established'.",
                    assertion_en: "Check that the peer key 'state' evaluates to 'Established'.",
                    example: "import json, subprocess\nout = subprocess.check_output(['vtysh', '-c', 'show ip bgp summary json'])\ndata = json.loads(out)\nassert data['peers'][peer_ip]['state'] == 'Established'"
                }
            },
            ospf: {
                cisco_xe: {
                    protocol: "RESTCONF (JSON / HTTPS) - YANG Model: Cisco-IOS-XE-ospf-oper",
                    path: "GET /restconf/data/Cisco-IOS-XE-ospf-oper:ospf-oper-data/ospf-state/neighbors",
                    strategy: "1. Consultar el endpoint RESTCONF de estado OSPF.\n2. Analizar vecinos activos y detectar estados transitorios (como EXSTART o EXCHANGE) que sugieren problemas de MTU.",
                    strategy_en: "1. Query OSPF operational state RESTCONF endpoint.\n2. Filter neighbor state values and search for stuck states like EXSTART or EXCHANGE, indicating MTU mismatch.",
                    assertion: "Validar que todos los vecinos tengan 'state' en 'FULL'.",
                    assertion_en: "Ensure neighbor status evaluates to 'FULL'.",
                    example: "resp = requests.get(url, auth=auth)\nstate = resp.json()['Cisco-IOS-XE-ospf-oper:neighbors']['neighbor'][0]['state']\nassert state == 'ospf-state-full'"
                },
                cisco_xr: {
                    protocol: "gNMI Telemetry - YANG Model: Cisco-IOS-XR-ipv4-ospf-oper",
                    path: "gNMI Subscription: /ospf/processes/process/default-vrf/neighbors",
                    strategy: "1. Suscribirse vía gRPC a las adyacencias OSPF.\n2. Monitorear flujos periódicos o por cambio para reaccionar ante flapping de OSPF.",
                    strategy_en: "1. Connect to gRPC stream for OSPF adjacencies.\n2. Analyze BUM/hellos and capture state changes in real-time.",
                    assertion: "Alertar si el estado de vecindad cae de 'FULL'.",
                    assertion_en: "Alert if OSPF neighbor state drops below 'FULL'.",
                    example: "# gNMI telemetry listener\nstate = update['ospf-state']\nif state != 'FULL': trigger_mtu_checks()"
                },
                juniper: {
                    protocol: "NETCONF XML-RPC (Junos PyEZ)",
                    path: "RPC XML: <get-ospf-neighbor-information/>",
                    strategy: "1. Enviar rpc get-ospf-neighbor-information.\n2. Extraer lista de vecinos en XML.\n3. Recopilar MTU de interfaz en caso de fallas.",
                    strategy_en: "1. Send OSPF neighbor info XML-RPC query.\n2. Extract list of neighbours.\n3. Correlate with interface MTU if stuck in Exchange.",
                    assertion: "Comprobar que '<ospf-neighbor-state>' contenga 'Full'.",
                    assertion_en: "Ensure '<ospf-neighbor-state>' equals 'Full'.",
                    example: "neigh = dev.rpc.get_ospf_neighbor_information()\nfor n in neigh.xpath('.//ospf-neighbor'):\n    assert n.findtext('ospf-neighbor-state') == 'Full'"
                },
                fortinet: {
                    protocol: "FortiOS REST API",
                    path: "GET /api/v2/monitor/router/ospf/neighbors",
                    strategy: "1. Consultar monitor de OSPF vía REST API.\n2. Leer estado y conteos de retransmisión.",
                    strategy_en: "1. Query OSPF neighbours database via FortiOS REST API.\n2. Read adjacency states and retransmission counters.",
                    assertion: "Validar que el estado del neighbor sea 'Full'.",
                    assertion_en: "Ensure OSPF neighbor state matches 'Full'.",
                    example: "res = requests.get(url, headers=headers)\nassert res.json()['results'][0]['state'] == 'Full'"
                },
                mikrotik: {
                    protocol: "RouterOS API",
                    path: "/routing/ospf/neighbor/print",
                    strategy: "1. Ejecutar query de neighbors en RouterOS.\n2. Validar IP local e IP del peer.",
                    strategy_en: "1. Query RouterOS OSPF neighbors resource path.\n2. Verify local interface binding and peer IP.",
                    assertion: "Comprobar que 'state' sea 'Full'.",
                    assertion_en: "Verify 'state' parameter matches 'Full'.",
                    example: "neighs = api.get_resource('/routing/ospf/neighbor').get()\nassert neighs[0]['state'] == 'Full'"
                },
                huawei: {
                    protocol: "NETCONF / XML",
                    path: "RPC Filter: <ospf xmlns='...'><processes><process><neighbors><neighbor><state/></neighbor></neighbors></process></processes></ospf>",
                    strategy: "1. Enviar filtro XML de vecinos OSPF.\n2. Parsear el árbol XML de retorno.",
                    strategy_en: "1. Query OSPF operational state tree.\n2. Parse OSPF neighbours list from VRP database.",
                    assertion: "Validar que '<state>' contenga 'Full'.",
                    assertion_en: "Ensure neighbor '<state>' equals 'Full'.",
                    example: "res = netconf_conn.get(filter=xml_filter)\nassert 'Full' in res.data_xml"
                },
                linux: {
                    protocol: "FRRouting CLI (vtysh) + JSON",
                    path: "CLI Command: vtysh -c \"show ip ospf neighbor json\"",
                    strategy: "1. Ejecutar show ip ospf neighbor con bandera JSON.\n2. Cargar JSON en Python y recorrer la lista de vecinos.",
                    strategy_en: "1. Run OSPF neighbor CLI check appending json option.\n2. Parse JSON output and iterate over neighbors list.",
                    assertion: "Validar que todos los peers tengan 'nbrState' en 'Full'.",
                    assertion_en: "Ensure neighbor 'nbrState' is equal to 'Full'.",
                    example: "data = json.loads(subprocess.check_output(['vtysh', '-c', 'show ip ospf neighbor json']))\nassert data['neighbors'][0]['nbrState'] == 'Full'"
                }
            },
            nat: {
                cisco_xe: {
                    protocol: "RESTCONF (JSON / HTTPS) - YANG Model: Cisco-IOS-XE-nat-oper",
                    path: "GET /restconf/data/Cisco-IOS-XE-nat-oper:nat-oper-data/nat-stats",
                    strategy: "1. Consultar estadísticas de pool y traducciones activas.\n2. Analizar descartes por límites de traducción superados.",
                    strategy_en: "1. Query operational statistics for NAT/PAT pools.\n2. Capture allocation rates and drops due to translation limits.",
                    assertion: "Monitorear que 'active-translations' sea menor al 85% de la capacidad del hardware.",
                    assertion_en: "Verify 'active-translations' count does not exceed 85% of hardware limit.",
                    example: "stats = requests.get(url, auth=auth).json()\nratio = stats['nat-stats']['active-entries'] / max_limit"
                },
                cisco_xr: {
                    protocol: "gNMI Telemetry - YANG Model: Cisco-IOS-XR-ip-nat-oper",
                    path: "gNMI Subscription: /nat/instances/instance/stats",
                    strategy: "1. Suscribirse a los contadores de NAT CGNAT (Carrier-Grade NAT).\n2. Auditar la tasa de creación de sesiones en vivo.",
                    strategy_en: "1. Connect to CGNAT operational telemetry streams.\n2. Monitor dynamic port allocation rate for translation pools.",
                    assertion: "Alertar si la tasa de fallas de asignación (ports exhausted) incrementa.",
                    assertion_en: "Raise critical alert if port allocation failure count increases.",
                    example: "if update['port-alloc-failures'] > 0: trigger_scale_out_pool()"
                },
                juniper: {
                    protocol: "NETCONF XML-RPC (Junos PyEZ)",
                    path: "RPC XML: <get-security-nat-source-pool-information/>",
                    strategy: "1. Enviar RPC para consultar el estado del pool de NAT de origen.\n2. Extraer puertos en uso y puertos totales.",
                    strategy_en: "1. Send query to retrieve source NAT pool status.\n2. Extract allocated ports versus available ports in pool.",
                    assertion: "Calcular porcentaje de uso del pool. Alertar si supera el 90%.",
                    assertion_en: "Ensure source port utilization ratio is less than 90%.",
                    example: "pools = dev.rpc.get_security_nat_source_pool_information()\nfor p in pools.xpath('.//source-pool-entry'):\n    assert int(p.findtext('port-percent-used')) < 90"
                },
                fortinet: {
                    protocol: "FortiOS REST API",
                    path: "GET /api/v2/monitor/firewall/ippool",
                    strategy: "1. Consultar estado de IP Pools del Firewall.\n2. Recuperar conteo de puertos IP efímeros asignados en PAT.",
                    strategy_en: "1. Retrieve ippools state via FortiOS API monitor.\n2. Extract current session port allocations to identify Port Exhaustion.",
                    assertion: "Comprobar que ningún pool tenga puertos colisionados o agotados.",
                    assertion_en: "Confirm port-allocation ratios do not indicate exhaustion.",
                    example: "res = requests.get(url, headers=headers).json()\nfor pool in res['results']:\n    assert pool['percent_used'] < 90"
                },
                mikrotik: {
                    protocol: "RouterOS API",
                    path: "/ip/firewall/connection/print stats",
                    strategy: "1. Consultar tabla de conexiones NAT activas.\n2. Filtrar conexiones con estado 'srcnat' o 'dstnat'.",
                    strategy_en: "1. Query active firewall connections count via RouterOS API.\n2. Filter items containing srcnat/dstnat action markers.",
                    assertion: "Validar que el número de conexiones simultáneas esté dentro de los límites de RAM del router.",
                    assertion_en: "Ensure total concurrent connections align with available system RAM.",
                    example: "conns = api.get_resource('/ip/firewall/connection').get()\nprint('Total active connections:', len(conns))"
                },
                huawei: {
                    protocol: "NETCONF / VRP NAT Oper",
                    path: "RPC Filter: <nat-instance xmlns='...'><nat-pool-usage/></nat-instance>",
                    strategy: "1. Enviar RPC solicitando estadísticas de pool de NAT.\n2. Parsear el porcentaje de uso de puertos.",
                    strategy_en: "1. Send NETCONF RPC for NAT instance pool usage.\n2. Monitor dynamic port usage percentages.",
                    assertion: "Gatillar alerta si el porcentaje de uso de puertos supera el 85%.",
                    assertion_en: "Alert if PAT port utilization ratio exceeds 85%.",
                    example: "usage = root.find('.//port-usage-percent').text\nassert int(usage) < 85"
                },
                linux: {
                    protocol: "Linux sysfs / Conntrack stats",
                    path: "CLI Command: cat /proc/sys/net/netfilter/nf_conntrack_count",
                    strategy: "1. Leer el contador actual de la tabla conntrack del kernel.\n2. Compararlo con el límite máximo (nf_conntrack_max).",
                    strategy_en: "1. Read conntrack table count directly from proc filesystem.\n2. Compare against maximum limits configured in sysctl.",
                    assertion: "Validar que la tabla conntrack no esté saturada (evitar descarte silencioso de conexiones).",
                    assertion_en: "Verify current conntrack count is under 80% of conntrack max.",
                    example: "count = int(open('/proc/sys/net/netfilter/nf_conntrack_count').read())\nmax_lim = int(open('/proc/sys/net/netfilter/nf_conntrack_max').read())\nassert count / max_lim < 0.8"
                }
            },
            mpls: {
                cisco_xe: {
                    protocol: "RESTCONF (JSON / HTTPS) - YANG Model: Cisco-IOS-XE-mpls-ldp-oper",
                    path: "GET /restconf/data/Cisco-IOS-XE-mpls-ldp-oper:mpls-ldp-oper-data/ldp-peers",
                    strategy: "1. Consultar adyacencias LDP y sesiones TCP activas (puerto 646).\n2. Asegurar que las etiquetas estén sincronizadas con la tabla IGP (OSPF/IS-IS).",
                    strategy_en: "1. Query active LDP peers and TCP session states (port 646).\n2. Correlate learned labels with current IGP paths.",
                    assertion: "Comprobar que todas las sesiones LDP estén en estado 'OPERATIONAL'.",
                    assertion_en: "Ensure all LDP neighbor sessions are in 'OPERATIONAL' state.",
                    example: "peers = requests.get(url, auth=auth).json()\nstate = peers['ldp-peers']['ldp-peer'][0]['session-state']\nassert state == 'session-operational'"
                },
                cisco_xr: {
                    protocol: "NETCONF / RESTCONF - YANG Model: Cisco-IOS-XR-mpls-ldp-oper",
                    path: "GET /restconf/data/Cisco-IOS-XR-mpls-ldp-oper:mpls-ldp/global/default-vrf/bindings",
                    strategy: "1. Recuperar base de datos de etiquetas LDP (LIB).\n2. Validar la existencia de etiquetas de entrada y salida para cada FEC (Forwarding Equivalence Class).",
                    strategy_en: "1. Retrieve complete LDP label bindings database (LIB).\n2. Verify valid local and remote label bindings for prefix FECs.",
                    assertion: "Confirmar que el prefijo FEC loopback tenga una etiqueta remota válida asignada por el nexthop.",
                    assertion_en: "Verify target Loopback FEC is actively bound to a remote label.",
                    example: "bindings = requests.get(url, auth=auth).json()\nassert bindings['bindings'][0]['local-label'] is not None"
                },
                juniper: {
                    protocol: "NETCONF XML-RPC (Junos PyEZ)",
                    path: "RPC XML: <get-ldp-session-information/>",
                    strategy: "1. Enviar RPC get-ldp-session-information.\n2. Parsear el estado de la sesión LDP TCP.",
                    strategy_en: "1. Send get LDP session operational information XML-RPC.\n2. Verify TCP transport socket states (port 646).",
                    assertion: "Validar que el estado de la sesión sea 'Operational'.",
                    assertion_en: "Ensure LDP session-state matches 'Operational'.",
                    example: "sess = dev.rpc.get_ldp_session_information()\nassert sess.findtext('.//ldp-session-state') == 'Operational'"
                },
                fortinet: {
                    protocol: "FortiOS REST API",
                    path: "GET /api/v2/monitor/router/ldp/sessions",
                    strategy: "1. Consultar estado del protocolo LDP en FortiOS.\n2. Recuperar la lista de etiquetas de transporte MPLS.",
                    strategy_en: "1. Query FortiOS LDP monitor database.\n2. Verify active label bindings mapped to routing nexthops.",
                    assertion: "Validar estado de la sesión con los routers vecinos.",
                    assertion_en: "Ensure peer sessions evaluate to active operational status.",
                    example: "res = requests.get(url, headers=headers).json()\nassert res['results'][0]['status'] == 'up'"
                },
                mikrotik: {
                    protocol: "RouterOS API",
                    path: "/mpls/ldp/neighbor/print",
                    strategy: "1. Consultar tabla de vecinos LDP.\n2. Correlacionar con la tabla LFIB (`/mpls/local-mappings/print`).",
                    strategy_en: "1. Query active LDP neighbors via API.\n2. Correlate with LFIB local mappings table.",
                    assertion: "Comprobar que el vecino esté activo y resolviendo etiquetas.",
                    assertion_en: "Ensure LDP neighbors are resolving prefix labels.",
                    example: "neighs = api.get_resource('/mpls/ldp/neighbor').get()\nassert neighs[0]['active'] == 'true'"
                },
                huawei: {
                    protocol: "NETCONF / VRP MPLS LDP",
                    path: "RPC Filter: <ldp xmlns='...'><sessions><session><session-state/></session></sessions></ldp>",
                    strategy: "1. Enviar consulta NETCONF para recuperar sesiones LDP.\n2. Verificar estado operacional.",
                    strategy_en: "1. Query VRP LDP session states using NETCONF.\n2. Validate adjacency parameters.",
                    assertion: "Comprobar que 'session-state' sea 'Operational'.",
                    assertion_en: "Ensure LDP session-state equals 'Operational'.",
                    example: "res = netconf_conn.get(filter=xml_filter)\nassert 'Operational' in res.data_xml"
                },
                linux: {
                    protocol: "Linux Kernel MPLS + FRR LDPD JSON",
                    path: "CLI Command: vtysh -c \"show mpls ldp neighbor json\"",
                    strategy: "1. Ejecutar diagnóstico de frr ldpd en formato JSON.\n2. Validar estado de sockets TCP LDP.",
                    strategy_en: "1. Read FRRouting LDP daemon neighbors list in JSON format.\n2. Verify MPLS kernel module forwarding tables.",
                    assertion: "Validar que la sesión esté establecida ('Operational').",
                    assertion_en: "Ensure FRR LDP daemon session state is 'Operational'.",
                    example: "data = json.loads(subprocess.check_output(['vtysh', '-c', 'show mpls ldp neighbor json']))\nassert data['neighbors'][0]['state'] == 'Operational'"
                }
            },
            evpn: {
                cisco_xe: {
                    protocol: "RESTCONF (JSON / HTTPS) - YANG Model: Cisco-IOS-XE-evpn-oper",
                    path: "GET /restconf/data/Cisco-IOS-XE-evpn-oper:evpn-oper-data/evpn-instance-table",
                    strategy: "1. Consultar el estado del plano de control EVPN.\n2. Auditar la sincronización de MAC/IP sobre VXLAN.",
                    strategy_en: "1. Query EVPN instance control plane via RESTCONF.\n2. Audit MAC/IP routing synchronization over VXLAN tunnels.",
                    assertion: "Validar que las tablas de rutas EVPN estén recibiendo rutas Tipo 2 (MAC/IP) de peers remotos.",
                    assertion_en: "Ensure BGP EVPN tables contain active Type 2 (MAC/IP Advertisement) routes.",
                    example: "instances = requests.get(url, auth=auth).json()\nassert len(instances['evpn-instance-table']['evpn-instance']) > 0"
                },
                cisco_xr: {
                    protocol: "NETCONF / RESTCONF - YANG Model: Cisco-IOS-XR-l2vpn-oper",
                    path: "GET /restconf/data/Cisco-IOS-XR-l2vpn-oper:l2vpn-forwarding/nodes/node/evpn/peers",
                    strategy: "1. Recuperar el listado de peers EVPN configurados.\n2. Verificar la alcanzabilidad del túnel NVE (VTEP) local al remoto.",
                    strategy_en: "1. Retrieve list of active EVPN peers from IOS-XR L2VPN database.\n2. Verify local VTEP to remote VTEP logical reachability.",
                    assertion: "Asegurar que el estado del túnel NVE hacia el peer sea 'UP'.",
                    assertion_en: "Ensure dynamic VTEP tunnel operational state is 'UP'.",
                    example: "peers = requests.get(url, auth=auth).json()\nassert peers['peers'][0]['status'] == 'up'"
                },
                juniper: {
                    protocol: "NETCONF XML-RPC (Junos PyEZ)",
                    path: "RPC XML: <get-evpn-database-information/>",
                    strategy: "1. Enviar RPC get-evpn-database-information.\n2. Extraer mapeos de direcciones MAC y VTEPs remotos.",
                    strategy_en: "1. Send evpn database query XML-RPC.\n2. Extract learned MAC addresses and associated remote VTEP IP mappings.",
                    assertion: "Comprobar que las MACs críticas estén aprendidas con el flag 'R' (Remoto).",
                    assertion_en: "Ensure critical customer MACs are marked as learned from remote VTEPs.",
                    example: "evpn_db = dev.rpc.get_evpn_database_information()\nfor mac in evpn_db.xpath('.//evpn-database-mac'):\n    assert mac.findtext('mac-learned-from') is not None"
                },
                fortinet: {
                    protocol: "FortiOS REST API",
                    path: "GET /api/v2/monitor/router/bgp/evpn",
                    strategy: "1. Consultar estado de la base de datos BGP EVPN.\n2. Verificar el estado de la encapsulación VXLAN.",
                    strategy_en: "1. Retrieve BGP EVPN database status using REST API.\n2. Audit VXLAN virtual switch interface states.",
                    assertion: "Asegurar que los peers EVPN estén establecidos.",
                    assertion_en: "Ensure BGP EVPN peering sessions are Established.",
                    example: "res = requests.get(url, headers=headers).json()\nassert res['results']['peers'][0]['state'] == 'Established'"
                },
                mikrotik: {
                    protocol: "RouterOS API",
                    path: "/interface/vxlan/vtep/print",
                    strategy: "1. Consultar tabla de peers VTEP estáticos/dinámicos.\n2. Verificar puertos UDP asociados (puerto 4789).",
                    strategy_en: "1. Query RouterOS VXLAN VTEP interface configuration.\n2. Verify UDP port mappings (default: 4789).",
                    assertion: "Validar que la interfaz VXLAN esté activa (running).",
                    assertion_en: "Ensure target VXLAN tunnel interface flag matches 'running'.",
                    example: "vteps = api.get_resource('/interface/vxlan/vtep').get()\nassert len(vteps) > 0"
                },
                huawei: {
                    protocol: "NETCONF / VRP EVPN",
                    path: "RPC Filter: <evpn xmlns='...'><evpn-instances><evpn-instance><mac-limits/></evpn-instance></evpn-instances></evpn>",
                    strategy: "1. Consultar tabla de instancias EVPN.\n2. Validar que no se hayan superado los límites de MACs.",
                    strategy_en: "1. Query active EVPN instances and resource tables.\n2. Verify MAC learning limit status to prevent control plane overflow.",
                    assertion: "Comprobar que no haya alarmas de superación de límites de MAC.",
                    assertion_en: "Ensure MAC learning limit exceed flags are false.",
                    example: "res = netconf_conn.get(filter=xml_filter)\nassert 'limit-exceeded' not in res.data_xml"
                },
                linux: {
                    protocol: "Linux Bridge (bridge link) + FRR BGP EVPN JSON",
                    path: "CLI Command: vtysh -c \"show evpn mac vni all json\"",
                    strategy: "1. Ejecutar comando de FRR para listar MACs EVPN aprendidas.\n2. Correlacionar con las interfaces VXLAN del kernel de Linux.",
                    strategy_en: "1. Query FRRouting BGP EVPN MAC tables in JSON format.\n2. Cross-reference with kernel VXLAN configurations.",
                    assertion: "Validar que la MAC esté asociada a la VNI y al VTEP remoto correspondiente.",
                    assertion_en: "Ensure destination MAC is correctly mapped to VNI and active VTEP.",
                    example: "macs = json.loads(subprocess.check_output(['vtysh', '-c', 'show evpn mac vni all json']))\nassert macs[0]['vni'] == 10010"
                }
            },
            gpon: {
                cisco_xe: {
                    protocol: "Netmiko (SSH / CLI) - Catalyst PON OLT",
                    path: "CLI Command: show gpon onu summary",
                    strategy: "1. Conectar vía SSH a la OLT Catalyst PON.\n2. Recuperar la lista de ONUs registradas y potencias ópticas en el canal.",
                    strategy_en: "1. Connect over SSH to Catalyst PON OLT.\n2. Extract ONUs registration matrix and optical link budgets.",
                    assertion: "Comprobar que el estado de la ONU sea 'Active' y que la potencia Rx esté entre -15 y -27 dBm.",
                    assertion_en: "Verify ONU state is 'Active' and Rx optical power lies between -15 and -27 dBm.",
                    example: "out = ssh.send_command('show gpon onu summary')\nassert 'Active' in out"
                },
                cisco_xr: {
                    protocol: "No aplica en IOS-XR (Se usan SFPs GPON inteligentes/ONT en Router)",
                    path: "CLI Command: show controllers optics <optics-port>",
                    strategy: "1. Consultar el estado óptico del SFP GPON inteligente insertado en el router Cisco XR.\n2. Leer potencias de láser e información DDM.",
                    strategy_en: "1. Query optics diagnostics for smart GPON ONU SFPs inserted in Cisco XR routers.\n2. Extract DDM (Digital Diagnostics Monitoring) parameters.",
                    assertion: "Validar que el nivel de potencia óptica recibido esté dentro del umbral operativo.",
                    assertion_en: "Verify Rx Optical Power is within operational thresholds.",
                    example: "out = ssh.send_command('show controllers optics 0/0/0/1')\nassert 'Rx Power' in out"
                },
                juniper: {
                    protocol: "Netmiko (SSH) / Juniper OLT XML",
                    path: "RPC XML: <get-gpon-onu-information/>",
                    strategy: "1. Enviar RPC para consultar ONUs registradas en OLT Juniper.\n2. Extraer potencias y alarmas ópticas.",
                    strategy_en: "1. Send get GPON ONU operational information XML-RPC.\n2. Extract laser levels and optical warning counters.",
                    assertion: "Asegurar que la potencia óptica en '<onu-rx-power>' no sea menor a -27 dBm.",
                    assertion_en: "Verify '<onu-rx-power>' does not exceed critical loss limits (worse than -27 dBm).",
                    example: "res = dev.rpc.get_gpon_onu_information()\npower = float(res.findtext('.//onu-rx-power'))\nassert power > -27.0"
                },
                fortinet: {
                    protocol: "FortiOS CLI (SSH) - FortiGate ONT SFP",
                    path: "CLI Command: get system interface transceiver <port>",
                    strategy: "1. Ejecutar comando para leer telemetría del transceptor SFP GPON en el puerto WAN.\n2. Recuperar potencia Rx de la fibra óptica del ISP.",
                    strategy_en: "1. Execute transceiver status query on target SFP WAN port.\n2. Read raw Rx power coming from the ISP GPON network.",
                    assertion: "Verificar que la potencia del receptor óptico sea mayor a -27 dBm.",
                    assertion_en: "Ensure optical Rx power does not indicate fiber breakage (worse than -27 dBm).",
                    example: "out = ssh.send_command('get system interface transceiver wan1')\n# Parse rx power\nassert rx_dbm > -27.0"
                },
                mikrotik: {
                    protocol: "RouterOS API - SFP GPON interface",
                    path: "/interface/ethernet/monitor sfp1 once",
                    strategy: "1. Consultar métricas DDM del puerto SFP donde se conecta el módulo ONT GPON.\n2. Leer voltaje, temperatura y potencia Tx/Rx.",
                    strategy_en: "1. Query RouterOS SFP port DDM monitoring metrics.\n2. Extract optical Rx/Tx power levels and temperature status.",
                    assertion: "Validar que 'sfp-rx-power' sea superior a -27 dBm y que la interfaz reconozca el enlace (link-ok).",
                    assertion_en: "Ensure sfp-rx-power is above -27 dBm and interface link status is ok.",
                    example: "mon = api.get_resource('/interface/ethernet').call('monitor', {'numbers': 'sfp1', 'once': True})\nassert float(mon[0]['sfp-rx-power']) > -27.0"
                },
                huawei: {
                    protocol: "Netmiko (SSH) - OLT SmartAX / MA5600 / MA5800",
                    path: "CLI Command: display ont optical-info <frame> <slot> <port> <ont_id>",
                    strategy: "1. Conectar vía SSH a la OLT Huawei.\n2. Ingresar a modo de configuración y ejecutar comando de diagnóstico para la ONU específica.\n3. Extraer potencia Tx de la OLT y Rx de la ONT.",
                    strategy_en: "1. Connect to Huawei OLT via SSH.\n2. Execute the optical diagnostic command for the specific ONT ID.\n3. Extract OLT Tx power and ONT Rx power.",
                    assertion: "Asegurar que la potencia Rx esté entre -15.0 y -27.0 dBm. Valores menores (ej. -29 dBm) causarán descargas lentas y desconexiones.",
                    assertion_en: "Verify Rx power is between -15.0 and -27.0 dBm to prevent bit errors and flapping.",
                    example: "res = ssh.send_command('display ont optical-info 0 1 2 15')\n# Parse Rx power from output\nassert rx_power > -27.0"
                },
                linux: {
                    protocol: "Linux sysfs / ethtool - SFP DDM Optics",
                    path: "CLI Command: ethtool -m <interface>",
                    strategy: "1. Ejecutar ethtool solicitando la lectura del EEPROM del transceptor DDM.\n2. Recuperar valores ópticos reportados por el hardware en tiempo real.",
                    strategy_en: "1. Execute ethtool with the module EEPROM option (-m).\n2. Parse real-time optical power metrics reported by the SFP module.",
                    assertion: "Validar que el Rx power se encuentre dentro de los límites de calibración del SFP.",
                    assertion_en: "Verify receiver power matches operational DDM specifications.",
                    example: "out = subprocess.check_output(['ethtool', '-m', 'eth1']).decode()\n# Extract Receiver signal average optical power\nassert rx_power_dbm > -27.0"
                }
            },
            linux: {
                cisco_xe: {
                    protocol: "RESTCONF (JSON / HTTPS) - YANG Model: Cisco-IOS-XE-device-physical-oper",
                    path: "GET /restconf/data/Cisco-IOS-XE-device-physical-oper:physical-oper-data/cpu-usage",
                    strategy: "1. Consultar consumo de CPU y memoria física del equipo de red.\n2. Monitorear procesos sospechosos de alto consumo.",
                    strategy_en: "1. Query system resource utilization RESTCONF endpoint.\n2. Correlate CPU spikes with active network interrupts.",
                    assertion: "Verificar que la CPU promedio de 5 minutos sea inferior al 80%.",
                    assertion_en: "Ensure average 5-minute CPU load is less than 80%.",
                    example: "cpu = requests.get(url, auth=auth).json()\nassert cpu['cpu-usage']['cpu-utilization-five-minutes'] < 80"
                },
                cisco_xr: {
                    protocol: "gNMI Telemetry - YANG Model: Cisco-IOS-XR-wdsysmon-fd-oper",
                    path: "gNMI Subscription: /system-monitoring/cpu-utilization",
                    strategy: "1. Suscribirse a la telemetría del monitor del sistema.\n2. Monitorear carga de núcleos del procesador.",
                    strategy_en: "1. Subscribe to CPU system monitoring metrics via gNMI.\n2. Detect individual core utilization peaks.",
                    assertion: "Alertar si la CPU supera el 90%.",
                    assertion_en: "Raise alert if system CPU usage exceeds 90%.",
                    example: "if update['total-cpu'] > 90: alert_admin()"
                },
                juniper: {
                    protocol: "NETCONF XML-RPC (Junos PyEZ)",
                    path: "RPC XML: <get-system-statistics-information/>",
                    strategy: "1. Consultar estadísticas de procesamiento del sistema.\n2. Obtener buffers de sockets y uso de memoria kernel.",
                    strategy_en: "1. Retrieve system statistics XML-RPC.\n2. Query socket buffers and kernel memory allocation.",
                    assertion: "Comprobar que no haya errores de asignación de memoria.",
                    assertion_en: "Ensure zero memory allocation failures exist in system statistics.",
                    example: "res = dev.rpc.get_system_statistics_information()\nassert int(res.findtext('.//memory-failures')) == 0"
                },
                fortinet: {
                    protocol: "FortiOS REST API",
                    path: "GET /api/v2/monitor/system/cpu",
                    strategy: "1. Consultar el uso de CPU de los cores del Firewall.\n2. Detectar procesos de inspección IPS/SSL saturando el sistema.",
                    strategy_en: "1. Fetch CPU utilization metrics via REST API.\n2. Monitor individual core loads related to IPS/SSL inspection daemons.",
                    assertion: "Validar que el uso global del sistema esté por debajo del 85%.",
                    assertion_en: "Ensure total CPU load does not exceed 85%.",
                    example: "res = requests.get(url, headers=headers).json()\nassert res['results']['cpu_usage'] < 85"
                },
                mikrotik: {
                    protocol: "RouterOS API",
                    path: "/system/resource/print",
                    strategy: "1. Recuperar información de recursos del sistema.\n2. Verificar CPU, memoria RAM libre y almacenamiento flash.",
                    strategy_en: "1. Query system resource allocation metrics.\n2. Read CPU, free RAM, and storage utilization.",
                    assertion: "Validar que la RAM libre sea superior a 16MB para evitar caídas por Out-Of-Memory.",
                    assertion_en: "Ensure free RAM is greater than 16MB to prevent OOM events.",
                    example: "res = api.get_resource('/system/resource').get()\nassert int(res[0]['free-memory']) > 16*1024*1024"
                },
                huawei: {
                    protocol: "NETCONF / VRP System",
                    path: "RPC Filter: <system xmlns='...'><cpu-usage/></system>",
                    strategy: "1. Consultar la CPU del procesador del switch/router.\n2. Analizar uso de memoria del plano de control.",
                    strategy_en: "1. Query CPU utilization of system controller cards.\n2. Audit control plane RAM consumption.",
                    assertion: "Asegurar que el porcentaje de uso de CPU sea menor al 80%.",
                    assertion_en: "Ensure CPU utilization ratio remains below 80%.",
                    example: "res = netconf_conn.get(filter=xml_filter)\nassert int(root.find('.//cpu-usage').text) < 80"
                },
                linux: {
                    protocol: "Linux sysfs / Socket Diagnostics (ss / iproute2)",
                    path: "CLI Command: ss -t -a -u --json",
                    strategy: "1. Ejecutar ss para listar estadísticas completas de sockets en formato JSON.\n2. Verificar sockets en estado de espera (TIME-WAIT) y buffers de recepción/transmisión saturados.",
                    strategy_en: "1. Run socket statistics (ss) command requesting JSON formatting.\n2. Inspect queues (Recv-Q/Send-Q) and sockets in TIME-WAIT state.",
                    assertion: "Alertar si hay sockets con Recv-Q mayor que cero o si las conexiones activas agotan los file descriptors.",
                    assertion_en: "Assert Recv-Q is 0 and active connections do not exceed file descriptor limits.",
                    example: "import json, subprocess\nsockets = json.loads(subprocess.check_output(['ss', '-t', '-a', '--json']))\nfor s in sockets:\n    assert s['recv_q'] == 0"
                }
            }
        };
    }

    switchAutomationSubTab(subTab) {
        document.querySelectorAll('.auto-tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const activeBtn = document.getElementById(`auto-btn-${subTab}`);
        if (activeBtn) activeBtn.classList.add('active');

        document.querySelectorAll('.auto-subview').forEach(view => {
            view.classList.add('hidden');
            view.classList.remove('active');
        });
        const activeView = document.getElementById(`auto-subview-${subTab}`);
        if (activeView) {
            activeView.classList.remove('hidden');
            activeView.classList.add('active');
        }

        if (subTab === 'vendors') {
            this.renderVendorMatrixDetails();
        }
    }

    renderVendorMatrixDetails() {
        const techSelect = document.getElementById('auto-matrix-tech');
        const vendorSelect = document.getElementById('auto-matrix-vendor');
        const renderCard = document.getElementById('auto-matrix-details-card');
        
        if (!techSelect || !vendorSelect || !renderCard) return;
        
        const tech = techSelect.value;
        const vendor = vendorSelect.value;
        
        if (!this.vendorMatrixData) {
            this.initVendorMatrixData();
        }
        
        const data = this.vendorMatrixData[tech] && this.vendorMatrixData[tech][vendor] ? this.vendorMatrixData[tech][vendor] : null;
        
        if (!data) {
            renderCard.innerHTML = `<p>${this.currentLang === 'es' ? 'No hay información disponible para esta combinación.' : 'No details available for this combination.'}</p>`;
            return;
        }
        
        const strategyText = this.currentLang === 'en' ? (data.strategy_en || data.strategy) : data.strategy;
        const assertionText = this.currentLang === 'en' ? (data.assertion_en || data.assertion) : data.assertion;
        
        const labelProtocol = this.currentLang === 'es' ? 'Protocolo y Modelo YANG' : 'Protocol & YANG Model';
        const labelEndpoint = this.currentLang === 'es' ? 'Path API / Endpoint / Comando' : 'API Path / Endpoint / Command';
        const labelStrategy = this.currentLang === 'es' ? 'Estrategia de Automatización' : 'Automation Strategy';
        const labelAssertion = this.currentLang === 'es' ? 'Lógica de Aserción y Diagnóstico' : 'Assertion & Diagnostic Logic';
        const labelExample = this.currentLang === 'es' ? 'Ejemplo de Implementación' : 'Implementation Example';
        
        renderCard.innerHTML = `
            <div class="matrix-detail-item">
                <h5><i data-lucide="cpu" style="width:16px;height:16px;display:inline-block;vertical-align:middle;margin-right:6px;"></i>\${labelProtocol}</h5>
                <p class="matrix-code-like">\${data.protocol}</p>
            </div>
            <div class="matrix-detail-item">
                <h5><i data-lucide="link" style="width:16px;height:16px;display:inline-block;vertical-align:middle;margin-right:6px;"></i>\${labelEndpoint}</h5>
                <p class="matrix-code-like" style="color:var(--text-accent);">\${data.path}</p>
            </div>
            <div class="matrix-detail-item">
                <h5><i data-lucide="list-checks" style="width:16px;height:16px;display:inline-block;vertical-align:middle;margin-right:6px;"></i>\${labelStrategy}</h5>
                <p style="white-space: pre-line;">\${strategyText}</p>
            </div>
            <div class="matrix-detail-item">
                <h5><i data-lucide="shield-alert" style="width:16px;height:16px;display:inline-block;vertical-align:middle;margin-right:6px;"></i>\${labelAssertion}</h5>
                <p style="color:#facc15;font-weight:500;">\${assertionText}</p>
            </div>
            <div class="matrix-detail-item code-block-wrapper">
                <h5><i data-lucide="code" style="width:16px;height:16px;display:inline-block;vertical-align:middle;margin-right:6px;"></i>\${labelExample}</h5>
                <pre><code class="language-python">\${data.example}</code></pre>
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    openAutomationView() {
        this.initVendorMatrixData();
        if (!this.autoScripts) {
            this.autoScripts = [
              {
                id: "bgp_tshoot",
                tech: "BGP",
                tech_en: "BGP",
                name: "Diagnóstico de Sesión y Verificación de Rutas BGP",
                name_en: "BGP Session Diagnostics & Route Verification",
                description: "Script para recopilar el estado de los peers BGP, contadores de prefijos y rutas anunciadas/recibidas.",
                description_en: "Script to collect BGP peer status, prefix counters, and advertised/received routes.",
                architect_note: "BGP es propenso a caídas por fallas de MTU y desincronización en keepalives bajo congestión. La recolección manual de diagnósticos consume tiempo valioso; el uso de automatización estructurada evita errores operativos y permite auditorías en paralelo sobre múltiples adyacencias. Para eBGP multipropósito, asegure que el TTL-security o multihop estén alineados si el peering no es por enlace directo.",
                architect_note_en: "BGP is prone to session drops from MTU issues and keepalive desynchronization under network congestion. Automated diagnostics save critical response time. Ensure TTL-security or multihop are aligned if peering over indirect links.",
                variables: {
                  host: { label: "IP / Hostname del Router", label_en: "Router IP / Hostname", default: "10.10.10.1" },
                  username: { label: "Usuario SSH", label_en: "SSH Username", default: "admin" },
                  password: { label: "Contraseña", label_en: "Password", default: "cisco123" },
                  peer_ip: { label: "IP del Peer BGP", label_en: "BGP Peer IP", default: "10.10.10.2" },
                  asn: { label: "ASN Local", label_en: "Local ASN", default: "65001" }
                },
                python: `# Python / Netmiko BGP Diagnostics
from netmiko import ConnectHandler
import sys

device = {
    'device_type': 'cisco_ios',  # Alternativas: 'juniper_junos', 'huawei'
    'host': '<host>',
    'username': '<username>',
    'password': '<password>',
}

print(f"[*] Conectando a {device['host']} para auditoría BGP...")
try:
    with ConnectHandler(**device) as ssh:
        print("[+] Conexión establecida. Ejecutando comandos...")
        
        # 1. Verificar resumen BGP y estado de sesión
        bgp_sum = ssh.send_command("show ip bgp summary")
        print("\\n=== RESUMEN BGP ===")
        print(bgp_sum)
        
        # 2. Detalles del Peer específico
        peer_details = ssh.send_command("show ip bgp neighbors <peer_ip>")
        print("\\n=== DETALLES DEL PEER <peer_ip> ===")
        print(peer_details)
        
        # 3. Rutas recibidas y anunciadas
        print("[*] Recuperando prefijos desde Adj-RIB-In y Adj-RIB-Out...")
        rec_routes = ssh.send_command("show ip bgp neighbors <peer_ip> received-routes")
        adv_routes = ssh.send_command("show ip bgp neighbors <peer_ip> advertised-routes")
        
        print("\\n=== RUTAS RECIBIDAS (Adj-RIB-In) ===")
        print(rec_routes)
        print("\\n=== RUTAS ANUNCIADAS (Adj-RIB-Out) ===")
        print(adv_routes)
        
except Exception as e:
    print(f"[-] Error durante el diagnóstico de red: {e}")
    sys.exit(1)
`,
                ansible: `---
- name: Diagnóstico Automatizado de Sesión BGP
  hosts: all
  gather_facts: no
  vars:
    peer_ip: "<peer_ip>"
    local_asn: "<asn>"
  tasks:
    - name: Consultar Resumen BGP y Neighbors (Cisco IOS)
      cisco.ios.ios_command:
        commands:
          - show ip bgp summary
          - show ip bgp neighbors {{ peer_ip }}
          - show ip bgp neighbors {{ peer_ip }} advertised-routes
      register: ios_bgp_output

    - name: Imprimir Resultados de Diagnóstico BGP
      debug:
        msg: "{{ item }}"
      loop: "{{ ios_bgp_output.stdout_lines }}"
`,
                api: `# Obtener estado operacional del neighbor BGP mediante RESTCONF (Cisco IOS-XE)
curl -k -s -X GET \\
  "https://<host>/restconf/data/Cisco-IOS-XE-bgp-oper:bgp-state-data/neighbors/neighbor=<peer_ip>" \\
  -H "Accept: application/yang-data+json" \\
  -u "<username>:<password>"
`
              },
              {
                id: "ospf_tshoot",
                tech: "OSPF",
                tech_en: "OSPF",
                name: "Auditoría de Adyacencias OSPF y Comparación de MTU",
                name_en: "OSPF Adjacencies Audit & MTU Matcher",
                description: "Script para verificar vecinos OSPF, estados de interfaz y validar posibles discrepancias de MTU.",
                description_en: "Script to verify OSPF neighbors, interface states, and identify potential MTU mismatches.",
                architect_note: "Si OSPF queda atascado en EXSTART/EXCHANGE, verifique de inmediato las MTUs configuradas en los extremos. OSPF incluye la MTU en los paquetes Database Description (DBD) y no progresará a FULL si hay un desajuste. Este script automatiza la extracción de MTUs físicas y lógicas junto con los retransmits.",
                architect_note_en: "If OSPF is stuck in EXSTART/EXCHANGE, inspect the MTUs configured on both ends immediately. OSPF checks MTU in Database Description (DBD) packets and won't progress to FULL if they mismatch. This script automates MTU extraction.",
                variables: {
                  host: { label: "IP del Router", label_en: "Router IP", default: "10.20.20.1" },
                  username: { label: "Usuario SSH", label_en: "SSH Username", default: "admin" },
                  password: { label: "Contraseña", label_en: "Password", default: "admin123" },
                  interface: { label: "Interfaz de Enlace", label_en: "Link Interface", default: "GigabitEthernet1" },
                  ospf_process: { label: "ID de Proceso OSPF", label_en: "OSPF Process ID", default: "1" }
                },
                python: `# Python / Netmiko OSPF Diagnostic Script
from netmiko import ConnectHandler

device = {
    'device_type': 'cisco_ios',
    'host': '<host>',
    'username': '<username>',
    'password': '<password>',
}

try:
    print(f"Connecting to {device['host']} for OSPF audit...")
    with ConnectHandler(**device) as ssh:
        # Extraer vecinos OSPF globales
        ospf_neigh = ssh.send_command("show ip ospf neighbor")
        
        # Analizar interfaz OSPF en particular
        ospf_int = ssh.send_command("show ip ospf interface <interface>")
        
        # Verificar MTU física en la interfaz
        mtu_info = ssh.send_command("show interfaces <interface> | include MTU")
        
        # Verificar detalles de adyacencia y conteos de retransmisión
        neigh_detail = ssh.send_command("show ip ospf neighbor <interface> detail")
        
        print("\\n=== VECINOS OSPF ===")
        print(ospf_neigh)
        print("\\n=== ESTADO OSPF EN <interface> ===")
        print(ospf_int)
        print("\\n=== MTU DE LA INTERFAZ ===")
        print(mtu_info)
        print("\\n=== DETALLES DE RETRANSMISIÓN / ESTADO VECINO ===")
        print(neigh_detail)
        
except Exception as e:
    print(f"[-] OSPF diagnostic execution failed: {e}")
`,
                ansible: `---
- name: Diagnóstico de Vecindades y MTU OSPF
  hosts: all
  gather_facts: no
  vars:
    ospf_int: "<interface>"
  tasks:
    - name: Obtener Neighbors y Detalles de Interfaces OSPF
      cisco.ios.ios_command:
        commands:
          - show ip ospf neighbor
          - show ip ospf interface {{ ospf_int }}
          - show interfaces {{ ospf_int }} | include MTU
      register: ospf_out

    - name: Imprimir Análisis de Adyacencia OSPF
      debug:
        msg: "{{ item }}"
      loop: "{{ ospf_out.stdout_lines }}"
`,
                api: `# Consultar vecinos OSPF usando la API de Juniper (NETCONF over XML XML-RPC)
curl -k -s -X POST \\
  "https://<host>:830/rpc/get-ospf-neighbor-information" \\
  -u "<username>:<password>" \\
  -H "Content-Type: application/xml" \\
  -d "<get-ospf-neighbor-information/>"
`
              },
              {
                id: "nat_exhaustion",
                tech: "NAT",
                tech_en: "NAT",
                name: "Auditoría de Agotamiento de Puertos y Traducciones NAT",
                name_en: "NAT Port Exhaustion & Session Audit",
                description: "Script para diagnosticar el uso de pools NAT (PAT) y detectar descartes por falta de puertos efímeros en Fortinet/Cisco.",
                description_en: "Script to diagnose NAT (PAT) pool usage and detect packet drops due to ephemeral port exhaustion on Fortinet/Cisco.",
                architect_note: "El agotamiento de puertos (Port Exhaustion) en PAT degrada silenciosamente la navegación web de usuarios finales. Cada IP pública soporta máximo ~64K puertos TCP/UDP simultáneos. Si el volumen de conexiones concurrentes excede esta capacidad, el cortafuegos descarta el tráfico nuevo. Este script evalúa la ocupación del pool en tiempo real.",
                architect_note_en: "PAT port exhaustion silently drops user packets when active sessions exceed the ~64K ephemeral port limit per public IP. This script evaluates the IP pool allocation rate and reports peak capacity indicators.",
                variables: {
                  host: { label: "IP de Administración (Firewall)", label_en: "Firewall Admin IP", default: "192.168.1.1" },
                  username: { label: "Usuario", label_en: "Username", default: "admin" },
                  password: { label: "Contraseña", label_en: "Password", default: "forty123" },
                  nat_pool_name: { label: "Nombre del Pool NAT", label_en: "NAT Pool Name", default: "OUTBOUND_POOL" }
                },
                python: `# Python / Netmiko FortiOS NAT Pool Auditor
from netmiko import ConnectHandler

device = {
    'device_type': 'fortinet',
    'host': '<host>',
    'username': '<username>',
    'password': '<password>',
}

try:
    print(f"Connecting to FortiGate firewall at {device['host']}...")
    with ConnectHandler(**device) as ssh:
        # 1. Obtener estado de sesiones activas en el sistema
        sess_status = ssh.send_command("get system session status")
        print("\\n=== ESTADO DE SESIONES GLOBLAL ===")
        print(sess_status)
        
        # 2. Consultar uso de IP Pools y puertos reservados
        pool_status = ssh.send_command("diagnose firewall ippool-all list | grep -A 6 <nat_pool_name>")
        print("\\n=== ESTADO DE IP POOL: <nat_pool_name> ===")
        print(pool_status)
        
        # 3. Consultar estadísticas de colisiones o descartes NAT
        nat_stats = ssh.send_command("diagnose firewall ippool-all stats")
        print("\\n=== ESTADÍSTICAS GLOBALES DE IP POOL ===")
        print(nat_stats)

except Exception as e:
    print(f"[-] NAT Pool Audit connection failed: {e}")
`,
                ansible: `---
- name: Diagnóstico de IP Pools en FortiGate
  hosts: firewalls
  gather_facts: no
  tasks:
    - name: Consultar Estado de Pools NAT
      fortinet.fortios.fortios_monitor_fact:
        selector: 'firewall_ippool'
        vdom: 'root'
      register: fortigate_pools

    - name: Mostrar Información de Uso de Direcciones
      debug:
        var: fortigate_pools.meta.results
`,
                api: `# Consultar las traducciones NAT activas en Cisco IOS-XE vía RESTCONF
curl -k -s -X GET \\
  "https://<host>/restconf/data/Cisco-IOS-XE-nat-oper:nat-oper-data/nat-translations" \\
  -H "Accept: application/yang-data+json" \\
  -u "<username>:<password>"
`
              },
              {
                id: "mpls_ldp",
                tech: "MPLS",
                tech_en: "MPLS",
                name: "Verificación de Control Plane MPLS y Sincronización LDP-IGP",
                name_en: "MPLS Control Plane & LDP-IGP Sync Auditor",
                description: "Script para auditar vecinos LDP, base de datos de etiquetas (LFIB) y túneles RSVP-TE.",
                description_en: "Script to audit LDP neighbors, label forwarding database (LFIB), and RSVP-TE tunnels.",
                architect_note: "El desalineamiento LDP-IGP (donde el IGP declara una ruta pero LDP aún no genera la etiqueta de transporte) provoca el descarte silencioso del tráfico ('blackholing'). Para mitigar esto, configure LDP-IGP Synchronization. Este script valida que todas las adyacencias MPLS en el core tengan etiquetas válidas programadas en la LFIB.",
                architect_note_en: "LDP-IGP desynchronization causes silent traffic blackholing in MPLS cores. Standardize on LDP-IGP synchronization. This script verifies LDP neighbor tables and ensures LSPs are actively mapped to LFIB labels.",
                variables: {
                  host: { label: "IP del Router Core", label_en: "Core Router IP", default: "10.255.0.1" },
                  username: { label: "Usuario SSH", label_en: "SSH Username", default: "admin" },
                  password: { label: "Contraseña", label_en: "Password", default: "juniper123" },
                  fec_prefix: { label: "Prefijo FEC a Verificar", label_en: "FEC Prefix to Verify", default: "10.255.0.254/32" }
                },
                python: `# Python / Netmiko JunOS MPLS Core Diagnostics
from netmiko import ConnectHandler

device = {
    'device_type': 'juniper_junos',
    'host': '<host>',
    'username': '<username>',
    'password': '<password>',
}

try:
    print(f"Connecting to Juniper PE/P router {device['host']}...")
    with ConnectHandler(**device) as ssh:
        # 1. Verificar vecinos LDP
        ldp_neigh = ssh.send_command("show ldp neighbor")
        print("\\n=== VECINOS LDP ===")
        print(ldp_neigh)
        
        # 2. Verificar sesiones LDP
        ldp_sess = ssh.send_command("show ldp session")
        print("\\n=== SESIONES LDP ===")
        print(ldp_sess)
        
        # 3. Inspeccionar tabla de etiquetas (LFIB)
        mpls_routes = ssh.send_command("show route table mpls.0")
        print("\\n=== TABLA DE REDIRECCIONAMIENTO MPLS (LFIB) ===")
        print(mpls_routes)
        
        # 4. Verificar ruta específica hacia FEC
        fec_route = ssh.send_command("show route <fec_prefix>")
        print("\\n=== RUTA HACIA FEC <fec_prefix> ===")
        print(fec_route)

except Exception as e:
    print(f"[-] MPLS Diagnostics failed: {e}")
`,
                ansible: `---
- name: Auditoría de Control Plane MPLS JunOS
  hosts: core_routers
  gather_facts: no
  tasks:
    - name: Consultar Protocolos LDP e Interface MPLS
      junipernetworks.junos.junos_command:
        commands:
          - show ldp neighbor
          - show mpls interface
          - show route table mpls.0
      register: junos_mpls_output

    - name: Imprimir Resultados de Diagnóstico MPLS
      debug:
        msg: "{{ item }}"
      loop: "{{ junos_mpls_output.stdout_lines }}"
`,
                api: `# Consultar base de datos de enlaces y etiquetas LDP en Cisco IOS-XR vía RESTCONF
curl -k -s -X GET \\
  "https://<host>/restconf/data/Cisco-IOS-XR-mpls-ldp-oper:mpls-ldp/global/default-vrf/bindings" \\
  -H "Accept: application/yang-data+json" \\
  -u "<username>:<password>"
`
              },
              {
                id: "evpn_vxlan",
                tech: "EVPN/VXLAN",
                tech_en: "EVPN/VXLAN",
                name: "Auditoría de Plano de Control EVPN y Estado de Túneles VTEP",
                name_en: "EVPN Control Plane & VTEP Tunnel Auditor",
                description: "Script para auditar el estado de los túneles VXLAN (NVE), sesiones BGP EVPN y verificar la sincronización de MAC/IP (Rutas Tipo 2/3).",
                description_en: "Script to audit VXLAN (NVE) tunnels, BGP EVPN peering, and verify MAC/IP database sync (Type 2/3 Routes).",
                architect_note: "El control plane EVPN elimina la necesidad de inundación de tráfico broadcast/multicast (flood & learn) al anunciar MACs vía BGP. Si las rutas tipo 3 (Inclusive Multicast) fallan, el tráfico BUM no se replicará. Si fallan las rutas tipo 2, los hosts remotos perderán conectividad unicast directa. Use este script para asegurar el peering EVPN y túneles NVE.",
                architect_note_en: "EVPN control plane prevents blind flooding by advertising MACs via BGP. If Type 3 routes fail, BUM traffic is dropped. If Type 2 routes fail, unicast connectivity drops. This script verifies both BGP EVPN states and dynamic VTEP mappings.",
                variables: {
                  host: { label: "IP del VTEP Leaf / Switch", label_en: "VTEP Leaf IP / Switch", default: "172.16.100.1" },
                  username: { label: "Usuario SSH", label_en: "SSH Username", default: "admin" },
                  password: { label: "Contraseña", label_en: "Password", default: "cisco123" },
                  vni_id: { label: "VNI ID (VXLAN Network Identifier)", label_en: "VNI ID (VXLAN Network Identifier)", default: "10010" },
                  mac_addr: { label: "Dirección MAC del Host Destino", label_en: "Destination MAC Address", default: "00:50:56:ab:cd:12" }
                },
                python: `# Python / Netmiko EVPN/VXLAN Leaf Auditor
from netmiko import ConnectHandler

device = {
    'device_type': 'cisco_ios', # O 'cisco_nxos' según corresponda
    'host': '<host>',
    'username': '<username>',
    'password': '<password>',
}

try:
    print(f"Connecting to VTEP Leaf {device['host']}...")
    with ConnectHandler(**device) as ssh:
        # 1. Verificar túneles NVE activos
        vtep_peers = ssh.send_command("show nve peers")
        print("\\n=== PEERS TÚNELES VTEP VXLAN ===")
        print(vtep_peers)
        
        # 2. Resumen de vecinos BGP EVPN
        bgp_evpn = ssh.send_command("show bgp l2vpn evpn summary")
        print("\\n=== RESUMEN BGP L2VPN EVPN ===")
        print(bgp_evpn)
        
        # 3. Verificar base de datos de rutas EVPN para la VNI específica
        evpn_routes = ssh.send_command("show bgp l2vpn evpn vni-id <vni_id>")
        print("\\n=== RUTAS EVPN PARA VNI <vni_id> ===")
        print(evpn_routes)
        
        # 4. Mapeo local de MAC para el host destino
        mac_vni = ssh.send_command("show mac address-table vni <vni_id> | include <mac_addr>")
        print("\\n=== BÚSQUEDA DE MAC EN VNI <vni_id> ===")
        print(mac_vni)

except Exception as e:
    print(f"[-] EVPN/VXLAN Diagnostic execution failed: {e}")
`,
                ansible: `---
- name: Diagnóstico de Plano de Control EVPN VXLAN
  hosts: leaves
  gather_facts: no
  tasks:
    - name: Consultar Estado de Interfaces NVE y Vecinos BGP EVPN
      cisco.ios.ios_command:
        commands:
          - show nve peers
          - show bgp l2vpn evpn summary
      register: evpn_out

    - name: Imprimir Estado del Plano de Control EVPN
      debug:
        msg: "{{ item }}"
      loop: "{{ evpn_out.stdout_lines }}"
`,
                api: `# Consultar túneles NVE configurados en Nexus a través de NX-API (JSON-RPC)
curl -k -s -X POST \\
  "https://<host>/ins" \\
  -H "Content-Type: application/json" \\
  -u "<username>:<password>" \\
  -d '{
    "ins_api": {
      "version": "1.0",
      "type": "cli_show",
      "chunk": "0",
      "sid": "1",
      "input": "show nve interface nve1",
      "output_format": "json"
    }
  }'
`
              },
              {
                id: "gpon_olt",
                tech: "GPON/ONT",
                tech_en: "GPON/ONT",
                name: "Auditoría de Potencia Óptica y Diagnóstico de ONTs en OLT",
                name_en: "GPON OLT Optical Power & ONT Diagnostic",
                description: "Script para recopilar de forma masiva los estados de las ONTs (online/offline) y niveles de potencia óptica (Rx/Tx) desde la OLT.",
                description_en: "Script to gather ONT statuses (online/offline) and optical power levels (Rx/Tx) in bulk from the OLT.",
                architect_note: "En redes de fibra FTTH, la potencia óptica debe mantenerse entre -15 dBm y -27 dBm. Un nivel superior a -28 dBm (atenuación severa por dobleces o conectores sucios) provoca desconexión intermitente. La automatización estructurada permite escanear puertos completos para programar mantenimientos preventivos antes de que los clientes reporten fallas.",
                architect_note_en: "In FTTH GPON networks, optical power must range from -15 to -27 dBm. Levels worse than -28 dBm cause intermittent flapping due to frame errors. This script scans the OLT port in bulk to identify deteriorating links.",
                variables: {
                  host: { label: "IP de la OLT GPON", label_en: "GPON OLT IP", default: "10.200.200.1" },
                  username: { label: "Usuario", label_en: "Username", default: "admin" },
                  password: { label: "Contraseña", label_en: "Password", default: "huawei123" },
                  frame: { label: "Frame / Bastidor OLT", label_en: "OLT Frame ID", default: "0" },
                  slot: { label: "Slot / Tarjeta OLT", label_en: "OLT Slot ID", default: "1" },
                  port: { label: "Puerto GPON OLT", label_en: "OLT GPON Port", default: "2" },
                  ont_id: { label: "ID de la ONT", label_en: "ONT ID", default: "15" }
                },
                python: `# Python / Netmiko GPON OLT Fiber Diagnostic Script
from netmiko import ConnectHandler

device = {
    'device_type': 'huawei', # Configurable para ZTE u OLTs genéricas
    'host': '<host>',
    'username': '<username>',
    'password': '<password>',
}

try:
    print(f"Connecting to GPON OLT at {device['host']}...")
    with ConnectHandler(**device) as ssh:
        # Habilitar modo privilegios en OLT Huawei
        ssh.send_command("enable")
        ssh.send_command("config")
        
        # 1. Consultar estado general de la ONT seleccionada
        print("[*] Recuperando información general de la ONT...")
        ont_info = ssh.send_command("display ont info <frame> <slot> <port> <ont_id>")
        print("\\n=== INFORMACIÓN DE LA ONT ===")
        print(ont_info)
        
        # 2. Consultar información óptica y atenuación
        print("[*] Recuperando estado de potencia óptica y transceptores...")
        optical_info = ssh.send_command("display ont optical-info <frame> <slot> <port> <ont_id>")
        print("\\n=== INFORMACIÓN ÓPTICA ONT ===")
        print(optical_info)
        
        # 3. Consultar alarmas críticas del puerto GPON
        print("[*] Auditando alarmas en el puerto GPON...")
        gpon_alarms = ssh.send_command("display alarm history all list | grep -E 'gpon|ont'")
        print("\\n=== ALARMAS ACTIVAS HISTRÓRICAS ===")
        print(gpon_alarms)

except Exception as e:
    print(f"[-] GPON OLT diagnostic run failed: {e}")
`,
                ansible: `---
- name: Diagnóstico de Potencia Óptica GPON (Huawei)
  hosts: olts
  gather_facts: no
  tasks:
    - name: Consultar Información Óptica de la ONT
      community.network.huawei_command:
        commands:
          - display ont optical-info <frame> <slot> <port> <ont_id>
      register: opt_output

    - name: Imprimir Mediciones del Rx/Tx de la Fibra
      debug:
        msg: "{{ opt_output.stdout_lines }}"
`,
                api: `# Consulta de inventario de ONTs registradas mediante API del Middleware de aprovisionamiento
curl -k -s -X GET \\
  "https://<host>/api/v1/olt/gpon-onu?frame=<frame>&slot=<slot>&port=<port>&onu_id=<ont_id>" \\
  -H "Authorization: Bearer TokenSecret123"
`
              },
              {
                id: "linux_tshoot",
                tech: "Linux",
                tech_en: "Linux",
                name: "Diagnóstico de Kernel, Tablas Conntrack y Socket States Linux",
                name_en: "Linux Kernel Network & Socket Diagnostics",
                description: "Script para recopilar tablas de ruteo, socket counters, reglas iptables de NAT, y verificar errores en interfaces a nivel kernel.",
                description_en: "Script to gather routing tables, socket counters, iptables NAT rules, and verify interface errors at the kernel level.",
                architect_note: "Los problemas de red en servidores Linux frecuentemente no provienen de los enlaces físicos, sino de límites agotados en la pila IP del kernel (sysctl), como tablas de seguimiento de conexiones (conntrack) saturadas o búferes de sockets saturados. Este script extrae estadísticas de bajo nivel y diagnósticos del kernel.",
                architect_note_en: "Network issues in Linux servers are often caused by exhaustion in kernel IP tables (conntrack tables saturated, socket buffer overflows) rather than physical interface issues. This script extracts kernel-level diagnostics.",
                variables: {
                  host: { label: "IP del Servidor Linux", label_en: "Linux Server IP", default: "192.168.10.10" },
                  username: { label: "Usuario SSH", label_en: "SSH Username", default: "ubuntu" },
                  password: { label: "Contraseña / Frase de Paso", label_en: "Password / Passphrase", default: "root123" },
                  interface: { label: "Interfaz Ethernet", label_en: "Ethernet Interface", default: "eth0" }
                },
                python: `# Python / Paramiko Linux Server Diagnostic Collector
import paramiko
sys_exit = False
try:
    import sys
    sys_exit = True
except ImportError:
    pass

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Connecting to Linux system...")
    ssh.connect('<host>', username='<username>', password='<password>')
    
    commands = [
        "ip route show",
        "ss -s",
        "sysctl net.ipv4.ip_forward net.netfilter.nf_conntrack_max net.netfilter.nf_conntrack_count",
        "cat /proc/net/dev",
        "sudo iptables -t nat -L -n -v"
    ]
    
    for cmd in commands:
        print(f"\\n=== EXECUTING: {cmd} ===")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"[!] Warning/Error: {err}")
            
    ssh.close()
except Exception as e:
    print(f"[-] SSH Linux collection failed: {e}")
    if sys_exit:
        sys.exit(1)
`,
                ansible: `---
- name: Diagnóstico de Red de Bajo Nivel en Linux
  hosts: servers
  become: yes
  tasks:
    - name: Recopilar Estado de Sockets y Sysctl
      shell: |
        echo "=== SS STATUS ===" && ss -s
        echo "=== SYSCTL ===" && sysctl -a | grep -E 'conntrack_max|conntrack_count'
        echo "=== NETDEV ===" && cat /proc/net/dev
      register: linux_net_out

    - name: Imprimir Métricas de Kernel
      debug:
        msg: "{{ linux_net_out.stdout_lines }}"
`,
                api: `# Consulta de métricas operacionales de red del host expuestas por Prometheus Node Exporter
curl -s "http://<host>:9100/metrics" | grep -E '^node_network_receive_bytes_total|^node_network_transmit_errs_total'
`
              },
              {
                id: "pyats_state_diff",
                tech: "NetDevOps",
                tech_en: "NetDevOps",
                name: "Perfilamiento de Estado de Red y Verificación Automatizada (pyATS/Genie)",
                name_en: "Network State Profiling & Automated Verification (pyATS/Genie)",
                description: "Script de alta tecnología que utiliza Cisco pyATS y Genie para capturar el estado completo de la red (rutas, vecinos BGP, interfaces) antes y después de un cambio, realizando un diff automático para validar la correctitud del mantenimiento.",
                description_en: "High-tech script using Cisco pyATS and Genie to profile the network state (learned routes, BGP neighbors, interfaces) before and after a change, performing an automated state-diff to validate maintenance correctness.",
                architect_note: "El perfilamiento del estado de la red ('Golden Baseline') antes y después de una ventana de mantenimiento es la mejor práctica de NetDevOps. En lugar de verificar manualmente docenas de routers, pyATS aprende la topología en estructuras de datos JSON nativas y genera un reporte exacto de discrepancias (rutas perdidas, interfaces caídas, peers BGP inestables).",
                architect_note_en: "Network state profiling ('Golden Baseline') before and after a maintenance window is a core NetDevOps best practice. Instead of manually checking dozens of routers, pyATS learns the state in native JSON data structures and highlights exact discrepancies (missing routes, dropped interfaces, down BGP peers).",
                variables: {
                  testbed_file: { label: "Archivo de Testbed pyATS (YAML)", label_en: "pyATS Testbed File (YAML)", default: "testbed.yaml" },
                  feature_to_learn: { label: "Característica a Aprender (bgp/routing/interface)", label_en: "Feature to Learn (bgp/routing/interface)", default: "bgp" },
                  pre_state_file: { label: "Snapshot previo (JSON)", label_en: "Pre Snapshot (JSON)", default: "pre_maintenance.json" },
                  post_state_file: { label: "Snapshot posterior (JSON)", label_en: "Post Snapshot (JSON)", default: "post_maintenance.json" }
                },
                python: `# Python / Cisco pyATS & Genie State Profiler
from genie.testbed import load
from genie.utils.diff import Diff
import json

print("[*] Cargando testbed de la red...")
tb = load('<testbed_file>')

# Conectar a los dispositivos
print("[*] Conectando a los equipos...")
for name, dev in tb.devices.items():
    dev.connect(log_stdout=False)

# Aprender características del estado de red
print("[*] Perfilando el estado de BGP y de las interfaces...")
bgp_state = {}
for name, dev in tb.devices.items():
    try:
        # Genie aprende el feature en un formato JSON agnóstico del vendor
        bgp_state[name] = dev.learn('<feature_to_learn>').to_dict()
    except Exception as e:
        print(f"[-] Dispositivo {name} no soporta learning de <feature_to_learn>: {e}")

# Guardar estado actual
output_file = '<post_state_file>'
print(f"[*] Guardando estado aprendido en {output_file}...")
with open(output_file, 'w') as f:
    json.dump(bgp_state, f, indent=2)

# Si existe un archivo previo, realizar un Diff matemático de estados
try:
    print("[*] Cargando estado previo a ventana de mantenimiento para comparar...")
    with open('<pre_state_file>', 'r') as f:
        pre_state = json.load(f)
        
    # Calcular diferencias utilizando Genie Diff
    diff = Diff(pre_state, bgp_state)
    diff.findDiff()
    
    if diff:
        print("\\n[!] ALERTA: Se detectaron cambios en el estado de la red:")
        print(diff)
    else:
        print("\\n[+] VERIFICACIÓN COMPLETADA: Cero discrepancias en el estado de red.")
except FileNotFoundError:
    print("\\n[i] No se encontró el archivo de estado previo <pre_state_file>. Guardado baseline inicial.")
`,
                ansible: `---
- name: Perfilamiento y Comparación del Estado de Red con pyATS
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Capturar estado de red antes de cambios (Cisco/Juniper)
      ansible.builtin.shell: |
        pyats learn <feature_to_learn> --testbed <testbed_file> --output pre_state
      register: pyats_pre

    - name: Imprimir resumen de captura pyATS
      debug:
        msg: "Estado capturado en directorio pre_state"
`,
                api: `# Ejecutar perfilamiento automatizado invocando la API de pyATS/Genie Dashboard
curl -X POST "http://localhost:8000/api/v1/profile/diff" \\
  -H "Content-Type: application/json" \\
  -d '{
    "testbed": "<testbed_file>",
    "pre_snapshot": "<pre_state_file>",
    "post_snapshot": "<post_state_file>",
    "feature": "<feature_to_learn>"
  }'
`
              },
              {
                id: "gnmi_streaming_telemetry",
                tech: "Telemetry",
                tech_en: "Telemetry",
                name: "Recolector de Telemetría en Tiempo Real vía gNMI (gRPC) y YANG",
                name_en: "Real-Time Telemetry Collector via gNMI (gRPC) & YANG",
                description: "Script para suscribirse a flujos de streaming telemetry estructurada vía gNMI para monitorizar interfaces, CPU y BGP sin sobrecarga de CLI.",
                description_en: "Script to subscribe to structured streaming telemetry streams via gNMI to monitor interfaces, CPU, and BGP without CLI screen-scraping overhead.",
                architect_note: "El raspado de CLI tradicional (screen scraping) no escala y satura el plano de control del router. La telemetría por streaming impulsada por modelos (gNMI/YANG) empuja datos de forma asíncrona mediante gRPC HTTP/2. Este script se conecta a un router compatible con gNMI (Cisco XE/XR, Juniper JunOS, Nokia SR-OS) y se suscribe a una ruta de YANG específica.",
                architect_note_en: "Traditional CLI scraping does not scale and overloads the router control plane. Model-Driven Streaming Telemetry (gNMI/YANG) pushes data asynchronously using gRPC over HTTP/2. This script connects to a gNMI-compliant router (Cisco XE/XR, Juniper JunOS, Nokia SR-OS) and subscribes to a specific YANG path.",
                variables: {
                  host: { label: "IP del Router Core", label_en: "Core Router IP", default: "10.255.255.1" },
                  port: { label: "Puerto gRPC (gNMI)", label_en: "gRPC Port (gNMI)", default: "57400" },
                  username: { label: "Usuario Telemetría", label_en: "Telemetry Username", default: "telemetry_user" },
                  password: { label: "Contraseña", label_en: "Password", default: "secure_pass123" },
                  yang_path: { label: "Ruta YANG Abierta (openconfig)", label_en: "YANG Path (openconfig)", default: "/interfaces/interface/state/counters" }
                },
                python: `# Python / gNMI Streaming Telemetry Client using pygnmi
from pygnmi.client import gNMIclient
import json

target = {
    'server': '<host>:<port>',
    'username': '<username>',
    'password': '<password>',
    'insecure': True  # Usar TLS auto-firmado
}

# Definir la ruta del modelo YANG a suscribir
subscribe_path = {
    'path': '<yang_path>',
    'origin': 'openconfig-interfaces'
}

print(f"[*] Conectando vía gRPC al router gNMI {target['server']}...")
try:
    with gNMIclient(target=target['server'], username=target['username'], password=target['password'], insecure=target['insecure']) as client:
        print("[+] Conexión establecida. Iniciando suscripción en tiempo real...")
        
        # Crear una suscripción STREAM asíncrona
        subscribe_options = {
            'subscription': [
                {
                    'path': subscribe_path['path'],
                    'mode': 'on_change'  # O 'sample' para intervalos periódicos
                }
            ],
            'mode': 'stream',
            'encoding': 'json_ietf'
        }
        
        for telemetry_msg in client.subscribe(subscribe=subscribe_options):
            # Parsear actualizaciones del modelo estructurado YANG
            update = telemetry_msg.get('update', {})
            if update:
                print("\\n[+] Nueva actualización recibida vía gNMI:")
                print(json.dumps(update, indent=2))
                
except KeyboardInterrupt:
    print("\\n[!] Deteniendo suscripción de telemetría.")
except Exception as e:
    print(f"[-] Error en el recolector gNMI: {e}")
`,
                ansible: `---
- name: Habilitar gNMI Telemetry en el Router
  hosts: cisco_routers
  gather_facts: no
  tasks:
    - name: Configurar gRPC y gNMI Server (Cisco IOS-XE)
      cisco.ios.ios_config:
        lines:
          - grpc port <port>
          - grpc active
          - gnmi-server
`,
                api: `# Consultar capacidades del servidor gNMI (Capabilities RPC) para ver qué modelos YANG soporta
curl -X POST "http://<host>:<port>/gnmi.gNMI/Capabilities" \\
  -H "Content-Type: application/grpc" \\
  --user "<username>:<password>"
`
              },
              {
                id: "closed_loop_remediation",
                tech: "Closed-Loop",
                tech_en: "Closed-Loop",
                name: "Automatización de Ciclo Cerrado (Remediación Ante Alertas)",
                name_en: "Closed-Loop Automation (Alert-Driven Remediation Listener)",
                description: "Servidor de automatización en FastAPI que escucha alertas HTTP POST (por ejemplo, desde Prometheus/Alertmanager o Zabbix) y activa de forma autónoma diagnósticos recolectando evidencias y aplicando acciones paliativas.",
                description_en: "FastAPI automation server that listens to HTTP POST alerts (e.g., from Prometheus/Alertmanager or Zabbix) and autonomously triggers diagnostics, collects logs, and applies failover mitigations.",
                architect_note: "La automatización de ciclo cerrado (Closed-Loop Automation) reduce el MTTR (Mean Time to Resolution) a segundos. Al detectar una alerta (ej: caída de peer BGP), el sistema de monitoreo dispara un webhook a este microservicio. Este recopila de inmediato información de diagnóstico de bajo nivel en el router y, si es necesario, aplica un desvío redirigiendo el tráfico antes de que intervenga un ingeniero.",
                architect_note_en: "Closed-Loop Automation reduces MTTR (Mean Time to Resolution) to seconds. When an alert triggers (e.g., BGP peer down), the monitoring system hits this microservice. It immediately queries raw diagnostic states from the router and can apply temporary redirection policies before an engineer is paged.",
                variables: {
                  listen_port: { label: "Puerto del Servidor Web", label_en: "Web Server Listening Port", default: "8000" },
                  target_router: { label: "IP del Router Objetivo", label_en: "Target Router IP", default: "10.10.10.1" },
                  monitored_interface: { label: "Interfaz a Monitorear", label_en: "Monitored Interface", default: "GigabitEthernet2" },
                  slack_webhook: { label: "Webhook de Canal Slack", label_en: "Slack Webhook URL", default: "https://hooks.slack.com/services/T00/B00/X00" }
                },
                python: `# Python / Closed-Loop Remediation Webhook Listener using FastAPI
from fastapi import FastAPI, Request
from netmiko import ConnectHandler
import uvicorn
import requests

app = FastAPI()

ROUTER_IP = "<target_router>"
DEVICE = {
    'device_type': 'cisco_ios',
    'host': ROUTER_IP,
    'username': 'admin',
    'password': 'securepassword123',
}
SLACK_WEBHOOK = "<slack_webhook>"

def alert_slack(msg):
    print(f"[*] Notificando: {msg}")
    try:
        requests.post(SLACK_WEBHOOK, json={"text": msg})
    except Exception as e:
        print(f"Error Slack: {e}")

@app.post("/webhook/alert")
async def receive_alert(request: Request):
    payload = await request.json()
    alert_name = payload.get("alertname", "Unknown Alert")
    status = payload.get("status", "firing")
    
    print(f"[!] Recibido Webhook de Alerta: {alert_name} [Estado: {status}]")
    
    if status == "firing":
        alert_slack(f"🚨 Alerta activa: {alert_name}. Iniciando remediación automática en {ROUTER_IP}...")
        
        # Ejecutar recolección de diagnósticos y acción autónoma
        try:
            with ConnectHandler(**DEVICE) as ssh:
                print(f"[*] Conectando a {ROUTER_IP} para aislar falla...")
                # 1. Recolectar estadísticas de la interfaz
                int_stats = ssh.send_command("show interfaces <monitored_interface>")
                
                # 2. Aplicar acción autónoma: Reciclar la interfaz (Shut/No-Shut) si hay fallas recurrentes
                print(f"[!] Reiniciando interfaz <monitored_interface> de forma preventiva...")
                config_cmds = [
                    "interface <monitored_interface>",
                    "shutdown",
                    "no shutdown"
                ]
                ssh.send_config_set(config_cmds)
                
                alert_slack(f"✅ Remediación ejecutada en {ROUTER_IP}. Interfaz <monitored_interface> reiniciada de forma autónoma. Evidencias recolectadas.")
        except Exception as e:
            alert_slack(f"❌ Falla al ejecutar la remediación autónoma: {e}")
            
    return {"message": "Webhook procesado"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int("<listen_port>"))
`,
                ansible: `---
- name: Playbook de Remediación Ante Alertas de Monitoreo
  hosts: routers
  gather_facts: no
  tasks:
    - name: Reiniciar Interfaz Afectada
      cisco.ios.ios_config:
        lines:
          - shutdown
          - no shutdown
        parents: "interface <monitored_interface>"
`,
                api: `# Simular el disparo de una alerta de monitoreo (Zabbix/Prometheus) enviando un Webhook de prueba
curl -X POST "http://localhost:<listen_port>/webhook/alert" \\
  -H "Content-Type: application/json" \\
  -d '{
    "alertname": "LinkDown_Interface_GigabitEthernet2",
    "status": "firing",
    "severity": "critical"
  }'
`
              },
              {
                id: "batfish_verification",
                tech: "Verification",
                tech_en: "Verification",
                name: "Análisis Estático de Configuraciones y Validación de Políticas (Batfish)",
                name_en: "Configuration Static Analysis & Policy Validation (Batfish)",
                description: "Script para validar de forma estática archivos de configuración sin conectarse a los equipos físicos, analizando alcanzabilidad IP, loops de enrutamiento y vulnerabilidades de ACL.",
                description_en: "Script to validate configuration files statically without connecting to live hardware, analyzing IP reachability, routing loops, and ACL security vulnerabilities.",
                architect_note: "Batfish parsea configuraciones de Cisco, Juniper, Arista, etc., y construye un modelo matemático del plano de control en memoria. Esto permite simular el comportamiento del enrutamiento antes de cargar los archivos al equipo real. Es ideal para validación preventiva en pipelines de CI/CD (Pre-Commit / Pre-Deploy) en repositorios Git de infraestructura como código.",
                architect_note_en: "Batfish parses Cisco, Juniper, and Arista configuration files and builds a mathematical model of the control plane in memory. This lets you simulate routing behavior before committing files to live hardware. It is perfect for pre-deployment CI/CD pipeline validation.",
                variables: {
                  snapshot_dir: { label: "Directorio de Snapshot (Configs)", label_en: "Snapshot Directory (Configs)", default: "/opt/net_snapshots/current" },
                  source_node: { label: "Nodo de Origen (Hostname)", label_en: "Source Node (Hostname)", default: "border-router-01" },
                  dest_ip: { label: "IP de Destino de Prueba", label_en: "Test Destination IP", default: "8.8.8.8" },
                  ospf_area: { label: "ID de Área OSPF", label_en: "OSPF Area ID", default: "0" }
                },
                python: `# Python / Batfish Network Static Configuration Verification
from pybatfish.client.commands import bf_session, bf_init_snapshot
from pybatfish.question import bfq
import pandas as pd

print("[*] Inicializando sesión de análisis estático Batfish...")
bf_session.host = "localhost" # Puerto de API por defecto: 9996/9997

# Cargar archivos de configuración de la red (Snapshots)
bf_init_snapshot('<snapshot_dir>', name='network_snapshot', overwrite=True)

# 1. Validar que las configuraciones sean correctas y parseables
print("[*] Analizando sintaxis de los archivos de configuración...")
parse_status = bfq.fileParseStatus().answer().frame()
unparsed = parse_status[parse_status['Status'] != 'PASSED']
if not unparsed.empty:
    print("[!] ALERTA: Archivos con errores de sintaxis detectados:")
    print(unparsed[['File', 'Status']])
else:
    print("[+] Todas las configuraciones parseadas exitosamente.")

# 2. Auditar adyacencias OSPF modeladas matemáticamente
print("[*] Validando adyacencias OSPF en el plano de control simulado...")
ospf_edges = bfq.ospfEdges().answer().frame()
print(ospf_edges)

# 3. Validar alcanzabilidad IP (Simular traceroute lógico)
print("[*] Simulando alcanzabilidad de paquete IP hacia <dest_ip>...")
reachability = bfq.traceroute(startActivePorts='@enter(<source_node>)[<source_node>]', dstIp='<dest_ip>').answer().frame()

# Mostrar resultados
pd.set_option('display.max_colwidth', None)
print(reachability[['Flow', 'Traces']])
`,
                ansible: `---
- name: Validación de Configuraciones con Batfish
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Ejecutar contenedor de Batfish para análisis estático
      community.docker.docker_container:
        name: batfish
        image: batfish/batfish
        ports:
          - "9996:9996"
          - "9997:9997"
        state: started
`,
                api: `# Consultar base de datos de Batfish REST API
curl -s -X GET "http://localhost:9996/v2/workmgr/workloads"
`
              }
            ];
            
            this.autoScripts.forEach(sc => {
                sc.customValues = {};
                for (const [vKey, vData] of Object.entries(sc.variables)) {
                    sc.customValues[vKey] = vData.default;
                }
            });
            
            this.selectedAutoScript = this.autoScripts[0];
            this.autoScriptFormat = 'python';
            this.autoSearchQuery = '';
        }
        
        this.showView('automation');
        document.querySelectorAll('.tech-item').forEach(item => item.classList.remove('active'));
        this.filterAutoScripts();
        
        if (this.selectedAutoScript) {
            this.selectAutoScript(this.selectedAutoScript.id);
        }
        
        this.switchAutomationSubTab('concepts');
    }

    filterAutoScripts(event) {
        const query = event ? event.target.value.toLowerCase() : '';
        this.autoSearchQuery = query;
        
        const listContainer = document.getElementById('auto-scripts-list');
        if (!listContainer) return;
        
        listContainer.innerHTML = '';
        
        const filtered = this.autoScripts.filter(sc => {
            const name = this.getLocalizedText(sc, 'name').toLowerCase();
            const desc = this.getLocalizedText(sc, 'description').toLowerCase();
            const tech = this.getLocalizedText(sc, 'tech').toLowerCase();
            return name.includes(query) || desc.includes(query) || tech.includes(query);
        });
        
        if (filtered.length === 0) {
            listContainer.innerHTML = `<div style="font-size:0.75rem;color:var(--text-muted);text-align:center;padding:12px;">${this.currentLang === 'es' ? 'No hay coincidencias.' : 'No matches found.'}</div>`;
            return;
        }
        
        filtered.forEach(sc => {
            const activeClass = (this.selectedAutoScript && this.selectedAutoScript.id === sc.id) ? 'active' : '';
            const techBadge = this.getLocalizedText(sc, 'tech');
            const nameText = this.getLocalizedText(sc, 'name');
            
            const btn = document.createElement('button');
            btn.className = `auto-script-item ${activeClass}`;
            btn.onclick = () => this.selectAutoScript(sc.id);
            btn.innerHTML = `
                <span>${techBadge}</span>
                <h4>${nameText}</h4>
            `;
            listContainer.appendChild(btn);
        });
    }

    selectAutoScript(scriptId) {
        const script = this.autoScripts.find(sc => sc.id === scriptId);
        if (!script) return;
        
        this.selectedAutoScript = script;
        
        document.querySelectorAll('.auto-script-item').forEach(btn => {
            btn.classList.remove('active');
        });
        
        this.filterAutoScripts(); 
        
        const emptyEl = document.getElementById('auto-script-detail-empty');
        const contentEl = document.getElementById('auto-script-detail-content');
        
        if (emptyEl) emptyEl.classList.add('hidden');
        if (contentEl) contentEl.classList.remove('hidden');
        
        const techBadge = document.getElementById('auto-tech-badge');
        if (techBadge) techBadge.innerText = this.getLocalizedText(script, 'tech');
        
        const titleEl = document.getElementById('auto-script-title');
        if (titleEl) titleEl.innerText = this.getLocalizedText(script, 'name');
        
        const descEl = document.getElementById('auto-script-desc');
        if (descEl) descEl.innerText = this.getLocalizedText(script, 'description');
        
        const architectNoteText = document.getElementById('auto-architect-note-text');
        if (architectNoteText) architectNoteText.innerText = this.getLocalizedText(script, 'architect_note');
        
        const formEl = document.getElementById('auto-variables-form');
        if (formEl) {
            formEl.innerHTML = '';
            for (const [vKey, vData] of Object.entries(script.variables)) {
                const grp = document.createElement('div');
                grp.className = 'auto-var-group';
                
                const labelText = this.currentLang === 'en' ? (vData.label_en || vData.label) : vData.label;
                const val = script.customValues[vKey] !== undefined ? script.customValues[vKey] : vData.default;
                
                grp.innerHTML = `
                    <label for="auto-var-${vKey}">${labelText}</label>
                    <input type="text" id="auto-var-${vKey}" value="${val}" oninput="app.handleAutoVarChange(event, '${vKey}')">
                `;
                formEl.appendChild(grp);
            }
        }
        
        this.switchAutoCodeFormat(this.autoScriptFormat);
    }

    handleAutoVarChange(event, varKey) {
        if (!this.selectedAutoScript) return;
        this.selectedAutoScript.customValues[varKey] = event.target.value;
        this.renderAutoCode();
    }

    switchAutoCodeFormat(format) {
        this.autoScriptFormat = format;
        
        document.querySelectorAll('.code-tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const tabBtn = document.getElementById(`code-tab-${format}`);
        if (tabBtn) tabBtn.classList.add('active');
        
        const codeDisplay = document.getElementById('auto-code-display');
        if (codeDisplay) {
            codeDisplay.className = format === 'python' ? 'language-python' : (format === 'ansible' ? 'language-yaml' : 'language-bash');
        }
        
        this.renderAutoCode();
    }

    renderAutoCode() {
        const sc = this.selectedAutoScript;
        if (!sc) return;
        
        let template = sc[this.autoScriptFormat] || '';
        
        for (const [vKey, vData] of Object.entries(sc.variables)) {
            const val = sc.customValues[vKey] !== undefined ? sc.customValues[vKey] : vData.default;
            
            const regexAngle = new RegExp(`<${vKey}>`, 'g');
            template = template.replace(regexAngle, val);
            
            const regexBraces = new RegExp('{{\\\\s*' + vKey + '\\\\s*}}', 'g');
            template = template.replace(regexBraces, val);
        }
        
        const codeDisplay = document.getElementById('auto-code-display');
        if (codeDisplay) {
            codeDisplay.textContent = template;
        }
    }

    copyAutoScriptToClipboard() {
        const codeDisplay = document.getElementById('auto-code-display');
        if (!codeDisplay) return;
        
        const code = codeDisplay.textContent;
        navigator.clipboard.writeText(code).then(() => {
            const copyBtnText = document.getElementById('lbl-copy-auto-text');
            if (copyBtnText) {
                const originalText = this.currentLang === 'es' ? 'Copiar Script' : 'Copy Script';
                const successText = this.currentLang === 'es' ? '¡Copiado!' : 'Copied!';
                
                copyBtnText.innerText = successText;
                
                if (this.copiedAutoTimeout) clearTimeout(this.copiedAutoTimeout);
                this.copiedAutoTimeout = setTimeout(() => {
                    copyBtnText.innerText = originalText;
                    this.copiedAutoTimeout = null;
                }, 2000);
            }
        }).catch(err => {
            console.error("Could not copy script: ", err);
        });
    }
}

// Instantiate global app

const categoryMap = {
    es: {
        'routing': 'Enrutamiento Core (BGP, OSPF, IS-IS)',
        'switching': 'Conmutación y Redundancia (L2, STP, VRRP)',
        'security': 'Seguridad y Traducción (NAT, Firewall, VPN)',
        'carrier': 'Tecnologías Carrier & SP (MPLS, VXLAN, SD-WAN, GPON)',
        'other': 'Otros Escenarios de Red'
    },
    en: {
        'routing': 'Core Routing (BGP, OSPF, IS-IS)',
        'switching': 'Switching & Redundancy (L2, STP, VRRP)',
        'security': 'Security & Translation (NAT, Firewall, VPN)',
        'carrier': 'Carrier & SP Technologies (MPLS, VXLAN, SD-WAN, GPON)',
        'other': 'Other Network Scenarios'
    }
};

const techToCategory = {
    'bgp': 'routing',
    'ip_trace': 'routing',
    'bgp_config': 'routing',
    'mpbgp': 'routing',
    'mpbgp_config': 'routing',
    'ospf': 'routing',
    'ospf_config': 'routing',
    'isis': 'routing',
    'isis_config': 'routing',
    'static': 'routing',
    'static_config': 'routing',
    'static_routing': 'routing',
    'bfd': 'routing',
    'bfd_config': 'routing',
    'eigrp': 'routing',
    'eigrp_config': 'routing',
    'pbr': 'routing',
    'pbr_config': 'routing',
    'multicast': 'routing',
    'multicast_config': 'routing',
    'ripv2_config': 'routing',
    'spanning_tree': 'switching',
    'spanning_tree_config': 'switching',
    'rstp': 'switching',
    'switch_l2': 'switching',
    'switch_l2_config': 'switching',
    'vrrp_hsrp': 'switching',
    'vrrp_hsrp_config': 'switching',
    'evc': 'switching',
    'evc_config': 'switching',
    'ccc_interface_switch': 'switching',
    'nat': 'security',
    'nat_config': 'security',
    'security': 'security',
    'seguridad_config': 'security',
    'dmvpn': 'security',
    'dmvpn_config': 'security',
    'mpls': 'carrier',
    'mpls_config': 'carrier',
    'vxlan': 'carrier',
    'vxlan_config': 'carrier',
    'sdwan': 'carrier',
    'sdwan_config': 'carrier',
    'sr_mpls': 'carrier',
    'segment_routing_config': 'carrier',
    'qos_traffic_eng': 'carrier',
    'qos_traffic_eng_config': 'carrier',
    'fiber_ont': 'carrier',
    'fiber_ont_config': 'carrier',
    'adtran_ta5000': 'carrier',
    'evpn': 'carrier',
    'evpn_config': 'carrier',
    'l2vpn': 'carrier',
    'l2vpn_config': 'carrier',
    'l3vpn': 'carrier',
    'l3vpn_config': 'carrier',
    'dhcp': 'other',
    'dhcp_config': 'other',
    'aaa': 'other',
    'aaa_config': 'other',
    'netflow': 'other',
    'netflow_config': 'other',
    'netflow_ipfix': 'other',
    'ipv6': 'other',
    'ipv6_config': 'other',
    'ipv6_ndp': 'other',
    'wireshark_tcpdump': 'other',
    'linux_tshoot': 'other',
    'loop_troubleshooting': 'other',
    'subnet_31': 'routing',
    'subnet_31_config': 'routing'
};

const uiTranslations = {
    es: {
        appName: "NET-TSHOOT",
        lblScientificMode: "Modo Científico:",
        btnScientificNormal: "Normal",
        btnScientificSemiStrict: "Semi-Estricto",
        btnScientificStrict: "Estricto",
        descScientificNormal: "<strong>Modo Normal:</strong> Ejecución estándar de diagnóstico. Las hipótesis científicas de cada paso se muestran con fines informativos, sin forzar la recolección de evidencia empírica.",
        descScientificSemiStrict: "<strong>Modo Semi-Estricto:</strong> Se muestran advertencias si intenta avanzar sin hacer clic en 'Registrar Evidencia'. Promueve el rigor científico sin bloquear el flujo.",
        descScientificStrict: "<strong>Modo Estricto:</strong> Bloqueo operativo. Es obligatorio registrar evidencia de la hipótesis falsable del paso actual para poder avanzar al siguiente paso de diagnóstico.",
        appSubtitle: "Architect & Tier 3 Diagnostics",
        sessionTierLabel: "Nivel de Sesión:",
        techTitle: "Tecnologías",
        filterPlaceholder: "Filtrar tecnologías...",
        tabTroubleshooting: "Troubleshooting",
        tabConfig: "Configuración",
        btnOsiSim: "Simulaciones por Capas OSI",
        welcomeBadge: "PLATAFORMA ARQUITECTÓNICA DE RED",
        welcomeTitle: "Guías Diagnósticas y de Configuración de Multi-Vendor",
        welcomeDesc: "Plataforma interactiva para ingenieros Tier 3 y Arquitectos de Redes. Diseñada para guiar paso a paso el diagnóstico de fallas y despliegues complejos en MPLS, BGP, EVPN, VXLAN y NAT en múltiples vendors sin ejecutar comandos directamente en los equipos.",
        btnSearchStart: "Iniciar Búsqueda Global",
        btnViewSims: "Ver Simulaciones OSI",
        statsVendors: "5+ Vendors Clave",
        statsVendorsDesc: "Juniper JunOS, Cisco IOS-XE/XR, Fortinet, MikroTik, ADTRAN, Huawei/ZTE.",
        statsTechs: "30+ Tecnologías",
        statsTechsDesc: "Soporte completo desde capas de transporte MPLS hasta direccionamiento BGP y NAT.",
        statsCmds: "Comandos Dinámicos",
        statsCmdsDesc: "Copia y pega comandos reales introduciendo variables directas en el navegador.",
        accessQuickTitle: "Acceso Rápido a Tecnologías Comunes",
        quickNat: "NAT (Source, Dest, Static)",
        quickNatDesc: "Diagnóstico de agotamiento de puertos, tablas de sesión y depuración.",
        quickNatConfig: "NAT Avanzado",
        quickNatConfigDesc: "Configuración de reglas Source NAT, Destination NAT y Static NAT.",
        quickBgp: "BGP (Border Gateway Protocol)",
        quickBgpDesc: "Establecimiento de sesiones TCP, estados de peers, y enrutamiento vector-ruta.",
        quickBgpConfig: "Políticas BGP Avanzadas",
        quickBgpConfigDesc: "Configuración eBGP, iBGP, filtros de prefijos, políticas de exportación y communities.",
        quickMpls: "MPLS & LDP",
        quickMplsDesc: "Verificación de tablas LFIB, intercambio de etiquetas, PHP y sesiones LDP.",
        quickEvpn: "EVPN / VXLAN Control Plane",
        quickEvpnDesc: "Túneles VTEP, tablas MAC/IP de rutas EVPN (Tipo 2 y Tipo 3) en core IP.",
        bitacoraTitle: "Bitácora de Sesión",
        bitacoraEmptyVars: "No hay variables configuradas en esta sesión.",
        bitacoraEmptyNotes: "No has tomado notas en ningún paso aún. Escribe en la caja de anotaciones de un paso para guardar un registro.",
        bitacoraActiveVars: "Variables Configuradas",
        bitacoraNotesLogged: "Notas Registradas",
        btnExport: "Exportar Reporte (.md)",
        btnContextSwitchToConfig: "Ver Configuración",
        btnContextSwitchToTs: "Ver Troubleshooting",
        lblSelectVendor: "Seleccionar Vendor:",
        lblSelectTier: "Intensidad (Tier):",
        lblTheoryTitle: "Conceptos y Definiciones de Arquitectura",
        tabDef: "Definición",
        tabKey: "Conceptos Clave",
        tabArch: "Arquitectura",
        tabCtrl: "Control vs Datos",
        tabTshoot: "Estrategia de TS",
        tabBasics: "Fundamentos",
        lblVarsBoxTitle: "Variables de Comandos en este Paso",
        lblCopyCmds: "Copiar Comandos",
        lblExpectedOutcome: "Resultado Esperado / Qué Buscar",
        lblNotesLabel: "Anotaciones y Hallazgos para este paso:",
        lblNotesPlaceholder: "Escribe tus observaciones aquí (se guardará automáticamente en tu bitácora de sesión)...",
        lblNotesSaved: "Guardado",
        lblNextActionTitle: "¿Qué deseas hacer a continuación?",
        lblSimTimeline: "Línea de Tiempo del Flujo",
        lblSimActionExecuted: "Acción Ejecutada",
        lblSimArchitectNote: "Nota del Arquitecto",
        lblSimOsiHeader: "Análisis de Encapsulación en Capas OSI",
        modalTitle: "Catálogo de Escenarios de Simulación",
        modalSearchPlaceholder: "Filtrar escenarios por tecnología o nombre...",
        noResults: "No se encontraron resultados",
        searchTitle: "Resultados de Búsqueda Global",
        searchSub: "Mostrando coincidencias encontradas para:",
        searchResultsCount: "resultados",
        lblActiveScenario: "Escenario Activo:",
        lblSelectScenarioPlaceholder: "Seleccionar Escenario...",
        lblStepOf: "Paso {current} de {total}",
        lblStepNumber: "Paso {num}",
        lblTerminalCommands: "Comandos",
        lblTerminalSimulate: "Ejecutar Simulación",
        lblRunSim: "Ejecutar Diagnóstico",
        lblClearSim: "Limpiar Consola",
        lblScenarioState: "Estado del Escenario:",
        lblSimStateFail: "Con Falla",
        lblSimStateOk: "Solucionado",
        btnAutomation: "Automatización de TS",
        autoHeaderTitle: "Automatización de Diagnóstico (NetDevOps)",
        autoHeaderDesc: "Aprenda a diseñar, programar y ejecutar remediaciones autónomas y auditorías de estado multi-vendor.",
        lblAutoConcepts: "Conceptos de Automatización",
        lblAutoVendors: "Soporte por Vendor & Tecnologías",
        lblAutoLibrary: "Biblioteca de Scripts",
        lblAutoMatrixTitle: "Matriz de Diagnósticos por API y Modelos de Datos",
        lblAutoMatrixDesc: "Consulte los protocolos recomendados, paths de telemetría / YANG y scripts para automatizar la recopilación de evidencia empírica en cada vendor.",
        lblMatrixTech: "Tecnología a diagnosticar:",
        lblMatrixVendor: "Fabricante / Sistema Operativo:",
        autoSidebarTitle: "Bibliotecas y Scripts",
        autoSearchPlaceholder: "Filtrar scripts...",
        autoEmptyState: "Seleccione un script de la biblioteca para visualizar su código, variables, y detalles de arquitectura.",
        autoVarsTitle: "Variables de Configuración del Script",
        autoNoteTitle: "Nota del Arquitecto de Soluciones",
        autoTabPython: "Python (Netmiko)",
        autoTabAnsible: "Ansible Playbook",
        autoTabApi: "REST API / cURL",
        autoBtnCopy: "Copiar Script",
        autoBtnCopied: "¡Copiado!"
    },
    en: {
        appName: "NET-TSHOOT",
        lblScientificMode: "Scientific Mode:",
        btnScientificNormal: "Normal",
        btnScientificSemiStrict: "Semi-Strict",
        btnScientificStrict: "Strict",
        descScientificNormal: "<strong>Normal Mode:</strong> Standard diagnostic execution. The scientific hypotheses for each step are displayed for informational purposes, without enforcing empirical evidence collection.",
        descScientificSemiStrict: "<strong>Semi-Strict Mode:</strong> Visual warnings are displayed if you attempt to proceed without clicking 'Record Evidence'. Promotes scientific rigor without blocking the flow.",
        descScientificStrict: "<strong>Strict Mode:</strong> Operational block. It is mandatory to record evidence for the current step's falsifiable hypothesis to proceed to the next diagnostic step.",
        appSubtitle: "Architect & Tier 3 Diagnostics",
        sessionTierLabel: "Session Noc Level:",
        techTitle: "Technologies",
        filterPlaceholder: "Filter technologies...",
        tabTroubleshooting: "Troubleshooting",
        tabConfig: "Configuration",
        btnOsiSim: "OSI Layer Simulations",
        welcomeBadge: "NETWORK ARCHITECTURAL PLANE",
        welcomeTitle: "Multi-Vendor Diagnostics & Configuration Guides",
        welcomeDesc: "Interactive platform for Tier 3 engineers and Network Architects. Designed to guide step-by-step troubleshooting and complex deployment of MPLS, BGP, EVPN, VXLAN, and NAT across multiple vendors without running commands directly on live devices.",
        btnSearchStart: "Start Global Search",
        btnViewSims: "View OSI Simulations",
        statsVendors: "5+ Key Vendors",
        statsVendorsDesc: "Juniper JunOS, Cisco IOS-XE/XR, Fortinet, MikroTik, ADTRAN, Huawei/ZTE.",
        statsTechs: "30+ Technologies",
        statsTechsDesc: "Full support from MPLS transport layers to BGP routing and NAT.",
        statsCmds: "Dynamic Commands",
        statsCmdsDesc: "Copy and paste real-world commands by entering variables directly in the browser.",
        accessQuickTitle: "Quick Access to Common Technologies",
        quickNat: "NAT (Source, Dest, Static)",
        quickNatDesc: "Diagnostics of port exhaustion, session tables, and debugging.",
        quickNatConfig: "Advanced NAT",
        quickNatConfigDesc: "Configuration of Source NAT, Destination NAT, and Static NAT rules.",
        quickBgp: "BGP (Border Gateway Protocol)",
        quickBgpDesc: "TCP session establishment, peer states, and path-vector routing.",
        quickBgpConfig: "Advanced BGP Policies",
        quickBgpConfigDesc: "eBGP, iBGP configuration, prefix filtering, export policies, and communities.",
        quickMpls: "MPLS & LDP",
        quickMplsDesc: "Verification of LFIB tables, label exchange, PHP, and LDP sessions.",
        quickEvpn: "EVPN / VXLAN Control Plane",
        quickEvpnDesc: "VTEP tunnels, MAC/IP tables of EVPN routes (Type 2 and Type 3) in IP core.",
        bitacoraTitle: "Session Log",
        bitacoraEmptyVars: "No variables configured in this session.",
        bitacoraEmptyNotes: "You have not taken notes on any step yet. Write in the notes box of any step to log comments.",
        bitacoraActiveVars: "Configured Variables",
        bitacoraNotesLogged: "Logged Notes",
        btnExport: "Export Report (.md)",
        btnContextSwitchToConfig: "View Configuration",
        btnContextSwitchToTs: "View Troubleshooting",
        lblSelectVendor: "Select Vendor:",
        lblSelectTier: "Intensity (Tier):",
        lblTheoryTitle: "Architecture Concepts and Definitions",
        tabDef: "Definition",
        tabKey: "Key Concepts",
        tabArch: "Architecture",
        tabCtrl: "Control vs Data",
        tabTshoot: "TS Strategy",
        tabBasics: "Foundations",
        lblVarsBoxTitle: "Command Variables in this Step",
        lblCopyCmds: "Copy Commands",
        lblExpectedOutcome: "Expected Outcome / What to Look For",
        lblNotesLabel: "Notes and Findings for this step:",
        lblNotesPlaceholder: "Write your observations here (auto-saved to session log)...",
        lblNotesSaved: "Saved",
        lblNextActionTitle: "What would you like to do next?",
        lblSimTimeline: "Flow Timeline",
        lblSimActionExecuted: "Action Executed",
        lblSimArchitectNote: "Architect Note",
        lblSimOsiHeader: "OSI Layer Encapsulation Analysis",
        modalTitle: "Simulation Scenarios Catalog",
        modalSearchPlaceholder: "Filter scenarios by tech or name...",
        noResults: "No results found",
        searchTitle: "Global Search Results",
        searchSub: "Showing matches found for:",
        searchResultsCount: "results",
        lblActiveScenario: "Active Scenario:",
        lblSelectScenarioPlaceholder: "Select Scenario...",
        lblStepOf: "Step {current} of {total}",
        lblStepNumber: "Step {num}",
        lblTerminalCommands: "Commands",
        lblTerminalSimulate: "Run Simulation",
        lblRunSim: "Run Diagnostics",
        lblClearSim: "Clear Console",
        lblScenarioState: "Scenario State:",
        lblSimStateFail: "Failed",
        lblSimStateOk: "Healthy",
        btnAutomation: "TS Automation",
        autoHeaderTitle: "Diagnostics Automation (NetDevOps)",
        autoHeaderDesc: "Learn how to design, program, and execute autonomous remediations and multi-vendor state audits.",
        lblAutoConcepts: "Automation Concepts",
        lblAutoVendors: "Vendor & Technology Support",
        lblAutoLibrary: "Script Library",
        lblAutoMatrixTitle: "API & Data Model Diagnostics Matrix",
        lblAutoMatrixDesc: "Check recommended protocols, telemetry/YANG paths, and scripts to automate empirical evidence collection across vendors.",
        lblMatrixTech: "Technology to diagnose:",
        lblMatrixVendor: "Vendor / Operating System:",
        autoSidebarTitle: "Libraries & Scripts",
        autoSearchPlaceholder: "Filter scripts...",
        autoEmptyState: "Select a script from the library to view its code, variables, and architecture design.",
        autoVarsTitle: "Script Configuration Variables",
        autoNoteTitle: "Solutions Architect Note",
        autoTabPython: "Python (Netmiko)",
        autoTabAnsible: "Ansible Playbook",
        autoTabApi: "REST API / cURL",
        autoBtnCopy: "Copy Script",
        autoBtnCopied: "Copied!"
    }
};





const app = new WebApp();
window.onload = () => app.init();
