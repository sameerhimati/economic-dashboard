import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Calendar, Tag } from 'lucide-react'
import type { Newsletter } from '@/types/newsletter'

interface NewsletterCardProps {
  newsletter: Newsletter
  defaultExpanded?: boolean
}

export function NewsletterCard({ newsletter, defaultExpanded = false }: NewsletterCardProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    }).format(date)
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 space-y-2">
            <CardTitle className="text-lg leading-tight">{newsletter.subject}</CardTitle>
            <CardDescription className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {formatDate(newsletter.received_date)}
              </span>
              <span className="flex items-center gap-1">
                <Tag className="h-3 w-3" />
                {newsletter.category}
              </span>
            </CardDescription>
          </div>
          <Badge variant="secondary" className="shrink-0">
            {newsletter.source}
          </Badge>
        </div>
      </CardHeader>

      {defaultExpanded && newsletter.key_points && (
        <CardContent className="space-y-4">
          {/* Headlines */}
          {newsletter.key_points.headlines?.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold mb-2">Headlines</h4>
              <ul className="space-y-1">
                {newsletter.key_points.headlines.map((headline, idx) => (
                  <li key={idx} className="text-sm text-muted-foreground">
                    • {headline}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Articles */}
          {newsletter.key_points.articles?.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold mb-2">Articles</h4>
              <ul className="space-y-1">
                {newsletter.key_points.articles.map((article, idx) => (
                  <li key={idx} className="text-sm">
                    {article.url ? (
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                      >
                        {article.headline}
                      </a>
                    ) : (
                      <span className="text-muted-foreground">{article.headline}</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      )}
    </Card>
  )
}
