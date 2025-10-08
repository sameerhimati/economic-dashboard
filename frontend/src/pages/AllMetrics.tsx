import { Layout } from '@/components/layout/Layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PageTransition } from '@/components/ui/page-transition'
import { BarChart3, TrendingUp, Calendar } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

export function AllMetrics() {
  return (
    <Layout>
      <PageTransition>
        <div className="space-y-8">
          {/* Hero Section */}
          <div className="space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                  All Economic Metrics
                </h1>
                <p className="text-base sm:text-lg text-muted-foreground mt-2">
                  Comprehensive view of all tracked economic indicators
                </p>
              </div>
              <Badge variant="secondary" className="gap-1">
                <Calendar className="h-3 w-3" />
                Live
              </Badge>
            </div>
          </div>

          {/* Coming Soon Card */}
          <Card className="bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-6 w-6 text-primary" />
                Metrics Explorer
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-3">
                <TrendingUp className="h-5 w-5 text-primary mt-0.5 shrink-0" />
                <div>
                  <h3 className="font-semibold mb-2">Comprehensive Metrics View</h3>
                  <p className="text-sm text-muted-foreground">
                    This page will provide a comprehensive view of all economic metrics tracked by the
                    dashboard. You'll be able to search, filter, and compare metrics across different
                    categories and time periods.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <BarChart3 className="h-5 w-5 text-primary mt-0.5 shrink-0" />
                <div>
                  <h3 className="font-semibold mb-2">Advanced Filtering</h3>
                  <p className="text-sm text-muted-foreground">
                    Filter metrics by category, data source, frequency, and time range. Create custom
                    views to track the indicators most relevant to your analysis.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <TrendingUp className="h-5 w-5 text-primary mt-0.5 shrink-0" />
                <div>
                  <h3 className="font-semibold mb-2">Interactive Visualizations</h3>
                  <p className="text-sm text-muted-foreground">
                    Compare multiple metrics side-by-side, overlay trends, and identify correlations
                    with advanced charting capabilities.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Links */}
          <Card>
            <CardHeader>
              <CardTitle>Explore the Dashboard</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <a
                  href="/"
                  className="p-4 rounded-lg border border-border hover:border-primary/50 hover:bg-primary/5 transition-colors"
                >
                  <h3 className="font-semibold mb-1">Economic Command Center</h3>
                  <p className="text-sm text-muted-foreground">
                    View all categories and The Big 5 indicators
                  </p>
                </a>
                <a
                  href="/focus"
                  className="p-4 rounded-lg border border-border hover:border-primary/50 hover:bg-primary/5 transition-colors"
                >
                  <h3 className="font-semibold mb-1">Today's Focus</h3>
                  <p className="text-sm text-muted-foreground">
                    Daily themed economic briefing with focused insights
                  </p>
                </a>
                <a
                  href="/newsstand"
                  className="p-4 rounded-lg border border-border hover:border-primary/50 hover:bg-primary/5 transition-colors"
                >
                  <h3 className="font-semibold mb-1">Newsstand</h3>
                  <p className="text-sm text-muted-foreground">
                    Latest economic news and market updates
                  </p>
                </a>
                <a
                  href="/settings"
                  className="p-4 rounded-lg border border-border hover:border-primary/50 hover:bg-primary/5 transition-colors"
                >
                  <h3 className="font-semibold mb-1">Settings</h3>
                  <p className="text-sm text-muted-foreground">
                    Customize your dashboard experience
                  </p>
                </a>
              </div>
            </CardContent>
          </Card>
        </div>
      </PageTransition>
    </Layout>
  )
}
