import { useCallback, useEffect, useRef, useState } from 'react'
import heroArtwork from './assets/hero.png'
import './App.css'

const PRODUCTION_API_URL = 'https://vetri-chatbot-1.onrender.com'

function resolveApiBase() {
  const fromEnv = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
  if (fromEnv) return fromEnv

  if (import.meta.env.DEV) return ''

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
const EMBED_SEARCH = new URLSearchParams(window.location.search)
const IS_EMBED = EMBED_SEARCH.get('embed') === '1'
const EMBED_HOST_WIDGET = EMBED_SEARCH.get('open') === '1'
const EMBED_PAUSED = false
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

const SUGGESTIONS = [
  'What products does VIS offer?',
  'What services does VIS provide?',
  'Tell me about Vetri Bills',
  'What is your mission and vision?',
  'How can I contact the VIS team?',
]

const ENQUIRY_TITLES = {
  quotation: 'Get Quotation',
  consultation: 'Book a Consultation',
  demo: 'Request a Product Demo',
  enroll: 'Enroll now',
  sales: 'Contact Sales Team',
  general: 'Submit Enquiry',
}

const ENQUIRY_CTA_LABELS = {
  quotation: 'Get quotation',
  consultation: 'Book consultation',
  demo: 'Request demo',
  enroll: 'Enroll now',
  sales: 'Contact sales',
}

const ENQUIRY_TYPE_TABS = [
  { type: 'enroll', label: 'Enroll' },
  { type: 'quotation', label: 'Quotation' },
  { type: 'consultation', label: 'Consultation' },
  { type: 'demo', label: 'Product Demo' },
  { type: 'sales', label: 'Sales' },
  { type: 'general', label: 'General' },
]

const ENQUIRY_SUBTEXT = {
  quotation:
    'Tell us what you want to achieve. You will get a tailored proposal, timeline, and indicative pricing.',
  consultation:
    'Speak directly with a VIS solution consultant — no call centres, no scripts.',
  demo:
    'See VIS enterprise products with live workflow previews. Tell us which product to explore.',
  enroll:
    'Share your details here. Our team will contact you about the course, website, product, or service. No website sign-in.',
  sales: 'Our sales team will help with product selection and enterprise requirements.',
  general: 'Tell us what you need. Our VIS team will contact you by email or phone.',
}

const DEMO_PRODUCT_OPTIONS = [
  'Vetri Bills',
  'Vetri Files',
  'Vetri Project Management',
  'Coach AI',
  'Vetri AI Assistant',
  'Vetri CRM',
  'Vetri Training Management System',
  'HR Management Tool',
]

const QUOTATION_INTEREST_OPTIONS = [
  ...DEMO_PRODUCT_OPTIONS,
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

const ENROLL_INTEREST_OPTIONS = [
  'Python Fullstack',
  'Java Fullstack',
  'Prompt Engineering',
  'UI/UX',
  'Software Testing',
  'Data Analytics',
  'Mobile App Development',
  'AWS & DevOps',
  'Data Science',
  'Digital Marketing',
  'Ecommerce website (₹9,999 + GST)',
  'Small retail shop website (₹3,000 + GST)',
  ...DEMO_PRODUCT_OPTIONS,
  'Other',
]

const CONSULTATION_INTEREST_OPTIONS = [
  'Product selection advice',
  'Custom software / web / mobile',
  'AI & automation strategy',
  'Training & courses',
  'Digital marketing / SEO',
  'Not sure — need guidance',
  'Other',
]

const ENQUIRY_FORM_CONFIG = {
  quotation: {
    companyLabel: 'Company / organisation',
    companyPlaceholder: 'Your company name',
    interestLabel: 'Product or service for quotation *',
    interestRequired: true,
    interestOptions: QUOTATION_INTEREST_OPTIONS,
    messageLabel: 'Project scope & requirements *',
    messagePlaceholder:
      'Describe what you need quoted — features, users, timeline, integrations, budget range if known…',
    submitLabel: 'Request Quotation',
  },
  consultation: {
    companyLabel: 'Company / organisation',
    companyPlaceholder: 'Your company or team name',
    interestLabel: 'Topic for consultation',
    interestRequired: false,
    interestOptions: CONSULTATION_INTEREST_OPTIONS,
    messageLabel: 'Your business goals & questions *',
    messagePlaceholder:
      'What challenge are you solving? Preferred day/time for a call? Any products you are considering?',
    submitLabel: 'Book Consultation',
  },
  demo: {
    companyLabel: 'Company name',
    companyPlaceholder: 'Where you work',
    interestLabel: 'Product to demo *',
    interestRequired: true,
    interestOptions: DEMO_PRODUCT_OPTIONS,
    messageLabel: 'Your use case *',
    messagePlaceholder:
      'Which workflows should we show? Your industry, team size, and preferred demo time help us prepare.',
    submitLabel: 'Request Demo',
  },
  enroll: {
    companyLabel: 'College or company',
    companyPlaceholder: 'Optional',
    interestLabel: 'What do you want to join? *',
    interestRequired: true,
    interestOptions: ENROLL_INTEREST_OPTIONS,
    messageLabel: 'Your details *',
    messagePlaceholder:
      'Your qualification, preferred start time, and anything the team should know.',
    submitLabel: 'Enroll now',
  },
  sales: {
    companyLabel: 'Company / organisation',
    companyPlaceholder: 'Your company name',
    interestLabel: 'What can our sales team help with?',
    interestRequired: false,
    interestOptions: [...DEMO_PRODUCT_OPTIONS, ...CONSULTATION_INTEREST_OPTIONS],
    messageLabel: 'How can we help? *',
    messagePlaceholder: 'Tell us what you are looking for and any requirements to know.',
    submitLabel: 'Contact sales',
  },
  general: {
    companyLabel: 'Company / organisation',
    companyPlaceholder: 'Optional',
    interestLabel: 'Area of interest',
    interestRequired: false,
    interestOptions: [...DEMO_PRODUCT_OPTIONS, ...CONSULTATION_INTEREST_OPTIONS],
    messageLabel: 'Your message *',
    messagePlaceholder: 'Tell us a little about what you need.',
    submitLabel: 'Send enquiry',
  },
}

const INTEREST_ALIASES = [
  ['vetri bills', 'Vetri Bills'],
  ['billing', 'Vetri Bills'],
  ['vetri crm', 'Vetri CRM'],
  ['crm', 'Vetri CRM'],
  ['coach ai', 'Coach AI'],
  ['project management', 'Vetri Project Management'],
  ['hr management', 'HR Management Tool'],
  ['website', 'Website Development'],
  ['mobile app', 'Mobile App Development'],
  ['python', 'Training Course'],
  ['course', 'Training Course'],
]

const EMPTY_ENQUIRY_FORM = {
  full_name: '',
  company: '',
  email: '',
  phone: '',
  interest: '',
  message: '',
}

function detectInterestFromChat(text, options) {
  const lowered = (text || '').toLowerCase()
  for (const [needle, value] of INTEREST_ALIASES) {
    if (lowered.includes(needle) && options.includes(value)) {
      return value
    }
  }
  for (const option of options) {
    if (lowered.includes(option.toLowerCase())) {
      return option
    }
  }
  return ''
}

function buildEnquiryPrefill(type, lastUserText) {
  const trimmed = (lastUserText || '').trim()
  if (!trimmed) return ''
  if (type === 'quotation') return `Quotation request: ${trimmed}`
  if (type === 'consultation') return `Consultation about: ${trimmed}`
  if (type === 'demo') return `Demo request: ${trimmed}`
  if (type === 'enroll') return `Enrollment request: ${trimmed}`
  return trimmed
}

function isEnquiryFormEmpty(form) {
  return !form.full_name && !form.company && !form.email && !form.phone && !form.interest && !form.message
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
  ai: 'AI answer',
  verified_kb: 'Verified VIS answer',
  eligibility: 'Eligibility check',
  unverified: 'Limited information',
}

const LOGO_SRC = '/vetriit-logo.webp'

function VisLogo({ size = 36, className = '' }) {
  return (
    <span
      className={`vis-logo vis-logo-image ${className}`.trim()}
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <img src={LOGO_SRC} alt="Vetri IT Systems" width={size} height={size} />
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

function SmileAvatar() {
  return (
    <img src="/coach-ai-avatar.jpg" alt="" className="avatar-photo" />
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
  enquiryCta = null,
  onEnquiryClick,
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
        <span className="avatar avatar-smile" aria-hidden="true">
          <SmileAvatar />
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
                  <span className="attachment-file">{item.name}</span>
                )}
              </div>
            ))}
          </div>
        )}
        <div className="bubble">
          {formatMessage(text)}
          {isBot && enquiryCta && ENQUIRY_CTA_LABELS[enquiryCta] && (
            <div className="bubble-enquiry-cta">
              <button
                type="button"
                className="bubble-enquiry-btn"
                onClick={() => onEnquiryClick?.(enquiryCta)}
              >
                {ENQUIRY_CTA_LABELS[enquiryCta]}
              </button>
            </div>
          )}
        </div>
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
                  Useful
                </button>
                <button
                  type="button"
                  className={`bubble-action-btn ${feedback === 'down' ? 'active' : ''}`}
                  onClick={() => onFeedback(messageId, 'down')}
                  aria-label="Not helpful"
                >
                  Not useful
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
  const fieldConfig = ENQUIRY_FORM_CONFIG[activeType] || ENQUIRY_FORM_CONFIG.quotation

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
            {fieldConfig.companyLabel}
            <input
              value={form.company}
              onChange={(event) => onChange('company', event.target.value)}
              placeholder={fieldConfig.companyPlaceholder}
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
            {fieldConfig.interestLabel}
            <select
              value={form.interest}
              onChange={(event) => onChange('interest', event.target.value)}
              required={fieldConfig.interestRequired}
            >
              <option value="">
                {fieldConfig.interestRequired ? 'Select one' : 'Optional — select a topic'}
              </option>
              {fieldConfig.interestOptions.map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <label>
            {fieldConfig.messageLabel}
            <textarea
              value={form.message}
              onChange={(event) => onChange('message', event.target.value)}
              placeholder={fieldConfig.messagePlaceholder}
              rows={4}
              required
            />
          </label>

          {error && <p className="enquiry-error">{error}</p>}

          <button type="submit" className="btn-green enquiry-submit-btn" disabled={submitting}>
            {submitting ? 'Submitting…' : fieldConfig.submitLabel}
          </button>
        </form>
      </div>
    </div>
  )
}

