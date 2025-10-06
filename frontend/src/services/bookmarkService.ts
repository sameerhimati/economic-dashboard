import { apiClient } from './api'
import type { Article } from '@/types/article'

export interface BookmarkList {
  id: string
  name: string
  article_count: number
  created_at: string
  updated_at: string
}

export interface ArticleInBookmark extends Article {
  bookmarked_at: string
}

export interface CreateBookmarkListRequest {
  name: string
}

export interface UpdateBookmarkListRequest {
  name: string
}

export interface BookmarkListResponse {
  lists: BookmarkList[]
}

export interface ArticlesInListResponse {
  articles: ArticleInBookmark[]
}

class BookmarkService {
  /**
   * Get all bookmark lists for the current user
   */
  async getLists(): Promise<BookmarkList[]> {
    try {
      const response = await apiClient.get<BookmarkListResponse>('/bookmarks/lists')
      return response.data.lists || []
    } catch (error) {
      console.error('Error fetching bookmark lists:', error)
      throw error
    }
  }

  /**
   * Create a new bookmark list
   */
  async createList(name: string): Promise<BookmarkList> {
    try {
      const response = await apiClient.post<BookmarkList>('/bookmarks/lists', { name })
      return response.data
    } catch (error: any) {
      console.error('Error creating bookmark list:', error)

      // Handle specific error cases
      if (error?.status === 400) {
        throw new Error('Maximum 10 bookmark lists reached')
      }
      if (error?.status === 409) {
        throw new Error('A list with this name already exists')
      }

      throw error
    }
  }

  /**
   * Update a bookmark list name
   */
  async updateList(listId: string, name: string): Promise<BookmarkList> {
    try {
      const response = await apiClient.put<BookmarkList>(`/bookmarks/lists/${listId}`, { name })
      return response.data
    } catch (error: any) {
      console.error('Error updating bookmark list:', error)

      if (error?.status === 404) {
        throw new Error('List not found')
      }
      if (error?.status === 409) {
        throw new Error('A list with this name already exists')
      }

      throw error
    }
  }

  /**
   * Delete a bookmark list
   */
  async deleteList(listId: string): Promise<void> {
    try {
      await apiClient.delete(`/bookmarks/lists/${listId}`)
    } catch (error: any) {
      console.error('Error deleting bookmark list:', error)

      if (error?.status === 404) {
        throw new Error('List not found')
      }

      throw error
    }
  }

  /**
   * Add an article to a bookmark list
   */
  async addArticleToList(listId: string, articleId: string): Promise<void> {
    try {
      await apiClient.post(`/bookmarks/lists/${listId}/articles/${articleId}`)
    } catch (error: any) {
      console.error('Error adding article to list:', error)

      if (error?.status === 404) {
        throw new Error('List or article not found')
      }

      throw error
    }
  }

  /**
   * Remove an article from a bookmark list
   */
  async removeArticleFromList(listId: string, articleId: string): Promise<void> {
    try {
      await apiClient.delete(`/bookmarks/lists/${listId}/articles/${articleId}`)
    } catch (error: any) {
      console.error('Error removing article from list:', error)

      if (error?.status === 404) {
        throw new Error('List or article not found')
      }

      throw error
    }
  }

  /**
   * Get all articles in a bookmark list
   */
  async getArticlesInList(listId: string): Promise<ArticleInBookmark[]> {
    try {
      const response = await apiClient.get<ArticlesInListResponse>(`/bookmarks/lists/${listId}/articles`)
      return response.data.articles || []
    } catch (error: any) {
      console.error('Error fetching articles in list:', error)

      if (error?.status === 404) {
        throw new Error('List not found')
      }

      throw error
    }
  }

  /**
   * Check which lists contain a specific article
   * This is a helper method that compares article IDs across all lists
   */
  async getListsContainingArticle(articleId: string): Promise<string[]> {
    try {
      const lists = await this.getLists()
      const listIds: string[] = []

      // Check each list to see if it contains this article
      for (const list of lists) {
        try {
          const articles = await this.getArticlesInList(list.id)
          if (articles.some(a => a.id === articleId)) {
            listIds.push(list.id)
          }
        } catch (error) {
          // If we can't fetch articles for a list, skip it
          console.warn(`Could not check list ${list.id}`, error)
        }
      }

      return listIds
    } catch (error) {
      console.error('Error checking lists containing article:', error)
      throw error
    }
  }
}

export const bookmarkService = new BookmarkService()
