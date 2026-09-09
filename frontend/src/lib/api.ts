export type Scenario = "fast" | "slow" | "fail"

export interface OrderResult {
  scenario: Scenario
  status: number
  elapsedMs: number
  orderId?: string
  traceId?: string
  error?: string
  at: string
}

export interface DoneEvent {
  intent: string
  trace_id: string | null
  tokens_in: number
  unverified_numbers: string[]
}

const ORDER_URL = import.meta.env.VITE_ORDER_URL
const AI_URL = import.meta.env.VITE_AI_URL

export async function postOrder(scenario: Scenario): Promise<OrderResult> {
  const start = performance.now()
  try {
    const resp = await fetch(`${ORDER_URL}/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Scenario": scenario },
      body: JSON.stringify({ item: "widget", quantity: 2 }),
    })
    const elapsedMs = Math.round(performance.now() - start)
    const data = await resp.json().catch(() => ({}))
    return {
      scenario,
      status: resp.status,
      elapsedMs,
      orderId: data.orderId,
      traceId: data.traceId || resp.headers.get("X-Trace-Id") || undefined,
      at: new Date().toISOString(),
    }
  } catch (e: any) {
    return {
      scenario,
      status: 0,
      elapsedMs: Math.round(performance.now() - start),
      error: e?.message || "fetch failed",
      at: new Date().toISOString(),
    }
  }
}

export async function streamChat(
  sessionId: string,
  question: string,
  onToken: (t: string) => void,
  onDone: (d: DoneEvent) => void,
): Promise<void> {
  const resp = await fetch(`${AI_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, question }),
  })
  if (!resp.body) return
  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split("\n\n")
    buffer = blocks.pop() || ""
    for (const block of blocks) {
      let event = ""
      let data = ""
      for (const line of block.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim()
        else if (line.startsWith("data:")) data += (data ? "\n" : "") + line.slice(5).replace(/^ /, "")
      }
      if (event === "token") onToken(data)
      else if (event === "done") onDone(JSON.parse(data))
    }
  }
}
