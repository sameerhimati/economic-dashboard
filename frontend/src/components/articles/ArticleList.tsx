import { ArticleItem } from './ArticleItem'
import type { Article } from '@/types/article'

interface ArticleListProps {
  articles: Article[]
  showBookmark?: boolean
  emptyMessage?: string
}

export function ArticleList({
  articles,
  showBookmark = true,
  emptyMessage = 'No articles available'
}: ArticleListProps) {
  if (articles.length === 0) {
    return (
      <div className="py-8 text-center">
        <p className="text-sm text-muted-foreground">{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div className="space-y-1">
      {articles.map((article, index) => (
        <div
          key={article.id}
          className="animate-slide-up"
          style={{ animationDelay: `${index * 30}ms` }}
        >
          <ArticleItem article={article} showBookmark={showBookmark} />
        </div>
      ))}
    </div>
  )
}
