import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { MetricCard } from './MetricCard'
import { formatDate } from '@/lib/utils'
import { Calendar, TrendingUp, TrendingDown, CheckCircle2 } from 'lucide-react'
import type { WeeklySummary as WeeklySummaryType } from '@/types'

interface WeeklySummaryProps {
  data: WeeklySummaryType | null
  isLoading: boolean
}

export function WeeklySummary({ data, isLoading }: WeeklySummaryProps) {
  if (isLoading) {
    return (
      <div className="space-y-4" id="weekly">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (!data) {
    return (
      <Card id="weekly">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Weekly Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center">No weekly summary available</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6" id="weekly">
      <div>
        <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Calendar className="h-7 w-7 text-primary" />
          Weekly Summary
        </h2>
        <p className="text-muted-foreground">
          {formatDate(data.weekStart)} - {formatDate(data.weekEnd)}
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Week Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground leading-relaxed">{data.summary}</p>
        </CardContent>
      </Card>

      {data.keyEvents && data.keyEvents.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Key Events</CardTitle>
            <CardDescription>Notable economic events this week</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {data.keyEvents.map((event, index) => (
                <li key={index} className="flex gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                  <span className="text-sm">{event}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {data.topPerformers && data.topPerformers.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-500">
                <TrendingUp className="h-5 w-5" />
                Top Performers
              </CardTitle>
              <CardDescription>Best performing indicators this week</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {data.topPerformers.map((metric) => (
                <MetricCard key={metric.id} metric={metric} />
              ))}
            </CardContent>
          </Card>
        )}

        {data.topDecliners && data.topDecliners.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-500">
                <TrendingDown className="h-5 w-5" />
                Top Decliners
              </CardTitle>
              <CardDescription>Weakest performing indicators this week</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {data.topDecliners.map((metric) => (
                <MetricCard key={metric.id} metric={metric} />
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
