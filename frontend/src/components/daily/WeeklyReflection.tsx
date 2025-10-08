import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { dailyMetricsService } from '@/services/dailyMetricsService'
import type { WeeklyReflectionResponse } from '@/types/dailyMetrics'
import { TrendingUp, TrendingDown, AlertTriangle, Calendar } from 'lucide-react'
import { format } from 'date-fns'

export function WeeklyReflection() {
  const [data, setData] = useState<WeeklyReflectionResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchWeeklyReflection()
  }, [])

  const fetchWeeklyReflection = async () => {
    setLoading(true)
    try {
      const response = await dailyMetricsService.getWeeklyReflection()
      setData(response)
    } catch (error) {
      console.error('Error fetching weekly reflection:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  if (!data) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          No weekly reflection data available.
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Week Header */}
      <Card className="bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-2xl">
            <Calendar className="h-6 w-6 text-primary" />
            Weekly Reflection
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="text-sm text-muted-foreground">
            {format(new Date(data.week_start), 'MMM d')} -{' '}
            {format(new Date(data.week_end), 'MMM d, yyyy')}
          </div>
          <p className="text-base leading-relaxed">{data.summary}</p>
        </CardContent>
      </Card>

      {/* Top Movers */}
      {data.top_movers && data.top_movers.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              Top Movers This Week
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.top_movers.slice(0, 5).map((mover, index) => {
                const isPositive = mover.change_percent > 0
                return (
                  <div
                    key={mover.code}
                    className="flex items-center justify-between p-3 rounded-lg bg-gradient-to-r from-accent/50 to-transparent hover:from-accent/70 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-sm">
                        {index + 1}
                      </div>
                      <div>
                        <div className="font-medium">{mover.display_name}</div>
                        <div className="text-xs text-muted-foreground">
                          {mover.latest_value.toLocaleString()} {mover.unit}
                        </div>
                      </div>
                    </div>
                    <Badge
                      variant="outline"
                      className={
                        isPositive
                          ? 'bg-green-500/10 text-green-600 border-green-500/50'
                          : 'bg-red-500/10 text-red-600 border-red-500/50'
                      }
                    >
                      <div className="flex items-center gap-1">
                        {isPositive ? (
                          <TrendingUp className="h-3 w-3" />
                        ) : (
                          <TrendingDown className="h-3 w-3" />
                        )}
                        <span className="font-semibold tabular-nums">
                          {isPositive && '+'}
                          {mover.change_percent.toFixed(2)}%
                        </span>
                      </div>
                    </Badge>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Threshold Crossings */}
      {data.threshold_crossings && data.threshold_crossings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-600" />
              Notable Threshold Crossings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.threshold_crossings.map((crossing) => (
                <div
                  key={`${crossing.code}-${crossing.threshold_type}`}
                  className="flex items-start gap-3 p-3 rounded-lg border border-amber-600/20 bg-amber-500/5"
                >
                  <AlertTriangle className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
                  <div className="space-y-1">
                    <div className="font-medium">{crossing.display_name}</div>
                    <div className="text-sm text-muted-foreground">
                      {crossing.description}
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {crossing.threshold_type}
                    </Badge>
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
