import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { MetricCard } from './MetricCard'
import { formatDateTime } from '@/lib/utils'
import { Activity, ExternalLink, AlertCircle, RefreshCw } from 'lucide-react'
import type { DashboardTodayFeed } from '@/types'
import { cn } from '@/lib/utils'

interface TodayFeedProps {
  data: DashboardTodayFeed | null
  isLoading: boolean
  error?: string | null
  onRefresh?: () => void
}

interface DayTheme {
  title: string
  icon: string
  color: string
  focus: string
  accentColor: string
}

const dayThemes: Record<number, DayTheme> = {
  0: {
    title: "Weekly Overview",
    icon: "📊",
    color: "blue",
    focus: "Market summary and week ahead",
    accentColor: "bg-blue-500/10 text-blue-500 border-blue-500/20"
  },
  1: {
    title: "Federal Reserve Focus",
    icon: "🏦",
    color: "green",
    focus: "Monetary policy and Fed activities",
    accentColor: "bg-green-500/10 text-green-500 border-green-500/20"
  },
  2: {
    title: "Real Estate Markets",
    icon: "🏢",
    color: "orange",
    focus: "Housing data and construction",
    accentColor: "bg-orange-500/10 text-orange-500 border-orange-500/20"
  },
  3: {
    title: "Economic Indicators",
    icon: "📈",
    color: "blue",
    focus: "GDP, employment, inflation data",
    accentColor: "bg-blue-500/10 text-blue-500 border-blue-500/20"
  },
  4: {
    title: "Regional & Banking",
    icon: "🏛️",
    color: "purple",
    focus: "Regional economics and banking sector",
    accentColor: "bg-purple-500/10 text-purple-500 border-purple-500/20"
  },
  5: {
    title: "Market Summary",
    icon: "🌍",
    color: "teal",
    focus: "Week in review and market performance",
    accentColor: "bg-teal-500/10 text-teal-500 border-teal-500/20"
  },
  6: {
    title: "Weekly Digest",
    icon: "📰",
    color: "indigo",
    focus: "Key insights from the week",
    accentColor: "bg-indigo-500/10 text-indigo-500 border-indigo-500/20"
  }
}

export function TodayFeed({ data, isLoading, error, onRefresh }: TodayFeedProps) {
  const [currentDay] = useState(() => new Date().getDay())
  const dayTheme = dayThemes[currentDay]

  // Auto-refresh every 5 minutes
  useEffect(() => {
    if (!onRefresh) return

    const interval = setInterval(() => {
      onRefresh()
    }, 5 * 60 * 1000) // 5 minutes

    return () => clearInterval(interval)
  }, [onRefresh])

  if (isLoading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <Skeleton className="h-32 w-full" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Card className="border-destructive/50 bg-destructive/5">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center justify-center space-y-4 py-8">
            <AlertCircle className="h-12 w-12 text-destructive" />
            <div className="text-center space-y-2">
              <p className="text-destructive font-medium">Failed to load data</p>
              <p className="text-sm text-muted-foreground">{error}</p>
            </div>
            {onRefresh && (
              <Button onClick={onRefresh} variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!data) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-muted-foreground text-center py-8">No data available</p>
        </CardContent>
      </Card>
    )
  }

  const getMarketStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'text-green-500 bg-green-500/10'
      case 'closed':
        return 'text-red-500 bg-red-500/10'
      case 'pre-market':
      case 'after-hours':
        return 'text-yellow-500 bg-yellow-500/10'
      default:
        return 'text-muted-foreground bg-muted'
    }
  }

  // Check for breaking news (high importance items from last hour)
  const breakingNews = data.news?.find(item =>
    item.importance === 'high' &&
    new Date(item.publishedAt).getTime() > Date.now() - 3600000
  )

  // Extract weekly insights from news
  const weeklyInsights = data.news?.slice(0, 3).map(item => item.title) || []

  return (
    <div className="space-y-6 animate-fade-in" id="overview">
      {/* Theme Header */}
      <div className={cn(
        "p-6 rounded-lg border-2 transition-all",
        dayTheme.accentColor
      )}>
        <div className="flex items-start gap-4">
          <div className="text-4xl">{dayTheme.icon}</div>
          <div className="flex-1">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h1 className="text-3xl font-bold tracking-tight mb-1">
                  {dayTheme.title}
                </h1>
                <p className="text-sm opacity-90 mb-3">
                  {dayTheme.focus}
                </p>
                <p className="text-xs text-muted-foreground">
                  Last updated: {formatDateTime(data.lastUpdated)}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className={cn(
                  'flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium',
                  getMarketStatusColor(data.marketStatus)
                )}>
                  <Activity className="h-3.5 w-3.5" />
                  <span className="capitalize">
                    {data.marketStatus.replace('-', ' ')}
                  </span>
                </div>
                {onRefresh && (
                  <Button
                    onClick={onRefresh}
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0"
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Breaking News Banner */}
      {breakingNews && (
        <Card className="border-red-500/50 bg-red-500/5 animate-pulse-subtle">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-bold text-red-500 uppercase tracking-wider">
                    Breaking News
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(breakingNews.publishedAt).toLocaleTimeString()}
                  </span>
                </div>
                <h3 className="font-semibold text-sm mb-1">{breakingNews.title}</h3>
                <p className="text-xs text-muted-foreground">{breakingNews.summary}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Metrics Grid */}
      <div>
        <div className="mb-4">
          <h2 className="text-2xl font-bold tracking-tight">Key Metrics</h2>
          <p className="text-sm text-muted-foreground">Live economic indicators</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data.indicators.slice(0, 6).map((indicator, index) => (
            <div
              key={indicator.id}
              className="animate-slide-up"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <MetricCard metric={indicator} />
            </div>
          ))}
        </div>
      </div>

      {/* Weekly Summary Section */}
      {weeklyInsights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>This Week in {dayTheme.title}</CardTitle>
            <CardDescription>Top stories and developments</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {weeklyInsights.map((insight, index) => (
                <li
                  key={index}
                  className="flex items-start gap-3 text-sm"
                >
                  <span className="text-primary font-medium mt-0.5">•</span>
                  <span>{insight}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Latest News */}
      {data.news && data.news.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Latest News</CardTitle>
            <CardDescription>Recent economic news and updates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.news.slice(0, 5).map((item) => (
                <div
                  key={item.id}
                  className="group flex gap-4 p-3 rounded-lg border border-transparent hover:border-border hover:bg-accent/50 transition-all cursor-pointer"
                  onClick={() => item.url && window.open(item.url, '_blank')}
                >
                  <div className="flex-1 space-y-1.5">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-sm group-hover:text-primary transition-colors">
                        {item.title}
                      </h4>
                      {item.url && (
                        <ExternalLink className="h-3 w-3 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {item.summary}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span className="font-medium">{item.source}</span>
                      <span>•</span>
                      <span>{new Date(item.publishedAt).toLocaleTimeString()}</span>
                      {item.importance && (
                        <>
                          <span>•</span>
                          <span className={cn(
                            'capitalize font-medium px-1.5 py-0.5 rounded',
                            item.importance === 'high' && 'bg-red-500/10 text-red-500',
                            item.importance === 'medium' && 'bg-yellow-500/10 text-yellow-500',
                            item.importance === 'low' && 'bg-green-500/10 text-green-500'
                          )}>
                            {item.importance}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
