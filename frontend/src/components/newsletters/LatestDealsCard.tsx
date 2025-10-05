import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { DollarSign, TrendingUp, MapPin, Calendar } from 'lucide-react'
import { newsletterService } from '@/services/newsletterService'
import type { Newsletter } from '@/types/newsletter'
import { cn } from '@/lib/utils'

interface DealInfo {
  value: string
  context: string
  newsletter: Newsletter
}

export function LatestDealsCard() {
  const [topDeal, setTopDeal] = useState<DealInfo | null>(null)
  const [recentDeals, setRecentDeals] = useState<DealInfo[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    const fetchDeals = async () => {
      setIsLoading(true)
      try {
        const deals = await newsletterService.getTopDeals(7, 4)

        if (deals.length > 0) {
          setTopDeal(deals[0])
          setRecentDeals(deals.slice(1, 4))
        }
      } catch (err) {
        console.error('Error fetching latest deals:', err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDeals()
  }, [])

  if (isLoading) {
    return (
      <Card className="border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 via-emerald-500/5 to-transparent">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Skeleton className="h-8 w-8 rounded-full" />
            <div className="flex-1">
              <Skeleton className="h-6 w-32 mb-2" />
              <Skeleton className="h-4 w-48" />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-24 w-full mb-4" />
          <div className="space-y-2">
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!topDeal) {
    return (
      <Card className="border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 via-emerald-500/5 to-transparent">
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-full bg-emerald-500/10">
              <DollarSign className="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <CardTitle>Latest Deals</CardTitle>
              <CardDescription>Top real estate transactions</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No deals available in the last 7 days
          </p>
        </CardContent>
      </Card>
    )
  }

  const getDaysAgo = (dateString: string): string => {
    const date = new Date(dateString)
    const now = new Date()
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))

    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    return `${diffDays}d ago`
  }

  return (
    <Card className="border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 via-emerald-500/5 to-transparent overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl -z-10" />

      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-full bg-emerald-500/10 ring-4 ring-emerald-500/10">
            <DollarSign className="h-5 w-5 text-emerald-600" />
          </div>
          <div>
            <CardTitle className="text-2xl">Latest Deals</CardTitle>
            <CardDescription>Top real estate transactions this week</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Top Deal - Featured */}
        <div className="relative p-5 rounded-xl bg-gradient-to-br from-emerald-500/10 to-emerald-500/5 border border-emerald-500/20 shadow-lg">
          <div className="absolute top-3 right-3">
            <Badge variant="outline" className="bg-emerald-500/10 border-emerald-500/30 text-emerald-700">
              <TrendingUp className="h-3 w-3 mr-1" />
              Top Deal
            </Badge>
          </div>

          <div className="space-y-3">
            <div>
              <div className="text-3xl font-bold text-emerald-600 mb-1">
                {topDeal.value}
              </div>
              <p className="text-sm text-foreground leading-relaxed">
                {topDeal.context}
              </p>
            </div>

            <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
              <div className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                <span className="font-medium">{topDeal.newsletter.category}</span>
              </div>
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                <span>{getDaysAgo(topDeal.newsletter.received_date)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Deals */}
        {recentDeals.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              More Recent Deals
            </h4>
            <div className="space-y-2">
              {recentDeals.map((deal, index) => (
                <div
                  key={index}
                  className={cn(
                    "p-3 rounded-lg bg-background/50 border border-transparent",
                    "hover:border-emerald-500/20 hover:bg-emerald-500/5",
                    "transition-all duration-200"
                  )}
                >
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <span className="text-base font-bold text-emerald-600">
                      {deal.value}
                    </span>
                    <span className="text-xs text-muted-foreground flex-shrink-0">
                      {getDaysAgo(deal.newsletter.received_date)}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {deal.context}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
