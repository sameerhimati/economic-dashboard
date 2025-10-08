import { memo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { SparkLine } from '@/components/charts/SparkLine'
import { AlertCircle, TrendingUp, TrendingDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { DailyMetricData } from '@/types/dailyMetrics'

interface MetricCardProps {
  metric: DailyMetricData
  onClick: (metric: DailyMetricData) => void
}

export const MetricCard = memo(function MetricCard({ metric, onClick }: MetricCardProps) {
  const hasAlerts = metric.alerts && metric.alerts.length > 0

  return (
    <Card
      className={cn(
        'group relative overflow-hidden transition-all duration-200',
        'hover:shadow-lg hover:border-primary/50 cursor-pointer',
        'active:scale-[0.98]',
        'focus-within:ring-2 focus-within:ring-primary focus-within:ring-offset-2',
        hasAlerts && 'border-amber-600/50'
      )}
      onClick={() => onClick(metric)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick(metric)
        }
      }}
      aria-label={`View details for ${metric.display_name}. Current value: ${metric.latest_value} ${metric.unit}`}
    >
      {/* Outlier Badge */}
      {metric.significance.is_outlier && (
        <div className="absolute top-2 right-2 z-10">
          <Badge variant="outline" className="bg-purple-500/10 text-purple-600 border-purple-500/50">
            Outlier
          </Badge>
        </div>
      )}

      {/* Alert Banner */}
      {hasAlerts && (
        <div className="bg-amber-500/10 border-b border-amber-600/20 px-4 py-2">
          <div className="flex items-center gap-2 text-xs text-amber-700">
            <AlertCircle className="h-3.5 w-3.5 shrink-0" />
            <span className="font-medium line-clamp-1">{metric.alerts[0]}</span>
          </div>
        </div>
      )}

      <CardHeader className={cn('pb-2', metric.significance.is_outlier && 'pr-24')}>
        <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wider line-clamp-1">
          {metric.display_name}
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Current Value */}
        <div className="space-y-1">
          <div className="text-3xl font-bold tabular-nums">
            {metric.latest_value.toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
            <span className="text-lg text-muted-foreground ml-1">{metric.unit}</span>
          </div>
          <div className="text-xs text-muted-foreground">
            as of {new Date(metric.latest_date).toLocaleDateString()}
          </div>
        </div>

        {/* Change Indicators Grid */}
        <div className="grid grid-cols-2 gap-2">
          <ChangeIndicator label="1D" value={metric.changes.vs_yesterday} />
          <ChangeIndicator label="1W" value={metric.changes.vs_last_week} />
          <ChangeIndicator label="1M" value={metric.changes.vs_last_month} />
          <ChangeIndicator label="1Y" value={metric.changes.vs_last_year} />
        </div>

        {/* Context Text */}
        {metric.context && (
          <p className="text-xs text-muted-foreground italic leading-relaxed line-clamp-2">
            {metric.context}
          </p>
        )}

        {/* Sparkline */}
        {metric.sparkline_data && metric.sparkline_data.length > 0 && (
          <div className="pt-2 border-t">
            <SparkLine data={metric.sparkline_data} height={60} />
          </div>
        )}

        {/* Click Hint */}
        <div className="text-xs text-muted-foreground/70 text-center opacity-0 group-hover:opacity-100 transition-opacity">
          Click for detailed historical view
        </div>
      </CardContent>
    </Card>
  )
})

interface ChangeIndicatorProps {
  label: string
  value: number
}

function ChangeIndicator({ label, value }: ChangeIndicatorProps) {
  const isPositive = value > 0
  const isNeutral = value === 0

  return (
    <div
      className={cn(
        'flex items-center justify-between px-2 py-1.5 rounded-md text-xs font-medium',
        isPositive && 'bg-green-500/10 text-green-600',
        isNeutral && 'bg-gray-500/10 text-gray-600',
        !isPositive && !isNeutral && 'bg-red-500/10 text-red-600'
      )}
    >
      <span className="font-semibold">{label}</span>
      <div className="flex items-center gap-1">
        {!isNeutral && (isPositive ? (
          <TrendingUp className="h-3 w-3" />
        ) : (
          <TrendingDown className="h-3 w-3" />
        ))}
        <span className="tabular-nums">
          {isPositive && '+'}
          {value.toFixed(2)}%
        </span>
      </div>
    </div>
  )
}
