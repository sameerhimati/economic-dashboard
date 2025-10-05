import { useState } from 'react'
import { Layout } from '@/components/layout/Layout'
import { PageTransition } from '@/components/ui/page-transition'
import { NewsletterFeed, NewsletterStats } from '@/components/newsletters'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { BookOpen, BarChart3, Inbox, Download, Loader2 } from 'lucide-react'
import { newsletterService } from '@/services/newsletterService'
import { toast } from 'sonner'

export function Newsletters() {
  const [fetching, setFetching] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  const handleFetchNewsletters = async () => {
    try {
      setFetching(true)
      const result = await newsletterService.fetchNewsletters(7)

      if (result.status === 'success') {
        toast.success('Newsletters fetched successfully', {
          description: `Fetched ${result.fetched} emails, stored ${result.stored} new newsletters, skipped ${result.skipped} duplicates`
        })
        // Trigger a refresh of the newsletter feed
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
                Your curated real estate newsletter feed • Currently featuring Bisnow, with more sources coming soon
              </p>
            </div>
            <Button onClick={handleFetchNewsletters} disabled={fetching} size="lg">
              {fetching ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Download className="mr-2 h-4 w-4" />
              )}
              Fetch Newsletters
            </Button>
          </div>

          {/* Tabs */}
          <Tabs defaultValue="feed" className="space-y-6">
            <TabsList className="grid w-full max-w-md grid-cols-2">
              <TabsTrigger value="feed" className="gap-2">
                <Inbox className="h-4 w-4" />
                Newsletter Feed
              </TabsTrigger>
              <TabsTrigger value="stats" className="gap-2">
                <BarChart3 className="h-4 w-4" />
                Statistics
              </TabsTrigger>
            </TabsList>

            <TabsContent value="feed" className="space-y-6">
              <NewsletterFeed key={refreshKey} initialLimit={20} showFilters={true} />
            </TabsContent>

            <TabsContent value="stats" className="space-y-6">
              <NewsletterStats />
            </TabsContent>
          </Tabs>
        </div>
      </PageTransition>
    </Layout>
  )
}
