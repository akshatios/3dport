// COMPLETE JAVASCRIPT CODE A

// 1. LOADING SCREEN - Fixed with timeout
setTimeout(() => {
    const loadingScreen = document.getElementById('loadingScreen');
    if (loadingScreen) {
        loadingScreen.classList.add('hidden');
        setTimeout(() => loadingScreen.style.display = 'none', 500);
    }
}, 1800);

window.addEventListener('load', () => {
    setTimeout(() => {
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            loadingScreen.classList.add('hidden');
            setTimeout(() => loadingScreen.style.display = 'none', 500);
        }
    }, 1000);
});

// 2. PARTICLES JS
if (typeof particlesJS !== 'undefined') {
    particlesJS('particles-js', {
        particles: {
            number: { value: 80, density: { enable: true, value_area: 800 } },
            color: { value: '#00f0ff' },
            shape: { type: 'circle' },
            opacity: { value: 0.5, random: false },
            size: { value: 3, random: true },
            line_linked: {
                enable: true,
                distance: 150,
                color: '#00f0ff',
                opacity: 0.4,
                width: 1
            },
            move: {
                enable: true,
                speed: 2,
                direction: 'none',
                random: false,
                straight: false,
                out_mode: 'out',
                bounce: false
            }
        },
        interactivity: {
            detect_on: 'canvas',
            events: {
                onhover: { enable: true, mode: 'grab' },
                onclick: { enable: true, mode: 'push' },
                resize: true
            },
            modes: {
                grab: { distance: 140, line_linked: { opacity: 1 } },
                push: { particles_nb: 4 }
            }
        },
        retina_detect: true
    });
}

// 3. CUSTOM CURSOR
const cursor = document.querySelector('.cursor');
const cursorDot = document.querySelector('.cursor-dot');
document.addEventListener('mousemove', (e) => {
    if (cursor && cursorDot) {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
        cursorDot.style.left = e.clientX + 'px';
        cursorDot.style.top = e.clientY + 'px';
    }
});

// 4. SCROLL PROGRESS BAR
window.addEventListener('scroll', () => {
    const winScroll = document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    const progressBar = document.getElementById('scrollProgress');
    if (progressBar) {
        progressBar.style.width = scrolled + '%';
    }
});

// 5. HEADER SCROLL EFFECT
const header = document.getElementById('header');
window.addEventListener('scroll', () => {
    if (header) {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }
});

// 6. MOBILE MENU TOGGLE
const menuToggle = document.getElementById('menuToggle');
const navMenu = document.getElementById('navMenu');
if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
        menuToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
    
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            menuToggle.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
}

// 7. TYPING ANIMATION
const typingText = document.getElementById('typingText');
const texts = [
    'Securing digital environments...',
    'Python programming...',
    'ChatBot development...',
    'Data analysis and visualization...',
    'Analyzing complex datasets...',
    'Building AI solutions...',
    'Creating innovative projects...'
];
let textIndex = 0;
let charIndex = 0;
let isDeleting = false;

function type() {
    if (!typingText) return;
    const currentText = texts[textIndex];
    
    if (isDeleting) {
        typingText.innerHTML = currentText.substring(0, charIndex - 1) + '<span class="typing-cursor"></span>';
        charIndex--;
    } else {
        typingText.innerHTML = currentText.substring(0, charIndex + 1) + '<span class="typing-cursor"></span>';
        charIndex++;
    }

    if (!isDeleting && charIndex === currentText.length) {
        isDeleting = true;
        setTimeout(type, 2000);
    } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        textIndex = (textIndex + 1) % texts.length;
        setTimeout(type, 500);
    } else {
        setTimeout(type, isDeleting ? 50 : 100);
    }
}
type();

// 8. ANIMATED COUNTER
function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;

    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            element.textContent = target + '+';
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// 9. INTERSECTION OBSERVER FOR ANIMATIONS
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            
            if (entry.target.classList.contains('stat-card')) {
                const counter = entry.target.querySelector('.stat-number');
                if (counter && !counter.classList.contains('animated')) {
                    counter.classList.add('animated');
                    animateCounter(counter);
                }
            }
        }
    });
}, observerOptions);

