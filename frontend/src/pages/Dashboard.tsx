import { useEffect, useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { BigMetricCard } from '@/components/dashboard/BigMetricCard'
import { MetricCard } from '@/components/dashboard/MetricCard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { EmptyState } from '@/components/ui/empty-state'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { PageTransition } from '@/components/ui/page-transition'
import { ProgressBar } from '@/components/ui/progress-bar'
import {
  AlertTriangle,
  ArrowRight,
  Calendar,
  BarChart3,
  Sparkles,
  ServerCrash,
} from 'lucide-react'
import { toast, Toaster } from 'sonner'
import { dailyMetricsService } from '@/services/dailyMetricsService'
import type { DailyMetricsResponse, DailyMetricData } from '@/types/dailyMetrics'
import {
  BIG_FIVE_METRICS,
  WEEKDAY_THEMES,
  getMetricsForWeekday,
  CATEGORY_INFO,
} from '@/data/weekdayThemes'

export function Dashboard() {
  const navigate = useNavigate()
  const [metrics, setMetrics] = useState<DailyMetricsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDailyMetrics()
  }, [])

  const fetchDailyMetrics = async () => {
    setLoading(true)
    setError(null)
    try {
      const today = new Date().toISOString().split('T')[0]
      const response = await dailyMetricsService.getDailyMetrics(today)
      setMetrics(response)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to load dashboard data'
      setError(errorMessage)
      toast.error('Failed to load data', {
        description: errorMessage,
      })
    } finally {
      setLoading(false)
    }
  }

  // Group metrics by category
  const metricsByCategory = useMemo(() => {
    if (!metrics) return {}

    const grouped: Record<string, DailyMetricData[]> = {}

    Object.entries(WEEKDAY_THEMES).forEach(([weekday, theme]) => {
      const weekdayNum = Number(weekday)
      if (weekdayNum >= 5) return // Skip weekend themes

      const metricCodes = getMetricsForWeekday(weekdayNum)
      const categoryMetrics = metrics.metrics.filter((m) =>
        metricCodes.includes(m.code)
      )

      if (categoryMetrics.length > 0) {
        grouped[theme] = categoryMetrics
      }
    })

    return grouped
  }, [metrics])

  // Get today's highlights
  const todaysHighlights = useMemo(() => {
    if (!metrics) return []

    const highlights: string[] = []

    // Add high-change metrics
    const topMovers = [...metrics.metrics]
      .sort((a, b) => Math.abs(b.changes.vs_yesterday) - Math.abs(a.changes.vs_yesterday))
      .slice(0, 3)

    topMovers.forEach((metric) => {
      const change = metric.changes.vs_yesterday
      if (Math.abs(change) > 1) {
        const direction = change > 0 ? 'up' : 'down'
        highlights.push(
          `${metric.display_name} ${direction} ${Math.abs(change).toFixed(1)}% - ${metric.context}`
        )
      }
    })

    // Add alerts
    metrics.metrics.forEach((metric) => {
      if (metric.alerts && metric.alerts.length > 0) {
        highlights.push(...metric.alerts.map((alert) => `${metric.display_name}: ${alert}`))
      }
    })

    return highlights.slice(0, 5)
  }, [metrics])

  return (
    <Layout>
      <ProgressBar isLoading={loading} />
      <Toaster position="top-right" richColors />

      <PageTransition>
        <div className="space-y-8">
          {/* Hero Section - Economic Pulse */}
          <div className="space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                  Economic Command Center
                </h1>
                <p className="text-base sm:text-lg text-muted-foreground mt-2">
                  Real-time insights into the U.S. economy
                </p>
              </div>
            </div>

            {/* Dashboard Summary Cards */}
            {loading ? (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Skeleton className="h-28" />
                <Skeleton className="h-28" />
                <Skeleton className="h-28" />
              </div>
            ) : metrics ? (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card className="bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20 hover:border-primary/30 transition-colors">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <p className="text-sm font-medium text-muted-foreground">Total Metrics</p>
                        <div className="flex items-baseline gap-2">
                          <span className="text-3xl font-bold tracking-tight">
                            {metrics.metrics.length}
                          </span>
                          <span className="text-sm text-muted-foreground">tracked</span>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Across {Object.keys(CATEGORY_INFO).length} categories
                        </p>
                      </div>
                      <BarChart3 className="h-10 w-10 text-primary/50" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 border-blue-500/20 hover:border-blue-500/30 transition-colors">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <p className="text-sm font-medium text-muted-foreground">Data Date</p>
                        <div className="flex items-baseline gap-2">
                          <span className="text-xl font-bold tracking-tight">
                            {new Date(metrics.date).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric',
                            })}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][metrics.weekday]}
                        </p>
                      </div>
                      <Calendar className="h-10 w-10 text-blue-500/50" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-amber-500/10 to-amber-500/5 border-amber-500/20 hover:border-amber-500/30 transition-colors">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <p className="text-sm font-medium text-muted-foreground">Active Alerts</p>
                        <div className="flex items-baseline gap-2">
                          <span className="text-3xl font-bold tracking-tight text-amber-600 dark:text-amber-500">
                            {metrics.alerts_count}
                          </span>
                          <span className="text-sm text-muted-foreground">signals</span>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Monitoring {metrics.metrics_up + metrics.metrics_down} changes
                        </p>
                      </div>
                      <AlertTriangle className="h-10 w-10 text-amber-500/50" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : null}
          </div>

          {/* The Big 5 - Core Economic Indicators */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
                  The Big 5
                </h2>
                <p className="text-sm text-muted-foreground">
                  Core economic indicators - the pulse of the economy
                </p>
              </div>
              <Badge variant="secondary" className="gap-1">
                <Calendar className="h-3 w-3" />
                Live
              </Badge>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-48" />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                {BIG_FIVE_METRICS.map((code) => (
                  <BigMetricCard key={code} metricCode={code} />
                ))}
              </div>
            )}
          </div>

          {/* Today's Highlights */}
          {!loading && todaysHighlights.length > 0 && (
            <Card className="border-primary/20 bg-primary/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  Today's Highlights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {todaysHighlights.map((highlight, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm">
                      <span className="text-primary mt-0.5">•</span>
                      <span>{highlight}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Category Sections - Collapsible */}
          {!loading && Object.keys(metricsByCategory).length > 0 && (
            <div className="space-y-4">
              <div>
                <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
                  All Indicators by Category
                </h2>
                <p className="text-sm text-muted-foreground">
                  Explore the full economic picture
                </p>
              </div>

              <Accordion type="multiple" className="space-y-4">
                {Object.entries(metricsByCategory).map(([category, categoryMetrics]) => {
                  const info = CATEGORY_INFO[category as keyof typeof CATEGORY_INFO]
                  return (
                    <AccordionItem
                      key={category}
                      value={category}
                      className="border rounded-lg px-4 bg-card"
                    >
                      <AccordionTrigger className="hover:no-underline py-4">
                        <div className="flex items-center gap-3 text-left">
                          {info && (
                            <span className="text-2xl shrink-0">{info.icon}</span>
                          )}
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <h3 className="text-lg font-semibold">{category}</h3>
                              <Badge variant="outline">
                                {categoryMetrics.length} metric{categoryMetrics.length > 1 ? 's' : ''}
                              </Badge>
                            </div>
                            {info && (
                              <p className="text-sm text-muted-foreground mt-0.5">
                                {info.description}
                              </p>
                            )}
                          </div>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="pb-4">
                        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 pt-4">
                          {categoryMetrics.map((metric, index) => (
                            <div
                              key={metric.code}
                              className="animate-slide-up"
                              style={{ animationDelay: `${index * 30}ms` }}
                            >
                              <MetricCard
                                metric={{
                                  id: metric.code,
                                  name: metric.display_name,
                                  value: metric.latest_value,
                                  change: metric.changes.vs_yesterday,
                                  sparkline: metric.sparkline_data.map((d) => d.value),
                                  description: metric.description,
                                  unit: metric.unit,
                                }}
                              />
                            </div>
                          ))}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  )
                })}
              </Accordion>
            </div>
          )}

          {/* Quick Actions */}
          <Card className="bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-semibold mb-1">
                    Want a deeper dive?
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Explore focused daily themes and weekly trends
                  </p>
                </div>
                <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full sm:w-auto">
                  <Button onClick={() => navigate('/focus')} className="gap-2 h-10 w-full sm:w-auto" size="default">
                    <span className="truncate">Today's Focus</span>
                    <ArrowRight className="h-4 w-4 shrink-0" />
                  </Button>
                  <Button variant="outline" onClick={() => navigate('/trends')} size="default" className="h-10 w-full sm:w-auto">
                    <span className="truncate">Weekly Trends</span>
                  </Button>
                  <Button variant="outline" onClick={() => navigate('/metrics')} size="default" className="h-10 w-full sm:w-auto">
                    <span className="truncate">All Metrics</span>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Error State */}
          {error && !loading && (
            <EmptyState
              icon={ServerCrash}
              title="Failed to load dashboard"
              description={error || 'An unexpected error occurred while loading the dashboard data. Please try again.'}
              action={{
                label: 'Retry',
                onClick: fetchDailyMetrics
              }}
            />
          )}
        </div>
      </PageTransition>
    </Layout>
  )
}
