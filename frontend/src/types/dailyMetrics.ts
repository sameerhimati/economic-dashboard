export interface SparklineDataPoint {
  date: string
  value: number
}

export interface MetricChanges {
  vs_yesterday: number
  vs_last_week: number
  vs_last_month: number
  vs_last_year: number
}

export interface MetricSignificance {
  percentile: number
  is_outlier: boolean
}

export interface DailyMetricData {
  code: string
  display_name: string
  description: string
  unit: string
  latest_value: number
  latest_date: string
  sparkline_data: SparklineDataPoint[]
  alerts: string[]
  context: string
  changes: MetricChanges
  significance: MetricSignificance
}

export interface DailyMetricsResponse {
  date: string
  weekday: number
  theme: string
  summary: string
  metrics_up: number
  metrics_down: number
  alerts_count: number
  metrics: DailyMetricData[]
}

export interface HistoricalDataPoint {
  date: string
  value: number
}

export interface HistoricalMetricsResponse {
  code: string
  display_name: string
  unit: string
  data: HistoricalDataPoint[]
  statistics: {
    current: number
    average: number
    high: number
    low: number
  }
}

export interface TopMover {
  code: string
  display_name: string
  change_percent: number
  latest_value: number
  unit: string
}

export interface ThresholdCrossing {
  code: string
  display_name: string
  threshold_type: string
  description: string
}

export interface WeeklyReflectionResponse {
  week_start: string
  week_end: string
  summary: string
  top_movers: TopMover[]
  threshold_crossings: ThresholdCrossing[]
}
