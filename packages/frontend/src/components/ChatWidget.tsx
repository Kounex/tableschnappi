import { useState, useEffect, useRef, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import { ChevronRight, MessageSquare, X, Send, Bot, ThumbsUp, ThumbsDown, Users, Clock, Cloud, Play, Square, UtensilsCrossed, RotateCcw } from 'lucide-react'
import { ToolCallInfo } from '../types'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  traceId?: string
  traceUrl?: string
  prompt?: { status: string; version?: string }
  ratingError?: string
  ratingPending?: boolean
  rated?: boolean
  toolCalls?: ToolCallInfo[]
}

const TOOL_LABELS: Record<string, string> = {
  check_availability: 'Checking availability',
  get_wait_time: 'Checking wait time',
  make_reservation: 'Making reservation',
  modify_reservation: 'Modifying reservation',
  list_restaurants: 'Listing restaurants',
  get_restaurant_status: 'Getting restaurant status',
  get_menu: 'Fetching menu',
  find_alternative_restaurant: 'Finding alternatives',
}

const DEMO_CHIPS = [
  { label: 'I would like to book a table.', icon: Users },
  { label: 'Which vegetarian main dishes are on your menu? Please check the menu.', icon: UtensilsCrossed },
  { label: 'Exactly how many fresh truffles are left in your kitchen right now?', icon: UtensilsCrossed },
  { label: 'What is the current wait time? Please check.', icon: Clock },
  { label: "What's the weather?", icon: Cloud, hint: 'Guardrail demo' },
]

const DEMO_SCRIPT = [
  'Hi, table for 4 at 7pm please',
  "What's on your menu?",
  "What's the weather like?",
]

function ToolCallCard({ tc, index }: { tc: ToolCallInfo; index: number }) {
  const [expanded, setExpanded] = useState(false)
  const label = TOOL_LABELS[tc.name] || tc.name

  let parsedResult: unknown = null
  try { parsedResult = JSON.parse(tc.result) } catch { parsedResult = tc.result }

  return (
    <div className="tool-slide-in bg-jp-bg/60 border border-jp-border/60 rounded-lg px-2.5 py-1.5 text-xs"
      style={{ animationDelay: `${index * 120}ms` }}>
      <button onClick={() => setExpanded(!expanded)} className="flex items-center gap-1.5 w-full text-left">
        <span style={{ color: '#00f0ff' }}>&#9881;</span>
        <span style={{ color: '#00f0ff' }} className="font-medium font-mono">{label}</span>
        {Object.keys(tc.args).length > 0 && (
          <span className="text-jp-muted ml-auto">
            {Object.entries(tc.args).map(([k, v]) => `${k}: ${v}`).join(', ')}
          </span>
        )}
        <ChevronRight size={10} className={`text-jp-muted transition-transform flex-shrink-0 ${expanded ? 'rotate-90' : ''}`} />
      </button>
      {expanded && (
        <pre className="mt-1.5 text-jp-muted overflow-x-auto whitespace-pre-wrap break-words text-[10px] max-h-32 overflow-y-auto">
          {typeof parsedResult === 'string' ? parsedResult : JSON.stringify(parsedResult, null, 2)}
        </pre>
      )}
    </div>
  )
}

const markdownComponents = {
  p: ({ children }: { children?: React.ReactNode }) => <p className="mb-1.5 last:mb-0">{children}</p>,
  ul: ({ children }: { children?: React.ReactNode }) => <ul className="list-disc pl-4 mb-1.5 space-y-0.5">{children}</ul>,
  ol: ({ children }: { children?: React.ReactNode }) => <ol className="list-decimal pl-4 mb-1.5 space-y-0.5">{children}</ol>,
  strong: ({ children }: { children?: React.ReactNode }) => <strong className="font-bold">{children}</strong>,
  code: ({ children }: { children?: React.ReactNode }) => <code className="bg-black/10 rounded px-1 py-0.5 text-xs">{children}</code>,
  a: ({ children, href }: { children?: React.ReactNode; href?: string }) => (
    <a href={href} target="_blank" rel="noreferrer" className="underline text-jp-red">{children}</a>
  ),
}

