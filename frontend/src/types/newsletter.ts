export type MetricType = 'cap_rate' | 'deal_value' | 'square_footage' | 'price_per_sf' | 'occupancy_rate'

export interface Article {
  headline: string
  url: string
}

export interface NewsletterMetric {
  type: MetricType
  value: string
  context: string
}

export interface NewsletterKeyPoints {
  headlines: string[]
  articles: Article[]
  metrics: NewsletterMetric[]
  locations: string[]
  companies: string[]
}

export interface Newsletter {
  id: string
  source: string
  category: string
  subject: string
  content_html?: string
  content_text?: string
  key_points: NewsletterKeyPoints
  received_date: string
  parsed_date: string
  created_at: string
  updated_at: string
}

export interface NewsletterStats {
  total_newsletters: number
  by_category: Record<string, number>
  by_source: Record<string, number>
  date_range?: {
    earliest: string
    latest: string
  }
  recent_count: number
}

export interface NewsletterFilters {
  category?: string
  limit?: number
  offset?: number
}
