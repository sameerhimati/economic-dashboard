import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Checkbox } from '@/components/ui/checkbox'
import { bookmarkService, type BookmarkList } from '@/services/bookmarkService'
import { toast } from 'sonner'
import { Bookmark, Plus, Loader2, FolderPlus } from 'lucide-react'
import { cn } from '@/lib/utils'

interface BookmarkButtonProps {
  articleId: string
  variant?: 'default' | 'ghost' | 'outline'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  className?: string
  onCreateList?: () => void
}

export function BookmarkButton({
  articleId,
  variant = 'ghost',
  size = 'sm',
  className,
  onCreateList
}: BookmarkButtonProps) {
  const [lists, setLists] = useState<BookmarkList[]>([])
  const [bookmarkedListIds, setBookmarkedListIds] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(false)
  const [updatingListId, setUpdatingListId] = useState<string | null>(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (open) {
      loadLists()
    }
  }, [open])

  const loadLists = async () => {
    try {
      setLoading(true)
      const allLists = await bookmarkService.getLists()
      setLists(allLists)

      // Check which lists contain this article
      const containingListIds: string[] = []
      for (const list of allLists) {
        try {
          const articles = await bookmarkService.getArticlesInList(list.id)
          if (articles.some(a => a.id === articleId)) {
            containingListIds.push(list.id)
          }
        } catch (error) {
          console.warn(`Could not check list ${list.id}`, error)
        }
      }

      setBookmarkedListIds(new Set(containingListIds))
    } catch (error: any) {
      console.error('Failed to load bookmark lists:', error)
      toast.error('Failed to load bookmark lists')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleBookmark = async (listId: string, isCurrentlyBookmarked: boolean) => {
    try {
      setUpdatingListId(listId)

      if (isCurrentlyBookmarked) {
        // Remove from list
        await bookmarkService.removeArticleFromList(listId, articleId)
        setBookmarkedListIds(prev => {
          const next = new Set(prev)
          next.delete(listId)
          return next
        })

        // Update the list count optimistically
        setLists(prev => prev.map(list =>
          list.id === listId
            ? { ...list, article_count: Math.max(0, list.article_count - 1) }
            : list
        ))

        const list = lists.find(l => l.id === listId)
        toast.success(`Removed from "${list?.name}"`)
      } else {
        // Add to list
        await bookmarkService.addArticleToList(listId, articleId)
        setBookmarkedListIds(prev => new Set(prev).add(listId))

        // Update the list count optimistically
        setLists(prev => prev.map(list =>
          list.id === listId
            ? { ...list, article_count: list.article_count + 1 }
            : list
        ))

        const list = lists.find(l => l.id === listId)
        toast.success(`Added to "${list?.name}"`)
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to update bookmark')
      // Reload to get correct state
      loadLists()
    } finally {
      setUpdatingListId(null)
    }
  }

  const isBookmarked = bookmarkedListIds.size > 0

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant={variant}
          size={size}
          className={cn(
            "gap-2 transition-colors min-h-[44px] min-w-[44px]",
            isBookmarked && "text-primary",
            className
          )}
        >
          <Bookmark className={cn(
            "h-4 w-4 transition-all",
            isBookmarked && "fill-current"
          )} />
          {size !== 'icon' && (
            <span className="hidden sm:inline">
              {isBookmarked ? 'Saved' : 'Save'}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel className="flex items-center gap-2">
          <Bookmark className="h-4 w-4" />
          Save to List
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        {loading ? (
          <div className="flex items-center justify-center py-6">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          </div>
        ) : lists.length === 0 ? (
          <div className="py-6 px-2 text-center">
            <FolderPlus className="h-8 w-8 mx-auto text-muted-foreground/50 mb-2" />
            <p className="text-sm text-muted-foreground mb-3">
              No bookmark lists yet
            </p>
            <Button
              variant="outline"
              size="sm"
              className="w-full gap-2"
              onClick={() => {
                setOpen(false)
                onCreateList?.()
              }}
            >
              <Plus className="h-4 w-4" />
              Create List
            </Button>
          </div>
        ) : (
          <>
            <div className="max-h-[300px] overflow-y-auto">
              {lists.map((list) => {
                const isChecked = bookmarkedListIds.has(list.id)
                const isUpdating = updatingListId === list.id

                return (
                  <DropdownMenuItem
                    key={list.id}
                    className="cursor-pointer"
                    onSelect={(e) => {
                      e.preventDefault()
                      handleToggleBookmark(list.id, isChecked)
                    }}
                  >
                    <div className="flex items-center gap-3 w-full">
                      <Checkbox
                        checked={isChecked}
                        disabled={isUpdating}
                        className="pointer-events-none"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{list.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {list.article_count} {list.article_count === 1 ? 'item' : 'items'}
                        </p>
                      </div>
                      {isUpdating && (
                        <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />
                      )}
                    </div>
                  </DropdownMenuItem>
                )
              })}
            </div>

            {lists.length < 10 && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="cursor-pointer text-primary"
                  onSelect={(e) => {
                    e.preventDefault()
                    setOpen(false)
                    onCreateList?.()
                  }}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Create New List
                </DropdownMenuItem>
              </>
            )}
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
