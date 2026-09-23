import { useEffect, useRef, useState } from 'react'
import './App.css'

// Set via VITE_API_URL (.env locally, Render env vars at build time for production).
const API_BASE = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const API_URL = `${API_BASE}/api/chatbot/chat/`
const HISTORY_URL = `${API_BASE}/api/chatbot/conversations/`
const IS_EMBED = new URLSearchParams(window.location.search).get('embed') === '1'

function getClientToken() {
  const key = 'visClientToken'
  let token = window.sessionStorage.getItem(key)
  if (!token) {
    token = crypto.randomUUID()
    window.sessionStorage.setItem(key, token)
  }
  return token
}

const WELCOME = {
  role: 'bot',
  text:
    'Welcome to Vetri IT Systems (VIS).\n\n' +
    'I am Coach AI, your virtual assistant for course information, duration, ' +
    'eligibility, how to apply, and contact details.\n\n' +
    'I provide only verified information from our official VIS course data. ' +
    'How may I assist you today?',
}

const SUGGESTIONS = [
  'What courses are available?',
  'How do I apply for a course?',
  'What is the course duration?',
  'What are the eligibility requirements?',
  'How can I contact the VIS team?',
]

const SECTION_LABELS = [
  'Welcome to',
  'Course Overview',
  'Course Duration',
  'Eligibility Requirements',
  'Eligibility Check',
  'Eligibility Assessment',
  'Available Courses',
  'Admission Eligibility',
  'How to Apply',
  'Course Fee Information',
  'Contact',
  'About',
  'Outcome:',
  'Step 1:',
  'Step 2:',
  'Step 3:',
  'Step 4:',
]

function ChatIcon() {
  return (
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v7A2.5 2.5 0 0 1 17.5 15H9l-4.5 3.5V5.5Z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function SendIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="m5 12 14-7-7 14-2-5-5-2Z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function ChevronIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="m9 6 6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

function formatMessage(text) {
  const lines = text.split('\n')
  return lines.map((line, index) => {
    const trimmed = line.trim()
    const isHeading = SECTION_LABELS.some((label) => trimmed.startsWith(label))
    const isOutcome = trimmed.startsWith('Outcome:')
    const isBullet = trimmed.startsWith('•')

    if (!trimmed) {
      return <br key={index} />
    }

    if (isHeading || isOutcome) {
      return (
        <p key={index} className={`msg-line ${isOutcome ? 'msg-outcome' : 'msg-heading'}`}>
          {line}
        </p>
      )
    }

    if (isBullet) {
      return <p key={index} className="msg-line msg-bullet">{line}</p>
    }

    return <p key={index} className="msg-line">{line}</p>
  })
}

function MessageBubble({ role, text }) {
  const isBot = role === 'bot'
  return (
    <div className={`bubble-row ${role}`}>
      {isBot && (
        <span className="avatar" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5" />
            <path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </span>
      )}
      <div className="bubble-wrap">
        {isBot && <span className="bubble-label">Coach AI</span>}
        <div className="bubble">{formatMessage(text)}</div>
      </div>
    </div>
  )
}

function SiteNav() {
  return (
    <nav className="site-nav" aria-label="Vetri IT Systems">
      <div className="site-nav-inner">
        <div className="site-brand">
          <span className="site-logo">V</span>
          <div>
            <span className="site-name">Vetri IT Systems</span>
            <span className="site-sub">Private Limited</span>
          </div>
        </div>
        <div className="site-nav-links">
          <span>Home</span>
          <span>Services</span>
          <span>Products</span>
          <span>Contact</span>
        </div>
        <span className="site-cta">Coach AI</span>
      </div>
    </nav>
  )
}

function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-footer-grid">
        <div className="footer-col">
          <strong>Vetri IT Systems</strong>
          <p>Enterprise Software, Applied AI and Digital Transformation for businesses that impact.</p>
        </div>
        <div className="footer-col">
          <strong>Quick Links</strong>
          <p>Home · Services · Portfolio · Contact</p>
        </div>
        <div className="footer-col">
          <strong>Our Products</strong>
          <p>Coach AI · Vetri AI Assistant · Vetri LMS</p>
        </div>
        <div className="footer-col">
          <strong>Contact</strong>
          <p>+91-8438164827</p>
          <p>+91-8438781327</p>
        </div>
      </div>
      <div className="site-footer-copy">
        © {new Date().getFullYear()} Vetri IT Systems. All rights reserved.
      </div>
    </footer>
  )
}

