import { LineChart, Line, ResponsiveContainer } from 'recharts'
import type { HistoricalDataPoint } from '@/types'

interface SparkLineProps {
  data: HistoricalDataPoint[]
  color?: string
}

export function SparkLine({ data, color = '#8b5cf6' }: SparkLineProps) {
  return (
    <ResponsiveContainer width="100%" height={40}>
      <LineChart data={data}>
        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
