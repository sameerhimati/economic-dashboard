import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { MetricCard } from './MetricCard'
import { formatDateTime } from '@/lib/utils'
import { Activity, ExternalLink } from 'lucide-react'
import type { DashboardTodayFeed } from '@/types'
import { cn } from '@/lib/utils'

interface TodayFeedProps {
  data: DashboardTodayFeed | null
  isLoading: boolean
}

export function TodayFeed({ data, isLoading }: TodayFeedProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-muted-foreground text-center">No data available</p>
        </CardContent>
      </Card>
    )
  }

  const getMarketStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'text-green-500'
      case 'closed':
        return 'text-red-500'
      case 'pre-market':
      case 'after-hours':
        return 'text-yellow-500'
      default:
        return 'text-muted-foreground'
    }
  }

  return (
    <div className="space-y-6" id="overview">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Today's Overview</h2>
          <p className="text-muted-foreground">
            Last updated: {formatDateTime(data.lastUpdated)}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4" />
          <span className={cn('font-medium capitalize', getMarketStatusColor(data.marketStatus))}>
            {data.marketStatus.replace('-', ' ')}
          </span>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data.indicators.map((indicator) => (
          <MetricCard key={indicator.id} metric={indicator} />
        ))}
      </div>

      {data.news && data.news.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Latest News</CardTitle>
            <CardDescription>Recent economic news and updates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.news.slice(0, 5).map((item) => (
                <div
                  key={item.id}
                  className="flex gap-4 p-3 rounded-lg hover:bg-accent transition-colors cursor-pointer"
                  onClick={() => item.url && window.open(item.url, '_blank')}
                >
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-sm">{item.title}</h4>
                      {item.url && <ExternalLink className="h-3 w-3 text-muted-foreground" />}
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {item.summary}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>{item.source}</span>
                      <span>•</span>
                      <span>{new Date(item.publishedAt).toLocaleTimeString()}</span>
                      {item.importance && (
                        <>
                          <span>•</span>
                          <span className={cn(
                            'capitalize',
                            item.importance === 'high' && 'text-red-500',
                            item.importance === 'medium' && 'text-yellow-500',
                            item.importance === 'low' && 'text-green-500'
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
