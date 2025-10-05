import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { FileText, Calendar, FolderOpen } from 'lucide-react'
import { newsletterService } from '@/services/newsletterService'
import type { NewsletterStats } from '@/types/newsletter'
import { toast } from 'sonner'

const CATEGORY_COLORS = [
  '#3b82f6', // blue
  '#10b981', // green
  '#8b5cf6', // purple
  '#f97316', // orange
  '#ec4899', // pink
  '#eab308', // yellow
  '#6366f1', // indigo
  '#6b7280', // gray
]

export function NewsletterStats() {
  const [stats, setStats] = useState<NewsletterStats | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    const fetchStats = async () => {
      setIsLoading(true)
      try {
        const data = await newsletterService.getStats()
        setStats(data)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch stats'
        console.error('Error fetching newsletter stats:', errorMessage)
        toast.error('Error loading stats', {
          description: errorMessage
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchStats()
  }, [])

  // Transform categories data for chart
  const chartData = stats?.by_category
    ? Object.entries(stats.by_category)
        .map(([category, count]) => ({
          category: category.length > 20 ? category.substring(0, 20) + '...' : category,
          count,
          fullName: category
        }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 8) // Show top 8 categories
    : []

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <Skeleton className="h-4 w-24" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-8 w-16" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <Skeleton className="h-4 w-24" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-8 w-32" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <Skeleton className="h-4 w-24" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-8 w-20" />
          </CardContent>
        </Card>
      </div>
    )
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  // Show empty state if no data
  if (!stats || stats.total_newsletters === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col items-center justify-center space-y-4 py-12">
            <BarChart className="h-16 w-16 text-muted-foreground/50" />
            <div className="text-center space-y-2 max-w-md">
              <p className="text-lg font-medium">No statistics available</p>
              <p className="text-sm text-muted-foreground">
                Configure your email settings and fetch newsletters to see statistics and insights.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const categoryCount = Object.keys(stats.by_category || {}).length

  return (
    <div className="space-y-6">
      {/* Quick Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardDescription className="text-xs font-medium">Total Newsletters</CardDescription>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_newsletters.toLocaleString()}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardDescription className="text-xs font-medium">Latest Newsletter</CardDescription>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-semibold">
              {formatDate(stats.date_range?.latest)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardDescription className="text-xs font-medium">Categories</CardDescription>
              <FolderOpen className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{categoryCount}</div>
          </CardContent>
        </Card>
      </div>

      {/* Category Breakdown Chart */}
      {chartData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Newsletters by Category</CardTitle>
            <CardDescription>
              Distribution of newsletters across categories
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis
                    dataKey="category"
                    angle={-45}
                    textAnchor="end"
                    height={100}
                    tick={{ fontSize: 12 }}
                    className="text-muted-foreground"
                  />
                  <YAxis
                    tick={{ fontSize: 12 }}
                    className="text-muted-foreground"
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="rounded-lg border bg-background p-3 shadow-lg">
                            <div className="text-sm font-semibold mb-1">
                              {payload[0].payload.fullName}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {payload[0].value} newsletter{payload[0].value !== 1 ? 's' : ''}
                            </div>
                          </div>
                        )
                      }
                      return null
                    }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {chartData.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Category Legend */}
            <div className="mt-6 space-y-2">
              <h4 className="text-sm font-semibold text-muted-foreground">All Categories</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {Object.entries(stats.by_category)
                  .sort(([, a], [, b]) => (b as number) - (a as number))
                  .map(([category, count], index) => (
                    <div
                      key={category}
                      className="flex items-center gap-2 text-sm p-2 rounded-md hover:bg-muted/50 transition-colors"
                    >
                      <div
                        className="w-3 h-3 rounded-sm flex-shrink-0"
                        style={{
                          backgroundColor: CATEGORY_COLORS[index % CATEGORY_COLORS.length]
                        }}
                      />
                      <span className="flex-1 truncate" title={category}>
                        {category}
                      </span>
                      <span className="text-muted-foreground font-medium">
                        {count as number}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
