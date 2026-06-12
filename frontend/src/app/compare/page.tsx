'use client'
import { useState } from 'react'

export default function ComparePage() {
  const [ids, setIds] = useState<string[]>([])
  const [search, setSearch] = useState('')
  const [results, setResults] = useState<any[]>([])
  const [models, setModels] = useState<any[]>([])

  const addModel = (id: string) => {
    if (ids.length >= 10 || ids.includes(id)) return
    const newIds = [...ids, id]
    setIds(newIds)
    fetch(`/api/v1/compare?ids=${newIds.join(',')}`).then(r => r.json()).then(setModels).catch(() => {})
  }

  const searchModels = (q: string) => {
    setSearch(q)
    if (q.length > 1) fetch(`/api/v1/models?search=${q}&page_size=5`).then(r => r.json()).then(d => setResults(d.items || [])).catch(() => {})
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Compare Models</h1>
      <input className="bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm w-full" placeholder="Search to add models (max 10)..." value={search} onChange={e => searchModels(e.target.value)} />
      {results.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded p-2 space-y-1">
          {results.map((r: any) => (
            <button key={r.id} onClick={() => { addModel(r.id); setResults([]) }} className="block w-full text-left px-2 py-1 hover:bg-gray-800 rounded text-sm">{r.name} <span className="text-gray-500">({r.provider})</span></button>
          ))}
        </div>
      )}
      {models.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-gray-800">
              <th className="text-left py-2 px-2">Model</th>
              <th className="text-right px-2">Input ¥/M</th>
              <th className="text-right px-2">Output ¥/M</th>
              <th className="text-right px-2">Context</th>
              <th className="text-center px-2">Vision</th>
              <th className="text-center px-2">Reasoning</th>
            </tr></thead>
            <tbody>
              {models.map((m: any) => (
                <tr key={m.id} className="border-b border-gray-800/50">
                  <td className="py-2 px-2 font-medium">{m.name}</td>
                  <td className="text-right px-2">¥{m.input_price_cny?.toFixed(1)}</td>
                  <td className="text-right px-2">¥{m.output_price_cny?.toFixed(1)}</td>
                  <td className="text-right px-2">{m.context_window ? `${(m.context_window/1000).toFixed(0)}K` : '-'}</td>
                  <td className="text-center px-2">{m.vision ? '✓' : '-'}</td>
                  <td className="text-center px-2">{m.reasoning ? '✓' : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