function SiteNav({ onEnquiry }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const navItems = [
    ['Home', '#home'],
    ['About', '#about'],
    ['Services', '#services'],
    ['Products', '#products'],
    ['Courses', '#courses'],
    ['Portfolios', '#portfolios'],
    ['Why VIS', '#why-vis'],
    ['Contact', '#contact'],
  ]

  function closeMenu() {
    setMenuOpen(false)
  }

  return (
    <header className="site-nav">
      <nav className="site-nav-inner" aria-label="Main navigation" onKeyDown={(event) => {
        if (event.key === 'Escape') closeMenu()
      }}>
        <a href="#home" className="site-brand" onClick={closeMenu} aria-label="Vetri IT Systems home">
          <VisLogo size={48} className="site-logo-mark" />
          <span className="site-brand-copy">
            <span className="site-name">Vetri IT Systems</span>
            <span className="site-sub">Technology with purpose</span>
          </span>
        </a>
        <button
          className={`mobile-menu-toggle ${menuOpen ? 'is-open' : ''}`}
          type="button"
          aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={menuOpen}
          aria-controls="main-navigation-links"
          onClick={() => setMenuOpen((open) => !open)}
        >
          <span />
          <span />
        </button>
        <div id="main-navigation-links" className={`site-nav-links ${menuOpen ? 'is-open' : ''}`}>
          {navItems.map(([label, href]) => (
            <a key={href} href={href} onClick={closeMenu}>{label}</a>
          ))}
        </div>
        <button className="site-cta" type="button" onClick={() => onEnquiry('quotation')}>
          Get a quotation <ArrowIcon />
        </button>
      </nav>
    </header>
  )
}

