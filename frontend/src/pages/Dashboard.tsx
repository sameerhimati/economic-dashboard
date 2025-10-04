import { useEffect } from 'react'
import { useData } from '@/hooks/useData'
import { Layout } from '@/components/layout/Layout'
import { TodayFeed } from '@/components/dashboard/TodayFeed'
import { BreakingNews } from '@/components/dashboard/BreakingNews'
import { WeeklySummary } from '@/components/dashboard/WeeklySummary'
import { MetricCard } from '@/components/dashboard/MetricCard'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { RefreshCw } from 'lucide-react'

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

  useEffect(() => {
    fetchAll()
  }, [])

  const handleRefresh = () => {
    fetchAll()
  }

  return (
    <Layout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Economic Dashboard</h1>
            <p className="text-muted-foreground mt-1">
              Your comprehensive view of economic indicators and market insights
            </p>
          </div>
          <Button onClick={handleRefresh} disabled={isLoading} variant="outline" size="sm">
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {error && (
          <Card className="border-destructive">
            <CardContent className="pt-6">
              <p className="text-destructive text-center">{error}</p>
            </CardContent>
          </Card>
        )}

        <TodayFeed data={todayFeed} isLoading={isLoading} />

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
          ) : metrics && metrics.metrics.length > 0 ? (
            <div className="space-y-4">
              <div>
                <h2 className="text-3xl font-bold tracking-tight">Key Metrics</h2>
                <p className="text-muted-foreground">
                  Important economic indicators at a glance
                </p>
              </div>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {metrics.metrics.map((metric) => (
                  <MetricCard key={metric.id} metric={metric} />
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
