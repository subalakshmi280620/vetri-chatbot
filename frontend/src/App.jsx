import { useCallback, useEffect, useRef, useState } from 'react'
import './App.css'

const PRODUCTION_API_URL = 'https://vetri-chatbot-1.onrender.com'

function resolveApiBase() {
  const fromEnv = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
  if (fromEnv) return fromEnv

  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    if (host.includes('onrender.com') || host.includes('vetriitsystems.com')) {
      return PRODUCTION_API_URL
    }
  }

  return 'http://127.0.0.1:8000'
}

// Set via VITE_API_URL (.env locally, Render env vars at build time for production).
const API_BASE = resolveApiBase()
const API_URL = `${API_BASE}/api/chatbot/chat/`
const HISTORY_URL = `${API_BASE}/api/chatbot/conversations/`
const FEEDBACK_URL = `${API_BASE}/api/chatbot/messages/feedback/`
const ENQUIRY_URL = `${API_BASE}/api/chatbot/enquiries/`
const MAX_ATTACHMENTS = 3
const ACCEPTED_FILE_TYPES =
  'image/jpeg,image/png,image/webp,image/gif,.pdf,.txt,.md,text/plain,text/markdown,application/pdf'
const SPEECH_RECOGNITION =
  typeof window !== 'undefined'
    ? window.SpeechRecognition || window.webkitSpeechRecognition
    : null

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(new Error(`Could not read ${file.name}.`))
    reader.readAsDataURL(file)
  })
}

function dataUrlToBase64(dataUrl) {
  const parts = String(dataUrl).split(',')
  return parts.length > 1 ? parts[1] : parts[0]
}

async function buildAttachmentFromFile(file) {
  const dataUrl = await readFileAsDataUrl(file)
  const mimeType = file.type || 'application/octet-stream'
  const isImage = mimeType.startsWith('image/')
  return {
    id: `${file.name}-${file.size}-${file.lastModified}`,
    name: file.name,
    mime_type: mimeType,
    type: isImage ? 'image' : 'document',
    data: dataUrlToBase64(dataUrl),
    previewUrl: isImage ? dataUrl : '',
  }
}
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
    'Building Tomorrow\'s Software Solutions Today.\n\n' +
    'I am Coach AI — your assistant for VIS products, services, portfolio, ' +
    'training courses, quotations, and contact details.\n\n' +
    'How may I assist you today?',
}

const SUGGESTIONS = [
  'What products does VIS offer?',
  'What services does VIS provide?',
  'Tell me about Vetri Bills',
  'What is your mission and vision?',
  'How can I contact the VIS team?',
]

const QUICK_ACTIONS = [
  { label: 'Get Quotation', type: 'quotation' },
  { label: 'Book Consultation', type: 'consultation' },
  { label: 'Request Demo', type: 'demo' },
]

const ENQUIRY_TITLES = {
  quotation: 'Get Quotation',
  consultation: 'Book a Consultation',
  demo: 'Request a Product Demo',
  sales: 'Contact Sales Team',
  general: 'Submit Enquiry',
}

const ENQUIRY_CTA_LABELS = {
  quotation: 'Submit quotation enquiry',
  consultation: 'Book consultation enquiry',
  demo: 'Request product demo',
  sales: 'Contact sales enquiry',
}

const ENQUIRY_TYPE_TABS = [
  { type: 'quotation', label: 'Quotation' },
  { type: 'consultation', label: 'Consultation' },
  { type: 'demo', label: 'Product Demo' },
]

const ENQUIRY_SUBTEXT = {
  quotation:
    'Tell us what you want to achieve. You will get a tailored proposal, timeline, and indicative pricing.',
  consultation:
    'Speak directly with a VIS solution consultant — no call centres, no scripts.',
  demo:
    'See VIS enterprise products with live workflow previews. Tell us which product to explore.',
  sales: 'Our sales team will help with product selection and enterprise requirements.',
  general: 'Tell us what you need. Our VIS team will contact you by email or phone.',
}

