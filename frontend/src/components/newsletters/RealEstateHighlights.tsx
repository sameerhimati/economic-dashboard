import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Building2, ExternalLink, ChevronRight } from 'lucide-react'
import { newsletterService } from '@/services/newsletterService'
import type { Newsletter } from '@/types/newsletter'
import { cn } from '@/lib/utils'

interface RealEstateHighlightsProps {
  limit?: number
  showViewAll?: boolean
  onViewAll?: () => void
}

export function RealEstateHighlights({
  limit = 5,
  showViewAll = true,
  onViewAll
}: RealEstateHighlightsProps) {
  const [highlights, setHighlights] = useState<Array<{
    headline: string
    newsletter: Newsletter
  }>>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    const fetchHighlights = async () => {
      setIsLoading(true)
      try {
        const newsletters = await newsletterService.getRecent(10)

        // Extract headlines from newsletters
        const allHighlights: Array<{
          headline: string
          newsletter: Newsletter
        }> = []

        for (const newsletter of newsletters) {
          for (const headline of newsletter.key_points.headlines) {
            allHighlights.push({ headline, newsletter })
          }
        }

        // Take the most recent highlights
        setHighlights(allHighlights.slice(0, limit))
      } catch (err) {
        console.error('Error fetching real estate highlights:', err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchHighlights()
  }, [limit])

  if (isLoading) {
    return (
      <Card className="border-orange-500/20 bg-gradient-to-br from-orange-500/5 to-transparent">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Building2 className="h-6 w-6 text-orange-500" />
            <div>
              <Skeleton className="h-6 w-48 mb-2" />
              <Skeleton className="h-4 w-64" />
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </CardContent>
      </Card>
    )
  }

  if (highlights.length === 0) {
    return (
      <Card className="border-orange-500/20 bg-gradient-to-br from-orange-500/5 to-transparent">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Building2 className="h-6 w-6 text-orange-500" />
            <div>
              <CardTitle>Tuesday's Real Estate Focus</CardTitle>
              <CardDescription>Latest Bisnow real estate headlines</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No real estate newsletters available yet
          </p>
        </CardContent>
      </Card>
    )
  }

  const getCategoryBadgeColor = (category: string): "blue" | "green" | "purple" | "orange" | "pink" => {
    const categoryLower = category.toLowerCase()
    if (categoryLower.includes('houston')) return 'blue'
    if (categoryLower.includes('austin')) return 'green'
    if (categoryLower.includes('national')) return 'purple'
    if (categoryLower.includes('multifamily')) return 'pink'
    return 'orange'
  }

  return (
    <Card className="border-orange-500/20 bg-gradient-to-br from-orange-500/5 to-transparent overflow-hidden">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-2">
            <Building2 className="h-6 w-6 text-orange-500" />
            <div>
              <CardTitle className="text-2xl">Tuesday's Real Estate Focus</CardTitle>
              <CardDescription>Latest Bisnow real estate headlines</CardDescription>
            </div>
          </div>
          {showViewAll && onViewAll && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onViewAll}
              className="text-orange-600 hover:text-orange-700 hover:bg-orange-100"
            >
              View All
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {highlights.map((item, index) => (
            <div
              key={index}
              className={cn(
                "group relative p-4 rounded-lg border border-transparent bg-background/50",
                "hover:border-orange-500/30 hover:bg-orange-500/5 hover:shadow-sm",
                "transition-all duration-200 cursor-pointer"
              )}
            >
              <div className="flex items-start gap-3">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge
                      variant={getCategoryBadgeColor(item.newsletter.category)}
                      className="text-xs"
                    >
                      {item.newsletter.category}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {new Date(item.newsletter.received_date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                  <p className="text-sm font-medium leading-relaxed group-hover:text-orange-600 transition-colors">
                    {item.headline}
                  </p>
                </div>
                <ExternalLink className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
