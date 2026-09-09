import { useState, useRef, useEffect } from "react"
import { streamChat, type DoneEvent } from "../lib/api"

interface Message {
  role: "user" | "assistant"
  text: string
  meta?: DoneEvent
}

interface Props {
  pendingQuestion: string | null
  onConsumed: () => void
}

export function ChatPanel({ pendingQuestion, onConsumed }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [busy, setBusy] = useState(false)
  const sessionId = useRef(crypto.randomUUID())
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (pendingQuestion) {
      setInput(pendingQuestion)
      onConsumed()
      // auto-send
      send(pendingQuestion)
    }
  }, [pendingQuestion])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  async function send(question: string) {
    if (!question.trim() || busy) return
    setBusy(true)
    setMessages((prev) => [...prev, { role: "user", text: question }, { role: "assistant", text: "" }])
    setInput("")
    let assistantIdx = -1
    setMessages((prev) => {
      assistantIdx = prev.length - 1
      return prev
    })
    await streamChat(
      sessionId.current,
      question,
      (token) => {
        setMessages((prev) => {
          const next = [...prev]
          next[assistantIdx] = { ...next[assistantIdx], text: next[assistantIdx].text + token }
          return next
        })
      },
      (done) => {
        setMessages((prev) => {
          const next = [...prev]
          next[assistantIdx] = { ...next[assistantIdx], meta: done }
          return next
        })
      },
    )
    setBusy(false)
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      send(input)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-4 flex flex-col h-[600px]">
      <h2 className="text-lg font-bold mb-3">Ask AI</h2>
      <div className="flex-1 overflow-y-auto mb-3 space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-right" : ""}>
            <div className={`inline-block max-w-[80%] px-3 py-2 rounded-lg ${m.role === "user" ? "bg-blue-100" : "bg-gray-100"}`}>
              {m.text || "..."}
            </div>
            {m.meta && (
              <div className="text-xs text-gray-400 mt-1 flex items-center gap-2">
                <span>
                  {m.meta.intent} · {m.meta.trace_id?.slice(0, 8) || "no-trace"} · tokens_in: {m.meta.tokens_in}
                  {m.meta.unverified_numbers.length > 0 && (
                    <span className="text-amber-600 ml-2">unverified: {m.meta.unverified_numbers.join(", ")}</span>
                  )}
                </span>
                {m.role === "assistant" && m.text && (
                  <button
                    onClick={() => send("is this a known issue?")}
                    className="text-indigo-500 hover:underline"
                  >
                    Known issue?
                  </button>
                )}
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Ask about slow or failed requests..."
          className="flex-1 border rounded px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
        <button
          onClick={() => send(input)}
          disabled={busy}
          className="px-4 py-2 bg-indigo-500 text-white rounded hover:bg-indigo-600 disabled:opacity-50"
        >
          {busy ? "..." : "Send"}
        </button>
      </div>
    </div>
  )
}
