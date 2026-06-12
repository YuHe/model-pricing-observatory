'use client'
import { useEffect, useState } from 'react'

export default function ChannelDetailPage({ params }: { params: { id: string } }) {
  const [prices, setPrices] = useState<any[]>([])

  useEffect(() => {
    fetch(`/api/v1/channels/${params.id}/prices`).then(r => r.json()).then(setPrices).catch(() => {})
  }, [params.id])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Channel Prices</h1>
      <table className="w-full text-sm">
        <thead><tr className="border-b border-gray-800"><th className="text-left py-2">Model</th><th className="text-right">Input ¥/M</th><th className="text-right">Output ¥/M</th></tr></thead>
        <tbody>
          {prices.map((p: any, i: number) => (
            <tr key={i} className="border-b border-gray-800/50">
              <td className="py-2">{p.model_name || p.name}</td>
              <td className="text-right">¥{p.input_price_cny?.toFixed(2)}</td>
              <td className="text-right">¥{p.output_price_cny?.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
