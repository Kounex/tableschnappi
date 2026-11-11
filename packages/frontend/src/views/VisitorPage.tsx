import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Clock, Users, MapPin, Phone, ChevronDown, Calendar, CheckCircle, Bot, Star, X, DollarSign, Shield, ShieldCheck, ShieldAlert, AlertTriangle, Zap } from 'lucide-react'
import { api } from '../api'
import { Restaurant, Table, MenuItem, WaitEstimate } from '../types'
import { SekkiWidget } from '../components/SekkiWidget'
import { ChatWidget, DEMO_CHIPS } from '../components/ChatWidget'
import { AttackDemo } from '../components/AttackDemo'

const HOURS: Record<string, string> = {
  'Mon-Thu': '11:30 - 14:00, 17:30 - 22:00',
  'Fri-Sat': '11:30 - 14:00, 17:30 - 23:00',
  'Sunday': '12:00 - 21:00',
}

const TAGLINES: Record<string, string> = {
  sakura: 'Elegant omakase & seasonal Japanese fine dining',
  koi: 'Underground ramen bar — loud bowls, late nights',
}

const KANJI_WATERMARK: Record<string, string> = { sakura: '桜', koi: '鯉' }

const RESTAURANT_VIBE: Record<string, { accent: string; accentGlow: string; icon: string; subtitle: string }> = {
  sakura: { accent: '#ff9ecf', accentGlow: 'rgba(255,158,207,0.3)', icon: '🌸', subtitle: 'Cherry Blossom Dining' },
  koi: { accent: '#00c6ff', accentGlow: 'rgba(0,198,255,0.3)', icon: '🐟', subtitle: 'Neon Ramen Underground' },
}

function ConfidenceBadge({ confidence }: { confidence: WaitEstimate['confidence'] }) {
  const map = { low: { label: '~', color: '#ff8a4c' }, medium: { label: '≈', color: '#ffd700' }, high: { label: '✓', color: '#00f0ff' } }
  const c = map[confidence]
  return <span className="text-xs font-semibold" style={{ color: c.color }}>{c.label} {confidence}</span>
}

const FOOD_ART: Record<string, { emoji: string; steam?: boolean }> = {
  'Tonkotsu Ramen': { emoji: '🍜', steam: true },
  'Chicken Katsu Curry': { emoji: '🍛', steam: true },
  'Salmon Teriyaki': { emoji: '🐟' },
  'Vegetable Udon': { emoji: '🍜', steam: true },
  'Chirashi Bowl': { emoji: '🍣' },
  'Edamame': { emoji: '🫛' },
  'Gyoza (6 pcs)': { emoji: '🥟' },
  'Takoyaki (6 pcs)': { emoji: '🐙' },
  'Miso Soup': { emoji: '🥣', steam: true },
  'Mochi Ice Cream (3 pcs)': { emoji: '🍡' },
  'Matcha Tiramisu': { emoji: '🍰' },
  'Matcha Latte': { emoji: '🍵', steam: true },
  'Yuzu Lemonade': { emoji: '🍋' },
  'Sapporo Beer': { emoji: '🍺' },
  'Jasmine Tea': { emoji: '🍵', steam: true },
  'Sake Selection': { emoji: '🍶' },
  'Shoyu Ramen': { emoji: '🍜', steam: true },
  'Spicy Miso Ramen': { emoji: '🌶️', steam: true },
  'Green Tea': { emoji: '🍵', steam: true },
}

function NeonBowlArt() {
  return (
    <div className="relative w-40 h-40">
      {/* Neon bowl outline */}
      <div className="absolute bottom-4 w-36 h-20 rounded-b-[50%] border-2 mx-2"
        style={{
          borderColor: '#ff2d75',
          boxShadow: '0 0 15px rgba(255,45,117,0.4), inset 0 0 15px rgba(255,45,117,0.1)',
          background: 'linear-gradient(180deg, rgba(255,45,117,0.08) 0%, rgba(157,78,221,0.05) 100%)',
        }}>
        {/* Neon noodle lines */}
        {[0, 1, 2, 3].map(i => (
          <div key={i} className="absolute rounded-full" style={{
            width: 40, height: 3, top: 4 + i * 6,
            left: 8 + (i % 2) * 12,
            background: `linear-gradient(90deg, transparent, rgba(255,215,0,${0.3 + i * 0.1}) 30%, rgba(255,138,76,${0.4 + i * 0.1}) 50%, rgba(255,215,0,${0.3 + i * 0.1}) 70%, transparent)`,
            transform: `rotate(${i % 2 ? -6 : 6}deg)`,
          }} />
        ))}
      </div>
      {/* Rim glow */}
      <div className="absolute bottom-[86px] w-36 h-4 rounded-[50%] mx-2"
        style={{
          background: 'linear-gradient(180deg, rgba(255,45,117,0.5) 0%, rgba(255,45,117,0.2) 100%)',
          boxShadow: '0 0 10px rgba(255,45,117,0.3)',
        }} />
      {/* Egg */}
      <div className="absolute bottom-[50px] right-[28px] w-5 h-4 rounded-full"
        style={{ background: 'radial-gradient(circle at 40% 40%, #ffd700 0%, #ff8a4c 100%)', boxShadow: '0 0 6px rgba(255,215,0,0.4)' }} />
      {/* Chopsticks */}
      <div className="absolute top-0 right-4 w-0.5 h-16 rounded-full rotate-[20deg]"
        style={{ background: 'linear-gradient(180deg, #ff8a4c 0%, #9d4edd 100%)', boxShadow: '0 0 4px rgba(255,138,76,0.3)' }} />
      <div className="absolute top-0 right-7 w-0.5 h-16 rounded-full rotate-[25deg]"
        style={{ background: 'linear-gradient(180deg, #ff8a4c80 0%, #9d4edd80 100%)' }} />
      {/* Emoji */}
      <span className="absolute bottom-[36px] left-1/2 -translate-x-1/2 text-5xl drop-shadow-2xl">🍜</span>
    </div>
  )
}

