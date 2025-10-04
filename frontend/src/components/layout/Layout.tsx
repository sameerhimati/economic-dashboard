import { Header } from './Header'
import { Navigation } from './Navigation'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <Navigation />
      <main className="container py-6">
        {children}
      </main>
    </div>
  )
}
