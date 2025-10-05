import { Header } from './Header'
import { Navigation } from './Navigation'
import { useDayGradient } from '@/hooks/useDayGradient'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const { gradientClass } = useDayGradient()

  return (
    <div className={`min-h-screen ${gradientClass} transition-colors duration-500`}>
      <Header />
      <Navigation />
      <main className="container mx-auto max-w-7xl px-4 py-8">
        {children}
      </main>
    </div>
  )
}
