import { ExternalLink } from 'lucide-react'
import { BookmarkButton } from '@/components/bookmarks/BookmarkButton'
import type { Article } from '@/types/article'
import { cn } from '@/lib/utils'

interface ArticleItemProps {
  article: Article
  showBookmark?: boolean
}

export function ArticleItem({ article, showBookmark = true }: ArticleItemProps) {
  const { id, headline, url } = article

  return (
    <div className="group flex items-center justify-between gap-4 py-3 px-4 rounded-lg transition-all hover:bg-accent/50 border border-transparent hover:border-border">
      <div className="flex-1 min-w-0">
        {url ? (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 group/link"
          >
            <span className={cn(
              "text-sm font-medium leading-relaxed transition-colors",
              "text-foreground group-hover/link:text-primary",
              "line-clamp-2"
            )}>
              {headline}
            </span>
            <ExternalLink className="h-3.5 w-3.5 shrink-0 text-muted-foreground group-hover/link:text-primary transition-colors opacity-0 group-hover:opacity-100" />
          </a>
        ) : (
          <span className="text-sm font-medium leading-relaxed text-foreground line-clamp-2">
            {headline}
          </span>
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
