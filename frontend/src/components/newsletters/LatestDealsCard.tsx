import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { DollarSign, TrendingUp, MapPin, Calendar, ExternalLink } from 'lucide-react'
import { newsletterService } from '@/services/newsletterService'
import { NewsletterModal } from './NewsletterModal'
import type { Newsletter } from '@/types/newsletter'
import { cn } from '@/lib/utils'

interface DealInfo {
  value: string
  context: string
  newsletter: Newsletter
}

interface LatestDealsCardProps {
  className?: string
}

export function LatestDealsCard({ className }: LatestDealsCardProps = {}) {
  const [topDeal, setTopDeal] = useState<DealInfo | null>(null)
  const [recentDeals, setRecentDeals] = useState<DealInfo[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [selectedNewsletter, setSelectedNewsletter] = useState<Newsletter | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  useEffect(() => {
    const fetchDeals = async () => {
      setIsLoading(true)
      try {
        const deals = await newsletterService.getTopDeals(7, 5)

        if (deals.length > 0) {
          setTopDeal(deals[0])
          setRecentDeals(deals.slice(1, 5))
        }
      } catch (err) {
        console.error('Error fetching latest deals:', err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDeals()
  }, [])

  const handleDealClick = (newsletter: Newsletter) => {
    setSelectedNewsletter(newsletter)
    setModalOpen(true)
  }

  const getLocationFromNewsletter = (newsletter: Newsletter): string | null => {
    if (newsletter.key_points.locations && newsletter.key_points.locations.length > 0) {
      return newsletter.key_points.locations[0]
    }
    return null
  }

  if (isLoading) {
    return (
      <Card className={cn("border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 via-emerald-500/5 to-transparent", className)}>
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
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!topDeal) {
    return (
      <Card className={cn("border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 via-emerald-500/5 to-transparent", className)}>
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

  const topDealLocation = getLocationFromNewsletter(topDeal.newsletter)

  return (
    <>
      <Card className={cn("border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 via-emerald-500/5 to-transparent overflow-hidden", className)}>
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
          <div
            onClick={() => handleDealClick(topDeal.newsletter)}
            className="group relative p-5 rounded-xl bg-gradient-to-br from-emerald-500/10 to-emerald-500/5 border border-emerald-500/20 shadow-lg cursor-pointer hover:shadow-xl hover:border-emerald-500/30 transition-all duration-200"
          >
            <div className="absolute top-3 right-3 flex items-center gap-2">
              <Badge variant="outline" className="bg-emerald-500/10 border-emerald-500/30 text-emerald-700">
                <TrendingUp className="h-3 w-3 mr-1" />
                Top Deal
              </Badge>
              <ExternalLink className="h-4 w-4 text-emerald-600 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>

            <div className="space-y-3">
              <div>
                <div className="text-3xl font-bold text-emerald-600 mb-1 group-hover:text-emerald-700 transition-colors">
                  {topDeal.value}
                </div>
                <p className="text-sm text-foreground leading-relaxed line-clamp-2">
                  {topDeal.context}
                </p>
              </div>

              <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
                {topDealLocation && (
                  <div className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    <span className="font-medium">{topDealLocation}</span>
                  </div>
                )}
                <div className="flex items-center gap-1">
                  <Badge variant="outline" className="text-xs">
                    {topDeal.newsletter.category}
                  </Badge>
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
              {recentDeals.map((deal, index) => {
                const location = getLocationFromNewsletter(deal.newsletter)
                return (
                  <div
                    key={index}
                    onClick={() => handleDealClick(deal.newsletter)}
                    className={cn(
                      "group p-3 rounded-lg bg-background/50 border border-transparent cursor-pointer",
                      "hover:border-emerald-500/20 hover:bg-emerald-500/5 hover:shadow-sm",
                      "transition-all duration-200"
                    )}
                  >
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div className="flex items-center gap-2 flex-1">
                        <span className="text-base font-bold text-emerald-600 group-hover:text-emerald-700 transition-colors">
                          {deal.value}
                        </span>
                        {location && (
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <MapPin className="h-3 w-3" />
                            <span>{location}</span>
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className="text-xs text-muted-foreground">
                          {getDaysAgo(deal.newsletter.received_date)}
                        </span>
                        <ExternalLink className="h-3.5 w-3.5 text-emerald-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {deal.context}
                    </p>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </CardContent>
    </Card>

    <NewsletterModal
      newsletter={selectedNewsletter}
      open={modalOpen}
      onOpenChange={setModalOpen}
    />
    </>
  )
}