function DishCard({ item }: { item: MenuItem }) {
  const art = FOOD_ART[item.name] || { emoji: item.category === 'drinks' ? '🍵' : '🍽️' }

  return (
    <div className="flex-shrink-0 w-48 bg-jp-card rounded-2xl overflow-hidden transition-all group hover:-translate-y-1 hover:shadow-xl"
      style={{
        border: '1px solid #2a2a3e',
        boxShadow: 'none',
      }}
      onMouseEnter={e => { e.currentTarget.style.border = '1px solid rgba(255,45,117,0.4)'; e.currentTarget.style.boxShadow = '0 0 20px rgba(255,45,117,0.1)' }}
      onMouseLeave={e => { e.currentTarget.style.border = '1px solid #2a2a3e'; e.currentTarget.style.boxShadow = 'none' }}>
      <div className="h-36 flex items-center justify-center relative overflow-hidden"
        style={{
          background: `
            radial-gradient(ellipse at 50% 80%, ${item.imageColor}30 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(255,45,117,0.04) 0%, transparent 70%),
            linear-gradient(180deg, #1a1a2a 0%, #0d0818 100%)
          `
        }}>
        {art.steam && (
          <div className="absolute top-1 left-1/2 -translate-x-1/2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
            {[0, 1, 2].map(i => (
              <div key={i} className="w-1 rounded-full steam-rise"
                style={{ height: 12 + i * 3, animationDelay: `${i * 400}ms`, background: 'rgba(255,45,117,0.15)' }} />
            ))}
          </div>
        )}
        <span className="text-5xl group-hover:scale-110 transition-transform duration-300 drop-shadow-lg relative z-10">
          {art.emoji}
        </span>
        {item.isPopular && (
          <span className="absolute top-2.5 right-2.5 flex items-center gap-0.5 text-[10px] font-bold px-2 py-0.5 rounded-full"
            style={{ background: 'rgba(255,45,117,0.9)', color: 'white', boxShadow: '0 0 8px rgba(255,45,117,0.4)' }}>
            <Star size={8} fill="currentColor" /> HOT
          </span>
        )}
        {item.spiceLevel && item.spiceLevel > 0 && (
          <span className="absolute top-2.5 left-2.5 text-[10px]">
            {'🌶️'.repeat(item.spiceLevel)}
          </span>
        )}
      </div>
      <div className="p-3.5">
        <p className="text-jp-text text-sm font-bold truncate">{item.name}</p>
        <p className="text-jp-muted text-xs truncate mb-2">{item.nameJa}</p>
        <div className="flex items-center justify-between">
          <p className="font-bold text-sm" style={{ color: '#ffd700' }}>CHF {item.price}</p>
          <span className="text-[10px] text-neon-cyan/60 bg-neon-cyan/5 border border-neon-cyan/20 px-2 py-0.5 rounded-full">{item.category}</span>
        </div>
      </div>
    </div>
  )
}

interface GarakExchange {
  prompt: string; reply: string; hit: boolean; detectors: string[]
}

interface GarakProbe {
  probe: string; desc: string; category: string; attempts: number; hits: number; asr?: number; elapsed?: number
  // A probe that produced no scoreable attempt. Without this the panel
  // divided 0 hits by 0 attempts, got 0, and painted a crashed probe the
  // same cyan PASS as one the model genuinely survived.
  failed?: boolean
  // Attempts the model answered but no detector could judge.
  unscored?: number
  error?: string | null
  // The actual attack/response pairs, so a probe can be opened up rather
  // than just scored. Absent until a scan has run.
  exchanges?: GarakExchange[]
}

interface GarakStatus {
  status: 'idle' | 'running' | 'done' | 'error'
  probes_total: number; probes_done: number; elapsed: number
  // null when nothing was scoreable — there is no safety score to report
  // for a sweep that never tested anything.
  results: GarakProbe[]; overall_asr: number | null; safety_score: number | null; error: string | null
}

// The probes this scan will run, shown before it starts so the panel is not
// empty. attempts/hits stay at zero until a real scan reports them: seeding
// them with fake counts made the panel announce "100% SAFE / 259 ATTACKS /
// 259 BLOCKED" to a first-time visitor who had never run anything, which is
// the last thing a demo about AI safety should do.
const DEFAULT_PROBES: GarakProbe[] = [
  { probe: 'DAN 11.0', desc: '"Do Anything Now" jailbreak', attempts: 0, hits: 0, category: 'jailbreak' },
  { probe: 'DAN 10.0', desc: 'Classic DAN variant', attempts: 0, hits: 0, category: 'jailbreak' },
  { probe: 'STAN', desc: '"Strive To Avoid Norms"', attempts: 0, hits: 0, category: 'jailbreak' },
  { probe: 'Base64 Injection', desc: 'Encoded payload bypass', attempts: 0, hits: 0, category: 'encoding' },
]

