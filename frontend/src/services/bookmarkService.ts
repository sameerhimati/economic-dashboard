import { apiClient } from './api'
import type { Newsletter } from '@/types/newsletter'

export interface BookmarkList {
  id: string
  name: string
  newsletter_count: number
  created_at: string
  updated_at: string
}

export interface NewsletterInBookmark extends Newsletter {
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

export interface NewslettersInListResponse {
  newsletters: NewsletterInBookmark[]
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
   * Add a newsletter to a bookmark list
   */
  async addNewsletterToList(listId: string, newsletterId: string): Promise<void> {
    try {
      await apiClient.post(`/bookmarks/lists/${listId}/newsletters/${newsletterId}`)
    } catch (error: any) {
      console.error('Error adding newsletter to list:', error)

      if (error?.status === 404) {
        throw new Error('List or newsletter not found')
      }

      throw error
    }
  }

  /**
   * Remove a newsletter from a bookmark list
   */
  async removeNewsletterFromList(listId: string, newsletterId: string): Promise<void> {
    try {
      await apiClient.delete(`/bookmarks/lists/${listId}/newsletters/${newsletterId}`)
    } catch (error: any) {
      console.error('Error removing newsletter from list:', error)

      if (error?.status === 404) {
        throw new Error('List or newsletter not found')
      }

      throw error
    }
  }

  /**
   * Get all newsletters in a bookmark list
   */
  async getNewslettersInList(listId: string): Promise<NewsletterInBookmark[]> {
    try {
      const response = await apiClient.get<NewslettersInListResponse>(`/bookmarks/lists/${listId}/newsletters`)
      return response.data.newsletters || []
    } catch (error: any) {
      console.error('Error fetching newsletters in list:', error)

      if (error?.status === 404) {
        throw new Error('List not found')
      }

      throw error
    }
  }

  /**
   * Check which lists contain a specific newsletter
   * This is a helper method that compares newsletter IDs across all lists
   */
  async getListsContainingNewsletter(newsletterId: string): Promise<string[]> {
    try {
      const lists = await this.getLists()
      const listIds: string[] = []

      // Check each list to see if it contains this newsletter
      for (const list of lists) {
        try {
          const newsletters = await this.getNewslettersInList(list.id)
          if (newsletters.some(n => n.id === newsletterId)) {
            listIds.push(list.id)
          }
        } catch (error) {
          // If we can't fetch newsletters for a list, skip it
          console.warn(`Could not check list ${list.id}`, error)
        }
      }

      return listIds
    } catch (error) {
      console.error('Error checking lists containing newsletter:', error)
      throw error
    }
  }
}

export const bookmarkService = new BookmarkService()
