import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Badge } from '@/components/ui/badge'
import { bookmarkService, type BookmarkList } from '@/services/bookmarkService'
import { toast } from 'sonner'
import { Plus, Trash2, Edit2, Bookmark, Loader2, FolderOpen } from 'lucide-react'
import { cn } from '@/lib/utils'

interface BookmarkListManagerProps {
  selectedListId?: string
  onSelectList?: (listId: string | null) => void
  compact?: boolean
}

export function BookmarkListManager({
  selectedListId,
  onSelectList,
  compact = false
}: BookmarkListManagerProps) {
  const [lists, setLists] = useState<BookmarkList[]>([])
  const [loading, setLoading] = useState(true)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [newListName, setNewListName] = useState('')
  const [editingList, setEditingList] = useState<BookmarkList | null>(null)
  const [deletingList, setDeletingList] = useState<BookmarkList | null>(null)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    loadLists()
  }, [])

  const loadLists = async () => {
    try {
      setLoading(true)
      const data = await bookmarkService.getLists()
      setLists(data)
    } catch (error: any) {
      console.error('Failed to load bookmark lists:', error)
      toast.error('Failed to load bookmark lists')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateList = async () => {
    if (!newListName.trim()) {
      toast.error('Please enter a list name')
      return
    }

    if (lists.length >= 10) {
      toast.error('Maximum 10 bookmark lists reached')
      return
    }

    try {
      setActionLoading(true)
      const newList = await bookmarkService.createList(newListName.trim())
      setLists(prev => [...prev, newList])
      setNewListName('')
      setIsCreateDialogOpen(false)
      toast.success(`Created list "${newList.name}"`)
    } catch (error: any) {
      toast.error(error.message || 'Failed to create list')
    } finally {
      setActionLoading(false)
    }
  }

  const handleUpdateList = async () => {
    if (!editingList || !newListName.trim()) {
      toast.error('Please enter a list name')
      return
    }

    try {
      setActionLoading(true)
      const updatedList = await bookmarkService.updateList(editingList.id, newListName.trim())
      setLists(prev => prev.map(l => l.id === updatedList.id ? updatedList : l))
      setNewListName('')
      setEditingList(null)
      setIsEditDialogOpen(false)
      toast.success(`Renamed to "${updatedList.name}"`)
    } catch (error: any) {
      toast.error(error.message || 'Failed to update list')
    } finally {
      setActionLoading(false)
    }
  }

  const handleDeleteList = async () => {
    if (!deletingList) return

    try {
      setActionLoading(true)
      await bookmarkService.deleteList(deletingList.id)
      setLists(prev => prev.filter(l => l.id !== deletingList.id))

      // If we deleted the selected list, clear selection
      if (selectedListId === deletingList.id && onSelectList) {
        onSelectList(null)
      }

      toast.success(`Deleted "${deletingList.name}"`)
      setDeletingList(null)
      setIsDeleteDialogOpen(false)
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete list')
    } finally {
      setActionLoading(false)
    }
  }

  const openEditDialog = (list: BookmarkList) => {
    setEditingList(list)
    setNewListName(list.name)
    setIsEditDialogOpen(true)
  }

  const openDeleteDialog = (list: BookmarkList) => {
    setDeletingList(list)
    setIsDeleteDialogOpen(true)
  }

  if (loading) {
    return (
      <Card className={cn(compact && "border-0 shadow-none")}>
        <CardContent className={cn("flex items-center justify-center p-12", compact && "p-8")}>
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <Card className={cn(compact && "border-0 shadow-none")}>
        <CardHeader className={cn(compact && "pb-3")}>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className={cn("flex items-center gap-2", compact && "text-lg")}>
                <Bookmark className="h-5 w-5" />
                Bookmark Lists
              </CardTitle>
              <CardDescription className={cn(compact && "text-xs mt-1")}>
                Organize your favorite articles
              </CardDescription>
            </div>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button
                  size={compact ? "sm" : "default"}
                  disabled={lists.length >= 10}
                  className="gap-2"
                >
                  <Plus className="h-4 w-4" />
                  {!compact && "New List"}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Bookmark List</DialogTitle>
                  <DialogDescription>
                    Give your bookmark list a memorable name
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <Input
                    placeholder="e.g., Houston Deals, Must Read"
                    value={newListName}
                    onChange={(e) => setNewListName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleCreateList()
                    }}
                    maxLength={50}
                  />
                  <p className="text-xs text-muted-foreground">
                    {lists.length}/10 lists created
                  </p>
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setIsCreateDialogOpen(false)
                      setNewListName('')
                    }}
                  >
                    Cancel
                  </Button>
                  <Button onClick={handleCreateList} disabled={actionLoading}>
                    {actionLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Create List
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>

        <CardContent className="space-y-2">
          {lists.length === 0 ? (
            <div className="text-center py-12">
              <FolderOpen className="h-12 w-12 mx-auto text-muted-foreground/50 mb-3" />
              <p className="text-sm text-muted-foreground mb-4">
                No bookmark lists yet
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsCreateDialogOpen(true)}
                className="gap-2"
              >
                <Plus className="h-4 w-4" />
                Create Your First List
              </Button>
            </div>
          ) : (
            lists.map((list) => (
              <div
                key={list.id}
                className={cn(
                  "group flex items-center justify-between p-3 rounded-lg border transition-all",
                  "hover:bg-muted/50 hover:border-primary/20",
                  selectedListId === list.id && "bg-primary/5 border-primary/40 ring-1 ring-primary/20",
                  onSelectList && "cursor-pointer"
                )}
                onClick={() => onSelectList?.(list.id)}
              >
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium text-sm truncate">{list.name}</h4>
                    <Badge variant="outline" className="text-xs">
                      {list.article_count}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Updated {new Date(list.updated_at).toLocaleDateString()}
                  </p>
                </div>

                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0"
                    onClick={(e) => {
                      e.stopPropagation()
                      openEditDialog(list)
                    }}
                  >
                    <Edit2 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                    onClick={(e) => {
                      e.stopPropagation()
                      openDeleteDialog(list)
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename List</DialogTitle>
            <DialogDescription>
              Enter a new name for this bookmark list
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Input
              placeholder="List name"
              value={newListName}
              onChange={(e) => setNewListName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleUpdateList()
              }}
              maxLength={50}
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsEditDialogOpen(false)
                setNewListName('')
                setEditingList(null)
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleUpdateList} disabled={actionLoading}>
              {actionLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Bookmark List?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{deletingList?.name}"?
              This will remove all {deletingList?.article_count || 0} articles from this list.
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setDeletingList(null)}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteList}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {actionLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Delete List
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
