import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { TrendingUp, LogOut } from 'lucide-react'

export function Header() {
  const { user, logout } = useAuth()

  const getInitials = (name?: string) => {
    if (!name) return '??'
    const parts = name.split(' ').filter(part => part.length > 0)
    if (parts.length === 0) return '??'
    return parts
      .map((n) => n[0] || '')
      .join('')
      .toUpperCase()
      .slice(0, 2) || '??'
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between">
        <div className="flex items-center gap-2.5">
          <TrendingUp className="h-5 w-5 text-primary" />
          <h1 className="text-lg font-semibold tracking-tight">
            Economic Dashboard
          </h1>
        </div>

        <div className="flex items-center gap-4">
          {user && (
            <>
              <div className="flex items-center gap-3">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-primary/10 text-primary text-xs font-medium">
                    {getInitials(user?.username)}
                  </AvatarFallback>
                </Avatar>
                <div className="hidden sm:block">
                  <p className="text-sm font-medium leading-none">{user?.username || 'User'}</p>
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
  )
}
