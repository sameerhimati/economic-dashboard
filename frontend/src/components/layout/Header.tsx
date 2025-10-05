import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { TrendingUp, LogOut, Sun, Moon, Monitor, Settings } from 'lucide-react'
import { useEffect, useState, useCallback } from 'react'
import { SettingsModal } from '@/components/settings/SettingsModal'
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'

type Theme = 'light' | 'dark' | 'system'

export function Header() {
  const { user, logout } = useAuth()
  const [theme, setTheme] = useState<Theme>(() => {
    const savedTheme = localStorage.getItem('theme') as Theme
    return savedTheme || 'dark'
  })
  const [settingsOpen, setSettingsOpen] = useState(false)

  const handleOpenSettings = useCallback(() => {
    setSettingsOpen(true)
  }, [])

  // Add keyboard shortcut for settings
  useKeyboardShortcuts({
    onSettings: handleOpenSettings,
  })

  useEffect(() => {
    const root = document.documentElement

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      root.classList.remove('light', 'dark')
      root.classList.add(systemTheme)
    } else {
      root.classList.remove('light', 'dark')
      root.classList.add(theme)
    }

    localStorage.setItem('theme', theme)
  }, [theme])

  const getInitials = (name?: string, email?: string) => {
    if (!name && !email) return '??'
    const displayName = name || email?.split('@')[0] || '??'
    const parts = displayName.split(' ').filter(part => part.length > 0)
    if (parts.length === 0) return '??'
    return parts
      .map((n) => n[0] || '')
      .join('')
      .toUpperCase()
      .slice(0, 2) || '??'
  }

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center justify-between px-4">
          <div className="flex items-center gap-2.5">
            <TrendingUp className="h-5 w-5 text-primary" />
            <h1 className="text-lg font-semibold tracking-tight">
              Economic Dashboard
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSettingsOpen(true)}
              className="h-8 w-8"
              title="Settings (Cmd+K)"
            >
              <Settings className="h-4 w-4" />
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  {theme === 'light' ? (
                    <Sun className="h-4 w-4" />
                  ) : theme === 'dark' ? (
                    <Moon className="h-4 w-4" />
                  ) : (
                    <Monitor className="h-4 w-4" />
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setTheme('light')}>
                  <Sun className="mr-2 h-4 w-4" />
                  Light
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTheme('dark')}>
                  <Moon className="mr-2 h-4 w-4" />
                  Dark
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTheme('system')}>
                  <Monitor className="mr-2 h-4 w-4" />
                  System
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {user && (
              <>
                <div className="flex items-center gap-3">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-primary/10 text-primary text-xs font-medium">
                      {getInitials(user?.full_name, user?.email)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="hidden sm:block">
                    <p className="text-sm font-medium leading-none">{user?.full_name || user?.email || 'User'}</p>
                    <p className="text-xs text-muted-foreground mt-1">{user?.email || ''}</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon" onClick={logout} className="h-8 w-8">
                  <LogOut className="h-4 w-4" />
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      <SettingsModal
        open={settingsOpen}
        onOpenChange={setSettingsOpen}
        theme={theme}
        onThemeChange={setTheme}
      />
    </>
  )
}
