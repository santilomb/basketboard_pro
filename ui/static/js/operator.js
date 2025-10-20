(function () {

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

    function updateThemeButtons(action, activeTheme) {
        document.querySelectorAll(`[data-action="${action}"]`).forEach((btn) => {
            const theme = btn.getAttribute('data-theme');
            if (theme === activeTheme) {
                btn.classList.add('btn--primary');
            } else {
                btn.classList.remove('btn--primary');
            }
        });
    }

    function updateState(state) {
        if (!state) {
            return;
        }
        const setText = (selector, value) => {
            const el = document.querySelector(selector);
            if (el) {
                el.textContent = value;
            }
        };

        setText('[data-field="local-score"]', state.points_local);
        setText('[data-field="visit-score"]', state.points_visit);
        setText('[data-field="timer"]', state.time);
        setText('[data-field="period"]', `Período ${state.period}`);
        setText('[data-field="countdown"]', `Cuenta previa: ${state.countdown}`);
        setText('[data-field="fouls-local"]', state.fouls_local);
        setText('[data-field="fouls-visit"]', state.fouls_visit);
        setText('[data-field="local-name"]', state.team_local.name);
        setText('[data-field="visit-name"]', state.team_visit.name);

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

        document.body.classList.remove('theme-dark', 'theme-light');
        document.body.classList.add(`theme-${state.operator_theme}`);

        updateThemeButtons('set-operator-theme', state.operator_theme);
        updateThemeButtons('set-display-theme', state.display_theme);
    }

    function attachBridge(bridge) {
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

        document.querySelectorAll('[data-action="set-display-theme"]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const theme = btn.getAttribute('data-theme');
                bridge.setDisplayTheme(theme);
                updateThemeButtons('set-display-theme', theme);
                showToast(`Tema del display: ${theme}`);
            });
        });

        document.querySelectorAll('[data-action="set-operator-theme"]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const theme = btn.getAttribute('data-theme');
                bridge.setOperatorTheme(theme);
                document.body.classList.remove('theme-dark', 'theme-light');
                document.body.classList.add(`theme-${theme}`);
                updateThemeButtons('set-operator-theme', theme);
                showToast(`Tema del operador: ${theme}`);
            });
        });

        const actionMap = {
            'start-pause': () => bridge.startPause(),
            'reset-time': () => bridge.resetTime(),
            'next-period': () => bridge.nextPeriod(),
            'start-countdown': () => bridge.startPregame(),
            'set-countdown': () => {
                const value = document.getElementById('countdown-input')?.value ?? '';
                bridge.setPregameCountdown(value, (success) => {
                    if (!success) {
                        showToast('Formato de tiempo inválido. Usa MM:SS', 'error');
                    } else {
                        showToast('Countdown actualizado');
                    }
                });
            },
        };

        document.querySelectorAll('[data-action="start-pause"], [data-action="reset-time"], [data-action="next-period"], [data-action="start-countdown"], [data-action="set-countdown"]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const action = btn.getAttribute('data-action');
                const handler = actionMap[action];
                if (handler) {
                    handler();
                }
            });
        });

        document.querySelectorAll('[data-action="score-local"]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const delta = parseIntOr(btn.getAttribute('data-value'), 0);
                bridge.scoreLocal(delta);
            });
        });

        document.querySelectorAll('[data-action="score-visit"]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const delta = parseIntOr(btn.getAttribute('data-value'), 0);
                bridge.scoreVisit(delta);
            });
        });

        document.querySelectorAll('[data-action="foul-local"]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const delta = parseIntOr(btn.getAttribute('data-value'), 0);
                bridge.foulLocal(delta);
            });
        });

        document.querySelectorAll('[data-action="foul-visit"]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const delta = parseIntOr(btn.getAttribute('data-value'), 0);
                bridge.foulVisit(delta);
            });
        });
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