function GarakSection() {
  const [expanded, setExpanded] = useState(false)
  const [scanState, setScanState] = useState<'idle' | 'running' | 'done' | 'error'>('idle')
  const [probes, setProbes] = useState<GarakProbe[]>(DEFAULT_PROBES)
  const [probesDone, setProbesDone] = useState(0)
  const [probesTotal, setProbesTotal] = useState(4)
  const [elapsed, setElapsed] = useState(0)
  // null until a scan has actually produced a score — not 100.
  const [safetyScore, setSafetyScore] = useState<number | null>(null)
  const [scanError, setScanError] = useState<string | null>(null)
  // Which probe's transcript is open. Only one at a time — these get long.
  const [openProbe, setOpenProbe] = useState<string | null>(null)

  const totalAttempts = probes.reduce((s, p) => s + p.attempts, 0)
  const totalHits = probes.reduce((s, p) => s + p.hits, 0)
  // null, not 0, when nothing was scoreable. Zero hits out of zero attempts
  // is not a 0% attack success rate — it is no measurement, and rendering it
  // as 0% drew a full cyan bar for a sweep that tested nothing.
  const overallASR = totalAttempts > 0 ? totalHits / totalAttempts : null
  const scoredProbes = probes.filter(p => !p.failed && p.attempts > 0).length
  const progress = probesTotal > 0 ? (probesDone / probesTotal) * 100 : 0

  const categoryIcons: Record<string, typeof Shield> = {
    jailbreak: ShieldAlert, signatures: AlertTriangle, encoding: Shield, adversarial: ShieldAlert,
  }

  useEffect(() => {
    if (scanState !== 'running') return
    const interval = setInterval(async () => {
      try {
        const res = await fetch('/api/garak/status')
        const data: GarakStatus = await res.json()
        setProbesDone(data.probes_done)
        setProbesTotal(data.probes_total)
        setElapsed(data.elapsed)
        if (data.results.length > 0) {
          setProbes(data.results)
          setExpanded(true)
        }
        if (data.status === 'done') {
          setScanState('done')
          setSafetyScore(data.safety_score)
          setProbes(data.results)
        } else if (data.status === 'error') {
          setScanState('error')
        }
      } catch { /* ignore poll errors */ }
    }, 2000)
    return () => clearInterval(interval)
  }, [scanState])

  const startScan = async () => {
    setScanState('running')
    setScanError(null)
    setProbesDone(0)
    setElapsed(0)
    setProbes([])
    setExpanded(true)
    try {
      const res = await fetch('/api/garak/run', { method: 'POST' })
      if (!res.ok) {
        // 501 means this build has no garak installed, 409 means a scan is
        // already running. Both used to be swallowed, leaving the panel
        // stuck on "SCANNING... 0/0" forever.
        const body = await res.json().catch(() => ({}))
        setScanError(body.error || `Scan could not start (HTTP ${res.status}).`)
        setScanState('error')
      }
    } catch {
      setScanError('Could not reach the assistant service.')
      setScanState('error')
    }
  }

  return (
    <div className="rounded-2xl overflow-hidden"
      style={{ border: '1px solid rgba(0,240,255,0.2)', boxShadow: '0 0 20px rgba(0,240,255,0.05)' }}>
      <div className="h-1" style={{ background: 'linear-gradient(90deg, #00f0ff, #9d4edd, #ff2d75)' }} />
      <div className="p-6 bg-jp-surface">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{ background: 'rgba(0,240,255,0.1)', boxShadow: '0 0 15px rgba(0,240,255,0.15)' }}>
            <ShieldCheck size={20} style={{ color: '#00f0ff' }} />
          </div>
          <div className="flex-1">
            <p className="font-bold gradient-text-cool">AI Safety & Red-Teaming</p>
            <p className="text-jp-muted text-xs font-mono">garak adversarial evaluation</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-black" style={{ color: '#00f0ff', textShadow: '0 0 10px rgba(0,240,255,0.4)' }}>
              {scanState === 'running' ? '...' : safetyScore === null ? '--' : `${safetyScore}%`}
            </p>
            <p className="text-[10px] text-jp-muted uppercase tracking-wider font-mono">SAFE</p>
          </div>
        </div>

        {/* Run button */}
        <button onClick={startScan} disabled={scanState === 'running'}
          className="w-full rounded-xl py-3 font-bold text-sm font-mono transition-all mb-5 flex items-center justify-center gap-2"
          style={scanState === 'running'
            ? { background: '#1a1a2a', color: '#9090a0', border: '1px solid #2a2a3e', cursor: 'not-allowed' }
            : { background: 'linear-gradient(135deg, #00f0ff, #9d4edd)', color: 'white', boxShadow: '0 0 15px rgba(0,240,255,0.3)' }
          }>
          {scanState === 'running' ? (
            <>
              <div className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: '#9d4edd', borderTopColor: 'transparent' }} />
              SCANNING... {probesDone}/{probesTotal} probes ({elapsed}s)
            </>
          ) : scanState === 'done' ? (
            <><Zap size={14} /> RUN_SCAN_AGAIN</>
          ) : (
            <><Zap size={14} /> RUN_RED_TEAM_SCAN</>
          )}
        </button>

        {/* Why a scan could not start — previously swallowed, which left the
            panel spinning on "SCANNING... 0/0" forever on builds without garak. */}
        {scanState === 'error' && scanError && (
          <div className="mb-5 rounded-xl px-4 py-3 text-xs font-mono"
            style={{ background: 'rgba(255,45,117,0.08)', border: '1px solid rgba(255,45,117,0.3)', color: '#ff8fb0' }}>
            {scanError}
          </div>
        )}

        {/* Progress bar when running */}
        {scanState === 'running' && (
          <div className="mb-5">
            <div className="h-2 bg-jp-bg rounded-full overflow-hidden" style={{ border: '1px solid rgba(0,240,255,0.1)' }}>
              <div className="h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.max(progress, 3)}%`, background: 'linear-gradient(90deg, #00f0ff, #9d4edd)' }} />
            </div>
            <p className="text-[10px] text-jp-muted font-mono mt-1 text-center">
              probe {probesDone + 1} of {probesTotal} running...
            </p>
          </div>
        )}

        <div className="grid grid-cols-3 gap-3 mb-5">
          {[
            { val: probes.length || probesTotal, label: 'PROBES', color: '#9d4edd' },
            { val: totalAttempts, label: 'ATTACKS', color: '#ff2d75' },
            { val: totalAttempts - totalHits, label: 'BLOCKED', color: '#00f0ff' },
          ].map(s => (
            <div key={s.label} className="bg-jp-bg rounded-xl p-3 text-center" style={{ border: `1px solid ${s.color}20` }}>
              <p className="text-xl font-bold font-mono" style={{ color: s.color }}>{s.val}</p>
              <p className="text-[9px] text-jp-muted uppercase tracking-wider font-mono">{s.label}</p>
            </div>
          ))}
        </div>

        <div className="mb-4">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-jp-muted font-mono text-[10px]">ATTACK_SUCCESS_RATE</span>
            <span className="font-bold font-mono" style={{ color: overallASR === null ? '#9090a0' : '#00f0ff' }}>
              {overallASR === null ? '--' : `${(overallASR * 100).toFixed(1)}%`}
            </span>
          </div>
          <div className="h-2.5 bg-jp-bg rounded-full overflow-hidden" style={{ border: '1px solid rgba(0,240,255,0.1)' }}>
            <div className="h-full rounded-full transition-all"
              style={{
                width: overallASR === null ? '0%' : `${Math.max(100 - overallASR * 100, 2)}%`,
                background: 'linear-gradient(90deg, #00f0ff, #9d4edd)',
              }} />
          </div>
          {/* A score drawn from two of four probes is not a score for four. */}
          {probes.length > 0 && scoredProbes < probes.length && (
            <p className="text-[10px] mt-1.5" style={{ color: '#9090a0' }}>
              Based on {scoredProbes} of {probes.length} probes — the rest produced nothing scoreable.
            </p>
          )}
        </div>

        <button onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-1.5 text-xs transition-colors mb-3 font-mono"
          style={{ color: '#9d4edd' }}>
          <ChevronDown size={12} className={`transition-transform ${expanded ? 'rotate-180' : ''}`} />
          {expanded ? 'COLLAPSE' : 'EXPAND'}_PROBES
        </button>

        {expanded && (
          <div className="space-y-2 fade-in">
            {probes.map(p => {
              const failed = p.failed || p.attempts === 0
              const asr = p.attempts > 0 ? p.hits / p.attempts : 0
              const ok = !failed && asr === 0
              const accent = failed ? '#9090a0' : ok ? '#00f0ff' : '#ff2d75'
              const Icon = categoryIcons[p.category] || Shield
              const hasTranscript = !!p.exchanges?.length
              const isOpen = openProbe === p.probe
              return (
                <div key={p.probe} className="bg-jp-bg rounded-lg" style={{ border: '1px solid rgba(0,240,255,0.08)' }}>
                <div
                  className={`flex items-center gap-3 px-3 py-2 ${hasTranscript ? 'cursor-pointer' : ''}`}
                  onClick={() => hasTranscript && setOpenProbe(isOpen ? null : p.probe)}
                  title={hasTranscript ? 'Show what was actually sent' : undefined}>
                  <Icon size={14} style={{ color: accent }} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-xs font-medium text-jp-text truncate font-mono">{p.probe}</p>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full font-mono"
                        style={{
                          background: failed ? 'rgba(144,144,160,0.15)'
                            : ok ? 'rgba(0,240,255,0.15)' : 'rgba(255,45,117,0.15)',
                          color: accent,
                        }}>
                        {failed ? 'NO RESULT' : ok ? 'PASS' : `${(asr * 100).toFixed(0)}%`}
                      </span>
                    </div>
                    <p className="text-[10px] text-jp-muted">{p.desc}</p>
                    {failed && p.error && (
                      <p className="text-[10px] mt-0.5" style={{ color: '#9090a0' }}>
                        {p.unscored ? 'Ran, but nothing the detector could score' : 'Did not run'} — {p.error}
                      </p>
                    )}
                    <div className="flex items-center gap-2 mt-1">
                      <div className="flex-1 h-1 bg-jp-border rounded-full overflow-hidden">
                        {/* A failed probe gets no bar at all. A bar that is
                            full because nothing ran reads as a clean pass. */}
                        <div className="h-full rounded-full" style={{
                          width: failed ? '0%' : `${Math.max(100 - asr * 100, 3)}%`,
                          background: ok ? '#00f0ff' : asr < 0.1 ? '#ff8a4c' : '#ff2d75',
                        }} />
                      </div>
                      <span className="text-[9px] text-jp-muted whitespace-nowrap font-mono">
                        {failed ? 'not scored' : `${p.hits}/${p.attempts}`}
                        {p.elapsed !== undefined && ` · ${p.elapsed}s`}
                        {hasTranscript && <span style={{ color: '#9d4edd' }}> · {isOpen ? '▾' : '▸'} transcript</span>}
                      </span>
                    </div>
                  </div>
                </div>

                {/* The attack transcript: what garak actually sent, and what
                    came back. A score alone tells an audience nothing. */}
                {isOpen && (
                  <div className="px-3 pb-3 pt-1 space-y-2" style={{ borderTop: '1px solid rgba(0,240,255,0.08)' }}>
                    {p.exchanges!.map((ex, i) => (
                      <div key={i} className="rounded-lg overflow-hidden" style={{
                        border: `1px solid ${ex.hit ? 'rgba(255,45,117,0.35)' : 'rgba(0,240,255,0.15)'}`,
                      }}>
                        <div className="flex items-center justify-between px-2 py-1" style={{
                          background: ex.hit ? 'rgba(255,45,117,0.12)' : 'rgba(0,240,255,0.08)',
                        }}>
                          <span className="text-[9px] font-mono font-bold" style={{ color: ex.hit ? '#ff2d75' : '#00f0ff' }}>
                            {ex.hit ? 'BYPASSED' : 'BLOCKED'}
                          </span>
                          <span className="text-[9px] text-jp-muted font-mono truncate ml-2">{ex.detectors.join(', ')}</span>
                        </div>
                        <div className="px-2 py-1.5">
                          <p className="text-[9px] font-mono mb-0.5" style={{ color: '#9d4edd' }}>ATTACK</p>
                          <p className="text-[10px] text-jp-text font-mono whitespace-pre-wrap break-words leading-snug">{ex.prompt}</p>
                        </div>
                        <div className="px-2 py-1.5" style={{ borderTop: '1px dashed rgba(255,255,255,0.08)' }}>
                          <p className="text-[9px] font-mono mb-0.5" style={{ color: '#9d4edd' }}>RESPONSE</p>
                          <p className="text-[10px] text-jp-muted font-mono whitespace-pre-wrap break-words leading-snug">{ex.reply}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                </div>
              )
            })}
          </div>
        )}

        <div className="mt-4 flex items-start gap-2 bg-jp-bg rounded-lg px-3 py-2" style={{ border: '1px solid rgba(157,78,221,0.15)' }}>
          <Zap size={12} style={{ color: '#9d4edd' }} className="mt-0.5 flex-shrink-0" />
          <p className="text-[10px] text-jp-muted leading-relaxed font-mono">
            <span style={{ color: '#ff2d75' }}>garak</span> red-team framework vs{' '}
            <span style={{ color: '#00f0ff' }}>NeMo Guardrails</span> I/O shields
            {scanState === 'done' && elapsed > 0 && (
              <span> // completed in {elapsed}s</span>
            )}
          </p>
        </div>
      </div>
    </div>
  )
}

function QrPattern() {
  const pattern = [1,1,1,0,1,0,1,1,1,0,1,1,0,1,0,1,1,1,1,0,1,1,1,1,0,0,0,1,0,0,0,0,1,0,1,0,1,0,1,0,0,1,0,1,0,1,1,1,1,1,1,0,0,1,0,1,1,0,1,0,1,1,1,1]
  return (
    <div className="inline-grid grid-cols-8 gap-px" style={{ width: 56, height: 56 }}>
      {pattern.map((v, i) => (
        <div key={i} style={{ background: v ? '#ff2d75' : 'transparent', boxShadow: v ? '0 0 3px rgba(255,45,117,0.4)' : 'none' }} />
      ))}
    </div>
  )
}

export default function VisitorPage() {
  const { slug = 'sakura' } = useParams<{ slug?: string }>()
  const navigate = useNavigate()

  const [restaurant, setRestaurant] = useState<Restaurant | null>(null)
  const [restaurants, setRestaurants] = useState<Restaurant[]>([])
  const [tables, setTables] = useState<Table[]>([])
  const [menu, setMenu] = useState<MenuItem[]>([])
  const [wait, setWait] = useState<WaitEstimate | null>(null)
  const [alternatives, setAlternatives] = useState<{ restaurant: Restaurant; waitEstimate: WaitEstimate }[]>([])
  const [partySize, setPartySize] = useState(2)
  const [submitted, setSubmitted] = useState(false)
  const [form, setForm] = useState({ name: '', phone: '', time: '', notes: '' })
  const [bannerVisible, setBannerVisible] = useState(true)

  useEffect(() => { api.getRestaurants().then(setRestaurants).catch(() => null) }, [])

  useEffect(() => {
    setSubmitted(false)
    setForm({ name: '', phone: '', time: '', notes: '' })
    api.getRestaurant(slug).then(setRestaurant).catch(() => null)
    api.getTables(slug).then(setTables).catch(() => null)
    api.getMenu(slug).then(setMenu).catch(() => null)
  }, [slug])

  useEffect(() => {
    if (!restaurant) return
    Promise.all([api.getWait(slug, partySize), api.getAlternatives(slug, partySize)])
      .then(([w, alts]) => { setWait(w); setAlternatives(alts) }).catch(() => null)
  }, [restaurant, partySize, slug])

  const handleReserve = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!restaurant) return
    await api.makeReservation(slug, {
      customerName: form.name, partySize,
      phone: form.phone || undefined,
      requestedTime: form.time || new Date(Date.now() + (wait?.estimatedWaitMinutes ?? 30) * 60000).toISOString(),
      notes: form.notes || undefined,
    })
    setSubmitted(true)
  }

  const freeTables = tables.filter(t => t.status === 'free').length
  const totalTables = tables.length
  const popularItems = menu.filter(m => m.isPopular)

  if (!restaurant) return (
    <div className="min-h-screen bg-jp-bg flex items-center justify-center">
      <div className="neon-text text-neon-pink animate-pulse">Loading...</div>
    </div>
  )

  const vibe = RESTAURANT_VIBE[slug] || RESTAURANT_VIBE.sakura
  const pageBg = slug === 'sakura'
    ? 'radial-gradient(ellipse at 50% 0%, rgba(255,158,207,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 30%, rgba(255,45,117,0.04) 0%, transparent 40%), radial-gradient(ellipse at 20% 70%, rgba(255,158,207,0.03) 0%, transparent 40%)'
    : 'radial-gradient(ellipse at 50% 0%, rgba(0,198,255,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 30%, rgba(0,100,200,0.04) 0%, transparent 40%), radial-gradient(ellipse at 20% 70%, rgba(0,198,255,0.03) 0%, transparent 40%)'

  return (
    <div className="min-h-screen crt-flicker" style={{ background: `${pageBg}, var(--color-jp-bg)` }}>
      {/* Scanline overlay */}
      <div className="fixed inset-0 z-[60] scanlines pointer-events-none" />

      {/* ── Conference Banner ─────────────────────────────────────── */}
      {bannerVisible && (
        <div className="sticky top-0 z-40 backdrop-blur px-4 py-2 flex items-center justify-center gap-3"
          style={{ background: 'rgba(13,8,24,0.9)', borderBottom: '1px solid rgba(255,45,117,0.3)' }}>
          <span className="text-xs text-jp-muted font-mono">
            <span className="neon-text font-bold" style={{ color: '#ff2d75' }}>LIVE_DEMO</span>
            {' // '}
            <span style={{ color: '#00f0ff' }}>Tool-calling model</span>
            {' · '}
            <span style={{ color: '#9d4edd' }}>LangGraph</span>
            {' · '}
            <span style={{ color: '#ffd700' }}>MLflow</span>
            {' · '}
            <span style={{ color: '#ff8a4c' }}>Guardrails</span>
            {' · '}
            <span style={{ color: '#ff2d75' }}>OpenShift AI</span>
          </span>
          <button onClick={() => setBannerVisible(false)} className="text-jp-muted hover:text-neon-pink transition-colors ml-2">
            <X size={12} />
          </button>
        </div>
      )}

      {/* ── Hero Section ──────────────────────────────────────────── */}
      <div className="relative washi-texture overflow-hidden" style={{
        background: slug === 'sakura'
          ? 'radial-gradient(ellipse at 20% 0%, rgba(255,158,207,0.18) 0%, transparent 50%), radial-gradient(ellipse at 80% 0%, rgba(255,45,117,0.10) 0%, transparent 45%), radial-gradient(ellipse at 50% 100%, rgba(255,158,207,0.06) 0%, transparent 40%), var(--color-jp-surface)'
          : 'radial-gradient(ellipse at 20% 0%, rgba(0,198,255,0.18) 0%, transparent 50%), radial-gradient(ellipse at 80% 0%, rgba(0,100,200,0.10) 0%, transparent 45%), radial-gradient(ellipse at 50% 100%, rgba(0,198,255,0.06) 0%, transparent 40%), var(--color-jp-surface)',
      }}>
        {/* Retro grid floor at bottom */}
        <div className="absolute bottom-0 left-0 right-0 h-32 retro-grid" style={{ perspective: '300px', transform: 'rotateX(45deg)', transformOrigin: 'bottom' }} />

        {/* Giant kanji watermark with neon tint */}
        <span className="absolute right-8 top-8 text-[14rem] font-bold leading-none select-none pointer-events-none"
          style={{ color: vibe.accent, opacity: 0.06, textShadow: `0 0 60px ${vibe.accentGlow}` }}>
          {KANJI_WATERMARK[slug] || '食'}
        </span>

        {/* Decorative elements — cherry blossoms for sakura, water for koi */}
        {slug === 'sakura' ? (
          <>
            <span className="absolute left-[6%] top-[18%] text-2xl opacity-[0.12] rotate-12 select-none pointer-events-none hero-float" style={{ animationDelay: '0s' }}>🌸</span>
            <span className="absolute right-[12%] top-[55%] text-xl opacity-[0.10] -rotate-[20deg] select-none pointer-events-none hero-float" style={{ animationDelay: '1.5s' }}>🌸</span>
            <span className="absolute left-[18%] top-[70%] text-lg opacity-[0.08] rotate-[35deg] select-none pointer-events-none hero-float" style={{ animationDelay: '3s' }}>🌸</span>
            <span className="absolute right-[25%] top-[25%] text-sm opacity-[0.06] select-none pointer-events-none hero-float" style={{ animationDelay: '2s' }}>🌸</span>
          </>
        ) : (
          <>
            <span className="absolute left-[8%] top-[20%] text-3xl opacity-[0.10] select-none pointer-events-none hero-float" style={{ animationDelay: '0s' }}>🐟</span>
            <span className="absolute right-[10%] top-[60%] text-2xl opacity-[0.08] -rotate-12 select-none pointer-events-none hero-float" style={{ animationDelay: '2s' }}>🐟</span>
            <div className="absolute left-[5%] top-[45%] w-px h-20 opacity-10" style={{ background: 'linear-gradient(180deg, transparent, #00c6ff, transparent)' }} />
            <div className="absolute right-[8%] top-[30%] w-px h-16 opacity-10" style={{ background: 'linear-gradient(180deg, transparent, #00c6ff, transparent)' }} />
          </>
        )}

        <div className="max-w-3xl mx-auto px-6 pt-20 pb-16 relative">
          <div className="flex flex-col md:flex-row md:items-center md:gap-10">
            <div className="flex-1">
              <h1 className="text-6xl font-black mb-2 gradient-text">{restaurant.name}</h1>
              <p className="text-2xl mb-4 font-light neon-text-cyan" style={{ color: '#00f0ff' }}>{restaurant.nameJa}</p>
              <p className="text-jp-muted text-lg mb-6 italic">{TAGLINES[slug] || restaurant.cuisine}</p>

              <div className="flex flex-wrap gap-x-5 gap-y-2 text-sm text-jp-muted mb-6">
                <span className="flex items-center gap-1.5"><MapPin size={14} style={{ color: '#ff2d75' }} /> {restaurant.address}</span>
                <span className="flex items-center gap-1.5"><Phone size={14} style={{ color: '#ff2d75' }} /> {restaurant.phone}</span>
                <span className="flex items-center gap-1.5"><DollarSign size={14} style={{ color: '#ff2d75' }} /> {restaurant.priceRange}</span>
              </div>

              <div className="mb-6"><SekkiWidget /></div>

              <div className="flex flex-wrap gap-x-6 gap-y-1 text-xs text-jp-muted font-mono">
                {Object.entries(HOURS).map(([days, times]) => (
                  <span key={days}>
                    <span style={{ color: '#ff8a4c' }}>{days}</span> {times}
                  </span>
                ))}
              </div>
            </div>

            {/* Neon ramen bowl */}
            <div className="hidden md:flex flex-col items-center justify-center mt-8 md:mt-0">
              <div className="relative hero-float">
                {/* Steam with neon */}
                <div className="absolute -top-6 left-1/2 -translate-x-1/2 flex gap-3">
                  {[0, 1, 2].map(i => (
                    <div key={i} className="w-1.5 rounded-full steam-rise"
                      style={{ height: 18, animationDelay: `${i * 600}ms`, background: 'rgba(255,45,117,0.15)' }} />
                  ))}
                </div>
                <NeonBowlArt />
                {/* Neon reflection */}
                <div className="w-32 h-3 mx-auto mt-1 rounded-[50%]"
                  style={{ background: 'radial-gradient(ellipse, rgba(255,45,117,0.3) 0%, transparent 70%)' }} />
              </div>
              <p className="text-xs mt-2 tracking-[0.3em] uppercase font-mono" style={{ color: '#ff2d75' }}>SIGNATURE_RAMEN</p>
            </div>
          </div>

          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 scroll-hint">
            <ChevronDown size={20} style={{ color: '#9d4edd' }} />
          </div>
        </div>
      </div>

      {/* ── Restaurant Switcher ───────────────────────────────────── */}
      {restaurants.length > 1 && (
        <div className="max-w-3xl mx-auto px-6 pt-6">
          <p className="text-[10px] text-jp-muted font-mono uppercase tracking-wider mb-2">CHOOSE_LOCATION</p>
          <div className="flex gap-3">
            {restaurants.map(r => {
              const vibe = RESTAURANT_VIBE[r.slug] || RESTAURANT_VIBE.sakura
              const active = r.slug === slug
              return (
                <button key={r.slug} onClick={() => navigate(`/book/${r.slug}`)}
                  className="flex-1 rounded-xl px-4 py-3.5 text-left transition-all"
                  style={{
                    background: active ? `${vibe.accent}10` : '#12121e',
                    border: active ? `1px solid ${vibe.accent}60` : '1px solid #2a2a3e',
                    boxShadow: active ? `0 0 15px ${vibe.accentGlow}` : 'none',
                  }}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">{vibe.icon}</span>
                    <p className="font-semibold text-sm text-jp-text">{r.name} <span className="font-normal" style={{ color: vibe.accent }}>{r.nameJa}</span></p>
                  </div>
                  <p className="text-[10px] font-mono uppercase tracking-wider mb-1" style={{ color: vibe.accent }}>{vibe.subtitle}</p>
                  <p className="text-xs text-jp-muted flex items-center gap-1"><MapPin size={10} /> {r.address}</p>
                </button>
              )
            })}
          </div>
        </div>
      )}

      <div className="max-w-3xl mx-auto px-6 py-8 space-y-8">

        {/* ── Live Status + Party Size ──────────────────────────── */}
        <div className="bg-jp-surface rounded-2xl p-6 space-y-5"
          style={{ border: '1px solid rgba(0,240,255,0.15)' }}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full neon-pulse"
                style={{ background: freeTables > 0 ? '#00f0ff' : '#ff2d75', color: freeTables > 0 ? '#00f0ff' : '#ff2d75' }} />
              <div>
                <p className="text-jp-text font-semibold">
                  {freeTables > 0
                    ? <><span style={{ color: '#00f0ff' }}>{freeTables}</span>/{totalTables} tables available</>
                    : <span style={{ color: '#ff2d75' }}>Currently full</span>}
                </p>
                {wait && wait.estimatedWaitMinutes > 0 && (
                  <p className="text-jp-muted text-xs flex items-center gap-1 mt-0.5 font-mono">
                    <Clock size={10} /> ~{wait.estimatedWaitMinutes}min
                    {wait.nextFreeAt && <> // next@{new Date(wait.nextFreeAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</>}
                  </p>
                )}
              </div>
            </div>
            {wait && <ConfidenceBadge confidence={wait.confidence} />}
          </div>

          <div>
            <p className="text-jp-muted text-xs mb-2 flex items-center gap-1.5 font-mono"><Users size={12} style={{ color: '#9d4edd' }} /> PARTY_SIZE</p>
            <div className="flex gap-2 flex-wrap">
              {[1,2,3,4,5,6,7,8].map(n => (
                <button key={n} onClick={() => setPartySize(n)}
                  className="w-10 h-10 rounded-full font-bold text-sm transition-all"
                  style={partySize === n
                    ? { background: '#ff2d75', color: 'white', boxShadow: '0 0 15px rgba(255,45,117,0.4)' }
                    : { background: '#1a1a2a', color: '#9090a0', border: '1px solid #2a2a3e' }
                  }>
                  {n}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* ── Chef's Selection ────────────────────────────────────── */}
        {popularItems.length > 0 && (() => {
          const hero = popularItems[0]
          const rest = popularItems.slice(1, 4)
          return (
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.2em] mb-1 font-mono" style={{ color: '#ff2d75' }}>FROM_THE_KITCHEN</p>
                  <h2 className="text-xl font-bold gradient-text">Chef's Selection</h2>
                </div>
                <a href={`/menu/${slug}/1`} className="text-xs font-medium hover:underline font-mono" style={{ color: '#00f0ff' }}>
                  FULL_MENU &rarr;
                </a>
              </div>
              {/* Hero dish */}
              <div className="rounded-2xl overflow-hidden mb-3 group transition-all"
                style={{ background: '#1a1a2a', border: '1px solid #2a2a3e' }}>
                <div className="flex flex-col sm:flex-row">
                  <div className="sm:w-1/2 h-48 sm:h-auto flex items-center justify-center relative overflow-hidden"
                    style={{
                      background: `
                        radial-gradient(ellipse at 50% 70%, ${hero.imageColor}30 0%, transparent 50%),
                        radial-gradient(ellipse at 30% 30%, rgba(255,45,117,0.06) 0%, transparent 60%),
                        linear-gradient(135deg, #0d0818 0%, #12121e 100%)
                      `
                    }}>
                    {FOOD_ART[hero.name]?.steam && (
                      <div className="absolute top-3 left-1/2 -translate-x-1/2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        {[0,1,2].map(i => (
                          <div key={i} className="w-1 rounded-full steam-rise" style={{ height: 14, animationDelay: `${i*400}ms`, background: 'rgba(255,45,117,0.12)' }} />
                        ))}
                      </div>
                    )}
                    <span className="text-6xl group-hover:scale-110 transition-transform duration-500 drop-shadow-2xl">
                      {(FOOD_ART[hero.name] || { emoji: '🍜' }).emoji}
                    </span>
                  </div>
                  <div className="sm:w-1/2 p-5 flex flex-col justify-center">
                    <span className="text-[10px] uppercase tracking-[0.2em] font-bold mb-2 font-mono" style={{ color: '#ffd700' }}>SIGNATURE_DISH</span>
                    <h3 className="text-xl font-bold text-jp-text mb-0.5">{hero.name}</h3>
                    <p className="text-sm mb-2" style={{ color: '#9d4edd' }}>{hero.nameJa}</p>
                    <p className="text-jp-muted text-sm leading-relaxed mb-3">{hero.description}</p>
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-lg" style={{ color: '#ffd700' }}>CHF {hero.price}</span>
                      {hero.spiceLevel && hero.spiceLevel > 0 && <span className="text-xs">{'🌶️'.repeat(hero.spiceLevel)}</span>}
                    </div>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {rest.map(item => <DishCard key={item.id} item={item} />)}
              </div>
            </div>
          )
        })()}

        {/* ── Reservation Form ────────────────────────────────────── */}
        {!submitted ? (
          <div className="bg-jp-surface rounded-2xl overflow-hidden" style={{ border: '1px solid rgba(255,45,117,0.2)' }}>
            <div className="h-1" style={{ background: 'linear-gradient(90deg, #ff2d75, #ff8a4c, #ffd700)' }} />
            <div className="p-6">
              <div className="flex items-center gap-3 mb-5">
                <div className="w-10 h-10 rounded-full flex items-center justify-center"
                  style={{ background: 'rgba(255,45,117,0.15)', boxShadow: '0 0 12px rgba(255,45,117,0.15)' }}>
                  <Calendar size={18} style={{ color: '#ff2d75' }} />
                </div>
                <div>
                  <p className="font-bold gradient-text">Reserve a Table</p>
                  <p className="text-jp-muted text-xs font-mono">party_size: {partySize}</p>
                </div>
              </div>
              <form onSubmit={handleReserve} className="space-y-3">
                <div>
                  <label className="text-jp-muted text-xs mb-1 block font-mono">name *</label>
                  <input required value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                    placeholder="Your name"
                    className="w-full bg-jp-bg rounded-xl px-4 py-2.5 text-jp-text text-sm focus:outline-none"
                    style={{ border: '1px solid #2a2a3e' }}
                    onFocus={e => e.target.style.border = '1px solid rgba(255,45,117,0.5)'}
                    onBlur={e => e.target.style.border = '1px solid #2a2a3e'} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-jp-muted text-xs mb-1 block font-mono">phone</label>
                    <input type="tel" value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))}
                      placeholder="+41 ..."
                      className="w-full bg-jp-bg rounded-xl px-4 py-2.5 text-jp-text text-sm focus:outline-none"
                      style={{ border: '1px solid #2a2a3e' }}
                      onFocus={e => e.target.style.border = '1px solid rgba(255,45,117,0.5)'}
                      onBlur={e => e.target.style.border = '1px solid #2a2a3e'} />
                  </div>
                  <div>
                    <label className="text-jp-muted text-xs mb-1 block font-mono">time</label>
                    <input type="time" value={form.time} onChange={e => setForm(f => ({ ...f, time: e.target.value }))}
                      className="w-full bg-jp-bg rounded-xl px-4 py-2.5 text-jp-text text-sm focus:outline-none"
                      style={{ border: '1px solid #2a2a3e' }}
                      onFocus={e => e.target.style.border = '1px solid rgba(255,45,117,0.5)'}
                      onBlur={e => e.target.style.border = '1px solid #2a2a3e'} />
                  </div>
                </div>
                <div>
                  <label className="text-jp-muted text-xs mb-1 block font-mono">notes</label>
                  <input value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
                    placeholder="Allergies, special requests..."
                    className="w-full bg-jp-bg rounded-xl px-4 py-2.5 text-jp-text text-sm focus:outline-none"
                    style={{ border: '1px solid #2a2a3e' }}
                    onFocus={e => e.target.style.border = '1px solid rgba(255,45,117,0.5)'}
                    onBlur={e => e.target.style.border = '1px solid #2a2a3e'} />
                </div>
                <button type="submit" className="w-full text-white rounded-xl py-3 font-bold transition-all"
                  style={{ background: 'linear-gradient(135deg, #ff2d75, #ff8a4c)', boxShadow: '0 0 20px rgba(255,45,117,0.3)' }}>
                  Request Reservation
                </button>
              </form>
            </div>
          </div>
        ) : (
          <div className="rounded-2xl p-6 text-center fade-in"
            style={{ background: 'rgba(0,240,255,0.05)', border: '1px solid rgba(0,240,255,0.3)', boxShadow: '0 0 20px rgba(0,240,255,0.1)' }}>
            <CheckCircle size={40} className="mx-auto mb-3" style={{ color: '#00f0ff' }} />
            <p className="font-bold text-xl mb-1 neon-text-cyan" style={{ color: '#00f0ff' }}>Reservation Requested!</p>
            <p className="text-jp-muted text-sm">See you soon, {form.name}!</p>
          </div>
        )}

        {/* ── Alternatives ────────────────────────────────────────── */}
        {alternatives.length > 0 && (
          <div className="rounded-2xl overflow-hidden"
            style={{ border: '1px solid rgba(255,138,76,0.3)', boxShadow: '0 0 20px rgba(255,138,76,0.05)' }}>
            <div className="h-1" style={{ background: 'linear-gradient(90deg, #ff8a4c, #ffd700)' }} />
            <div className="p-5">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">🔄</span>
                <p className="font-bold text-sm gradient-text">Can't get a table?</p>
              </div>
              <p className="text-jp-muted text-xs mb-4 font-mono">Try our sister location — same quality, different vibe</p>
              <div className="space-y-3">
                {alternatives.map(({ restaurant: alt, waitEstimate }) => {
                  const vibe = RESTAURANT_VIBE[alt.slug] || RESTAURANT_VIBE.sakura
                  return (
                    <button key={alt.id} onClick={() => navigate(`/book/${alt.slug}`)}
                      className="w-full bg-jp-bg rounded-xl p-4 flex items-center justify-between transition-all text-left"
                      style={{ border: `1px solid ${vibe.accent}30` }}
                      onMouseEnter={e => { e.currentTarget.style.border = `1px solid ${vibe.accent}60`; e.currentTarget.style.boxShadow = `0 0 15px ${vibe.accentGlow}` }}
                      onMouseLeave={e => { e.currentTarget.style.border = `1px solid ${vibe.accent}30`; e.currentTarget.style.boxShadow = 'none' }}>
                      <div>
                        <div className="flex items-center gap-2 mb-0.5">
                          <span>{vibe.icon}</span>
                          <p className="font-semibold text-jp-text">{alt.name} <span style={{ color: vibe.accent }}>{alt.nameJa}</span></p>
                        </div>
                        <p className="text-[10px] font-mono uppercase tracking-wider mb-0.5" style={{ color: vibe.accent }}>{vibe.subtitle}</p>
                        <p className="text-jp-muted text-xs flex items-center gap-1"><MapPin size={10} /> {alt.address}</p>
                      </div>
                      <div className="text-right">
                        {waitEstimate.estimatedWaitMinutes === 0
                          ? <span className="font-bold text-sm" style={{ color: '#00f0ff' }}>Available now</span>
                          : <span className="font-bold text-sm" style={{ color: '#ff8a4c' }}>~{waitEstimate.estimatedWaitMinutes}m</span>}
                        <p className="text-jp-muted text-xs">{alt.priceRange}</p>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {/* ── AI Concierge Section ────────────────────────────────── */}
        <button
          onClick={() => window.dispatchEvent(new CustomEvent('open-chat'))}
          className="w-full bg-jp-surface rounded-2xl p-6 text-center transition-all cursor-pointer group"
          style={{ border: '1px solid rgba(157,78,221,0.2)' }}
          onMouseEnter={e => { e.currentTarget.style.border = '1px solid rgba(157,78,221,0.5)'; e.currentTarget.style.boxShadow = '0 0 25px rgba(157,78,221,0.15)' }}
          onMouseLeave={e => { e.currentTarget.style.border = '1px solid rgba(157,78,221,0.2)'; e.currentTarget.style.boxShadow = 'none' }}>
          <div className="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform"
            style={{ background: 'linear-gradient(135deg, rgba(157,78,221,0.2), rgba(255,45,117,0.15))', boxShadow: '0 0 25px rgba(157,78,221,0.2)' }}>
            <Bot size={26} style={{ color: '#9d4edd' }} />
          </div>
          <h2 className="text-xl font-bold gradient-text-cool mb-1">Meet Our AI Host</h2>
          <p className="text-jp-muted text-sm mb-5 max-w-md mx-auto">
            Ask about availability, browse the menu, or make a reservation
          </p>
          <div className="flex gap-2 justify-center flex-wrap" onClick={e => e.stopPropagation()}>
            {DEMO_CHIPS.map(chip => (
              <span key={chip.label}
                onClick={() => window.dispatchEvent(new CustomEvent('open-chat', { detail: { message: chip.label } }))}
                className="flex items-center gap-1 text-xs text-jp-muted rounded-full px-3 py-1.5 cursor-pointer transition-all hover:text-jp-text"
                style={{ background: 'rgba(157,78,221,0.08)', border: '1px solid rgba(157,78,221,0.2)' }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(157,78,221,0.5)'; e.currentTarget.style.background = 'rgba(157,78,221,0.15)' }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(157,78,221,0.2)'; e.currentTarget.style.background = 'rgba(157,78,221,0.08)' }}>
                <chip.icon size={10} />
                {chip.label}
                {'hint' in chip && chip.hint && (
                  <span className="text-[9px] ml-0.5" style={{ color: '#ff8a4c' }}>({chip.hint})</span>
                )}
              </span>
            ))}
          </div>
          <p className="text-jp-muted text-[10px] mt-4 font-mono group-hover:text-neon-purple transition-colors">tap to start chatting</p>
        </button>

        {/* ── Garak Red-Team Security ─────────────────────────────── */}
        <GarakSection />

        {/* ── Footer ──────────────────────────────────────────────── */}
        <footer className="pt-8 pb-12" style={{ borderTop: '1px solid rgba(255,45,117,0.15)' }}>
          <div className="flex flex-col sm:flex-row items-start justify-between gap-6">
            <div>
              <p className="font-bold text-lg gradient-text">{restaurant.name}</p>
              <p className="text-sm mb-3" style={{ color: '#9d4edd' }}>{restaurant.nameJa}</p>
              <p className="text-jp-muted text-xs flex items-center gap-1.5 mb-1"><MapPin size={10} style={{ color: '#ff2d75' }} /> {restaurant.address}</p>
              <p className="text-jp-muted text-xs flex items-center gap-1.5"><Phone size={10} style={{ color: '#ff2d75' }} /> {restaurant.phone}</p>
              <div className="mt-3 space-y-0.5 font-mono">
                {Object.entries(HOURS).map(([days, times]) => (
                  <p key={days} className="text-jp-muted text-xs">
                    <span style={{ color: '#ff8a4c' }}>{days}</span> {times}
                  </p>
                ))}
              </div>
            </div>
            <div className="text-right sm:text-left flex flex-col items-end sm:items-start gap-2">
              <QrPattern />
              <p className="text-jp-muted text-[10px] font-mono">SCAN_TO_VISIT</p>
              <div className="mt-2">
                <p className="text-jp-muted text-xs font-mono">powered_by</p>
                <p className="font-bold text-sm neon-text" style={{ color: '#ff2d75' }}>TableSchnappi</p>
                <p className="text-jp-muted text-[10px] mt-0.5 font-mono">ai_restaurant_mgmt</p>
              </div>
            </div>
          </div>
        </footer>
      </div>

      <AttackDemo slug={slug} />
      <ChatWidget slug={slug} />
    </div>
  )
}