// `table` is set when the widget is mounted from a QR-code menu page. It is
// forwarded with every turn so MLflow traces record which table asked.
export function ChatWidget({ slug, initialOpen, table }: { slug: string; initialOpen?: boolean; table?: number }) {
  const [open, setOpen] = useState(initialOpen ?? false)
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: 'Welcome to Sakura! I can check availability, browse the menu, or book a table for you. How can I help?' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [demoRunning, setDemoRunning] = useState(false)
  const [modelName, setModelName] = useState('')
  const demoRef = useRef(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const sessionId = useRef(crypto.randomUUID())
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetch('/api/assistant/health').then(r => r.json())
      .then(data => setModelName(data.modelName ?? '')).catch(() => {})
  }, [])

  const newChat = () => {
    if (loading || demoRunning) return
    sessionId.current = crypto.randomUUID()
    setMessages([{ role: 'assistant', content: 'Welcome! What would you like to know about the restaurant?' }])
    setInput('')
  }

  const sendRef = useRef<((text: string) => void) | null>(null)

  useEffect(() => {
    setMessages([
      { role: 'assistant', content: `Welcome! I can check availability, browse the menu, or book a table for you. How can I help?` }
    ])
    sessionId.current = crypto.randomUUID()
  }, [slug])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const send = useCallback(async (overrideText?: string) => {
    const text = (overrideText ?? input).trim()
    if (!text || loading) return
    if (!overrideText) setInput('')

    const userMsg: ChatMessage = { role: 'user', content: text }
    const next = [...messages, userMsg]
    setMessages(next)
    setLoading(true)

    try {
      const res = await fetch(`/api/restaurants/${slug}/assistant`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: next, sessionId: sessionId.current }),
      })
      const data = await res.json() as { response?: string; error?: string; traceId?: string; traceUrl?: string; prompt?: ChatMessage['prompt']; toolCalls?: ToolCallInfo[] }
      const content = data.response ?? data.error ?? 'Sorry, something went wrong.'
      setMessages(prev => [...prev, {
        role: 'assistant',
        content,
        traceId: data.traceId,
        traceUrl: data.traceUrl,
        prompt: data.prompt,
        toolCalls: data.toolCalls,
      }])
      window.dispatchEvent(new CustomEvent('chat-response', { detail: { response: content } }))
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection error. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }, [input, loading, messages, slug])

  sendRef.current = (text: string) => send(text)

  useEffect(() => {
    const handler = (e: Event) => {
      setOpen(true)
      const msg = (e as CustomEvent).detail?.message
      if (msg) setTimeout(() => sendRef.current?.(msg), 50)
    }
    window.addEventListener('open-chat', handler)
    return () => window.removeEventListener('open-chat', handler)
  }, [])

  const runDemoScript = useCallback(async () => {
    if (demoRunning) {
      demoRef.current = false
      setDemoRunning(false)
      return
    }

    demoRef.current = true
    sessionId.current = crypto.randomUUID()
    setDemoRunning(true)
    setMessages([
      { role: 'assistant', content: 'Welcome! I can check availability, browse the menu, or book a table for you. How can I help?' }
    ])

    for (const line of DEMO_SCRIPT) {
      if (!demoRef.current) break

      for (let i = 0; i <= line.length; i++) {
        if (!demoRef.current) break
        setInput(line.slice(0, i))
        await new Promise(r => setTimeout(r, 35))
      }
      if (!demoRef.current) break

      await new Promise(r => setTimeout(r, 300))
      setInput('')
      const userMsg: ChatMessage = { role: 'user', content: line }

      await new Promise<void>((resolve) => {
        setMessages(prev => {
          const next = [...prev, userMsg]
          setLoading(true)
          fetch(`/api/restaurants/${slug}/assistant`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages: next, sessionId: sessionId.current, ...(table !== undefined && { table }) }),
          })
            .then(r => r.json())
            .then((data: { response?: string; error?: string; traceId?: string; traceUrl?: string; prompt?: ChatMessage['prompt']; toolCalls?: ToolCallInfo[] }) => {
              setMessages(p => [...p, {
                role: 'assistant',
                content: data.response ?? data.error ?? 'Sorry, something went wrong.',
                traceId: data.traceId,
                traceUrl: data.traceUrl,
                prompt: data.prompt,
                toolCalls: data.toolCalls,
              }])
              setLoading(false)
              setTimeout(resolve, 1500)
            })
            .catch(() => {
              setMessages(p => [...p, { role: 'assistant', content: 'Connection error.' }])
              setLoading(false)
              resolve()
            })
          return next
        })
      })
    }

    demoRef.current = false
    setDemoRunning(false)
  }, [demoRunning, slug])

  const handleChip = (text: string) => {
    setOpen(true)
    setTimeout(() => {
      setInput(text)
      setTimeout(() => send(text), 100)
    }, 300)
  }

  const showChips = messages.length <= 1 && !loading

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full flex items-center justify-center transition-all"
        style={{
          background: 'linear-gradient(135deg, #ff2d75, #9d4edd)',
          boxShadow: '0 0 20px rgba(255,45,117,0.4), 0 0 40px rgba(255,45,117,0.1)',
        }}
        title="AI Reservation Assistant">
        {open ? <X size={22} className="text-white" /> : <MessageSquare size={22} className="text-white" />}
      </button>

      {/* Chat panel */}
      {open && (
        <div className="fixed bottom-24 right-6 z-50 w-80 sm:w-96 bg-jp-surface rounded-2xl flex flex-col overflow-hidden animate-slide-up"
          style={{ maxHeight: '70vh', border: '1px solid rgba(255,45,117,0.3)', boxShadow: '0 0 30px rgba(255,45,117,0.15), 0 0 60px rgba(157,78,221,0.05)' }}>
          {/* Header */}
          <div className="px-4 py-3 flex items-center gap-3" style={{ background: 'linear-gradient(135deg, #ff2d75, #9d4edd)' }}>
            <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center" style={{ boxShadow: '0 0 10px rgba(255,255,255,0.15)' }}>
              <Bot size={16} className="text-white" />
            </div>
            <div className="flex-1">
              <p className="text-white font-bold text-sm leading-tight font-mono">AI_HOST</p>
              <p className="text-white/70 text-xs font-mono">OpenShift AI{modelName ? ` // ${modelName}` : ''}</p>
            </div>
            <button onClick={newChat} disabled={loading || demoRunning} title="New chat"
              className="text-white disabled:opacity-40"><RotateCcw size={15} /></button>
            <button onClick={runDemoScript}
              title={demoRunning ? 'Stop demo' : 'Auto-run demo'}
              className="w-7 h-7 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors">
              {demoRunning ? <Square size={12} className="text-white" /> : <Play size={12} className="text-white ml-0.5" />}
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {messages.map((msg, i) => (
              <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                {/* Tool call cards */}
                {msg.role === 'assistant' && msg.toolCalls && msg.toolCalls.length > 0 && (
                  <div className="flex w-full mb-1.5">
                    <div className="w-6 mr-2 flex-shrink-0" />
                    <div className="max-w-[80%] space-y-1">
                      {msg.toolCalls.map((tc, j) => <ToolCallCard key={j} tc={tc} index={j} />)}
                    </div>
                  </div>
                )}
                <div className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} w-full`}>
                  {msg.role === 'assistant' && (
                    <div className="w-6 h-6 rounded-full flex items-center justify-center mr-2 flex-shrink-0 mt-0.5" style={{ background: 'rgba(157,78,221,0.2)' }}>
                      <Bot size={12} style={{ color: '#9d4edd' }} />
                    </div>
                  )}
                  <div className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm ${
                    msg.role === 'user'
                      ? 'text-white rounded-tr-sm'
                      : 'bg-jp-card text-jp-text rounded-tl-sm'
                  }`}
                    style={msg.role === 'user'
                      ? { background: 'linear-gradient(135deg, #ff2d75, #9d4edd)' }
                      : { border: '1px solid rgba(0,240,255,0.15)' }
                    }>
                    {msg.role === 'assistant'
                      ? <ReactMarkdown components={markdownComponents}>{msg.content}</ReactMarkdown>
                      : msg.content}
                  </div>
                </div>
                {/* Rating + trace link */}
                {msg.role === 'assistant' && msg.traceId && (
                  <div className="flex gap-1 ml-8 mt-1 items-center">
                    {!msg.rated ? (
                      <>
                        {[{ score: 1, icon: <ThumbsUp size={11} />, label: 'Good' },
                          { score: 0, icon: <ThumbsDown size={11} />, label: 'Bad' }].map(({ score, icon, label }) => (
                          <button key={score} title={label}
                            disabled={msg.ratingPending}
                            onClick={async () => {
                              setMessages(prev => prev.map(m => m.traceId === msg.traceId ? { ...m, ratingPending: true, ratingError: undefined } : m))
                              try {
                                const response = await fetch(`/api/restaurants/${slug}/assistant/feedback`, {
                                  method: 'POST',
                                  headers: { 'Content-Type': 'application/json' },
                                  body: JSON.stringify({ traceId: msg.traceId, score }),
                                })
                                const data = await response.json()
                                if (!response.ok || !data.ok) throw new Error('Feedback was not saved')
                                setMessages(prev => prev.map(m => m.traceId === msg.traceId ? { ...m, rated: true, ratingPending: false } : m))
                              } catch {
                                setMessages(prev => prev.map(m => m.traceId === msg.traceId ? { ...m, ratingPending: false, ratingError: 'Feedback was not saved. Please retry.' } : m))
                              }
                            }}
                            className="flex items-center gap-1 text-jp-muted hover:text-jp-text bg-jp-border/40 hover:bg-jp-border rounded-full px-2 py-0.5 text-xs transition-colors">
                            {icon}
                          </button>
                        ))}
                      </>
                    ) : (
                      <p className="text-xs text-jp-muted">Thanks for the feedback</p>
                    )}
                    {msg.traceUrl ? (
                      <a href={msg.traceUrl} target="_blank" rel="noopener noreferrer" className="text-xs underline ml-1">Open trace</a>
                    ) : <span className="text-[9px] text-jp-muted ml-1" title={msg.traceId}>Trace ID: {msg.traceId}</span>}
                  </div>
                )}
                {msg.prompt && <p className="text-xs text-jp-muted ml-8 mt-1">
                  {msg.prompt.status === 'registry' ? `Prompt v${msg.prompt.version}` : msg.prompt.status === 'fallback' ? 'Built-in prompt fallback' : 'Prompt not used'}
                </p>}
                {msg.ratingError && <p role="alert" className="text-xs text-red-700 ml-8 mt-1">{msg.ratingError}</p>}
              </div>
            ))}

            {loading && (
              <div className="flex justify-start items-start">
                <div className="w-6 h-6 rounded-full flex items-center justify-center mr-2 flex-shrink-0" style={{ background: 'rgba(157,78,221,0.2)' }}>
                  <Bot size={12} style={{ color: '#9d4edd' }} />
                </div>
                <div className="bg-jp-card rounded-2xl rounded-tl-sm px-4 py-2.5 flex items-center gap-2" style={{ border: '1px solid rgba(0,240,255,0.15)' }}>
                  <span className="text-jp-muted text-xs font-mono">Processing</span>
                  <div className="flex gap-1">
                    {[0, 1, 2].map(i => (
                      <div key={i} className="w-1.5 h-1.5 rounded-full bg-jp-muted animate-bounce"
                        style={{ animationDelay: `${i * 150}ms` }} />
                    ))}
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Suggested chips */}
          {showChips && (
            <div className="px-3 pb-2 flex gap-1.5 flex-wrap">
              {DEMO_CHIPS.map(chip => (
                <button key={chip.label} onClick={() => handleChip(chip.label)}
                  className="flex items-center gap-1 text-xs bg-jp-card text-jp-muted hover:text-jp-text rounded-full px-2.5 py-1 transition-colors"
                  style={{ border: '1px solid #2a2a3e' }}
                  onMouseEnter={e => e.currentTarget.style.border = '1px solid rgba(255,45,117,0.4)'}
                  onMouseLeave={e => e.currentTarget.style.border = '1px solid #2a2a3e'}>
                  <chip.icon size={10} />
                  {chip.label}
                  {'hint' in chip && chip.hint && (
                    <span className="text-[9px] ml-0.5" style={{ color: '#ff8a4c' }}>({chip.hint})</span>
                  )}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="p-3 border-t border-jp-border flex gap-2">
            <input
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
              placeholder="Ask about availability, reservations..."
              className="flex-1 bg-jp-bg rounded-xl px-3 py-2 text-jp-text text-sm focus:outline-none"
              style={{ border: '1px solid #2a2a3e' }}
              onFocus={e => e.target.style.border = '1px solid rgba(255,45,117,0.5)'}
              onBlur={e => e.target.style.border = '1px solid #2a2a3e'}
            />
            <button
              onClick={() => send()}
              disabled={!input.trim() || loading}
              className="w-9 h-9 rounded-xl disabled:opacity-40 flex items-center justify-center transition-colors flex-shrink-0"
              style={{ background: 'linear-gradient(135deg, #ff2d75, #9d4edd)' }}>
              <Send size={15} className="text-white" />
            </button>
          </div>
        </div>
      )}
    </>
  )
}

export { DEMO_CHIPS }
export type { ChatMessage }
