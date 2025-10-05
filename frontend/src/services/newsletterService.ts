import { apiClient } from './api'
import type { Newsletter, NewsletterStats, NewsletterFilters } from '@/types/newsletter'

export interface SearchFilters extends NewsletterFilters {
  query: string
}

class NewsletterService {
  /**
   * Get recent newsletters with optional category filter
   */
  async getRecent(limit: number = 20, category?: string): Promise<Newsletter[]> {
    try {
      const params: Record<string, string | number> = { limit }
      if (category && category !== 'all') {
        params.category = category
      }

      const response = await apiClient.get<Newsletter[]>('/newsletters/recent', { params })
      return response.data
    } catch (error) {
      console.error('Error fetching recent newsletters:', error)
      throw error
    }
  }

  /**
   * Search newsletters by query
   */
  async search(query: string, filters?: NewsletterFilters): Promise<Newsletter[]> {
    try {
      const params: Record<string, string | number> = { query }

      if (filters?.category && filters.category !== 'all') {
        params.category = filters.category
      }
      if (filters?.limit) {
        params.limit = filters.limit
      }
      if (filters?.offset) {
        params.offset = filters.offset
      }

      const response = await apiClient.get<Newsletter[]>('/newsletters/search', { params })
      return response.data
    } catch (error) {
      console.error('Error searching newsletters:', error)
      throw error
    }
  }

  /**
   * Get a single newsletter by ID
   */
  async getById(id: string): Promise<Newsletter> {
    try {
      const response = await apiClient.get<Newsletter>(`/newsletters/${id}`)
      return response.data
    } catch (error) {
      console.error(`Error fetching newsletter ${id}:`, error)
      throw error
    }
  }

  /**
   * Get newsletter statistics
   */
  async getStats(): Promise<NewsletterStats> {
    try {
      const response = await apiClient.get<NewsletterStats>('/newsletters/stats/overview')
      return response.data
    } catch (error) {
      console.error('Error fetching newsletter stats:', error)
      throw error
    }
  }

  /**
   * Get all available categories
   */
  async getCategories(): Promise<string[]> {
    try {
      const response = await apiClient.get<string[]>('/newsletters/categories/list')
      return response.data
    } catch (error) {
      console.error('Error fetching categories:', error)
      throw error
    }
  }

  /**
   * Get top deals from recent newsletters
   * Extracts deal_value metrics from newsletters in the last N days
   */
  async getTopDeals(days: number = 7, limit: number = 5): Promise<Array<{
    value: string
    context: string
    newsletter: Newsletter
  }>> {
    try {
      const newsletters = await this.getRecent(50) // Fetch more to analyze

      const deals: Array<{
        value: string
        context: string
        newsletter: Newsletter
        numericValue: number
      }> = []

      const cutoffDate = new Date()
      cutoffDate.setDate(cutoffDate.getDate() - days)

      for (const newsletter of newsletters) {
        const receivedDate = new Date(newsletter.received_date)
        if (receivedDate < cutoffDate) continue

        const dealMetrics = newsletter.key_points.metrics.filter(
          m => m.type === 'deal_value'
        )

        for (const metric of dealMetrics) {
          // Extract numeric value for sorting
          const numericMatch = metric.value.match(/[\d,]+/)
          if (numericMatch) {
            const numericValue = parseFloat(numericMatch[0].replace(/,/g, ''))
            deals.push({
              value: metric.value,
              context: metric.context,
              newsletter,
              numericValue
            })
          }
        }
      }

      // Sort by numeric value descending
      deals.sort((a, b) => b.numericValue - a.numericValue)

      // Return top N deals without numeric value
      return deals.slice(0, limit).map(({ value, context, newsletter }) => ({
        value,
        context,
        newsletter
      }))
    } catch (error) {
      console.error('Error fetching top deals:', error)
      throw error
    }
  }
}

export const newsletterService = new NewsletterService()