function SiteFooter({ onEnquiry }) {
  return (
    <footer className="site-footer">
      <div className="site-footer-grid">
        <div className="footer-col footer-brand-col">
          <div className="footer-brand">
            <VisLogo size={46} />
            <strong>Vetri IT Systems</strong>
          </div>
          <p>Enterprise software, applied AI and digital transformation for businesses that intend to lead their category.</p>
        </div>
        <div className="footer-col">
          <strong>Quick Links</strong>
          <a href="#home">Home</a>
          <a href="#about">About</a>
          <a href="#services">Services</a>
          <a href="#courses">Courses</a>
          <a href="#why-vis">Why VIS</a>
          <a href="#contact">Contact</a>
        </div>
        <div className="footer-col">
          <strong>Our Products</strong>
          <a href="#products">Vetri Bills</a>
          <a href="#products">Vetri Files</a>
          <a href="#products">Vetri Project Management</a>
          <a href="#products">Coach AI</a>
          <a href="#products">Vetri AI Assistant</a>
          <a href="#products">Vetri CRM</a>
        </div>
        <div className="footer-col">
          <strong>Talk to our team</strong>
          <a href="tel:+918438154827" className="footer-link">+91 84381 54827</a>
          <a href="mailto:support@vetri-it.com" className="footer-link">support@vetri-it.com</a>
          <button className="footer-contact-btn" type="button" onClick={() => onEnquiry('general')}>
            Start an enquiry <ArrowIcon />
          </button>
        </div>
      </div>
      <div className="site-footer-copy">
        <span>© {new Date().getFullYear()} Vetri IT Systems Pvt Ltd</span>
        <span>Built around your business.</span>
      </div>
    </footer>
  )
}

const SERVICE_LIST = [
  ['Website Development', 'Responsive websites and web applications designed around your business.'],
  ['Mobile App Development', 'Native and cross-platform apps for iOS and Android.'],
  ['Software Development', 'Custom enterprise software, APIs and automation tools.'],
  ['UI/UX Design', 'Research-led interfaces, design systems and usability testing.'],
  ['AI Solutions', 'Models, assistants and agents mapped to real business needs.'],
  ['Generative AI', 'Content, code and document intelligence on secure LLM pipelines.'],
  ['Simplify Operations', 'Connected platforms for billing, HR, projects and customer management.'],
  ['CRM Development', 'Pipeline, quotation and follow-up automation for your sales motion.'],
  ['ERP Development', 'Inventory, production and finance modules shaped to how you operate.'],
  ['Cloud Services', 'Cloud architecture, deployment and managed support.'],
  ['Digital Marketing', 'SEO, social media, search advertising and content strategy.'],
  ['Google Ads', 'Search and performance campaigns tuned for qualified leads.'],
  ['SEO', 'Technical SEO, content strategy and authority building.'],
  ['Meta Ads', 'Creative testing and retargeting across Facebook and Instagram.'],
]

const PRODUCT_LIST = [
  ['Vetri Bills', 'GST Billing & Invoicing', 'GST-ready billing, inventory management, barcode support, POS and sales reporting.'],
  ['Vetri Files', 'Document Management', 'A secure document vault with OCR indexing, permissions, versioning and audit trail.'],
  ['Vetri Project Management', 'Project & Delivery', 'Kanban, Gantt, time tracking, collaboration and automated workflows.'],
  ['Coach AI', 'AI Learning Platform', 'Adaptive coaching that assesses skill gaps and builds learning journeys.'],
  ['Vetri AI Assistant', 'Generative AI', 'A private assistant grounded in company knowledge, ready to answer, draft and act.'],
  ['Vetri CRM', 'Sales & Customer', 'Lead capture, follow-ups, AI-scored pipelines and instant quotations.'],
  ['Vetri Training Management System', 'Training Management', 'Enterprise training management for institutes and teams.'],
  ['HR Management Tool', 'People-first HRMS', 'Employee records, attendance, payroll, leave and performance reviews.'],
]

