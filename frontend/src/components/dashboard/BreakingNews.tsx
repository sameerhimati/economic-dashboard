import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { formatDateTime } from '@/lib/utils'
import { AlertCircle, ExternalLink } from 'lucide-react'
import type { BreakingNews as BreakingNewsType } from '@/types'
import { cn } from '@/lib/utils'

interface BreakingNewsProps {
  data: BreakingNewsType | null
  isLoading: boolean
}

export function BreakingNews({ data, isLoading }: BreakingNewsProps) {
  if (isLoading) {
    return (
      <div className="space-y-4" id="breaking">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (!data || !data.items || data.items.length === 0) {
    return (
      <Card id="breaking">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            Breaking News
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center">No breaking news at this time</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4" id="breaking">
      <div>
        <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <AlertCircle className="h-7 w-7 text-red-500" />
          Breaking News
        </h2>
        <p className="text-muted-foreground">
          Last updated: {formatDateTime(data.lastUpdated)}
        </p>
      </div>

      <div className="grid gap-4">
        {data.items.map((item) => (
          <Card
            key={item.id}
            className={cn(
              'transition-all hover:shadow-lg cursor-pointer',
              item.importance === 'high' && 'border-red-500/50 bg-red-500/5'
            )}
            onClick={() => item.url && window.open(item.url, '_blank')}
          >
            <CardContent className="pt-6">
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {item.importance === 'high' && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-red-500/20 text-red-500 rounded">
                          <AlertCircle className="h-3 w-3" />
                          High Priority
                        </span>
                      )}
                      {item.category && (
                        <span className="px-2 py-1 text-xs font-medium bg-primary/10 text-primary rounded">
                          {item.category}
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                      {item.title}
                      {item.url && <ExternalLink className="h-4 w-4 text-muted-foreground" />}
                    </h3>
                    <p className="text-sm text-muted-foreground mb-3">{item.summary}</p>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span className="font-medium">{item.source}</span>
                      <span>•</span>
                      <span>{formatDateTime(item.publishedAt)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