const INTEREST_OPTIONS = [
  'Vetri Bills',
  'Vetri Files',
  'Vetri Project Management',
  'Coach AI',
  'Vetri AI Assistant',
  'Vetri CRM',
  'Vetri Training Management System',
  'Website Development',
  'Mobile App Development',
  'UI/UX Design',
  'AI Solutions',
  'Generative AI',
  'ERP Development',
  'Digital Marketing',
  'SEO',
  'Cloud Services',
  'Training Course',
  'Other',
]

const EMPTY_ENQUIRY_FORM = {
  full_name: '',
  company: '',
  email: '',
  phone: '',
  interest: '',
  message: '',
}

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
  'Enquiry Submitted',
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
  unverified: 'Limited information',
}

function VisLogo({ size = 36, className = '' }) {
  return (
    <span
      className={`vis-logo vis-logo-image ${className}`.trim()}
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <img src="/vis-logo.svg" alt="" width={size} height={size} />
    </span>
  )
}

const LINKIFY_RE = /(\+?\d[\d\s-]{8,}\d|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})/gi

function linkifyLine(line) {
  const parts = line.split(LINKIFY_RE)
  return parts.map((part, index) => {
    if (!part) return null
    if (part.includes('@')) {
      return (
        <a key={index} href={`mailto:${part}`} className="msg-link">
          {part}
        </a>
      )
    }
    if (/^\+?\d/.test(part.trim())) {
      const tel = part.replace(/[\s-]/g, '')
      return (
        <a key={index} href={`tel:${tel}`} className="msg-link">
          {part}
        </a>
      )
    }
    return part
  })
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

function MicIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 15a3 3 0 0 0 3-3V7a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Z"
        stroke="currentColor"
        strokeWidth="1.75"
      />
      <path d="M5 11a7 7 0 0 0 14 0M12 18v3" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
    </svg>
  )
}

function AttachIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M16 7.5V15a4 4 0 0 1-8 0V6.5a3 3 0 0 1 6 0V14a2 2 0 0 1-4 0V7"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
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
          {linkifyLine(line)}
        </p>
      )
    }

    if (isBullet) {
      return <p key={index} className="msg-line msg-bullet">{linkifyLine(line)}</p>
    }

    return <p key={index} className="msg-line">{linkifyLine(line)}</p>
  })
}

