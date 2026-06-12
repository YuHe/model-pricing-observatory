interface StatsCardProps {
  label: string
  value: string | number
}

export function StatsCard({ label, value }: StatsCardProps) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <p className="text-sm text-gray-400">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  )
}
