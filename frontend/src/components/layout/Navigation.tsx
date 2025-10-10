import { cn } from '@/lib/utils'
import { LayoutDashboard, Calendar, BookOpen, Menu, X } from 'lucide-react'
import { useLocation, Link } from 'react-router-dom'
import { useState } from 'react'
import { Button } from '@/components/ui/button'

interface NavItem {
  icon: React.ElementType
  label: string
  href: string
}

const navItems: NavItem[] = [
  { icon: LayoutDashboard, label: 'Overview', href: '/' },
  { icon: Calendar, label: "Today's Focus", href: '/focus' },
  { icon: BookOpen, label: 'Newsstand', href: '/newsstand' },
]

export function Navigation() {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleNavClick = () => {
    setMobileMenuOpen(false)
  }

  return (
    <nav className="border-b bg-background sticky top-14 z-40 shadow-sm">
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

        {/* Desktop Navigation */}
        <div className="hidden md:flex gap-1 py-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.href

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
          })}
        </div>

        {/* Mobile Navigation - dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t">
            <div className="py-2 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.href

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
              })}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
