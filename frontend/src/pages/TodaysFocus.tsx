import { Layout } from '@/components/layout/Layout'
import { PageTransition } from '@/components/ui/page-transition'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar, TrendingUp, AlertCircle, BarChart3 } from 'lucide-react'

export function TodaysFocus() {
  return (
    <Layout>
      <PageTransition>
        <div className="space-y-6 sm:space-y-8">
          {/* Header */}
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <Calendar className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">Today's Focus</h1>
                <p className="text-sm sm:text-base text-muted-foreground mt-1">
                  Your daily economic intelligence briefing
                </p>
              </div>
            </div>
          </div>

          {/* Coming Soon Card */}
          <Card className="border-2 border-dashed">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                Coming Soon
              </CardTitle>
              <CardDescription>
                An AI-powered daily economic briefing showing what changed today
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <p className="text-muted-foreground leading-relaxed">
                The Today's Focus feature will provide you with intelligent, context-aware economic insights
                tailored to each day of the week. Instead of raw numbers, you'll see what changed and why it matters.
              </p>

              <div className="space-y-4">
                <h3 className="font-semibold text-lg">Planned Features:</h3>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="flex gap-3">
                    <AlertCircle className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-medium mb-1">Intelligent Alerts</h4>
                      <p className="text-sm text-muted-foreground">
                        Automatic detection of significant changes, threshold crossings, and trend reversals
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <BarChart3 className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-medium mb-1">Historical Context</h4>
                      <p className="text-sm text-muted-foreground">
                        Compare today's values against 1D, 1W, 1M, and 1Y timeframes
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <Calendar className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-medium mb-1">Daily Themes</h4>
                      <p className="text-sm text-muted-foreground">
                        Curated metrics for each weekday: Fed rates on Monday, Housing on Tuesday, etc.
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <TrendingUp className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-medium mb-1">Interactive Charts</h4>
                      <p className="text-sm text-muted-foreground">
                        Dive deep into historical data with 30d, 90d, 1y, and 5y views
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground italic">
                  This feature is currently under development. Check back soon!
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </PageTransition>
    </Layout>
  )
}
