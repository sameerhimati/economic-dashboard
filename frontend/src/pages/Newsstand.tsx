import { useState, useEffect } from 'react'
import { Layout } from '@/components/layout/Layout'
import { PageTransition } from '@/components/ui/page-transition'
import { ArticleList } from '@/components/articles'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent } from '@/components/ui/card'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { BookOpen, Download, Loader2, Newspaper, FolderOpen, RefreshCw } from 'lucide-react'
import { articleService } from '@/services/articleService'
import { newsletterService } from '@/services/newsletterService'
import { toast } from 'sonner'
import type { ArticlesByCategory } from '@/types/article'
import { apiClient } from '@/services/api'

export function Newsstand() {
  const [categories, setCategories] = useState<ArticlesByCategory[]>([])
  const [newsletterCount, setNewsletterCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [fetching, setFetching] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    loadArticles()
  }, [refreshKey])

  const loadArticles = async () => {
    try {
      setLoading(true)
      const response = await articleService.getRecent(100, true)

      // Check if response has categories (grouped) or is just array
      if ('categories' in response && Array.isArray(response.categories)) {
        setCategories(response.categories)
        setNewsletterCount(response.newsletter_count || 0)
      } else if (Array.isArray(response)) {
        setCategories(response)
        setNewsletterCount(0)
      } else {
        console.warn('Unexpected API response format:', response)
        setCategories([])
        setNewsletterCount(0)
      }
    } catch (error: any) {
      console.error('Error loading articles:', error)
      setCategories([]) // Set empty array on error
      toast.error('Failed to load articles', {
        description: error.message || 'Please try again later'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleResetDatabase = async () => {
    try {
      setResetting(true)
      const response = await apiClient.post('/admin/reset-newsletters-articles')

      if (response.data.status === 'success') {
        toast.success('Database reset successfully', {
          description: 'All newsletters and articles have been cleared'
        })
        // Trigger a refresh of the articles
        setRefreshKey(prev => prev + 1)
      } else {
        toast.error('Failed to reset database', {
          description: response.data.message
        })
      }
    } catch (error: any) {
      console.error('Error resetting database:', error)
      toast.error('Error', {
        description: 'Failed to reset database'
      })
    } finally {
      setResetting(false)
    }
  }

  const handleFetchNewsletters = async () => {
    try {
      setFetching(true)
      const result = await newsletterService.fetchNewsletters(7)

      if (result.status === 'success') {
        toast.success('Newsletters fetched successfully', {
          description: `Fetched ${result.fetched} emails, stored ${result.stored} new newsletters, skipped ${result.skipped} duplicates`
        })
        // Trigger a refresh of the articles
        setRefreshKey(prev => prev + 1)
      } else {
        toast.error('Failed to fetch newsletters', {
          description: 'Please check your email configuration'
        })
      }
    } catch (error: any) {
      console.error('Error fetching newsletters:', error)
      const errorMessage = error.response?.data?.detail || 'Failed to fetch newsletters'
      toast.error('Error', {
        description: errorMessage
      })
    } finally {
      setFetching(false)
    }
  }

  const totalArticles = categories?.reduce((sum, cat) => sum + cat.article_count, 0) ?? 0

  return (
    <Layout>
      <PageTransition>
        <div className="space-y-8">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <BookOpen className="h-8 w-8 text-primary" />
                <h1 className="text-4xl font-bold tracking-tight">Newsstand</h1>
              </div>
              <p className="text-muted-foreground">
                Your curated real estate article feed • Currently featuring Bisnow, with more sources coming soon
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleResetDatabase}
                disabled={resetting || fetching}
                size="lg"
                variant="outline"
              >
                {resetting ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="mr-2 h-4 w-4" />
                )}
                Reset DB
              </Button>
              <Button onClick={handleFetchNewsletters} disabled={fetching || resetting} size="lg">
                {fetching ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Download className="mr-2 h-4 w-4" />
                )}
                Fetch Newsletters
              </Button>
            </div>
          </div>

          {/* Article Count Summary - Always show when not loading */}
          {!loading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Newspaper className="h-4 w-4" />
              <span>
                {categories.length > 0 ? (
                  <>
                    {totalArticles} {totalArticles === 1 ? 'article' : 'articles'} from {newsletterCount} {newsletterCount === 1 ? 'newsletter' : 'newsletters'} across {categories.length} {categories.length === 1 ? 'category' : 'categories'}
                  </>
                ) : (
                  'No articles loaded yet - click "Fetch Newsletters" to get started'
                )}
              </span>
            </div>
          )}

          {/* Loading State */}
          {loading ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <Card key={i}>
                  <CardContent className="p-6">
                    <Skeleton className="h-6 w-48 mb-4" />
                    <div className="space-y-3">
                      <Skeleton className="h-12 w-full" />
                      <Skeleton className="h-12 w-full" />
                      <Skeleton className="h-12 w-full" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : categories.length === 0 ? (
            /* Empty State */
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16">
                <FolderOpen className="h-16 w-16 text-muted-foreground/50 mb-4" />
                <h3 className="text-xl font-semibold mb-2">No articles yet</h3>
                <p className="text-sm text-muted-foreground text-center max-w-md mb-6">
                  Click "Fetch Newsletters" above to load your latest real estate articles from your email
                </p>
                <Button onClick={handleFetchNewsletters} disabled={fetching}>
                  {fetching ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Download className="mr-2 h-4 w-4" />
                  )}
                  Fetch Newsletters
                </Button>
              </CardContent>
            </Card>
          ) : (
            /* Articles by Category */
            <Accordion type="multiple" className="space-y-4" defaultValue={categories.map(cat => cat.category)}>
              {categories.map((category, index) => (
                <Card key={category.category} className="overflow-hidden animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
                  <AccordionItem value={category.category} className="border-0">
                    <AccordionTrigger className="px-6 hover:no-underline hover:bg-accent/50 transition-colors">
                      <div className="flex items-center justify-between w-full pr-4">
                        <div className="flex items-center gap-3">
                          <Newspaper className="h-5 w-5 text-primary" />
                          <span className="text-lg font-semibold">{category.category}</span>
                        </div>
                        <Badge variant="secondary" className="ml-auto mr-2">
                          {category.article_count} {category.article_count === 1 ? 'article' : 'articles'}
                        </Badge>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-6 pb-2">
                      <ArticleList
                        articles={category.articles}
                        emptyMessage={`No articles in ${category.category}`}
                      />
                    </AccordionContent>
                  </AccordionItem>
                </Card>
              ))}
            </Accordion>
          )}
        </div>
      </PageTransition>
    </Layout>
  )
}
