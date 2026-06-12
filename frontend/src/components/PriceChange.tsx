interface PriceChangeProps {
  percent: number | null
}

export function PriceChange({ percent }: PriceChangeProps) {
  if (!percent) return <span className="text-gray-500">—</span>
  const isDown = percent < 0
  return (
    <span className={isDown ? 'text-green-400' : 'text-red-400'}>
      {isDown ? '▼' : '▲'} {Math.abs(percent).toFixed(1)}%
    </span>
  )
}
