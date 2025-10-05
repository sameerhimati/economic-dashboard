import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatNumber, formatPercent } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import type { EconomicIndicator } from '@/types'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'

interface MetricCardComparisonProps {
  metric: EconomicIndicator
  previousValue?: number
  comparisonLabel?: string
  previousLabel?: string
}

export function MetricCardComparison({
  metric,
  previousValue,
  comparisonLabel = 'This Week',
  previousLabel = 'Last Week',
}: MetricCardComparisonProps) {
  if (!metric) return null

  const currentValue = metric?.value ?? 0
  const lastWeekValue = previousValue ?? currentValue
  const weekOverWeekChange = currentValue - lastWeekValue
  const weekOverWeekPercent = lastWeekValue !== 0
    ? ((weekOverWeekChange / lastWeekValue) * 100)
    : 0

  const isPositive = weekOverWeekChange > 0
  const isNeutral = weekOverWeekChange === 0

  return (
    <Card className="overflow-hidden hover:shadow-lg transition-all duration-200 cursor-pointer group">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          {metric?.name}
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          {/* This Week */}
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {comparisonLabel}
            </p>
            <motion.p
              className="text-2xl font-bold metric-value"
              initial={{ scale: 1 }}
              animate={{ scale: 1 }}
              key={currentValue}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              {formatNumber(currentValue)}
            </motion.p>
          </div>

          {/* Last Week */}
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {previousLabel}
            </p>
            <p className="text-2xl font-bold metric-value text-muted-foreground/60">
              {formatNumber(lastWeekValue)}
            </p>
          </div>
        </div>

        {/* Change */}
        <div className="pt-3 border-t">
          <div
            className={cn(
              'inline-flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-semibold',
              isPositive && 'bg-green-500/10 text-green-500',
              isNeutral && 'bg-gray-500/10 text-gray-500',
              !isPositive && !isNeutral && 'bg-red-500/10 text-red-500'
            )}
          >
            {isPositive ? (
              <TrendingUp className="h-4 w-4" />
            ) : isNeutral ? (
              <Minus className="h-4 w-4" />
            ) : (
              <TrendingDown className="h-4 w-4" />
            )}
            <span className="metric-value">
              {formatPercent(weekOverWeekPercent)} vs {previousLabel.toLowerCase()}
            </span>
          </div>
        </div>

        {/* Description */}
        {metric?.description && (
          <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed pt-2">
            {metric.description}
          </p>
        )}

        {/* Footer */}
        {metric?.lastUpdated && (
          <div className="text-xs text-muted-foreground/70 pt-2 border-t">
            Updated {new Date(metric.lastUpdated).toLocaleTimeString()}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
