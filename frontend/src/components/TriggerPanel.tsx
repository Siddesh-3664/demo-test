import { useState } from "react"
import { postOrder, type Scenario, type OrderResult } from "../lib/api"

const JAEGER_URL = import.meta.env.VITE_JAEGER_URL

interface Props {
  onAsk: (traceId: string, failed: boolean) => void
}

export function TriggerPanel({ onAsk }: Props) {
  const [rows, setRows] = useState<OrderResult[]>([])
  const [busy, setBusy] = useState<Scenario | null>(null)

  async function handle(scenario: Scenario) {
    setBusy(scenario)
    const result = await postOrder(scenario)
    setRows((prev) => [result, ...prev].slice(0, 10))
    setBusy(null)
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-bold mb-3">Trigger Requests</h2>
      <div className="flex gap-2 mb-4">
        {(["fast", "slow", "fail"] as Scenario[]).map((s) => (
          <button
            key={s}
            onClick={() => handle(s)}
            disabled={busy !== null}
            className={`px-4 py-2 rounded font-medium capitalize ${
              busy === s ? "bg-gray-400" : s === "fail" ? "bg-red-500" : s === "slow" ? "bg-yellow-500" : "bg-green-500"
            } text-white disabled:opacity-50`}
          >
            {busy === s ? "..." : s}
          </button>
        ))}
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 border-b">
            <th className="py-1">Time</th>
            <th>Scenario</th>
            <th>Status</th>
            <th>ms</th>
            <th>Trace</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-b">
              <td className="py-1 text-gray-500">{new Date(r.at).toLocaleTimeString()}</td>
              <td className="capitalize">{r.scenario}</td>
              <td className={r.status >= 500 ? "text-red-600 font-bold" : r.status >= 200 && r.status < 300 ? "text-green-600" : "text-gray-500"}>
                {r.status || "ERR"}
              </td>
              <td>{r.elapsedMs}</td>
              <td>
                {r.traceId && (
                  <a
                    target="_blank"
                    href={`${JAEGER_URL}/trace/${r.traceId}`}
                    className="text-blue-500 hover:underline font-mono"
                  >
                    {r.traceId.slice(0, 8)}
                  </a>
                )}
              </td>
              <td>
                {r.traceId && (
                  <button
                    onClick={() => onAsk(r.traceId, r.status >= 500)}
                    className="text-xs px-2 py-1 bg-indigo-500 text-white rounded hover:bg-indigo-600"
                  >
                    Ask AI
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
