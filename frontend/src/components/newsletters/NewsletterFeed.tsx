import { useState, useEffect, useCallback } from 'react'
import { NewsletterCard } from './NewsletterCard'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent } from '@/components/ui/card'
import { Search, AlertCircle, RefreshCw, Inbox } from 'lucide-react'
import { newsletterService } from '@/services/newsletterService'
import type { Newsletter } from '@/types/newsletter'
import { toast } from 'sonner'

interface NewsletterFeedProps {
  initialLimit?: number
  showFilters?: boolean
}

export function NewsletterFeed({
  initialLimit = 20,
  showFilters = true
}: NewsletterFeedProps) {
  const [newsletters, setNewsletters] = useState<Newsletter[]>([])
  const [categories, setCategories] = useState<string[]>(['all'])
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [debouncedSearch, setDebouncedSearch] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [loadMoreCount, setLoadMoreCount] = useState<number>(0)

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery)
    }, 300)

    return () => clearTimeout(timer)
  }, [searchQuery])

  // Fetch categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const cats = await newsletterService.getCategories()
        setCategories(['all', ...cats])
      } catch (err) {
        console.error('Error fetching categories:', err)
        // Don't show error toast for categories, just use default
      }
    }

    fetchCategories()
  }, [])

  // Fetch newsletters based on filters
  const fetchNewsletters = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      let results: Newsletter[]

      if (debouncedSearch.trim()) {
        // Search mode
        results = await newsletterService.search(debouncedSearch, {
          category: selectedCategory !== 'all' ? selectedCategory : undefined,
          limit: initialLimit + (loadMoreCount * 10)
        })
      } else {
        // Browse mode
        results = await newsletterService.getRecent(
          initialLimit + (loadMoreCount * 10),
          selectedCategory !== 'all' ? selectedCategory : undefined
        )
      }

      setNewsletters(results)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch newsletters'
      setError(errorMessage)
      toast.error('Error', {
        description: errorMessage
      })
    } finally {
      setIsLoading(false)
    }
  }, [debouncedSearch, selectedCategory, initialLimit, loadMoreCount])

  // Fetch on filter change
  useEffect(() => {
    fetchNewsletters()
  }, [fetchNewsletters])

  // Reset load more count when filters change
  useEffect(() => {
    setLoadMoreCount(0)
  }, [debouncedSearch, selectedCategory])

  const handleLoadMore = () => {
    setLoadMoreCount(prev => prev + 1)
  }

  const handleRefresh = () => {
    setLoadMoreCount(0)
    fetchNewsletters()
  }

  // Check if there might be more newsletters to load
  const hasMore = newsletters.length >= (initialLimit + (loadMoreCount * 10))

  return (
    <div className="space-y-6">
      {/* Filters */}
      {showFilters && (
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search newsletters..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Category Filter */}
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-full sm:w-[200px]">
              <SelectValue placeholder="All Categories" />
            </SelectTrigger>
            <SelectContent>
              {categories.map((category) => (
                <SelectItem key={category} value={category}>
                  {category === 'all' ? 'All Categories' : category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Refresh Button */}
          <Button
            variant="outline"
            size="icon"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      )}

      {/* Results Info */}
      {!isLoading && newsletters.length > 0 && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            Showing {newsletters.length} newsletter{newsletters.length !== 1 ? 's' : ''}
            {debouncedSearch && (
              <> for &quot;{debouncedSearch}&quot;</>
            )}
            {selectedCategory !== 'all' && (
              <> in {selectedCategory}</>
            )}
          </span>
        </div>
      )}

      {/* Loading State */}
      {isLoading && newsletters.length === 0 && (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="space-y-4">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-6 w-full" />
                  <div className="space-y-2">
                    <Skeleton className="h-16 w-full" />
                    <Skeleton className="h-16 w-full" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center space-y-4 py-8">
              <AlertCircle className="h-12 w-12 text-destructive" />
              <div className="text-center space-y-2">
                <p className="text-destructive font-medium">Failed to load newsletters</p>
                <p className="text-sm text-muted-foreground">{error}</p>
              </div>
              <Button onClick={handleRefresh} variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {!isLoading && !error && newsletters.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center space-y-6 py-12 max-w-2xl mx-auto">
              <Inbox className="h-16 w-16 text-muted-foreground/50" />
              <div className="text-center space-y-2">
                <p className="text-lg font-medium">No newsletters found</p>
                <p className="text-sm text-muted-foreground">
                  {debouncedSearch
                    ? 'Try adjusting your search query or filters'
                    : 'Connect your Gmail to import Bisnow real estate newsletters. More sources coming soon!'
                  }
                </p>
              </div>
              {(debouncedSearch || selectedCategory !== 'all') ? (
                <Button
                  onClick={() => {
                    setSearchQuery('')
                    setSelectedCategory('all')
                  }}
                  variant="outline"
                  size="sm"
                >
                  Clear Filters
                </Button>
              ) : (
                <div className="w-full space-y-6">
                  <div className="bg-muted/50 rounded-lg p-6 space-y-4 text-left">
                    <h3 className="font-semibold text-sm">📧 Setup Instructions</h3>
                    <ol className="list-decimal list-inside space-y-3 text-sm text-muted-foreground">
                      <li className="leading-relaxed">
                        <span className="font-medium text-foreground">Create Gmail App Password</span>
                        <ul className="list-disc list-inside ml-6 mt-1 space-y-1">
                          <li>Go to <a href="https://myaccount.google.com/apppasswords" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Google App Passwords</a></li>
                          <li>Select "Mail" and "Other (Custom name)"</li>
                          <li>Copy the 16-character password</li>
                        </ul>
                      </li>
                      <li className="leading-relaxed">
                        <span className="font-medium text-foreground">Configure Email Settings</span>
                        <ul className="list-disc list-inside ml-6 mt-1 space-y-1">
                          <li>Go to Settings → Email Configuration (coming soon)</li>
                          <li>Enter your Gmail address and app password</li>
                          <li>Save configuration</li>
                        </ul>
                      </li>
                      <li className="leading-relaxed">
                        <span className="font-medium text-foreground">Import Newsletters</span>
                        <ul className="list-disc list-inside ml-6 mt-1">
                          <li>Click "Fetch Newsletters" to import from your inbox</li>
                        </ul>
                      </li>
                    </ol>
                    <div className="pt-2 text-xs text-muted-foreground border-t space-y-1">
                      <p>📰 <strong>Note:</strong> You must be subscribed to Bisnow newsletters at your Gmail address. <a href="https://www.bisnow.com" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Subscribe at Bisnow.com</a></p>
                      <p>✨ <strong>Currently supported:</strong> Bisnow (Houston, Austin, National Deal Brief, and more)</p>
                      <p>🚀 <strong>Coming soon:</strong> CoStar, Commercial Observer, and custom RSS feeds</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Newsletter List */}
      {newsletters.length > 0 && (
        <div className="space-y-4">
          {newsletters.map((newsletter, index) => (
            <div
              key={newsletter.id}
              className="animate-slide-up"
              style={{ animationDelay: `${index * 30}ms` }}
            >
              <NewsletterCard newsletter={newsletter} />
            </div>
          ))}
        </div>
      )}

      {/* Load More */}
      {!isLoading && hasMore && newsletters.length > 0 && (
        <div className="flex justify-center pt-4">
          <Button
            onClick={handleLoadMore}
            variant="outline"
            disabled={isLoading}
          >
            Load More Newsletters
          </Button>
        </div>
      )}

      {/* Loading More Indicator */}
      {isLoading && newsletters.length > 0 && (
        <div className="flex justify-center py-4">
          <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      )}
    </div>
  )
}
