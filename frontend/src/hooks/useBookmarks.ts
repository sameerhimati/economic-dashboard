import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface BookmarksState {
  bookmarkedIds: Set<string>
  isBookmarked: (id: string) => boolean
  toggleBookmark: (id: string) => void
  clearBookmarks: () => void
}

export const useBookmarks = create<BookmarksState>()(
  persist(
    (set, get) => ({
      bookmarkedIds: new Set<string>(),

      isBookmarked: (id: string) => {
        return get().bookmarkedIds.has(id)
      },

      toggleBookmark: (id: string) => {
        set((state) => {
          const newBookmarks = new Set(state.bookmarkedIds)
          if (newBookmarks.has(id)) {
            newBookmarks.delete(id)
          } else {
            newBookmarks.add(id)
          }
          return { bookmarkedIds: newBookmarks }
        })
      },

      clearBookmarks: () => {
        set({ bookmarkedIds: new Set<string>() })
      },
    }),
    {
      name: 'economic-dashboard-bookmarks',
      storage: {
        getItem: (name) => {
          const str = localStorage.getItem(name)
          if (!str) return null
          const { state } = JSON.parse(str)
          return {
            state: {
              ...state,
              bookmarkedIds: new Set(state.bookmarkedIds || []),
            },
          }
        },
        setItem: (name, value) => {
          const { state } = value
          localStorage.setItem(
            name,
            JSON.stringify({
              state: {
                ...state,
                bookmarkedIds: Array.from(state.bookmarkedIds),
              },
            })
          )
        },
        removeItem: (name) => localStorage.removeItem(name),
      },
    }
  )
)
