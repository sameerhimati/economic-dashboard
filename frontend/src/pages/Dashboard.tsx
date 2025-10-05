import { useEffect, useState, useMemo } from 'react'
import { useData } from '@/hooks/useData'
import { useBookmarks } from '@/hooks/useBookmarks'
import { Layout } from '@/components/layout/Layout'
import { TodayFeed } from '@/components/dashboard/TodayFeed'
import { BreakingNews } from '@/components/dashboard/BreakingNews'
import { WeeklySummary } from '@/components/dashboard/WeeklySummary'
import { MetricCard } from '@/components/dashboard/MetricCard'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { RefreshCw, Clock, Star } from 'lucide-react'
import type { EconomicIndicator } from '@/types'

export function Dashboard() {
  const {
    todayFeed,
    metrics,
    breakingNews,
    weeklySummary,
    isLoading,
    error,
    fetchAll,
  } = useData()

  const { bookmarkedIds } = useBookmarks()
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  // Combine all metrics from all sources
  const allMetrics = useMemo(() => {
    const combined: EconomicIndicator[] = []
    if (todayFeed?.indicators) combined.push(...todayFeed.indicators)
    if (metrics?.metrics) combined.push(...metrics.metrics)
    return combined
  }, [todayFeed, metrics])

  // Filter bookmarked metrics
  const bookmarkedMetrics = useMemo(() => {
    return allMetrics.filter((metric) => {
      const metricId = metric?.id || metric?.name || ''
      return bookmarkedIds.has(metricId)
    })
  }, [allMetrics, bookmarkedIds])

  // Filter non-bookmarked metrics for Additional Metrics section
  const nonBookmarkedMetrics = useMemo(() => {
    if (!metrics?.metrics) return []
    return metrics.metrics.filter((metric) => {
      const metricId = metric?.id || metric?.name || ''
      return !bookmarkedIds.has(metricId)
    })
  }, [metrics, bookmarkedIds])

  useEffect(() => {
    fetchAll()
    setLastRefresh(new Date())
  }, [])

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const REFRESH_INTERVAL = 5 * 60 * 1000 // 5 minutes in milliseconds

    const intervalId = setInterval(() => {
      fetchAll()
      setLastRefresh(new Date())
    }, REFRESH_INTERVAL)

    return () => clearInterval(intervalId)
  }, [fetchAll])

  const handleRefresh = () => {
    fetchAll()
    setLastRefresh(new Date())
  }

  return (
    <Layout>
      <div className="space-y-12">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Economic Dashboard</h1>
            <p className="text-muted-foreground mt-1 flex items-center gap-2">
              <span>Your comprehensive view of economic indicators and market insights</span>
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-xs text-muted-foreground flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5" />
              <span>Last refresh: {lastRefresh.toLocaleTimeString()}</span>
            </div>
            <Button
              onClick={handleRefresh}
              disabled={isLoading}
              variant="outline"
              size="sm"
              className="gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        <TodayFeed
          data={todayFeed}
          isLoading={isLoading}
          error={error}
          onRefresh={handleRefresh}
        />

        {bookmarkedMetrics.length > 0 && (
          <div id="favorites" className="animate-fade-in border-t pt-12">
            <div className="flex items-center gap-3 mb-4">
              <Star className="h-6 w-6 text-yellow-500 fill-yellow-500" />
              <div>
                <h2 className="text-3xl font-bold tracking-tight">Favorites</h2>
                <p className="text-sm text-muted-foreground">
                  Your bookmarked metrics for quick access
                </p>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {bookmarkedMetrics.map((metric, index) => (
                <div
                  key={metric?.id || metric?.name || `favorite-${index}`}
                  className="animate-slide-up"
                  style={{ animationDelay: `${index * 30}ms` }}
                >
                  <MetricCard metric={metric} />
                </div>
              ))}
            </div>
          </div>
        )}

        <div id="metrics">
          {isLoading && !metrics ? (
            <div className="space-y-4">
              <Skeleton className="h-8 w-48" />
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <Skeleton key={i} className="h-48" />
                ))}
              </div>
            </div>
          ) : nonBookmarkedMetrics.length > 0 ? (
            <div className="space-y-4 animate-fade-in border-t pt-12">
              <div>
                <h2 className="text-3xl font-bold tracking-tight">Additional Metrics</h2>
                <p className="text-sm text-muted-foreground">
                  Extended economic indicators and data points
                </p>
              </div>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {nonBookmarkedMetrics.map((metric, index) => (
                  <div
                    key={metric?.id || `metric-${index}`}
                    className="animate-slide-up"
                    style={{ animationDelay: `${index * 30}ms` }}
                  >
                    <MetricCard metric={metric} />
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>

        <BreakingNews data={breakingNews} isLoading={isLoading} />

        <WeeklySummary data={weeklySummary} isLoading={isLoading} />
      </div>
    </Layout>
  )
}
