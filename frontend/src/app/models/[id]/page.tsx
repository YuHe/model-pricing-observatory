'use client'
import { useEffect, useState } from 'react'
import { PriceChart } from '@/components/PriceChart'

export default function ModelDetailPage({ params }: { params: { id: string } }) {
  const [model, setModel] = useState<any>(null)
  const [history, setHistory] = useState<any[]>([])

  useEffect(() => {
    fetch(`/api/v1/models/${params.id}`).then(r => r.json()).then(setModel).catch(() => {})
    fetch(`/api/v1/models/${params.id}/history`).then(r => r.json()).then(setHistory).catch(() => {})
  }, [params.id])

  if (!model) return <div className="text-gray-400">Loading...</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{model.name}</h1>
        <p className="text-gray-400">{model.provider}</p>
      </div>
      <div className="flex flex-wrap gap-2">
        {model.vision && <span className="px-2 py-1 bg-blue-900/50 text-blue-300 rounded text-xs">Vision</span>}
        {model.reasoning && <span className="px-2 py-1 bg-purple-900/50 text-purple-300 rounded text-xs">Reasoning</span>}
        {model.tool_calling && <span className="px-2 py-1 bg-green-900/50 text-green-300 rounded text-xs">Tools</span>}
      </div>
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
        <h2 className="text-lg font-medium mb-4">Price History (90 days)</h2>
        <PriceChart data={history} />
      </div>
    </div>
  )
}