document.querySelectorAll('.fade-in, .stat-card').forEach(el => {
    observer.observe(el);
});

// 10. THEME SWITCHER
const themeButtons = document.querySelectorAll('.theme-btn');
const root = document.documentElement;
const themes = {
    cyan: { primary: '#00f0ff', secondary: '#ff00ff', accent: '#ffff00' },
    purple: { primary: '#ff00ff', secondary: '#00f0ff', accent: '#ff00aa' },
    green: { primary: '#00ff00', secondary: '#00ffff', accent: '#ffff00' }
};

themeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const theme = btn.getAttribute('data-theme');
        const colors = themes[theme];
        root.style.setProperty('--primary', colors.primary);
        root.style.setProperty('--secondary', colors.secondary);
        root.style.setProperty('--accent', colors.accent);
        root.style.setProperty('--glow-primary', `0 0 20px ${colors.primary}, 0 0 40px ${colors.primary}`);
        root.style.setProperty('--glow-secondary', `0 0 20px ${colors.secondary}, 0 0 40px ${colors.secondary}`);
        btn.style.transform = 'scale(1.3)';
        setTimeout(() => { btn.style.transform = 'scale(1)'; }, 200);
    });
});

// 11. SCROLL TO TOP BUTTON
const scrollTopBtn = document.getElementById('scrollTop');
window.addEventListener('scroll', () => {
    if (scrollTopBtn) {
        if (window.scrollY > 500) {
            scrollTopBtn.classList.add('visible');
        } else {
            scrollTopBtn.classList.remove('visible');
        }
    }
});

if (scrollTopBtn) {
    scrollTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// 12. SMOOTH SCROLLING FOR LINKS
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#' || !href.startsWith('#')) return;
        
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            const headerOffset = 80;
            const elementPosition = target.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            window.scrollTo({ top: offsetPosition, behavior: 'smooth' });
        }
    });
});

// 13. CONTACT FORM SUBMISSION WITH EMAILJS
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const submitBtn = contactForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="ri-loader-4-line"></i> Sending...';
        submitBtn.disabled = true;
        
        if (typeof emailjs === 'undefined') {
            alert('❌ EmailJS not loaded');
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            return;
        }
        
        emailjs.init('AUKPUbYlCpQv9zjQY');
        emailjs.sendForm('service_f3ld74f', 'template_csvh6gt', contactForm)
            .then(() => {
                alert('✅ Message sent successfully!');
                contactForm.reset();
            })
            .catch(err => {
                console.error('Error:', err);
                alert('❌ Error: ' + (err.text || err.message || 'Failed'));
            })
            .finally(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
    });
}

// 14. CURSOR INTERACTION EFFECTS
const interactiveElements = document.querySelectorAll('.cyber-btn, .social-icon, .project-card, .skill-item, .contact-item, .resume-item');
interactiveElements.forEach(element => {
    element.addEventListener('mouseenter', () => {
        if (cursor && cursorDot) {
            cursor.style.width = '40px';
            cursor.style.height = '40px';
            cursor.style.backgroundColor = 'rgba(0, 240, 255, 0.2)';
        }
    });
    element.addEventListener('mouseleave', () => {
        if (cursor && cursorDot) {
            cursor.style.width = '20px';
            cursor.style.height = '20px';
            cursor.style.backgroundColor = 'transparent';
        }
    });
});

// 15. PARALLAX EFFECT
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const parallaxElements = document.querySelectorAll('.hero-visual, .hologram-container');
    parallaxElements.forEach(el => {
        const speed = 0.5;
        el.style.transform = `translateY(${scrolled * speed}px)`;
    });
});

// 16. LOGO GLITCH EFFECT
const logo = document.querySelector('.logo');
if (logo) {
    let glitchInterval;
    logo.addEventListener('mouseenter', () => {
        let count = 0;
        glitchInterval = setInterval(() => {
            if (count < 5) {
                logo.style.transform = `translate(${Math.random() * 4 - 2}px, ${Math.random() * 4 - 2}px)`;
                count++;
            } else {
                logo.style.transform = 'translate(0, 0)';
                clearInterval(glitchInterval);
            }
        }, 50);
    });
}

