// State
        let fullData = null;
        let appData = null;
        let activeSteps = []; 
        let currentStep = 0;
        let isAnimating = false;

        // Init
        async function loadDataAndInit() {
            try {
                // He actualizado el mock también para que funcione el preview en Canvas con tus nuevos pasos
                const mockConfig = {
                    "common_config": {
                        "boot_sequence": {
                            "loading_text": "INICIALIZANDO NEURAL LINK...",
                            "logs": ["CONECTANDO A RED UNSC...", "BYPASS DE SEGURIDAD...", "VERIFICANDO PERMISOS...", "SISTEMA LISTO"]
                        }
                    },
                    "languages": {
                        "es": {
                            "ui_labels": {
                                "footer_text": "UNSC SECURE CHANNEL", "phase_1": "FASE 1 - PREPARACIÓN", "phase_2": "FASE 2 - INSTALACIÓN",
                                "tactical_order_header": "ORDEN TÁCTICA", "key_label": "CLAVE DE ACTIVACIÓN",
                                "skip_download_btn": "SALTAR DESCARGA", "download_btn": "DESCARGAR MOD", "continue_btn": "CONTINUAR",
                                "finish_btn": "FINALIZAR", "next_btn_default": "SIGUIENTE", "back_btn": "ATRÁS",
                                "already_installed_btn": "YA ACABÉ DE INSTALAR",
                                "popup_confirm_title": "VERIFICACIÓN DE RUTA",
                                "popup_confirm_desc": "¿Confirmas que instalaste el juego en otra carpeta (ej. C:\\Games\\Halo) y NO en Program Files?",
                                "popup_confirm_btn": "SÍ, CONFIRMO", "popup_cancel_btn": "NO, REVISAR"
                            },
                            "splash_screen": {
                                "subtitle": "PROYECTO SPARTAN", "title": "HALO CE VR", "description": "Protocolo de instalación automatizado para inmersión neuronal en entorno de combate.",
                                "features": ["Soporte de seguimiento 6DOF", "Movimiento de Armas en VR", "Escalado Inmersivo"], "btn_start": "INICIAR SECUENCIA"
                            },
                            "installation_steps": [
                                {
                                    "phase": 1, "title": "AUTENTICACIÓN", "desc": "Validación de software para la instalación base.", "icon": "ph-fingerprint",
                                    "instruction": "Necesitarás esta licencia para instalar Halo: CE. Cópiala haciendo clic en ella antes de continuar.",
                                    "isKey": true, "key": "HVR0-CE24-UNSC-7777"
                                },
                                {
                                    "phase": 1, "title": "INSTALACIÓN", "desc": "Despliegue de archivos en disco local.", "icon": "ph-hard-drives",
                                    "instruction": "Instala el juego en cualquier carpeta MENOS en Program Files (ejemplo: C:/Game/Halo)",
                                    "isInstallStep": true
                                },
                                {
                                    "phase": 2, "title": "COMPLETADO", "desc": "Protocolos finalizados correctamente. Estás listo para el despliegue.", "icon": "ph-check-circle",
                                    "isGameEnd": true
                                }
                            ]
                        }
                    }
                };

                const response = await fetch('config.json');
                if(!response.ok) throw new Error("config.json local no encontrado");
                fullData = await response.json();
            } catch (error) {
                console.warn("Cargando datos de respaldo (Mock) para que funcione la vista previa.");
                fullData = error.message.includes("Mock") ? null : mockConfig;
            }
        }

        // Lang
        function selectLanguage(lang) {
            if (!fullData) return;
            const selectedLang = fullData.languages[lang] ? lang : 'es';
            appData = { ...fullData.common_config, ...fullData.languages[selectedLang] };
            
            const langScreen = document.getElementById('language-screen');
            langScreen.style.opacity = '0';
            langScreen.style.pointerEvents = 'none';

            setTimeout(() => {
                langScreen.remove();
                document.getElementById('boot-screen').classList.remove('hidden');
                document.getElementById('boot-screen').style.opacity = '1';
                initBootSequence();
            }, 700);
        }

        // Boot
        function initBootSequence() {
            const logContainer = document.getElementById('boot-logs');
            const loadingText = document.getElementById('boot-loading-text');
            if(loadingText && appData.boot_sequence) loadingText.innerText = appData.boot_sequence.loading_text;

            const logs = appData.boot_sequence ? appData.boot_sequence.logs : [];
            let delay = 0;

            if(logs.length > 0) {
                logs.forEach((log, index) => {
                    setTimeout(() => {
                        const p = document.createElement('div');
                        p.className = 'log-line font-tech';
                        p.innerText = log;
                        logContainer.appendChild(p);
                        if(index === logs.length - 1) setTimeout(finishBoot, 1000);
                    }, delay);
                    delay += 250; 
                });
            } else {
                finishBoot();
            }
        }

        function finishBoot() {
            const bootScreen = document.getElementById('boot-screen');
            const introScreen = document.getElementById('intro-screen');
            
            bootScreen.style.opacity = '0';
            introScreen.classList.remove('hidden');
            introScreen.style.opacity = '1';

            setTimeout(() => {
                bootScreen.remove();
                startAutoSequence();
            }, 800);
        }

        // AutoSeq
        function startAutoSequence() {
            const introVisual = document.getElementById('intro-visual');
            const introIcon = document.getElementById('intro-icon');
            const introScreen = document.getElementById('intro-screen');
            const videoContainer = document.getElementById('video-bg-container');
            const video = document.getElementById('bg-video');

            introVisual.classList.add('reactor-mode');
            introIcon.style.opacity = '1';
            introIcon.style.color = 'white';
            introIcon.classList.add('animate-pulse');

            setTimeout(() => {
                video.muted = false;
                video.classList.add('active-mode');
                videoContainer.classList.remove('opacity-0');
                videoContainer.style.opacity = "1"; 
                
                const playPromise = video.play();
                if (playPromise !== undefined) playPromise.catch(() => {});

                const mainInterface = document.getElementById('main-interface');
                mainInterface.classList.remove('opacity-0', 'pointer-events-none');
                mainInterface.style.opacity = '1';
                mainInterface.style.pointerEvents = 'all';
                document.getElementById('footer-text').innerHTML = appData.ui_labels.footer_text;
                showSplashScreen();

                introScreen.style.transition = 'opacity 1.5s ease-in-out';
                introScreen.style.opacity = '0';
                introScreen.style.pointerEvents = 'none';

                setTimeout(() => introScreen.classList.add('hidden'), 1500);
            }, 1500);
        }

        // Transitions
        async function transitionContent(updateFunction) {
            const container = document.getElementById('content-container');
            const visual = document.getElementById('visual-icon-container');
            
            Array.from(container.children).forEach((child) => {
                child.style.transition = 'all 0.3s ease';
                child.style.opacity = '0';
                child.style.transform = 'translateX(-20px)';
            });

            visual.style.opacity = '0';
            visual.style.transform = 'scale(0.9)';

            await new Promise(r => setTimeout(r, 300));
            updateFunction();
            visual.style.opacity = '1';
            visual.style.transform = 'scale(1)';
        }

        // Utils - Copiado al Portapapeles
        function copyKeySegment(text, btnElement) {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            textArea.style.left = "-999999px";
            textArea.style.top = "-999999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();

            try {
                document.execCommand('copy');
                btnElement.classList.add('copied-state');
                setTimeout(() => btnElement.classList.remove('copied-state'), 1500);
            } catch (err) {
                console.error('No se pudo copiar el texto', err);
            }

            document.body.removeChild(textArea);
        }

        // Modal de Confirmación
        function showInstallConfirmPopup() {
            const modal = document.getElementById('install-modal');
            const content = document.getElementById('install-modal-content');
            
            document.getElementById('modal-title').innerText = appData.ui_labels.popup_confirm_title;
            document.getElementById('modal-desc').innerText = appData.ui_labels.popup_confirm_desc;
            document.getElementById('modal-cancel').querySelector('span').innerText = appData.ui_labels.popup_cancel_btn;
            document.getElementById('modal-confirm-text').innerText = appData.ui_labels.popup_confirm_btn;

            modal.classList.remove('hidden');
            modal.style.pointerEvents = 'all';
            
            // Timeout ligero para que la animación CSS actúe tras quitar el display:none
            setTimeout(() => {
                modal.classList.remove('opacity-0');
                modal.classList.add('opacity-100');
                content.classList.remove('scale-95');
                content.classList.add('scale-100');
            }, 10);
        }

        function cancelInstallPath() {
            const modal = document.getElementById('install-modal');
            const content = document.getElementById('install-modal-content');
            
            modal.classList.remove('opacity-100');
            modal.classList.add('opacity-0');
            content.classList.remove('scale-100');
            content.classList.add('scale-95');
            modal.style.pointerEvents = 'none';
            
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 300);
        }

        function confirmInstallPath() {
            cancelInstallPath();
            changeStep(1);
        }

        // Screens
        function showSplashScreen() {
            const container = document.getElementById('content-container');
            const visual = document.getElementById('visual-icon-container');
            const data = appData.splash_screen;

            document.getElementById('nav-controls').classList.add('opacity-0', 'pointer-events-none');
            document.getElementById('progress-wrapper').classList.add('opacity-0');

            visual.innerHTML = `<i class="ph ph-planet visual-icon" style="color: white; filter: drop-shadow(0 0 30px white);"></i>`;

            let featuresHtml = '<div class="features-grid mt-4 anim-slide-in delay-2">';
            if(data.features) {
                data.features.forEach(feat => {
                    featuresHtml += `<div class="feature-card"><i class="ph ph-check text-white/50"></i><span>${feat}</span></div>`;
                });
            }
            featuresHtml += '</div>';

            container.innerHTML = `
                <div class="splash-container py-4">
                    <h2 class="text-white/60 font-tech text-sm tracking-[0.4em] mb-2 anim-slide-in delay-0 uppercase">${data.subtitle}</h2>
                    <h1 class="step-title mb-4 anim-slide-in delay-1">${data.title}</h1>
                    <div class="h-[2px] w-24 bg-white mb-4 anim-slide-in delay-2 shadow-[0_0_15px_white]"></div>
                    <p class="text-zinc-300 text-sm md:text-base font-light leading-relaxed max-w-lg mb-4 anim-slide-in delay-3">${data.description}</p>
                    ${featuresHtml}
                    <div class="mt-8">
                        <button onclick="startInstallation()" class="btn-action anim-slide-in delay-4 group"><span>${data.btn_start}</span></button>
                    </div>
                </div>
            `;
        }

        function startInstallation() {
            activeSteps = appData.installation_steps;
            currentStep = 0;
            
            const nav = document.getElementById('nav-controls');
            nav.classList.remove('opacity-0', 'pointer-events-none');
            nav.classList.add('opacity-100', 'anim-fade-up');
            document.getElementById('progress-wrapper').classList.remove('opacity-0');
            document.getElementById('btn-back-text').innerText = appData.ui_labels.back_btn;

            changeStep(0, true);
        }

        async function changeStep(direction, isInit = false) {
            if (isAnimating && !isInit) return;
            let nextIndex = isInit ? 0 : currentStep + direction;

            if (nextIndex < 0) {
                isAnimating = true;
                await transitionContent(() => showSplashScreen());
                isAnimating = false;
                return;
            }

            if (nextIndex >= activeSteps.length) return;

            isAnimating = true;
            const updateAction = () => { currentStep = nextIndex; renderStep(); };

            if(isInit) transitionContent(updateAction);
            else await transitionContent(updateAction);
            
            isAnimating = false;
        }

        function renderStep() {
            const step = activeSteps[currentStep];
            const contentDiv = document.getElementById('content-container');
            const visualIconContainer = document.getElementById('visual-icon-container');
            const btnNext = document.getElementById('btn-next');
            const btnNextText = document.getElementById('btn-next-text');
            const phaseLabel = document.getElementById('phase-label');
            const navControls = document.getElementById('nav-controls');

            const existingSkip = document.getElementById('btn-skip-dl');
            if(existingSkip) existingSkip.remove();

            const totalStepsPhase1 = activeSteps.filter(s => s.phase === 1).length;
            const totalStepsPhase2 = activeSteps.filter(s => s.phase === 2).length;
            let width1 = '0%', width2 = '0%';

            if (step.phase === 1) {
                const currentInPhase = activeSteps.slice(0, currentStep + 1).filter(s => s.phase === 1).length;
                width1 = `${(currentInPhase / totalStepsPhase1) * 100}%`;
                phaseLabel.innerText = appData.ui_labels.phase_1;
            } else {
                width1 = '100%';
                const currentInPhase = activeSteps.slice(0, currentStep + 1).filter(s => s.phase === 2).length;
                width2 = `${(currentInPhase / totalStepsPhase2) * 100}%`;
                phaseLabel.innerText = appData.ui_labels.phase_2;
            }

            document.getElementById('prog-bar-1').style.width = width1;
            document.getElementById('prog-bar-2').style.width = width2;

            let html = `<div class="anim-slide-in delay-0"><h1 class="step-title">${step.title}</h1></div>
                        <div class="anim-slide-in delay-1"><p class="step-desc">${step.desc}</p></div>`;

            if (step.instruction) {
                html += `<div class="glass-card mt-4 anim-slide-in delay-2 group">
                            <div class="flex items-center gap-2 mb-2"><i class="ph ph-caret-right text-white"></i><span class="text-xs font-tech uppercase tracking-widest text-white/60">${appData.ui_labels.tactical_order_header}</span></div>
                            <div class="dotted-line"></div>
                            <div class="flex items-start gap-4 mt-3"><div class="text-white text-lg font-light leading-relaxed">${step.instruction}</div></div>
                        </div>`;
            }

            if (step.isKey) {
                const keyParts = step.key.split('-');
                let keyHtml = '<div class="flex flex-wrap gap-2 md:gap-3 justify-center items-center mt-4">';
                
                keyParts.forEach((part, idx) => {
                    keyHtml += `
                        <button onclick="copyKeySegment('${part}', this)" class="key-segment group">
                            <span class="font-mono text-xl font-bold tracking-widest base-text">${part}</span>
                            <div class="hover-overlay">
                                <i class="ph ph-copy text-lg"></i> <span class="font-tech tracking-widest text-xs mt-0.5">COPIAR</span>
                            </div>
                            <div class="copied-overlay">
                                <i class="ph ph-check text-lg"></i> <span class="font-tech tracking-widest text-xs mt-0.5">COPIADO</span>
                            </div>
                        </button>${idx < keyParts.length - 1 ? '<span class="text-white/30 font-bold">-</span>' : ''}`;
                });
                keyHtml += '</div>';

                html += `<div class="anim-slide-in delay-3">
                            <div class="glass-card flex flex-col justify-center items-center py-6 bg-white/5">
                                <span class="text-xs text-white/50 font-tech mb-4 tracking-[0.2em] uppercase">${appData.ui_labels.key_label}</span>
                                ${keyHtml}
                            </div>
                        </div>`;
            }

            contentDiv.innerHTML = html;
            visualIconContainer.innerHTML = `<i class="ph ${step.icon} visual-icon" style="color: white;"></i>`;

            btnNext.onclick = null;
            
            if (step.showSkip === true) {
                const skipBtn = document.createElement('button');
                skipBtn.id = 'btn-skip-dl';
                skipBtn.className = 'btn-ghost anim-fade-up';
                skipBtn.innerHTML = `<span>${appData.ui_labels.skip_download_btn}</span>`;
                skipBtn.onclick = () => changeStep(1);
                navControls.insertBefore(skipBtn, btnNext);
            }

            // Aquí inyectamos la lógica del botón y el modal en base al paso
            if (step.isDownload) {
                btnNextText.innerText = appData.ui_labels.download_btn;
                btnNext.onclick = () => {
                    window.open(step.url, '_blank');
                    btnNextText.innerText = appData.ui_labels.continue_btn;
                    const skip = document.getElementById('btn-skip-dl');
                    if(skip) { skip.style.opacity = '0'; setTimeout(()=>skip.remove(), 300); }
                    btnNext.onclick = () => changeStep(1);
                };
            } else if (step.isGameEnd) {
                btnNextText.innerText = appData.ui_labels.finish_btn;
                btnNext.onclick = () => window.close();
            } else if (step.isInstallStep) {
                btnNextText.innerText = appData.ui_labels.already_installed_btn;
                btnNext.onclick = () => showInstallConfirmPopup();
            } else {
                btnNextText.innerText = appData.ui_labels.next_btn_default;
                btnNext.onclick = () => changeStep(1);
            }
        }

        window.addEventListener('load', loadDataAndInit);