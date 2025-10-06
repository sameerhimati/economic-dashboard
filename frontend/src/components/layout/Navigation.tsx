import { cn } from '@/lib/utils'
import { LayoutDashboard, TrendingUp, Newspaper, Calendar, BookOpen, Bookmark, Settings, Menu, X } from 'lucide-react'
import { useLocation, Link } from 'react-router-dom'
import { useState } from 'react'
import { Button } from '@/components/ui/button'

interface NavItem {
  icon: React.ElementType
  label: string
  href: string
  isRoute?: boolean
}

const navItems: NavItem[] = [
  { icon: LayoutDashboard, label: 'Overview', href: '/', isRoute: true },
  { icon: TrendingUp, label: 'Metrics', href: '#metrics' },
  { icon: Newspaper, label: 'Breaking News', href: '#breaking' },
  { icon: Calendar, label: 'Weekly Summary', href: '#weekly' },
  { icon: BookOpen, label: 'Newsstand', href: '/newsstand', isRoute: true },
  { icon: Bookmark, label: 'Bookmarks', href: '/bookmarks', isRoute: true },
  { icon: Settings, label: 'Settings', href: '/settings', isRoute: true },
]

export function Navigation() {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleScroll = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault()
    const element = document.querySelector(href)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
    setMobileMenuOpen(false)
  }

  const handleNavClick = () => {
    setMobileMenuOpen(false)
  }

  return (
    <nav className="border-b bg-background sticky top-14 z-40">
      <div className="container px-3 sm:px-4">
        {/* Mobile Menu Button */}
        <div className="flex md:hidden items-center justify-between py-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="gap-2"
          >
            {mobileMenuOpen ? (
              <X className="h-4 w-4" />
            ) : (
              <Menu className="h-4 w-4" />
            )}
            <span className="text-sm font-medium">Menu</span>
          </Button>
        </div>

        {/* Desktop Navigation - horizontal scroll */}
        <div className="hidden md:flex gap-1 overflow-x-auto py-2 scrollbar-hide">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = item.isRoute && location.pathname === item.href

            if (item.isRoute) {
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors whitespace-nowrap',
                    'hover:bg-accent hover:text-accent-foreground',
                    'text-sm font-medium',
                    isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              )
            }

            return (
              <a
                key={item.href}
                href={item.href}
                onClick={(e) => handleScroll(e, item.href)}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors whitespace-nowrap',
                  'hover:bg-accent hover:text-accent-foreground',
                  'text-sm font-medium text-muted-foreground'
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </a>
            )
          })}
        </div>

        {/* Mobile Navigation - dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t">
            <div className="py-2 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = item.isRoute && location.pathname === item.href

                if (item.isRoute) {
                  return (
                    <Link
                      key={item.href}
                      to={item.href}
                      onClick={handleNavClick}
                      className={cn(
                        'flex items-center gap-3 px-3 py-3 rounded-lg transition-colors',
                        'hover:bg-accent hover:text-accent-foreground',
                        'text-sm font-medium',
                        'active:scale-98',
                        isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'
                      )}
                    >
                      <Icon className="h-5 w-5" />
                      <span>{item.label}</span>
                    </Link>
                  )
                }

                return (
                  <a
                    key={item.href}
                    href={item.href}
                    onClick={(e) => handleScroll(e, item.href)}
                    className={cn(
                      'flex items-center gap-3 px-3 py-3 rounded-lg transition-colors',
                      'hover:bg-accent hover:text-accent-foreground',
                      'text-sm font-medium text-muted-foreground',
                      'active:scale-98'
                    )}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.label}</span>
                  </a>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