const COURSE_LIST = [
  'Python Fullstack',
  'Prompt Engineering',
  'Java Fullstack',
  'UI/UX',
  'Software Testing',
  'Data Analytics',
  'Mobile App Development',
  'AWS & DevOps',
  'Data Science',
  'Digital Marketing',
]

const PORTFOLIO_LIST = [
  {
    name: 'Retail POS System',
    type: 'Web + Mobile',
    metric: '+40% Sales Efficiency',
    description: 'Point-of-sale software for a 12-store retail chain across Tamil Nadu, with real-time inventory sync.',
    tech: 'React · Node.js · PostgreSQL',
  },
  {
    name: 'Healthcare Portal',
    type: 'Web App',
    metric: '10K+ Active Users',
    description: 'Appointment booking, telemedicine and electronic health records for a multi-specialty clinic.',
    tech: 'Next.js · WebSocket · AWS',
  },
  {
    name: 'Food Delivery App',
    type: 'Mobile App',
    metric: '50K+ Downloads',
    description: 'Cross-platform ordering with live tracking, multiple payment options and a restaurant dashboard.',
    tech: 'React Native · Firebase · Maps',
  },
  {
    name: 'E-commerce Platform',
    type: 'Full Stack',
    metric: '+60% Conversion Rate',
    description: 'Fashion commerce with product recommendations, secure payments and an analytics dashboard.',
    tech: 'Vue.js · Stripe · Elasticsearch',
  },
]

function ArrowIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M5 12h13M13 6l6 6-6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function SparkIcon() {
  return (
    <svg width="21" height="21" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="m12 2 1.5 7 6.5 3-6.5 2.5L12 22l-1.5-7.5L4 12l6.5-3L12 2Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
      <path d="m19 2 .6 2.4L22 5l-2.4.6L19 8l-.6-2.4L16 5l2.4-.6L19 2Z" fill="currentColor" />
    </svg>
  )
}

