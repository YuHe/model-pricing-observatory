'use client'
import { useEffect, useState } from 'react'
import { PriceChange } from '@/components/PriceChange'
import Link from 'next/link'

interface ModelItem {
  id: string; name: string; provider: string; family: string
  input_price_cny: number; output_price_cny: number
  context_window: number; price_change_percent: number
  vision: boolean; reasoning: boolean; tool_calling: boolean
}

export default function ModelsPage() {
  const [models, setModels] = useState<ModelItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [sortBy, setSortBy] = useState('input_price_cny')
  const [sortOrder, setSortOrder] = useState('asc')
  const [search, setSearch] = useState('')
  const [view, setView] = useState<'list' | 'card'>('list')

  useEffect(() => {
    const params = new URLSearchParams({ page: String(page), page_size: '50', sort_by: sortBy, sort_order: sortOrder })
    if (search) params.set('search', search)
    fetch(`/api/v1/models?${params}`)
      .then(r => r.json())
      .then(d => { setModels(d.items || []); setTotal(d.total || 0) })
      .catch(() => {})
  }, [page, sortBy, sortOrder, search])

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <input className="bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm flex-1" placeholder="Search models..." value={search} onChange={e => setSearch(e.target.value)} />
        <select className="bg-gray-900 border border-gray-700 rounded px-2 py-2 text-sm" value={sortBy} onChange={e => setSortBy(e.target.value)}>
          <option value="input_price_cny">Input Price</option>
          <option value="output_price_cny">Output Price</option>
          <option value="context_window">Context</option>
        </select>
        <button className="text-sm text-gray-400" onClick={() => setSortOrder(o => o === 'asc' ? 'desc' : 'asc')}>{sortOrder === 'asc' ? '↑' : '↓'}</button>
        <button className="text-sm text-gray-400" onClick={() => setView(v => v === 'list' ? 'card' : 'list')}>{view === 'list' ? '▦' : '≡'}</button>
      </div>
      <div className={view === 'list' ? 'space-y-1' : 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'}>
        {models.map(m => (
          <Link key={m.id} href={`/models/${m.id}`} className="block bg-gray-900 border border-gray-800 rounded-lg p-3 hover:border-gray-600 transition">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-medium">{m.name}</span>
                <span className="text-xs text-gray-500 ml-2">{m.provider}</span>
              </div>
              <PriceChange percent={m.price_change_percent} />
            </div>
            <div className="flex gap-4 mt-2 text-sm text-gray-400">
              <span>¥{m.input_price_cny?.toFixed(1)} in</span>
              <span>¥{m.output_price_cny?.toFixed(1)} out</span>
              <span>{m.context_window ? `${(m.context_window/1000).toFixed(0)}K ctx` : ''}</span>
            </div>
          </Link>
        ))}
      </div>
      <div className="flex justify-center gap-2 text-sm">
        <button disabled={page <= 1} onClick={() => setPage(p => p-1)} className="px-3 py-1 bg-gray-800 rounded disabled:opacity-50">Prev</button>
        <span className="px-3 py-1 text-gray-400">Page {page} / {Math.ceil(total/50) || 1}</span>
        <button onClick={() => setPage(p => p+1)} className="px-3 py-1 bg-gray-800 rounded">Next</button>
      </div>
    </div>
  )
}
