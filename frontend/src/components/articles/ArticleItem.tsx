import { ExternalLink, Newspaper } from 'lucide-react'
import { BookmarkButton } from '@/components/bookmarks/BookmarkButton'
import type { Article } from '@/types/article'
import { cn } from '@/lib/utils'
import { formatDistanceToNow } from 'date-fns'
import { Badge } from '@/components/ui/badge'

interface ArticleItemProps {
  article: Article
  showBookmark?: boolean
  showCategory?: boolean
}

export function ArticleItem({ article, showBookmark = true, showCategory = false }: ArticleItemProps) {
  const { id, headline, url, received_date, category, source_count, newsletter_subjects } = article

  // Format the received date
  const receivedDate = new Date(received_date)
  const timeAgo = formatDistanceToNow(receivedDate, { addSuffix: true })

  // Extract domain from URL for favicon
  const getFaviconUrl = (url: string | null) => {
    if (!url) return null
    try {
      const domain = new URL(url).hostname
      return `https://www.google.com/s2/favicons?domain=${domain}&sz=32`
    } catch {
      return null
    }
  }

  const faviconUrl = getFaviconUrl(url)

  // Get category color based on category name
  const getCategoryColor = (cat: string) => {
    const colors: Record<string, string> = {
      'Houston Morning Brief': 'bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20',
      'Chicago Morning Brief': 'bg-purple-500/10 text-purple-700 dark:text-purple-400 border-purple-500/20',
      'National Deal Brief': 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20',
      'Texas Tea': 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20',
      'Events/Awards': 'bg-pink-500/10 text-pink-700 dark:text-pink-400 border-pink-500/20',
    }
    return colors[cat] || 'bg-gray-500/10 text-gray-700 dark:text-gray-400 border-gray-500/20'
  }

  return (
    <div className="group flex items-start gap-4 py-3 px-4 rounded-lg transition-all hover:bg-accent/50 border border-transparent hover:border-border">
      {/* Favicon */}
      {faviconUrl && (
        <div className="shrink-0 mt-0.5">
          <img
            src={faviconUrl}
            alt=""
            className="h-4 w-4 rounded opacity-60 group-hover:opacity-100 transition-opacity"
            onError={(e) => {
              e.currentTarget.style.display = 'none'
            }}
          />
        </div>
      )}

      <div className="flex-1 min-w-0 space-y-2">
        {url ? (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="block group/link"
          >
            <div className="flex items-start gap-2">
              <span className={cn(
                "text-sm font-medium leading-relaxed transition-colors",
                "text-foreground group-hover/link:text-primary",
                "line-clamp-2 flex-1"
              )}>
                {headline}
              </span>
              <ExternalLink className="h-3.5 w-3.5 shrink-0 text-muted-foreground group-hover/link:text-primary transition-colors opacity-0 group-hover:opacity-100 mt-0.5" />
            </div>
          </a>
        ) : (
          <div>
            <span className="text-sm font-medium leading-relaxed text-foreground line-clamp-2 block">
              {headline}
            </span>
          </div>
        )}

        {/* Metadata row */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-muted-foreground">
            {timeAgo}
          </span>

          {/* Category badge (only show if showCategory is true) */}
          {showCategory && (
            <>
              <span className="text-xs text-muted-foreground">•</span>
              <Badge variant="outline" className={cn("text-xs py-0 h-5", getCategoryColor(category))}>
                {category}
              </Badge>
            </>
          )}

          {/* Source indicator */}
          {source_count > 1 && (
            <>
              <span className="text-xs text-muted-foreground">•</span>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Newspaper className="h-3 w-3" />
                <span>{source_count} newsletters</span>
              </div>
            </>
          )}
        </div>

        {/* Newsletter sources (expandable on hover) */}
        {newsletter_subjects && newsletter_subjects.length > 0 && (
          <div className="text-xs text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity">
            <span className="font-medium">Sources:</span> {newsletter_subjects.join(', ')}
          </div>
        )}
      </div>

      {showBookmark && (
        <div className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
          <BookmarkButton articleId={id} size="sm" />
        </div>
      )}
    </div>
  )
}
