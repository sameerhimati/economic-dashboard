import { useEffect } from 'react'

interface ShortcutHandlers {
  onRefresh?: () => void
  onSettings?: () => void
  onSearch?: () => void
}

export function useKeyboardShortcuts(handlers: ShortcutHandlers) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore if user is typing in an input
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement
      ) {
        return
      }

      // R for refresh
      if (event.key === 'r' || event.key === 'R') {
        event.preventDefault()
        handlers.onRefresh?.()
      }

      // ? for keyboard shortcuts help
      if (event.key === '?' && event.shiftKey) {
        event.preventDefault()
        // Could show a help modal here
      }

      // / for search
      if (event.key === '/') {
        event.preventDefault()
        handlers.onSearch?.()
      }

      // Cmd+K or Ctrl+K for settings
      if (event.key === 'k' && (event.metaKey || event.ctrlKey)) {
        event.preventDefault()
        handlers.onSettings?.()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handlers])
}
