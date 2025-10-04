import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { SparkLine } from '@/components/charts/SparkLine'
import { formatNumber, formatPercent } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import type { EconomicIndicator } from '@/types'
import { cn } from '@/lib/utils'

interface MetricCardProps {
  metric: EconomicIndicator
}

export function MetricCard({ metric }: MetricCardProps) {
  const isPositive = metric.change > 0
  const isNeutral = metric.change === 0
  const color = isPositive ? '#10b981' : isNeutral ? '#6b7280' : '#ef4444'

  return (
    <Card className="group relative overflow-hidden transition-all duration-200 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5">
      {/* Subtle accent bar on left */}
      <div
        className={cn(
          "absolute left-0 top-0 bottom-0 w-1 transition-all duration-200",
          isPositive && "bg-green-500",
          isNeutral && "bg-gray-500",
          !isPositive && !isNeutral && "bg-red-500"
        )}
      />

      <CardHeader className="pb-2 pl-5">
        <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          {metric.name}
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4 pl-5">
        <div className="flex items-end justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="text-3xl font-bold tracking-tight metric-value mb-1">
              {formatNumber(metric.value)}
            </div>
            <div
              className={cn(
                'inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-semibold transition-colors',
                isPositive && 'bg-green-500/10 text-green-500',
                isNeutral && 'bg-gray-500/10 text-gray-500',
                !isPositive && !isNeutral && 'bg-red-500/10 text-red-500'
              )}
            >
              {isPositive ? (
                <TrendingUp className="h-3.5 w-3.5" />
              ) : isNeutral ? (
                <Minus className="h-3.5 w-3.5" />
              ) : (
                <TrendingDown className="h-3.5 w-3.5" />
              )}
              <span className="metric-value">{formatPercent(metric.changePercent)}</span>
            </div>
          </div>

          {metric.historicalData && metric.historicalData.length > 0 && (
            <div className="w-20 h-12 flex-shrink-0">
              <SparkLine data={metric.historicalData} color={color} />
            </div>
          )}
        </div>

        {metric.description && (
          <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
            {metric.description}
          </p>
        )}

        {metric.lastUpdated && (
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground/70">
              Updated {new Date(metric.lastUpdated).toLocaleTimeString()}
            </span>
            {metric.source && (
              <span className="text-muted-foreground/50 text-[10px] uppercase tracking-wider">
                {metric.source}
              </span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
