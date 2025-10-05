import { useEffect, useState, useMemo, useCallback } from 'react'
import { useData } from '@/hooks/useData'
import { useBookmarks } from '@/hooks/useBookmarks'
import { useSettings } from '@/hooks/useSettings'
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { Layout } from '@/components/layout/Layout'
import { TodayFeed } from '@/components/dashboard/TodayFeed'
import { BreakingNews } from '@/components/dashboard/BreakingNews'
import { WeeklySummary } from '@/components/dashboard/WeeklySummary'
import { MetricCard } from '@/components/dashboard/MetricCard'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { ProgressBar } from '@/components/ui/progress-bar'
import { OnboardingTour } from '@/components/onboarding/OnboardingTour'
import { PageTransition } from '@/components/ui/page-transition'
import { RefreshCw, Clock, Star } from 'lucide-react'
import { toast, Toaster } from 'sonner'
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
  const {
    showTodayFeed,
    showFavorites,
    showMetrics,
    showBreakingNews,
    showWeeklySummary,
    refreshInterval,
  } = useSettings()
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  // Combine all metrics from all sources (for Favorites)
  const allMetrics = useMemo(() => {
    const combined: EconomicIndicator[] = []
    const seenIds = new Set<string>()

    // Add from Today Feed
    if (todayFeed?.indicators) {
      todayFeed.indicators.forEach(metric => {
        const id = metric?.id || metric?.name || ''
        if (id && !seenIds.has(id)) {
          combined.push(metric)
          seenIds.add(id)
        }
      })
    }

    // Add from Additional Metrics (only if not already added)
    if (metrics?.metrics) {
      metrics.metrics.forEach(metric => {
        const id = metric?.id || metric?.name || ''
        if (id && !seenIds.has(id)) {
          combined.push(metric)
          seenIds.add(id)
        }
      })
    }

    return combined
  }, [todayFeed, metrics])

  // Filter bookmarked metrics (unique)
  const bookmarkedMetrics = useMemo(() => {
    const uniqueBookmarked: EconomicIndicator[] = []
    const seenIds = new Set<string>()

    allMetrics.forEach((metric) => {
      const metricId = metric?.id || metric?.name || ''
      if (metricId && bookmarkedIds.has(metricId) && !seenIds.has(metricId)) {
        uniqueBookmarked.push(metric)
        seenIds.add(metricId)
      }
    })

    return uniqueBookmarked
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

  // Auto-refresh based on settings
  useEffect(() => {
    if (refreshInterval === 0) return // Manual refresh only

    const intervalMs = refreshInterval * 60 * 1000
    const intervalId = setInterval(() => {
      fetchAll()
      setLastRefresh(new Date())
      toast.success('Dashboard refreshed', {
        description: 'All data has been updated',
        duration: 2000,
      })
    }, intervalMs)

    return () => clearInterval(intervalId)
  }, [fetchAll, refreshInterval])

  const handleRefresh = useCallback(() => {
    fetchAll()
    setLastRefresh(new Date())
    toast.success('Refreshing dashboard...', {
      description: 'Fetching latest data',
      duration: 2000,
    })
  }, [fetchAll])

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onRefresh: handleRefresh,
  })

  return (
    <Layout>
      <ProgressBar isLoading={isLoading} />
      <Toaster position="top-right" richColors />
      <OnboardingTour />

      <PageTransition>
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
                title="Refresh (Press R)"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>

          {showTodayFeed && (
            <div id="today-feed">
              <TodayFeed
                data={todayFeed}
                isLoading={isLoading}
                error={error}
                onRefresh={handleRefresh}
              />
            </div>
          )}

          {showFavorites && bookmarkedMetrics.length > 0 && (
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

          {showMetrics && (
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
          )}

          {showBreakingNews && (
            <BreakingNews data={breakingNews} isLoading={isLoading} />
          )}

          {showWeeklySummary && (
            <WeeklySummary data={weeklySummary} isLoading={isLoading} />
          )}
        </div>
      </PageTransition>
    </Layout>
  )
}
