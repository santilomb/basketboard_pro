(function () {
    const INPUT_TAGS = new Set(['INPUT', 'SELECT', 'TEXTAREA']);
    const KEYBOARD_SHORTCUTS = [
        { code: 'Space', action: 'start-pause', label: 'Espacio' },
        { code: 'KeyR', action: 'reset-time', label: 'R' },
        { code: 'KeyP', action: 'next-period', label: 'P' },
        { code: 'KeyQ', action: 'score-local', value: 1, label: 'Q' },
        { code: 'KeyW', action: 'score-local', value: 2, label: 'W' },
        { code: 'KeyE', action: 'score-local', value: 3, label: 'E' },
        { code: 'KeyA', action: 'score-local', value: -1, label: 'A' },
        { code: 'KeyZ', action: 'foul-local', value: 1, label: 'Z' },
        { code: 'KeyX', action: 'foul-local', value: -1, label: 'X' },
        { code: 'KeyU', action: 'score-visit', value: 1, label: 'U' },
        { code: 'KeyI', action: 'score-visit', value: 2, label: 'I' },
        { code: 'KeyO', action: 'score-visit', value: 3, label: 'O' },
        { code: 'KeyJ', action: 'score-visit', value: -1, label: 'J' },
        { code: 'KeyM', action: 'foul-visit', value: 1, label: 'M' },
        { code: 'KeyN', action: 'foul-visit', value: -1, label: 'N' },
        { code: 'KeyT', action: 'set-countdown', label: 'T' },
        { code: 'KeyC', action: 'start-countdown', label: 'C' },
    ];

    function parseIntOr(value, fallback) {
        const parsed = parseInt(value, 10);
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function showToast(message, type = 'info') {
        const containerId = 'bbp-toast-container';
        let container = document.getElementById(containerId);
        if (!container) {
            container = document.createElement('div');
            container.id = containerId;
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => {
            toast.classList.add('is-visible');
        }, 20);
        setTimeout(() => {
            toast.classList.remove('is-visible');
            setTimeout(() => toast.remove(), 320);
        }, 3200);
    }

    function setText(selector, value) {
        document.querySelectorAll(selector).forEach((el) => {
            el.textContent = value;
        });
    }

    function updateState(state) {
        if (!state) {
            return;
        }
        setText('[data-field="local-score"]', state.points_local);
        setText('[data-field="visit-score"]', state.points_visit);
        setText('[data-field="period"]', `Período ${state.period}`);
        setText('[data-field="countdown"]', `Cuenta previa: ${state.countdown}`);
        setText('[data-field="fouls-local"]', state.fouls_local);
        setText('[data-field="fouls-visit"]', state.fouls_visit);
        setText('[data-field="local-name"]', state.team_local.name);
        setText('[data-field="visit-name"]', state.team_visit.name);

        document.querySelectorAll('[data-field="timer"]').forEach((el) => {
            el.textContent = state.time;
            const isCritical = state.time_style === 'critical';
            el.classList.toggle('timer-display--critical', isCritical);
            el.classList.toggle('timer-display--regular', !isCritical);
        });

        const countdownInput = document.getElementById('countdown-input');
        if (countdownInput && document.activeElement !== countdownInput) {
            countdownInput.value = state.countdown;
        }

        const localSelect = document.getElementById('local-team');
        if (localSelect && document.activeElement !== localSelect) {
            localSelect.value = String(state.selected.local);
        }

        const visitSelect = document.getElementById('visit-team');
        if (visitSelect && document.activeElement !== visitSelect) {
            visitSelect.value = String(state.selected.visit);
        }

        const typeSelect = document.getElementById('game-type');
        if (typeSelect && document.activeElement !== typeSelect) {
            typeSelect.value = String(state.selected.game_type);
        }

        const operatorTemplateSelect = document.getElementById('operator-template');
        if (operatorTemplateSelect && document.activeElement !== operatorTemplateSelect) {
            operatorTemplateSelect.value = state.operator_template;
        }

        const displayTemplateSelect = document.getElementById('display-template');
        if (displayTemplateSelect && document.activeElement !== displayTemplateSelect) {
            displayTemplateSelect.value = state.display_template;
        }
    }

    function triggerAction(bridge, action, value) {
        switch (action) {
            case 'start-pause':
                bridge.startPause();
                break;
            case 'reset-time':
                bridge.resetTime();
                break;
            case 'next-period':
                bridge.nextPeriod();
                break;
            case 'start-countdown':
                bridge.startPregame();
                showToast('Countdown iniciado');
                break;
            case 'set-countdown': {
                const input = document.getElementById('countdown-input');
                const countdownValue = input ? input.value : '';
                const success = bridge.setPregameCountdown(countdownValue ?? '');
                if (!success) {
                    showToast('Formato de tiempo inválido. Usa MM:SS', 'error');
                } else {
                    showToast('Countdown actualizado');
                }
                break;
            }
            case 'score-local':
                bridge.scoreLocal(parseIntOr(value, 0));
                break;
            case 'score-visit':
                bridge.scoreVisit(parseIntOr(value, 0));
                break;
            case 'foul-local':
                bridge.foulLocal(parseIntOr(value, 0));
                break;
            case 'foul-visit':
                bridge.foulVisit(parseIntOr(value, 0));
                break;
            default:
                break;
        }
    }

    function registerButtonActions(bridge) {
        document
            .querySelectorAll('[data-action]')
            .forEach((btn) => {
                btn.addEventListener('click', () => {
                    const action = btn.getAttribute('data-action');
                    if (!action) {
                        return;
                    }
                    const valueAttr = btn.getAttribute('data-value');
                    const value = valueAttr !== null ? parseIntOr(valueAttr, 0) : undefined;
                    triggerAction(bridge, action, value);
                });
            });
    }

    function keyLabelFromCode(code, fallback) {
        if (fallback) {
            return fallback;
        }
        if (code === 'Space') {
            return 'Espacio';
        }
        if (code.startsWith('Key')) {
            return code.replace('Key', '');
        }
        return code;
    }

    function applyShortcutHints(shortcuts) {
        shortcuts.forEach((shortcut) => {
            const selector = `[data-action="${shortcut.action}"]${
                typeof shortcut.value !== 'undefined' ? `[data-value="${shortcut.value}"]` : ''
            }`;
            document.querySelectorAll(selector).forEach((el) => {
                const label = keyLabelFromCode(shortcut.code, shortcut.label);
                el.setAttribute('title', `Atajo: ${label}`);
                if (!el.hasAttribute('data-shortcut')) {
                    el.setAttribute('data-shortcut', label);
                }
            });
        });
    }

    function setupKeyboardShortcuts(bridge) {
        document.addEventListener('keydown', (event) => {
            if (event.repeat) {
                return;
            }
            const target = event.target;
            if (target && (INPUT_TAGS.has(target.tagName) || target.isContentEditable)) {
                return;
            }
            const shortcut = KEYBOARD_SHORTCUTS.find((item) => item.code === event.code);
            if (!shortcut) {
                return;
            }
            event.preventDefault();
            triggerAction(bridge, shortcut.action, shortcut.value);
        });
        applyShortcutHints(KEYBOARD_SHORTCUTS);
    }

    function setupTabs() {
        const buttons = Array.from(document.querySelectorAll('[data-tab-target]'));
        const panels = Array.from(document.querySelectorAll('[data-tab-panel]'));
        const activate = (target) => {
            buttons.forEach((btn) => {
                const isActive = btn.getAttribute('data-tab-target') === target;
                btn.classList.toggle('is-active', isActive);
                btn.setAttribute('aria-selected', String(isActive));
            });
            panels.forEach((panel) => {
                const isActive = panel.getAttribute('data-tab-panel') === target;
                panel.classList.toggle('is-active', isActive);
                panel.setAttribute('aria-hidden', String(!isActive));
            });
        };
        buttons.forEach((btn) => {
            btn.addEventListener('click', () => {
                const target = btn.getAttribute('data-tab-target');
                if (target) {
                    activate(target);
                }
            });
        });
        const defaultTarget = buttons[0]?.getAttribute('data-tab-target');
        if (defaultTarget) {
            activate(defaultTarget);
        }
    }

    function attachBridge(bridge) {
        setupTabs();
        registerButtonActions(bridge);
        setupKeyboardShortcuts(bridge);

        const form = document.getElementById('match-form');
        if (form) {
            form.addEventListener('submit', (event) => {
                event.preventDefault();
                const local = parseIntOr(document.getElementById('local-team')?.value, 0);
                const visit = parseIntOr(document.getElementById('visit-team')?.value, 0);
                const gameType = parseIntOr(document.getElementById('game-type')?.value, 0);
                bridge.createMatch(local, visit, gameType);
                showToast('Configuración aplicada');
            });
        }

        const operatorTemplateSelect = document.getElementById('operator-template');
        if (operatorTemplateSelect) {
            operatorTemplateSelect.addEventListener('change', () => {
                const value = operatorTemplateSelect.value;
                bridge.setOperatorTemplate(value);
                const label = operatorTemplateSelect.selectedOptions[0]?.textContent || value;
                showToast(`Template del operador: ${label}`);
            });
        }

        const displayTemplateSelect = document.getElementById('display-template');
        if (displayTemplateSelect) {
            displayTemplateSelect.addEventListener('change', () => {
                const value = displayTemplateSelect.value;
                bridge.setDisplayTemplate(value);
                const label = displayTemplateSelect.selectedOptions[0]?.textContent || value;
                showToast(`Template del display: ${label}`);
            });
        }
    }

    if (typeof qt === 'undefined' || !qt.webChannelTransport) {
        console.error('Qt WebChannel no está disponible.');
        return;
    }

    new QWebChannel(qt.webChannelTransport, (channel) => {
        const bridge = channel.objects.OperatorBridge;
        if (!bridge) {
            console.error('No se encontró OperatorBridge.');
            return;
        }
        attachBridge(bridge);
        bridge.stateUpdated.connect((payload) => {
            try {
                const state = JSON.parse(payload);
                updateState(state);
            } catch (error) {
                console.error('No se pudo actualizar el estado', error);
            }
        });
        bridge.requestInitialState();
    });
})();
