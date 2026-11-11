import { Router } from 'express'

const ASSISTANT_URL = process.env.ASSISTANT_URL
  ?? 'http://mlflow-proxy.tableschnappi.svc.cluster.local:8000'

export function createAssistantRouter(): Router {
  const router = Router()

  // Proxy all assistant turns to the Python service
  // Python handles: prompt registry, tool loop, MLflow @mlflow.trace
  router.post('/restaurants/:slug/assistant', async (req, res) => {
    const { slug } = req.params
    try {
      const r = await fetch(`${ASSISTANT_URL}/assistant`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...req.body, slug }),
      })
      if (!r.ok) {
        console.error('Assistant upstream error:', r.status, await r.text())
        return res.status(r.status).json({ error: 'Assistant is temporarily unavailable.' })
      }
      res.json(await r.json())
    } catch (e) {
      console.error('Assistant proxy error:', e)
      res.status(502).json({ error: 'Assistant is temporarily unavailable.' })
    }
  })

  // The UI needs to know whether the guardrails shield is actually deployed.
  // Without it the attack demo cannot tell "the model was jailbroken" from
  // "there is no shield on this profile" — they look identical from the
  // response text alone.
  router.get('/assistant/health', async (_req, res) => {
    try {
      const r = await fetch(`${ASSISTANT_URL}/health`)
      res.json(await r.json())
    } catch {
      // Assume guarded on error: claiming a bypass because a health probe
      // failed would be the same false alarm in a different costume.
      res.json({ ok: false, guardrails_enabled: true })
    }
  })

  // Proxy human feedback (👍/👎) to the Python service
  router.post('/restaurants/:slug/assistant/feedback', async (req, res) => {
    const { traceId, score } = req.body
    if (!traceId || score === undefined) {
      return res.status(400).json({ error: 'traceId and score required' })
    }
    try {
      const upstream = await fetch(`${ASSISTANT_URL}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ traceId, score }),
      })
      return res.status(upstream.status).json(await upstream.json())
    } catch (e) {
      console.error('Feedback proxy error:', e)
      return res.status(502).json({ ok: false, error: 'Feedback was not saved. Please retry.' })
    }
  })

  // Proxy garak run/status to the Python service
  router.post('/garak/run', async (_req, res) => {
    try {
      const r = await fetch(`${ASSISTANT_URL}/garak/run`, { method: 'POST' })
      res.status(r.status).json(await r.json())
    } catch {
      res.status(502).json({ error: 'Garak service unavailable.' })
    }
  })

  router.get('/garak/status', async (_req, res) => {
    try {
      const r = await fetch(`${ASSISTANT_URL}/garak/status`)
      res.json(await r.json())
    } catch {
      res.status(502).json({ error: 'Garak service unavailable.' })
    }
  })

  return router
}