// 17. MAGNETIC EFFECT FOR BUTTONS
const magneticElements = document.querySelectorAll('.cyber-btn, .social-icon');
magneticElements.forEach(el => {
    el.addEventListener('mousemove', (e) => {
        const rect = el.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        el.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
    });
    el.addEventListener('mouseleave', () => {
        el.style.transform = 'translate(0, 0)';
    });
});

// 18. 3D CARD ROTATION FOR PROJECTS
const projectCards = document.querySelectorAll('.project-card');
projectCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-15px)`;
    });
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
    });
});

// 19. SKILL RIPPLE EFFECT
const skillItems = document.querySelectorAll('.skill-item');
skillItems.forEach(item => {
    item.addEventListener('mouseenter', () => {
        const ripple = document.createElement('div');
        ripple.style.cssText = 'position:absolute;width:100%;height:100%;top:0;left:0;background:radial-gradient(circle,rgba(0,240,255,0.3) 0%,transparent 70%);transform:scale(0);transition:transform 0.6s ease-out;pointer-events:none;';
        item.appendChild(ripple);
        setTimeout(() => { ripple.style.transform = 'scale(2)'; }, 10);
        setTimeout(() => { ripple.remove(); }, 600);
    });
});

// 20. ANIMATED SCAN LINE
const scanLine = document.createElement('div');
scanLine.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:2px;background:linear-gradient(90deg,transparent,var(--primary),transparent);opacity:0.3;pointer-events:none;z-index:9998;animation:scanLine 4s linear infinite;';
document.body.appendChild(scanLine);

const style = document.createElement('style');
style.textContent = '@keyframes scanLine { 0% { top: 0; } 100% { top: 100%; } }';
document.head.appendChild(style);

// 21. KONAMI CODE EASTER EGG
const konamiCode = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a'];
let konamiIndex = 0;
document.addEventListener('keydown', (e) => {
    if (e.key === konamiCode[konamiIndex]) {
        konamiIndex++;
        if (konamiIndex === konamiCode.length) {
            document.body.style.animation = 'glitch 0.3s infinite';
            setTimeout(() => {
                document.body.style.animation = '';
                alert('🎮 CHEAT CODE ACTIVATED!\n⚡ Ultra Cyberpunk Mode Enabled! ⚡');
            }, 2000);
            konamiIndex = 0;
        }
    } else {
        konamiIndex = 0;
    }
});

// 22. CURSOR PARTICLE TRAIL
document.addEventListener('mousemove', (e) => {
    if (Math.random() > 0.95) {
        const particle = document.createElement('div');
        particle.style.cssText = `position:fixed;left:${e.clientX}px;top:${e.clientY}px;width:4px;height:4px;background:var(--primary);border-radius:50%;pointer-events:none;z-index:9999;box-shadow:var(--glow-primary);animation:particleFade 1s ease-out forwards;`;
        document.body.appendChild(particle);
        setTimeout(() => { particle.remove(); }, 1000);
    }
});

const particleStyle = document.createElement('style');
particleStyle.textContent = `@keyframes particleFade { 0% { opacity:1; transform:translate(0,0) scale(1); } 100% { opacity:0; transform:translate(${Math.random()*100-50}px,${Math.random()*100-50}px) scale(0); } }`;
document.head.appendChild(particleStyle);

// 23. NOISE TEXTURE OVERLAY
const noiseCanvas = document.createElement('canvas');
noiseCanvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9997;opacity:0.03;mix-blend-mode:overlay;';
document.body.appendChild(noiseCanvas);
const ctx = noiseCanvas.getContext('2d');
noiseCanvas.width = window.innerWidth;
noiseCanvas.height = window.innerHeight;

function drawNoise() {
    const imageData = ctx.createImageData(noiseCanvas.width, noiseCanvas.height);
    const buffer = new Uint32Array(imageData.data.buffer);
    for (let i = 0; i < buffer.length; i++) {
        buffer[i] = Math.random() > 0.5 ? 0xffffffff : 0xff000000;
    }
    ctx.putImageData(imageData, 0, 0);
}
setInterval(drawNoise, 100);

window.addEventListener('resize', () => {
    noiseCanvas.width = window.innerWidth;
    noiseCanvas.height = window.innerHeight;
});

// 24. GRID ANIMATION
const cyberGrid = document.querySelector('.cyber-grid');
let gridHue = 180;
function animateGrid() {
    gridHue = (gridHue + 0.5) % 360;
    if (cyberGrid) {
        cyberGrid.style.backgroundImage = `
            linear-gradient(90deg, transparent 99%, hsla(${gridHue}, 100%, 50%, 0.1) 100%),
            linear-gradient(0deg, transparent 99%, hsla(${gridHue}, 100%, 50%, 0.1) 100%)
        `;
    }
    requestAnimationFrame(animateGrid);
}
animateGrid();

// 25. CONSOLE MESSAGES
console.log('%c🚀 SYSTEM INITIALIZED 🚀', 'color:#00f0ff;font-size:20px;font-weight:bold;text-shadow:0 0 10px #00f0ff;');
console.log('%c⚡ Ultra Cyberpunk Mode Active ⚡', 'color:#ff00ff;font-size:16px;font-weight:bold;');
console.log('%c💻 Developed by Akshat Jain 💻', 'color:#ffff00;font-size:14px;');
console.log('%c🎮 Try the Konami Code: ↑↑↓↓←→←→BA', 'color:#00ff00;font-size:12px;');

// Initialize all animations on page load
window.addEventListener('load', () => {
    document.querySelectorAll('.fade-in').forEach((el, index) => {
        setTimeout(() => {
            el.classList.add('visible');
        }, index * 100);
    });
});

// ===== CHATBOT — PRODUCTION v2 =====
(function () {
    const CHATBOT_API  = 'http://localhost:8000/chat';
    const WA_FALLBACK  = 'https://wa.me/918103214221?text=Hello%20Akshat%2C%20I%20found%20your%20portfolio!';
    const STORAGE_KEY  = 'akshat_chat_history';
    const SESSION_KEY  = 'akshat_chat_session';
    const MAX_CHARS    = 500;
    const RETRY_DELAYS = [1000, 2000, 4000]; // exponential backoff ms

    // ── Elements ──────────────────────────────────────────────────────────────
    const toggle   = document.getElementById('chatbotToggle');
    const win      = document.getElementById('chatbotWindow');
    const openIcon = document.getElementById('chatbotOpenIcon');
    const closeIcon= document.getElementById('chatbotCloseIcon');
    const msgBox   = document.getElementById('chatbotMessages');
    const input    = document.getElementById('chatbotInput');
    const sendBtn  = document.getElementById('chatbotSend');

    if (!toggle || !win || !msgBox || !input || !sendBtn) return;

    // ── Session ID (persisted) ────────────────────────────────────────────────
    let sessionId = sessionStorage.getItem(SESSION_KEY);
    if (!sessionId) {
        sessionId = 'sess_' + Math.random().toString(36).slice(2, 10);
        sessionStorage.setItem(SESSION_KEY, sessionId);
    }

    // ── Auto-scroll lock ──────────────────────────────────────────────────────
    let userScrolled = false;
    msgBox.addEventListener('scroll', () => {
        const atBottom = msgBox.scrollHeight - msgBox.scrollTop - msgBox.clientHeight < 40;
        userScrolled = !atBottom;
    });
    function scrollToBottom() {
        if (!userScrolled) msgBox.scrollTop = msgBox.scrollHeight;
    }

    // ── Timestamp helper ──────────────────────────────────────────────────────
    function timeLabel() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // ── Markdown renderer (bold, bullets, code, links) ──────────────────────
    function renderMarkdown(text) {
        // 1. Extract [label](url) markdown links before escaping
        const links = [];
        text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, (_, label, url) => {
            links.push({ label, url });
            return `%%LINK${links.length - 1}%%`;
        });
        // 2. HTML escape
        text = text
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            // 3. Inline formatting
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/`([^`]+)`/g, '<code style="background:rgba(0,240,255,0.1);padding:1px 5px;border-radius:4px;font-size:0.85em">$1</code>')
            .replace(/^• (.+)$/gm, '<span style="display:block;padding-left:0.5rem">• $1</span>')
            .replace(/^→ (.+)$/gm, '<span style="display:block;padding-left:0.8rem;color:var(--primary)">→ $1</span>')
            .replace(/^🔹 (.+)$/gm, '<span style="display:block;padding-left:0.5rem">🔹 $1</span>')
            // 4. Bare URLs
            .replace(/(https?:\/\/[^\s<>"]+)/g, (url) => {
                const label = url.replace(/^https?:\/\//, '').replace(/\.git$/, '');
                const short = label.length > 35 ? label.slice(0, 32) + '…' : label;
                return `<a href="${url}" target="_blank" rel="noopener" style="color:var(--primary);text-decoration:underline">${short}</a>`;
            })
            .replace(/\n/g, '<br>');
        // 5. Restore markdown links
        links.forEach(({ label, url }, i) => {
            text = text.replace(`%%LINK${i}%%`, `<a href="${url}" target="_blank" rel="noopener" style="color:var(--primary);text-decoration:underline">${label}</a>`);
        });
        return text;
    }

    // ── Append message to UI ──────────────────────────────────────────────────
    function appendMessage(html, role, save = true) {
        const wrap = document.createElement('div');
        wrap.className = `chat-msg ${role}`;
        wrap.innerHTML = `
            <div class="chat-bubble">${html}</div>
            <div class="chat-time">${timeLabel()}</div>`;
        msgBox.appendChild(wrap);
        scrollToBottom();
        if (save) saveHistory(html, role);
    }

    // ── Typing indicator ──────────────────────────────────────────────────────
    function showTyping() {
        const el = document.createElement('div');
        el.className = 'chat-msg bot'; el.id = 'chatTyping';
        el.innerHTML = '<div class="chat-typing"><span></span><span></span><span></span></div>';
        msgBox.appendChild(el);
        scrollToBottom();
    }
    function removeTyping() {
        document.getElementById('chatTyping')?.remove();
    }

    // ── localStorage history ──────────────────────────────────────────────────
    function saveHistory(html, role) {
        try {
            const hist = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            hist.push({ html, role, time: timeLabel() });
            if (hist.length > 40) hist.splice(0, hist.length - 40);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(hist));
        } catch {}
    }

    function loadHistory() {
        try {
            const hist = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            if (hist.length === 0) return false;
            // Only replay last 10 messages to avoid stale/bloated history
            hist.slice(-10).forEach(({ html, role }) => appendMessage(html, role, false));
            return true;
        } catch { return false; }
    }

    function clearHistory() {
        localStorage.removeItem(STORAGE_KEY);
        sessionStorage.removeItem(SESSION_KEY);
        msgBox.innerHTML = '';
        sessionId = 'sess_' + Math.random().toString(36).slice(2, 10);
        sessionStorage.setItem(SESSION_KEY, sessionId);
        userScrolled = false;
        appendMessage('🗑️ Chat cleared. How can I help you?', 'bot', false);
    }

    // ── Fetch with retry ──────────────────────────────────────────────────────
    async function fetchWithRetry(message, attempt = 0) {
        try {
            const res = await fetch(CHATBOT_API, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, session_id: sessionId }),
                signal: AbortSignal.timeout(8000),
            });
            if (res.status === 429) throw new Error('rate_limit');
            if (!res.ok) throw new Error('api_error');
            return await res.json();
        } catch (err) {
            if (err.message === 'rate_limit') throw err;
            if (attempt < RETRY_DELAYS.length) {
                await new Promise(r => setTimeout(r, RETRY_DELAYS[attempt]));
                return fetchWithRetry(message, attempt + 1);
            }
            throw err;
        }
    }

    // ── Send message ──────────────────────────────────────────────────────────
    async function sendMessage(message) {
        message = message.trim();
        if (!message || sendBtn.disabled) return;

        if (message.length > MAX_CHARS) {
            appendMessage(`⚠️ Message too long (max ${MAX_CHARS} chars).`, 'bot');
            return;
        }

        appendMessage(message, 'user');
        input.value = '';
        updateCharCount();
        sendBtn.disabled = true;
        userScrolled = false;
        showTyping();

        try {
            const data = await fetchWithRetry(message);
            removeTyping();

            if (data.type === 'whatsapp') {
                const html = `${renderMarkdown(data.message)}<br><br>
                    <a class="whatsapp-btn" href="${data.whatsapp_url}" target="_blank" rel="noopener">
                        <i class="ri-whatsapp-fill"></i> Open WhatsApp
                    </a>`;
                appendMessage(html, 'bot');
                setTimeout(() => window.open(data.whatsapp_url, '_blank'), 900);
            } else {
                appendMessage(renderMarkdown(data.message), 'bot');
            }
        } catch (err) {
            removeTyping();
            if (err.message === 'rate_limit') {
                appendMessage('⏳ Too many messages. Please wait a moment and try again.', 'bot');
            } else {
                appendMessage(
                    '⚠️ <strong>Backend is offline.</strong><br>' +
                    'Start it: <code>cd chatbot &amp;&amp; start.bat</code><br><br>' +
                    '📧 <strong>Email:</strong> akshatjain9989@gmail.com<br>' +
                    `<a class="whatsapp-btn" href="${WA_FALLBACK}" target="_blank" rel="noopener">` +
                    '<i class="ri-whatsapp-fill"></i> WhatsApp Akshat</a>',
                    'bot'
                );
            }
        } finally {
            sendBtn.disabled = false;
            input.focus();
        }
    }

    // ── Character counter ─────────────────────────────────────────────────────
    function updateCharCount() {
        const len = input.value.length;
        let counter = document.getElementById('chatCharCount');
        if (!counter) {
            counter = document.createElement('div');
            counter.id = 'chatCharCount';
            counter.style.cssText = 'font-size:0.65rem;color:rgba(255,255,255,0.3);text-align:right;padding:0 1rem 0.3rem;';
            win.querySelector('.chatbot-input-row').before(counter);
        }
        counter.textContent = len > 0 ? `${len}/${MAX_CHARS}` : '';
        counter.style.color = len > MAX_CHARS * 0.9 ? 'var(--secondary)' : 'rgba(255,255,255,0.3)';
    }

    // ── Toggle open/close ─────────────────────────────────────────────────────
    function toggleChat() {
        const isOpen = win.classList.toggle('open');
        openIcon.style.display  = isOpen ? 'none'  : 'block';
        closeIcon.style.display = isOpen ? 'block' : 'none';
        if (isOpen) { scrollToBottom(); setTimeout(() => input.focus(), 300); }
    }

    // ── Init ──────────────────────────────────────────────────────────────────
    function init() {
        const hadHistory = loadHistory();
        if (!hadHistory) {
            appendMessage(
                '👋 Hi! I\'m Akshat\'s AI assistant.<br><br>' +
                'Ask me about his <strong>skills</strong>, <strong>projects</strong>, ' +
                '<strong>experience</strong>, or type <strong>\'connect to whatsapp\'</strong> to reach him!',
                'bot', false
            );
        }

        // Clear button in header
        const clearBtn = document.createElement('button');
        clearBtn.title = 'Clear chat';
        clearBtn.style.cssText = 'background:none;border:none;color:rgba(255,255,255,0.4);cursor:pointer;font-size:1rem;padding:0;';
        clearBtn.innerHTML = '<i class="ri-delete-bin-line"></i>';
        clearBtn.addEventListener('click', clearHistory);
        win.querySelector('.chatbot-header').appendChild(clearBtn);
    }

    // ── Event listeners ───────────────────────────────────────────────────────
    toggle.addEventListener('click', toggleChat);
    sendBtn.addEventListener('click', () => sendMessage(input.value));
    input.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input.value); } });
    input.addEventListener('input', updateCharCount);

    // Mobile: prevent page scroll when typing in chatbot
    input.addEventListener('focus', () => { if (window.innerWidth < 480) win.scrollIntoView({ behavior: 'smooth' }); });

    document.querySelectorAll('.chat-suggestion').forEach(btn => {
        btn.addEventListener('click', () => { if (win.classList.contains('open')) sendMessage(btn.dataset.msg); else { toggleChat(); setTimeout(() => sendMessage(btn.dataset.msg), 400); } });
    });

    init();
})();
