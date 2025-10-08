import { useState, useEffect, useMemo } from 'react'
import { Layout } from '@/components/layout/Layout'
import { Card, CardContent } from '@/components/ui/card'
import { PageTransition } from '@/components/ui/page-transition'
import { BarChart3, Calendar, Search, Filter, TrendingUp, TrendingDown } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { MetricCard } from '@/components/dashboard/MetricCard'
import { dailyMetricsService } from '@/services/dailyMetricsService'
import type { DailyMetricsResponse, DailyMetricData } from '@/types/dailyMetrics'
import { WEEKDAY_THEMES, getMetricsForWeekday, CATEGORY_INFO } from '@/data/weekdayThemes'
import { toast } from 'sonner'

type CategoryKey = keyof typeof CATEGORY_INFO

export function AllMetrics() {
  const [metrics, setMetrics] = useState<DailyMetricsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<'name' | 'change'>('name')

  useEffect(() => {
    fetchMetrics()
  }, [])

  const fetchMetrics = async () => {
    setLoading(true)
    try {
      const today = new Date().toISOString().split('T')[0]
      const response = await dailyMetricsService.getDailyMetrics(today)
      setMetrics(response)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to load metrics'
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

  // Filter and sort metrics
  const filteredMetrics = useMemo(() => {
    if (!metrics) return []

    let filtered = metrics.metrics

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (m) =>
          m.display_name.toLowerCase().includes(query) ||
          m.code.toLowerCase().includes(query) ||
          m.description.toLowerCase().includes(query)
      )
    }

    // Apply category filter
    if (selectedCategory) {
      const categoryMetricCodes = Object.entries(WEEKDAY_THEMES)
        .filter(([_, theme]) => theme === selectedCategory)
        .flatMap(([weekday]) => getMetricsForWeekday(Number(weekday)))

      filtered = filtered.filter((m) => categoryMetricCodes.includes(m.code))
    }

    // Apply sorting
    if (sortBy === 'name') {
      filtered = [...filtered].sort((a, b) =>
        a.display_name.localeCompare(b.display_name)
      )
    } else if (sortBy === 'change') {
      filtered = [...filtered].sort(
        (a, b) =>
          Math.abs(b.changes.vs_yesterday) - Math.abs(a.changes.vs_yesterday)
      )
    }

    return filtered
  }, [metrics, searchQuery, selectedCategory, sortBy])

  // Stats for the header
  const stats = useMemo(() => {
    if (!metrics) return { total: 0, up: 0, down: 0, alerts: 0 }
    return {
      total: metrics.metrics.length,
      up: metrics.metrics_up,
      down: metrics.metrics_down,
      alerts: metrics.alerts_count,
    }
  }, [metrics])

  return (
    <Layout>
      <PageTransition>
        <div className="space-y-8">
          {/* Hero Section */}
          <div className="space-y-4">
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div className="min-w-0 flex-1">
                <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                  All Economic Metrics
                </h1>
                <p className="text-base sm:text-lg text-muted-foreground mt-2">
                  Comprehensive view of all tracked economic indicators
                </p>
              </div>
              <Badge variant="secondary" className="gap-1 shrink-0">
                <Calendar className="h-3 w-3" />
                Live
              </Badge>
            </div>

            {/* Quick Stats */}
            {!loading && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <Card className="bg-primary/5 border-primary/20">
                  <CardContent className="pt-4 pb-4">
                    <div className="space-y-1">
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                        Total Metrics
                      </p>
                      <p className="text-2xl font-bold">{stats.total}</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-green-500/5 border-green-500/20">
                  <CardContent className="pt-4 pb-4">
                    <div className="space-y-1">
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                        Trending Up
                      </p>
                      <div className="flex items-center gap-1.5">
                        <TrendingUp className="h-5 w-5 text-green-600" />
                        <p className="text-2xl font-bold text-green-600">{stats.up}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-red-500/5 border-red-500/20">
                  <CardContent className="pt-4 pb-4">
                    <div className="space-y-1">
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                        Trending Down
                      </p>
                      <div className="flex items-center gap-1.5">
                        <TrendingDown className="h-5 w-5 text-red-600" />
                        <p className="text-2xl font-bold text-red-600">{stats.down}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-amber-500/5 border-amber-500/20">
                  <CardContent className="pt-4 pb-4">
                    <div className="space-y-1">
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                        Active Alerts
                      </p>
                      <p className="text-2xl font-bold text-amber-600">{stats.alerts}</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>

          {/* Search and Filters */}
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-3">
              {/* Search Bar */}
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search metrics by name, code, or description..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 h-11"
                />
              </div>

              {/* Sort Dropdown */}
              <div className="flex gap-2">
                <Button
                  variant={sortBy === 'name' ? 'default' : 'outline'}
                  onClick={() => setSortBy('name')}
                  className="gap-2 h-11 px-4"
                >
                  <Filter className="h-4 w-4" />
                  Name
                </Button>
                <Button
                  variant={sortBy === 'change' ? 'default' : 'outline'}
                  onClick={() => setSortBy('change')}
                  className="gap-2 h-11 px-4"
                >
                  <TrendingUp className="h-4 w-4" />
                  Change
                </Button>
              </div>
            </div>

            {/* Category Filter Pills */}
            <div className="flex flex-wrap gap-2">
              <Button
                variant={selectedCategory === null ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(null)}
                className="h-9"
              >
                All Categories
              </Button>
              {Object.entries(CATEGORY_INFO).map(([category, info]) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? 'default' : 'outline'}
                  size="sm"
                  onClick={() =>
                    setSelectedCategory(selectedCategory === category ? null : category)
                  }
                  className="h-9 gap-1.5"
                >
                  <span>{info.icon}</span>
                  <span>{category}</span>
                </Button>
              ))}
            </div>
          </div>

          {/* Metrics Grid */}
          {loading ? (
            <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 12 }).map((_, i) => (
                <Skeleton key={i} className="h-48 rounded-xl" />
              ))}
            </div>
          ) : filteredMetrics.length > 0 ? (
            <>
              {/* Filtered View */}
              {(searchQuery || selectedCategory) && (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold">
                      {selectedCategory || 'Search Results'}
                    </h2>
                    <Badge variant="secondary">
                      {filteredMetrics.length} metric{filteredMetrics.length !== 1 ? 's' : ''}
                    </Badge>
                  </div>
                  <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                    {filteredMetrics.map((metric, index) => (
                      <div
                        key={metric.code}
                        className="animate-slide-up"
                        style={{ animationDelay: `${index * 20}ms` }}
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
                </div>
              )}

              {/* Category View (default) */}
              {!searchQuery && !selectedCategory && (
                <div className="space-y-8">
                  {Object.entries(metricsByCategory).map(([category, categoryMetrics]) => {
                    const info = CATEGORY_INFO[category as CategoryKey]
                    return (
                      <div key={category} className="space-y-4">
                        <div className="flex items-center gap-3 pb-3 border-b">
                          <span className="text-3xl">{info.icon}</span>
                          <div className="flex-1">
                            <h2 className="text-2xl font-bold">{category}</h2>
                            <p className="text-sm text-muted-foreground">
                              {info.description}
                            </p>
                          </div>
                          <Badge variant="outline">
                            {categoryMetrics.length} metric{categoryMetrics.length !== 1 ? 's' : ''}
                          </Badge>
                        </div>
                        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                          {categoryMetrics.map((metric, index) => (
                            <div
                              key={metric.code}
                              className="animate-slide-up"
                              style={{ animationDelay: `${index * 20}ms` }}
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
                      </div>
                    )
                  })}
                </div>
              )}
            </>
          ) : (
            <Card className="border-2 border-dashed">
              <CardContent className="pt-12 pb-12 text-center">
                <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-semibold mb-2">No metrics found</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Try adjusting your search or filter criteria
                </p>
                <Button
                  variant="outline"
                  onClick={() => {
                    setSearchQuery('')
                    setSelectedCategory(null)
                  }}
                >
                  Clear Filters
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </PageTransition>
    </Layout>
  )
}
