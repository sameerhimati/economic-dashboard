import { cn } from '@/lib/utils'
import { LayoutDashboard, TrendingUp, Newspaper, Calendar } from 'lucide-react'

interface NavItem {
  icon: React.ElementType
  label: string
  href: string
}

const navItems: NavItem[] = [
  { icon: LayoutDashboard, label: 'Overview', href: '#overview' },
  { icon: TrendingUp, label: 'Metrics', href: '#metrics' },
  { icon: Newspaper, label: 'Breaking News', href: '#breaking' },
  { icon: Calendar, label: 'Weekly Summary', href: '#weekly' },
]

export function Navigation() {
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
