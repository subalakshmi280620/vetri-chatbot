import { useEffect, useRef, useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const API_URL = `${API_BASE}/api/chatbot/chat/`
const HISTORY_URL = `${API_BASE}/api/chatbot/conversations/`
const IS_EMBED = new URLSearchParams(window.location.search).get('embed') === '1'

const WELCOME = {
  role: 'bot',
  text: 'Hi, I am Vetri AI Coach. Ask me about courses, mock interviews, pricing, or how to get started.',
}

const SUGGESTIONS = [
  'What courses do you offer?',
  'Tell me about Python Fullstack',
  'Tell me about UI/UX',
  'How do mock interviews work?',
  'Is Vetri AI free to use?',
  'How can I contact you?',
]

function App() {
  const [messages, setMessages] = useState([WELCOME])
  const [conversationId, setConversationId] = useState(
    () => window.sessionStorage.getItem('vetriConversationId') || ''
  )
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showHistory, setShowHistory] = useState(false)
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
    if (!IS_EMBED || !widgetOpen) return
    const savedId = window.sessionStorage.getItem('vetriConversationId')
    if (!savedId) return
    openConversation(savedId)
  }, [widgetOpen])

  function rememberConversation(id) {
    setConversationId(id)
    window.sessionStorage.setItem('vetriConversationId', id)
  }

  async function loadHistoryList() {
    try {
      const res = await fetch(HISTORY_URL)
      const data = await res.json()
      setHistoryList(data.conversations || [])
    } catch {
      setError('Could not load chat history.')
    }
  }

  async function openHistory() {
    setShowHistory(true)
    await loadHistoryList()
  }

  async function openConversation(id) {
    try {
      const res = await fetch(`${HISTORY_URL}${id}/`)
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
      setShowHistory(false)
    } catch (err) {
      setError(err.message)
    }
  }

  function newChat() {
    window.sessionStorage.removeItem('vetriConversationId')
    setConversationId('')
    setMessages([WELCOME])
    setShowHistory(false)
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
    } catch (err) {
      const fallback =
        err instanceof TypeError
          ? API_BASE.includes('127.0.0.1') || API_BASE.includes('localhost')
            ? 'Cannot reach the backend. Make sure Django is running on port 8000.'
            : `Cannot reach the API (${API_BASE}). On Render, set VITE_API_URL to the Web Service URL and redeploy the Static Site.`
          : err.message
      setError(fallback)
      setMessages((prev) => [
        ...prev,
        { role: 'bot', text: 'Sorry, I could not respond just now. Please try again.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  function onSubmit(event) {
    event.preventDefault()
    sendMessage()
  }

  return (
    <div className={IS_EMBED ? 'widget-root' : undefined}>
      {IS_EMBED && !widgetOpen && (
        <button
          type="button"
          className="launcher"
          onClick={() => setWidgetOpen(true)}
          aria-label="Open Vetri AI Coach"
        >
          V
        </button>
      )}

      {(!IS_EMBED || widgetOpen) && (
    <div className={`app ${IS_EMBED ? 'app-embed' : ''}`}>
      <header className="topbar">
        <div className="brand">
          <span className="logo" aria-hidden="true">
            V
          </span>
          <div>
            <h1>Vetri AI Coach</h1>
            <p>Interview prep for Vetri IT Systems</p>
          </div>
        </div>
        <div className="top-actions">
          <button type="button" className="ghost" onClick={newChat}>
            New chat
          </button>
          <button
            type="button"
            className="ghost"
            onClick={() =>
              IS_EMBED
                ? conversationId
                  ? openConversation(conversationId)
                  : setError('No saved chat in this tab yet. Send a message first.')
                : openHistory()
            }
          >
            History
          </button>
          {IS_EMBED && (
            <button type="button" className="ghost" onClick={() => setWidgetOpen(false)}>
              Close
            </button>
          )}
          <span className="status">
            <span className="dot" />
            Online
          </span>
        </div>
      </header>

      {showHistory && (
        <aside className="history">
          <div className="history-head">
            <strong>Saved chats</strong>
            <button type="button" className="ghost" onClick={() => setShowHistory(false)}>
              Close
            </button>
          </div>
          {historyList.length === 0 && <p className="muted">No saved chats yet. Send a message first.</p>}
          <ul>
            {historyList.map((item) => (
              <li key={item.id}>
                <button type="button" onClick={() => openConversation(item.id)}>
                  <span>{item.preview}</span>
                  <small>{new Date(item.created_at).toLocaleString()}</small>
                </button>
              </li>
            ))}
          </ul>
        </aside>
      )}

      <main className="thread" aria-live="polite">
        {messages.map((msg, index) => (
          <div key={index} className={`bubble-row ${msg.role}`}>
            <div className="bubble">{msg.text}</div>
          </div>
        ))}
        {loading && (
          <div className="bubble-row bot">
            <div className="bubble typing">Thinking…</div>
          </div>
        )}
        <div ref={bottomRef} />
      </main>

      {error && <p className="error">{error}</p>}

      <div className="suggestions">
        {SUGGESTIONS.map((item) => (
          <button
            key={item}
            type="button"
            disabled={loading}
            onClick={() => sendMessage(item)}
          >
            {item}
          </button>
        ))}
      </div>

      <form className="composer" onSubmit={onSubmit}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about courses, mock interviews, or contact info…"
          disabled={loading}
          aria-label="Chat message"
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
      )}
    </div>
  )
}

export default App
