import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { SparkLine } from '@/components/charts/SparkLine'
import { formatNumber, formatPercent } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus, Star } from 'lucide-react'
import type { EconomicIndicator } from '@/types'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'
import { useBookmarks } from '@/hooks/useBookmarks'
import { AnimatedNumber } from '@/components/ui/count-up'
import { toast } from 'sonner'

interface MetricCardProps {
  metric: EconomicIndicator
}

export function MetricCard({ metric }: MetricCardProps) {
  const { isBookmarked, toggleBookmark } = useBookmarks()

  if (!metric) {
    return null
  }

  const metricId = metric?.id || metric?.name || ''
  const bookmarked = isBookmarked(metricId)
  const isPositive = (metric?.change ?? 0) > 0
  const isNeutral = (metric?.change ?? 0) === 0
  const color = isPositive ? '#10b981' : isNeutral ? '#6b7280' : '#ef4444'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -4 }}
    >
      <Card
        className={cn(
          "group relative overflow-hidden transition-all duration-200",
          "bg-gradient-to-br from-card to-card/80",
          "hover:from-card hover:to-accent/5",
          "hover:border-primary/50 hover:shadow-lg hover:shadow-primary/10",
          "cursor-pointer",
          "card-hover"
        )}
        onClick={() => {
          toast.info(metric?.name || 'Metric Details', {
            description: metric?.description || 'View full metric details',
            duration: 3000,
          })
        }}
      >
        {/* Bookmark/Save button */}
        <button
          className={cn(
            "absolute top-2 right-2 h-6 w-6 z-10 transition-all flex items-center justify-center",
            "hover:scale-110 active:scale-95",
            bookmarked ? "opacity-100" : "opacity-0 group-hover:opacity-100",
            bookmarked ? "text-yellow-500" : "text-muted-foreground hover:text-foreground"
          )}
          onClick={(e) => {
            e.stopPropagation()
            toggleBookmark(metricId)
            toast.success(
              bookmarked ? 'Removed from favorites' : 'Added to favorites',
              {
                description: metric?.name,
                duration: 2000,
              }
            )
          }}
        >
          <Star className={cn("h-4 w-4 transition-all", bookmarked && "fill-current")} />
        </button>

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
          {metric?.name || 'Unknown Metric'}
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4 pl-5">
        <div className="flex items-end justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="text-3xl font-bold tracking-tight metric-value mb-1">
              <AnimatedNumber
                value={metric?.value ?? 0}
                formatValue={(val) => formatNumber(val)}
              />
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
              <span className="metric-value">{formatPercent(metric?.changePercent ?? 0)}</span>
            </div>
          </div>

          {metric?.historicalData && metric.historicalData.length > 0 && (
            <div className="w-20 h-12 flex-shrink-0">
              <SparkLine data={metric.historicalData} color={color} />
            </div>
          )}
        </div>

        {metric?.description && (
          <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
            {metric.description}
          </p>
        )}

        {metric?.lastUpdated && (
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground/70">
              Updated {new Date(metric.lastUpdated).toLocaleTimeString()}
            </span>
            {metric?.source && (
              <span className="text-muted-foreground/50 text-[10px] uppercase tracking-wider">
                {metric.source}
              </span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
    </motion.div>
  )
}
