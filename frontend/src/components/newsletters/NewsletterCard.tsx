import { useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ChevronDown, ChevronUp, MapPin, Building2, ExternalLink } from 'lucide-react'
import { cn } from '@/lib/utils'
import { getCategoryColor, getMetricIcon, formatMetricType, getRelativeTime } from '@/lib/newsletter-utils'
import { NewsletterModal } from './NewsletterModal'
import { BookmarkButton } from '@/components/bookmarks/BookmarkButton'
import type { Newsletter } from '@/types/newsletter'

interface NewsletterCardProps {
  newsletter: Newsletter
  defaultExpanded?: boolean
  onOpenModal?: (newsletter: Newsletter) => void
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
          <div className="flex items-center gap-1 flex-shrink-0">
            <BookmarkButton
              newsletterId={newsletter.id}
              variant="ghost"
              size="sm"
            />
            {hasContent && (
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0"
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

        {/* Articles */}
        {newsletter.key_points.articles && newsletter.key_points.articles.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Top Stories
            </h4>
            <ul className="space-y-2">
              {newsletter.key_points.articles.slice(0, isExpanded ? undefined : 5).map((article, index) => (
                <li key={index} className="group">
                  {article.url ? (
                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-start gap-2 text-sm hover:text-primary transition-colors p-2 -m-2 rounded-md hover:bg-muted/50"
                    >
                      <span className="text-primary font-bold mt-0.5 flex-shrink-0">•</span>
                      <span className="flex-1 line-clamp-2">{article.headline}</span>
                      <ExternalLink className="h-3.5 w-3.5 mt-0.5 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground" />
                    </a>
                  ) : (
                    <div className="flex items-start gap-2 text-sm p-2 -m-2">
                      <span className="text-primary font-bold mt-0.5 flex-shrink-0">•</span>
                      <span className="flex-1 line-clamp-2 text-muted-foreground">{article.headline}</span>
                    </div>
                  )}
                </li>
              ))}
            </ul>
            {!isExpanded && newsletter.key_points.articles.length > 5 && (
              <button
                onClick={() => setIsExpanded(true)}
                className="text-xs text-primary hover:underline font-medium"
              >
                +{newsletter.key_points.articles.length - 5} more stories
              </button>
            )}
          </div>
        )}

        {/* Fallback to headlines if no articles */}
        {(!newsletter.key_points.articles || newsletter.key_points.articles.length === 0) &&
         newsletter.key_points.headlines.length > 0 && (
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
