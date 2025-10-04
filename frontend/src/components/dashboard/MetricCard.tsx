import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { SparkLine } from '@/components/charts/SparkLine'
import { formatNumber, formatPercent } from '@/lib/utils'
import { TrendingUp, TrendingDown } from 'lucide-react'
import type { EconomicIndicator } from '@/types'
import { cn } from '@/lib/utils'

interface MetricCardProps {
  metric: EconomicIndicator
}

export function MetricCard({ metric }: MetricCardProps) {
  const isPositive = metric.change >= 0
  const color = isPositive ? '#10b981' : '#ef4444'

  return (
    <Card className="transition-all hover:shadow-lg hover:-translate-y-1">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {metric.name}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-end justify-between">
          <div>
            <div className="text-2xl font-bold">
              {formatNumber(metric.value)}
            </div>
            <div
              className={cn(
                'flex items-center gap-1 text-sm font-medium',
                isPositive ? 'text-green-500' : 'text-red-500'
              )}
            >
              {isPositive ? (
                <TrendingUp className="h-4 w-4" />
              ) : (
                <TrendingDown className="h-4 w-4" />
              )}
              <span>{formatPercent(metric.changePercent)}</span>
            </div>
          </div>
          {metric.historicalData && metric.historicalData.length > 0 && (
            <div className="w-24">
              <SparkLine data={metric.historicalData} color={color} />
            </div>
          )}
        </div>
        {metric.description && (
          <p className="text-xs text-muted-foreground line-clamp-2">
            {metric.description}
          </p>
        )}
        {metric.lastUpdated && (
          <p className="text-xs text-muted-foreground">
            Updated {new Date(metric.lastUpdated).toLocaleTimeString()}
          </p>
        )}
      </CardContent>
    </Card>
  )
}
