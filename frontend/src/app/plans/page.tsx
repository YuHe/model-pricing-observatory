'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'

export default function PlansPage() {
  const [plans, setPlans] = useState<any[]>([])

  useEffect(() => {
    fetch('/api/v1/plans').then(r => r.json()).then(setPlans).catch(() => {})
  }, [])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Subscription Plans</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {plans.map((p: any) => (
          <Link key={p.id} href={`/plans/${p.id}`} className="bg-gray-900 border border-gray-800 rounded-lg p-4 hover:border-gray-600 transition">
            <h3 className="font-medium">{p.plan_name}</h3>
            <p className="text-sm text-gray-400">{p.provider}</p>
            <p className="text-xl font-bold mt-2">${p.monthly_price}/mo</p>
            <p className="text-sm text-gray-500">≈ ¥{p.monthly_price_cny}/mo</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
