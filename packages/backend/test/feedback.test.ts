import test from 'node:test'
import assert from 'node:assert/strict'
import { once } from 'node:events'
import express from 'express'

// Exercise real HTTP handling: the browser must see an upstream write failure.
test('feedback forwards upstream errors and reports unavailable service', async () => {
  const upstream = express()
  upstream.post('/feedback', (_req, res) => res.status(503).json({ ok: false, error: 'Not saved' }))
  const upstreamServer = upstream.listen(0, '127.0.0.1')
  await once(upstreamServer, 'listening')
  const address = upstreamServer.address() as { port: number }
  process.env.ASSISTANT_URL = `http://127.0.0.1:${address.port}`
  const { createAssistantRouter } = await import('../src/assistant')
  const backend = express()
  backend.use(express.json(), createAssistantRouter())
  const server = backend.listen(0, '127.0.0.1')
  await once(server, 'listening')
  const target = server.address() as { port: number }
  const send = () => fetch(`http://127.0.0.1:${target.port}/restaurants/sakura/assistant/feedback`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ traceId: 'tr-test', score: 1 }),
  })
  try {
    const failed = await send()
    assert.equal(failed.status, 503)
    assert.equal((await failed.json()).ok, false)
    await new Promise<void>(resolve => upstreamServer.close(() => resolve()))
    const unavailable = await send()
    assert.equal(unavailable.status, 502)
    assert.equal((await unavailable.json()).ok, false)
  } finally {
    upstreamServer.close()
    await new Promise<void>(resolve => server.close(() => resolve()))
    delete process.env.ASSISTANT_URL
  }
})
