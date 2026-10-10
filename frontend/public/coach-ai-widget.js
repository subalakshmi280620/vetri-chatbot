/**
 * Coach AI — embed widget for vetriitsystems.com and other VIS sites.
 *
 * Usage (before </body>):
 *   <script src="https://vetri-chatbot-ui.onrender.com/coach-ai-widget.js" defer></script>
 *
 * Optional:
 *   data-chat-url="https://vetri-chatbot-ui.onrender.com"
 *   data-title="Coach AI"
 *   data-icon-url="https://vetri-chatbot-ui.onrender.com/coach-ai-embed-icon.png"
 */
(function initCoachAiWidget() {
  const EMBED_PAUSED = true
  if (EMBED_PAUSED) {
    return
  }

  if (document.getElementById('coach-ai-widget-root')) {
    return
  }

  const script = document.currentScript
  const scriptOrigin = (() => {
    if (!script || !script.src) {
      return window.location.origin
    }
    try {
      return new URL(script.src, window.location.href).origin
    } catch {
      return window.location.origin
    }
  })()
  const chatBase = (script && script.getAttribute('data-chat-url')) || scriptOrigin
  const chatTitle = (script && script.getAttribute('data-title')) || 'Coach AI'
  const chatRoot = chatBase.replace(/\/$/, '')
  const chatUrl = `${chatRoot}/?embed=1&open=1`
  const iconUrl = (script && script.getAttribute('data-icon-url'))
    || `${scriptOrigin}/coach-ai-embed-icon.png`

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
      display: block;
      width: 84px;
      height: 84px;
      padding: 0;
      border: 0;
      border-radius: 0;
      background: transparent;
      cursor: pointer;
      box-shadow: none;
      transition: transform 0.15s ease, filter 0.15s ease;
    }
    #coach-ai-widget-root .coach-ai-launcher:hover {
      transform: translateY(-3px) scale(1.03);
    }
    #coach-ai-widget-root .coach-ai-launcher:focus-visible {
      outline: 3px solid var(--vis-navy);
      outline-offset: 3px;
    }
    #coach-ai-widget-root .coach-ai-launcher img {
      width: 100%;
      height: 100%;
      display: block;
      object-fit: contain;
      pointer-events: none;
      user-select: none;
      filter: drop-shadow(0 8px 14px rgba(12, 30, 61, 0.22));
    }
    #coach-ai-widget-root .coach-ai-launcher:hover img {
      filter: drop-shadow(0 12px 20px rgba(12, 30, 61, 0.28));
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
        width: 72px;
        height: 72px;
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
  launcher.innerHTML = `<img src="${iconUrl}" alt="" width="84" height="84" decoding="async">`

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
