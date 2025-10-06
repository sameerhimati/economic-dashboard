import { apiClient } from './api'
import type { Article, ArticleWithSources, ArticlesByCategory } from '@/types/article'

export interface ArticleListResponse {
  articles: Article[]
  count: number
  page?: number
  page_size?: number
}

export interface ArticlesByCategoryResponse {
  categories: ArticlesByCategory[]
  total_articles: number
}

export interface ArticleSearchResponse {
  articles: Article[]
  count: number
  total_count: number
  query: string
  page: number
  page_size: number
}

class ArticleService {
  /**
   * Get recent articles with optional grouping by category
   */
  async getRecent(limit: number = 100, groupByCategory: boolean = false): Promise<ArticlesByCategory[] | Article[]> {
    try {
      const params: Record<string, string | number | boolean> = { limit }

      if (groupByCategory) {
        params.group_by_category = true
        const response = await apiClient.get<ArticlesByCategoryResponse>('/articles/recent', { params })
        return response.data.categories
      } else {
        const response = await apiClient.get<ArticleListResponse>('/articles/recent', { params })
        return response.data.articles
      }
    } catch (error) {
      console.error('Error fetching recent articles:', error)
      throw error
    }
  }

  /**
   * Get articles by category
   */
  async getByCategory(category: string, limit: number = 50, offset: number = 0): Promise<Article[]> {
    try {
      const params = { category, limit, offset }
      const response = await apiClient.get<ArticleListResponse>('/articles/by-category', { params })
      return response.data.articles
    } catch (error) {
      console.error(`Error fetching articles for category ${category}:`, error)
      throw error
    }
  }

  /**
   * Search articles by query
   */
  async search(query: string, limit: number = 50, offset: number = 0): Promise<Article[]> {
    try {
      const params = { query, limit, offset }
      const response = await apiClient.get<ArticleSearchResponse>('/articles/search', { params })
      return response.data.articles
    } catch (error) {
      console.error('Error searching articles:', error)
      throw error
    }
  }

  /**
   * Get a single article by ID with source information
   */
  async getById(id: string): Promise<ArticleWithSources> {
    try {
      const response = await apiClient.get<ArticleWithSources>(`/articles/${id}`)
      return response.data
    } catch (error) {
      console.error(`Error fetching article ${id}:`, error)
      throw error
    }
  }
}

export const articleService = new ArticleService()
