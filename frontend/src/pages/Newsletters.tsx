import { Layout } from '@/components/layout/Layout'
import { PageTransition } from '@/components/ui/page-transition'
import { NewsletterFeed, NewsletterStats } from '@/components/newsletters'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Building2, BarChart3, Inbox } from 'lucide-react'

export function Newsletters() {
  return (
    <Layout>
      <PageTransition>
        <div className="space-y-8">
          {/* Header */}
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Building2 className="h-8 w-8 text-primary" />
              <h1 className="text-4xl font-bold tracking-tight">Real Estate Newsletters</h1>
            </div>
            <p className="text-muted-foreground">
              Stay updated with the latest Bisnow real estate news, deals, and market insights
            </p>
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
              <NewsletterFeed initialLimit={20} showFilters={true} />
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
