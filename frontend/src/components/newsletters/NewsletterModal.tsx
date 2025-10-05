import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Bookmark,
  TrendingUp,
  MapPin,
  Building2,
  Check,
  Copy,
  ExternalLink,
  FileText,
  Newspaper
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { getCategoryColor, getMetricIcon, formatMetricType } from '@/lib/newsletter-utils'
import { isBookmarked, toggleBookmark } from '@/lib/bookmarks'
import { toast } from 'sonner'
import type { Newsletter } from '@/types/newsletter'

interface NewsletterModalProps {
  newsletter: Newsletter | null
  open: boolean
  onOpenChange: (open: boolean) => void
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

        {/* Content with Tabs */}
        <div className="overflow-y-auto px-6 py-4 max-h-[calc(90vh-200px)]">
          <Tabs defaultValue="articles" className="w-full">
            <TabsList className="grid w-full grid-cols-4 mb-4">
              <TabsTrigger value="articles" className="gap-1.5">
                <Newspaper className="h-4 w-4" />
                <span className="hidden sm:inline">Articles</span>
                {newsletter.key_points.articles && newsletter.key_points.articles.length > 0 && (
                  <Badge variant="secondary" className="ml-1 h-5 min-w-5 px-1.5">
                    {newsletter.key_points.articles.length}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="metrics" className="gap-1.5">
                <TrendingUp className="h-4 w-4" />
                <span className="hidden sm:inline">Metrics</span>
                {newsletter.key_points.metrics.length > 0 && (
                  <Badge variant="secondary" className="ml-1 h-5 min-w-5 px-1.5">
                    {newsletter.key_points.metrics.length}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="details" className="gap-1.5">
                <Building2 className="h-4 w-4" />
                <span className="hidden sm:inline">Details</span>
              </TabsTrigger>
              <TabsTrigger value="content" className="gap-1.5">
                <FileText className="h-4 w-4" />
                <span className="hidden sm:inline">Full Text</span>
              </TabsTrigger>
            </TabsList>

            {/* Articles Tab */}
            <TabsContent value="articles" className="space-y-4 mt-0">
              {newsletter.key_points.articles && newsletter.key_points.articles.length > 0 ? (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Newspaper className="h-5 w-5 text-primary" />
                      Featured Articles
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3">
                      {newsletter.key_points.articles.map((article, index) => (
                        <li key={index} className="group border-b border-border/50 last:border-0 pb-3 last:pb-0">
                          {article.url ? (
                            <a
                              href={article.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-start gap-3 p-2 -mx-2 rounded-lg hover:bg-muted/50 transition-all"
                            >
                              <span className="text-primary font-bold text-lg mt-0.5 flex-shrink-0">
                                {index + 1}.
                              </span>
                              <div className="flex-1 min-w-0">
                                <p className="text-base font-medium leading-relaxed group-hover:text-primary transition-colors">
                                  {article.headline}
                                </p>
                                <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                                  <ExternalLink className="h-3 w-3" />
                                  Read on Bisnow
                                </p>
                              </div>
                              <ExternalLink className="h-4 w-4 mt-1 flex-shrink-0 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                            </a>
                          ) : (
                            <div className="flex items-start gap-3 p-2 -mx-2">
                              <span className="text-muted-foreground font-bold text-lg mt-0.5 flex-shrink-0">
                                {index + 1}.
                              </span>
                              <p className="text-base leading-relaxed text-muted-foreground">
                                {article.headline}
                              </p>
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center py-8 text-muted-foreground">
                      <Newspaper className="h-12 w-12 mx-auto mb-3 opacity-50" />
                      <p className="text-sm">No articles extracted from this newsletter</p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Fallback to headlines if no articles */}
              {(!newsletter.key_points.articles || newsletter.key_points.articles.length === 0) &&
               newsletter.key_points.headlines.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Headlines</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2.5">
                      {newsletter.key_points.headlines.map((headline, index) => (
                        <li key={index} className="flex items-start gap-3 text-base">
                          <span className="text-primary font-bold mt-1 flex-shrink-0">•</span>
                          <span className="flex-1 leading-relaxed">{headline}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Metrics Tab */}
            <TabsContent value="metrics" className="space-y-4 mt-0">
              {newsletter.key_points.metrics.length > 0 ? (
                <div className="grid gap-3 sm:grid-cols-2">
                  {newsletter.key_points.metrics.map((metric, index) => {
                    const Icon = getMetricIcon(metric.type)
                    return (
                      <Card key={index} className="hover:shadow-md transition-shadow">
                        <CardContent className="pt-6">
                          <div className="flex items-start gap-3">
                            <div className="p-2 rounded-lg bg-primary/10">
                              <Icon className="h-5 w-5 text-primary" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-xs font-medium text-muted-foreground mb-1">
                                {formatMetricType(metric.type)}
                              </p>
                              <p className="text-xl font-bold mb-2">
                                {metric.value}
                              </p>
                              <p className="text-sm text-muted-foreground leading-relaxed">
                                {metric.context}
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              ) : (
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center py-8 text-muted-foreground">
                      <TrendingUp className="h-12 w-12 mx-auto mb-3 opacity-50" />
                      <p className="text-sm">No metrics extracted from this newsletter</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Details Tab */}
            <TabsContent value="details" className="space-y-4 mt-0">
              {/* Locations */}
              {newsletter.key_points.locations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <MapPin className="h-5 w-5 text-primary" />
                      Locations Mentioned
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {newsletter.key_points.locations.map((location, index) => (
                        <Badge key={index} variant="outline" className="text-sm py-1.5 px-3">
                          <MapPin className="h-3 w-3 mr-1.5" />
                          {location}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Companies */}
              {newsletter.key_points.companies.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Building2 className="h-5 w-5 text-primary" />
                      Companies Mentioned
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {newsletter.key_points.companies.map((company, index) => (
                        <Badge key={index} variant="outline" className="text-sm py-1.5 px-3">
                          <Building2 className="h-3 w-3 mr-1.5" />
                          {company}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Metadata */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Newsletter Metadata</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid gap-3 text-sm">
                    <div className="flex items-start justify-between py-2 border-b border-border/50">
                      <span className="font-medium text-muted-foreground">Source</span>
                      <span className="text-right font-mono text-xs">{newsletter.source}</span>
                    </div>
                    <div className="flex items-start justify-between py-2 border-b border-border/50">
                      <span className="font-medium text-muted-foreground">Category</span>
                      <Badge variant={categoryColor}>{newsletter.category}</Badge>
                    </div>
                    <div className="flex items-start justify-between py-2 border-b border-border/50">
                      <span className="font-medium text-muted-foreground">Received</span>
                      <span className="text-right">
                        {new Date(newsletter.received_date).toLocaleString()}
                      </span>
                    </div>
                    <div className="flex items-start justify-between py-2">
                      <span className="font-medium text-muted-foreground">Parsed</span>
                      <span className="text-right">
                        {new Date(newsletter.parsed_date).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Empty State */}
              {newsletter.key_points.locations.length === 0 &&
               newsletter.key_points.companies.length === 0 && (
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center py-8 text-muted-foreground">
                      <Building2 className="h-12 w-12 mx-auto mb-3 opacity-50" />
                      <p className="text-sm">No locations or companies extracted</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Full Content Tab */}
            <TabsContent value="content" className="mt-0">
              {(newsletter.content_html || newsletter.content_text) ? (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <FileText className="h-5 w-5 text-primary" />
                      Full Newsletter Content
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="max-h-[60vh] overflow-y-auto p-4 rounded-lg bg-muted/30 border border-border/50">
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
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center py-8 text-muted-foreground">
                      <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
                      <p className="text-sm">No content available</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>

          {/* Keyboard Shortcuts Hint */}
          <div className="pt-4 mt-4 border-t">
            <p className="text-xs text-muted-foreground text-center">
              Keyboard shortcuts: <kbd className="px-1.5 py-0.5 rounded bg-muted text-xs">B</kbd> Bookmark • <kbd className="px-1.5 py-0.5 rounded bg-muted text-xs">S</kbd> Share • <kbd className="px-1.5 py-0.5 rounded bg-muted text-xs">ESC</kbd> Close
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
