'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'

export default function ProvidersPage() {
  const [providers, setProviders] = useState<any[]>([])

  useEffect(() => {
    fetch('/api/v1/providers').then(r => r.json()).then(setProviders).catch(() => {})
  }, [])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Providers</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {providers.map((p: any) => (
          <Link key={p.id} href={`/providers/${p.id}`} className="bg-gray-900 border border-gray-800 rounded-lg p-4 hover:border-gray-600 transition">
            <h3 className="font-medium">{p.name}</h3>
            <div className="text-sm text-gray-400 mt-2">
              <span>{p.model_count || 0} models</span>
              <span className="ml-4">{p.country}</span>
              <span className="ml-4 capitalize">{p.type}</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
