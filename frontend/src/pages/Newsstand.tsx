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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { BookOpen, Download, Loader2, Newspaper, FolderOpen, RefreshCw, Calendar, ListFilter, Bookmark } from 'lucide-react'
import { articleService } from '@/services/articleService'
import { newsletterService } from '@/services/newsletterService'
import { bookmarkService } from '@/services/bookmarkService'
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
  const [fetchDays, setFetchDays] = useState(7)
  const [articleLimit, setArticleLimit] = useState(500)
  const [showBookmarksOnly, setShowBookmarksOnly] = useState(false)
  const [bookmarkedArticleIds, setBookmarkedArticleIds] = useState<Set<string>>(new Set())

  useEffect(() => {
    loadArticles()
  }, [refreshKey, articleLimit])

  useEffect(() => {
    loadBookmarkedArticles()
  }, [refreshKey])

  const loadBookmarkedArticles = async () => {
    try {
      const lists = await bookmarkService.getLists()
      const articleIds = new Set<string>()

      // Fetch articles from all bookmark lists
      await Promise.all(
        lists.map(async (list) => {
          try {
            const articles = await bookmarkService.getArticlesInList(list.id)
            articles.forEach(article => articleIds.add(article.id))
          } catch (error) {
            console.warn(`Could not fetch articles for list ${list.id}`, error)
          }
        })
      )

      setBookmarkedArticleIds(articleIds)
    } catch (error) {
      console.error('Error loading bookmarked articles:', error)
    }
  }

  const loadArticles = async () => {
    try {
      setLoading(true)
      const response = await articleService.getRecent(articleLimit, true) as any

      // Response is always ArticlesByCategoryResponse when groupByCategory=true
      if (response && 'categories' in response && Array.isArray(response.categories)) {
        setCategories(response.categories)
        setNewsletterCount(response.newsletter_count || 0)
      } else {
        console.warn('Unexpected API response format:', response)
        setCategories([])
        setNewsletterCount(0)
      }
    } catch (error: any) {
      console.error('Error loading articles:', error)
      setCategories([]) // Set empty array on error
      setNewsletterCount(0)
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
      const result = await newsletterService.fetchNewsletters(fetchDays)

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

  // Filter categories based on bookmarks
  const displayedCategories = showBookmarksOnly
    ? categories.map(category => ({
        ...category,
        articles: category.articles.filter(article => bookmarkedArticleIds.has(article.id)),
        article_count: category.articles.filter(article => bookmarkedArticleIds.has(article.id)).length
      })).filter(category => category.article_count > 0)
    : categories

  const totalArticles = displayedCategories?.reduce((sum, cat) => sum + cat.article_count, 0) ?? 0
  const totalBookmarkedArticles = bookmarkedArticleIds.size

  return (
    <Layout>
      <PageTransition>
        <div className="space-y-6 sm:space-y-8">
          {/* Header */}
          <div className="space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 sm:gap-3 mb-2">
                  <BookOpen className="h-6 w-6 sm:h-8 sm:w-8 text-primary shrink-0" />
                  <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight">Newsstand</h1>
                </div>
                <p className="text-sm sm:text-base text-muted-foreground">
                  Your curated real estate article feed
                </p>
              </div>
            </div>

            {/* Controls - Fetch Settings & Actions */}
            <div className="flex flex-col gap-3">
              {/* Fetch Settings */}
              <div className="flex flex-col sm:flex-row gap-2">
                <div className="flex items-center gap-2 flex-1">
                  <Calendar className="h-4 w-4 text-muted-foreground shrink-0" />
                  <span className="text-sm text-muted-foreground shrink-0">Fetch:</span>
                  <Select value={fetchDays.toString()} onValueChange={(v) => setFetchDays(Number(v))}>
                    <SelectTrigger className="w-full sm:w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7">7 days</SelectItem>
                      <SelectItem value="14">14 days</SelectItem>
                      <SelectItem value="30">30 days</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center gap-2 flex-1">
                  <ListFilter className="h-4 w-4 text-muted-foreground shrink-0" />
                  <span className="text-sm text-muted-foreground shrink-0">Show:</span>
                  <Select value={articleLimit.toString()} onValueChange={(v) => setArticleLimit(Number(v))}>
                    <SelectTrigger className="w-full sm:w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="100">100</SelectItem>
                      <SelectItem value="200">200</SelectItem>
                      <SelectItem value="500">500</SelectItem>
                      <SelectItem value="1000">All</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-2">
                <Button
                  onClick={handleResetDatabase}
                  disabled={resetting || fetching}
                  size="default"
                  variant="outline"
                  className="w-full sm:w-auto"
                >
                  {resetting ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <RefreshCw className="mr-2 h-4 w-4" />
                  )}
                  Reset DB
                </Button>
                <Button
                  onClick={handleFetchNewsletters}
                  disabled={fetching || resetting}
                  size="default"
                  className="w-full sm:w-auto"
                >
                  {fetching ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Download className="mr-2 h-4 w-4" />
                  )}
                  Fetch Newsletters ({fetchDays} days)
                </Button>
                <Button
                  onClick={() => setShowBookmarksOnly(!showBookmarksOnly)}
                  size="default"
                  variant={showBookmarksOnly ? "default" : "outline"}
                  className="w-full sm:w-auto"
                >
                  <Bookmark className={`mr-2 h-4 w-4 ${showBookmarksOnly ? 'fill-current' : ''}`} />
                  {showBookmarksOnly ? `Showing ${totalBookmarkedArticles} Bookmarks` : 'Show Bookmarks Only'}
                </Button>
              </div>
            </div>
          </div>

          {/* Article Count Summary - Always show when not loading */}
          {!loading && (
            <div className="flex items-start gap-2 text-xs sm:text-sm text-muted-foreground">
              <Newspaper className="h-4 w-4 shrink-0 mt-0.5" />
              <span className="leading-relaxed">
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
            <Accordion type="multiple" className="space-y-3 sm:space-y-4" defaultValue={displayedCategories.map(cat => cat.category)}>
              {displayedCategories.map((category, index) => (
                <Card key={category.category} className="overflow-hidden animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
                  <AccordionItem value={category.category} className="border-0">
                    <AccordionTrigger className="px-4 sm:px-6 hover:no-underline hover:bg-accent/50 transition-colors">
                      <div className="flex items-center justify-between w-full pr-2 sm:pr-4 gap-2">
                        <div className="flex items-center gap-2 sm:gap-3 min-w-0">
                          <Newspaper className="h-4 w-4 sm:h-5 sm:w-5 text-primary shrink-0" />
                          <span className="text-base sm:text-lg font-semibold truncate">{category.category}</span>
                        </div>
                        <Badge variant="secondary" className="ml-auto mr-1 sm:mr-2 shrink-0 text-xs">
                          {category.article_count}
                        </Badge>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-2 sm:px-6 pb-2">
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
