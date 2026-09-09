import { useState } from "react"
import { TriggerPanel } from "./components/TriggerPanel"
import { ChatPanel } from "./components/ChatPanel"

export default function App() {
  const [pendingQuestion, setPendingQuestion] = useState<string | null>(null)

  function onAsk(traceId: string, failed: boolean) {
    setPendingQuestion(failed ? `why did ${traceId} fail?` : `why was ${traceId} slow?`)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-indigo-600 text-white p-4">
        <h1 className="text-xl font-bold">Observability AI Demo</h1>
      </header>
      <div className="grid grid-cols-2 gap-4 p-4 max-w-7xl mx-auto">
        <TriggerPanel onAsk={onAsk} />
        <ChatPanel pendingQuestion={pendingQuestion} onConsumed={() => setPendingQuestion(null)} />
      </div>
    </div>
  )
}