function HistorySidebar({ items, activeId, onSelect, onNewChat }) {
  return (
    <aside className="history-sidebar">
      <div className="history-sidebar-head">
        <strong>History</strong>
        <button type="button" className="btn-green btn-sm" onClick={onNewChat}>
          New chat
        </button>
      </div>
      {items.length === 0 ? (
        <p className="muted history-empty">No saved conversations yet.</p>
      ) : (
        <ul className="history-list">
          {items.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                className={item.id === activeId ? 'active' : ''}
                onClick={() => onSelect(item.id)}
              >
                <span>{item.preview}</span>
                <small>
                  {new Date(item.updated_at || item.created_at).toLocaleString()}
                </small>
              </button>
            </li>
          ))}
        </ul>
      )}
    </aside>
  )
}

function App() {
  const [messages, setMessages] = useState([WELCOME])
  const [conversationId, setConversationId] = useState(
    () => window.sessionStorage.getItem('visConversationId') || ''
  )
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [historyList, setHistoryList] = useState([])
  const [widgetOpen, setWidgetOpen] = useState(!IS_EMBED)
  const bottomRef = useRef(null)

  useEffect(() => {
    document.documentElement.classList.toggle('embed', IS_EMBED)
    document.body.classList.toggle('embed', IS_EMBED)
    return () => {
      document.documentElement.classList.remove('embed')
      document.body.classList.remove('embed')
    }
  }, [])

  useEffect(() => {
    if (IS_EMBED) return
    loadHistoryList()
    const savedId = window.sessionStorage.getItem('visConversationId')
    if (savedId) {
      openConversation(savedId)
    }
  }, [])

  useEffect(() => {
    if (!IS_EMBED || !widgetOpen) return
    const savedId = window.sessionStorage.getItem('visConversationId')
    if (!savedId) return
    openConversation(savedId)
  }, [widgetOpen])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function rememberConversation(id) {
    setConversationId(id)
    window.sessionStorage.setItem('visConversationId', id)
  }

  async function loadHistoryList() {
    try {
      const res = await fetch(`${HISTORY_URL}?client_token=${encodeURIComponent(getClientToken())}`)
      const data = await res.json()
      setHistoryList(data.conversations || [])
    } catch {
      if (!IS_EMBED) {
        setError('Unable to load conversation history. Please try again.')
      }
    }
  }

  async function openConversation(id) {
    try {
      const res = await fetch(
        `${HISTORY_URL}${id}/?client_token=${encodeURIComponent(getClientToken())}`
      )
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.error || 'Conversation not found')
      }
      rememberConversation(id)
      const loaded = (data.messages || []).map((item) => ({
        role: item.role,
        text: item.text,
      }))
      setMessages(loaded.length ? loaded : [WELCOME])
      setError('')
    } catch (err) {
      setError(err.message)
    }
  }

  function newChat() {
    window.sessionStorage.removeItem('visConversationId')
    setConversationId('')
    setMessages([WELCOME])
    setError('')
  }

  async function sendMessage(text) {
    const message = (text ?? input).trim()
    if (!message || loading) return

    setError('')
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', text: message }])
    setLoading(true)

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          client_token: getClientToken(),
          conversation_id: conversationId || undefined,
        }),
      })
      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.error || 'Could not get a reply.')
      }

      if (data.conversation_id) {
        rememberConversation(data.conversation_id)
      }

      setMessages((prev) => [
        ...prev,
        { role: 'bot', text: data.reply || 'No reply received.' },
      ])

      if (!IS_EMBED) {
        loadHistoryList()
      }
    } catch (err) {
      const fallback =
        err instanceof TypeError
          ? API_BASE.includes('127.0.0.1') || API_BASE.includes('localhost')
            ? 'The assistant is temporarily unavailable. Please ensure the backend service is running on port 8000.'
            : `The assistant is temporarily unavailable. Please verify the API connection (${API_BASE}).`
          : err.message
      setError(fallback)
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          text:
            'We apologise for the inconvenience. I am unable to respond at the moment. ' +
            'Please try again in a few moments.',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  function onSubmit(event) {
    event.preventDefault()
    sendMessage()
  }

  const showSuggestions = !messages.some((msg) => msg.role === 'user')

  return (
    <div className={IS_EMBED ? 'widget-root' : 'page'}>
      {!IS_EMBED && <SiteNav />}

      {IS_EMBED && !widgetOpen && (
        <button
          type="button"
          className="launcher"
          onClick={() => setWidgetOpen(true)}
          aria-label="Open Coach AI"
        >
          <ChatIcon />
        </button>
      )}

      {(!IS_EMBED || widgetOpen) && (
        <div className={`app ${IS_EMBED ? 'app-embed' : 'app-standalone'}`}>
          <header className="topbar">
            <div className="brand">
              <span className="logo" aria-hidden="true">AI</span>
              <div>
                <h1>Coach AI</h1>
                <p>Vetri IT Systems · Course Assistant</p>
              </div>
            </div>
            <div className="top-actions">
              {IS_EMBED && (
                <>
                  <button type="button" className="ghost" onClick={newChat}>
                    New chat
                  </button>
                  <button
                    type="button"
                    className="ghost"
                    onClick={() =>
                      conversationId
                        ? openConversation(conversationId)
                        : setError('No saved conversation in this tab yet. Please send a message first.')
                    }
                  >
                    History
                  </button>
                  <button type="button" className="ghost icon-btn" onClick={() => setWidgetOpen(false)}>
                    ×
                  </button>
                </>
              )}
              <span className="status">
                <span className="dot" />
                Online
              </span>
            </div>
          </header>

          <div className="workspace">
            <div className="chat-panel">
              <main className="thread" aria-live="polite">
                {showSuggestions && (
                  <div className="welcome-card">
                    <span className="pill-tag">Coach AI</span>
                    <h2>
                      How can we help you <span className="highlight">today?</span>
                    </h2>
                    <p>
                      Ask about courses, duration, eligibility, fees, or how to apply.
                      I share only verified VIS information.
                    </p>
                  </div>
                )}

                {messages.map((msg, index) => (
                  <MessageBubble key={index} role={msg.role} text={msg.text} />
                ))}

                {loading && (
                  <div className="bubble-row bot">
                    <span className="avatar" aria-hidden="true">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5" />
                        <path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                      </svg>
                    </span>
                    <div className="bubble-wrap">
                      <span className="bubble-label">Coach AI</span>
                      <div className="bubble typing">
                        <span className="typing-dots" aria-hidden="true">
                          <span />
                          <span />
                          <span />
                        </span>
                        Preparing your response…
                      </div>
                    </div>
                  </div>
                )}
                <div ref={bottomRef} />
              </main>

              {error && <p className="error">{error}</p>}

              {showSuggestions && (
                <div className="suggestions">
                  <p className="suggestions-label">Frequently Asked Questions</p>
                  <div className="faq-list">
                    {SUGGESTIONS.map((item) => (
                      <button
                        key={item}
                        type="button"
                        className="faq-item"
                        disabled={loading}
                        onClick={() => sendMessage(item)}
                      >
                        <span>{item}</span>
                        <ChevronIcon />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <form className="composer" onSubmit={onSubmit}>
                <input
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder="Type your question here…"
                  disabled={loading}
                  aria-label="Chat message"
                />
                <button
                  type="submit"
                  className="btn-green send-btn"
                  disabled={loading || !input.trim()}
                  aria-label="Send message"
                >
                  <SendIcon />
                </button>
              </form>

              <footer className="chat-footer">
                Powered by Vetri IT Systems · Verified information only
              </footer>
            </div>

            {!IS_EMBED && (
              <HistorySidebar
                items={historyList}
                activeId={conversationId}
                onSelect={openConversation}
                onNewChat={newChat}
              />
            )}
          </div>
        </div>
      )}

      {!IS_EMBED && <SiteFooter />}
    </div>
  )
}

export default App
