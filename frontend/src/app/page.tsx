import { StatsCard } from '@/components/StatsCard'

export default async function Home() {
  let stats = { provider_count: 0, model_count: 0, channel_count: 0, today_updated: 0 }
  try {
    const res = await fetch('http://backend:3722/api/v1/stats', { next: { revalidate: 300 } })
    if (res.ok) stats = await res.json()
  } catch {}

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Model Pricing Observatory</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatsCard label="Providers" value={stats.provider_count} />
        <StatsCard label="Models" value={stats.model_count} />
        <StatsCard label="Channels" value={stats.channel_count} />
        <StatsCard label="Updated Today" value={stats.today_updated} />
      </div>
    </div>
  )
}