function MarketingSite({ onEnquiry, onChat }) {
  return (
    <main className="marketing-site">
      <section className="hero-section" id="home">
        <div className="hero-grid-glow" aria-hidden="true" />
        <div className="hero-inner">
          <div className="hero-copy">
            <div className="hero-eyebrow"><span className="eyebrow-dot" /> AI-FIRST ENTERPRISE TECHNOLOGY <span className="eyebrow-rule" /> TAMIL NADU, INDIA</div>
            <h1>Technology that moves <span>business forward.</span></h1>
            <p className="hero-lede">We build practical software, apply AI where it matters, and help teams make digital transformation real.</p>
            <p className="hero-detail">From custom platforms and mobile applications to enterprise products and career training, Vetri IT Systems brings business thinking and engineering together.</p>
            <div className="hero-actions">
              <button className="btn-primary" type="button" onClick={() => onEnquiry('consultation')}>Book a consultation <ArrowIcon /></button>
              <a className="btn-quiet" href="#services">Explore our services <span className="circle-arrow"><ArrowIcon /></span></a>
            </div>
            <div className="hero-proofline"><span className="proof-mark"><span /></span><span>One accountable partner for software, AI, cloud and growth.</span></div>
          </div>
          <div className="hero-art" aria-label="Abstract layered technology illustration">
            <div className="art-orbit orbit-one" />
            <div className="art-orbit orbit-two" />
            <div className="art-axis axis-one" />
            <div className="art-axis axis-two" />
            <div className="art-core">
              <img src={heroArtwork} alt="" />
              <div className="core-label"><span className="core-label-kicker">VETRI IT SYSTEMS</span><strong>Build for<br />what’s next.</strong><span className="core-label-status"><i /> READY TO BUILD</span></div>
            </div>
            <div className="art-node node-ai"><SparkIcon /><span>Applied AI</span></div>
            <div className="art-node node-cloud"><span className="node-line-icon">↗</span><span>Cloud native</span></div>
            <div className="art-note"><span className="note-label">IDEA → IMPACT</span><span>Connected by design</span></div>
          </div>
        </div>
        <div className="hero-bottomline"><span>ENGINEERING WITH INTENT</span><span className="line-fill" /><span>SOFTWARE · AI · TRAINING</span></div>
      </section>

      <section className="about-section section-pad" id="about">
        <div className="section-container about-layout">
          <div className="about-intro">
            <p className="section-kicker"><span>01</span> ABOUT VETRI IT SYSTEMS</p>
            <h2>Technology built around <span>your business.</span></h2>
            <p className="section-lede">Technology should solve real business problems — not create more complexity.</p>
            <p>We work with businesses to understand their goals, identify the right technology approach and build solutions that are practical, scalable and ready for the future. From custom software and digital applications to AI-powered solutions, we combine technical expertise with a business-first approach.</p>
            <button type="button" className="text-action" onClick={() => onEnquiry('consultation')}>Talk through your next step <ArrowIcon /></button>
          </div>
          <div className="about-side">
            <div className="about-statement"><span className="statement-index">A / 01</span><span className="statement-overline">DIGITAL TRANSFORMATION</span><strong>Process <span>→</span> Platform</strong><small>Move from friction to a clearer way of working.</small></div>
            <div className="about-statement"><span className="statement-index">A / 02</span><span className="statement-overline">APPLIED AI</span><strong>Assistants, agents & automation</strong><small>Put useful intelligence inside everyday workflows.</small></div>
            <div className="about-statement"><span className="statement-index">A / 03</span><span className="statement-overline">ENGINEERING DEPTH</span><strong>Web, mobile, cloud, data</strong><small>Connected systems, made for real operations.</small></div>
            <div className="about-tags"><span>Scalable architecture</span><span>Security minded</span><span>Made in India</span></div>
          </div>
        </div>
        <div className="section-container values-strip">
          <div><span className="value-n">01</span><strong>Enterprise trust</strong><p>Compliance, security and support built into every engagement.</p></div>
          <div><span className="value-n">02</span><strong>Cloud native</strong><p>Scalable architectures on modern cloud infrastructure.</p></div>
          <div><span className="value-n">03</span><strong>Product mindset</strong><p>Enterprise products as well as one-off projects.</p></div>
          <div><span className="value-n">04</span><strong>AI-first engineering</strong><p>Intelligence and automation considered from the start.</p></div>
        </div>
      </section>

      <section className="mission-section">
        <div className="section-container">
          <div className="mission-heading">
            <p className="section-kicker"><span>02</span> MISSION & VISION</p>
            <h2>What drives every line<br />of code we ship.</h2>
          </div>
          <div className="mission-cards">
            <article className="mission-card vision-card">
              <span className="mission-orb"><SparkIcon /></span><span className="mission-label">OUR VISION</span>
              <h3>An AI-powered business for everyone.</h3>
              <p>To become the trusted AI and digital transformation partner for growing enterprises — where every process is automated, every decision is data-backed, and every team is amplified by AI.</p>
            </article>
            <article className="mission-card">
              <span className="mission-orb"><span className="orb-target">◎</span></span><span className="mission-label">OUR MISSION</span>
              <h3>Make enterprise technology effortless.</h3>
              <p>To deliver dependable, intelligent software that removes manual work, gives leaders real-time clarity, and lets businesses of every size compete with the very best.</p>
            </article>
          </div>
        </div>
      </section>

      <section className="products-section section-pad" id="products">
        <div className="section-container">
          <div className="section-heading section-heading-centered">
            <p className="section-kicker"><span>03</span> OUR PRODUCTS</p>
            <h2>Enterprise products.<br /><span>Built for the work.</span></h2>
            <p>Purpose-built software for the operational details that keep a business moving.</p>
          </div>
          <div className="product-grid">
            {PRODUCT_LIST.map(([name, category, description], index) => (
              <article className="product-card" key={name}>
                <div className="product-card-top"><span className="product-index">0{index + 1}</span><span className="product-symbol">{name.slice(0, 1)}</span></div>
                <p className="product-category">{category}</p>
                <h3>{name}</h3>
                <p className="product-description">{description}</p>
                <button type="button" className="card-link" onClick={() => onEnquiry('demo', name)}>Request a demo <ArrowIcon /></button>
              </article>
            ))}
          </div>
          <div className="product-footnote"><span>ONE PRODUCT FAMILY</span><span className="line-fill" /><span>BUILT TO WORK TOGETHER</span></div>
        </div>
      </section>

      <section className="services-section section-pad" id="services">
        <div className="section-container">
          <div className="services-heading">
            <div><p className="section-kicker"><span>04</span> OUR SERVICES</p><h2>End-to-end capability,<br /><span>from idea to scale.</span></h2></div>
            <div className="services-head-aside"><p>One accountable partner across design, engineering, AI, cloud and growth — so your roadmap never stalls between vendors.</p><button type="button" className="text-action" onClick={() => onEnquiry('consultation')}>Explore a project together <ArrowIcon /></button></div>
          </div>
          <div className="service-list">
            {SERVICE_LIST.map(([name, description], index) => (
              <article className="service-item" key={name}>
                <span className="service-index">{String(index + 1).padStart(2, '0')}</span>
                <h3>{name}</h3>
                <p>{description}</p>
                <button type="button" aria-label={`Enquire about ${name}`} onClick={() => onEnquiry('quotation', name)}><ArrowIcon /></button>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="ai-section">
        <div className="section-container ai-layout">
          <div className="ai-copy">
            <p className="section-kicker section-kicker-light"><span>05</span> APPLIED AI</p>
            <h2>Intelligence layered across <span>every business process.</span></h2>
            <p>We design AI systems that are grounded, governed and useful — deployed inside your workflows, not bolted on beside them.</p>
            <button type="button" className="ai-cta" onClick={() => onEnquiry('consultation', 'AI & automation strategy')}>Talk about AI for your business <ArrowIcon /></button>
          </div>
          <div className="ai-diagram">
            <div className="process-line" aria-label="Data to context to model to action to impact">
              {['Data', 'Context', 'Model', 'Action', 'Impact'].map((step, index) => <div className="process-step" key={step}><span>{index + 1}</span><small>{step}</small></div>)}
            </div>
            <div className="ai-capabilities">
              <article><span className="cap-icon">AI</span><strong>Generative AI</strong><p>Content, code and document intelligence built on secure LLM pipelines.</p></article>
              <article><span className="cap-icon">01</span><strong>AI assistants</strong><p>Knowledge-led assistants designed around your systems and teams.</p></article>
              <article><span className="cap-icon">↗</span><strong>Workflow automation</strong><p>Reduce repetitive work and connect hand-offs across processes.</p></article>
            </div>
            <div className="ai-side-note"><span>GROUND</span><span>GOVERN</span><span>DEPLOY</span></div>
          </div>
        </div>
      </section>

      <section className="courses-section section-pad" id="courses">
        <div className="section-container course-layout">
          <div className="course-intro">
            <p className="section-kicker"><span>06</span> VIS ACADEMY</p>
            <h2>Build skills for <span>what comes next.</span></h2>
            <p className="section-lede">Practical training programmes designed to help learners move forward with confidence.</p>
            <div className="course-facts">
              <div><strong>180 days</strong><span>Course duration</span></div>
              <div><strong>3 months</strong><span>Internship included</span></div>
              <div><strong>Any degree</strong><span>Eligibility requirement</span></div>
            </div>
            <button type="button" className="btn-primary" onClick={() => onEnquiry('enroll')}>Ask about enrolment <ArrowIcon /></button>
            <small className="course-note">Course fees are shared by the team. No fixed fee is listed here.</small>
          </div>
          <div className="course-panel">
            <div className="course-panel-head"><span>AVAILABLE PROGRAMMES</span><span>10 TRACKS</span></div>
            <div className="course-list">
              {COURSE_LIST.map((course, index) => (
                <button type="button" key={course} onClick={() => onEnquiry('enroll', course)}>
                  <span className="course-row-index">{String(index + 1).padStart(2, '0')}</span><span>{course}</span><ArrowIcon />
                </button>
              ))}
            </div>
            <div className="course-panel-foot">Explore your options with the VIS team.</div>
          </div>
        </div>
      </section>

      <section className="portfolio-section section-pad" id="portfolios">
        <div className="section-container">
          <div className="portfolio-heading">
            <div><p className="section-kicker"><span>07</span> SELECTED PORTFOLIO</p><h2>Work that makes<br /><span>business move.</span></h2></div>
            <p>Selected project examples from the VIS portfolio.</p>
          </div>
          <div className="portfolio-grid">
            {PORTFOLIO_LIST.map((project, index) => (
              <article className={`portfolio-card portfolio-card-${index + 1}`} key={project.name}>
                <div className="portfolio-visual">
                  <span className="portfolio-type">{project.type}</span>
                  <div className="portfolio-screen"><div className="screen-top"><i /><i /><i /><span>VIS / PROJECT</span></div><div className="screen-content"><span className="screen-small-line" /><span className="screen-large-line" /><span className="screen-large-line short" /><div className="screen-bars"><i /><i /><i /><i /><i /></div></div></div>
                  <span className="portfolio-count">0{index + 1} / 04</span>
                </div>
                <div className="portfolio-copy">
                  <span className="portfolio-result">{project.metric}</span><h3>{project.name}</h3><p>{project.description}</p><span className="portfolio-tech">{project.tech}</span>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="why-section section-pad" id="why-vis">
        <div className="section-container why-layout">
          <div className="why-aside"><p className="section-kicker"><span>08</span> WHY VIS</p><span className="why-aside-line" /><span className="why-aside-note">THE PARTNER<br />BEHIND THE PLATFORM</span></div>
          <div className="why-main">
            <h2>Good technology is more than the code. It’s <span>how it works for you.</span></h2>
            <p className="why-lede">A practical technology partner for businesses ready to make a meaningful next move.</p>
            <div className="why-points">
              <article><span>01</span><div><h3>Business-first thinking</h3><p>We start with your goals and processes, then match the technology to the problem.</p></div><span className="why-mark">↗</span></article>
              <article><span>02</span><div><h3>One connected team</h3><p>Design, software, AI and digital growth under one partner.</p></div><span className="why-mark">↗</span></article>
              <article><span>03</span><div><h3>Products and custom builds</h3><p>Choose a ready-to-use VIS product or build around your specific operation.</p></div><span className="why-mark">↗</span></article>
              <article><span>04</span><div><h3>Support beyond launch</h3><p>Work with a team that can keep developing and supporting your solution.</p></div><span className="why-mark">↗</span></article>
            </div>
            <button type="button" className="btn-primary" onClick={() => onEnquiry('consultation')}>Let’s talk about your goals <ArrowIcon /></button>
          </div>
        </div>
      </section>

      <section className="contact-section section-pad" id="contact">
        <div className="section-container">
          <div className="contact-heading"><p className="section-kicker"><span>09</span> GET IN TOUCH</p><h2>Let’s scope your next <span>transformation.</span></h2><p>Tell us what you’re trying to achieve. The VIS team will help you find a practical next step.</p></div>
          <div className="contact-grid">
            <div className="contact-form-card">
              <div className="contact-form-top"><span>START A CONVERSATION</span><span className="contact-top-line" /></div>
              <h3>Where should we begin?</h3>
              <p>Share your goals with our team — whether you’re exploring a product, a custom build, or training.</p>
              <div className="contact-choices">
                <button type="button" onClick={() => onEnquiry('quotation')}>Request a quotation <ArrowIcon /></button>
                <button type="button" onClick={() => onEnquiry('consultation')}>Book a consultation <ArrowIcon /></button>
                <button type="button" onClick={() => onEnquiry('demo')}>Request a product demo <ArrowIcon /></button>
                <button type="button" onClick={() => onEnquiry('enroll')}>Ask about courses <ArrowIcon /></button>
              </div>
              <button className="contact-submit" type="button" onClick={() => onEnquiry('general')}>Send an enquiry <ArrowIcon /></button>
              <small>Every enquiry is sent securely to the Vetri IT Systems team.</small>
            </div>
            <aside className="contact-details">
              <span className="contact-details-kicker">DIRECT CONTACT</span>
              <h3>Talk to our team.</h3>
              <p>Speak directly with a solution consultant — no call centres, no scripts.</p>
              <a href="tel:+918438154827"><span className="contact-icon">T</span><span><small>CALL US</small><strong>+91 84381 54827</strong></span><ArrowIcon /></a>
              <a href="mailto:support@vetri-it.com"><span className="contact-icon">@</span><span><small>EMAIL</small><strong>support@vetri-it.com</strong></span><ArrowIcon /></a>
              <div className="contact-address"><span className="contact-icon">V</span><span><small>VISIT</small><strong>Vetri Academy, Aerial Complex,<br />Behind Bus Stand, Surandai</strong></span></div>
              <button type="button" className="chat-invite" onClick={onChat}><span className="chat-invite-indicator" /><span>Prefer a quick answer?</span><strong>Ask Coach AI <ArrowIcon /></strong></button>
            </aside>
          </div>
        </div>
      </section>
    </main>
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
          Tap a chat below to continue it, or use + New chat for a fresh conversation.
        </footer>
      </aside>
    </>
  )
}

function App() {
  const [messages, setMessages] = useState([])
  const [conversationId, setConversationId] = useState('')
  const [input, setInput] = useState('')
  const [pendingAttachments, setPendingAttachments] = useState([])
  const [isListening, setIsListening] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [historyList, setHistoryList] = useState([])
  const [widgetOpen, setWidgetOpen] = useState(IS_EMBED ? EMBED_HOST_WIDGET : false)
  const [historyOpen, setHistoryOpen] = useState(false)
  const [apiStatus, setApiStatus] = useState('checking')
  const [followUps, setFollowUps] = useState([])
  const [enquiryCta, setEnquiryCta] = useState('')
  const [enquiryOpen, setEnquiryOpen] = useState(false)
  const [enquiryType, setEnquiryType] = useState('quotation')
  const [enquiryForm, setEnquiryForm] = useState(EMPTY_ENQUIRY_FORM)
  const [enquirySubmitting, setEnquirySubmitting] = useState(false)
  const [enquiryError, setEnquiryError] = useState('')
  const [siteNotice, setSiteNotice] = useState('')
  const bottomRef = useRef(null)
  const abortRef = useRef(null)
  const fileInputRef = useRef(null)
  const speechRef = useRef(null)
  const voiceSupported = Boolean(SPEECH_RECOGNITION)

  const loadHistoryList = useCallback(async () => {
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
  }, [])

  const bootstrapChat = useCallback(async () => {
    await loadHistoryList()
    removeStoredItem(CONVERSATION_ID_KEY)
    setConversationId('')
    setMessages([])
    setFollowUps([])
    setError('')
  }, [loadHistoryList])

  useEffect(() => {
    document.documentElement.classList.toggle('embed', IS_EMBED)
    document.body.classList.toggle('embed', IS_EMBED)
    document.documentElement.classList.toggle('embed-host', IS_EMBED && EMBED_HOST_WIDGET)
    document.body.classList.toggle('embed-host', IS_EMBED && EMBED_HOST_WIDGET)
    return () => {
      document.documentElement.classList.remove('embed', 'embed-host')
      document.body.classList.remove('embed', 'embed-host')
    }
  }, [])

  useEffect(() => {
    if (IS_EMBED) return
    const timer = window.setTimeout(() => {
      void bootstrapChat()
    }, 0)
    return () => window.clearTimeout(timer)
  }, [bootstrapChat])

  useEffect(() => {
    if (EMBED_PAUSED || !IS_EMBED || !widgetOpen) return
    const timer = window.setTimeout(() => {
      void bootstrapChat()
    }, 0)
    return () => window.clearTimeout(timer)
  }, [bootstrapChat, widgetOpen])

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
    if (IS_EMBED && EMBED_PAUSED) return
    const initialCheck = window.setTimeout(() => {
      void checkHealth()
    }, 0)
    const timer = window.setInterval(() => {
      void checkHealth({ retries: 1, delayMs: 0 })
    }, 60000)
    return () => {
      window.clearTimeout(initialCheck)
      window.clearInterval(timer)
    }
  }, [checkHealth])

  function rememberConversation(id) {
    setConversationId(id)
    setStoredItem(CONVERSATION_ID_KEY, id)
  }

  function closeEmbedWidget() {
    setWidgetOpen(false)
    if (EMBED_HOST_WIDGET && window.parent !== window) {
      window.parent.postMessage({ type: 'coach-ai-close' }, '*')
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
      setMessages(loaded.length ? loaded : [])
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
    setMessages([])
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

      await loadHistoryList()
      if (wasActive) {
        newChat()
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

  function handleEnquiryTypeChange(type) {
    const config = ENQUIRY_FORM_CONFIG[type]
    setEnquiryType(type)
    if (!config) return
    setEnquiryForm((prev) => {
      const interestValid = config.interestOptions.includes(prev.interest)
      return interestValid ? prev : { ...prev, interest: '' }
    })
  }

  function openEnquiry(type = 'general', desiredInterest = '') {
    const activeType = ENQUIRY_TYPE_TABS.some((tab) => tab.type === type) ? type : 'quotation'
    const config = ENQUIRY_FORM_CONFIG[activeType]
    setEnquiryType(activeType)
    setEnquiryError('')

    const lastUser = [...messages].reverse().find((item) => item.role === 'user')
    const chatContext = lastUser?.text || ''

    setEnquiryForm((prev) => {
      if (!isEnquiryFormEmpty(prev)) {
        const interestValid = config.interestOptions.includes(prev.interest)
        if (config.interestOptions.includes(desiredInterest)) {
          return { ...prev, interest: desiredInterest }
        }
        return interestValid ? prev : { ...prev, interest: '' }
      }
      const detectedInterest = detectInterestFromChat(chatContext, config.interestOptions)
      return {
        ...EMPTY_ENQUIRY_FORM,
        interest: config.interestOptions.includes(desiredInterest) ? desiredInterest : detectedInterest,
        message: buildEnquiryPrefill(activeType, chatContext),
      }
    })
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
      setSiteNotice(data.confirmation || 'Thank you. Your enquiry has been submitted.')
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
    if (messages.length === 0) {
      setError('Send a message first, then use Export to download this chat.')
      return
    }
    const transcript = messages
      .map((msg) => `${msg.role === 'user' ? 'You' : 'Coach AI'}:\n${msg.text}`)
      .join('\n\n')
    const blob = new Blob([transcript], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `coach-ai-chat-${new Date().toISOString().slice(0, 10)}.txt`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.setTimeout(() => URL.revokeObjectURL(url), 1000)
    setError('')
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

  if (IS_EMBED && EMBED_PAUSED) {
    return (
      <div className="widget-root widget-root-host" style={{ padding: 24 }}>
        <p style={{ margin: 0, color: '#0c1e3d', fontWeight: 700 }}>Coach AI embed is paused</p>
        <p style={{ margin: '8px 0 0', color: '#4b5563', fontSize: 14, lineHeight: 1.5 }}>
          The website button is turned off until the mentor review so it does not use the daily AI quota.
          Use the main chat page for the demo.
        </p>
        </div>
    )
  }

  return (
    <div
      className={
        IS_EMBED
          ? `widget-root${EMBED_HOST_WIDGET ? ' widget-root-host' : ''}`
          : 'page'
      }
    >
      {!IS_EMBED && (
        <>
          <SiteNav onEnquiry={openEnquiry} />
          <MarketingSite onEnquiry={openEnquiry} onChat={() => setWidgetOpen(true)} />
          <SiteFooter onEnquiry={openEnquiry} />
        </>
      )}
      {siteNotice && !IS_EMBED && (
        <div className="site-notice" role="status">
          <span className="notice-check" aria-hidden="true">✓</span>
          <span>{siteNotice}</span>
          <button type="button" onClick={() => setSiteNotice('')} aria-label="Dismiss enquiry confirmation">×</button>
        </div>
      )}

      {!widgetOpen && (
        <div className="widget-root">
        <button
          type="button"
          className="launcher"
          onClick={() => setWidgetOpen(true)}
          aria-label="Open Coach AI"
          aria-haspopup="dialog"
        >
          <span className="launcher-pulse" aria-hidden="true" />
          <ChatIcon />
          <span className="launcher-label">Coach AI</span>
        </button>
        </div>
      )}

      {widgetOpen && (
        <div className={`${IS_EMBED ? `widget-root${EMBED_HOST_WIDGET ? ' widget-root-host' : ''}` : 'widget-chat-root'}`}>
        <div className={`app ${IS_EMBED ? 'app-embed' : 'app-widget'}`} role={!IS_EMBED ? 'dialog' : undefined} aria-modal={!IS_EMBED ? 'false' : undefined} aria-label={!IS_EMBED ? 'Coach AI chat' : undefined}>
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
              {!EMBED_HOST_WIDGET && (
                <button type="button" className="ghost icon-btn" onClick={closeEmbedWidget} aria-label="Close Coach AI">
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
                      Ask me about VIS products, services, training, or company info.
                      For a quote, consultation, or demo, use the <strong>Enquiry</strong> button above.
                    </p>
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
                    enquiryCta={
                      msg.role === 'bot' && index === lastBotIndex && !loading
                        ? enquiryCta
                        : null
                    }
                    onEnquiryClick={openEnquiry}
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
                    <span className="avatar avatar-smile" aria-hidden="true">
                      <SmileAvatar />
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
                        <span className="composer-attachment-name">{item.name}</span>
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
        </div>
      )}

      {!widgetOpen && !IS_EMBED && <span className="chat-launcher-hint" aria-hidden="true">Need a quick answer? Talk with Coach AI.</span>}

      <EnquiryModal
        open={enquiryOpen}
        enquiryType={enquiryType}
        form={enquiryForm}
        onChange={updateEnquiryField}
        onTypeChange={handleEnquiryTypeChange}
        onClose={closeEnquiry}
        onSubmit={submitEnquiryForm}
        submitting={enquirySubmitting}
        error={enquiryError}
      />
    </div>
  )
}

export default App
