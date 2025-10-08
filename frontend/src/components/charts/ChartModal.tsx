import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Brush,
} from 'recharts'
import { dailyMetricsService } from '@/services/dailyMetricsService'
import type { HistoricalMetricsResponse } from '@/types/dailyMetrics'
import { format } from 'date-fns'
import { TrendingUp, TrendingDown, BarChart3, Activity } from 'lucide-react'

interface ChartModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  metricCode: string
  metricName: string
}

type TimeRange = '30d' | '90d' | '1y' | '5y'

export function ChartModal({
  open,
  onOpenChange,
  metricCode,
  metricName,
}: ChartModalProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('90d')
  const [data, setData] = useState<HistoricalMetricsResponse | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (open && metricCode) {
      fetchData()
    }
  }, [open, metricCode, timeRange])

  const fetchData = async () => {
    setLoading(true)
    try {
      const response = await dailyMetricsService.getHistoricalMetrics(
        metricCode,
        timeRange
      )
      setData(response)
    } catch (error) {
      console.error('Error fetching historical metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatYAxis = (value: number) => {
    if (Math.abs(value) >= 1e9) {
      return `${(value / 1e9).toFixed(1)}B`
    } else if (Math.abs(value) >= 1e6) {
      return `${(value / 1e6).toFixed(1)}M`
    } else if (Math.abs(value) >= 1e3) {
      return `${(value / 1e3).toFixed(1)}K`
    }
    return value.toFixed(2)
  }

  const formatXAxis = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      if (timeRange === '5y' || timeRange === '1y') {
        return format(date, 'MMM yyyy')
      }
      return format(date, 'MMM d')
    } catch {
      return dateStr
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-7xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl">
            <BarChart3 className="h-6 w-6 text-primary" />
            {metricName}
            <span className="text-sm text-muted-foreground font-normal">({metricCode})</span>
          </DialogTitle>
        </DialogHeader>

        {/* Time Range Tabs */}
        <Tabs value={timeRange} onValueChange={(v) => setTimeRange(v as TimeRange)}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="30d">30 Days</TabsTrigger>
            <TabsTrigger value="90d">90 Days</TabsTrigger>
            <TabsTrigger value="1y">1 Year</TabsTrigger>
            <TabsTrigger value="5y">5 Years</TabsTrigger>
          </TabsList>
        </Tabs>

        {loading ? (
          <div className="space-y-4">
            <Skeleton className="h-96 w-full" />
            <div className="grid grid-cols-4 gap-4">
              <Skeleton className="h-24" />
              <Skeleton className="h-24" />
              <Skeleton className="h-24" />
              <Skeleton className="h-24" />
            </div>
          </div>
        ) : data ? (
          <div className="space-y-6">
            {/* Chart */}
            <Card>
              <CardContent className="pt-6">
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={data.data}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                    <XAxis
                      dataKey="date"
                      tickFormatter={formatXAxis}
                      tick={{ fontSize: 12 }}
                      tickLine={false}
                    />
                    <YAxis
                      tickFormatter={formatYAxis}
                      tick={{ fontSize: 12 }}
                      tickLine={false}
                      width={80}
                    />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (!active || !payload || payload.length === 0) return null
                        const dataPoint = payload[0]
                        return (
                          <Card className="border-primary/50 shadow-lg">
                            <CardContent className="p-3 space-y-1">
                              <p className="text-xs text-muted-foreground">
                                {formatXAxis(dataPoint.payload.date)}
                              </p>
                              <p className="text-lg font-bold tabular-nums">
                                {dataPoint.value?.toLocaleString('en-US', {
                                  minimumFractionDigits: 2,
                                  maximumFractionDigits: 2,
                                })}
                                <span className="text-sm text-muted-foreground ml-1">
                                  {data.unit}
                                </span>
                              </p>
                            </CardContent>
                          </Card>
                        )
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="hsl(var(--primary))"
                      strokeWidth={2}
                      dot={false}
                      animationDuration={500}
                    />
                    <Brush
                      dataKey="date"
                      height={30}
                      stroke="hsl(var(--primary))"
                      tickFormatter={formatXAxis}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                icon={<Activity className="h-4 w-4" />}
                label="Current"
                value={data.statistics.current}
                unit={data.unit}
              />
              <StatCard
                icon={<BarChart3 className="h-4 w-4" />}
                label="Average"
                value={data.statistics.average}
                unit={data.unit}
              />
              <StatCard
                icon={<TrendingUp className="h-4 w-4 text-green-600" />}
                label="High"
                value={data.statistics.high}
                unit={data.unit}
                variant="success"
              />
              <StatCard
                icon={<TrendingDown className="h-4 w-4 text-red-600" />}
                label="Low"
                value={data.statistics.low}
                unit={data.unit}
                variant="danger"
              />
            </div>
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  )
}

interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: number
  unit: string
  variant?: 'default' | 'success' | 'danger'
}

function StatCard({ icon, label, value, unit, variant = 'default' }: StatCardProps) {
  return (
    <Card
      className={
        variant === 'success'
          ? 'border-green-600/50 bg-green-500/5'
          : variant === 'danger'
          ? 'border-red-600/50 bg-red-500/5'
          : ''
      }
    >
      <CardHeader className="pb-2">
        <CardTitle className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
          {icon}
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold tabular-nums">
          {value.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}
          <span className="text-sm text-muted-foreground ml-1">{unit}</span>
        </div>
      </CardContent>
    </Card>
  )
}
