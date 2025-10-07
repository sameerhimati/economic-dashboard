import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu'
import { TrendingUp, LogOut, Sun, Moon, Monitor, Settings, ChevronDown } from 'lucide-react'
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
        <div className="container flex h-14 items-center justify-between px-3 sm:px-4">
          <div className="flex items-center gap-2 sm:gap-2.5 min-w-0">
            <TrendingUp className="h-4 w-4 sm:h-5 sm:w-5 text-primary shrink-0" />
            <h1 className="text-sm sm:text-lg font-semibold tracking-tight truncate">
              Economic Dashboard
            </h1>
          </div>

          <div className="flex items-center gap-1 sm:gap-2 shrink-0">
            {user && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-2 h-9">
                    <Avatar className="h-7 w-7">
                      <AvatarFallback className="bg-primary/10 text-primary text-xs font-medium">
                        {getInitials(user?.full_name, user?.email)}
                      </AvatarFallback>
                    </Avatar>
                    <span className="hidden sm:inline text-sm font-medium">
                      {user?.full_name || user?.email?.split('@')[0] || 'User'}
                    </span>
                    <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel>
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{user?.full_name || 'User'}</p>
                      <p className="text-xs leading-none text-muted-foreground">{user?.email || ''}</p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />

                  <DropdownMenuItem onClick={() => setSettingsOpen(true)}>
                    <Settings className="mr-2 h-4 w-4" />
                    Dashboard Settings
                  </DropdownMenuItem>

                  <DropdownMenuSub>
                    <DropdownMenuSubTrigger>
                      {theme === 'light' ? (
                        <Sun className="mr-2 h-4 w-4" />
                      ) : theme === 'dark' ? (
                        <Moon className="mr-2 h-4 w-4" />
                      ) : (
                        <Monitor className="mr-2 h-4 w-4" />
                      )}
                      Theme
                    </DropdownMenuSubTrigger>
                    <DropdownMenuSubContent>
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
                    </DropdownMenuSubContent>
                  </DropdownMenuSub>

                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={logout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
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
