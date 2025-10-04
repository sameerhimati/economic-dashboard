export interface User {
  id: string
  username?: string
  email: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterCredentials {
  username: string
  email: string
  password: string
}

export interface EconomicIndicator {
  id?: string
  name?: string
  value?: number
  change?: number
  changePercent?: number
  lastUpdated?: string
  source?: string
  description?: string
  historicalData?: HistoricalDataPoint[]
}

export interface HistoricalDataPoint {
  date: string
  value: number
}

export interface NewsItem {
  id?: string
  title?: string
  summary?: string
  source?: string
  publishedAt?: string
  url?: string
  importance?: 'high' | 'medium' | 'low'
  category?: string
}

export interface DashboardTodayFeed {
  marketStatus: 'open' | 'closed' | 'pre-market' | 'after-hours'
  lastUpdated: string
  indicators?: EconomicIndicator[]
  news?: NewsItem[]
}

export interface DashboardMetrics {
  lastUpdated: string
  metrics?: EconomicIndicator[]
}

export interface BreakingNews {
  lastUpdated?: string
  items: NewsItem[]
}

export interface WeeklySummary {
  weekStart?: string
  weekEnd?: string
  summary?: string
  keyEvents?: string[]
  topPerformers?: EconomicIndicator[]
  topDecliners?: EconomicIndicator[]
}

export interface ApiError {
  detail: string
  status?: number
}
