import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
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
  Link as LinkIcon,
  ArrowUpRight,
  ArrowDownRight,
  Gauge,
  ExternalLink
} from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { getMetricEducation, hasMetricEducation } from '@/data/metricEncyclopedia'
import { cn } from '@/lib/utils'

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
  const [timeRange, setTimeRange] = useState<TimeRange>('5y')
  const [activeTab, setActiveTab] = useState<ModalTab>('chart')
  const [data, setData] = useState<HistoricalMetricsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const modalRef = useRef<HTMLDivElement>(null)

  const education = hasMetricEducation(metricCode) ? getMetricEducation(metricCode) : null

  const fetchData = useCallback(async () => {
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
  }, [metricCode, timeRange, metricName])

  useEffect(() => {
    if (open && metricCode) {
      fetchData()
    }
  }, [open, metricCode, fetchData])

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

  const getStatusLabel = (percentile: number): { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' } => {
    if (percentile >= 80) return { label: 'Historically High', variant: 'destructive' }
    if (percentile >= 60) return { label: 'Above Average', variant: 'secondary' }
    if (percentile >= 40) return { label: 'Average', variant: 'outline' }
    if (percentile >= 20) return { label: 'Below Average', variant: 'secondary' }
    return { label: 'Historically Low', variant: 'outline' }
  }

  const getTrend = () => {
    if (!data) return null
    const { current, average } = data.statistics
    const percentDiff = ((current - average) / average) * 100
    return {
      direction: percentDiff > 0 ? 'up' : percentDiff < 0 ? 'down' : 'neutral',
      percent: Math.abs(percentDiff),
    }
  }

  const trend = getTrend()

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        ref={modalRef}
        className="max-w-6xl max-h-[90vh] overflow-y-auto p-0"
      >
        {/* Clean Header with Summary */}
        <DialogHeader className="px-8 pt-8 pb-6 border-b bg-gradient-to-b from-background to-muted/10">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 space-y-2">
              <div className="flex items-center gap-3 flex-wrap">
                <DialogTitle className="text-3xl font-bold tracking-tight">
                  {metricName}
                </DialogTitle>
                <Button
                  variant="outline"
                  size="default"
                  className="gap-1.5 sm:gap-2 text-sm font-medium hover:bg-primary/5 hover:text-primary hover:border-primary/30 transition-all h-9 px-3 sm:px-4"
                  asChild
                >
                  <a
                    href={`https://fred.stlouisfed.org/series/${metricCode}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <ExternalLink className="h-4 w-4 shrink-0" />
                    <span className="hidden sm:inline">View on FRED</span>
                    <span className="sm:hidden">FRED</span>
                  </a>
                </Button>
              </div>
              <DialogDescription className="text-base text-muted-foreground leading-relaxed max-w-4xl">
                {education?.whatIsIt || 'View historical trends and detailed analysis'}
              </DialogDescription>
              <div className="flex items-center gap-2 flex-wrap">
                <Badge variant="outline" className="font-mono text-xs">
                  {metricCode}
                </Badge>
                {data && trend && (
                  <Badge
                    variant={trend.direction === 'up' ? 'default' : trend.direction === 'down' ? 'secondary' : 'outline'}
                    className={cn(
                      "gap-1.5",
                      trend.direction === 'up' && "bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20",
                      trend.direction === 'down' && "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20"
                    )}
                  >
                    {trend.direction === 'up' ? (
                      <ArrowUpRight className="h-3 w-3" />
                    ) : trend.direction === 'down' ? (
                      <ArrowDownRight className="h-3 w-3" />
                    ) : (
                      <Gauge className="h-3 w-3" />
                    )}
                    {trend.percent > 0 && `${trend.percent.toFixed(1)}% ${trend.direction === 'up' ? 'above' : 'below'} average`}
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </DialogHeader>

        {/* Main Content Area */}
        <div className="px-8 py-6">
          {/* Prominent Navigation Tabs */}
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as ModalTab)} className="space-y-6">
            <TabsList className="grid w-full grid-cols-4 h-12 bg-muted/50 p-1 rounded-lg">
              <TabsTrigger
                value="chart"
                className="gap-2 text-sm font-medium data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-md"
              >
                <BarChart3 className="h-4 w-4" />
                <span className="hidden sm:inline">Chart & Stats</span>
                <span className="sm:hidden">Chart</span>
              </TabsTrigger>
              <TabsTrigger
                value="interpret"
                className="gap-2 text-sm font-medium data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-md"
              >
                <Lightbulb className="h-4 w-4" />
                <span className="hidden sm:inline">How to Read</span>
                <span className="sm:hidden">Read</span>
              </TabsTrigger>
              <TabsTrigger
                value="about"
                className="gap-2 text-sm font-medium data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-md"
              >
                <BookOpen className="h-4 w-4" />
                <span className="hidden sm:inline">About</span>
                <span className="sm:hidden">About</span>
              </TabsTrigger>
              <TabsTrigger
                value="history"
                className="gap-2 text-sm font-medium data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-md"
              >
                <History className="h-4 w-4" />
                <span className="hidden sm:inline">History</span>
                <span className="sm:hidden">History</span>
              </TabsTrigger>
            </TabsList>

          {/* Tab 1: Chart & Stats */}
          <TabsContent value="chart" className="space-y-6 mt-0">
            {/* Time Range Selector */}
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Historical Trend</h3>
              <Tabs value={timeRange} onValueChange={(v) => setTimeRange(v as TimeRange)}>
                <TabsList className="h-auto bg-transparent border-0 gap-2 p-0">
                  <TabsTrigger value="30d" className="text-sm px-2 py-1 data-[state=active]:bg-transparent data-[state=active]:text-primary data-[state=active]:shadow-none data-[state=active]:font-bold data-[state=inactive]:text-muted-foreground">30D</TabsTrigger>
                  <TabsTrigger value="90d" className="text-sm px-2 py-1 data-[state=active]:bg-transparent data-[state=active]:text-primary data-[state=active]:shadow-none data-[state=active]:font-bold data-[state=inactive]:text-muted-foreground">90D</TabsTrigger>
                  <TabsTrigger value="1y" className="text-sm px-2 py-1 data-[state=active]:bg-transparent data-[state=active]:text-primary data-[state=active]:shadow-none data-[state=active]:font-bold data-[state=inactive]:text-muted-foreground">1Y</TabsTrigger>
                  <TabsTrigger value="5y" className="text-sm px-2 py-1 data-[state=active]:bg-transparent data-[state=active]:text-primary data-[state=active]:shadow-none data-[state=active]:font-bold data-[state=inactive]:text-muted-foreground">5Y</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>

            {loading ? (
              <div className="space-y-6">
                <Skeleton className="h-80 w-full rounded-xl" />
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Skeleton className="h-28 rounded-xl" />
                  <Skeleton className="h-28 rounded-xl" />
                  <Skeleton className="h-28 rounded-xl" />
                  <Skeleton className="h-28 rounded-xl" />
                </div>
              </div>
            ) : error ? (
              <Alert variant="destructive" className="border-2">
                <AlertCircle className="h-5 w-5" />
                <AlertDescription className="text-base">{error}</AlertDescription>
              </Alert>
            ) : data ? (
              <div className="space-y-6">
                {/* Clean Chart with Card Background */}
                <div className="bg-card rounded-xl border-2 border-border p-6 shadow-sm">
                  <ResponsiveContainer width="100%" height={360}>
                    <LineChart data={data.data} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="hsl(var(--border))"
                        opacity={0.6}
                        vertical={false}
                      />
                      <XAxis
                        dataKey="date"
                        tickFormatter={formatXAxis}
                        tick={{ fontSize: 13, fill: 'hsl(var(--muted-foreground))' }}
                        tickLine={false}
                        axisLine={{ stroke: 'hsl(var(--border))' }}
                        dy={10}
                      />
                      <YAxis
                        tickFormatter={formatYAxis}
                        tick={{ fontSize: 13, fill: 'hsl(var(--muted-foreground))' }}
                        tickLine={false}
                        axisLine={{ stroke: 'hsl(var(--border))' }}
                        width={70}
                        dx={-5}
                      />
                      <Tooltip
                        content={({ active, payload }) => {
                          if (!active || !payload || payload.length === 0) return null
                          const dataPoint = payload[0]
                          return (
                            <div className="bg-popover border-2 border-primary/30 rounded-lg shadow-xl p-4 backdrop-blur-sm">
                              <p className="text-xs font-medium text-muted-foreground mb-1">
                                {formatXAxis(dataPoint.payload.date)}
                              </p>
                              <p className="text-2xl font-bold tabular-nums">
                                {dataPoint.value?.toLocaleString('en-US', {
                                  minimumFractionDigits: 2,
                                  maximumFractionDigits: 2,
                                })}
                                <span className="text-sm font-normal text-muted-foreground ml-2">
                                  {data.unit}
                                </span>
                              </p>
                            </div>
                          )
                        }}
                        cursor={{ stroke: 'hsl(var(--primary))', strokeWidth: 1, strokeDasharray: '4 4' }}
                      />
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="hsl(var(--primary))"
                        strokeWidth={3}
                        dot={false}
                        animationDuration={800}
                        animationEasing="ease-in-out"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Enhanced Statistics Cards */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Key Statistics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <EnhancedStatCard
                      icon={<Activity className="h-5 w-5" />}
                      label="Current Value"
                      value={data.statistics.current}
                      unit={data.unit}
                      variant="current"
                    />
                    <EnhancedStatCard
                      icon={<BarChart3 className="h-5 w-5" />}
                      label="Average"
                      value={data.statistics.average}
                      unit={data.unit}
                      variant="neutral"
                    />
                    <EnhancedStatCard
                      icon={<TrendingUp className="h-5 w-5" />}
                      label="Highest"
                      value={data.statistics.high}
                      unit={data.unit}
                      variant="high"
                    />
                    <EnhancedStatCard
                      icon={<TrendingDown className="h-5 w-5" />}
                      label="Lowest"
                      value={data.statistics.low}
                      unit={data.unit}
                      variant="low"
                    />
                  </div>
                </div>
              </div>
            ) : null}
          </TabsContent>

          {/* Tab 3: About */}
          <TabsContent value="about" className="space-y-6 mt-0">
            {education ? (
              <>
                <div className="bg-card rounded-xl border-2 p-6">
                  <div className="flex items-start gap-4 mb-4">
                    <div className="p-3 bg-primary/10 rounded-lg">
                      <BookOpen className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold mb-2">What is this metric?</h3>
                      <p className="text-base leading-relaxed text-muted-foreground">
                        {education.whatIsIt}
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-bold mb-4">Why It Matters</h3>
                  <div className="bg-muted/50 rounded-xl p-6 border-2">
                    <ul className="space-y-4">
                      {education.whyItMatters.map((point, idx) => (
                        <li key={idx} className="flex items-start gap-3">
                          <div className="p-1.5 bg-primary/10 rounded-md mt-0.5">
                            <AlertCircle className="h-4 w-4 text-primary" />
                          </div>
                          <span className="flex-1 text-base leading-relaxed">{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {data && (
                  <div className="bg-gradient-to-br from-primary/5 to-primary/10 rounded-xl border-2 border-primary/20 p-6">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                      <Activity className="h-6 w-6 text-primary" />
                      Current Status
                    </h3>
                    <div className="space-y-5">
                      <div className="flex items-center justify-between p-4 bg-background/60 rounded-lg">
                        <span className="text-base font-medium text-muted-foreground">Current Value</span>
                        <span className="font-bold text-2xl tabular-nums">
                          {data.statistics.current.toLocaleString('en-US', {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}
                          <span className="text-base font-normal text-muted-foreground ml-2">{data.unit}</span>
                        </span>
                      </div>
                      <div className="flex items-center justify-between p-4 bg-background/60 rounded-lg">
                        <span className="text-base font-medium text-muted-foreground">Historical Position</span>
                        <div className="text-right">
                          <span className="font-bold text-xl tabular-nums">
                            {getPercentile(data.statistics.current, data.statistics.high, data.statistics.low)}th
                            <span className="text-sm font-normal text-muted-foreground ml-1">percentile</span>
                          </span>
                          <p className="text-sm text-muted-foreground mt-0.5">
                            Higher than {getPercentile(data.statistics.current, data.statistics.high, data.statistics.low)}% of historical values
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between p-4 bg-background/60 rounded-lg">
                        <span className="text-base font-medium text-muted-foreground">Status</span>
                        <Badge
                          variant={getStatusLabel(getPercentile(data.statistics.current, data.statistics.high, data.statistics.low)).variant}
                          className="text-sm px-4 py-1.5"
                        >
                          {getStatusLabel(getPercentile(data.statistics.current, data.statistics.high, data.statistics.low)).label}
                        </Badge>
                      </div>
                    </div>
                  </div>
                )}

                {/* Data Source Section */}
                <div className="bg-blue-100/5 dark:bg-blue-950/10 rounded-xl border-2 border-blue-200/50 dark:border-blue-800/50 p-6">
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-blue-500/10 rounded-lg">
                        <ExternalLink className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold mb-1 text-blue-900 dark:text-blue-100">Official Data Source</h3>
                        <p className="text-sm text-blue-700/80 dark:text-blue-300/80">
                          View complete dataset and download historical data
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="default"
                      size="default"
                      className="gap-1.5 sm:gap-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 h-10 px-4 sm:px-6 text-sm font-medium"
                      asChild
                    >
                      <a
                        href={`https://fred.stlouisfed.org/series/${metricCode}`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <span className="truncate">View on FRED</span>
                        <ExternalLink className="h-4 w-4 shrink-0" />
                      </a>
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <Alert className="border-2">
                <BookOpen className="h-5 w-5" />
                <AlertDescription className="text-base">
                  Educational content for this metric is coming soon. We're working on adding comprehensive information about what this metric measures and why it matters.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>

          {/* Tab 2: How to Interpret - FIRST for Education */}
          <TabsContent value="interpret" className="space-y-6 mt-0">
            {education ? (
              <>
                {/* Simple Explainer at Top */}
                <div className="bg-primary/5 border-2 border-primary/20 rounded-xl p-6">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-primary/10 rounded-lg">
                      <Lightbulb className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold mb-2">Quick Guide</h3>
                      <p className="text-base leading-relaxed text-muted-foreground">
                        {education.whatIsIt}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Reading the Numbers - Enhanced Visual */}
                <div>
                  <h3 className="text-xl font-bold mb-4">How to Read the Numbers</h3>
                  <div className="space-y-4">
                    <div className="border-2 border-green-500/30 bg-green-100/10 dark:bg-green-950/20 rounded-xl p-5">
                      <div className="flex items-start gap-4">
                        <div className="p-2 bg-green-500/20 rounded-lg">
                          <TrendingUp className="h-5 w-5 text-green-700 dark:text-green-400" />
                        </div>
                        <div className="flex-1">
                          <div className="text-lg font-bold text-green-700 dark:text-green-400 mb-1">
                            High: {education.readingTheNumbers.high.range}
                          </div>
                          <p className="text-base text-green-900/80 dark:text-green-100/80">
                            {education.readingTheNumbers.high.meaning}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="border-2 border-blue-500/30 bg-blue-100/10 dark:bg-blue-950/20 rounded-xl p-5">
                      <div className="flex items-start gap-4">
                        <div className="p-2 bg-blue-500/20 rounded-lg">
                          <Activity className="h-5 w-5 text-blue-700 dark:text-blue-400" />
                        </div>
                        <div className="flex-1">
                          <div className="text-lg font-bold text-blue-700 dark:text-blue-400 mb-1">
                            Normal: {education.readingTheNumbers.normal.range}
                          </div>
                          <p className="text-base text-blue-900/80 dark:text-blue-100/80">
                            {education.readingTheNumbers.normal.meaning}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="border-2 border-amber-500/30 bg-amber-100/10 dark:bg-amber-950/20 rounded-xl p-5">
                      <div className="flex items-start gap-4">
                        <div className="p-2 bg-amber-500/20 rounded-lg">
                          <TrendingDown className="h-5 w-5 text-amber-700 dark:text-amber-400" />
                        </div>
                        <div className="flex-1">
                          <div className="text-lg font-bold text-amber-700 dark:text-amber-400 mb-1">
                            Low: {education.readingTheNumbers.low.range}
                          </div>
                          <p className="text-base text-amber-900/80 dark:text-amber-100/80">
                            {education.readingTheNumbers.low.meaning}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* What to Watch For */}
                <div>
                  <h3 className="text-xl font-bold mb-4">What to Watch For</h3>
                  <div className="bg-muted/50 rounded-xl p-6 border-2">
                    <ul className="space-y-4">
                      {education.whatToWatch.map((point, idx) => (
                        <li key={idx} className="flex items-start gap-3">
                          <div className="p-1.5 bg-primary/10 rounded-md mt-0.5">
                            <AlertCircle className="h-4 w-4 text-primary" />
                          </div>
                          <span className="flex-1 text-base leading-relaxed">{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Key Thresholds */}
                <div>
                  <h3 className="text-xl font-bold mb-4">Important Thresholds</h3>
                  <div className="space-y-3">
                    {education.keyThresholds.map((threshold, idx) => (
                      <div
                        key={idx}
                        className="flex items-start gap-4 p-4 rounded-xl bg-card border-2 hover:border-primary/30 transition-colors"
                      >
                        <Badge variant="secondary" className="shrink-0 text-sm px-3 py-1 font-mono">
                          {threshold.value}
                        </Badge>
                        <span className="text-base flex-1">{threshold.meaning}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <Alert className="border-2">
                <Lightbulb className="h-5 w-5" />
                <AlertDescription className="text-base">
                  Detailed interpretation guidance for this metric is coming soon. Check back later for insights on how to read and understand this data.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>

          {/* Tab 4: Historical Context */}
          <TabsContent value="history" className="space-y-6 mt-0">
            {education ? (
              <>
                <div>
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <History className="h-6 w-6 text-primary" />
                    Notable Historical Events
                  </h3>
                  <div className="space-y-4">
                    {education.historicalEvents.map((event, idx) => (
                      <div
                        key={idx}
                        className="relative pl-8 pb-6 last:pb-0 border-l-2 border-primary/30 ml-3"
                      >
                        {/* Timeline dot */}
                        <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-primary border-2 border-background" />

                        <div className="bg-card rounded-xl border-2 p-5 hover:border-primary/30 transition-colors">
                          <div className="flex items-center gap-3 mb-3">
                            <Badge variant="secondary" className="text-sm font-bold px-3 py-1">
                              {event.year}
                            </Badge>
                            <span className="font-bold text-lg">{event.event}</span>
                          </div>
                          <p className="text-base text-muted-foreground leading-relaxed">
                            {event.impact}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {education.relatedMetrics.length > 0 && (
                  <div>
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                      <LinkIcon className="h-6 w-6 text-primary" />
                      Related Metrics
                    </h3>
                    <div className="space-y-3">
                      {education.relatedMetrics.map((related, idx) => (
                        <div
                          key={idx}
                          className="p-5 rounded-xl bg-muted/50 hover:bg-muted border-2 border-transparent hover:border-primary/30 transition-all cursor-pointer"
                        >
                          <div className="flex items-start gap-4">
                            <Badge variant="outline" className="shrink-0 text-sm font-mono px-3 py-1">
                              {related.code}
                            </Badge>
                            <div className="flex-1">
                              <div className="font-bold text-base mb-2">{related.name}</div>
                              <p className="text-base text-muted-foreground leading-relaxed">
                                {related.relationship}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <Alert className="border-2">
                <History className="h-5 w-5" />
                <AlertDescription className="text-base">
                  Historical context and related metrics for this indicator are coming soon. Check back later for detailed timeline of major events.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>
        </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  )
}

interface EnhancedStatCardProps {
  icon: React.ReactNode
  label: string
  value: number
  unit: string
  variant: 'current' | 'neutral' | 'high' | 'low'
}

function EnhancedStatCard({ icon, label, value, unit, variant }: EnhancedStatCardProps) {
  const variantStyles = {
    current: {
      border: 'border-primary/40',
      bg: 'bg-primary/5',
      iconBg: 'bg-primary/10',
      iconColor: 'text-primary',
      ring: 'ring-2 ring-primary/20',
    },
    neutral: {
      border: 'border-border',
      bg: 'bg-muted/30',
      iconBg: 'bg-muted',
      iconColor: 'text-muted-foreground',
      ring: '',
    },
    high: {
      border: 'border-green-500/40',
      bg: 'bg-green-50/50 dark:bg-green-950/20',
      iconBg: 'bg-green-500/10',
      iconColor: 'text-green-600 dark:text-green-500',
      ring: '',
    },
    low: {
      border: 'border-red-500/40',
      bg: 'bg-red-50/50 dark:bg-red-950/20',
      iconBg: 'bg-red-500/10',
      iconColor: 'text-red-600 dark:text-red-500',
      ring: '',
    },
  }

  const styles = variantStyles[variant]

  return (
    <div
      className={cn(
        'rounded-xl border-2 p-5 transition-all hover:shadow-md',
        styles.border,
        styles.bg,
        styles.ring
      )}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={cn('p-2 rounded-lg', styles.iconBg)}>
          <div className={styles.iconColor}>{icon}</div>
        </div>
      </div>
      <div className="space-y-1">
        <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
          {label}
        </p>
        <p className="text-3xl font-bold tabular-nums">
          {value.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}
        </p>
        <p className="text-sm font-medium text-muted-foreground">{unit}</p>
      </div>
    </div>
  )
}

export default ChartModal
