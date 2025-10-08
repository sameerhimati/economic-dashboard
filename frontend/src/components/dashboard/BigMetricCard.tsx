import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { LineChart, Line, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, Info, AlertCircle } from 'lucide-react'
import { dailyMetricsService } from '@/services/dailyMetricsService'
import type { DailyMetricData } from '@/types/dailyMetrics'
import ChartModal from '@/components/charts/ChartModal'
import { cn } from '@/lib/utils'

interface BigMetricCardProps {
  metricCode: string
}

export function BigMetricCard({ metricCode }: BigMetricCardProps) {
  const [metric, setMetric] = useState<DailyMetricData | null>(null)
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
      // Fetch today's metrics and find this specific metric
      const today = new Date().toISOString().split('T')[0]
      const response = await dailyMetricsService.getDailyMetrics(today)
      const foundMetric = response.metrics.find((m) => m.code === metricCode)

      if (foundMetric) {
        setMetric(foundMetric)
      } else {
        setError('Metric not found')
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

  const change1d = metric.changes.vs_yesterday
  const isPositive = change1d > 0
  const isNeutral = Math.abs(change1d) < 0.01

  return (
    <>
      <Card
        className="overflow-hidden hover:border-primary/50 transition-all duration-200 hover:shadow-lg cursor-pointer group"
        onClick={() => setModalOpen(true)}
      >
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between gap-2">
            <span className="text-sm font-medium text-muted-foreground truncate">
              {metric.display_name}
            </span>
            <Info className="h-4 w-4 text-muted-foreground shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Current Value */}
          <div className="space-y-1">
            <div className="text-3xl font-bold tabular-nums tracking-tight">
              {metric.latest_value.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
              <span className="text-sm font-normal text-muted-foreground ml-1.5">
                {metric.unit}
              </span>
            </div>
            {/* Change Indicator */}
            <div className="flex items-center gap-2">
              {!isNeutral && (
                <div
                  className={cn(
                    'flex items-center gap-1 text-sm font-medium',
                    isPositive ? 'text-green-600' : 'text-red-600'
                  )}
                >
                  {isPositive ? (
                    <TrendingUp className="h-3.5 w-3.5" />
                  ) : (
                    <TrendingDown className="h-3.5 w-3.5" />
                  )}
                  <span>
                    {isPositive ? '+' : ''}
                    {change1d.toFixed(2)}%
                  </span>
                </div>
              )}
              <span className="text-xs text-muted-foreground">vs yesterday</span>
            </div>
          </div>

          {/* Sparkline */}
          <div className="h-16 -mx-2">
            {metric.sparkline_data && metric.sparkline_data.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metric.sparkline_data}>
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke={isPositive ? '#16a34a' : isNeutral ? '#6366f1' : '#dc2626'}
                    strokeWidth={2}
                    dot={false}
                    animationDuration={300}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-muted-foreground">
                No sparkline data
              </div>
            )}
          </div>

          {/* Alerts & Status */}
          <div className="flex items-center justify-between gap-2">
            {metric.alerts && metric.alerts.length > 0 ? (
              <Badge variant="destructive" className="text-xs">
                {metric.alerts.length} Alert{metric.alerts.length > 1 ? 's' : ''}
              </Badge>
            ) : metric.significance.is_outlier ? (
              <Badge variant="secondary" className="text-xs">
                Outlier
              </Badge>
            ) : (
              <div />
            )}

            <Button
              variant="ghost"
              size="sm"
              className="text-xs h-7 opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={(e) => {
                e.stopPropagation()
                setModalOpen(true)
              }}
            >
              Learn More
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
