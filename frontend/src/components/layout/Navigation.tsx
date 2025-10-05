import { cn } from '@/lib/utils'
import { LayoutDashboard, TrendingUp, Newspaper, Calendar, Building2 } from 'lucide-react'
import { useLocation, Link } from 'react-router-dom'

interface NavItem {
  icon: React.ElementType
  label: string
  href: string
  isRoute?: boolean
}

const navItems: NavItem[] = [
  { icon: LayoutDashboard, label: 'Overview', href: '#overview' },
  { icon: TrendingUp, label: 'Metrics', href: '#metrics' },
  { icon: Newspaper, label: 'Breaking News', href: '#breaking' },
  { icon: Calendar, label: 'Weekly Summary', href: '#weekly' },
  { icon: Building2, label: 'Bisnow Articles', href: '/newsletters', isRoute: true },
]

export function Navigation() {
  const location = useLocation()

  const handleScroll = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault()
    const element = document.querySelector(href)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <nav className="border-b bg-background">
      <div className="container">
        <div className="flex gap-1 overflow-x-auto py-2">
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
      </div>
    </nav>
  )
}
