import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Bookmark,
  TrendingUp,
  DollarSign,
  Building,
  BadgeDollarSign,
  Percent,
  MapPin,
  Building2,
  Check,
  Copy
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { isBookmarked, toggleBookmark } from '@/lib/bookmarks'
import { toast } from 'sonner'
import type { Newsletter, MetricType } from '@/types/newsletter'

interface NewsletterModalProps {
  newsletter: Newsletter | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

// Map categories to badge colors (same as NewsletterCard)
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

export function NewsletterModal({ newsletter, open, onOpenChange }: NewsletterModalProps) {
  const [bookmarked, setBookmarked] = useState(false)
  const [copied, setCopied] = useState(false)

  // Update bookmark state when newsletter changes
  useEffect(() => {
    if (newsletter) {
      setBookmarked(isBookmarked(newsletter.id))
    }
  }, [newsletter])

  // Reset copied state when modal closes
  useEffect(() => {
    if (!open) {
      setCopied(false)
    }
  }, [open])

  // Keyboard shortcuts
  useEffect(() => {
    if (!open || !newsletter) return

    const handleKeyDown = (e: KeyboardEvent) => {
      // ESC already handled by Dialog component
      // B for bookmark
      if (e.key === 'b' || e.key === 'B') {
        e.preventDefault()
        handleBookmarkToggle()
      }
      // S for share
      if (e.key === 's' || e.key === 'S') {
        e.preventDefault()
        handleShare()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, newsletter])

  if (!newsletter) return null

  const categoryColor = getCategoryColor(newsletter.category)

  const handleBookmarkToggle = () => {
    try {
      const newState = toggleBookmark(newsletter.id)
      setBookmarked(newState)

      toast.success(
        newState ? 'Newsletter bookmarked' : 'Bookmark removed',
        {
          description: newState
            ? 'You can find this newsletter in your bookmarks'
            : 'Newsletter removed from bookmarks'
        }
      )
    } catch (error) {
      toast.error('Error', {
        description: 'Failed to update bookmark'
      })
    }
  }

  const handleShare = async () => {
    try {
      // Create a shareable URL (could be updated with actual URL structure)
      const shareUrl = `${window.location.origin}/newsletters?id=${newsletter.id}`

      await navigator.clipboard.writeText(shareUrl)
      setCopied(true)

      toast.success('Link copied', {
        description: 'Newsletter link copied to clipboard'
      })

      // Reset copied state after 2 seconds
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      toast.error('Error', {
        description: 'Failed to copy link to clipboard'
      })
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] p-0 gap-0">
        {/* Header */}
        <DialogHeader className="px-6 pt-6 pb-4 border-b space-y-3">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 space-y-3">
              <div className="flex items-center gap-2 flex-wrap">
                <Badge variant={categoryColor}>
                  {newsletter.category}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {new Date(newsletter.received_date).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </div>
              <DialogTitle className="text-2xl leading-tight pr-8">
                {newsletter.subject}
              </DialogTitle>
              <DialogDescription className="text-sm">
                <span className="font-medium">Source:</span> {newsletter.source}
              </DialogDescription>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 pt-2">
            <Button
              variant={bookmarked ? "default" : "outline"}
              size="sm"
              onClick={handleBookmarkToggle}
              className={cn(
                "gap-2 transition-all",
                bookmarked && "bg-primary hover:bg-primary/90"
              )}
            >
              <Bookmark className={cn("h-4 w-4", bookmarked && "fill-current")} />
              {bookmarked ? 'Bookmarked' : 'Bookmark'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleShare}
              className="gap-2"
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4" />
                  Share
                </>
              )}
            </Button>
          </div>
        </DialogHeader>

        {/* Content */}
        <div className="overflow-y-auto px-6 py-6 max-h-[calc(90vh-200px)]">
          <div className="space-y-6 pb-6">
            {/* Key Metrics */}
            {newsletter.key_points.metrics.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  Key Metrics
                </h3>
                <div className="grid gap-3 sm:grid-cols-2">
                  {newsletter.key_points.metrics.map((metric, index) => {
                    const Icon = getMetricIcon(metric.type)
                    return (
                      <div
                        key={index}
                        className="flex items-start gap-3 p-4 rounded-lg bg-muted/50 hover:bg-muted transition-colors border border-border/50"
                      >
                        <Icon className="h-5 w-5 mt-0.5 text-primary flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-baseline gap-2 flex-wrap mb-1">
                            <span className="text-xs font-medium text-muted-foreground">
                              {formatMetricType(metric.type)}
                            </span>
                            <span className="text-lg font-bold">
                              {metric.value}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground">
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
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                  Headlines
                </h3>
                <ul className="space-y-2.5">
                  {newsletter.key_points.headlines.map((headline, index) => (
                    <li key={index} className="flex items-start gap-3 text-base">
                      <span className="text-primary font-bold mt-1 flex-shrink-0">•</span>
                      <span className="flex-1 leading-relaxed">{headline}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Locations */}
            {newsletter.key_points.locations.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Locations
                </h3>
                <div className="flex flex-wrap gap-2">
                  {newsletter.key_points.locations.map((location, index) => (
                    <Badge key={index} variant="outline" className="text-sm py-1 px-3">
                      {location}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Companies */}
            {newsletter.key_points.companies.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  Companies
                </h3>
                <div className="flex flex-wrap gap-2">
                  {newsletter.key_points.companies.map((company, index) => (
                    <Badge key={index} variant="outline" className="text-sm py-1 px-3">
                      {company}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Full Content */}
            {(newsletter.content_html || newsletter.content_text) && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                  Full Content
                </h3>
                <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
                  {newsletter.content_html ? (
                    <div
                      className="prose prose-sm dark:prose-invert max-w-none prose-headings:text-foreground prose-p:text-foreground prose-li:text-foreground prose-strong:text-foreground prose-a:text-primary hover:prose-a:text-primary/80"
                      dangerouslySetInnerHTML={{ __html: newsletter.content_html }}
                    />
                  ) : (
                    <p className="text-sm whitespace-pre-wrap break-words leading-relaxed">
                      {newsletter.content_text}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Keyboard Shortcuts Hint */}
            <div className="pt-4 border-t">
              <p className="text-xs text-muted-foreground text-center">
                Keyboard shortcuts: <kbd className="px-1.5 py-0.5 rounded bg-muted text-xs">B</kbd> Bookmark • <kbd className="px-1.5 py-0.5 rounded bg-muted text-xs">S</kbd> Share • <kbd className="px-1.5 py-0.5 rounded bg-muted text-xs">ESC</kbd> Close
              </p>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
