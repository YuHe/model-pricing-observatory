'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'

export default function ChannelsPage() {
  const [channels, setChannels] = useState<any[]>([])

  useEffect(() => {
    fetch('/api/v1/channels').then(r => r.json()).then(setChannels).catch(() => {})
  }, [])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Channels</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {channels.map((c: any) => (
          <Link key={c.id} href={`/channels/${c.id}`} className="bg-gray-900 border border-gray-800 rounded-lg p-4 hover:border-gray-600 transition">
            <h3 className="font-medium">{c.name}</h3>
            <p className="text-sm text-gray-400 mt-1">{c.model_count || 0} models</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
