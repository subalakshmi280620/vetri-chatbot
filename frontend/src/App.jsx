import { useEffect, useRef, useState } from 'react'
import './App.css'

// Set via VITE_API_URL (.env locally, Render env vars at build time for production).
const API_BASE = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const API_URL = `${API_BASE}/api/chatbot/chat/`
const HISTORY_URL = `${API_BASE}/api/chatbot/conversations/`
const FEEDBACK_URL = `${API_BASE}/api/chatbot/messages/feedback/`
const HEALTH_URL = `${API_BASE}/health/`
const IS_EMBED = new URLSearchParams(window.location.search).get('embed') === '1'
const CLIENT_TOKEN_KEY = 'visClientToken'
const CONVERSATION_ID_KEY = 'visConversationId'

function migrateLegacySessionStorage() {
  for (const key of [CLIENT_TOKEN_KEY, CONVERSATION_ID_KEY]) {
    const legacyValue = window.sessionStorage.getItem(key)
    if (legacyValue && !window.localStorage.getItem(key)) {
      window.localStorage.setItem(key, legacyValue)
    }
    window.sessionStorage.removeItem(key)
  }
}

migrateLegacySessionStorage()

function getStoredItem(key) {
  return window.localStorage.getItem(key)
}

function setStoredItem(key, value) {
  window.localStorage.setItem(key, value)
}

function removeStoredItem(key) {
  window.localStorage.removeItem(key)
}

function getClientToken() {
  let token = getStoredItem(CLIENT_TOKEN_KEY)
  if (!token) {
    token = crypto.randomUUID()
    setStoredItem(CLIENT_TOKEN_KEY, token)
  }
  return token
}

const WELCOME = {
  role: 'bot',
  text:
    'Welcome to Vetri IT Systems.\n\n' +
    'I am Coach AI — your assistant for VIS products, services, company info, ' +
    'training courses, quotations, and contact details.\n\n' +
    'Transforming Businesses with AI-Powered Digital Solutions.\n\n' +
    'How may I assist you today?',
}

const SUGGESTIONS = [
  'What products does VIS offer?',
  'What services does VIS provide?',
  'Tell me about Vetri Bills',
  'What is your mission and vision?',
  'How can I get a quotation?',
]

const SECTION_LABELS = [
  'Welcome to',
  'Course Overview',
  'Course Duration',
  'General Eligibility',
  'Eligibility Requirements',
  'Eligibility Check',
  'Eligibility Assessment',
  'Available Courses',
  'Admission Eligibility',
  'How to Apply',
  'Course Fee Information',
  'Contact',
  'About',
  'Our Products',
  'Our Services',
  'Portfolio',
  'Mission & Vision',
  'Why VIS',
  'AI Solutions',
  'Get Quotation',
  'Pricing & Quotation',
  'Technology Built',
  'Our Vision',
  'Our Mission',
  'Outcome:',
  'Step 1:',
  'Step 2:',
  'Step 3:',
  'Step 4:',
]

const SOURCE_LABELS = {
  verified_kb: 'Verified VIS answer',
  eligibility: 'Eligibility check',
  ai: 'AI-assisted answer',
  unverified: 'Limited information',
}

function VisLogo({ size = 36, className = '' }) {
  return (
    <span
      className={`vis-logo ${className}`.trim()}
      style={{ width: size, height: size, fontSize: Math.round(size * 0.3) }}
      aria-hidden="true"
    >
      VIS
    </span>
  )
}

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

