import { useState, useEffect, useRef } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
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
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Activity,
  AlertCircle,
  BookOpen,
  Lightbulb,
  History,
  Link as LinkIcon
} from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { getMetricEducation, hasMetricEducation } from '@/data/metricEncyclopedia'

interface ChartModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  metricCode: string
  metricName: string
}

type TimeRange = '30d' | '90d' | '1y' | '5y'
type ModalTab = 'chart' | 'about' | 'interpret' | 'history'

function ChartModal({
  open,
  onOpenChange,
  metricCode,
  metricName,
}: ChartModalProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('90d')
  const [activeTab, setActiveTab] = useState<ModalTab>('chart')
  const [data, setData] = useState<HistoricalMetricsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const modalRef = useRef<HTMLDivElement>(null)

  const education = hasMetricEducation(metricCode) ? getMetricEducation(metricCode) : null

  useEffect(() => {
    if (open && metricCode) {
      fetchData()
    }
  }, [open, metricCode, timeRange])

  // Handle Escape key to close modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onOpenChange(false)
      }
    }

    if (open) {
      window.addEventListener('keydown', handleEscape)
    }

    return () => window.removeEventListener('keydown', handleEscape)
  }, [open, onOpenChange])

  // Focus trap implementation
  useEffect(() => {
    if (!open) return

    const modal = modalRef.current
    if (!modal) return

    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstElement = focusableElements[0] as HTMLElement
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement?.focus()
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault()
          firstElement?.focus()
        }
      }
    }

    modal.addEventListener('keydown', handleTab as EventListener)
    firstElement?.focus()

    return () => modal.removeEventListener('keydown', handleTab as EventListener)
  }, [open, loading, activeTab])

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await dailyMetricsService.getHistoricalMetrics(
        metricCode,
        timeRange
      )

      if (!response.data || response.data.length === 0) {
        setError(`No data available for ${metricName} in the ${timeRange} range.`)
      } else {
        setData(response)
      }
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Failed to load chart data. Please try again.'
      )
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

  const getPercentile = (current: number, high: number, low: number): number => {
    if (high === low) return 50
    return Math.round(((current - low) / (high - low)) * 100)
  }

  const getStatusLabel = (percentile: number): { label: string; variant: 'default' | 'secondary' | 'destructive' } => {
    if (percentile >= 80) return { label: 'Historically High', variant: 'destructive' }
    if (percentile >= 60) return { label: 'Above Average', variant: 'secondary' }
    if (percentile >= 40) return { label: 'Average', variant: 'default' }
    if (percentile >= 20) return { label: 'Below Average', variant: 'secondary' }
    return { label: 'Historically Low', variant: 'default' }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent ref={modalRef} className="max-w-7xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl">
            <BarChart3 className="h-6 w-6 text-primary" />
            {metricName}
            <span className="text-sm text-muted-foreground font-normal">({metricCode})</span>
          </DialogTitle>
        </DialogHeader>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as ModalTab)}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="chart" className="gap-2">
              <BarChart3 className="h-4 w-4" />
              Chart
            </TabsTrigger>
            <TabsTrigger value="about" className="gap-2">
              <BookOpen className="h-4 w-4" />
              About
            </TabsTrigger>
            <TabsTrigger value="interpret" className="gap-2">
              <Lightbulb className="h-4 w-4" />
              How to Interpret
            </TabsTrigger>
            <TabsTrigger value="history" className="gap-2">
              <History className="h-4 w-4" />
              Historical Context
            </TabsTrigger>
          </TabsList>

          {/* Tab 1: Chart */}
          <TabsContent value="chart" className="space-y-4">
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
            ) : error ? (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
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
          </TabsContent>

          {/* Tab 2: About */}
          <TabsContent value="about" className="space-y-6">
            {education ? (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BookOpen className="h-5 w-5 text-primary" />
                      What is this metric?
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-base leading-relaxed">{education.whatIsIt}</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertCircle className="h-5 w-5 text-primary" />
                      Why it matters
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {education.whyItMatters.map((point, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-primary mt-1">•</span>
                          <span className="flex-1">{point}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                {data && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Activity className="h-5 w-5 text-primary" />
                        Current Status
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Current value:</span>
                          <span className="font-bold text-xl tabular-nums">
                            {data.statistics.current.toLocaleString('en-US', {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}{' '}
                            {data.unit}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Percentile:</span>
                          <span className="font-semibold">
                            {getPercentile(data.statistics.current, data.statistics.high, data.statistics.low)}th
                            <span className="text-sm text-muted-foreground ml-1">
                              (higher than {getPercentile(data.statistics.current, data.statistics.high, data.statistics.low)}% of historical values)
                            </span>
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground">Status:</span>
                          <Badge variant={getStatusLabel(getPercentile(data.statistics.current, data.statistics.high, data.statistics.low)).variant}>
                            {getStatusLabel(getPercentile(data.statistics.current, data.statistics.high, data.statistics.low)).label}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Alert>
                <BookOpen className="h-4 w-4" />
                <AlertDescription>
                  Educational content for this metric is coming soon.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>

          {/* Tab 3: How to Interpret */}
          <TabsContent value="interpret" className="space-y-6">
            {education ? (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5 text-primary" />
                      Reading the Numbers
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="border-l-4 border-red-500 pl-4">
                        <div className="font-semibold text-red-600 mb-1">
                          Low: {education.readingTheNumbers.low.range}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {education.readingTheNumbers.low.meaning}
                        </p>
                      </div>
                      <div className="border-l-4 border-yellow-500 pl-4">
                        <div className="font-semibold text-yellow-600 mb-1">
                          Normal: {education.readingTheNumbers.normal.range}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {education.readingTheNumbers.normal.meaning}
                        </p>
                      </div>
                      <div className="border-l-4 border-green-500 pl-4">
                        <div className="font-semibold text-green-600 mb-1">
                          High: {education.readingTheNumbers.high.range}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {education.readingTheNumbers.high.meaning}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Lightbulb className="h-5 w-5 text-primary" />
                      What to Watch For
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {education.whatToWatch.map((point, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <TrendingUp className="h-4 w-4 text-primary mt-1 shrink-0" />
                          <span className="flex-1">{point}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertCircle className="h-5 w-5 text-primary" />
                      Key Thresholds
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {education.keyThresholds.map((threshold, idx) => (
                        <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                          <Badge variant="outline" className="shrink-0">
                            {threshold.value}
                          </Badge>
                          <span className="text-sm">{threshold.meaning}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Alert>
                <Lightbulb className="h-4 w-4" />
                <AlertDescription>
                  Interpretation guidance for this metric is coming soon.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>

          {/* Tab 4: Historical Context */}
          <TabsContent value="history" className="space-y-6">
            {education ? (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <History className="h-5 w-5 text-primary" />
                      Notable Events
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {education.historicalEvents.map((event, idx) => (
                        <div key={idx} className="border-l-2 border-primary/50 pl-4 pb-4 last:pb-0">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="secondary">{event.year}</Badge>
                            <span className="font-semibold">{event.event}</span>
                          </div>
                          <p className="text-sm text-muted-foreground">{event.impact}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {education.relatedMetrics.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <LinkIcon className="h-5 w-5 text-primary" />
                        Related Metrics to Compare
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {education.relatedMetrics.map((related, idx) => (
                          <div key={idx} className="p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors">
                            <div className="flex items-start gap-3">
                              <Badge variant="outline" className="shrink-0">
                                {related.code}
                              </Badge>
                              <div className="flex-1">
                                <div className="font-medium mb-1">{related.name}</div>
                                <p className="text-sm text-muted-foreground">
                                  {related.relationship}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Alert>
                <History className="h-4 w-4" />
                <AlertDescription>
                  Historical context for this metric is coming soon.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>
        </Tabs>
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

export default ChartModal
