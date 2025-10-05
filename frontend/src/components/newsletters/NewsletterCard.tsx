import { useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ChevronDown, ChevronUp, TrendingUp, DollarSign, Building, BadgeDollarSign, Percent, MapPin, Building2, ExternalLink } from 'lucide-react'
import { cn } from '@/lib/utils'
import { NewsletterModal } from './NewsletterModal'
import type { Newsletter, MetricType } from '@/types/newsletter'

interface NewsletterCardProps {
  newsletter: Newsletter
  defaultExpanded?: boolean
  onOpenModal?: (newsletter: Newsletter) => void
}

// Map categories to badge colors
const getCategoryColor = (category: string): "blue" | "green" | "purple" | "orange" | "pink" | "yellow" | "indigo" | "gray" => {
  const categoryLower = category.toLowerCase()

  if (categoryLower.includes('houston')) return 'blue'
  if (categoryLower.includes('austin') || categoryLower.includes('san antonio')) return 'green'
  if (categoryLower.includes('national')) return 'purple'
  if (categoryLower.includes('capital markets')) return 'orange'
  if (categoryLower.includes('multifamily')) return 'pink'
  if (categoryLower.includes('retail')) return 'yellow'
  if (categoryLower.includes('student housing')) return 'indigo'

  return 'gray'
}

// Map metric types to icons
const getMetricIcon = (type: MetricType) => {
  switch (type) {
    case 'cap_rate':
      return TrendingUp
    case 'deal_value':
      return DollarSign
    case 'square_footage':
      return Building
    case 'price_per_sf':
      return BadgeDollarSign
    case 'occupancy_rate':
      return Percent
  }
}

// Format metric type for display
const formatMetricType = (type: MetricType): string => {
  const typeMap: Record<MetricType, string> = {
    cap_rate: 'Cap Rate',
    deal_value: 'Deal Value',
    square_footage: 'Square Footage',
    price_per_sf: 'Price/SF',
    occupancy_rate: 'Occupancy'
  }
  return typeMap[type]
}

// Calculate relative time
const getRelativeTime = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSeconds < 60) return 'just now'
  if (diffMinutes < 60) return `${diffMinutes}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays === 1) return 'yesterday'
  if (diffDays < 7) return `${diffDays}d ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`

  return date.toLocaleDateString()
}

export function NewsletterCard({ newsletter, defaultExpanded = false, onOpenModal }: NewsletterCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const categoryColor = getCategoryColor(newsletter.category)
  const topMetrics = newsletter.key_points.metrics.slice(0, 3)
  const hasContent = newsletter.content_text || newsletter.content_html

  const handleOpenModal = () => {
    if (onOpenModal) {
      onOpenModal(newsletter)
    } else {
      setIsModalOpen(true)
    }
  }

  return (
    <>
      <Card className={cn(
        "transition-all duration-200 hover:shadow-md",
        isExpanded && "ring-2 ring-primary/20"
      )}>
        <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant={categoryColor}>
                {newsletter.category}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {getRelativeTime(newsletter.received_date)}
              </span>
            </div>
            <h3 className="font-semibold text-base leading-snug line-clamp-2">
              {newsletter.subject}
            </h3>
          </div>
          {hasContent && (
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 flex-shrink-0"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Top Metrics */}
        {topMetrics.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Key Metrics
            </h4>
            <div className="space-y-2">
              {topMetrics.map((metric, index) => {
                const Icon = getMetricIcon(metric.type)
                return (
                  <div
                    key={index}
                    className="flex items-start gap-2 p-2 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                  >
                    <Icon className="h-4 w-4 mt-0.5 text-primary flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-baseline gap-2 flex-wrap">
                        <span className="text-xs font-medium text-muted-foreground">
                          {formatMetricType(metric.type)}:
                        </span>
                        <span className="text-sm font-semibold">
                          {metric.value}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                        {metric.context}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Headlines */}
        {newsletter.key_points.headlines.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Headlines
            </h4>
            <ul className="space-y-1.5">
              {newsletter.key_points.headlines.slice(0, isExpanded ? undefined : 3).map((headline, index) => (
                <li key={index} className="flex items-start gap-2 text-sm">
                  <span className="text-primary font-bold mt-0.5 flex-shrink-0">•</span>
                  <span className="flex-1">{headline}</span>
                </li>
              ))}
            </ul>
            {!isExpanded && newsletter.key_points.headlines.length > 3 && (
              <button
                onClick={() => setIsExpanded(true)}
                className="text-xs text-primary hover:underline"
              >
                +{newsletter.key_points.headlines.length - 3} more headlines
              </button>
            )}
          </div>
        )}

        {/* Expanded Content */}
        {isExpanded && (
          <div className="space-y-4 animate-slide-down">
            {/* Locations */}
            {newsletter.key_points.locations.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
                  <MapPin className="h-3.5 w-3.5" />
                  Locations
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {newsletter.key_points.locations.map((location, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {location}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Companies */}
            {newsletter.key_points.companies.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
                  <Building2 className="h-3.5 w-3.5" />
                  Companies
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {newsletter.key_points.companies.map((company, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {company}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Full Content Preview */}
            {newsletter.content_text && (
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Content Preview
                </h4>
                <div className="p-3 rounded-lg bg-muted/30 max-h-48 overflow-y-auto">
                  <p className="text-sm whitespace-pre-wrap break-words line-clamp-6">
                    {newsletter.content_text}
                  </p>
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="pt-2 border-t text-xs text-muted-foreground space-y-1">
              <div>
                <span className="font-medium">Source:</span> {newsletter.source}
              </div>
              <div>
                <span className="font-medium">Received:</span>{' '}
                {new Date(newsletter.received_date).toLocaleString()}
              </div>
            </div>
          </div>
        )}

        {/* View Full Content Button */}
        {hasContent && (
          <div className="pt-4 border-t mt-4">
            <Button
              variant="outline"
              size="sm"
              onClick={handleOpenModal}
              className="w-full gap-2"
            >
              <ExternalLink className="h-4 w-4" />
              View Full Newsletter
            </Button>
          </div>
        )}
      </CardContent>
    </Card>

    {/* Modal */}
    <NewsletterModal
      newsletter={newsletter}
      open={isModalOpen}
      onOpenChange={setIsModalOpen}
    />
    </>
  )
}
