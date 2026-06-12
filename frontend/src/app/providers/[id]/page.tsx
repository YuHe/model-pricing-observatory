'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'

export default function ProviderDetailPage({ params }: { params: { id: string } }) {
  const [provider, setProvider] = useState<any>(null)

  useEffect(() => {
    fetch(`/api/v1/providers/${params.id}`).then(r => r.json()).then(setProvider).catch(() => {})
  }, [params.id])

  if (!provider) return <div className="text-gray-400">Loading...</div>

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{provider.name}</h1>
      <p className="text-gray-400">{provider.country} · {provider.type}</p>
      <div className="space-y-2">
        {(provider.models || []).map((m: any) => (
          <Link key={m.id} href={`/models/${m.id}`} className="block bg-gray-900 border border-gray-800 rounded p-3 hover:border-gray-600 text-sm">{m.name}</Link>
        ))}
      </div>
    </div>
  )
}
