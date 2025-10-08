import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { LineChart, Line, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, Info, AlertCircle } from 'lucide-react'
import { dailyMetricsService } from '@/services/dailyMetricsService'
import ChartModal from '@/components/charts/ChartModal'
import { cn } from '@/lib/utils'

interface BigMetricCardProps {
  metricCode: string
}

interface MetricDisplayData {
  code: string
  display_name: string
  unit: string
  latest_value: number
  change_percent: number
  sparkline_data: Array<{ date: string; value: number }>
}

export function BigMetricCard({ metricCode }: BigMetricCardProps) {
  const [metric, setMetric] = useState<MetricDisplayData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  useEffect(() => {
    fetchMetric()
  }, [metricCode])

  const fetchMetric = async () => {
    setLoading(true)
    setError(null)
    try {
      // Fetch historical data to get the latest value
      const response = await dailyMetricsService.getHistoricalMetrics(metricCode, '5y')

      if (response.data && response.data.length > 0) {
        // Get the latest data point
        const latestValue = response.data[response.data.length - 1].value

        // Calculate change by comparing last 2 data points
        let changePercent = 0
        if (response.data.length >= 2) {
          const previousValue = response.data[response.data.length - 2].value
          if (previousValue !== 0) {
            changePercent = ((latestValue - previousValue) / previousValue) * 100
          }
        }

        // Get sparkline data (last 30 data points)
        const sparklineData = response.data.slice(-30)

        setMetric({
          code: response.code,
          display_name: response.display_name,
          unit: response.unit,
          latest_value: latestValue,
          change_percent: changePercent,
          sparkline_data: sparklineData,
        })
      } else {
        setError('No data available')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load metric')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card className="overflow-hidden">
        <CardHeader className="pb-3">
          <Skeleton className="h-5 w-32" />
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-10 w-24" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-6 w-20" />
        </CardContent>
      </Card>
    )
  }

  if (error || !metric) {
    return (
      <Card className="overflow-hidden border-destructive/50">
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">{error || 'Failed to load'}</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  const changePercent = metric.change_percent
  const isPositive = changePercent > 0
  const isNeutral = Math.abs(changePercent) < 0.01

  return (
    <>
      <Card
        className="overflow-hidden hover:border-primary/50 transition-all duration-200 hover:shadow-lg cursor-pointer group"
        onClick={() => setModalOpen(true)}
      >
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center justify-between gap-2">
            <span className="text-sm font-semibold text-muted-foreground truncate leading-snug">
              {metric.display_name}
            </span>
            <Info className="h-4 w-4 text-muted-foreground shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 pt-0">
          {/* Current Value */}
          <div className="space-y-2">
            <div className="text-3xl font-bold tabular-nums tracking-tight leading-none">
              {metric.latest_value.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
              <span className="text-sm font-medium text-muted-foreground ml-2">
                {metric.unit}
              </span>
            </div>
            {/* Change Indicator */}
            <div className="flex items-center gap-2 min-h-[20px]">
              {!isNeutral && (
                <div
                  className={cn(
                    'flex items-center gap-1.5 text-sm font-semibold',
                    isPositive ? 'text-green-600 dark:text-green-500' : 'text-red-600 dark:text-red-500'
                  )}
                >
                  {isPositive ? (
                    <TrendingUp className="h-4 w-4" />
                  ) : (
                    <TrendingDown className="h-4 w-4" />
                  )}
                  <span>
                    {isPositive ? '+' : ''}
                    {changePercent.toFixed(2)}%
                  </span>
                </div>
              )}
              <span className="text-xs text-muted-foreground font-medium">vs previous</span>
            </div>
          </div>

          {/* Sparkline */}
          <div className="h-20 -mx-2">
            {metric.sparkline_data && metric.sparkline_data.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metric.sparkline_data}>
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke={isPositive ? '#16a34a' : isNeutral ? '#6366f1' : '#dc2626'}
                    strokeWidth={2.5}
                    dot={false}
                    animationDuration={300}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-muted-foreground bg-muted/30 rounded">
                No sparkline data
              </div>
            )}
          </div>

          {/* View Details Button */}
          <div className="flex items-center justify-end gap-2 pt-1">
            <Button
              variant="ghost"
              size="sm"
              className="text-xs h-8 px-3 font-medium opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={(e) => {
                e.stopPropagation()
                setModalOpen(true)
              }}
            >
              Details
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Chart Modal */}
      <ChartModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        metricCode={metric.code}
        metricName={metric.display_name}
      />
    </>
  )
}
