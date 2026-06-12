'use client'
import { useEffect, useState } from 'react'
import { PriceChart } from '@/components/PriceChart'

export default function PlanDetailPage({ params }: { params: { id: string } }) {
  const [plan, setPlan] = useState<any>(null)
  const [history, setHistory] = useState<any[]>([])

  useEffect(() => {
    fetch(`/api/v1/plans/${params.id}`).then(r => r.json()).then(setPlan).catch(() => {})
    fetch(`/api/v1/plans/${params.id}/history`).then(r => r.json()).then(setHistory).catch(() => {})
  }, [params.id])

  if (!plan) return <div className="text-gray-400">Loading...</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{plan.plan_name}</h1>
        <p className="text-gray-400">{plan.provider}</p>
        <p className="text-3xl font-bold mt-2">${plan.monthly_price}/mo</p>
      </div>
      {history.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <h2 className="text-lg font-medium mb-4">Price History</h2>
          <PriceChart data={history.map((h: any) => ({ date: h.date, input_price_cny: h.monthly_price_cny, output_price_cny: h.monthly_price_cny }))} />
        </div>
      )}
    </div>
  )
}