function MessageBubble({
  role,
  text,
  source,
  feedback,
  messageId,
  onFeedback,
  showActions = false,
}) {
  const isBot = role === 'bot'
  const [copied, setCopied] = useState(false)

  async function copyText() {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1500)
    } catch {
      setCopied(false)
    }
  }

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
        {isBot && (
          <div className="bubble-meta">
            <span className="bubble-label">Coach AI</span>
            {source && (
              <span className={`source-badge source-${source}`}>
                {SOURCE_LABELS[source] || 'Coach AI'}
              </span>
            )}
          </div>
        )}
        <div className="bubble">{formatMessage(text)}</div>
        {isBot && showActions && (
          <div className="bubble-actions">
            <button type="button" className="bubble-action-btn" onClick={copyText}>
              {copied ? 'Copied' : 'Copy'}
            </button>
            {messageId && (
              <>
                <button
                  type="button"
                  className={`bubble-action-btn ${feedback === 'up' ? 'active' : ''}`}
                  onClick={() => onFeedback(messageId, 'up')}
                  aria-label="Helpful answer"
                >
                  👍
                </button>
                <button
                  type="button"
                  className={`bubble-action-btn ${feedback === 'down' ? 'active' : ''}`}
                  onClick={() => onFeedback(messageId, 'down')}
                  aria-label="Not helpful"
                >
                  👎
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function FollowUpChips({ items, disabled, onSelect }) {
  if (!items?.length) return null
  return (
    <div className="follow-up-chips">
      <p className="follow-up-label">Suggested next questions</p>
      <div className="follow-up-list">
        {items.map((item) => (
          <button
            key={item}
            type="button"
            className="follow-up-chip"
            disabled={disabled}
            onClick={() => onSelect(item)}
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  )
}

function SiteNav() {
  return (
    <nav className="site-nav" aria-label="Vetri IT Systems">
      <div className="site-nav-inner">
        <div className="site-brand">
          <VisLogo size={36} className="site-logo-mark" />
          <div>
            <span className="site-name">Vetri IT Systems</span>
            <span className="site-sub">Private Limited</span>
          </div>
        </div>
        <div className="site-nav-links">
          <span>Home</span>
          <span>Services</span>
          <span>Products</span>
          <span>Portfolios</span>
          <span>Why VIS</span>
          <span>Contact</span>
        </div>
        <span className="site-cta">Get Quotation</span>
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
          <p>Enterprise Software, Applied AI And Digital Transformation For Businesses That Intend To Lead Their Category.</p>
        </div>
        <div className="footer-col">
          <strong>Quick Links</strong>
          <p>Home · About Us · Services · Products · Why VIS · Contact</p>
        </div>
        <div className="footer-col">
          <strong>Our Products</strong>
          <p>Vetri Bills · Vetri Files · Coach AI · Vetri AI Assistant · Vetri CRM</p>
        </div>
        <div className="footer-col">
          <strong>Contact</strong>
          <p>+91 84381 54827</p>
          <p>support@vetri-it.com</p>
        </div>
      </div>
      <div className="site-footer-copy">
        © {new Date().getFullYear()} Vetri IT Systems. All rights reserved.
      </div>
    </footer>
  )
}

function formatChatDate(iso) {
  if (!iso) return ''
  const date = new Date(iso)
  const now = new Date()
  const isToday = date.toDateString() === now.toDateString()
  const yesterday = new Date(now)
  yesterday.setDate(now.getDate() - 1)
  const isYesterday = date.toDateString() === yesterday.toDateString()
  if (isToday) return `Today · ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
  if (isYesterday) return `Yesterday · ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
  return date.toLocaleString()
}

function HistorySidebar({
  items,
  activeId,
  onSelect,
  onNewChat,
  onDelete,
  onClose,
  open = true,
}) {
  return (
    <>
      <button
        type="button"
        className="history-overlay"
        aria-label="Close chat history"
        onClick={onClose}
      />
      <aside className={`history-sidebar history-sidebar-drawer ${open ? 'open' : ''}`}>
        <div className="history-sidebar-head">
          <div className="history-sidebar-title">
            <strong>Chat History</strong>
            <span className="history-sidebar-sub">
              {items.length} saved chat{items.length === 1 ? '' : 's'} on this device
            </span>
          </div>
          <div className="history-sidebar-actions">
            <button type="button" className="btn-green btn-sm" onClick={onNewChat}>
              + New chat
            </button>
            <button
              type="button"
              className="history-close-btn"
              aria-label="Close history"
              onClick={onClose}
            >
              ×
            </button>
          </div>
        </div>

        <div className="history-sidebar-toolbar">
          <span className="history-toolbar-label">Your conversations</span>
          <button type="button" className="history-toolbar-link" onClick={onNewChat}>
            Start new
          </button>
        </div>

        {items.length === 0 ? (
          <p className="muted history-empty">
            No chats yet. Ask a question and your conversation will be saved here automatically.
          </p>
        ) : (
          <ul className="history-list">
            {items.map((item) => (
              <li key={item.id} className="history-list-item">
                <button
                  type="button"
                  className={`history-chat-btn ${item.id === activeId ? 'active' : ''}`}
                  onClick={() => onSelect(item.id)}
                >
                <span className="history-chat-title">{item.title || item.preview}</span>
                {item.first_question &&
                  item.question_count > 1 &&
                  item.first_question !== item.title && (
                    <small className="history-chat-started">
                      Started with: {item.first_question}
                    </small>
                  )}
                <small className="history-chat-meta">
                  {item.question_count || 1} question
                  {(item.question_count || 1) === 1 ? '' : 's'}
                  {item.message_count ? ` · ${item.message_count} messages` : ''}
                  {' · '}
                  {formatChatDate(item.updated_at || item.created_at)}
                </small>
                </button>
                <button
                  type="button"
                  className="history-delete-btn"
                  aria-label="Delete chat"
                  title="Delete chat"
                  onClick={(event) => {
                    event.stopPropagation()
                    onDelete(item.id)
                  }}
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        )}

        <footer className="history-sidebar-foot">
          Saved on this browser only. Other people and other devices cannot see your chats.
          Use + New chat to start a separate conversation.
        </footer>
      </aside>
    </>
  )
}

function App() {
  const [messages, setMessages] = useState([WELCOME])
  const [conversationId, setConversationId] = useState(
    () => getStoredItem(CONVERSATION_ID_KEY) || ''
  )
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [historyList, setHistoryList] = useState([])
  const [widgetOpen, setWidgetOpen] = useState(!IS_EMBED)
  const [historyOpen, setHistoryOpen] = useState(false)
  const [apiOnline, setApiOnline] = useState(true)
  const [followUps, setFollowUps] = useState([])
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
    void bootstrapChat()
  }, [])

  useEffect(() => {
    if (!IS_EMBED || !widgetOpen) return
    void bootstrapChat()
  }, [widgetOpen])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading, followUps])

  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await fetch(HEALTH_URL)
        setApiOnline(res.ok)
      } catch {
        setApiOnline(false)
      }
    }
    checkHealth()
    const timer = window.setInterval(checkHealth, 60000)
    return () => window.clearInterval(timer)
  }, [])

  function rememberConversation(id) {
    setConversationId(id)
    setStoredItem(CONVERSATION_ID_KEY, id)
  }

  async function bootstrapChat() {
    const conversations = await loadHistoryList()
    const savedId = getStoredItem(CONVERSATION_ID_KEY)
    if (savedId && conversations.some((item) => item.id === savedId)) {
      await openConversation(savedId)
      return
    }
    if (savedId) {
      removeStoredItem(CONVERSATION_ID_KEY)
      setConversationId('')
    }
    if (conversations.length > 0) {
      await openConversation(conversations[0].id)
    }
  }

  async function loadHistoryList() {
    try {
      const res = await fetch(`${HISTORY_URL}?client_token=${encodeURIComponent(getClientToken())}`)
      if (!res.ok) {
        return []
      }
      const data = await res.json()
      const conversations = data.conversations || []
      setHistoryList(conversations)
      return conversations
    } catch {
      if (!IS_EMBED) {
        setError('Unable to load conversation history. Please check the backend is running.')
      }
      return []
    }
  }

  async function openConversation(id) {
    try {
      const res = await fetch(
        `${HISTORY_URL}${id}/?client_token=${encodeURIComponent(getClientToken())}`
      )
      const data = await res.json()
      if (!res.ok) {
        if (res.status === 403 || res.status === 404) {
          removeStoredItem(CONVERSATION_ID_KEY)
          setConversationId('')
        }
        throw new Error(data.error || 'Conversation not found')
      }
      rememberConversation(id)
      const loaded = (data.messages || []).map((item) => ({
        role: item.role,
        text: item.text,
        source: item.source || '',
        feedback: item.feedback || '',
        messageId: item.id || null,
      }))
      setMessages(loaded.length ? loaded : [WELCOME])
      setFollowUps([])
      setError('')
      await loadHistoryList()
      return true
    } catch (err) {
      setError(err.message)
      return false
    }
  }

  function newChat() {
    removeStoredItem(CONVERSATION_ID_KEY)
    setConversationId('')
    setMessages([WELCOME])
    setFollowUps([])
    setError('')
    setHistoryOpen(false)
  }

  async function submitFeedback(messageId, rating) {
    try {
      const res = await fetch(FEEDBACK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message_id: messageId,
          rating,
          client_token: getClientToken(),
        }),
      })
      if (!res.ok) return
      setMessages((prev) =>
        prev.map((msg) =>
          msg.messageId === messageId ? { ...msg, feedback: rating } : msg
        )
      )
    } catch {
      // Feedback is optional; ignore network errors quietly.
    }
  }

  async function deleteConversation(id) {
    if (!window.confirm('Delete this chat from your history?')) return

    try {
      const wasActive = id === conversationId
      const res = await fetch(
        `${HISTORY_URL}${id}/?client_token=${encodeURIComponent(getClientToken())}`,
        { method: 'DELETE' }
      )
      if (!res.ok && res.status !== 204) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.error || 'Could not delete chat.')
      }

      const conversations = await loadHistoryList()
      if (wasActive) {
        if (conversations.length > 0) {
          await openConversation(conversations[0].id)
        } else {
          newChat()
        }
      }
    } catch (err) {
      setError(err.message)
    }
  }

  async function openHistoryPanel() {
    await loadHistoryList()
    setHistoryOpen(true)
  }

  function closeHistoryPanel() {
    setHistoryOpen(false)
  }

  function toggleHistoryPanel() {
    if (historyOpen) {
      closeHistoryPanel()
      return
    }
    void openHistoryPanel()
  }

  async function sendMessage(text) {
    const message = (text ?? input).trim()
    if (!message || loading) return

    setError('')
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', text: message }])
    setFollowUps([])
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
        {
          role: 'bot',
          text: data.reply || 'No reply received.',
          source: data.source || '',
          messageId: data.message_id || null,
          feedback: '',
        },
      ])
      setFollowUps(data.suggestions || [])

      loadHistoryList()
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
  const lastBotIndex = messages.reduce(
    (index, msg, current) => (msg.role === 'bot' ? current : index),
    -1
  )

  return (
    <div className={IS_EMBED ? 'widget-root' : 'page'}>
      {!IS_EMBED && <SiteNav />}

      {!IS_EMBED && (
        <section className="page-hero" aria-label="Coach AI introduction">
          <div className="page-hero-inner">
            <VisLogo size={48} className="hero-logo-mark" />
            <div>
              <h1 className="page-hero-title">
                Transforming Businesses with <span>AI-Powered Digital Solutions</span>
              </h1>
              <p className="page-hero-text">
                AI-first enterprise technology — products, services, training, and support from Vetri IT Systems.
              </p>
            </div>
          </div>
        </section>
      )}

      {IS_EMBED && !widgetOpen && (
        <button
          type="button"
          className="launcher"
          onClick={() => setWidgetOpen(true)}
          aria-label="Open Coach AI"
        >
          <span className="launcher-pulse" aria-hidden="true" />
          <ChatIcon />
          <span className="launcher-label">Coach AI</span>
        </button>
      )}

      {(!IS_EMBED || widgetOpen) && (
        <div className={`app ${IS_EMBED ? 'app-embed' : 'app-standalone'}`}>
          <header className="topbar">
            <div className="brand">
              <VisLogo size={42} className="chat-logo-mark" />
              <div>
                <h1>Coach AI</h1>
                <p>Vetri IT Systems · Course Assistant</p>
              </div>
            </div>
            <div className="top-actions">
              <button type="button" className="ghost" onClick={newChat}>
                New chat
              </button>
              <button
                type="button"
                className={`ghost ${historyOpen ? 'active-top-btn' : ''}`}
                onClick={toggleHistoryPanel}
              >
                History
              </button>
              {IS_EMBED && (
                <button type="button" className="ghost icon-btn" onClick={() => setWidgetOpen(false)}>
                  ×
                </button>
              )}
              <span className={`status ${apiOnline ? '' : 'status-offline'}`}>
                <span className="dot" />
                {apiOnline ? 'Online' : 'Offline'}
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
                      Ask about courses, products, services, eligibility, fees, or how to apply.
                      I share only verified VIS information.
                    </p>
                  </div>
                )}

                {messages.map((msg, index) => (
                  <MessageBubble
                    key={msg.messageId || `${msg.role}-${index}`}
                    role={msg.role}
                    text={msg.text}
                    source={msg.source}
                    feedback={msg.feedback}
                    messageId={msg.messageId}
                    onFeedback={submitFeedback}
                    showActions={msg.role === 'bot' && index === lastBotIndex && !loading}
                  />
                ))}

                {!loading && (
                  <FollowUpChips
                    items={followUps}
                    disabled={loading}
                    onSelect={sendMessage}
                  />
                )}

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

            {historyOpen && (
              <HistorySidebar
                items={historyList}
                activeId={conversationId}
                onSelect={(id) => {
                  openConversation(id)
                  closeHistoryPanel()
                }}
                onNewChat={newChat}
                onDelete={deleteConversation}
                onClose={closeHistoryPanel}
                open={historyOpen}
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
