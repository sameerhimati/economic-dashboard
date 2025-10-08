import { useState, useEffect, useMemo, lazy, Suspense } from 'react'
import { Layout } from '@/components/layout/Layout'
import { PageTransition } from '@/components/ui/page-transition'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { MetricCard } from '@/components/daily/MetricCard'
import { WeeklyReflection } from '@/components/daily/WeeklyReflection'
import { dailyMetricsService } from '@/services/dailyMetricsService'
import type { DailyMetricsResponse, DailyMetricData } from '@/types/dailyMetrics'
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  TrendingDown,
  AlertCircle,
} from 'lucide-react'
import { format, addDays, subDays, isAfter } from 'date-fns'
import { toast } from 'sonner'

const ChartModal = lazy(() => import('@/components/charts/ChartModal'))

export function TodaysFocus() {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [data, setData] = useState<DailyMetricsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedMetric, setSelectedMetric] = useState<DailyMetricData | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  const isWeekend = useMemo(() => {
    const weekday = currentDate.getDay()
    return weekday === 0 || weekday === 6
  }, [currentDate])

  const isFutureDate = isAfter(currentDate, new Date())

  useEffect(() => {
    fetchDailyMetrics()
  }, [currentDate])

  const fetchDailyMetrics = async () => {
    setLoading(true)
    try {
      const dateStr = format(currentDate, 'yyyy-MM-dd')
      const response = await dailyMetricsService.getDailyMetrics(dateStr)
      setData(response)
    } catch (error) {
      console.error('Error fetching daily metrics:', error)
      toast.error('Failed to load metrics', {
        description: 'Please try again later',
      })
    } finally {
      setLoading(false)
    }
  }

  const handlePreviousDay = () => {
    setCurrentDate(subDays(currentDate, 1))
  }

  const handleNextDay = () => {
    if (!isFutureDate) {
      setCurrentDate(addDays(currentDate, 1))
    }
  }

  const handleMetricClick = (metric: DailyMetricData) => {
    setSelectedMetric(metric)
    setModalOpen(true)
  }

  return (
    <Layout>
      <PageTransition>
        <div className="space-y-6 sm:space-y-8">
          {/* Header with Date Navigation */}
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <Calendar className="h-8 w-8 text-primary" />
                <div>
                  <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">
                    Today's Focus
                  </h1>
                  <p className="text-sm sm:text-base text-muted-foreground mt-1">
                    Your daily economic intelligence briefing
                  </p>
                </div>
              </div>
            </div>

            {/* Date Navigation */}
            <div className="flex items-center justify-between gap-4 p-4 bg-accent/50 rounded-lg">
              <Button
                variant="outline"
                size="sm"
                onClick={handlePreviousDay}
                className="gap-2"
                aria-label="Previous day"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous Day
              </Button>

              <div className="text-center">
                <div className="text-lg font-semibold" aria-label={`Selected date: ${format(currentDate, 'EEEE, MMMM d, yyyy')}`}>
                  {format(currentDate, 'EEEE, MMMM d, yyyy')}
                </div>
                {isWeekend && (
                  <div className="text-xs text-muted-foreground mt-0.5">
                    Weekend Mode
                  </div>
                )}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={handleNextDay}
                disabled={isFutureDate}
                className="gap-2"
                aria-label="Next day"
              >
                Next Day
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Loading State */}
          {loading ? (
            <div className="space-y-6">
              <Skeleton className="h-32 w-full" />
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <Skeleton key={i} className="h-96" />
                ))}
              </div>
            </div>
          ) : isWeekend ? (
            <WeeklyReflection />
          ) : data ? (
            <>
              {/* Daily Summary Card */}
              <Card className="bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
                <CardHeader>
                  <CardTitle className="text-2xl">{data.theme}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-base leading-relaxed">{data.summary}</p>

                  <div className="flex items-center gap-6 text-sm">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      <span className="font-semibold text-green-600">
                        {data.metrics_up}
                      </span>
                      <span className="text-muted-foreground">up</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <TrendingDown className="h-4 w-4 text-red-600" />
                      <span className="font-semibold text-red-600">
                        {data.metrics_down}
                      </span>
                      <span className="text-muted-foreground">down</span>
                    </div>
                    {data.alerts_count > 0 && (
                      <div className="flex items-center gap-2">
                        <AlertCircle className="h-4 w-4 text-amber-600" />
                        <span className="font-semibold text-amber-600">
                          {data.alerts_count}
                        </span>
                        <span className="text-muted-foreground">alerts</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Empty State for No Metrics */}
              {data.metrics.length === 0 ? (
                <Card>
                  <CardContent className="pt-6 text-center py-12">
                    <p className="text-muted-foreground">
                      No metrics available for this date.
                    </p>
                  </CardContent>
                </Card>
              ) : (
                /* Metrics Grid */
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {data.metrics.map((metric) => (
                    <MetricCard
                      key={metric.code}
                      metric={metric}
                      onClick={handleMetricClick}
                    />
                  ))}
                </div>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                No data available for this date.
              </CardContent>
            </Card>
          )}
        </div>
      </PageTransition>

      {/* Chart Modal */}
      {selectedMetric && (
        <Suspense fallback={
          <div className="fixed inset-0 z-50 bg-background/95 backdrop-blur-sm flex items-center justify-center">
            <div className="text-muted-foreground">Loading chart...</div>
          </div>
        }>
          <ChartModal
            open={modalOpen}
            onOpenChange={setModalOpen}
            metricCode={selectedMetric.code}
            metricName={selectedMetric.display_name}
          />
        </Suspense>
      )}
    </Layout>
  )
}
