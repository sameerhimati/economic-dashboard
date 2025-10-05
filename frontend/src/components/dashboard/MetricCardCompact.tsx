import { SparkLine } from '@/components/charts/SparkLine'
import { formatNumber, formatPercent } from '@/lib/utils'
import type { EconomicIndicator } from '@/types'
import { cn } from '@/lib/utils'

interface MetricCardCompactProps {
  metric: EconomicIndicator
  onClick?: () => void
}

export function MetricCardCompact({ metric, onClick }: MetricCardCompactProps) {
  if (!metric) return null

  const isPositive = (metric?.change ?? 0) > 0
  const isNeutral = (metric?.change ?? 0) === 0
  const color = isPositive ? '#10b981' : isNeutral ? '#6b7280' : '#ef4444'

  const handleClick = () => {
    if (onClick) {
      onClick()
    } else {
      console.log('Clicked compact metric:', metric.name)
    }
  }

  return (
    <div
      className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors cursor-pointer group"
      onClick={handleClick}
    >
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{metric?.name || 'Unknown'}</p>
        <p className="text-xs text-muted-foreground">
          {metric?.source || 'FRED'}
        </p>
      </div>

      <div className="flex items-center gap-3">
        <div className="text-right">
          <p className="text-lg font-bold metric-value">
            {formatNumber(metric?.value ?? 0)}
          </p>
          <p
            className={cn(
              'text-xs font-medium',
              isPositive && 'text-green-500',
              isNeutral && 'text-gray-500',
              !isPositive && !isNeutral && 'text-red-500'
            )}
          >
            {formatPercent(metric?.changePercent ?? 0)}
          </p>
        </div>

        {metric?.historicalData && metric.historicalData.length > 0 && (
          <div className="w-16 h-8 flex-shrink-0">
            <SparkLine
              data={metric.historicalData}
              color={color}
            />
          </div>
        )}
      </div>
    </div>
  )
}
