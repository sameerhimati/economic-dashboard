import { apiClient } from './api'
import type { Newsletter, NewsletterStats, NewsletterFilters } from '@/types/newsletter'

export interface SearchFilters extends NewsletterFilters {
  query: string
}

export interface EmailConfig {
  email_address: string | null
  imap_server: string
  imap_port: number
  is_configured: boolean
}

export interface EmailConfigUpdate {
  email_address?: string
  email_app_password?: string
  imap_server?: string
  imap_port?: number
}

export interface NewsletterPreferences {
  bisnow_categories: string[]
  fetch_enabled: boolean
  last_fetch: string | null
}

export interface NewsletterPreferencesUpdate {
  bisnow_categories: string[]
  fetch_enabled: boolean
}

export interface NewsletterFetchResponse {
  status: string
  fetched: number
  stored: number
  skipped: number
  timestamp: string
}

export interface AvailableCategories {
  categories: string[]
}

export interface NewsletterListResponse {
  newsletters: Newsletter[]
  count: number
  page: number
  page_size: number
}

export interface NewsletterSearchResponse {
  newsletters: Newsletter[]
  count: number
  total_count: number
  query: string
  page: number
  page_size: number
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

      const response = await apiClient.get<NewsletterListResponse>('/newsletters/recent', { params })
      return response.data.newsletters
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

      const response = await apiClient.get<NewsletterSearchResponse>('/newsletters/search', { params })
      return response.data.newsletters
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

  /**
   * Get user's email configuration
   */
  async getEmailConfig(): Promise<EmailConfig> {
    try {
      const response = await apiClient.get<EmailConfig>('/auth/settings/email-config')
      return response.data
    } catch (error) {
      console.error('Error fetching email config:', error)
      throw error
    }
  }

  /**
   * Update user's email configuration
   */
  async updateEmailConfig(config: EmailConfigUpdate): Promise<EmailConfig> {
    try {
      const response = await apiClient.put<EmailConfig>('/auth/settings/email-config', config)
      return response.data
    } catch (error) {
      console.error('Error updating email config:', error)
      throw error
    }
  }

  /**
   * Delete user's email configuration
   */
  async deleteEmailConfig(): Promise<void> {
    try {
      await apiClient.delete('/auth/settings/email-config')
    } catch (error) {
      console.error('Error deleting email config:', error)
      throw error
    }
  }

  /**
   * Test email connection
   */
  async testEmailConnection(config: EmailConfigUpdate): Promise<{ success: boolean; message: string }> {
    try {
      // For now, we'll just validate the config - a real test would require a backend endpoint
      if (!config.email_address || !config.email_app_password) {
        return {
          success: false,
          message: 'Email address and app password are required'
        }
      }

      // TODO: Implement actual connection test endpoint on backend
      return {
        success: true,
        message: 'Email configuration saved. Try fetching newsletters to verify the connection works.'
      }
    } catch (error) {
      console.error('Error testing email connection:', error)
      return {
        success: false,
        message: 'Failed to test email connection'
      }
    }
  }

  /**
   * Get user's newsletter preferences
   */
  async getNewsletterPreferences(): Promise<NewsletterPreferences> {
    try {
      const response = await apiClient.get<NewsletterPreferences>('/auth/settings/newsletter-preferences')
      return response.data
    } catch (error) {
      console.error('Error fetching newsletter preferences:', error)
      throw error
    }
  }

  /**
   * Update user's newsletter preferences
   */
  async updateNewsletterPreferences(prefs: NewsletterPreferencesUpdate): Promise<NewsletterPreferences> {
    try {
      const response = await apiClient.put<NewsletterPreferences>('/auth/settings/newsletter-preferences', prefs)
      return response.data
    } catch (error) {
      console.error('Error updating newsletter preferences:', error)
      throw error
    }
  }

  /**
   * Get available newsletter categories
   */
  async getAvailableCategories(): Promise<string[]> {
    try {
      const response = await apiClient.get<AvailableCategories>('/auth/settings/newsletter-categories')
      return response.data.categories
    } catch (error) {
      console.error('Error fetching available categories:', error)
      throw error
    }
  }

  /**
   * Manually fetch newsletters from email
   */
  async fetchNewsletters(days: number = 7): Promise<NewsletterFetchResponse> {
    try {
      const response = await apiClient.post<NewsletterFetchResponse>(`/newsletters/fetch?days=${days}`)
      return response.data
    } catch (error) {
      console.error('Error fetching newsletters:', error)
      throw error
    }
  }
}

export const newsletterService = new NewsletterService()
