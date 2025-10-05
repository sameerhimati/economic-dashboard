import { useState, useEffect } from 'react'
import { Layout } from '@/components/layout/Layout'
import { PageTransition } from '@/components/ui/page-transition'
import { BookmarkListManager } from '@/components/bookmarks/BookmarkListManager'
import { NewsletterCard } from '@/components/newsletters/NewsletterCard'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { bookmarkService, type BookmarkList, type NewsletterInBookmark } from '@/services/bookmarkService'
import { toast } from 'sonner'
import { Bookmark, Loader2, FolderOpen, Inbox } from 'lucide-react'

export function Bookmarks() {
  const [selectedListId, setSelectedListId] = useState<string | null>(null)
  const [selectedList, setSelectedList] = useState<BookmarkList | null>(null)
  const [newsletters, setNewsletters] = useState<NewsletterInBookmark[]>([])
  const [loading, setLoading] = useState(false)
  const [listsKey, setListsKey] = useState(0)

  useEffect(() => {
    if (selectedListId) {
      loadNewsletters(selectedListId)
    } else {
      setNewsletters([])
      setSelectedList(null)
    }
  }, [selectedListId])

  const loadNewsletters = async (listId: string) => {
    try {
      setLoading(true)
      const [data, lists] = await Promise.all([
        bookmarkService.getNewslettersInList(listId),
        bookmarkService.getLists()
      ])

      setNewsletters(data)

      // Find and set the selected list details
      const list = lists.find(l => l.id === listId)
      setSelectedList(list || null)
    } catch (error: any) {
      console.error('Failed to load newsletters:', error)
      toast.error(error.message || 'Failed to load newsletters')

      // If list not found, deselect it
      if (error.message?.includes('not found')) {
        setSelectedListId(null)
        // Trigger list refresh to remove deleted list
        setListsKey(prev => prev + 1)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSelectList = (listId: string | null) => {
    setSelectedListId(listId)
  }

  return (
    <Layout>
      <PageTransition>
        <div className="space-y-8">
          {/* Header */}
          <div className="flex items-center gap-3">
            <Bookmark className="h-8 w-8 text-primary" />
            <div>
              <h1 className="text-4xl font-bold tracking-tight">Bookmarks</h1>
              <p className="text-muted-foreground mt-1">
                Your saved newsletters, organized in custom lists
              </p>
            </div>
          </div>

          {/* Main Content Grid */}
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Sidebar - List Manager */}
            <div className="lg:col-span-1">
              <div className="lg:sticky lg:top-8">
                <BookmarkListManager
                  key={listsKey}
                  selectedListId={selectedListId || undefined}
                  onSelectList={handleSelectList}
                />
              </div>
            </div>

            {/* Main Content - Selected List Newsletters */}
            <div className="lg:col-span-2">
              {!selectedListId ? (
                <Card>
                  <CardContent className="flex flex-col items-center justify-center py-16">
                    <FolderOpen className="h-16 w-16 text-muted-foreground/50 mb-4" />
                    <h3 className="text-xl font-semibold mb-2">No list selected</h3>
                    <p className="text-sm text-muted-foreground text-center max-w-md">
                      Select a bookmark list from the sidebar to view your saved newsletters,
                      or create a new list to get started
                    </p>
                  </CardContent>
                </Card>
              ) : loading ? (
                <Card>
                  <CardContent className="flex items-center justify-center py-16">
                    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-6">
                  {/* List Header */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Inbox className="h-5 w-5" />
                        {selectedList?.name || 'Bookmark List'}
                      </CardTitle>
                      <CardDescription>
                        {newsletters.length} {newsletters.length === 1 ? 'newsletter' : 'newsletters'} saved
                        {selectedList?.updated_at && (
                          <> • Last updated {new Date(selectedList.updated_at).toLocaleDateString()}</>
                        )}
                      </CardDescription>
                    </CardHeader>
                  </Card>

                  {/* Newsletters */}
                  {newsletters.length === 0 ? (
                    <Card>
                      <CardContent className="flex flex-col items-center justify-center py-12">
                        <Inbox className="h-12 w-12 text-muted-foreground/50 mb-3" />
                        <h3 className="font-semibold mb-1">No newsletters saved yet</h3>
                        <p className="text-sm text-muted-foreground text-center max-w-md">
                          Click the bookmark button on any newsletter to add it to this list
                        </p>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="space-y-4">
                      {newsletters.map((newsletter, index) => (
                        <div
                          key={newsletter.id}
                          className="animate-slide-up"
                          style={{ animationDelay: `${index * 50}ms` }}
                        >
                          <NewsletterCard
                            newsletter={newsletter}
                            defaultExpanded={false}
                          />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </PageTransition>
    </Layout>
  )
}
