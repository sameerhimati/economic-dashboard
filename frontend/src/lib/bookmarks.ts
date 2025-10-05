/**
 * Bookmark management utilities using localStorage
 * Stores bookmarked newsletter IDs
 */

const BOOKMARK_STORAGE_KEY = 'newsletter-bookmarks'

export interface BookmarkState {
  newsletterIds: string[]
  lastUpdated: string
}

/**
 * Get all bookmarked newsletter IDs
 */
export function getBookmarks(): string[] {
  try {
    const stored = localStorage.getItem(BOOKMARK_STORAGE_KEY)
    if (!stored) return []

    const state: BookmarkState = JSON.parse(stored)
    return state.newsletterIds || []
  } catch (error) {
    console.error('Error reading bookmarks:', error)
    return []
  }
}

/**
 * Check if a newsletter is bookmarked
 */
export function isBookmarked(newsletterId: string): boolean {
  const bookmarks = getBookmarks()
  return bookmarks.includes(newsletterId)
}

/**
 * Add a newsletter to bookmarks
 */
export function addBookmark(newsletterId: string): void {
  try {
    const bookmarks = getBookmarks()

    // Avoid duplicates
    if (bookmarks.includes(newsletterId)) {
      return
    }

    const newState: BookmarkState = {
      newsletterIds: [...bookmarks, newsletterId],
      lastUpdated: new Date().toISOString()
    }

    localStorage.setItem(BOOKMARK_STORAGE_KEY, JSON.stringify(newState))
  } catch (error) {
    console.error('Error adding bookmark:', error)
    throw new Error('Failed to add bookmark')
  }
}

/**
 * Remove a newsletter from bookmarks
 */
export function removeBookmark(newsletterId: string): void {
  try {
    const bookmarks = getBookmarks()
    const filtered = bookmarks.filter(id => id !== newsletterId)

    const newState: BookmarkState = {
      newsletterIds: filtered,
      lastUpdated: new Date().toISOString()
    }

    localStorage.setItem(BOOKMARK_STORAGE_KEY, JSON.stringify(newState))
  } catch (error) {
    console.error('Error removing bookmark:', error)
    throw new Error('Failed to remove bookmark')
  }
}

/**
 * Toggle bookmark state for a newsletter
 * Returns the new bookmark state (true = bookmarked, false = not bookmarked)
 */
export function toggleBookmark(newsletterId: string): boolean {
  const currentlyBookmarked = isBookmarked(newsletterId)

  if (currentlyBookmarked) {
    removeBookmark(newsletterId)
    return false
  } else {
    addBookmark(newsletterId)
    return true
  }
}

/**
 * Clear all bookmarks
 */
export function clearAllBookmarks(): void {
  try {
    localStorage.removeItem(BOOKMARK_STORAGE_KEY)
  } catch (error) {
    console.error('Error clearing bookmarks:', error)
    throw new Error('Failed to clear bookmarks')
  }
}

/**
 * Get bookmark count
 */
export function getBookmarkCount(): number {
  return getBookmarks().length
}
