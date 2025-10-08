import { LineChart, Line, ResponsiveContainer } from 'recharts'
import type { HistoricalDataPoint } from '@/types'
import type { SparklineDataPoint } from '@/types/dailyMetrics'

interface SparkLineProps {
  data: HistoricalDataPoint[] | SparklineDataPoint[]
  color?: string
  height?: number
}

export function SparkLine({ data, color, height = 40 }: SparkLineProps) {
  if (!data || data.length === 0) {
    return null
  }

  // Auto-determine color based on trend if not provided
  let lineColor = color
  if (!lineColor) {
    const firstValue = data[0]?.value ?? 0
    const lastValue = data[data.length - 1]?.value ?? 0
    const isPositive = lastValue >= firstValue
    lineColor = isPositive ? 'hsl(142 76% 36%)' : 'hsl(0 84% 60%)'
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <Line
          type="monotone"
          dataKey="value"
          stroke={lineColor}
          strokeWidth={2}
          dot={false}
          animationDuration={300}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
