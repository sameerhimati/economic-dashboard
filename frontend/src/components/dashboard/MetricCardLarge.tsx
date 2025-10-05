import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { LineChart } from '@/components/charts/LineChart'
import { formatNumber, formatPercent } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus, Star } from 'lucide-react'
import type { EconomicIndicator } from '@/types'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'

interface MetricCardLargeProps {
  metric: EconomicIndicator
  featured?: boolean
}

export function MetricCardLarge({ metric, featured = false }: MetricCardLargeProps) {
  if (!metric) return null

  const isPositive = (metric?.change ?? 0) > 0
  const isNeutral = (metric?.change ?? 0) === 0
  const color = isPositive ? '#10b981' : isNeutral ? '#6b7280' : '#ef4444'

  return (
    <Card
      className={cn(
        "relative overflow-hidden transition-all duration-300",
        "bg-gradient-to-br from-card via-card to-accent/5",
        "hover:shadow-2xl hover:shadow-primary/20",
        "cursor-pointer border-2",
        featured && "ring-2 ring-primary/20",
        "group"
      )}
      onClick={() => {
        console.log('Clicked large metric:', metric.name)
      }}
    >
      {/* Bookmark button */}
      <Button
        variant="ghost"
        size="icon"
        className="absolute top-4 right-4 h-8 w-8 z-10 opacity-0 group-hover:opacity-100 transition-opacity"
        onClick={(e) => {
          e.stopPropagation()
          console.log('Bookmarked:', metric.name)
        }}
      >
        <Star className="h-4 w-4" />
      </Button>

      {/* Accent bar */}
      <div
        className={cn(
          "absolute left-0 top-0 bottom-0 w-2",
          isPositive && "bg-green-500",
          isNeutral && "bg-gray-500",
          !isPositive && !isNeutral && "bg-red-500"
        )}
      />

      <CardHeader className="pb-3 pl-6">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          {metric?.name || 'Unknown Metric'}
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-6 pl-6">
        {/* Value and Change */}
        <div className="space-y-2">
          <motion.div
            className="text-5xl font-bold tracking-tight metric-value"
            initial={{ scale: 1 }}
            animate={{ scale: 1 }}
            key={metric?.value}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
          >
            {formatNumber(metric?.value ?? 0)}
          </motion.div>

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
            <span className="metric-value">{formatPercent(metric?.changePercent ?? 0)}</span>
          </div>
        </div>

        {/* Full chart instead of sparkline */}
        {metric?.historicalData && metric.historicalData.length > 0 && (
          <div className="h-32">
            <LineChart
              data={metric.historicalData}
              color={color}
            />
          </div>
        )}

        {/* Description */}
        {metric?.description && (
          <p className="text-sm text-muted-foreground leading-relaxed">
            {metric.description}
          </p>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between text-xs pt-4 border-t">
          <span className="text-muted-foreground/70">
            Updated {metric?.lastUpdated ? new Date(metric.lastUpdated).toLocaleTimeString() : 'Unknown'}
          </span>
          {metric?.source && (
            <span className="text-muted-foreground/50 text-[10px] uppercase tracking-wider">
              {metric.source}
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