function MessageBubble({
  role,
  text,
  attachments = [],
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
            {source && SOURCE_LABELS[source] && (
              <span className={`source-badge source-${source}`}>
                {SOURCE_LABELS[source]}
              </span>
            )}
          </div>
        )}
        {attachments.length > 0 && (
          <div className="bubble-attachments">
            {attachments.map((item) => (
              <div key={item.id || item.name} className="bubble-attachment">
                {item.previewUrl ? (
                  <img src={item.previewUrl} alt={item.name} className="attachment-preview" />
                ) : (
                  <span className="attachment-file">📄 {item.name}</span>
                )}
              </div>
            ))}
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

function QuickActionChips({ items, disabled, onSelect }) {
  return (
    <div className="quick-actions">
      <p className="quick-actions-label">Quick actions</p>
      <div className="quick-actions-list">
        {items.map((item) => (
          <button
            key={item.label}
            type="button"
            className="quick-action-chip"
            disabled={disabled}
            onClick={() => onSelect(item.type)}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  )
}

function EnquiryModal({
  open,
  enquiryType,
  form,
  onChange,
  onTypeChange,
  onClose,
  onSubmit,
  submitting,
  error,
}) {
  if (!open) return null

  const activeType = ENQUIRY_TYPE_TABS.some((tab) => tab.type === enquiryType)
    ? enquiryType
    : 'quotation'

  return (
    <div className="enquiry-overlay" onClick={onClose}>
      <div
        className="enquiry-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="enquiry-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="enquiry-modal-head">
          <h2 id="enquiry-title">{ENQUIRY_TITLES[activeType] || ENQUIRY_TITLES.general}</h2>
          <button type="button" className="enquiry-close-btn" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        <div className="enquiry-type-tabs" role="tablist" aria-label="Enquiry type">
          {ENQUIRY_TYPE_TABS.map((tab) => (
            <button
              key={tab.type}
              type="button"
              role="tab"
              aria-selected={activeType === tab.type}
              className={`enquiry-type-tab ${activeType === tab.type ? 'active' : ''}`}
              onClick={() => onTypeChange(tab.type)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <p className="enquiry-modal-sub">
          {ENQUIRY_SUBTEXT[activeType] || ENQUIRY_SUBTEXT.general}
        </p>

        <form className="enquiry-form" onSubmit={onSubmit}>
          <label>
            Full name *
            <input
              value={form.full_name}
              onChange={(event) => onChange('full_name', event.target.value)}
              placeholder="Your name"
              required
            />
          </label>
          <label>
            Company
            <input
              value={form.company}
              onChange={(event) => onChange('company', event.target.value)}
              placeholder="Company name"
            />
          </label>
          <label>
            Work email *
            <input
              type="email"
              value={form.email}
              onChange={(event) => onChange('email', event.target.value)}
              placeholder="you@company.com"
              required
            />
          </label>
          <label>
            Phone
            <input
              value={form.phone}
              onChange={(event) => onChange('phone', event.target.value)}
              placeholder="+91"
            />
          </label>
          <label>
            Product / service of interest
            <select
              value={form.interest}
              onChange={(event) => onChange('interest', event.target.value)}
            >
              <option value="">Select product / service</option>
              {INTEREST_OPTIONS.map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <label>
            How can we help? *
            <textarea
              value={form.message}
              onChange={(event) => onChange('message', event.target.value)}
              placeholder="Describe your requirement"
              rows={4}
              required
            />
          </label>

          {error && <p className="enquiry-error">{error}</p>}

          <button type="submit" className="btn-green enquiry-submit-btn" disabled={submitting}>
            {submitting ? 'Submitting…' : 'Submit Enquiry'}
          </button>
        </form>
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
          <p>
            <a href="tel:+918438154827" className="footer-link">+91 84381 54827</a>
          </p>
          <p>
            <a href="mailto:support@vetri-it.com" className="footer-link">support@vetri-it.com</a>
          </p>
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
  const [query, setQuery] = useState('')
  const normalizedQuery = query.trim().toLowerCase()
  const filteredItems = normalizedQuery
    ? items.filter((item) => {
        const haystack = [
          item.title,
          item.preview,
          item.first_question,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()
        return haystack.includes(normalizedQuery)
      })
    : items

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

        {items.length > 0 && (
          <div className="history-search-wrap">
            <input
              type="search"
              className="history-search-input"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search chats…"
              aria-label="Search chat history"
            />
          </div>
        )}

        {items.length === 0 ? (
          <p className="muted history-empty">
            No chats yet. Ask a question and your conversation will be saved here automatically.
          </p>
        ) : filteredItems.length === 0 ? (
          <p className="muted history-empty">No chats match your search.</p>
        ) : (
          <ul className="history-list">
            {filteredItems.map((item) => (
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
  const [pendingAttachments, setPendingAttachments] = useState([])
  const [isListening, setIsListening] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [historyList, setHistoryList] = useState([])
  const [widgetOpen, setWidgetOpen] = useState(!IS_EMBED)
  const [historyOpen, setHistoryOpen] = useState(false)
  const [apiStatus, setApiStatus] = useState('checking')
  const [followUps, setFollowUps] = useState([])
  const [enquiryCta, setEnquiryCta] = useState('')
  const [enquiryOpen, setEnquiryOpen] = useState(false)
  const [enquiryType, setEnquiryType] = useState('quotation')
  const [enquiryForm, setEnquiryForm] = useState(EMPTY_ENQUIRY_FORM)
  const [enquirySubmitting, setEnquirySubmitting] = useState(false)
  const [enquiryError, setEnquiryError] = useState('')
  const bottomRef = useRef(null)
  const abortRef = useRef(null)
  const fileInputRef = useRef(null)
  const speechRef = useRef(null)
  const voiceSupported = Boolean(SPEECH_RECOGNITION)

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

  const checkHealth = useCallback(async ({ retries = 4, delayMs = 4000 } = {}) => {
    setApiStatus('checking')
    for (let attempt = 0; attempt < retries; attempt += 1) {
      try {
        const controller = new AbortController()
        const timeoutId = window.setTimeout(() => controller.abort(), 90000)
        const res = await fetch(HEALTH_URL, {
          signal: controller.signal,
          cache: 'no-store',
        })
        window.clearTimeout(timeoutId)
        if (res.ok) {
          setApiStatus('online')
          return true
        }
      } catch {
        // Render free tier may be waking up — retry.
      }
      if (attempt < retries - 1) {
        await new Promise((resolve) => window.setTimeout(resolve, delayMs))
      }
    }
    setApiStatus('offline')
    return false
  }, [])

  useEffect(() => {
    void checkHealth()
    const timer = window.setInterval(() => {
      void checkHealth({ retries: 1, delayMs: 0 })
    }, 60000)
    return () => window.clearInterval(timer)
  }, [checkHealth])

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

  function stopGenerating() {
    abortRef.current?.abort()
  }

  function openEnquiry(type = 'general') {
    setEnquiryType(type)
    setEnquiryError('')
    setEnquiryOpen(true)
  }

  function closeEnquiry() {
    if (enquirySubmitting) return
    setEnquiryOpen(false)
    setEnquiryError('')
  }

  function updateEnquiryField(field, value) {
    setEnquiryForm((prev) => ({ ...prev, [field]: value }))
  }

  async function submitEnquiryForm(event) {
    event.preventDefault()
    if (enquirySubmitting) return

    setEnquiryError('')
    setEnquirySubmitting(true)

    try {
      const res = await fetch(ENQUIRY_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...enquiryForm,
          enquiry_type: enquiryType,
          client_token: getClientToken(),
          conversation_id: conversationId || undefined,
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.error || 'Could not submit enquiry.')
      }

      setEnquiryOpen(false)
      setEnquiryForm(EMPTY_ENQUIRY_FORM)
      setMessages((prev) => [
        ...prev,
        {
          role: 'user',
          text:
            `Submitted enquiry: ${ENQUIRY_TITLES[enquiryType] || ENQUIRY_TITLES.general}\n` +
            `Name: ${enquiryForm.full_name}\nEmail: ${enquiryForm.email}`,
        },
        {
          role: 'bot',
          text: data.confirmation || 'Thank you. Your enquiry has been submitted.',
          source: 'verified_kb',
        },
      ])
      setApiStatus('online')
    } catch (err) {
      const message = err?.message || ''
      if (message === 'Failed to fetch') {
        setEnquiryError(
          'Cannot reach the server. Start the backend locally (python manage.py runserver), ' +
            'or wait a moment if the Render API is waking up. Check EMAIL_HOST settings if this started after adding SMTP.',
        )
      } else {
        setEnquiryError(message || 'Could not submit enquiry.')
      }
    } finally {
      setEnquirySubmitting(false)
    }
  }

  function exportChat() {
    if (messages.length === 0) return
    const transcript = messages
      .map((msg) => `${msg.role === 'user' ? 'You' : 'Coach AI'}:\n${msg.text}`)
      .join('\n\n')
    const blob = new Blob([transcript], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `coach-ai-chat-${new Date().toISOString().slice(0, 10)}.txt`
    link.click()
    URL.revokeObjectURL(url)
  }

  useEffect(() => {
    return () => {
      if (speechRef.current) {
        speechRef.current.stop()
        speechRef.current = null
      }
    }
  }, [])

  function removePendingAttachment(id) {
    setPendingAttachments((prev) => prev.filter((item) => item.id !== id))
  }

  async function handleAttachmentSelect(event) {
    const files = Array.from(event.target.files || [])
    event.target.value = ''
    if (!files.length) return

    const remaining = MAX_ATTACHMENTS - pendingAttachments.length
    if (remaining <= 0) {
      setError(`You can attach up to ${MAX_ATTACHMENTS} files per message.`)
      return
    }

    try {
      const selected = files.slice(0, remaining)
      const built = await Promise.all(selected.map((file) => buildAttachmentFromFile(file)))
      setPendingAttachments((prev) => [...prev, ...built])
      setError('')
    } catch (err) {
      setError(err.message || 'Could not read the selected file.')
    }
  }

  function toggleVoiceInput() {
    if (!voiceSupported || loading) return

    if (isListening && speechRef.current) {
      speechRef.current.stop()
      return
    }

    const recognition = new SPEECH_RECOGNITION()
    recognition.lang = 'en-IN'
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => {
      setIsListening(false)
      speechRef.current = null
    }
    recognition.onerror = () => {
      setIsListening(false)
      speechRef.current = null
      setError('Voice input failed. Try Chrome/Edge or type your question.')
    }
    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript || ''
      if (transcript) {
        setInput((prev) => (prev ? `${prev} ${transcript}` : transcript))
      }
    }

    speechRef.current = recognition
    recognition.start()
  }

  async function sendMessage(text, attachmentsOverride = null) {
    const message = (text ?? input).trim()
    const attachments = attachmentsOverride ?? pendingAttachments
    if ((!message && attachments.length === 0) || loading) return

    const displayText = message || `Shared ${attachments.map((item) => item.name).join(', ')}`

    setError('')
    setInput('')
    setPendingAttachments([])
    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        text: displayText,
        attachments: attachments.map((item) => ({
          id: item.id,
          name: item.name,
          previewUrl: item.previewUrl,
        })),
      },
    ])
    setFollowUps([])
    setEnquiryCta('')
    setLoading(true)

    const controller = new AbortController()
    abortRef.current = controller

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          client_token: getClientToken(),
          conversation_id: conversationId || undefined,
          attachments: attachments.map((item) => ({
            name: item.name,
            mime_type: item.mime_type,
            type: item.type,
            data: item.data,
          })),
        }),
        signal: controller.signal,
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
      setEnquiryCta(data.suggest_enquiry || '')
      setApiStatus('online')

      loadHistoryList()
    } catch (err) {
      if (err.name === 'AbortError') {
        setMessages((prev) => [
          ...prev,
          { role: 'bot', text: 'Response stopped.' },
        ])
        return
      }

      setApiStatus('offline')
      const fallback =
        err instanceof TypeError
          ? API_BASE.includes('127.0.0.1') || API_BASE.includes('localhost')
            ? 'The assistant is temporarily unavailable. Please ensure the backend service is running on port 8000.'
            : 'The assistant is waking up or temporarily unavailable. Please wait a moment and tap Retry.'
          : err.message
      setError(fallback)
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          text:
            'We apologise for the inconvenience. I am unable to respond at the moment. ' +
            'Please try again in a few moments, or contact support@vetri-it.com.',
        },
      ])
    } finally {
      abortRef.current = null
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
                <p>Vetri IT Systems · VIS Assistant</p>
              </div>
        </div>
            <div className="top-actions">
              <button type="button" className="ghost enquiry-top-btn" onClick={() => openEnquiry('quotation')}>
                Enquiry
              </button>
              <button type="button" className="ghost" onClick={exportChat} title="Export chat">
                Export
              </button>
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
              <button
                type="button"
                className={`status status-btn ${
                  apiStatus === 'offline'
                    ? 'status-offline'
                    : apiStatus === 'checking'
                      ? 'status-checking'
                      : ''
                }`}
                onClick={() => void checkHealth()}
                title="Check connection"
              >
                <span className="dot" />
                {apiStatus === 'checking' ? 'Connecting…' : apiStatus === 'online' ? 'Online' : 'Offline'}
              </button>
            </div>
          </header>

          <div className="workspace">
            <div className="chat-panel">
              {apiStatus === 'offline' && (
                <div className="offline-banner" role="status">
                  <span>Server is waking up or unreachable. Free hosting may take up to a minute on first visit.</span>
                  <button type="button" className="offline-retry-btn" onClick={() => void checkHealth()}>
                    Retry
                  </button>
                </div>
              )}

              <main className="thread" aria-live="polite">
                {showSuggestions && (
                  <div className="welcome-card">
                    <span className="pill-tag">Coach AI</span>
                    <h2>
                      How can we help you <span className="highlight">today?</span>
                    </h2>
                    <p>
                      Ask about products, services, quotations, training courses, or contact details.
                      I share only verified VIS information.
                    </p>
                    <QuickActionChips
                      items={QUICK_ACTIONS}
                      disabled={loading}
                      onSelect={openEnquiry}
                    />
                  </div>
                )}

                {messages.map((msg, index) => (
                  <MessageBubble
                    key={msg.messageId || `${msg.role}-${index}`}
                    role={msg.role}
                    text={msg.text}
                    attachments={msg.attachments || []}
                    source={msg.source}
                    feedback={msg.feedback}
                    messageId={msg.messageId}
                    onFeedback={submitFeedback}
                    showActions={msg.role === 'bot' && index === lastBotIndex && !loading}
                  />
                ))}

                {!loading && enquiryCta && ENQUIRY_CTA_LABELS[enquiryCta] && (
                  <div className="enquiry-cta">
                    <button
                      type="button"
                      className="btn-green enquiry-cta-btn"
                      onClick={() => openEnquiry(enquiryCta)}
                    >
                      {ENQUIRY_CTA_LABELS[enquiryCta]}
                    </button>
                  </div>
                )}

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

              {pendingAttachments.length > 0 && (
                <div className="composer-attachments">
                  {pendingAttachments.map((item) => (
                    <div key={item.id} className="composer-attachment-chip">
                      {item.previewUrl ? (
                        <img src={item.previewUrl} alt="" className="composer-attachment-thumb" />
                      ) : (
                        <span className="composer-attachment-name">📄 {item.name}</span>
                      )}
                      <button
                        type="button"
                        className="composer-attachment-remove"
                        onClick={() => removePendingAttachment(item.id)}
                        aria-label={`Remove ${item.name}`}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <form className="composer" onSubmit={onSubmit}>
                <input
                  ref={fileInputRef}
                  type="file"
                  className="composer-file-input"
                  accept={ACCEPTED_FILE_TYPES}
                  multiple
                  onChange={handleAttachmentSelect}
                  tabIndex={-1}
                  aria-hidden="true"
                />
                <button
                  type="button"
                  className="composer-tool-btn"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading || pendingAttachments.length >= MAX_ATTACHMENTS}
                  aria-label="Attach image or document"
                  title="Attach image or document"
                >
                  <AttachIcon />
                </button>
                {voiceSupported && (
                  <button
                    type="button"
                    className={`composer-tool-btn ${isListening ? 'is-active' : ''}`}
                    onClick={toggleVoiceInput}
                    disabled={loading}
                    aria-label={isListening ? 'Stop voice input' : 'Speak your question'}
                    title={isListening ? 'Listening…' : 'Voice input'}
                  >
                    <MicIcon />
                  </button>
                )}
                <input
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder={
                    isListening
                      ? 'Listening… speak now'
                      : 'Type, speak, or attach a file…'
                  }
                  disabled={loading}
                  aria-label="Chat message"
                />
                {loading ? (
                  <button
                    type="button"
                    className="btn-green send-btn stop-btn"
                    onClick={stopGenerating}
                    aria-label="Stop response"
                  >
                    Stop
                  </button>
                ) : (
                  <button
                    type="submit"
                    className="btn-green send-btn"
                    disabled={!input.trim() && pendingAttachments.length === 0}
                    aria-label="Send message"
                  >
                    <SendIcon />
                  </button>
                )}
              </form>

              <footer className="chat-footer">
                Text · Voice · Photos · PDF/TXT · Powered by Vetri IT Systems
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

      <EnquiryModal
        open={enquiryOpen}
        enquiryType={enquiryType}
        form={enquiryForm}
        onChange={updateEnquiryField}
        onTypeChange={setEnquiryType}
        onClose={closeEnquiry}
        onSubmit={submitEnquiryForm}
        submitting={enquirySubmitting}
        error={enquiryError}
      />
    </div>
  )
}

export default App
