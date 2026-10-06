/**
 * Coach AI — embed widget for vetriitsystems.com and other VIS sites.
 *
 * Usage (before </body>):
 *   <script src="https://vetri-chatbot-ui.onrender.com/coach-ai-widget.js" defer></script>
 *
 * Optional:
 *   data-chat-url="https://vetri-chatbot-ui.onrender.com"
 *   data-title="Coach AI"
 */
(function initCoachAiWidget() {
  const EMBED_PAUSED = false
  if (EMBED_PAUSED) {
    return
  }

  if (document.getElementById('coach-ai-widget-root')) {
    return
  }

  const script = document.currentScript
  const chatBase = (script && script.getAttribute('data-chat-url')) || 'https://vetri-chatbot-ui.onrender.com'
  const chatTitle = (script && script.getAttribute('data-title')) || 'Coach AI'
  const chatUrl = `${chatBase.replace(/\/$/, '')}/?embed=1&open=1`

  const root = document.createElement('div')
  root.id = 'coach-ai-widget-root'
  root.setAttribute('aria-live', 'polite')

  const style = document.createElement('style')
  style.textContent = `
    #coach-ai-widget-root {
      --vis-navy: #0c1e3d;
      --vis-green: #4ade80;
      --vis-green-text: #0c1e3d;
      font-family: Inter, 'Segoe UI', system-ui, sans-serif;
    }
    #coach-ai-widget-root .coach-ai-launcher {
      position: fixed;
      right: 20px;
      bottom: 20px;
      z-index: 2147483000;
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 60px;
      height: 60px;
      padding: 0 18px 0 16px;
      border: 0;
      border-radius: 999px;
      background: var(--vis-green);
      color: var(--vis-green-text);
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 20px rgba(74, 222, 128, 0.45);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    #coach-ai-widget-root .coach-ai-launcher:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 28px rgba(74, 222, 128, 0.55);
    }
    #coach-ai-widget-root .coach-ai-launcher:focus-visible {
      outline: 3px solid var(--vis-navy);
      outline-offset: 3px;
    }
    #coach-ai-widget-root .coach-ai-launcher svg {
      width: 22px;
      height: 22px;
      flex-shrink: 0;
    }
    #coach-ai-widget-root .coach-ai-panel {
      position: fixed;
      right: 16px;
      bottom: 16px;
      z-index: 2147483001;
      width: min(400px, calc(100vw - 24px));
      height: min(640px, calc(100svh - 80px));
      border: 0;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 16px 48px rgba(12, 30, 61, 0.28);
      background: transparent;
      display: none;
    }
    #coach-ai-widget-root.coach-ai-open .coach-ai-panel {
      display: block;
    }
    #coach-ai-widget-root.coach-ai-open .coach-ai-launcher {
      display: none;
    }
    #coach-ai-widget-root .coach-ai-panel iframe {
      width: 100%;
      height: 100%;
      border: 0;
      background: transparent;
    }
    @media (max-width: 480px) {
      #coach-ai-widget-root .coach-ai-launcher {
        right: 16px;
        bottom: 16px;
        height: 56px;
        padding: 0 16px 0 14px;
      }
      #coach-ai-widget-root .coach-ai-panel {
        right: 0;
        bottom: 0;
        width: 100%;
        height: min(600px, 92svh);
        border-radius: 16px 16px 0 0;
      }
    }
  `
  document.head.appendChild(style)

  const launcher = document.createElement('button')
  launcher.type = 'button'
  launcher.className = 'coach-ai-launcher'
  launcher.setAttribute('aria-label', `Open ${chatTitle}`)
  launcher.setAttribute('aria-expanded', 'false')
  launcher.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v8A2.5 2.5 0 0 1 17.5 16H11l-4.2 3.15a.75.75 0 0 1-1.15-.64V16H6.5A2.5 2.5 0 0 1 4 13.5v-8Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
    </svg>
    <span>${chatTitle}</span>
  `

  const panel = document.createElement('div')
  panel.className = 'coach-ai-panel'
  panel.setAttribute('role', 'dialog')
  panel.setAttribute('aria-label', chatTitle)
  panel.hidden = true

  let iframeLoaded = false

  function openPanel() {
    if (!iframeLoaded) {
      const iframe = document.createElement('iframe')
      iframe.src = chatUrl
      iframe.title = `${chatTitle} — Vetri IT Systems`
      iframe.loading = 'lazy'
      iframe.allow = 'microphone'
      panel.appendChild(iframe)
      iframeLoaded = true
    }
    root.classList.add('coach-ai-open')
    panel.hidden = false
    launcher.setAttribute('aria-expanded', 'true')
  }

  function closePanel() {
    root.classList.remove('coach-ai-open')
    panel.hidden = true
    launcher.setAttribute('aria-expanded', 'false')
    launcher.focus()
  }

  launcher.addEventListener('click', openPanel)

  window.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'coach-ai-close') {
      closePanel()
    }
  })

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && root.classList.contains('coach-ai-open')) {
      closePanel()
    }
  })

  root.appendChild(launcher)
  root.appendChild(panel)
  document.body.appendChild(root)
})()
