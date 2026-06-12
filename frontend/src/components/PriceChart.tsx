'use client'
import dynamic from 'next/dynamic'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

interface PriceChartProps {
  data: { date: string; input_price_cny: number; output_price_cny: number }[]
}

export function PriceChart({ data }: PriceChartProps) {
  const option = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { data: ['Input', 'Output'], textStyle: { color: '#999' } },
    xAxis: { type: 'category', data: data.map(d => d.date), axisLabel: { color: '#666' } },
    yAxis: { type: 'value', axisLabel: { color: '#666', formatter: '¥{value}' } },
    series: [
      { name: 'Input', type: 'line', data: data.map(d => d.input_price_cny), smooth: true, itemStyle: { color: '#3b82f6' } },
      { name: 'Output', type: 'line', data: data.map(d => d.output_price_cny), smooth: true, itemStyle: { color: '#8b5cf6' } },
    ],
  }
  return <ReactECharts option={option} style={{ height: 300 }} />
}
